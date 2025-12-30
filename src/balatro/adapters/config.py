"""
Configuration repository implementation using JSON files.

Handles loading and saving resolution profile configurations.
"""

import json
import logging
from pathlib import Path
from typing import Any

from ..domain.exceptions import ProfileNotFoundError
from ..domain.model import Coordinates, ProfileConfig, Region

logger = logging.getLogger(__name__)


def _create_default_config() -> dict[str, Any]:
    """Create the default configuration with standard 1080p profile."""
    return {
        'current_profile': '1080p',
        'profiles': {
            '1080p': {
                'desc': 'Standard Full HD (1920x1080)',
                'actions': {
                    'skip_slot_1': [715, 850],
                    'skip_slot_2': [1070, 850],
                    'package_specialized_skip': [1335, 975],
                    'new_game_top': [955, 355],
                    'new_game_confirm': [955, 830],
                },
                'rois': {
                    'skip_slots_1': [543, 784, 296, 153],
                    'skip_slots_2': [910, 852, 266, 108],
                    'the_soul': [
                        [613, 651, 174, 241],
                        [786, 657, 173, 236],
                        [958, 652, 171, 247],
                        [1130, 655, 168, 236],
                        [1303, 654, 167, 236],
                    ],
                },
            }
        },
    }


def _parse_coordinates(data: list[int]) -> Coordinates:
    """Parse a JSON array into Coordinates."""
    return Coordinates(x=data[0], y=data[1])


def _parse_region(data: list[int]) -> Region:
    """Parse a JSON array into Region."""
    return Region(left=data[0], top=data[1], width=data[2], height=data[3])


def _parse_rois(rois_data: dict[str, Any]) -> dict[str, list[Region]]:
    """Parse ROI configuration into Region objects."""
    result: dict[str, list[Region]] = {}

    for name, data in rois_data.items():
        if not data:
            result[name] = []
        elif isinstance(data[0], list):
            # List of regions
            result[name] = [_parse_region(r) for r in data]
        else:
            # Single region
            result[name] = [_parse_region(data)]

    return result


class JsonConfigRepository:
    """
    Configuration repository using JSON file storage.
    """

    def __init__(self, config_path: Path):
        """
        Initialize the config repository.

        Args:
            config_path: Path to the JSON configuration file.
        """
        self.config_path = config_path
        self._config: dict[str, Any] = {}
        self._ensure_config_exists()
        self._load_config()

    def _ensure_config_exists(self) -> None:
        """Create default config if it doesn't exist."""
        if not self.config_path.exists():
            logger.info(f'Creating default config at {self.config_path}')
            default_config = _create_default_config()
            self.config_path.parent.mkdir(parents=True, exist_ok=True)
            with open(self.config_path, 'w') as f:
                json.dump(default_config, f, indent=4)

    def _load_config(self) -> None:
        """Load configuration from file."""
        try:
            with open(self.config_path, 'r') as f:
                self._config = json.load(f)
            logger.info(f'Loaded configuration from {self.config_path}')
        except Exception as e:
            logger.error(f'Failed to load config: {e}')
            self._config = _create_default_config()

    def get_current_profile_name(self) -> str:
        """Get the name of the currently active profile."""
        return self._config.get('current_profile', '1080p')

    def list_profiles(self) -> list[str]:
        """List all available profile names."""
        profiles = self._config.get('profiles', {})
        return list(profiles.keys())

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
        profiles = self._config.get('profiles', {})

        if profile_name not in profiles:
            raise ProfileNotFoundError(profile_name)

        profile_data = profiles[profile_name]

        # Parse actions
        actions: dict[str, Coordinates] = {}
        for name, coords in profile_data.get('actions', {}).items():
            actions[name] = _parse_coordinates(coords)

        # Parse ROIs
        rois = _parse_rois(profile_data.get('rois', {}))

        return ProfileConfig(
            name=profile_name,
            description=profile_data.get('desc', ''),
            actions=actions,
            rois=rois,
        )

    def save_profile(self, config: ProfileConfig) -> None:
        """
        Save a profile configuration.

        Args:
            config: The profile configuration to save.
        """
        # Convert ProfileConfig back to JSON format
        actions_data = {
            name: [coords.x, coords.y]
            for name, coords in config.actions.items()
        }

        rois_data: dict[str, Any] = {}
        for name, regions in config.rois.items():
            if len(regions) == 1:
                r = regions[0]
                rois_data[name] = [r.left, r.top, r.width, r.height]
            else:
                rois_data[name] = [
                    [r.left, r.top, r.width, r.height] for r in regions
                ]

        profile_data = {
            'desc': config.description,
            'actions': actions_data,
            'rois': rois_data,
        }

        self._config.setdefault('profiles', {})[config.name] = profile_data

        with open(self.config_path, 'w') as f:
            json.dump(self._config, f, indent=4)

        logger.info(f'Saved profile: {config.name}')
