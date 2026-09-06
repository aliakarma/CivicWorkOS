#!/usr/bin/env python
"""Parameter-sensitivity sweep of the unconstrained SCV argmax (report
Sec. 16.2 recommendation M1; targets Paper Sec. 7.2's open question 3:
"whether the parameter set admits any stable configuration, or whether
[the argmax] is so sensitive to small perturbations that a panel's
deliberation is effectively arbitrary").

Perturbs w1..w9 by +/-`--pct` percent (relative, then renormalized to
sum to 1) via Latin-hypercube-style random sampling, and reports the
fraction of a fixed candidate set whose argmax mode changes relative to
the paper's default weights.

This is REPORT SEC. 22's proposed experiment E1, run here at reduced
scale as a demonstration of the harness, not as the full pre-registered
study the paper's own Sec. 6 never conducted. Nothing this script prints
should be read as a claim about the real framework's stability -- only
about the stability of the worked example's four Table 3 candidates
under this specific perturbation scheme.

Usage:
    python scripts/sensitivity_sweep.py [n_samples] [pct]
"""

from __future__ import annotations

import random
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "src"))

from civicworkos.scoring.cad import DebtComponents, DebtWeights, civic_automation_debt
from civicworkos.scoring.scv import ScoreWeights, TermVector, sustainable_civic_value

_TABLE3 = {
    "H": dict(Q=0.72, S=0.55, P=0.40, Eq_srv=0.70, Tr=0.80, Cost=0.85, En=0.20, Pr=0.10,
              D=(0.00, 0.00, 0.00, 0.00, 0.00)),
    "H+A": dict(Q=0.86, S=0.60, P=0.62, Eq_srv=0.72, Tr=0.74, Cost=0.62, En=0.28, Pr=0.25,
                D=(0.25, 0.15, 0.07, 0.30, 0.10)),
    "H+R": dict(Q=0.80, S=0.88, P=0.70, Eq_srv=0.70, Tr=0.72, Cost=0.58, En=0.55, Pr=0.30,
                D=(0.30, 0.25, 0.05, 0.35, 0.20)),
    "H+A+R": dict(Q=0.91, S=0.90, P=0.88, Eq_srv=0.74, Tr=0.68, Cost=0.50, En=0.60, Pr=0.38,
                  D=(0.45, 0.35, 0.13, 0.50, 0.30)),
}


def _perturb_weights(base: tuple[float, ...], pct: float, rng: random.Random) -> tuple[float, ...]:
    perturbed = [max(1e-6, w * (1.0 + rng.uniform(-pct, pct))) for w in base]
    total = sum(perturbed)
    return tuple(w / total for w in perturbed)


def _argmax_mode(score_weights: ScoreWeights, debt_weights: DebtWeights) -> str:
    best_mode, best_scv = None, float("-inf")
    for mode, row in _TABLE3.items():
        dc = DebtComponents(D_skill=row["D"][0], D_fall=row["D"][1], D_acct=row["D"][2],
                             D_dep=row["D"][3], D_trans=row["D"][4])
        cad = civic_automation_debt(dc, debt_weights)
        tv = TermVector(Q=row["Q"], S=row["S"], P=row["P"], Eq_srv=row["Eq_srv"], Tr=row["Tr"],
                         Cost=row["Cost"], En=row["En"], Pr=row["Pr"])
        scv = sustainable_civic_value(tv, cad, score_weights)
        if scv > best_scv:
            best_mode, best_scv = mode, scv
    return best_mode


def main() -> int:
    n_samples = int(sys.argv[1]) if len(sys.argv) > 1 else 2000
    pct = float(sys.argv[2]) if len(sys.argv) > 2 else 0.20

    rng = random.Random(1234)
    default_sw = ScoreWeights.paper_default()
    default_dw = DebtWeights.paper_default()
    baseline_mode = _argmax_mode(default_sw, default_dw)

    flips = 0
    mode_counts: dict[str, int] = {}
    sw_base = default_sw.as_tuple()
    dw_base = default_dw.as_tuple()

    for _ in range(n_samples):
        sw_sample = _perturb_weights(sw_base, pct, rng)
        dw_sample = _perturb_weights(dw_base, pct, rng)
        sw = ScoreWeights(*sw_sample)
        dw = DebtWeights(*dw_sample)
        mode = _argmax_mode(sw, dw)
        mode_counts[mode] = mode_counts.get(mode, 0) + 1
        if mode != baseline_mode:
            flips += 1

    print(f"Baseline (default weights) argmax: {baseline_mode}")
    print(f"Perturbation: +/-{pct*100:.0f}% relative on each weight, renormalized, n={n_samples}")
    print(f"Argmax-flip rate vs. baseline: {flips / n_samples:.4f}")
    print("Mode distribution under perturbation:")
    for mode, count in sorted(mode_counts.items(), key=lambda kv: -kv[1]):
        print(f"  {mode:10s} {count / n_samples:.4f}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
