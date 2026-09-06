"""Adaptive Oversight Zones: Paper Sec. 4.7, Table 2.

Four zones classify tasks by how much autonomy they may be given:

    Z1 Autonomous     -- high-confidence, low-rights-impact tasks may run unattended.
    Z2 Augmented      -- AI/robots do substantial work; a human stays meaningfully involved.
    Z3 Human Authority -- AI may advise; a designated human authority decides. Remedy zone
                          for upheld appeals (Suppl. S1.4).
    Z4 Human Reserved -- automation restricted; also the terminal fallback when the
                          admissible set empties (Algorithm 1, line 14).

Zone membership is conditioned on continuously updated SCV/CAD evidence
and incidents/appeals, not assigned once as a static risk category. A
class moves Z2->Z1 after sustained safety performance, and back to Z3
after incidents, drift, cyber risk, public concern, or lost fallback
capacity (Paper Sec. 4.7). Upheld-appeal rate above threshold triggers
AUTOMATIC one-zone demotion; restoration requires an affirmative panel
decision and cannot occur automatically (Suppl. S1.4) -- that asymmetry
is enforced in code below, not left to caller discipline.
"""

from __future__ import annotations

from dataclasses import dataclass
from datetime import datetime, timezone
from enum import IntEnum


class Zone(IntEnum):
    """Ordered Z1 (most autonomous) .. Z4 (least autonomous), so demotion = +1."""

    Z1_AUTONOMOUS = 1
    Z2_AUGMENTED = 2
    Z3_HUMAN_AUTHORITY = 3
    Z4_HUMAN_RESERVED = 4


@dataclass(frozen=True)
class ZoneTransition:
    """One recorded zone change -- a versioned policy act, not a silent parameter change."""

    task_class: str
    from_zone: Zone
    to_zone: Zone
    reason: str
    automatic: bool
    timestamp: datetime
    authorizing_panel_decision: str | None = None


class ZoneRegistry:
    """Tracks zone membership per task class and enforces the demotion asymmetry.

    Demotion (moving toward Z4) may be automatic, triggered by an
    upheld-appeal-rate threshold. Restoration (moving toward Z1) may
    NEVER be automatic in this implementation -- it always requires an
    `authorizing_panel_decision` -- matching Suppl. S1.4's stated rule.
    """

    def __init__(self) -> None:
        self._current: dict[str, Zone] = {}
        self._history: dict[str, list[ZoneTransition]] = {}

    def assign(self, task_class: str, zone: Zone, reason: str = "initial assignment") -> None:
        if task_class in self._current:
            raise ValueError(f"task class {task_class!r} already has an assigned zone; use transition()")
        self._current[task_class] = zone
        self._history.setdefault(task_class, [])

    def current_zone(self, task_class: str) -> Zone:
        try:
            return self._current[task_class]
        except KeyError as exc:
            raise KeyError(f"task class {task_class!r} has no assigned zone") from exc

    def transition(
        self,
        task_class: str,
        to_zone: Zone,
        reason: str,
        *,
        automatic: bool = False,
        authorizing_panel_decision: str | None = None,
        timestamp: datetime | None = None,
    ) -> ZoneTransition:
        from_zone = self.current_zone(task_class)
        is_restoration = to_zone < from_zone
        if is_restoration and authorizing_panel_decision is None:
            raise ValueError(
                "zone restoration (toward Z1) requires an affirmative panel decision "
                "(Suppl. S1.4); automatic restoration is not permitted"
            )
        if automatic and is_restoration:
            raise ValueError("automatic transitions may only demote (toward Z4), never restore")
        record = ZoneTransition(
            task_class=task_class,
            from_zone=from_zone,
            to_zone=to_zone,
            reason=reason,
            automatic=automatic,
            timestamp=timestamp or datetime.now(timezone.utc),
            authorizing_panel_decision=authorizing_panel_decision,
        )
        self._current[task_class] = to_zone
        self._history.setdefault(task_class, []).append(record)
        return record

    def demote_on_appeal_threshold(
        self, task_class: str, upheld_appeal_rate: float, threshold: float
    ) -> ZoneTransition | None:
        """Automatic one-zone demotion if the upheld-appeal rate exceeds threshold (Suppl. S1.4)."""
        if upheld_appeal_rate <= threshold:
            return None
        current = self.current_zone(task_class)
        if current == Zone.Z4_HUMAN_RESERVED:
            return None  # already at the most restrictive zone
        target = Zone(current + 1)
        return self.transition(
            task_class,
            target,
            reason=f"upheld-appeal rate {upheld_appeal_rate:.3f} exceeded threshold {threshold:.3f}",
            automatic=True,
        )

    def history(self, task_class: str) -> list[ZoneTransition]:
        return list(self._history.get(task_class, []))
