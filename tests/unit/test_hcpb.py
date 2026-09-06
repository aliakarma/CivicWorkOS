"""Unit tests for civicworkos.constraints.hcpb: Eq. 7-9."""

from __future__ import annotations

import pytest

from civicworkos.constraints.hcpb import (
    HCPBParameters,
    capability_budget,
    hcpb_satisfied,
    hcpb_shortfall,
    phi_for_mode,
)


def test_phi_fixed_for_pure_modes():
    assert phi_for_mode("H", {}) == 1.0
    assert phi_for_mode("A", {}) == 0.0
    assert phi_for_mode("R", {}) == 0.0
    assert phi_for_mode("A+R", {}) == 0.0


def test_phi_for_hybrid_requires_configuration():
    with pytest.raises(KeyError, match="not configured"):
        phi_for_mode("H+A", {})


def test_phi_for_hybrid_uses_configured_value():
    assert phi_for_mode("H+R", {"H+R": 0.70}) == 0.70


def test_phi_for_hybrid_rejects_out_of_range():
    with pytest.raises(ValueError, match=r"\[0,1\]"):
        phi_for_mode("H+A", {"H+A": 1.5})


def test_capability_budget_floor_binds_when_estimate_is_low():
    params = HCPBParameters(N_k=2, r_k=0.05, h_k=100, eta_k=1.0, B_k_min=1200)
    # eta*N*r*h = 1*2*0.05*100 = 10, far below the 1200 floor.
    assert capability_budget(params) == 1200


def test_capability_budget_estimate_binds_when_high():
    params = HCPBParameters(N_k=24, r_k=0.12, h_k=600, eta_k=1.2, B_k_min=1200)
    assert capability_budget(params) == pytest.approx(2073.6)


def test_units_close_people_times_rate_times_hours_per_person():
    """Dimensional check the paper states explicitly (Sec. 3.5): N_k * r_k
    * h_k = people * period^-1 * hours/person = hours/period.
    """
    N_k, r_k, h_k = 24.0, 0.12, 600.0
    hours_per_period = N_k * r_k * h_k
    assert hours_per_period == pytest.approx(1728.0)


@pytest.mark.parametrize("bad_field,kwargs", [
    ("N_k", dict(N_k=-1, r_k=0.1, h_k=100, eta_k=1.0, B_k_min=0)),
    ("r_k", dict(N_k=10, r_k=1.5, h_k=100, eta_k=1.0, B_k_min=0)),
    ("h_k", dict(N_k=10, r_k=0.1, h_k=0, eta_k=1.0, B_k_min=0)),
    ("eta_k", dict(N_k=10, r_k=0.1, h_k=100, eta_k=0, B_k_min=0)),
    ("B_k_min", dict(N_k=10, r_k=0.1, h_k=100, eta_k=1.0, B_k_min=-1)),
])
def test_hcpb_parameters_validate(bad_field, kwargs):
    with pytest.raises(ValueError):
        HCPBParameters(**kwargs)


def test_shortfall_and_satisfied_are_consistent():
    assert hcpb_satisfied(delivered_hours=100, budget_hours=100)
    assert hcpb_shortfall(delivered_hours=100, budget_hours=100) == 0
    assert not hcpb_satisfied(delivered_hours=90, budget_hours=100)
    assert hcpb_shortfall(delivered_hours=90, budget_hours=100) == pytest.approx(10)
    assert hcpb_shortfall(delivered_hours=150, budget_hours=100) == 0  # never negative
