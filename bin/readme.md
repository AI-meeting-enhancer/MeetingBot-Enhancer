
# AI meeting note taker and action item generator

This project is innovative solution about AI meeting enhancing by applying bot which can join, record, transcribe meeting as well as action item gerneration.

## Author

- [@AI-meeting-enhancer](https://www.github.com/AI-meeting-enhancer)
## Run Locally [ Ubuntu only temperally ]

### Preparation
1. [Docker environment Installation](https://www.docker.com/)
1. [Zoom Account](https://support.zoom.us/hc/en-us/articles/207278726-Plan-Types-)
1. [Zoom Meeting SDK Credentials](https://marketplace.zoom.us/) in "./bots/zoom_bot/config.toml" file
    1. Client ID
    1. Client Secret
1. Install [Python](https://www.python.org/downloads/)
1. [Google STT API](https://console.cloud.google.com/)'s JSON credential file in "/credentials" directory

### 1. Clone the project

```bash
  https://github.com/AI-meeting-enhancer/MeetingBot-Enhancer.git
```

### 2. Go to the project directory

```bash
  cd MeetingBot-Enhancer
```

### 3. Install dependencies

Install and activate virtual environment
```bash
  python -m venv venv
```
```bash
   source venv/bin/activate
```

Install necessary modules
```bash
  pip install -r requirements.txt
```

### 4. Start the server
Download proper SDK from Zoom marketplace and copy it into ./bots/zoombot/lib/zoomsdk<br>
```bash
  cd ./bots/zoom_bot/
```
Bot Run with Google STT API for speech recognition:
```bash
docker run -v ./sock/googleApi/:/tmp/zoom_bot/sock/ -v .:/tmp/zoom_bot/ zoom_bot-zoomsdk
```
Or Run with Deepgram API for speech recognition:
```bash
docker run -v ./sock/deepgramApi/:/tmp/zoom_bot/sock/ -v .:/tmp/zoom_bot/ zoom_bot-zoomsdk
```

Enhancer run:
```bash
python3 main.py -t g
```

## Support

For support, email yaskivartur0830@gmail.com or join our Slack channel.
