from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy import select, func
from sqlalchemy.ext.asyncio import AsyncSession

from backend.app.database import get_db
from backend.app.dependencies import get_current_user
from backend.app.models.diary import DiaryEntry
from backend.app.models.user import User
from backend.app.models.video_task import VideoTask
from backend.app.schemas.diary import DiaryCreate, DiaryListItem, DiaryRead, DiaryUpdate

router = APIRouter(prefix="/api/diaries", tags=["diaries"])


@router.get("", response_model=list[DiaryListItem])
async def list_diaries(
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    result = await db.execute(
        select(DiaryEntry)
        .where(DiaryEntry.user_id == current_user.id)
        .order_by(DiaryEntry.created_at.desc())
    )
    diaries = result.scalars().all()

    diary_ids = [d.id for d in diaries]
    video_result = await db.execute(
        select(VideoTask.diary_id)
        .where(
            VideoTask.diary_id.in_(diary_ids),
            VideoTask.status == "completed",
        )
        .distinct()
    )
    has_video_ids = {row[0] for row in video_result}

    return [
        DiaryListItem(
            id=d.id,
            title=d.title,
            word_count=d.word_count,
            mood_tag=d.mood_tag,
            has_video=d.id in has_video_ids,
            created_at=d.created_at,
        )
        for d in diaries
    ]


@router.post("", response_model=DiaryRead, status_code=status.HTTP_201_CREATED)
async def create_diary(
    body: DiaryCreate,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    diary = DiaryEntry(
        user_id=current_user.id,
        title=body.title,
        content=body.content,
        word_count=len(body.content),
        mood_tag=body.mood_tag,
        is_public=body.is_public,
    )
    db.add(diary)
    await db.commit()
    await db.refresh(diary)
    return diary


@router.get("/{diary_id}", response_model=DiaryRead)
async def get_diary(
    diary_id: str,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    result = await db.execute(
        select(DiaryEntry).where(
            DiaryEntry.id == diary_id,
            DiaryEntry.user_id == current_user.id,
        )
    )
    diary = result.scalar_one_or_none()
    if not diary:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="日记未找到")
    return diary


@router.put("/{diary_id}", response_model=DiaryRead)
async def update_diary(
    diary_id: str,
    body: DiaryUpdate,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    result = await db.execute(
        select(DiaryEntry).where(
            DiaryEntry.id == diary_id,
            DiaryEntry.user_id == current_user.id,
        )
    )
    diary = result.scalar_one_or_none()
    if not diary:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="日记未找到")

    if body.title is not None:
        diary.title = body.title
    if body.content is not None:
        diary.content = body.content
        diary.word_count = len(body.content)
    if body.mood_tag is not None:
        diary.mood_tag = body.mood_tag
    if body.is_public is not None:
        diary.is_public = body.is_public

    await db.commit()
    await db.refresh(diary)
    return diary


@router.delete("/{diary_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_diary(
    diary_id: str,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    result = await db.execute(
        select(DiaryEntry).where(
            DiaryEntry.id == diary_id,
            DiaryEntry.user_id == current_user.id,
        )
    )
    diary = result.scalar_one_or_none()
    if not diary:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="日记未找到")

    await db.delete(diary)
    await db.commit()
