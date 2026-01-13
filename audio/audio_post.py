from pydub import AudioSegment
import json
import sys
import os
import string

WORDS_JSON = None
SEGMENTS_JSON = None
RECIPE = "recipe_audio.json"

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

def find_segment_time(segments, name):
    name = name.lower()
    for s in segments:
        intent = s.get("intent", "").lower()
        if name in ["hook", "cta"] and intent == "emphasis":
            return s["start"]
        if name == "normal" and intent == "normal":
            return s["start"]
    return None

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

def apply_sfx(base_audio, sfx_list, words, segments):
    for sfx in sfx_list:
        sound = AudioSegment.from_file(sfx["file"])
        sound = sound + sfx.get("volume", 7)

        start_time = None

        if "at_word" in sfx:
            start_time = find_word_time(words, sfx["at_word"])
            if start_time is None:
                continue
            start_time += sfx.get("offset", 0)

        elif "at_segment" in sfx:
            start_time = find_segment_time(segments, sfx["at_segment"])
            if start_time is None:
                continue

        elif "start" in sfx:
            start_time = sfx["start"]

        if start_time is None:
            continue

        base_audio = base_audio.overlay(sound, position=int(start_time * 1000))

    return base_audio

# ------------------- PIPELINE -------------------

def render_audio_with_recipe(input_audio, words_json, segments_json, output_audio):
    print("🎧 Loading narration...")
    narration = AudioSegment.from_file(input_audio)

    print("📖 Loading recipe...")
    recipe = load_json(RECIPE)

    print("🕒 Loading alignment data...")
    words = load_json(words_json)
    segments = []

    if "music" in recipe:
        print("🎵 Applying background music...")
        narration = apply_music(narration, recipe["music"])

    if "sfx" in recipe:
        print("🔊 Applying sound effects...")
        narration = apply_sfx(narration, recipe["sfx"], words, segments)

    print("💾 Exporting final audio...")
    os.makedirs(os.path.dirname(output_audio), exist_ok=True)
    narration.export(output_audio, format="wav", parameters=["-ar", "48000", "-ac", "2"])

    print("✅ Final audio written to:", output_audio)

if __name__ == "__main__":
    if len(sys.argv) < 5:
        print("Usage: python audio_post.py <input_audio> <words_json> <segments_json> <output_audio>")
        sys.exit(1)

    input_audio = sys.argv[1]
    words_json = sys.argv[2]
    segments_json = sys.argv[3]
    output_audio = sys.argv[4]

    render_audio_with_recipe(input_audio, words_json, segments_json, output_audio)
