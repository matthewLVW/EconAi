from scripts.script_generator import generate_best_script
from scripts.voice_generator import parse_script, generate_audio
from scripts.audio_postprocess import postprocess_audio_clips
from scripts.generate_captions_data import generate_and_save_captions
from scripts.video_assembler import assemble_video
from scripts.Metadata_generator import save_metadata_for_script

if __name__ == "__main__":
    topic = "Why are payday loans so bad?"

    # Step 1: Generate and save best script
    #best_script = generate_best_script(topic, save_path="script.txt")
    #script_lines = parse_script("script.txt")
    #generate_audio(script_lines)
    #postprocess_audio_clips("assets/AudioTemp", "ProcessedAudio")
    #generate_and_save_captions("script.txt", "ProcessedAudio", "captions.json")
    assemble_video(topic)
    save_metadata_for_script("script.txt")