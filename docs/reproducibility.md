# Reproducibility

This document draws one distinction carefully, because the source paper
itself insists on it: **software-pipeline reproducibility** (this repository
runs the same way every time, and its arithmetic matches the paper's own
worked example) is completely different from **scientific result
reproduction** (there are no scientific results in the paper to reproduce).

## What the paper itself says

> "No datasets were generated or analyzed for this Hypothesis and Theory
> contribution, and no measured results are reported." — Data Availability
> Statement

> "[Figure 3] illustrates what the model implies and establishes nothing
> about what a city would experience." — §7, status box

The paper's OWN reproducibility claim is narrower and true: its worked
example (§5.3) and analytic model (§7.1, Fig. 3) are "reproducible from the
article alone." This repository independently verified that claim
(`scripts/verify_worked_example.py`) and found it correct to within
numerical tolerance.

## What IS reproducible from this repository

1. **The worked example's arithmetic**, exactly, from the paper's own stated
   inputs — see [evaluation.md](evaluation.md) §1. Run
   `python scripts/verify_worked_example.py`; it should print
   `All worked-example numbers reproduced within tolerance.` and exit 0,
   deterministically, on any machine with the dependencies installed.
2. **The test suite**, deterministically — no external data, no random seeds
   left unfixed in a way that would change pass/fail status (the simulation
   demo takes an explicit `seed` argument).
3. **The Docker image's build**, from the pinned `pyproject.toml`
   dependencies (see [setup.md](setup.md)).

## What is NOT reproducible, because it does not exist

- **The paper's evaluation study** (§6): six sectors, ten years, five
  strategies, ≥30 seeds, thirteen metrics, seven stress scenarios, ten
  pre-registered predictions. The paper states this platform "has not been
  built" and "no result from it appears anywhere in this paper." This
  repository's `sim/` package is a reduced-scope demonstration
  of the PROTOCOL's software shape — not a reconstruction of a study that
  was never run, and its numbers are not comparable to anything the paper
  reports (because the paper reports nothing from this study).
- **Calibration against real municipal data**: the paper names seven
  intended open-data sources (NYC Open Data, London Datastore, Open Data
  BCN, Helsinki Region Infoshare, national bridge inventories) and states
  explicitly that "no data from them has yet been retrieved or analyzed."
  This repository does not retrieve them either — `sim.calibration.sources`
  documents them as metadata only.
- **The three parameters the entire capability mechanism depends on**
  (`learn_i`, hybrid `phi_m`, `h_k`'s real-world value) — Suppl. S4 states
  "no open portal known to us publishes the practitioner-level developmental
  data" these require. They must be elicited from practitioners (paper's
  own stated future work, Phase 11); no simulation run, including this
  repository's, can substitute for that elicitation.

## Reproducibility scorecard (this repository's own honest self-assessment)

| Dimension | Score | Why |
| --- | --- | --- |
| Worked-example arithmetic | Exact | Verified digit-by-digit against the paper's Table 3 and Fig. 3 caption values. |
| Core equations as code | High | Eq. 2, 4, 7-9, 10-14, 15, 17-19, 21 implemented and unit-tested. |
| Full system behavior | N/A | The paper describes no system to compare against — none was built. |
| Evaluation study (§6) | Not attempted at paper scale | Reduced-scope demo only; see `docs/assumptions.md` A10. |
| Calibration to real data | Not attempted | Consistent with the paper's own stated status (no data retrieved). |

## Determinism notes

- `sim.calibration.sources.synthetic_demo_tasks(n, domain, service, seed)`
  is deterministic given the same seed.
- `civicworkos.solver.rebalance.solve_rebalance` calls CBC with a bounded
  time limit (`CIVICWORKOS_SOLVER_TIME_LIMIT_SECONDS`, default 60s); a
  large, highly symmetric instance may return a different (but still
  feasible) integer solution across runs if CBC's search is interrupted
  before proving optimality — see
  [troubleshooting.md](troubleshooting.md#slow-or-hanging-mip-solves).
- The LP relaxation used for dual extraction is deterministic given a fixed
  problem; CBC's LP solve does not time out in the scales this repository
  exercises.
