import asyncio
import logging
import threading
import traceback
from datetime import datetime, timezone

from arq.connections import ArqRedis
from fastapi import APIRouter, BackgroundTasks, Depends, HTTPException, status
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from backend.app.database import async_session, get_db
from backend.app.dependencies import get_current_user, get_redis_optional
from backend.app.models.diary import DiaryEntry
from backend.app.models.user import User
from backend.app.models.video_task import VideoTask
from backend.app.schemas.video import TaskStatusRead

logger = logging.getLogger(__name__)
router = APIRouter(prefix="/api/tasks", tags=["tasks"])


def _create_rate_limit_check():
    from datetime import datetime
    today_start = datetime.now(timezone.utc).replace(hour=0, minute=0, second=0, microsecond=0)
    return today_start


async def _check_and_create_task(
    diary_id: str,
    current_user: User,
    db: AsyncSession,
) -> tuple[VideoTask, str]:
    result = await db.execute(
        select(DiaryEntry).where(
            DiaryEntry.id == diary_id,
            DiaryEntry.user_id == current_user.id,
        )
    )
    diary = result.scalar_one_or_none()
    if not diary:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="日记未找到")

    # Rate limit check
    from datetime import datetime
    from sqlalchemy import func
    today_start = datetime.now(timezone.utc).replace(hour=0, minute=0, second=0, microsecond=0)
    count_result = await db.execute(
        select(func.count(VideoTask.id)).where(
            VideoTask.user_id == current_user.id,
            VideoTask.created_at >= today_start,
            VideoTask.status != "failed",
        )
    )
    today_count = count_result.scalar()
    from backend.app.config import settings
    if today_count >= settings.max_videos_per_user_day:
        raise HTTPException(
            status_code=status.HTTP_429_TOO_MANY_REQUESTS,
            detail=f"每日生成次数已达上限（{settings.max_videos_per_user_day}次），失败的生成不计入限额",
        )

    task = VideoTask(
        diary_id=diary.id,
        user_id=current_user.id,
        status="pending",
    )
    db.add(task)
    await db.commit()
    await db.refresh(task)

    return task, diary.content


@router.post("/generate/{diary_id}", response_model=TaskStatusRead)
async def generate_video(
    diary_id: str,
    background_tasks: BackgroundTasks,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
    redis: ArqRedis | None = Depends(get_redis_optional),
):
    task, content = await _check_and_create_task(diary_id, current_user, db)

    # If Redis is available, use task queue; otherwise run in background
    if redis:
        logger.info(f"Enqueuing task {task.id} to ARQ worker")
        await redis.enqueue_job("backend.app.worker.jobs.run_video_pipeline", str(task.id), content)
    else:
        logger.info(f"No Redis, starting background pipeline for task {task.id}")
        background_tasks.add_task(_run_pipeline_safely, str(task.id), content)

    return TaskStatusRead(
        id=task.id,
        status=task.status,
        progress=task.progress,
        current_stage=task.current_stage,
        error_message=task.error_message,
        video_id=None,
    )


async def _run_pipeline_safely(task_id: str, content: str):
    import traceback
    from backend.app.services.pipeline import execute_pipeline

    try:
        await execute_pipeline(task_id, content)
    except Exception:
        logger.error(f"Background pipeline failed for task {task_id}:\n{traceback.format_exc()}")
        from backend.app.database import async_session
        async with async_session() as db:
            result = await db.execute(select(VideoTask).where(VideoTask.id == task_id))
            task = result.scalar_one_or_none()
            if task and task.status != "failed":
                task.status = "failed"
                task.error_message = str(
                    traceback.format_exc()[-500:]
                )
                task.current_stage = "failed"
                await db.commit()


@router.get("/{task_id}", response_model=TaskStatusRead)
async def get_task_status(
    task_id: str,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    result = await db.execute(
        select(VideoTask).where(
            VideoTask.id == task_id,
            VideoTask.user_id == current_user.id,
        )
    )
    task = result.scalar_one_or_none()
    if not task:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="任务未找到")

    return TaskStatusRead(
        id=task.id,
        status=task.status,
        progress=task.progress,
        current_stage=task.current_stage,
        error_message=task.error_message,
        video_id=task.id if task.status == "completed" else None,
    )
