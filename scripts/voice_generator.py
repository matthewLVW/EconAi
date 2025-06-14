# scripts/voice_generator.py

import os
import random
import requests
import tempfile
from pydub import AudioSegment
from dotenv import load_dotenv
import shutil

load_dotenv()

# Voice IDs for each character (customize if needed)
STEWIE_VOICE_ID = "DL63rxhw9dXPUx8xlBxa"
PETER_VOICE_ID = "oRgIPTyhED338KvRzKFh"

ELEVEN_LABS_API_KEY = os.getenv("ELEVENLABS_API_KEY")
if not ELEVEN_LABS_API_KEY:
    raise RuntimeError("Please set the ELEVENLABS_API_KEY environment variable.")

ELEVEN_LABS_API_URL = "https://api.elevenlabs.io/v1/text-to-speech/"


def tts_generate(voice_id: str, text: str) -> bytes:
    """
    Calls the ElevenLabs TTS endpoint and returns raw MP3 audio bytes.
    """
    url = ELEVEN_LABS_API_URL + voice_id
    headers = {
        "xi-api-key": ELEVEN_LABS_API_KEY,
        "Content-Type": "application/json"
    }
    payload = {
        "text": text,
        "model_id": "eleven_multilingual_v2",
        "voice_settings": {
            "stability": 0.75,
            "similarity_boost": 0.9
        }
    }
    response = requests.post(url, json=payload, headers=headers)
    response.raise_for_status()
    return response.content


def parse_script(script_path: str) -> list[tuple[str, str]]:
    """
    Reads a script.txt and returns [(speaker, line_text), ...]
    """
    lines = []
    with open(script_path, "r", encoding="utf-8") as f:
        for raw in f:
            if ":" not in raw:
                continue
            speaker, text = raw.split(":", 1)
            lines.append((speaker.strip(), text.strip()))
    return lines


def generate_audio(script_lines: list[tuple[str, str]], output_path: str = "output/output.mp3"):
    """
    Generates individual audio files to ./AudioTemp and saves full output.mp3.
    """
    audio_segments = []
    temp_files = []
    shutil.rmtree("assets/AudioTemp", ignore_errors=True)
    os.makedirs("assets/AudioTemp", exist_ok=True)
    os.makedirs("output", exist_ok=True)
    speaker_counts = {"stewie": 0, "peter": 0}

    try:
        for speaker, text in script_lines:
            key = speaker.lower()
            if key == "stewie":
                voice_id = STEWIE_VOICE_ID
            elif key == "peter":
                voice_id = PETER_VOICE_ID
            else:
                print(f"⚠️ Skipping unknown speaker: {speaker}")
                continue

            print(f"[TTS] {speaker}: {text[:40]}...")
            audio_bytes = tts_generate(voice_id, text)

            # Save individual clip
            speaker_counts[key] += 1
            filename = f"{speaker.capitalize()}{speaker_counts[key]}.mp3"
            full_path = os.path.join("assets/AudioTemp", filename)
            with open(full_path, "wb") as f:
                f.write(audio_bytes)

            # Save to temp and load with pydub
            tmp = tempfile.NamedTemporaryFile(delete=False, suffix=".mp3")
            tmp.write(audio_bytes)
            tmp.flush()
            tmp.close()
            temp_files.append(tmp.name)
            segment = AudioSegment.from_file(tmp.name)
            audio_segments.append(segment)

        if not audio_segments:
            raise RuntimeError("No audio segments were created.")

        # Stitch final audio
        combined = audio_segments[0]
        for seg in audio_segments[1:]:
            pause = AudioSegment.silent(duration=random.randint(200, 400))
            combined += pause + seg

        combined.export(output_path, format="mp3")
        print(f"✅ Final audio saved to: {output_path}")

    finally:
        for tmp in temp_files:
            try:
                os.remove(tmp)
            except:
                pass
