def save_transcription_in_real_time(speaker, text, output_file):
    with open(output_file, "a") as file:
        file.write(f"Speaker {speaker}: {text.strip()}\n")
    print(f"Saved: Speaker {speaker}: {text.strip()}")