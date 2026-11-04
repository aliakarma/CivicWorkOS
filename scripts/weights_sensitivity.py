"""How much the worked allocation depends on the objective weights (added in revision).

    python scripts/weights_sensitivity.py

Exact arithmetic on Table tab:worked-terms: for each weight vector, the
unconstrained winner among the modes that pass the safety floor and the exact
optimum of the budget-constrained linear program (the best single mode or
two-mode mix reaching the required mean credited share). Weights are drawn from
Dirichlet distributions centered on the defaults, from the uniform distribution
on the simplex, and from named alternatives. Nothing here is a measurement of
stakeholder preference. Writes reproducibility/data/weights_sensitivity.json.
"""

from __future__ import annotations

import json
import sys
from pathlib import Path

import numpy as np

ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT))

from manuscript_values import MODES, WORKED  # noqa: E402

FLOWS = ("Q", "S", "P", "Eq", "Tr")
PENALTIES = ("Cost", "En", "Pr")
W_NAMES = (*FLOWS, *PENALTIES, "CAD")
W_DEFAULT = np.array([0.15, 0.18, 0.14, 0.10, 0.05, 0.08, 0.03, 0.05, 0.22])
D_DEFAULT = np.array([0.28, 0.22, 0.18, 0.12, 0.20])
ADMISSIBLE = ("H+R/a0", "H+R/a1", "H+A+R/a0", "H+A+R/a1")
N_DRAWS = 100_000


def roc(order: np.ndarray) -> np.ndarray:
    """Rank-order centroid weights for the given ranks (ties share their centroids' mean)."""
    n = len(order)
    centroid = np.array([sum(1.0 / k for k in range(i + 1, n + 1)) / n for i in range(n)])
    out = np.zeros(n)
    for value in np.unique(order):
        idx = np.where(order == value)[0]
        rank_positions = np.where(np.sort(order)[::-1] == value)[0]
        out[idx] = centroid[rank_positions].mean()
    return out


def scv(mode, w: np.ndarray, d: np.ndarray) -> float:
    debt = d @ np.array([mode.D_skill, mode.D_fall, mode.D_acct, mode.D_dep, mode.D_trans])
    flows = sum(w[i] * getattr(mode, name) for i, name in enumerate(FLOWS))
    penalties = sum(w[5 + i] * getattr(mode, name) for i, name in enumerate(PENALTIES))
    return float(flows - penalties - w[8] * debt)


def solve(w: np.ndarray, d: np.ndarray, required: float) -> dict:
    """Exact optimum over single modes and two-mode mixes: a vertex has at most two active modes."""
    modes = [MODES[n] for n in ADMISSIBLE]
    values = [scv(m, w, d) for m in modes]
    credit = [m.credited for m in modes]
    best = (-np.inf, None, None, None)
    for i in range(4):
        if credit[i] >= required and values[i] > best[0]:
            best = (values[i], i, i, 1.0)
        for j in range(4):
            if credit[i] > required > credit[j]:
                share = (required - credit[j]) / (credit[i] - credit[j])
                v = share * values[i] + (1.0 - share) * values[j]
                if v > best[0]:
                    best = (v, i, j, share)
    value, i, j, share = best
    top = int(np.argmax(values))
    a1_share = (share if ADMISSIBLE[i].endswith("a1") else 0.0) + ((1.0 - share) if ADMISSIBLE[j].endswith("a1") else 0.0)
    hr_share = (share if ADMISSIBLE[i].startswith("H+R") else 0.0) + ((1.0 - share) if ADMISSIBLE[j].startswith("H+R") else 0.0)
    return {"unconstrained": ADMISSIBLE[top], "unconstrained_value": values[top], "optimum_value": float(value),
            "optimum": sorted({ADMISSIBLE[i], ADMISSIBLE[j]}), "a1_share": a1_share, "hr_share": hr_share,
            "cost_percent": 100.0 * (values[top] - value) / abs(values[top])}


def summarize(results: list[dict]) -> dict:
    cost = np.array([r["cost_percent"] for r in results])
    a1 = np.array([r["a1_share"] for r in results])
    hr = np.array([r["hr_share"] for r in results])
    return {"n": len(results),
            "unconstrained_winner_shares": {m: float(np.mean([r["unconstrained"] == m for r in results])) for m in ADMISSIBLE},
            "share_unconstrained_lead_only": float(np.mean([r["unconstrained"].endswith("a0") for r in results])),
            "share_baseline_mix": float(np.mean([r["optimum"] == ["H+A+R/a1", "H+R/a1"] for r in results])),
            "a1_share_min": float(a1.min()), "a1_share_median": float(np.median(a1)),
            "hr_share_median": float(np.median(hr)),
            "cost_percent": {"p2.5": float(np.percentile(cost, 2.5)), "median": float(np.median(cost)),
                             "p97.5": float(np.percentile(cost, 97.5)), "max": float(cost.max())}}


def main() -> int:
    bk = max(WORKED["B_min"], WORKED["eta_k"] * WORKED["N_k"] * WORKED["r_k"] * WORKED["h_k"])
    required = bk / WORKED["Phi_k"]
    rng = np.random.default_rng([0, 7919, 105])
    out: dict = {"label": "added in revision; exact arithmetic on the worked allocation",
                 "required_credited_share": required, "n_draws": N_DRAWS, "named": {}, "distributions": {}}
    named = {
        "default": (W_DEFAULT, D_DEFAULT),
        "equal": (np.full(9, 1 / 9), np.full(5, 0.2)),
        "rank_order_centroid": (roc(W_DEFAULT), roc(D_DEFAULT)),
        "debt_free": (np.append(W_DEFAULT[:8] / W_DEFAULT[:8].sum(), 0.0), D_DEFAULT),
        "safety_doubled": (np.array([0.15, 0.36, 0.14, 0.10, 0.05, 0.08, 0.03, 0.05, 0.22]) / 1.18, D_DEFAULT),
        "cost_doubled": (np.array([0.15, 0.18, 0.14, 0.10, 0.05, 0.16, 0.03, 0.05, 0.22]) / 1.08, D_DEFAULT),
    }
    for name, (w, d) in named.items():
        out["named"][name] = {"weights": dict(zip(W_NAMES, map(float, w))), **solve(w, d, required)}
    for label, c in (("dirichlet_c20", 20.0), ("dirichlet_c50", 50.0), ("uniform_simplex", None)):
        if c is None:
            ws = rng.dirichlet(np.ones(9), N_DRAWS)
            ds = rng.dirichlet(np.ones(5), N_DRAWS)
        else:
            ws = rng.dirichlet(c * W_DEFAULT, N_DRAWS)
            ds = rng.dirichlet(c * D_DEFAULT, N_DRAWS)
        out["distributions"][label] = summarize([solve(w, d, required) for w, d in zip(ws, ds)])
    # the floor on a1 follows from the constraint alone, whatever the weights
    out["a1_share_lower_bound_from_constraint"] = required / max(MODES[n].credited for n in ADMISSIBLE)
    assert abs(solve(W_DEFAULT, D_DEFAULT, required)["optimum_value"] - 0.327750) < 1e-5   # the printed LP value
    dest = ROOT / "reproducibility" / "data" / "weights_sensitivity.json"
    dest.write_text(json.dumps(out, indent=2), encoding="utf-8")
    print(json.dumps({k: out[k] for k in ("required_credited_share", "a1_share_lower_bound_from_constraint")}))
    print(json.dumps(out["named"], indent=1)[:2600])
    print(json.dumps(out["distributions"], indent=1))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
