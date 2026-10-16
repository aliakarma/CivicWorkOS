"""Urban Task Digital Twin: task encoding and developmental content.

Implements Paper sec:layer1, eq:task and eq:ell:

    T_i = { cog_i, phy_i, emp_i, risk_i, auth_i, priv_i, urg_i, learn_i, crit_i ; d_i }   (eq:task)
    ell_i = learn_i * d_i    [qualified-practice hours]                                   (eq:ell)

eq:ell is the paper's central unit conversion: it turns a normative
judgement about developmental value (learn_i, in [0,1]) into a
budgetable quantity in hours (ell_i). Six of the nine dimensions of
eq:task have a named data source in the paper; `learn_i` does not -- see
docs/assumptions.md, item A2.
"""

from __future__ import annotations

from dataclasses import dataclass

_DEMAND_FIELDS = ("cog", "phy", "emp", "risk", "auth", "priv", "urg", "learn", "crit")


def _validate_unit_interval(name: str, value: float) -> float:
    if not 0.0 <= value <= 1.0:
        raise ValueError(f"{name} must lie in [0, 1], got {value!r}")
    return float(value)


@dataclass(frozen=True)
class TaskProfile:
    """One unit of municipal work, encoded per Paper eq:task.

    Attributes
    ----------
    task_id: opaque identifier for audit-trail linkage.
    service: sigma(i), the service map -- an input, not a decision (Paper sec:problem).
    domain: kappa(i), the capability-domain map -- an input, not a decision.
    cog, phy, emp: cognitive, physical, empathy/social demand, each in [0,1].
    risk: safety risk, in [0,1].
    auth, priv: legal-authority requirement and privacy sensitivity, in [0,1].
        The paper states these are policy outputs (from the Policy Digital
        Twin's rule encoding), not independent ratings.
    urg: urgency, in [0,1].
    learn: human learning value ("structured judgment of developmental
        value for a junior practitioner"), in [0,1]. No elicitation
        instrument is specified in the paper -- see docs/assumptions.md A2.
    crit: criticality tier, in [0,1].
    duration_hours: d_i, expected execution time in hours.
    """

    task_id: str
    service: str
    domain: str
    cog: float
    phy: float
    emp: float
    risk: float
    auth: float
    priv: float
    urg: float
    learn: float
    crit: float
    duration_hours: float

    def __post_init__(self) -> None:
        for name in _DEMAND_FIELDS:
            object.__setattr__(self, name, _validate_unit_interval(name, getattr(self, name)))
        if self.duration_hours <= 0:
            raise ValueError(f"duration_hours must be positive, got {self.duration_hours!r}")

    @property
    def demand_vector(self) -> dict[str, float]:
        """The nine [0,1] demand dimensions of eq:task, excluding d_i."""
        return {name: getattr(self, name) for name in _DEMAND_FIELDS}

    @property
    def ell(self) -> float:
        """ell_i, the developmental content in qualified-practice hours (eq:ell)."""
        return developmental_content(self.learn, self.duration_hours)


def developmental_content(learn_i: float, d_i: float) -> float:
    """ell_i = learn_i * d_i (eq:ell).

    A 10-hour task at learn=0.8 and a 20-hour task at learn=0.4 are
    treated as identical developmental goods by this multiplicative
    form -- the paper does not discuss whether developmental value is
    in fact linear in exposure time (the pre-release audit, [CRIT]).
    """
    if not 0.0 <= learn_i <= 1.0:
        raise ValueError(f"learn_i must lie in [0, 1], got {learn_i!r}")
    if d_i <= 0:
        raise ValueError(f"d_i must be positive, got {d_i!r}")
    return learn_i * d_i
