from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession

from backend.app.database import get_db
from backend.app.dependencies import get_current_user
from backend.app.models.user import User
from backend.app.schemas.user import Token, TokenRefresh, UserCreate, UserLogin, UserRead
from backend.app.services import auth_service

router = APIRouter(prefix="/api/auth", tags=["auth"])


@router.post("/register", response_model=Token, status_code=status.HTTP_201_CREATED)
async def register(body: UserCreate, db: AsyncSession = Depends(get_db)):
    existing = await auth_service.get_user_by_email(db, body.email)
    if existing:
        raise HTTPException(status_code=status.HTTP_409_CONFLICT, detail="邮箱已被注册")

    user = await auth_service.create_user(db, body.email, body.username, body.password)
    access_token = auth_service.create_access_token(user.id)
    refresh_token = auth_service.create_refresh_token(user.id)
    return Token(access_token=access_token, refresh_token=refresh_token)


@router.post("/login", response_model=Token)
async def login(body: UserLogin, db: AsyncSession = Depends(get_db)):
    user = await auth_service.get_user_by_email(db, body.email)
    if not user or not auth_service.verify_password(body.password, user.hashed_password):
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="邮箱或密码错误")
    if not user.is_active:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="账户已被禁用")

    access_token = auth_service.create_access_token(user.id)
    refresh_token = auth_service.create_refresh_token(user.id)
    return Token(access_token=access_token, refresh_token=refresh_token)


@router.post("/refresh", response_model=Token)
async def refresh_token(body: TokenRefresh, db: AsyncSession = Depends(get_db)):
    try:
        payload = auth_service.decode_token(body.refresh_token)
        if payload.get("type") != "refresh":
            raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="无效的刷新令牌")
        user_id = payload.get("sub")
        user = await auth_service.get_user_by_id(db, user_id)
        if not user or not user.is_active:
            raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="用户不存在或已被禁用")
    except Exception:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="无效的刷新令牌")

    access_token = auth_service.create_access_token(user_id)
    new_refresh_token = auth_service.create_refresh_token(user_id)
    return Token(access_token=access_token, refresh_token=new_refresh_token)


@router.get("/me", response_model=UserRead)
async def get_me(current_user: User = Depends(get_current_user)):
    return current_user
