
# AI meeting note taker and action item generator

This project is innovative solution about AI meeting enhancing by applying bot which can join, record, transcribe meeting as well as action item gerneration.

## Author

- [@AI-meeting-enhancer](https://www.github.com/AI-meeting-enhancer)
## Run Locally [ Ubuntu only temperally ]

### 1. Clone the project

```bash
  https://github.com/AI-meeting-enhancer/MeetingBot-Enhancer.git
```

### 2. Go to the project directory

```bash
  cd MeetingBot-Enhancer
```

### 3. Install dependencies

```bash
  pip install -r requirements.txt
```

### 4. Start the server
Download proper SDK from Zoom marketplace and copy it into ./bots/zoombot/lib/zoomsdk<br>
Bot run with composer build:
```bash
  cd ./bots/zoom_bot/
  docker compose up
```
Enhancer run:
```bash
python3 main.py -t g
```
Bot Run:
```bash
docker run -v ./sock/deepgramApi/:/tmp/zoom_bot/sock/ -v .:/tmp/zoom_bot/ zoom_bot-zoomsdk
```
```bash
docker run -v ./sock/googleApi/:/tmp/zoom_bot/sock/ -v .:/tmp/zoom_bot/ zoom_bot-zoomsdk
```

## Support

For support, email yaskivartur0830@gmail.com or join our Slack channel.
