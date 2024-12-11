import threading, os
from config.settings import Config
import argparse

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
    
    parser = argparse.ArgumentParser(description="A simple command line argument parser.")
    # parser.add_argument('-o', '--outputFileName', type=str, required=True, help="Temp file name to store meeting transcription.")
    # parser.add_argument('-s', '--socketPath', type=str, help="dir name for unix socket")
    parser.add_argument('-t', '--translatorApi', type=str, required=True, help="API abbriviation for transcription among 'g':Google stt api, 'd':Deepgram api.")

    args = parser.parse_args()
    if args.translatorApi == 'g':
        Config.SOCKET_PATH = './bots/zoom_bot/sock/googleApi/meeting.sock'
        Config.OUTPUT_FILE = './tmp/meeting_temp_google.txt'
    else:
        Config.SOCKET_PATH = './bots/zoom_bot/sock/deepgramApi/meeting.sock'
        Config.OUTPUT_FILE = './tmp/meeting_temp_deepgram.txt'

    transcription_thread = threading.Thread(target=start_real_time_transcription)
    transcription_thread.start()

    try:
        transcription_thread.join()
    except KeyboardInterrupt:
        print("\nTerminating transcription...")
        stop_transcription = True
        transcription_thread.join()