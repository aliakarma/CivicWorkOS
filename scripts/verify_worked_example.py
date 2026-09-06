#!/usr/bin/env python
"""Recompute every checkable number in Paper Sec. 5.3 (the worked
bridge-inspection allocation) and Sec. 7.1 / Fig. 3 (the analytic debt
model), and report PASS/FAIL against the values printed in the article.

This is the repository's own "ground truth" check (report Sec. 7,
Phase 0): the ONLY part of the paper with numbers this code can be
checked against, because the paper reports no measured results anywhere
else. Run it first, before anything else, after cloning:

    python scripts/verify_worked_example.py

Exit code 0 iff every check passes. Wired into CI as the first gate
(.github/workflows/ci.yml).
"""

from __future__ import annotations

import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "src"))

from civicworkos.analytic.debt_model import FIG3_STRATEGIES, accumulated_debt
from civicworkos.constraints.hcpb import HCPBParameters, capability_budget
from civicworkos.scoring.cad import DebtComponents, DebtWeights, civic_automation_debt
from civicworkos.scoring.scv import ScoreWeights, TermVector, sustainable_civic_value

TOL = 5e-4
_failures: list[str] = []


def check(name: str, actual: float, expected: float, tol: float = TOL) -> None:
    ok = abs(actual - expected) <= tol
    status = "PASS" if ok else "FAIL"
    print(f"[{status}] {name}: expected={expected:.6f} actual={actual:.6f}")
    if not ok:
        _failures.append(name)


def main() -> int:
    print("=== Sec. 5.3 worked bridge-inspection allocation ===")
    dw = DebtWeights.paper_default()
    sw = ScoreWeights.paper_default()

    table3 = {
        "H": dict(Q=0.72, S=0.55, P=0.40, Eq_srv=0.70, Tr=0.80, Cost=0.85, En=0.20, Pr=0.10,
                  D=(0.00, 0.00, 0.00, 0.00, 0.00)),
        "H+A": dict(Q=0.86, S=0.60, P=0.62, Eq_srv=0.72, Tr=0.74, Cost=0.62, En=0.28, Pr=0.25,
                    D=(0.25, 0.15, 0.07, 0.30, 0.10)),
        "H+R": dict(Q=0.80, S=0.88, P=0.70, Eq_srv=0.70, Tr=0.72, Cost=0.58, En=0.55, Pr=0.30,
                    D=(0.30, 0.25, 0.05, 0.35, 0.20)),
        "H+A+R": dict(Q=0.91, S=0.90, P=0.88, Eq_srv=0.74, Tr=0.68, Cost=0.50, En=0.60, Pr=0.38,
                      D=(0.45, 0.35, 0.13, 0.50, 0.30)),
    }
    expected_cad = {"H": 0.0000, "H+A": 0.1716, "H+R": 0.2300, "H+A+R": 0.3464}
    expected_scv = {"H": 0.2940, "H+A": 0.3245, "H+R": 0.3539, "H+A+R": 0.3765}

    cads, scvs = {}, {}
    for mode, row in table3.items():
        dc = DebtComponents(D_skill=row["D"][0], D_fall=row["D"][1], D_acct=row["D"][2],
                             D_dep=row["D"][3], D_trans=row["D"][4])
        cad = civic_automation_debt(dc, dw)
        tv = TermVector(Q=row["Q"], S=row["S"], P=row["P"], Eq_srv=row["Eq_srv"], Tr=row["Tr"],
                         Cost=row["Cost"], En=row["En"], Pr=row["Pr"])
        scv = sustainable_civic_value(tv, cad, sw)
        cads[mode], scvs[mode] = cad, scv
        check(f"CAD_{mode}", cad, expected_cad[mode], tol=5e-3)
        check(f"SCV_{mode}", scv, expected_scv[mode], tol=5e-3)

    print("\n=== HCPB budget ===")
    hcpb = HCPBParameters(N_k=24, r_k=0.12, h_k=600, eta_k=1.2, B_k_min=1200)
    b_k = capability_budget(hcpb)
    check("B_k (Eq. 9)", b_k, 2073.6, tol=1e-6)

    total_content = 340 * 8
    check("total developmental content", total_content, 2720)
    required_phi = b_k / total_content
    check("required mean phi", required_phi, 0.762, tol=1e-3)

    print("\n=== Constrained optimum (via LP; see civicworkos.solver) ===")
    import pulp

    xH = pulp.LpVariable("xH", 0, 1)
    xHR = pulp.LpVariable("xHR", 0, 1)
    xHA = pulp.LpVariable("xHA", 0, 1)
    xHAR = pulp.LpVariable("xHAR", 0, 1)
    prob = pulp.LpProblem("worked_example", pulp.LpMaximize)
    n_tasks = 340
    budget_per_task = b_k / n_tasks  # hours of protected practice required per task, on average

    prob += scvs["H"] * xH + scvs["H+R"] * xHR + scvs["H+A"] * xHA + scvs["H+A+R"] * xHAR
    prob += xH + xHR + xHA + xHAR == 1, "assignment"
    prob += (
        8 * 1.00 * xH + 8 * 0.70 * xHR + 8 * 0.75 * xHA + 8 * 0.55 * xHAR >= budget_per_task,
        "hcpb",
    )
    prob.solve(pulp.PULP_CBC_CMD(msg=0))

    check("mix share H", xH.value(), 0.208, tol=2e-3)
    check("mix share H+R", xHR.value(), 0.792, tol=2e-3)
    check("mix share H+A", xHA.value(), 0.0, tol=1e-6)
    check("mix share H+A+R", xHAR.value(), 0.0, tol=1e-6)

    hcpb_pi = prob.constraints["hcpb"].pi
    lambda_k = abs(hcpb_pi) if hcpb_pi is not None else 0.0
    check("dual lambda_k", lambda_k, 0.0250, tol=2e-3)

    scv_tilde_h = scvs["H"] + 8 * 1.00 * lambda_k
    scv_tilde_hr = scvs["H+R"] + 8 * 0.70 * lambda_k
    scv_tilde_har = scvs["H+A+R"] + 8 * 0.55 * lambda_k
    check("SCV~_H", scv_tilde_h, 0.4937, tol=3e-3)
    check("SCV~_H+R", scv_tilde_hr, 0.4937, tol=3e-3)
    check("SCV~_H+A+R", scv_tilde_har, 0.4863, tol=3e-3)

    unconstrained_annual = scvs["H+A+R"] * 340
    constrained_annual = (xH.value() * scvs["H"] + xHR.value() * scvs["H+R"]) * 340
    check("unconstrained annual value", unconstrained_annual, 128.0, tol=0.5)
    check("constrained annual value", constrained_annual, 116.1, tol=0.5)
    pct_cost = (unconstrained_annual - constrained_annual) / unconstrained_annual * 100
    check("objective cost percent", pct_cost, 9.3, tol=0.3)

    print("\n=== Sec. 7.1 analytic debt model (Fig. 3) ===")
    expected_c10 = {
        "automation_first": 100.0,
        "cost_performance": 110.0,
        "capability_matching": 65.0,
        "civicworkos": 30.0 * (1 - pow(2.718281828459045, -10 / 3)),
        "human_first": 5.0 * (1 - pow(2.718281828459045, -2 * 10)),
    }
    for name, params in FIG3_STRATEGIES.items():
        c10 = accumulated_debt(10.0, params)
        check(f"C(10) {name}", c10, expected_c10[name], tol=0.5)

    print()
    if _failures:
        print(f"FAILED: {len(_failures)} check(s) did not reproduce the paper's numbers: {_failures}")
        return 1
    print("All worked-example numbers reproduced within tolerance.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
