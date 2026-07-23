import json
import logging
import traceback
from datetime import datetime, timezone
from pathlib import Path

from sqlalchemy import select

from backend.app.database import async_session
from backend.app.models.video_task import VideoTask
from backend.app.models.scene import Scene
from backend.app.models.task_event import TaskEvent
from backend.app.services.script_gen import ScriptOutput, generate_script
from backend.app.services.image_gen import generate_scene_images
from backend.app.services.tts import generate_voiceover
from backend.app.services.bgm import select_and_prepare_bgm
from backend.app.services.compositor import composite_video

logger = logging.getLogger(__name__)


async def _update_task(task_id: str, **kwargs) -> None:
    async with async_session() as db:
        result = await db.execute(select(VideoTask).where(VideoTask.id == task_id))
        task = result.scalar_one_or_none()
        if task is None:
            return
        for key, value in kwargs.items():
            setattr(task, key, value)
        await db.commit()


async def _add_event(task_id: str, event_type: str, stage_name: str, message: str, metadata: dict | None = None) -> None:
    async with async_session() as db:
        event = TaskEvent(
            task_id=task_id,
            event_type=event_type,
            stage_name=stage_name,
            message=message,
            metadata=metadata,
        )
        db.add(event)
        await db.commit()


async def _save_scenes(task_id: str, script: ScriptOutput, image_paths: list[Path]) -> None:
    async with async_session() as db:
        for i, scene in enumerate(script.scenes):
            image_filename = image_paths[i].name if i < len(image_paths) else None
            db_scene = Scene(
                task_id=task_id,
                scene_index=scene.index,
                description_cn=scene.scene_description_cn,
                narration_cn=scene.narration_text_cn,
                duration_s=scene.suggested_duration_s,
                emotion=scene.emotion,
                image_prompt=scene.image_prompt,
                image_filename=image_filename,
            )
            db.add(db_scene)
        await db.commit()


async def execute_pipeline(task_id: str, diary_text: str) -> str:
    await _update_task(task_id, status="processing", current_stage="script_gen", progress=5)

    try:
        # Stage 1: Script generation
        await _add_event(task_id, "stage_start", "script_gen", "正在分析日记，生成动画剧本...")
        script = await generate_script(diary_text)
        await _update_task(
            task_id,
            current_stage="script_gen",
            progress=20,
            script_output={
                "title": script.title,
                "overall_emotion": script.overall_emotion,
                "total_duration_suggestion": script.total_duration_suggestion,
                "bgm_category": script.bgm_category,
                "scenes": [
                    {
                        "index": s.index,
                        "scene_description_cn": s.scene_description_cn,
                        "narration_text_cn": s.narration_text_cn,
                        "suggested_duration_s": s.suggested_duration_s,
                        "emotion": s.emotion,
                        "image_prompt": s.image_prompt,
                    }
                    for s in script.scenes
                ],
            },
        )
        await _add_event(
            task_id, "stage_complete", "script_gen",
            f"剧本生成完成：{script.title}，共{len(script.scenes)}个场景"
        )

        # Stage 2: Image generation
        await _update_task(task_id, current_stage="image_gen", progress=20)
        await _add_event(
            task_id, "stage_start", "image_gen",
            f"正在绘制{len(script.scenes)}个动画场景..."
        )
        image_paths = await generate_scene_images(script.scenes, task_id)
        await _update_task(task_id, current_stage="image_gen", progress=50)
        await _add_event(
            task_id, "stage_complete", "image_gen",
            f"场景绘制完成：成功{len(image_paths)}/{len(script.scenes)}张"
        )

        # Stage 3: TTS voiceover
        await _update_task(task_id, current_stage="tts", progress=50)
        await _add_event(task_id, "stage_start", "tts", "正在录制温暖旁白...")
        voiceover_path, audio_duration = await generate_voiceover(script.scenes, task_id)
        await _update_task(task_id, current_stage="tts", progress=65)
        await _add_event(
            task_id, "stage_complete", "tts",
            f"旁白录制完成，时长{audio_duration:.0f}秒"
        )

        # Stage 4: BGM selection
        await _update_task(task_id, current_stage="bgm", progress=65)
        await _add_event(task_id, "stage_start", "bgm", "正在匹配背景音乐...")
        bgm_path = select_and_prepare_bgm(
            script.bgm_category, audio_duration, task_id
        )
        if bgm_path:
            await _add_event(task_id, "stage_complete", "bgm", "背景音乐准备完成")
        else:
            await _add_event(task_id, "stage_complete", "bgm", "未找到匹配的BGM，将生成无声版本")

        # Stage 5: Compositing
        await _update_task(task_id, current_stage="compositing", progress=70)
        await _add_event(task_id, "stage_start", "compositing", "正在合成视频...")
        video_path = await composite_video(
            script.scenes, image_paths, voiceover_path, bgm_path, task_id
        )

        # Save scenes to database
        await _save_scenes(task_id, script, image_paths)

        file_size = video_path.stat().st_size
        await _update_task(
            task_id,
            status="completed",
            progress=100,
            current_stage="done",
            total_duration_s=audio_duration,
            bgm_category=script.bgm_category,
            video_filename=video_path.name,
            video_duration_s=audio_duration,
            video_size_bytes=file_size,
            completed_at=datetime.now(timezone.utc),
        )
        await _add_event(
            task_id, "stage_complete", "done",
            f"视频生成完成！文件大小：{file_size / 1024 / 1024:.1f}MB"
        )

        return str(video_path)

    except Exception as e:
        logger.error(f"Pipeline failed for task {task_id}: {traceback.format_exc()}")
        await _update_task(
            task_id,
            status="failed",
            error_message=str(e),
            current_stage="failed",
        )
        await _add_event(task_id, "error", "failed", f"生成失败：{e}")
        raise
