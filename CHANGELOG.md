# Changelog

## [Unreleased]

Housekeeping after the tagged release, with no change to the simulator, its results, or the hash-checked files.

- Record the Zenodo DOI of `v1.0-submission` (10.5281/zenodo.23953172) in `CITATION.cff`.
- Correct the scope message of `scripts/verify_worked_example.py` and the docstring of `sim/__init__.py`, which still said the protocol had not been executed.
- Replace "pre-registration" with "internal pre-specification" in comments and docstrings outside the hash-checked files.
- Ignore line length for three files in ruff, including `sim/protocol/engine.py`, which cannot be reformatted without invalidating the stored runs.

## [1.0.0] - 2026-11-03

Release `v1.0-submission`, archived with the revised manuscript.

- Add the exploratory analyses of the peer-review revision, defined in `configs/protocol/exploratory_r1.yaml` and produced by `make revision` (`scripts/run_revision.py`, `scripts/weights_sensitivity.py`, `reproducibility/make_revision_tables.py`). New engine options (`WorldModel`, add-one and drop-one policies, read-only revision counters) are off by default, and a replay reproduced all 630 stored reference and baseline records. None enters the Holm family. The article's "pre-registration" wording becomes "internally pre-specified".
- Add exploratory analyses that were added after internal pre-specification, as submission phase P4. They are defined in `configs/protocol/exploratory_p4.yaml` before any of them was run, and `scripts/run_exploratory.py --blocks ...` produces them. The new blocks in `reproducibility/data/exploratory.json` are `baselines`, `sensor_realism`, `takeover_sweep`, `model_sensitivity`, `derived`, and `p4_meta`, and the existing `outcome_only` and `sensitivity` blocks are byte-identical. None of them enters the Holm family.
- Add three rule-based baselines in a separate registry (`EXPLORATORY_POLICY_FLAGS`): `efficiency_quota`, `efficiency_recency`, and `efficiency_quota_recency`. `POLICIES`, `POLICY_FLAGS`, and the 450-run reference execution are unchanged.
- Add person-specific sensor bias (`SensorRealism`, default zero) drawn from separate generators `[seed, 7919, 1]` and `[seed, 7919, 2]`, and read-only stop-cause, incident-free-completion, and workload-estimate counters returned only by `run_one(..., counters=True)`. See `docs/sensor_realism.md`.
- Generate the manuscript blocks for the P4 evidence: Panel C of the exploratory table (`EXPTABLE`), the sensor-realism figure (`SENSORFIG`), and five supplementary tables (`SUPPBASELINES`, `SUPPSENSOR`, `SUPPTAKEOVER`, `SUPPMODEL`, `SUPPDERIVED`). Extend `reproducibility/audit_numbers.py` with 67 checks of the new numbers quoted in prose (390 PASS / 0 FAIL).
- Append per-point 95% t-interval columns (`<policy>_curr_lo/_hi`) to `trajectory_*.dat` and draw them as bands in `fig:trajectories`. The original columns are unchanged. All 450 reporting runs, `summary.json`, and `hypotheses.json` reproduce byte for byte.

- Move the manuscript audit, table generator, six frozen data files, and eight generated LaTeX blocks into public `reproducibility/`. Keep the manuscript private.
- Repoint the shared manuscript constants, protocol and exploratory writers, Makefile, tests, and documentation to the public paths. `make protocol` now runs without manuscript sources. Private splicing remains available with `python reproducibility/make_sim_tables.py --splice`.
- Preserve every stored result and generated block. The public audit requires no manuscript source. Git attributes preserve the frozen data and generated-block bytes across checkouts.

All notable changes to this repository are documented here.
The format follows [Keep a Changelog](https://keepachangelog.com/en/1.1.0/).

## [0.3.0] - 2026-10-16

Retargeting to *Frontiers in Neurorobotics* (Methods article, Research Topic
"Data-driven Neurorobotics: Multimodal Learning, Adaptive Intelligence, and
Reproducible Human-Robot Interaction") under the new title *CivicWorkOS:
Capability-Preserving Adaptive Task Allocation Among Humans, AI Agents, and
Robots in Municipal Services*.

### Added

- `sim/protocol/`: the article's evaluation protocol, executed. A day-stepped
  synthetic testbed with three service domains, five policies (static,
  efficiency-focused, CivicWorkOS, and two ablations), three scenarios
  (routine, demand surge, silent automation disruption), and five metric
  families (completion, cost, workload, skill retention, takeover).
- `sim/protocol/skill.py`: the proficiency model (learning curve, decay
  without human-led work, recency interval of Proposition 1).
- `sim/protocol/estimation.py`: the adaptive learning mechanism
  (assumed-density-filtering outcome update, Kalman update for multimodal
  observations).
- `configs/protocol/hypotheses.yaml`: hypotheses H1-H8, written before the
  evaluation code.
- `scripts/run_protocol.py` and `make protocol`: the reference execution
  (seeds 0-29, 450 runs); `Paper/Frontiers/make_sim_tables.py` generates the
  article's simulation tables and Figure 4 from its outputs.
- 24 tests for the proficiency model, the learning updates, the statistics,
  and the testbed's determinism and common random numbers.
- `audit_numbers.py` checks every simulation number quoted in the article's
  prose against `Paper/Frontiers/data/`.

### Changed

- Manuscript restructured for the new journal: adaptive learning, proficiency
  dynamics, workload, periodic human-led tasks, uncertainty-gated oversight,
  and readiness-constrained control transfer are now central; legal, data
  protection, and contestability detail moved to the Supplementary Material.
- The raster architecture and workflow figures were replaced by vector TikZ.
- README, CITATION.cff, and docs describe the new evidence base. The README's
  citation block previously listed an author set that did not match the
  manuscript; it now matches.
- Dependencies: `numpy` and `scipy` added for the testbed.

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
