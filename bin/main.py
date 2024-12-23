from config.settings import Config
import os, argparse, subprocess, time

os.environ["GOOGLE_APPLICATION_CREDENTIALS"] = Config.GOOGLE_APPLICATION_CREDENTIALS

from audio.audio_stream import stream_audio_to_text
from transcription.modify_transcription import modify_transcription


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


    # Delete the output file before run the Bot
    try:
        if os.path.exists(Config.SOCKET_PATH):
            os.remove(Config.SOCKET_PATH)
    except Exception as e:
        print(f"Error deleting file: {e}")


    os.chdir("bots/zoom_bot")
    # Prepare the command as a list
    command = [
        "./build_app/zoomsdk",  # Ensure this is the correct executable path
        "RawAudio", "-t", "-s", "--sock-dir", "sock/googleApi", "--sock-file", "meeting.sock"
    ]

    # Start the C++ application
    bot_process = subprocess.Popen(command, stdout=subprocess.PIPE, stderr=subprocess.PIPE)

    # Wait until Bot is ready
    os.chdir("../../")
    while True:
        if os.path.exists(Config.SOCKET_PATH):
            print("Bot is started successfully.\n")
            break
        time.sleep(1)

    # Now that the zoomsdk has completed and the socket file is ready, start transcription
    start_real_time_transcription()
    