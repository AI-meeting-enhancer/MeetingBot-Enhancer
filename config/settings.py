import os

class Config:
    GOOGLE_APPLICATION_CREDENTIALS = "./credentials/zoom-service-account-key.json"
    SOCKET_PATH = './bots/zoom_bot/sock/meeting.sock'
    OUTPUT_FILE = "./tmp/meeting_temp.txt"
    SUMMARY_TEMPLATE = "./credentials/summary_template.html"
    SAMPLE_RATE = 32000
    MIN_SPEAKER_COUNT = 2
    MAX_SPEAKER_COUNT = 5