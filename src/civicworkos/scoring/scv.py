"""Sustainable Civic Value (SCV): Paper Sec. 4.3, Eq. 15.

    SCV_{i,m} = w1*Q + w2*S + w3*P + w4*Eq_srv + w5*Tr
              - w6*Cost - w7*En - w8*Pr - w9*CAD_{i,m}

The per-task objective: five terms rewarded, four penalized, plus the
single largest weight (w9 = 0.22 by default) on Civic Automation Debt.

Normalization (Paper Sec. 4.3) is deliberately NOT uniform: the six
operational terms (Q, S, P, Cost, En, Pr) use trailing-window min-max
normalization (civicworkos.scoring.normalize_windowed), while the four
long-horizon terms (the CAD components' anchors, Eq_srv, D_trans) are
anchored absolutely (civicworkos.scoring.normalize_anchored). This
module operates on ALREADY-NORMALIZED [0,1] terms; it does not perform
normalization itself, so that the two normalization regimes stay in
separately-auditable code paths as the paper requires -- see
docs/paper_implementation_mapping.md.
"""

from __future__ import annotations

from dataclasses import dataclass, fields
from typing import Protocol

_TOLERANCE = 1e-9


def _check_unit_interval(name: str, value: float) -> None:
    if not -_TOLERANCE <= value <= 1.0 + _TOLERANCE:
        raise ValueError(f"{name} must lie in [0, 1], got {value!r}")


@dataclass(frozen=True)
class TermVector:
    """The eight flow terms of Eq. 15, each normalized to [0,1].

    Q: service quality (+).            S: safety (+).
    P: productivity (+).               Eq_srv: service equity (+).
    Tr: agent trust (+).               Cost: operating cost (-).
    En: energy use (-).                Pr: privacy risk (-).
    """

    Q: float
    S: float
    P: float
    Eq_srv: float
    Tr: float
    Cost: float
    En: float
    Pr: float

    def __post_init__(self) -> None:
        for f in fields(self):
            _check_unit_interval(f.name, getattr(self, f.name))


@dataclass(frozen=True)
class ScoreWeights:
    """w1..w9 of Eq. 15. Paper default (Sec. 6.4):

    (0.15, 0.18, 0.14, 0.10, 0.05, 0.08, 0.03, 0.05, 0.22)
    for (Q, S, P, Eq_srv, Tr, Cost, En, Pr, CAD) respectively.
    """

    w1_quality: float
    w2_safety: float
    w3_productivity: float
    w4_equity: float
    w5_trust: float
    w6_cost: float
    w7_energy: float
    w8_privacy: float
    w9_cad: float

    def __post_init__(self) -> None:
        total = sum(self.as_tuple())
        if abs(total - 1.0) > 1e-6:
            raise ValueError(f"score weights (w1..w9) must sum to 1.0, got sum={total!r}")

    def as_tuple(self) -> tuple[float, ...]:
        return (
            self.w1_quality,
            self.w2_safety,
            self.w3_productivity,
            self.w4_equity,
            self.w5_trust,
            self.w6_cost,
            self.w7_energy,
            self.w8_privacy,
            self.w9_cad,
        )

    @classmethod
    def paper_default(cls) -> ScoreWeights:
        """The illustrative defaults of Paper Sec. 6.4. Not fitted estimates."""
        return cls(
            w1_quality=0.15,
            w2_safety=0.18,
            w3_productivity=0.14,
            w4_equity=0.10,
            w5_trust=0.05,
            w6_cost=0.08,
            w7_energy=0.03,
            w8_privacy=0.05,
            w9_cad=0.22,
        )

    def effective_weights(self, debt_weights: DebtWeightsLike) -> dict[str, float]:
        """Table 4: decompose w9 across the five debt components.

        Returns the effective weight each construct carries in the
        composed objective, e.g. "skill formation" = w9 * alpha.
        """
        alpha, beta, gamma, delta, epsilon = debt_weights.as_tuple()
        return {
            "safety": self.w2_safety,
            "service_quality": self.w1_quality,
            "productivity": self.w3_productivity,
            "service_equity_residents": self.w4_equity,
            "operating_cost": self.w6_cost,
            "skill_formation": self.w9_cad * alpha,
            "trust": self.w5_trust,
            "privacy_risk": self.w8_privacy,
            "fallback_capacity": self.w9_cad * beta,
            "labour_transition_burden": self.w9_cad * epsilon,
            "accountability": self.w9_cad * gamma,
            "energy": self.w7_energy,
            "vendor_dependency": self.w9_cad * delta,
        }


class DebtWeightsLike(Protocol):
    """Structural type hint: anything with an as_tuple() -> 5-tuple."""

    def as_tuple(self) -> tuple[float, float, float, float, float]: ...  # pragma: no cover


def sustainable_civic_value(terms: TermVector, cad: float, weights: ScoreWeights) -> float:
    """SCV_{i,m} (Eq. 15)."""
    _check_unit_interval("CAD", cad)
    return (
        weights.w1_quality * terms.Q
        + weights.w2_safety * terms.S
        + weights.w3_productivity * terms.P
        + weights.w4_equity * terms.Eq_srv
        + weights.w5_trust * terms.Tr
        - weights.w6_cost * terms.Cost
        - weights.w7_energy * terms.En
        - weights.w8_privacy * terms.Pr
        - weights.w9_cad * cad
    )
