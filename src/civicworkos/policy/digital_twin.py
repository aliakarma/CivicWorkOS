"""Policy Digital Twin: Paper Sec. 3.4, Eq. 6.

    P(T_i, m, t) in {allow, allow-with-oversight, restrict, prohibit}

Converts statute, ordinance, licensing, and collective-agreement rules
into machine-checkable predicates, evaluated PER MODE (not per task) --
the paper is explicit that per-task filtering is a specification error
(report Sec. 20, Phase 3 validation criterion).

`allow-with-oversight` binds a designated reviewer and propagates two
effects the paper requires and this repository implements as annotations
on the returned PolicyDecision, for the market layer to consume: reviewer
time enters that mode's Cost, and phi_m is raised (Paper Sec. 3.4).

`restrict` narrows candidates to modes retaining a minimum human share;
this repository's PolicyDigitalTwin.filter_modes() applies that directly.

Rule currency ("a recurring legal-engineering cost, not a one-time
setup", Paper Sec. 5.1) is modeled by requiring every PolicyRule to carry
a version and an effective_date, so a rule-staleness report is possible
(civicworkos.utils.staleness, used by docs/deployment.md's monitoring list).
"""

from __future__ import annotations

from collections.abc import Callable
from dataclasses import dataclass
from datetime import date
from enum import Enum

from civicworkos import MODES
from civicworkos.twin.task import TaskProfile

_SEVERITY_ORDER = ("allow", "allow_with_oversight", "restrict", "prohibit")


class PolicyStatus(str, Enum):
    """The four-valued status of Eq. 6."""

    ALLOW = "allow"
    ALLOW_WITH_OVERSIGHT = "allow_with_oversight"
    RESTRICT = "restrict"
    PROHIBIT = "prohibit"

    @property
    def _severity(self) -> int:
        return _SEVERITY_ORDER.index(self.value)

    @staticmethod
    def most_restrictive(statuses: list[PolicyStatus]) -> PolicyStatus:
        """When multiple rules apply to the same (task, mode), the most
        restrictive status governs (prohibit > restrict >
        allow-with-oversight > allow). Not stated explicitly by the paper
        as a combination rule for multiple simultaneous rules; this is the
        conservative reading consistent with a rule base whose purpose is
        to enforce legal floors, not to relax them -- see docs/assumptions.md A4.
        """
        if not statuses:
            return PolicyStatus.ALLOW
        return max(statuses, key=lambda s: s._severity)


RulePredicate = Callable[[TaskProfile, str], PolicyStatus | None]
"""A rule predicate: (task, mode) -> status, or None if the rule does not apply."""


@dataclass(frozen=True)
class PolicyRule:
    """One versioned, machine-checkable rule.

    rule_id: stable identifier for audit-trail linkage.
    version: this rule's revision (every parameter change is a signed,
        dated policy act -- Paper Sec. 5.1).
    effective_date: when this version took effect.
    description: human-readable statement of the underlying statute,
        ordinance, licensing rule, or collective-agreement clause.
    predicate: (task, mode) -> PolicyStatus | None.
    """

    rule_id: str
    version: str
    effective_date: date
    description: str
    predicate: RulePredicate


class PolicyDigitalTwin:
    """Evaluates Eq. 6 per mode against a versioned rule base."""

    def __init__(self, rules: list[PolicyRule] | None = None) -> None:
        self._rules: list[PolicyRule] = list(rules) if rules else []

    def add_rule(self, rule: PolicyRule) -> None:
        self._rules.append(rule)

    @property
    def rules(self) -> list[PolicyRule]:
        return list(self._rules)

    def status(self, task: TaskProfile, mode: str, t: date | None = None) -> PolicyStatus:
        """P(T_i, m, t) (Eq. 6): the combined status for one (task, mode)."""
        if mode not in MODES:
            raise ValueError(f"unknown mode {mode!r}; must be one of {MODES}")
        applicable = []
        for rule in self._rules:
            if t is not None and rule.effective_date > t:
                continue  # not yet in force
            result = rule.predicate(task, mode)
            if result is not None:
                applicable.append(result)
        return PolicyStatus.most_restrictive(applicable)

    def filter_modes(
        self, task: TaskProfile, modes: tuple[str, ...] = MODES, t: date | None = None
    ) -> dict[str, PolicyStatus]:
        """Evaluate every mode and drop those with status PROHIBIT.

        Returns {mode: status} for every SURVIVING mode. This is Algorithm 1's
        per-mode policy-filter step (lines 4-6); a mode absent from the
        returned dict has been prohibited.
        """
        result: dict[str, PolicyStatus] = {}
        for mode in modes:
            status = self.status(task, mode, t)
            if status != PolicyStatus.PROHIBIT:
                result[mode] = status
        return result


def requires_licensed_human_rule(rule_id: str, version: str, effective_date: date, description: str) -> PolicyRule:
    """Factory for the worked example's statutory sign-off rule (Paper Sec. 5.3):

    "A structural determination of this kind carries a statutory sign-off
    requirement, so the Policy Digital Twin returns prohibit for every
    mode lacking a licensed human" -- reducing M to M' = {H, H+A, H+R, H+A+R}.
    """

    def predicate(task: TaskProfile, mode: str) -> PolicyStatus | None:
        if "H" not in mode.split("+"):
            return PolicyStatus.PROHIBIT
        return None

    return PolicyRule(
        rule_id=rule_id,
        version=version,
        effective_date=effective_date,
        description=description,
        predicate=predicate,
    )
