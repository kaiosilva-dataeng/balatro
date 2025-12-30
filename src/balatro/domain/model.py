"""
Domain models for the Balatro automation.

These are pure Python data classes with no external dependencies.
They represent the core concepts of the domain.
"""

from dataclasses import dataclass, field
from enum import Enum, auto
from typing import Optional


@dataclass(frozen=True)
class Coordinates:
    """
    Value Object representing screen coordinates.

    Immutable to ensure it can be safely passed around and used as dict keys.
    """

    x: int
    y: int

    def offset(self, dx: int, dy: int) -> 'Coordinates':
        """Return new coordinates offset by dx, dy."""
        return Coordinates(self.x + dx, self.y + dy)

    def to_tuple(self) -> tuple[int, int]:
        """Convert to tuple for compatibility with pyautogui/pydirectinput."""
        return (self.x, self.y)


@dataclass(frozen=True)
class Region:
    """
    Value Object representing a screen region (Region of Interest).

    Used for targeted screen scanning to improve performance.
    """

    left: int
    top: int
    width: int
    height: int

    def to_tuple(self) -> tuple[int, int, int, int]:
        """Convert to tuple for compatibility with pyautogui."""
        return (self.left, self.top, self.width, self.height)

    def contains(self, coords: Coordinates) -> bool:
        """Check if coordinates fall within this region."""
        return (
            self.left <= coords.x < self.left + self.width
            and self.top <= coords.y < self.top + self.height
        )

    def local_to_global(self, local_coords: Coordinates) -> Coordinates:
        """Convert region-local coordinates to global screen coordinates."""
        return Coordinates(
            x=local_coords.x + self.left, y=local_coords.y + self.top
        )


@dataclass(frozen=True)
class AssetConfig:
    """
    Value Object representing configuration for an image asset.
    """

    name: str
    confidence_threshold: float = 0.8


@dataclass
class ScanResult:
    """
    Entity representing a detected asset on screen.

    Contains position, confidence score, and which slot it was found in.
    """

    asset_name: str
    position: Coordinates
    confidence: float
    slot: int = 0

    def __repr__(self) -> str:
        return (
            f'ScanResult({self.asset_name!r}, '
            f'pos={self.position.to_tuple()}, '
            f'conf={self.confidence:.2f}, slot={self.slot})'
        )


class FarmingPhase(Enum):
    """Represents the current phase of the farming loop."""

    IDLE = auto()
    SCANNING = auto()
    ACTING = auto()
    RESETTING = auto()


@dataclass
class GameState:
    """
    Entity representing the current state of the automation.

    Mutable state that tracks whether the automation is running/paused.
    """

    is_running: bool = True
    is_farming: bool = False
    phase: FarmingPhase = FarmingPhase.IDLE
    current_run: int = 0
    souls_found: int = 0

    def start_farming(self) -> None:
        """Resume the farming loop."""
        self.is_farming = True
        self.phase = FarmingPhase.SCANNING

    def pause_farming(self) -> None:
        """Pause the farming loop."""
        self.is_farming = False
        self.phase = FarmingPhase.IDLE

    def stop(self) -> None:
        """Stop the automation completely."""
        self.is_running = False
        self.is_farming = False
        self.phase = FarmingPhase.IDLE

    def increment_run(self) -> None:
        """Record a new game reset."""
        self.current_run += 1

    def record_soul_found(self) -> None:
        """Record finding a soul card."""
        self.souls_found += 1


@dataclass(frozen=True)
class ProfileConfig:
    """
    Value Object representing a resolution profile configuration.

    Contains named coordinates for UI actions and regions for scanning.
    """

    name: str
    description: str
    actions: dict[str, Coordinates] = field(default_factory=dict)
    rois: dict[str, list[Region]] = field(default_factory=dict)

    def get_action(self, action_name: str) -> Optional[Coordinates]:
        """Get coordinates for a named action."""
        return self.actions.get(action_name)

    def get_rois(self, roi_name: str) -> list[Region]:
        """Get list of regions for a named ROI."""
        return self.rois.get(roi_name, [])
