"""
Screen adapter implementation using PyAutoGUI and OpenCV.

Handles screen capture and template matching for image recognition.
"""

import logging
from pathlib import Path
from typing import Optional

import cv2
import numpy as np
import pyautogui

from ..domain.exceptions import AssetNotFoundError
from ..domain.model import Coordinates, Region, ScanResult

logger = logging.getLogger(__name__)


class PyAutoGuiScreenAdapter:
    """
    Screen adapter using PyAutoGUI for capture and OpenCV for matching.

    Caches loaded templates for performance.
    """

    def __init__(self, assets_dir: Path):
        """
        Initialize the screen adapter.

        Args:
            assets_dir: Path to directory containing image assets.
        """
        self.assets_dir = assets_dir
        self._template_cache: dict[str, np.ndarray] = {}

        # Pre-configured asset thresholds
        self._asset_thresholds: dict[str, float] = {
            'the_soul.png': 0.65,
            'double.png': 0.90,
            'charm.png': 0.90,
        }

    def capture_region(self, region: Optional[Region] = None) -> np.ndarray:
        """
        Capture a screenshot of the screen or a specific region.

        Args:
            region: Optional region to capture. None captures full screen.

        Returns:
            NumPy array of the captured image in BGR format.
        """
        region_tuple = region.to_tuple() if region else None
        screenshot = pyautogui.screenshot(region=region_tuple)
        return cv2.cvtColor(np.array(screenshot), cv2.COLOR_RGB2BGR)

    def load_asset(self, asset_name: str) -> np.ndarray:
        """
        Load an image asset from disk, using cache if available.

        Args:
            asset_name: Name of the asset file.

        Returns:
            NumPy array of the loaded image in BGR format.

        Raises:
            AssetNotFoundError: If the asset file cannot be loaded.
        """
        if asset_name in self._template_cache:
            return self._template_cache[asset_name]

        asset_path = self.assets_dir / asset_name
        template = cv2.imread(str(asset_path))

        if template is None:
            raise AssetNotFoundError(asset_name, str(asset_path))

        self._template_cache[asset_name] = template
        logger.debug(f'Loaded and cached asset: {asset_name}')
        return template

    def get_threshold(self, asset_name: str) -> float:
        """Get the configured confidence threshold for an asset."""
        return self._asset_thresholds.get(asset_name, 0.8)

    def match_template(
        self,
        haystack: np.ndarray,
        asset_name: str,
        confidence_threshold: Optional[float] = None,
        slot: int = 0,
        region_offset: Optional[Coordinates] = None,
    ) -> list[ScanResult]:
        """
        Find occurrences of an asset template in the haystack image.

        Args:
            haystack: The image to search in (BGR format).
            asset_name: Name of the asset file to search for.
            confidence_threshold: Minimum confidence
                (defaults to asset-specific threshold).
            slot: Slot number to assign to found matches.
            region_offset: Offset to add to coordinates (for ROI scanning).

        Returns:
            List of ScanResult objects for each match found.
        """
        results: list[ScanResult] = []
        offset = region_offset or Coordinates(0, 0)

        try:
            template = self.load_asset(asset_name)
        except AssetNotFoundError:
            logger.error(f'Could not load asset: {asset_name}')
            return []

        threshold = confidence_threshold or self.get_threshold(asset_name)

        # Template matching
        result = cv2.matchTemplate(haystack, template, cv2.TM_CCOEFF_NORMED)
        locations = np.where(result >= threshold)
        matches = list(zip(*locations[::-1]))  # Convert to (x, y) format

        # Sort by confidence (highest first)
        matches.sort(key=lambda pt: result[pt[1], pt[0]], reverse=True)

        # Filter duplicates (within 10px proximity)
        processed_points: list[tuple[int, int]] = []
        template_height, template_width = template.shape[:2]

        for pt in matches:
            # Skip if too close to already processed point
            if any(
                abs(pt[0] - pp[0]) < 10 and abs(pt[1] - pp[1]) < 10
                for pp in processed_points
            ):
                continue

            processed_points.append(pt)
            confidence = float(result[pt[1], pt[0]])

            # Calculate center of match
            center_x = pt[0] + template_width // 2 + offset.x
            center_y = pt[1] + template_height // 2 + offset.y

            results.append(
                ScanResult(
                    asset_name=asset_name,
                    position=Coordinates(center_x, center_y),
                    confidence=confidence,
                    slot=slot,
                )
            )

            logger.info(
                f'Found {asset_name} | Slot {slot} | Conf: {confidence:.2f} | '
                f'Pos: ({center_x}, {center_y})'
            )

        return results

    def scan_for_asset(
        self, asset_name: str, region: Optional[Region] = None, slot: int = 0
    ) -> list[ScanResult]:
        """
        Convenience method to capture screen and match in one call.

        Args:
            asset_name: Name of the asset to search for.
            region: Optional region to scan.
            slot: Slot number to assign to matches.

        Returns:
            List of ScanResult objects.
        """
        haystack = self.capture_region(region)
        offset = Coordinates(region.left, region.top) if region else None
        return self.match_template(
            haystack, asset_name, slot=slot, region_offset=offset
        )
