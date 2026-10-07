# Changelog

All notable changes to this repository are documented here.
The format follows [Keep a Changelog](https://keepachangelog.com/en/1.1.0/).

## [0.2.0] - 2026-10-07

Reconciliation of this repository with the revised manuscript (Phase 3 of
`Paper/Frontiers/REVISION-PROGRAMME.md`). The repository had come to document a
paper that no longer existed: it verified an earlier draft's parameterisation,
credited a different author list, and cited section and equation numbers from two
superseded numberings. Every check passed while doing so, which is the failure
mode this release is about.

### Fixed

- **The verification oracle verified the wrong paper.**
  `scripts/verify_worked_example.py`, `tests/smoke/test_worked_example.py` and
  `tests/integration/test_rebalance_solver.py` each asserted `B_k = 2073.6`
  against a manuscript that computes `4976.64`, scored four *execution* modes
  where the article scores eight *staffed* modes, and priced protected practice
  at `lambda_k = 0.0250` against a printed `0.0454`. All three now reproduce the
  article's published values, and the capability price is recovered
  independently by the hand-rolled LP, by the general MIP builder, and by
  closed-form algebra.
- **One definition for every manuscript value.** New `manuscript_values.py`
  re-exports the constants in `Paper/Frontiers/audit_numbers.py`, the module that
  gates the manuscript's own arithmetic. Nothing in the repository restates a
  value the article states. Duplication was the cause of the defect above, so
  the duplication was removed rather than the copies corrected.
- **Author list.** `README.md` and `CITATION.cff` credited four names that are
  not on the manuscript. Both now match `\def\Authors` exactly, in order, and
  `check_repo.py` fails if they ever diverge again.
- **The first CI gate did not run.** `PuLP` was pinned `>=2.7,<4`, but 3.x
  deprecates the `LpVariable` constructor the solver uses and `pytest.ini`
  promotes `DeprecationWarning` to an error, so a clean install collected eight
  errors before running. Pinned to `<3`, with the reason recorded at the pin.
- **The debt model implemented a superseded equation.**
  `civicworkos.analytic.debt_model` modelled a single scalar `pi(t)`, which is
  `D_skill` and nothing else, and labelled the output as CAD. eq:cadmodel sums
  over all five components, each with its own asymptote and time constant; the
  module now implements that, with `residual_slope` and `bounded_ceiling`
  separating the unbounded part from the saturating one. This closes assumption
  A9, and its consequence is unflattering: CivicWorkOS does not bound total
  debt, and Human-First accrues less of it until year 13.23.
- **The shipped domain configuration was the earlier draft's.**
  `configs/domains/structural_inspection.yaml` carried `h_k: 600` where eq:hconv
  gives 1,440 qualified-practice hours, so `B_k` computed from the repository's
  own governance artifact did not match the article. A test now asserts that it
  does.

### Changed

- **The manuscript is cited by LaTeX label, never by number.** All 565 numbered
  references across `README.md`, `docs/`, `scripts/`, `sim/`, `src/`, `tests/`,
  `configs/` and the CI workflow became `sec:worked`, `eq:cad`, `tab:cadparams`
  and so on. Labels survive renumbering; numbers have now moved three times.
  References to the undistributed `PROJECT_REPORT.md` are cited as "the
  pre-release audit", since no reader can resolve a section number in a document
  they do not have. The convention is documented in `CONTRIBUTING.md`.
- **Staffed-mode names are accepted throughout.**
  `PolicyDigitalTwin.status` and `task_delta_resilience` validate the execution-mode
  family and ignore the roster suffix, so `H+A+R/a1` is a valid mode and `H/a1`
  is no longer wrongly prohibited by the statutory sign-off guard.
- `CandidatePair.phi_m` and `AgentEstimate.phi_m` are documented as carrying the
  *credited* share `phi_m * psi_a`. The single-field shape is recorded as
  assumption A12.

### Added

- `Paper/Frontiers/check_repo.py`: three reconciliation gates — every cited
  label resolves in the compiled article, no numbered reference survives, and the
  author list is identical in all three places. Wired into
  `Paper/Frontiers/check.sh` alongside a gate asserting that the suite passes and
  that its count matches the README badge.

## [0.1.0] - 2026-09-03

### Added

Initial engineering reconstruction of the CivicWorkOS formalism from the
source Frontiers *Hypothesis and Theory* manuscript and its accompanying
pre-release audit.

- Core scoring kernel: Civic Automation Debt (eq:cad) and Sustainable Civic
  Value (eq:scv), verified against the paper's worked example (sec:worked)
  to within numerical tolerance.
- Task encoding and developmental content (eq:task and eq:ell).
- Human Capability Preservation Budget (eq:phi, eq:hcpb and eq:hcpb-estimator), Capability Access and
  Just Transition constraints (eq:accessshare, eq:access and eq:justtransition), 3R Reversibility/Resilience
  Reserve (eq:cs and eq:res3r).
- City-wide allocation program (eq:program) as a PuLP MIP, with LP-relaxation
  dual extraction for the online rule's shadow prices.
- Algorithm 1 (eq:aug, eq:admis and eq:argmax): the online Lagrangian rule with the
  feasibility-restoration admissibility test (eq:admis), including both
  restoration branches.
- Civic Capability Ledger (eq:ledger), Policy Digital Twin (eq:policy), Adaptive
  Oversight Zones (tab:zones) with the demotion/restoration asymmetry
  (Suppl. S1.4).
- Seven-item evidentiary record and append-only audit store (Suppl. S1.3),
  contestability workflow with asymmetric appeal windows (Suppl. Table S1).
- Analytic debt-accumulation model (eq:cadmodel), verified against all five
  fig:cad-trend curves.
- A reduced-scope simulation testbed (`sim/`) over synthetic, clearly
  labeled demo data, implementing the five baseline strategies
  (Paper sec:protocol) and a subset of the thirteen evaluation metrics
  (Paper sec:protocol).
- Governance-artifact configuration schema with an explicit `UNSET`
  sentinel for unconfigured normative parameters (Paper sec:feedback).
- Full test suite: unit, integration, and smoke tests, including the
  worked-example oracle (`tests/smoke/test_worked_example.py`).

### Known limitations

See [IMPLEMENTATION_STATUS.md](IMPLEMENTATION_STATUS.md) and
[docs/assumptions.md](docs/assumptions.md). Most significantly: the five
debt-component estimators (beyond `D_skill`), the hybrid-mode `phi_m`
elicitation, `learn_i` elicitation, and the task-granularity resilience
attribution are all necessarily invented by this repository, since the
source paper specifies none of them.
