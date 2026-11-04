"""Revision options (R1): off by default, and each moves only what it should."""

from __future__ import annotations

import json
import math
from dataclasses import replace

import pytest

from sim.protocol.config import EXPLORATORY_POLICY_FLAGS, POLICY_FLAGS, RunConfig, SimParams, WorldModel, policy_flags
from sim.protocol.engine import run_one
from sim.protocol.estimation import cauchit_link, cloglog_link, sigmoid
from sim.protocol.skill import current_proficiency, current_proficiency_power

SHORT = replace(SimParams(), days=40)
SEED = 1000  # development seed, never a reporting seed


def _strip(record: dict) -> str:
    return json.dumps({k: v for k, v in record.items() if k != "rev_counters"})


def test_revision_counters_do_not_move_the_run():
    for policy in ("civicworkos", "efficiency", "static"):
        plain = run_one(SEED, "disruption", policy, RunConfig(params=SHORT))
        counted = run_one(SEED, "disruption", policy, RunConfig(params=SHORT), revision=True)
        assert _strip(counted) == json.dumps(plain)


def test_default_world_model_records_nothing_new():
    assert "world" not in RunConfig().as_dict()
    assert "world" in RunConfig(world=WorldModel(link="cauchit")).as_dict()


def test_reference_policy_flags_are_unchanged():
    assert set(POLICY_FLAGS) == {"static", "efficiency", "civicworkos", "civicworkos_nolearn",
                                 "civicworkos_noretention", "civicworkos_outcomeonly"}
    assert policy_flags("eqr_ceiling").workload_guard and not policy_flags("efficiency_quota_recency").workload_guard
    assert not EXPLORATORY_POLICY_FLAGS["cw_nogate"].oversight


@pytest.mark.parametrize("link", [cloglog_link, cauchit_link])
def test_links_are_centered_like_the_logistic(link):
    assert link(0.0) == pytest.approx(0.5)
    slope = (link(1e-5) - link(-1e-5)) / 2e-5
    assert slope == pytest.approx(0.25, rel=1e-4)
    assert 0.0 <= link(-50.0) <= link(50.0) <= 1.0
    assert sigmoid(0.0) == pytest.approx(0.5)


def test_power_forgetting_equals_exponential_at_tau():
    a = current_proficiency(0.85, 120.0, 120.0, 0.45)
    b = current_proficiency_power(0.85, 120.0, 120.0, 0.45)
    assert a == pytest.approx(b)
    assert current_proficiency_power(0.85, 480.0, 120.0, 0.45) > current_proficiency(0.85, 480.0, 120.0, 0.45)


def test_strict_restoration_truth_only_lowers_true_proficiency_not_the_log():
    cfg = RunConfig(params=replace(SimParams(), days=120), world=WorldModel(led_threshold_true=1.0))
    strict = run_one(SEED, "routine", "civicworkos", cfg)
    base = run_one(SEED, "routine", "civicworkos", RunConfig(params=replace(SimParams(), days=120)))
    assert strict["mean_proficiency_end"] < base["mean_proficiency_end"]


def test_momentary_load_changes_workload_and_has_its_own_stream():
    cfg = RunConfig(params=SHORT, world=WorldModel(load_ar_sd=0.3))
    moved = run_one(SEED, "routine", "efficiency", cfg)
    base = run_one(SEED, "routine", "efficiency", RunConfig(params=SHORT))
    assert moved["mean_workload"] != base["mean_workload"]
    assert moved["arrived"] == base["arrived"]   # the exogenous streams are untouched


def test_fault_injection_counts_every_domain_twice_a_day():
    r = run_one(SEED, "routine", "civicworkos", RunConfig(params=SHORT), revision=True)["rev_counters"]
    assert r["fi_start_n"] == [40.0, 40.0, 40.0]
    assert r["fi_end_n"] == [40.0, 40.0, 40.0]
    for k in range(3):
        assert r["fi_end_stop"][k] + r["fi_end_attempted"][k] == 40.0
        assert 0.0 <= r["fi_end_recovered_p"][k] <= r["fi_end_attempted"][k]
    assert r["max_planned_hours_over_cap"] <= 1e-9   # the admission test holds for planned hours
    assert math.isfinite(r["min_machine_hours_left"]) and r["min_machine_hours_left"] >= -1e-9
