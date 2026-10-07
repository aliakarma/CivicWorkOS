"""Contestability: Paper sec:contest, Suppl. app:contest.

Standing (S1.1): any resident or worker affected by an allocation
decision may appeal, EXPLICITLY IRRESPECTIVE OF CONTRACT STATUS -- the
paper grants this to non-payroll workers even though they are otherwise
invisible to N_k(t), ineligible as assignees, and unprotected by the
Just Transition Constraint (eq:justtransition). The paper is candid that standing
"does not repair the exclusion but ensures it is at least reportable."

Windows (Suppl. Table S1) are asymmetric by appeal type:
  - routine:              20 working days to lodge, 20 to resolve
  - rights-affecting:     20 working days to lodge, 10 to resolve, OUTCOME SUSPENDED
  - worker access/displacement: 40 working days to lodge, 30 to resolve, DISPLACEMENT SUSPENDED

Remedy: re-decision under Zone Z3 by a NAMED human decision-maker, who
may depart from the recommendation on the record (Suppl. S1.4).

Systemic trigger: an upheld-appeal rate above a policy threshold causes
AUTOMATIC one-zone demotion (civicworkos.zones.ZoneRegistry handles the
demotion/restoration asymmetry) plus a panel referral.

Disclosure: the full evidentiary record is disclosable to the appellant,
with third-party PII redacted -- and ONLY that redaction; the paper does
not authorize withholding record items on other grounds.
"""

from __future__ import annotations

from dataclasses import dataclass
from datetime import datetime, timedelta
from enum import Enum


class AppealType(str, Enum):
    ROUTINE = "routine"
    RIGHTS_AFFECTING = "rights_affecting"
    WORKER_ACCESS_OR_DISPLACEMENT = "worker_access_or_displacement"


@dataclass(frozen=True)
class AppealWindow:
    lodge_working_days: int
    resolve_working_days: int
    suspends: str | None  # "outcome" | "displacement" | None


APPEAL_WINDOWS: dict[AppealType, AppealWindow] = {
    AppealType.ROUTINE: AppealWindow(lodge_working_days=20, resolve_working_days=20, suspends=None),
    AppealType.RIGHTS_AFFECTING: AppealWindow(
        lodge_working_days=20, resolve_working_days=10, suspends="outcome"
    ),
    AppealType.WORKER_ACCESS_OR_DISPLACEMENT: AppealWindow(
        lodge_working_days=40, resolve_working_days=30, suspends="displacement"
    ),
}


class AppealStatus(str, Enum):
    LODGED = "lodged"
    UNDER_REVIEW = "under_review"
    UPHELD = "upheld"
    DENIED = "denied"
    RESOLVED = "resolved"


@dataclass
class Appeal:
    """One contestability case against an allocation decision.

    appellant_contract_status: recorded but NEVER used to deny standing
        (Suppl. S1.1) -- kept only to make the "irrespective of contract
        status" guarantee auditable, not to gate it.
    """

    appeal_id: str
    task_id: str
    appeal_type: AppealType
    appellant_id: str
    appellant_contract_status: str
    lodged_at: datetime
    status: AppealStatus = AppealStatus.LODGED
    remedy_decision_maker: str | None = None
    remedy_rationale: str | None = None
    resolved_at: datetime | None = None

    @property
    def window(self) -> AppealWindow:
        return APPEAL_WINDOWS[self.appeal_type]

    @property
    def resolve_by(self) -> datetime:
        # Working-day arithmetic is approximated as calendar days here for
        # simplicity; a production deployment must use a real business-day
        # calendar (holidays, municipal calendar) -- see docs/assumptions.md.
        return self.lodged_at + timedelta(days=self.window.resolve_working_days)

    def is_overdue(self, as_of: datetime) -> bool:
        return self.status not in (AppealStatus.RESOLVED,) and as_of > self.resolve_by

    def uphold(self, remedy_decision_maker: str, remedy_rationale: str, resolved_at: datetime) -> None:
        """Remedy: re-decision under Z3 by a NAMED human (Suppl. S1.4).

        The decision-maker's rationale is recorded even when it departs
        from any system recommendation -- the paper requires the human
        be able to do so "on the record."
        """
        if not remedy_decision_maker:
            raise ValueError("remedy under Z3 requires a named accountable human")
        self.status = AppealStatus.UPHELD
        self.remedy_decision_maker = remedy_decision_maker
        self.remedy_rationale = remedy_rationale
        self.resolved_at = resolved_at

    def deny(self, remedy_decision_maker: str, remedy_rationale: str, resolved_at: datetime) -> None:
        if not remedy_decision_maker:
            raise ValueError("a denial still requires a named accountable human")
        self.status = AppealStatus.DENIED
        self.remedy_decision_maker = remedy_decision_maker
        self.remedy_rationale = remedy_rationale
        self.resolved_at = resolved_at


def upheld_appeal_rate(appeals: list[Appeal]) -> float:
    """Fraction of resolved appeals that were upheld -- input to the
    systemic trigger (Suppl. S1.4) via ZoneRegistry.demote_on_appeal_threshold.
    """
    resolved = [a for a in appeals if a.status in (AppealStatus.UPHELD, AppealStatus.DENIED)]
    if not resolved:
        return 0.0
    upheld = sum(1 for a in resolved if a.status == AppealStatus.UPHELD)
    return upheld / len(resolved)
