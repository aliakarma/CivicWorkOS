"""Integration test: civicworkos.program + civicworkos.solver against the
worked example of Paper sec:worked, at its actual task population.

This exercises the GENERAL eq:program MIP builder
(civicworkos.program.city_program) and the two-solve dual-extraction strategy
(civicworkos.solver.rebalance), not the hand-rolled LP in tests/smoke -- it is
the production code path a real rebalance would use. The property under test is
that the general solver recovers the article's constrained optimum: a mix of the
two staffed modes of tab:worked-mix, priced at the lambda_k of eq:lambdaworked.

Like tests/smoke and scripts/verify_worked_example.py, this file was rebuilt in
Phase 3 of the revision programme (finding N2). It previously scored four
*execution* modes against an earlier draft's parameters -- h_k = 600, B_k =
2073.6, 340 tasks, lambda_k = 0.0250 -- and asserted them. All manuscript inputs
now come from `manuscript_values`, which re-exports the single definition in
`Paper/Frontiers/audit_numbers.py`.
"""

from __future__ import annotations

import pytest

from civicworkos.constraints.hcpb import HCPBParameters, capability_budget
from civicworkos.program.city_program import CandidatePair, ProgramInputs, TaskInstance
from civicworkos.scoring.cad import DebtComponents, DebtWeights, civic_automation_debt
from civicworkos.scoring.scv import ScoreWeights, TermVector, sustainable_civic_value
from civicworkos.solver.rebalance import solve_rebalance
from manuscript_values import MODES, WORKED

DOMAIN = "structural_inspection"

# The worked example runs 2,100 inspections a year, but 2,100 near-identical
# binary candidates make the MIP combinatorially SYMMETRIC -- every permutation
# of "which 594 tasks take the lead-only roster" is an equivalent optimum --
# which is a known difficulty for generic branch-and-bound independent of any
# difficulty in the LP sense. See civicworkos.solver.rebalance's default time
# limit and docs/troubleshooting.md. This test therefore uses a reduced task
# count at the same per-task budget intensity, which preserves the mode
# economics exactly and so preserves both the optimal mix and the dual. It does
# NOT claim that CivicWorkOS solves a 2,100-task rebalance quickly; the
# pre-release audit names problem-size behaviour as an open question the article
# does not address, and sec:limitations says the same.
N_TASKS = 60


def _build_inputs() -> ProgramInputs:
    w = WORKED
    ell = w["ell_i"]
    dw = DebtWeights.paper_default()
    sw = ScoreWeights.paper_default()

    tasks = [
        TaskInstance(
            task_id=f"insp-{i}",
            domain=DOMAIN,
            service="structural_inspection_service",
            ell_i=ell,
            duration_hours=w["d_i"],
        )
        for i in range(N_TASKS)
    ]

    candidates = []
    for task in tasks:
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
            candidates.append(
                CandidatePair(
                    task_id=task.task_id,
                    mode=name,
                    scv=sustainable_civic_value(tv, cad, sw),
                    # The CREDITED share phi_m * psi_a, not a bare phi_m: eq:hcpb
                    # accrues practice only below independent competence, so the
                    # a0 (competent) staffed modes credit zero.
                    phi_m=m.credited,
                )
            )

    # eq:bkworked gives B_k = 4,976.64 hours against the domain's 2,100 tasks.
    # Scaling the same per-task intensity to N_TASKS keeps the mode economics
    # and therefore the same optimal split and the same dual; using the
    # unscaled budget against 60 candidates would be infeasible outright, which
    # would be an artifact of this test rather than a property of
    # eq:hcpb-estimator.
    b_k = capability_budget(
        HCPBParameters(
            N_k=w["N_k"], r_k=w["r_k"], h_k=w["h_k"], eta_k=w["eta_k"], B_k_min=w["B_min"]
        )
    )
    budget = (b_k / w["n_k"]) * N_TASKS

    return ProgramInputs(
        tasks=tasks,
        candidates=candidates,
        domain_budgets={DOMAIN: budget},
        access_constraints={},
        reserve_states={},
        resource_capacities={},
    )


@pytest.fixture(scope="module")
def solved():
    return solve_rebalance(_build_inputs())


@pytest.fixture(scope="module")
def scaled_budget():
    w = WORKED
    b_k = capability_budget(
        HCPBParameters(
            N_k=w["N_k"], r_k=w["r_k"], h_k=w["h_k"], eta_k=w["eta_k"], B_k_min=w["B_min"]
        )
    )
    return (b_k / w["n_k"]) * N_TASKS


def test_solve_status_optimal(solved):
    assert solved.status == "Optimal"


def test_the_two_active_staffed_modes_carry_the_assignment(solved, scaled_budget):
    """tab:worked-mix: the optimum is a mix of two staffed modes, both at the
    developing career stage.

    At finite N_TASKS, integer rounding of the budget constraint can push a task
    or two to a third mode at the margin -- a genuine MIP-vs-LP integrality gap
    (tests/smoke checks the exact continuous split). The N-independent properties
    are checked instead: the two active modes of tab:worked-mix carry nearly
    everything, the unconstrained winner is used rarely if at all, and the
    budget is actually met.
    """
    w = WORKED
    counts = {name: 0 for name in MODES}
    delivered = 0.0
    for (_task_id, mode), value in solved.assignment.items():
        if value and value > 0.5:
            counts[mode] += 1
            delivered += w["ell_i"] * MODES[mode].credited

    active = counts[w["mode_lo"]] + counts[w["mode_hi"]]
    assert active >= N_TASKS - 2, counts
    # H+A+R/a0 maximizes SCV but credits no practice at all, so the budget
    # should keep it almost entirely out of the solution.
    assert counts[w["mode_unc"]] <= 2, counts
    assert delivered >= scaled_budget - 1e-6


def test_the_budget_binds(solved, scaled_budget):
    """The constraint is what makes the instance interesting: it should be
    tight, not slack, which is why it carries a non-zero price."""
    w = WORKED
    delivered = sum(
        w["ell_i"] * MODES[mode].credited
        for (_t, mode), value in solved.assignment.items()
        if value and value > 0.5
    )
    # Tight to within one task's developmental credit.
    assert delivered - scaled_budget < w["ell_i"] * MODES[w["mode_lo"]].credited


def test_dual_price_reproduces_worked_example(solved):
    """eq:lambdaworked: the general solver recovers 0.0454 objective units per
    qualified-practice hour, the same price the hand-rolled LP in tests/smoke
    and scripts/verify_worked_example.py obtain."""
    assert solved.lambda_k[DOMAIN] == pytest.approx(0.045353, abs=2e-3)


def test_objective_value_scales_with_task_count(solved):
    """sec:costs reports 688.3 objective units a year over 2,100 tasks; every
    task carries the same SCV structure, so the total scales linearly."""
    expected = 688.3 * N_TASKS / WORKED["n_k"]
    assert solved.objective_value == pytest.approx(expected, rel=0.05)
