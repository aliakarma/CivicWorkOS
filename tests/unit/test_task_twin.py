"""Unit tests for civicworkos.twin.task: Eq. 3-4."""

from __future__ import annotations

import pytest

from civicworkos.twin.task import TaskProfile, developmental_content


def test_ell_matches_worked_example():
    """Paper Sec. 5.3: learn=0.80, d_i=10h -> ell_i = 8 qualified-practice hours."""
    assert developmental_content(0.80, 10.0) == pytest.approx(8.0)


def test_task_profile_computes_ell_property():
    task = TaskProfile(
        task_id="t1", service="s", domain="d",
        cog=0.8, phy=0.6, emp=0.1, risk=0.7, auth=0.9, priv=0.2, urg=0.4, learn=0.8, crit=0.9,
        duration_hours=10.0,
    )
    assert task.ell == pytest.approx(8.0)


def test_demand_vector_has_nine_dimensions():
    task = TaskProfile(
        task_id="t1", service="s", domain="d",
        cog=0.1, phy=0.2, emp=0.3, risk=0.4, auth=0.5, priv=0.6, urg=0.7, learn=0.8, crit=0.9,
        duration_hours=5.0,
    )
    assert len(task.demand_vector) == 9
    assert task.demand_vector["learn"] == pytest.approx(0.8)


@pytest.mark.parametrize("field", ["cog", "phy", "emp", "risk", "auth", "priv", "urg", "learn", "crit"])
def test_out_of_range_demand_dimension_rejected(field):
    kwargs = dict(
        task_id="t1", service="s", domain="d",
        cog=0.1, phy=0.1, emp=0.1, risk=0.1, auth=0.1, priv=0.1, urg=0.1, learn=0.1, crit=0.1,
        duration_hours=5.0,
    )
    kwargs[field] = 1.5
    with pytest.raises(ValueError, match=r"\[0, 1\]"):
        TaskProfile(**kwargs)


def test_zero_duration_rejected():
    with pytest.raises(ValueError, match="positive"):
        TaskProfile(
            task_id="t1", service="s", domain="d",
            cog=0.1, phy=0.1, emp=0.1, risk=0.1, auth=0.1, priv=0.1, urg=0.1, learn=0.1, crit=0.1,
            duration_hours=0.0,
        )


def test_linearity_in_duration_is_a_named_modelling_assumption():
    """Report Sec. 8.2 [CRIT]: the multiplicative form makes a 10h task at
    learn=0.8 and a 20h task at learn=0.4 identical developmental goods.
    This test documents that this is what the equation actually does, not
    an endorsement that it should."""
    assert developmental_content(0.8, 10.0) == developmental_content(0.4, 20.0)
