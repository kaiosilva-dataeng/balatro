"""
Input adapter implementation using PyDirectInput and keyboard library.

Handles mouse movement, clicks, and keyboard input including hotkeys.
"""

import logging
import sys
from typing import Callable

import keyboard

if sys.platform == 'win32':
    import pydirectinput
else:
    pydirectinput = None

from ..domain.model import Coordinates

logger = logging.getLogger(__name__)


class DirectInputAdapter:
    """
    Input adapter using PyDirectInput for mouse/keyboard
    and keyboard library for hotkeys.

    PyDirectInput is used for game input as it works with DirectX games.
    """

    def __init__(self):
        """Initialize the input adapter."""
        self._hotkey_callbacks: dict[str, Callable[[], None]] = {}

    def click(self, coords: Coordinates) -> None:
        """
        Move to coordinates and click.

        Args:
            coords: Screen coordinates to click.
        """
        pydirectinput.moveTo(coords.x, coords.y)
        pydirectinput.click()
        logger.debug(f'Clicked at ({coords.x}, {coords.y})')

    def move_to(self, coords: Coordinates) -> None:
        """
        Move mouse to coordinates.

        Args:
            coords: Screen coordinates to move to.
        """
        pydirectinput.moveTo(coords.x, coords.y)

    def press_key(self, key: str) -> None:
        """
        Press and release a keyboard key.

        Args:
            key: Key name (e.g., 'esc', 'enter').
        """
        pydirectinput.press(key)
        logger.debug(f'Pressed key: {key}')

    def register_hotkey(self, key: str, callback: Callable[[], None]) -> None:
        """
        Register a hotkey callback.

        Args:
            key: Key name to listen for.
            callback: Function to call when key is pressed.
        """

        # Wrap callback to match keyboard library's expected signature
        def on_press(event):
            callback()

        keyboard.on_press_key(key, on_press)
        self._hotkey_callbacks[key] = callback
        logger.debug(f'Registered hotkey: {key}')

    def unregister_all_hotkeys(self) -> None:
        """Remove all registered hotkey callbacks."""
        keyboard.unhook_all()
        self._hotkey_callbacks.clear()
        logger.debug('Unregistered all hotkeys')
