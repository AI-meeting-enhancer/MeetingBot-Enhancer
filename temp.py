import threading, os, json
from config.settings import Config

from jinja2 import Template
os.environ["GOOGLE_APPLICATION_CREDENTIALS"] = Config.GOOGLE_APPLICATION_CREDENTIALS

from audio.audio_stream import stream_audio_to_text
from transcription.summary_generator import generate_meeting_summary


json_response = """
{
  "meeting_name": "Zoom Meeting SDK setup",
  "meeting_date": "",
  "recap": "Discussed setting up Zoom Meeting SDK on Linux using Docker, including building a container with ALSA and PulseAudio for raw audio capture. Walkthrough of the setup process, covering prerequisites, cloning the repository, downloading the SDK files, and initial app configuration.",
  "actions": [
    "Run `docker-compose up` command to build the container with ALSA and PulseAudio.",
    "Clone the Zoom SDK repository.",
    "Download the Zoom Linux SDK files from the Zoom App Marketplace.",
    "Create a new Zoom Meeting SDK app and name it (e.g., 'sample bot').",
    "Enable the Meeting SDK option in the app configuration."
  ],
  "summary_items": [
    {
      "title": "Docker Setup",
      "content": "A Docker container will be used to capture raw audio data in a headless manner. The container includes a base Linux OS, ALSA, and PulseAudio. The command `docker-compose up` is used to build and run the container."
    },
    {
      "title": "SDK Setup",
      "content": "The Zoom Linux SDK files need to be downloaded.  These files include the shared library and other necessary library files for the C++ program. The files can be downloaded from the Zoom App Marketplace."
    },
    {
      "title": "App Configuration",
      "content": "A new Zoom Meeting SDK app needs to be created.  The Meeting SDK option should be enabled within the app's settings. An example app name is 'sample bot'."
    }
  ]
}
"""


# with open("./config/summary_template.html") as template_file:
#     html_template = template_file.read()

# data = json.loads(json_response)
# template = Template(html_template)
# rendered_html = template.render(data)


# print(rendered_html)

generate_meeting_summary()