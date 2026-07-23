from fastapi import APIRouter

from backend.app.api.auth import router as auth_router
from backend.app.api.diaries import router as diaries_router
from backend.app.api.tasks import router as tasks_router
from backend.app.api.videos import router as videos_router

api_router = APIRouter()
api_router.include_router(auth_router)
api_router.include_router(diaries_router)
api_router.include_router(tasks_router)
api_router.include_router(videos_router)
