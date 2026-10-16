#!/usr/bin/env python
"""Solve the city-wide allocation program (eq:program) for a small task
batch and print the assignment and published dual prices.

Uses the worked example's own tab:worked-terms term values (Paper sec:worked) at a
reduced task count -- see tests/integration/test_rebalance_solver.py for
why a reduced count is used (combinatorial symmetry in the MIP at the
paper's real 2,100-inspection population; civicworkos.solver.rebalance's
default time limit bounds worst-case runtime regardless).

Usage:
    python scripts/run_rebalance.py [n_tasks]
"""

from __future__ import annotations

import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "src"))

from civicworkos.constraints.hcpb import HCPBParameters, capability_budget
from civicworkos.program.city_program import CandidatePair, ProgramInputs, TaskInstance
from civicworkos.scoring.cad import DebtComponents, DebtWeights, civic_automation_debt
from civicworkos.scoring.scv import ScoreWeights, TermVector, sustainable_civic_value
from civicworkos.solver.rebalance import solve_rebalance

DOMAIN = "structural_inspection"

_TABLE3 = {
    "H": dict(Q=0.72, S=0.55, P=0.40, Eq_srv=0.70, Tr=0.80, Cost=0.85, En=0.20, Pr=0.10,
              D=(0.00, 0.00, 0.00, 0.00, 0.00), phi=1.00),
    "H+A": dict(Q=0.86, S=0.60, P=0.62, Eq_srv=0.72, Tr=0.74, Cost=0.62, En=0.28, Pr=0.25,
                D=(0.25, 0.15, 0.07, 0.30, 0.10), phi=0.75),
    "H+R": dict(Q=0.80, S=0.88, P=0.70, Eq_srv=0.70, Tr=0.72, Cost=0.58, En=0.55, Pr=0.30,
                D=(0.30, 0.25, 0.05, 0.35, 0.20), phi=0.70),
    "H+A+R": dict(Q=0.91, S=0.90, P=0.88, Eq_srv=0.74, Tr=0.68, Cost=0.50, En=0.60, Pr=0.38,
                  D=(0.45, 0.35, 0.13, 0.50, 0.30), phi=0.55),
}


def main() -> int:
    n_tasks = int(sys.argv[1]) if len(sys.argv) > 1 else 12
    dw = DebtWeights.paper_default()
    sw = ScoreWeights.paper_default()

    tasks = [
        TaskInstance(task_id=f"insp-{i}", domain=DOMAIN, service="structural_inspection_service",
                     ell_i=8.0, duration_hours=10.0)
        for i in range(n_tasks)
    ]
    candidates = []
    for task in tasks:
        for mode, row in _TABLE3.items():
            dc = DebtComponents(D_skill=row["D"][0], D_fall=row["D"][1], D_acct=row["D"][2],
                                 D_dep=row["D"][3], D_trans=row["D"][4])
            cad = civic_automation_debt(dc, dw)
            tv = TermVector(Q=row["Q"], S=row["S"], P=row["P"], Eq_srv=row["Eq_srv"], Tr=row["Tr"],
                             Cost=row["Cost"], En=row["En"], Pr=row["Pr"])
            scv = sustainable_civic_value(tv, cad, sw)
            candidates.append(CandidatePair(task_id=task.task_id, mode=mode, scv=scv, phi_m=row["phi"]))

    hcpb = HCPBParameters(N_k=24, r_k=0.12, h_k=1440, eta_k=1.2, B_k_min=2000)
    budget = capability_budget(hcpb) / 2100 * n_tasks  # scaled to this batch's size

    inputs = ProgramInputs(
        tasks=tasks, candidates=candidates, domain_budgets={DOMAIN: budget},
        access_constraints={}, reserve_states={}, resource_capacities={},
    )

    result = solve_rebalance(inputs)
    print(f"Status: {result.status}")
    print(f"Objective value: {result.objective_value:.4f}")
    print(f"Dual lambda_k[{DOMAIN}]: {result.lambda_k.get(DOMAIN, 0.0):.6f}")
    print(f"Dual extraction method: {result.dual_extraction_method}")

    counts: dict[str, int] = {m: 0 for m in _TABLE3}
    for (task_id, mode), value in result.assignment.items():
        if value and value > 0.5:
            counts[mode] += 1
    print("Mode counts:", counts)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
