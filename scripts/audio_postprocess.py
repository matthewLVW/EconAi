# scripts/audio_postprocess.py

import os
from pydub import AudioSegment
from pydub.effects import normalize, compress_dynamic_range

def process_stewie(audio: AudioSegment) -> AudioSegment:
    eq_boosted = (
        audio
        .high_pass_filter(140)
        .low_pass_filter(6000)
        .apply_gain(+1.5)
    )
    compressed = compress_dynamic_range(
        eq_boosted,
        threshold=-24,
        ratio=5.5,
        attack=2,
        release=100
    )
    nasal = compressed.low_pass_filter(1150).high_pass_filter(850).apply_gain(+2.0)
    enhanced = compressed.overlay(nasal)
    return enhanced

def process_peter(audio: AudioSegment) -> AudioSegment:
    processed = (
        audio
        .low_pass_filter(2800)
        .high_pass_filter(150)
        .apply_gain(-3.5)
        .fade_in(300)
        .fade_out(300)
    )
    return compress_dynamic_range(
        processed,
        threshold=-24.0,
        ratio=6.5,
        attack=3,
        release=300
    )

def normalize_group(clips: list[AudioSegment], target_dBFS: float = -16.0):
    loudnesses = [clip.dBFS for clip in clips]
    gains = [target_dBFS - dbfs for dbfs in loudnesses]
    return [clip.apply_gain(gain) for clip, gain in zip(clips, gains)]

def postprocess_audio_clips(input_dir="AudioTemp", output_dir="ProcessedAudio"):
    os.makedirs(output_dir, exist_ok=True)
    speaker_clips = {"peter": [], "stewie": []}
    speaker_filenames = {"peter": [], "stewie": []}

    for filename in sorted(os.listdir(input_dir)):
        if not filename.endswith(".mp3"):
            continue
        speaker = "stewie" if "stewie" in filename.lower() else "peter"
        path = os.path.join(input_dir, filename)
        audio = AudioSegment.from_file(path)
        processed = process_stewie(audio) if speaker == "stewie" else process_peter(audio)
        speaker_clips[speaker].append(processed)
        speaker_filenames[speaker].append(filename)

    for speaker in ["peter", "stewie"]:
        normalized = normalize_group(speaker_clips[speaker])
        for clip, fname in zip(normalized, speaker_filenames[speaker]):
            out_path = os.path.join(output_dir, fname)
            clip.export(out_path, format="mp3")
            print(f"✅ Exported normalized {fname} ➝ {out_path}")
