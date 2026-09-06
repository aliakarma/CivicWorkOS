"""Unit tests for civicworkos.online.algorithm1.admissible(): Eq. 18.

This is the paper's most important correction (Sec. 4.5) and the one
report Sec. 9.1's failure-mode #1 warns is easiest to get wrong:
implementing a NAIVE per-constraint filter instead of the
feasibility-restoration form causes total collapse to Z4 in exactly the
below-threshold state the framework exists to escape. Every branch of
Eq. 18 is exercised explicitly below so this property cannot regress
silently.
"""

from __future__ import annotations

from civicworkos.online.algorithm1 import admissible


def _base_kwargs(**overrides):
    kwargs = dict(
        safety_estimate=0.9,
        safety_min=0.5,
        resilience_now=50.0,
        delta_res=0.0,
        rho_s=30.0,
        lambda_accrued_now=2000.0,
        ell_i=8.0,
        phi_m=0.7,
        b_bar_k=1500.0,
    )
    kwargs.update(overrides)
    return kwargs


def test_safety_floor_rejects_unsafe_mode():
    ok, reason = admissible(**_base_kwargs(safety_estimate=0.3, safety_min=0.5))
    assert not ok
    assert reason == "safety_floor"


def test_admissible_when_all_clauses_satisfied():
    ok, reason = admissible(**_base_kwargs())
    assert ok
    assert reason is None


def test_resilience_clause_ordinary_case_rejects_a_mode_that_breaches_threshold():
    """Reserve is currently ABOVE threshold (50 >= 30); a mode whose
    delta_res would push it below threshold is rejected."""
    ok, reason = admissible(**_base_kwargs(resilience_now=50.0, rho_s=30.0, delta_res=-25.0))
    assert not ok
    assert reason == "resilience_clause"


def test_resilience_feasibility_restoration_branch_admits_improving_mode():
    """THE KEY CORRECTION (Eq. 18, clause 2): reserve is currently BELOW
    threshold (20 < 30). A naive filter would reject every mode here. The
    paper's actual rule admits a mode that does not worsen it
    (delta_res >= 0), even though the post-state (20+5=25) is still below
    rho_s=30 -- this is what lets the city climb back above threshold."""
    ok, reason = admissible(**_base_kwargs(resilience_now=20.0, rho_s=30.0, delta_res=5.0))
    assert ok
    assert reason is None


def test_resilience_feasibility_restoration_branch_still_rejects_a_worsening_mode():
    """Same below-threshold state, but this candidate mode WORSENS
    reserve (delta_res < 0) -- must still be rejected even though the
    city is already below threshold, per Eq. 18's 'must not worsen it'."""
    ok, reason = admissible(**_base_kwargs(resilience_now=20.0, rho_s=30.0, delta_res=-1.0))
    assert not ok
    assert reason == "resilience_clause"


def test_capability_clause_accrual_is_monotonic_so_a_satisfied_budget_stays_satisfied():
    """Unlike resilience (which a mode CAN reduce), accrued practice
    Lambda_k only ever increases (ell_i, phi_m >= 0). So once
    lambda_accrued_now already meets the pro-rated budget, EVERY mode
    remains admissible on this clause, including a phi_m=0 mode -- there
    is no 'ordinary' capability rejection distinct from the
    feasibility-restoration case below, because Lambda cannot be pushed
    back below a threshold it has already cleared."""
    ok, reason = admissible(
        **_base_kwargs(lambda_accrued_now=1600.0, b_bar_k=1500.0, ell_i=200.0, phi_m=0.0)
    )
    assert ok
    assert reason is None


def test_capability_feasibility_restoration_branch_admits_any_phi_positive_mode():
    """THE KEY CORRECTION (Eq. 18, clause 3): Lambda_k is currently BELOW
    the pro-rated trajectory (1000 < 1500) -- the domain is already
    behind budget. A naive filter would reject every mode that doesn't
    immediately close the gap. The paper's rule admits ANY mode with
    phi_m > 0, even a small one, because it 'contributes to restoring'
    the budget rather than requiring it be restored in one step."""
    ok, reason = admissible(
        **_base_kwargs(lambda_accrued_now=1000.0, b_bar_k=1500.0, ell_i=8.0, phi_m=0.1)
    )
    assert ok
    assert reason is None


def test_capability_feasibility_restoration_branch_rejects_phi_zero_mode():
    """Same below-budget state, but a fully-automated mode (phi_m=0)
    contributes NOTHING to restoring the budget and must still be
    rejected -- this is exactly the pathology the paper names: 'a city
    below threshold would have every mode removed and every task routed
    to human-reserved execution, including the robot allocations that
    would free the human capacity needed to climb back above threshold' --
    Eq. 18 prevents routing to Z4 for OTHER modes, but a phi=0 mode
    itself is correctly excluded because it cannot help."""
    ok, reason = admissible(
        **_base_kwargs(lambda_accrued_now=1000.0, b_bar_k=1500.0, ell_i=8.0, phi_m=0.0)
    )
    assert not ok
    assert reason == "capability_clause"


def test_capability_clause_satisfied_when_post_state_clears_budget():
    ok, reason = admissible(
        **_base_kwargs(lambda_accrued_now=1490.0, b_bar_k=1500.0, ell_i=8.0, phi_m=1.0)
    )
    assert ok
    assert reason is None


def test_clause_order_safety_checked_before_resilience_and_capability():
    """An unsafe mode is rejected on the safety floor even if it would
    also fail the resilience or capability clauses -- the reason
    reported must be the FIRST failing clause (Eq. 18's stated order)."""
    ok, reason = admissible(
        **_base_kwargs(
            safety_estimate=0.1, safety_min=0.5,
            resilience_now=20.0, rho_s=30.0, delta_res=-5.0,
            lambda_accrued_now=1000.0, b_bar_k=1500.0, phi_m=0.0,
        )
    )
    assert not ok
    assert reason == "safety_floor"
