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

def audio_generator(sock):
    buffer_size = 4096
    while True:
        try:
            data = sock.recv(buffer_size)
            if not data:
                break
            if len(data) < 4:
                print("Received data is too short to contain an index.")
                continue
            
            index = struct.unpack('<I', data[:4])[0]  # Read the first 4 bytes as an integer
            audio_data = data[4:]  # The rest is audio data
            
            yield audio_data, index  # Yield both audio data and index
        except Exception as e:
            print(f"Socket error: {e}")
            break

def process_audio(user_index, audio_queue):
    rate = 32000

    config = speech.RecognitionConfig(
        encoding=speech.RecognitionConfig.AudioEncoding.LINEAR16,
        sample_rate_hertz=rate,
        language_code="en-US",
        enable_automatic_punctuation=True
    )

    streaming_config = speech.StreamingRecognitionConfig(
        config=config,
        interim_results=True
    )

    requests = (speech.StreamingRecognizeRequest(audio_content=content) for content in iter(audio_queue.get, None))

    responses = client.streaming_recognize(config=streaming_config, requests=requests)
    
    try:
        for response in responses:
            if not response.results:
                continue

            result = response.results[0]
            if not result.alternatives:
                continue

            # Extract transcript and speaker information
            transcript = result.alternatives[0].transcript
            
            if result.is_final:
                # Use user_index as the speaker identifier
                if user_index not in speaker_buffer:
                    speaker_buffer[user_index] = ""
                speaker_buffer[user_index] += f" {transcript}"

                # Save the transcription in real-time
                save_transcription_in_real_time(user_index, speaker_buffer[user_index], Config.OUTPUT_FILE)
                speaker_buffer[user_index] = ""  # Clear buffer for the next round

    except Exception as e:
        print("Error during streaming:", e)
    finally:
        print(f"Thread for user index {user_index} finished.")
        # generate_meeting_summary()

def handle_stream(sock):
    for audio_data, index in audio_generator(sock):
        if index in user_threads:
            # If thread exists, put audio data in the existing queue
            audio_queues[index].put(audio_data)
        else:
            # Create a new queue and thread for the user
            audio_queue = queue.Queue()
            audio_queues[index] = audio_queue
            
            # Print message for new user
            print(f"New user detected: {index}. Creating a new thread for this user.")
            
            thread = threading.Thread(target=process_audio, args=(index, audio_queue))
            user_threads[index] = thread
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