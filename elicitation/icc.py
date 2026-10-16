"""Intraclass correlation for the elicitation protocol (App. S4, `app:elicit-procedure`).

The protocol fixes the agreement statistic: the two-way random-effects
intraclass correlation coefficient ICC(2,k), the reliability of the *mean* of
k raters, with a pre-set acceptance threshold of 0.75. Definitions follow
Shrout and Fleiss (1979), Psychological Bulletin 86(2):420-428, the ICC(2,1) and ICC(2,k) definitions:

    ICC(2,1) = (MSR - MSE) / (MSR + (k-1) MSE + k (MSC - MSE) / n)
    ICC(2,k) = (MSR - MSE) / (MSR + (MSC - MSE) / n)

with n targets (rows), k raters (columns), and the mean squares from the
two-way ANOVA without replication.

Verified in `tests/test_icc.py` against the worked example in Shrout and Fleiss (1979).
"""

from __future__ import annotations

import numpy as np

ACCEPT = 0.75   # pre-set acceptance threshold, app:elicit-procedure


def mean_squares(x: np.ndarray) -> tuple[float, float, float, int, int]:
    """Row, column and residual mean squares of an n x k complete matrix."""
    x = np.asarray(x, dtype=float)
    if x.ndim != 2:
        raise ValueError("ratings must be an n_targets x k_raters matrix")
    n, k = x.shape
    if n < 2 or k < 2:
        raise ValueError(f"ICC needs at least 2 targets and 2 raters, got {n}x{k}")
    if not np.isfinite(x).all():
        raise ValueError("ratings contain NaN/inf; drop incomplete targets first")
    grand = x.mean()
    ss_rows = k * ((x.mean(axis=1) - grand) ** 2).sum()
    ss_cols = n * ((x.mean(axis=0) - grand) ** 2).sum()
    ss_total = ((x - grand) ** 2).sum()
    ss_err = ss_total - ss_rows - ss_cols
    msr = ss_rows / (n - 1)
    msc = ss_cols / (k - 1)
    mse = ss_err / ((n - 1) * (k - 1))
    return msr, msc, mse, n, k


def icc_2_1(x: np.ndarray) -> float:
    msr, msc, mse, n, k = mean_squares(x)
    return (msr - mse) / (msr + (k - 1) * mse + k * (msc - mse) / n)


def icc_2_k(x: np.ndarray) -> float:
    msr, msc, mse, n, _ = mean_squares(x)
    return (msr - mse) / (msr + (msc - mse) / n)


def bootstrap_icc_2_k(x: np.ndarray, reps: int = 2000, seed: int = 20261008,
                      alpha: float = 0.05) -> tuple[float, float]:
    """Percentile interval for ICC(2,k), resampling *targets* with replacement.

    Raters are the fixed panel whose agreement is being judged, so they are not
    resampled. Resamples whose targets are all identical give an undefined ICC
    and are skipped; the count skipped is not hidden because with fewer than
    about eight targets the interval is wide and should be read as such.
    """
    x = np.asarray(x, dtype=float)
    rng = np.random.default_rng(seed)
    n = x.shape[0]
    vals = []
    for _ in range(reps):
        sample = x[rng.integers(0, n, size=n)]
        try:
            v = icc_2_k(sample)
        except (ValueError, FloatingPointError, ZeroDivisionError):
            continue
        if np.isfinite(v):
            vals.append(v)
    if not vals:
        return float("nan"), float("nan")
    lo, hi = np.percentile(vals, [100 * alpha / 2, 100 * (1 - alpha / 2)])
    return float(lo), float(hi)


def meets_threshold(icc: float) -> bool:
    """The protocol's decision rule: a point value only if ICC(2,k) >= 0.75."""
    return bool(np.isfinite(icc) and icc >= ACCEPT)
