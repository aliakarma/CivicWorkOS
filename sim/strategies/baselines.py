"""Five baseline allocation strategies: Paper Sec. 6.2.

"Five strategies are compared, each a configuration of (Eq. 15) and its
constraints." All five are ablations of the authors' own objective, not
independent external systems -- the paper concedes this directly
(Sec. 7.2: "a tautology about the objective, not a discovery about
cities") and report Sec. 20.13 flags it as a limitation: the study can
show the mechanism does what it was built to do, not that it beats
alternative designs.

- Automation-First: maximizes quality and productivity, preferring
  automation wherever policy permits; w9=0; HCPB/access/3R relaxed.
- Cost/Performance Optimization: maximizes (Q,P) net of Cost and En only.
- Human-First: restricts m to modes containing H whenever available.
- Conventional Capability Matching: the task-agent fit criterion of
  prior HRC work, without debt, budget, access, or reserve terms --
  implemented here as SCV with w9 renormalized to 0 and no constraints,
  which is what the paper's own description reduces to (report Sec. 20.13,
  [CRIT]: "a zeroed-out CivicWorkOS").
- CivicWorkOS: the full objective under all constraints of Eq. 16.

Only CivicWorkOS is evaluated through the constrained AllocationEngine
(civicworkos.online); the other four are unconstrained argmax over a
strategy-specific score, matching the paper's own description of them
as constraint-relaxed configurations.
"""

from __future__ import annotations

from dataclasses import dataclass
from typing import Literal

from civicworkos.scoring.scv import TermVector

StrategyName = Literal[
    "automation_first",
    "cost_performance",
    "human_first",
    "capability_matching",
    "civicworkos",
]


@dataclass(frozen=True)
class StrategyConfig:
    name: StrategyName
    restrict_to_human_containing: bool
    enforce_capability_constraints: bool  # HCPB, access, 3R, admissibility test


STRATEGIES: dict[StrategyName, StrategyConfig] = {
    "automation_first": StrategyConfig("automation_first", False, False),
    "cost_performance": StrategyConfig("cost_performance", False, False),
    "human_first": StrategyConfig("human_first", True, False),
    "capability_matching": StrategyConfig("capability_matching", False, False),
    "civicworkos": StrategyConfig("civicworkos", False, True),
}


def score_for_strategy(name: StrategyName, terms: TermVector, cad: float = 0.0) -> float:
    """The unconstrained score a strategy uses to rank modes.

    civicworkos's own score is Eq. 15 with the paper's default weights
    and is computed elsewhere (civicworkos.scoring.sustainable_civic_value)
    since CivicWorkOS additionally runs through the constrained engine;
    this function covers the four ablations.
    """
    if name == "automation_first":
        # "Maximizes quality and productivity" -- w9=0, no other penalty.
        return 0.5 * terms.Q + 0.5 * terms.P
    if name == "cost_performance":
        # "Maximizes (Q,P) net of Cost and En only."
        return 0.35 * terms.Q + 0.35 * terms.P - 0.20 * terms.Cost - 0.10 * terms.En
    if name in ("human_first", "capability_matching"):
        # Conventional Capability Matching: SCV with w9 removed and its
        # weight redistributed proportionally over w1..w8 (renormalized to
        # sum to 1), so the same eight flow terms are weighed in the same
        # RELATIVE proportion as the paper's default SCV, with no debt
        # penalty. Human-First uses the identical score but additionally
        # restricts the candidate set (enforced by the caller), matching
        # the paper's description of it as an H-containing restriction on
        # top of the same underlying fit criterion.
        default_pos = (0.15, 0.18, 0.14, 0.10, 0.05)  # w1..w5
        default_neg = (0.08, 0.03, 0.05)  # w6..w8
        scale = 1.0 / (sum(default_pos) + sum(default_neg))
        w1, w2, w3, w4, w5 = (w * scale for w in default_pos)
        w6, w7, w8 = (w * scale for w in default_neg)
        return (
            w1 * terms.Q + w2 * terms.S + w3 * terms.P + w4 * terms.Eq_srv + w5 * terms.Tr
            - w6 * terms.Cost - w7 * terms.En - w8 * terms.Pr
        )
    raise ValueError(f"unknown strategy {name!r}")
