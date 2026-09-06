r"""The city-wide allocation program: Paper Sec. 4.4, Eq. 16.

    max_x   sum_i sum_m  x_{i,m} * SCV_{i,m}                                  (16a)
    s.t.    sum_m x_{i,m} = 1                                       for all i  (16b)  assignment
            x_{i,m} = 0  if P(T_i,m,t) = prohibit                              (16c)  policy
            x_{i,m} = 0  if S_{i,m} < S^min_i                                  (16d)  safety floor
            sum_{i in T_k} sum_m x_{i,m}*ell_i*phi_m >= B_k(t)      for all k  (16e)  HCPB
            Pi_{k,g}(x) >= theta_{k,g} - epsilon_k              for all k,g   (16f)  access
            Res^(n_s)_s(x) >= kappa_s*D_peak_s                   for all s    (16h)  3R reserve
            sum_i sum_m x_{i,m}*u_{i,m,r} <= U_r                  for all r   (16i)  resource
            x_{i,m} in {0,1}                                                  (16j)

Complexity (Sec. 4.4): "A binary multi-dimensional assignment problem
with side constraints, NP-hard in general -- it reduces to a generalized
assignment problem when only (16i) binds -- which is why the framework
solves it periodically over a window rather than continuously."

Scope of this builder (documented, not hidden -- see docs/assumptions.md A8):
  - (16c)/(16d) are enforced by NOT INCLUDING a variable for a
    policy-prohibited or unsafe (task, mode) pair, rather than as an
    explicit zero constraint -- equivalent, smaller model.
  - (16f) is linear-fractional in x (Eq. 10's ratio); this builder
    linearizes it by multiplying through the constant
    (theta_{k,g} - epsilon_k) rather than the variable denominator,
    which is valid because the denominator's coefficients are also
    linear in x -- report Sec. 8.4 flags this linearization as [INFER],
    not stated by the paper.
  - (16h) uses the same invented task-granularity resilience attribution
    as the online rule (civicworkos.constraints.resilience.task_delta_resilience),
    for internal consistency between the batch and online paths.
  - (16g), the Just Transition Constraint, is DELIBERATELY NOT embedded
    as a MIP constraint here. Delta_g requires a baseline allocation of
    ALL task-hours (not just protected-practice hours) to each group,
    which needs an assignee mapping for every mode -- not only the
    phi_m > 0 modes (16f) needs -- compounding an already-invented
    assumption. This repository instead evaluates (16g) POST HOC against
    a realized solution via civicworkos.constraints.access.JustTransitionConstraint,
    so the assumption stays visible rather than buried inside solver output.
"""

from __future__ import annotations

from dataclasses import dataclass, field

import pulp

from civicworkos.constraints.access import CapabilityAccessConstraint
from civicworkos.constraints.resilience import ReserveState, resilience_reserve, task_delta_resilience


@dataclass(frozen=True)
class TaskInstance:
    """One task in the rebalancing window."""

    task_id: str
    domain: str
    service: str
    ell_i: float
    duration_hours: float


@dataclass(frozen=True)
class CandidatePair:
    """One policy-admissible, safety-admissible (task, mode) pair.

    scv: SCV_{i,m} (Eq. 15), already composed.
    phi_m: human developmental share of this mode (Eq. 7).
    assignee_group: [INFER] the worker group Eq. 10/16f attributes this
        pair's protected-practice hours to. The paper does not specify
        who chooses this; see civicworkos.online.algorithm1.select_assignee_group
        for the online-rule analogue, and docs/assumptions.md A6.
    resource_usage: {resource_id: u_{i,m,r}} consumed if this pair is chosen.
    """

    task_id: str
    mode: str
    scv: float
    phi_m: float
    assignee_group: str | None = None
    resource_usage: dict[str, float] = field(default_factory=dict)


@dataclass(frozen=True)
class ProgramInputs:
    tasks: list[TaskInstance]
    candidates: list[CandidatePair]
    domain_budgets: dict[str, float]  # B_k(t), Eq. 9, per domain
    access_constraints: dict[tuple[str, str], CapabilityAccessConstraint]  # (domain, group)
    reserve_states: dict[str, ReserveState]  # per service
    resource_capacities: dict[str, float]  # U_r


@dataclass
class BuiltProgram:
    problem: pulp.LpProblem
    variables: dict[tuple[str, str], pulp.LpVariable]  # (task_id, mode) -> x
    hcpb_constraint_names: dict[str, str]  # domain -> constraint name
    access_constraint_names: dict[tuple[str, str], str]  # (domain, group) -> constraint name
    reserve_constraint_names: dict[str, str]  # service -> constraint name


def build_program(inputs: ProgramInputs, *, integer: bool = True) -> BuiltProgram:
    """Construct Eq. 16 as a PuLP problem.

    `integer=False` builds the LP relaxation (x continuous in [0,1]),
    used by civicworkos.solver.rebalance for dual extraction, since
    integer programs do not have LP-style duals (report Sec. 16.2's
    recommendation, followed here rather than reading duals off a MIP
    incumbent).
    """
    tasks_by_id = {t.task_id: t for t in inputs.tasks}
    problem = pulp.LpProblem("civicworkos_city_program", pulp.LpMaximize)

    cat = pulp.LpBinary if integer else pulp.LpContinuous
    variables: dict[tuple[str, str], pulp.LpVariable] = {}
    for c in inputs.candidates:
        var = pulp.LpVariable(f"x_{c.task_id}_{c.mode}", lowBound=0, upBound=1, cat=cat)
        variables[(c.task_id, c.mode)] = var

    # (16a) objective.
    problem += pulp.lpSum(c.scv * variables[(c.task_id, c.mode)] for c in inputs.candidates)

    # (16b) assignment: each task picks exactly one of its surviving candidates.
    candidates_by_task: dict[str, list[CandidatePair]] = {}
    for c in inputs.candidates:
        candidates_by_task.setdefault(c.task_id, []).append(c)
    for task_id, cands in candidates_by_task.items():
        problem += (
            pulp.lpSum(variables[(task_id, c.mode)] for c in cands) == 1,
            f"assignment_{task_id}",
        )

    # (16e) HCPB per domain.
    hcpb_names: dict[str, str] = {}
    domains = {t.domain for t in inputs.tasks}
    for domain in domains:
        if domain not in inputs.domain_budgets:
            continue
        terms = []
        for c in inputs.candidates:
            task = tasks_by_id[c.task_id]
            if task.domain != domain:
                continue
            terms.append(task.ell_i * c.phi_m * variables[(c.task_id, c.mode)])
        if not terms:
            continue
        name = f"hcpb_{domain}"
        problem += (pulp.lpSum(terms) >= inputs.domain_budgets[domain], name)
        hcpb_names[domain] = name

    # (16f) Capability Access Constraint, linearized (report Sec. 8.4, [INFER]):
    #   sum_{assignee in g} x*ell*phi  >=  (theta_kg - eps_k) * sum_{all} x*ell*phi
    access_names: dict[tuple[str, str], str] = {}
    for (domain, group), constraint in inputs.access_constraints.items():
        all_terms = []
        group_terms = []
        for c in inputs.candidates:
            task = tasks_by_id[c.task_id]
            if task.domain != domain or c.phi_m <= 0:
                continue
            term = task.ell_i * c.phi_m * variables[(c.task_id, c.mode)]
            all_terms.append(term)
            if c.assignee_group == group:
                group_terms.append(term)
        if not all_terms:
            continue
        name = f"access_{domain}_{group}"
        problem += (
            pulp.lpSum(group_terms) - constraint.floor * pulp.lpSum(all_terms) >= 0,
            name,
        )
        access_names[(domain, group)] = name

    # (16h) 3R Reserve per service, using the same invented per-task
    # attribution as the online rule for consistency.
    reserve_names: dict[str, str] = {}
    for service, state in inputs.reserve_states.items():
        baseline = resilience_reserve(state)
        deltas = []
        for c in inputs.candidates:
            task = tasks_by_id[c.task_id]
            if task.service != service:
                continue
            delta = task_delta_resilience(c.mode, task.duration_hours, state.total_capacity)
            deltas.append(delta * variables[(c.task_id, c.mode)])
        if not deltas:
            continue
        name = f"reserve_{service}"
        problem += (baseline + pulp.lpSum(deltas) >= state.rho_s, name)
        reserve_names[service] = name

    # (16i) resource capacity.
    resources = {r for c in inputs.candidates for r in c.resource_usage}
    for resource in resources:
        cap = inputs.resource_capacities.get(resource)
        if cap is None:
            continue
        terms = [
            c.resource_usage.get(resource, 0.0) * variables[(c.task_id, c.mode)]
            for c in inputs.candidates
        ]
        problem += (pulp.lpSum(terms) <= cap, f"resource_{resource}")

    return BuiltProgram(
        problem=problem,
        variables=variables,
        hcpb_constraint_names=hcpb_names,
        access_constraint_names=access_names,
        reserve_constraint_names=reserve_names,
    )
