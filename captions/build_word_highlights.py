import json
import os

WORDS = "alignment/words.json"
BLOCKS = "captions/word_blocks.json"
OUTPUT = "captions/word_highlights.json"

with open(WORDS, "r", encoding="utf-8") as f:
    words = json.load(f)

with open(BLOCKS, "r", encoding="utf-8") as f:
    blocks = json.load(f)

highlights = []

word_idx = 0

for block in blocks:
    block_words = []
    block_start = block["start"]
    block_end = block["end"]

    while word_idx < len(words):
        w = words[word_idx]
        if w["start"] >= block_start and w["end"] <= block_end:
            block_words.append(w)
            word_idx += 1
        elif w["start"] > block_end:
            break
        else:
            word_idx += 1

    for i, w in enumerate(block_words):
        highlights.append({
            "full_text": block["text"],
            "highlight": w["word"],
            "start": round(w["start"], 3),
            "end": round(w["end"], 3)
        })

os.makedirs("captions", exist_ok=True)

with open(OUTPUT, "w", encoding="utf-8") as f:
    json.dump(highlights, f, indent=2)

print(f"Generated {len(highlights)} word highlights → {OUTPUT}")
