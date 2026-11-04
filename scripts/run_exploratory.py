"""Exploratory analyses added in revision (NOT part of the pre-specified family).

    python scripts/run_exploratory.py                     # every block below
    python scripts/run_exploratory.py --blocks baselines  # selected blocks only

Results go to ``reproducibility/data/exploratory.json``; per-run records go to
``results/exploratory/``. Blocks that are not run keep their stored content
byte for byte, so a subset run never rewrites another block.

Original revision blocks (unchanged jobs and computations):

1. ``outcome_only``: CivicWorkOS learning from task outcomes only (skill
   probes, fleet telemetry and physiological workload readings removed), all
   three scenarios, paired with the stored reporting runs of CivicWorkOS.
2. ``sensitivity``: the CivicWorkOS-versus-efficiency contrast under the
   retention time constant (tau_ret x0.5 and x2) and machine prices (x3),
   routine operations.

Blocks added after internal pre-specification (submission phase P4), defined in
``configs/protocol/exploratory_p4.yaml`` before any of them was run:

3. ``baselines``: Efficiency + apprenticeship quota, + recency rule, and both.
4. ``sensor_realism``: per-person bias, noise and availability of the
   physiological channel, and a combined setting degrading every channel.
5. ``takeover_sweep``: out-of-loop factor, situation-awareness time and the
   inspection time budget, with read-only stop-cause counters.
6. ``model_sensitivity``: hybrid phi_m, the outcome-model slope gamma, and the
   fault rate.
7. ``derived``: cost per current practitioner and incident-free window
   completion, from per-run records.

All use the reporting seeds 0-29 so that comparisons are paired; none enters
the Holm family of configs/protocol/hypotheses.yaml, and the article labels
every result from this script as exploratory. P4 blocks also rerun the
reference configuration with the read-only counters switched on (the counter
replay) and check that every original field equals the stored record.
"""

from __future__ import annotations

import argparse
import hashlib
import json
import sys
import time
from concurrent.futures import ProcessPoolExecutor
from dataclasses import replace
from pathlib import Path
from typing import Any

import numpy as np

ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT))

from sim.protocol.analysis import mean_ci, rank_biserial, wilcoxon_p  # noqa: E402
from sim.protocol.config import DOMAINS, POLICIES, RunConfig, SensorRealism, SimParams  # noqa: E402
from sim.protocol.engine import run_one  # noqa: E402

SEEDS = range(0, 30)
METRICS = ["completion_rate", "completion_rate_window", "cost_per_completed", "overload_share",
           "current_end", "current_share_end", "certified_end", "takeover_success_window",
           "incidents_per_1000_window", "proficiency_mae_end", "machine_mae", "machine_mae_window"]
P4_METRICS = METRICS + ["graduations", "trainee_credit_per_year", "takeover_success_rate", "takeover_requests_window",
                        "incidents_per_1000", "mrc", "mean_workload"]
SCENARIOS3 = ("routine", "surge", "disruption")
LEGACY = ("outcome_only", "sensitivity")
P4_BLOCKS = ("baselines", "sensor_realism", "takeover_sweep", "model_sensitivity", "derived")
LABEL = "added after internal pre-specification; exploratory (configs/protocol/exploratory_p4.yaml)"
# SHA-256 of the 450 frozen reporting runs (P0 baseline). Pairing uses only these records.
REFERENCE_RUNS_SHA256 = "45101231c93211204ccbaf64ba5b21d210e7168cfb3944340ee3d03cfd2e57ec"
CODE_FILES = ("sim/protocol/engine.py", "sim/protocol/config.py", "sim/protocol/estimation.py", "sim/protocol/skill.py")

BASELINES = ("efficiency_quota", "efficiency_recency", "efficiency_quota_recency")
SENSOR_SETTINGS: dict[str, tuple[dict[str, Any], dict[str, float]]] = {
    "bias_0.05": ({}, {"workload_sensor_bias_sd": 0.05}),
    "bias_0.10": ({}, {"workload_sensor_bias_sd": 0.10}),
    "bias_0.15": ({}, {"workload_sensor_bias_sd": 0.15}),
    "noise_0.20": ({"workload_sensor_sd": 0.20}, {}),
    "noise_0.30": ({"workload_sensor_sd": 0.30}, {}),
    "avail_0.35": ({"workload_sensor_prob": 0.35}, {}),
    "combined": ({"workload_sensor_sd": 0.20, "workload_sensor_prob": 0.35, "probe_sd": 0.16, "probe_prob": 0.15,
                  "telemetry_sd": 0.20, "telemetry_prob": 0.25},
                 {"workload_sensor_bias_sd": 0.10, "probe_bias_sd": 0.05}),
}
SENSOR_AXES = {"bias": ("bias_0.05", "bias_0.10", "bias_0.15"), "noise": ("noise_0.20", "noise_0.30"),
               "availability": ("avail_0.35",), "combined": ("combined",)}
TAKEOVER_SETTINGS: dict[str, dict[str, Any]] = {"ootl_0.3": {"ootl_factor": 0.3}, "ootl_1.0": {"ootl_factor": 1.0},
                     "t_sa_6": {"t_sa": 6.0}, "t_sa_10": {"t_sa": 10.0}, "ins_budget_20": {}}
MODEL_SETTINGS: dict[str, Any] = {"phi_hybrid_minus_0.10": -0.10, "phi_hybrid_plus_0.10": 0.10,
                  "gamma_6": {"gamma": 6.0}, "gamma_10": {"gamma": 10.0},
                  "fault_0.01": {"fault_rate": 0.01}, "fault_0.04": {"fault_rate": 0.04}}
STOP_KEYS = ("mrc", "no_certified", "seq_competence", "seq_workload", "seq_time",
             "bind_competence", "bind_workload", "bind_time", "bind_none", "ootl")


def _shift_hybrids(delta: float):
    """Every hybrid mode (0 < phi_m < 1) shifted by delta; pure modes unchanged."""
    return tuple(replace(d, modes=tuple(replace(m, phi=round(m.phi + delta, 10)) if 0.0 < m.phi < 1.0 else m
                                        for m in d.modes)) for d in DOMAINS)


def config(variant: str) -> RunConfig:
    if variant == "base":
        return RunConfig()
    if variant == "tau_half":
        return RunConfig(params=replace(SimParams(), tau_ret=60.0))
    if variant == "tau_double":
        return RunConfig(params=replace(SimParams(), tau_ret=240.0))
    if variant == "machine_price_x3":
        return RunConfig(domains=tuple(replace(d, machine_cost_per_h=3 * d.machine_cost_per_h) for d in DOMAINS))
    if variant in SENSOR_SETTINGS:
        params, sensors = SENSOR_SETTINGS[variant]
        return RunConfig(params=replace(SimParams(), **params), sensors=SensorRealism(**sensors))
    if variant == "ins_budget_20":
        return RunConfig(domains=tuple(replace(d, takeover_budget_min=20.0) if d.key == "INS" else d
                                       for d in DOMAINS))
    if variant in TAKEOVER_SETTINGS:
        return RunConfig(params=replace(SimParams(), **TAKEOVER_SETTINGS[variant]))
    if variant.startswith("phi_hybrid"):
        return RunConfig(domains=_shift_hybrids(MODEL_SETTINGS[variant]))
    if variant in MODEL_SETTINGS:
        return RunConfig(params=replace(SimParams(), **MODEL_SETTINGS[variant]))
    raise ValueError(variant)


def _job(args):
    seed, scenario, policy, variant = args
    r = run_one(seed, scenario, policy, config(variant))
    r.pop("trajectory")
    r["variant"] = variant
    return r


def _job_p4(args):
    seed, scenario, policy, variant = args
    r = run_one(seed, scenario, policy, config(variant), counters=True)
    r.pop("trajectory")
    r["variant"] = variant
    return r


def _sha(data: bytes) -> str:
    return hashlib.sha256(data).hexdigest()


def code_sha() -> str:
    return _sha(b"".join((ROOT / f).read_bytes() for f in CODE_FILES))


def config_sha(variant: str) -> str:
    return _sha(json.dumps(config(variant).as_dict(), sort_keys=True).encode())


def load_stored() -> dict:
    path = ROOT / "results" / "protocol" / "runs.jsonl"
    if _sha(path.read_bytes()) != REFERENCE_RUNS_SHA256:
        raise SystemExit(f"{path} does not match the frozen reporting runs; regenerate with `make protocol`")
    stored = {}
    for line in open(path, encoding="utf-8"):
        r = json.loads(line)
        stored[(r["seed"], r["scenario"], r["policy"], "base")] = r
        STORED_LINES[(r["seed"], r["scenario"], r["policy"])] = line.rstrip("\n")
    return stored


STORED_LINES: dict = {}   # the frozen run records exactly as written


def run_p4(name: str, jobs: list, out: Path, workers: int | None, log: dict) -> list[dict]:
    """Run (or reuse after validation) one set of counter-carrying P4 jobs."""
    path = out / name / "runs.jsonl"
    want = {(s, sc, p, v): config_sha(v) for s, sc, p, v in jobs}
    code = code_sha()
    if path.exists():
        rows = [json.loads(line) for line in open(path, encoding="utf-8")]
        have = {(r["seed"], r["scenario"], r["policy"], r["variant"]): r for r in rows}
        if (set(have) == set(want) and all(r["config_sha"] == want[k] and r["code_sha"] == code
                                           for k, r in have.items())):
            log[name] = {"runs": len(rows), "reused": True, "path": str(path.relative_to(ROOT))}
            print(f"{name}: reused {len(rows)} validated runs", flush=True)
            return rows
    t0 = time.time()
    with ProcessPoolExecutor(max_workers=workers) as ex:
        rows = list(ex.map(_job_p4, jobs, chunksize=1))
    for r in rows:
        r["config_sha"] = want[(r["seed"], r["scenario"], r["policy"], r["variant"])]
        r["code_sha"] = code
    path.parent.mkdir(parents=True, exist_ok=True)
    with open(path, "w", encoding="utf-8") as f:
        for r in rows:
            f.write(json.dumps(r) + "\n")
    log[name] = {"runs": len(rows), "reused": False, "wall_seconds": round(time.time() - t0, 1),
                 "path": str(path.relative_to(ROOT))}
    print(f"{name}: {len(rows)} runs in {time.time() - t0:.0f} s", flush=True)
    return rows


# ---------------------------------------------------------------------------
# statistics
# ---------------------------------------------------------------------------

def _nan(v) -> bool:
    return isinstance(v, float) and v != v


def paired_values(a: dict, b: dict, fa, fb=None):
    """Paired per-seed values of fa(record) over seeds where both are defined."""
    fb = fb or fa
    xa, xb = [], []
    for s in SEEDS:
        x, y = fa(a[s]), fb(b[s])
        if x is None or y is None or _nan(x) or _nan(y):
            continue
        xa.append(x)
        xb.append(y)
    return xa, xb


def summarize_diff(xa: list, xb: list) -> dict:
    d = np.array(xa, dtype=float) - np.array(xb, dtype=float)
    m, lo, hi, n = mean_ci(list(d))
    return {"a_mean": float(np.mean(xa)) if xa else float("nan"), "b_mean": float(np.mean(xb)) if xb else float("nan"),
            "diff": m, "ci_low": lo, "ci_high": hi, "n": n, "p_unadjusted": wilcoxon_p(d), "effect_r": rank_biserial(d)}


def contrast_p4(a: dict, b: dict, metric: str) -> dict:
    return summarize_diff(*paired_values(a, b, lambda r: r[metric]))


def cost_index(a: dict, eff: dict) -> dict:
    vals = [100 * a[s]["cost_per_completed"] / eff[s]["cost_per_completed"] for s in SEEDS]
    return dict(zip(("mean", "ci_low", "ci_high", "n"), mean_ci(vals)))


def level(rows: dict, f) -> dict:
    return dict(zip(("mean", "ci_low", "ci_high", "n"), mean_ci([f(rows[s]) for s in SEEDS])))


def by_seed(rows: list[dict], scenario: str, policy: str, variant: str) -> dict:
    return {r["seed"]: r for r in rows if r["scenario"] == scenario and r["policy"] == policy
            and r["variant"] == variant}


def original_view(r: dict) -> str:
    """The record as the reference execution writes it (counter key and P4 tags removed)."""
    x = {k: v for k, v in r.items() if k not in ("p4_counters", "variant", "config_sha", "code_sha")}
    return json.dumps(x)


def check_identity(rows: list[dict], stored: dict) -> dict:
    """Exact comparison of every replayed record's original fields with the stored line's bytes."""
    mismatches = []
    for r in rows:
        if original_view(r) != STORED_LINES[(r["seed"], r["scenario"], r["policy"])]:
            mismatches.append([r["seed"], r["scenario"], r["policy"]])
    return {"records_compared": len(rows), "mismatches": mismatches, "identical": not mismatches}


def stop_block(recs: dict, window: bool) -> dict:
    sfx = "_w" if window else ""
    out: dict[str, Any] = {key: level(recs, lambda r, k=key: r["p4_counters"][k + sfx]) for key in STOP_KEYS}
    def n_empty(r):   # stops with an empty readiness set: the out-of-loop denominator
        return r["p4_counters"]["mrc" + sfx] - r["p4_counters"]["no_certified" + sfx]

    empty = sum(n_empty(r) for r in recs.values())
    ootl = sum(r["p4_counters"]["ootl" + sfx] for r in recs.values())
    per_seed = [r["p4_counters"]["ootl" + sfx] / n_empty(r) for r in recs.values() if n_empty(r) > 0]
    out["ootl_share_pooled"] = ootl / empty if empty else float("nan")
    out["ootl_share_per_seed"] = dict(zip(("mean", "ci_low", "ci_high", "n"), mean_ci(per_seed)))
    out["empty_readiness_stops_total"] = empty
    return out


# ---------------------------------------------------------------------------
# P4 blocks
# ---------------------------------------------------------------------------

def block_baselines(rows, replay, stored) -> dict:
    out: dict = {"label": LABEL, "learning": "on in every baseline (isolates the rule)", "scenarios": {}}
    for sc in SCENARIOS3:
        ref = {p: by_seed(replay, sc, p, "base") for p in POLICIES}
        res: dict = {"levels": {}, "civicworkos_minus": {}, "minus_efficiency": {}, "quota_counters": {}}
        for b in BASELINES:
            recs = by_seed(rows, sc, b, "base")
            res["levels"][b] = {m: level(recs, lambda r, m=m: r[m]) for m in P4_METRICS}
            res["levels"][b]["cost_index"] = cost_index(recs, ref["efficiency"])
            res["civicworkos_minus"][b] = {m: contrast_p4(ref["civicworkos"], recs, m) for m in P4_METRICS}
            res["civicworkos_minus"][b]["cost_index_points"] = summarize_diff(
                [100 * ref["civicworkos"][s]["cost_per_completed"] / ref["efficiency"][s]["cost_per_completed"]
                 for s in SEEDS],
                [100 * recs[s]["cost_per_completed"] / ref["efficiency"][s]["cost_per_completed"] for s in SEEDS])
            res["minus_efficiency"][b] = {m: contrast_p4(recs, ref["efficiency"], m) for m in P4_METRICS}
            res["quota_counters"][b] = {k: level(recs, lambda r, k=k: r["p4_counters"][k])
                                        for k in ("quota_human_picks", "quota_switches", "quota_already_paired",
                                                  "quota_unavailable")}
        res["levels"]["civicworkos"] = {m: level(ref["civicworkos"], lambda r, m=m: r[m]) for m in P4_METRICS}
        res["levels"]["efficiency"] = {m: level(ref["efficiency"], lambda r, m=m: r[m]) for m in P4_METRICS}
        res["levels"]["civicworkos"]["cost_index"] = cost_index(ref["civicworkos"], ref["efficiency"])
        out["scenarios"][sc] = res
    return out


def break_even(diffs: dict) -> dict:
    """Pre-specified rule: first setting on each axis whose 95% CI upper bound of d reaches 0."""
    res = {}
    for axis, settings in SENSOR_AXES.items():
        hit = next((s for s in settings if diffs[s]["ci_high"] >= 0.0), None)
        reversal = next((s for s in settings if diffs[s]["diff"] >= 0.0), None)
        res[axis] = {"settings_in_order": list(settings), "break_even": hit or "none within the grid",
                     "first_reversal": reversal or "none within the grid"}
    return res


def block_sensor(rows, replay, stored, invariance) -> dict:
    metrics = ["overload_share", "proficiency_mae_end", "current_end", "takeover_success_window",
               "completion_rate", "completion_rate_window", "mrc", "incidents_per_1000_window", "mean_workload"]
    out: dict = {"label": LABEL, "policy": "civicworkos", "settings": {k: {"params": v[0], "sensors": v[1]}
                                                                      for k, v in SENSOR_SETTINGS.items()},
                 "invariance": invariance, "scenarios": {}}
    for sc in ("routine", "disruption"):
        base = by_seed(replay, sc, "civicworkos", "base")
        nolearn = by_seed(replay, sc, "civicworkos_nolearn", "base")
        eff = by_seed(replay, sc, "efficiency", "base")
        res: dict = {"baseline": {m: level(base, lambda r, m=m: r[m]) for m in metrics},
                     "no_learning": {m: level(nolearn, lambda r, m=m: r[m]) for m in metrics},
                     "efficiency": {m: level(eff, lambda r, m=m: r[m]) for m in metrics},
                     "settings": {}}
        res["baseline"]["load_mae_end"] = level(base, lambda r: r["p4_counters"]["load_mae_end"])
        res["no_learning"]["load_mae_end"] = level(nolearn, lambda r: r["p4_counters"]["load_mae_end"])
        for v in SENSOR_SETTINGS:
            recs = by_seed(rows, sc, "civicworkos", v)
            eff_v = by_seed(rows, sc, "efficiency", v) if v == "combined" else eff
            entry = {"levels": {m: level(recs, lambda r, m=m: r[m]) for m in metrics},
                     "minus_no_learning": {m: contrast_p4(recs, nolearn, m) for m in metrics},
                     "minus_efficiency": {m: contrast_p4(recs, eff_v, m) for m in metrics},
                     "minus_baseline": {m: contrast_p4(recs, base, m) for m in metrics},
                     "efficiency_reference": "rerun at this setting" if v == "combined" else "stored (unaffected)"}
            entry["levels"]["load_mae_end"] = level(recs, lambda r: r["p4_counters"]["load_mae_end"])
            entry["minus_baseline"]["load_mae_end"] = summarize_diff(
                *paired_values(recs, base, lambda r: r["p4_counters"]["load_mae_end"]))
            res["settings"][v] = entry
        res["overload_break_even"] = break_even({v: res["settings"][v]["minus_no_learning"]["overload_share"]
                                                 for v in SENSOR_SETTINGS})
        out["scenarios"][sc] = res
    return out


def block_takeover(rows, replay) -> dict:
    metrics = ["takeover_success_window", "takeover_success_rate", "mrc", "incidents_per_1000_window",
               "completion_rate_window", "takeover_requests_window", "takeover_time_mean"]
    out: dict = {"label": LABEL, "scenario": "disruption",
                 "settings": {**{k: v for k, v in TAKEOVER_SETTINGS.items() if v},
                              "ins_budget_20": {"INS.takeover_budget_min": 20.0}},
                 "baseline_values": {"ootl_factor": 0.6, "t_sa_min": 8.0, "INS.takeover_budget_min": 15.0},
                 "routine_reference": {}, "disruption": {}}
    for p in ("civicworkos", "static"):
        recs = by_seed(replay, "routine", p, "base")
        out["routine_reference"][p] = {"stops_all_run": stop_block(recs, False)}
    for v in ("base", *TAKEOVER_SETTINGS):
        src = replay if v == "base" else rows
        cw = by_seed(src, "disruption", "civicworkos", v)
        st = by_seed(src, "disruption", "static", v)
        entry = {"civicworkos": {m: level(cw, lambda r, m=m: r[m]) for m in metrics},
                 "static": {m: level(st, lambda r, m=m: r[m]) for m in metrics},
                 "civicworkos_minus_static": {m: contrast_p4(cw, st, m) for m in metrics},
                 "civicworkos_stops_all_run": stop_block(cw, False),
                 "civicworkos_stops_window": stop_block(cw, True),
                 "static_stops_all_run": stop_block(st, False)}
        for m in ("mrc_w",):
            entry["civicworkos"][m] = level(cw, lambda r, m=m: r["p4_counters"][m])
            entry["static"][m] = level(st, lambda r, m=m: r["p4_counters"][m])
        if v != "base":
            cw0 = by_seed(replay, "disruption", "civicworkos", "base")
            st0 = by_seed(replay, "disruption", "static", "base")
            entry["civicworkos_minus_baseline"] = {m: contrast_p4(cw, cw0, m) for m in metrics}
            entry["static_minus_baseline"] = {m: contrast_p4(st, st0, m) for m in metrics}
        out["disruption"][v] = entry
    return out


def block_model(rows, replay) -> dict:
    metrics = ["current_share_end", "completion_rate", "overload_share", "current_end", "graduations",
               "takeover_success_rate", "incidents_per_1000", "cost_per_completed"]
    out: dict = {"label": LABEL, "scenario": "routine", "format": "CivicWorkOS minus Efficiency (Table 9B)",
                 "settings": {"phi_hybrid_minus_0.10": "hybrid phi_m - 0.10",
                              "phi_hybrid_plus_0.10": "hybrid phi_m + 0.10",
                              **{k: v for k, v in MODEL_SETTINGS.items() if isinstance(v, dict)}},
                 "variants": {}}
    for v in ("base", *MODEL_SETTINGS):
        src = replay if v == "base" else rows
        cw = by_seed(src, "routine", "civicworkos", v)
        ef = by_seed(src, "routine", "efficiency", v)
        block = {m: contrast_p4(cw, ef, m) for m in metrics}
        block["cost_index"] = cost_index(cw, ef)
        out["variants"][v] = block
    return out


def _bootstrap_ratio(dc: np.ndarray, dn: np.ndarray, reps: int = 10_000) -> tuple[float, float]:
    rng = np.random.default_rng([0, 7919, 101])
    idx = rng.integers(0, len(dc), size=(reps, len(dc)))
    num, den = dc[idx].mean(axis=1), dn[idx].mean(axis=1)
    ok = den != 0
    vals = num[ok] / den[ok]
    return float(np.percentile(vals, 2.5)), float(np.percentile(vals, 97.5))


def block_derived(baseline_rows, replay) -> dict:
    out: dict = {"label": LABEL, "cost_per_current": {}, "joint_safety_completion": {},
                 "definitions": "configs/protocol/exploratory_p4.yaml (derived)"}

    def total_cost(r):   # pre-specified reconstruction from the stored per-run fields
        return r["cost_per_completed"] * r["completion_rate"] * r["arrived"]

    recon_err = max(abs(total_cost(r) - r["p4_counters"]["total_cost"]) for r in replay + baseline_rows)
    out["cost_reconstruction_max_abs_error"] = recon_err
    comps = ("efficiency", "static", "civicworkos_nolearn", *BASELINES)
    for sc in SCENARIOS3:
        recs = {p: by_seed(replay, sc, p, "base") for p in POLICIES}
        recs.update({b: by_seed(baseline_rows, sc, b, "base") for b in BASELINES})

        def cpc(r):
            return None if r["current_end"] == 0 else total_cost(r) / r["current_end"]

        res: dict = {"units": "model cost units (1 = one certified practitioner-hour) per current practitioner at end",
                     "levels": {}, "civicworkos_minus": {}, "incremental": {}}
        for p, rr in recs.items():
            vals = [cpc(r) for r in rr.values()]
            res["levels"][p] = dict(zip(("mean", "ci_low", "ci_high", "n"),
                                        mean_ci([v for v in vals if v is not None])))
            res["levels"][p]["dropped_zero_current"] = sum(v is None for v in vals)
            res["levels"][p]["total_cost"] = level(rr, total_cost)
        for c in comps:
            res["civicworkos_minus"][c] = summarize_diff(*paired_values(recs["civicworkos"], recs[c], cpc))
            dc = np.array([total_cost(recs["civicworkos"][s]) - total_cost(recs[c][s]) for s in SEEDS])
            dn = np.array([recs["civicworkos"][s]["current_end"] - recs[c][s]["current_end"] for s in SEEDS], float)
            lo, hi = _bootstrap_ratio(dc, dn)
            res["incremental"][c] = {"mean_cost_diff": float(dc.mean()), "mean_current_diff": float(dn.mean()),
                                     "ratio_of_paired_means": float(dc.mean() / dn.mean()) if dn.mean() else None,
                                     "bootstrap_ci": [lo, hi],
                                     "note": "ratio of paired mean differences, percentile bootstrap over seeds"}
        out["cost_per_current"][sc] = res
    for sc in ("disruption", "surge"):
        recs = {p: by_seed(replay, sc, p, "base") for p in POLICIES}
        recs.update({b: by_seed(baseline_rows, sc, b, "base") for b in BASELINES})

        def clean(r):
            c = r["p4_counters"]
            return c["completed_w_clean"] / c["arrived_w"] if c["arrived_w"] else None

        res2: dict[str, Any] = {"metric": "incident-free completion of window-arrived tasks",
               "levels": {p: level(rr, clean) for p, rr in recs.items()},
               "completion_window_levels": {p: level(rr, lambda r: r["completion_rate_window"])
                                            for p, rr in recs.items()},
               "civicworkos_minus": {c: summarize_diff(*paired_values(recs["civicworkos"], recs[c], clean))
                                     for c in ("civicworkos_nolearn", "efficiency", "static", *BASELINES)}}
        out["joint_safety_completion"][sc] = res2
    out["joint_safety_completion"]["h7_note"] = "H7's pre-specified verdict (not supported) is unchanged"
    return out


# ---------------------------------------------------------------------------

def legacy_blocks(workers: int | None, out: Path, stored: dict) -> dict:
    jobs = [(s, sc, "civicworkos_outcomeonly", "base") for s in SEEDS for sc in ("routine", "surge", "disruption")]
    for variant in ("tau_half", "tau_double", "machine_price_x3"):
        jobs += [(s, "routine", p, variant) for s in SEEDS for p in ("efficiency", "civicworkos")]
    t0 = time.time()
    with ProcessPoolExecutor(max_workers=workers) as ex:
        rows = list(ex.map(_job, jobs, chunksize=1))
    out.mkdir(parents=True, exist_ok=True)
    with open(out / "runs.jsonl", "w", encoding="utf-8") as f:
        for r in rows:
            f.write(json.dumps(r) + "\n")
    stored = dict(stored)
    for r in rows:
        stored[(r["seed"], r["scenario"], r["policy"], r["variant"])] = r

    def contrast(scenario, a, b, variant_a, variant_b, metric):
        diffs, va, vb = [], [], []
        for s in SEEDS:
            x = stored[(s, scenario, a, variant_a)][metric]
            y = stored[(s, scenario, b, variant_b)][metric]
            if any(isinstance(v, float) and v != v for v in (x, y)):
                continue
            va.append(x)
            vb.append(y)
            diffs.append(x - y)
        d = np.array(diffs)
        m, lo, hi, n = mean_ci(diffs)
        return {"a_mean": float(np.mean(va)), "b_mean": float(np.mean(vb)), "diff": m, "ci_low": lo,
                "ci_high": hi, "n": n, "p_unadjusted": wilcoxon_p(d), "effect_r": rank_biserial(d)}

    result: dict = {"note": "Exploratory analyses; not part of the pre-specified Holm family.",
                    "wall_seconds": round(time.time() - t0, 1), "outcome_only": {}, "sensitivity": {}}
    for sc in ("routine", "surge", "disruption"):
        result["outcome_only"][sc] = {m: contrast(sc, "civicworkos", "civicworkos_outcomeonly", "base", "base", m)
                                      for m in METRICS}
    for variant in ("base", "tau_half", "tau_double", "machine_price_x3"):
        block = {m: contrast("routine", "civicworkos", "efficiency", variant, variant, m) for m in METRICS}
        ratios = [stored[(s, "routine", "civicworkos", variant)]["cost_per_completed"]
                  / stored[(s, "routine", "efficiency", variant)]["cost_per_completed"] for s in SEEDS]
        block["cost_index"] = dict(zip(("mean", "ci_low", "ci_high", "n"), mean_ci([100 * r for r in ratios])))
        result["sensitivity"][variant] = block
    print(f"{len(rows)} runs in {time.time() - t0:.0f} s")
    return result


def main() -> int:
    ap = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    ap.add_argument("--blocks", nargs="+", choices=LEGACY + P4_BLOCKS, default=list(LEGACY + P4_BLOCKS))
    ap.add_argument("--dest", default=str(ROOT / "reproducibility" / "data" / "exploratory.json"))
    ap.add_argument("--out", default=str(ROOT / "results" / "exploratory"))
    ap.add_argument("--workers", type=int, default=None)
    a = ap.parse_args()
    out, dest = Path(a.out), Path(a.dest)
    stored = load_stored()
    result: dict = json.loads(dest.read_text(encoding="utf-8")) if dest.exists() else {}

    if any(b in LEGACY for b in a.blocks):
        legacy = legacy_blocks(a.workers, out, stored)
        for key in ("note", "wall_seconds"):
            result[key] = legacy[key]
        for b in LEGACY:
            if b in a.blocks:
                result[b] = legacy[b]

    p4 = [b for b in a.blocks if b in P4_BLOCKS]
    if p4:
        t0 = time.time()
        runs: dict = {}
        replay = run_p4("counter_replay", [(s, sc, p, "base") for s in SEEDS for sc in SCENARIOS3 for p in POLICIES],
                        out, a.workers, runs)
        identity = check_identity(replay, stored)
        if not identity["identical"]:
            raise SystemExit(f"counter replay differs from the stored reporting runs: {identity['mismatches'][:5]}")
        meta = {"label": LABEL, "seeds": [0, 29], "code_sha256": code_sha(), "runs": runs,
                "counter_replay_identity": identity, "python": sys.version.split()[0],
                "numpy": np.__version__}
        if "baselines" in p4 or "derived" in p4:
            base_rows = run_p4("baselines", [(s, sc, p, "base") for s in SEEDS for sc in SCENARIOS3 for p in BASELINES],
                               out, a.workers, runs)
        if "baselines" in p4:
            result["baselines"] = block_baselines(base_rows, replay, stored)
        if "sensor_realism" in p4:
            two = ("routine", "disruption")
            jobs = [(s, sc, "civicworkos", v) for v in SENSOR_SETTINGS for sc in two for s in SEEDS]
            jobs += [(s, sc, "efficiency", "combined") for sc in two for s in SEEDS]
            sens = run_p4("sensor_realism", jobs, out, a.workers, runs)
            inv_jobs = [(s, sc, "efficiency", "bias_0.15") for sc in ("routine", "disruption") for s in SEEDS]
            inv_jobs += [(s, sc, "civicworkos_nolearn", "combined") for sc in ("routine", "disruption") for s in SEEDS]
            inv = run_p4("sensor_invariance", inv_jobs, out, a.workers, runs)
            invariance = check_identity(inv, stored)
            invariance["checked"] = "efficiency at bias_0.15 and No-learning at combined equal the stored records"
            if not invariance["identical"]:
                raise SystemExit(f"pairing assumption fails: {invariance['mismatches'][:5]}")
            result["sensor_realism"] = block_sensor(sens, replay, stored, invariance)
        if "takeover_sweep" in p4:
            jobs = [(s, "disruption", p, v) for v in TAKEOVER_SETTINGS for p in ("civicworkos", "static")
                    for s in SEEDS]
            result["takeover_sweep"] = block_takeover(run_p4("takeover_sweep", jobs, out, a.workers, runs), replay)
        if "model_sensitivity" in p4:
            jobs = [(s, "routine", p, v) for v in MODEL_SETTINGS for p in ("civicworkos", "efficiency") for s in SEEDS]
            result["model_sensitivity"] = block_model(run_p4("model_sensitivity", jobs, out, a.workers, runs), replay)
        if "derived" in p4:
            result["derived"] = block_derived(base_rows, replay)
        meta["wall_seconds"] = round(time.time() - t0, 1)
        result["p4_meta"] = meta

    text = json.dumps(result, indent=2)
    dest.parent.mkdir(parents=True, exist_ok=True)
    dest.write_text(text, encoding="utf-8")
    if dest == ROOT / "reproducibility" / "data" / "exploratory.json":
        (out / "exploratory.json").write_text(text, encoding="utf-8")
    print(f"wrote {', '.join(a.blocks)} -> {dest}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
