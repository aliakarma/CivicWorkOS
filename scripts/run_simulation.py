#!/usr/bin/env python
"""Run the reduced-scope simulation testbed (sim.des) over synthetic
demo tasks for all five baseline strategies (Paper sec:protocol) and print
the subset of metrics it computes (Paper sec:protocol -- see sim/des/engine.py
for exactly which of the thirteen are implemented here).

THIS IS NOT THE PAPER'S EVALUATION STUDY. It runs on synthetic,
uncalibrated demo data over a short horizon, not the six-sector,
ten-year, seed-replicated protocol of Paper sec:protocol / Suppl. S2-S4.
See docs/reproducibility.md for what this script does and does not
demonstrate.

Usage:
    python scripts/run_simulation.py [n_tasks] [seed] [--seeds N]
"""

from __future__ import annotations

import argparse
import math
import sys
from collections import defaultdict
from datetime import date
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "src"))
sys.path.insert(0, str(ROOT))

from civicworkos.config.loader import load_domain_config
from civicworkos.constraints.hcpb import HCPBParameters, capability_budget
from civicworkos.constraints.resilience import ReserveState
from civicworkos.market.agents import HeuristicMarket
from civicworkos.policy.digital_twin import PolicyDigitalTwin, requires_licensed_human_rule
from sim.calibration.sources import synthetic_demo_tasks
from sim.des.engine import SimulationMetrics, run_strategy
from sim.strategies.baselines import StrategyName

DOMAIN = "structural_inspection"
SERVICE = "structural_inspection_service"
ALL_STRATEGIES: tuple[StrategyName, ...] = (
    "automation_first",
    "cost_performance",
    "human_first",
    "capability_matching",
    "civicworkos",
)


def _mean_std(values: list[float]) -> tuple[float, float]:
    n = len(values)
    if n == 0:
        return 0.0, 0.0
    mean = sum(values) / n
    variance = sum((x - mean) ** 2 for x in values) / n if n > 1 else 0.0
    return mean, math.sqrt(variance)


def main() -> int:
    parser = argparse.ArgumentParser(description="Run CivicWorkOS multi-strategy simulation.")
    parser.add_argument("n_tasks", nargs="?", type=int, default=200, help="Number of tasks (default: 200)")
    parser.add_argument("seed", nargs="?", type=int, default=42, help="Initial random seed (default: 42)")
    parser.add_argument("--seeds", type=int, default=1, help="Number of random seeds to evaluate over (default: 1)")
    args = parser.parse_args()

    n_tasks: int = args.n_tasks
    initial_seed: int = args.seed
    num_seeds: int = max(1, args.seeds)

    print("=" * 70)
    print("SYNTHETIC DEMO DATA -- not calibrated to any real source.")
    print("See sim/calibration/sources.py and docs/reproducibility.md.")
    if num_seeds > 1:
        print(f"MULTI-SEED EVALUATION: {num_seeds} seeds ({initial_seed} .. {initial_seed + num_seeds - 1})")
    print("=" * 70)

    domain_cfg = load_domain_config(ROOT / "configs" / "domains" / "structural_inspection.yaml")
    hcpb_params = HCPBParameters(
        N_k=domain_cfg.N_k, r_k=domain_cfg.r_k, h_k=domain_cfg.h_k,
        eta_k=domain_cfg.eta_k, B_k_min=domain_cfg.B_k_min,
    )
    budget_hours = capability_budget(hcpb_params)

    policy_twin = PolicyDigitalTwin()
    policy_twin.add_rule(
        requires_licensed_human_rule("signoff", "v1", date(2020, 1, 1), "statutory sign-off requirement")
    )
    market = HeuristicMarket(hybrid_phi={DOMAIN: domain_cfg.hybrid_phi})
    reserve_states = {
        SERVICE: ReserveState(
            component_capacities={"ai_inspection_pool": 40.0, "drone_fleet_class_a": 25.0,
                                   "contracted_ndt_vendor": 15.0},
            n_s=1, kappa_s=0.6, peak_demand=50.0,
        )
    }

    # Collect runs across seeds
    collected_metrics: dict[StrategyName, list[SimulationMetrics]] = defaultdict(list)
    collected_cfi: dict[StrategyName, list[float]] = defaultdict(list)
    mode_counts_total: dict[StrategyName, dict[str, int]] = defaultdict(lambda: defaultdict(int))

    for s_idx in range(num_seeds):
        current_seed = initial_seed + s_idx
        tasks = synthetic_demo_tasks(n_tasks, DOMAIN, SERVICE, seed=current_seed)
        for strategy in ALL_STRATEGIES:
            m = run_strategy(
                strategy, tasks,
                policy_twin=policy_twin, market=market, hcpb_params=hcpb_params,
                reserve_states=reserve_states, access_constraints={},
                worker_groups={DOMAIN: domain_cfg.groups},
            )
            collected_metrics[strategy].append(m)
            collected_cfi[strategy].append(m.capability_formation_index(budget_hours))
            for mode, count in m.mode_counts.items():
                mode_counts_total[strategy][mode] += count

    if num_seeds == 1:
        print(
            f"\n{'Strategy':<22}{'Prod. idx':>12}{'Cost idx':>12}"
            f"{'Accum. CAD':>12}{'Cap.Form.Idx':>14}{'Z4 rate':>10}"
        )
        for strategy in ALL_STRATEGIES:
            m = collected_metrics[strategy][0]
            cfi = collected_cfi[strategy][0]
            print(
                f"{strategy:<22}{m.productivity_index:>12.2f}{m.operating_cost_index:>12.2f}"
                f"{m.accumulated_cad:>12.2f}{cfi:>14.4f}{m.z4_routing_rate:>10.3f}"
            )
        print("\nMode Selection Breakdown by Strategy:")
        for strategy in ALL_STRATEGIES:
            m = collected_metrics[strategy][0]
            modes_str = ", ".join(f"{k}: {v}" for k, v in sorted(m.mode_counts.items()))
            print(f"  {strategy:<22} -> {modes_str}")
    else:
        print(
            f"\n{'Strategy':<22}{'Prod. idx (mean+/-sd)':>22}{'Cost idx (mean+/-sd)':>22}"
            f"{'Accum. CAD (mean+/-sd)':>22}{'Cap.Form.Idx (mean+/-sd)':>24}{'Z4 rate (mean+/-sd)':>20}"
        )
        for strategy in ALL_STRATEGIES:
            ms = collected_metrics[strategy]
            cfis = collected_cfi[strategy]
            p_mean, p_sd = _mean_std([m.productivity_index for m in ms])
            c_mean, c_sd = _mean_std([m.operating_cost_index for m in ms])
            cad_mean, cad_sd = _mean_std([m.accumulated_cad for m in ms])
            cfi_mean, cfi_sd = _mean_std(cfis)
            z4_mean, z4_sd = _mean_std([m.z4_routing_rate for m in ms])

            p_str = f"{p_mean:.2f} +/- {p_sd:.2f}"
            c_str = f"{c_mean:.2f} +/- {c_sd:.2f}"
            cad_str = f"{cad_mean:.2f} +/- {cad_sd:.2f}"
            cfi_str = f"{cfi_mean:.4f} +/- {cfi_sd:.4f}"
            z4_str = f"{z4_mean:.3f} +/- {z4_sd:.3f}"

            print(f"{strategy:<22}{p_str:>22}{c_str:>22}{cad_str:>22}{cfi_str:>24}{z4_str:>20}")

        print("\nTotal Mode Selection Distribution Across All Seeds:")
        for strategy in ALL_STRATEGIES:
            modes_str = ", ".join(f"{k}: {v}" for k, v in sorted(mode_counts_total[strategy].items()))
            print(f"  {strategy:<22} -> {modes_str}")

    print(
        "\nNotes:"
        "\n  - Productivity and Operating Cost indices are normalized per allocated task (excluding Z4 fallbacks)."
        "\n  - CivicWorkOS runs with active dual shadow price lambda_k=0.0454 (eq:aug)."
        "\n  - Accumulated CAD represents raw sums over synthetic tasks for relative comparison."
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
