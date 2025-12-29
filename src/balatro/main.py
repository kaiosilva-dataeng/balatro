from .soul_farm import soul_farm
from .process_log import process_balatro_logs
def main():
    content = soul_farm().read_text()

    process_balatro_logs(content)

if __name__ == "__main__":
    main()

