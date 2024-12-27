import os
import google.generativeai as genai
from config.settings import Config

def modify_transcription():

    # Check if the transcription file exists and is not empty
    if not os.path.exists(Config.OUTPUT_FILE) or os.path.getsize(Config.OUTPUT_FILE) == 0:
        print("No transcription data available. Skipping modification.")
        return

    try:
        # Read the transcription text from the output file
        with open(Config.OUTPUT_FILE, 'r') as file:
            transcription_text = file.read()

        # Initialize the generative AI model
        model = genai.GenerativeModel("gemini-1.5-pro")
        # Create a prompt for the AI model to summarize the meeting
        prompt = (
            """Please review the following meeting transcription and correct any errors based on the context of the entire conversation. 
            Ensure that the corrected transcription accurately reflects the intended dialogue.""" + f"\nMeeting Transcription: {transcription_text}"
        )
        
        # Generate content using the AI model
        response = model.generate_content(prompt)
        
        # Check if the response has text
        if hasattr(response, 'text'):
            # Check if the response is empty
            if not response.text:
                print("Error: Received an empty response from the model.")
                return

            with open(Config.OUTPUT_FILE, "w") as file:
                file.write(response.text)
            # Remove the original transcription file
        else:
            print("Error: No modification result.")
    except Exception as e:
        # Handle any exceptions that occur during the process
        print(f"An error occurred: {e}")