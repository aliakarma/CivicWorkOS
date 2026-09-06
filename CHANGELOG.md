# Changelog

All notable changes to this repository are documented here.
The format follows [Keep a Changelog](https://keepachangelog.com/en/1.1.0/).

## [0.1.0] - 2026-09-03

### Added

Initial engineering reconstruction of the CivicWorkOS formalism from the
source Frontiers *Hypothesis and Theory* manuscript and its accompanying
`PROJECT_REPORT.md`.

- Core scoring kernel: Civic Automation Debt (Eq. 2) and Sustainable Civic
  Value (Eq. 15), verified against the paper's worked example (Sec. 5.3)
  to within numerical tolerance.
- Task encoding and developmental content (Eq. 3-4).
- Human Capability Preservation Budget (Eq. 7-9), Capability Access and
  Just Transition constraints (Eq. 10-12), 3R Reversibility/Resilience
  Reserve (Eq. 13-14).
- City-wide allocation program (Eq. 16) as a PuLP MIP, with LP-relaxation
  dual extraction for the online rule's shadow prices.
- Algorithm 1 (Eq. 17-19): the online Lagrangian rule with the
  feasibility-restoration admissibility test (Eq. 18), including both
  restoration branches.
- Civic Capability Ledger (Eq. 5), Policy Digital Twin (Eq. 6), Adaptive
  Oversight Zones (Table 2) with the demotion/restoration asymmetry
  (Suppl. S1.4).
- Seven-item evidentiary record and append-only audit store (Suppl. S1.3),
  contestability workflow with asymmetric appeal windows (Suppl. Table S1).
- Analytic debt-accumulation model (Eq. 21), verified against all five
  Fig. 3 curves.
- A reduced-scope simulation testbed (`sim/`) over synthetic, clearly
  labeled demo data, implementing the five baseline strategies
  (Paper Sec. 6.2) and a subset of the thirteen evaluation metrics
  (Paper Sec. 6.3).
- Governance-artifact configuration schema with an explicit `UNSET`
  sentinel for unconfigured normative parameters (Paper Sec. 5.1).
- Full test suite: unit, integration, and smoke tests, including the
  worked-example oracle (`tests/smoke/test_worked_example.py`).

### Known limitations

See [IMPLEMENTATION_STATUS.md](IMPLEMENTATION_STATUS.md) and
[docs/assumptions.md](docs/assumptions.md). Most significantly: the five
debt-component estimators (beyond `D_skill`), the hybrid-mode `phi_m`
elicitation, `learn_i` elicitation, and the task-granularity resilience
attribution are all necessarily invented by this repository, since the
source paper specifies none of them.
