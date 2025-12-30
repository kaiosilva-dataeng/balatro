"""
Module for calibrating the screen coordinates of Balatro UI elements.
"""
import json
import time
from pathlib import Path

import keyboard
import pyautogui

CONFIG_FILE = Path(__file__).parent / "config.json"

ACTIONS = {
    "skip_slot_1": "HOVER over 'Skip Slot 1' (Small Blind)",
    "skip_slot_2": "HOVER over 'Skip Slot 2' (Big Blind)",
    "package_specialized_skip": "HOVER over 'Pack Skip/Next' button",
    "new_game_top": "HOVER over 'New Game' (Menu Top)",
    "new_game_confirm": "HOVER over 'New Game' (Confirm/Deck Select)",
}


def calibrate() -> None:
    print("=== BALATRO AUTOMATION CALIBRATION ===")
    print("We will capture the screen coordinates for each action.")
    print("For each step:")
    print("  1. Mouse over the requested button.")
    print("  2. Press 'C' to capture.")
    print("  3. Press 'Q' to quit at any time.\n")

    config = {}
    config["window"] = pyautogui.size()
    for key, prompt in ACTIONS.items():
        print(f"\n👉 {prompt}")
        print("   [Waiting for 'C' key...]")

        while True:
            if keyboard.is_pressed("q"):
                print("calibration aborted.")
                return

            if keyboard.is_pressed("c"):
                # Debounce
                while keyboard.is_pressed("c"):
                    time.sleep(0.1)

                x, y = pyautogui.position()
                config[key] = (x, y)
                print(f"   ✅ Captured: ({x}, {y})")
                time.sleep(0.5)
                break

            time.sleep(0.01)

    print("\n---------------------------------")
    print("Calibration Complete!")
    print(json.dumps(config, indent=2))

    with open(CONFIG_FILE, "w") as f:
        json.dump(config, f, indent=4)

    print(f"\nConfiguration saved to: {CONFIG_FILE}")


if __name__ == "__main__":
    calibrate()
