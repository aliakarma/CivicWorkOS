"""Unit tests for civicworkos.analytic.debt_model: eq:cadode, eq:cadmodel.

Beyond the fig:cad-trend reproduction in tests/smoke, this file checks the
model's stated mathematical properties directly: pi_j(0) = 0, the pi_inf = 1
saturation limit c_j * tau_j, unbounded linear growth when pi_inf < 1, and the
weighted five-component sum of eq:cadmodel.

It also pins the property that motivated replacing the one-component model: a
strategy saturates only when *every* weighted component is fully replenished,
so a single unreplenished component is enough to leave total debt unbounded.
"""

from __future__ import annotations

import pytest

from civicworkos.analytic.debt_model import (
    CAD_COMPONENTS,
    ComponentDebtParameters,
    accumulated_debt,
    bounded_ceiling,
    component_debt,
    delivery_fraction,
    residual_slope,
    strategy_from_table,
)

WEIGHTS = {"skill": 0.28, "fall": 0.22, "acct": 0.18, "dep": 0.12, "trans": 0.20}


def _uniform(c_j=10.0, pi_inf=0.0, tau=0.0):
    """One strategy with the same parameters on all five components."""
    return {j: ComponentDebtParameters(c_j, pi_inf, tau) for j in CAD_COMPONENTS}


# --- eq:cadode, the per-component replenishment path ---------------------

def test_delivery_fraction_is_zero_at_t_zero():
    p = ComponentDebtParameters(c_j=10, pi_inf=0.8, tau=2.0)
    assert delivery_fraction(0.0, p) == 0.0


def test_delivery_fraction_converges_to_pi_inf():
    p = ComponentDebtParameters(c_j=10, pi_inf=0.8, tau=2.0)
    assert delivery_fraction(1000.0, p) == pytest.approx(0.8, abs=1e-6)


def test_component_debt_is_zero_at_t_zero():
    p = ComponentDebtParameters(c_j=10, pi_inf=0.5, tau=3.0)
    assert component_debt(0.0, p) == pytest.approx(0.0)


def test_component_saturates_at_c_tau_when_fully_replenished():
    """pi_inf = 1 removes the linear term, so the component stops at c_j * tau_j."""
    p = ComponentDebtParameters(c_j=10, pi_inf=1.0, tau=3.0)
    assert component_debt(1000.0, p) == pytest.approx(p.c_j * p.tau, rel=1e-6)


def test_component_unbounded_when_never_replenished():
    p = ComponentDebtParameters(c_j=10, pi_inf=0.0, tau=3.0)
    assert component_debt(100.0, p) == pytest.approx(1000.0)  # C_j(t) = c_j * t


def test_partial_replenishment_is_linear_at_a_reduced_slope():
    p = ComponentDebtParameters(c_j=10, pi_inf=0.4, tau=2.0)
    far, further = component_debt(500.0, p), component_debt(600.0, p)
    assert (further - far) / 100.0 == pytest.approx(10.0 * 0.6, abs=1e-6)


# --- eq:cadmodel, the weighted sum ---------------------------------------

def test_accumulated_debt_is_the_weighted_sum_of_components():
    strategy = _uniform(c_j=10.0, pi_inf=0.0, tau=0.0)
    # Every component accrues 10t and the weights sum to one, so C(t) = 10t.
    assert accumulated_debt(10.0, strategy, WEIGHTS) == pytest.approx(100.0, abs=1e-9)


def test_components_are_weighted_individually():
    """Doubling one component's rate moves C(t) by that component's weight."""
    base = _uniform()
    raised = dict(base, dep=ComponentDebtParameters(20.0, 0.0, 0.0))
    delta = accumulated_debt(10.0, raised, WEIGHTS) - accumulated_debt(10.0, base, WEIGHTS)
    assert delta == pytest.approx(WEIGHTS["dep"] * 10.0 * 10.0, abs=1e-9)


def test_residual_slope_is_zero_only_when_every_component_replenishes():
    """The property the one-component model obscured.

    Total debt is bounded iff *every* weighted component is fully replenished.
    One unreplenished component leaves the whole trajectory unbounded, which is
    exactly CivicWorkOS's position on vendor dependency.
    """
    all_replenished = _uniform(pi_inf=1.0, tau=2.0)
    assert residual_slope(all_replenished, WEIGHTS) == pytest.approx(0.0, abs=1e-12)

    one_short = dict(all_replenished, dep=ComponentDebtParameters(10.0, 0.10, 2.0))
    assert residual_slope(one_short, WEIGHTS) == pytest.approx(
        WEIGHTS["dep"] * 10.0 * 0.90, abs=1e-9
    )
    assert residual_slope(one_short, WEIGHTS) > 0.0


def test_bounded_ceiling_is_the_saturating_part():
    strategy = _uniform(pi_inf=1.0, tau=2.0)
    assert bounded_ceiling(strategy, WEIGHTS) == pytest.approx(20.0, abs=1e-9)
    # With no residual slope the ceiling is the actual limit of C(t).
    assert accumulated_debt(500.0, strategy, WEIGHTS) == pytest.approx(20.0, abs=1e-6)


def test_bounded_ceiling_is_not_a_limit_when_a_residual_remains():
    strategy = dict(
        _uniform(pi_inf=1.0, tau=2.0), dep=ComponentDebtParameters(10.0, 0.0, 0.0)
    )
    ceiling = bounded_ceiling(strategy, WEIGHTS)
    assert accumulated_debt(500.0, strategy, WEIGHTS) > ceiling


def test_strategy_from_table_round_trips_a_cadparams_row():
    row = {j: (10.0, 0.5, 1.5) for j in CAD_COMPONENTS}
    strategy = strategy_from_table(row)
    assert set(strategy) == set(CAD_COMPONENTS)
    assert strategy["skill"] == ComponentDebtParameters(10.0, 0.5, 1.5)


# --- validation ----------------------------------------------------------

@pytest.mark.parametrize("bad_kwargs", [
    dict(c_j=-1, pi_inf=0.5, tau=1.0),
    dict(c_j=1, pi_inf=1.5, tau=1.0),
    dict(c_j=1, pi_inf=0.5, tau=-1.0),
])
def test_parameters_validate(bad_kwargs):
    with pytest.raises(ValueError):
        ComponentDebtParameters(**bad_kwargs)


def test_negative_time_rejected():
    p = ComponentDebtParameters(c_j=10, pi_inf=0.5, tau=1.0)
    with pytest.raises(ValueError):
        component_debt(-1.0, p)
    with pytest.raises(ValueError):
        delivery_fraction(-1.0, p)
    with pytest.raises(ValueError):
        accumulated_debt(-1.0, _uniform(), WEIGHTS)


def test_weights_must_sum_to_one():
    with pytest.raises(ValueError, match="sum to 1.0"):
        accumulated_debt(1.0, _uniform(), {"skill": 0.5, "fall": 0.2})


def test_missing_component_is_an_error_not_a_zero():
    """A component present in the weights but absent from the strategy is a
    bug, not a debt-free component. Treating it as zero is how a
    five-component model gets reported as though it were one."""
    partial = {j: ComponentDebtParameters(10.0, 0.0, 0.0) for j in ("skill", "fall")}
    with pytest.raises(ValueError, match="dep"):
        accumulated_debt(1.0, partial, WEIGHTS)
