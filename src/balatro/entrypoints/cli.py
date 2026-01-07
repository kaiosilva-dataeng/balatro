"""
CLI entrypoint for the Balatro Soul Farm automation.

This module wires up all dependencies and starts the application.
"""

import argparse
import logging
import shutil
import sys
import tempfile
import time
from pathlib import Path
from typing import Optional

from ..service_layer.analytics import AnalyticsService

# Setup directories
BASE_DIR = Path(__file__).resolve().parent.parent
ASSETS_DIR = BASE_DIR / 'assets'
ASSETS_DIR.mkdir(exist_ok=True)

LOG_DIR = Path.home() / '.balatro' / 'logs'
LOG_DIR.mkdir(parents=True, exist_ok=True)
CONFIG_FILE = BASE_DIR / 'config.json'

logger = logging.getLogger(__name__)


def setup_logging() -> Path:
    """Configure logging and return the log file path."""
    log_file = LOG_DIR / f'{time.strftime("%Y-%m-%d_%H-%M-%S")}.log'

    logging.basicConfig(
        level=logging.INFO,
        format='%(asctime)s - %(levelname)s - %(message)s',
        handlers=[
            logging.FileHandler(log_file),
            logging.StreamHandler(sys.stdout),
        ],
    )
    return log_file


def run_farming(args: argparse.Namespace) -> None:
    """Run the farming automation."""
    # Delay imports to avoid side effects (hooks, DLLs) when running 'stats'
    import pyautogui  # noqa: PLC0415

    from ..adapters.config import JsonConfigRepository  # noqa: PLC0415
    from ..adapters.input import DirectInputAdapter  # noqa: PLC0415
    from ..adapters.screen import PyAutoGuiScreenAdapter  # noqa: PLC0415
    from ..service_layer.farming import FarmingService  # noqa: PLC0415

    log_file = setup_logging()

    logger.info('Balatro Automation Ready.')
    logger.info(f'Resolution: {pyautogui.size()}')
    logger.info(f'Log file: {log_file}')
    if args.fast:
        logger.info('Running in FAST MODE')

    # Wire up dependencies
    screen = PyAutoGuiScreenAdapter(ASSETS_DIR)
    input_adapter = DirectInputAdapter()
    config = JsonConfigRepository(CONFIG_FILE)

    # Create and run farming service
    farming = FarmingService(
        screen=screen,
        input_adapter=input_adapter,
        config=config,
        fast_mode=args.fast,
    )

    try:
        farming.run()
    except KeyboardInterrupt:
        logger.info('Automation stopped by user.')
        input_adapter.unregister_all_hotkeys()

    # Process and display statistics
    if log_file.exists():
        print(f'\nLOG FILE: {log_file.absolute()}')
        analytics = AnalyticsService()
        analytics.process_log_file(log_file)
    else:
        print('No log file generated.')


def get_latest_log_file() -> Optional[Path]:
    """Find the most recent log file in the log directory."""
    try:
        logs = list(LOG_DIR.glob('*.log'))
        if not logs:
            return None
        return max(logs, key=lambda p: p.stat().st_mtime)
    except Exception as e:
        print(f'Error finding logs: {e}')
        return None


def run_stats(args: argparse.Namespace) -> None:
    """Display statistics for the latest log file."""
    # Only configure basic console logging for stats command
    logging.basicConfig(level=logging.ERROR, format='%(message)s')

    latest_log = get_latest_log_file()

    if not latest_log:
        print('No log files found in ~/.balatro/logs')
        return

    print(f'Reading stats from latest log: {latest_log.name}')
    print('-' * 40)

    # Copy to temp file to avoid file locking conflicts
    with tempfile.NamedTemporaryFile(delete=False, suffix='.log') as tmp:
        temp_path = Path(tmp.name)

    try:
        # Use copy2 to preserve metadata (though not strictly necessary)
        # We copy because the main process has the file open for writing,
        # and Windows file locking might prevent reading or cause conflicts.
        shutil.copy2(latest_log, temp_path)

        analytics = AnalyticsService()
        analytics.process_log_file(temp_path)

    except Exception as e:
        print(f'Error reading log file: {e}')
    finally:
        if temp_path.exists():
            try:
                temp_path.unlink()
            except OSError:
                pass


def main() -> None:
    """Main entry point for the Balatro automation CLI."""
    parser = argparse.ArgumentParser(description='Balatro Automation Tool')
    subparsers = parser.add_subparsers(
        dest='command', help='Available commands'
    )

    # 'farm' command (default)
    farm_parser = subparsers.add_parser(
        'farm', help='Start the farming automation'
    )
    farm_parser.add_argument(
        '--fast',
        action='store_true',
        help='Enable aggressive timings for modded games',
    )
    farm_parser.set_defaults(func=run_farming)

    # 'stats' command
    stats_parser = subparsers.add_parser(
        'stats', help='Show stats from the last run'
    )
    stats_parser.set_defaults(func=run_stats)

    args = parser.parse_args()

    if args.command is None:
        # Default to farming if no command provided, for backward compatibility
        # We need to set 'fast' attribute since it's expected by run_farming
        if not hasattr(args, 'fast'):
            args.fast = False
        run_farming(args)
    else:
        args.func(args)


if __name__ == '__main__':
    main()
