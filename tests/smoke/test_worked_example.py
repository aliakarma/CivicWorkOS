"""THE ORACLE: reproduces every checkable number in Paper Sec. 5.3 (the
worked bridge-inspection allocation) and Sec. 7.1 / Fig. 3.

This is the only part of the paper with a ground truth this repository
can be checked against -- see docs/reproducibility.md. If any test here
fails, something in civicworkos.scoring, civicworkos.constraints.hcpb,
or civicworkos.analytic no longer matches the article, and that is a
release blocker (report Sec. 7, Phase 0: "make this test the
repository's first CI gate").
"""

from __future__ import annotations

import math

import pulp
import pytest

from civicworkos.analytic.debt_model import FIG3_STRATEGIES, accumulated_debt
from civicworkos.constraints.hcpb import HCPBParameters, capability_budget
from civicworkos.scoring.cad import DebtComponents, DebtWeights, civic_automation_debt
from civicworkos.scoring.scv import ScoreWeights, TermVector, sustainable_civic_value

TABLE3 = {
    "H": dict(Q=0.72, S=0.55, P=0.40, Eq_srv=0.70, Tr=0.80, Cost=0.85, En=0.20, Pr=0.10,
              D=(0.00, 0.00, 0.00, 0.00, 0.00)),
    "H+A": dict(Q=0.86, S=0.60, P=0.62, Eq_srv=0.72, Tr=0.74, Cost=0.62, En=0.28, Pr=0.25,
                D=(0.25, 0.15, 0.07, 0.30, 0.10)),
    "H+R": dict(Q=0.80, S=0.88, P=0.70, Eq_srv=0.70, Tr=0.72, Cost=0.58, En=0.55, Pr=0.30,
                D=(0.30, 0.25, 0.05, 0.35, 0.20)),
    "H+A+R": dict(Q=0.91, S=0.90, P=0.88, Eq_srv=0.74, Tr=0.68, Cost=0.50, En=0.60, Pr=0.38,
                  D=(0.45, 0.35, 0.13, 0.50, 0.30)),
}


@pytest.fixture(scope="module")
def cad_scv_by_mode():
    dw = DebtWeights.paper_default()
    sw = ScoreWeights.paper_default()
    result = {}
    for mode, row in TABLE3.items():
        dc = DebtComponents(D_skill=row["D"][0], D_fall=row["D"][1], D_acct=row["D"][2],
                             D_dep=row["D"][3], D_trans=row["D"][4])
        cad = civic_automation_debt(dc, dw)
        tv = TermVector(Q=row["Q"], S=row["S"], P=row["P"], Eq_srv=row["Eq_srv"], Tr=row["Tr"],
                         Cost=row["Cost"], En=row["En"], Pr=row["Pr"])
        scv = sustainable_civic_value(tv, cad, sw)
        result[mode] = (cad, scv)
    return result


@pytest.mark.parametrize(
    "mode,expected_cad",
    [("H", 0.0000), ("H+A", 0.1716), ("H+R", 0.2300), ("H+A+R", 0.3464)],
)
def test_cad_reproduces_table3(cad_scv_by_mode, mode, expected_cad):
    cad, _ = cad_scv_by_mode[mode]
    assert cad == pytest.approx(expected_cad, abs=5e-3)


@pytest.mark.parametrize(
    "mode,expected_scv",
    [("H", 0.2940), ("H+A", 0.3245), ("H+R", 0.3539), ("H+A+R", 0.3765)],
)
def test_scv_reproduces_table3(cad_scv_by_mode, mode, expected_scv):
    _, scv = cad_scv_by_mode[mode]
    assert scv == pytest.approx(expected_scv, abs=5e-3)


def test_hcpb_budget_reproduces_worked_example():
    params = HCPBParameters(N_k=24, r_k=0.12, h_k=600, eta_k=1.2, B_k_min=1200)
    assert capability_budget(params) == pytest.approx(2073.6, abs=1e-6)


def test_required_mean_phi_reproduces_worked_example():
    b_k = 2073.6
    total_content = 340 * 8
    assert total_content == 2720
    assert (b_k / total_content) == pytest.approx(0.762, abs=1e-3)


@pytest.fixture(scope="module")
def constrained_lp_solution(cad_scv_by_mode):
    scv = {mode: s for mode, (_, s) in cad_scv_by_mode.items()}
    n_tasks = 340
    b_k = 2073.6
    budget_per_task = b_k / n_tasks

    x = {mode: pulp.LpVariable(f"x_{mode.replace('+', '')}", 0, 1) for mode in TABLE3}
    phi = {"H": 1.00, "H+A": 0.75, "H+R": 0.70, "H+A+R": 0.55}

    prob = pulp.LpProblem("worked_example", pulp.LpMaximize)
    prob += pulp.lpSum(scv[m] * x[m] for m in TABLE3)
    prob += pulp.lpSum(x[m] for m in TABLE3) == 1, "assignment"
    prob += (
        pulp.lpSum(8 * phi[m] * x[m] for m in TABLE3) >= budget_per_task,
        "hcpb",
    )
    prob.solve(pulp.PULP_CBC_CMD(msg=0))
    shares = {m: x[m].value() for m in TABLE3}
    lambda_k = abs(prob.constraints["hcpb"].pi)
    return shares, lambda_k, scv


def test_constrained_optimum_mix_reproduces_worked_example(constrained_lp_solution):
    shares, _, _ = constrained_lp_solution
    assert shares["H"] == pytest.approx(0.208, abs=2e-3)
    assert shares["H+R"] == pytest.approx(0.792, abs=2e-3)
    assert shares["H+A"] == pytest.approx(0.0, abs=1e-6)
    assert shares["H+A+R"] == pytest.approx(0.0, abs=1e-6)


def test_dual_price_reproduces_worked_example(constrained_lp_solution):
    _, lambda_k, _ = constrained_lp_solution
    assert lambda_k == pytest.approx(0.0250, abs=2e-3)


def test_augmented_score_reverses_ranking(constrained_lp_solution):
    """Eq. 17: substituting lambda_k reverses the unconstrained winner
    (H+A+R) in favour of a tie between H and H+R -- "the mechanism the
    whole framework exists to produce" (Paper Sec. 5.3).
    """
    _, lambda_k, scv = constrained_lp_solution
    phi = {"H": 1.00, "H+A": 0.75, "H+R": 0.70, "H+A+R": 0.55}
    tilde = {m: scv[m] + 8 * phi[m] * lambda_k for m in TABLE3}

    assert tilde["H"] == pytest.approx(0.4937, abs=3e-3)
    assert tilde["H+R"] == pytest.approx(0.4937, abs=3e-3)
    assert tilde["H"] == pytest.approx(tilde["H+R"], abs=1e-6)
    assert tilde["H+A+R"] == pytest.approx(0.4863, abs=3e-3)
    assert tilde["H"] > tilde["H+A+R"] > tilde["H+A"]


def test_objective_cost_of_preservation(constrained_lp_solution):
    shares, _, scv = constrained_lp_solution
    unconstrained_annual = scv["H+A+R"] * 340
    constrained_annual = sum(shares[m] * scv[m] for m in TABLE3) * 340
    assert unconstrained_annual == pytest.approx(128.0, abs=0.5)
    assert constrained_annual == pytest.approx(116.1, abs=0.5)
    pct = (unconstrained_annual - constrained_annual) / unconstrained_annual * 100
    assert pct == pytest.approx(9.3, abs=0.3)


@pytest.mark.parametrize(
    "strategy,expected_c10",
    [
        ("automation_first", 100.0),
        ("cost_performance", 110.0),
        ("capability_matching", 65.0),
        ("civicworkos", 30.0 * (1 - math.exp(-10 / 3))),
        ("human_first", 5.0 * (1 - math.exp(-2 * 10))),
    ],
)
def test_analytic_debt_model_reproduces_fig3(strategy, expected_c10):
    c10 = accumulated_debt(10.0, FIG3_STRATEGIES[strategy])
    assert c10 == pytest.approx(expected_c10, abs=0.5)


def test_civicworkos_debt_saturates_others_do_not():
    """Paper Sec. 7.1: pi_inf=1 (CivicWorkOS, Human-First) saturates;
    pi_inf<1 (the other three) grows without bound as t increases.
    """
    saturating = accumulated_debt(100.0, FIG3_STRATEGIES["civicworkos"]) - accumulated_debt(
        50.0, FIG3_STRATEGIES["civicworkos"]
    )
    unbounded = accumulated_debt(100.0, FIG3_STRATEGIES["automation_first"]) - accumulated_debt(
        50.0, FIG3_STRATEGIES["automation_first"]
    )
    assert saturating < 1e-4
    assert unbounded == pytest.approx(500.0, abs=1e-6)
