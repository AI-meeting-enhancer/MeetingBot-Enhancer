import os
import re
import json
from datetime import datetime
import google.generativeai as genai
from config.settings import Config
from jinja2 import Template

def extract_content(input_text):
    # Remove code block markers (```) and "html" label
    cleaned_text = re.sub(r'```json|```', '', input_text)
    return cleaned_text.strip()  # Remove leading/trailing whitespace

def generate_meeting_summary():

    name = input("Input your name:---> ")
    current_date = datetime.now()
    meeting_date = current_date.strftime("%m/%d/%Y")

    if not os.path.exists(Config.OUTPUT_FILE) or os.path.getsize(Config.OUTPUT_FILE) == 0:
        print("No transcription data available. Skipping summary generation.")
        return

    try:
        with open(Config.OUTPUT_FILE, 'r') as file:
            transcription_text = file.read()

        with open(Config.SUMMARY_TEMPLATE) as template_file:
            html_template = template_file.read()

        model = genai.GenerativeModel("gemini-1.5-pro")
        prompt = (
            """You are an AI meeting assistant. Summarize the following transcription using this JSON structure:\n
            {
                "meeting_name": '""" + name + """',
                "meeting_date":'(""" + meeting_date + """)',
                "recap": "<Brief meeting summary>",
                "actions": [
                    "<Action 1>",
                    "<Action 2>",
                    "<Action 3>"
                ],
                "summary_items": [
                    {
                    "title": "<Section Title 1>",
                    "content": "<Section Content 1>"
                    },
                    {
                    "title": "<Section Title 2>",
                    "content": "<Section Content 2>"
                    },
                    {
                    "title": "<Section Title 3>",
                    "content": "<Section Content 3>"
                    }
                ]
            }""" + f"\nMeeting Transcription: {transcription_text}"
        )
        
        response = model.generate_content(prompt)
        
        if hasattr(response, 'text'):
            json_response = extract_content(response.text)
            print("Raw response from model:", json_response)  # Debugging line
            
            if not json_response:
                print("Error: Received an empty response from the model.")
                return
            
            try:
                data = json.loads(json_response)
            except json.JSONDecodeError as e:
                print("Error: Response is not valid JSON.", e)
                return
            
            template = Template(html_template)
            rendered_html = template.render(data)

            print("\nMeeting Summary:\n", rendered_html)
            output_file_path = f"./output/Meeting_Note_{datetime.now().strftime('%Y-%m-%d_%H-%M-%S')}.html"
            with open(output_file_path, "w+") as file:
                file.write(rendered_html)
            os.remove(Config.OUTPUT_FILE)
        else:
            print("Error: No summary generated.")
    except Exception as e:
        print(f"An error occurred: {e}")