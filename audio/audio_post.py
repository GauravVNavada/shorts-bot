from pydub import AudioSegment
import json
import sys
import os
import string

# ------------------- HELPERS -------------------

def load_json(path):
    with open(path, "r", encoding="utf-8") as f:
        return json.load(f)

def normalize_word(w):
    return w.strip().lower().translate(str.maketrans("", "", string.punctuation))

def find_word_time(words, target):
    target = normalize_word(target)
    for w in words:
        if normalize_word(w["word"]) == target:
            return w["start"]
    return None

def find_segment_time(segment_timeline, name):
    name = name.lower()
    segment = segment_timeline.get(name)
    if not segment:
        return None
    return segment["start"]

# ------------------- CORE ENGINE -------------------

def apply_music(narration, music_cfg):
    music = AudioSegment.from_file(music_cfg["track"])
    loops = int(len(narration) / len(music)) + 1
    music = (music * loops)[:len(narration)]

    music = music + music_cfg.get("volume", 0)

    if music_cfg.get("fade_in"):
        music = music.fade_in(int(music_cfg["fade_in"] * 1000))
    if music_cfg.get("fade_out"):
        music = music.fade_out(int(music_cfg["fade_out"] * 1000))

    if music_cfg.get("duck_under_voice", False):
        music = music - 10

    return narration.overlay(music)

def apply_sfx(base_audio, sfx_list, words, segment_timeline):
    for sfx in sfx_list:
        sound = AudioSegment.from_file(sfx["file"])

        # Risers need headroom
        if sfx.get("type") == "riser":
            sound = sound + sfx.get("volume", 6)   # boost riser
            sound = sound.fade_in(150)              # smooth start
        else:
            sound = sound + sfx.get("volume", 0)


        start_time = None

        if "at_word" in sfx:
            start_time = find_word_time(words, sfx["at_word"])
            if start_time is None:
                continue
            start_time += sfx.get("offset", 0)

        elif "at_segment" in sfx:
            start_time = find_segment_time(segment_timeline, sfx["at_segment"])
            if start_time is None:
                print(f"⚠️ Segment not found: {sfx['at_segment']}")
                continue

        elif "start" in sfx:
            start_time = sfx["start"]

        if start_time is None:
            continue

        base_audio = base_audio.overlay(
            sound,
            position=int(start_time * 1000)
        )

    return base_audio

# ------------------- PIPELINE -------------------

def render_audio_with_recipe(input_audio, words_json, segments_json, output_audio):
    print("🎧 Loading narration...")
    narration = AudioSegment.from_file(input_audio)

    print("📖 Loading recipe...")
    recipe = load_json("recipe_audio.json")

    print("🕒 Loading alignment data...")
    words = load_json(words_json)

    print("🧭 Loading segment timeline...")
    segment_data = load_json(segments_json)
    segment_timeline = segment_data.get("segments", {})

    if "music" in recipe:
        print("🎵 Applying background music...")
        narration = apply_music(narration, recipe["music"])

    if "sfx" in recipe:
        print("🔊 Applying sound effects...")
        narration = apply_sfx(
            narration,
            recipe["sfx"],
            words,
            segment_timeline
        )

    print("💾 Exporting final audio...")
    os.makedirs(os.path.dirname(output_audio), exist_ok=True)
    narration.export(
        output_audio,
        format="wav",
        parameters=["-ar", "48000", "-ac", "2"]
    )

    print("✅ Final audio written to:", output_audio)

# ------------------- ENTRY -------------------

if __name__ == "__main__":
    if len(sys.argv) < 5:
        print("Usage: python audio_post.py <input_audio> <words_json> <segments_json> <output_audio>")
        sys.exit(1)

    render_audio_with_recipe(
        sys.argv[1],
        sys.argv[2],
        sys.argv[3],
        sys.argv[4]
    )
