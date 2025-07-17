import pprint
import numpy as np
import sounddevice as sd

def print_available_devices():
    """Prints available sound devices."""
    print("Available sound devices:")
    available_devices = sd.query_devices()
    pprint.pprint(available_devices)


def check_device_exists(device_id: int) -> None:
    """Checks if a sound device with the given ID exists."""
    available_devices = sd.query_devices()
    device_ids = [device['index'] for device in available_devices]
    if device_id not in device_ids:
        raise ValueError(f'Device ID {device_id} is not available.')


def check_device_is_input(device_id: int) -> None:
    """Checks if the sound device is an input device."""
    device_info = sd.query_devices(device_id, 'input')
    if device_info['max_input_channels'] < 1:
        raise ValueError(f'Device ID {device_id} is not an input device.')


def check_device_availability(device_id: int) -> None:
    """Checks if the device exists and is an input device."""
    check_device_exists(device_id)
    check_device_is_input(device_id)


def normalize_audio(audio_np):
    """Normalizes audio data to ensure it is within the range [-1, 1]."""
    max_abs_val = np.max(np.abs(audio_np))
    if max_abs_val < 1e-3:
        print(
            'Warning: audio too quiet, possible microphone issue'
        )
        return audio_np
    return audio_np / max_abs_val