# Architecture

This document explains what this repository actually implements. For the
paper's own reference architecture (Fig. 1) and how each node maps to code,
see [paper_implementation_mapping.md](paper_implementation_mapping.md).

## What CivicWorkOS is

A decision layer that sits between a city's work queue and its execution
channels. It does not perform city work; it decides who or what performs it,
prices the deferred liability of that decision, and records the decision for
audit and appeal.

It is **not a machine-learning system**. The entire framework is a weighted
sum (Eq. 2, Eq. 15), a mixed-integer program (Eq. 16), and a Lagrangian
relaxation of that program (Eq. 17-19). The one place the paper mentions a
learned component (an optional AI-quality/trust surrogate, §6.4) has no
specified architecture and is not implemented — see
[training.md](training.md).

## Module layout

```
src/civicworkos/
├── twin/          Task encoding (Eq. 3-4): TaskProfile, ell_i
├── ledger/        Civic Capability Ledger (Eq. 5): per-domain state, group decomposition
├── policy/        Policy Digital Twin (Eq. 6): per-mode rule evaluation, versioning
├── constraints/
│   ├── hcpb.py         Human Capability Preservation Budget (Eq. 7-9)
│   ├── access.py       Capability Access + Just Transition (Eq. 10-12)
│   └── resilience.py   3R Reversibility/Resilience Reserve (Eq. 13-14)
├── scoring/       CAD (Eq. 2) and SCV (Eq. 15) — the pure scoring kernel
├── market/        The 10 market agents: contracts.py (interface) + agents.py ([INVENTED] estimator)
├── online/        Algorithm 1: the online Lagrangian rule + admissibility test (Eq. 17-19)
├── program/       The city-wide allocation program (Eq. 16) as a PuLP model
├── solver/        Rebalancing: MIP solve + LP-relaxation dual extraction
├── zones/         Adaptive Oversight Zones (Table 2)
├── audit/         Evidentiary record + append-only store (Suppl. S1.3)
├── appeals/        Contestability workflow (Suppl. S1.1-S1.4)
├── feedback/      The pub/sub bus (Eq. 20) — the single path both governance services update from
├── analytic/      The closed-form debt model (Eq. 21)
└── config/        Governance-artifact schema + YAML loaders (weights, domains), with the UNSET sentinel
```

`sim/` (repository root, alongside `src/`) is a **separate, reduced-scope**
package: a synthetic-data demo of the paper's evaluation protocol
(§6), not part of the paper-fidelity core. See
[reproducibility.md](reproducibility.md) for why it is kept structurally
separate.

## Two operating regimes

1. **Online per-task path** (`civicworkos.online.AllocationEngine.allocate`):
   for one arriving task, encode → policy-filter every mode → query the
   market → compose CAD/SCV → test admissibility (Eq. 18) → augment with
   published duals (Eq. 17) → argmax (Eq. 19) → execute → emit to the
   feedback bus → write the evidentiary record. O(|M|) = O(7) per task.
2. **Periodic rebalance** (`civicworkos.solver.solve_rebalance`): solve the
   full city-wide program (Eq. 16) as a MIP over a window's task set, then
   solve its LP relaxation to extract fresh dual prices, which the online
   rule consumes until the next rebalance. NP-hard in general (report §8.1);
   this repository bounds worst-case solve time via a configurable timeout
   rather than assume any problem-size envelope, since the paper gives none.

## Why no database, message broker, or web framework

The paper names exactly four technologies: Python, a discrete-event
simulation library, a mixed-integer solver, and "a publish-subscribe bus"
(§6.4, §4.1). Everything else in a typical production checklist — a
database, Kafka/RabbitMQ, a REST API, a frontend — is either **not required**
by the formalism (state fits in-process for a reference implementation) or
**explicitly out of scope** (the paper places robot safety interlocks outside
the allocation path by design). Adding them would be technology for its own
sake, which the task instructions for this repository explicitly warn
against. See [deployment.md](deployment.md) for what a REAL production
deployment would need beyond what this repository provides.

## Two normalization regimes (not yet fully implemented)

Paper §4.3 requires SIX operational SCV terms (`Q, S, P, Cost, En, Pr`) to
use trailing-12-month, sector-specific min-max normalization, and the four
long-horizon terms (anchoring `D_skill`, `D_fall`, `Eq_srv`, `D_trans`) to use
ABSOLUTE anchors that do not decay as a capability pipeline empties out. This
repository's `civicworkos.scoring.sustainable_civic_value()` takes
already-normalized `[0,1]` values and does not implement either normalizer —
see [paper_implementation_mapping.md](paper_implementation_mapping.md) for
why this is flagged as unimplemented rather than approximated.

## Governance artifacts are data, not code

Weights (`configs/weights/*.yaml`) and per-domain parameters
(`configs/domains/*.yaml`) are versioned YAML files validated by
`civicworkos.config`, not Python constants. This mirrors Paper §5.1's
requirement that every allocation trace to "the configuration that
authorized it." An unset `theta_{k,g}` or `tau_g` parses to the `Unset`
sentinel (never a numeric default) so the constraint stays flagged for panel
attention rather than silently assumed.
