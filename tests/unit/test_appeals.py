"""Unit tests for civicworkos.appeals.contestability: Suppl. app:contest."""

from __future__ import annotations

from datetime import datetime

import pytest

from civicworkos.appeals.contestability import (
    APPEAL_WINDOWS,
    Appeal,
    AppealStatus,
    AppealType,
    upheld_appeal_rate,
)


def test_worker_windows_are_wider_than_routine_and_suspend_displacement():
    """Suppl. Table S1's stated asymmetry: worker access/displacement
    appeals get 40/30 days with displacement suspended; routine gets
    20/20 with nothing suspended."""
    routine = APPEAL_WINDOWS[AppealType.ROUTINE]
    worker = APPEAL_WINDOWS[AppealType.WORKER_ACCESS_OR_DISPLACEMENT]
    assert worker.lodge_working_days > routine.lodge_working_days
    assert worker.resolve_working_days > routine.resolve_working_days
    assert worker.suspends == "displacement"
    assert routine.suspends is None


def test_rights_affecting_appeals_suspend_outcome_with_shorter_resolve_window():
    rights = APPEAL_WINDOWS[AppealType.RIGHTS_AFFECTING]
    assert rights.suspends == "outcome"
    assert rights.resolve_working_days == 10


def test_standing_irrespective_of_contract_status():
    """Suppl. S1.1: standing is granted regardless of contract status --
    this repository records contract_status but never uses it to gate
    appeal creation (there is no such check anywhere in Appeal.__init__)."""
    appeal = Appeal(
        appeal_id="a1", task_id="t1", appeal_type=AppealType.WORKER_ACCESS_OR_DISPLACEMENT,
        appellant_id="worker-42", appellant_contract_status="platform_mediated",
        lodged_at=datetime(2026, 1, 1),
    )
    assert appeal.status == AppealStatus.LODGED  # created successfully, no status-based gate


def test_uphold_requires_named_decision_maker():
    appeal = Appeal(
        appeal_id="a1", task_id="t1", appeal_type=AppealType.ROUTINE,
        appellant_id="resident-1", appellant_contract_status="n/a",
        lodged_at=datetime(2026, 1, 1),
    )
    with pytest.raises(ValueError, match="named accountable human"):
        appeal.uphold("", "no name given", datetime(2026, 1, 5))


def test_uphold_records_rationale_even_if_it_departs_from_recommendation():
    appeal = Appeal(
        appeal_id="a1", task_id="t1", appeal_type=AppealType.ROUTINE,
        appellant_id="resident-1", appellant_contract_status="n/a",
        lodged_at=datetime(2026, 1, 1),
    )
    appeal.uphold("Jane Doe, Ombudsman", "departs from system recommendation because X", datetime(2026, 1, 5))
    assert appeal.status == AppealStatus.UPHELD
    assert appeal.remedy_decision_maker == "Jane Doe, Ombudsman"
    assert "departs" in appeal.remedy_rationale


def test_is_overdue():
    appeal = Appeal(
        appeal_id="a1", task_id="t1", appeal_type=AppealType.ROUTINE,
        appellant_id="resident-1", appellant_contract_status="n/a",
        lodged_at=datetime(2026, 1, 1),
    )
    assert not appeal.is_overdue(datetime(2026, 1, 10))
    assert appeal.is_overdue(datetime(2026, 3, 1))


def test_upheld_appeal_rate_computed_over_resolved_only():
    appeals = [
        Appeal("a1", "t1", AppealType.ROUTINE, "u1", "permanent", datetime(2026, 1, 1), status=AppealStatus.UPHELD),
        Appeal("a2", "t2", AppealType.ROUTINE, "u2", "permanent", datetime(2026, 1, 1), status=AppealStatus.DENIED),
        Appeal("a3", "t3", AppealType.ROUTINE, "u3", "permanent", datetime(2026, 1, 1), status=AppealStatus.LODGED),
    ]
    # 1 upheld, 1 denied, 1 still pending (excluded from the denominator)
    assert upheld_appeal_rate(appeals) == pytest.approx(0.5)


def test_upheld_appeal_rate_with_no_resolved_appeals_is_zero():
    appeals = [
        Appeal("a1", "t1", AppealType.ROUTINE, "u1", "permanent", datetime(2026, 1, 1)),
    ]
    assert upheld_appeal_rate(appeals) == 0.0
