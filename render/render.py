import os
import json
import sys
import random

import numpy as np
from PIL import Image, ImageDraw, ImageFont

from moviepy import (
    VideoFileClip,
    AudioFileClip,
    CompositeVideoClip,
    ImageClip,
)

# ---------------- CONFIG ----------------
GAMEPLAY = "assets/gameplay/subway.mp4"
WIDTH = 1080
HEIGHT = 1920
FPS = 30

FONT_PATH = "assets/fonts/KOMIKAX_.ttf"
FONT_SIZE = 96

TEXT_COLOR = "#FFFFFF"
EMPHASIS_COLOR = "#FFD54F"
STROKE_COLOR = "#000000"
STROKE_WIDTH = 4

PAD_X = 40
PAD_Y = 40
LINE_GAP = 6

SAFE_TEXT_WIDTH = int(WIDTH * 0.92)  # 🔒 hard safety clamp


# ---------------- HELPERS ----------------

def load_blocks(path):
    with open(path, "r", encoding="utf-8") as f:
        return json.load(f)

def get_video_duration(path):
    clip = VideoFileClip(path)
    dur = clip.duration
    clip.close()
    return dur


# ---------------- CAPTION CLIP ----------------

def make_caption_clip(words, start, end, do_pop):
    font = ImageFont.truetype(FONT_PATH, FONT_SIZE)

    dummy = Image.new("RGBA", (10, 10))
    d = ImageDraw.Draw(dummy)

    full_line = " ".join(w["text"] for w in words)
    bbox = d.textbbox((0, 0), full_line, font=font, stroke_width=STROKE_WIDTH)

    text_w = bbox[2] - bbox[0]
    text_h = bbox[3] - bbox[1]

    img = Image.new(
        "RGBA",
        (text_w + PAD_X * 2, text_h + PAD_Y * 2),
        (0, 0, 0, 0),
    )

    draw = ImageDraw.Draw(img)

    x = PAD_X
    y = PAD_Y

    for token in words:
        word = token["text"]
        is_emph = token.get("emphasis", False)

        color = EMPHASIS_COLOR if is_emph else TEXT_COLOR

        draw.text(
            (x, y),
            word + " ",
            font=font,
            fill=color,
            stroke_fill=STROKE_COLOR,
            stroke_width=STROKE_WIDTH,
        )

        x += font.getlength(word + " ")

    clip = ImageClip(np.array(img))

    # 🔒 FIX: SCALE DOWN IF TOO WIDE (NO REWRAP, NO SPACING CHANGES)
    if clip.w > SAFE_TEXT_WIDTH:
        scale = SAFE_TEXT_WIDTH / clip.w
        clip = clip.resized(scale)

    # ---- POSITION (LOCKED SAFE CENTER) ----
    def settle_y(t):
        if t < 0.10:
            return -2 * (1 - t / 0.10)
        return 0

    clip = clip.with_position(lambda t: ("center", HEIGHT // 2 + settle_y(t)))

    # ---- POP (SAFE) ----
    if do_pop:
        clip = clip.resized(lambda t: 0.85 + min(t / 0.15, 1) * 0.15)

    return clip.with_start(start).with_end(end)


# ---------------- RENDER ----------------

def render_video(audio_path, captions_path, output_path):
    print("🎞 Rendering video with MoviePy...")
    os.makedirs(os.path.dirname(output_path), exist_ok=True)

    blocks = load_blocks(captions_path)

    audio = AudioFileClip(audio_path)
    audio_duration = audio.duration

    video_duration = get_video_duration(GAMEPLAY)
    start_time = random.uniform(0, max(0, video_duration - audio_duration))

    base_video = (
        VideoFileClip(GAMEPLAY)
        .subclipped(start_time, start_time + audio_duration)
        .resized((WIDTH, HEIGHT))
        .with_fps(FPS)
        .with_audio(audio)
    )

    caption_clips = []
    prev_end = None

    for block in blocks:
        start = float(block["start"])
        end = float(block["end"])
        words = block["words"]

        do_pop = True
        if prev_end is not None and start - prev_end < 0.30:
            do_pop = False

        caption_clips.append(
            make_caption_clip(words, start, end, do_pop)
        )

        prev_end = end

    final = CompositeVideoClip(
        [base_video] + caption_clips,
        size=(WIDTH, HEIGHT),
    )

    final.write_videofile(
        output_path,
        codec="libx264",
        audio_codec="aac",
        fps=FPS,
        threads=4,
        preset="medium",
    )

    final.close()
    audio.close()
    print("✅ Video rendered:", output_path)


# ---------------- ENTRY ----------------

if __name__ == "__main__":
    if len(sys.argv) < 4:
        print("Usage: python render.py <audio_path> <captions_path> <output_path>")
        sys.exit(1)

    render_video(sys.argv[1], sys.argv[2], sys.argv[3])
