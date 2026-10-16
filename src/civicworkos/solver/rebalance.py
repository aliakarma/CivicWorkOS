"""Periodic rebalance: solve eq:program, publish duals.

Paper sec:program and sec:online: "The relationship between the two [online rule and
batch program] is standard for Lagrangian decomposition." The paper
names NEITHER a solver NOR a dual-extraction method (the pre-release audit,
"Unspecified"). This module makes an explicit, documented choice
(the pre-release audit's recommendation): solve the MIP for the assignment
x, then solve the LP RELAXATION of the SAME model to extract shadow
prices, because integer programs do not have LP-style duals -- reading
them off a MIP incumbent would be meaningless.

Backend: PuLP with its bundled CBC solver. The paper names "a mixed-
integer solver" without specifying one; the pre-release audit recommends "a
modelling layer with pluggable open and commercial backends" so the
formulation is not rewritten to change solvers -- PuLP already provides
that pluggability (CBC by default; GLPK, HiGHS, Gurobi, CPLEX etc. via
the same `LpProblem.solve(solver=...)` call).
"""

from __future__ import annotations

import os
from dataclasses import dataclass

import pulp

from civicworkos.program.city_program import ProgramInputs, build_program


@dataclass
class RebalanceResult:
    status: str
    assignment: dict[tuple[str, str], float]  # (task_id, mode) -> x value (0/1 for the MIP)
    objective_value: float
    lambda_k: dict[str, float]  # HCPB dual per domain
    mu_s: dict[str, float]  # 3R reserve dual per service
    nu_kg: dict[tuple[str, str], float]  # access dual per (domain, group)
    dual_extraction_method: str


_DEFAULT_TIME_LIMIT_SECONDS = 60
"""[REC, not in the paper] eq:program is NP-hard in general and the paper
gives no problem-size envelope or infeasibility/timeout policy (the
pre-release audit flags both). A large population of near-IDENTICAL task
candidates (as in the worked example at its full 2,100 inspections) is also
combinatorially symmetric, which can make branch-and-bound solvers
explore far longer than the LP relaxation's triviality would suggest.
Rather than let a rebalance hang indefinitely, this module bounds the
default solver call and reports whatever CBC's status was when it
stopped -- a caller needing an exact certificate for a large, symmetric
instance should pass its own `solver=` with a longer or no time limit.
Overridable via the CIVICWORKOS_SOLVER_TIME_LIMIT_SECONDS environment
variable (see .env.example) without changing calling code.
"""


def _default_time_limit_seconds() -> int:
    raw = os.environ.get("CIVICWORKOS_SOLVER_TIME_LIMIT_SECONDS")
    if raw is None:
        return _DEFAULT_TIME_LIMIT_SECONDS
    try:
        return int(raw)
    except ValueError as exc:
        raise ValueError(
            f"CIVICWORKOS_SOLVER_TIME_LIMIT_SECONDS must be an integer, got {raw!r}"
        ) from exc


def _solve(problem: pulp.LpProblem, solver: pulp.LpSolver | None) -> str:
    chosen = solver or pulp.PULP_CBC_CMD(msg=0, timeLimit=_default_time_limit_seconds())
    status_code = problem.solve(chosen)
    return pulp.LpStatus[status_code]


def solve_rebalance(inputs: ProgramInputs, *, solver: pulp.LpSolver | None = None) -> RebalanceResult:
    """Solve eq:program (MIP) for the assignment, then its LP relaxation for duals."""
    mip = build_program(inputs, integer=True)
    mip_status = _solve(mip.problem, solver)
    if mip_status != "Optimal":
        return RebalanceResult(
            status=mip_status,
            assignment={},
            objective_value=float("nan"),
            lambda_k={},
            mu_s={},
            nu_kg={},
            dual_extraction_method="none (MIP not optimal)",
        )

    assignment = {key: var.value() for key, var in mip.variables.items()}
    objective_value = pulp.value(mip.problem.objective)

    lp = build_program(inputs, integer=False)
    lp_status = _solve(lp.problem, solver)
    lambda_k: dict[str, float] = {}
    mu_s: dict[str, float] = {}
    nu_kg: dict[tuple[str, str], float] = {}
    if lp_status == "Optimal":
        for domain, name in lp.hcpb_constraint_names.items():
            pi = lp.problem.constraints[name].pi
            lambda_k[domain] = abs(pi) if pi is not None else 0.0
        for service, name in lp.reserve_constraint_names.items():
            pi = lp.problem.constraints[name].pi
            mu_s[service] = abs(pi) if pi is not None else 0.0
        for key, name in lp.access_constraint_names.items():
            pi = lp.problem.constraints[name].pi
            nu_kg[key] = abs(pi) if pi is not None else 0.0

    return RebalanceResult(
        status=mip_status,
        assignment=assignment,
        objective_value=objective_value,
        lambda_k=lambda_k,
        mu_s=mu_s,
        nu_kg=nu_kg,
        dual_extraction_method=(
            "LP relaxation shadow price (constraint.pi), sign normalized to "
            "the paper's non-negative dual convention (eq:aug: lambda,mu,nu >= 0)"
            if lp_status == "Optimal"
            else f"LP relaxation status was {lp_status}, no duals extracted"
        ),
    )
