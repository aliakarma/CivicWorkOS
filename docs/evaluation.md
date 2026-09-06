# Evaluation

Two entirely different things are documented here, and conflating them is
the single most important mistake to avoid with this repository: **the
worked-example verification** (real, exact, checkable) and **the simulation
demo** (illustrative, synthetic, not the paper's study).

## 1. The worked-example oracle (real verification)

The paper's §5.3 worked bridge-inspection allocation is the ONLY part of the
manuscript with a checkable ground truth. This repository verifies it two
ways:

```bash
python scripts/verify_worked_example.py     # standalone script, human-readable output
pytest tests/smoke/test_worked_example.py -v  # the same checks as pytest assertions
```

Both recompute, from the paper's own stated inputs (Table 3, the HCPB
parameters, Fig. 3's caption parameters) and **without reference to the
paper's printed outputs**: all four `CAD`/`SCV` values, the HCPB budget
(2073.6 h/yr), the constrained-optimum mix (20.8%/79.2%), the dual price
(`lambda_k = 0.0250`), the augmented-score tie/reversal (`SCV~_H =
SCV~_{H+R} = 0.4937 > 0.4863 > 0.4743`), the 9.3% objective cost, and all
five Fig. 3 curves. See
[docs/reproducibility.md](reproducibility.md) for the distinction between
this and "reproducing the paper's results" (there are no other results to
reproduce — see the manuscript's Data Availability Statement).

## 2. Metrics implemented by the simulation demo

The paper specifies thirteen metrics (§6.3). The reduced-scope demo
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
| — | Z4-routing rate | Implemented (not a paper metric; this repository's own monitoring signal, report §18.3) | `SimulationMetrics.z4_routing_rate` |

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

Solves Eq. 16 as a MIP (assignment) and its LP relaxation (duals) over a
small task batch scaled from the worked example's own per-task budget
intensity. See `tests/integration/test_rebalance_solver.py` for why a
reduced task count is used (MIP symmetry at the paper's real 340-task
population — documented, not hidden, in that test's own docstring).

## 4. Baselines

The five strategies of Paper §6.2 are implemented in `sim.strategies.baselines`.
As the paper itself concedes (§7.2), all five are ablations of the same
objective, not independent external systems — report §20.13 names this
limitation directly, and this repository's baseline implementation
(`Conventional Capability Matching` as SCV with `w9` renormalized away) makes
that structural fact explicit in code rather than hiding it behind a
differently-named scoring function.

## 5. Parameter sensitivity

```bash
python scripts/sensitivity_sweep.py 2000 0.20
```

Targets report §16.2's recommendation M1 / Paper §7.2's open question 3
("whether a panel's deliberation is effectively arbitrary" under small
weight perturbations). Runs entirely on the four worked-example candidates —
see the script's own docstring for scope.

## What NOT to report from this repository

Do not present any number from `scripts/run_simulation.py`,
`scripts/sensitivity_sweep.py`, or the `HeuristicMarket` estimator as
evidence about the real framework's behavior. They are software-pipeline
demonstrations. The paper reports no measured results (see its Data
Availability Statement), and this repository does not manufacture any.
