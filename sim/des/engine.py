"""Simulation engine: a REDUCED-SCOPE stand-in for Paper Sec. 6.1's "city
digital twin and multi-agent discrete-event simulation."

Scope reduction (documented in docs/assumptions.md A10, not hidden):
this is a TIME-STEPPED sequential task processor, not a priority-queue
discrete-event engine, and it runs over a short demo horizon (a
configurable number of synthetic tasks) rather than the paper's ten
simulated years across six sectors. It computes a SUBSET of the
paper's thirteen metrics (Sec. 6.3):

    IMPLEMENTED (approximated on synthetic data):
      - productivity_index, operating_cost_index (raw means; the paper
        normalizes both to Automation-First = 100, done by the caller)
      - accumulated_cad (running sum of Eq. 2)
      - capability_formation_index (delivered practice hours / B_k)
      - z4_routing_rate (CivicWorkOS only -- the other four strategies
        have no Z4 fallback concept in this reduced model)

    NOT IMPLEMENTED here (report Sec. 12.4 items 4-5, 10-13):
      safety incidents, energy use index, mean recovery time (no stress-
      scenario injection wired into this loop -- see sim.stress for the
      scenario definitions themselves), realized dual reporting beyond a
      single rebalance, protected-practice share by group Pi_{k,g} beyond
      what AllocationEngine already tracks internally, displacement
      Delta_g, service-equity dispersion, and contestability throughput.

Nothing this engine produces should be cited as reproducing the paper's
(nonexistent) evaluation results -- see docs/reproducibility.md.
"""

from __future__ import annotations

from dataclasses import dataclass, field
from datetime import date, datetime, timezone

from civicworkos.audit.evidentiary_record import EvidentiaryRecordStore
from civicworkos.constraints.hcpb import HCPBParameters
from civicworkos.constraints.resilience import ReserveState
from civicworkos.feedback.bus import FeedbackBus
from civicworkos.ledger.capability_ledger import CapabilityLedger, LedgerSnapshot
from civicworkos.market.agents import HeuristicMarket
from civicworkos.online.algorithm1 import AllocationEngine, Duals
from civicworkos.policy.digital_twin import PolicyDigitalTwin
from civicworkos.scoring.cad import DebtWeights, civic_automation_debt
from civicworkos.scoring.scv import ScoreWeights
from civicworkos.twin.task import TaskProfile
from sim.strategies.baselines import STRATEGIES, StrategyName, score_for_strategy


@dataclass
class SimulationMetrics:
    strategy: StrategyName
    n_tasks: int = 0
    n_z4: int = 0
    sum_productivity: float = 0.0
    sum_cost: float = 0.0
    accumulated_cad: float = 0.0
    delivered_practice_hours: float = 0.0
    mode_counts: dict[str, int] = field(default_factory=dict)

    @property
    def n_allocated(self) -> int:
        return self.n_tasks - self.n_z4

    @property
    def productivity_index(self) -> float:
        denom = self.n_allocated if self.n_allocated > 0 else self.n_tasks
        return (self.sum_productivity / denom * 100.0) if denom else 0.0

    @property
    def operating_cost_index(self) -> float:
        denom = self.n_allocated if self.n_allocated > 0 else self.n_tasks
        return (self.sum_cost / denom * 100.0) if denom else 0.0

    @property
    def z4_routing_rate(self) -> float:
        return (self.n_z4 / self.n_tasks) if self.n_tasks else 0.0

    def capability_formation_index(self, budget_hours: float) -> float:
        return (self.delivered_practice_hours / budget_hours) if budget_hours > 0 else 0.0


def _run_unconstrained_strategy(
    strategy: StrategyName,
    tasks: list[TaskProfile],
    policy_twin: PolicyDigitalTwin,
    market: HeuristicMarket,
    reference_date: date,
) -> SimulationMetrics:
    """Run one of the four ablation strategies (no Eq. 8/11/12/14 enforcement)."""
    metrics = SimulationMetrics(strategy=strategy)
    if not tasks:
        return metrics
    config = STRATEGIES[strategy]
    debt_weights = DebtWeights.paper_default()
    ledger = LedgerSnapshot(domain=tasks[0].domain, H_k=0, A_k=0, R_k=0, F_k=0, E_k=0)

    for task in tasks:
        surviving = policy_twin.filter_modes(task, t=reference_date)
        if config.restrict_to_human_containing:
            # Human-First: prioritizes pure human execution ("H") wherever policy permits;
            # falls back to human-bearing hybrid modes if pure H is restricted.
            if "H" in surviving:
                surviving = {"H": surviving["H"]}
            else:
                surviving = {m: s for m, s in surviving.items() if "H" in m.split("+")}

        if not surviving:
            metrics.n_z4 += 1
            metrics.n_tasks += 1
            metrics.mode_counts["Z4_human_reserved"] = metrics.mode_counts.get("Z4_human_reserved", 0) + 1
            continue

        best_score, best_estimate, best_mode = float("-inf"), None, None
        for mode, status in surviving.items():
            estimate = market.query(task, mode, status, ledger, reference_date)
            score = score_for_strategy(strategy, estimate.terms)
            if score > best_score:
                best_score, best_estimate, best_mode = score, estimate, mode

        cad = civic_automation_debt(best_estimate.debts, debt_weights)
        metrics.n_tasks += 1
        metrics.sum_productivity += best_estimate.terms.P
        metrics.sum_cost += best_estimate.terms.Cost
        metrics.accumulated_cad += cad
        metrics.delivered_practice_hours += task.ell * best_estimate.phi_m
        if best_mode is not None:
            metrics.mode_counts[best_mode] = metrics.mode_counts.get(best_mode, 0) + 1

    return metrics


def run_strategy(
    strategy: StrategyName,
    tasks: list[TaskProfile],
    *,
    policy_twin: PolicyDigitalTwin,
    market: HeuristicMarket,
    hcpb_params: HCPBParameters,
    reserve_states: dict[str, ReserveState],
    access_constraints: dict,
    worker_groups: dict[str, list[str]],
    duals: Duals | None = None,
    reference_date: date | None = None,
) -> SimulationMetrics:
    """Run one strategy over a batch of tasks and return reduced-scope metrics.

    CivicWorkOS runs through the real constrained AllocationEngine
    (Eq. 8, 11-12, 14, 17-19); the other four strategies run through the
    unconstrained ablation scorer above, matching Paper Sec. 6.2's own
    description of them as constraint-relaxed configurations.
    """
    reference_date = reference_date or date.today()
    if strategy != "civicworkos":
        return _run_unconstrained_strategy(strategy, tasks, policy_twin, market, reference_date)

    metrics = SimulationMetrics(strategy=strategy)
    if not tasks:
        return metrics

    domain = tasks[0].domain
    ledger = CapabilityLedger()
    ledger.initialize(LedgerSnapshot(domain=domain, H_k=0, A_k=0, R_k=0, F_k=0, E_k=0))

    active_duals = duals or Duals(
        lambda_k={domain: 0.0250},
        rebalance_timestamp=datetime.now(timezone.utc),
    )

    engine = AllocationEngine(
        policy_twin=policy_twin,
        market=market,
        ledger=ledger,
        hcpb_params={domain: hcpb_params},
        reserve_states=reserve_states,
        access_constraints=access_constraints,
        worker_groups=worker_groups,
        score_weights=ScoreWeights.paper_default(),
        debt_weights=DebtWeights.paper_default(),
        duals=active_duals,
        audit_store=EvidentiaryRecordStore(),
        feedback_bus=FeedbackBus(),
        config_version="sim-demo-v1",
        authorizing_panel_decision="sim-demo-panel-decision",
    )

    for i, task in enumerate(tasks):
        elapsed_days = 365.0 * (i + 1) / max(len(tasks), 1)
        result = engine.allocate(task, reference_date, elapsed_days)
        metrics.n_tasks += 1
        metrics.mode_counts[result.selected_mode] = metrics.mode_counts.get(result.selected_mode, 0) + 1
        metrics.delivered_practice_hours = ledger.current(domain).accrued_practice_hours
        if result.is_z4_fallback:
            metrics.n_z4 += 1
            continue
        selected = next(c for c in result.evidentiary_record.candidates if c.mode == result.selected_mode)
        metrics.sum_productivity += selected.terms["P"]
        metrics.sum_cost += selected.terms["Cost"]
        metrics.accumulated_cad += selected.cad

    return metrics
