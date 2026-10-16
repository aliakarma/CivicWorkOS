"""Human proficiency dynamics: acquisition through credited practice, decay
through gaps in human-led work.

These are the closed forms of the article's proficiency model (Section
"Human Proficiency as a Changing Resource"):

* the *asymptotic proficiency* a practitioner's logged practice supports,
  ``theta_inf(c) = 1 - (1 - theta_0) * exp(-c / c0)``, with ``c0`` chosen so
  that ``theta_inf(h_k) = theta_comp``: the records-based competence
  threshold ``c_w >= h_k`` of the original framework is exactly the point at
  which the learning curve crosses the competence level;
* the *current proficiency* after a gap of ``Delta`` working days without a
  human-led task, ``theta = f + (theta_inf - f) * exp(-Delta / tau)``, which
  decays toward a residual level ``f`` and is restored by human-led practice;
* the *recency interval* ``Delta_max = tau * ln((theta_inf - f) / (theta_comp - f))``,
  the longest gap that keeps a certified practitioner at or above the
  competence level (Proposition "Recency interval" in the article).

Everything here is deterministic arithmetic. The stochastic world that uses
it lives in :mod:`sim.protocol.engine`.
"""

from __future__ import annotations

import math


def learning_scale(h_k: float, theta_0: float, theta_comp: float) -> float:
    """Return ``c0`` such that ``theta_inf(h_k) == theta_comp``."""
    if not 0.0 <= theta_0 < theta_comp < 1.0:
        raise ValueError("need 0 <= theta_0 < theta_comp < 1")
    return h_k / math.log((1.0 - theta_0) / (1.0 - theta_comp))


def asymptotic_proficiency(c: float, h_k: float, theta_0: float, theta_comp: float,
                           rate_multiplier: float = 1.0) -> float:
    """Proficiency supported by ``c`` credited practice hours, with no gap.

    ``rate_multiplier`` scales the practitioner's learning rate; 1.0 is the
    nominal learner the certification scheme assumes.
    """
    c0 = learning_scale(h_k, theta_0, theta_comp) / rate_multiplier
    return 1.0 - (1.0 - theta_0) * math.exp(-max(c, 0.0) / c0)


def current_proficiency(theta_inf: float, gap_days: float, tau: float, residual: float) -> float:
    """Proficiency after ``gap_days`` without a human-led task."""
    if theta_inf <= residual:
        return theta_inf
    return residual + (theta_inf - residual) * math.exp(-max(gap_days, 0.0) / tau)


def recency_interval(theta_inf: float, tau: float, residual: float, theta_comp: float) -> float:
    """Longest gap (working days) keeping proficiency at or above ``theta_comp``.

    Returns 0.0 when ``theta_inf`` is already below the competence level: no
    recency rule can keep a practitioner current whose practice record does
    not support competence in the first place.
    """
    if not residual < theta_comp:
        raise ValueError("the residual level must lie below the competence level")
    if theta_inf < theta_comp:
        return 0.0
    return tau * math.log((theta_inf - residual) / (theta_comp - residual))


def retention_volume(n_certified: float, period_days: float, interval_days: float,
                     task_hours: float) -> float:
    """Human-led clock hours per period that keep ``n_certified`` practitioners current.

    One human-led task of ``task_hours`` at least every ``interval_days``
    working days for each certified practitioner.
    """
    if interval_days <= 0.0:
        return math.inf
    return n_certified * math.ceil(period_days / interval_days) * task_hours
