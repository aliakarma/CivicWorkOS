"""Evidentiary record: Paper sec:contest, Suppl. S1.3.

Every allocation decision writes an append-only, disclosable record with
SEVEN items (Suppl. S1.3), reproduced here field-by-field:

    1. task profile, including d_i and ell_i
    2. drafted mode set M and the surviving set, with the policy status
       returned for each REMOVED mode (not just a pass/fail flag)
    3. per-candidate full term vector, five debt components, composed
       CAD, base SCV, and augmented SCV~
    4. admissibility outcome, and WHICH bracket of eq:admis excluded each
       rejected candidate
    5. the duals in force plus the rebalance timestamp they came from
    6. the configuration version and the authorizing panel decision
    7. the accountable human, where one is designated (Z3/Z4)

Items 5-6 are what make a POLICY appeal possible, not only a decision
appeal (the pre-release audit's engineering note on Phase 9) -- they are
therefore stored as resolvable pointers (a version string and a panel
decision id), not compressed into a hash.

The store is append-only: `EvidentiaryRecordStore.add()` is the only
mutator, and validate_replay() checks the report's own stated Phase 9
validation criterion -- "every stored decision can be replayed from its
record to the same m*."
"""

from __future__ import annotations

import hashlib
import json
from dataclasses import asdict, dataclass, field
from datetime import datetime, timezone


@dataclass(frozen=True)
class CandidateRecord:
    """One admissible or rejected mode's full pricing, item 3 of the record."""

    mode: str
    terms: dict[str, float]
    debts: dict[str, float]
    cad: float
    scv: float
    scv_tilde: float | None  # None if excluded before augmentation


@dataclass(frozen=True)
class RejectionRecord:
    """Item 2 (removed-by-policy) and item 4 (removed-by-admissibility), unified."""

    mode: str
    stage: str  # "policy_filter" or "admissibility_test"
    reason: str  # e.g. the policy status, or which eq:admis clause failed


@dataclass(frozen=True)
class EvidentiaryRecord:
    """The seven-item append-only record for one allocation decision."""

    task_id: str
    domain: str
    service: str
    d_i: float
    ell_i: float
    drafted_modes: tuple[str, ...]
    rejections: tuple[RejectionRecord, ...]
    candidates: tuple[CandidateRecord, ...]
    selected_mode: str
    duals_in_force: dict[str, float]
    rebalance_timestamp: datetime
    config_version: str
    authorizing_panel_decision: str
    accountable_human: str | None
    decided_at: datetime = field(default_factory=lambda: datetime.now(timezone.utc))

    def content_hash(self) -> str:
        """Content address for tamper-evidence (the pre-release audit's recommended
        audit-store property: "content-addressed append-only log")."""
        payload = asdict(self)
        payload["decided_at"] = payload["decided_at"].isoformat()
        payload["rebalance_timestamp"] = payload["rebalance_timestamp"].isoformat()
        serialized = json.dumps(payload, sort_keys=True, default=str).encode("utf-8")
        return hashlib.sha256(serialized).hexdigest()


class EvidentiaryRecordStore:
    """Append-only store. No update or delete method exists by design."""

    def __init__(self) -> None:
        self._records: list[EvidentiaryRecord] = []

    def add(self, record: EvidentiaryRecord) -> str:
        self._records.append(record)
        return record.content_hash()

    def all(self) -> list[EvidentiaryRecord]:
        return list(self._records)

    def for_task(self, task_id: str) -> list[EvidentiaryRecord]:
        return [r for r in self._records if r.task_id == task_id]

    def validate_replay(self, record: EvidentiaryRecord, recompute_argmax) -> bool:
        """Check that `recompute_argmax(record)` reproduces `record.selected_mode`.

        `recompute_argmax` is caller-supplied because replaying the argmax
        requires re-running eq:aug, eq:admis and eq:argmax against the stored candidates, which
        this module (a storage layer) does not itself implement -- see
        civicworkos.online.algorithm1 for that logic and
        tests/integration/test_audit_replay.py for the exercised check.
        """
        return recompute_argmax(record) == record.selected_mode
