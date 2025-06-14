# generate_captions_data.py

import os
import json
from pydub import AudioSegment
import textstat

SCRIPT_PATH = "script.txt"
AUDIO_DIR = "assets\AudioTemp"
OUTPUT_JSON = "captions.json"
import unicodedata
import re

def clean_caption_text(text):
    # Normalize to NFKC (handles ligatures, smart quotes, etc.)
    text = unicodedata.normalize("NFKC", text)

    # Replace dashes, smart quotes, ellipses
    text = (
        text.replace("’", "'").replace("‘", "'")
            .replace("“", '"').replace("”", '"')
            .replace("—", "").replace("–", "-").replace("…", "...")
    )

    # Remove emojis/symbols/non-text unicode (Symbol or Other)
    text = ''.join(ch for ch in text if not unicodedata.category(ch).startswith(('S', 'C')))

    # Remove stray non-alphanum punctuation except standard sentence characters
    text = re.sub(r"[^\w\s.,!?'\"]+", "", text)

    # Normalize all whitespace
    text = re.sub(r"\s+", " ", text).strip()

    return text

def build_captions(script_path, audio_dir):
    with open(script_path, "r", encoding="utf-8-sig") as f:
        lines = [line.strip() for line in f if ':' in line]

    current_time = 0.0
    captions = []
    speaker_counts = {"peter": 0, "stewie": 0}

    for line in lines:
        speaker, text = line.split(':', 1)
        speaker = speaker.strip().lower()
        text = text.strip()
        text = clean_caption_text(text)

        speaker_counts[speaker] += 1
        audio_file = os.path.join(audio_dir, f"{speaker}{speaker_counts[speaker]}.mp3")
        
        if not os.path.exists(audio_file):
            raise FileNotFoundError(f"Missing audio file: {audio_file}")

        audio = AudioSegment.from_file(audio_file)
        duration = len(audio) / 1000.0



        captions.append({
            "start": round(current_time, 2),
            "end": round(current_time + duration, 2),
            "speaker": speaker,
            "text": text,
            "audio_path": audio_file
        })

        current_time += duration

    return captions
def estimate_syllables(word):
    return max(textstat.syllable_count(word), 1)  # fallback to 1 to avoid zero

def syllable_chunked_captions(captions, max_syllables=5):
    """
    Splits captions into phrases of ≤ max_syllables each,
    reassigns timing across the resulting chunks.
    """
    new_captions = []

    for cap in captions:
        words = cap["text"].split()
        total_duration = cap["end"] - cap["start"]
        if total_duration <= 0 or not words:
            continue

        # Build syllable-limited chunks
        chunks = []
        current_chunk = []
        current_syllables = 0

        for word in words:
            sylls = estimate_syllables(word)
            if current_syllables + sylls > max_syllables and current_chunk:
                chunks.append(" ".join(current_chunk))
                current_chunk = [word]
                current_syllables = sylls
            else:
                current_chunk.append(word)
                current_syllables += sylls

        if current_chunk:
            chunks.append(" ".join(current_chunk))

        # Split duration evenly across chunks
        chunk_duration = total_duration / len(chunks)
        for i, chunk in enumerate(chunks):
            new_captions.append({
                "text": chunk,
                "start": cap["start"] + i * chunk_duration,
                "end": cap["start"] + (i + 1) * chunk_duration,
                "speaker": cap["speaker"],
                "audio_path": cap["audio_path"]
            })

    return new_captions
def generate_and_save_captions(script_path, audio_dir, output_json_path, output_dir="output"):
    caption_data = build_captions(script_path, audio_dir)

    os.makedirs(output_dir, exist_ok=True)
    filename = os.path.basename(output_json_path)
    output_path = os.path.join(output_dir, filename)

    with open(output_path, "w") as out:
        json.dump(caption_data, out, indent=2)

    print(f"[✅] Saved {len(caption_data)} caption entries to {output_path}")
    return output_path  # Optional: return the path for downstream use

