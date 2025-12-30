"""
Tests for the domain layer decision logic.
"""

from balatro.domain.decisions import (
    DecisionContext,
    FarmingDecision,
    decide_farming_action,
    get_decision_description,
)
from balatro.domain.model import Coordinates, ScanResult


class TestDecisionContext:
    """Tests for DecisionContext creation."""

    def test_from_empty_results(self):
        context = DecisionContext.from_scan_results([], [])
        assert not context.has_double_slot1
        assert not context.has_charm_slot1
        assert not context.has_charm_slot2

    def test_from_double_slot1(self):
        double_matches = [
            ScanResult('double.png', Coordinates(500, 500), 0.95, slot=1)
        ]
        context = DecisionContext.from_scan_results(double_matches, [])
        assert context.has_double_slot1
        assert not context.has_charm_slot1

    def test_from_charm_both_slots(self):
        charm_matches = [
            ScanResult('charm.png', Coordinates(500, 500), 0.95, slot=1),
            ScanResult('charm.png', Coordinates(600, 500), 0.90, slot=2),
        ]
        context = DecisionContext.from_scan_results([], charm_matches)
        assert context.has_charm_slot1
        assert context.has_charm_slot2


class TestDecideFarmingAction:
    """Tests for the decide_farming_action function."""

    def test_no_matches_returns_none(self):
        context = DecisionContext()
        decision = decide_farming_action(context)
        assert decision == FarmingDecision.NONE

    def test_double_and_charm_returns_skip_both(self):
        context = DecisionContext(has_double_slot1=True, has_charm_slot2=True)
        decision = decide_farming_action(context)
        assert decision == FarmingDecision.SKIP_BOTH_SLOTS

    def test_charm_both_slots_returns_skip_both(self):
        context = DecisionContext(has_charm_slot1=True, has_charm_slot2=True)
        decision = decide_farming_action(context)
        assert decision == FarmingDecision.SKIP_BOTH_SLOTS

    def test_charm_slot1_only_returns_skip_slot1(self):
        context = DecisionContext(has_charm_slot1=True)
        decision = decide_farming_action(context)
        assert decision == FarmingDecision.SKIP_SLOT_1

    def test_charm_slot2_only_returns_skip_slot2(self):
        context = DecisionContext(has_charm_slot2=True)
        decision = decide_farming_action(context)
        assert decision == FarmingDecision.SKIP_SLOT_2

    def test_double_alone_returns_none(self):
        # Double without charm in slot 2 should not trigger
        context = DecisionContext(has_double_slot1=True)
        decision = decide_farming_action(context)
        assert decision == FarmingDecision.NONE


class TestDecisionDescription:
    """Tests for get_decision_description."""

    def test_descriptions_exist_for_all_decisions(self):
        for decision in FarmingDecision:
            desc = get_decision_description(decision)
            assert isinstance(desc, str)
            assert len(desc) > 0
