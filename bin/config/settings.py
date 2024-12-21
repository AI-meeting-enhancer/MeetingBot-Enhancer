class Config:
    GOOGLE_APPLICATION_CREDENTIALS = "./credentials/zoom-service-account-key.json"
    SOCKET_PATH = './bots/zoom_bot/sock/meeting.sock'
    OUTPUT_FILE = "./tmp/meeting_temp_google.txt"
    SUMMARY_TEMPLATE = "./templates/summary_template.html"
    RETURN_JSON_TEMPLATE = "./templates/json_template.json"
    SAMPLE_RATE = 32000
    MEETING_NAME = ""