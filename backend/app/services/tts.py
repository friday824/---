import asyncio
import io
import logging
import re
import wave
from pathlib import Path

import httpx
from dashscope.audio.http_tts.http_speech_synthesizer import HttpSpeechSynthesizer

from backend.app.config import settings
from backend.app.services.script_gen import SceneScript
from backend.app.utils.exceptions import TTSError

logger = logging.getLogger(__name__)

MAX_CHARS_PER_TTS_CALL = 200


def _clean_text(text: str) -> str:
    """Normalize text for CosyVoice: remove emoji, convert English punctuation to Chinese."""
    text = text.strip()
    # 英文标点转中文标点
    text = text.replace(",", "，").replace(":", "：").replace(";", "；")
    text = text.replace("!", "！").replace("?", "？").replace("(", "（").replace(")", "）")
    # 去掉多余空白
    text = re.sub(r"\s+", "", text)
    return text


def _split_text(text: str, max_chars: int = MAX_CHARS_PER_TTS_CALL) -> list[str]:
    """Split text at sentence boundaries, keeping each chunk under max_chars."""
    text = _clean_text(text)
    sentences = re.split(r"(?<=[。！？；\n])\s*", text)
    chunks: list[str] = []
    current: str = ""

    for sentence in sentences:
        sentence = sentence.strip()
        if not sentence:
            continue
        if len(current) + len(sentence) <= max_chars:
            current += sentence
        else:
            if current:
                chunks.append(current)
            # 单句超限则强制截断
            if len(sentence) > max_chars:
                sentence = sentence[:max_chars]
            current = sentence

    if current:
        chunks.append(current)

    return chunks if chunks else [text]


def _concat_wav_files(wav_data_list: list[bytes]) -> bytes:
    """Concatenate multiple WAV files into one."""
    if len(wav_data_list) == 1:
        return wav_data_list[0]

    merged = io.BytesIO()
    params = None
    total_frames = 0

    for data in wav_data_list:
        with wave.open(io.BytesIO(data), "rb") as wf:
            if params is None:
                params = wf.getparams()
            total_frames += wf.getnframes()

    with wave.open(merged, "wb") as out:
        out.setparams(params)
        for data in wav_data_list:
            with wave.open(io.BytesIO(data), "rb") as wf:
                out.writeframes(wf.readframes(wf.getnframes()))

    return merged.getvalue()


async def _tts_single(text: str, retries: int = 2) -> bytes:
    """Call CosyVoice TTS for a single chunk of text, with retry on transient failures."""
    if not text.strip():
        raise TTSError("TTS输入文本为空")

    last_error: Exception | None = None

    logger.info(f"TTS request: text_len={len(text)}, preview={text[:80]}...")

    for attempt in range(retries + 1):
        try:
            result = await asyncio.to_thread(
                HttpSpeechSynthesizer.call,
                model="cosyvoice-v3-plus",
                text=text,
                voice="longanhuan",
                format="wav",
                sample_rate=24000,
                volume=50,
                rate=0.95,
                pitch=1.0,
                stream=False,
                api_key=settings.dashscope_api_key,
            )

            audio_url = result.audio_url
            if not audio_url:
                raise TTSError("TTS未返回音频URL")

            async with httpx.AsyncClient(timeout=60.0) as client:
                resp = await client.get(audio_url, follow_redirects=True)
                if resp.status_code != 200:
                    raise TTSError(f"下载配音音频失败: HTTP {resp.status_code}")

            return resp.content

        except Exception as e:
            last_error = e
            logger.warning(
                f"TTS attempt {attempt + 1}/{retries + 1} failed: "
                f"text_len={len(text)}, text={text[:120]}, error={e}"
            )
            if attempt < retries:
                await asyncio.sleep(1.0 * (attempt + 1))

    raise TTSError(
        f"配音合成失败(len={len(text)}, preview={text[:60]}...): {last_error}"
    )


def _get_wav_duration(data: bytes) -> float:
    with wave.open(io.BytesIO(data), "rb") as wf:
        return wf.getnframes() / float(wf.getframerate())


async def generate_voiceover(
    scenes: list[SceneScript], task_id: str
) -> tuple[Path, float]:
    full_narration = "  ".join(
        s.narration_text_cn for s in scenes if s.narration_text_cn.strip()
    )

    if not full_narration.strip():
        raise TTSError("旁白文本为空")

    chunks = _split_text(full_narration)
    logger.info(f"TTS: narration split into {len(chunks)} chunk(s) for task {task_id}")

    wav_data_list: list[bytes] = []
    for i, chunk in enumerate(chunks):
        logger.info(f"TTS chunk {i+1}/{len(chunks)}: {len(chunk)} chars")
        try:
            data = await _tts_single(chunk)
            wav_data_list.append(data)
        except Exception as e:
            raise TTSError(
                f"配音合成失败(片段{i+1}/{len(chunks)}, "
                f"len={len(chunk)}, text={chunk[:80]}...): {e}"
            )

    combined = _concat_wav_files(wav_data_list)

    audio_dir = settings.audio_output_dir
    audio_dir.mkdir(parents=True, exist_ok=True)
    audio_path = audio_dir / f"{task_id}_voiceover.wav"
    audio_path.write_bytes(combined)

    audio_duration_s = _get_wav_duration(combined)
    return audio_path, audio_duration_s
