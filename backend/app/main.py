import logging
from contextlib import asynccontextmanager

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from sqlalchemy import update

from backend.app.api import api_router
from backend.app.config import settings
from backend.app.database import async_session, engine
from backend.app.models import Base
from backend.app.models.video_task import VideoTask

logger = logging.getLogger(__name__)


@asynccontextmanager
async def lifespan(app: FastAPI):
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)

    # Mark stale pending/processing tasks as failed (lost on server restart)
    async with async_session() as db:
        result = await db.execute(
            update(VideoTask)
            .where(VideoTask.status.in_(["pending", "processing"]))
            .values(
                status="failed",
                error_message="服务器重启，任务丢失，请重新生成",
                current_stage="failed",
            )
        )
        await db.commit()
        if result.rowcount:
            logger.info(f"Marked {result.rowcount} stale task(s) as failed after restart")

    yield
    await engine.dispose()


app = FastAPI(
    title="日记动漫化",
    description="把你的日记变成温馨的小动画",
    version="0.1.0",
    lifespan=lifespan,
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.cors_origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(api_router)

data_dir = settings.data_dir
data_dir.mkdir(parents=True, exist_ok=True)
app.mount("/static", StaticFiles(directory=str(data_dir)), name="static")


@app.get("/api/health")
async def health():
    return {"status": "ok"}
