"""Unit tests for civicworkos.policy.digital_twin: eq:policy."""

from __future__ import annotations

from datetime import date

import pytest

from civicworkos.policy.digital_twin import (
    PolicyDigitalTwin,
    PolicyRule,
    PolicyStatus,
    requires_licensed_human_rule,
)
from civicworkos.twin.task import TaskProfile


def _task(**overrides) -> TaskProfile:
    defaults = dict(
        task_id="t1", service="structural_inspection_service", domain="structural_inspection",
        cog=0.8, phy=0.6, emp=0.1, risk=0.7, auth=0.9, priv=0.2, urg=0.4, learn=0.8, crit=0.9,
        duration_hours=10.0,
    )
    defaults.update(overrides)
    return TaskProfile(**defaults)


def test_statutory_signoff_reduces_mode_set_to_worked_example():
    twin = PolicyDigitalTwin()
    twin.add_rule(
        requires_licensed_human_rule(
            "signoff", "v1", date(2026, 1, 1), "statutory sign-off requirement"
        )
    )
    surviving = twin.filter_modes(_task(), t=date(2026, 6, 1))
    assert set(surviving.keys()) == {"H", "H+A", "H+R", "H+A+R"}
    for mode in surviving.values():
        assert mode == PolicyStatus.ALLOW


def test_prohibited_modes_absent_from_status_per_mode():
    twin = PolicyDigitalTwin()
    twin.add_rule(requires_licensed_human_rule("signoff", "v1", date(2026, 1, 1), "d"))
    assert twin.status(_task(), "A", date(2026, 6, 1)) == PolicyStatus.PROHIBIT
    assert twin.status(_task(), "H", date(2026, 6, 1)) == PolicyStatus.ALLOW


def test_no_rules_means_everything_allowed():
    twin = PolicyDigitalTwin()
    surviving = twin.filter_modes(_task())
    assert len(surviving) == 7


def test_rule_not_yet_effective_is_ignored():
    twin = PolicyDigitalTwin()
    twin.add_rule(requires_licensed_human_rule("future_rule", "v1", date(2030, 1, 1), "d"))
    surviving = twin.filter_modes(_task(), t=date(2026, 1, 1))
    assert len(surviving) == 7  # rule not yet in force


def test_most_restrictive_status_wins_when_rules_overlap():
    def always_restrict(task, mode):
        return PolicyStatus.RESTRICT

    def always_oversight(task, mode):
        return PolicyStatus.ALLOW_WITH_OVERSIGHT

    twin = PolicyDigitalTwin(
        [
            PolicyRule("r1", "v1", date(2020, 1, 1), "d", always_restrict),
            PolicyRule("r2", "v1", date(2020, 1, 1), "d", always_oversight),
        ]
    )
    assert twin.status(_task(), "H") == PolicyStatus.RESTRICT


def test_unknown_mode_rejected():
    twin = PolicyDigitalTwin()
    with pytest.raises(ValueError, match="unknown execution mode"):
        twin.status(_task(), "Z", date(2026, 1, 1))


def test_staffed_mode_names_are_accepted():
    """sec:problem writes a staffed mode as an execution mode paired with a
    roster at a declared career stage. Validation applies to the execution mode;
    the roster suffix is free-form, because which rosters are admissible depends
    on who is available for the task rather than on a fixed enumeration."""
    twin = PolicyDigitalTwin()
    assert twin.status(_task(), "H+A+R/a1", date(2026, 1, 1)) == PolicyStatus.ALLOW
    assert twin.status(_task(), "H/a0", date(2026, 1, 1)) == PolicyStatus.ALLOW
    with pytest.raises(ValueError, match="unknown execution mode"):
        twin.status(_task(), "Z/a1", date(2026, 1, 1))


def test_rule_can_be_added_live_without_redeploying_the_market():
    """Scenario vii (Suppl. Table S2): a new prohibit rule can be added
    without redeploying the market -- exercised directly here."""
    twin = PolicyDigitalTwin()
    assert twin.status(_task(), "A") == PolicyStatus.ALLOW

    def new_ban(task, mode):
        return PolicyStatus.PROHIBIT if mode == "A" else None

    twin.add_rule(PolicyRule("new_reg", "v2", date(2026, 1, 1), "new municipal regulation", new_ban))
    assert twin.status(_task(), "A") == PolicyStatus.PROHIBIT
    assert twin.status(_task(), "H") == PolicyStatus.ALLOW
