#!/usr/bin/env python
"""Analyse round-two elicitation ratings (App. S4) and re-run the worked example.

    python elicitation/analyze.py ratings.csv --out elicitation/out

Input is the long-format CSV described in `packet/data-format.md`. The first
non-blank lines are header comments, and two are mandatory:

    # provenance: real            (or: synthetic)
    # ethics-approval: <reference issued by the approving committee>

What this script refuses, and why
---------------------------------
* A file with no ``provenance`` line, or no ``ethics-approval`` line when the
  provenance is ``real``. The protocol (`app:elicit-ethics`) forbids collection
  without approval; the analysis should not be able to launder data that lacked
  it.
* ``provenance: synthetic`` unless ``--allow-synthetic`` is given. The pipeline
  is tested on synthetic ratings (see `tests/test_pipeline.py`), and synthetic
  ratings are never a result. A permitted synthetic run writes every output
  under a ``SYNTHETIC-`` prefix and starts each LaTeX fragment with a
  ``\\PackageError``, so including one in the manuscript breaks the build.
  This is the guard against reintroducing defect C1.

What it computes
----------------
Per parameter, from round-two ratings: the point value, ICC(2,k) with a
target-bootstrap interval, the protocol's decision (point value if
ICC(2,k) >= 0.75, otherwise a range), a rater-bootstrap 95% interval, and group
means for the three rater groups. Then the worked example is re-solved
(`model.py`) at the elicited values beside the estimated ones, one parameter at
a time, and jointly under a stratified rater bootstrap.
"""

from __future__ import annotations

import argparse
import csv
import json
import sys
from collections import defaultdict
from pathlib import Path

import numpy as np

_HERE = Path(__file__).resolve().parent
if str(_HERE) not in sys.path:
    sys.path.insert(0, str(_HERE))

import icc as icc_mod  # noqa: E402
from model import Inputs, psi_from_ratio, solve  # noqa: E402

SCALE = 10.0                      # eleven-point anchored scale, 0..10
GROUPS = ("competent", "developing", "supervisor")
HYBRID = ("H+A", "H+R", "H+A+R")
PARAMS = ("learn", "phi", "psi_ratio", "h_raw_doc", "h_raw_prac")

# The article's own estimates (tab:worked-terms, sec:workedsetup): the "estimated"
# column. Read from the model baseline rather than restated.
BASE = solve()


class DataError(Exception):
    pass


# --------------------------------------------------------------------------
# Loading and validation
# --------------------------------------------------------------------------

def read_ratings(path: Path, allow_synthetic: bool):
    headers, body = {}, []
    with open(path, newline="", encoding="utf-8") as fh:
        for line in fh:
            if line.lstrip().startswith("#"):
                key, _, val = line.lstrip()[1:].partition(":")
                headers[key.strip().lower()] = val.strip()
            elif line.strip():
                body.append(line)
    prov = headers.get("provenance", "").lower()
    if prov not in ("real", "synthetic"):
        raise DataError("missing '# provenance: real|synthetic' header")
    if prov == "synthetic" and not allow_synthetic:
        raise DataError("synthetic ratings are never a result; pass "
                        "--allow-synthetic to exercise the pipeline")
    if prov == "real" and not headers.get("ethics-approval"):
        raise DataError("real ratings need '# ethics-approval: <reference>' "
                        "(app:elicit-ethics forbids collection without it)")
    rows = list(csv.DictReader(body))
    need = {"rater_id", "group", "round", "parameter", "item_id", "value"}
    if not rows or need - set(rows[0]):
        raise DataError(f"columns required: {sorted(need)}")
    clean = []
    for i, r in enumerate(rows, start=2):
        if r["parameter"] not in PARAMS:
            raise DataError(f"line {i}: unknown parameter {r['parameter']!r}")
        if r["group"] not in GROUPS:
            raise DataError(f"line {i}: unknown group {r['group']!r}")
        if r["round"] not in ("1", "2"):
            raise DataError(f"line {i}: round must be 1 or 2")
        try:
            v = float(r["value"])
        except ValueError:
            raise DataError(f"line {i}: value {r['value']!r} is not a number")
        p = r["parameter"]
        if p in ("learn", "phi") and not (0.0 <= v <= SCALE):
            raise DataError(f"line {i}: {p} rating {v} outside 0..{SCALE:g}")
        if p == "psi_ratio" and v < 0:
            raise DataError(f"line {i}: supervision ratio cannot be negative")
        if p.startswith("h_raw") and v <= 0:
            raise DataError(f"line {i}: hours must be positive")
        if p == "phi" and r["item_id"].split("|")[0] not in HYBRID:
            raise DataError(f"line {i}: phi item must be '<mode>|<task>' with "
                            f"mode in {HYBRID}")
        clean.append(dict(rater=r["rater_id"], group=r["group"],
                          round=int(r["round"]), p=p, item=r["item_id"], v=v))
    seen: dict[str, str] = {}
    for r in clean:
        if seen.setdefault(r["rater"], r["group"]) != r["group"]:
            raise DataError(f"rater {r['rater']} appears in two groups")
    return prov, headers, clean


def _table(rows, rnd):
    """{parameter: {rater: {item: value}}} for one round."""
    out = {p: defaultdict(dict) for p in PARAMS}
    for r in rows:
        if r["round"] == rnd:
            out[r["p"]][r["rater"]][r["item"]] = r["v"]
    return out


def _groups(rows):
    return {r["rater"]: r["group"] for r in rows}


def _matrix(tab_p, raters, items):
    m = np.full((len(items), len(raters)), np.nan)
    for j, rid in enumerate(raters):
        for i, it in enumerate(items):
            if it in tab_p.get(rid, {}):
                m[i, j] = tab_p[rid][it]
    return m


# --------------------------------------------------------------------------
# Aggregation: ratings -> model inputs
# --------------------------------------------------------------------------

def aggregate(tab, raters, worked_item):
    """Point values of the four judgment parameters from a (multi)set of raters.

    Rules, fixed in advance and stated in `packet/analysis-plan.md`:
      learn_i  mean over raters of the worked-task rating / 10
      phi_m    mean over raters and bank tasks of the rating / 10, per mode
      psi_a1   n/(n+1) at the mean elicited supervision ratio n
      h_raw_k  median over raters of the *practice* hours (the judgment)
    """
    def vals(p, pick=lambda it: True):
        return [v for rid in raters for it, v in tab[p].get(rid, {}).items()
                if pick(it)]

    out = {}
    lv = vals("learn", lambda it: it == worked_item)
    out["learn"] = np.mean(lv) / SCALE if lv else np.nan
    for mode in HYBRID:
        pv = vals("phi", lambda it, m=mode: it.split("|")[0] == m)
        out[f"phi_{mode}"] = np.mean(pv) / SCALE if pv else np.nan
    sv = vals("psi_ratio")
    out["psi_a1"] = psi_from_ratio(np.mean(sv)) if sv else np.nan
    hv = vals("h_raw_prac")
    out["h_raw"] = float(np.median(hv)) if hv else np.nan
    return out


def to_inputs(agg, only=None):
    """Model inputs from aggregate values; `only` restricts to some parameters."""
    use = lambda k: only is None or k in only
    phi = {m: agg[f"phi_{m}"] for m in HYBRID
           if use(f"phi_{m}") and np.isfinite(agg[f"phi_{m}"])}
    return Inputs.make(
        learn=agg["learn"] if use("learn") and np.isfinite(agg["learn"]) else None,
        h_raw=agg["h_raw"] if use("h_raw") and np.isfinite(agg["h_raw"]) else None,
        phi=phi,
        psi_a1=agg["psi_a1"] if use("psi_a1") and np.isfinite(agg["psi_a1"]) else None,
    )


def _summ(res):
    if not res.feasible:
        return dict(feasible=False, required_share=res.required_share,
                    zeta_bar=res.zeta_bar, B_k=res.B_k)
    return dict(feasible=True, lam=res.lam, cost=res.cost_of_preservation,
                lead_only=res.lead_only_share, phi_bar=res.phi_bar,
                tau=res.tau_k, n_hat=res.n_hat_k, B_k=res.B_k,
                required_share=res.required_share, zeta_bar=res.zeta_bar,
                mix=res.mix)


# --------------------------------------------------------------------------
# Analysis
# --------------------------------------------------------------------------

ESTIMATED = {"learn": 0.80, "phi_H+A": 0.75, "phi_H+R": 0.70,
             "phi_H+A+R": 0.55, "psi_a1": 0.50, "h_raw": 1800.0}
LABEL = {"learn": r"$learn_i$ (worked task)",
         "phi_H+A": r"$\phi_{H+A}$", "phi_H+R": r"$\phi_{H+R}$",
         "phi_H+A+R": r"$\phi_{H+A+R}$",
         "psi_a1": r"$\psi_{a_1}$", "h_raw": r"$h^{raw}_k$ (h)"}


def analyze(rows, worked_item, reps, seed):
    r1, r2 = _table(rows, 1), _table(rows, 2)
    gmap = _groups(rows)
    raters = sorted({r["rater"] for r in rows if r["round"] == 2})
    if len(raters) < 2:
        raise DataError("need round-two ratings from at least two raters")
    by_group = {g: [r for r in raters if gmap[r] == g] for g in GROUPS}

    # --- agreement ---
    def icc_for(tab, p, pick=None):
        items = sorted({it for rid in raters for it in tab[p].get(rid, {})
                        if pick is None or pick(it)})
        m = _matrix(tab[p], raters, items)
        keep = ~np.isnan(m).any(axis=1)
        dropped = int((~keep).sum())
        m = m[keep]
        if m.shape[0] < 3 or m.shape[1] < 2:
            return dict(icc=None, lo=None, hi=None, n_items=int(m.shape[0]),
                        dropped=dropped, note="ICC needs >=3 complete targets")
        v = icc_mod.icc_2_k(m)
        lo, hi = icc_mod.bootstrap_icc_2_k(m, reps=reps, seed=seed)
        return dict(icc=float(v), lo=lo, hi=hi, n_items=int(m.shape[0]),
                    dropped=dropped, note="", icc_1=float(icc_mod.icc_2_1(m)))

    agree = {"learn": icc_for(r2, "learn"), "psi_a1": icc_for(r2, "psi_ratio")}
    for mode in HYBRID:
        agree[f"phi_{mode}"] = icc_for(
            r2, "phi", lambda it, m=mode: it.split("|")[0] == m)
    # h_raw is a single target: ICC is undefined and is reported as such.
    agree["h_raw"] = dict(icc=None, lo=None, hi=None, n_items=1, dropped=0,
                          note="single target: ICC undefined; dispersion only")
    for k, a in agree.items():
        a["decision"] = ("point value" if a["icc"] is not None
                         and icc_mod.meets_threshold(a["icc"]) else "range")
    agree_r1 = {"learn": icc_for(r1, "learn")}   # Delphi convergence, descriptive

    # --- point values and intervals ---
    point = aggregate(r2, raters, worked_item)
    rng = np.random.default_rng(seed)
    boots, jointly = [], []
    for _ in range(reps):
        sample = []
        for g, members in by_group.items():
            if members:
                sample += list(rng.choice(members, size=len(members), replace=True))
        agg = aggregate(r2, sample, worked_item)
        boots.append(agg)
        jointly.append(_summ(solve(to_inputs(agg))))
    interval = {}
    for k in ESTIMATED:
        vs = np.array([b[k] for b in boots], dtype=float)
        vs = vs[np.isfinite(vs)]
        interval[k] = (float(np.percentile(vs, 2.5)), float(np.percentile(vs, 97.5))) \
            if len(vs) else (np.nan, np.nan)

    # --- documented vs practised certification hours ---
    doc = [v for rid in raters for v in r2["h_raw_doc"].get(rid, {}).values()]
    prac = [v for rid in raters for v in r2["h_raw_prac"].get(rid, {}).values()]
    h_gap = (dict(documented_median=float(np.median(doc)),
                  practised_median=float(np.median(prac)),
                  ratio=float(np.median(prac) / np.median(doc)))
             if doc and prac else None)

    # --- group means (descriptive) ---
    gm = {}
    for g, members in by_group.items():
        if members:
            gm[g] = {k: float(v) for k, v in aggregate(r2, members, worked_item).items()}

    # --- re-solve the worked example ---
    scen = {"estimated": _summ(BASE), "measured": _summ(solve(to_inputs(point)))}
    scen["one_at_a_time"] = {
        k: _summ(solve(to_inputs(point, only={k}))) for k in ESTIMATED}
    rng_scen = {}
    for k in ESTIMATED:
        if agree[k]["decision"] == "range":
            for tag, val in zip(("low", "high"), interval[k]):
                swapped = {kk: np.nan for kk in ESTIMATED}
                swapped[k] = val
                rng_scen[f"{k}:{tag}"] = _summ(solve(to_inputs(swapped, only={k})))
    scen["range_scenarios"] = rng_scen

    feas = [j["feasible"] for j in jointly]
    dist = {"p_feasible": float(np.mean(feas))}
    for key in ("lam", "cost", "tau", "n_hat", "lead_only"):
        vs = np.array([j[key] for j in jointly if j["feasible"]], dtype=float)
        dist[key] = (None if len(vs) == 0 else
                     dict(median=float(np.median(vs)),
                          lo=float(np.percentile(vs, 2.5)),
                          hi=float(np.percentile(vs, 97.5))))
    return dict(n_raters=len(raters),
                n_by_group={g: len(m) for g, m in by_group.items()},
                worked_item=worked_item, point=point, interval=interval,
                agreement=agree, agreement_round1=agree_r1, group_means=gm,
                h_raw_divergence=h_gap,
                scenarios=scen, bootstrap=dist, reps=reps, seed=seed,
                accept=icc_mod.ACCEPT)


# --------------------------------------------------------------------------
# Output
# --------------------------------------------------------------------------

def _f(x, nd=3):
    return "n/a" if x is None or not np.isfinite(x) else f"{x:.{nd}f}"


def tex_fragments(res, synthetic):
    guard = ""
    if synthetic:
        guard = ("\\PackageError{civicworkos-elicitation}"
                 "{SYNTHETIC test data in a manuscript fragment}"
                 "{Regenerate from real, ethics-approved ratings.}\n")
    a, iv, pt = res["agreement"], res["interval"], res["point"]
    rows = []
    for k in ESTIMATED:
        icc_s = ("n/a" if a[k]["icc"] is None else
                 f"{a[k]['icc']:.2f} [{_f(a[k]['lo'], 2)}, {_f(a[k]['hi'], 2)}]")
        nd = 0 if k == "h_raw" else 2
        rows.append(f"{LABEL[k]} & {_f(ESTIMATED[k], nd)} & {_f(pt[k], nd)} "
                    f"[{_f(iv[k][0], nd)}, {_f(iv[k][1], nd)}] & {icc_s} "
                    f"& {a[k]['decision']}\\\\")
    t1 = (guard + "\\begin{tabular}{@{}lcccl@{}}\n\\toprule\n"
          "Parameter & Estimated & Measured [95\\% CI] & ICC(2,$k$) [95\\% CI] "
          "& Reported as\\\\\n\\midrule\n" + "\n".join(rows) +
          "\n\\bottomrule\n\\end{tabular}\n")

    sc, bs = res["scenarios"], res["bootstrap"]
    def cell(d, key, nd, pct=False):
        if not d["feasible"]:
            return "infeasible"
        v = d[key] * (100 if pct else 1)
        return f"{v:.{nd}f}" + ("\\%" if pct else "")

    def band(key, nd, pct=False):
        d = bs[key]
        if d is None:
            return "---"
        m = 100 if pct else 1
        return (f"{d['median']*m:.{nd}f} [{d['lo']*m:.{nd}f}, {d['hi']*m:.{nd}f}]"
                + ("\\%" if pct else ""))
    spec = [("$\\lambda_k$", "lam", 4, False), ("Cost of preservation", "cost", 2, True),
            ("$\\tau_k$ (years)", "tau", 2, False), ("$\\hat n_k$ (posts)", "n_hat", 1, False),
            ("Lead-only share of tasks", "lead_only", 1, True)]
    r2 = [f"{n} & {cell(sc['estimated'], k, nd, p)} & {cell(sc['measured'], k, nd, p)} "
          f"& {band(k, nd, p)}\\\\" for n, k, nd, p in spec]
    r2.append(f"Proposition feasibility holds & "
              f"{'yes' if sc['estimated']['feasible'] else 'no'} & "
              f"{'yes' if sc['measured']['feasible'] else 'no'} & "
              f"{100*bs['p_feasible']:.0f}\\% of resamples\\\\")
    t2 = (guard + "\\begin{tabular}{@{}lccc@{}}\n\\toprule\n"
          "Outcome & Estimated inputs & Measured inputs & Rater bootstrap, median [95\\% CI]"
          "\\\\\n\\midrule\n" + "\n".join(r2) + "\n\\bottomrule\n\\end{tabular}\n")
    return t1, t2


def markdown(res, synthetic, headers):
    L = []
    if synthetic:
        L += ["> **SYNTHETIC TEST DATA. NOT A RESULT. DO NOT CITE.**", ""]
    L += ["# Elicitation analysis", "",
          f"Raters: {res['n_raters']} ({res['n_by_group']}). Ethics approval: "
          f"{headers.get('ethics-approval', 'n/a (synthetic)')}. "
          f"Bootstrap: {res['reps']} resamples, seed {res['seed']}.", "",
          "## Agreement (round 2)", "",
          "| Parameter | Estimated | Measured [95% CI] | ICC(2,k) [95% CI] | Targets | Reported as |",
          "|---|---|---|---|---|---|"]
    for k in ESTIMATED:
        a = res["agreement"][k]
        i = "n/a" if a["icc"] is None else \
            f"{a['icc']:.2f} [{_f(a['lo'],2)}, {_f(a['hi'],2)}]"
        nd = 0 if k == "h_raw" else 3
        L.append(f"| {k} | {ESTIMATED[k]:g} | {_f(res['point'][k],nd)} "
                 f"[{_f(res['interval'][k][0],nd)}, {_f(res['interval'][k][1],nd)}] "
                 f"| {i} | {a['n_items']} | {a['decision']} |")
    g = res["h_raw_divergence"]
    gap = ("" if g is None else
           f" Documented certification hours (median {g['documented_median']:.0f}) "
           f"against hours raters say are required in practice "
           f"(median {g['practised_median']:.0f}): ratio {g['ratio']:.2f}. "
           "The model uses the practised figure.")
    L += ["", f"Acceptance threshold ICC(2,k) >= {res['accept']}. "
          "h_raw has a single target, so ICC is undefined and it is always "
          "reported as a range." + gap, "", "## Worked example re-solved", "",
          "| Outcome | Estimated | Measured | Rater bootstrap |", "|---|---|---|---|"]
    sc, bs = res["scenarios"], res["bootstrap"]
    for name, key, nd in [("lambda_k", "lam", 4), ("cost", "cost", 4),
                          ("tau_k", "tau", 3), ("n_hat_k", "n_hat", 2)]:
        e = _f(sc["estimated"].get(key), nd)
        m = _f(sc["measured"].get(key), nd) if sc["measured"]["feasible"] else "infeasible"
        b = bs[key]
        bb = "n/a" if b is None else f"{b['median']:.{nd}f} [{b['lo']:.{nd}f}, {b['hi']:.{nd}f}]"
        L.append(f"| {name} | {e} | {m} | {bb} |")
    L += ["", f"P(feasible) under the rater bootstrap: {bs['p_feasible']:.3f}", "",
          "## One parameter at a time (others at the article's estimate)", "",
          "| Parameter set to its measured value | feasible | lambda_k | cost | tau_k |",
          "|---|---|---|---|---|"]
    for k, d in sc["one_at_a_time"].items():
        L.append(f"| {k} | {d['feasible']} | {_f(d.get('lam'),4)} | "
                 f"{_f(d.get('cost'),4)} | {_f(d.get('tau'),3)} |")
    return "\n".join(L) + "\n"


def main(argv=None):
    ap = argparse.ArgumentParser(description=__doc__.split("\n\n")[0])
    ap.add_argument("ratings", type=Path)
    ap.add_argument("--out", type=Path, default=_HERE / "out")
    ap.add_argument("--allow-synthetic", action="store_true")
    ap.add_argument("--reps", type=int, default=2000)
    ap.add_argument("--seed", type=int, default=20261008)
    ap.add_argument("--worked-item", default="T01",
                    help="item id of the worked task in the learn_i bank")
    a = ap.parse_args(argv)
    try:
        prov, headers, rows = read_ratings(a.ratings, a.allow_synthetic)
        res = analyze(rows, a.worked_item, a.reps, a.seed)
    except DataError as e:
        print(f"REFUSED: {e}", file=sys.stderr)
        return 2
    synthetic = prov == "synthetic"
    pre = "SYNTHETIC-" if synthetic else ""
    a.out.mkdir(parents=True, exist_ok=True)
    t1, t2 = tex_fragments(res, synthetic)
    (a.out / f"{pre}measured_vs_estimated.tex").write_text(t1, encoding="utf-8")
    (a.out / f"{pre}rerun.tex").write_text(t2, encoding="utf-8")
    (a.out / f"{pre}report.md").write_text(markdown(res, synthetic, headers),
                                           encoding="utf-8")
    (a.out / f"{pre}results.json").write_text(
        json.dumps(dict(provenance=prov, **res), indent=2, default=float),
        encoding="utf-8")
    print(f"wrote {a.out}/{pre}report.md  (provenance: {prov})")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
