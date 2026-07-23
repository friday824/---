"""CLI tool to test the AI pipeline: python -m backend.cli diary.txt"""

import asyncio
import sys
import uuid
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent.parent))

from backend.app.database import async_session, engine
from backend.app.models import Base
from backend.app.models.video_task import VideoTask
from backend.app.services.pipeline import execute_pipeline


async def init_db():
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)


async def run_pipeline(diary_text: str) -> str:
    await init_db()

    task_id = str(uuid.uuid4())

    async with async_session() as db:
        task = VideoTask(
            id=task_id,
            diary_id=str(uuid.uuid4()),
            user_id=str(uuid.uuid4()),
            status="pending",
        )
        db.add(task)
        await db.commit()

    print(f"Task ID: {task_id}")
    print(f"Diary length: {len(diary_text)} chars")
    print("-" * 50)

    video_path = await execute_pipeline(task_id, diary_text)
    print(f"\nVideo generated: {video_path}")
    return video_path


def main():
    if len(sys.argv) < 2:
        print("Usage: python -m backend.cli <diary_file>")
        print("   or: python -m backend.cli - (read from stdin)")
        sys.exit(1)

    if sys.argv[1] == "-":
        text = sys.stdin.read()
    else:
        text = Path(sys.argv[1]).read_text(encoding="utf-8")

    if not text.strip():
        print("Error: empty input")
        sys.exit(1)

    asyncio.run(run_pipeline(text))


if __name__ == "__main__":
    main()
