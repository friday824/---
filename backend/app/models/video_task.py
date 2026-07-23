import uuid
from datetime import datetime

from sqlalchemy import BigInteger, DateTime, Float, ForeignKey, Integer, String, Text, func
from sqlalchemy.dialects.sqlite import CHAR, JSON
from sqlalchemy.orm import Mapped, mapped_column, relationship

from backend.app.database import Base


class VideoTask(Base):
    __tablename__ = "video_tasks"

    id: Mapped[str] = mapped_column(
        CHAR(36), primary_key=True, default=lambda: str(uuid.uuid4())
    )
    diary_id: Mapped[str] = mapped_column(
        CHAR(36), ForeignKey("diary_entries.id"), nullable=False, index=True
    )
    user_id: Mapped[str] = mapped_column(
        CHAR(36), ForeignKey("users.id"), nullable=False, index=True
    )
    status: Mapped[str] = mapped_column(String(20), default="pending", index=True)
    progress: Mapped[int] = mapped_column(Integer, default=0)
    current_stage: Mapped[str | None] = mapped_column(String(50), nullable=True)
    error_message: Mapped[str | None] = mapped_column(Text, nullable=True)
    script_output: Mapped[dict | None] = mapped_column(JSON, nullable=True)
    total_duration_s: Mapped[float | None] = mapped_column(Float, nullable=True)
    bgm_category: Mapped[str | None] = mapped_column(String(50), nullable=True)
    video_filename: Mapped[str | None] = mapped_column(String(255), nullable=True)
    video_duration_s: Mapped[float | None] = mapped_column(Float, nullable=True)
    video_size_bytes: Mapped[int | None] = mapped_column(BigInteger, nullable=True)
    created_at: Mapped[datetime] = mapped_column(DateTime, server_default=func.now())
    updated_at: Mapped[datetime] = mapped_column(
        DateTime, server_default=func.now(), onupdate=func.now()
    )
    completed_at: Mapped[datetime | None] = mapped_column(DateTime, nullable=True)

    diary = relationship("DiaryEntry", back_populates="video_tasks")
    user = relationship("User", back_populates="video_tasks")
    scenes = relationship("Scene", back_populates="task", cascade="all, delete-orphan")
    events = relationship("TaskEvent", back_populates="task", cascade="all, delete-orphan")
