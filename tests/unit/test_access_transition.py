"""Unit tests for civicworkos.constraints.access: eq:accessshare, eq:access and eq:justtransition.

Includes the "who receives the protected practice" arithmetic of sec:whoworked:
a composition-blind 12.5% share against an access-constrained 27% share of the
capability budget. The budget and the composition figures are imported from
`manuscript_values` rather than restated, which is the Phase 3 correction for
finding N2 -- this file previously hard-coded an earlier draft's 2,073.6-hour
budget and the 259/560-hour figures that follow from it.
"""

from __future__ import annotations

import pytest

from civicworkos.constraints.access import (
    CapabilityAccessConstraint,
    JustTransitionConstraint,
    realized_access_share,
)
from manuscript_values import WORKED


def _budget() -> float:
    """B_k from eq:bkworked, at the manuscript's stated inputs."""
    from civicworkos.constraints.hcpb import HCPBParameters, capability_budget

    w = WORKED
    return capability_budget(
        HCPBParameters(
            N_k=w["N_k"], r_k=w["r_k"], h_k=w["h_k"], eta_k=w["eta_k"], B_k_min=w["B_min"]
        )
    )


def test_realized_access_share_normalizes_to_one():
    """tab:dist apportions B_k by share, so the two blocks must total B_k."""
    b_k = _budget()
    shares = realized_access_share({"men": 0.875 * b_k, "women": 0.125 * b_k})
    assert shares["men"] + shares["women"] == pytest.approx(1.0)
    assert shares["women"] == pytest.approx(0.125, abs=1e-9)


def test_realized_access_share_rejects_zero_denominator():
    with pytest.raises(ValueError, match="must be positive"):
        realized_access_share({"men": 0.0, "women": 0.0})


def test_composition_blind_vs_access_constrained_hours_worked_example():
    """sec:whoworked: incumbent composition is 87.5%/12.5% (men/women) while the
    qualified labour pool is 68%/32%.

    A composition-blind budget sends 622 of the 4,976.64 protected hours to
    women. The access constraint (theta = 0.32, epsilon = 0.05) requires at
    least 1,344 -- 2.16 times as many. The multiplier is the point: it is a
    property of the gap between incumbent composition and the labour pool, and
    it does not depend on the size of the budget at all.
    """
    w = WORKED
    b_k = _budget()
    composition_blind_hours = w["incumbent_women"] * b_k
    assert composition_blind_hours == pytest.approx(622.08, abs=0.01)

    constraint = CapabilityAccessConstraint(
        theta_kg=w["pool_women"], epsilon_k=w["epsilon_k"]
    )
    assert constraint.floor == pytest.approx(0.27, abs=1e-9)
    required_hours = constraint.required_hours(b_k)
    assert required_hours == pytest.approx(1343.69, abs=0.5)

    multiplier = required_hours / composition_blind_hours
    assert multiplier == pytest.approx(2.16, abs=5e-3)
    # Scale-invariance: the same multiplier at any budget.
    assert constraint.required_hours(1.0) / w["incumbent_women"] == pytest.approx(
        multiplier, rel=1e-12
    )


def test_access_constraint_is_satisfied_boundary():
    constraint = CapabilityAccessConstraint(theta_kg=0.32, epsilon_k=0.05)
    assert constraint.is_satisfied(0.27)
    assert constraint.is_satisfied(0.30)
    assert not constraint.is_satisfied(0.26999)


@pytest.mark.parametrize("theta,eps", [(-0.1, 0.05), (1.1, 0.05), (0.5, -0.1), (0.5, 1.1)])
def test_access_constraint_validates_inputs(theta, eps):
    with pytest.raises(ValueError):
        CapabilityAccessConstraint(theta_kg=theta, epsilon_k=eps)


def test_just_transition_constraint_both_clauses_must_hold():
    jtc = JustTransitionConstraint(tau_g=0.10, chi_min=0.80)
    assert jtc.is_satisfied(delta_g=0.05, chi_g=0.90)
    assert not jtc.is_satisfied(delta_g=0.15, chi_g=0.90)  # displacement too fast
    assert not jtc.is_satisfied(delta_g=0.05, chi_g=0.50)  # reskilling coverage too low
    assert not jtc.is_satisfied(delta_g=0.15, chi_g=0.50)  # both fail
