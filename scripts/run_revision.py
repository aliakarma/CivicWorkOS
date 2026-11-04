"""Exploratory analyses added in revision (NOT part of the pre-specified family).

    python scripts/run_revision.py                    # every block, reusing validated runs
    python scripts/run_revision.py --blocks replay    # selected blocks only

Definitions: ``configs/protocol/exploratory_r1.yaml``. Per-run records go to
``results/revision/<block>/runs.jsonl`` (one file per block, validated against the
code and configuration hashes before reuse) and the summary to
``reproducibility/data/revision.json``. None of this enters the Holm family of
``configs/protocol/hypotheses.yaml``, and the article labels every result as
exploratory.
"""

from __future__ import annotations

import argparse
import hashlib
import json
import math
import sys
import time
from concurrent.futures import ProcessPoolExecutor
from dataclasses import replace
from pathlib import Path
from typing import Any

import numpy as np
from scipy import stats

ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT))

from sim.protocol.analysis import evaluate, mean_ci, rank_biserial, wilcoxon_p  # noqa: E402
from sim.protocol.config import DOMAINS, RunConfig, SimParams, WorldModel  # noqa: E402
from sim.protocol.engine import run_one  # noqa: E402

SEEDS = tuple(range(30))
FRESH = tuple(range(100, 130))
LHS_SEEDS = tuple(range(5))
LHS_N = 40
SC3 = ("routine", "surge", "disruption")
SC2 = ("routine", "disruption")
REF_POLICIES = ("static", "efficiency", "civicworkos", "civicworkos_nolearn", "civicworkos_noretention")
EQR = "efficiency_quota_recency"
LABEL = "added in revision; exploratory (configs/protocol/exploratory_r1.yaml)"
CODE_FILES = ("sim/protocol/engine.py", "sim/protocol/config.py", "sim/protocol/estimation.py", "sim/protocol/skill.py")

WORLD_VARIANTS: dict[str, dict[str, Any]] = {
    "power": {"forgetting": "power"},
    "partial_0.50": {"restoration": 0.50},
    "partial_0.25": {"restoration": 0.25},
    "cloglog": {"link": "cloglog"},
    "cauchit": {"link": "cauchit"},
    "load_ar_0.15": {"load_ar_sd": 0.15, "load_decoder_tracking": 1.0},
    "load_ar_0.30": {"load_ar_sd": 0.30, "load_decoder_tracking": 1.0},
    "load_ar_0.30_t0.5": {"load_ar_sd": 0.30, "load_decoder_tracking": 0.5},
    "load_outcome": {"load_outcome_penalty": 0.30},
    "combined": {"forgetting": "power", "restoration": 0.50, "link": "cloglog", "load_ar_sd": 0.15,
                 "load_decoder_tracking": 0.5},
}
WORLD_DISRUPTION = ("power", "partial_0.50", "cauchit", "combined")
WORLD_LOAD = ("load_ar_0.15", "load_ar_0.30", "load_ar_0.30_t0.5", "combined")
TRUTH_ONLY: dict[str, dict[str, Any]] = {
    "led_true_0.50": {"led_threshold_true": 0.50},
    "led_true_0.60": {"led_threshold_true": 0.60},
    "led_true_0.70": {"led_threshold_true": 0.70},
    "led_true_1.00": {"led_threshold_true": 1.00},
    "graded_linear": {"graded": "linear"},
    "graded_quadratic": {"graded": "quadratic"},
}
INFORMED = {f"led_both_{t:.2f}": t for t in (0.50, 0.60, 0.70, 1.00)}
ADD_ONE = ("eqr_floor", "eqr_gate", "eqr_ceiling", "eqr_ready", "eqr_budget", "eqr_all")
DROP_ONE = ("cw_nofloor", "cw_nogate", "cw_noceiling", "cw_noready", "cw_nobudget")
LHS_BOUNDS: dict[str, tuple[float, float]] = {
    "gamma": (6.0, 10.0), "tau_ret": (60.0, 240.0), "tau_ret_cv": (0.15, 0.45), "rate_cv": (0.10, 0.40),
    "load_sd": (0.10, 0.25), "theta_comp": (0.65, 0.75), "residual": (0.35, 0.55), "human_led_share": (0.30, 0.60),
    "omega_trainee": (0.40, 0.60), "avail_h": (4.0, 5.0), "overtime_factor": (1.1, 1.5),
    "workload_margin": (0.85, 1.00), "takeover_headroom": (1.00, 1.20), "machine_drift_sd": (0.002, 0.008),
    "fault_rate": (0.01, 0.04), "t_detect": (1.0, 3.0), "t_reach": (2.0, 5.0), "t_sa": (6.0, 10.0),
    "ootl_factor": (0.3, 1.0), "overload_sa_factor": (1.2, 1.8), "value": (5.0, 20.0), "wage_trainee": (0.4, 0.8),
    "incident_cost": (15.0, 60.0), "p_incident_failure": (0.10, 0.20), "p_incident_takeover_failure": (0.30, 0.70),
    "p_incident_mrc": (0.01, 0.10), "variance_scale": (0.5, 2.0), "probe_prob": (0.15, 0.45),
    "probe_sd": (0.04, 0.16), "telemetry_prob": (0.25, 0.75), "telemetry_sd": (0.05, 0.20),
    "workload_sensor_prob": (0.35, 0.90), "workload_sensor_sd": (0.05, 0.20), "eta": (0.8, 1.6),
    "oversight_p_sd": (0.03, 0.12), "readiness_z": (0.84, 1.96), "retention_guard": (0.3, 0.8),
    "supervision_recovery": (0.50, 0.90), "attrition": (0.06, 0.18), "machine_price_mult": (1.0, 3.0),
    "hybrid_phi_shift": (-0.10, 0.10),
}
# Constants outside the hypercube: one at a time, CivicWorkOS and Efficiency, routine.
EXTRA_OAT = ("demand_minus_0.10", "demand_plus_0.10", "dur_har_0.70", "dur_har_0.90", "bonus_0.00", "bonus_0.10",
             "theta0_0.20", "theta0_0.40")
H_DEF = (0.0, 0.03, 0.05, 0.10, 0.15, 0.30, 0.50)
H_STOP = (0.03, 0.15, 0.50)


def lhs_design() -> list[dict[str, float]]:
    rng = np.random.default_rng([0, 7919, 103])
    names = list(LHS_BOUNDS)
    draws: list[dict[str, float]] = [{} for _ in range(LHS_N)]
    for name in names:
        low, high = LHS_BOUNDS[name]
        cells = (rng.permutation(LHS_N) + rng.random(LHS_N)) / LHS_N
        for i in range(LHS_N):
            draws[i][name] = float(low + cells[i] * (high - low))
    return draws


def lhs_config(values: dict[str, float]) -> RunConfig:
    base = SimParams()
    scale = values["variance_scale"]
    fields = {k: v for k, v in values.items() if hasattr(base, k)}
    params = replace(base, **fields, prior_offset_var=base.prior_offset_var * scale,
                     human_process_var=base.human_process_var * scale,
                     machine_prior_var=base.machine_prior_var * scale,
                     machine_process_var=base.machine_process_var * scale,
                     requirement_prior_var=base.requirement_prior_var * scale)
    shift = values["hybrid_phi_shift"]
    domains = tuple(replace(d, attrition_per_year=values["attrition"],
                            machine_cost_per_h=d.machine_cost_per_h * values["machine_price_mult"],
                            modes=tuple(replace(m, phi=m.phi + shift) if 0.0 < m.phi < 1.0 else m for m in d.modes))
                    for d in DOMAINS)
    return RunConfig(params=params, domains=domains,
                     world=WorldModel(supervision_recovery=values["supervision_recovery"]))


_DESIGN = lhs_design()


def extra_config(variant: str) -> RunConfig:
    name, value = variant.rsplit("_", 1)
    x = float(value)
    if name == "theta0":
        return RunConfig(params=replace(SimParams(), theta_0=x))
    if name.startswith("demand"):
        sign = -x if "minus" in name else x
        return RunConfig(domains=tuple(replace(d, modes=tuple(replace(m, demand=round(m.demand + sign, 10))
                                                              if 0.0 < m.phi < 1.0 else m for m in d.modes))
                                       for d in DOMAINS))
    if name == "dur_har":
        return RunConfig(domains=tuple(replace(d, modes=tuple(replace(m, duration_mult=x) if m.name == "H+A+R" else m
                                                              for m in d.modes)) for d in DOMAINS))
    if name == "bonus":
        return RunConfig(domains=tuple(replace(d, modes=tuple(replace(m, machine_bonus=x) if m.name == "H+A+R" else m
                                                              for m in d.modes)) for d in DOMAINS))
    raise ValueError(variant)


def config(variant: str) -> RunConfig:
    if variant == "base":
        return RunConfig()
    if variant in WORLD_VARIANTS:
        return RunConfig(world=WorldModel(**WORLD_VARIANTS[variant]))
    if variant in TRUTH_ONLY:
        return RunConfig(world=WorldModel(**TRUTH_ONLY[variant]))
    if variant in INFORMED:
        return RunConfig(params=replace(SimParams(), human_led_share=INFORMED[variant]))
    if variant.startswith("lhs_"):
        return lhs_config(_DESIGN[int(variant[4:])])
    if variant in EXTRA_OAT:
        return extra_config(variant)
    raise ValueError(variant)


def _job(args):
    seed, scenario, policy, variant = args
    r = run_one(seed, scenario, policy, config(variant), revision=True)
    r.pop("trajectory")
    r["variant"] = variant
    return r


def _sha(data: bytes) -> str:
    return hashlib.sha256(data).hexdigest()


def code_sha() -> str:
    return _sha(b"".join((ROOT / f).read_bytes() for f in CODE_FILES))


def config_sha(variant: str) -> str:
    return _sha(json.dumps(config(variant).as_dict(), sort_keys=True).encode())


def run_block(name: str, jobs: list, out: Path, workers: int | None, log: dict) -> list[dict]:
    path = out / name / "runs.jsonl"
    want = {j: config_sha(j[3]) for j in jobs}
    code = code_sha()
    if path.exists():
        rows = [json.loads(line) for line in open(path, encoding="utf-8")]
        have = {(r["seed"], r["scenario"], r["policy"], r["variant"]): r for r in rows}
        if set(have) == set(want) and all(r["config_sha"] == want[k] and r["code_sha"] == code
                                          for k, r in have.items()):
            log[name] = {"runs": len(rows), "reused": True}
            print(f"{name}: reused {len(rows)} validated runs", flush=True)
            return rows
    t0 = time.time()
    with ProcessPoolExecutor(max_workers=workers) as ex:
        rows = list(ex.map(_job, jobs, chunksize=1))
    for r in rows:
        r["config_sha"] = want[(r["seed"], r["scenario"], r["policy"], r["variant"])]
        r["code_sha"] = code
    path.parent.mkdir(parents=True, exist_ok=True)
    with open(path, "w", encoding="utf-8") as f:
        for r in rows:
            f.write(json.dumps(r) + "\n")
    log[name] = {"runs": len(rows), "reused": False, "wall_seconds": round(time.time() - t0, 1)}
    print(f"{name}: {len(rows)} runs in {time.time() - t0:.0f} s", flush=True)
    return rows


# ---------------------------------------------------------------------------
# per-run derived quantities (all from the recorded counters)
# ---------------------------------------------------------------------------

RISK = np.array([d.risk for d in DOMAINS])
DOM = tuple(d.key for d in DOMAINS)


def _rc(r: dict, key: str) -> np.ndarray:
    return np.array(r["rev_counters"][key], dtype=float)


def total_completed(r: dict) -> float:
    return float(_rc(r, "completed").sum())


def nonwage_cost(r: dict, incident_cost: float = 30.0) -> float:
    return float(_rc(r, "machine_cost").sum() + _rc(r, "incidents").sum() * incident_cost)


def payroll_per_completed(r: dict) -> float:
    return (float(_rc(r, "payroll").sum() + _rc(r, "overtime").sum()) + nonwage_cost(r)) / total_completed(r)


def fullday_per_completed(r: dict, hours: float = 8.0, wage_trainee: float = 0.6) -> float:
    pay = hours * (float(_rc(r, "cert_days").sum()) + wage_trainee * float(_rc(r, "trainee_days").sum()))
    return (pay + nonwage_cost(r)) / total_completed(r)


def per_1000(r: dict, numerator: float) -> float:
    return 1000.0 * numerator / _rc(r, "arrived_w").sum()


def hazard_adjusted(r: dict, h_def: float, h_stop: float) -> float:
    missed = _rc(r, "arrived_w") - _rc(r, "completed_w")
    return per_1000(r, _rc(r, "incidents_w").sum() + h_def * float((RISK * missed).sum())
                    + (h_stop - 0.03) * float((RISK * _rc(r, "mrc_w")).sum()))


def fault_recovered(r: dict, phase: str, window: bool = False, k: int | None = None) -> float:
    tag = f"fi_{phase}{'_w' if window else ''}"
    n, ok = _rc(r, f"{tag}_n"), _rc(r, f"{tag}_recovered_p")
    return float(ok.sum() / n.sum()) if k is None else float(ok[k] / n[k])


def fault_stop(r: dict, phase: str, window: bool = False) -> float:
    tag = f"fi_{phase}{'_w' if window else ''}"
    return float(_rc(r, f"{tag}_stop").sum() / _rc(r, f"{tag}_n").sum())


def fault_hazard(r: dict, phase: str, h_stop: float, window: bool = False) -> float:
    """Expected incidents per 1,000 injected faults, each domain weighted by its own faults."""
    tag = f"fi_{phase}{'_w' if window else ''}"
    att, ok, stop, n = (_rc(r, f"{tag}_{s}") for s in ("attempted", "recovered_p", "stop", "n"))
    return 1000.0 * float((RISK * (0.5 * (att - ok) + h_stop * stop)).sum() / n.sum())


# ---------------------------------------------------------------------------
# statistics
# ---------------------------------------------------------------------------

def by_seed(rows: list[dict], scenario: str, policy: str, variant: str = "base") -> dict:
    return {r["seed"]: r for r in rows if r["scenario"] == scenario and r["policy"] == policy
            and r["variant"] == variant}


def level(recs: dict, f) -> dict:
    vals = [f(r) for r in recs.values()]
    return dict(zip(("mean", "ci_low", "ci_high", "n"), mean_ci([float(v) for v in vals])))


def contrast(a: dict, b: dict, f) -> dict:
    keep = [s for s in a if s in b]
    xa, xb = [], []
    for s in keep:
        x, y = float(f(a[s])), float(f(b[s]))
        if math.isnan(x) or math.isnan(y):
            continue
        xa.append(x)
        xb.append(y)
    d = np.array(xa) - np.array(xb)
    m, lo, hi, n = mean_ci(list(d))
    return {"a_mean": float(np.mean(xa)), "b_mean": float(np.mean(xb)), "diff": m, "ci_low": lo, "ci_high": hi, "n": n,
            "p_unadjusted": wilcoxon_p(d), "effect_r": rank_biserial(d)}


def cost_index(a: dict, eff: dict, f=lambda r: r["cost_per_completed"]) -> dict:
    return dict(zip(("mean", "ci_low", "ci_high", "n"), mean_ci([100.0 * f(a[s]) / f(eff[s]) for s in a if s in eff])))


METRICS = ("completion_rate", "current_share_end", "current_end", "certified_end", "graduations", "overload_share",
           "mean_workload", "takeover_success_rate", "incidents_per_1000", "mrc", "proficiency_mae_end")
WINDOW_METRICS = ("completion_rate_window", "takeover_success_window", "takeover_requests_window",
                  "incidents_per_1000_window")


def policy_levels(recs: dict, eff: dict, scenario: str) -> dict:
    ms = METRICS + (WINDOW_METRICS if scenario != "routine" else ())
    out = {m: level(recs, lambda r, m=m: r[m]) for m in ms}
    out["cost_index"] = cost_index(recs, eff)
    return out


# ---------------------------------------------------------------------------
# blocks
# ---------------------------------------------------------------------------

def block_replay(rows: list[dict]) -> dict:
    stored: dict = {}
    for line in open(ROOT / "results" / "protocol" / "runs.jsonl", encoding="utf-8"):
        r = json.loads(line)
        stored[(r["seed"], r["scenario"], r["policy"])] = r
    for line in open(ROOT / "results" / "exploratory" / "baselines" / "runs.jsonl", encoding="utf-8"):
        r = json.loads(line)
        stored[(r["seed"], r["scenario"], r["policy"])] = r
    bad, compared = [], 0
    for r in rows:
        ref = stored[(r["seed"], r["scenario"], r["policy"])]
        compared += 1
        for k, v in ref.items():
            if k in ("p4_counters", "variant", "config_sha", "code_sha", "trajectory"):
                continue
            if json.dumps(v) != json.dumps(r[k]):
                bad.append([r["seed"], r["scenario"], r["policy"], k])
    if bad:
        raise SystemExit(f"replay differs from the stored records: {bad[:5]}")
    return {"records_compared": compared, "mismatches": 0}


def block_domains(rows: list[dict]) -> dict:
    out: dict = {}
    for sc in SC3:
        out[sc] = {}
        for p in (*REF_POLICIES, EQR):
            recs = by_seed(rows, sc, p)
            res: dict = {}
            for k, key in enumerate(DOM):
                res[key] = {
                    "completion": level(recs, lambda r, k=k: _rc(r, "completed")[k] / _rc(r, "arrived")[k]),
                    "cost_per_completed": level(recs, lambda r, k=k: _rc(r, "cost")[k] / _rc(r, "completed")[k]),
                    "overload": level(recs, lambda r, k=k: _rc(r, "overload_days")[k] / _rc(r, "human_days")[k]),
                    "certified_end": level(recs, lambda r, k=k: _rc(r, "certified_end")[k]),
                    "current_end": level(recs, lambda r, k=k: _rc(r, "current_end")[k]),
                    "current_share": level(recs, lambda r, k=k: _rc(r, "current_end")[k] / _rc(r, "certified_end")[k]),
                    "graduations": level(recs, lambda r, k=k: _rc(r, "graduations")[k]),
                    "incidents_per_1000": level(recs, lambda r, k=k: 1000 * _rc(r, "incidents")[k]
                                                / _rc(r, "arrived")[k]),
                }
            out[sc][p] = res
    return out


def _attainment(r: dict, k: int, y: int) -> float:
    return r["rev_counters"]["lam_year"][k][y] / r["rev_counters"]["budget_year"][k][y]


def block_budget(rows: list[dict]) -> dict:
    out: dict = {"definition": "Lambda_k over B_k at each year's close, B_k = eta N_k(t) r_k h_k with N_k at the close"}
    for p in ("civicworkos", "civicworkos_nolearn", "civicworkos_noretention", "static", EQR):
        recs = by_seed(rows, "routine", p)
        res: dict = {}
        for k, key in enumerate(DOM):
            res[key] = {
                "lambda_mean": level(recs, lambda r, k=k: float(np.mean(r["rev_counters"]["lam_year"][k]))),
                "budget_mean": level(recs, lambda r, k=k: float(np.mean(r["rev_counters"]["budget_year"][k]))),
                "attainment_by_year": [level(recs, lambda r, k=k, y=y: _attainment(r, k, y)) for y in range(3)],
                "attainment": level(recs, lambda r, k=k: float(sum(r["rev_counters"]["lam_year"][k])
                                                               / sum(r["rev_counters"]["budget_year"][k]))),
                "share_of_years_met": float(np.mean([_attainment(r, k, y) >= 1.0 for r in recs.values()
                                                     for y in range(3)])),
            }
        res["all"] = {
            "lambda_total": level(recs, lambda r: float(sum(sum(v) for v in r["rev_counters"]["lam_year"]) / 3)),
            "budget_total": level(recs, lambda r: float(sum(sum(v) for v in r["rev_counters"]["budget_year"]) / 3)),
            "attainment": level(recs, lambda r: float(sum(sum(v) for v in r["rev_counters"]["lam_year"])
                                                      / sum(sum(v) for v in r["rev_counters"]["budget_year"]))),
        }
        out[p] = res
    return out


def block_payroll(rows: list[dict]) -> dict:
    out: dict = {}
    for sc in SC3:
        eff = by_seed(rows, sc, "efficiency")
        out[sc] = {}
        for p in (*REF_POLICIES, "efficiency_recency", EQR):
            recs = by_seed(rows, sc, p)
            out[sc][p] = {
                "assigned_hours_index": cost_index(recs, eff),
                "fixed_payroll_index": cost_index(recs, eff, payroll_per_completed),
                "full_day_index": cost_index(recs, eff, fullday_per_completed),
                "fixed_payroll_per_completed": level(recs, payroll_per_completed),
                "payroll_share_idle": level(recs, lambda r: 1.0 - (float(_rc(r, "cost").sum()) - nonwage_cost(r))
                                            / float(_rc(r, "payroll").sum() + _rc(r, "overtime").sum())),
                "person_days_certified": level(recs, lambda r: float(_rc(r, "cert_days").sum())),
                "person_days_trainee": level(recs, lambda r: float(_rc(r, "trainee_days").sum())),
                "mean_workload": level(recs, lambda r: r["mean_workload"]),
            }
    return out


def _exposure(r: dict) -> dict:
    return {"recovered_per_1000": per_1000(r, _rc(r, "recovered_w").sum()),
            "unrecovered_per_1000": per_1000(r, _rc(r, "requests_w").sum() - _rc(r, "recovered_w").sum()),
            "stopped_per_1000": per_1000(r, _rc(r, "mrc_w").sum()),
            "failed_takeover_per_1000": per_1000(r, _rc(r, "requests_w").sum() - _rc(r, "recovered_w").sum()
                                                 - _rc(r, "mrc_w").sum())}


def block_takeover(rows: list[dict]) -> dict:
    out: dict = {"common_exposure": {}, "fault_injection": {}, "deferral_hazard": {}}
    pols = (*REF_POLICIES, "efficiency_recency", EQR)
    recs = {p: by_seed(rows, "disruption", p) for p in pols}
    for p in pols:
        out["common_exposure"][p] = {
            key: level(recs[p], lambda r, key=key: _exposure(r)[key])
            for key in ("recovered_per_1000", "unrecovered_per_1000", "stopped_per_1000", "failed_takeover_per_1000")}
        out["common_exposure"][p]["incidents_per_1000_window"] = level(recs[p], lambda r: r["incidents_per_1000_window"])
        out["common_exposure"][p]["completion_window"] = level(recs[p], lambda r: r["completion_rate_window"])
        out["common_exposure"][p]["missed_share_window"] = level(recs[p], lambda r: 1.0 - r["completion_rate_window"])
    for sc in SC2:
        out["fault_injection"][sc] = {}
        for p in pols:
            rr = by_seed(rows, sc, p)
            res: dict = {}
            for phase in ("start", "end"):
                res[phase] = {"recovered": level(rr, lambda r, ph=phase: fault_recovered(r, ph)),
                              "stop": level(rr, lambda r, ph=phase: fault_stop(r, ph)),
                              "by_domain": {key: level(rr, lambda r, ph=phase, k=k: fault_recovered(r, ph, k=k))
                                            for k, key in enumerate(DOM)},
                              "hazard_per_1000": {str(h): level(rr, lambda r, ph=phase, h=h: fault_hazard(r, ph, h))
                                                  for h in H_STOP}}
                if sc == "disruption":
                    res[phase]["recovered_window"] = level(rr, lambda r, ph=phase: fault_recovered(r, ph, True))
                    res[phase]["stop_window"] = level(rr, lambda r, ph=phase: fault_stop(r, ph, True))
            out["fault_injection"][sc][p] = res
    cw = recs["civicworkos"]
    out["fault_injection_contrasts"] = {
        phase: {p: {"recovered": contrast(cw, recs[p], lambda r, ph=phase: fault_recovered(r, ph)),
                    **{f"hazard_{h}": contrast(cw, recs[p], lambda r, ph=phase, h=h: fault_hazard(r, ph, h))
                       for h in H_STOP}}
                for p in pols if p != "civicworkos"}
        for phase in ("start", "end")}
    for h_stop in H_STOP:
        block: dict = {}
        for h_def in H_DEF:
            block[str(h_def)] = {
                "levels": {p: level(recs[p], lambda r, a=h_def, b=h_stop: hazard_adjusted(r, a, b)) for p in pols},
                "civicworkos_minus": {p: contrast(cw, recs[p], lambda r, a=h_def, b=h_stop: hazard_adjusted(r, a, b))
                                      for p in pols if p != "civicworkos"},
            }
        out["deferral_hazard"][str(h_stop)] = block
    breakeven: dict = {}
    for p in pols:
        if p == "civicworkos":
            continue
        d0 = np.mean([hazard_adjusted(cw[s], 0.0, 0.03) - hazard_adjusted(recs[p][s], 0.0, 0.03) for s in cw])
        d1 = np.mean([hazard_adjusted(cw[s], 1.0, 0.03) - hazard_adjusted(recs[p][s], 1.0, 0.03) for s in cw])
        slope = d1 - d0
        breakeven[p] = {"h_def_where_equal": None if slope == 0 else float(-d0 / slope), "diff_at_0": float(d0),
                        "slope": float(slope)}
    out["deferral_breakeven_h_stop_0.03"] = breakeven
    return out


def block_uncertainty(rows_addone: list[dict], replay: list[dict]) -> dict:
    out: dict = {}
    for sc in SC2:
        cw = by_seed(replay, sc, "civicworkos")
        nu = by_seed(rows_addone, sc, "cw_nouncertainty")
        eff = by_seed(replay, sc, "efficiency")
        ms = METRICS + (WINDOW_METRICS if sc != "routine" else ())
        out[sc] = {"levels": policy_levels(nu, eff, sc), "civicworkos": policy_levels(cw, eff, sc),
                   "civicworkos_minus": {m: contrast(cw, nu, lambda r, m=m: r[m]) for m in ms}}
        out[sc]["fault_end"] = {"civicworkos": level(cw, lambda r: fault_recovered(r, "end")),
                                "no_uncertainty": level(nu, lambda r: fault_recovered(r, "end"))}
    cw = by_seed(replay, "routine", "civicworkos")
    dis = by_seed(replay, "disruption", "civicworkos")
    out["coverage"] = {
        "proficiency_1.28": level(cw, lambda r: float(_rc(r, "prof_cov_128").sum() / _rc(r, "prof_n").sum())),
        "proficiency_1.96": level(cw, lambda r: float(_rc(r, "prof_cov_196").sum() / _rc(r, "prof_n").sum())),
        "machine_1.96": level(cw, lambda r: float(_rc(r, "mach_cov_196").sum() / _rc(r, "mach_days").sum())),
        "machine_1.96_disruption_window": level(dis, lambda r: float(_rc(r, "mach_cov_196_w").sum()
                                                                     / _rc(r, "mach_days_w").sum())),
        "gate_uncertainty_blocks": level(cw, lambda r: float(_rc(r, "gate_uncertainty_blocks").sum())),
        "gate_uncertainty_blocks_disruption": level(dis, lambda r: float(_rc(r, "gate_uncertainty_blocks").sum())),
    }
    return out


def block_add_one(rows: list[dict], replay: list[dict]) -> dict:
    out: dict = {}
    for sc in SC2:
        eff = by_seed(replay, sc, "efficiency")
        base = by_seed(replay, sc, EQR)
        cw = by_seed(replay, sc, "civicworkos")
        ms = METRICS + (WINDOW_METRICS if sc != "routine" else ())
        res: dict = {"base": policy_levels(base, eff, sc), "civicworkos": policy_levels(cw, eff, sc),
                     "add_one": {}, "drop_one": {}}
        for p in ADD_ONE:
            recs = by_seed(rows, sc, p)
            res["add_one"][p] = {"levels": policy_levels(recs, eff, sc),
                                 "minus_base": {m: contrast(recs, base, lambda r, m=m: r[m]) for m in ms}}
            res["add_one"][p]["levels"]["fixed_payroll_index"] = cost_index(recs, eff, payroll_per_completed)
        for p in DROP_ONE:
            recs = by_seed(rows, sc, p)
            res["drop_one"][p] = {"levels": policy_levels(recs, eff, sc),
                                  "civicworkos_minus": {m: contrast(cw, recs, lambda r, m=m: r[m]) for m in ms}}
            res["drop_one"][p]["levels"]["fixed_payroll_index"] = cost_index(recs, eff, payroll_per_completed)
        res["base"]["fixed_payroll_index"] = cost_index(base, eff, payroll_per_completed)
        res["civicworkos"]["fixed_payroll_index"] = cost_index(cw, eff, payroll_per_completed)
        out[sc] = res
    return out


def block_world(rows: list[dict], replay: list[dict]) -> dict:
    out: dict = {}
    for v in ("base", *WORLD_VARIANTS):
        out[v] = {}
        src = replay if v == "base" else rows
        for sc in SC2:
            cw = by_seed(src, sc, "civicworkos", v)
            if not cw:
                continue
            eff = by_seed(src, sc, "efficiency", v)
            eqr = by_seed(src, sc, EQR, v)
            ms = METRICS + (WINDOW_METRICS if sc != "routine" else ())
            res = {"civicworkos": policy_levels(cw, eff, sc), "efficiency": policy_levels(eff, eff, sc),
                   "eqr": policy_levels(eqr, eff, sc),
                   "minus_efficiency": {m: contrast(cw, eff, lambda r, m=m: r[m]) for m in ms},
                   "minus_eqr": {m: contrast(cw, eqr, lambda r, m=m: r[m]) for m in ms},
                   "fixed_payroll_index": cost_index(cw, eff, payroll_per_completed)}
            nl = by_seed(src, sc, "civicworkos_nolearn", v)
            if nl:
                res["no_learning"] = policy_levels(nl, eff, sc)
                res["minus_no_learning"] = {m: contrast(cw, nl, lambda r, m=m: r[m]) for m in ms}
            out[v][sc] = res
    return out


def block_restoration(rows: list[dict], replay: list[dict]) -> dict:
    out: dict = {"base": {}}
    def row(src, v):
        cw, eff, eqr = (by_seed(src, "routine", p, v) for p in ("civicworkos", "efficiency", EQR))
        return {"civicworkos": policy_levels(cw, eff, "routine"), "efficiency": policy_levels(eff, eff, "routine"),
                "eqr": policy_levels(eqr, eff, "routine"),
                "cw_minus_efficiency_share": contrast(cw, eff, lambda r: r["current_share_end"]),
                "cw_minus_eqr_share": contrast(cw, eqr, lambda r: r["current_share_end"]),
                "cw_minus_efficiency_current": contrast(cw, eff, lambda r: r["current_end"])}
    out["base"] = row(replay, "base")
    out["truth_only"] = {v: row(rows, v) for v in TRUTH_ONLY}
    out["allocator_informed"] = {v: row(rows, v) for v in INFORMED}
    return out


def block_fresh(rows: list[dict], replay: list[dict]) -> dict:
    import yaml

    spec = yaml.safe_load((ROOT / "configs" / "protocol" / "hypotheses.yaml").read_text(encoding="utf-8"))
    tests_fresh = evaluate([r for r in rows if r["policy"] in REF_POLICIES], spec)
    tests_ref = evaluate([r for r in replay if r["policy"] in REF_POLICIES], spec)
    keep = ("id", "scenario", "comparison", "n", "estimate", "ci_low", "ci_high", "p_holm", "effect_r", "supported")
    out: dict = {"tests_fresh": [{k: t[k] for k in keep} for t in tests_fresh],
                 "tests_reference": [{k: t[k] for k in keep} for t in tests_ref]}
    out["verdicts_agree"] = all(a["supported"] == b["supported"] for a, b in zip(tests_fresh, tests_ref))
    out["levels"] = {}
    for sc in SC3:
        eff = by_seed(rows, sc, "efficiency")
        out["levels"][sc] = {p: policy_levels(by_seed(rows, sc, p), eff, sc) for p in (*REF_POLICIES, EQR)}
    # percentile bootstrap against the t-interval, for the paired contrasts of the family
    rng = np.random.default_rng([0, 7919, 104])
    checks = []
    for t in tests_ref:
        a = by_seed(replay, t["scenario"], "civicworkos")
        b = by_seed(replay, t["scenario"], t["comparison"])
        metric = t["metric"]
        if metric == "cost_per_completed_ratio_to_efficiency":
            vals = np.array([a[s]["cost_per_completed"] / b[s]["cost_per_completed"] for s in SEEDS])
        else:
            vals = np.array([a[s][metric] - b[s][metric] for s in SEEDS if not (
                math.isnan(a[s][metric]) or math.isnan(b[s][metric]))])
        boot = vals[rng.integers(0, len(vals), size=(10000, len(vals)))].mean(axis=1)
        lo, hi = np.percentile(boot, [2.5, 97.5])
        half = (t["ci_high"] - t["ci_low"]) / 2.0
        checks.append({"id": t["id"], "scenario": t["scenario"], "comparison": t["comparison"], "t_low": t["ci_low"],
                       "t_high": t["ci_high"], "boot_low": float(lo), "boot_high": float(hi),
                       "max_endpoint_gap_over_t_half_width": float(max(abs(lo - t["ci_low"]), abs(hi - t["ci_high"]))
                                                                   / half) if half else 0.0,
                       "skew": float(stats.skew(vals)), "shapiro_p": float(stats.shapiro(vals).pvalue)
                       if np.ptp(vals) > 0 else None})
    out["interval_check"] = checks
    return out


def block_lhs(rows: list[dict]) -> dict:
    names = list(LHS_BOUNDS)
    per: dict = {}
    def mean_of(recs, f):
        return float(np.mean([f(r) for r in recs.values()]))
    for i in range(LHS_N):
        v = f"lhs_{i}"
        d: dict = {}
        for sc in SC2:
            cw, eff, eqr = (by_seed(rows, sc, p, v) for p in ("civicworkos", "efficiency", EQR))
            for name, a, b in (("eff", cw, eff), ("eqr", cw, eqr)):
                d[f"{sc}_share_minus_{name}"] = mean_of(a, lambda r: r["current_share_end"]) - mean_of(
                    b, lambda r: r["current_share_end"])
                d[f"{sc}_current_minus_{name}"] = mean_of(a, lambda r: r["current_end"]) - mean_of(
                    b, lambda r: r["current_end"])
                d[f"{sc}_overload_minus_{name}"] = 100 * (mean_of(a, lambda r: r["overload_share"]) - mean_of(
                    b, lambda r: r["overload_share"]))
                d[f"{sc}_completion_minus_{name}"] = 100 * (mean_of(a, lambda r: r["completion_rate"]) - mean_of(
                    b, lambda r: r["completion_rate"]))
                d[f"{sc}_certified_minus_{name}"] = mean_of(a, lambda r: r["certified_end"]) - mean_of(
                    b, lambda r: r["certified_end"])
            d[f"{sc}_cost_index_cw"] = float(np.mean([100 * cw[s]["cost_per_completed"] / eff[s]["cost_per_completed"]
                                                      for s in cw]))
            d[f"{sc}_cost_index_eqr"] = float(np.mean([100 * eqr[s]["cost_per_completed"] / eff[s]["cost_per_completed"]
                                                       for s in cw]))
            d[f"{sc}_fixed_payroll_index_cw"] = float(np.mean([100 * payroll_per_completed(cw[s])
                                                               / payroll_per_completed(eff[s]) for s in cw]))
            d[f"{sc}_share_cw"] = mean_of(cw, lambda r: r["current_share_end"])
            d[f"{sc}_overload_cw"] = 100 * mean_of(cw, lambda r: r["overload_share"])
            d[f"{sc}_completion_cw"] = 100 * mean_of(cw, lambda r: r["completion_rate"])
            if sc == "disruption":
                for name, b in (("eff", eff), ("eqr", eqr)):
                    d[f"takeover_window_minus_{name}"] = mean_of(cw, lambda r: r["takeover_success_window"]) - mean_of(
                        b, lambda r: r["takeover_success_window"])
                    d[f"incidents_window_minus_{name}"] = mean_of(cw, lambda r: r["incidents_per_1000_window"]) - mean_of(
                        b, lambda r: r["incidents_per_1000_window"])
        per[v] = d
    outcomes = list(next(iter(per.values())))
    design = np.array([[_DESIGN[i][n] for n in names] for i in range(LHS_N)])
    out: dict = {"n_draws": LHS_N, "seeds_per_draw": len(LHS_SEEDS), "bounds": {k: list(v) for k, v in LHS_BOUNDS.items()},
                 "outcomes": {}}
    for o in outcomes:
        vals = np.array([per[f"lhs_{i}"][o] for i in range(LHS_N)])
        corr = []
        for j, n in enumerate(names):
            rho = float(stats.spearmanr(design[:, j], vals).statistic)
            corr.append((n, rho))
        corr.sort(key=lambda x: -abs(x[1]))
        out["outcomes"][o] = {"min": float(vals.min()), "median": float(np.median(vals)), "max": float(vals.max()),
                              "share_positive": float(np.mean(vals > 0)), "share_negative": float(np.mean(vals < 0)),
                              "top_spearman": corr[:4]}
    out["critical_abs_spearman_0.05"] = float(stats.t.ppf(0.975, LHS_N - 2)
                                              / math.sqrt(LHS_N - 2 + stats.t.ppf(0.975, LHS_N - 2) ** 2))
    return out


def block_extra(rows: list[dict], replay: list[dict]) -> dict:
    out: dict = {}
    for v in ("base", *EXTRA_OAT):
        src = replay if v == "base" else rows
        cw, eff = by_seed(src, "routine", "civicworkos", v), by_seed(src, "routine", "efficiency", v)
        out[v] = {m: contrast(cw, eff, lambda r, m=m: r[m]) for m in ("current_share_end", "completion_rate", "overload_share")}
        out[v]["cost_index"] = cost_index(cw, eff)
        out[v]["current_share_cw"] = level(cw, lambda r: r["current_share_end"])
    return out


def block_proposition(rows: list[dict]) -> dict:
    recs = [r["rev_counters"] for r in rows]
    return {"runs": len(recs),
            "max_planned_hours_over_cap": max(r["max_planned_hours_over_cap"] for r in recs),
            "max_total_hours_over_cap": max(r["max_total_hours_over_cap"] for r in recs),
            "min_machine_hours_left": min(r["min_machine_hours_left"] for r in recs)}


# ---------------------------------------------------------------------------

BLOCKS = ("replay", "add_one", "world", "restoration", "fresh", "lhs", "extra_oat")


def jobs_for(block: str) -> list:
    if block == "replay":
        return [(s, sc, p, "base") for s in SEEDS for sc in SC3 for p in (*REF_POLICIES, "efficiency_recency", EQR)]
    if block == "add_one":
        return [(s, sc, p, "base") for s in SEEDS for sc in SC2 for p in (*ADD_ONE, *DROP_ONE, "cw_nouncertainty")]
    if block == "world":
        jobs = []
        for v in WORLD_VARIANTS:
            for sc in (SC2 if v in WORLD_DISRUPTION else ("routine",)):
                jobs += [(s, sc, p, v) for s in SEEDS for p in ("civicworkos", "efficiency", EQR)]
            if v in WORLD_LOAD:
                jobs += [(s, "routine", "civicworkos_nolearn", v) for s in SEEDS]
        return jobs
    if block == "restoration":
        return [(s, "routine", p, v) for v in (*TRUTH_ONLY, *INFORMED) for s in SEEDS
                for p in ("civicworkos", "efficiency", EQR)]
    if block == "fresh":
        return [(s, sc, p, "base") for s in FRESH for sc in SC3 for p in (*REF_POLICIES, EQR)]
    if block == "lhs":
        return [(s, sc, p, f"lhs_{i}") for i in range(LHS_N) for s in LHS_SEEDS for sc in SC2
                for p in ("civicworkos", "efficiency", EQR)]
    if block == "extra_oat":
        return [(s, "routine", p, v) for v in EXTRA_OAT for s in SEEDS for p in ("civicworkos", "efficiency")]
    raise ValueError(block)


def main() -> int:
    ap = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    ap.add_argument("--blocks", nargs="+", choices=BLOCKS, default=list(BLOCKS))
    ap.add_argument("--out", default=str(ROOT / "results" / "revision"))
    ap.add_argument("--dest", default=str(ROOT / "reproducibility" / "data" / "revision.json"))
    ap.add_argument("--workers", type=int, default=None)
    ap.add_argument("--runs-only", action="store_true", help="run the blocks without writing the summary")
    a = ap.parse_args()
    out, dest = Path(a.out), Path(a.dest)
    log: dict = {}
    data = {b: run_block(b, jobs_for(b), out, a.workers, log) for b in a.blocks}
    if a.runs_only:
        return 0
    result: dict = json.loads(dest.read_text(encoding="utf-8")) if dest.exists() else {}
    result["label"] = LABEL
    if "replay" in data:
        R = data["replay"]
        result["replay_identity"] = block_replay(R)
        result["per_domain"] = block_domains(R)
        result["budget"] = block_budget(R)
        result["payroll"] = block_payroll(R)
        result["takeover"] = block_takeover(R)
        result["proposition_resources"] = block_proposition(R)
    replay = data.get("replay") or run_block("replay", jobs_for("replay"), out, a.workers, log)
    if "add_one" in data:
        result["add_one"] = block_add_one(data["add_one"], replay)
        result["uncertainty"] = block_uncertainty(data["add_one"], replay)
    if "world" in data:
        result["world"] = block_world(data["world"], replay)
    if "restoration" in data:
        result["restoration"] = block_restoration(data["restoration"], replay)
    if "fresh" in data:
        result["fresh_seeds"] = block_fresh(data["fresh"], replay)
    if "lhs" in data:
        result["lhs"] = block_lhs(data["lhs"])
    if "extra_oat" in data:
        result["extra_oat"] = block_extra(data["extra_oat"], replay)
    result["meta"] = {"code_sha256": code_sha(), "python": sys.version.split()[0], "numpy": np.__version__, "runs": log}
    dest.parent.mkdir(parents=True, exist_ok=True)
    dest.write_text(json.dumps(result, indent=2), encoding="utf-8")
    print(f"wrote {dest}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
