"""Civic Capability Ledger: Paper sec:layer2, eq:ledger.

    L_k(t) = { H_k, A_k, R_k, F_k, E_k, {E_{k,g}} }

Per-domain capability state: human/AI/robot capacity, fallback capacity
F_k, human expertise pipeline E_k, and its GROUP DECOMPOSITION E_{k,g}.

The group decomposition is NOT optional reporting: without it the
Capability Access Constraint (eq:access) cannot be evaluated (Paper sec:layer2).
This module enforces that invariant (Sigma_g E_{k,g} = E_k) and accepts
feedback from BOTH machine and human outcomes, per fig:architecture's caption: "the
Ledger holds AI and robot capability terms that cannot be maintained if
machine outcomes bypass it."
"""

from __future__ import annotations

from dataclasses import dataclass, field, replace

_RECONCILE_TOLERANCE = 1e-6


@dataclass(frozen=True)
class LedgerSnapshot:
    """One immutable L_k(t) for one capability domain k at one instant.

    H_k, A_k, R_k: human / AI / robot capacity contributions to domain k.
    F_k: fallback capacity -- human capability retained as a backstop
        if automated channels fail.
    E_k: size of the human expertise pipeline (competent + in-formation).
    E_kg: {group_id: expertise_share} decomposing E_k by worker group.
        Required to sum to E_k (Paper sec:layer2).
    accrued_practice_hours: Lambda_k(t), qualified-practice hours
        delivered so far in the current budget period.
    """

    domain: str
    H_k: float
    A_k: float
    R_k: float
    F_k: float
    E_k: float
    E_kg: dict[str, float] = field(default_factory=dict)
    accrued_practice_hours: float = 0.0

    def __post_init__(self) -> None:
        if self.E_kg:
            total = sum(self.E_kg.values())
            if abs(total - self.E_k) > _RECONCILE_TOLERANCE:
                raise ValueError(
                    f"E_kg does not reconcile to E_k for domain {self.domain!r}: "
                    f"sum(E_kg)={total!r} != E_k={self.E_k!r}"
                )
        for name in ("H_k", "A_k", "R_k", "F_k", "E_k", "accrued_practice_hours"):
            if getattr(self, name) < 0:
                raise ValueError(f"{name} must be non-negative, got {getattr(self, name)!r}")


class CapabilityLedger:
    """Mutable per-domain L_k(t) time series, keyed by domain.

    This is an in-process reference implementation of eq:ledger's state.
    civicworkos.audit provides the append-only, disclosable record of
    the decisions that drive these updates; this class holds only the
    current and historical *state*, reconstructable from that record
    (the pre-release audit's stated validation criterion for Phase 4).
    """

    def __init__(self) -> None:
        self._current: dict[str, LedgerSnapshot] = {}
        self._history: dict[str, list[LedgerSnapshot]] = {}

    def initialize(self, snapshot: LedgerSnapshot) -> None:
        self._current[snapshot.domain] = snapshot
        self._history.setdefault(snapshot.domain, []).append(snapshot)

    def current(self, domain: str) -> LedgerSnapshot:
        try:
            return self._current[domain]
        except KeyError as exc:
            raise KeyError(f"domain {domain!r} has not been initialized in the ledger") from exc

    def history(self, domain: str) -> list[LedgerSnapshot]:
        return list(self._history.get(domain, []))

    def accrue_practice(self, domain: str, hours: float) -> LedgerSnapshot:
        """Lambda_k += ell_i * phi_{m*}, the online rule's post-execution update."""
        if hours < 0:
            raise ValueError(f"hours must be non-negative, got {hours!r}")
        current = self.current(domain)
        updated = replace(current, accrued_practice_hours=current.accrued_practice_hours + hours)
        self._current[domain] = updated
        self._history[domain].append(updated)
        return updated

    def reset_budget_period(self, domain: str) -> LedgerSnapshot:
        """Zero Lambda_k at the start of a new budget period (Paper sec:hcpb)."""
        current = self.current(domain)
        updated = replace(current, accrued_practice_hours=0.0)
        self._current[domain] = updated
        self._history[domain].append(updated)
        return updated

    def update_group_shares(self, domain: str, e_kg: dict[str, float]) -> LedgerSnapshot:
        """Replace E_{k,g}; must still reconcile to E_k."""
        current = self.current(domain)
        updated = replace(current, E_kg=dict(e_kg))
        self._current[domain] = updated
        self._history[domain].append(updated)
        return updated
