"""Integration test: Algorithm 1 (civicworkos.online.AllocationEngine) wired end
to end -- policy twin, ledger, market, HCPB, resilience, duals, audit store,
feedback bus -- against the worked example's own tab:worked-terms inputs.

Unlike tests/smoke/test_worked_example.py, which checks the bare eq:cad / eq:scv
/ eq:cadmodel arithmetic and the batch LP, this test exercises the full
Algorithm 1 control flow: per-mode policy filtering, the market protocol, the
admissibility test (eq:admis), and the Lagrangian augmentation (eq:aug) with an
ALREADY-SOLVED dual supplied as input -- which is exactly how the online rule is
meant to consume a rebalance's output.

The mode set is the eight **staffed** modes of tab:worked-terms, not the seven
execution modes: eq:aug prices the credited share phi_m * psi_a, so a career
stage has to be present in the decision for the capability price to do anything
at all. Every value comes from `manuscript_values`. This file previously built
its own four-execution-mode table at an earlier draft's parameters and asserted
a lambda_k of 0.0250 against a manuscript that prices practice at 0.0454
(finding N2, revision programme Phase 3).

One divergence is worth naming because this test makes it visible. eq:aug prices
`ell_i * phi_m * psi_a`, while `civicworkos.online.algorithm1` multiplies by a
single `phi_m` field. The field therefore carries the credited share, and this
test supplies it that way -- see docs/assumptions.md.

The worked example specifies no safety floor S^min_i and no 3R Reserve
instantiation for this domain, so this test supplies a permissive floor and an
oversized reserve baseline to isolate the capability-budget mechanism, documented
inline where set.
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
from manuscript_values import MODES, WORKED

DOMAIN = "structural_inspection"
SERVICE = "structural_inspection_service"

# The eight staffed modes of tab:worked-terms, imported rather than restated.
STAFFED_MODES = tuple(MODES)
ELL_I = WORKED["ell_i"]

# eq:lambdaworked. Supplied as an input, as a rebalance would publish it.
LAMBDA_K = 0.045353



class FixtureMarket(MarketProtocol):
    """Returns the worked example's own literal tab:worked-terms values -- NOT the
    invented HeuristicMarket -- so this test checks Algorithm 1's
    orchestration logic against a paper-traceable fixture, not against
    this repository's own estimator heuristics.
    """

    def query(self, task, mode, policy_status, ledger, t=None) -> AgentEstimate:
        m = MODES[mode]
        terms = TermVector(Q=m.Q, S=m.S, P=m.P, Eq_srv=m.Eq, Tr=m.Tr,
                           Cost=m.Cost, En=m.En, Pr=m.Pr)
        debts = DebtComponents(D_skill=m.D_skill, D_fall=m.D_fall, D_acct=m.D_acct,
                               D_dep=m.D_dep, D_trans=m.D_trans)
        # The CREDITED share phi_m * psi_a, not a bare phi_m: see the module
        # docstring on the eq:aug divergence.
        return AgentEstimate(terms=terms, debts=debts, phi_m=m.credited)


def _hcpb_params() -> HCPBParameters:
    """eq:hcpb-estimator at the manuscript's stated inputs (B_k = 4,976.64 h)."""
    w = WORKED
    return HCPBParameters(
        N_k=w["N_k"], r_k=w["r_k"], h_k=w["h_k"], eta_k=w["eta_k"], B_k_min=w["B_min"]
    )


def _worked_example_task() -> TaskProfile:
    return TaskProfile(
        task_id="bridge-1", service=SERVICE, domain=DOMAIN,
        cog=0.80, phy=0.60, emp=0.10, risk=0.70, auth=0.90, priv=0.20, urg=0.40,
        learn=0.80, crit=0.90, duration_hours=10.0,
    )


def _permissive_reserve_state() -> ReserveState:
    # The worked example does not instantiate the 3R Reserve for this
    # domain at all. TWO oversized components (so N-1 still leaves a huge
    # remainder) with a tiny rho_s ensure eq:admis's resilience clause never
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
        hcpb_params={DOMAIN: _hcpb_params()},
        modes=STAFFED_MODES,
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
        # default so this test isolates eq:aug, eq:admis and eq:argmax from an unrelated,
        # separately-tested mechanism (see tests/unit/test_admissibility.py).
        safety_floor_fn=lambda task: 0.0,
    )


def test_policy_filter_reduces_to_worked_example_mode_set():
    """The statutory sign-off rule prohibits every mode lacking a licensed
    human, reducing the seven execution modes to four."""
    engine = _build_engine(lambda_k=0.0)
    task = _worked_example_task()
    surviving = engine.policy_twin.filter_modes(task, t=date(2026, 1, 1))
    assert set(surviving.keys()) == {"H", "H+A", "H+R", "H+A+R"}


def test_policy_filter_admits_every_staffed_mode():
    """All eight staffed modes carry a licensed human, so the sign-off rule
    removes none of them. The guard reads the mode family and ignores the roster
    suffix -- splitting the raw string would wrongly prohibit "H/a1", the one
    staffed mode that is entirely human."""
    engine = _build_engine(lambda_k=0.0)
    task = _worked_example_task()
    surviving = engine.policy_twin.filter_modes(
        task, STAFFED_MODES, t=date(2026, 1, 1)
    )
    assert set(surviving.keys()) == set(STAFFED_MODES)


def test_unconstrained_lambda_zero_selects_the_scv_winner():
    """With lambda_k = 0 there is no capability price, so the online rule picks
    the unconstrained SCV winner: H+A+R/a0 at 0.34261 -- the staffed mode that
    credits no developmental practice at all."""
    engine = _build_engine(lambda_k=0.0)
    task = _worked_example_task()
    result = engine.allocate(task, date(2026, 1, 1), elapsed_days_in_period=0.0)
    assert not result.is_z4_fallback
    assert result.selected_mode == WORKED["mode_unc"] == "H+A+R/a0"
    assert result.scv_tilde_by_mode[result.selected_mode] == pytest.approx(
        0.342612, abs=1e-5
    )


def test_capability_price_reverses_the_ranking():
    """THE central claim: substituting lambda_k into eq:aug reverses the
    unconstrained winner.

    At the capability price, the two developing-roster modes of tab:worked-mix
    tie at 0.435229 and both beat H+A+R/a0, which won on raw SCV. The tie is
    exact by construction, because lambda_k is *defined* as the price at which
    the two become indifferent (eq:lambdaworked) -- so the equality is a
    property of eq:aug, not a numerical coincidence.
    """
    engine = _build_engine(lambda_k=LAMBDA_K)
    task = _worked_example_task()
    result = engine.allocate(task, date(2026, 1, 1), elapsed_days_in_period=0.0)

    assert not result.is_z4_fallback
    scores = result.scv_tilde_by_mode
    lo, hi, unc = WORKED["mode_lo"], WORKED["mode_hi"], WORKED["mode_unc"]

    assert scores[lo] == pytest.approx(0.435229, abs=1e-5)
    assert scores[hi] == pytest.approx(0.435229, abs=1e-5)
    assert scores[lo] == pytest.approx(scores[hi], abs=1e-5)
    assert scores[unc] == pytest.approx(0.342612, abs=1e-5)

    # The reversal: both active modes now outrank the raw-SCV winner.
    assert scores[lo] > scores[unc]
    assert scores[hi] > scores[unc]
    assert result.selected_mode in (lo, hi)

    # Every mode that credits no practice is unmoved by the price.
    for name, m in MODES.items():
        if m.credited == 0.0:
            assert scores[name] == pytest.approx(m.scv, abs=1e-9)


def test_evidentiary_record_captures_all_seven_items():
    engine = _build_engine(lambda_k=LAMBDA_K)
    task = _worked_example_task()
    result = engine.allocate(task, date(2026, 1, 1), elapsed_days_in_period=0.0)
    record = result.evidentiary_record

    assert record.d_i == pytest.approx(10.0)                       # item 1: task profile
    assert record.ell_i == pytest.approx(8.0)                      # item 1: ell_i
    assert set(record.drafted_modes) == set(STAFFED_MODES)          # item 2
    # Every staffed mode here carries a licensed human, so the sign-off rule
    # rejects none of them; the prohibition path is covered by
    # test_policy_filter_reduces_to_worked_example_mode_set and by
    # test_all_modes_prohibited_routes_to_z4.
    assert all(r.reason != "prohibit" for r in record.rejections)    # item 2
    assert len(record.candidates) == len(STAFFED_MODES)             # item 3
    assert record.duals_in_force[f"lambda_{DOMAIN}"] == pytest.approx(LAMBDA_K)  # item 5
    assert record.config_version == "v2026-09-01"                  # item 6
    assert record.authorizing_panel_decision == "PANEL-2026-001"   # item 6


def test_ledger_accrues_practice_via_the_feedback_bus():
    """eq:feedback / fig:architecture: the bus, not a direct call, must be what updates
    the ledger -- checked here by inspecting post-allocation state."""
    engine = _build_engine(lambda_k=LAMBDA_K)
    task = _worked_example_task()
    result = engine.allocate(task, date(2026, 1, 1), elapsed_days_in_period=0.0)
    expected_credited = MODES[result.selected_mode].credited
    accrued = engine.ledger.current(DOMAIN).accrued_practice_hours
    assert accrued == pytest.approx(ELL_I * expected_credited)


def test_all_modes_prohibited_routes_to_z4():
    """A rule that prohibits every mode (e.g. an emergency shutdown) must
    route to Z4 rather than leaving the argmax undefined (fig:workflow)."""
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
        hcpb_params={DOMAIN: _hcpb_params()},
        modes=STAFFED_MODES,
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
        hcpb_params={DOMAIN: _hcpb_params()},
        modes=STAFFED_MODES,
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
