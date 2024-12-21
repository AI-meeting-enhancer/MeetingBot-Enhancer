import threading, os
from config.settings import Config
import argparse

os.environ["GOOGLE_APPLICATION_CREDENTIALS"] = Config.GOOGLE_APPLICATION_CREDENTIALS

from audio.audio_stream import stream_audio_to_text
from transcription.modify_transcription import modify_transcription


# Flag to control the transcription thread
stop_transcription = False

def start_real_time_transcription():
    try:
        stream_audio_to_text()
    except Exception as e:
        print(f"An error occured: {e}")

if __name__ == "__main__":
    
    parser = argparse.ArgumentParser(description="A simple command line argument parser.")
    parser.add_argument('-t', '--translatorApi', type=str, required=True, help="API abbriviation for transcription among 'g':Google stt api, 'd':Deepgram api.")
    parser.add_argument('-m', '--modification', type=bool, help="if you set this argument, this script will work for only modification")
    parser.add_argument('-n', '--meetingName', type=str, required=True, help="Name of meeting for attend into meeting with")
    
    args = parser.parse_args()
    
    if args.translatorApi == 'g':
        Config.SOCKET_PATH = './bots/zoom_bot/sock/googleApi/meeting.sock'
        Config.OUTPUT_FILE = './tmp/meeting_temp_google.txt'
    else:
        Config.SOCKET_PATH = './bots/zoom_bot/sock/deepgramApi/meeting.sock'
        Config.OUTPUT_FILE = './tmp/meeting_temp_deepgram.txt'
        
    Config.MEETING_NAME = args.meetingName

    if args.modification:
        modify_transcription()
        exit(0)

    transcription_thread = threading.Thread(target=start_real_time_transcription)
    transcription_thread.start()

    try:
        transcription_thread.join()
    except KeyboardInterrupt:
        print("\nTerminating transcription...")
        stop_transcription = True
        transcription_thread.join()