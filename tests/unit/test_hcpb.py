"""Unit tests for civicworkos.constraints.hcpb: eq:phi, eq:hcpb and eq:hcpb-estimator."""

from __future__ import annotations

import pytest

from civicworkos.constraints.hcpb import (
    HCPBParameters,
    capability_budget,
    hcpb_satisfied,
    hcpb_shortfall,
    phi_for_mode,
)
from manuscript_values import WORKED


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
    """eq:bkworked at the worked example's inputs: the attrition estimate
    dominates the floor, giving B_k = 1.2 * 24 * 0.12 * 1440 = 4,976.64 hours.

    h_k is 1,440 *qualified-practice* hours, not the 1,800 supervised clock
    hours certification requires: eq:hconv converts between them through the
    task's learning value. Using the clock figure, or an earlier draft's 600,
    changes every number downstream of the budget.
    """
    w = WORKED
    params = HCPBParameters(
        N_k=w["N_k"], r_k=w["r_k"], h_k=w["h_k"], eta_k=w["eta_k"], B_k_min=w["B_min"]
    )
    assert capability_budget(params) == pytest.approx(4976.64)
    assert params.h_k == pytest.approx(w["learn"] * w["h_raw_k"])


def test_units_close_people_times_rate_times_hours_per_person():
    """Dimensional check the paper states explicitly (sec:hcpb): N_k * r_k
    * h_k = people * period^-1 * hours/person = hours/period.
    """
    w = WORKED
    N_k, r_k, h_k = w["N_k"], w["r_k"], w["h_k"]
    hours_per_period = N_k * r_k * h_k
    assert hours_per_period == pytest.approx(4147.2)


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
