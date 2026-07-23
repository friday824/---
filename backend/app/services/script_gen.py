import asyncio
import json
import logging
from dataclasses import dataclass, field

import dashscope
from dashscope import Generation

from backend.app.config import settings
from backend.app.utils.exceptions import ScriptGenerationError

logger = logging.getLogger(__name__)

dashscope.api_key = settings.dashscope_api_key

SYSTEM_PROMPT = """你是一位专业的动画剧本作家和情感分析师。用户会提供一篇日记，请你：

1. 深入分析日记中的关键情感时刻、场景、人物
2. 将日记改写成一个温暖人心的动画短片剧本
3. 将剧本拆分为3-8个场景（数量由内容决定）
4. 每个场景必须包含：中文场景描述、中文旁白文字、建议时长（秒）、情感标签、用于AI绘图的提示词

重要规则：
- 旁白文字要温暖、有画面感，像是在给朋友讲故事
- 图像提示词必须以 "anime style, Ghibli-inspired, warm lighting, high quality, 16:9 composition, soft colors" 开头
- 建议时长每个场景5-12秒，总时长30-90秒
- 输出必须是严格的JSON格式，不要有任何其他文字

你必须严格按照以下JSON schema输出（字段名必须完全一致）：
{
  "title": "动画标题",
  "overall_emotion": "warm_happy",
  "total_duration_suggestion": 45,
  "scenes": [
    {
      "index": 1,
      "scene_description_cn": "场景的详细中文描述",
      "narration_text_cn": "这个场景的中文旁白文字，要温暖有画面感",
      "suggested_duration_s": 8,
      "emotion": "warm_happy",
      "image_prompt": "anime style, Ghibli-inspired, warm lighting, high quality, 16:9 composition, soft colors, 具体的场景画面描述"
    }
  ]
}"""


@dataclass
class SceneScript:
    index: int
    scene_description_cn: str
    narration_text_cn: str
    suggested_duration_s: float
    emotion: str
    image_prompt: str


@dataclass
class ScriptOutput:
    title: str
    overall_emotion: str
    total_duration_suggestion: float
    bgm_category: str
    scenes: list[SceneScript] = field(default_factory=list)


def _get_field(d: dict, *keys: str, default: str = "") -> str:
    """Try multiple keys, returning the first non-empty value."""
    for k in keys:
        val = d.get(k, "")
        if val and val.strip():
            return val.strip()
    return default


def _map_emotion_to_bgm(emotion: str) -> str:
    mapping = {
        "warm_happy": "warm_happy",
        "joyful": "warm_happy",
        "happy": "warm_happy",
        "nostalgic": "nostalgic_sad",
        "bittersweet": "nostalgic_sad",
        "sad": "nostalgic_sad",
        "exciting": "exciting_adventure",
        "adventurous": "exciting_adventure",
        "calm": "calm_reflective",
        "peaceful": "calm_reflective",
        "reflective": "calm_reflective",
        "romantic": "romantic",
        "loving": "romantic",
    }
    return mapping.get(emotion, "warm_happy")


async def generate_script(diary_text: str) -> ScriptOutput:
    response = await asyncio.to_thread(
        Generation.call,
        model="qwen-max",
        messages=[
            {"role": "system", "content": SYSTEM_PROMPT},
            {"role": "user", "content": diary_text},
        ],
        result_format="message",
        response_format={"type": "json_object"},
    )

    if response.status_code != 200:
        raise ScriptGenerationError(
            f"API调用失败: code={response.code}, message={response.message}"
        )

    try:
        raw_content = response.output.choices[0].message.content
        logger.info(f"AI raw response (first 500 chars): {raw_content[:500]}")
        data = json.loads(raw_content)
    except (json.JSONDecodeError, AttributeError, KeyError) as e:
        raise ScriptGenerationError(f"解析AI返回的JSON失败: {e}")

    if "scenes" not in data:
        raise ScriptGenerationError("AI返回的数据缺少scenes字段")

    scenes = []
    for s in data["scenes"]:
        desc = _get_field(
            s,
            "scene_description_cn", "scene_description",
            "description_cn", "description", "场景描述",
        )
        narration = _get_field(
            s,
            "narration_text_cn", "narration_text", "narration_cn",
            "narration", "旁白文字", "旁白", "旁白文本",
        )
        # Fallback: use description as narration if narration is empty
        if not narration and desc:
            narration = desc

        scenes.append(
            SceneScript(
                index=s.get("index", len(scenes) + 1),
                scene_description_cn=desc,
                narration_text_cn=narration,
                suggested_duration_s=float(s.get("suggested_duration_s", 8)),
                emotion=s.get("emotion", "warm_happy"),
                image_prompt=s.get("image_prompt", "anime style, warm atmosphere"),
            )
        )

    if not scenes:
        raise ScriptGenerationError("AI未生成任何场景")

    # Validate: at least one scene must have narration text
    if not any(s.narration_text_cn for s in scenes):
        raw_snippet = raw_content[:300]
        raise ScriptGenerationError(
            f"AI生成的所有场景旁白文本均为空，请检查AI返回的字段名是否正确。"
            f"AI原始返回(前300字符): {raw_snippet}"
        )

    overall_emotion = data.get("overall_emotion", "warm_happy")

    return ScriptOutput(
        title=data.get("title", "我的日记"),
        overall_emotion=overall_emotion,
        total_duration_suggestion=float(data.get("total_duration_suggestion", 45)),
        bgm_category=_map_emotion_to_bgm(overall_emotion),
        scenes=scenes,
    )
