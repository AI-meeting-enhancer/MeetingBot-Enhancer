def save_transcription_in_real_time(speaker, text, output_file):
    if(text.strip()):
        with open(output_file, "a") as file:
            file.write(f"{speaker}: {text.strip()}\n")
        print(f"{speaker}: {text.strip()}")
