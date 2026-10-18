"""Tests for the exploratory additions of submission phase P4.

Covers the rule-based baselines, the separate sensor-bias streams, the
read-only stop and incident counters, and exact reproduction of a stored
reporting run. See configs/protocol/exploratory_p4.yaml.
"""

from __future__ import annotations

import json
import math
from dataclasses import fields, replace
from pathlib import Path

import numpy as np
import pytest

from sim.protocol.config import (
    EXPLORATORY_POLICY_FLAGS,
    POLICIES,
    POLICY_FLAGS,
    SCENARIOS,
    TRAINEE_QUOTA,
    PolicyFlags,
    RunConfig,
    SensorRealism,
    SimParams,
    policy_flags,
)
from sim.protocol.engine import STOP_CAUSES, Run, make_world, run_one

SHORT = RunConfig(params=replace(SimParams(), days=120))
REFERENCE = Path(__file__).resolve().parent.parent / "data" / "reference_run_seed0_routine_civicworkos.json"


def _same(a, b) -> bool:
    if isinstance(a, float) and math.isnan(a):
        return isinstance(b, float) and math.isnan(b)
    return a == b


# ---- registries and flags -------------------------------------------------

def test_reference_registry_is_unchanged():
    assert POLICIES == ("static", "efficiency", "civicworkos", "civicworkos_nolearn", "civicworkos_noretention")
    assert not set(EXPLORATORY_POLICY_FLAGS) & set(POLICY_FLAGS)
    assert [f.name for f in fields(PolicyFlags)] == ["learning", "capability_terms", "retention", "workload_guard",
                                                     "oversight", "readiness_takeover", "multimodal"]


def test_baseline_flags():
    eff = POLICY_FLAGS["efficiency"]
    assert policy_flags("efficiency_quota") == eff
    recency = PolicyFlags(learning=True, capability_terms=False, retention=True, workload_guard=False,
                          oversight=False, readiness_takeover=False)
    assert policy_flags("efficiency_recency") == recency
    assert policy_flags("efficiency_quota_recency") == recency
    assert TRAINEE_QUOTA == {"efficiency_quota", "efficiency_quota_recency"}
    with pytest.raises(KeyError):
        policy_flags("no_such_policy")


# ---- apprenticeship quota -------------------------------------------------

def _first_inspection_task(world):
    return next(i for i, (d, k) in enumerate(zip(world.task_day, world.task_dom)) if d == 0 and k == 0)


def test_quota_attaches_the_free_trainee_to_the_efficiency_pick():
    world = make_world(5, SCENARIOS["routine"], SHORT)
    ti = _first_inspection_task(world)
    eff, quota = Run(world, "efficiency", SHORT), Run(world, "efficiency_quota", SHORT)
    for r in (eff, quota):
        r.mach_left = [spec.machine_units * r.P.machine_h_per_unit for spec in r.D]
    pe, pq = eff.choose(0, ti, 0), quota.choose(0, ti, 0)
    assert pe is not None and pe["lead"] is not None and pe["tr"] is None   # inspection is always human-involved
    assert pq["mode"].name == pe["mode"].name and pq["lead"].slot == pe["lead"].slot
    assert pq["tr"] is not None and not quota.certified(0, pq["tr"])
    free = [p for p in quota.pract[0] if p.active and not quota.certified(0, p)]
    assert pq["tr"].slot == min(free, key=lambda p: (p.hours, p.slot)).slot
    assert quota.C["quota_switches"] == 1 and quota.C["quota_human_picks"] == 1


def test_quota_policies_form_practitioners_and_efficiency_does_not():
    rows = {p: run_one(7, "routine", p, SHORT, counters=True) for p in ("efficiency", *EXPLORATORY_POLICY_FLAGS)}
    assert rows["efficiency"]["trainee_credit_per_year"] == 0.0
    for p in TRAINEE_QUOTA:
        c = rows[p]["p4_counters"]
        assert rows[p]["trainee_credit_per_year"] > 0.0
        assert c["quota_switches"] > 0
        assert c["quota_human_picks"] == c["quota_switches"] + c["quota_already_paired"] + c["quota_unavailable"]
    assert rows["efficiency_recency"]["p4_counters"]["quota_human_picks"] == 0
    assert rows["efficiency_recency"]["retention_reservations"] > 0


# ---- sensor-bias streams --------------------------------------------------

def test_zero_bias_draws_nothing_and_leaves_the_world_unchanged():
    w0 = make_world(11, SCENARIOS["routine"], SHORT)
    assert w0.sensor_bias is None and w0.probe_bias is None
    biased = replace(SHORT, sensors=SensorRealism(workload_sensor_bias_sd=0.1, probe_bias_sd=0.05))
    w1 = make_world(11, SCENARIOS["routine"], biased)
    for name in ("task_day", "task_dom", "task_req", "task_cons", "task_u", "task_z", "machine_rel",
                 "telemetry_ok", "telemetry_z", "sensor_u", "sensor_z"):
        assert np.array_equal(getattr(w0, name), getattr(w1, name)), name
    assert w0.pool == w1.pool


def test_bias_streams_are_separate_and_documented():
    cfg = replace(SHORT, sensors=SensorRealism(workload_sensor_bias_sd=0.1, probe_bias_sd=0.05))
    w = make_world(11, SCENARIOS["routine"], cfg)
    ref_w = 0.1 * np.random.default_rng([11, 7919, 1]).standard_normal(w.sensor_bias.shape)
    ref_p = 0.05 * np.random.default_rng([11, 7919, 2]).standard_normal(w.probe_bias.shape)
    assert np.array_equal(w.sensor_bias, ref_w) and np.array_equal(w.probe_bias, ref_p)
    only_w = make_world(11, SCENARIOS["routine"], replace(SHORT, sensors=SensorRealism(workload_sensor_bias_sd=0.1)))
    assert only_w.probe_bias is None and np.array_equal(only_w.sensor_bias, w.sensor_bias)


def test_explicit_zero_bias_run_equals_default_run():
    a = run_one(12, "routine", "civicworkos", SHORT)
    b = run_one(12, "routine", "civicworkos", replace(SHORT, sensors=SensorRealism(0.0, 0.0)))
    assert a.keys() == b.keys() and all(_same(a[k], b[k]) for k in a)


def test_workload_bias_changes_only_the_learned_policies_that_read_it():
    biased = replace(SHORT, sensors=SensorRealism(workload_sensor_bias_sd=0.15))
    for policy in ("efficiency", "civicworkos_nolearn"):   # no workload guard / no learning: channel unused
        a, b = run_one(13, "routine", policy, SHORT), run_one(13, "routine", policy, biased)
        assert all(_same(a[k], b[k]) for k in a), policy
    a = run_one(13, "routine", "civicworkos", SHORT, counters=True)
    b = run_one(13, "routine", "civicworkos", biased, counters=True)
    assert b["p4_counters"]["load_mae_end"] > a["p4_counters"]["load_mae_end"]


# ---- read-only counters ---------------------------------------------------

@pytest.fixture(scope="module")
def disruption_runs():
    cfg = RunConfig(params=replace(SimParams(), days=540))
    return {p: (run_one(14, "disruption", p, cfg), run_one(14, "disruption", p, cfg, counters=True))
            for p in ("civicworkos", "static")}


def test_counters_do_not_change_the_record(disruption_runs):
    for plain, counted in disruption_runs.values():
        c = dict(counted)
        c.pop("p4_counters")
        assert plain.keys() == c.keys() and all(_same(plain[k], c[k]) for k in plain)


def test_stop_causes_account_for_every_stop(disruption_runs):
    for policy, (_, counted) in disruption_runs.items():
        c = counted["p4_counters"]
        for sfx in ("", "_w"):
            assert c["mrc" + sfx] == sum(c[k + sfx] for k in ("no_certified", "seq_competence", "seq_workload",
                                                              "seq_time"))
            empty = c["mrc" + sfx] - c["no_certified" + sfx]
            binds = sum(c[k + sfx] for k in ("bind_competence", "bind_workload", "bind_time", "bind_none"))
            assert empty <= binds <= 3 * empty    # overlapping indicators, at least one per empty-set stop
            assert c["bind_none" + sfx] <= empty and c["ootl" + sfx] <= empty
        assert all(c[k + "_w"] <= c[k] for k in ("mrc", *STOP_CAUSES))
        assert c["mrc"] == counted["mrc"]
        assert c["completed_clean"] <= c["completed"] and c["completed_w_clean"] <= c["completed_w"]
    assert disruption_runs["civicworkos"][1]["p4_counters"]["mrc"] > 0
    static = disruption_runs["static"][1]["p4_counters"]
    assert static["mrc"] == static["no_certified"]   # Static stops only when nobody is certified


# ---- exact reproduction of the reference execution -----------------------

def test_a_stored_reporting_run_reproduces_byte_for_byte():
    stored = REFERENCE.read_text(encoding="utf-8").strip()
    r = run_one(0, "routine", "civicworkos")
    r.pop("trajectory")
    assert json.dumps(r) == stored
