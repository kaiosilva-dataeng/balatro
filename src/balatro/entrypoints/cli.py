"""
CLI entrypoint for the Balatro Soul Farm automation.

This module wires up all dependencies and starts the application.
"""

import logging
import sys
import time
from pathlib import Path

import pyautogui

from ..adapters.config import JsonConfigRepository
from ..adapters.input import DirectInputAdapter
from ..adapters.screen import PyAutoGuiScreenAdapter
from ..service_layer.analytics import AnalyticsService
from ..service_layer.farming import FarmingService

# Setup directories
BASE_DIR = Path(__file__).resolve().parent.parent
ASSETS_DIR = BASE_DIR / 'assets'
ASSETS_DIR.mkdir(exist_ok=True)

LOG_DIR = Path.home() / '.balatro' / 'logs'
LOG_DIR.mkdir(parents=True, exist_ok=True)
LOG_FILE = LOG_DIR / f'{time.strftime("%Y-%m-%d_%H-%M-%S")}.log'
CONFIG_FILE = BASE_DIR / 'config.json'

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler(LOG_FILE),
        logging.StreamHandler(sys.stdout),
    ],
)
logger = logging.getLogger(__name__)


def main() -> None:
    """
    Main entry point for the Balatro automation CLI.

    Wires up all dependencies and starts the farming service.
    """

    logger.info('Balatro Automation Ready.')
    logger.info(f'Resolution: {pyautogui.size()}')
    logger.info(f'Log file: {LOG_FILE}')

    # Wire up dependencies
    screen = PyAutoGuiScreenAdapter(ASSETS_DIR)
    input_adapter = DirectInputAdapter()
    config = JsonConfigRepository(CONFIG_FILE)

    # Create and run farming service
    farming = FarmingService(
        screen=screen,
        input_adapter=input_adapter,
        config=config,
    )

    try:
        farming.run()
    except KeyboardInterrupt:
        logger.info('Automation stopped by user.')
        input_adapter.unregister_all_hotkeys()

    # Process and display statistics
    if LOG_FILE.exists():
        print(f'\nLOG FILE: {LOG_FILE.absolute()}')
        analytics = AnalyticsService()
        analytics.process_log_file(LOG_FILE)
    else:
        print('No log file generated.')


if __name__ == '__main__':
    main()
