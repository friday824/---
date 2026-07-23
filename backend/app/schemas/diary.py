from datetime import datetime
from pydantic import BaseModel


class DiaryCreate(BaseModel):
    title: str
    content: str
    mood_tag: str | None = None
    is_public: bool = False


class DiaryUpdate(BaseModel):
    title: str | None = None
    content: str | None = None
    mood_tag: str | None = None
    is_public: bool | None = None


class DiaryRead(BaseModel):
    id: str
    user_id: str
    title: str
    content: str
    word_count: int
    mood_tag: str | None
    is_public: bool
    created_at: datetime
    updated_at: datetime

    model_config = {"from_attributes": True}


class DiaryListItem(BaseModel):
    id: str
    title: str
    word_count: int
    mood_tag: str | None
    has_video: bool = False
    created_at: datetime

    model_config = {"from_attributes": True}
