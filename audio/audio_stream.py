import threading
import socket
from google.cloud import speech
from .socket_connection import connect_unix_socket
from transcription.transcription_handler import save_transcription_in_real_time
from config.settings import Config
from transcription.summary_generator import generate_meeting_summary

client = speech.SpeechClient()

def audio_generator(sock):
    buffer_size = 4096
    while True:
        try:
            data = sock.recv(buffer_size)
            if not data:
                break
            
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
        
        except Exception as e:
            print(f"Socket error: {e}")
            break

def stream_audio_to_text():
    sock = connect_unix_socket()
    if not sock:
        return

    audio_stream = audio_generator(sock)

    # Prepare to send audio to the Speech API
    requests = []
    current_display_name = None

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