"""Unit tests for civicworkos.constraints.resilience: Eq. 13-14, and the
invented task-granularity Delta^res_s(m) attribution."""

from __future__ import annotations

import pytest

from civicworkos.constraints.resilience import (
    ReserveState,
    reserve_satisfied,
    resilience_reserve,
    task_delta_resilience,
)


def _state(n_s=1, kappa_s=0.6, peak_demand=50.0):
    return ReserveState(
        component_capacities={"ai_pool": 40.0, "drone_fleet": 25.0, "vendor_platform": 15.0},
        n_s=n_s,
        kappa_s=kappa_s,
        peak_demand=peak_demand,
    )


def test_reserve_removes_the_n_largest_components():
    state = _state(n_s=1)
    # Largest component is ai_pool (40); removing it leaves 25+15=40.
    assert state.largest_n_components == ["ai_pool"]
    assert resilience_reserve(state) == pytest.approx(40.0)


def test_reserve_removes_two_largest_for_n2():
    state = _state(n_s=2)
    # Two largest: ai_pool (40), drone_fleet (25); leaves vendor_platform (15).
    assert set(state.largest_n_components) == {"ai_pool", "drone_fleet"}
    assert resilience_reserve(state) == pytest.approx(15.0)


def test_rho_s_is_kappa_times_peak_demand():
    state = _state(kappa_s=0.6, peak_demand=50.0)
    assert state.rho_s == pytest.approx(30.0)


def test_reserve_satisfied_boundary():
    state = _state(n_s=1, kappa_s=0.6, peak_demand=50.0)  # reserve=40, rho=30
    assert reserve_satisfied(state)
    tight_state = _state(n_s=1, kappa_s=0.9, peak_demand=50.0)  # rho=45 > 40
    assert not reserve_satisfied(tight_state)


def test_n_s_must_be_one_or_two():
    with pytest.raises(ValueError, match="n_s must be 1 or 2"):
        ReserveState(component_capacities={"only_one": 10.0}, n_s=3, kappa_s=0.5, peak_demand=10.0)  # type: ignore[arg-type]


def test_n_s_cannot_exceed_component_count():
    with pytest.raises(ValueError, match="N-2 contingency"):
        ReserveState(component_capacities={"only_one": 10.0}, n_s=2, kappa_s=0.5, peak_demand=10.0)


@pytest.mark.parametrize("mode,expected_sign", [("H", 1), ("A", -1), ("R", -1), ("A+R", -1)])
def test_delta_resilience_sign_by_automation_dependence(mode, expected_sign):
    """[INVENTED] A human-only mode should INCREASE reserve (free automated
    capacity); a fully automated mode should DECREASE it -- the documented
    engineering choice in task_delta_resilience()."""
    delta = task_delta_resilience(mode, task_duration_hours=8.0, component_capacity_baseline=80.0)
    assert (delta > 0) == (expected_sign > 0)
    assert (delta < 0) == (expected_sign < 0)


def test_delta_resilience_hybrid_is_between_pure_modes():
    d_h = task_delta_resilience("H", 8.0, 80.0)
    d_hr = task_delta_resilience("H+R", 8.0, 80.0)
    d_r = task_delta_resilience("R", 8.0, 80.0)
    assert d_r < d_hr < d_h


def test_delta_resilience_validates_inputs():
    with pytest.raises(ValueError):
        task_delta_resilience("H", 0.0, 80.0)
    with pytest.raises(ValueError):
        task_delta_resilience("H", 8.0, 0.0)
    with pytest.raises(ValueError):
        task_delta_resilience("unknown_mode", 8.0, 80.0)
