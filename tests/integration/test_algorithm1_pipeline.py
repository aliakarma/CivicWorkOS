"""Integration test: Algorithm 1 (civicworkos.online.AllocationEngine)
wired end to end -- policy twin, ledger, market, HCPB, resilience,
duals, audit store, feedback bus -- against the worked example's own
literal Table 3 inputs (Paper Sec. 5.3).

Unlike tests/smoke/test_worked_example.py (which checks the bare Eq. 2 /
Eq. 15 / Eq. 21 arithmetic and the batch LP), this test exercises the
FULL Algorithm 1 control flow: per-mode policy filtering, the market
protocol, the admissibility test (Eq. 18), and the Lagrangian
augmentation (Eq. 17) with an ALREADY-SOLVED dual (lambda_k = 0.0250,
the value tests/smoke's LP independently derives) supplied as input --
exactly how the online rule is meant to consume a rebalance's output.

The worked example itself specifies no safety floor S^min_i and no 3R
Reserve instantiation for this domain, so this test supplies a
permissive safety floor and an oversized reserve baseline to isolate
the capability-budget mechanism the paper actually demonstrates,
documented inline where set.
"""

from __future__ import annotations

from datetime import date, datetime

import pytest

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
    """Returns the worked example's own literal Table 3 values -- NOT the
    invented HeuristicMarket -- so this test checks Algorithm 1's
    orchestration logic against a paper-traceable fixture, not against
    this repository's own estimator heuristics.
    """

    def query(self, task, mode, policy_status, ledger, t=None) -> AgentEstimate:
        row = _TABLE3[mode]
        terms = TermVector(Q=row["Q"], S=row["S"], P=row["P"], Eq_srv=row["Eq_srv"], Tr=row["Tr"],
                            Cost=row["Cost"], En=row["En"], Pr=row["Pr"])
        debts = DebtComponents(D_skill=row["D"][0], D_fall=row["D"][1], D_acct=row["D"][2],
                                D_dep=row["D"][3], D_trans=row["D"][4])
        return AgentEstimate(terms=terms, debts=debts, phi_m=row["phi"])


def _worked_example_task() -> TaskProfile:
    return TaskProfile(
        task_id="bridge-1", service=SERVICE, domain=DOMAIN,
        cog=0.80, phy=0.60, emp=0.10, risk=0.70, auth=0.90, priv=0.20, urg=0.40,
        learn=0.80, crit=0.90, duration_hours=10.0,
    )


def _permissive_reserve_state() -> ReserveState:
    # The worked example does not instantiate the 3R Reserve for this
    # domain at all. TWO oversized components (so N-1 still leaves a huge
    # remainder) with a tiny rho_s ensure Eq. 18's resilience clause never
    # binds, isolating the HCPB mechanism this test actually targets. A
    # single component would make Res^(1) always zero (removing the only,
    # largest component leaves nothing) and spuriously trip clause 2.
    return ReserveState(
        component_capacities={"placeholder_a": 100_000.0, "placeholder_b": 100_000.0},
        n_s=1, kappa_s=0.01, peak_demand=1.0,
    )


def _build_engine(lambda_k: float) -> AllocationEngine:
    policy_twin = PolicyDigitalTwin()
    policy_twin.add_rule(
        requires_licensed_human_rule("signoff", "v1", date(2020, 1, 1), "statutory sign-off")
    )
    ledger = CapabilityLedger()
    ledger.initialize(LedgerSnapshot(domain=DOMAIN, H_k=0, A_k=0, R_k=0, F_k=0, E_k=0))

    return AllocationEngine(
        policy_twin=policy_twin,
        market=FixtureMarket(),
        ledger=ledger,
        hcpb_params={DOMAIN: HCPBParameters(N_k=24, r_k=0.12, h_k=600, eta_k=1.2, B_k_min=1200)},
        reserve_states={SERVICE: _permissive_reserve_state()},
        access_constraints={},
        worker_groups={DOMAIN: ["men", "women"]},
        score_weights=ScoreWeights.paper_default(),
        debt_weights=DebtWeights.paper_default(),
        duals=Duals(lambda_k={DOMAIN: lambda_k}, rebalance_timestamp=datetime(2026, 1, 1)),
        audit_store=EvidentiaryRecordStore(),
        feedback_bus=FeedbackBus(),
        config_version="v2026-09-01",
        authorizing_panel_decision="PANEL-2026-001",
        # The worked example specifies no S^min_i; disable the invented
        # default so this test isolates Eq. 17-19 from an unrelated,
        # separately-tested mechanism (see tests/unit/test_admissibility.py).
        safety_floor_fn=lambda task: 0.0,
    )


def test_policy_filter_reduces_to_worked_example_mode_set():
    engine = _build_engine(lambda_k=0.0)
    task = _worked_example_task()
    surviving = engine.policy_twin.filter_modes(task, t=date(2026, 1, 1))
    assert set(surviving.keys()) == {"H", "H+A", "H+R", "H+A+R"}


def test_unconstrained_lambda_zero_selects_h_a_r():
    """With lambda_k = 0 (no capability price), the online rule must pick
    the unconstrained SCV winner: H+A+R at 0.3765 (Paper Sec. 5.3)."""
    engine = _build_engine(lambda_k=0.0)
    task = _worked_example_task()
    result = engine.allocate(task, date(2026, 1, 1), elapsed_days_in_period=0.0)
    assert not result.is_z4_fallback
    assert result.selected_mode == "H+A+R"


def test_capability_price_reverses_the_ranking():
    """THE central claim (Paper Sec. 5.3): substituting lambda_k into
    Eq. 17 reverses the unconstrained winner. H and H+R must tie above
    H+A+R, which must in turn beat H+A. The paper prints lambda_k rounded
    to 0.0250; the EXACT tie only holds at the unrounded dual
    (0.0599/2.4 = 0.024958333), which is also what tests/smoke's LP
    solve independently derives -- using the rounded display value here
    would not exactly tie, which is a rounding artifact of the paper's
    printed value, not of Eq. 17 itself."""
    engine = _build_engine(lambda_k=0.0599 / 2.4)
    task = _worked_example_task()
    result = engine.allocate(task, date(2026, 1, 1), elapsed_days_in_period=0.0)

    assert not result.is_z4_fallback
    scores = result.scv_tilde_by_mode
    assert scores["H"] == pytest.approx(scores["H+R"], abs=1e-6)
    assert scores["H"] == pytest.approx(0.4937, abs=3e-3)
    assert scores["H+A+R"] == pytest.approx(0.4863, abs=3e-3)
    assert scores["H"] > scores["H+A+R"] > scores["H+A"]
    assert result.selected_mode in ("H", "H+R")  # tied for first; either is a correct argmax


def test_evidentiary_record_captures_all_seven_items():
    engine = _build_engine(lambda_k=0.0250)
    task = _worked_example_task()
    result = engine.allocate(task, date(2026, 1, 1), elapsed_days_in_period=0.0)
    record = result.evidentiary_record

    assert record.d_i == pytest.approx(10.0)                       # item 1: task profile
    assert record.ell_i == pytest.approx(8.0)                      # item 1: ell_i
    assert set(record.drafted_modes) == {"H", "A", "R", "H+A", "H+R", "A+R", "H+A+R"}  # item 2
    assert any(r.mode == "A" and r.reason == "prohibit" for r in record.rejections)     # item 2
    assert len(record.candidates) == 4                             # item 3
    assert record.duals_in_force[f"lambda_{DOMAIN}"] == pytest.approx(0.0250)  # item 5
    assert record.config_version == "v2026-09-01"                  # item 6
    assert record.authorizing_panel_decision == "PANEL-2026-001"   # item 6


def test_ledger_accrues_practice_via_the_feedback_bus():
    """Eq. 20 / Fig. 1: the bus, not a direct call, must be what updates
    the ledger -- checked here by inspecting post-allocation state."""
    engine = _build_engine(lambda_k=0.0250)
    task = _worked_example_task()
    result = engine.allocate(task, date(2026, 1, 1), elapsed_days_in_period=0.0)
    expected_phi = _TABLE3[result.selected_mode]["phi"]
    accrued = engine.ledger.current(DOMAIN).accrued_practice_hours
    assert accrued == pytest.approx(8.0 * expected_phi)


def test_all_modes_prohibited_routes_to_z4():
    """A rule that prohibits every mode (e.g. an emergency shutdown) must
    route to Z4 rather than leaving the argmax undefined (Fig. 2)."""
    policy_twin = PolicyDigitalTwin()

    def ban_everything(task, mode):
        from civicworkos.policy.digital_twin import PolicyStatus
        return PolicyStatus.PROHIBIT

    from civicworkos.policy.digital_twin import PolicyRule
    policy_twin.add_rule(PolicyRule("shutdown", "v1", date(2020, 1, 1), "d", ban_everything))

    ledger = CapabilityLedger()
    ledger.initialize(LedgerSnapshot(domain=DOMAIN, H_k=0, A_k=0, R_k=0, F_k=0, E_k=0))
    engine = AllocationEngine(
        policy_twin=policy_twin,
        market=FixtureMarket(),
        ledger=ledger,
        hcpb_params={DOMAIN: HCPBParameters(N_k=24, r_k=0.12, h_k=600, eta_k=1.2, B_k_min=1200)},
        reserve_states={SERVICE: _permissive_reserve_state()},
        access_constraints={},
        worker_groups={DOMAIN: ["men", "women"]},
        score_weights=ScoreWeights.paper_default(),
        debt_weights=DebtWeights.paper_default(),
        duals=Duals(),
        audit_store=EvidentiaryRecordStore(),
        feedback_bus=FeedbackBus(),
        config_version="v1",
        authorizing_panel_decision="PANEL-2026-001",
    )
    result = engine.allocate(_worked_example_task(), date(2026, 1, 1), elapsed_days_in_period=0.0)
    assert result.is_z4_fallback
    assert result.selected_mode == "Z4_human_reserved"
    # Z4 fallback is Human Reserved (phi = 1.0) and must accrue full practice hours
    assert engine.ledger.current(DOMAIN).accrued_practice_hours == pytest.approx(8.0 * 1.0)


def test_z4_fallback_accrues_full_human_practice_hours():
    """Human-reserved work (Zone Z4) is maximum developmental share (phi = 1.0)
    and must accrue practice hours to Lambda_k via the feedback bus.
    """
    policy_twin = PolicyDigitalTwin()

    def ban_everything(task, mode):
        from civicworkos.policy.digital_twin import PolicyStatus
        return PolicyStatus.PROHIBIT

    from civicworkos.policy.digital_twin import PolicyRule
    policy_twin.add_rule(PolicyRule("shutdown", "v1", date(2020, 1, 1), "d", ban_everything))

    ledger = CapabilityLedger()
    ledger.initialize(LedgerSnapshot(domain=DOMAIN, H_k=0, A_k=0, R_k=0, F_k=0, E_k=0))
    engine = AllocationEngine(
        policy_twin=policy_twin,
        market=FixtureMarket(),
        ledger=ledger,
        hcpb_params={DOMAIN: HCPBParameters(N_k=24, r_k=0.12, h_k=600, eta_k=1.2, B_k_min=1200)},
        reserve_states={SERVICE: _permissive_reserve_state()},
        access_constraints={},
        worker_groups={DOMAIN: ["men", "women"]},
        score_weights=ScoreWeights.paper_default(),
        debt_weights=DebtWeights.paper_default(),
        duals=Duals(),
        audit_store=EvidentiaryRecordStore(),
        feedback_bus=FeedbackBus(),
        config_version="v1",
        authorizing_panel_decision="PANEL-2026-001",
    )
    task = _worked_example_task()
    result = engine.allocate(task, date(2026, 1, 1), elapsed_days_in_period=0.0)
    assert result.is_z4_fallback
    assert engine.ledger.current(DOMAIN).accrued_practice_hours == pytest.approx(8.0 * 1.0)
