"""
Entry point for the Balatro automation application.
"""
import sys
import pyautogui
from .soul_farm import soul_farm, LOG_FILE, CONFIG_FILE, load_config
from .process_log import process_balatro_logs
from .calibrate import calibrate

def main() -> None:
    """
    Main entry point of the application.
    Checks for first-run calibration needs, then executes soul farming.
    """
    # Auto-calibrate if not 1080p and no config exists
    width, height = pyautogui.size()
    if (width, height) != (1920, 1080) and not CONFIG_FILE.exists():
        print(f"Detected non-standard resolution: {width}x{height}")
        print("Starting first-run calibration...")
        try:
            calibrate()
            load_config() # Reload config after calibration
        except KeyboardInterrupt:
            print("\nCalibration cancelled.")
            sys.exit(0)

    try:
        log_path = soul_farm()
    except KeyboardInterrupt:
        print("\nStopping automation...")
        log_path = LOG_FILE
    
    if log_path.exists():
        content = log_path.read_text(encoding='utf-8')
        print("LOG FILE: ", log_path.absolute())
        process_balatro_logs(content)
    else:
        print("No log file generated.")

if __name__ == "__main__":
    main()

