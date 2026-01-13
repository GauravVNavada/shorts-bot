import subprocess
import json
import os
import textwrap
import random
import sys


GAMEPLAY = "assets/gameplay/subway.mp4"

WIDTH = 1080
HEIGHT = 1920
FPS = 30

FONT = "assets/fonts/KOMIKAX_.ttf"


# ----------------- helpers -----------------

def ffmpeg_escape(text: str) -> str:
    return (
        text.replace("\\", r"\\")
            .replace(":", r"\:")
            .replace("'", r"\'")
            .replace(",", r"\,")
    )


def wrap_text(text, max_chars=18):
    return "\n".join(textwrap.wrap(text, max_chars))


def get_audio_duration(audio_path):
    cmd = [
        "ffprobe", "-v", "error",
        "-show_entries", "format=duration",
        "-of", "default=noprint_wrappers=1:nokey=1",
        audio_path
    ]

    result = subprocess.run(cmd, capture_output=True, text=True)
    output = result.stdout.strip()

    if not output:
        raise RuntimeError(
            f"❌ Could not read audio duration with ffprobe.\n"
            f"STDERR: {result.stderr}\n"
            f"PATH: {audio_path}"
        )

    return float(output)


def get_video_duration(path):
    result = subprocess.run(
        ["ffprobe", "-v", "error", "-show_entries",
         "format=duration", "-of",
         "default=noprint_wrappers=1:nokey=1", path],
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
        text=True
    )
    return float(result.stdout.strip())


# ----------------- BASE BLOCKS -----------------

def build_drawtext_filters(blocks):
    filters = []

    for block in blocks:
        raw_text = block["text"]
        text = ffmpeg_escape(wrap_text(raw_text))

        start = block["start"]
        end = block["end"]

        filters.append(
            "drawtext="
            f"text='{text}':"
            f"fontfile={FONT}:"
            "fontcolor=white:"
            "fontsize=96:"
            "line_spacing=10:"
            "box=1:"
            "boxcolor=black@0.55:"
            "boxborderw=24:"
            "borderw=2:bordercolor=black:"
            "x=(w-text_w)/2:"
            "y=(h*0.50-text_h/2):"
            f"enable='between(t\\,{start}\\,{end})'"
        )

    return ",".join(filters)


# ----------------- RENDER -----------------

def render_video(audio_path, captions_path, output_path):
    print("🎞 Rendering video...")
    os.makedirs(os.path.dirname(output_path), exist_ok=True)

    # Load captions
    with open(captions_path, "r", encoding="utf-8") as f:
        blocks = json.load(f)

    block_layer = build_drawtext_filters(blocks)

    # Get durations
    audio_duration = get_audio_duration(audio_path)
    video_duration = get_video_duration(GAMEPLAY)

    max_start = max(0, video_duration - audio_duration)
    start_time = random.uniform(0, max_start)

    print(f"🎮 Using gameplay from {start_time:.2f}s for {audio_duration:.2f}s")

    vf = (
        f"scale={WIDTH}:{HEIGHT}:force_original_aspect_ratio=increase,"
        f"crop={WIDTH}:{HEIGHT},"
        f"{block_layer}"
    )

    cmd = [
        "ffmpeg",
        "-y",
        "-ss", str(start_time),
        "-i", GAMEPLAY,
        "-i", audio_path,
        "-t", str(audio_duration),
        "-map", "0:v:0",
        "-map", "1:a:0",
        "-vf", vf,
        "-r", str(FPS),
        "-c:v", "libx264",
        "-c:a", "aac",
        "-b:a", "192k",
        "-pix_fmt", "yuv420p",
        output_path
    ]

    subprocess.run(cmd, check=True)
    print("✅ Video rendered:", output_path)


if __name__ == "__main__":
    if len(sys.argv) < 4:
        print("Usage: python render.py <audio_path> <captions_path> <output_path>")
        sys.exit(1)

    audio_path = sys.argv[1]
    captions_path = sys.argv[2]
    output_path = sys.argv[3]

    render_video(audio_path, captions_path, output_path)
