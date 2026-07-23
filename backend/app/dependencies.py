from arq import create_pool
from arq.connections import ArqRedis, RedisSettings
from fastapi import Depends, HTTPException, status
from fastapi.security import HTTPAuthorizationCredentials, HTTPBearer
from jose import JWTError
from sqlalchemy.ext.asyncio import AsyncSession

from backend.app.config import settings
from backend.app.database import get_db
from backend.app.models.user import User
from backend.app.services.auth_service import decode_token, get_user_by_id

security = HTTPBearer()


async def get_current_user(
    credentials: HTTPAuthorizationCredentials = Depends(security),
    db: AsyncSession = Depends(get_db),
) -> User:
    token = credentials.credentials
    try:
        payload = decode_token(token)
        if payload.get("type") != "access":
            raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="无效的令牌类型")
        user_id: str = payload.get("sub")
        if user_id is None:
            raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="无效的令牌")
    except JWTError:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="无效的令牌")

    user = await get_user_by_id(db, user_id)
    if user is None:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="用户不存在")
    if not user.is_active:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="账户已被禁用")
    return user


_redis_pool: ArqRedis | None = None


async def get_redis() -> ArqRedis:
    global _redis_pool
    if _redis_pool is None:
        _redis_pool = await create_pool(RedisSettings.from_dsn(settings.redis_url))
    return _redis_pool


async def get_redis_optional() -> ArqRedis | None:
    global _redis_pool
    if _redis_pool is None:
        try:
            _redis_pool = await create_pool(RedisSettings.from_dsn(settings.redis_url))
        except Exception:
            return None
    try:
        await _redis_pool.ping()
        return _redis_pool
    except Exception:
        return None
