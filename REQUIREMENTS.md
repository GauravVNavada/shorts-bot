# REQUIREMENTS.md

## Project Name
Shorts Bot — Local, Automated, Scalable Shorts Generator

---

## 1. Vision & Goal

The goal of this project is to build a **fully automated short-form video generation system** that runs **locally**, is **free to operate**, and can scale to multiple daily uploads.

The system should:
- Generate engaging short-form content (20–30 seconds)
- Target high-retention, rewatchable formats
- Be automation-friendly (one-click / scheduled)
- Improve over time using performance feedback
- Avoid reliance on paid APIs for daily operation

This is not a toy project.  
This is a **production-grade content automation pipeline**.

---

## 2. Content Strategy (Locked)

### Style
**Aggressive Informational Brainrot**
- Real facts
- High-stakes, fast-paced delivery
- Addictive but meaningful
- Makes viewers think “wait, what?” and keep watching

### Initial Content Types
1. Physics / Science explainers
2. “Sus History” stories
3. Mini IQ tests / riddles

### Audience
- Primary: US audience
- Secondary: global English-speaking
- Optimized for retention, loops, and shorts algorithms

---

## 3. Core Constraints (Non-Negotiable)

- Must run **locally**
- Must be **free for daily operation**
- GPU available: GTX 1650 (limited VRAM)
- Internet usage should be minimal
- Chunked processing is required to avoid crashes
- Paid tools may be used **only once** (e.g., voice reference)

---

## 4. System Overview (High-Level Flow)

User clicks “run” (or scheduled trigger)
↓
Script Generator (LLM-assisted)
↓
Script Transformer (deterministic)
↓
Voice Generation (XTTS-v2)
↓
Audio Post-Processing
↓
Video Rendering (gameplay + captions + audio)
↓
Upload (YouTube Shorts / Instagram Reels)
↓
Performance Metrics Collected
↓
Patterns fed back into script generation


---

## 5. Components & Responsibilities

### 5.1 Script Generator
- Produces raw human-readable scripts
- Focuses on story, hook, pacing, clarity
- Does NOT handle technical constraints

Source:
- ChatGPT (manual or automated)
- Local prompts/templates

---

### 5.2 Script Transformer (Planned)

Purpose:
Convert raw scripts into **machine-ready narration chunks**

Responsibilities:
- Split into logical sentences
- Expand contractions
- Insert emphasis markers
- Insert pause intent (not timing)
- Output structured chunks

This ensures consistency and prevents human error.

---

### 5.3 Voice System (Implemented)

Model:
- XTTS-v2 (Coqui TTS)
- Local inference
- GPU-enabled
- Reference-based voice cloning

Requirements:
- Consistent male voice
- Clear pronunciation
- Stable pacing
- Natural emphasis

Notes:
- ElevenLabs used ONCE to generate reference.wav
- No paid TTS used in production

---

### 5.4 Audio Post-Processing (Deferred but Planned)

Purpose:
Improve clarity, pacing, and polish without changing the voice model.

Planned fixes:
- Trim trailing silence per chunk
- Controlled pauses (120–180 ms)
- Loudness normalization (LUFS)
- Peak limiting
- Micro crossfades (5–10 ms)
- Optional light smoothing

Important rule:
> Audio logic decides *how*, not *why*.

---

### 5.5 Video Renderer (Planned)

Inputs:
- Final audio WAV
- Gameplay video (Subway Surfers, Minecraft, GTA, etc.)
- Caption text

Rules:
- Gameplay is background
- Captions on top of gameplay
- No mid-video layout switching
- Automation-friendly structure

Renderer:
- FFmpeg-based
- Recipe-driven (JSON instructions)
- Deterministic output

---

### 5.6 Asset System

Assets are stored locally and categorized:


---

## 5. Components & Responsibilities

### 5.1 Script Generator
- Produces raw human-readable scripts
- Focuses on story, hook, pacing, clarity
- Does NOT handle technical constraints

Source:
- ChatGPT (manual or automated)
- Local prompts/templates

---

### 5.2 Script Transformer (Planned)

Purpose:
Convert raw scripts into **machine-ready narration chunks**

Responsibilities:
- Split into logical sentences
- Expand contractions
- Insert emphasis markers
- Insert pause intent (not timing)
- Output structured chunks

This ensures consistency and prevents human error.

---

### 5.3 Voice System (Implemented)

Model:
- XTTS-v2 (Coqui TTS)
- Local inference
- GPU-enabled
- Reference-based voice cloning

Requirements:
- Consistent male voice
- Clear pronunciation
- Stable pacing
- Natural emphasis

Notes:
- ElevenLabs used ONCE to generate reference.wav
- No paid TTS used in production

---

### 5.4 Audio Post-Processing (Deferred but Planned)

Purpose:
Improve clarity, pacing, and polish without changing the voice model.

Planned fixes:
- Trim trailing silence per chunk
- Controlled pauses (120–180 ms)
- Loudness normalization (LUFS)
- Peak limiting
- Micro crossfades (5–10 ms)
- Optional light smoothing

Important rule:
> Audio logic decides *how*, not *why*.

---

### 5.5 Video Renderer (Planned)

Inputs:
- Final audio WAV
- Gameplay video (Subway Surfers, Minecraft, GTA, etc.)
- Caption text

Rules:
- Gameplay is background
- Captions on top of gameplay
- No mid-video layout switching
- Automation-friendly structure

Renderer:
- FFmpeg-based
- Recipe-driven (JSON instructions)
- Deterministic output

---

### 5.6 Asset System

Assets are stored locally and categorized:

assets/
├── gameplay/
├── music/
├── sfx/
├── fonts/
├── overlays/


Assets are **described**, not hardcoded.

Future plan:
- Metadata / recipe-based asset usage
- Renderer never “decides” creatively

---

### 5.7 Automation Layer (Planned)

- One-click local run
- Optional scheduler (later)
- No manual intervention per video
- Safe failure handling

Potential tools:
- Python scripts
- n8n (optional later)

---

### 5.8 Feedback Loop (Future Phase)

Goal:
Improve scripts based on what actually performs.

Metrics:
- Retention
- Loop rate
- Likes / comments
- Watch duration

Approach:
- Pattern reinforcement
- Not “training a model”
- Adjust templates and hooks over time

---

## 6. Project Phases

### Phase 1 — Design & Constraints ✅
- Vision defined
- Constraints locked
- Content direction decided

### Phase 2 — Voice Feasibility ✅
- XTTS-v2 installed
- Reference cloning working
- Acceptable baseline quality achieved

### Phase 3 — Script Transformer (Next)
- Deterministic script formatting
- Chunk logic
- Emphasis control

### Phase 4 — Audio Polish
- Fix gaps
- Fix crackle
- Normalize output
- Lock pacing

### Phase 5 — Video Rendering
- Gameplay + captions + audio
- FFmpeg pipeline
- Recipe-based control

### Phase 6 — Full Automation
- One-click execution
- Batch generation
- Upload integration

### Phase 7 — Feedback & Optimization
- Pattern tracking
- Script improvement over time

---

## 7. Out of Scope (For Now)

- Perfect human-level voice acting
- Real-time generation
- Live-stream content
- Heavy ML training
- Paid API dependency

---

## 8. Guiding Principles

- Build systems, not hacks
- Defer polish, don’t skip it
- Solve hardest problems first
- One source of truth
- Deterministic > clever
- Consistency beats novelty

---

## 9. How to Resume This Project

If returning after a break:
1. Read this file
2. Identify current phase
3. Resume from the next incomplete phase
4. Do NOT redo completed work

If unsure:
> “Proceed from Phase 3 — Script Transformer.”

---

## End of Requirements
