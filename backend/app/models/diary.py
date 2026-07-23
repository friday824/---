import uuid
from datetime import datetime

from sqlalchemy import Boolean, DateTime, ForeignKey, Integer, String, Text, func
from sqlalchemy.dialects.sqlite import CHAR
from sqlalchemy.orm import Mapped, mapped_column, relationship

from backend.app.database import Base


class DiaryEntry(Base):
    __tablename__ = "diary_entries"

    id: Mapped[str] = mapped_column(
        CHAR(36), primary_key=True, default=lambda: str(uuid.uuid4())
    )
    user_id: Mapped[str] = mapped_column(
        CHAR(36), ForeignKey("users.id"), nullable=False, index=True
    )
    title: Mapped[str] = mapped_column(String(255), nullable=False)
    content: Mapped[str] = mapped_column(Text, nullable=False)
    word_count: Mapped[int] = mapped_column(Integer, default=0)
    mood_tag: Mapped[str | None] = mapped_column(String(50), nullable=True)
    is_public: Mapped[bool] = mapped_column(Boolean, default=False)
    created_at: Mapped[datetime] = mapped_column(DateTime, server_default=func.now())
    updated_at: Mapped[datetime] = mapped_column(
        DateTime, server_default=func.now(), onupdate=func.now()
    )

    user = relationship("User", back_populates="diaries")
    video_tasks = relationship("VideoTask", back_populates="diary", cascade="all, delete-orphan")
