"""Stress-scenario injectors: Paper sec:protocol, Suppl. Table S2.

Reads configs/scenarios/stress_scenarios.yaml (the paper's own protocol
specification, reproduced as data) and provides one small, real,
independently-testable transform function per scenario KIND. These are
parameter perturbations applied to this repository's own state objects
(ReserveState, HCPBParameters, a PolicyDigitalTwin, an arrival count) --
they are NOT a claim that the paper's full stress-test protocol (which
also requires the six-sector, ten-year simulation testbed this repo does
not build -- see sim.des) has been executed. civicworkos.constraints
verification against the perturbed state is left to the caller (e.g.
tests/integration or a notebook), matching the reduced scope declared in
docs/assumptions.md A10.

Scenario -> function mapping:
  i   ai_service_outage            -> remove_capacity(channel="ai")
  ii  cyberattack_on_fleet_c2      -> remove_capacity(channel="robot")
  iii robot_fleet_mechanical_failure -> remove_capacity(channel="robot", partial)
  iv  emergency_demand_surge       -> scale_arrivals()
  v   retirement_wave              -> retirement_wave()
  vi  rapid_ai_capability_improvement -> uplift_quality_trust()
  vii new_municipal_regulation     -> PolicyDigitalTwin.add_rule() directly
      (already live-mutable without redeploying the market -- see
      civicworkos.policy.digital_twin; no separate wrapper needed here,
      which is itself the point the scenario tests).
"""

from __future__ import annotations

from dataclasses import replace
from pathlib import Path

import yaml

from civicworkos.constraints.hcpb import HCPBParameters
from civicworkos.constraints.resilience import ReserveState

_DEFAULT_SCENARIOS_PATH = (
    Path(__file__).resolve().parents[2] / "configs" / "scenarios" / "stress_scenarios.yaml"
)


def load_scenarios(path: Path | str = _DEFAULT_SCENARIOS_PATH) -> list[dict]:
    with open(path, encoding="utf-8") as f:
        data = yaml.safe_load(f)
    return data["scenarios"]


def remove_capacity(state: ReserveState, fraction: float, component_ids: list[str] | None = None) -> ReserveState:
    """Scenarios i/ii/iii: remove `fraction` of capacity from the named
    components (or all components if none named), for the duration of
    the injection. Returns a NEW ReserveState; the caller re-checks
    eq:res3r against it and measures recovery time by how long it takes
    capacity to be restored in subsequent state updates.
    """
    if not 0.0 <= fraction <= 1.0:
        raise ValueError(f"fraction must lie in [0,1], got {fraction!r}")
    targets = component_ids or list(state.component_capacities.keys())
    new_caps = dict(state.component_capacities)
    for c in targets:
        if c in new_caps:
            new_caps[c] = new_caps[c] * (1.0 - fraction)
    return replace(state, component_capacities=new_caps)


def retirement_wave(params: HCPBParameters, r_k_override: float) -> HCPBParameters:
    """Scenario v: r_k raised to `r_k_override` (paper: 0.25) for the
    scenario's duration. Paper sec:protocol: "raises r_k, hence B_k through
    (9), hence lambda_k, pushing allocation toward human-inclusive modes
    at exactly the moment fewer humans are available." Whether that
    feedback is stabilizing or oscillatory is P7 -- this function only
    performs the parameter change; oscillation must be checked by
    running the online rule across successive periods and tracking
    lambda_k, which this repository does not automate into a single
    call (see docs/assumptions.md A10).
    """
    return replace(params, r_k=r_k_override)


def scale_arrivals(base_task_count: int, multiplier: float) -> int:
    """Scenario iv: arrival rate x`multiplier` for the injection window."""
    if multiplier <= 0:
        raise ValueError(f"multiplier must be positive, got {multiplier!r}")
    return round(base_task_count * multiplier)


def uplift_quality_trust(value: float, uplift_fraction: float) -> float:
    """Scenario vi: raise a [0,1] quality or trust estimate by
    `uplift_fraction` (paper: 0.20 over 3 years), clipped to 1.0.
    Applied per-call to whatever Q/Tr value the market produced, rather
    than mutating HeuristicMarket's fixed archetypes in place.
    """
    return min(1.0, value * (1.0 + uplift_fraction))
