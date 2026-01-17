import json
import os
import sys

if len(sys.argv) < 4:
    print("Usage: python build_word_blocks.py <words.json> <ideas.json> <output.json>")
    sys.exit(1)

WORDS_PATH = sys.argv[1]
IDEAS_PATH = sys.argv[2]
OUTPUT_PATH = sys.argv[3]

MAX_WORDS = 3
MAX_DURATION = 0.8
PAUSE_THRESHOLD = 0.18
MAX_CHARS = 18


# ---------------- HELPERS ----------------

def normalize(w: str) -> str:
    return w.lower().strip(".,!?\"'")


# ---------------- LOAD INPUTS ----------------

with open(WORDS_PATH, "r", encoding="utf-8") as f:
    words = json.load(f)

with open(IDEAS_PATH, "r", encoding="utf-8") as f:
    ideas = json.load(f)

# Pick the *pending* idea (this is important)
idea = None
for v in ideas.values():
    if v.get("status") == "pending":
        idea = v
        break

if idea is None:
    # fallback: last idea
    idea = list(ideas.values())[-1]

captions_cfg = idea.get("captions", {})
emphasis_cfg = captions_cfg.get("emphasis", {}) if captions_cfg.get("highlight_emphasis") else {}

EMPHASIS_WORDS = {normalize(w) for w in emphasis_cfg.keys()}

print("🎨 Emphasis source words:", EMPHASIS_WORDS)


# ---------------- BUILD BLOCKS ----------------

blocks = []
current = []
block_start = None
prev_end = None


def flush(end_time):
    global current, block_start
    if not current:
        return

    blocks.append({
        "words": current.copy(),
        "start": round(block_start, 3),
        "end": round(end_time, 3)
    })

    current.clear()
    block_start = None


for w in words:
    raw_word = w["word"]
    start = w["start"]
    end = w["end"]

    if block_start is None:
        block_start = start

    # Pause detection
    if prev_end is not None:
        gap = start - prev_end
        if gap >= PAUSE_THRESHOLD and current:
            flush(prev_end)
            block_start = start

    token = normalize(raw_word)

    is_emphasis = any(
        ew in normalize(raw_word)
        for ew in EMPHASIS_WORDS
    )


    current.append({
        "text": raw_word,
        "emphasis": is_emphasis
    })

    # Debug visibility (IMPORTANT)
    if is_emphasis:
        print(f"⭐ Emphasis matched: '{raw_word}' at {start:.2f}s")

    # Width / duration / count constraints
    text_len = sum(len(x["text"]) for x in current) + len(current) - 1
    duration = end - block_start

    if (
        text_len > MAX_CHARS or
        duration >= MAX_DURATION or
        len(current) >= MAX_WORDS
    ):
        flush(end)

    prev_end = end


if current:
    flush(prev_end)


# ---------------- WRITE OUTPUT ----------------

os.makedirs(os.path.dirname(OUTPUT_PATH), exist_ok=True)

with open(OUTPUT_PATH, "w", encoding="utf-8") as f:
    json.dump(blocks, f, indent=2)

print(f"✅ Generated {len(blocks)} caption blocks → {OUTPUT_PATH}")
