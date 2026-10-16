"""THE ORACLE: reproduces every checkable number in Paper sec:worked (the
worked bridge-inspection allocation) and sec:cadmodel / fig:cad-trend (the
analytic debt trajectory).

This is the only part of the article with a ground truth this repository can be
checked against -- see docs/reproducibility.md. If any test here fails,
something in `civicworkos.scoring`, `civicworkos.constraints.hcpb` or
`civicworkos.analytic` no longer matches the manuscript, and that is a release
blocker.

Every manuscript value is imported from `manuscript_values`, which re-exports
the single definition in `Paper/Frontiers/audit_numbers.py`. This file does not
restate a single input the article states. It holds only the *printed* values --
what a reader sees on the page -- because the question it exists to answer is
whether the library reproduces what was published.

That rule is the correction for finding N2 of the revision programme. Until
Phase 3 this file carried its own copy of the inputs, the article moved, and the
copy did not: the oracle asserted ``B_k = 2073.6`` against a manuscript that
computes 4976.64, scored four *execution* modes where the article scores eight
*staffed* modes, priced practice at 0.025 against a printed 0.0454, and checked
a one-component debt curve that eq:cadmodel has since replaced. All of it
passed. An oracle that certifies the wrong paper is worse than no oracle, so the
copy had to go rather than merely be corrected.
"""

from __future__ import annotations

import pulp
import pytest

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

# --- the printed values of tab:worked-terms -------------------------------
PRINTED_CAD = {
    "H/a0": 0.2800, "H/a1": 0.1400,
    "H+A/a0": 0.3816, "H+A/a1": 0.2766,
    "H+R/a0": 0.4260, "H+R/a1": 0.3280,
    "H+A+R/a0": 0.5004, "H+A+R/a1": 0.4234,
}
PRINTED_SCV = {
    "H/a0": 0.2324, "H/a1": 0.2391,
    "H+A/a0": 0.2783, "H+A/a1": 0.2773,
    "H+R/a0": 0.3108, "H+R/a1": 0.3082,
    "H+A+R/a0": 0.3426, "H+A+R/a1": 0.3355,
}

DEBT_WEIGHTS = DebtWeights(
    alpha=CAD_W["skill"],
    beta=CAD_W["fall"],
    gamma=CAD_W["acct"],
    delta=CAD_W["dep"],
    epsilon=CAD_W["trans"],
)


@pytest.fixture(scope="module")
def cad_scv_by_mode():
    """Score all eight staffed modes through the library.

    The staffed mode is the unit the article scores: an execution mode paired
    with a named roster at a declared career stage, written ``H+A+R/a1``. The
    stage sets psi_a, the developmental eligibility, which sets the credited
    share phi_m * psi_a that D_skill is defined against (eq:dskill). Scoring
    execution modes without a roster -- as this file once did -- makes the
    capability budget unsatisfiable at the article's parameters.
    """
    sw = ScoreWeights.paper_default()
    out = {}
    for name, m in MODES.items():
        dc = DebtComponents(
            D_skill=m.D_skill,
            D_fall=m.D_fall,
            D_acct=m.D_acct,
            D_dep=m.D_dep,
            D_trans=m.D_trans,
        )
        cad = civic_automation_debt(dc, DEBT_WEIGHTS)
        tv = TermVector(
            Q=m.Q, S=m.S, P=m.P, Eq_srv=m.Eq, Tr=m.Tr, Cost=m.Cost, En=m.En, Pr=m.Pr
        )
        out[name] = (cad, sustainable_civic_value(tv, cad, sw))
    return out


@pytest.mark.parametrize("mode,printed", sorted(PRINTED_CAD.items()))
def test_cad_reproduces_worked_terms(cad_scv_by_mode, mode, printed):
    cad, _ = cad_scv_by_mode[mode]
    assert cad == pytest.approx(printed, abs=1e-4)


@pytest.mark.parametrize("mode,printed", sorted(PRINTED_SCV.items()))
def test_scv_reproduces_worked_terms(cad_scv_by_mode, mode, printed):
    _, scv = cad_scv_by_mode[mode]
    assert scv == pytest.approx(printed, abs=1e-4)


def test_unconstrained_winner_to_five_decimals(cad_scv_by_mode):
    """The Abstract quotes the unconstrained optimum to five decimals."""
    _, scv = cad_scv_by_mode[WORKED["mode_unc"]]
    assert scv == pytest.approx(0.34261, abs=1e-5)


def test_weights_sum_to_one():
    assert sum(ScoreWeights.paper_default().as_tuple()) == pytest.approx(1.0, abs=1e-9)
    assert sum(CAD_W.values()) == pytest.approx(1.0, abs=1e-9)


# --- sec:binds, the capability budget ------------------------------------

@pytest.fixture(scope="module")
def budget():
    w = WORKED
    return capability_budget(
        HCPBParameters(
            N_k=w["N_k"], r_k=w["r_k"], h_k=w["h_k"], eta_k=w["eta_k"], B_k_min=w["B_min"]
        )
    )


def test_capability_budget_reproduces_worked_example(budget):
    """eq:bkworked: B_k = max(2000, 1.2 * 24 * 0.12 * 1440) = 4,976.64 hours."""
    assert budget == pytest.approx(4976.64, abs=1e-6)


def test_qualified_practice_conversion():
    """eq:hconv: h_k = learn_i * h_raw_k = 0.8 * 1800 = 1,440 hours."""
    w = WORKED
    assert w["learn"] * w["h_raw_k"] == pytest.approx(1440.0, abs=1e-6)


def test_required_mean_credited_share(budget):
    w = WORKED
    phi_k = w["n_k"] * w["ell_i"]
    assert phi_k == pytest.approx(16800.0, abs=1e-6)
    assert budget / phi_k == pytest.approx(0.2962, abs=1e-4)


def test_feasibility_headroom(budget):
    """prop:feasibility: the roster guard admits 5,880 hours against a
    4,976.64-hour budget, so the instance is feasible with ~15% headroom."""
    w = WORKED
    admissible = w["n_k"] * w["ell_i"] * w["zeta_bar"]
    assert admissible == pytest.approx(5880.0, abs=1e-6)
    assert budget < admissible


# --- sec:solving, the constrained optimum --------------------------------

@pytest.fixture(scope="module")
def lp_solution(cad_scv_by_mode, budget):
    """Solve the worked instance as an LP and keep the dual of the budget."""
    scv = {name: s for name, (_, s) in cad_scv_by_mode.items()}
    w = WORKED
    ell = w["ell_i"]

    x = {name: pulp.LpVariable(f"x_{i}", 0, 1) for i, name in enumerate(MODES)}
    prob = pulp.LpProblem("worked_example", pulp.LpMaximize)
    prob += pulp.lpSum(scv[name] * x[name] for name in MODES)
    prob += pulp.lpSum(x[name] for name in MODES) == 1, "assignment"
    prob += (
        pulp.lpSum(ell * MODES[name].credited * x[name] for name in MODES)
        >= budget / w["n_k"],
        "hcpb",
    )
    prob.solve(pulp.PULP_CBC_CMD(msg=0))
    assert pulp.LpStatus[prob.status] == "Optimal"
    shares = {name: (x[name].value() or 0.0) for name in MODES}
    return shares, abs(prob.constraints["hcpb"].pi), scv


def test_constrained_optimum_is_a_two_mode_mix(lp_solution):
    """tab:worked-mix: 28.30% on the lead-only roster, 71.70% on the dual."""
    shares, _, _ = lp_solution
    w = WORKED
    assert shares[w["mode_lo"]] == pytest.approx(0.2830, abs=5e-4)
    assert shares[w["mode_hi"]] == pytest.approx(0.7170, abs=5e-4)
    for name in MODES:
        if name not in (w["mode_lo"], w["mode_hi"]):
            assert shares[name] == pytest.approx(0.0, abs=1e-6)


def test_constrained_mean_objective(lp_solution):
    shares, _, scv = lp_solution
    mean = sum(shares[n] * scv[n] for n in MODES)
    assert mean == pytest.approx(0.327750, abs=1e-5)


def test_optimum_meets_the_budget_exactly(lp_solution):
    """The budget binds, so the mix delivers the required share and no more."""
    shares, _, _ = lp_solution
    assert sum(shares[n] * MODES[n].credited for n in MODES) == pytest.approx(
        0.2962, abs=1e-4
    )


def test_integrality_straddles_the_budget(budget):
    """sec:solving: 2,100 tasks do not divide into the mix, so the integer
    optimum is 595 tasks on the lead-only roster -- 594 falls 0.24 hours short."""
    w = WORKED
    ell, n_k = w["ell_i"], w["n_k"]
    lo, hi = MODES[w["mode_lo"]], MODES[w["mode_hi"]]

    def hours(n: int) -> float:
        return n * ell * lo.credited + (n_k - n) * ell * hi.credited

    assert hours(594) == pytest.approx(4976.40, abs=1e-6)
    assert hours(595) == pytest.approx(4977.00, abs=1e-6)
    assert hours(594) < budget <= hours(595)
    assert budget - hours(594) == pytest.approx(0.24, abs=1e-6)


def test_capability_price_reproduces_worked_example(lp_solution):
    """eq:lambdaworked: the dual of the capability budget is 0.045353
    objective units per qualified-practice hour, quoted as 0.0454."""
    _, lambda_k, _ = lp_solution
    assert lambda_k == pytest.approx(0.045353, abs=1e-6)
    assert round(lambda_k, 4) == pytest.approx(0.0454, abs=1e-9)


def test_augmented_score_reverses_the_ranking(lp_solution):
    """eq:augworked, the mechanism the whole framework exists to produce.

    At lambda_k the two active staffed modes tie and both beat the
    unconstrained winner. The tie is exact rather than approximate, because
    lambda_k is *defined* by it -- an earlier draft printed the two augmented
    values as differing in the fourth decimal, which was an artifact of
    substituting a rounded lambda_k rather than a real asymmetry.
    """
    shares, lambda_k, scv = lp_solution
    w = WORKED
    ell = w["ell_i"]
    aug = {n: scv[n] + lambda_k * ell * MODES[n].credited for n in MODES}

    assert aug[w["mode_lo"]] == pytest.approx(0.435229, abs=1e-6)
    assert aug[w["mode_hi"]] == pytest.approx(0.435229, abs=1e-6)
    assert aug[w["mode_lo"]] == pytest.approx(aug[w["mode_hi"]], abs=1e-9)
    assert aug[w["mode_lo"]] > aug[w["mode_unc"]]


def test_cost_of_preservation(lp_solution, budget):
    """sec:costs: preserving capability costs 4.34% of annual objective value."""
    shares, _, scv = lp_solution
    w = WORKED
    n_k = w["n_k"]
    unconstrained = scv[w["mode_unc"]] * n_k
    constrained = sum(shares[n] * scv[n] for n in MODES) * n_k
    assert unconstrained == pytest.approx(719.5, abs=0.05)
    assert constrained == pytest.approx(688.3, abs=0.05)
    assert (unconstrained - constrained) / unconstrained == pytest.approx(0.0434, abs=5e-5)
    # The average price per hour sits below the marginal price, as convexity requires.
    assert (unconstrained - constrained) / budget < 0.045353


def test_replenishment_exceeds_attrition(budget):
    """sec:costs: 3.456 competent-equivalents a year against attrition of 2.88."""
    w = WORKED
    assert budget / w["h_k"] == pytest.approx(3.456, abs=1e-6)
    assert w["N_k"] * w["r_k"] == pytest.approx(2.88, abs=1e-9)
    assert budget / w["h_k"] > w["N_k"] * w["r_k"]


# --- sec:pipeline, the intake requirement --------------------------------

def test_intake_requirement(lp_solution):
    """prop:intake, the article's most citable result.

    Machine-assisted supervised practice dilutes a trainee's qualifying hours,
    so time to competence stretches from the 1.2 years the certification
    requirement implies to 4.05, and a city sizing intake from certification
    hours provisions four posts where fourteen are required.
    """
    shares, _, _ = lp_solution
    w = WORKED
    phi_bar = sum(shares[n] * MODES[n].phi for n in MODES)
    assert phi_bar == pytest.approx(0.5925, abs=5e-5)

    naive = w["h_raw_k"] / w["Theta_k"]
    tau_k = naive / (phi_bar * w["omega_bar"])
    assert naive == pytest.approx(1.20, abs=1e-9)
    assert tau_k == pytest.approx(4.05, abs=5e-3)
    assert tau_k / naive == pytest.approx(3.38, abs=5e-3)

    n_hat = w["eta_k"] * w["N_k"] * w["r_k"] * tau_k
    assert n_hat == pytest.approx(14.0, abs=5e-2)
    # An independent route to the same number: trainee clock hours / Theta_k.
    assert w["n_k"] * w["d_i"] / w["Theta_k"] == pytest.approx(14.0, abs=1e-9)
    # Sizing intake from the certification figure alone gives four posts.
    assert w["eta_k"] * w["N_k"] * w["r_k"] * naive == pytest.approx(4.0, abs=0.15)


# --- sec:whoworked, the access constraint --------------------------------

def test_access_constraint_multiplies_protected_hours(budget):
    """sec:whoworked: 622 hours composition-blind against 1,344 required."""
    w = WORKED
    blind = w["incumbent_women"] * budget
    floor = w["pool_women"] - w["epsilon_k"]
    assert blind == pytest.approx(622.08, abs=0.01)
    assert floor == pytest.approx(0.27, abs=1e-9)
    assert floor * budget == pytest.approx(1344.0, abs=0.5)
    assert (floor * budget) / blind == pytest.approx(2.16, abs=5e-3)


# --- sec:cadmodel, the debt trajectory -----------------------------------

@pytest.fixture(scope="module")
def strategies():
    return {name: strategy_from_table(row) for name, row in CAD_STRATEGIES.items()}


@pytest.mark.parametrize("name,printed", sorted(CAD_PRINTED.items()))
def test_debt_trajectory_reproduces_cadparams(strategies, name, printed):
    """tab:cadparams: both computed columns, for all six strategies."""
    printed_slope, printed_c10 = printed
    s = strategies[name]
    assert residual_slope(s, CAD_W) == pytest.approx(printed_slope, abs=5e-3)
    assert accumulated_debt(10.0, s, CAD_W) == pytest.approx(printed_c10, abs=5e-3)


def test_no_strategy_bounds_total_debt(strategies):
    """sec:cadmodel, the finding unfavourable to the framework.

    CivicWorkOS does NOT bound total debt. Its saturating components contribute
    a bounded 17.98 index units, 11.34 of that from skill formation, but a
    linear residual of 1.45 units a year accrues without limit, 1.08 of it
    vendor dependency -- which the allocation mechanism does not control. The
    one-component model this test replaced made the curve appear to saturate.
    """
    for name, s in strategies.items():
        assert residual_slope(s, CAD_W) > 0.0, f"{name} should not saturate"

    cw = strategies["CivicWorkOS"]
    assert bounded_ceiling(cw, CAD_W) == pytest.approx(17.98, abs=1e-2)
    skill = cw["skill"]
    assert CAD_W["skill"] * skill.c_j * skill.pi_inf * skill.tau == pytest.approx(
        11.34, abs=5e-3
    )
    dep = cw["dep"]
    assert CAD_W["dep"] * dep.c_j * (1.0 - dep.pi_inf) == pytest.approx(1.08, abs=5e-3)
    assert residual_slope(cw, CAD_W) == pytest.approx(1.45, abs=5e-3)


def test_human_first_beats_civicworkos_for_thirteen_years(strategies):
    """sec:cadmodel: the curves cross at t = 13.23 at 36.73 index units.

    The article reports this against itself rather than burying it: a strategy
    that keeps humans on everything accrues less total debt early, because it
    replenishes fallback, accountability, dependency and transition immediately
    while CivicWorkOS is still filling its pipeline over a 4.05-year constant.
    """
    cw, hf = strategies["CivicWorkOS"], strategies["Human-First"]

    assert accumulated_debt(10.0, hf, CAD_W) < accumulated_debt(10.0, cw, CAD_W)
    assert accumulated_debt(20.0, hf, CAD_W) > accumulated_debt(20.0, cw, CAD_W)
    assert accumulated_debt(20.0, cw, CAD_W) == pytest.approx(46.89, abs=5e-3)
    assert accumulated_debt(20.0, hf, CAD_W) == pytest.approx(52.89, abs=5e-3)

    lo, hi = 1.0, 60.0
    for _ in range(200):
        mid = 0.5 * (lo + hi)
        if accumulated_debt(mid, hf, CAD_W) - accumulated_debt(mid, cw, CAD_W) < 0.0:
            lo = mid
        else:
            hi = mid
    t_cross = 0.5 * (lo + hi)
    assert t_cross == pytest.approx(13.23, abs=5e-3)
    assert accumulated_debt(t_cross, cw, CAD_W) == pytest.approx(36.73, abs=5e-3)
