from datetime import datetime

from sqlalchemy import DateTime, ForeignKey, Integer, String, Text, func
from sqlalchemy.dialects.sqlite import CHAR, JSON
from sqlalchemy.orm import Mapped, mapped_column, relationship

from backend.app.database import Base


class TaskEvent(Base):
    __tablename__ = "task_events"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    task_id: Mapped[str] = mapped_column(
        CHAR(36), ForeignKey("video_tasks.id"), nullable=False, index=True
    )
    event_type: Mapped[str] = mapped_column(String(50), nullable=False)
    stage_name: Mapped[str | None] = mapped_column(String(50), nullable=True)
    message: Mapped[str | None] = mapped_column(Text, nullable=True)
    extra_data: Mapped[dict | None] = mapped_column("metadata", JSON, nullable=True)
    created_at: Mapped[datetime] = mapped_column(DateTime, server_default=func.now())

    task = relationship("VideoTask", back_populates="events")
