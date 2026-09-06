"""Unit tests for civicworkos.ledger.capability_ledger: Eq. 5."""

from __future__ import annotations

import pytest

from civicworkos.ledger.capability_ledger import CapabilityLedger, LedgerSnapshot


def test_e_kg_must_reconcile_to_e_k():
    """Paper Sec. 3.3: the group decomposition is required, not optional
    reporting -- E_kg summing to something other than E_k is a fixed data
    error, not a valid state."""
    with pytest.raises(ValueError, match="does not reconcile"):
        LedgerSnapshot(
            domain="structural_inspection", H_k=10, A_k=5, R_k=5, F_k=10, E_k=100,
            E_kg={"men": 80, "women": 15},  # sums to 95, not 100
        )


def test_e_kg_reconciled_is_accepted():
    snap = LedgerSnapshot(
        domain="structural_inspection", H_k=10, A_k=5, R_k=5, F_k=10, E_k=100,
        E_kg={"men": 68, "women": 32},
    )
    assert sum(snap.E_kg.values()) == pytest.approx(snap.E_k)


def test_negative_fields_rejected():
    with pytest.raises(ValueError, match="non-negative"):
        LedgerSnapshot(domain="d", H_k=-1, A_k=0, R_k=0, F_k=0, E_k=0)


def test_accrue_practice_accumulates():
    ledger = CapabilityLedger()
    ledger.initialize(LedgerSnapshot(domain="structural_inspection", H_k=0, A_k=0, R_k=0, F_k=0, E_k=0))
    ledger.accrue_practice("structural_inspection", 8.0)
    ledger.accrue_practice("structural_inspection", 5.6)
    assert ledger.current("structural_inspection").accrued_practice_hours == pytest.approx(13.6)
    assert len(ledger.history("structural_inspection")) == 3  # initial + 2 accruals


def test_accrue_practice_rejects_negative_hours():
    ledger = CapabilityLedger()
    ledger.initialize(LedgerSnapshot(domain="d", H_k=0, A_k=0, R_k=0, F_k=0, E_k=0))
    with pytest.raises(ValueError, match="non-negative"):
        ledger.accrue_practice("d", -1.0)


def test_reset_budget_period_zeroes_accrual():
    ledger = CapabilityLedger()
    ledger.initialize(LedgerSnapshot(domain="d", H_k=0, A_k=0, R_k=0, F_k=0, E_k=0))
    ledger.accrue_practice("d", 100.0)
    ledger.reset_budget_period("d")
    assert ledger.current("d").accrued_practice_hours == 0.0


def test_unknown_domain_raises():
    ledger = CapabilityLedger()
    with pytest.raises(KeyError, match="not been initialized"):
        ledger.current("nonexistent")


def test_update_group_shares_must_still_reconcile():
    ledger = CapabilityLedger()
    ledger.initialize(LedgerSnapshot(domain="d", H_k=0, A_k=0, R_k=0, F_k=0, E_k=100))
    ledger.update_group_shares("d", {"men": 68, "women": 32})
    assert ledger.current("d").E_kg == {"men": 68, "women": 32}
    with pytest.raises(ValueError, match="does not reconcile"):
        ledger.update_group_shares("d", {"men": 68, "women": 20})
