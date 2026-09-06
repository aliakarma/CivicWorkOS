"""Allocation Market agent interface: Paper Sec. 3.8.

The paper names ten market agents (five capability, five civic) and
what each produces, but specifies NO interface contract: no input/output
schema, no latency budget, no failure semantics (report Sec. 14.3, item
9). `MarketProtocol` below is this repository's own invented contract,
built to be the smallest interface Algorithm 1 needs:

    query(task, mode, policy_status, ledger) -> AgentEstimate

conditioned on the oversight duty the policy status imposes
(Algorithm 1, line 7): an `allow_with_oversight` status must raise
`phi_m` and add reviewer time to `Cost`, which `AgentEstimate` carries
as already-composed fields rather than as a separate side channel.

Failure semantics [REC, not in the paper]: a `MarketTimeoutError` raised
by an agent implementation is treated by the online rule (civicworkos.online)
as equivalent to that mode being unavailable -- the conservative choice,
since the paper is silent and an allocation must not proceed on an
estimate it could not obtain.
"""

from __future__ import annotations

from dataclasses import dataclass
from datetime import date
from typing import Protocol

from civicworkos.ledger.capability_ledger import LedgerSnapshot
from civicworkos.policy.digital_twin import PolicyStatus
from civicworkos.scoring.cad import DebtComponents
from civicworkos.scoring.scv import TermVector
from civicworkos.twin.task import TaskProfile


class MarketTimeoutError(RuntimeError):
    """Raised when an agent estimate cannot be obtained within budget.

    No latency budget is stated in the paper; civicworkos.online treats
    any MarketTimeoutError as grounds to drop the affected mode from the
    admissible set for that task (report Sec. 18.2 names this an open
    production requirement).
    """


@dataclass(frozen=True)
class AgentEstimate:
    """Everything Algorithm 1 needs from the market for one (task, mode):
    the eight flow terms, the five debt components, and phi_m.
    """

    terms: TermVector
    debts: DebtComponents
    phi_m: float

    def __post_init__(self) -> None:
        if not 0.0 <= self.phi_m <= 1.0:
            raise ValueError(f"phi_m must lie in [0,1], got {self.phi_m!r}")


class MarketProtocol(Protocol):
    """Structural interface every market implementation must satisfy."""

    def query(
        self,
        task: TaskProfile,
        mode: str,
        policy_status: PolicyStatus,
        ledger: LedgerSnapshot,
        t: date | None = None,
    ) -> AgentEstimate:
        """Return the composed estimate for (task, mode) at time t.

        Implementations MUST raise MarketTimeoutError, not return a
        degraded estimate silently, if any underlying agent cannot answer.
        """
        ...  # pragma: no cover
