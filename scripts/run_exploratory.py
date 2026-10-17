"""Exploratory analyses added in revision (NOT part of the pre-specified family).

    python scripts/run_exploratory.py            # writes results/exploratory/ and Paper/Frontiers/data/exploratory.json

1. Multimodal-channel ablation: CivicWorkOS learning from task outcomes only
   (skill probes, fleet telemetry and physiological workload readings removed),
   all three scenarios, paired with the stored reporting runs of CivicWorkOS.
2. Sensitivity of the CivicWorkOS-versus-efficiency contrast to the retention
   time constant (tau_ret x0.5 and x2) and to machine prices (x3), routine
   operations.

All use the reporting seeds 0-29 so that comparisons are paired; none enters
the Holm family of configs/protocol/hypotheses.yaml, and the article labels
every result from this script as exploratory.
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

from sim.protocol.analysis import mean_ci, rank_biserial, wilcoxon_p  # noqa: E402
from sim.protocol.config import DOMAINS, RunConfig, SimParams  # noqa: E402
from sim.protocol.engine import run_one  # noqa: E402

SEEDS = range(0, 30)
METRICS = ["completion_rate", "completion_rate_window", "cost_per_completed", "overload_share",
           "current_end", "current_share_end", "certified_end", "takeover_success_window",
           "incidents_per_1000_window", "proficiency_mae_end", "machine_mae", "machine_mae_window"]


def config(variant: str) -> RunConfig:
    if variant == "base":
        return RunConfig()
    if variant == "tau_half":
        return RunConfig(params=replace(SimParams(), tau_ret=60.0))
    if variant == "tau_double":
        return RunConfig(params=replace(SimParams(), tau_ret=240.0))
    if variant == "machine_price_x3":
        return RunConfig(domains=tuple(replace(d, machine_cost_per_h=3 * d.machine_cost_per_h) for d in DOMAINS))
    raise ValueError(variant)


def _job(args):
    seed, scenario, policy, variant = args
    r = run_one(seed, scenario, policy, config(variant))
    r.pop("trajectory")
    r["variant"] = variant
    return r


def main() -> int:
    jobs = [(s, sc, "civicworkos_outcomeonly", "base") for s in SEEDS for sc in ("routine", "surge", "disruption")]
    for variant in ("tau_half", "tau_double", "machine_price_x3"):
        jobs += [(s, "routine", p, variant) for s in SEEDS for p in ("efficiency", "civicworkos")]
    t0 = time.time()
    with ProcessPoolExecutor() as ex:
        rows = list(ex.map(_job, jobs, chunksize=1))
    out = ROOT / "results" / "exploratory"
    out.mkdir(parents=True, exist_ok=True)
    with open(out / "runs.jsonl", "w", encoding="utf-8") as f:
        for r in rows:
            f.write(json.dumps(r) + "\n")

    stored = {}
    for line in open(ROOT / "results" / "protocol" / "runs.jsonl", encoding="utf-8"):
        r = json.loads(line)
        stored[(r["seed"], r["scenario"], r["policy"], "base")] = r
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
    text = json.dumps(result, indent=2)
    (out / "exploratory.json").write_text(text, encoding="utf-8")
    (ROOT / "Paper" / "Frontiers" / "data" / "exploratory.json").write_text(text, encoding="utf-8")
    print(f"{len(rows)} runs in {time.time() - t0:.0f} s")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
