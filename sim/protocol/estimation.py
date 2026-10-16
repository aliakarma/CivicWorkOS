"""Adaptive learning mechanism: Gaussian beliefs over task requirements and
participant capabilities, updated from task outcomes and, where available,
multimodal observations.

The outcome model is the logistic link of the article's adaptive-learning
section, ``P(success) = sigmoid(gamma * z)`` with ``z`` a linear combination
of independent latent quantities (human proficiency offsets, machine
reliability, task requirement). Beliefs are updated by assumed-density
filtering: the logistic likelihood is replaced by its probit approximation
``Phi(kappa * gamma * z)`` with ``kappa = sqrt(pi / 8)``, and the posterior is
projected back onto independent Gaussians by moment matching (Minka, 2001),
the same update used by Bayesian rating systems (Glickman, 1999). Direct
observations of a latent quantity (a skill probe, a telemetry health index,
a physiological workload estimate) enter through a scalar Kalman update.

All functions are pure; callers own the belief state.
"""

from __future__ import annotations

import math
from collections.abc import Sequence

KAPPA = math.sqrt(math.pi / 8.0)
_SQRT2 = math.sqrt(2.0)
_INV_SQRT2PI = 1.0 / math.sqrt(2.0 * math.pi)


def _pdf(t: float) -> float:
    return _INV_SQRT2PI * math.exp(-0.5 * t * t)


def _cdf(t: float) -> float:
    return 0.5 * (1.0 + math.erf(t / _SQRT2))


def sigmoid(x: float) -> float:
    if x >= 0:
        return 1.0 / (1.0 + math.exp(-x))
    e = math.exp(x)
    return e / (1.0 + e)


def predictive_success(mean: float, var: float, gamma: float) -> float:
    """Posterior-predictive success probability (probit-moderated logistic)."""
    return sigmoid(gamma * mean / math.sqrt(1.0 + math.pi * gamma * gamma * var / 8.0))


def lower_confidence_success(mean: float, var: float, gamma: float, z: float = 1.645) -> float:
    """Success probability at the lower ``z``-sigma bound of the linear predictor."""
    return sigmoid(gamma * (mean - z * math.sqrt(max(var, 0.0))))


def adf_bernoulli(means: Sequence[float], variances: Sequence[float], coefs: Sequence[float],
                  offset: float, outcome: bool, gamma: float) -> tuple[list[float], list[float]]:
    """Assumed-density-filtering update for one Bernoulli outcome.

    The linear predictor is ``z = offset + sum_j coefs[j] * x_j`` with
    independent beliefs ``x_j ~ N(means[j], variances[j])``. Returns the
    updated means and variances.
    """
    m = offset + sum(a * mu for a, mu in zip(coefs, means))
    v = sum(a * a * s2 for a, s2 in zip(coefs, variances))
    k = KAPPA * gamma
    denom = math.sqrt(1.0 + k * k * v)
    sign = 1.0 if outcome else -1.0
    t = sign * k * m / denom
    cdf = max(_cdf(t), 1e-12)
    vt = _pdf(t) / cdf
    wt = vt * (vt + t)
    new_means = [mu + sign * a * s2 * k * vt / denom for mu, s2, a in zip(means, variances, coefs)]
    new_vars = [max(s2 * (1.0 - a * a * s2 * k * k * wt / (1.0 + k * k * v)), 1e-8)
                for s2, a in zip(variances, coefs)]
    return new_means, new_vars


def kalman_scalar(mean: float, var: float, observation: float, noise_var: float) -> tuple[float, float]:
    """Scalar Kalman update for a direct noisy observation of a latent quantity."""
    gain = var / (var + noise_var)
    return mean + gain * (observation - mean), (1.0 - gain) * var
