"""Integration test: every stored decision replays to the same m*.

The pre-release audit states this as Phase 9's validation criterion: "every
stored decision can be replayed from its record to the same m*." This
test runs Algorithm 1 via AllocationEngine, then reconstructs the
argmax purely from the stored EvidentiaryRecord (not from re-running the
engine), proving the record is sufficient on its own to reproduce the
decision -- the point of Suppl. S1.3's requirement that the record carry
every candidate's full pricing, not just the winner.
"""

from __future__ import annotations

from datetime import date, datetime

from civicworkos.audit.evidentiary_record import EvidentiaryRecordStore
from civicworkos.constraints.hcpb import HCPBParameters
from civicworkos.constraints.resilience import ReserveState
from civicworkos.feedback.bus import FeedbackBus
from civicworkos.ledger.capability_ledger import CapabilityLedger, LedgerSnapshot
from civicworkos.market.contracts import AgentEstimate, MarketProtocol
from civicworkos.online.algorithm1 import AllocationEngine, Duals
from civicworkos.policy.digital_twin import PolicyDigitalTwin, requires_licensed_human_rule
from civicworkos.scoring.cad import DebtComponents, DebtWeights
from civicworkos.scoring.scv import ScoreWeights, TermVector
from civicworkos.twin.task import TaskProfile

DOMAIN = "structural_inspection"
SERVICE = "structural_inspection_service"

_TABLE3 = {
    "H": dict(Q=0.72, S=0.55, P=0.40, Eq_srv=0.70, Tr=0.80, Cost=0.85, En=0.20, Pr=0.10,
              D=(0.00, 0.00, 0.00, 0.00, 0.00), phi=1.00),
    "H+A": dict(Q=0.86, S=0.60, P=0.62, Eq_srv=0.72, Tr=0.74, Cost=0.62, En=0.28, Pr=0.25,
                D=(0.25, 0.15, 0.07, 0.30, 0.10), phi=0.75),
    "H+R": dict(Q=0.80, S=0.88, P=0.70, Eq_srv=0.70, Tr=0.72, Cost=0.58, En=0.55, Pr=0.30,
                D=(0.30, 0.25, 0.05, 0.35, 0.20), phi=0.70),
    "H+A+R": dict(Q=0.91, S=0.90, P=0.88, Eq_srv=0.74, Tr=0.68, Cost=0.50, En=0.60, Pr=0.38,
                  D=(0.45, 0.35, 0.13, 0.50, 0.30), phi=0.55),
}


class FixtureMarket(MarketProtocol):
    def query(self, task, mode, policy_status, ledger, t=None) -> AgentEstimate:
        row = _TABLE3[mode]
        terms = TermVector(Q=row["Q"], S=row["S"], P=row["P"], Eq_srv=row["Eq_srv"], Tr=row["Tr"],
                            Cost=row["Cost"], En=row["En"], Pr=row["Pr"])
        debts = DebtComponents(D_skill=row["D"][0], D_fall=row["D"][1], D_acct=row["D"][2],
                                D_dep=row["D"][3], D_trans=row["D"][4])
        return AgentEstimate(terms=terms, debts=debts, phi_m=row["phi"])


def _engine(lambda_k: float) -> AllocationEngine:
    policy_twin = PolicyDigitalTwin()
    policy_twin.add_rule(requires_licensed_human_rule("signoff", "v1", date(2020, 1, 1), "d"))
    ledger = CapabilityLedger()
    ledger.initialize(LedgerSnapshot(domain=DOMAIN, H_k=0, A_k=0, R_k=0, F_k=0, E_k=0))
    reserve = ReserveState(
        component_capacities={"a": 100_000.0, "b": 100_000.0}, n_s=1, kappa_s=0.01, peak_demand=1.0
    )
    return AllocationEngine(
        policy_twin=policy_twin,
        market=FixtureMarket(),
        ledger=ledger,
        hcpb_params={DOMAIN: HCPBParameters(N_k=24, r_k=0.12, h_k=1440, eta_k=1.2, B_k_min=2000)},
        reserve_states={SERVICE: reserve},
        access_constraints={},
        worker_groups={DOMAIN: ["men", "women"]},
        score_weights=ScoreWeights.paper_default(),
        debt_weights=DebtWeights.paper_default(),
        duals=Duals(lambda_k={DOMAIN: lambda_k}, rebalance_timestamp=datetime(2026, 1, 1)),
        audit_store=EvidentiaryRecordStore(),
        feedback_bus=FeedbackBus(),
        config_version="v2026-09-01",
        authorizing_panel_decision="PANEL-2026-001",
        safety_floor_fn=lambda task: 0.0,
    )


def _task() -> TaskProfile:
    return TaskProfile(
        task_id="bridge-1", service=SERVICE, domain=DOMAIN,
        cog=0.80, phy=0.60, emp=0.10, risk=0.70, auth=0.90, priv=0.20, urg=0.40,
        learn=0.80, crit=0.90, duration_hours=10.0,
    )


def _recompute_argmax_from_record(record) -> str:
    """Reconstruct m* using ONLY what the stored record carries -- the
    per-candidate scv_tilde values -- not by re-running the market or
    the engine. This is the actual replay Suppl. S1.3 is meant to enable.
    """
    admissible = [c for c in record.candidates if c.scv_tilde is not None]
    return max(admissible, key=lambda c: c.scv_tilde).mode


def test_decision_replays_from_its_own_record_unconstrained():
    engine = _engine(lambda_k=0.0)
    result = engine.allocate(_task(), date(2026, 1, 1), elapsed_days_in_period=0.0)
    assert engine.audit_store.validate_replay(result.evidentiary_record, _recompute_argmax_from_record)


def test_decision_replays_from_its_own_record_with_capability_price():
    engine = _engine(lambda_k=0.0599 / 2.4)
    result = engine.allocate(_task(), date(2026, 1, 1), elapsed_days_in_period=0.0)
    assert engine.audit_store.validate_replay(result.evidentiary_record, _recompute_argmax_from_record)


def test_stored_record_exposes_rejected_candidates_not_only_the_winner():
    """A record that omitted rejected candidates would make it impossible
    to show what was NOT chosen -- the pre-release audit's named failure mode."""
    engine = _engine(lambda_k=0.0)
    result = engine.allocate(_task(), date(2026, 1, 1), elapsed_days_in_period=0.0)
    record = result.evidentiary_record
    policy_rejected_modes = {r.mode for r in record.rejections if r.stage == "policy_filter"}
    assert policy_rejected_modes == {"A", "R", "A+R"}
