import uuid
from datetime import datetime

from sqlalchemy import DateTime, Float, ForeignKey, Integer, String, Text, func
from sqlalchemy.dialects.sqlite import CHAR
from sqlalchemy.orm import Mapped, mapped_column, relationship

from backend.app.database import Base


class Scene(Base):
    __tablename__ = "scenes"

    id: Mapped[str] = mapped_column(
        CHAR(36), primary_key=True, default=lambda: str(uuid.uuid4())
    )
    task_id: Mapped[str] = mapped_column(
        CHAR(36), ForeignKey("video_tasks.id"), nullable=False, index=True
    )
    scene_index: Mapped[int] = mapped_column(Integer, nullable=False)
    description_cn: Mapped[str] = mapped_column(Text, nullable=False)
    narration_cn: Mapped[str] = mapped_column(Text, nullable=False)
    duration_s: Mapped[float] = mapped_column(Float, nullable=False)
    emotion: Mapped[str | None] = mapped_column(String(50), nullable=True)
    image_prompt: Mapped[str] = mapped_column(Text, nullable=False)
    image_filename: Mapped[str | None] = mapped_column(String(255), nullable=True)
    created_at: Mapped[datetime] = mapped_column(DateTime, server_default=func.now())

    task = relationship("VideoTask", back_populates="scenes")
