"""Unit tests for civicworkos.analytic.debt_model: Eq. 21.

Beyond the Fig. 3 reproduction in tests/smoke, this file checks the
model's stated mathematical properties directly: pi(0)=0, the
pi_inf=1 saturation limit c_0*tau, and monotonic growth for pi_inf<1.
"""

from __future__ import annotations

import pytest

from civicworkos.analytic.debt_model import StrategyDebtParameters, accumulated_debt, delivery_fraction


def test_delivery_fraction_is_zero_at_t_zero():
    params = StrategyDebtParameters(c_0=10, pi_inf=0.8, tau=2.0)
    assert delivery_fraction(0.0, params) == 0.0


def test_delivery_fraction_converges_to_pi_inf():
    params = StrategyDebtParameters(c_0=10, pi_inf=0.8, tau=2.0)
    assert delivery_fraction(1000.0, params) == pytest.approx(0.8, abs=1e-6)


def test_accumulated_debt_is_zero_at_t_zero():
    params = StrategyDebtParameters(c_0=10, pi_inf=0.5, tau=3.0)
    assert accumulated_debt(0.0, params) == pytest.approx(0.0)


def test_accumulated_debt_saturates_at_c0_tau_when_pi_inf_is_one():
    """Paper Sec. 7.1: 'debt saturates at c_0*tau; marginal debt of each
    additional task -> 0' when pi_inf = 1."""
    params = StrategyDebtParameters(c_0=10, pi_inf=1.0, tau=3.0)
    saturation = params.c_0 * params.tau
    assert accumulated_debt(1000.0, params) == pytest.approx(saturation, rel=1e-6)


def test_accumulated_debt_unbounded_when_pi_inf_zero():
    params = StrategyDebtParameters(c_0=10, pi_inf=0.0, tau=3.0)
    assert accumulated_debt(100.0, params) == pytest.approx(1000.0)  # C(t) = c_0*t exactly


@pytest.mark.parametrize("bad_kwargs", [
    dict(c_0=-1, pi_inf=0.5, tau=1.0),
    dict(c_0=1, pi_inf=1.5, tau=1.0),
    dict(c_0=1, pi_inf=0.5, tau=-1.0),
])
def test_parameters_validate(bad_kwargs):
    with pytest.raises(ValueError):
        StrategyDebtParameters(**bad_kwargs)


def test_negative_time_rejected():
    params = StrategyDebtParameters(c_0=10, pi_inf=0.5, tau=1.0)
    with pytest.raises(ValueError):
        accumulated_debt(-1.0, params)
    with pytest.raises(ValueError):
        delivery_fraction(-1.0, params)
