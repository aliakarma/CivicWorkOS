"""The re-solver must reproduce the article, not just run.

The printed rows below are copied from `tab:sensitivity` and the baseline from
`sec:worked` / `eq:lambdaworked`. If the manuscript's table changes, these fail
and the solver, not the table, is the first suspect to check.
"""

import pytest

from model import Inputs, psi_from_ratio, solve


def test_baseline_matches_the_article():
    r = solve()
    assert r.feasible
    assert r.B_k == pytest.approx(4976.64, abs=1e-6)
    assert r.required_share == pytest.approx(0.2962, abs=5e-5)
    assert r.lam == pytest.approx(0.045353, abs=1e-6)
    assert r.cost_of_preservation == pytest.approx(0.0434, abs=5e-5)
    assert r.mix["H+R/a1"] == pytest.approx(0.2830, abs=5e-4)
    assert r.mix["H+A+R/a1"] == pytest.approx(0.7170, abs=5e-4)
    assert r.tau_k == pytest.approx(4.05, abs=5e-3)
    assert r.n_hat_k == pytest.approx(14.0, abs=5e-2)
    assert r.certification_years == pytest.approx(1.2)


# (override, lead-only share, lambda, cost) copied from tab:sensitivity
ROWS = [
    (dict(h_raw=1200), 0.282, 0.0033, 0.0150),
    (dict(h_raw=1500), 0.102, 0.0033, 0.0188),
    (dict(r_k=0.06),   0.461, 0.0033, 0.0113),
    (dict(r_k=0.09),   0.192, 0.0033, 0.0169),
    (dict(eta_k=0.8),  0.282, 0.0033, 0.0150),
    (dict(phi={"H+A+R": 0.60}), 0.013, 0.0023, 0.0162),
    (dict(phi={"H+A+R": 0.70}), 0.154, 0.0009, 0.0063),
    (dict(psi_a1=0.67), 0.196, 0.0005, 0.0033),
]


@pytest.mark.parametrize("over,lead,lam,cost", ROWS)
def test_no_reversal_rows_of_the_sensitivity_table(over, lead, lam, cost):
    r = solve(Inputs.make(**over))
    assert r.feasible
    assert r.lead_only_share == pytest.approx(lead, abs=6e-4)
    assert r.lam == pytest.approx(lam, abs=6e-5)
    assert r.cost_of_preservation == pytest.approx(cost, abs=6e-5)


REVERSAL = [
    (dict(r_k=0.14), 0.0454, 0.0957),
    (dict(eta_k=1.4), 0.0454, 0.0957),
    (dict(phi={"H+R": 0.60}), 0.1515, 0.0960),
    (dict(phi={"H+R": 0.85}), 0.0188, 0.0302),
    (dict(phi={"H+A+R": 0.45}), 0.0241, 0.0700),
]


@pytest.mark.parametrize("over,lam,cost", REVERSAL)
def test_reversal_and_near_critical_rows(over, lam, cost):
    r = solve(Inputs.make(**over))
    assert r.feasible and r.lead_only_share == pytest.approx(0.0, abs=1e-9)
    assert r.lam == pytest.approx(lam, abs=6e-5)
    assert r.cost_of_preservation == pytest.approx(cost, abs=6e-5)


@pytest.mark.parametrize("over", [
    dict(h_raw=2400), dict(h_raw=3000), dict(eta_k=1.6),
    dict(phi={"H+R": 0.55}), dict(psi_a1=0.40),
])
def test_infeasible_rows(over):
    r = solve(Inputs.make(**over))
    assert not r.feasible and r.lam is None and r.n_hat_k is None


def test_feasibility_boundaries_of_proposition_feasibility():
    # critical values printed in tab:sensitivity: h_raw 2127, r_k 0.1418, psi 0.4232
    assert solve(Inputs.make(h_raw=2126.0)).feasible
    assert not solve(Inputs.make(h_raw=2128.0)).feasible
    assert solve(Inputs.make(r_k=0.1417)).feasible
    assert not solve(Inputs.make(r_k=0.1419)).feasible
    assert solve(Inputs.make(psi_a1=0.4233)).feasible
    assert not solve(Inputs.make(psi_a1=0.4231)).feasible


def test_psi_from_supervision_ratio_matches_the_articles_two_rosters():
    assert psi_from_ratio(1) == pytest.approx(0.5)        # roster a1
    assert psi_from_ratio(2) == pytest.approx(2 / 3)      # sec:shocks
    assert psi_from_ratio(0) == 0.0


def test_phi_H_cannot_be_overridden():
    with pytest.raises(ValueError):
        solve(Inputs.make(phi={"H": 0.9}))


def test_unknown_mode_rejected():
    with pytest.raises(ValueError):
        solve(Inputs.make(phi={"H+X": 0.5}))
