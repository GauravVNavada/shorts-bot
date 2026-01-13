# Shorts-Bot Project

## Version 1 (V1)
Pipeline:
Script → TTS (chunked) → Whisper alignment → Caption blocks → FFmpeg render

Features:
- Batch generation with per-video folders
- Recipe-based scripts (idea_001 etc.)
- Audio SFX + background music
- Caption grouping with pause detection + width control

Problems:
- TTS audio has glitches, rushing, stretching
- Caption spacing and aesthetics degraded after batching
- FFmpeg subtitles are too rigid

Goals for Version 2:
- Fix audio quality at architecture level (not hacks)
- Switch subtitles to MoviePy for better visuals
- Expand assets (music, SFX, overlays)
- Asset-aware recipe logic
- Production-quality output
- Later: scheduling + automated YouTube uploads
