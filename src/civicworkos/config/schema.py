"""Configuration schema: governance artifacts, not code constants.

Paper sec:feedback: every allocation must trace to "the configuration that
authorized it," and weight/threshold changes are signed, dated policy
acts, not silent code edits. This module models that:

  - WeightsConfig: w1..w9 and alpha..epsilon (eq:scv, eq:cad), versioned.
  - DomainConfig: per-domain HCPB/access/transition parameters (eq:hcpb-estimator through eq:justtransition),
    versioned, with an explicit UNSET sentinel.

UNSET sentinel (the pre-release audit's recommendation, directly required by
Paper sec:feedback): "an unset theta_{k,g} or tau_g must leave its
constraint unbound and flagged, never silently defaulted." A bare YAML
omission or a numeric default (e.g. 0.0) would either crash unexpectedly
or silently authorize an unintended policy. `Unset` is a distinct
singleton, never equal to any float, so `isinstance(x, Unset)` is the
only way code can treat it as configured-absent.
"""

from __future__ import annotations

from dataclasses import dataclass, field
from datetime import date

from pydantic import BaseModel, model_validator


class Unset:
    """Sentinel: this normative parameter has not been set by the panel.

    Distinct from any numeric default (including 0.0). A constraint whose
    parameter is UNSET must be treated as unbound and flagged for panel
    attention, never silently defaulted (Paper sec:feedback).
    """

    _instance: Unset | None = None

    def __new__(cls) -> Unset:
        if cls._instance is None:
            cls._instance = super().__new__(cls)
        return cls._instance

    def __repr__(self) -> str:
        return "UNSET"

    def __bool__(self) -> bool:
        return False


UNSET = Unset()


class WeightsConfig(BaseModel):
    """w1..w9 (eq:scv) and alpha..epsilon (eq:cad), one versioned artifact.

    Defaults below are the paper's own illustrative values (sec:weights),
    reproduced verbatim as the config's factory default -- NOT fitted
    estimates, and the panel of sec:feedback is the paper's stated authority
    to revise them.
    """

    version: str
    effective_date: date
    w1_quality: float = 0.15
    w2_safety: float = 0.18
    w3_productivity: float = 0.14
    w4_equity: float = 0.10
    w5_trust: float = 0.05
    w6_cost: float = 0.08
    w7_energy: float = 0.03
    w8_privacy: float = 0.05
    w9_cad: float = 0.22
    alpha_skill: float = 0.28
    beta_fallback: float = 0.22
    gamma_accountability: float = 0.18
    delta_dependency: float = 0.12
    epsilon_transition: float = 0.20

    @model_validator(mode="after")
    def _check_sums(self) -> WeightsConfig:
        score_sum = (
            self.w1_quality
            + self.w2_safety
            + self.w3_productivity
            + self.w4_equity
            + self.w5_trust
            + self.w6_cost
            + self.w7_energy
            + self.w8_privacy
            + self.w9_cad
        )
        if abs(score_sum - 1.0) > 1e-6:
            raise ValueError(f"w1..w9 must sum to 1.0, got {score_sum!r}")
        debt_sum = (
            self.alpha_skill
            + self.beta_fallback
            + self.gamma_accountability
            + self.delta_dependency
            + self.epsilon_transition
        )
        if abs(debt_sum - 1.0) > 1e-6:
            raise ValueError(f"alpha..epsilon must sum to 1.0, got {debt_sum!r}")
        return self


@dataclass(frozen=True)
class DomainConfig:
    """Per-domain HCPB (eq:hcpb-estimator), access (eq:access), and transition (eq:justtransition)
    parameters. `theta_kg` and `tau_g` entries may be `UNSET`.

    version / effective_date: this configuration is itself a versioned
        policy act (Paper sec:feedback).
    """

    domain: str
    version: str
    effective_date: date
    N_k: float
    r_k: float
    h_k: float
    eta_k: float
    B_k_min: float
    hybrid_phi: dict[str, float] = field(default_factory=dict)
    groups: list[str] = field(default_factory=list)
    theta_kg: dict[str, float | Unset] = field(default_factory=dict)
    epsilon_k: float = 0.05
    tau_g: dict[str, float | Unset] = field(default_factory=dict)
    chi_min: float = 0.0

    def unset_parameters(self) -> list[str]:
        """List every UNSET theta_kg/tau_g entry, for a panel-facing flag report."""
        flagged = []
        for group in self.groups:
            if isinstance(self.theta_kg.get(group, UNSET), Unset):
                flagged.append(f"theta_{self.domain}_{group}")
            if isinstance(self.tau_g.get(group, UNSET), Unset):
                flagged.append(f"tau_{group}")
        return flagged
