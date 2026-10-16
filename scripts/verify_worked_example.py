#!/usr/bin/env python
"""Verify that THIS CODE reproduces the numbers the manuscript prints.

Scope: the worked bridge-inspection allocation of Paper sec:worked and its
subsections, and the debt trajectory of sec:cadmodel / fig:cad-trend. That is
the whole of the article's quantitative content. The article reports no dataset
and no measured empirical result, and the evaluation protocol it specifies
(sec:protocol, Appendix app:protocol) has not been executed, so there is nothing
else here with a ground truth to check against.

Run it first, before anything else, after cloning:

    python scripts/verify_worked_example.py

Exit code 0 iff every check passes. Wired into CI as the first gate
(.github/workflows/ci.yml) and into the manuscript's own gate script
(Paper/Frontiers/check.sh).

Why this file was rewritten (finding N2, revision programme Phase 3). Until
Phase 3 this script verified an earlier draft: it asserted ``B_k = 2073.6``
where the manuscript computes ``B_k = 4976.64``, scored four execution modes
where the manuscript scores eight *staffed* modes, priced practice at
``lambda_k = 0.025`` against a printed 0.0454, and checked a one-component debt
curve the manuscript has since replaced with the five-component eq:cadmodel.
Every one of those checks passed. The script exited 0 while certifying a paper
that no longer existed, which is the worst failure mode available to a
verification artifact, because it converts the absence of a signal into a
positive one.

The cause was duplication: this script kept its own copy of the manuscript's
constants, the article moved, and nothing forced the two back into agreement.
So the fix is structural. Every manuscript value below is imported from
`manuscript_values`, which re-exports the single definition in
`Paper/Frontiers/audit_numbers.py`. Nothing in this file restates a number the
article states. What this file *does* hold is the printed values themselves --
the figures a reader sees on the page -- because the question it exists to
answer is whether the library's output matches what was published.

The division of labour between the repository's two gates:

* `Paper/Frontiers/audit_numbers.py` asks whether the *manuscript* is
  internally consistent -- whether each printed number follows from the inputs
  the article states. It caught the defect class that dominated the peer review:
  prose that misreported a correct table.
* this script asks whether *this code* reproduces those printed numbers --
  whether `civicworkos.scoring`, `civicworkos.constraints.hcpb` and
  `civicworkos.analytic` compute what the article publishes.
"""

from __future__ import annotations

import sys
from pathlib import Path

_ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(_ROOT / "src"))
sys.path.insert(0, str(_ROOT))

import pulp

from civicworkos.analytic.debt_model import (
    accumulated_debt,
    bounded_ceiling,
    residual_slope,
    strategy_from_table,
)
from civicworkos.constraints.hcpb import HCPBParameters, capability_budget
from civicworkos.scoring.cad import DebtComponents, DebtWeights, civic_automation_debt
from civicworkos.scoring.scv import ScoreWeights, TermVector, sustainable_civic_value
from manuscript_values import CAD_PRINTED, CAD_STRATEGIES, CAD_W, MODES, WORKED

TOL = 1e-4
_failures: list[str] = []
_count = 0


def check(name: str, actual: float, expected: float, tol: float = TOL) -> None:
    global _count
    _count += 1
    ok = abs(actual - expected) <= tol
    status = "PASS" if ok else "FAIL"
    print(f"[{status}] {name}: printed={expected:.6f} computed={actual:.6f}")
    if not ok:
        _failures.append(name)


def _library_cad_scv() -> tuple[dict[str, float], dict[str, float]]:
    """Score all eight staffed modes of tab:worked-terms through the library.

    The staffed mode is the unit the manuscript scores: an execution mode paired
    with a named roster at a declared career stage, written ``H+A+R/a1``. The
    career stage is not decoration -- it sets psi_a, the developmental
    eligibility, and so sets the credited share phi_m * psi_a that D_skill is
    defined against (eq:dskill). An earlier version of this script scored four
    *execution* modes with no roster, which made the capability budget
    unsatisfiable at the manuscript's parameters and is why its numbers could
    not be reconciled with the article's.
    """
    # Build the weights from the manuscript's own definition rather than the
    # library default, so a change to either is caught here instead of hidden.
    dw = DebtWeights(
        alpha=CAD_W["skill"],
        beta=CAD_W["fall"],
        gamma=CAD_W["acct"],
        delta=CAD_W["dep"],
        epsilon=CAD_W["trans"],
    )
    sw = ScoreWeights.paper_default()

    cads: dict[str, float] = {}
    scvs: dict[str, float] = {}
    for name, m in MODES.items():
        dc = DebtComponents(
            D_skill=m.D_skill,
            D_fall=m.D_fall,
            D_acct=m.D_acct,
            D_dep=m.D_dep,
            D_trans=m.D_trans,
        )
        cad = civic_automation_debt(dc, dw)
        tv = TermVector(
            Q=m.Q, S=m.S, P=m.P, Eq_srv=m.Eq, Tr=m.Tr, Cost=m.Cost, En=m.En, Pr=m.Pr
        )
        cads[name] = cad
        scvs[name] = sustainable_civic_value(tv, cad, sw)
    return cads, scvs


def main() -> int:
    w = WORKED
    ell = w["ell_i"]
    n_k = w["n_k"]

    # ------------------------------------------------------------------
    print("=== sec:weights -- the weight vectors (eq:scv, eq:cad) ===")
    sw = ScoreWeights.paper_default()
    check("objective weights sum to one", sum(sw.as_tuple()), 1.0, tol=1e-9)
    check("debt weights sum to one", sum(CAD_W.values()), 1.0, tol=1e-9)
    check("w9 on deferred liability", sw.w9_cad, 0.22, tol=1e-9)

    # ------------------------------------------------------------------
    print("\n=== tab:worked-terms -- CAD by staffed mode (eq:cad) ===")
    cads, scvs = _library_cad_scv()
    printed_cad = {
        "H/a0": 0.2800, "H/a1": 0.1400,
        "H+A/a0": 0.3816, "H+A/a1": 0.2766,
        "H+R/a0": 0.4260, "H+R/a1": 0.3280,
        "H+A+R/a0": 0.5004, "H+A+R/a1": 0.4234,
    }
    for name, printed in printed_cad.items():
        check(f"CAD {name}", cads[name], printed)

    print("\n=== tab:worked-terms -- SCV by staffed mode (eq:scv) ===")
    printed_scv = {
        "H/a0": 0.2324, "H/a1": 0.2391,
        "H+A/a0": 0.2783, "H+A/a1": 0.2773,
        "H+R/a0": 0.3108, "H+R/a1": 0.3082,
        "H+A+R/a0": 0.3426, "H+A+R/a1": 0.3355,
    }
    for name, printed in printed_scv.items():
        check(f"SCV {name}", scvs[name], printed)
    check("unconstrained SCV, five decimals", scvs["H+A+R/a0"], 0.34261, tol=1e-5)

    # ------------------------------------------------------------------
    print("\n=== sec:binds -- the capability budget (eq:bkworked) ===")
    hcpb = HCPBParameters(
        N_k=w["N_k"], r_k=w["r_k"], h_k=w["h_k"], eta_k=w["eta_k"], B_k_min=w["B_min"]
    )
    b_k = capability_budget(hcpb)
    check("B_k", b_k, 4976.64, tol=1e-6)
    check("h_k = learn_i * h_raw_k (eq:hconv)", w["learn"] * w["h_raw_k"], 1440.0, tol=1e-6)
    check("Phi_k = n_k * ell_i", n_k * ell, 16800.0, tol=1e-6)
    check("required mean credited share", b_k / (n_k * ell), 0.2962)
    check("Phi_k * zeta_bar (prop:feasibility)", n_k * ell * w["zeta_bar"], 5880.0, tol=1e-6)

    # ------------------------------------------------------------------
    print("\n=== sec:solving -- the constrained optimum, by LP ===")
    lo_name, hi_name, unc_name = w["mode_lo"], w["mode_hi"], w["mode_unc"]
    budget_per_task = b_k / n_k

    x = {name: pulp.LpVariable(f"x_{i}", 0, 1) for i, name in enumerate(MODES)}
    prob = pulp.LpProblem("worked_example", pulp.LpMaximize)
    prob += pulp.lpSum(scvs[name] * x[name] for name in MODES)
    prob += pulp.lpSum(x[name] for name in MODES) == 1, "assignment"
    prob += (
        pulp.lpSum(ell * MODES[name].credited * x[name] for name in MODES)
        >= budget_per_task,
        "hcpb",
    )
    prob.solve(pulp.PULP_CBC_CMD(msg=0))
    if pulp.LpStatus[prob.status] != "Optimal":
        print(f"[FAIL] LP did not solve to optimality: {pulp.LpStatus[prob.status]}")
        return 1

    shares = {name: (x[name].value() or 0.0) for name in MODES}
    check(f"share on {lo_name}", shares[lo_name], 0.2830, tol=5e-4)
    check(f"share on {hi_name}", shares[hi_name], 0.7170, tol=5e-4)
    for name in MODES:
        if name not in (lo_name, hi_name):
            check(f"share on {name} is zero", shares[name], 0.0, tol=1e-6)

    mean_scv = sum(shares[name] * scvs[name] for name in MODES)
    check("constrained mean SCV", mean_scv, 0.327750, tol=1e-5)
    check(
        "mean credited share at the optimum",
        sum(shares[name] * MODES[name].credited for name in MODES),
        0.2962,
    )

    # Integrality, sec:solving: 2,100 tasks do not divide into the mix exactly.
    def hours(n: int) -> float:
        """Practice hours delivered when n tasks take the lead-only roster."""
        return (
            n * ell * MODES[lo_name].credited
            + (n_k - n) * ell * MODES[hi_name].credited
        )

    check("fractional task count on the lead-only roster", shares[lo_name] * n_k, 594.4, tol=0.05)
    check("hours delivered by 594 tasks", hours(594), 4976.40, tol=1e-6)
    check("hours delivered by 595 tasks", hours(595), 4977.00, tol=1e-6)
    check("budget shortfall at 594 tasks", b_k - hours(594), 0.24, tol=1e-6)

    # ------------------------------------------------------------------
    print("\n=== eq:lambdaworked -- the capability price (the LP dual) ===")
    hcpb_pi = prob.constraints["hcpb"].pi
    lambda_k = abs(hcpb_pi) if hcpb_pi is not None else 0.0
    check("lambda_k from the solver dual", lambda_k, 0.045353, tol=1e-6)
    check("lambda_k at the quoted four decimals", round(lambda_k, 4), 0.0454, tol=1e-9)

    print("\n=== eq:augworked -- the ranking reversal ===")
    # The mechanism the framework exists to produce: at lambda_k the two active
    # staffed modes tie, and both beat the unconstrained winner. The tie is
    # exact by construction, because lambda_k is *defined* by it.
    aug = {name: scvs[name] + lambda_k * ell * MODES[name].credited for name in MODES}
    check(f"augmented SCV {lo_name}", aug[lo_name], 0.435229, tol=1e-6)
    check(f"augmented SCV {hi_name}", aug[hi_name], 0.435229, tol=1e-6)
    check("tie residual between the active modes", abs(aug[lo_name] - aug[hi_name]), 0.0, tol=1e-9)
    check(f"augmented SCV {unc_name}", aug[unc_name], 0.3426)
    if not aug[lo_name] > aug[unc_name]:
        print("[FAIL] the capability price does not reverse the unconstrained winner")
        _failures.append("ranking reversal")

    # ------------------------------------------------------------------
    print("\n=== sec:costs -- what preservation costs ===")
    unc_year = scvs[unc_name] * n_k
    con_year = mean_scv * n_k
    check("unconstrained annual objective", unc_year, 719.5, tol=0.05)
    check("constrained annual objective", con_year, 688.3, tol=0.05)
    check("annual cost of the constraint", unc_year - con_year, 31.2, tol=0.05)
    check("relative cost of preservation", (unc_year - con_year) / unc_year, 0.0434, tol=5e-5)
    check("average price per practice hour", (unc_year - con_year) / b_k, 0.0063, tol=5e-5)
    check("competent-equivalents formed per year", b_k / w["h_k"], 3.456, tol=1e-6)
    check("annual attrition in practitioners", w["N_k"] * w["r_k"], 2.88, tol=1e-9)

    # ------------------------------------------------------------------
    print("\n=== sec:pipeline -- the intake requirement (prop:intake) ===")
    # The article's most citable result, and the one no headcount plan surfaces.
    phi_bar = sum(shares[name] * MODES[name].phi for name in MODES)
    check("phi_bar_k at the optimum", phi_bar, 0.5925, tol=5e-5)
    tau_k = (w["h_raw_k"] / w["Theta_k"]) / (phi_bar * w["omega_bar"])
    check("certification-implied duration h_raw/Theta", w["h_raw_k"] / w["Theta_k"], 1.20, tol=1e-9)
    check("tau_k, years to competence (eq:tauworked)", tau_k, 4.05, tol=5e-3)
    check("dilution factor", tau_k / (w["h_raw_k"] / w["Theta_k"]), 3.38, tol=5e-3)
    n_hat = w["eta_k"] * w["N_k"] * w["r_k"] * tau_k
    check("intake requirement n_hat_k (eq:intakeworked)", n_hat, 14.0, tol=5e-2)
    check("n_hat_k, independent route: trainee hours / Theta_k", n_k * w["d_i"] / w["Theta_k"], 14.0, tol=1e-9)
    check(
        "naive intake from the certification figure",
        w["eta_k"] * w["N_k"] * w["r_k"] * (w["h_raw_k"] / w["Theta_k"]),
        4.0,
        tol=0.15,
    )

    # ------------------------------------------------------------------
    print("\n=== sec:whoworked -- who receives the protected practice ===")
    blind = w["incumbent_women"] * b_k
    floor = w["pool_women"] - w["epsilon_k"]
    check("composition-blind hours to the group", blind, 622.0, tol=0.1)
    check("required share Pi_{k,g} (eq:accessshare)", floor, 0.27, tol=1e-9)
    check("hours under the access constraint", floor * b_k, 1344.0, tol=0.5)
    check("access multiplier", (floor * b_k) / blind, 2.16, tol=5e-3)

    # ------------------------------------------------------------------
    print("\n=== tab:cadparams / fig:cad-trend -- the debt trajectory ===")
    strategies = {
        name: strategy_from_table(row) for name, row in CAD_STRATEGIES.items()
    }
    for name, (printed_slope, printed_c10) in CAD_PRINTED.items():
        s = strategies[name]
        check(f"residual slope -- {name}", residual_slope(s, CAD_W), printed_slope, tol=5e-3)
        check(f"C(10) -- {name}", accumulated_debt(10.0, s, CAD_W), printed_c10, tol=5e-3)

    cw, hf = strategies["CivicWorkOS"], strategies["Human-First"]
    check("CivicWorkOS bounded part", bounded_ceiling(cw, CAD_W), 17.98, tol=1e-2)
    check(
        "of which skill formation",
        CAD_W["skill"] * cw["skill"].c_j * cw["skill"].pi_inf * cw["skill"].tau,
        11.34,
        tol=5e-3,
    )
    check(
        "vendor dependency share of the residual",
        CAD_W["dep"] * cw["dep"].c_j * (1.0 - cw["dep"].pi_inf),
        1.08,
        tol=5e-3,
    )
    check("CivicWorkOS C(20)", accumulated_debt(20.0, cw, CAD_W), 46.89, tol=5e-3)
    check("Human-First C(20)", accumulated_debt(20.0, hf, CAD_W), 52.89, tol=5e-3)

    # The crossover, by bisection. Human-First accrues less debt than
    # CivicWorkOS until year 13.23 and more thereafter; the article reports this
    # against itself rather than burying it.
    lo_t, hi_t = 1.0, 60.0
    for _ in range(200):
        mid = 0.5 * (lo_t + hi_t)
        if accumulated_debt(mid, hf, CAD_W) - accumulated_debt(mid, cw, CAD_W) < 0.0:
            lo_t = mid
        else:
            hi_t = mid
    t_cross = 0.5 * (lo_t + hi_t)
    check("Human-First / CivicWorkOS crossover year", t_cross, 13.23, tol=5e-3)
    check("debt index at the crossover", accumulated_debt(t_cross, cw, CAD_W), 36.73, tol=5e-3)

    # ------------------------------------------------------------------
    print()
    if _failures:
        print(
            f"FAILED: {len(_failures)} of {_count} checks did not reproduce the "
            f"manuscript's printed values: {_failures}"
        )
        return 1
    print(
        f"All {_count} checks reproduce the manuscript's printed values within "
        f"tolerance."
    )
    print(
        "Scope: sec:worked and sec:cadmodel only. The article reports no dataset "
        "and no measured result, and the protocol of sec:protocol has not been "
        "executed, so nothing else in it has a ground truth to check."
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
