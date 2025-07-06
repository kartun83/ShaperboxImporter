import json
import pyautogui
import time
from pynput import mouse, keyboard
import os

recording = []
is_recording = False
current_position = (0, 0)
last_typed = ""
hotkey_active = False


def on_move(x, y):
    global current_position
    current_position = (x, y)


def on_click(x, y, button, pressed):
    global is_recording, hotkey_active
    if is_recording and pressed and not hotkey_active:
        recording.append({
            "type": "move_click",
            "x": x,
            "y": y,
            "button": button.name,
            "relative": False,
            "delay_after": 1.0,
            "description": f"Click at ({x}, {y})"
        })
        print(f"Recorded click at ({x}, {y})")


def on_press(key):
    global is_recording, hotkey_active, last_typed

    # Toggle recording
    if key == keyboard.Key.f8:
        is_recording = not is_recording
        status = "STARTED" if is_recording else "STOPPED"
        print(f"Recording {status}")
        if not is_recording and recording:
            with open('recorded_automation.json', 'w') as f:
                json.dump({"steps": recording}, f, indent=2)
            print("Saved to recorded_automation.json")
        return

    # Capture filename if in dialog
    if is_recording and hasattr(key, 'char') and key.char:
        last_typed += key.char
        hotkey_active = False

    # Capture Enter press as file selection
    elif key == keyboard.Key.enter and is_recording and last_typed:
        # Extract filename from path if needed
        filename = os.path.basename(last_typed) if '/' in last_typed else last_typed
        base_name = os.path.splitext(filename)[0]

        recording.append({
            "type": "file_selection",
            "filename": base_name,
            "description": f"File selected: {base_name}"
        })
        print(f"Recorded file selection: {base_name}")
        last_typed = ""
        hotkey_active = False


def on_release(key):
    global hotkey_active
    if key in (keyboard.Key.ctrl, keyboard.Key.ctrl_l, keyboard.Key.ctrl_r,
               keyboard.Key.alt, keyboard.Key.cmd):
        hotkey_active = False


# Start listeners
mouse_listener = mouse.Listener(on_move=on_move, on_click=on_click)
keyboard_listener = keyboard.Listener(on_press=on_press, on_release=on_release)

mouse_listener.start()
keyboard_listener.start()

print("Press F8 to start/stop recording")
print("Type filename and press Enter to record file selections")
mouse_listener.join()
keyboard_listener.join()