import json
import os
import sys

if len(sys.argv) < 3:
    print("Usage: python build_word_blocks.py <words.json> <output.json>")
    sys.exit(1)

INPUT = sys.argv[1]
OUTPUT = sys.argv[2]

MAX_WORDS = 3
MAX_DURATION = 0.8
PAUSE_THRESHOLD = 0.18
MAX_CHARS = 18   # keep text compact (this is what you lost)

with open(INPUT, "r", encoding="utf-8") as f:
    words = json.load(f)

blocks = []
current_words = []
block_start = None
prev_end = None


def flush_block(end_time):
    global current_words, block_start
    if not current_words:
        return

    blocks.append({
        "text": " ".join(word["word"] for word in current_words),
        "start": round(block_start, 3),
        "end": round(end_time, 3)
    })
    current_words = []
    block_start = None


for i, w in enumerate(words):
    if block_start is None:
        block_start = w["start"]

    # Pause detection
    if prev_end is not None:
        gap = w["start"] - prev_end
        if gap >= PAUSE_THRESHOLD and current_words:
            flush_block(prev_end)
            block_start = w["start"]

    current_words.append(w)

    # Visual width control
    text = " ".join(word["word"] for word in current_words)
    too_wide = len(text) > MAX_CHARS

    duration = w["end"] - block_start
    too_long = duration >= MAX_DURATION
    too_many = len(current_words) >= MAX_WORDS

    if too_wide:
        overflow_word = current_words.pop()
        flush_block(prev_end)
        current_words = [overflow_word]
        block_start = overflow_word["start"]

    elif too_many or too_long:
        flush_block(w["end"])

    prev_end = w["end"]


if current_words:
    flush_block(prev_end)

os.makedirs(os.path.dirname(OUTPUT), exist_ok=True)

with open(OUTPUT, "w", encoding="utf-8") as f:
    json.dump(blocks, f, indent=2)

print(f"✅ Generated {len(blocks)} word blocks → {OUTPUT}")
