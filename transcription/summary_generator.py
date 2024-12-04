import os, re
from datetime import datetime
import google.generativeai as genai
from config.settings import Config

def extract_html(input_text):
    # Remove code block markers (```) and "html" label
    cleaned_text = re.sub(r'```html|```', '', input_text)

    return cleaned_text.strip()  # Remove leading/trailing whitespace

def generate_meeting_summary():
    if not os.path.exists(Config.OUTPUT_FILE) or os.path.getsize(Config.OUTPUT_FILE) == 0:
        print("No transcription data available. Skipping summary generation.")
        return

    with open(Config.OUTPUT_FILE, 'r') as file:
        transcription_text = file.read()

    with open(Config.SUMMARY_TEMPLATE) as template_file:
        template = template_file.read()

    model = genai.GenerativeModel("gemini-1.5-pro")
    response = model.generate_content(f"{template}########## My name is Yaskiv.This is template. use current date for title's date. Make a summary html with this style for following meeting content.Give me only html, no desciption. Don't insert timestamp and ``` things in answer. I need only html:\n\n{transcription_text}")
    
    
    if hasattr(response, 'text'):
        print("\nMeeting Summary:\n", response.text)
        with open(f"./output/Meeting_Note_{datetime.now().strftime('%Y-%m-%d_%H-%M-%S')}.html", "w+") as file:
            file.write(f"{extract_html(response.text)}")
        os.remove(Config.OUTPUT_FILE)
    else:
        print("Error: No summary generated.")