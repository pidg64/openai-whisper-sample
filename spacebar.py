from pynput import keyboard
import requests

API_URL = "http://127.0.0.1:8001"
recording = False

print("Proceso iniciado")

def toggle_grabacion():
    global recording
    if not recording:
        print("Iniciando grabación...")
        response = requests.post(f"{API_URL}/start")
        if response.status_code == 200:
            recording = True
        else:
            print("Error al iniciar:", response.json())
    else:
        print("Deteniendo grabación...")
        response = requests.post(f"{API_URL}/stop")
        if response.status_code == 200:
            transcripcion = response.json().get("transcripcion", "")
            print("Transcripción:")
            print(transcripcion.strip())
        else:
            print("Error al detener:", response.json())
        recording = False

def on_press(key):
    try:
        if key == keyboard.Key.space:
            toggle_grabacion()
    except Exception as e:
        print("Error:", e)

with keyboard.Listener(on_press=on_press) as listener:
    listener.join()
