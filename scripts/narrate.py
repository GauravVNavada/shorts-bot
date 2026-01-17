import sys
import os
import json
from TTS.api import TTS
from transformer import transform_script
from pydub import AudioSegment

# ---------- USAGE ----------
# python narrate.py <script_path> <job_intermediate_dir>

if len(sys.argv) < 3:
    print("Usage: python narrate.py <script_path> <job_intermediate_dir>")
    sys.exit(1)

SCRIPT_PATH = sys.argv[1]
JOB_DIR = sys.argv[2]

# ---------- CONFIG ----------
REFERENCE_VOICE = "C:/tts/reference.wav"
MODEL_NAME = "tts_models/multilingual/multi-dataset/xtts_v2"

CHUNKS_DIR = os.path.join(JOB_DIR, "audio_chunks")
FINAL_AUDIO = os.path.join(JOB_DIR, "narration.wav")

os.makedirs(CHUNKS_DIR, exist_ok=True)

# ---------- LOAD TTS ----------
tts = TTS(
    model_name=MODEL_NAME,
    gpu=True
)

# ---------- LOAD SCRIPT ----------
with open(SCRIPT_PATH, "r", encoding="utf-8") as f:
    raw_script = f.read()

# ---------- TRANSFORM SCRIPT ----------
chunks = transform_script(raw_script)

# ---------- BUILD FULL TEXT ----------
text_parts = []
for chunk in chunks:
    t = chunk["text"].strip()
    if t:
        text_parts.append(t)

full_text = " ".join(text_parts)

# ---------- SPLIT INTO SENTENCES (LOW MEMORY, NATURAL FLOW) ----------
sentences = [s.strip() for s in full_text.split(".") if s.strip()]

print(f"🎙 Generating narration using {len(sentences)} sentences...")

combined = AudioSegment.empty()

for idx, sentence in enumerate(sentences):
    out_path = os.path.join(CHUNKS_DIR, f"sent_{idx:02d}.wav")

    print(f"Generating: {out_path}")
    tts.tts_to_file(
        text=sentence + ".",
        speaker_wav=REFERENCE_VOICE,
        language="en",
        file_path=out_path
    )

    audio = AudioSegment.from_file(out_path)
    combined += audio
    combined += AudioSegment.silent(duration=200)  # small natural pause

print("🎙 Narration segments generated.")

# ---------- EXPORT FINAL AUDIO ----------
combined.export(FINAL_AUDIO, format="wav")
print(f"✅ Narration built: {FINAL_AUDIO}")
