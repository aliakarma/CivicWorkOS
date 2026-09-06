# Deployment / Productionization

## Framing

The source paper is a *Hypothesis and Theory* article and makes no
production-readiness claim. This document separates what the paper's own
architecture requires from what a real municipal deployment would ALSO
need — clearly marking which is which, per report §18.

## Required by the paper (implemented here)

| Requirement | Paper evidence | Where in this repository |
| --- | --- | --- |
| Event-driven architecture; governance services persistent behind pub/sub | §4.1 | `civicworkos.feedback.bus.FeedbackBus`, subscribed by `AllocationEngine` at construction |
| Market instantiates a short-lived per-task negotiation | §4.1 | `AllocationEngine.allocate()` queries the market fresh per task |
| Rebalancing solver as a scheduled batch job | §4.1 | `civicworkos.solver.solve_rebalance` — this repository does not itself provide a scheduler; call it periodically from cron/Airflow/etc. |
| Feedback bus updates BOTH ledger and policy-compliance monitoring | §4.1, Fig. 1 caption | `AllocationEngine` registers both subscribers together, so a caller cannot wire only one |
| Versioned parameter updates; every allocation traces to its authorizing config | §5.1 | `civicworkos.config` (Pydantic schema with `version`/`effective_date`); `EvidentiaryRecord.config_version` |
| Published dual prices | §4.5 | `RebalanceResult.lambda_k/.mu_s/.nu_kg` — printing/publishing them is the caller's responsibility |
| Append-only, disclosable evidentiary record per decision | Suppl. S1.3 | `EvidentiaryRecordStore` (no update/delete method exists) |
| Appeal windows with outcome/displacement suspension | Suppl. Table S1 | `civicworkos.appeals.contestability.APPEAL_WINDOWS` |
| Automatic one-zone demotion; restoration requires a panel decision | Suppl. S1.4 | `civicworkos.zones.oversight_zones.ZoneRegistry` enforces this asymmetry in code (raises if violated) |
| Constraint updates without redeploying the market | Stress scenario vii | `PolicyDigitalTwin.add_rule()` mutates live state; exercised in `tests/unit/test_policy_twin.py` |

## Required for production, ABSENT from the paper and NOT built here

This is deliberate: the paper does not specify these, and inventing a
production-grade design for each would be presenting invention as
reproduction. A team deploying this repository must build:

- **API/service boundary.** This repository is a library; there is no HTTP
  server, authentication, or authorization layer. Wrap `AllocationEngine`
  and `solve_rebalance` behind whatever service layer the deployment needs.
- **Agent interface contracts with real latency/failure semantics.**
  `civicworkos.market.contracts.MarketTimeoutError` exists as an extension
  point, but no real agent, timeout budget, or retry policy is implemented.
- **Persistent storage.** `CapabilityLedger` and `EvidentiaryRecordStore`
  are in-process, in-memory. A real deployment needs a real database for
  the ledger's time series and a real append-only/content-addressed store
  (e.g. an object store with hash-addressed keys) for the audit trail.
- **A real rule engine / DSL** if non-engineers must author policy rules.
  `PolicyRule` currently wraps arbitrary Python callables.
- **Signature verification on governance-artifact configs.** YAML files
  under `configs/weights/` and `configs/domains/` are loaded as plain
  files; nothing verifies they were actually authorized by "the panel."
- **Cross-validation of self-reported signals** (`Q`, `Tr`) against
  independent outcomes — the paper names this requirement (§8.1) and states
  it does NOT design it either. See [SECURITY.md](../SECURITY.md).
- **Cold-start handling** for the trailing-12-month normalization windows
  (not implemented at all — see `docs/architecture.md`) and for
  `Lambda_k`'s pro-rated trajectory at a domain's first budget period.
- **Infeasibility policy** for Eq. 16 at rebalance (e.g. if Eq. 11's access
  constraint has no eligible supply — report §20.4). `solve_rebalance`
  currently returns an empty result with `status != "Optimal"`; a real
  deployment needs an operational response to that state.
- **Robot fleet middleware enforcing ISO 10218-1:2025.** Explicitly outside
  this repository's scope BY DESIGN (the paper places it outside the
  allocation path so a policy bug cannot defeat a hardware interlock) — a
  real deployment must supply this middleware independently.

## Monitoring (report §18.3's recommendation, not built here)

If deploying for real, instrument at minimum:

- Z4-routing rate per domain (degeneration into Human-First — Paper §7.2's
  own named failure mode)
- Admissibility-rejection reason histogram (which Eq. 18 clause is binding)
- `lambda_k` trajectory and volatility (retirement-wave oscillation, P7)
- `Pi_{k,g}` drift vs. `theta_{k,g}` (access constraint inert or violated, P8)
- Rule staleness per policy rule (`PolicyRule.effective_date` age)

`AllocationEngine.policy_compliance_log` is a starting point for this: it
receives every `Outcome` event via the feedback bus and can be tailed by a
real monitoring pipeline.

## What this repository explicitly does not scale to

No problem-size envelope is given by the paper (report §8.1), and this
repository does not invent one. `civicworkos.solver.rebalance` bounds MIP
solve time via a configurable timeout rather than assume any city's real
task volume is tractable — see
[troubleshooting.md](troubleshooting.md#slow-or-hanging-mip-solves).
