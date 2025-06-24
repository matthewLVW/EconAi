import json
import os
from scripts.generate_captions_data import syllable_chunked_captions
import re
from moviepy import (
    VideoFileClip,
    AudioFileClip,
    CompositeAudioClip,
    CompositeVideoClip,
    concatenate_audioclips,
    TextClip,
    ColorClip
)

# === CONFIGURATION ===
VIDEO_PATH = "assets/backgrounds/SO6.mp4"
CAPTIONS_PATH = "output/captions.json"
FONT_PATH = "assets/fonts/Bangers-Regular.ttf"
FONT_SIZE = 85
STEWIE_COLOR = "#ADD8E6"  # Light blue
PETER_COLOR = "#FFD700"   # Light gold
CAPTION_WIDTH_PCT = 0.90
STROKE_WIDTH = 2
STROKE_COLOR = "black"
PETER_IMG_PATH = "assets/images/peter_resized.png"
STEWIE_IMG_PATH = "assets/images/stewie_resized.png"
CHAR_IMG_HEIGHT = 500  # You can adjust for size

def safe_filename(text: str) -> str:
    return re.sub(r'[^a-zA-Z0-9_\-]', '_', text.strip().lower())

# === LOAD CAPTIONS ===
def load_captions(path):
    with open(path, "r") as f:
        return json.load(f)

# === CREATE CAPTION CLIP ===
def create_caption_clip(text, start, end, color, video_width, video_height):
    """
    Create a caption overlay with a subtle stroke/glow effect, layered on the video.
    """
    max_text_width = int(video_width * CAPTION_WIDTH_PCT)
    position = ("center", "center")

    # Soft shadow behind text for glow effect
    shadow = TextClip(
        text=text,
        font=FONT_PATH,
        font_size=FONT_SIZE,
        color="black",  # shadow color
        method="caption",
        size=(max_text_width, FONT_SIZE * 2)
    ).with_position((position[0], position[1])) \
     .with_opacity(0.4) \
     .with_start(start) \
     .with_duration(end - start)

    # Main visible text
    text_clip = TextClip(
        text=text,
        font=FONT_PATH,
        font_size=FONT_SIZE,
        color=color,
        stroke_color=STROKE_COLOR,
        stroke_width=STROKE_WIDTH,
        method="caption",
        size=(max_text_width, FONT_SIZE * 2)
    ).with_position(position) \
     .with_start(start) \
     .with_duration(end - start)

    return [shadow, text_clip]

from moviepy.video.VideoClip import ImageClip

def create_character_overlay(speaker, start, end, video_width, video_height):
    """
    Returns a positioned ImageClip for the given speaker between start and end time.
    """
    if speaker.lower() == "peter":
        img_path = PETER_IMG_PATH
        img_height = CHAR_IMG_HEIGHT*1.7  # 2x size for Peter
        position = (video_width - 650, video_height - img_height - 50)
    elif speaker.lower() == "stewie":
        img_path = STEWIE_IMG_PATH
        img_height = int(CHAR_IMG_HEIGHT)  # 1.3x size for Stewie
        position = (50, video_height - img_height - 50)
    else:
        return []

    img_clip = ImageClip(img_path) \
        .resized(height=img_height)\
        .with_position(position) \
        .with_start(start) \
        .with_duration(end - start)

    return [img_clip]

# === MAIN FUNCTION ===
def assemble_video(topic: str):
    audioCAP_data = load_captions(CAPTIONS_PATH)
    caption_data = syllable_chunked_captions(audioCAP_data)  # 👈 Add this line
    # Load background video and adjust
    video = VideoFileClip(VIDEO_PATH)
    video = video.without_audio()
    video = video.resized(height=1920)
    video = video.cropped(x_center=video.w / 2, width=1080, height=1920)

    # Combine dialogue audio
    dialogue_audio_clips = [AudioFileClip(cap["audio_path"]) for cap in audioCAP_data]
    dialogue_audio = concatenate_audioclips(dialogue_audio_clips)

    # Mix background + dialogue audio
    video_duration = dialogue_audio.duration
    video = video.subclipped(0, video_duration)

    # Generate captions
    overlay_clips = []
    for cap in caption_data:
        speaker = cap["speaker"]
        text = cap["text"]
        start = cap["start"]
        end = cap["end"]
        color = STEWIE_COLOR if speaker.lower() == "stewie" else PETER_COLOR
        overlay_clips += create_caption_clip(text, start, end, color, video.w, video.h)
        overlay_clips += create_character_overlay(speaker, start, end, video.w, video.h)

        # Debug: Print timing info to catch zero-duration captions
        duration = end - start
        print(f"[CAPTION] '{text[:30]}' | start: {start:.2f}s, end: {end:.2f}s, duration: {duration:.2f}s")

        if duration <= 0:
            print("⚠️ SKIPPING: Caption has zero or negative duration")
            continue

    print(f"[INFO] Total overlay clips created: {len(overlay_clips)}")
    FINAL_OUTPUT = os.path.join("output", f"{safe_filename(topic)}.mp4")
    # Final composite
    final_video = CompositeVideoClip([video] + overlay_clips)
    final_video = final_video.with_audio(dialogue_audio)
    final_video.write_videofile(FINAL_OUTPUT, fps=30, threads=8)

# === RUN SCRIPT ===
if __name__ == "__main__":
    assemble_video()
