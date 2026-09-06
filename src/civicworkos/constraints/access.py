"""Capability Access and Just Transition: Paper Sec. 3.6, Eq. 10-12.

    Pi_{k,g} = [ sum_i sum_m x_{i,m} * ell_i * phi_m * 1{assignee(i,m) in g} ]
               / [ sum_i sum_m x_{i,m} * ell_i * phi_m ]                      (Eq. 10)

    Pi_{k,g} >= theta_{k,g} - epsilon_k    for all g in G                     (Eq. 11)

    Delta_g(t, t+DeltaT) <= tau_g   and   chi_g >= chi_min   for all g in G   (Eq. 12)

Eq. 8 (hcpb.py) decides HOW MUCH developmental work is protected;
Eq. 11 decides WHO receives it. The paper's argument for why this must
be a separate constraint (Sec. 3.6): a budget sized from incumbent
headcount, left alone, allocates protected practice in proportion to
who already holds the posts -- "the mechanism designed to protect
workers becomes, without a further constraint, one that protects
incumbents."

theta_{k,g} is a TARGET the panel publishes; it is explicitly NOT the
incumbent share E_{k,g}/E_k (though a panel may choose to set it equal,
which is then "a recorded political decision to freeze composition
rather than an unnoticed property of the arithmetic").

Implementation note (report Sec. 8.4, [INFER]): Eq. 10 is a ratio of
decision-variable-dependent sums, so Eq. 11 is linear-fractional in the
assignment variables x. This module implements the ratio directly for
monitoring/evaluation of a *realized* allocation; civicworkos.program
linearizes it (by multiplying through the positive denominator) for use
inside the MIP of Eq. 16 -- see docs/assumptions.md A6.
"""

from __future__ import annotations

from dataclasses import dataclass


def realized_access_share(protected_hours_by_group: dict[str, float]) -> dict[str, float]:
    """Pi_{k,g} (Eq. 10): each group's share of a domain's realized protected-practice hours.

    `protected_hours_by_group` maps group id -> sum_i sum_m x_{i,m}*ell_i*phi_m
    restricted to assignees in that group. The denominator (Eq. 10) is the
    sum over all groups.
    """
    total = sum(protected_hours_by_group.values())
    if total <= 0:
        raise ValueError(
            "total protected-practice hours must be positive to compute Pi_{k,g}; "
            "the denominator of Eq. 10 requires at least one phi_m > 0 mode selected"
        )
    return {group: hours / total for group, hours in protected_hours_by_group.items()}


@dataclass(frozen=True)
class CapabilityAccessConstraint:
    """One group's target composition and tolerance for domain k (Eq. 11).

    theta_kg: published TARGET share, in [0,1]. Not the incumbent share.
    epsilon_k: tolerance band (worked example uses 0.05).
    """

    theta_kg: float
    epsilon_k: float

    def __post_init__(self) -> None:
        if not 0.0 <= self.theta_kg <= 1.0:
            raise ValueError(f"theta_kg must lie in [0,1], got {self.theta_kg!r}")
        if not 0.0 <= self.epsilon_k <= 1.0:
            raise ValueError(f"epsilon_k must lie in [0,1], got {self.epsilon_k!r}")

    @property
    def floor(self) -> float:
        """theta_{k,g} - epsilon_k, the right-hand side of Eq. 11."""
        return self.theta_kg - self.epsilon_k

    def is_satisfied(self, pi_kg: float) -> bool:
        """Eq. 11 as a boolean check for a realized share pi_kg."""
        return pi_kg >= self.floor

    def required_hours(self, budget_hours: float) -> float:
        """(theta_kg - epsilon_k) * B_k -- hours group g must receive at minimum.

        Used by [§20.4]/H4: reports the raw hour demand so a supply-side
        feasibility guard (not specified by the paper) can be checked
        against the group's eligible headcount before Eq. 16 is solved.
        """
        return max(0.0, self.floor) * budget_hours


@dataclass(frozen=True)
class JustTransitionConstraint:
    """One group's displacement ceiling and reskilling floor (Eq. 12).

    tau_g: ceiling on displacement pace for group g, in [0,1].
    chi_min: floor on the share of affected workers with a funded
        reskilling/redeployment pathway, in [0,1].
    """

    tau_g: float
    chi_min: float

    def __post_init__(self) -> None:
        if not 0.0 <= self.tau_g <= 1.0:
            raise ValueError(f"tau_g must lie in [0,1], got {self.tau_g!r}")
        if not 0.0 <= self.chi_min <= 1.0:
            raise ValueError(f"chi_min must lie in [0,1], got {self.chi_min!r}")

    def is_satisfied(self, delta_g: float, chi_g: float) -> bool:
        """Eq. 12: both the displacement ceiling and the reskilling floor must hold."""
        return delta_g <= self.tau_g and chi_g >= self.chi_min
