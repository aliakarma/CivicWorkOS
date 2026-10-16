r"""Analytic model of debt accumulation: Paper sec:cadmodel, eq:cadode,
eq:cadmodel, tab:cadparams, fig:cad-trend.

Each of the five CAD components of eq:cad replenishes at its own rate towards
its own asymptote, with its own time constant (eq:cadode):

    Cdot_j(t) = c_j * [1 - pi_j(t)],   pi_j(t) = pi_j_inf * (1 - e^{-t/tau_j})

Integrating from pi_j(0) = 0 and weighting by the debt weights of eq:cad gives
the total trajectory (eq:cadmodel):

    C(t) = sum_j w_j * c_j * [ (1 - pi_j_inf)*t
                               + pi_j_inf * tau_j * (1 - e^{-t/tau_j}) ]

**This module previously implemented a superseded model and the change is
deliberate.** Earlier drafts carried a single scalar ``pi(t)``, described as
"the fraction of required developmental practice delivered", and plotted the
result as though it were CAD. That scalar is ``D_skill`` and nothing else, so
the plot labelled a one-component quantity with a five-component name. The
manuscript now says so in sec:cadmodel and models all five components
separately, because the mechanism driving each asymptote is different and the
differences are what the figure is for:

* ``skill`` is driven to one by the hard capability budget of eq:hcpb, with
  ``tau_skill = tau_k = 4.05`` years *derived* from prop:intake rather than
  assumed -- the only parameter in tab:cadparams that is not an illustrative
  choice;
* ``fall`` is driven to one by the resilience reserve of eq:res3r;
* ``acct`` is driven high but not to one by the oversight zones, which are
  revisable;
* ``trans`` is driven high by the just-transition constraint of eq:justtransition;
* ``dep`` -- vendor dependency -- **has no mechanism in this framework at all.**
  Its asymptote stays low and the component keeps accruing linearly.

That last point is why the five-component form matters. Under the one-component
model CivicWorkOS appeared to bound total debt. Under eq:cadmodel it does not:
its saturating components contribute a bounded 17.98 index units, but a linear
residual of 1.45 units a year accrues without limit, and 1.08 of those 1.45
units is vendor dependency. The honest claim is narrower than the earlier
presentation asserted -- a capability budget converts *skill* debt from
unbounded to bounded, and says nothing about the other four except through
weights that competing terms can outvote.

Nothing here is measured or simulated. The parameters of tab:cadparams are the
article's illustrative choices, tabulated so that every point of fig:cad-trend
is recoverable by substitution rather than asserted. The article's own caveat,
preserved here rather than smoothed over: the ordering of the curves is not
evidence, because it follows analytically from the parameters. The model's
empirical content lies entirely in whether each ``pi_j_inf`` can be driven to
its stated value in a real task population, and in what each ``tau_j`` actually
is.

The tab:cadparams values themselves are NOT duplicated in this module. They are
manuscript values, and the repository keeps exactly one copy of those, in
`Paper/Frontiers/audit_numbers.py`, reachable through `manuscript_values`. This
module implements the equation; see `tests/unit/test_analytic_debt_model.py` for
its mathematical properties and `tests/smoke/test_worked_example.py` for the
reproduction of fig:cad-trend.
"""

from __future__ import annotations

import math
from collections.abc import Mapping
from dataclasses import dataclass

#: The five components of eq:cad, in the order its weights are stated.
CAD_COMPONENTS = ("skill", "fall", "acct", "dep", "trans")


@dataclass(frozen=True)
class ComponentDebtParameters:
    """c_j, pi_j_inf, tau_j for ONE debt component under one strategy.

    c_j: accrual rate for this component at zero replenishment (index
        units/year). Unmeasured; tab:cadparams uses 10 throughout except for
        Cost/Performance, which carries c_acct = 14 and c_dep = 16.
    pi_inf: the replenished fraction this component converges to, in [0,1].
        Unmeasured, except that the framework's own constraints determine which
        components can be driven to one at all.
    tau: time constant, years. Unmeasured, except tau_skill = 4.05, derived
        from prop:intake. Must be > 0 when pi_inf > 0; tau = 0 is the
        instantaneous-replenishment limit, handled explicitly below.
    """

    c_j: float
    pi_inf: float
    tau: float

    def __post_init__(self) -> None:
        if self.c_j < 0:
            raise ValueError(f"c_j must be non-negative, got {self.c_j!r}")
        if not 0.0 <= self.pi_inf <= 1.0:
            raise ValueError(f"pi_inf must lie in [0,1], got {self.pi_inf!r}")
        if self.tau < 0:
            raise ValueError(f"tau must be non-negative, got {self.tau!r}")


def delivery_fraction(t: float, params: ComponentDebtParameters) -> float:
    """pi_j(t) = pi_j_inf * (1 - e^{-t/tau_j}) (eq:cadode). pi_j(0) = 0."""
    if t < 0:
        raise ValueError(f"t must be non-negative, got {t!r}")
    if params.tau == 0.0:
        # Instantaneous-replenishment limit: pi jumps to pi_inf for t > 0.
        return params.pi_inf if t > 0 else 0.0
    return params.pi_inf * (1.0 - math.exp(-t / params.tau))


def component_debt(t: float, params: ComponentDebtParameters) -> float:
    """The unweighted bracket of eq:cadmodel for one component.

    - pi_inf = 0: the linear term survives alone, so debt accrues at c_j
      without bound.
    - 0 < pi_inf < 1: linear at a reduced slope, still unbounded.
    - pi_inf = 1: no linear term; this component saturates at c_j * tau_j.
    """
    if t < 0:
        raise ValueError(f"t must be non-negative, got {t!r}")
    if params.tau == 0.0:
        # tau -> 0 limit of the closed form: saturation at t = 0+.
        return params.c_j * (1.0 - params.pi_inf) * t
    return params.c_j * (
        (1.0 - params.pi_inf) * t
        + params.pi_inf * params.tau * (1.0 - math.exp(-t / params.tau))
    )


def _check_weights(weights: Mapping[str, float]) -> None:
    total = sum(weights.values())
    if abs(total - 1.0) > 1e-6:
        raise ValueError(
            f"debt weights must sum to 1.0 (eq:cad), got sum={total!r}"
        )


def accumulated_debt(
    t: float,
    strategy: Mapping[str, ComponentDebtParameters],
    weights: Mapping[str, float],
) -> float:
    """C(t) (eq:cadmodel): the weighted sum over the five components.

    strategy: one component name -> its parameters, for every weighted
        component. A component present in `weights` but absent here is an
        error rather than a zero, because silently treating a missing
        component as debt-free is how a five-component model gets reported as
        though it were one.
    weights: alpha..epsilon of eq:cad, keyed by component name, summing to one.
    """
    if t < 0:
        raise ValueError(f"t must be non-negative, got {t!r}")
    _check_weights(weights)
    missing = set(weights) - set(strategy)
    if missing:
        raise ValueError(
            f"no parameters given for weighted debt component(s) {sorted(missing)}; "
            "eq:cadmodel sums over all five"
        )
    return sum(w * component_debt(t, strategy[j]) for j, w in weights.items())


def residual_slope(
    strategy: Mapping[str, ComponentDebtParameters],
    weights: Mapping[str, float],
) -> float:
    """The unbounded linear rate of eq:cadmodel: sum_j w_j c_j (1 - pi_j_inf).

    Zero iff every weighted component is fully replenished. For CivicWorkOS it
    is 1.45 index units a year, three-quarters of it vendor dependency, which
    is the figure's least flattering and most important number.
    """
    _check_weights(weights)
    return sum(
        w * strategy[j].c_j * (1.0 - strategy[j].pi_inf) for j, w in weights.items()
    )


def bounded_ceiling(
    strategy: Mapping[str, ComponentDebtParameters],
    weights: Mapping[str, float],
) -> float:
    """The bounded part of eq:cadmodel: sum_j w_j c_j pi_j_inf tau_j.

    The total debt a strategy accrues from its *saturating* components. Total
    debt is this plus `residual_slope` times t, so it is a ceiling only when the
    residual slope is zero. For CivicWorkOS it is 17.98 index units, 11.34 of
    that from skill formation -- the one component the capability budget governs.
    """
    _check_weights(weights)
    return sum(
        w * strategy[j].c_j * strategy[j].pi_inf * strategy[j].tau
        for j, w in weights.items()
    )


def strategy_from_table(
    row: Mapping[str, tuple[float, float, float]],
) -> dict[str, ComponentDebtParameters]:
    """Build a strategy from a tab:cadparams row of (c_j, pi_j_inf, tau_j).

    The tuple layout is the one `audit_numbers.CAD_STRATEGIES` uses, so the
    manuscript's table can drive this module without either side restating the
    other's numbers.
    """
    return {j: ComponentDebtParameters(*vals) for j, vals in row.items()}
