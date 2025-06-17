import os
import whisper
import threading
import numpy as np
import sounddevice as sd

from fastapi import FastAPI
from scipy.io import wavfile
from dotenv import load_dotenv
from fastapi.responses import JSONResponse

load_dotenv()

rec_device_env = os.getenv("REC_DEVICE")

if rec_device_env is None:
    raise ValueError("Environment variable REC_DEVICE is not set")

REC_DEVICE = int(rec_device_env)

DEBUG = os.getenv("DEBUG", "False").lower() in ("true", "1", "yes")

app = FastAPI()

model = whisper.load_model(
    "medium",
    device="cpu",
    download_root="./models/whisper"
)

# Variables de estado
recording = False
audio_data = []
sample_rate = 16000
record_thread = None
transcripcion_final = ""

def grabar_audio(device_id=REC_DEVICE):
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
            f"El dispositivo {device_id} no tiene canales de entrada"
        )
    print(f"Grabando audio desde el dispositivo: {device_name}")
    while recording:
        bloque = sd.rec(
            int(sample_rate * 1),
            samplerate=sample_rate,
            channels=1,
            dtype='float32',
            device=device_id
        )
        sd.wait()
        audio_data.append(np.squeeze(bloque))

def normalizar_audio(audio_np):
    max_abs_val = np.max(np.abs(audio_np))
    if max_abs_val < 1e-3:
        print(
            "Advertencia: audio demasiado bajo, posible problema de micrófono"
        )
        return audio_np
    return audio_np / max_abs_val

@app.post("/start")
def start_recording():
    global recording, audio_data, record_thread
    if recording:
        return JSONResponse(
            content={"status": "Ya está grabando"},
            status_code=400
        )
    audio_data = []
    recording = True
    record_thread = threading.Thread(target=grabar_audio)
    record_thread.start()
    return {"status": "Grabación iniciada"}

@app.post("/stop")
def stop_recording():
    global recording, audio_data, transcripcion_final
    if not recording:
        return JSONResponse(
            content={"status": "No estaba grabando"},
            status_code=400
        )
    recording = False
    record_thread.join()
    audio_np = np.concatenate(audio_data, axis=0)
    if audio_np.ndim > 1:
        audio_np = np.squeeze(audio_np)
    print("Procesando audio...")
    if DEBUG:
        print(
            f"Array shape: {audio_np.shape} - ",
            f"Audio data type: {audio_np.dtype} - ",
            f"Max. audio: {np.max(audio_np)} - ",
            f"Min. audio: {np.min(audio_np)}"
        )
        print("Guardando archivo de audio...")
        # Guardar el audio grabado para depuración
        wavfile.write("debug.wav", sample_rate, audio_np)
    audio_np = normalizar_audio(audio_np)
    result = model.transcribe(audio_np, language="es", fp16=False)
    transcripcion_final = result["text"]
    return {
        "status": "Grabación detenida",
        "transcripcion": transcripcion_final
    }


@app.get("/transcripcion")
def get_transcripcion():
    return {"transcripcion": transcripcion_final}


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(
        'run_whisper:app',
        host='0.0.0.0',
        port=8001
    )
