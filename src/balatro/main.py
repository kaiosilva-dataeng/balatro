"""
Entry point for the Balatro automation application.
"""

import json
import sys

import keyboard
import pyautogui

from .calibrate import calibrate
from .process_log import process_balatro_logs
from .soul_farm import CONFIG_FILE, LOG_FILE, load_config, soul_farm


def main() -> None:
    """
    Main entry point of the application.
    Checks for first-run calibration needs, then executes soul farming.
    """
    # Auto-calibrate if not 1080p and no config exists
    width, height = pyautogui.size()

    if CONFIG_FILE.exists():
        try:
            with open(CONFIG_FILE, "r") as f:
                saved_config = json.load(f)
            if tuple(saved_config.get("window", [])) != (width, height):
                print(f"Detected resolution change: {width}x{height}")
                print("Removing old config...")
                CONFIG_FILE.unlink()
        except Exception:
            pass

    if (width, height) != (1920, 1080) and not CONFIG_FILE.exists():
        print(f"Detected non-standard resolution: {width}x{height}")
        print("Starting first-run calibration...")
        try:
            calibrate()
            load_config()  # Reload config after calibration
        except KeyboardInterrupt:
            print("\nCalibration cancelled.")
            sys.exit(0)

    try:
        log_path = soul_farm()
    except KeyboardInterrupt:
        print("\nStopping automation...")
        keyboard.unhook_all()
        log_path = LOG_FILE

    if log_path.exists():
        content = log_path.read_text(encoding="utf-8")
        print("LOG FILE: ", log_path.absolute())
        process_balatro_logs(content)
    else:
        print("No log file generated.")


if __name__ == "__main__":
    main()
