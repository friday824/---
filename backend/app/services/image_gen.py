import asyncio
from pathlib import Path

import httpx

from backend.app.config import settings
from backend.app.services.script_gen import SceneScript
from backend.app.utils.exceptions import ImageGenerationError

NEGATIVE_PROMPT = (
    "photorealistic, 3d, real person, blurry, low quality, "
    "text, watermark, ugly, deformed, bad anatomy, extra fingers"
)


async def _generate_single_image(image_prompt: str, output_path: Path) -> None:
    from dashscope.aigc.image_generation import ImageGeneration
    from dashscope.api_entities.dashscope_response import Message, Role

    message = Message(
        role=Role.USER,
        content=[{"text": image_prompt}],
    )

    result = await asyncio.to_thread(
        ImageGeneration.call,
        model=ImageGeneration.Models.wan2_6_t2i,
        api_key=settings.dashscope_api_key,
        messages=[message],
        negative_prompt=NEGATIVE_PROMPT,
        n=1,
        size="1280*720",
        prompt_extend=True,
        watermark=False,
    )

    if result.status_code != 200:
        raise ImageGenerationError(
            f"通义万相API返回错误: code={result.code}, message={result.message}"
        )

    image_url = None
    try:
        choices = result.output.get("choices", []) if result.output else []
        if choices:
            content_list = choices[0].get("message", {}).get("content", [])
            if content_list:
                image_url = content_list[0].get("image", "")
    except (AttributeError, KeyError, IndexError):
        pass

    # Check for async task fallback
    if not image_url:
        task_id = result.output.get("task_id", "") if result.output else ""
        if task_id:
            image_url = await _poll_task(task_id)

    if not image_url:
        raise ImageGenerationError(f"通义万相未返回图片: {result.output}")

    async with httpx.AsyncClient(timeout=120.0) as client:
        img_resp = await client.get(image_url, follow_redirects=True)
        if img_resp.status_code != 200:
            raise ImageGenerationError(f"下载图片失败: HTTP {img_resp.status_code}")

    output_path.parent.mkdir(parents=True, exist_ok=True)
    output_path.write_bytes(img_resp.content)


async def _poll_task(task_id: str, max_wait: int = 120) -> str:
    from dashscope.aigc.image_generation import ImageGeneration

    for _ in range(max_wait):
        await asyncio.sleep(1)
        result = await asyncio.to_thread(ImageGeneration.fetch, task_id, api_key=settings.dashscope_api_key)

        if result.status_code != 200:
            continue

        task_status = result.output.get("task_status", "") if result.output else ""

        if task_status == "SUCCEEDED":
            choices = result.output.get("choices", []) if result.output else []
            if choices:
                content_list = choices[0].get("message", {}).get("content", [])
                if content_list:
                    return content_list[0].get("image", "")
            raise ImageGenerationError("任务完成但未返回图片URL")

        if task_status == "FAILED":
            msg = (result.output or {}).get("message", "未知错误")
            raise ImageGenerationError(f"图片生成任务失败: {msg}")

    raise ImageGenerationError(f"图片生成任务超时 (task_id={task_id})")


async def generate_scene_images(
    scenes: list[SceneScript], task_id: str
) -> list[Path]:
    image_dir = settings.image_output_dir / task_id
    image_dir.mkdir(parents=True, exist_ok=True)

    semaphore = asyncio.Semaphore(3)

    async def generate_one(scene: SceneScript) -> Path:
        image_path = image_dir / f"scene_{scene.index:02d}.png"
        async with semaphore:
            await _generate_single_image(scene.image_prompt, image_path)
        return image_path

    tasks = [generate_one(s) for s in scenes]
    results = await asyncio.gather(*tasks, return_exceptions=True)

    successful = []
    failures = []
    for result in results:
        if isinstance(result, Exception):
            failures.append(result)
        else:
            successful.append(result)

    if len(successful) < 2 and failures:
        raise ImageGenerationError(
            f"图片生成失败过多 ({len(failures)}/{len(scenes)}): {failures[0]}"
        )

    return successful