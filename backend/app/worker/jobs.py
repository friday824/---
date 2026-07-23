from backend.app.services.pipeline import execute_pipeline


async def run_video_pipeline(ctx: dict, task_id: str, diary_content: str) -> str:
    return await execute_pipeline(task_id, diary_content)
