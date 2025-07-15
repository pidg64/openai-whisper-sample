# Voice Transcription System

This project allows you to transcribe audio in English using a `faster-whisper`, a reimplementation of OpenAI's Whisper model. The system consists of a REST API that handles recording and transcription, and a keyboard control script that lets you start and stop recordings by pressing the spacebar.

## Requirements

- Python 3.8 or higher
- Python packages listed in `requirements.txt`
- Configured audio device/microphone

## Installation

1. Clone this repository
2. Install dependencies:

```bash
pip install -r requirements.txt
```

3. Set up your environment variables. You can create a `.env` file in the project root or export them in your shell.

### Environment Variables

- `REC_DEVICE`: **(Required)** The ID of your recording device. The application will print a list of available devices when it starts, which can help you find the correct ID.
- `LANGUAGE`: The language for transcription. Defaults to `en`.
- `VAD_MIN_SILENCE_DURATION_MS`: The minimum duration of silence in milliseconds for the Voice Activity Detection (VAD) filter. Defaults to `500`.
- `DEBUG`: Set to `True` to enable debug mode, which saves the recorded audio to `debug.wav`. Defaults to `False`.

Example `.env` file:

```
REC_DEVICE=1
LANGUAGE=en
VAD_MIN_SILENCE_DURATION_MS=500
DEBUG=True
```

## Usage

### 1. Start the Whisper REST API

First, you need to start the Whisper API server:

```bash
python run_whisper.py
```

This command will start the server at `http://0.0.0.0:8001`. When it starts, it will print a list of available input audio devices. Note the ID of the device you want to use and set it in the `REC_DEVICE` environment variable.

### 2. Run the keyboard controller

Once the API is running, execute the keyboard control script:

```bash
python spacebar.py
```

### 3. Control the recording

- **Press the spacebar once** to start recording.
- **Press the spacebar again** to stop recording and see the transcription.

## How spacebar.py works

The `spacebar.py` script works as follows:

1. It uses the `pynput` library to listen for keyboard events.
2. When the spacebar is pressed, it toggles between starting and stopping the recording.
3. To start the recording, it sends a POST request to the `/start` endpoint of the API.
4. To stop the recording, it sends a POST request to the `/stop` endpoint.
5. When stopping the recording, it displays the transcription obtained from the audio.

## Important notes

- The `spacebar.py` script completely depends on the REST API running beforehand.
- The transcription is configured for English by default but can be changed with the `LANGUAGE` environment variable.
- To exit the control script, press Ctrl+C in the terminal.
- If you have issues with the audio device, check the list of available devices printed by `run_whisper.py` and configure the `REC_DEVICE` variable with the correct ID.

## Troubleshooting

- If the API doesn't respond, check that the server is active on port 8001.
- If the transcriptions are poor, check your microphone's audio level or try adjusting `VAD_MIN_SILENCE_DURATION_MS`.
- To activate debug mode, set the environment variable `DEBUG=True`. This will save the recorded audio as `debug.wav` for inspection.
