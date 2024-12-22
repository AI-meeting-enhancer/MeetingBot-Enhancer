class Config:
    GOOGLE_APPLICATION_CREDENTIALS = "./credentials/zoom-service-account-key.json"
    SOCKET_PATH = './bots/zoom_bot/sock/meeting.sock'
    OUTPUT_FILE = "./tmp/meeting_temp_google.txt"
    SUMMARY_TEMPLATE = "./templates/zoom/summary_template.html"
    RETURN_JSON_TEMPLATE = "./templates/zoom/json_template.json"
    INSTRUCTION_FOR_SUMMARY = "./templates/default_ins.txt"
    SAMPLE_RATE = 32000
    MEETING_NAME = ""