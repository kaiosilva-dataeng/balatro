"""
Farming service - main orchestration for the soul farm automation.

This is the primary use case that coordinates scanning, decision-making,
and action execution.
"""

import logging
import time
from typing import Optional

from ..adapters.ports import (
    AbstractConfigPort,
    AbstractInputPort,
    AbstractScreenPort,
)
from ..domain.decisions import (
    DecisionContext,
    FarmingDecision,
    decide_farming_action,
    get_decision_description,
)
from ..domain.model import Coordinates, GameState
from .scanning import ScanService

logger = logging.getLogger(__name__)


class FarmingService:
    """
    Service that orchestrates the soul farming automation loop.

    Uses dependency injection for all external I/O to enable testing.
    """

    # Timing constants (seconds)
    SOUL_WAIT_TIME = 5.0
    ACTION_DELAY = 0.5
    CLICK_DELAY = 1.5
    RESET_DELAY = 3.0
    IDLE_SLEEP = 0.1

    def __init__(
        self,
        screen: AbstractScreenPort,
        input_adapter: AbstractInputPort,
        config: AbstractConfigPort,
        profile_name: Optional[str] = None,
    ):
        """
        Initialize the farming service.

        Args:
            screen: Screen adapter for capture and matching.
            input_adapter: Input adapter for mouse/keyboard.
            config: Config repository for profile loading.
            profile_name: Name of profile to use (defaults to current).
        """
        self.screen = screen
        self.input = input_adapter
        self.config = config

        # Load profile
        profile_name = profile_name or config.get_current_profile_name()
        self.profile = config.load_profile(profile_name)
        logger.info(f'Using Profile: {self.profile.name}')

        # Initialize services
        self.scanner = ScanService(screen, self.profile)
        self.state = GameState()

    def _setup_hotkeys(self) -> None:
        """Register keyboard hotkeys for control."""

        def on_start():
            if not self.state.is_farming:
                print('\n[Resuming Automation]')
                self.state.start_farming()

        def on_pause():
            if self.state.is_farming:
                print('\n[Pausing Automation]')
                self.state.pause_farming()

        def on_stop():
            print('\n[Stopping Automation]')
            self.state.stop()

        self.input.unregister_all_hotkeys()
        self.input.register_hotkey('p', on_start)
        self.input.register_hotkey('m', on_pause)
        self.input.register_hotkey('l', on_stop)

    def _click_action(self, action_name: str) -> bool:
        """
        Click a named action from the profile.

        Args:
            action_name: Name of the action in the profile.

        Returns:
            True if action was found and clicked.
        """
        coords = self.profile.get_action(action_name)
        if not coords:
            logger.warning(f"Action '{action_name}' not found in profile")
            return False

        self.input.click(coords)
        logger.info(f'ACTION: {action_name}')
        return True

    def _buy_the_soul(self) -> bool:
        """
        Attempt to find and buy The Soul card.

        Returns:
            True if soul was found and purchased.
        """
        time.sleep(self.SOUL_WAIT_TIME)

        soul_match = self.scanner.scan_for_soul()
        if not soul_match:
            return False

        logger.info(f'Selecting SOUL card at {soul_match.position.to_tuple()}')
        self.state.record_soul_found()

        # Click the soul card
        self.input.click(soul_match.position)
        time.sleep(self.CLICK_DELAY)

        # Click "Use" button (offset below the card)
        use_button = soul_match.position.offset(0, 100)
        self.input.click(use_button)
        time.sleep(self.ACTION_DELAY)

        return True

    def _skip_slot_1(self) -> None:
        """Skip the first tag slot and check for soul."""
        self._click_action('skip_slot_1')
        self._buy_the_soul()

    def _skip_slot_2(self) -> None:
        """Skip the second tag slot and check for soul."""
        self._click_action('skip_slot_1')
        time.sleep(self.ACTION_DELAY)
        self._click_action('skip_slot_2')
        self._buy_the_soul()

    def _skip_both_slots(self) -> None:
        """Skip first slot, buy specialized skip, skip second slot."""
        self._click_action('skip_slot_1')
        self._buy_the_soul()

        self._click_action('package_specialized_skip')
        time.sleep(self.ACTION_DELAY)

        self._click_action('skip_slot_2')
        self._buy_the_soul()

    def _execute_decision(self, decision: FarmingDecision) -> None:
        """Execute the given farming decision."""
        if decision == FarmingDecision.SKIP_SLOT_1:
            self._skip_slot_1()
        elif decision == FarmingDecision.SKIP_SLOT_2:
            self._skip_slot_2()
        elif decision == FarmingDecision.SKIP_BOTH_SLOTS:
            self._skip_both_slots()
        # NONE decision - do nothing

    def _new_game(self) -> None:
        """Reset game state and start a new run."""
        self.input.press_key('esc')
        time.sleep(self.ACTION_DELAY)

        self._click_action('new_game_top')
        time.sleep(self.ACTION_DELAY)

        self._click_action('new_game_confirm')
        time.sleep(self.ACTION_DELAY)

        # Move mouse out of the way
        self.input.move_to(Coordinates(5, 5))
        time.sleep(self.RESET_DELAY)

        self.state.increment_run()
        logger.info('ACTION: New Game Started')

    def scan_and_decide(self) -> FarmingDecision:
        """
        Scan the screen and determine what action to take.

        Returns:
            The farming decision based on detected tags.
        """
        double_matches, charm_matches = self.scanner.scan_slots_for_tags()
        context = DecisionContext.from_scan_results(
            double_matches, charm_matches
        )
        decision = decide_farming_action(context)

        if decision != FarmingDecision.NONE:
            logger.info(f'DECISION: {get_decision_description(decision)}')

        return decision

    def run_iteration(self) -> None:
        """Run a single farming iteration (scan, decide, act, reset)."""
        decision = self.scan_and_decide()
        self._execute_decision(decision)
        self._new_game()

    def run(self) -> None:
        """
        Main farming loop.

        Runs until stopped via 'L' hotkey or KeyboardInterrupt.
        """
        print('Balatro Soul Farm Automation Ready.')
        print(f'Profile: {self.profile.name} - {self.profile.description}')
        print("Press 'P' to start/resume.")
        print("Press 'M' to pause loop.")
        print("Press 'L' to exit completely.")

        self._setup_hotkeys()

        try:
            while self.state.is_running:
                if self.state.is_farming:
                    self.run_iteration()
                else:
                    time.sleep(self.IDLE_SLEEP)
        except Exception as e:
            logger.error(f'Error in farming loop: {e}')
            raise
        finally:
            self.input.unregister_all_hotkeys()
