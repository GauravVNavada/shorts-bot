# SHORTS_BOT_PLAN.md

## Purpose
This document is the single source of truth for the Shorts automation project.
It exists so that future work can resume **without rethinking or re-explaining**
decisions already made.

If you are continuing this project:
- DO NOT redo completed steps
- DO NOT prematurely optimize deferred items
- Resume work strictly from the “DEFERRED (FIX LATER)” section, in order

---

## PROJECT GOAL (LOCKED)

Build a **fully local, automated Shorts pipeline** that:
- Generates scripts
- Generates high-quality, consistent voiceover (XTTS-v2)
- Renders short-form videos
- Is scalable and automation-friendly
- Does NOT rely on paid APIs in daily operation

Voice quality goal:
- Consistent pacing
- Clear pronunciation
- Confident “internet narrator” energy
- Not identical to ElevenLabs Adam, but **stylistically comparable**

---

## DONE (DO NOT REVISIT)

These items are complete and working.  
Do not refactor or “improve” them unless explicitly stated later.

### Environment & Models
- Python virtual environment created (`C:\tts\venv`)
- GPU setup verified (GTX 1650 working)
- PyTorch downgraded to XTTS-compatible version (2.1.2 + CUDA 11.8)
- Coqui TTS installed successfully
- XTTS-v2 model loaded and verified
- Transformers pinned to compatible version (4.30.2)

### Voice System
- XTTS-v2 confirmed working locally
- Reference voice created using **ElevenLabs Adam (one-time use)**
- Reference audio stored as `reference.wav`
- Voice cloning via XTTS-v2 confirmed successful
- Chunked audio generation implemented to avoid VRAM crashes

### Current Audio Quality State
- Pronunciation: mostly correct
- Pacing: controllable
- Consistency: achieved
- Output: acceptable for now

---

## ACCEPTED AS-IS (TEMPORARY, INTENTIONAL)

These issues are **known and accepted** for now.
They are NOT bugs — they are deferred polish.

- Noticeable silence gaps between sentences
- Slight crackly / grainy audio texture
- Energy not fully optimized
- Audio stitching is functional but naive
- No loudness normalization yet

These are postponed to avoid rework.
Do NOT attempt to “quick-fix” them ad hoc.

---

## DEFERRED (FIX LATER — STRICT ORDER)

⚠️ IMPORTANT  
Work on these ONLY after the current phase is complete.
Follow the order exactly.

---

### 1️⃣ AUDIO POST-PROCESSING (FIRST PRIORITY)

Goal: clean, broadcast-safe audio with controlled rhythm.

Tasks:
- Trim trailing silence from each XTTS chunk
- Add controlled pauses (≈120–180 ms)
- Variable pause length based on intent (hook vs lore vs punchline)
- Loudness normalization (LUFS-based)
- Peak limiting to prevent clipping
- Micro crossfade (5–10 ms) between chunks
- Optional very light smoothing (NO aggressive denoise)

Rule:
> render.py must not decide *why* audio is shaped — only *how*

---

### 2️⃣ ENERGY TUNING

Goal: improve perceived hype without changing the voice model.

Tasks:
- Define sentence roles:
  - Hook
  - Lore
  - Punchline
- Control rhythm via structure, not punctuation
- Avoid long monotone sequences
- Energy comes from script flow, not TTS parameters

---

### 3️⃣ SCRIPT TRANSFORMER

Goal: remove human inconsistency from script input.

Build a transformer that converts:
Raw human script
→ XTTS-ready chunks


Responsibilities:
- Expand contractions (don’t → do not)
- Split sentences intelligently
- Insert pause markers
- Capitalize emphasis words
- Output chunk list suitable for XTTS

This must be deterministic and reusable.

---

### 4️⃣ CLEAN AUTOMATION HOOK

Goal: one clean function that handles all audio rendering.

Design:
- Single `render_audio()` or equivalent
- Steps:
  1. Receive script
  2. Transform script (via transformer)
  3. Generate XTTS chunks
  4. Apply post-processing
  5. Output final WAV

Rules:
- No scattered logic
- No hardcoded hacks
- Easy to extend later

---

## IMPORTANT CONSTRAINTS (DO NOT BREAK)

- XTTS-v2 must remain local and free
- ElevenLabs must NOT be used in daily generation
- GTX 1650 VRAM constraints must be respected
- Chunked generation is mandatory
- render.py must consume a “recipe”, not make creative decisions

---

## HOW TO RESUME THIS PROJECT LATER

If you are returning after a break, do this:

1. Read this file fully
2. Ignore the DONE section
3. Ignore ACCEPTED AS-IS
4. Resume at:
   **DEFERRED → Step 1 (Audio Post-Processing)**

If unsure:
> “Let’s do the deferred audio fixes now.”

That is the correct re-entry point.

---

## FINAL NOTE

This project prioritizes:
- clarity over speed
- structure over hacks
- consistency over novelty

Do not rush polish.
Finish systems first.

