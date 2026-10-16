# Evaluation

Two entirely different things are documented here, and conflating them is
the single most important mistake to avoid with this repository: **the
worked-example verification** (real, exact, checkable) and **the simulation
demo** (illustrative, synthetic, not the paper's study).

## 1. The worked-example oracle (real verification)

The paper's sec:worked worked bridge-inspection allocation is the ONLY part of the
manuscript with a checkable ground truth. This repository verifies it two
ways:

```bash
python scripts/verify_worked_example.py     # standalone script, human-readable output
pytest tests/smoke/test_worked_example.py -v  # the same checks as pytest assertions
```

Both recompute, from the paper's own stated inputs (tab:worked-terms, the HCPB
parameters, tab:cadparams) and **without reference to the paper's printed
outputs**: all eight staffed modes' `CAD` and `SCV` values, the HCPB budget
(4,976.64 h/yr from eq:bkworked), the constrained-optimum mix (28.30%/71.70%,
tab:worked-mix), the dual price (`lambda_k = 0.045353`, eq:lambdaworked), the
augmented-score tie and reversal (both active staffed modes at 0.435229, above
the unconstrained winner's 0.342612), the 4.34% objective cost of preservation,
the intake requirement (`tau_k = 4.05` years, `n_hat_k = 14`) by two independent
routes, the access arithmetic (622 h against 1,344 h, a 2.16x multiplier), and
all six fig:cad-trend trajectories under the five-component eq:cadmodel.

Every manuscript input is imported from `manuscript_values`, which re-exports the
single definition in `Paper/Frontiers/audit_numbers.py`. Neither the script nor
the test suite restates a value the article states; what they hold is the
*printed* values, because the question they answer is whether this code
reproduces what was published.

See [docs/reproducibility.md](reproducibility.md) for the distinction between
this and "reproducing the paper's results" (there are no other results to
reproduce -- see the manuscript's Data Availability Statement).

## 2. Metrics implemented by the simulation demo

The paper specifies thirteen metrics (sec:protocol). The reduced-scope demo
(`sim.des.engine`) computes five of them, approximately, on synthetic data:

| # | Paper metric | Implemented? | Where |
| --- | --- | --- | --- |
| 1 | Productivity index | Approximated (raw mean `P`, not normalized to Automation-First=100) | `SimulationMetrics.productivity_index` |
| 2 | Operating cost index | Approximated (raw mean `Cost`) | `SimulationMetrics.operating_cost_index` |
| 3 | Service quality | Not implemented | — |
| 4 | Safety incidents | Not implemented | — |
| 5 | Energy use index | Not implemented | — |
| 6 | Mean recovery time | Not implemented (no stress-scenario injection wired into the demo loop) | — |
| 7 | Capability-Formation Index | Implemented | `SimulationMetrics.capability_formation_index` |
| 8 | Accumulated CAD | Implemented (not normalized to Automation-First=100) | `SimulationMetrics.accumulated_cad` |
| 9 | Realized dual `lambda_k` | Not wired into the demo loop (available via `civicworkos.solver`) | — |
| 10 | Protected-practice share by group `Pi_{k,g}` | Tracked internally by `AllocationEngine` but not surfaced by the demo's metrics object | `AllocationEngine._group_hours` |
| 11 | Displacement by group `Delta_g` | Not implemented (see `docs/assumptions.md` A8) | — |
| 12 | Service-equity dispersion | Not implemented | — |
| 13 | Contestability throughput | Not implemented in the demo loop (the appeals workflow itself IS implemented — `civicworkos.appeals`) | — |
| — | Z4-routing rate | Implemented (not a paper metric; this repository's own monitoring signal, the pre-release audit) | `SimulationMetrics.z4_routing_rate` |

Run it:

```bash
python scripts/run_simulation.py 200 42
```

**This is not the paper's evaluation study.** It runs a single domain over a
short synthetic task list, not six sectors over ten years with ≥30 paired
seeds. See [reproducibility.md](reproducibility.md).

## 3. Rebalancing and duals

```bash
python scripts/run_rebalance.py 12
```

Solves eq:program as a MIP (assignment) and its LP relaxation (duals) over a
small task batch scaled from the worked example's own per-task budget
intensity. See `tests/integration/test_rebalance_solver.py` for why a
reduced task count is used (MIP symmetry at the paper's real 2,100-inspection
population — documented, not hidden, in that test's own docstring).

## 4. Baselines

The five strategies of Paper sec:protocol are implemented in `sim.strategies.baselines`.
As the paper itself concedes (sec:whatworked), all five are ablations of the same
objective, not independent external systems — the pre-release audit names this
limitation directly, and this repository's baseline implementation
(`Conventional Capability Matching` as SCV with `w9` renormalized away) makes
that structural fact explicit in code rather than hiding it behind a
differently-named scoring function.

## 5. Parameter sensitivity

```bash
python scripts/sensitivity_sweep.py 2000 0.20
```

Targets the pre-release audit's recommendation M1 / Paper sec:whatworked's open question 3
("whether a panel's deliberation is effectively arbitrary" under small
weight perturbations). Runs entirely on the four worked-example candidates —
see the script's own docstring for scope.

## What NOT to report from this repository

Do not present any number from `scripts/run_simulation.py`,
`scripts/sensitivity_sweep.py`, or the `HeuristicMarket` estimator as
evidence about the real framework's behavior. They are software-pipeline
demonstrations. The paper reports no measured results (see its Data
Availability Statement), and this repository does not manufacture any.
