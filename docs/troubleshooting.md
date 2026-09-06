# Troubleshooting

## `scripts/verify_worked_example.py` fails

This is the repository's ground-truth check. A failure here means either
your environment is broken (check `pip list` against `requirements.txt`) or
a regression was introduced into `civicworkos.scoring`,
`civicworkos.constraints.hcpb`, or `civicworkos.analytic`. Do not weaken the
tolerance in that script to make it pass — fix the underlying arithmetic.

## `pip install -e .` fails with `invalid command 'bdist_wheel'`

Older `pip`/`setuptools` combinations need the `wheel` package explicitly:

```bash
pip install wheel
pip install -e .
```

This was hit and fixed during this repository's own build — see
[SMOKE_TEST_REPORT.md](../SMOKE_TEST_REPORT.md).

## Slow or hanging MIP solves

`civicworkos.program.city_program` builds a binary variable per (task,
mode) pair. If your task population contains many **near-identical**
candidates (the same SCV values repeated across tasks — e.g. the worked
example scaled to its real 340 tasks/year), the resulting MIP is
**combinatorially symmetric**: every permutation of "which N tasks get mode
H" is an equally-good optimum, and generic branch-and-bound solvers (CBC
included) can spend a very long time distinguishing between symmetric
solutions even though the LP relaxation solves instantly.

This was observed directly while building this repository:
`civicworkos.solver.solve_rebalance` on 340 identical worked-example
candidates did not return within several minutes; on 12-30 identical
candidates it returns in under a second (see
`tests/integration/test_rebalance_solver.py`'s docstring and
[SMOKE_TEST_REPORT.md](../SMOKE_TEST_REPORT.md) for the exact numbers
observed).

**Mitigations, in order of preference:**

1. **Reduce symmetry** by giving each task a slightly different SCV (e.g. a
   tiny task-specific perturbation, or genuinely different demand vectors —
   real municipal tasks are rarely truly identical).
2. **Lower `CIVICWORKOS_SOLVER_TIME_LIMIT_SECONDS`** (default 60) to fail
   fast and inspect the best-found solution rather than waiting for a
   proof of optimality that may never come at scale.
3. **Solve the LP relaxation only** if you need the aggregate mix (fractional
   shares) rather than a literal per-task integer assignment — this is what
   `tests/smoke/test_worked_example.py` does, and it is exact and instant.
4. **Supply your own `solver=` argument** to `solve_rebalance()` with a
   commercial solver (Gurobi, CPLEX) if you need an exact integer solution
   at real scale — PuLP supports this without changing the model.

The paper itself gives no problem-size envelope for Eq. 16 and names this
as an open question (report §8.1); this is not a defect specific to this
implementation.

## `PulpSolverError` mentioning `cbc.exe`

Usually means a previous CBC process was killed mid-solve (e.g. by an OS
timeout or a forced process kill) and left a lock or corrupted temp file.
Ensure no orphaned `cbc` process is running, and retry. If it persists,
check that `PuLP`'s bundled solver binary has execute permissions (rare on
some Linux/CI images — see PuLP's own documentation for
`pulp.pulpTestAll()`).

## Docker build succeeds but `docker run` fails / Docker daemon not running

This repository's own validation pass hit `error during connect ... open
//./pipe/dockerDesktopLinuxEngine` — Docker Desktop was installed but its
daemon was not running. Start Docker Desktop (or your Docker daemon) before
running `docker build`/`docker run`. This is an environment issue, not a
Dockerfile defect; see [SMOKE_TEST_REPORT.md](../SMOKE_TEST_REPORT.md) for
what was and was not validated.

## `AllocationEngine.allocate()` always routes to Z4

Two independent [INVENTED] components can be poorly calibrated against each
other if you swap one out: `civicworkos.online.algorithm1.default_safety_floor`
and `civicworkos.market.agents.HeuristicMarket`'s archetype safety values.
This repository's defaults are calibrated so a moderate-risk task usually
clears the floor (see `docs/assumptions.md` A7); a HIGH-risk/HIGH-criticality
task, or a custom market estimator with lower safety outputs, can
legitimately push every mode below the floor — that is the framework working
as specified (Fig. 2: "either filtering stage may empty the candidate set"),
not a bug. If it happens unexpectedly, print each candidate's
`terms.S` and compare against `default_safety_floor(task)` (or your custom
`safety_floor_fn`) to see which clause is excluding every mode.

## Tests pass locally but a config file doesn't validate

`civicworkos.config.load_weights_config` / `load_domain_config` raise if
`w1..w9` or `alpha..epsilon` do not sum to 1.0 (within `1e-6`), or if a
domain config is missing a required field. This is intentional — Paper
§5.1 requires weight vectors to be exact governance artifacts; there is no
silent renormalization. Fix the YAML file's values rather than relaxing the
validator.
