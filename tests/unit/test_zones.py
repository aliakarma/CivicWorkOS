"""Unit tests for civicworkos.zones.oversight_zones: tab:zones, Suppl. S1.4.

The load-bearing property under test: automatic DEMOTION is allowed;
automatic RESTORATION is not, and must always carry a panel decision.
"""

from __future__ import annotations

import pytest

from civicworkos.zones.oversight_zones import Zone, ZoneRegistry


def test_assign_and_read_current_zone():
    registry = ZoneRegistry()
    registry.assign("bridge_inspection", Zone.Z2_AUGMENTED)
    assert registry.current_zone("bridge_inspection") == Zone.Z2_AUGMENTED


def test_automatic_demotion_on_appeal_threshold():
    registry = ZoneRegistry()
    registry.assign("bridge_inspection", Zone.Z2_AUGMENTED)
    transition = registry.demote_on_appeal_threshold("bridge_inspection", upheld_appeal_rate=0.30, threshold=0.20)
    assert transition is not None
    assert transition.automatic is True
    assert transition.to_zone == Zone.Z3_HUMAN_AUTHORITY
    assert registry.current_zone("bridge_inspection") == Zone.Z3_HUMAN_AUTHORITY


def test_no_demotion_below_threshold():
    registry = ZoneRegistry()
    registry.assign("bridge_inspection", Zone.Z2_AUGMENTED)
    transition = registry.demote_on_appeal_threshold("bridge_inspection", upheld_appeal_rate=0.05, threshold=0.20)
    assert transition is None
    assert registry.current_zone("bridge_inspection") == Zone.Z2_AUGMENTED


def test_automatic_restoration_is_rejected():
    """Suppl. S1.4: restoration requires an affirmative panel decision
    and cannot occur automatically."""
    registry = ZoneRegistry()
    registry.assign("bridge_inspection", Zone.Z3_HUMAN_AUTHORITY)
    with pytest.raises(ValueError, match="affirmative panel decision"):
        registry.transition("bridge_inspection", Zone.Z2_AUGMENTED, reason="looks fine now", automatic=True)


def test_restoration_with_panel_decision_succeeds():
    registry = ZoneRegistry()
    registry.assign("bridge_inspection", Zone.Z3_HUMAN_AUTHORITY)
    transition = registry.transition(
        "bridge_inspection",
        Zone.Z2_AUGMENTED,
        reason="panel review after sustained safety performance",
        authorizing_panel_decision="PANEL-2026-014",
    )
    assert transition.to_zone == Zone.Z2_AUGMENTED
    assert registry.current_zone("bridge_inspection") == Zone.Z2_AUGMENTED


def test_z4_is_terminal_for_further_demotion():
    registry = ZoneRegistry()
    registry.assign("bridge_inspection", Zone.Z4_HUMAN_RESERVED)
    transition = registry.demote_on_appeal_threshold("bridge_inspection", upheld_appeal_rate=0.99, threshold=0.01)
    assert transition is None  # already at the most restrictive zone


def test_history_records_every_transition():
    registry = ZoneRegistry()
    registry.assign("bridge_inspection", Zone.Z1_AUTONOMOUS)
    registry.demote_on_appeal_threshold("bridge_inspection", upheld_appeal_rate=0.5, threshold=0.1)
    assert len(registry.history("bridge_inspection")) == 1
