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
REFERENCE_VOICE = "C:/tts/reference.wav"   # adjust if needed
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

# ---------- GENERATE CHUNKS ----------
generated_files = []

for idx, chunk in enumerate(chunks):
    out_path = os.path.join(CHUNKS_DIR, f"chunk_{idx:02d}_{chunk['type']}.wav")

    print(f"Generating: {out_path}")
    tts.tts_to_file(
        text=chunk["text"],
        speaker_wav=REFERENCE_VOICE,
        language="en",
        file_path=out_path
    )

    generated_files.append(out_path)

print("🎙 Narration chunks generated.")

# ---------- MERGE CHUNKS ----------
print("🧩 Building narration from chunks...")
combined = AudioSegment.empty()

for wav in generated_files:
    print(f"➕ Adding {wav}")
    audio = AudioSegment.from_file(wav)
    combined += audio

combined.export(FINAL_AUDIO, format="wav")
print(f"✅ Narration built: {FINAL_AUDIO}")
