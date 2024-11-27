import threading
from google.cloud import speech
from .socket_connection import connect_unix_socket
from transcription.transcription_handler import save_transcription_in_real_time
from config.settings import Config
from transcription.summary_generator import generate_meeting_summary

client = speech.SpeechClient()

speaker_buffer = {}

def audio_generator(sock):
    buffer_size = 4096
    while True:
        try:
            data = sock.recv(buffer_size)
            if not data:
                break
            yield data
        except Exception as e:
            print(f"Socket error: {e}")
            break

def stream_audio_to_text():
    sock = connect_unix_socket()
    # Configure Speech-to-Text API
    
    rate = 32000

    # Google Cloud Speech-to-Text API config with dynamic diarization
    diarization_config = speech.SpeakerDiarizationConfig(
        enable_speaker_diarization=True,
        min_speaker_count=2,
        max_speaker_count=5
    )

    config = speech.RecognitionConfig(
        encoding=speech.RecognitionConfig.AudioEncoding.LINEAR16,
        sample_rate_hertz=rate,
        language_code="en-US",
        enable_automatic_punctuation=True,
        diarization_config=diarization_config
    )

    streaming_config = speech.StreamingRecognitionConfig(
        config=config,
        interim_results=True
    )


    # Send the audio stream to the Google Speech API
    requests = (speech.StreamingRecognizeRequest(audio_content=content) for content in audio_generator(sock))
    
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
            speaker_number = result.alternatives[0].words[0].speaker_tag if result.alternatives[0].words else None

            if result.is_final:
                print(f"Final Transcript: {transcript}")

                if speaker_number:
                    if speaker_number not in speaker_buffer:
                        speaker_buffer[speaker_number] = ""
                    speaker_buffer[speaker_number] += f" {transcript}"

                    save_transcription_in_real_time(speaker_number, speaker_buffer[speaker_number], Config.OUTPUT_FILE )
                    speaker_buffer[speaker_number] = ""  # Clear buffer for the next round

    except Exception as e:
        print("Error during streaming:", e)
    finally:
        sock.close()
        print("Socket closed.")
        generate_meeting_summary()

    # Process responses (similar to your original implementation)
    sock.close()