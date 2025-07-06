import json
import time
import platform
import pyautogui
import subprocess
import sys
import os
from pynput import keyboard


def get_window_rect(title):
    system = platform.system()

    if system == 'Windows' or system == 'Darwin':
        import pygetwindow as gw
        try:
            wins = gw.getWindowsWithTitle(title)
            if wins:
                win = wins[0]
                win.activate()
                time.sleep(0.5)
                return (win.left, win.top, win.width, win.height)
        except Exception as e:
            print(f"Window error: {e}")
            return None

    elif system == 'Linux':
        try:
            cmd = ['xdotool', 'search', '--name', title]
            result = subprocess.run(cmd, capture_output=True, text=True)
            if not result.stdout.strip():
                return None
            win_id = result.stdout.split()[0]

            subprocess.run(['xdotool', 'windowactivate', win_id])
            time.sleep(0.5)

            cmd = ['xdotool', 'getwindowgeometry', '--shell', win_id]
            result = subprocess.run(cmd, capture_output=True, text=True)
            geometry = {}
            for line in result.stdout.splitlines():
                if '=' in line:
                    key, val = line.split('=')
                    geometry[key] = int(val)
            return (geometry['X'], geometry['Y'], geometry['WIDTH'], geometry['HEIGHT'])
        except Exception as e:
            print(f"Linux window error: {e}")
            return None

    return None


def type_filename(filename):
    """Type filename with error checking and clearing"""
    # pyautogui.hotkey('ctrl', 'a')  # Select existing text
    # pyautogui.press('backspace')
    time.sleep(0.2)
    pyautogui.typewrite(filename)
    time.sleep(0.5)


def execute_file_selection(step, config, main_window_rect):
    # Get files from directory
    files = [f for f in os.listdir(config['file_directory'])
             if f.endswith(config['file_extension'])]
    files.sort()

    if not files:
        print("No files found in directory")
        return

    # Activate file dialog
    dialog_rect = get_window_rect(config.get('file_dialog_title', 'Open File'))
    if not dialog_rect:
        print("File dialog not found! Trying to proceed...")
        dialog_rect = main_window_rect

    # Calculate coordinates
    # target_x, target_y = step['relative_target']
    # open_x, open_y = step['open_button']
    #
    # if dialog_rect:
    #     target_x += dialog_rect[0]
    #     target_y += dialog_rect[1]
    #     open_x += dialog_rect[0]
    #     open_y += dialog_rect[1]

    # Process files
    for filename in files:
        print(f"Processing: {filename}")

        # Click file list area
        # pyautogui.click(target_x, target_y)
        # time.sleep(0.5)

        # Type filename
        type_filename(filename)
        time.sleep(0.5)

        # Press enter
        pyautogui.press('enter')
        time.sleep(0.5)

        # Wait for operation to complete
        time.sleep(step.get('delay_after', 2.0))

        # Check if we need to reopen dialog for next file
        if filename != files[-1]:
            # Reopen file dialog
            execute_steps(config['steps'][:-1], config, main_window_rect)


def execute_steps(steps, config, main_window_rect, filename=None):
    for step in steps:
        # Handle file selection step differently
        if step['type'] == 'file_selection':
            if filename:
                # Get filename without extension
                file_base = os.path.splitext(filename)[0]
                type_filename(file_base)
                time.sleep(0.5)
                pyautogui.press('enter')
                print(f"Selected file: {file_base}")
            else:
                print("No filename provided for file selection step")
            time.sleep(step.get('delay_after', 2.0))
            continue

        # Calculate coordinates for non-file steps
        if step.get('relative', False) and main_window_rect:
            x = main_window_rect[0] + step['x']
            y = main_window_rect[1] + step['y']
        else:
            x = step['x']
            y = step['y']

        # Execute actions
        if step['type'] == 'move_click':
            pyautogui.moveTo(x, y, duration=0.2)
            pyautogui.click()
            print(f"Clicked at ({x}, {y}) for: {step.get('description', '')}")

        time.sleep(step.get('delay_after', 0.3))


if __name__ == "__main__":
    try:
        with open('recorded_automation.json', 'r') as f:
            config = json.load(f)

        # Get files from directory
        files = [f for f in os.listdir(config['file_directory'])
                 if f.endswith(config['file_extension'])]
        files.sort()

        if not files:
            print("No files found in directory")
            sys.exit(0)

        # Get main window - do this once at start
        main_window_rect = get_window_rect(config['window_title'])

        # Process each file
        for filename in files:
            print(f"\nProcessing file: {filename}")

            # Execute full sequence of steps for this file
            execute_steps(config['steps'], config, main_window_rect, filename)

            # Short pause between files
            time.sleep(1.0)

        print("Automation complete!")

    except Exception as e:
        print(f"Error: {e}")
