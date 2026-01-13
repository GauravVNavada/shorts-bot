import sys
import json
import whisper

if len(sys.argv) < 3:
    print("Usage: python whisper_align.py <input_wav> <output_json>")
    sys.exit(1)

audio_path = sys.argv[1]
output_path = sys.argv[2]

print("🎧 Loading Whisper model...")
model = whisper.load_model("base")

print("🕒 Running alignment...")
result = model.transcribe(audio_path, word_timestamps=True)

words = []
for segment in result["segments"]:
    for w in segment["words"]:
        words.append({
            "word": w["word"],
            "start": round(w["start"], 3),
            "end": round(w["end"], 3)
        })

with open(output_path, "w", encoding="utf-8") as f:
    json.dump(words, f, indent=2)

print(f"✅ Word alignment written to: {output_path}")
