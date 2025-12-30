"""
Tests for the domain models.
"""

import pytest

from balatro.domain.model import (
    Coordinates,
    FarmingPhase,
    GameState,
    ProfileConfig,
    Region,
    ScanResult,
)


class TestCoordinates:
    """Tests for Coordinates value object."""

    def test_creation(self):
        coords = Coordinates(100, 200)
        assert coords.x == 100
        assert coords.y == 200

    def test_immutability(self):
        coords = Coordinates(100, 200)
        with pytest.raises(AttributeError):
            coords.x = 300

    def test_offset(self):
        coords = Coordinates(100, 200)
        new_coords = coords.offset(50, -30)
        assert new_coords.x == 150
        assert new_coords.y == 170
        # Original unchanged
        assert coords.x == 100

    def test_to_tuple(self):
        coords = Coordinates(100, 200)
        assert coords.to_tuple() == (100, 200)

    def test_equality(self):
        a = Coordinates(100, 200)
        b = Coordinates(100, 200)
        c = Coordinates(100, 300)
        assert a == b
        assert a != c


class TestRegion:
    """Tests for Region value object."""

    def test_creation(self):
        region = Region(left=10, top=20, width=100, height=50)
        assert region.left == 10
        assert region.top == 20
        assert region.width == 100
        assert region.height == 50

    def test_to_tuple(self):
        region = Region(10, 20, 100, 50)
        assert region.to_tuple() == (10, 20, 100, 50)

    def test_contains_inside(self):
        region = Region(100, 100, 50, 50)
        inside = Coordinates(125, 125)
        assert region.contains(inside)

    def test_contains_outside(self):
        region = Region(100, 100, 50, 50)
        outside = Coordinates(200, 200)
        assert not region.contains(outside)

    def test_contains_on_edge(self):
        region = Region(100, 100, 50, 50)
        edge = Coordinates(100, 100)
        assert region.contains(edge)

    def test_local_to_global(self):
        region = Region(100, 200, 50, 50)
        local = Coordinates(25, 25)
        global_coords = region.local_to_global(local)
        assert global_coords.x == 125
        assert global_coords.y == 225


class TestScanResult:
    """Tests for ScanResult entity."""

    def test_creation(self):
        result = ScanResult(
            asset_name='charm.png',
            position=Coordinates(500, 600),
            confidence=0.95,
            slot=1,
        )
        assert result.asset_name == 'charm.png'
        assert result.confidence == 0.95
        assert result.slot == 1

    def test_repr(self):
        result = ScanResult(
            asset_name='charm.png',
            position=Coordinates(500, 600),
            confidence=0.95,
            slot=1,
        )
        repr_str = repr(result)
        assert 'charm.png' in repr_str
        assert '0.95' in repr_str


class TestGameState:
    """Tests for GameState entity."""

    def test_initial_state(self):
        state = GameState()
        assert state.is_running
        assert not state.is_farming
        assert state.phase == FarmingPhase.IDLE
        assert state.current_run == 0

    def test_start_farming(self):
        state = GameState()
        state.start_farming()
        assert state.is_farming
        assert state.phase == FarmingPhase.SCANNING

    def test_pause_farming(self):
        state = GameState()
        state.start_farming()
        state.pause_farming()
        assert not state.is_farming
        assert state.phase == FarmingPhase.IDLE

    def test_stop(self):
        state = GameState()
        state.start_farming()
        state.stop()
        assert not state.is_running
        assert not state.is_farming

    def test_increment_run(self):
        state = GameState()
        assert state.current_run == 0
        state.increment_run()
        state.increment_run()
        assert state.current_run == 2

    def test_record_soul(self):
        state = GameState()
        assert state.souls_found == 0
        state.record_soul_found()
        assert state.souls_found == 1


class TestProfileConfig:
    """Tests for ProfileConfig value object."""

    def test_creation(self):
        profile = ProfileConfig(
            name='1080p',
            description='Full HD',
            actions={'skip_slot_1': Coordinates(715, 850)},
            rois={'the_soul': [Region(613, 651, 174, 241)]},
        )
        assert profile.name == '1080p'
        assert profile.description == 'Full HD'

    def test_get_action_exists(self):
        profile = ProfileConfig(
            name='test',
            description='Test',
            actions={'skip_slot_1': Coordinates(715, 850)},
        )
        coords = profile.get_action('skip_slot_1')
        assert coords == Coordinates(715, 850)

    def test_get_action_missing(self):
        profile = ProfileConfig(name='test', description='Test')
        coords = profile.get_action('nonexistent')
        assert coords is None

    def test_get_rois_exists(self):
        roi = Region(613, 651, 174, 241)
        profile = ProfileConfig(
            name='test', description='Test', rois={'the_soul': [roi]}
        )
        rois = profile.get_rois('the_soul')
        assert len(rois) == 1
        assert rois[0] == roi

    def test_get_rois_missing(self):
        profile = ProfileConfig(name='test', description='Test')
        rois = profile.get_rois('nonexistent')
        assert rois == []
