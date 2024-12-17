import threading
import struct, time
from google.cloud import speech
from google.api_core.exceptions import OutOfRange
from .socket_connection import connect_unix_socket
from transcription.transcription_handler import save_transcription_in_real_time
from config.settings import Config
from transcription.summary_generator import generate_meeting_summary
import queue
from deepgram import (
    DeepgramClient,
    LiveTranscriptionEvents,
    LiveOptions,
)
import os, sys, math
from dotenv import load_dotenv
from itertools import chain, tee

RED = "\033[0;31m"
GREEN = "\033[0;32m"
YELLOW = "\033[0;33m"
WHITE = "\033[0;37m"

last_content_length = 0

load_dotenv()

deepgram_api_key = os.getenv('DEEPGRAM_API_KEY')

speaker_buffer = {}
user_threads = {}  # Dictionary to hold threads by user index
audio_queues = {}  # Dictionary to hold audio queues by user index
user_mapping = {}  # Map to keep track of user identifiers
dg_connection = None
is_finals = []

def audio_generator(sock):
    index_size = 4  # Size for the user index
    display_name_size = 50  # Size for the display name

    while True:
        try:
            # Read the length of the incoming message (4 bytes)
            length_bytes = sock.recv(4)
            if not length_bytes:
                break  # Connection closed

            # Unpack the length (network byte order to host byte order)
            message_length = struct.unpack('<I', length_bytes)[0]  # '!I' means big-endian unsigned int

            # Read the actual message based on the lengt
            data = sock.recv(message_length)

            if not data:
                print(f"Error : No data received from socket")
                break
            if len(data) < index_size + display_name_size:
                print("Received data is too short to contain user ID and display name.")
                continue
            
            # Extract user index
            user_index = struct.unpack('<I', data[:index_size])[0]  # Read first 4 bytes as user index
            
            try:
                # Extract display name
                display_name_bytes = data[index_size:index_size + display_name_size]
                display_name = display_name_bytes.split(b'\x00', 1)[0].decode('utf-8')  # Decode and strip nulls
            except UnicodeDecodeError as e:
                print(f"Error decoding display name {len(data)}: {e}")
                continue
            # The rest is audio data
            audio_data = data[index_size + display_name_size:]

            yield audio_data, user_index, display_name  # Yield audio data, user index, and display name
        except Exception as e:
            print(f"Socket error: {e}")
            break

def process_audio_deepgram(user_id, audio_queue, display_name):
    global is_finals
    silent_audio_interval = 5

    try:
        deepgram: DeepgramClient = DeepgramClient(deepgram_api_key)
        dg_connection = deepgram.listen.websocket.v("1")

        def on_open(self, open, **kwargs):
            pass

        def on_message(self, result, **kwargs):
            global is_finals
            try:
                sentence = result.channel.alternatives[0].transcript
                if not sentence:
                    return
                if result.is_final:
                    # print(f"[{display_name}] : {sentence}")
                    is_finals.append(sentence)
                    if result.speech_final:
                        utterance = " ".join(is_finals)
                        update_terminal_print(f"{display_name} : {utterance}\n", GREEN)
                        # print(f"[{display_name}] Speech Final: {utterance}")
                        save_transcription_in_real_time(display_name, utterance, Config.OUTPUT_FILE)
                        is_finals = []
                else:
                    utterance = " ".join(is_finals)
                    update_terminal_print(f"{display_name} : {utterance} {sentence}\r", RED)
                    pass
                    # print(f"[{display_name}] Interim Results: {sentence}")
            except Exception as e:
                print(f"[{display_name}] Error processing message: {e}")

        def on_close(self, close, **kwargs):
            if is_finals:
                final_utterance = " ".join(is_finals)
                save_transcription_in_real_time(display_name, final_utterance, Config.OUTPUT_FILE)
                is_finals.clear()  # Clear the list after saving

        dg_connection.on(LiveTranscriptionEvents.Open, on_open)
        dg_connection.on(LiveTranscriptionEvents.Transcript, on_message)
        dg_connection.on(LiveTranscriptionEvents.Close, on_close)

        options: LiveOptions = LiveOptions(
            model="nova-2",
            language="en-US",
            smart_format=True,
            encoding="linear16",
            channels=1,
            sample_rate=32000,
            interim_results=True,
            utterance_end_ms="1000",
            vad_events=True,
            endpointing=400,
            punctuate=True,
        )

        if not dg_connection.start(options):
            print(f"[{display_name}] Failed to connect to Deepgram")
            return
        def send_silent_audio():
            while dg_connection and dg_connection.is_connected:
                time.sleep(silent_audio_interval)
                silent_audio = b'\x00' * 32000  # 1 second of silent audio at 32kHz
                dg_connection.send(silent_audio)
        # Start a thread to send silent audio periodically
        silent_audio_thread = threading.Thread(target=send_silent_audio)
        silent_audio_thread.daemon = True
        silent_audio_thread.start()

        while dg_connection and dg_connection.is_connected:
            try:
                # Fetch audio data
                audio_data = audio_queue.get(timeout=5)
                if audio_data:
                    dg_connection.send(audio_data)
                else:
                    # Send silent audio to keep the connection alive
                    silent_audio = b'\x00' * 32000  # 1 second of silent audio at 32kHz
                    dg_connection.send(silent_audio)
            except queue.Empty:
                continue
            except Exception as e:
                break

    except Exception as e:
        print(f"[{display_name}] Could not open connection: {e}")
    finally:
        # Ensure the connection is properly closed
        if dg_connection and dg_connection.is_connected:
            dg_connection.finish()

def update_terminal_print(content: str, colorCode: str = WHITE) -> None:
    global last_content_length

    # get the terminal size
    terminal_size = os.get_terminal_size()
    line_length = terminal_size.columns
    num_lines = math.ceil(last_content_length / line_length)
    for i in range(num_lines):
        if i != 0:
            sys.stdout.write("\033[F")  # Move cursor up one line
        sys.stdout.write("\033[K")  # Clear the line
    
    sys.stdout.write(colorCode)
    sys.stdout.write(content)
    
    if content[-1] == "\r":
        last_content_length = len(content) - 1
    elif content[-1] == "\n":
        last_content_length = 0

    sys.stdout.write(WHITE)
    pass

def process_audio_google(user_id, audio_queue, display_name):
    config = speech.RecognitionConfig(
        encoding=speech.RecognitionConfig.AudioEncoding.LINEAR16,
        sample_rate_hertz=Config.SAMPLE_RATE,
        language_code="en-US",
        enable_automatic_punctuation=True
    )
    startTime = time.time()
    client = speech.SpeechClient()
    while True:  # Keep the process running to handle reconnections
        try:                  
            # Create a streaming configuration
            streaming_config = speech.StreamingRecognitionConfig(
                config=config,
                interim_results=True,
            )
            pre_audio = None
            audio = iter(audio_queue.get, None)
            if pre_audio:
                audio = chain(pre_audio, audio)
            requests = (speech.StreamingRecognizeRequest(audio_content=content) for content in audio)
            responses = client.streaming_recognize(config=streaming_config, requests=requests)
            for response in responses:
                if not response.results:
                    continue

                result = response.results[0]
                if not result.alternatives:
                    continue

                # Extract transcript and speaker information
                transcript = result.alternatives[0].transcript
                
                if result.is_final:
                    # Use display_name instead of user_id
                    if display_name not in speaker_buffer:
                        speaker_buffer[display_name] = ""
                    speaker_buffer[display_name] += f" {transcript}"

                    # Save the transcription in real-time using display name
                    save_transcription_in_real_time(display_name, speaker_buffer[display_name], Config.OUTPUT_FILE)
                    update_terminal_print(f"{display_name} : {transcript}\n", GREEN)
                    speaker_buffer[display_name] = ""  # Clear buffer for the next round
                else:
                    update_terminal_print(f"{display_name} : {transcript}\r", RED)
                
                if time.time() - startTime > 100:
                    pre_audio = tee(audio)
                    print(f"--------- Current Queue Size: {audio_queue.qsize()} ----------")
                    startTime = time.time()
                    print("Reconnecting Google Cloud Speech ...")
                    
                    # -------- Output temp result as final in case of timeout
                    # Use display_name instead of user_id
                    if display_name not in speaker_buffer:
                        speaker_buffer[display_name] = ""
                    speaker_buffer[display_name] += f" {transcript}"

                    # Save the transcription in real-time using display name
                    save_transcription_in_real_time(display_name, speaker_buffer[display_name], Config.OUTPUT_FILE)
                    update_terminal_print(f"{display_name} : {transcript}\n", GREEN)
                    speaker_buffer[display_name] = ""  # Clear buffer for the next round
                    break
            pre_audio = None
            
        # ignore rate limit
        except OutOfRange as e:
            print(f"[Rate limit exceeded]:{e}")
            continue

        # except Exception as e:
        #     print(f"Exception:{e}")
        #     # Handle specific exceptions as needed
        #     if "Audio Timeout Error" in str(e):
        #         pass
        #         # Continue the loop to wait for new audio data instead of breaking

def handle_stream(sock):
    for audio_data, user_index, display_name in audio_generator(sock):

        # Check if the user index already exists in user_mapping
        if user_index not in user_mapping:
            user_mapping[user_index] = len(user_mapping)  # Use the current size as the new user ID

        user_id = user_mapping[user_index]

        if user_id in user_threads:
            # If thread exists, put audio data in the existing queue
            audio_queues[user_id].put(audio_data)
        else:
            # Create a new queue and thread for the user
            audio_queue = queue.Queue()
            audio_queues[user_id] = audio_queue
            
            if Config.OUTPUT_FILE.find("google")>=0:
                thread = threading.Thread(target=process_audio_google, args=(user_id, audio_queue, display_name))
            else:
                thread = threading.Thread(target=process_audio_deepgram, args=(user_id, audio_queue, display_name))
            user_threads[user_id] = thread
            thread.start()
            audio_queue.put(audio_data)  # Start processing with the first audio chunk


def stream_audio_to_text():
    sock = connect_unix_socket()
    try:
        handle_stream(sock)
    finally:
        sock.close()
        
        print("Socket closed.")
        # After breaking out of the loop, generate the meeting summary
        generate_meeting_summary()