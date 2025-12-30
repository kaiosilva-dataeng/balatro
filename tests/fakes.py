"""
Fake adapters for testing.

These provide in-memory implementations of the adapter ports
for fast unit testing without real screen/keyboard I/O.
"""

from typing import Callable, Optional

import numpy as np

from balatro.domain.model import Coordinates, ProfileConfig, Region, ScanResult


class FakeScreenAdapter:
    """
    Fake screen adapter for testing.

    Configurable scan results allow testing decision logic
    without actual screen capture.
    """

    def __init__(self, scan_results: Optional[list[ScanResult]] = None):
        self.scan_results = scan_results or []
        self.captured_regions: list[Optional[Region]] = []
        self.match_calls: list[tuple[str, int]] = []

    def capture_region(self, region: Optional[Region] = None) -> np.ndarray:
        self.captured_regions.append(region)
        return np.zeros((100, 100, 3), dtype=np.uint8)

    def match_template(
        self,
        haystack: np.ndarray,
        asset_name: str,
        confidence_threshold: float = 0.8,
        slot: int = 0,
        region_offset: Optional[Coordinates] = None,
    ) -> list[ScanResult]:
        self.match_calls.append((asset_name, slot))
        return [
            r
            for r in self.scan_results
            if r.asset_name == asset_name and r.slot == slot
        ]

    def load_asset(self, asset_name: str) -> np.ndarray:
        return np.zeros((50, 50, 3), dtype=np.uint8)


class FakeInputAdapter:
    """
    Fake input adapter for testing.

    Records all actions for verification.
    """

    def __init__(self):
        self.clicks: list[Coordinates] = []
        self.moves: list[Coordinates] = []
        self.key_presses: list[str] = []
        self.hotkeys: dict[str, Callable[[], None]] = {}

    def click(self, coords: Coordinates) -> None:
        self.clicks.append(coords)

    def move_to(self, coords: Coordinates) -> None:
        self.moves.append(coords)

    def press_key(self, key: str) -> None:
        self.key_presses.append(key)

    def register_hotkey(self, key: str, callback: Callable[[], None]) -> None:
        self.hotkeys[key] = callback

    def unregister_all_hotkeys(self) -> None:
        self.hotkeys.clear()

    def trigger_hotkey(self, key: str) -> None:
        """Helper to simulate pressing a hotkey."""
        if key in self.hotkeys:
            self.hotkeys[key]()


class FakeConfigRepository:
    """
    Fake config repository for testing.

    Returns configurable profile data.
    """

    def __init__(self, profile: Optional[ProfileConfig] = None):
        self.profile = profile or ProfileConfig(
            name='test',
            description='Test profile',
            actions={
                'skip_slot_1': Coordinates(715, 850),
                'skip_slot_2': Coordinates(1070, 850),
                'package_specialized_skip': Coordinates(1335, 975),
                'new_game_top': Coordinates(955, 355),
                'new_game_confirm': Coordinates(955, 830),
            },
            rois={
                'skip_slots_1': [Region(543, 784, 296, 153)],
                'skip_slots_2': [Region(910, 852, 266, 108)],
                'the_soul': [Region(613, 651, 174, 241)],
            },
        )
        self.saved_profiles: list[ProfileConfig] = []

    def load_profile(self, profile_name: str) -> ProfileConfig:
        return self.profile

    def get_current_profile_name(self) -> str:
        return self.profile.name

    def list_profiles(self) -> list[str]:
        return [self.profile.name]

    def save_profile(self, config: ProfileConfig) -> None:
        self.saved_profiles.append(config)
