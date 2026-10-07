"""[INVENTED -- Category C approximation, NOT paper content]

Paper sec:layer6 names ten market agents and what each estimates
(capability, quality, trust, cost, energy, safety, developmental share,
debt components, service equity, transition burden) but specifies NO
computation for any of them except D_skill = 1 - phi_m (eq:phi) and phi_H
= 1, phi_A = phi_R = phi_{A+R} = 0 (also eq:phi). The pre-release audit states
this plainly: "The framework's entire output is a function of numbers
no one currently knows how to produce."

`HeuristicMarket` is this repository's own deterministic, documented
stand-in for those ten agents, built so the simulation testbed
(civicworkos.sim) and the online rule (civicworkos.online) can be
exercised end-to-end on synthetic tasks. It is NOT used by the
worked-example oracle test (tests/smoke/test_worked_example.py), which
instead constructs term vectors directly from the paper's published
tab:worked-terms values -- this heuristic estimator has no claim to reproduce
those or any other paper number, and must never be cited as doing so.

The method: each pure mode (H, A, R) has a fixed "archetype" vector over
the eight flow terms and four non-skill debt components (D_skill is
always derived from phi_m, never estimated here). A task's nine demand
dimensions perturb the archetype by simple, documented rules (e.g.
higher risk_i raises the weight on safety and lowers AI/robot quality
for high-empathy tasks). A composite mode's estimate is the mean of its
constituent archetypes' perturbed vectors, then clipped to [0,1].
Nothing here should be read as a claim about real human, AI, or robot
performance.
"""

from __future__ import annotations

from dataclasses import dataclass
from datetime import date

from civicworkos.constraints.hcpb import phi_for_mode
from civicworkos.ledger.capability_ledger import LedgerSnapshot
from civicworkos.market.contracts import AgentEstimate
from civicworkos.policy.digital_twin import PolicyStatus
from civicworkos.scoring.cad import DebtComponents
from civicworkos.scoring.scv import TermVector
from civicworkos.twin.task import TaskProfile

_ARCHETYPES: dict[str, dict[str, float]] = {
    # quality, safety, productivity, equity, trust, cost, energy, privacy,
    # fallback_erosion, accountability_gap, vendor_dependency, transition_burden
    "H": dict(
        quality=0.60, safety=0.60, productivity=0.35, equity=0.65, trust=0.85,
        cost=0.85, energy=0.10, privacy=0.05,
        fallback=0.00, acct=0.00, dep=0.00, trans=0.00,
    ),
    "A": dict(
        quality=0.75, safety=0.50, productivity=0.85, equity=0.55, trust=0.55,
        cost=0.35, energy=0.50, privacy=0.55,
        fallback=0.60, acct=0.50, dep=0.70, trans=0.60,
    ),
    "R": dict(
        quality=0.70, safety=0.55, productivity=0.80, equity=0.55, trust=0.55,
        cost=0.40, energy=0.65, privacy=0.20,
        fallback=0.55, acct=0.35, dep=0.60, trans=0.55,
    ),
}

_DEFAULT_HYBRID_PHI = {"H+A": 0.75, "H+R": 0.70, "H+A+R": 0.55}
"""[INVENTED] Illustrative hybrid developmental shares, matching the
worked example's own illustrative values (Paper Table, sec:worked) as a
reasonable default -- NOT a claim that these are correct for any real
domain. Real deployments must elicit these per Paper sec:hcpb."""


def _clip01(x: float) -> float:
    return max(0.0, min(1.0, x))


def _components_of(mode: str) -> list[str]:
    return mode.split("+")


def _perturb(archetype: dict[str, float], task: TaskProfile, component: str) -> dict[str, float]:
    """[INVENTED] Nudge an archetype by the task's demand vector.

    Documented rules, all deliberately simple:
    - risk_i raises the effective weight on safety for every component.
    - emp_i (empathy) raises H's quality and trust, and lowers A/R's.
    - cog_i (cognitive load) raises A's quality and lowers H's productivity.
    - phy_i (physical demand) raises R's productivity and safety.
    - crit_i raises accountability-gap sensitivity for A and R.
    """
    v = dict(archetype)
    if component == "H":
        v["quality"] = _clip01(v["quality"] + 0.15 * task.emp - 0.05 * task.cog)
        v["trust"] = _clip01(v["trust"] + 0.10 * task.emp)
        v["productivity"] = _clip01(v["productivity"] - 0.10 * task.phy)
        v["safety"] = _clip01(v["safety"] + 0.10 * task.risk)
    elif component == "A":
        v["quality"] = _clip01(v["quality"] + 0.15 * task.cog - 0.10 * task.emp)
        v["safety"] = _clip01(v["safety"] - 0.15 * task.risk)
        v["acct"] = _clip01(v["acct"] + 0.15 * task.crit)
    elif component == "R":
        v["productivity"] = _clip01(v["productivity"] + 0.15 * task.phy)
        v["safety"] = _clip01(v["safety"] + 0.10 * task.phy - 0.10 * task.risk)
        v["acct"] = _clip01(v["acct"] + 0.10 * task.crit)
    return v


def _combine(vectors: list[dict[str, float]]) -> dict[str, float]:
    keys = vectors[0].keys()
    n = len(vectors)
    combined = {k: sum(v[k] for v in vectors) / n for k in keys}
    # Redundancy bonus: a multi-component mode is a LITTLE safer than the
    # mean of its parts (independent failure paths) -- an invented, small,
    # documented effect capped so it cannot push safety above 1.
    if n > 1:
        combined["safety"] = _clip01(combined["safety"] + 0.03 * (n - 1))
    return combined


@dataclass
class HeuristicMarket:
    """[INVENTED] Deterministic stand-in for the ten market agents of sec:layer6.

    hybrid_phi: per-domain hybrid developmental shares (eq:phi); falls
        back to `_DEFAULT_HYBRID_PHI` if a domain has not configured its own.
    oversight_cost_penalty: [REC] extra Cost, and oversight_phi_boost extra
        phi_m, applied when the policy status is allow_with_oversight
        (Algorithm 1 line 7 requires both effects; the paper gives no
        magnitude for either, so these are explicit, overridable constants).
    """

    hybrid_phi: dict[str, dict[str, float]] | None = None
    oversight_cost_penalty: float = 0.05
    oversight_phi_boost: float = 0.05

    def query(
        self,
        task: TaskProfile,
        mode: str,
        policy_status: PolicyStatus,
        ledger: LedgerSnapshot,
        t: date | None = None,
    ) -> AgentEstimate:
        components = _components_of(mode)
        perturbed = [_perturb(_ARCHETYPES[c], task, c) for c in components]
        combined = _combine(perturbed)

        domain_phi = (self.hybrid_phi or {}).get(task.domain, _DEFAULT_HYBRID_PHI)
        phi_m = phi_for_mode(mode, domain_phi)

        cost = combined["cost"]
        if policy_status == PolicyStatus.ALLOW_WITH_OVERSIGHT:
            cost = _clip01(cost + self.oversight_cost_penalty)
            phi_m = _clip01(phi_m + self.oversight_phi_boost)

        terms = TermVector(
            Q=combined["quality"],
            S=combined["safety"],
            P=combined["productivity"],
            Eq_srv=combined["equity"],
            Tr=combined["trust"],
            Cost=cost,
            En=combined["energy"],
            Pr=combined["privacy"],
        )
        debts = DebtComponents(
            D_skill=1.0 - phi_m,  # eq:phi: the one component the paper does specify.
            D_fall=combined["fallback"],
            D_acct=combined["acct"],
            D_dep=combined["dep"],
            D_trans=combined["trans"],
        )
        return AgentEstimate(terms=terms, debts=debts, phi_m=phi_m)
