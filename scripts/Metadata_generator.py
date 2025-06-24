import os
import json
import re
import csv
from datetime import datetime
from openai import OpenAI
from dotenv import load_dotenv

load_dotenv()
client = OpenAI()

def build_metadata_prompt_from_script(script_text: str):
    return [
        {
            "role": "system",
            "content": (
                "You are a short-form content strategist. Based on the script below, "
                "generate a viral-ready video title, a punchy caption (under 200 characters), "
                "and a list of 6–8 hashtags optimized for TikTok, YouTube Shorts, Instagram Reels, and X.\n\n"
                "The caption should be clear, funny, or curiosity-driven, using natural human tone.\n"
                "Hashtags must start with '#' and be lowercase, space-free, and relevant to the script.\n"
                "Return only a JSON object with keys: 'title', 'caption', and 'hashtags'."
            )
        },
        {
            "role": "user",
            "content": (
                "Script:\n" + script_text +
                "\n\nNow generate metadata for this video."
            )
        }
    ]

def load_script_text(script_path: str) -> str:
    with open(script_path, "r", encoding="utf-8") as f:
        return f.read().strip()

def extract_json_like(text):
    match = re.search(r"\{.*\}", text, re.DOTALL)
    return match.group(0) if match else text

def generate_post_metadata_from_script(script_path: str):
    script_text = load_script_text(script_path)
    messages = build_metadata_prompt_from_script(script_text)

    response = client.chat.completions.create(
        model="gpt-4.1",
        messages=messages,
        temperature=0.7,
        max_tokens=400
    )

    raw = response.choices[0].message.content.strip()

    if raw.startswith("```json") or raw.startswith("```"):
        raw = raw.strip("`").strip("json").strip()

    try:
        metadata = json.loads(raw)
    except Exception as e:
        print(f"\n❌ JSON parse error: {e}")
        print("🔍 Attempting fallback JSON extraction...")
        try:
            fallback = extract_json_like(raw)
            metadata = json.loads(fallback)
        except Exception as e2:
            print(f"\n🧨 Fallback parse failed: {e2}")
            print("Raw output:\n", raw)
            metadata = {
                "title": f"[Error parsing title] {e2}",
                "caption": "[Failed to parse caption]",
                "hashtags": []
            }

    return metadata

def sanitize_filename(text: str) -> str:
    return re.sub(r"[^a-zA-Z0-9_\-]", "_", text.strip().lower())[:50]

def process_schedule(schedule_path: str):
    with open(schedule_path, "r", encoding="utf-8") as f:
        lines = [line.strip().split("\t") for line in f if line.strip()]

    os.makedirs("metadata", exist_ok=True)
    os.makedirs("final_output", exist_ok=True)

    with open("final_output/posting_schedule.csv", "w", newline="", encoding="utf-8") as csvfile:
        writer = csv.DictWriter(csvfile, fieldnames=["Topic", "Date", "Time", "Title", "Caption", "Hashtags", "Metadata File"])
        writer.writeheader()

        for topic, date, time in lines:
            script_path = f"scripts/{sanitize_filename(topic)}.txt"
            if not os.path.exists(script_path):
                print(f"⚠️ Script file not found: {script_path}")
                continue

            metadata = generate_post_metadata_from_script(script_path)
            metadata_filename = sanitize_filename(metadata.get("title", topic)) + ".json"
            metadata_path = os.path.join("metadata", metadata_filename)

            with open(metadata_path, "w", encoding="utf-8") as f:
                json.dump(metadata, f, indent=2, ensure_ascii=False)

            writer.writerow({
                "Topic": topic,
                "Date": date,
                "Time": time,
                "Title": metadata.get("title", ""),
                "Caption": metadata.get("caption", ""),
                "Hashtags": " ".join(metadata.get("hashtags", [])),
                "Metadata File": metadata_filename
            })
            print(f"✅ Processed: {topic}")

def save_metadata_for_script(script_path: str, metadata_dir="metadata"):
    metadata = generate_post_metadata_from_script(script_path)
    os.makedirs(metadata, exist_ok=True)
    filename = sanitize_filename(metadata.get("title", "untitled")) + ".json"
    out_path = os.path.join(metadata_dir, filename)

    with open(out_path, "w", encoding="utf-8") as f:
        json.dump(metadata, f, indent=2, ensure_ascii=False)

    print(f"[📦] Metadata saved: {out_path}")
    return metadata


if __name__ == "__main__":
    process_schedule("video_schedule.tsv")
