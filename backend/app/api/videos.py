from fastapi import APIRouter, Depends, HTTPException, Query, status
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload

from backend.app.database import get_db
from backend.app.dependencies import get_current_user
from backend.app.models.user import User
from backend.app.models.video_task import VideoTask
from backend.app.schemas.video import VideoTaskListItem, VideoTaskRead
from backend.app.services.auth_service import decode_token, get_user_by_id

router = APIRouter(prefix="/api/videos", tags=["videos"])


@router.get("", response_model=list[VideoTaskListItem])
async def list_videos(
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    result = await db.execute(
        select(VideoTask)
        .where(VideoTask.user_id == current_user.id)
        .order_by(VideoTask.created_at.desc())
    )
    tasks = result.scalars().all()

    items = []
    for t in tasks:
        video_url = f"/static/videos/{t.video_filename}" if t.video_filename else None
        items.append(
            VideoTaskListItem(
                id=t.id,
                diary_id=t.diary_id,
                title=t.script_output.get("title", "") if t.script_output else "",
                status=t.status,
                progress=t.progress,
                current_stage=t.current_stage,
                total_duration_s=t.total_duration_s,
                video_filename=t.video_filename,
                video_url=video_url,
                created_at=t.created_at,
                completed_at=t.completed_at,
            )
        )
    return items


@router.get("/{video_id}", response_model=VideoTaskRead)
async def get_video(
    video_id: str,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    result = await db.execute(
        select(VideoTask)
        .where(VideoTask.id == video_id, VideoTask.user_id == current_user.id)
        .options(selectinload(VideoTask.scenes), selectinload(VideoTask.events))
    )
    task = result.scalar_one_or_none()
    if not task:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="视频未找到")

    resp = VideoTaskRead.model_validate(task)
    if task.video_filename:
        resp.video_url = f"/static/videos/{task.video_filename}"
    return resp


@router.delete("/{video_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_video(
    video_id: str,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    from pathlib import Path

    result = await db.execute(
        select(VideoTask)
        .where(VideoTask.id == video_id, VideoTask.user_id == current_user.id)
        .options(selectinload(VideoTask.scenes))
    )
    task = result.scalar_one_or_none()
    if not task:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="视频未找到")

    # Delete video file
    if task.video_filename:
        video_path = Path("data/videos") / task.video_filename
        if video_path.exists():
            video_path.unlink()

    # Delete scene images
    for scene in task.scenes:
        if scene.image_filename:
            img_path = Path("data/images") / scene.image_filename
            if img_path.exists():
                img_path.unlink()

    # Delete audio files
    for prefix in [f"{task.id}_voiceover", f"{task.id}_bgm_prepared"]:
        for ext in [".mp3", ".wav"]:
            audio_path = Path("data/audio") / (prefix + ext)
            if audio_path.exists():
                audio_path.unlink()

    await db.delete(task)
    await db.commit()


@router.get("/{video_id}/file")
async def get_video_file(
    video_id: str,
    token: str | None = Query(None),
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    from fastapi.responses import FileResponse
    from pathlib import Path

    # Support both header auth (API calls) and query param token (browser <video> tag)
    user = current_user
    if token:
        try:
            payload = decode_token(token)
            if payload.get("type") != "access":
                raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="无效的令牌类型")
            uid = payload.get("sub")
            if uid:
                from backend.app.services.auth_service import get_user_by_id
                u = await get_user_by_id(db, uid)
                if u and u.is_active:
                    user = u
        except Exception:
            pass

    result = await db.execute(
        select(VideoTask).where(
            VideoTask.id == video_id,
            VideoTask.user_id == user.id,
            VideoTask.status == "completed",
        )
    )
    task = result.scalar_one_or_none()
    if not task or not task.video_filename:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="视频文件未找到")

    video_path = Path("data/videos") / task.video_filename
    if not video_path.exists():
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="视频文件不存在")

    return FileResponse(
        video_path,
        media_type="video/mp4",
        filename=f"{task.script_output.get('title', 'video')}.mp4" if task.script_output else "video.mp4",
    )
