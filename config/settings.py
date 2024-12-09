import os

class Config:
    GOOGLE_APPLICATION_CREDENTIALS = "./credentials/zoom-service-account-key.json"
    SOCKET_PATH = './bots/zoom_bot/sock/meeting.sock'
    OUTPUT_FILE = "./tmp/meeting_temp.txt"
    SUMMARY_TEMPLATE = "./config/summary_template.html"
    SAMPLE_RATE = 32000