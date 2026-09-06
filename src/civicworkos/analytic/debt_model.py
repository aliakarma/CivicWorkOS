r"""Analytic model of debt accumulation: Paper Sec. 7.1, Eq. 21, Fig. 3.

    Cdot(t) = c_0 * [1 - pi(t)],   pi(t) = pi_inf * (1 - e^{-t/tau})

    => C(t) = c_0 * [ (1 - pi_inf)*t + pi_inf*tau*(1 - e^{-t/tau}) ]     (Eq. 21)

This is NOT experimental data. The paper's own status box (Sec. 7)
states plainly: "Fig. 3 is the graph of Eq. (21) at the stated
parameters, so it illustrates what the model implies and establishes
nothing about what a city would experience." The functions below
compute the closed form and are exercised against the five captioned
Fig. 3 parameter sets in tests/smoke/test_worked_example.py.

The paper's own caveat, preserved here rather than smoothed over: "The
ordering of the curves is not evidence, because it follows analytically
from the parameters ... The model's empirical content lies entirely in
whether pi_inf can be driven to one in a real task population ..., and
in what tau actually is."

[CRIT, report Sec. 20.3] Eq. 21 has ONE driver (pi, the unmet
developmental-practice fraction) but its output is labelled "accumulated
Civic Automation Debt", which Eq. 2 defines over FIVE components. The
HCPB drives pi_inf -> 1 for D_skill (and indirectly D_fall); it does
nothing for D_dep (vendor concentration). Total CAD should therefore
NOT saturate under CivicWorkOS the way Eq. 21 alone implies. This
module implements Eq. 21 exactly as specified and does not silently
"fix" this over-claim; see docs/assumptions.md A9 and
docs/paper_implementation_mapping.md for the caveat carried alongside it.
"""

from __future__ import annotations

import math
from dataclasses import dataclass


@dataclass(frozen=True)
class StrategyDebtParameters:
    """c_0, pi_inf, tau for one allocation strategy's analytic debt curve.

    c_0: debt accrual rate at zero delivery (index units/year). Unmeasured.
    pi_inf: delivery fraction the strategy converges to, in [0,1]. Unmeasured.
    tau: onboarding time constant, years. Unmeasured; must be > 0 if pi_inf > 0
        (tau -> 0 is the instantaneous-onboarding limit, handled separately).
    """

    c_0: float
    pi_inf: float
    tau: float

    def __post_init__(self) -> None:
        if self.c_0 < 0:
            raise ValueError(f"c_0 must be non-negative, got {self.c_0!r}")
        if not 0.0 <= self.pi_inf <= 1.0:
            raise ValueError(f"pi_inf must lie in [0,1], got {self.pi_inf!r}")
        if self.tau < 0:
            raise ValueError(f"tau must be non-negative, got {self.tau!r}")


def delivery_fraction(t: float, params: StrategyDebtParameters) -> float:
    """pi(t) = pi_inf * (1 - e^{-t/tau}). pi(0) = 0 by construction."""
    if t < 0:
        raise ValueError(f"t must be non-negative, got {t!r}")
    if params.tau == 0.0:
        # Instantaneous-onboarding limit: pi jumps to pi_inf immediately for t > 0.
        return params.pi_inf if t > 0 else 0.0
    return params.pi_inf * (1.0 - math.exp(-t / params.tau))


def accumulated_debt(t: float, params: StrategyDebtParameters) -> float:
    """C(t) (Eq. 21), the closed-form integral of Cdot(t) = c_0*[1 - pi(t)].

    - pi_inf = 0: linear term survives, exponential vanishes -> debt
      accrues linearly and without bound: C(t) = c_0 * t.
    - 0 < pi_inf < 1: linear term at reduced slope, still unbounded.
    - pi_inf = 1: no linear term; debt saturates at c_0*tau.
    """
    if t < 0:
        raise ValueError(f"t must be non-negative, got {t!r}")
    if params.tau == 0.0:
        # tau -> 0 limit of the closed form: instantaneous saturation at t=0+.
        return params.c_0 * (1.0 - params.pi_inf) * t
    return params.c_0 * (
        (1.0 - params.pi_inf) * t + params.pi_inf * params.tau * (1.0 - math.exp(-t / params.tau))
    )


# Fig. 3 caption parameters, verified in report Sec. 13.2 to reproduce the
# plotted curves exactly. Reproduced here as fixtures for tests/smoke, NOT
# as measured data -- these are the paper's own illustrative choices.
FIG3_STRATEGIES: dict[str, StrategyDebtParameters] = {
    "automation_first": StrategyDebtParameters(c_0=10.0, pi_inf=0.0, tau=0.0),
    "cost_performance": StrategyDebtParameters(c_0=11.0, pi_inf=0.0, tau=0.0),
    "capability_matching": StrategyDebtParameters(c_0=10.0, pi_inf=0.35, tau=0.0),
    "civicworkos": StrategyDebtParameters(c_0=10.0, pi_inf=1.0, tau=3.0),
    "human_first": StrategyDebtParameters(c_0=10.0, pi_inf=1.0, tau=0.5),
}
