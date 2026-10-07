#!/usr/bin/env python
"""Run Algorithm 1 (civicworkos.online.AllocationEngine) on one task.

This is the "inference" entry point for CivicWorkOS: given a task and a
governance configuration, decide the execution mode. It uses the
[INVENTED] HeuristicMarket (civicworkos.market.agents) as the estimator
backend by default -- see that module's docstring for what it is and is
not. For the paper-traceable worked example, use
scripts/verify_worked_example.py instead, which uses the literal tab:worked-terms
values rather than this heuristic estimator.

Usage:
    python scripts/run_allocation.py
"""

from __future__ import annotations

import json
import sys
from datetime import date, datetime, timezone
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "src"))

from civicworkos.audit.evidentiary_record import EvidentiaryRecordStore
from civicworkos.config.loader import load_domain_config, load_weights_config
from civicworkos.constraints.hcpb import HCPBParameters
from civicworkos.constraints.resilience import ReserveState
from civicworkos.feedback.bus import FeedbackBus
from civicworkos.ledger.capability_ledger import CapabilityLedger, LedgerSnapshot
from civicworkos.market.agents import HeuristicMarket
from civicworkos.online.algorithm1 import AllocationEngine, Duals
from civicworkos.policy.digital_twin import PolicyDigitalTwin, requires_licensed_human_rule
from civicworkos.scoring.cad import DebtWeights
from civicworkos.scoring.scv import ScoreWeights
from civicworkos.twin.task import TaskProfile


def main() -> int:
    weights = load_weights_config(ROOT / "configs" / "weights" / "default.yaml")
    domain_cfg = load_domain_config(ROOT / "configs" / "domains" / "structural_inspection.yaml")

    score_weights = ScoreWeights(
        w1_quality=weights.w1_quality, w2_safety=weights.w2_safety, w3_productivity=weights.w3_productivity,
        w4_equity=weights.w4_equity, w5_trust=weights.w5_trust, w6_cost=weights.w6_cost,
        w7_energy=weights.w7_energy, w8_privacy=weights.w8_privacy, w9_cad=weights.w9_cad,
    )
    debt_weights = DebtWeights(
        alpha=weights.alpha_skill, beta=weights.beta_fallback, gamma=weights.gamma_accountability,
        delta=weights.delta_dependency, epsilon=weights.epsilon_transition,
    )

    policy_twin = PolicyDigitalTwin()
    policy_twin.add_rule(
        requires_licensed_human_rule("signoff", "v1", date(2020, 1, 1), "statutory sign-off requirement")
    )

    domain = domain_cfg.domain
    service = "structural_inspection_service"
    ledger = CapabilityLedger()
    ledger.initialize(LedgerSnapshot(domain=domain, H_k=0, A_k=0, R_k=0, F_k=0, E_k=0))

    reserve_state = ReserveState(
        component_capacities={"ai_inspection_pool": 40.0, "drone_fleet_class_a": 25.0,
                               "contracted_ndt_vendor": 15.0},
        n_s=1, kappa_s=0.6, peak_demand=50.0,
    )

    engine = AllocationEngine(
        policy_twin=policy_twin,
        market=HeuristicMarket(hybrid_phi={domain: domain_cfg.hybrid_phi}),
        ledger=ledger,
        hcpb_params={domain: HCPBParameters(
            N_k=domain_cfg.N_k, r_k=domain_cfg.r_k, h_k=domain_cfg.h_k,
            eta_k=domain_cfg.eta_k, B_k_min=domain_cfg.B_k_min,
        )},
        reserve_states={service: reserve_state},
        access_constraints={},
        worker_groups={domain: domain_cfg.groups},
        score_weights=score_weights,
        debt_weights=debt_weights,
        duals=Duals(lambda_k={domain: 0.045353}, rebalance_timestamp=datetime.now(timezone.utc)),
        audit_store=EvidentiaryRecordStore(),
        feedback_bus=FeedbackBus(),
        config_version=weights.version,
        authorizing_panel_decision="DEMO-PANEL-DECISION-001",
    )

    # A moderate-risk demo task (deliberately NOT the worked example's
    # high-risk/high-criticality profile, which was calibrated against
    # the paper's literal tab:worked-terms estimates -- see
    # scripts/verify_worked_example.py). Combined with the invented
    # HeuristicMarket and default_safety_floor(), a high-risk task here
    # can legitimately route every mode below the safety floor and fall
    # back to Z4; that is the framework doing what fig:workflow says it should
    # ("either filtering stage may empty the candidate set"), not a bug.
    task = TaskProfile(
        task_id="demo-task-1", service=service, domain=domain,
        cog=0.55, phy=0.40, emp=0.20, risk=0.30, auth=0.60, priv=0.20, urg=0.40,
        learn=0.60, crit=0.40, duration_hours=6.0,
    )

    result = engine.allocate(task, date.today(), elapsed_days_in_period=180.0)

    print(f"Selected mode: {result.selected_mode}")
    print(f"Z4 fallback: {result.is_z4_fallback}")
    print("Augmented scores (SCV~) by admissible mode:")
    print(json.dumps(result.scv_tilde_by_mode, indent=2))
    print(f"Evidentiary record hash: {result.record_hash}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
