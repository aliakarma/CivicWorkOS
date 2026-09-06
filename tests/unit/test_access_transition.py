"""Unit tests for civicworkos.constraints.access: Eq. 10-12.

Includes the worked example's "who receives the protected work" numbers
(Paper Sec. 5.3): a composition-blind 12.5% share vs. an access-
constrained 27% share of the 2073.6-hour budget.
"""

from __future__ import annotations

import pytest

from civicworkos.constraints.access import (
    CapabilityAccessConstraint,
    JustTransitionConstraint,
    realized_access_share,
)


def test_realized_access_share_normalizes_to_one():
    shares = realized_access_share({"men": 1814.6, "women": 259.0})
    assert shares["men"] + shares["women"] == pytest.approx(1.0)
    assert shares["women"] == pytest.approx(0.125, abs=1e-3)


def test_realized_access_share_rejects_zero_denominator():
    with pytest.raises(ValueError, match="must be positive"):
        realized_access_share({"men": 0.0, "women": 0.0})


def test_composition_blind_vs_access_constrained_hours_worked_example():
    """Paper Sec. 5.3: incumbent composition is 87.5%/12.5% (men/women);
    the qualified labour pool is 68%/32%. A composition-blind budget
    sends 0.125*2073.6 = 259 hours to women; the access constraint
    (theta=0.32, epsilon=0.05) requires at least 0.27*2073.6 = 560 hours
    -- "2.2 times" the composition-blind rate.
    """
    b_k = 2073.6
    composition_blind_hours = 0.125 * b_k
    assert composition_blind_hours == pytest.approx(259.2, abs=0.1)

    constraint = CapabilityAccessConstraint(theta_kg=0.32, epsilon_k=0.05)
    assert constraint.floor == pytest.approx(0.27, abs=1e-9)
    required_hours = constraint.required_hours(b_k)
    assert required_hours == pytest.approx(559.87, abs=0.5)

    multiplier = required_hours / composition_blind_hours
    assert multiplier == pytest.approx(2.16, abs=0.05)


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
