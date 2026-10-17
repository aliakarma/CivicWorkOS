"""Unit tests for the proficiency model and the adaptive learning updates
(article Sections "Human Proficiency as a Changing Resource" and
"Adaptive Learning Mechanism")."""

from __future__ import annotations

import math

import pytest

from sim.protocol.analysis import holm, rank_biserial
from sim.protocol.estimation import (
    adf_bernoulli,
    kalman_scalar,
    lower_confidence_success,
    predictive_success,
)
from sim.protocol.skill import (
    asymptotic_proficiency,
    current_proficiency,
    learning_scale,
    recency_interval,
    retention_volume,
)

TH0, THC, THR = 0.30, 0.70, 0.45


def test_learning_curve_crosses_competence_exactly_at_certification_hours():
    for h in (400.0, 600.0, 1440.0):
        assert asymptotic_proficiency(h, h, TH0, THC) == pytest.approx(THC, abs=1e-12)


def test_learning_curve_starts_at_novice_level_and_saturates():
    assert asymptotic_proficiency(0.0, 600.0, TH0, THC) == pytest.approx(TH0)
    assert asymptotic_proficiency(1e6, 600.0, TH0, THC) == pytest.approx(1.0)


def test_faster_learner_reaches_competence_sooner():
    slow = asymptotic_proficiency(300.0, 600.0, TH0, THC, rate_multiplier=0.8)
    fast = asymptotic_proficiency(300.0, 600.0, TH0, THC, rate_multiplier=1.25)
    assert fast > slow


def test_decay_is_monotone_and_bounded_by_residual():
    vals = [current_proficiency(0.9, g, 120.0, THR) for g in (0, 10, 100, 1000)]
    assert vals == sorted(vals, reverse=True)
    assert vals[0] == pytest.approx(0.9)
    assert vals[-1] > THR


def test_recency_interval_matches_worked_example():
    # Section "What Preservation Costs": c = 2 h_k gives 0.8714 and 62.7 days.
    th_inf = asymptotic_proficiency(2 * 1440.0, 1440.0, TH0, THC)
    assert th_inf == pytest.approx(0.8714, abs=5e-5)
    assert recency_interval(th_inf, 120.0, THR, THC) == pytest.approx(62.7, abs=0.05)


def test_recency_interval_is_the_exact_lapse_point():
    th_inf, tau = 0.88, 100.0
    e_max = recency_interval(th_inf, tau, THR, THC)
    assert current_proficiency(th_inf, e_max, tau, THR) == pytest.approx(THC, abs=1e-12)
    assert current_proficiency(th_inf, e_max + 1, tau, THR) < THC


def test_barely_certified_practitioner_has_no_recency_margin():
    assert recency_interval(THC, 120.0, THR, THC) == pytest.approx(0.0)
    assert recency_interval(0.6, 120.0, THR, THC) == 0.0


def test_retention_volume_counts_one_task_per_interval_per_practitioner():
    assert retention_volume(10, 250, 62.7, 1.0) == 10 * math.ceil(250 / 62.7)
    assert retention_volume(10, 250, 0.0, 1.0) == math.inf


def test_learning_scale_rejects_inconsistent_levels():
    with pytest.raises(ValueError):
        learning_scale(600.0, 0.8, 0.7)


def test_adf_success_raises_means_and_shrinks_variances():
    means, variances = [0.0, 0.5], [0.01, 0.01]
    new_m, new_v = adf_bernoulli(means, variances, [1.0, -1.0], 0.1, True, 8.0)
    assert new_m[0] > means[0] and new_m[1] < means[1]
    assert all(nv < v for nv, v in zip(new_v, variances))


def test_adf_failure_lowers_proficiency_belief():
    new_m, _ = adf_bernoulli([0.0], [0.01], [1.0], 0.2, False, 8.0)
    assert new_m[0] < 0.0


def test_adf_credit_follows_coefficient_and_uncertainty():
    # the less certain, more heavily weighted factor absorbs more of the update
    new_m, _ = adf_bernoulli([0.0, 0.0], [0.04, 0.0025], [1.0, 1.0], -0.1, False, 8.0)
    assert abs(new_m[0]) > abs(new_m[1])


def test_kalman_update_moves_toward_observation_by_gain():
    m, v = kalman_scalar(0.5, 0.01, 0.7, 0.01)
    assert m == pytest.approx(0.6)
    assert v == pytest.approx(0.005)


def test_lower_confidence_success_is_below_predictive():
    assert lower_confidence_success(0.2, 0.004, 8.0) < predictive_success(0.2, 0.004, 8.0)


def test_holm_is_monotone_and_capped():
    adj = holm([0.01, 0.04, 0.03, 0.5])
    assert adj == [0.04, 0.09, 0.09, 0.5]
    assert all(a <= 1.0 for a in adj)


def test_rank_biserial_extremes():
    import numpy as np

    assert rank_biserial(np.array([1.0, 2.0, 3.0])) == 1.0
    assert rank_biserial(np.array([-1.0, -2.0])) == -1.0
    assert rank_biserial(np.array([0.0, 0.0])) == 0.0
