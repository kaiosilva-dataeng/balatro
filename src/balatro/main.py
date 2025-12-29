"""
Entry point for the Balatro automation application.
"""
from .soul_farm import soul_farm
from .process_log import process_balatro_logs

def main() -> None:
    """
    Main entry point of the application.
    Executes the soul farming loop and processes the logs upon completion.
    """
    content = soul_farm().read_text(encoding='utf-8')

    process_balatro_logs(content)

if __name__ == "__main__":
    main()

