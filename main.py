import threading, os
from config.settings import Config

os.environ["GOOGLE_APPLICATION_CREDENTIALS"] = Config.GOOGLE_APPLICATION_CREDENTIALS

from audio.audio_stream import stream_audio_to_text
from transcription.summary_generator import generate_meeting_summary


# Flag to control the transcription thread
stop_transcription = False

def start_real_time_transcription():
    try:
        stream_audio_to_text()
    except Exception as e:
        print(f"An error occured: {e}")

if __name__ == "__main__":
    transcription_thread = threading.Thread(target=start_real_time_transcription)
    transcription_thread.start()

    try:
        transcription_thread.join()
    except KeyboardInterrupt:
        print("\nTerminating transcription...")
        stop_transcription = True
        transcription_thread.join()