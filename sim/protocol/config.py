"""Parameters of the reference evaluation (synthetic municipal testbed).

Every value here is an illustrative modeling choice, not a calibrated
estimate of any city. The article's protocol section tabulates them; the
run script writes the resolved configuration next to its outputs so that a
reported number can always be traced to the parameters that produced it.
"""

from __future__ import annotations

from dataclasses import asdict, dataclass, field


@dataclass(frozen=True)
class ModeSpec:
    """An execution mode available in a domain."""

    name: str
    phi: float              # human developmental share phi_m
    machine: bool           # whether an AI agent or robot participates
    duration_mult: float    # clock-time multiplier relative to the domain's base duration
    machine_bonus: float    # known reliability offset of the machine component in this mode
    demand: float           # human workload demand factor per clock hour


@dataclass(frozen=True)
class DomainSpec:
    """One municipal service domain of the synthetic testbed."""

    key: str
    label: str
    machine_kind: str               # "robot" or "AI agent"
    arrivals_per_day: float
    duration_h: float
    learn: float
    risk: float
    crit: float
    consequential_share: float      # share of tasks with high legal or rights consequence
    requirement: float              # true mean task requirement b_k
    requirement_sd: float
    requirement_prior_bias: float   # commissioning estimate minus truth
    deadline_days: int
    takeover_budget_min: float      # task-specific safe takeover time budget
    n_certified: int
    n_trainee_posts: int
    h_k: float                      # credited practice hours to certification
    machine_units: int
    machine_reliability: float
    machine_cost_per_h: float
    attrition_per_year: float
    modes: tuple[ModeSpec, ...]
    static_mode: str                # fixed allocation-table entry


INSPECTION = DomainSpec(
    key="INS", label="Structural inspection", machine_kind="robot",
    arrivals_per_day=6.0, duration_h=4.0, learn=0.80, risk=0.70, crit=0.90,
    consequential_share=1.0, requirement=0.62, requirement_sd=0.04, requirement_prior_bias=-0.04,
    deadline_days=5, takeover_budget_min=15.0,
    n_certified=10, n_trainee_posts=4, h_k=600.0,
    machine_units=4, machine_reliability=0.86, machine_cost_per_h=0.50, attrition_per_year=0.12,
    modes=(
        ModeSpec("H", 1.00, False, 1.20, 0.00, 0.85),
        ModeSpec("H+R", 0.70, True, 1.00, 0.00, 0.70),
        ModeSpec("H+A+R", 0.55, True, 0.80, 0.05, 0.60),
    ),
    static_mode="H+A+R",
)

SANITATION = DomainSpec(
    key="SAN", label="Street maintenance and sanitation", machine_kind="robot",
    arrivals_per_day=20.0, duration_h=2.0, learn=0.50, risk=0.50, crit=0.60,
    consequential_share=0.10, requirement=0.55, requirement_sd=0.05, requirement_prior_bias=-0.04,
    deadline_days=1, takeover_budget_min=20.0,
    n_certified=12, n_trainee_posts=4, h_k=500.0,
    machine_units=7, machine_reliability=0.82, machine_cost_per_h=0.30, attrition_per_year=0.12,
    modes=(
        ModeSpec("H", 1.00, False, 1.00, 0.00, 1.00),
        ModeSpec("H+R", 0.60, True, 1.00, 0.00, 0.70),
        ModeSpec("R", 0.00, True, 1.00, 0.00, 0.00),
    ),
    static_mode="R",
)

CASEWORK = DomainSpec(
    key="CAS", label="Citizen-service casework", machine_kind="AI agent",
    arrivals_per_day=40.0, duration_h=1.0, learn=0.60, risk=0.30, crit=0.70,
    consequential_share=0.30, requirement=0.58, requirement_sd=0.05, requirement_prior_bias=-0.04,
    deadline_days=2, takeover_budget_min=45.0,
    n_certified=10, n_trainee_posts=4, h_k=400.0,
    machine_units=12, machine_reliability=0.88, machine_cost_per_h=0.08, attrition_per_year=0.12,
    modes=(
        ModeSpec("H", 1.00, False, 1.00, 0.00, 1.00),
        ModeSpec("H+A", 0.60, True, 1.00, 0.00, 0.70),
        ModeSpec("A", 0.00, True, 1.00, 0.00, 0.00),
    ),
    static_mode="A",
)

DOMAINS: tuple[DomainSpec, ...] = (INSPECTION, SANITATION, CASEWORK)


@dataclass(frozen=True)
class SimParams:
    """World, learning and decision parameters shared by every domain."""

    days: int = 750                       # three years of 250 working days
    days_per_year: int = 250
    avail_h: float = 4.5                  # daily hours each practitioner gives this task stream
    overtime_factor: float = 1.3          # hours cap as a multiple of avail_h
    machine_h_per_unit: float = 7.5
    gamma: float = 8.0                    # logistic slope of the outcome model
    theta_0: float = 0.30                 # proficiency at zero credited practice
    theta_comp: float = 0.70              # competence level
    residual: float = 0.45                # forgetting floor of a certified practitioner
    tau_ret: float = 120.0                # nominal retention time constant (working days)
    tau_ret_cv: float = 0.30              # person-level heterogeneity of tau
    rate_cv: float = 0.25                 # person-level heterogeneity of learning rate
    load_sd: float = 0.15                 # person-level heterogeneity of workload demand
    human_led_share: float = 0.30         # phi_m * omega at or above this is a human-led task
    omega_trainee: float = 0.5            # trainee's work share on a supervised roster
    workload_ceiling: float = 1.0         # true workload index above this is overload
    workload_margin: float = 0.95         # CivicWorkOS plans to this share of the ceiling
    # automation dynamics
    machine_drift_sd: float = 0.004
    machine_reversion: float = 0.95
    fault_rate: float = 0.02
    # takeover model (minutes)
    t_detect: float = 2.0
    t_reach: float = 3.0
    t_sa: float = 8.0
    ootl_days: int = 5
    ootl_factor: float = 0.6
    overload_sa_factor: float = 1.5
    # economics
    value: float = 10.0
    wage_certified: float = 1.0
    wage_trainee: float = 0.6
    incident_cost: float = 30.0
    p_incident_failure: float = 0.15
    p_incident_takeover_failure: float = 0.50
    p_incident_mrc: float = 0.03
    # adaptive learning
    prior_offset_var: float = 0.0025
    human_process_var: float = 1e-4
    machine_prior_var: float = 0.0025
    machine_process_var: float = 2e-4
    requirement_prior_var: float = 0.0025
    probe_prob: float = 0.30              # chance a skill probe accompanies a human-involved task
    probe_sd: float = 0.08
    telemetry_prob: float = 0.50          # chance of a fleet health reading on a given day
    telemetry_sd: float = 0.10
    workload_sensor_prob: float = 0.70
    workload_sensor_sd: float = 0.10
    # CivicWorkOS decision rules
    eta: float = 1.2
    oversight_consequence: float = 0.6    # crit*auth-type threshold for human oversight
    oversight_p_sd: float = 0.06          # predictive-success uncertainty routed to oversight
    readiness_z: float = 1.28             # lower-bound multiplier in the readiness test
    retention_guard: float = 0.5          # a practitioner is due at this share of Delta_max
    takeover_headroom: float = 1.10       # estimated workload ceiling admitted for a takeover


@dataclass(frozen=True)
class Scenario:
    name: str
    surge_start: int = -1
    surge_days: int = 0
    surge_factor: float = 1.0
    disruption_start: int = -1
    disruption_days: int = 0
    disruption_reliability: float = 0.45
    disruption_fault_rate: float = 0.25
    disruption_capacity: float = 0.5

    def window(self) -> tuple[int, int] | None:
        if self.surge_start >= 0:
            return self.surge_start, self.surge_start + self.surge_days
        if self.disruption_start >= 0:
            return self.disruption_start, self.disruption_start + self.disruption_days
        return None


SCENARIOS: dict[str, Scenario] = {
    "routine": Scenario("routine"),
    "surge": Scenario("surge", surge_start=400, surge_days=30, surge_factor=2.0),
    "disruption": Scenario("disruption", disruption_start=500, disruption_days=20),
}

POLICIES: tuple[str, ...] = (
    "static",
    "efficiency",
    "civicworkos",
    "civicworkos_nolearn",
    "civicworkos_noretention",
)


@dataclass(frozen=True)
class PolicyFlags:
    learning: bool
    capability_terms: bool
    retention: bool
    workload_guard: bool
    oversight: bool
    readiness_takeover: bool


POLICY_FLAGS: dict[str, PolicyFlags] = {
    "static": PolicyFlags(False, False, False, False, False, False),
    "efficiency": PolicyFlags(True, False, False, False, False, False),
    "civicworkos": PolicyFlags(True, True, True, True, True, True),
    "civicworkos_nolearn": PolicyFlags(False, True, True, True, True, True),
    "civicworkos_noretention": PolicyFlags(True, True, False, True, True, True),
}


@dataclass
class RunConfig:
    params: SimParams = field(default_factory=SimParams)
    domains: tuple[DomainSpec, ...] = DOMAINS

    def as_dict(self) -> dict:
        return {"params": asdict(self.params), "domains": [asdict(d) for d in self.domains],
                "scenarios": {k: asdict(v) for k, v in SCENARIOS.items()},
                "policies": {k: asdict(v) for k, v in POLICY_FLAGS.items()}}
