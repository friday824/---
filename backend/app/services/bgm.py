import json
import random
import subprocess
from pathlib import Path

from backend.app.config import settings

BGM_CATEGORIES = [
    "warm_happy",
    "nostalgic_sad",
    "exciting_adventure",
    "calm_reflective",
    "romantic",
]


def select_and_prepare_bgm(
    emotion: str, target_duration_s: float, task_id: str
) -> Path | None:
    category = emotion if emotion in BGM_CATEGORIES else "warm_happy"
    bgm_dir = settings.bgm_library_dir / category

    if not bgm_dir.exists():
        return None

    audio_files = list(bgm_dir.glob("*.mp3")) + list(bgm_dir.glob("*.wav"))
    if not audio_files:
        return None

    source = random.choice(audio_files)
    output_dir = settings.audio_output_dir
    output_dir.mkdir(parents=True, exist_ok=True)
    output_path = output_dir / f"{task_id}_bgm_prepared.mp3"

    target_duration_s = max(target_duration_s, 5.0)

    try:
        subprocess.run(
            [
                "ffmpeg",
                "-y",
                "-stream_loop", "-1",
                "-i", str(source),
                "-t", str(target_duration_s + 2),
                "-af", "afade=t=in:d=1,afade=t=out:st={}:d=2".format(
                    max(target_duration_s - 2, 1)
                ),
                "-q:a", "2",
                str(output_path),
            ],
            capture_output=True,
            timeout=30,
            check=True,
        )
        return output_path
    except (subprocess.CalledProcessError, subprocess.TimeoutExpired):
        return None
