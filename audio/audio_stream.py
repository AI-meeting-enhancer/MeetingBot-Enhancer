import threading
<<<<<<< HEAD
import socket
=======
import json
import struct
>>>>>>> again
from google.cloud import speech
from .socket_connection import connect_unix_socket
from transcription.transcription_handler import save_transcription_in_real_time
from config.settings import Config
from transcription.summary_generator import generate_meeting_summary
import queue

client = speech.SpeechClient()
<<<<<<< HEAD
=======
speaker_buffer = {}
user_threads = {}  # Dictionary to hold threads by user index
audio_queues = {}  # Dictionary to hold audio queues by user index
>>>>>>> again

def audio_generator(sock):
    buffer_size = 4096
    while True:
        try:
            data = sock.recv(buffer_size)
            if not data:
                break
<<<<<<< HEAD
            
            # Ensure data is valid and extract display name and audio
            if len(data) < 2:
                continue  # Not enough data to extract node ID and display name length

            node_id = data[0]  # Node ID (1 byte)
            display_name_length = data[1]  # Length of display name (1 byte)

            if len(data) < 2 + display_name_length:
                continue  # Not enough data to extract the full display name

            # Extract display name safely
            display_name = data[2:2 + display_name_length].decode('utf-8', errors='ignore')  # Ignore errors if any
            audio_data = data[2 + display_name_length:]  # Remaining data is audio

            yield (display_name, audio_data)  # Yield tuple of (display_name, audio_data)
        
=======
            if len(data) < 4:
                print("Received data is too short to contain an index.")
                continue
            
            index = struct.unpack('<I', data[:4])[0]  # Read the first 4 bytes as an integer
            audio_data = data[4:]  # The rest is audio data
            
            yield audio_data, index  # Yield both audio data and index
>>>>>>> again
        except Exception as e:
            print(f"Socket error: {e}")
            break

<<<<<<< HEAD
def stream_audio_to_text():
    sock = connect_unix_socket()
    if not sock:
        return

    audio_stream = audio_generator(sock)

    # Prepare to send audio to the Speech API
    requests = []
    current_display_name = None
=======
def process_audio(user_index, audio_queue):
    rate = 32000

    config = speech.RecognitionConfig(
        encoding=speech.RecognitionConfig.AudioEncoding.LINEAR16,
        sample_rate_hertz=rate,
        language_code="en-US",
        enable_automatic_punctuation=True
    )
>>>>>>> again

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

<<<<<<< HEAD
    # Create a generator for the requests
    def generate_requests():
        for display_name, audio in audio_stream:
            yield speech.StreamingRecognizeRequest(audio_content=audio)

    # Start the streaming recognition
    responses = client.streaming_recognize(config=streaming_config, requests=generate_requests())

    # Process responses
    for response in responses:
        if not response.results:
            continue

        result = response.results[0]
        if not result.alternatives:
            continue

        transcript = result.alternatives[0].transcript
        current_display_name = response.results[0].alternatives[0].words[0].speaker_tag if response.results[0].alternatives[0].words else None

        if result.is_final:
            save_transcription_in_real_time(current_display_name, transcript, Config.OUTPUT_FILE)

    sock.close()
    print("Socket closed.")
    generate_meeting_summary()

# To run the stream_audio_to_text in a separate thread
if __name__ == "__main__":
    transcription_thread = threading.Thread(target=stream_audio_to_text)
    transcription_thread.start()

    try:
        transcription_thread.join()
    except KeyboardInterrupt:
        print("\nTerminating transcription...")
        transcription_thread.join()
=======
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
>>>>>>> again
