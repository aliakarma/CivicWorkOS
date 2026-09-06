"""Reversibility and Resilience (3R) Reserve: Paper Sec. 3.7, Eq. 13-14.

    Res^(n)_s(t) = C_s(t) - sum_{c in C^(n)_s(t)} C_{s,c}(t)     (Eq. 13)

    Res^(n_s)_s(t) >= rho_s ,  rho_s = kappa_s * D_peak_s         (Eq. 14)

The N-1/N-2 criterion from reliability engineering, applied to a
workforce of humans, AI agents, and robots. The paper is explicit that
this is "not a novel invention but an adaptation of a decades-old
reliability paradigm" and corrects a common error: the threshold is
against PEAK DEMAND, not against the lost component's own capacity.

Eq. 13-14 are stated at FLEET granularity (components C_{s,c}). Eq. 17
and Eq. 18 need Delta^res_s(m), the change in surviving capacity
attributable to a SINGLE task's mode -- a mapping the paper never
defines (report Sec. 20.8 / H2). `task_delta_resilience` below is this
repository's own invented attribution, clearly separated from Eq. 13-14
themselves, which are exact.
"""

from __future__ import annotations

from dataclasses import dataclass

# [REC/invented] Approximate automation-dependence of each mode, used only
# by task_delta_resilience(). Not present in the paper. A mode that leans
# on automated capacity components (A, R) is treated as consuming reserve;
# a mode that leans on humans (H) is treated as contributing to it.
_AUTOMATION_DEPENDENCE = {
    "H": 0.0,
    "A": 1.0,
    "R": 1.0,
    "H+A": 0.5,
    "H+R": 0.5,
    "A+R": 1.0,
    "H+A+R": 2.0 / 3.0,
}


@dataclass(frozen=True)
class ReserveState:
    """Fleet-scale inputs to Eq. 13-14 for one critical service s.

    component_capacities: {component_id: C_{s,c}(t)} -- the automation-
        dependent capacity components serving s (an AI-agent pool, a
        robot-fleet class, a vendor platform).
    n_s: contingency order, 1 or 2.
    kappa_s: policy-set share of peak demand that must remain servable, in (0,1].
    peak_demand: D_peak_s over the planning window.
    """

    component_capacities: dict[str, float]
    n_s: int
    kappa_s: float
    peak_demand: float

    def __post_init__(self) -> None:
        if self.n_s not in (1, 2):
            raise ValueError(f"n_s must be 1 or 2, got {self.n_s!r}")
        if not 0.0 < self.kappa_s <= 1.0:
            raise ValueError(f"kappa_s must lie in (0,1], got {self.kappa_s!r}")
        if self.peak_demand < 0:
            raise ValueError(f"peak_demand must be non-negative, got {self.peak_demand!r}")
        if self.n_s > len(self.component_capacities):
            raise ValueError(
                f"n_s={self.n_s} exceeds the number of capacity components "
                f"({len(self.component_capacities)}); N-{self.n_s} contingency is undefined"
            )

    @property
    def total_capacity(self) -> float:
        """C_s(t): the service's total automation-dependent capacity."""
        return sum(self.component_capacities.values())

    @property
    def largest_n_components(self) -> list[str]:
        """C^(n)_s(t): the n_s largest components by capacity."""
        ranked = sorted(self.component_capacities, key=lambda c: self.component_capacities[c], reverse=True)
        return ranked[: self.n_s]

    @property
    def rho_s(self) -> float:
        """rho_s = kappa_s * D_peak_s, the RHS of Eq. 14."""
        return self.kappa_s * self.peak_demand


def resilience_reserve(state: ReserveState) -> float:
    """Res^(n_s)_s(t) (Eq. 13): total capacity minus the n_s largest components."""
    lost = sum(state.component_capacities[c] for c in state.largest_n_components)
    return state.total_capacity - lost


def reserve_satisfied(state: ReserveState) -> bool:
    """Eq. 14 as a boolean check."""
    return resilience_reserve(state) >= state.rho_s


def task_delta_resilience(mode: str, task_duration_hours: float, component_capacity_baseline: float) -> float:
    """[INVENTED -- not in the paper] Delta^res_s(m) at single-task granularity.

    Res^(n)_s(t) is defined only at fleet scale (Eq. 13); the paper gives
    no rule for how one task's mode moves it (report Sec. 20.8, blocker H2).
    This repository defines an explicit, documented attribution so that
    Eq. 17's mu_s term and Eq. 18's second admissibility clause are
    computable, and labels it as an engineering addition:

        Delta^res_s(m) = -task_duration_hours / component_capacity_baseline
                          * (2 * automation_dependence(m) - 1)

    A mode with automation_dependence=1 (e.g. A, R) consumes a task's-worth
    of automated capacity and so REDUCES reserve; a mode with
    automation_dependence=0 (H) frees capacity that would otherwise have
    been committed to automation and so INCREASES reserve, at the same
    magnitude; hybrids interpolate. `component_capacity_baseline` is the
    service's total automation-dependent capacity (ReserveState.total_capacity),
    used to express the single task's commitment as a fraction of it.
    """
    if mode not in _AUTOMATION_DEPENDENCE:
        raise ValueError(f"unknown mode {mode!r}")
    if task_duration_hours <= 0:
        raise ValueError(f"task_duration_hours must be positive, got {task_duration_hours!r}")
    if component_capacity_baseline <= 0:
        raise ValueError(
            f"component_capacity_baseline must be positive, got {component_capacity_baseline!r}"
        )
    dependence = _AUTOMATION_DEPENDENCE[mode]
    fraction = task_duration_hours / component_capacity_baseline
    return -fraction * (2.0 * dependence - 1.0)
