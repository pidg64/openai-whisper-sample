import os
import time
import uvicorn
import threading
import numpy as np
import sounddevice as sd

from fastapi import FastAPI
from scipy.io import wavfile
from dotenv import load_dotenv
from faster_whisper import WhisperModel
from fastapi.responses import JSONResponse

from sound_utils import (
    check_device_availability, print_available_devices, normalize_audio
)

load_dotenv()

# Load environment variables
REC_DEVICE = os.getenv('REC_DEVICE')
if REC_DEVICE is None:
    raise ValueError('Environment variable REC_DEVICE is not set')
REC_DEVICE = int(REC_DEVICE)
LANGUAGE = os.getenv('LANGUAGE', 'en').lower()
VAD_MIN_SILENCE_DURATION_MS = int(
    os.getenv('VAD_MIN_SILENCE_DURATION_MS', '500')
)
DEBUG = os.getenv('DEBUG', 'False').lower() in ('true', '1', 'yes')

app = FastAPI(title='Whisper API')

model = WhisperModel(
    'small.en',
    device='cpu',
    compute_type='int8',
    download_root='./models/faster-whisper'
)

# Global variables for recording state
recording = False
audio_data = []
sample_rate = 16000
record_thread = None
transcripcion_final = ''


def record_audio(device_id):
    global audio_data, recording
    device_info = sd.query_devices(device_id, 'input')
    # device_info is a dict-like object, but if it's a tuple, convert to dict
    if isinstance(device_info, dict):
        max_input_channels = device_info.get('max_input_channels', 0)
        device_name = device_info.get('name', str(device_id))
    else:
        # fallback: try to access by index (not recommended, but for safety)
        max_input_channels = device_info[1] if len(device_info) > 1 else 0
        device_name = device_info[0] if len(device_info) > 0 else str(device_id)
    if max_input_channels < 1:
        raise ValueError(
            f'Device {device_id} does not have input channels'
        )
    print(f'Recording audio from device: {device_name}')
    while recording:
        block = sd.rec(
            int(sample_rate * 1),
            samplerate=sample_rate,
            channels=1,
            dtype='float32',
            device=device_id
        )
        sd.wait()
        audio_data.append(np.squeeze(block))


@app.post('/start')
def start_recording():
    global recording, audio_data, record_thread
    if recording:
        return JSONResponse(
            content={'status': 'Already recording'},
            status_code=400
        )
    audio_data = []
    recording = True
    record_thread = threading.Thread(target=record_audio, args=(REC_DEVICE,))
    record_thread.start()
    return {'status': 'Recording started'}


@app.post('/stop')
def stop_recording():
    global recording, audio_data, transcripcion_final
    if not recording:
        return JSONResponse(
            content={'status': 'Not recording'},
            status_code=400
        )
    recording = False
    if record_thread:
        record_thread.join()
    audio_np = np.concatenate(audio_data, axis=0)
    if audio_np.ndim > 1:
        audio_np = np.squeeze(audio_np)
    if DEBUG:
        print(
            f'Array shape: {audio_np.shape} - ',
            f'Audio data type: {audio_np.dtype} - ',
            f'Max. audio: {np.max(audio_np)} - ',
            f'Min. audio: {np.min(audio_np)}'
        )
        print('Saving audio file...')
        wavfile.write('debug.wav', sample_rate, audio_np)
    print('Normalyzing recorded audio')
    audio_np = normalize_audio(audio_np)
    print('Transcribing audio')
    start_time = time.time()
    segments, info = model.transcribe(
        audio_np,
        language=LANGUAGE,
        beam_size=5,
        # Uncomment to activate VAD (Voice Activity Detection)
        # vad_filter=True,
        # vad_parameters=dict(min_silence_duration_ms=VAD_MIN_SILENCE_DURATION_MS),
    )
    transcripcion_final = "".join(segment.text for segment in segments)
    print(f"Transcription time: {time.time() - start_time:.2f} seconds")
    # result = model.transcribe(audio_np, language=LANGUAGE, fp16=False)
    # transcripcion_final = result['text']
    return {
        'status': 'Recording stopped',
        'transcription': transcripcion_final
    }


@app.get('/transcription')
def get_transcripcion():
    return {'transcription': transcripcion_final}


if __name__ == '__main__':
    print_available_devices()
    check_device_availability(REC_DEVICE)
    uvicorn.run(
        'main:app',
        host='0.0.0.0',
        port=8001
    )
