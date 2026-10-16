"""Civic Automation Debt (CAD): Paper sec:problem, eq:cad.

    CAD_{i,m} = alpha * D_skill + beta * D_fall + gamma * D_acct
              + delta * D_dep   + epsilon * D_trans
              with  alpha + beta + gamma + delta + epsilon = 1

Purpose: price, as one scalar in [0,1], the deferred liability a mode
creates for a task. Computationally this is a dot product of two
five-vectors and is cheap; all of the difficulty is upstream, in
producing the five components (see civicworkos.market for the
estimators this repository invents, and docs/assumptions.md for why
they must be invented).

D_skill is the one component the paper defines as a computation
(D_skill = 1 - phi_m, eq:phi) rather than a prose description; the other
four are defined only in prose (the pre-release audit).
"""

from __future__ import annotations

from dataclasses import dataclass, fields

CAD_COMPONENT_FIELDS = ("D_skill", "D_fall", "D_acct", "D_dep", "D_trans")

_TOLERANCE = 1e-9


def _check_unit_interval(name: str, value: float) -> None:
    if not -_TOLERANCE <= value <= 1.0 + _TOLERANCE:
        raise ValueError(f"{name} must lie in [0, 1], got {value!r}")


def _check_weights_sum_to_one(name: str, values: tuple[float, ...]) -> None:
    total = sum(values)
    if abs(total - 1.0) > 1e-6:
        raise ValueError(f"{name} must sum to 1.0, got {values!r} (sum={total!r})")


@dataclass(frozen=True)
class DebtComponents:
    """The five debt components of eq:cad, each a scalar in [0,1].

    D_skill: skill-formation loss, defined as 1 - phi_m (eq:phi).
    D_fall: fractional reduction in fallback capacity if mode m were
        generalized across the domain. No estimator specified in the paper.
    D_acct: share of decision steps lacking a designated accountable
        human, weighted by crit_i. No decision-step decomposition specified.
    D_dep: share of automated inputs from a single vendor with no
        qualified alternative. No estimator specified.
    D_trans: projected share of affected workers without an identified
        reskilling pathway, computed per group before aggregation.
        Aggregation rule not specified.
    """

    D_skill: float
    D_fall: float
    D_acct: float
    D_dep: float
    D_trans: float

    def __post_init__(self) -> None:
        for f in fields(self):
            _check_unit_interval(f.name, getattr(self, f.name))

    def as_tuple(self) -> tuple[float, float, float, float, float]:
        return (self.D_skill, self.D_fall, self.D_acct, self.D_dep, self.D_trans)


@dataclass(frozen=True)
class DebtWeights:
    """alpha..epsilon of eq:cad. Paper default (sec:weights): (0.28, 0.22, 0.18, 0.12, 0.20)."""

    alpha: float
    beta: float
    gamma: float
    delta: float
    epsilon: float

    def __post_init__(self) -> None:
        _check_weights_sum_to_one("debt weights (alpha..epsilon)", self.as_tuple())

    def as_tuple(self) -> tuple[float, float, float, float, float]:
        return (self.alpha, self.beta, self.gamma, self.delta, self.epsilon)

    @classmethod
    def paper_default(cls) -> DebtWeights:
        """The illustrative defaults of Paper sec:weights. Not fitted estimates."""
        return cls(alpha=0.28, beta=0.22, gamma=0.18, delta=0.12, epsilon=0.20)


def civic_automation_debt(components: DebtComponents, weights: DebtWeights) -> float:
    """CAD_{i,m} (eq:cad): a convex combination of the five debt components."""
    return sum(w * c for w, c in zip(weights.as_tuple(), components.as_tuple()))
