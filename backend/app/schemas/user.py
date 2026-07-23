from datetime import datetime
from pydantic import BaseModel, EmailStr


class UserCreate(BaseModel):
    email: str
    username: str
    password: str


class UserLogin(BaseModel):
    email: str
    password: str


class UserRead(BaseModel):
    id: str
    email: str
    username: str
    is_active: bool
    created_at: datetime

    model_config = {"from_attributes": True}


class Token(BaseModel):
    access_token: str
    refresh_token: str
    token_type: str = "bearer"


class TokenRefresh(BaseModel):
    refresh_token: str
