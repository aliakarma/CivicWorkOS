"""Statistical analysis of the reference execution.

Implements the decision rules fixed in ``configs/protocol/hypotheses.yaml``:
paired two-sided Wilcoxon signed-rank tests over seeds, Holm--Bonferroni
step-down control over the whole family, matched-pairs rank-biserial effect
sizes, and t-intervals for the non-inferiority hypotheses.
"""

from __future__ import annotations

import math
from collections import defaultdict

import numpy as np
from scipy import stats


def mean_ci(values: list[float], level: float = 0.95) -> tuple[float, float, float, int]:
    x = np.array([v for v in values if not (isinstance(v, float) and math.isnan(v))], dtype=float)
    n = len(x)
    if n == 0:
        return float("nan"), float("nan"), float("nan"), 0
    m = float(x.mean())
    if n < 2:
        return m, m, m, n
    half = float(stats.t.ppf(0.5 + level / 2, n - 1) * x.std(ddof=1) / math.sqrt(n))
    return m, m - half, m + half, n


def rank_biserial(diffs: np.ndarray) -> float:
    d = diffs[diffs != 0]
    if len(d) == 0:
        return 0.0
    ranks = stats.rankdata(np.abs(d))
    w_plus = ranks[d > 0].sum()
    w_minus = ranks[d < 0].sum()
    return float((w_plus - w_minus) / (w_plus + w_minus))


def wilcoxon_p(diffs: np.ndarray) -> float:
    if len(diffs) == 0 or np.all(diffs == 0):
        return 1.0
    return float(stats.wilcoxon(diffs, zero_method="wilcox", alternative="two-sided").pvalue)


def holm(pvalues: list[float]) -> list[float]:
    m = len(pvalues)
    order = sorted(range(m), key=lambda i: pvalues[i])
    adjusted = [0.0] * m
    running = 0.0
    for rank, i in enumerate(order):
        running = max(running, min(1.0, (m - rank) * pvalues[i]))
        adjusted[i] = running
    return adjusted


def index(rows: list[dict]) -> dict:
    """Map (scenario, policy) -> {seed: row}."""
    out: dict = defaultdict(dict)
    for r in rows:
        out[(r["scenario"], r["policy"])][r["seed"]] = r
    return out


def paired(idx: dict, scenario: str, a: str, b: str, metric: str, ratio: bool = False) -> np.ndarray:
    ra, rb = idx[(scenario, a)], idx[(scenario, b)]
    vals = []
    for seed in sorted(set(ra) & set(rb)):
        x, y = ra[seed][metric], rb[seed][metric]
        if any(isinstance(v, float) and math.isnan(v) for v in (x, y)):
            continue
        vals.append(x / y if ratio else x - y)
    return np.array(vals, dtype=float)


def evaluate(rows: list[dict], spec: dict) -> list[dict]:
    """Apply the pre-specified hypotheses; return one record per test."""
    idx = index(rows)
    alpha = float(spec.get("alpha", 0.05))
    tests = []
    for hid, h in spec["hypotheses"].items():
        scenarios = h["scenario"] if isinstance(h["scenario"], list) else [h["scenario"]]
        for scenario in scenarios:
            for comp in h["comparisons"]:
                direction = h["direction"]
                if h["metric"] == "cost_per_completed_ratio_to_efficiency":
                    ratios = paired(idx, scenario, "civicworkos", comp, "cost_per_completed", ratio=True)
                    diffs = ratios - 1.0
                    est, lo, hi, n = mean_ci(list(ratios))
                else:
                    diffs = paired(idx, scenario, "civicworkos", comp, h["metric"])
                    est, lo, hi, n = mean_ci(list(diffs))
                tests.append({
                    "id": hid, "scenario": scenario, "comparison": comp, "metric": h["metric"],
                    "direction": direction, "threshold": h.get("threshold"), "margin": h.get("margin"),
                    "n": n, "estimate": est, "ci_low": lo, "ci_high": hi,
                    "p": wilcoxon_p(diffs), "effect_r": rank_biserial(diffs),
                })
    adjusted = holm([t["p"] for t in tests])
    for t, p_adj in zip(tests, adjusted):
        t["p_holm"] = p_adj
        d, est = t["direction"], t["estimate"]
        if d == "noninferior_upper":
            t["supported"] = bool(t["ci_high"] <= t["margin"])
        elif d == "noninferior_lower":
            t["supported"] = bool(t["ci_low"] >= t["margin"])
        else:
            sign_ok = est > 0 if d == "greater" else est < 0
            thr = t["threshold"]
            thr_ok = thr is None or (abs(est) >= thr and sign_ok)
            t["supported"] = bool(p_adj < alpha and sign_ok and thr_ok)
    return tests


def summarize(rows: list[dict], metrics: list[str]) -> dict:
    idx = index(rows)
    out: dict = {}
    for (scenario, policy), by_seed in idx.items():
        recs = list(by_seed.values())
        out.setdefault(scenario, {})[policy] = {
            m: dict(zip(("mean", "ci_low", "ci_high", "n"), mean_ci([r[m] for r in recs]))) for m in metrics
        }
        eff = idx.get((scenario, "efficiency"), {})
        ratios = [by_seed[s]["cost_per_completed"] / eff[s]["cost_per_completed"] for s in by_seed if s in eff]
        out[scenario][policy]["cost_index"] = dict(zip(("mean", "ci_low", "ci_high", "n"),
                                                       mean_ci([100.0 * r for r in ratios])))
    return out
