import os
from datetime import datetime
import google.generativeai as genai
from config.settings import Config

def generate_meeting_summary():
    if not os.path.exists(Config.OUTPUT_FILE) or os.path.getsize(Config.OUTPUT_FILE) == 0:
        print("No transcription data available. Skipping summary generation.")
        return

    with open(Config.OUTPUT_FILE, 'r') as file:
        transcription_text = file.read()

    model = genai.GenerativeModel("gemini-1.5-flash")
    response = model.generate_content(f"Provide meeting notes and action items for this transcription. Use current timestamp:\n\n{transcription_text}")
    
    if hasattr(response, 'text'):
        print("\nMeeting Summary:\n", response.text)
        with open(f"./output/Meeting_Note_{datetime.now().strftime('%Y-%m-%d_%H-%M-%S')}.txt", "w+") as file:
            file.write(f"{datetime.now().strftime('%Y-%m-%d %H:%M')}\n\n {response.text}")
        os.remove(Config.OUTPUT_FILE)
    else:
        print("Error: No summary generated.")