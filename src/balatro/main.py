"""
Entry point for the Balatro automation application.
"""
import sys
from .soul_farm import soul_farm, LOG_FILE
from .process_log import process_balatro_logs

def main() -> None:
    """
    Main entry point of the application.
    Executes the soul farming loop and processes the logs upon completion.
    """
    try:
        log_path = soul_farm()
    except KeyboardInterrupt:
        print("\nStopping automation...")
        log_path = LOG_FILE
    
    if log_path.exists():
        content = log_path.read_text(encoding='utf-8')
        process_balatro_logs(content)
    else:
        print("No log file generated.")

if __name__ == "__main__":
    main()

