"""Integration tests for the reference execution of the evaluation protocol.

Runs a shortened horizon so the suite stays fast. These tests check the
properties the protocol's validity rests on -- determinism, common random
numbers across policies, and the qualitative behavior of each mechanism --
not the reported numbers, which ``Paper/Frontiers/audit_numbers.py`` checks.
"""

from __future__ import annotations

import math
from dataclasses import replace

import pytest

from sim.protocol.config import POLICIES, SCENARIOS, RunConfig, SimParams
from sim.protocol.engine import Run, make_world, run_one

SHORT = RunConfig(params=replace(SimParams(), days=200))


@pytest.fixture(scope="module")
def routine_runs():
    return {p: run_one(1000, "routine", p, SHORT) for p in POLICIES}


def test_run_is_deterministic_for_a_seed():
    a = run_one(1001, "routine", "civicworkos", SHORT)
    b = run_one(1001, "routine", "civicworkos", SHORT)
    assert a.pop("trajectory") == b.pop("trajectory")
    assert a.keys() == b.keys()
    for k in a:
        x, y = a[k], b[k]
        if isinstance(x, float) and math.isnan(x):
            assert isinstance(y, float) and math.isnan(y), k
        else:
            assert x == y, k


def test_policies_share_the_exogenous_task_stream(routine_runs):
    arrived = {r["arrived"] for r in routine_runs.values()}
    assert len(arrived) == 1


def test_world_is_identical_across_policy_runs():
    w = make_world(1002, SCENARIOS["routine"], SHORT)
    r1, r2 = Run(w, "static", SHORT), Run(w, "civicworkos", SHORT)
    assert [p.tau for p in r1.pract[0]] == [p.tau for p in r2.pract[0]]


def test_efficiency_forms_no_one_and_civicworkos_delivers_trainee_practice(routine_runs):
    assert routine_runs["efficiency"]["trainee_credit_per_year"] == 0.0
    assert routine_runs["civicworkos"]["trainee_credit_per_year"] > 0.0


def test_retention_mechanism_keeps_more_practitioners_current(routine_runs):
    assert routine_runs["civicworkos"]["current_end"] > routine_runs["civicworkos_noretention"]["current_end"]
    assert routine_runs["civicworkos"]["current_end"] > routine_runs["efficiency"]["current_end"]


def test_learned_workload_ceiling_limits_overload(routine_runs):
    assert routine_runs["civicworkos"]["overload_share"] <= routine_runs["civicworkos_nolearn"]["overload_share"]


def test_disruption_is_silent_and_raises_faults_for_non_learning_policies():
    short_disruption = RunConfig(params=replace(SimParams(), days=540))
    static = run_one(1003, "disruption", "static", short_disruption)
    learner = run_one(1003, "disruption", "civicworkos", short_disruption)
    assert static["takeover_requests_window"] > learner["takeover_requests_window"]
    assert 0.0 <= learner["takeover_success_window"] <= 1.0


def test_metrics_are_well_formed(routine_runs):
    for r in routine_runs.values():
        assert 0.0 <= r["completion_rate"] <= 1.0
        assert 0.0 <= r["overload_share"] <= 1.0
        assert r["cost_per_completed"] > 0.0
        assert r["current_end"] <= r["certified_end"]
