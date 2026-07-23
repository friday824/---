from datetime import datetime
from pydantic import BaseModel


class SceneRead(BaseModel):
    id: str
    scene_index: int
    description_cn: str
    narration_cn: str
    duration_s: float
    emotion: str | None
    image_prompt: str
    image_filename: str | None

    model_config = {"from_attributes": True}


class TaskEventRead(BaseModel):
    id: int
    event_type: str
    stage_name: str | None
    message: str | None
    created_at: datetime

    model_config = {"from_attributes": True}


class VideoTaskRead(BaseModel):
    id: str
    diary_id: str
    status: str
    progress: int
    current_stage: str | None
    error_message: str | None
    total_duration_s: float | None
    bgm_category: str | None
    video_filename: str | None
    video_duration_s: float | None
    video_size_bytes: int | None
    video_url: str | None = None
    created_at: datetime
    completed_at: datetime | None
    scenes: list[SceneRead] = []
    events: list[TaskEventRead] = []

    model_config = {"from_attributes": True}


class VideoTaskListItem(BaseModel):
    id: str
    diary_id: str
    title: str = ""
    status: str
    progress: int
    current_stage: str | None
    total_duration_s: float | None
    video_filename: str | None
    video_url: str | None = None
    created_at: datetime
    completed_at: datetime | None

    model_config = {"from_attributes": True}


class TaskStatusRead(BaseModel):
    id: str
    status: str
    progress: int
    current_stage: str | None
    error_message: str | None
    video_id: str | None

    model_config = {"from_attributes": True}
