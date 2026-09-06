r"""Algorithm 1 -- Online Policy-Aware Sustainable Civic Value Allocation.

Paper Sec. 4.5, Eq. 17-19; control flow in Fig. 2 (Sec. 4.2).

    SCV~_{i,m} = SCV_{i,m} + lambda_{k(i)}*ell_i*phi_m
               + mu_{s(i)}*Delta^res_{s(i)}(m)
               + nu_{k(i),g(i,m)}*ell_i*phi_m                                (Eq. 17)

    m in A(i,t) iff
        P(T_i,m,t) != prohibit  AND  S_{i,m} >= S^min_i  AND
        [ Res^(n_s)_s(t+|m) >= rho_s  OR  (Res^(n_s)_s(t) < rho_s AND Delta^res_s(m) >= 0) ]  AND
        [ Lambda_k(t+|m) >= Bbar_k(t)  OR  (Lambda_k(t) < Bbar_k(t) AND phi_m > 0) ]           (Eq. 18)

    m*_i = argmax_{m in A(i,t)} SCV~_{i,m}                                    (Eq. 19)

with Bbar_k(t) = B_k(t) * t/DeltaT, the pro-rated budget trajectory.

Eq. 18's admissibility test is NOT a naive per-constraint filter. The
paper is explicit about why (Sec. 4.5): testing (16e)/(16h) as written
inside a loop over m would remove either every candidate or none, and a
city already below threshold would route every task to Z4 -- "including
the robot allocations that would free the human capacity needed to climb
back above threshold." Each bracket therefore reads: leave the
constraint satisfied, OR (if already violated) do not worsen it and
contribute to restoring it. `admissible()` below implements exactly this
reading, and tests/unit/test_admissibility.py exercises both restoration
branches explicitly so this property cannot regress silently.

Three quantities Algorithm 1 needs have no computation specified by the
paper, and are supplied here as explicit, overridable, documented
inventions rather than hidden defaults (report Sec. 14.3, items 3-4):

  - S^min_i, the per-task safety floor -- `default_safety_floor()`.
  - Delta^res_s(m) at task granularity -- civicworkos.constraints.resilience.task_delta_resilience.
  - g(i,m), the assignee's group -- `select_assignee_group()`.
"""

from __future__ import annotations

from collections.abc import Callable
from dataclasses import dataclass, field
from datetime import date, datetime, timezone

from civicworkos import MODES
from civicworkos.audit.evidentiary_record import (
    CandidateRecord,
    EvidentiaryRecord,
    EvidentiaryRecordStore,
    RejectionRecord,
)
from civicworkos.constraints.access import CapabilityAccessConstraint
from civicworkos.constraints.hcpb import HCPBParameters, capability_budget
from civicworkos.constraints.resilience import ReserveState, resilience_reserve, task_delta_resilience
from civicworkos.feedback.bus import FeedbackBus, Outcome
from civicworkos.ledger.capability_ledger import CapabilityLedger
from civicworkos.market.contracts import AgentEstimate, MarketProtocol, MarketTimeoutError
from civicworkos.policy.digital_twin import PolicyDigitalTwin
from civicworkos.scoring.cad import DebtWeights, civic_automation_debt
from civicworkos.scoring.scv import ScoreWeights, sustainable_civic_value
from civicworkos.twin.task import TaskProfile

ZONE_Z4 = "Z4_human_reserved"


def default_safety_floor(task: TaskProfile) -> float:
    """[INVENTED] S^min_i is used in Eq. 16d/18 but never defined by the
    paper. This default scales the floor with task risk and criticality
    (a riskier or more critical task demands a higher safety floor) and
    is fully overridable by callers -- see docs/assumptions.md A7.

    Calibrated to civicworkos.market.agents.HeuristicMarket's [0.4, 0.9]-
    ish typical safety-estimate range: a low-risk, low-criticality task
    gets a permissive floor (~0.3), and only a high-risk, high-criticality
    task pushes the floor high enough to exclude most modes. A
    higher-baseline floor would reject every mode for nearly every task
    regardless of risk, which is not a meaningful safety gate.
    """
    return min(0.95, 0.30 + 0.35 * task.risk + 0.25 * task.crit)


def select_assignee_group(
    domain: str,
    groups: list[str],
    realized_hours_by_group: dict[str, float],
    access_constraints: dict[tuple[str, str], CapabilityAccessConstraint],
) -> str:
    """[INVENTED] g(i,m): which group's member performs this task.

    The paper needs assignee(i,m) for Eq. 10 and Eq. 17's nu term but
    never specifies how the assignee is chosen within a mode (report
    Sec. 14.3 item 4). This greedy heuristic assigns to whichever group
    is furthest BELOW its target share theta_{k,g} (Eq. 11), which is
    the natural policy the access constraint's dual nu_{k,g} is meant to
    price -- but it is this repository's invention, not the paper's.
    """
    if not groups:
        raise ValueError("at least one worker group must be defined")
    total = sum(realized_hours_by_group.get(g, 0.0) for g in groups) or 1.0
    deficits = {}
    for g in groups:
        share = realized_hours_by_group.get(g, 0.0) / total
        constraint = access_constraints.get((domain, g))
        target = constraint.theta_kg if constraint is not None else 1.0 / len(groups)
        deficits[g] = target - share
    return max(deficits, key=lambda g: deficits[g])


@dataclass(frozen=True)
class Duals:
    """The most recent solution of Eq. 16's dual prices.

    lambda_k: HCPB dual (16e) per domain -- "literally what one hour of
        qualified practice in domain k is worth to the city," published.
    mu_s: 3R Reserve dual (16h) per service.
    nu_kg: access-constraint dual (16f) per (domain, group).
    """

    lambda_k: dict[str, float] = field(default_factory=dict)
    mu_s: dict[str, float] = field(default_factory=dict)
    nu_kg: dict[tuple[str, str], float] = field(default_factory=dict)
    rebalance_timestamp: datetime = field(default_factory=lambda: datetime.now(timezone.utc))


def admissible(
    *,
    safety_estimate: float,
    safety_min: float,
    resilience_now: float,
    delta_res: float,
    rho_s: float,
    lambda_accrued_now: float,
    ell_i: float,
    phi_m: float,
    b_bar_k: float,
) -> tuple[bool, str | None]:
    """Eq. 18, all three clauses, with both feasibility-restoration branches.

    Returns (is_admissible, rejection_reason). `rejection_reason` is one
    of "safety_floor", "resilience_clause", "capability_clause", or None.
    """
    if safety_estimate < safety_min:
        return False, "safety_floor"

    resilience_post = resilience_now + delta_res
    resilience_ok = resilience_post >= rho_s or (resilience_now < rho_s and delta_res >= 0)
    if not resilience_ok:
        return False, "resilience_clause"

    lambda_post = lambda_accrued_now + ell_i * phi_m
    capability_ok = lambda_post >= b_bar_k or (lambda_accrued_now < b_bar_k and phi_m > 0)
    if not capability_ok:
        return False, "capability_clause"

    return True, None


@dataclass
class AllocationResult:
    """What Algorithm 1 returns for one task, plus enough detail for callers to inspect."""

    task_id: str
    selected_mode: str
    is_z4_fallback: bool
    scv_tilde_by_mode: dict[str, float]
    evidentiary_record: EvidentiaryRecord
    record_hash: str


class AllocationEngine:
    """Orchestrates Algorithm 1 end to end using the paper's own components.

    Every collaborator below corresponds to a named component in Fig. 1 /
    Table in report Sec. 5.2; the engine itself performs no pricing or
    constraint logic of its own beyond composing them in the order
    Algorithm 1 specifies.
    """

    def __init__(
        self,
        *,
        policy_twin: PolicyDigitalTwin,
        market: MarketProtocol,
        ledger: CapabilityLedger,
        hcpb_params: dict[str, HCPBParameters],
        reserve_states: dict[str, ReserveState],
        access_constraints: dict[tuple[str, str], CapabilityAccessConstraint],
        worker_groups: dict[str, list[str]],  # domain -> [group ids]
        score_weights: ScoreWeights,
        debt_weights: DebtWeights,
        duals: Duals,
        audit_store: EvidentiaryRecordStore,
        feedback_bus: FeedbackBus,
        config_version: str,
        authorizing_panel_decision: str,
        budget_period_days: float = 365.0,
        safety_floor_fn: Callable[[TaskProfile], float] = default_safety_floor,
        modes: tuple[str, ...] = MODES,
    ) -> None:
        self.policy_twin = policy_twin
        self.market = market
        self.ledger = ledger
        self.hcpb_params = hcpb_params
        self.reserve_states = reserve_states
        self.access_constraints = access_constraints
        self.worker_groups = worker_groups
        self.score_weights = score_weights
        self.debt_weights = debt_weights
        self.duals = duals
        self.audit_store = audit_store
        self.feedback_bus = feedback_bus
        self.config_version = config_version
        self.authorizing_panel_decision = authorizing_panel_decision
        self.budget_period_days = budget_period_days
        self.safety_floor_fn = safety_floor_fn
        self.modes = modes
        self._group_hours: dict[str, dict[str, float]] = {}
        self.policy_compliance_log: list[Outcome] = []

        # Fig. 1's required property: the SAME bus event updates BOTH
        # governance services -- the Ledger (practice accrual) and the
        # Policy Twin's compliance-monitoring side (here, a log that
        # zone-transition and rule-staleness monitoring can read). Wiring
        # only one destination is the failure mode the caption warns
        # against, so both subscribers are registered together and neither
        # can be added without the other by a caller of this class.
        self.feedback_bus.subscribe(self._accrue_ledger_on_outcome)
        self.feedback_bus.subscribe(self._log_for_policy_compliance)

    def _accrue_ledger_on_outcome(self, outcome: Outcome) -> None:
        """Ledger side of Eq. 20: accrue Lambda_k from the emitted outcome.

        Machine outcomes (AI/robot channels) update the ledger exactly
        like human ones -- Fig. 1's caption is explicit that the Ledger
        holds AI and robot capability terms that cannot be maintained if
        machine outcomes bypass it.
        """
        if outcome.event_type != "execution_outcome":
            return
        ell_times_phi = outcome.payload.get("ell_times_phi")
        if ell_times_phi is not None:
            self.ledger.accrue_practice(outcome.domain, ell_times_phi)

    def _log_for_policy_compliance(self, outcome: Outcome) -> None:
        """Policy-Twin side of Eq. 20: compliance monitoring depends on
        human outcomes as much as machine ones (Fig. 1 caption). This
        repository does not mutate the rule base from outcomes (rule
        changes are versioned policy acts per Sec. 5.1); it records the
        outcome stream that a rule-staleness or zone-transition monitor
        (civicworkos.zones) would consume.
        """
        self.policy_compliance_log.append(outcome)

    def _pro_rated_budget(self, domain: str, elapsed_days: float) -> float:
        b_k = capability_budget(self.hcpb_params[domain])
        return b_k * (elapsed_days / self.budget_period_days)

    def allocate(
        self,
        task: TaskProfile,
        t: date,
        elapsed_days_in_period: float,
    ) -> AllocationResult:
        """Run Algorithm 1 for one task and return the selected mode."""
        ell_i = task.ell
        domain = task.domain
        service = task.service

        surviving = self.policy_twin.filter_modes(task, self.modes, t)
        rejections: list[RejectionRecord] = []
        for mode in self.modes:
            if mode not in surviving:
                status = self.policy_twin.status(task, mode, t)
                rejections.append(RejectionRecord(mode=mode, stage="policy_filter", reason=status.value))

        if not surviving:
            return self._route_to_z4(task, ell_i, rejections, [], reason="all modes prohibited")

        ledger_snapshot = self.ledger.current(domain)
        reserve_state = self.reserve_states[service]
        resilience_now = resilience_reserve(reserve_state)
        rho_s = reserve_state.rho_s
        b_bar_k = self._pro_rated_budget(domain, elapsed_days_in_period)
        lambda_now = ledger_snapshot.accrued_practice_hours
        safety_min = self.safety_floor_fn(task)

        candidates: list[CandidateRecord] = []
        admissible_scores: dict[str, float] = {}

        for mode, status in surviving.items():
            try:
                estimate: AgentEstimate = self.market.query(task, mode, status, ledger_snapshot, t)
            except MarketTimeoutError:
                rejections.append(RejectionRecord(mode=mode, stage="policy_filter", reason="market_timeout"))
                continue

            cad = civic_automation_debt(estimate.debts, self.debt_weights)
            scv = sustainable_civic_value(estimate.terms, cad, self.score_weights)

            delta_res = task_delta_resilience(mode, task.duration_hours, reserve_state.total_capacity)

            ok, why = admissible(
                safety_estimate=estimate.terms.S,
                safety_min=safety_min,
                resilience_now=resilience_now,
                delta_res=delta_res,
                rho_s=rho_s,
                lambda_accrued_now=lambda_now,
                ell_i=ell_i,
                phi_m=estimate.phi_m,
                b_bar_k=b_bar_k,
            )
            if not ok:
                rejections.append(RejectionRecord(mode=mode, stage="admissibility_test", reason=why or "unknown"))
                candidates.append(
                    CandidateRecord(
                        mode=mode,
                        terms=estimate.terms.__dict__,
                        debts=estimate.debts.__dict__,
                        cad=cad,
                        scv=scv,
                        scv_tilde=None,
                    )
                )
                continue

            groups = self.worker_groups.get(domain, ["unspecified"])
            hours_by_group = self._group_hours.setdefault(domain, {})
            g = select_assignee_group(domain, groups, hours_by_group, self.access_constraints)

            lambda_k = self.duals.lambda_k.get(domain, 0.0)
            mu_s = self.duals.mu_s.get(service, 0.0)
            nu_kg = self.duals.nu_kg.get((domain, g), 0.0)

            scv_tilde = (
                scv
                + lambda_k * ell_i * estimate.phi_m
                + mu_s * delta_res
                + nu_kg * ell_i * estimate.phi_m
            )
            admissible_scores[mode] = scv_tilde
            candidates.append(
                CandidateRecord(
                    mode=mode,
                    terms=estimate.terms.__dict__,
                    debts=estimate.debts.__dict__,
                    cad=cad,
                    scv=scv,
                    scv_tilde=scv_tilde,
                )
            )

        if not admissible_scores:
            return self._route_to_z4(task, ell_i, rejections, candidates, reason="admissible set emptied")

        m_star = max(admissible_scores, key=lambda m: admissible_scores[m])
        estimate_star = self.market.query(task, m_star, surviving[m_star], ledger_snapshot, t)

        hours_by_group = self._group_hours.setdefault(domain, {})
        groups = self.worker_groups.get(domain, ["unspecified"])
        g_star = select_assignee_group(domain, groups, hours_by_group, self.access_constraints)
        hours_by_group[g_star] = hours_by_group.get(g_star, 0.0) + ell_i * estimate_star.phi_m

        record = EvidentiaryRecord(
            task_id=task.task_id,
            domain=domain,
            service=service,
            d_i=task.duration_hours,
            ell_i=ell_i,
            drafted_modes=self.modes,
            rejections=tuple(rejections),
            candidates=tuple(candidates),
            selected_mode=m_star,
            duals_in_force={
                **{f"lambda_{k}": v for k, v in self.duals.lambda_k.items()},
                **{f"mu_{s}": v for s, v in self.duals.mu_s.items()},
            },
            rebalance_timestamp=self.duals.rebalance_timestamp,
            config_version=self.config_version,
            authorizing_panel_decision=self.authorizing_panel_decision,
            accountable_human=None,
        )
        record_hash = self.audit_store.add(record)

        self.feedback_bus.emit(
            Outcome(
                task_id=task.task_id,
                domain=domain,
                service=service,
                mode=m_star,
                channel=_channel_for_mode(m_star),
                event_type="execution_outcome",
                payload={
                    "phi_m": estimate_star.phi_m,
                    "ell_times_phi": ell_i * estimate_star.phi_m,
                    "cad": next(c.cad for c in candidates if c.mode == m_star),
                },
                timestamp=datetime.now(timezone.utc),
            )
        )

        return AllocationResult(
            task_id=task.task_id,
            selected_mode=m_star,
            is_z4_fallback=False,
            scv_tilde_by_mode=admissible_scores,
            evidentiary_record=record,
            record_hash=record_hash,
        )

    def _route_to_z4(
        self,
        task: TaskProfile,
        ell_i: float,
        rejections: list[RejectionRecord],
        candidates: list[CandidateRecord],
        reason: str,
    ) -> AllocationResult:
        """Algorithm 1, lines 14-16: an empty admissible set routes to Z4
        human-reserved, "rather than leaving the argmax undefined."
        """
        record = EvidentiaryRecord(
            task_id=task.task_id,
            domain=task.domain,
            service=task.service,
            d_i=task.duration_hours,
            ell_i=ell_i,
            drafted_modes=self.modes,
            rejections=tuple(rejections),
            candidates=tuple(candidates),
            selected_mode=ZONE_Z4,
            duals_in_force={
                **{f"lambda_{k}": v for k, v in self.duals.lambda_k.items()},
                **{f"mu_{s}": v for s, v in self.duals.mu_s.items()},
            },
            rebalance_timestamp=self.duals.rebalance_timestamp,
            config_version=self.config_version,
            authorizing_panel_decision=self.authorizing_panel_decision,
            accountable_human=None,
        )
        record_hash = self.audit_store.add(record)
        self.feedback_bus.emit(
            Outcome(
                task_id=task.task_id,
                domain=task.domain,
                service=task.service,
                mode=ZONE_Z4,
                channel="human",
                event_type="execution_outcome",
                payload={"reason": reason, "ell_times_phi": task.ell * 1.0},
                timestamp=datetime.now(timezone.utc),
            )
        )
        return AllocationResult(
            task_id=task.task_id,
            selected_mode=ZONE_Z4,
            is_z4_fallback=True,
            scv_tilde_by_mode={},
            evidentiary_record=record,
            record_hash=record_hash,
        )


def _channel_for_mode(mode: str) -> str:
    components = mode.split("+")
    if "H" in components and len(components) == 1:
        return "human"
    if "R" in components:
        return "robot"
    return "ai"
