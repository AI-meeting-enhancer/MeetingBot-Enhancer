import threading
import json
import struct
from google.cloud import speech
from .socket_connection import connect_unix_socket
from transcription.transcription_handler import save_transcription_in_real_time
from config.settings import Config
from transcription.summary_generator import generate_meeting_summary
import queue

client = speech.SpeechClient()
speaker_buffer = {}
user_threads = {}  # Dictionary to hold threads by user index
audio_queues = {}  # Dictionary to hold audio queues by user index
user_mapping = {}  # Map to keep track of user identifiers

def audio_generator(sock):
    index_size = 4  # Size for the user index
    display_name_size = 50  # Size for the display name
    buffer_size = 4096

    while True:
        try:
            data = sock.recv(buffer_size)
            if not data:
                break
            if len(data) < index_size + display_name_size:
                print("Received data is too short to contain user ID and display name.")
                continue
            
            # Extract user index
            user_index = struct.unpack('<I', data[:index_size])[0]  # Read first 4 bytes as user index
            
            # Extract display name
            display_name_bytes = data[index_size:index_size + display_name_size]
            display_name = display_name_bytes.split(b'\x00', 1)[0].decode('utf-8')  # Decode and strip nulls

            # The rest is audio data
            audio_data = data[index_size + display_name_size:]

            yield audio_data, user_index, display_name  # Yield audio data, user index, and display name
        except Exception as e:
            print(f"Socket error: {e}")
            break

def process_audio(user_id, audio_queue, display_name):
    rate = 32000

    config = speech.RecognitionConfig(
        encoding=speech.RecognitionConfig.AudioEncoding.LINEAR16,
        sample_rate_hertz=rate,
        language_code="en-US",
        enable_automatic_punctuation=True
    )

    while True:  # Keep the process running to handle reconnections
        try:
            # Create a streaming configuration
            streaming_config = speech.StreamingRecognitionConfig(
                config=speech.RecognitionConfig(
                    encoding=speech.RecognitionConfig.AudioEncoding.LINEAR16,
                    sample_rate_hertz=Config.SAMPLE_RATE,
                    language_code="en-US",
                    enable_automatic_punctuation=True,
                ),
                interim_results=True,
            )

            requests = (speech.StreamingRecognizeRequest(audio_content=content) for content in iter(audio_queue.get, None))

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
                    speaker_buffer[display_name] = ""  # Clear buffer for the next round

        except Exception as e:
            # Handle specific exceptions as needed
            if "Audio Timeout Error" in str(e):
                pass
                # Continue the loop to wait for new audio data instead of breaking

    print(f"Thread for user ID {user_id} (Display Name: {display_name}) finished.")

def handle_stream(sock):
    for audio_data, user_index, display_name in audio_generator(sock):
        # print(f"Received audio data from user ID: {user_index}, Display Name: {display_name}")

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
            
            print(f"New user detected: {user_id}. Creating a new thread for this user.")
            
            thread = threading.Thread(target=process_audio, args=(user_id, audio_queue, display_name))
            user_threads[user_id] = thread
            thread.start()
            audio_queue.put(audio_data)  # Start processing with the first audio chunk

    # After breaking out of the loop, generate the meeting summary
    generate_meeting_summary()

def stream_audio_to_text():
    sock = connect_unix_socket()
    try:
        handle_stream(sock)
    finally:
        sock.close()
        print("Socket closed.")