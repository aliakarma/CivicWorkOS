"""Execute the CivicWorkOS evaluation protocol on the synthetic testbed.

    python scripts/run_protocol.py                    # reporting seeds 0-29
    python scripts/run_protocol.py --seeds 1000 1009  # development seeds
    python scripts/run_protocol.py --workers 8 --out results/protocol

Writes, under ``--out``:
  runs.jsonl          one record per (seed, scenario, policy)
  config.json         the resolved parameters of the execution
  summary.json        means and 95% intervals per scenario and policy
  hypotheses.json     the pre-specified tests and their verdicts
  trajectory_*.dat    seed-averaged capability trajectories (pgfplots input)

Pass ``--paper`` to also copy the summary, verdicts and trajectories into
``Paper/Frontiers/data/``, from which the article's tables and figure are
built and against which ``Paper/Frontiers/audit_numbers.py`` checks every
reported value.
"""

from __future__ import annotations

import argparse
import json
import shutil
import sys
import time
from concurrent.futures import ProcessPoolExecutor
from pathlib import Path

import numpy as np
import yaml

ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT))

from sim.protocol.analysis import evaluate, summarize  # noqa: E402
from sim.protocol.config import POLICIES, SCENARIOS, RunConfig  # noqa: E402
from sim.protocol.engine import run_one  # noqa: E402

METRICS = [
    "completion_rate", "completion_rate_window", "cost_per_completed", "overload_share", "mean_workload",
    "certified_end", "current_end", "current_share_end", "mean_proficiency_end",
    "takeover_requests", "takeover_success_rate", "takeover_success_window", "takeover_requests_window",
    "takeover_time_mean", "mrc", "incidents_per_1000", "incidents_per_1000_window",
    "trainee_credit_per_year", "graduations",
    "proficiency_mae_end", "machine_mae", "machine_mae_window",
]


def _job(args: tuple[int, str, str]) -> dict:
    return run_one(*args)


def main() -> int:
    ap = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    ap.add_argument("--seeds", nargs=2, type=int, default=[0, 29], metavar=("FIRST", "LAST"))
    ap.add_argument("--workers", type=int, default=None)
    ap.add_argument("--out", default=str(ROOT / "results" / "protocol"))
    ap.add_argument("--paper", action="store_true", help="copy outputs into Paper/Frontiers/data/")
    ap.add_argument("--from-runs", action="store_true",
                    help="rebuild summary.json and hypotheses.json from an existing runs.jsonl without simulating")
    a = ap.parse_args()

    out = Path(a.out)
    out.mkdir(parents=True, exist_ok=True)
    trajectories: dict = {}
    if a.from_runs:
        rows = [json.loads(line) for line in open(out / "runs.jsonl", encoding="utf-8")]
        elapsed = json.loads((out / "config.json").read_text(encoding="utf-8")).get("wall_seconds", 0.0)
    else:
        jobs = [(s, sc, p) for s in range(a.seeds[0], a.seeds[1] + 1) for sc in SCENARIOS for p in POLICIES]
        t0 = time.time()
        with ProcessPoolExecutor(max_workers=a.workers) as ex:
            rows = list(ex.map(_job, jobs, chunksize=1))
        elapsed = time.time() - t0
        trajectories = {(r["scenario"], r["policy"]): [] for r in rows}
        with open(out / "runs.jsonl", "w", encoding="utf-8") as f:
            for r in rows:
                trajectories[(r["scenario"], r["policy"])].append(r.pop("trajectory"))
                f.write(json.dumps(r) + "\n")
        cfg = RunConfig().as_dict()
        cfg["seeds"] = a.seeds
        cfg["runs"] = len(rows)
        cfg["wall_seconds"] = round(elapsed, 1)
        (out / "config.json").write_text(json.dumps(cfg, indent=2), encoding="utf-8")

    summary = summarize(rows, METRICS)
    (out / "summary.json").write_text(json.dumps(summary, indent=2), encoding="utf-8")
    spec = yaml.safe_load((ROOT / "configs" / "protocol" / "hypotheses.yaml").read_text(encoding="utf-8"))
    tests = evaluate(rows, spec)
    (out / "hypotheses.json").write_text(json.dumps(tests, indent=2), encoding="utf-8")

    for scenario in ("routine", "disruption") if trajectories else ():
        cols = []
        for policy in POLICIES:
            arr = np.array(trajectories[(scenario, policy)], dtype=float)   # seeds x points x 4
            cols.append(arr.mean(axis=0))
        days = cols[0][:, 0]
        with open(out / f"trajectory_{scenario}.dat", "w", encoding="utf-8") as f:
            f.write("day " + " ".join(f"{p}_cert {p}_curr" for p in POLICIES) + "\n")
            for i, d in enumerate(days):
                f.write(f"{int(d)} " + " ".join(f"{c[i, 1]:.3f} {c[i, 2]:.3f}" for c in cols) + "\n")

    print(f"{len(rows)} runs in {elapsed:.0f} s -> {out}")
    for t in tests:
        verdict = "SUPPORTED" if t["supported"] else "not supported"
        print(f"{t['id']} {t['scenario']:<10} vs {t['comparison']:<24} est={t['estimate']:+.4f} "
              f"[{t['ci_low']:+.4f},{t['ci_high']:+.4f}] p_holm={t['p_holm']:.2e} r={t['effect_r']:+.2f} {verdict}")

    if a.paper:
        dest = ROOT / "Paper" / "Frontiers" / "data"
        dest.mkdir(parents=True, exist_ok=True)
        for name in ("summary.json", "hypotheses.json", "config.json",
                     "trajectory_routine.dat", "trajectory_disruption.dat"):
            shutil.copy(out / name, dest / name)
        print(f"copied outputs to {dest}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
