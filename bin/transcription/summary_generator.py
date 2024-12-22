import os
import re
import json
from datetime import datetime
import google.generativeai as genai
from config.settings import Config
from jinja2 import Template

def extract_content(input_text):
    # Remove code block markers (```) and "json" label from the input text
    cleaned_text = re.sub(r'```json|```', '', input_text)
    return cleaned_text.strip()  # Remove leading/trailing whitespace

def generate_meeting_summary():
    # Get the current date
    current_date = datetime.now()
    meeting_date = current_date.strftime("%m/%d/%Y")  # Format the date

    # Check if the transcription file exists and is not empty
    if not os.path.exists(Config.OUTPUT_FILE) or os.path.getsize(Config.OUTPUT_FILE) == 0:
        print("No transcription data available. Skipping summary generation.")
        return

    # try:
    # Read the transcription text from the output file
    with open(Config.OUTPUT_FILE, 'r') as file:
        transcription_text = file.read()

    # Read the HTML template for the summary
    with open(Config.SUMMARY_TEMPLATE) as template_file:
        html_template = template_file.read()
        
    # Read the JSON template for retrieving from Gemini
    with open(Config.RETURN_JSON_TEMPLATE) as json_template:
        json_template = json_template.read()
        
        
    # Read the JSON template for retrieving from Gemini
    with open(Config.INSTRUCTION_FOR_SUMMARY) as instruction_file:
        instruction = instruction_file.read()

    # Initialize the generative AI model
    model = genai.GenerativeModel("gemini-1.5-pro")
    # Create a prompt for the AI model to summarize the meeting
    prompt = (
        f"{instruction}:\n{json_template}\nMeeting Transcription: {transcription_text}"
    )
    
    # Generate content using the AI model
    response = model.generate_content(prompt)
    
    # Check if the response has text
    if hasattr(response, 'text'):
        # Clean the response text
        json_response = extract_content(response.text)
        
        # Check if the response is empty
        if not json_response:
            print("Error: Received an empty response from the model.")
            return
        
        # Attempt to parse the JSON response
        try:
            data = json.loads(json_response)
            data.update(json.loads('{"meeting_name":"'+Config.MEETING_NAME+'", "meeting_date":"'+meeting_date+'"}'))
            
        except json.JSONDecodeError as e:
            print("Error: Response is not valid JSON.", e)
            return
        
        # Render the HTML summary using the Jinja2 template
        template = Template(html_template)
        rendered_html = template.render(data)

        # Save the rendered HTML to a file with a timestamp
        output_file_path = f"./output/Meeting_Note_{datetime.now().strftime('%Y-%m-%d_%H-%M-%S')}.html"
        with open(output_file_path, "w+") as file:
            file.write(rendered_html)
        # Remove the original transcription file
        os.remove(Config.OUTPUT_FILE)
        quit()
    else:
        print("Error: No summary generated.")
    # except Exception as e:
    #     # Handle any exceptions that occur during the process
    #     print(f"An error occurred: {e}")
