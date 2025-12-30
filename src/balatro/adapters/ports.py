"""
Abstract ports (interfaces) for external dependencies.

These protocols define the contracts that adapters must implement.
Using protocols allows for easy testing with fakes and future flexibility.
"""

from abc import abstractmethod
from pathlib import Path
from typing import Callable, Optional, Protocol, runtime_checkable

import numpy as np

from ..domain.model import Coordinates, ProfileConfig, Region, ScanResult


@runtime_checkable
class AbstractScreenPort(Protocol):
    """
    Port for screen capture and image matching operations.
    """

    @abstractmethod
    def capture_region(self, region: Optional[Region] = None) -> np.ndarray:
        """
        Capture a screenshot of the screen or a specific region.

        Args:
            region: Optional region to capture. None captures full screen.

        Returns:
            NumPy array of the captured image in BGR format.
        """
        ...

    @abstractmethod
    def match_template(
        self,
        haystack: np.ndarray,
        asset_name: str,
        confidence_threshold: float = 0.8,
        slot: int = 0,
        region_offset: Optional[Coordinates] = None,
    ) -> list[ScanResult]:
        """
        Find occurrences of an asset template in the haystack image.

        Args:
            haystack: The image to search in (BGR format).
            asset_name: Name of the asset file to search for.
            confidence_threshold: Minimum confidence for a match.
            slot: Slot number to assign to found matches.
            region_offset: Offset to add to coordinates (for ROI scanning).

        Returns:
            List of ScanResult objects for each match found.
        """
        ...

    @abstractmethod
    def load_asset(self, asset_name: str) -> np.ndarray:
        """
        Load an image asset from disk.

        Args:
            asset_name: Name of the asset file.

        Returns:
            NumPy array of the loaded image in BGR format.

        Raises:
            AssetNotFoundError: If the asset file cannot be loaded.
        """
        ...


@runtime_checkable
class AbstractInputPort(Protocol):
    """
    Port for mouse and keyboard input operations.
    """

    @abstractmethod
    def click(self, coords: Coordinates) -> None:
        """
        Move to coordinates and click.

        Args:
            coords: Screen coordinates to click.
        """
        ...

    @abstractmethod
    def move_to(self, coords: Coordinates) -> None:
        """
        Move mouse to coordinates.

        Args:
            coords: Screen coordinates to move to.
        """
        ...

    @abstractmethod
    def press_key(self, key: str) -> None:
        """
        Press and release a keyboard key.

        Args:
            key: Key name (e.g., 'esc', 'enter').
        """
        ...

    @abstractmethod
    def register_hotkey(self, key: str, callback: Callable[[], None]) -> None:
        """
        Register a hotkey callback.

        Args:
            key: Key name to listen for.
            callback: Function to call when key is pressed.
        """
        ...

    @abstractmethod
    def unregister_all_hotkeys(self) -> None:
        """Remove all registered hotkey callbacks."""
        ...


@runtime_checkable
class AbstractConfigPort(Protocol):
    """
    Port for configuration persistence.
    """

    @abstractmethod
    def load_profile(self, profile_name: str) -> ProfileConfig:
        """
        Load a resolution profile by name.

        Args:
            profile_name: Name of the profile to load.

        Returns:
            The loaded ProfileConfig.

        Raises:
            ProfileNotFoundError: If the profile doesn't exist.
        """
        ...

    @abstractmethod
    def get_current_profile_name(self) -> str:
        """Get the name of the currently active profile."""
        ...

    @abstractmethod
    def list_profiles(self) -> list[str]:
        """List all available profile names."""
        ...

    @abstractmethod
    def save_profile(self, config: ProfileConfig) -> None:
        """
        Save a profile configuration.

        Args:
            config: The profile configuration to save.
        """
        ...


@runtime_checkable
class AbstractLogPort(Protocol):
    """
    Port for logging operations.
    """

    @abstractmethod
    def get_log_path(self) -> Path:
        """Get the path to the current log file."""
        ...

    @abstractmethod
    def read_log(self) -> str:
        """Read the contents of the current log file."""
        ...
