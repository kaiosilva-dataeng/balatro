"""
Domain decision logic for the Balatro automation.

Pure functions that contain the core business rules for farming decisions.
These functions have no I/O dependencies and are easily testable.
"""

from dataclasses import dataclass
from enum import Enum, auto

from .model import ScanResult


class FarmingDecision(Enum):
    """Represents the decision of what action to take after scanning."""

    NONE = auto()
    SKIP_SLOT_1 = auto()
    SKIP_SLOT_2 = auto()
    SKIP_BOTH_SLOTS = auto()


@dataclass
class DecisionContext:
    """
    Value Object containing the context for making a farming decision.
    """

    has_double_slot1: bool = False
    has_charm_slot1: bool = False
    has_charm_slot2: bool = False

    @classmethod
    def from_scan_results(
        cls, double_matches: list[ScanResult], charm_matches: list[ScanResult]
    ) -> "DecisionContext":
        """
        Factory method to create context from scan results.
        """
        has_double_slot1 = any(m.slot == 1 for m in double_matches)
        has_charm_slot1 = any(m.slot == 1 for m in charm_matches)
        has_charm_slot2 = any(m.slot == 2 for m in charm_matches)

        return cls(
            has_double_slot1=has_double_slot1,
            has_charm_slot1=has_charm_slot1,
            has_charm_slot2=has_charm_slot2,
        )


def decide_farming_action(context: DecisionContext) -> FarmingDecision:
    """
    Pure business logic to decide what farming action to take.

    Decision rules:
    1. If double in slot 1 AND charm in slot 2 -> skip both
    2. If charm in slot 1 AND charm in slot 2 -> skip both
    3. If only charm in slot 1 -> skip slot 1
    4. If only charm in slot 2 -> skip slot 2
    5. Otherwise -> no action

    Args:
        context: The decision context with detected tags

    Returns:
        The farming decision to execute
    """
    if context.has_double_slot1 and context.has_charm_slot2:
        return FarmingDecision.SKIP_BOTH_SLOTS

    if context.has_charm_slot1 and context.has_charm_slot2:
        return FarmingDecision.SKIP_BOTH_SLOTS

    if context.has_charm_slot1:
        return FarmingDecision.SKIP_SLOT_1

    if context.has_charm_slot2:
        return FarmingDecision.SKIP_SLOT_2

    return FarmingDecision.NONE


def get_decision_description(decision: FarmingDecision) -> str:
    """Get a human-readable description of the decision."""
    descriptions = {
        FarmingDecision.NONE: "No matching tags found",
        FarmingDecision.SKIP_SLOT_1: "Skip for charm (slot 1)",
        FarmingDecision.SKIP_SLOT_2: "Skip for charm (slot 2)",
        FarmingDecision.SKIP_BOTH_SLOTS: "Skip for double/charm and charm",
    }
    return descriptions.get(decision, "Unknown decision")
