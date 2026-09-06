"""Unit tests for civicworkos.scoring: Eq. 2 (CAD) and Eq. 15 (SCV)."""

from __future__ import annotations

import pytest

from civicworkos.scoring.cad import DebtComponents, DebtWeights, civic_automation_debt
from civicworkos.scoring.scv import ScoreWeights, TermVector, sustainable_civic_value


def test_debt_weights_must_sum_to_one():
    with pytest.raises(ValueError, match="sum to 1"):
        DebtWeights(alpha=0.5, beta=0.5, gamma=0.5, delta=0.0, epsilon=0.0)


def test_score_weights_must_sum_to_one():
    with pytest.raises(ValueError, match="sum to 1.0"):
        ScoreWeights(
            w1_quality=0.5, w2_safety=0.5, w3_productivity=0.5, w4_equity=0,
            w5_trust=0, w6_cost=0, w7_energy=0, w8_privacy=0, w9_cad=0,
        )


def test_debt_component_out_of_range_rejected():
    with pytest.raises(ValueError, match=r"\[0, 1\]"):
        DebtComponents(D_skill=1.5, D_fall=0, D_acct=0, D_dep=0, D_trans=0)


def test_term_vector_out_of_range_rejected():
    with pytest.raises(ValueError, match=r"\[0, 1\]"):
        TermVector(Q=-0.1, S=0.5, P=0.5, Eq_srv=0.5, Tr=0.5, Cost=0.5, En=0.5, Pr=0.5)


def test_cad_all_zero_components_gives_zero_debt():
    dw = DebtWeights.paper_default()
    dc = DebtComponents(D_skill=0, D_fall=0, D_acct=0, D_dep=0, D_trans=0)
    assert civic_automation_debt(dc, dw) == pytest.approx(0.0)


def test_cad_all_one_components_gives_unit_debt():
    dw = DebtWeights.paper_default()
    dc = DebtComponents(D_skill=1, D_fall=1, D_acct=1, D_dep=1, D_trans=1)
    assert civic_automation_debt(dc, dw) == pytest.approx(1.0)


def test_scv_penalizes_cad():
    """Holding all flow terms fixed, higher CAD must strictly reduce SCV
    (Eq. 15's -w9*CAD term) -- the mechanism's whole reason to exist.
    """
    sw = ScoreWeights.paper_default()
    tv = TermVector(Q=0.8, S=0.8, P=0.8, Eq_srv=0.8, Tr=0.8, Cost=0.2, En=0.2, Pr=0.2)
    low_cad_scv = sustainable_civic_value(tv, cad=0.0, weights=sw)
    high_cad_scv = sustainable_civic_value(tv, cad=1.0, weights=sw)
    assert low_cad_scv > high_cad_scv
    assert (low_cad_scv - high_cad_scv) == pytest.approx(sw.w9_cad)


def test_effective_weights_match_table4():
    """Paper Table 4 prints these rounded to 3 decimals (e.g. 0.22*0.28 =
    0.0616 displays as 0.062). This test checks the EXACT arithmetic our
    code performs, with a tolerance wide enough to cover the paper's own
    rounding, rather than asserting equality with the rounded display."""
    sw = ScoreWeights.paper_default()
    dw = DebtWeights.paper_default()
    effective = sw.effective_weights(dw)
    assert effective["safety"] == pytest.approx(0.180)
    assert effective["service_quality"] == pytest.approx(0.150)
    assert effective["productivity"] == pytest.approx(0.140)
    assert effective["service_equity_residents"] == pytest.approx(0.100)
    assert effective["operating_cost"] == pytest.approx(0.080)
    assert effective["skill_formation"] == pytest.approx(0.0616, abs=1e-6)
    assert effective["trust"] == pytest.approx(0.050)
    assert effective["privacy_risk"] == pytest.approx(0.050)
    assert effective["fallback_capacity"] == pytest.approx(0.0484, abs=1e-6)
    assert effective["labour_transition_burden"] == pytest.approx(0.044, abs=1e-6)
    assert effective["accountability"] == pytest.approx(0.0396, abs=1e-6)
    assert effective["energy"] == pytest.approx(0.030)
    assert effective["vendor_dependency"] == pytest.approx(0.0264, abs=1e-6)
    assert sum(effective.values()) == pytest.approx(1.000, abs=1e-9)
    # Table 4's headline claim: the deferred (debt) block is the single
    # largest share of the objective, larger than productivity (0.14).
    deferred_block = (
        effective["skill_formation"] + effective["fallback_capacity"]
        + effective["accountability"] + effective["vendor_dependency"]
        + effective["labour_transition_burden"]
    )
    assert deferred_block == pytest.approx(0.22, abs=1e-9)
    assert deferred_block > effective["productivity"]
