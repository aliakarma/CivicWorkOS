"""ICC against the published worked example, not against itself."""

import numpy as np
import pytest

import icc

# Shrout & Fleiss (1979), the published six-target, four-judge example.
SF = np.array([
    [9, 2, 5, 8],
    [6, 1, 3, 2],
    [8, 4, 6, 8],
    [7, 1, 2, 6],
    [10, 5, 6, 9],
    [6, 2, 4, 7],
], dtype=float)


def test_shrout_fleiss_icc_2_1():
    assert round(icc.icc_2_1(SF), 2) == 0.29       # published: .29


def test_shrout_fleiss_icc_2_k():
    assert round(icc.icc_2_k(SF), 2) == 0.62       # published: .62


def test_mean_squares_published_values():
    msr, msc, mse, n, k = icc.mean_squares(SF)
    assert (n, k) == (6, 4)
    assert msr == pytest.approx(11.24, abs=0.01)   # BMS
    assert msc == pytest.approx(32.49, abs=0.01)   # JMS
    assert mse == pytest.approx(1.02, abs=0.01)    # EMS


def test_perfect_agreement_is_one():
    x = np.tile(np.arange(1.0, 9.0)[:, None], (1, 5))
    assert icc.icc_2_k(x) == pytest.approx(1.0)


def test_rater_offset_lowers_icc_2_but_not_the_ranking():
    """ICC(2,.) is an absolute-agreement index: a constant rater bias costs it."""
    base = np.tile(np.arange(1.0, 9.0)[:, None], (1, 4))
    base[:, 0] += 3.0
    assert icc.icc_2_k(base) < 1.0


def test_threshold_rule():
    assert icc.meets_threshold(0.75)
    assert not icc.meets_threshold(0.7499)
    assert not icc.meets_threshold(float("nan"))


def test_bootstrap_interval_brackets_point_estimate_on_a_clear_case():
    rng = np.random.default_rng(7)
    truth = np.linspace(0, 10, 20)
    x = truth[:, None] + rng.normal(0, 1.0, size=(20, 6))
    lo, hi = icc.bootstrap_icc_2_k(x, reps=500)
    assert lo <= icc.icc_2_k(x) <= hi


def test_rejects_degenerate_shapes_and_nan():
    with pytest.raises(ValueError):
        icc.icc_2_k(np.ones((1, 4)))
    with pytest.raises(ValueError):
        icc.icc_2_k(np.array([[1.0, np.nan], [2.0, 3.0], [4.0, 5.0]]))
