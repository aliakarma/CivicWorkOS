"""Unit tests for civicworkos.market.agents.HeuristicMarket.

This is [INVENTED] estimator code (see the module docstring in
market/agents.py) -- these tests check its own internal consistency
(bounds, oversight effects, D_skill = 1 - phi_m), NOT that it reproduces
any paper number. It must never be exercised by tests/smoke.
"""

from __future__ import annotations

from civicworkos.ledger.capability_ledger import LedgerSnapshot
from civicworkos.market.agents import HeuristicMarket
from civicworkos.policy.digital_twin import PolicyStatus
from civicworkos.twin.task import TaskProfile


def _task(**overrides) -> TaskProfile:
    defaults = dict(
        task_id="t1", service="s", domain="structural_inspection",
        cog=0.5, phy=0.5, emp=0.5, risk=0.5, auth=0.5, priv=0.5, urg=0.5, learn=0.5, crit=0.5,
        duration_hours=8.0,
    )
    defaults.update(overrides)
    return TaskProfile(**defaults)


def _ledger():
    return LedgerSnapshot(domain="structural_inspection", H_k=0, A_k=0, R_k=0, F_k=0, E_k=0)


def test_all_terms_and_debts_are_within_unit_interval():
    market = HeuristicMarket()
    task = _task()
    for mode in ("H", "A", "R", "H+A", "H+R", "A+R", "H+A+R"):
        estimate = market.query(task, mode, PolicyStatus.ALLOW, _ledger())
        for value in estimate.terms.__dict__.values():
            assert 0.0 <= value <= 1.0
        for value in estimate.debts.__dict__.values():
            assert 0.0 <= value <= 1.0
        assert 0.0 <= estimate.phi_m <= 1.0


def test_d_skill_always_equals_one_minus_phi_m():
    """The one debt component the paper DOES define as a computation
    (eq:phi): D_skill = 1 - phi_m, for every mode."""
    market = HeuristicMarket()
    task = _task()
    for mode in ("H", "A", "R", "H+A", "H+R", "A+R", "H+A+R"):
        estimate = market.query(task, mode, PolicyStatus.ALLOW, _ledger())
        assert estimate.debts.D_skill == 1.0 - estimate.phi_m


def test_pure_mode_phi_is_fixed_by_eq7():
    market = HeuristicMarket()
    task = _task()
    assert market.query(task, "H", PolicyStatus.ALLOW, _ledger()).phi_m == 1.0
    assert market.query(task, "A", PolicyStatus.ALLOW, _ledger()).phi_m == 0.0
    assert market.query(task, "R", PolicyStatus.ALLOW, _ledger()).phi_m == 0.0
    assert market.query(task, "A+R", PolicyStatus.ALLOW, _ledger()).phi_m == 0.0


def test_oversight_status_raises_cost_and_phi_per_algorithm1_line7():
    market = HeuristicMarket(oversight_cost_penalty=0.1, oversight_phi_boost=0.1)
    task = _task()
    allow = market.query(task, "H+A", PolicyStatus.ALLOW, _ledger())
    oversight = market.query(task, "H+A", PolicyStatus.ALLOW_WITH_OVERSIGHT, _ledger())
    assert oversight.terms.Cost > allow.terms.Cost
    assert oversight.phi_m > allow.phi_m


def test_hybrid_phi_uses_domain_configured_value_when_supplied():
    market = HeuristicMarket(hybrid_phi={"structural_inspection": {"H+A": 0.75, "H+R": 0.70, "H+A+R": 0.55}})
    task = _task(domain="structural_inspection")
    assert market.query(task, "H+R", PolicyStatus.ALLOW, _ledger()).phi_m == 0.70
