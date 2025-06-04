"""
eleven_labs_tts.py

This script takes a parameterized dialogue script in the format:

    Stewie: Hey, Peter! What are put options? I bet they're not what I put in my cereal this morning!
    Peter: Oh, Stewie, put options are a bit more exciting than that! ...

and uses the ElevenLabs Text-to-Speech API to generate separate audio clips
for "Peter" and "Stewie" using their respective voice IDs. It then concatenates
all generated audio segments into a single output file: `output.mp3`.

Before running:
1. Install required packages:
     pip install requests pydub

2. Set your Eleven Labs API Key as an environment variable:
     export ELEVENLABS_API_KEY="your_elevenlabs_api_key_here"

3. Replace the placeholder voice IDs for STEWIE_VOICE_ID and PETER_VOICE_ID
   with the actual voice IDs from your Eleven Labs account.

Usage:
    python eleven_labs_tts.py input_script.txt
"""

import os
import sys
import random
import requests
import tempfile
from pydub import AudioSegment
from dotenv import load_dotenv
load_dotenv()

# Replace these with your actual Eleven Labs voice IDs
STEWIE_VOICE_ID = "DL63rxhw9dXPUx8xlBxa"
PETER_VOICE_ID = "oRgIPTyhED338KvRzKFh"

ELEVEN_LABS_API_KEY = os.getenv("ELEVENLABS_API_KEY")
if not ELEVEN_LABS_API_KEY:
    raise RuntimeError("Please set the ELEVENLABS_API_KEY environment variable.")

ELEVEN_LABS_API_URL = "https://api.elevenlabs.io/v1/text-to-speech/"


def tts_generate(voice_id: str, text: str) -> bytes:
    """
    Calls the ElevenLabs TTS endpoint with the given voice_id and text.
    Returns raw audio bytes (MP3 format).
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
            "stability": 0.7,
            "similarity_boost": 0.9
        }
    }
    response = requests.post(url, json=payload, headers=headers)
    response.raise_for_status()
    return response.content


def parse_script_file(script_path: str) -> list:
    """
    Reads the script file and returns a list of tuples: (speaker, line_text).
    Expects lines in the format:
        Speaker: Dialogue text...
    """
    lines = []
    with open(script_path, "r", encoding="utf-8") as f:
        for raw_line in f:
            line = raw_line.strip()
            if not line:
                continue
            if ":" not in line:
                continue  # skip malformed lines
            speaker, text = line.split(":", 1)
            speaker = speaker.strip()
            text = text.strip()
            lines.append((speaker, text))
    return lines


def generate_and_concatenate(script_lines: list, output_path: str = "output.mp3"):
    audio_segments = []
    temp_files = []

    os.makedirs("AudioTemp", exist_ok=True)
    speaker_counts = {"stewie": 0, "peter": 0}

    try:
        for speaker, text in script_lines:
            speaker_lower = speaker.lower()
            if speaker_lower == "stewie":
                voice_id = STEWIE_VOICE_ID
            elif speaker_lower == "peter":
                voice_id = PETER_VOICE_ID
            else:
                print(f"Warning: Unrecognized speaker '{speaker}'. Skipping line.")
                continue

            print(f"Generating audio for {speaker}: \"{text[:30]}...\"")
            audio_bytes = tts_generate(voice_id, text)

            # Save to temporary file
            tmp_file = tempfile.NamedTemporaryFile(delete=False, suffix=".mp3")
            tmp_file.write(audio_bytes)
            tmp_file.flush()
            tmp_file.close()
            temp_files.append(tmp_file.name)

            # Save individual file to AudioTemp
            speaker_counts[speaker_lower] += 1
            numbered_filename = f"{speaker.capitalize()}{speaker_counts[speaker_lower]}.mp3"
            output_individual_path = os.path.join("AudioTemp", numbered_filename)
            with open(output_individual_path, "wb") as f:
                f.write(audio_bytes)

            # Load with pydub
            segment = AudioSegment.from_file(tmp_file.name, format="mp3")
            audio_segments.append(segment)

        if not audio_segments:
            raise RuntimeError("No audio segments generated. Check your script format and voice IDs.")

        # Concatenate all segments
        combined = audio_segments[0]
        for seg in audio_segments[1:]:
            random_pause = AudioSegment.silent(duration=random.randint(200, 400))
            combined += random_pause + seg

        # Export final audio
        combined.export(output_path, format="mp3")
        print(f"Final combined audio saved to: {output_path}")

    finally:
        # Clean up temp files
        for tmp in temp_files:
            try:
                os.remove(tmp)
            except OSError:
                pass


def main():
    script_path = "Script.txt"
    if not os.path.isfile(script_path):
        print(f"Error: File not found: {script_path}")
        sys.exit(1)

    script_lines = parse_script_file(script_path)
    generate_and_concatenate(script_lines)
    print(script_lines)

if __name__ == "__main__":
    main()
