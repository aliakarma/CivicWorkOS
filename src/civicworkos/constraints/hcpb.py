"""Human Capability Preservation Budget: Paper Sec. 3.5, Eq. 7-9.

    phi_H = 1, phi_A = phi_R = phi_{A+R} = 0,
    phi_{H+A}, phi_{H+R}, phi_{H+A+R} in [0,1], set per domain          (Eq. 7)

    sum_{i in T_k(DeltaT)} sum_m x_{i,m} * ell_i * phi_m >= B_k(t)      (Eq. 8)

    B_k(t) = max( B_k^min , eta_k * N_k(t) * r_k(t) * h_k )             (Eq. 9)

This is the framework's ONLY capability constraint. The paper is
emphatic that "formulations that additionally compare a capability
stock against B_k conflate two different objects, and (8) is the
operative form" (Sec. 3.5). It is not a jobs quota: it bounds a volume
of qualified-practice hours, not a headcount.

Dimensional check (Sec. 3.5): N_k * r_k * h_k = people * period^-1 *
hours/person = hours/period, matching Eq. 8's left side. Verified below
in capability_budget() and exercised by tests/unit/test_hcpb.py.
"""

from __future__ import annotations

from dataclasses import dataclass

# Eq. 7: fixed shares for pure modes. Hybrid shares are domain-configured
# (see configs/domains/*.yaml) because the paper gives no formula for them.
FIXED_PHI = {
    "H": 1.0,
    "A": 0.0,
    "R": 0.0,
    "A+R": 0.0,
}
HYBRID_MODES = ("H+A", "H+R", "H+A+R")


def phi_for_mode(mode: str, hybrid_phi: dict[str, float]) -> float:
    """phi_m (Eq. 7): human developmental share of mode m.

    Pure-mode values are fixed by the paper. Hybrid values must be
    supplied from a domain configuration (elicited from practitioners
    per Paper Sec. 3.5 -- the paper names no elicitation instrument;
    see docs/assumptions.md A3).
    """
    if mode in FIXED_PHI:
        return FIXED_PHI[mode]
    if mode in HYBRID_MODES:
        try:
            value = hybrid_phi[mode]
        except KeyError as exc:
            raise KeyError(
                f"phi_{mode} not configured; hybrid developmental shares must be "
                "elicited per-domain (Paper Sec. 3.5) and supplied explicitly"
            ) from exc
        if not 0.0 <= value <= 1.0:
            raise ValueError(f"phi_{mode} must lie in [0,1], got {value!r}")
        return value
    raise ValueError(f"unknown mode {mode!r}")


@dataclass(frozen=True)
class HCPBParameters:
    """Inputs to Eq. 9, one capability domain, one budget period.

    N_k: practitioners active in the domain (people).
    r_k: fraction lost to attrition per budget period (period^-1).
    h_k: hours to independent competence (hours/person).
    eta_k: policy-set replacement-generation factor (eta>1 builds
        margin; eta<1 deliberately allows the domain to shrink).
    B_k_min: hours floor per period.
    """

    N_k: float
    r_k: float
    h_k: float
    eta_k: float
    B_k_min: float

    def __post_init__(self) -> None:
        if self.N_k < 0:
            raise ValueError(f"N_k must be non-negative, got {self.N_k!r}")
        if not 0.0 <= self.r_k <= 1.0:
            raise ValueError(f"r_k must lie in [0,1], got {self.r_k!r}")
        if self.h_k <= 0:
            raise ValueError(f"h_k must be positive, got {self.h_k!r}")
        if self.eta_k <= 0:
            raise ValueError(f"eta_k must be positive, got {self.eta_k!r}")
        if self.B_k_min < 0:
            raise ValueError(f"B_k_min must be non-negative, got {self.B_k_min!r}")


def capability_budget(params: HCPBParameters) -> float:
    """B_k(t) = max(B_k_min, eta_k * N_k * r_k * h_k)  (Eq. 9), hours/period.

    Units close: people * period^-1 * hours/person = hours/period.
    """
    return max(params.B_k_min, params.eta_k * params.N_k * params.r_k * params.h_k)


def hcpb_shortfall(delivered_hours: float, budget_hours: float) -> float:
    """max(0, B_k(t) - delivered) -- how far a domain is below its budget.

    Not itself in the paper; a convenience used by the online rule's
    admissibility test (Eq. 18) and by monitoring (report Sec. 18.3).
    """
    return max(0.0, budget_hours - delivered_hours)


def hcpb_satisfied(delivered_hours: float, budget_hours: float) -> bool:
    """Eq. 8 as a boolean check for a given accumulation of practice hours."""
    return delivered_hours >= budget_hours
