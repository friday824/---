import subprocess
from pathlib import Path


def get_video_duration(video_path: Path) -> float:
    try:
        result = subprocess.run(
            [
                "ffprobe",
                "-v", "error",
                "-show_entries", "format=duration",
                "-of", "default=noprint_wrappers=1:nokey=1",
                str(video_path),
            ],
            capture_output=True,
            text=True,
            timeout=10,
        )
        return float(result.stdout.strip())
    except Exception:
        return 0.0


def extract_thumbnail(video_path: Path, output_path: Path, at_time: float = 1.0) -> Path | None:
    try:
        subprocess.run(
            [
                "ffmpeg",
                "-y",
                "-ss", str(at_time),
                "-i", str(video_path),
                "-vframes", "1",
                "-q:v", "2",
                str(output_path),
            ],
            capture_output=True,
            timeout=15,
            check=True,
        )
        return output_path
    except Exception:
        return None
