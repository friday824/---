import subprocess
import tempfile
from pathlib import Path

from backend.app.config import settings
from backend.app.services.script_gen import SceneScript
from backend.app.utils.exceptions import CompositorError


def _run_ffmpeg(args: list[str], timeout: int = 300) -> None:
    try:
        result = subprocess.run(
            ["ffmpeg", "-y"] + args,
            capture_output=True,
            text=True,
            timeout=timeout,
        )
        if result.returncode != 0:
            raise CompositorError(
                f"FFmpeg错误 (exit={result.returncode}): {result.stderr[-500:]}"
            )
    except subprocess.TimeoutExpired:
        raise CompositorError("视频合成超时")
    except FileNotFoundError:
        raise CompositorError("未找到FFmpeg，请确认已安装并添加到PATH")


def _create_scene_clip(
    image_path: Path,
    duration_s: float,
    output_path: Path,
) -> None:
    fps = 24
    total_frames = int(duration_s * fps)

    _run_ffmpeg([
        "-loop", "1",
        "-i", str(image_path),
        "-vf",
        f"zoompan=z='min(zoom+0.0015,1.15)':x='iw/2-(iw/zoom/2)':"
        f"y='ih/2-(ih/zoom/2)':d={total_frames}:s=1280x720:fps={fps}",
        "-t", str(duration_s),
        "-pix_fmt", "yuv420p",
        "-c:v", "libx264",
        "-preset", "fast",
        "-crf", "23",
        str(output_path),
    ])


async def composite_video(
    scenes: list[SceneScript],
    image_paths: list[Path],
    voiceover_path: Path | None,
    bgm_path: Path | None,
    task_id: str,
) -> Path:
    video_dir = settings.video_output_dir
    video_dir.mkdir(parents=True, exist_ok=True)
    output_path = video_dir / f"{task_id}.mp4"

    if not scenes or not image_paths:
        raise CompositorError("没有可合成的场景")

    with tempfile.TemporaryDirectory() as tmpdir_str:
        tmpdir = Path(tmpdir_str)

        # Step 1: Generate individual scene clips with Ken Burns effect
        clip_paths = []
        for i, (scene, img_path) in enumerate(zip(scenes, image_paths)):
            if not Path(img_path).exists():
                continue
            clip_path = tmpdir / f"clip_{i:02d}.mp4"
            dur = max(scene.suggested_duration_s, 3.0)
            _create_scene_clip(Path(img_path), dur, clip_path)
            clip_paths.append((clip_path, dur, scene.narration_text_cn))

        if not clip_paths:
            raise CompositorError("没有成功生成的场景片段")

        # Step 2: Build concat file
        concat_file = tmpdir / "concat.txt"

        with open(concat_file, "w", encoding="utf-8") as f:
            for clip_path, dur, _ in clip_paths:
                f.write(f"file '{clip_path.as_posix()}'\n")
                f.write(f"duration {dur}\n")

        # Step 3: Create subtitle file
        subtitle_file = tmpdir / "subtitles.ass"
        _write_subtitles_ass(clip_paths, subtitle_file)

        # Step 4: Determine audio inputs
        audio_inputs = []
        audio_filter_parts = []

        if voiceover_path and voiceover_path.exists():
            audio_inputs.extend(["-i", str(voiceover_path)])
            audio_filter_parts.append("[1:a]")

        if bgm_path and bgm_path.exists():
            idx = 2 if (voiceover_path and voiceover_path.exists()) else 1
            audio_inputs.extend(["-i", str(bgm_path)])
            if audio_filter_parts:
                audio_filter_parts.append(f"[{idx}:a]volume=0.25[a2];")
                audio_filter_parts.append("[a1][a2]amix=inputs=2:duration=longest:normalize=0[amix]")
            else:
                audio_filter_parts.append(f"[{idx}:a]volume=0.4[amix]")

        # Step 5: Composite everything
        cmd = [
            "-f", "concat",
            "-safe", "0",
            "-i", str(concat_file),
        ]

        if audio_inputs:
            cmd.extend(audio_inputs)

        escaped_sub_path = subtitle_file.as_posix().replace(":", "\\:")
        cmd.extend([
            "-vf", f"ass={escaped_sub_path}",
            "-c:v", "libx264",
            "-preset", "medium",
            "-crf", "20",
            "-pix_fmt", "yuv420p",
            "-c:a", "aac",
            "-b:a", "192k",
            "-shortest",
            str(output_path),
        ])

        # For audio filter, we need a different approach - handle via filter_complex
        if voiceover_path and voiceover_path.exists():
            # Build a filter_complex for both video subtitles and audio mixing
            cmd = _build_complex_command(
                concat_file, clip_paths, voiceover_path, bgm_path,
                subtitle_file, output_path
            )

        _run_ffmpeg(cmd, timeout=300)

    return output_path


def _build_complex_command(
    concat_file: Path,
    clip_paths: list,
    voiceover_path: Path | None,
    bgm_path: Path | None,
    subtitle_file: Path,
    output_path: Path,
) -> list[str]:
    cmd = [
        "-f", "concat",
        "-safe", "0",
        "-i", str(concat_file),
        "-i", str(voiceover_path),
    ]

    escaped_sub_path = subtitle_file.as_posix().replace(":", "\\\\:")
    filter_parts = ["[0:v]ass={}:alpha=1[v]".format(escaped_sub_path)]

    if bgm_path and bgm_path.exists():
        cmd.extend(["-i", str(bgm_path)])
        filter_parts.append("[2:a]volume=0.25[bgm];")
        filter_parts.append("[1:a][bgm]amix=inputs=2:duration=longest[outa]")
    else:
        filter_parts.append("[1:a]anull[outa]")

    cmd.extend([
        "-filter_complex", ";".join(filter_parts),
        "-map", "[v]",
        "-map", "[outa]",
        "-c:v", "libx264",
        "-preset", "medium",
        "-crf", "20",
        "-pix_fmt", "yuv420p",
        "-c:a", "aac",
        "-b:a", "192k",
        "-shortest",
        str(output_path),
    ])

    return cmd


def _write_subtitles_ass(
    clip_paths: list, output_path: Path
) -> None:
    lines = [
        "[Script Info]",
        "ScriptType: v4.00+",
        "PlayResX: 1280",
        "PlayResY: 720",
        "ScaledBorderAndShadow: yes",
        "",
        "[V4+ Styles]",
        "Format: Name, Fontname, Fontsize, PrimaryColour, SecondaryColour, "
        "OutlineColour, BackColour, Bold, Italic, Underline, StrikeOut, "
        "ScaleX, ScaleY, Spacing, Angle, BorderStyle, Outline, Shadow, "
        "Alignment, MarginL, MarginR, MarginV, Encoding",
        (
            "Style: Default,Noto Sans SC,26,&H00FFFFFF,&H00000000,"
            "&H00000000,&H80000000,0,0,0,0,100,100,0,0,1,2.5,1.5,"
            "2,40,40,40,1"
        ),
        "",
        "[Events]",
        "Format: Layer, Start, End, Style, Name, MarginL, MarginR, "
        "MarginV, Effect, Text",
    ]

    current_time = 0.0
    for _, dur, narration in clip_paths:
        start = current_time
        end = start + dur

        subtitle_lines = _split_subtitle_text(narration)
        sub_duration = (end - start) / len(subtitle_lines)

        for j, sub_line in enumerate(subtitle_lines):
            sub_start = start + j * sub_duration
            sub_end = sub_start + sub_duration
            start_str = _seconds_to_ass_time(sub_start)
            end_str = _seconds_to_ass_time(sub_end)
            lines.append(
                f"Dialogue: 0,{start_str},{end_str},Default,,0,0,0,,{sub_line}"
            )

        current_time = end

    output_path.write_text("\n".join(lines), encoding="utf-8")


def _split_subtitle_text(text: str) -> list[str]:
    """Split long text into subtitle-friendly chunks."""
    if len(text) <= 30:
        return [text]

    chunks = []
    remaining = text
    while remaining:
        if len(remaining) <= 30:
            chunks.append(remaining)
            break
        split_at = remaining.rfind("，", 0, 30)
        if split_at == -1:
            split_at = remaining.rfind("。", 0, 30)
        if split_at == -1:
            split_at = remaining.rfind("、", 0, 30)
        if split_at == -1 or split_at < 10:
            split_at = 25
        chunks.append(remaining[: split_at + 1])
        remaining = remaining[split_at + 1 :]

    return chunks if chunks else [text]


def _seconds_to_ass_time(seconds: float) -> str:
    h = int(seconds // 3600)
    m = int((seconds % 3600) // 60)
    s = seconds % 60
    return f"{h:01d}:{m:02d}:{s:05.2f}"
