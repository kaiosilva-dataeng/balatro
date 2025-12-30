"""
Integration tests for the ScanService.

Focused on core scanning logic: multi-asset detection and best match selection.
"""

from balatro.domain.model import Coordinates, ProfileConfig, Region, ScanResult
from balatro.service_layer.scanning import ScanService

from .fakes import FakeInputAdapter, FakeScreenAdapter


class TestScanServiceCore:
    """Core tests for ScanService behavior."""

    def test_scan_slots_returns_both_tag_types(self):
        """Verify both double and charm matches are returned together."""
        screen = FakeScreenAdapter(
            scan_results=[
                ScanResult('double.png', Coordinates(600, 800), 0.95, slot=1),
                ScanResult('charm.png', Coordinates(950, 900), 0.90, slot=2),
            ]
        )
        input_adapter = FakeInputAdapter()
        profile = ProfileConfig(
            name='test',
            description='Test profile',
            actions={},
            rois={
                'skip_slots_1': [Region(543, 784, 296, 153)],
                'skip_slots_2': [Region(910, 852, 266, 108)],
            },
        )

        scanner = ScanService(screen, input_adapter, profile)
        double_matches, charm_matches = scanner.scan_slots_for_tags()

        assert len(double_matches) == 1
        assert len(charm_matches) == 1

    def test_scan_slots_with_no_matches(self):
        """Verify empty results when no assets found."""
        screen = FakeScreenAdapter(scan_results=[])
        input_adapter = FakeInputAdapter()
        profile = ProfileConfig(
            name='test',
            description='Test profile',
            actions={},
            rois={
                'skip_slots_1': [Region(543, 784, 296, 153)],
                'skip_slots_2': [Region(910, 852, 266, 108)],
            },
        )

        scanner = ScanService(screen, input_adapter, profile)
        double_matches, charm_matches = scanner.scan_slots_for_tags()

        assert double_matches == []
        assert charm_matches == []

    def test_scan_for_soul_returns_best_match(self):
        """Verify highest confidence match is returned."""
        screen = FakeScreenAdapter(
            scan_results=[
                ScanResult(
                    'the_soul.png', Coordinates(700, 700), 0.70, slot=1
                ),
                ScanResult(
                    'the_soul.png', Coordinates(800, 700), 0.85, slot=1
                ),
            ]
        )
        input_adapter = FakeInputAdapter()
        profile = ProfileConfig(
            name='test',
            description='Test profile',
            actions={},
            rois={
                'the_soul': [Region(613, 651, 174, 241)],
            },
        )

        scanner = ScanService(screen, input_adapter, profile)
        result = scanner.scan_for_soul()

        assert result is not None
        assert result.confidence == 0.85

    def test_scan_for_soul_with_no_match(self):
        """Verify None returned when no soul found."""
        screen = FakeScreenAdapter(scan_results=[])
        input_adapter = FakeInputAdapter()
        profile = ProfileConfig(
            name='test',
            description='Test profile',
            actions={},
            rois={
                'the_soul': [Region(613, 651, 174, 241)],
            },
        )

        scanner = ScanService(screen, input_adapter, profile)
        result = scanner.scan_for_soul()

        assert result is None
