"""
Integration tests for FarmingService.

Focused on state machine transitions and complex action sequences.
"""

from balatro.domain.model import Coordinates
from balatro.service_layer.farming import FarmingService

from .fakes import FakeConfigRepository, FakeInputAdapter, FakeScreenAdapter


class TestStateMachine:
    """Core tests for hotkey-driven state transitions."""

    def test_hotkey_p_starts_farming(self):
        """Verify P hotkey transitions from idle to farming."""
        screen = FakeScreenAdapter()
        input_adapter = FakeInputAdapter()
        config = FakeConfigRepository()

        farming = FarmingService(screen, input_adapter, config)
        farming._setup_hotkeys()

        assert not farming.state.is_farming
        input_adapter.trigger_hotkey('p')
        assert farming.state.is_farming

    def test_hotkey_m_pauses_farming(self):
        """Verify M hotkey transitions from farming to paused."""
        screen = FakeScreenAdapter()
        input_adapter = FakeInputAdapter()
        config = FakeConfigRepository()

        farming = FarmingService(screen, input_adapter, config)
        farming._setup_hotkeys()
        farming.state.start_farming()

        assert farming.state.is_farming
        input_adapter.trigger_hotkey('m')
        assert not farming.state.is_farming

    def test_hotkey_l_stops_automation(self):
        """Verify L hotkey stops automation completely."""
        screen = FakeScreenAdapter()
        input_adapter = FakeInputAdapter()
        config = FakeConfigRepository()

        farming = FarmingService(screen, input_adapter, config)
        farming._setup_hotkeys()
        farming.state.start_farming()

        assert farming.state.is_running
        input_adapter.trigger_hotkey('l')
        assert not farming.state.is_running
        assert not farming.state.is_farming


class TestComplexActions:
    """Core tests for multi-step action sequences."""

    def test_skip_both_slots_includes_specialized_skip(self):
        """Verify skip both executes the full action sequence correctly."""
        screen = FakeScreenAdapter()
        input_adapter = FakeInputAdapter()
        config = FakeConfigRepository()

        farming = FarmingService(screen, input_adapter, config)
        farming._skip_both_slots()

        # Must include: skip_slot_1, package_specialized_skip, skip_slot_2
        assert Coordinates(715, 850) in input_adapter.clicks  # skip_slot_1
        assert Coordinates(1335, 975) in input_adapter.clicks  # specialized
        assert Coordinates(1070, 850) in input_adapter.clicks  # skip_slot_2
