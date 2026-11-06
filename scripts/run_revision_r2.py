"""Exploratory analyses added in the second review round (NOT part of the pre-specified family).

    python scripts/run_revision_r2.py

Definitions: ``configs/protocol/exploratory_r2.yaml``. Per-run records go to
``results/revision_r2/runs.jsonl`` and the summary to
``reproducibility/data/revision_r2.json``. The new policy variant is registered
here at import time, so ``sim/protocol`` and the stored reference and round-1
records are unchanged.
"""

from __future__ import annotations

import json
import sys
import time
from concurrent.futures import ProcessPoolExecutor
from dataclasses import replace
from pathlib import Path

import numpy as np

ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT))
sys.path.insert(0, str(ROOT / "scripts"))

import run_revision as RV  # noqa: E402

from sim.protocol import config as C  # noqa: E402
from sim.protocol import engine as E  # noqa: E402
from sim.protocol.config import DOMAINS, RunConfig, SimParams, WorldModel  # noqa: E402

# R1 round 2, comment 2: the workload ceiling and the budget stage together on Efficiency + quota + recency.
NEW = "eqr_ceiling_budget"
C.EXPLORATORY_POLICY_FLAGS[NEW] = replace(C.EXPLORATORY_POLICY_FLAGS["efficiency_quota_recency"], workload_guard=True)
E.TRAINEE_QUOTA_ADD_ONE = E.TRAINEE_QUOTA_ADD_ONE | {NEW}
E.BUDGET_STAGE_ON = E.BUDGET_STAGE_ON | {NEW}

SEEDS = RV.SEEDS
LED = ("led_true_0.60", "led_true_0.70")
# R1 round 2, comment 1: which rule makes the recency baseline fall below Efficiency.
LED_POLICIES = ("efficiency_recency", "efficiency_quota", "cw_nobudget")
SWEEP_POLICIES = ("civicworkos", "efficiency", RV.EQR)


def _reference_values() -> dict[str, float]:
    base, world = SimParams(), WorldModel()
    ref = {k: getattr(base, k) for k in RV.LHS_BOUNDS if hasattr(base, k)}
    ref.update(variance_scale=1.0, hybrid_phi_shift=0.0, machine_price_mult=1.0,
               attrition=DOMAINS[0].attrition_per_year, supervision_recovery=world.supervision_recovery)
    assert all(d.attrition_per_year == ref["attrition"] for d in DOMAINS)
    return ref


SWEEP_POINTS = {"sweep_reference": _reference_values(),
                "sweep_center": {k: 0.5 * (lo + hi) for k, (lo, hi) in RV.LHS_BOUNDS.items()}}


def config(variant: str) -> RunConfig:
    if variant in SWEEP_POINTS:
        return RV.lhs_config(SWEEP_POINTS[variant])
    return RV.config(variant)


def _job(args):
    seed, scenario, policy, variant = args
    r = E.run_one(seed, scenario, policy, config(variant), revision=True)
    r.pop("trajectory")
    r["variant"] = variant
    return r


def jobs() -> list:
    j = [(s, sc, NEW, "base") for s in SEEDS for sc in RV.SC2]
    j += [(s, "routine", p, v) for v in LED for p in LED_POLICIES for s in SEEDS]
    j += [(s, "routine", p, v) for v in SWEEP_POINTS for p in SWEEP_POLICIES for s in RV.LHS_SEEDS]
    return j


def routine_hazard(r: dict, h_def: float) -> float:
    """Incidents per 1,000 arrived routine tasks when every missed task carries h_def per unit of risk."""
    arrived, done = RV._rc(r, "arrived"), RV._rc(r, "completed")
    return 1000.0 * (RV._rc(r, "incidents").sum() + h_def * float((RV.RISK * (arrived - done)).sum())) / arrived.sum()


def _load(block: str) -> list[dict]:
    return [json.loads(line) for line in open(ROOT / "results" / "revision" / block / "runs.jsonl", encoding="utf-8")]


def summarize(rows: list[dict], replay: list[dict]) -> dict:
    out: dict = {"label": "added in round 2 of review; exploratory (configs/protocol/exploratory_r2.yaml)"}
    # comment 2: every add-one variant, the new pair, and CivicWorkOS, on one footing
    add = _load("add_one")
    table: dict = {}
    for sc in RV.SC2:
        eff = RV.by_seed(replay, sc, "efficiency")
        base = RV.by_seed(replay, sc, RV.EQR)
        src = {"efficiency": (replay, "efficiency"), "eqr": (replay, RV.EQR), "civicworkos": (replay, "civicworkos"),
               **{p: (add, p) for p in RV.ADD_ONE}, NEW: (rows, NEW)}
        res = {}
        for name, (pool, p) in src.items():
            recs = RV.by_seed(pool, sc, p)
            lv = RV.policy_levels(recs, eff, sc)
            lv["fixed_payroll_index"] = RV.cost_index(recs, eff, RV.payroll_per_completed)
            if name not in ("efficiency", "eqr"):
                lv["minus_eqr"] = {m: RV.contrast(recs, base, lambda r, m=m: r[m])
                                   for m in ("overload_share", "graduations", "current_share_end", "completion_rate")}
            res[name] = lv
        cw = RV.by_seed(replay, sc, "civicworkos")
        pair = RV.by_seed(rows, sc, NEW)
        allfive = RV.by_seed(add, sc, "eqr_all")
        ms = RV.METRICS + (RV.WINDOW_METRICS if sc != "routine" else ())
        res["civicworkos_minus_pair"] = {m: RV.contrast(cw, pair, lambda r, m=m: r[m]) for m in ms}
        res["civicworkos_minus_all_five"] = {m: RV.contrast(cw, allfive, lambda r, m=m: r[m]) for m in ms}
        table[sc] = res
    out["add_one_table"] = table
    # comment 1: which rule drives the reversal under a stricter restoration threshold
    restor = _load("restoration")
    led: dict = {}
    for v in LED:
        eff = RV.by_seed(restor, "routine", "efficiency", v)
        row = {}
        for p, pool in (("efficiency", restor), (RV.EQR, restor), ("civicworkos", restor),
                        *((q, rows) for q in LED_POLICIES)):
            recs = RV.by_seed(pool, "routine", p, v)
            row[p] = {m: RV.level(recs, lambda r, m=m: r[m])
                      for m in ("current_share_end", "graduations", "completion_rate")}
            if p != "efficiency":
                row[p]["minus_efficiency_share"] = RV.contrast(recs, eff, lambda r: r["current_share_end"])
        led[v] = row
    out["restoration_by_rule"] = led
    # comment 3: the sweep at the reference point and at the center of the hypercube
    pts: dict = {}
    for v in SWEEP_POINTS:
        recs = {p: RV.by_seed(rows, "routine", p, v) for p in SWEEP_POLICIES}
        pts[v] = {p: {m: RV.level(recs[p], lambda r, m=m: r[m])
                      for m in ("completion_rate", "current_share_end", "overload_share")} for p in SWEEP_POLICIES}
        pts[v]["completion_minus_efficiency"] = RV.contrast(recs["civicworkos"], recs["efficiency"],
                                                            lambda r: r["completion_rate"])
        pts[v]["completion_minus_eqr"] = RV.contrast(recs["civicworkos"], recs[RV.EQR], lambda r: r["completion_rate"])
    pts["values"] = SWEEP_POINTS
    per: dict = {}
    for r in _load("lhs"):
        if r["scenario"] == "routine":
            per.setdefault((r["variant"], r["policy"]), []).append(r["completion_rate"])
    diffs = np.array([100 * (np.mean(per[(f"lhs_{i}", "civicworkos")]) - np.mean(per[(f"lhs_{i}", "efficiency")]))
                      for i in range(RV.LHS_N)])
    ref_cw, ref_eff = (RV.by_seed(replay, "routine", p) for p in ("civicworkos", "efficiency"))
    ref_diff = 100 * RV.contrast(ref_cw, ref_eff, lambda r: r["completion_rate"])["diff"]
    pts["draws_completion_minus_efficiency"] = sorted(float(x) for x in diffs)
    pts["share_of_draws_milder_than_reference"] = float(np.mean(diffs > ref_diff))
    pts["reference_30_seeds_points"] = float(ref_diff)
    out["sweep_points"] = pts
    # comment 4: missed routine tasks given a hazard
    hz: dict = {}
    recs = {p: RV.by_seed(replay, "routine", p) for p in ("civicworkos", "efficiency", RV.EQR)}
    for h in (0.0, 0.03, 0.05, 0.10, 0.15):
        hz[str(h)] = {p: RV.level(recs[p], lambda r, h=h: routine_hazard(r, h)) for p in recs}
        hz[str(h)]["civicworkos_minus_efficiency"] = RV.contrast(recs["civicworkos"], recs["efficiency"],
                                                                 lambda r, h=h: routine_hazard(r, h))
    cw, eff = recs["civicworkos"], recs["efficiency"]
    d0 = np.mean([routine_hazard(cw[s], 0.0) - routine_hazard(eff[s], 0.0) for s in cw])
    d1 = np.mean([routine_hazard(cw[s], 1.0) - routine_hazard(eff[s], 1.0) for s in cw])
    hz["h_def_where_equal_vs_efficiency"] = float(-d0 / (d1 - d0))
    hz["missed_inspections_per_year"] = {
        p: RV.level(recs[p], lambda r: float(RV._rc(r, "arrived")[0] - RV._rc(r, "completed")[0]) / 3.0)
        for p in recs}
    out["routine_deferral_hazard"] = hz
    return out


ROW_NAMES = (("efficiency", "Efficiency-focused"), ("eqr", "Efficiency + quota + recency (base)"),
             ("eqr_floor", "+ lower-bound safety floor"), ("eqr_gate", "+ oversight gate"),
             ("eqr_ceiling", "+ workload ceiling"), ("eqr_ready", "+ readiness-gated takeover"),
             ("eqr_budget", "+ budget stage"), (NEW, "+ ceiling and budget stage"), ("eqr_all", "+ all five"),
             ("civicworkos", "CivicWorkOS"))


def addone_rows(t: dict) -> str:
    """Body rows of the main-text add-one table (Table 11)."""
    lines = []
    for key, label in ROW_NAMES:
        r, w = t["routine"][key], t["disruption"][key]
        v = lambda d, m: d[m]["mean"]  # noqa: E731
        lines.append(f"{label} & {v(r, 'current_share_end'):.2f} & {v(r, 'graduations'):.1f} & "
                     f"{100 * v(r, 'overload_share'):.2f} & {100 * v(r, 'completion_rate'):.1f} & "
                     f"{v(r, 'cost_index'):.1f} & {v(r, 'fixed_payroll_index'):.1f} & "
                     f"{v(w, 'takeover_success_window'):.3f} & {v(w, 'incidents_per_1000_window'):.1f} & "
                     f"{100 * v(w, 'completion_rate_window'):.1f}" + r"\\")
        if key in ("eqr", "eqr_all"):
            lines.append(r"\midrule")
    return "\n".join(lines).replace("+ ", "${+}$ ") + "\n"


def main() -> int:
    out = ROOT / "results" / "revision_r2" / "runs.jsonl"
    dest = ROOT / "reproducibility" / "data" / "revision_r2.json"
    if out.exists():
        rows = [json.loads(line) for line in open(out, encoding="utf-8")]
    else:
        t0 = time.time()
        with ProcessPoolExecutor() as ex:
            rows = list(ex.map(_job, jobs(), chunksize=1))
        code = RV.code_sha()
        for r in rows:
            r["code_sha"] = code
        out.parent.mkdir(parents=True, exist_ok=True)
        with open(out, "w", encoding="utf-8") as f:
            for r in rows:
                f.write(json.dumps(r) + "\n")
        print(f"{len(rows)} runs in {time.time() - t0:.0f} s", flush=True)
    replay = _load("replay")
    res = summarize(rows, replay)
    # self-check: the sweep machinery at the reference point reproduces the reference runs of seeds 0-4
    ref = {(r["seed"], r["policy"]): r["completion_rate"] for r in rows if r["variant"] == "sweep_reference"}
    base = {(r["seed"], r["policy"]): r["completion_rate"] for r in replay
            if r["scenario"] == "routine" and r["seed"] in RV.LHS_SEEDS and r["policy"] in SWEEP_POLICIES}
    res["sweep_points"]["reference_reproduces_replay"] = all(abs(ref[k] - base[k]) < 1e-12 for k in ref)
    dest.write_text(json.dumps(res, indent=2), encoding="utf-8")
    gen = ROOT / "reproducibility" / "generated" / "rev_r2_addone.tex"
    gen.write_text(addone_rows(res["add_one_table"]), encoding="utf-8")
    print(f"wrote {gen}")
    print(f"wrote {dest}; reference reproduces replay: {res['sweep_points']['reference_reproduces_replay']}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
