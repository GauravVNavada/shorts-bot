import os
import subprocess
import json
from datetime import datetime
import sys

VIDEOS_DIR = "videos"
IDEAS_FILE = "ideas.json"


def load_ideas():
    with open(IDEAS_FILE, "r", encoding="utf-8") as f:
        return json.load(f)


def save_ideas(data):
    with open(IDEAS_FILE, "w", encoding="utf-8") as f:
        json.dump(data, f, indent=2)


def get_next_video_id():
    os.makedirs(VIDEOS_DIR, exist_ok=True)
    existing = [d for d in os.listdir(VIDEOS_DIR) if d.startswith("video_")]
    if not existing:
        return 1
    nums = [int(d.split("_")[1]) for d in existing if d.split("_")[1].isdigit()]
    return max(nums) + 1


def build_script_text(script_obj):
    return (
        f"{script_obj['hook']} "
        f"{script_obj['beat']} "
        f"{script_obj['lore']} "
        f"{script_obj['cta']}"
    )


def get_next_pending_idea(ideas):
    for key, idea in ideas.items():
        if idea.get("status") == "pending":
            return key, idea
    return None, None


def create_video_job(video_index, idea_key, idea):
    video_id = f"video_{video_index:03d}"
    base_path = os.path.join(VIDEOS_DIR, video_id)

    input_dir = os.path.join(base_path, "input")
    intermediate_dir = os.path.join(base_path, "intermediate")
    output_dir = os.path.join(base_path, "output")

    os.makedirs(input_dir, exist_ok=True)
    os.makedirs(intermediate_dir, exist_ok=True)
    os.makedirs(output_dir, exist_ok=True)

    print(f"\n🎬 Creating {video_id} from {idea_key}")

    # 1️⃣ Build script from JSON
    script_text = build_script_text(idea["script"])
    script_path = os.path.join(input_dir, "script.txt")
    with open(script_path, "w", encoding="utf-8") as f:
        f.write(script_text)

    # 2️⃣ TTS → narration.wav
    print("🎙 Generating narration...")
    subprocess.run(
        [sys.executable, "scripts/narrate.py", script_path, intermediate_dir],
        check=True
    )

    narration_path = os.path.join(intermediate_dir, "narration.wav")

    # 3️⃣ Whisper alignment
    print("🕒 Running alignment...")
    words_json = os.path.join(intermediate_dir, "words.json")
    subprocess.run(
        [sys.executable, "alignment/whisper_align.py", narration_path, words_json],
        check=True
    )

    # 4️⃣ Build captions
    print("📝 Building captions...")
    blocks_json = os.path.join(intermediate_dir, "word_blocks.json")
    ideas_json = "ideas.json"  # path to your main recipe file

    subprocess.run(
        [
            sys.executable,
            "captions/build_word_blocks.py",
            words_json,
            ideas_json,
            blocks_json,
        ],
        check=True
    )


    # 5️⃣ Audio post (music + SFX)
    print("🎧 Applying music and SFX...")
    final_audio = os.path.join(output_dir, "audio.wav")

    subprocess.run(
        [
            sys.executable,
            "audio/audio_post.py",
            narration_path,
            words_json,
            blocks_json,
            final_audio
        ],
        check=True
    )

    # 6️⃣ Video render
    print("🎞 Rendering video...")
    final_video = os.path.join(output_dir, "video.mp4")
    subprocess.run(
        [sys.executable, "render/render.py", final_audio, blocks_json, final_video],
        check=True
    )

    # 7️⃣ Update idea status + log
    idea["status"] = "rendered"
    idea["log"]["rendered_at"] = datetime.now().isoformat()
    idea["log"]["video_path"] = final_video

    # Save updated ideas.json
    ideas = load_ideas()
    ideas[idea_key] = idea
    save_ideas(ideas)

    print(f"✅ {video_id} completed and {idea_key} marked as rendered")


def generate_batch(count=1):
    ideas = load_ideas()
    start_id = get_next_video_id()

    for i in range(count):
        idea_key, idea = get_next_pending_idea(ideas)
        if not idea:
            print("🚫 No pending ideas left in ideas.json")
            return

        create_video_job(start_id + i, idea_key, idea)


if __name__ == "__main__":
    count = int(sys.argv[1]) if len(sys.argv) > 1 else 1
    generate_batch(count)
