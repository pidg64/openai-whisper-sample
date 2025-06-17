# Voice Transcription System with Spacebar

This project allows you to transcribe audio in Spanish using OpenAI's Whisper model. The system consists of a REST API that handles recording and transcription, and a keyboard control script that lets you start and stop recordings by pressing the spacebar.

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

3. Set the `REC_DEVICE` environment variable with your recording device ID.

```bash
export REC_DEVICE=1  # Adjust this number according to your device
```

## Usage

### 1. Start the Whisper REST API

First, you need to start the Whisper API server:

```bash
python run_whisper.py
```

This command will start the server at `http://0.0.0.0:8001`.

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
- The transcription is configured for Spanish by default.
- To exit the control script, press Ctrl+C in the terminal.
- If you have issues with the audio device, configure the `REC_DEVICE` variable with the correct ID of your device.

## Troubleshooting

- If the API doesn't respond, check that the server is active on port 8001.
- If the transcriptions are poor, check your microphone's audio level.
- To activate debug mode, set the environment variable `DEBUG=True`.
