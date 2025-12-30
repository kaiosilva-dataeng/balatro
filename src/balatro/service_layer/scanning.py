"""
Scanning service for image detection.

Orchestrates screen capture and template matching across configured ROIs.
"""

import logging
from typing import Optional

from ..adapters.ports import AbstractScreenPort
from ..domain.model import Coordinates, ProfileConfig, Region, ScanResult

logger = logging.getLogger(__name__)


class ScanService:
    """
    Service for scanning the screen for game elements.

    Handles the logic of scanning multiple ROIs and aggregating results.
    """

    def __init__(self, screen: AbstractScreenPort, profile: ProfileConfig):
        """
        Initialize the scan service.

        Args:
            screen: Screen adapter for capture and matching.
            profile: Current resolution profile configuration.
        """
        self.screen = screen
        self.profile = profile

    def scan_region_for_asset(
        self, asset_name: str, region: Optional[Region] = None, slot: int = 0
    ) -> list[ScanResult]:
        """
        Scan a specific region for an asset.

        Args:
            asset_name: Name of the asset to search for.
            region: Region to scan (None for full screen).
            slot: Slot number to assign to matches.

        Returns:
            List of scan results.
        """
        haystack = self.screen.capture_region(region)
        offset = None
        if region:
            offset = Coordinates(region.left, region.top)

        return self.screen.match_template(
            haystack=haystack,
            asset_name=asset_name,
            slot=slot,
            region_offset=offset,
        )

    def scan_slots_for_tags(self) -> tuple[list[ScanResult], list[ScanResult]]:
        """
        Scan both blind slots for double and charm tags.

        Returns:
            Tuple of (double_matches, charm_matches) across both slots.
        """
        double_matches: list[ScanResult] = []
        charm_matches: list[ScanResult] = []

        # Scan Slot 1
        slot1_rois = self.profile.get_rois('skip_slots_1')
        for roi in slot1_rois:
            logger.debug(f'Scanning Slot 1 ROI: {roi}')
            double_matches.extend(
                self.scan_region_for_asset('double.png', roi, slot=1)
            )
            charm_matches.extend(
                self.scan_region_for_asset('charm.png', roi, slot=1)
            )

        # Scan Slot 2
        slot2_rois = self.profile.get_rois('skip_slots_2')
        for roi in slot2_rois:
            logger.debug(f'Scanning Slot 2 ROI: {roi}')
            double_matches.extend(
                self.scan_region_for_asset('double.png', roi, slot=2)
            )
            charm_matches.extend(
                self.scan_region_for_asset('charm.png', roi, slot=2)
            )

        # Log summary
        detection_summary = []
        if any(m.slot == 1 for m in double_matches):
            detection_summary.append('Double(Slot1)')
        if any(m.slot == 1 for m in charm_matches):
            detection_summary.append('Charm(Slot1)')
        if any(m.slot == 2 for m in charm_matches):
            detection_summary.append('Charm(Slot2)')

        if detection_summary:
            logger.info(
                f'SCAN_RESULT: detected {", ".join(detection_summary)}'
            )

        return double_matches, charm_matches

    def scan_for_soul(self) -> Optional[ScanResult]:
        """
        Scan the soul card ROIs for The Soul card.

        Returns:
            The best matching ScanResult if found, None otherwise.
        """
        soul_rois = self.profile.get_rois('the_soul')

        for i, roi in enumerate(soul_rois):
            logger.debug(f'Scanning Soul ROI {i + 1}: {roi}')
            matches = self.scan_region_for_asset(
                'the_soul.png', roi, slot=i + 1
            )

            if matches:
                # Return the best match
                return max(matches, key=lambda m: m.confidence)

        return None
