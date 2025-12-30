"""
Entry point for the Balatro automation application.
"""

import json
import sys

import keyboard
import pyautogui

from .process_log import process_balatro_logs
from .soul_farm import LOG_FILE, soul_farm


def main() -> None:
    """
    Main entry point of the application.
    Executes soul farming.
    """
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
