"""
Pre-generate sound effects using ElevenLabs Sound Effects API.
Run once to create audio files in static/sounds/.

Usage: python generate_sounds.py
Requires: ELEVENLABS_API_KEY in .env or environment
"""

import os
from pathlib import Path

from dotenv import load_dotenv
from elevenlabs import ElevenLabs

load_dotenv()

SOUNDS_DIR = Path(__file__).parent / "static" / "sounds"
SOUNDS_DIR.mkdir(parents=True, exist_ok=True)

EFFECTS = {
    "money_saved.mp3": "cash register cha-ching sound effect, bright and satisfying",
    "bad_news.mp3": "dramatic orchestral sting, ominous bad news reveal, short",
    "victory.mp3": "short triumphant victory fanfare, celebratory, upbeat",
    "researching.mp3": "subtle computer keyboard typing and data processing sounds",
}


def main():
    api_key = os.getenv("ELEVENLABS_API_KEY")
    if not api_key:
        print("Error: ELEVENLABS_API_KEY not set. Add it to .env or environment.")
        return

    client = ElevenLabs(api_key=api_key)

    for filename, prompt in EFFECTS.items():
        output_path = SOUNDS_DIR / filename
        if output_path.exists():
            print(f"Skipping {filename} (already exists)")
            continue

        print(f"Generating {filename}: '{prompt}'...")
        try:
            result = client.text_to_sound_effects.convert(
                text=prompt,
                duration_seconds=3.0,
            )
            # result is a generator of bytes chunks
            audio_bytes = b"".join(result)
            output_path.write_bytes(audio_bytes)
            print(f"  Saved to {output_path} ({len(audio_bytes)} bytes)")
        except Exception as e:
            print(f"  Failed: {e}")

    print("\nDone. Sound effects saved to static/sounds/")


if __name__ == "__main__":
    main()
