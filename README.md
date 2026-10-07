# CivicWorkOS

**A Capability-Preserving, Policy-Aware Multi-Agent Framework for Human–AI–Robot Work Allocation and Distributional Accountability in the AI City**

Author reference implementation of the theoretical framework by Toqeer Ali Syed, Ali Akarma, Raghda M. Alqurashi, Muhammad Tayyab Naqash, and Abdulaziz Alqurashi (*Frontiers*, Hypothesis and Theory).

[![CI](https://img.shields.io/badge/CI-passing-brightgreen)](.github/workflows/ci.yml)
[![Python 3.10 | 3.11 | 3.12](https://img.shields.io/badge/Python-3.10%20%7C%203.11%20%7C%203.12-blue)](pyproject.toml)
[![Tests](https://img.shields.io/badge/Tests-196%20passed-success)](tests/)
[![Type Checking: mypy](https://img.shields.io/badge/Type%20Checking-mypy%20clean-blue)](pyproject.toml)
[![Linting: ruff](https://img.shields.io/badge/Linting-ruff-black)](pyproject.toml)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](LICENSE)
[![Article: Frontiers](https://img.shields.io/badge/Frontiers-Hypothesis%20%26%20Theory-red)](CITATION.cff)

> [!IMPORTANT]
> **Author-provided reference implementation.** This repository is maintained by **Ali Akarma**, a co-author of the manuscript, to translate the theoretical mathematics, the mixed-integer programming (MIP) formulation, and the online Lagrangian allocation rule of *CivicWorkOS* into an executable, independently verifiable research software package.
>
> As stated in the manuscript's Data Availability Statement, this *Hypothesis and Theory* article presents a normative theoretical architecture and reports **no dataset and no measured empirical result**. This repository recomputes every checkable number the article publishes — the worked bridge-inspection allocation of sec:worked and the per-component debt trajectory of sec:cadmodel / fig:cad-trend — and reports the agreement explicitly, check by check, in [Verification Against the Published Worked Example](#verification-against-the-published-worked-example). Every manuscript value used in those checks is imported from a single definition, never restated here.
>
> Everything under [`sim/`](sim/) runs on **clearly labelled synthetic demonstration data**. It exercises the protocol's software shape and must never be cited as empirical municipal validation. See [docs/reproducibility.md](docs/reproducibility.md).
>
> **The evaluation protocol specified in the article has not been executed.** The article specifies it in full — six sectors, a ten-year horizon, thirty paired seeds, six strategies, and ten hypotheses with refutation criteria — so that the evaluation is fixed in advance and auditable. No outcome of it is reported anywhere, in the article or here. The article's evidence is the worked bridge-inspection allocation, its sensitivity frontier, its two parameter shocks, and the debt trajectory, all of which are exact arithmetic reproducible from the published values. The article cites this repository for that reproduction and for nothing else.

---

## Table of Contents

- [Overview](#overview)
  - [The Municipal Allocation Problem](#the-municipal-allocation-problem)
  - [Seven Execution Modes](#seven-execution-modes)
  - [Four Adaptive Oversight Zones](#four-adaptive-oversight-zones)
- [Mathematical Model](#mathematical-model)
  - [Task Encoding and Developmental Content](#task-encoding-and-developmental-content)
  - [Civic Automation Debt](#civic-automation-debt)
  - [Sustainable Civic Value](#sustainable-civic-value)
  - [Governance Constraints](#governance-constraints)
  - [Online Allocation Rule](#online-allocation-rule)
- [Verification Against the Published Worked Example](#verification-against-the-published-worked-example)
- [Installation](#installation)
  - [Prerequisites](#prerequisites)
  - [Linux and macOS](#linux-and-macos)
  - [Windows](#windows)
  - [Installation Options](#installation-options)
  - [Docker](#docker)
- [Quick Start](#quick-start)
- [Python API](#python-api)
- [Governance Configuration](#governance-configuration)
  - [Declarative YAML Artifacts](#declarative-yaml-artifacts)
  - [The UNSET Sentinel](#the-unset-sentinel)
  - [Environment Variables](#environment-variables)
- [Simulation Testbed](#simulation-testbed)
  - [Dispatch Strategies](#dispatch-strategies)
  - [Multi-Seed Results](#multi-seed-results)
  - [Stress Scenario Catalogue](#stress-scenario-catalogue)
- [Quality Assurance](#quality-assurance)
  - [Verification Gates](#verification-gates)
  - [Test Suite](#test-suite)
  - [Continuous Integration](#continuous-integration)
  - [Developer Shortcuts](#developer-shortcuts)
- [Repository Structure](#repository-structure)
- [Documentation](#documentation)
- [Scope and Limitations](#scope-and-limitations)
  - [Software Reproducibility versus Scientific Reproduction](#software-reproducibility-versus-scientific-reproduction)
  - [Engineering Assumptions](#engineering-assumptions)
  - [Manuscript and Implementation Divergences](#manuscript-and-implementation-divergences)
- [Troubleshooting](#troubleshooting)
- [Citation](#citation)
- [Contributing](#contributing)
- [License](#license)

---

## Overview

### The Municipal Allocation Problem

Cities are moving from passive sensing-and-analytics infrastructure toward autonomous, multi-agent municipal operations. Routine decisions — structural bridge inspection, wastewater monitoring, citizen casework, transit dispatch, emergency logistics — create trade-offs across stakeholder groups that current automation paradigms do not price. Those paradigms optimise narrowly for short-term operating expenditure or throughput, leaving unpriced the long-term erosion of qualified human expertise, public accountability, and emergency fallback capacity.

**CivicWorkOS** formalises a municipal operating-system layer that decides, per task, whether work is allocated to a human, an AI agent, a field robot, or a hybrid team. Two design commitments distinguish it:

1. **Future civic capability is priced in the objective.** The capability consumed by each automation decision enters the score as a weighted quantity, not as an externality.
2. **The admissible dispatch space is hard-constrained.** Capability, equity, transition, and resilience constraints bound what the optimiser may choose at all, rather than appearing as penalties it can buy its way past.

### Seven Execution Modes

Every candidate task $i$ is evaluated across the seven execution modes of eq:modeset, enumerated in [`civicworkos.MODES`](src/civicworkos/__init__.py):

$$\mathcal{M} = \lbrace H,\; A,\; R,\; H{+}A,\; H{+}R,\; A{+}R,\; H{+}A{+}R \rbrace$$

Each mode carries a **human developmental share** $\phi_m \in [0,1]$ (eq:phi) — the fraction of the task's developmental content that accrues as qualified human practice.

| Mode | Composition | Operational description | $\phi_m$ |
| :--- | :--- | :--- | :---: |
| **`H`** | Human | Traditional qualified human inspection and action | $1.00$ — full qualification practice |
| **`A`** | AI | Fully autonomous algorithmic evaluation | $0.00$ — no human practice |
| **`R`** | Robot | Autonomous field hardware execution | $0.00$ — no human practice |
| **`H+A`** | Human + AI | Algorithmic copilot supporting a licensed human | $0.50$ — partial human practice |
| **`H+R`** | Human + Robot | Human field operator teleoperating or supervising a robot | $0.70$ — field qualification practice |
| **`A+R`** | AI + Robot | Embodied autonomous agent, no human in the loop | $0.00$ — no human practice |
| **`H+A+R`** | Full hybrid | Tripartite team: human oversight, AI analysis, robot execution | $0.30$ — supervisory practice |

> [!NOTE]
> The four pure-mode values are fixed by eq:phi and hard-coded in [`constraints/hcpb.py`](src/civicworkos/constraints/hcpb.py). The three **hybrid** shares are deliberately *not* defaulted inside the fidelity modules: `phi_for_mode()` raises `KeyError` unless a domain configuration supplies them, because the manuscript specifies no elicitation instrument (see [docs/assumptions.md](docs/assumptions.md), A3). The values currently shipped in [`configs/domains/structural_inspection.yaml`](configs/domains/structural_inspection.yaml) differ from this table — see [Manuscript and Implementation Divergences](#manuscript-and-implementation-divergences).

### Four Adaptive Oversight Zones

Tasks are classified into oversight zones by consequence severity, reversibility, and statutory accountability. Zone membership is **continuously re-evaluated** against SCV/CAD evidence, incidents, and appeals — it is not a static risk label assigned once.

| Zone | Designation | Regulatory requirement | Operational mechanism | Code identifier |
| :---: | :--- | :--- | :--- | :--- |
| $Z_1$ | Autonomous Permissible | Full machine autonomy permitted | Lowest-cost admissible mode selected | `Z1_AUTONOMOUS` |
| $Z_2$ | Supervised Operation | Human-in-the-loop or teleoperation required | Machine autonomy requires an active human copilot | `Z2_AUGMENTED` |
| $Z_3$ | Real-Time Escalation | Risk thresholds trigger human intervention | Autonomously drafted modes held pending human review | `Z3_HUMAN_AUTHORITY` |
| $Z_4$ | Human Statutory Fallback | Qualified human sign-off legally required | Machine modes inadmissible; routed to a licensed human at $1.0 \times \ell_i$ | `Z4_HUMAN_RESERVED` |

Two properties are enforced in [`zones/oversight_zones.py`](src/civicworkos/zones/oversight_zones.py) rather than left to caller discipline:

- **Demotion may be automatic.** An upheld-appeal rate above threshold triggers an automatic one-zone demotion toward $Z_4$.
- **Restoration may never be automatic.** Any move toward $Z_1$ requires an `authorizing_panel_decision`; `ZoneRegistry.transition()` raises `ValueError` without one.

$Z_4$ is also the **terminal fallback**: when Algorithm 1's admissible set empties, the task routes to $Z_4$ rather than to a degraded mode. Simulation output reports this as `Z4_human_reserved`.

---

## Mathematical Model

### Task Encoding and Developmental Content

A task is encoded as a nine-dimensional demand vector plus an expected duration (eq:task), implemented as [`TaskProfile`](src/civicworkos/twin/task.py):

$$T_i = \lbrace \mathrm{cog}_i, \mathrm{phy}_i, \mathrm{emp}_i, \mathrm{risk}_i, \mathrm{auth}_i, \mathrm{priv}_i, \mathrm{urg}_i, \mathrm{learn}_i, \mathrm{crit}_i ;\, d_i \rbrace$$

eq:ell performs the framework's central unit conversion, turning a normative judgement about developmental value into a budgetable quantity in hours:

$$\ell_i = \mathrm{learn}_i \cdot d_i \qquad \textsf{[qualified-practice hours]}$$

### Civic Automation Debt

CAD (eq:cad) prices, as one scalar in $[0,1]$, the deferred institutional, legal, and workforce liability a mode creates:

$$\mathrm{CAD}_{i,m} = \alpha D_{\mathrm{skill}} + \beta D_{\mathrm{fall}} + \gamma D_{\mathrm{acct}} + \delta D_{\mathrm{dep}} + \varepsilon D_{\mathrm{trans}}, \qquad \alpha + \beta + \gamma + \delta + \varepsilon = 1$$

| Component | Symbol | Focus | Default weight |
| :--- | :---: | :--- | :---: |
| **Skill erosion** | $D_{\mathrm{skill}}$ | Atrophy of the qualified practitioner pipeline | $\alpha = 0.28$ |
| **Fallback incapacity** | $D_{\mathrm{fall}}$ | Loss of manual capability during power, network, or cyber outages | $\beta = 0.22$ |
| **Accountability dilution** | $D_{\mathrm{acct}}$ | Obfuscation of legal responsibility and evidentiary chains | $\gamma = 0.18$ |
| **Vendor dependency** | $D_{\mathrm{dep}}$ | Proprietary lock-in and municipal infrastructure capture | $\delta = 0.12$ |
| **Labour transition** | $D_{\mathrm{trans}}$ | Worker displacement outpacing natural workforce attrition | $\varepsilon = 0.20$ |

Only $D_{\mathrm{skill}}$ is defined by the manuscript as a computation, $D_{\mathrm{skill}} = 1 - \phi_m$ (eq:phi). The other four are defined in prose only; this repository supplies deterministic, explicitly labelled proxy estimators in [`market/agents.py`](src/civicworkos/market/agents.py) (assumption A1).

### Sustainable Civic Value

The per-task objective (eq:scv) rewards five operational terms and penalises four, placing the single largest weight on Civic Automation Debt:

$$\mathrm{SCV}_{i,m} = w_1 Q + w_2 S + w_3 P + w_4 \mathrm{Eq}_{\mathrm{srv}} + w_5 \mathrm{Tr} - w_6 \mathrm{Cost} - w_7 \mathrm{En} - w_8 \mathrm{Pr} - w_9 \mathrm{CAD}_{i,m}$$

All nine weights sum to $1.0$; `ScoreWeights.__post_init__` rejects any vector that does not.

| Term | Symbol | Construct | Sign | Default weight |
| :---: | :---: | :--- | :---: | :---: |
| $V_1$ | $Q$ | Operational quality | $+$ | $w_1 = 0.15$ |
| $V_2$ | $S$ | Operational safety | $+$ | $w_2 = 0.18$ |
| $V_3$ | $P$ | Public trust | $+$ | $w_3 = 0.14$ |
| $V_4$ | $\mathrm{Eq}_{\mathrm{srv}}$ | Service equity | $+$ | $w_4 = 0.10$ |
| $V_5$ | $\mathrm{Tr}$ | Decision transparency | $+$ | $w_5 = 0.05$ |
| $V_6$ | $\mathrm{Cost}$ | Operating cost | $-$ | $w_6 = 0.08$ |
| $V_7$ | $\mathrm{En}$ | Energy use | $-$ | $w_7 = 0.03$ |
| $V_8$ | $\mathrm{Pr}$ | Privacy risk | $-$ | $w_8 = 0.05$ |
| $V_9$ | $\mathrm{CAD}$ | **Civic Automation Debt** | $-$ | $w_9 = 0.22$ |

At $w_9 = 0.22$, debt mitigation carries the largest single weight in the default governance configuration — more than safety ($0.18$) or quality ($0.15$).

> [!NOTE]
> Normalisation is deliberately **not** uniform. The six operational terms use trailing-window min–max normalisation; the long-horizon terms are anchored absolutely. The two regimes are kept in separately auditable code paths as the manuscript requires, so [`scoring/scv.py`](src/civicworkos/scoring/scv.py) operates on already-normalised $[0,1]$ inputs rather than normalising internally.

### Governance Constraints

Four hard constraints bound the admissible dispatch space.

**1 — Human Capability Preservation Budget (HCPB), eq:hcpb and eq:hcpb-estimator.** An annual floor $B_k$ on qualified human practice hours in capability domain $k$:

$$\sum_{i \in \mathcal{T}_k(\Delta T)} \sum_{m} x_{i,m} \, \ell_i \, \phi_m \;\ge\; B_k(t), \qquad B_k(t) = \max\left( B_k^{\min},\; \eta_k N_k(t) \, r_k(t) \, h_k \right)$$

This bounds a *volume of practice hours*, not a headcount. The dimensional identity $N_k \cdot r_k \cdot h_k = \textsf{people} \times \textsf{period}^{-1} \times \textsf{hours/person} = \textsf{hours/period}$ is asserted in [`capability_budget()`](src/civicworkos/constraints/hcpb.py) and unit-tested.

**2 — Capability Access Constraint, eq:accessshare and eq:access.** eq:hcpb decides *how much* developmental work is protected; eq:access decides *who receives it*:

$$\Pi_{k,g} = \frac{\sum_i \sum_m x_{i,m} \ell_i \phi_m \cdot \mathbb{1}\lbrace \mathrm{assignee}(i,m) \in g \rbrace}{\sum_i \sum_m x_{i,m} \ell_i \phi_m}, \qquad \Pi_{k,g} \ge \theta_{k,g} - \epsilon_k \quad \forall g \in \mathcal{G}$$

$\theta_{k,g}$ is a target the oversight panel publishes — explicitly **not** the incumbent share. Without this constraint, a budget sized from incumbent headcount allocates protected practice in proportion to who already holds the posts, so the mechanism designed to protect workers would instead protect incumbents.

**3 — Just Transition Constraint, eq:justtransition.** Caps displacement per period and floors reskilling provision:

$$\Delta_g(t, t + \Delta T) \le \tau_g \quad \textsf{and} \quad \chi_g \ge \chi^{\min} \qquad \forall g \in \mathcal{G}$$

**4 — Reversibility and Resilience (3R) Reserve, eq:cs and eq:res3r.** The N-1 / N-2 criterion from reliability engineering, applied to a mixed workforce of humans, AI agents, and robots:

$$\mathrm{Res}^{(n)}_s(t) = C_s(t) - \sum_{c \in \mathcal{C}^{(n)}_s(t)} C_{s,c}(t), \qquad \mathrm{Res}^{(n_s)}_s(t) \ge \rho_s = \kappa_s D^{\mathrm{peak}}_s$$

The threshold is measured against **peak demand**, not against the lost component's own capacity — a distinction [`constraints/resilience.py`](src/civicworkos/constraints/resilience.py) flags explicitly as a common error in adaptations of this criterion.

### Online Allocation Rule

Algorithm 1 (eq:aug, eq:admis and eq:argmax) dispatches a single task in real time using the shadow prices published by the most recent city-wide rebalance. The augmented score adds the Lagrangian value of the constraints each mode relieves:

$$\widetilde{\mathrm{SCV}}_{i,m} = \mathrm{SCV}_{i,m} + \lambda_{k(i)} \ell_i \phi_m + \mu_{s(i)} \Delta^{\mathrm{res}}_{s(i)}(m) + \nu_{k(i),g(i,m)} \ell_i \phi_m$$

$$m^{*}_i = \arg\max_{m \, \in \, \mathcal{A}(i,t)} \widetilde{\mathrm{SCV}}_{i,m}$$

The dual $\lambda_k$ is *"literally what one hour of qualified practice in domain $k$ is worth to the city"* — a published, auditable price rather than an internal tuning constant.

Admissibility (eq:admis) is **not** a naive per-constraint filter. Each clause reads: *leave the constraint satisfied, **or** — if it is already violated — do not worsen it and contribute to restoring it.* Testing the constraints as literally written inside a loop over $m$ would remove either every candidate or none, and a city already below threshold would route every task to $Z_4$ — including the robot allocations that would free the human capacity needed to climb back above threshold. Both feasibility-restoration branches are exercised explicitly in [`tests/unit/test_admissibility.py`](tests/unit/test_admissibility.py) so the property cannot regress silently.

The Policy Digital Twin returns the four-valued status of eq:policy — `allow`, `allow_with_oversight`, `restrict`, `prohibit` — and the **most restrictive** status governs when several rules apply to the same task–mode pair.

---

## Verification Against the Published Worked Example

[`scripts/verify_worked_example.py`](scripts/verify_worked_example.py) recomputes every checkable number in sec:worked (the bridge-inspection allocation over 2,100 annual inspections) and sec:cadmodel / fig:cad-trend (the per-component debt trajectory), and exits non-zero if any check fails. It is the repository's ground-truth oracle and the **first gate in CI**.

```bash
python scripts/verify_worked_example.py
```

It prints 82 checks and a one-line verdict. Tolerances are set **per check**, not globally: structural quantities that should be exact are checked at $10^{-6}$, values the article prints to four decimals at $10^{-4}$, and annual aggregates in objective units at $0.05$.

> [!NOTE]
> **Every manuscript input comes from one definition.** The script and the test suite import from [`manuscript_values.py`](manuscript_values.py), which re-exports the constants in `Paper/Frontiers/audit_numbers.py` — the same file that gates the manuscript's own arithmetic. Earlier releases kept a second copy here, the article moved, and the copy did not: the oracle verified `B_k = 2073.6` against a paper that computes `4976.64`, and exited 0 while doing so. There is now exactly one place where a manuscript value is written down.

#### sec:worked — the eight staffed modes (tab:worked-terms)

The unit the article scores is a *staffed mode*: an execution mode paired with a named roster at a declared career stage, written `H+A+R/a1`. The stage is not decoration — it fixes $\psi_a$, the developmental eligibility, and so fixes the credited share $\phi_m\psi_a$ that $D^{skill}$ is defined against.

| Staffed mode | CAD (paper) | CAD (computed) | SCV (paper) | SCV (computed) |
| :--- | ---: | ---: | ---: | ---: |
| `H/a0` | 0.2800 | 0.280000 | 0.2324 | 0.232400 |
| `H/a1` | 0.1400 | 0.140000 | 0.2391 | 0.239100 |
| `H+A/a0` | 0.3816 | 0.381600 | 0.2783 | 0.278348 |
| `H+A/a1` | 0.2766 | 0.276600 | 0.2773 | 0.277348 |
| `H+R/a0` | 0.4260 | 0.426000 | 0.3108 | 0.310780 |
| `H+R/a1` | 0.3280 | 0.328000 | 0.3082 | 0.308240 |
| `H+A+R/a0` | 0.5004 | 0.500400 | 0.3426 | 0.342612 |
| `H+A+R/a1` | 0.4234 | 0.423400 | 0.3355 | 0.335452 |

`H+A+R/a0` is the unconstrained winner at $\mathrm{SCV} = 0.34261$ — and it credits no developmental practice whatsoever, which is the tension the rest of the instance resolves.

#### sec:worked — capability budget and constrained optimum

| Quantity | Paper | Computed | Tolerance |
| :--- | ---: | ---: | ---: |
| $h_k$, qualified-practice hours to competence (eq:hconv) | 1440 h | 1440.000000 | $10^{-6}$ |
| $\Phi_k = n_k \ell_i$, annual developmental content | 16800 h | 16800.000000 | $10^{-6}$ |
| HCPB annual budget $B_k$ (eq:bkworked) | 4976.64 h | 4976.640000 | $10^{-6}$ |
| Required mean credited share | 0.2962 | 0.296229 | $10^{-4}$ |
| $\Phi_k\bar\zeta_k$, roster-guard ceiling (prop:feasibility) | 5880 h | 5880.000000 | $10^{-6}$ |
| Mix share on `H+R/a1` | 0.2830 | 0.282667 | $5\times10^{-4}$ |
| Mix share on `H+A+R/a1` | 0.7170 | 0.717333 | $5\times10^{-4}$ |
| Share on each of the other six modes | 0.0000 | 0.000000 | $10^{-6}$ |
| Constrained mean SCV | 0.327750 | 0.327750 | $10^{-5}$ |
| Hours delivered by 594 tasks on the lead-only roster | 4976.40 h | 4976.400000 | $10^{-6}$ |
| Hours delivered by 595 tasks | 4977.00 h | 4977.000000 | $10^{-6}$ |

The budget straddles an integer boundary: 594 tasks on the lead-only roster fall 0.24 hours short, so the integer optimum is 595.

#### eq:lambdaworked — the capability price, and the ranking reversal

| Quantity | Paper | Computed | Tolerance |
| :--- | ---: | ---: | ---: |
| $\lambda_k$, from the LP dual | 0.045353 | 0.045353 | $10^{-6}$ |
| $\lambda_k$ at the quoted four decimals | 0.0454 | 0.045400 | $10^{-9}$ |
| $\widetilde{\mathrm{SCV}}$(`H+R/a1`) (eq:augworked) | 0.435229 | 0.435229 | $10^{-6}$ |
| $\widetilde{\mathrm{SCV}}$(`H+A+R/a1`) | 0.435229 | 0.435229 | $10^{-6}$ |
| $\widetilde{\mathrm{SCV}}$(`H+A+R/a0`), the unconstrained winner | 0.3426 | 0.342612 | $10^{-4}$ |

The tie between the two active modes is **exact**, not approximate, because $\lambda_k$ is *defined* by it. Both beat the unconstrained winner once practice is priced, which is the mechanism the framework exists to produce. The same dual is recovered independently by the general MIP builder in [`tests/integration/test_rebalance_solver.py`](tests/integration/test_rebalance_solver.py), through a different code path.

#### sec:costs and sec:pipeline — what preservation costs, and the intake requirement

| Quantity | Paper | Computed | Tolerance |
| :--- | ---: | ---: | ---: |
| Unconstrained annual objective | 719.5 | 719.485200 | $0.05$ |
| Constrained annual objective | 688.3 | 688.274387 | $0.05$ |
| Relative cost of preservation | 4.34 % | 4.3379 % | $5\times10^{-5}$ |
| Competent-equivalents formed per year | 3.456 | 3.456000 | $10^{-6}$ |
| Annual attrition in practitioners | 2.88 | 2.880000 | $10^{-9}$ |
| $\bar\phi_k$ at the optimum | 0.5925 | 0.592457 | $5\times10^{-5}$ |
| $\tau_k$, years to competence (eq:tauworked) | 4.05 | 4.050926 | $5\times10^{-3}$ |
| Certification-implied duration $h^{raw}_k/\Theta_k$ | 1.20 | 1.200000 | $10^{-9}$ |
| Dilution factor | 3.38 | 3.375772 | $5\times10^{-3}$ |
| Intake requirement $\hat{n}_k$ (eq:intakeworked) | 14.0 | 14.000000 | $5\times10^{-2}$ |
| $\hat{n}_k$, independent route (trainee hours / $\Theta_k$) | 14.0 | 14.000000 | $10^{-9}$ |
| Naive intake from the certification figure | 4 | 4.147200 | $0.15$ |
| Composition-blind hours to the group | 622 h | 622.080000 | $0.1$ |
| Hours under the access constraint | 1344 h | 1343.692800 | $0.5$ |
| Access multiplier | 2.16$\times$ | 2.160000 | $5\times10^{-3}$ |

The intake result is the article's most citable, and it is reproduced here by two independent routes. Machine-assisted supervised practice dilutes a trainee's qualifying hours, so time to competence stretches from the 1.2 years the certification requirement implies to 4.05 — and a city sizing intake from certification hours provisions **four** trainee posts where **fourteen** are required.

#### sec:cadmodel / fig:cad-trend — the debt trajectory

eq:cadmodel sums over the **five** debt components, each with its own asymptote and time constant:

$$C(t) = \sum_j w_j c_j \left[ (1 - \pi_{j,\infty}) t + \pi_{j,\infty} \tau_j (1 - e^{-t/\tau_j}) \right]$$

Earlier releases of this repository implemented a single-scalar $\pi(t)$, which is $D^{skill}$ and nothing else, and plotted it as though it were CAD. The manuscript now models all five, and `civicworkos.analytic.debt_model` follows it. The parameters come from tab:cadparams, so every plotted point is recoverable by substitution:

| Strategy | Residual slope (paper) | Computed | $C(10)$ (paper) | Computed |
| :--- | ---: | ---: | ---: | ---: |
| Automation-First | 10.00 | 10.000000 | 100.00 | 100.000000 |
| Cost/Performance | 11.44 | 11.440000 | 114.40 | 114.400000 |
| Capability Matching | 8.36 | 8.360000 | 88.54 | 88.544098 |
| Ergonomics-Aware Role Allocation | 7.89 | 7.890000 | 85.02 | 85.018650 |
| Human-First | 2.38 | 2.380000 | 28.96 | 28.956997 |
| **CivicWorkOS** | **1.45** | **1.450000** | **31.51** | **31.510254** |

> [!WARNING]
> **No strategy here bounds total debt, CivicWorkOS included.** Its saturating components contribute a bounded 17.98 index units, 11.34 of that from skill formation — the component the capability budget actually governs. But a linear residual of 1.45 units a year accrues without limit, and 1.08 of those 1.45 units is vendor dependency, which the allocation mechanism does not control at all. The claim a capability budget supports is narrower than earlier presentations of this framework asserted: it converts *skill* debt from unbounded to bounded, and says nothing about the other four components except through weights that competing terms can outvote.
>
> **Human-First accumulates less debt than CivicWorkOS for thirteen years.** The curves cross at $t = 13.23$, both at 36.73 index units, reaching 46.89 against 52.89 by year twenty. This is not an artifact and the article does not bury it: a strategy that keeps humans on everything replenishes fallback, accountability, dependency and transition immediately, while CivicWorkOS is still filling its pipeline over a 4.05-year time constant.
>
> The curve ordering follows analytically from the chosen parameters and is **not evidence**. The article's own caveat: fig:cad-trend *"illustrates what the model implies and establishes nothing about what a city would experience."* Reproducing these numbers verifies this repository's arithmetic against the article, not the framework's empirical validity.

---

## Installation

### Prerequisites

| Requirement | Detail |
| :--- | :--- |
| **Python** | `3.10`, `3.11`, or `3.12` (developed and tested on `3.11.9`) |
| **Operating system** | OS-independent — Linux, macOS, Windows |
| **MIP solver** | None to install. `PuLP` bundles the open-source **COIN-OR Branch and Cut (CBC)** executable for all supported platforms; no commercial licence is required |

Runtime dependencies are minimal and pinned to major versions in [`pyproject.toml`](pyproject.toml): `pydantic>=2,<3`, `PyYAML>=6,<7`, `PuLP>=2.7,<3`. The PuLP ceiling is deliberate: 3.x deprecates the `LpVariable` constructor the solver code uses, and `pytest.ini` promotes `DeprecationWarning` to an error, so an unpinned install fails the suite on collection.

### Linux and macOS

```bash
# 1. Clone the repository
git clone https://github.com/aliakarma/CivicWorkOS.git
cd CivicWorkOS

# 2. Create and activate a clean virtual environment
python3 -m venv .venv
source .venv/bin/activate

# 3. Upgrade the build frontend
pip install --upgrade pip wheel
```

### Windows

```powershell
# 1. Clone the repository
git clone https://github.com/aliakarma/CivicWorkOS.git
cd CivicWorkOS

# 2. Create and activate a clean virtual environment
python -m venv .venv
.venv\Scripts\Activate.ps1
# If activation is blocked, first run:
#   Set-ExecutionPolicy -Scope Process -ExecutionPolicy Bypass

# 3. Upgrade the build frontend
pip install --upgrade pip wheel
```

### Installation Options

**Standard installation** — core library plus the simulation testbed, in editable mode:

```bash
pip install -e . --no-build-isolation
```

**Developer installation** — adds `pytest`, `ruff`, and `mypy`:

```bash
pip install -e ".[dev]" --no-build-isolation
```

**Immediate verification** — confirm the installation reproduces the published ground truth:

```bash
python scripts/verify_worked_example.py
```

A successful run ends with `All worked-example numbers reproduced within tolerance.` and exits `0`.

### Docker

Runs the full verification suite in isolation, with no local Python configuration:

```bash
# Build the image
docker build -t civicworkos .

# Default entrypoint: the ground-truth verification oracle
docker run --rm civicworkos

# Override the entrypoint for any other script
docker run --rm civicworkos python scripts/run_simulation.py 200 42
```

The image is built on `python:3.11-slim` and installs `libgomp1`, the one system library CBC requires on Debian-slim bases.

---

## Quick Start

All command-line utilities run directly from the repository root and insert `src/` onto `sys.path` themselves, so they work before an editable install. Outputs below are **verbatim**.

**1 — Verify the implementation against the published worked example.**

```bash
python scripts/verify_worked_example.py
```

```text
=== tab:worked-terms -- CAD by staffed mode (eq:cad) ===
[PASS] CAD H+A+R/a1: printed=0.423400 computed=0.423400
...
=== sec:binds -- the capability budget (eq:bkworked) ===
[PASS] B_k: printed=4976.640000 computed=4976.640000
...
=== eq:lambdaworked -- the capability price (the LP dual) ===
[PASS] lambda_k from the solver dual: printed=0.045353 computed=0.045353
...
=== sec:pipeline -- the intake requirement (prop:intake) ===
[PASS] tau_k, years to competence (eq:tauworked): printed=4.050000 computed=4.050926
[PASS] intake requirement n_hat_k (eq:intakeworked): printed=14.000000 computed=14.000000
...
=== tab:cadparams / fig:cad-trend -- the debt trajectory ===
[PASS] C(10) -- CivicWorkOS: printed=31.510000 computed=31.510254

All 82 checks reproduce the manuscript's printed values within tolerance.` and exits `0`.

### Docker

Runs the full verification suite in isolation, with no local Python configuration:

```bash
# Build the image
docker build -t civicworkos .

# Default entrypoint: the ground-truth verification oracle
docker run --rm civicworkos

# Override the entrypoint for any other script
docker run --rm civicworkos python scripts/run_simulation.py 200 42
```

The image is built on `python:3.11-slim` and installs `libgomp1`, the one system library CBC requires on Debian-slim bases.

---

## Quick Start

All command-line utilities run directly from the repository root and insert `src/` onto `sys.path` themselves, so they work before an editable install. Outputs below are **verbatim**.

**1 — Verify the implementation against the published worked example.**

```bash
python scripts/verify_worked_example.py
```

```text
=== tab:worked-terms -- CAD by staffed mode (eq:cad) ===
[PASS] CAD H+A+R/a1: printed=0.423400 computed=0.423400
...
=== sec:binds -- the capability budget (eq:bkworked) ===
[PASS] B_k: printed=4976.640000 computed=4976.640000
...
=== eq:lambdaworked -- the capability price (the LP dual) ===
[PASS] lambda_k from the solver dual: printed=0.045353 computed=0.045353
...
=== tab:cadparams / fig:cad-trend -- the debt trajectory ===
[PASS] C(10) -- CivicWorkOS: printed=31.510000 computed=31.510254

All 82 checks reproduce the manuscript's printed values within tolerance.
```

**2 — Execute a single online allocation decision (Algorithm 1).**

```bash
python scripts/run_allocation.py
```

```text
Selected mode: H
Z4 fallback: False
Augmented scores (SCV~) by admissible mode:
{
  "H": 0.3721749999999999,
  "H+A": 0.31792699999999996,
  "H+R": 0.32355549999999994,
  "H+A+R": 0.29456333333333334
}
Evidentiary record hash: <64-character SHA-256 digest>
```

> [!NOTE]
> The evidentiary hash **changes on every run and this is by design.** `EvidentiaryRecord.decided_at` defaults to the current UTC instant and is part of the hashed payload, so the digest binds a decision to the moment it was made. The allocation itself is fully deterministic: the selected mode and every $\widetilde{\mathrm{SCV}}$ score reproduce exactly. To obtain a stable digest, pass an explicit `decided_at`.

**3 — Solve the city-wide periodic MIP program (eq:program).**

```bash
python scripts/run_rebalance.py 12
```

```text
Status: Optimal
Objective value: 4.0897
Dual lambda_k[structural_inspection]: 0.024958
Dual extraction method: LP relaxation shadow price (constraint.pi), sign normalized to the paper's non-negative dual convention (eq:aug: lambda,mu,nu >= 0)
Mode counts: {'H': 3, 'H+A': 0, 'H+R': 8, 'H+A+R': 1}
```

The task count is an optional positional argument (default `12`). A reduced count is used deliberately: at the worked example's full 2,100-inspection population the MIP exhibits combinatorial symmetry across identical candidates.

**4 — Run the multi-strategy simulation benchmark across five seeds.**

```bash
python scripts/run_simulation.py 200 42 --seeds 5
```

Positional arguments are `n_tasks` (default `200`) and the initial `seed` (default `42`); `--seeds N` sweeps `N` consecutive seeds. See [Multi-Seed Results](#multi-seed-results).

**5 — Run a Monte Carlo weight-perturbation sensitivity sweep.**

```bash
python scripts/sensitivity_sweep.py 2000 0.20
```

```text
Baseline (default weights) argmax: H+A+R
Perturbation: +/-20% relative on each weight, renormalized, n=2000
Argmax-flip rate vs. baseline: 0.0000
Mode distribution under perturbation:
  H+A+R      1.0000
```

This addresses the manuscript's own open question — whether the parameter set admits a stable configuration, or whether the argmax is so perturbation-sensitive that panel deliberation would be effectively arbitrary. Under $\pm 20\%$ relative perturbation of all nine weights, the unconstrained argmax over the four sec:worked candidates does not flip. The result characterises those four candidates under this specific perturbation scheme, and nothing broader.

---

## Python API

The script below is self-contained and runnable from the repository root. It loads the ratified governance artifacts from [`configs/`](configs/), configures a statutory sign-off rule, and evaluates one candidate task through `AllocationEngine`.

```python
from datetime import date, datetime, timezone
from pathlib import Path

from civicworkos.audit.evidentiary_record import EvidentiaryRecordStore
from civicworkos.config.loader import load_domain_config, load_weights_config
from civicworkos.constraints.hcpb import HCPBParameters
from civicworkos.constraints.resilience import ReserveState
from civicworkos.feedback.bus import FeedbackBus
from civicworkos.ledger.capability_ledger import CapabilityLedger, LedgerSnapshot
from civicworkos.market.agents import HeuristicMarket
from civicworkos.online.algorithm1 import AllocationEngine, Duals
from civicworkos.policy.digital_twin import PolicyDigitalTwin, requires_licensed_human_rule
from civicworkos.scoring.cad import DebtWeights
from civicworkos.scoring.scv import ScoreWeights
from civicworkos.twin.task import TaskProfile

ROOT = Path(".")

# 1. Load the versioned governance artifacts (never hard-code panel-ratified values)
weights = load_weights_config(ROOT / "configs" / "weights" / "default.yaml")
domain_cfg = load_domain_config(ROOT / "configs" / "domains" / "structural_inspection.yaml")

domain = domain_cfg.domain
service = "structural_inspection_service"

# 2. Define a candidate municipal task (eq:task)
task = TaskProfile(
    task_id="INSPECT-BR-402",
    service=service,
    domain=domain,
    cog=0.55, phy=0.40, emp=0.20, risk=0.30, auth=0.60, priv=0.20, urg=0.40,
    learn=0.60, crit=0.40, duration_hours=6.0,
)

# 3. Register statutory rules in the Policy Digital Twin (eq:policy).
#    This rule prohibits every mode lacking a licensed human,
#    reducing the mode set to M' = {H, H+A, H+R, H+A+R}.
policy_twin = PolicyDigitalTwin()
policy_twin.add_rule(
    requires_licensed_human_rule("signoff", "v1", date(2020, 1, 1), "statutory sign-off requirement")
)

# 4. Initialise per-domain capability state (eq:ledger)
ledger = CapabilityLedger()
ledger.initialize(LedgerSnapshot(domain=domain, H_k=0, A_k=0, R_k=0, F_k=0, E_k=0))

# 5. Assemble the engine with the duals published by the last rebalance (eq:aug)
engine = AllocationEngine(
    policy_twin=policy_twin,
    market=HeuristicMarket(hybrid_phi={domain: domain_cfg.hybrid_phi}),
    ledger=ledger,
    hcpb_params={
        domain: HCPBParameters(
            N_k=domain_cfg.N_k, r_k=domain_cfg.r_k, h_k=domain_cfg.h_k,
            eta_k=domain_cfg.eta_k, B_k_min=domain_cfg.B_k_min,
        )
    },
    reserve_states={
        service: ReserveState(
            component_capacities={
                "ai_inspection_pool": 40.0,
                "drone_fleet_class_a": 25.0,
                "contracted_ndt_vendor": 15.0,
            },
            n_s=1, kappa_s=0.6, peak_demand=50.0,
        )
    },
    access_constraints={},
    worker_groups={domain: domain_cfg.groups},
    score_weights=ScoreWeights.paper_default(),
    debt_weights=DebtWeights.paper_default(),
    duals=Duals(lambda_k={domain: 0.045353}, rebalance_timestamp=datetime.now(timezone.utc)),
    audit_store=EvidentiaryRecordStore(),
    feedback_bus=FeedbackBus(),
    config_version=weights.version,
    authorizing_panel_decision="PANEL-DECISION-2026-014",
)

# 6. Run Algorithm 1 for this task (eq:aug, eq:admis, eq:argmax)
result = engine.allocate(task, t=date.today(), elapsed_days_in_period=180.0)

print(f"Selected mode : {result.selected_mode}")
print(f"Z4 fallback   : {result.is_z4_fallback}")
for mode, score in sorted(result.scv_tilde_by_mode.items(), key=lambda kv: -kv[1]):
    print(f"  SCV~[{mode:<7}] = {score:.6f}")
```

**Output**

```text
Selected mode : H
Z4 fallback   : False
  SCV~[H      ] = 0.372175
  SCV~[H+R    ] = 0.323555
  SCV~[H+A    ] = 0.317927
  SCV~[H+A+R  ] = 0.294563
```

Pure `A`, `R`, and `A+R` are absent from the score table because the statutory rule registered in step 3 prohibits them outright. `result.evidentiary_record` carries the full decision provenance — the candidate set, every rejection with its reason (`safety_floor`, `resilience_clause`, or `capability_clause`), the duals in force, and the configuration version.

> [!TIP]
> Substituting a real estimator for `HeuristicMarket` requires only implementing `civicworkos.market.contracts.MarketProtocol` — a single `query()` method. No other component needs to change.

---

## Governance Configuration

### Declarative YAML Artifacts

Municipal policies and panel ratifications are decoupled from code and maintained as versioned, dated artifacts under [`configs/`](configs/). Each carries `version` and `effective_date` fields and is modelled as a **signed policy act**, not a code constant.

| Artifact | Contents |
| :--- | :--- |
| [`weights/default.yaml`](configs/weights/default.yaml) | Objective weights $w_1 \ldots w_9$ (eq:scv) and debt weights $\alpha \ldots \varepsilon$ (eq:cad) |
| [`domains/structural_inspection.yaml`](configs/domains/structural_inspection.yaml) | HCPB, access, and transition parameters: $N_k$, $r_k$, $h_k$, $\eta_k$, $B_k^{\min}$, $\phi_m$, $\theta_{k,g}$, $\epsilon_k$, $\tau_g$, $\chi^{\min}$ |
| [`services/structural_inspection_service.yaml`](configs/services/structural_inspection_service.yaml) | 3R Reserve parameters: component capacities, $n_s$, $\kappa_s$, $D^{\mathrm{peak}}_s$ |
| [`groups/taxonomy.yaml`](configs/groups/taxonomy.yaml) | Worker group taxonomy — the cross product of occupational class, gender, contract status, and district |
| [`policy/structural_inspection_signoff.yaml`](configs/policy/structural_inspection_signoff.yaml) | Machine-checkable provenance metadata for one statutory rule |
| [`scenarios/stress_scenarios.yaml`](configs/scenarios/stress_scenarios.yaml) | The seven stress scenarios of the evaluation protocol |

> [!IMPORTANT]
> Changing a governance artifact means **bumping its `version` and `effective_date`**, not editing values in place. The evidentiary record binds every allocation decision to the `config_version` that produced it; in-place edits break that chain.

The group taxonomy makes the framework's most consequential distributional limitation visible rather than hiding it: $N_k(t)$ is drawn from municipal workforce records and structurally does not see `contracted` or `platform_mediated` workers, so they are ineligible assignees under eq:accessshare and unprotected by eq:justtransition. The contestability module ([`appeals/contestability.py`](src/civicworkos/appeals/contestability.py)) grants them appeal standing regardless of contract status, which — as the manuscript states plainly — *"does not repair the exclusion but ensures it is at least reportable."*

### The UNSET Sentinel

Parameters not yet ratified by an oversight panel parse to a distinct `UNSET` sentinel rather than silently defaulting to `0.0` or `None`. An unset parameter must be **unbound and flagged for the panel**, never quietly assumed.

The shipped domain configuration demonstrates this with a genuine gap — the manuscript assigns no value to the Just Transition ceiling $\tau_g$ for this domain:

```yaml
# tau_g (Just Transition displacement ceiling, eq:justtransition) is NOT given
# anywhere in the worked example. Left UNSET rather than defaulted.
tau_g:
  men: UNSET
  women: UNSET
```

Any dispatch evaluation that reaches an `UNSET` parameter raises a configuration error or routes the task to $Z_4$ fallback. `DomainConfig.unset_parameters()` enumerates outstanding gaps for panel review.

### Environment Variables

CivicWorkOS requires **no runtime secrets** — it is a library and a set of scripts, not a hosted service, and the framework names no external API, database, or credentialed dependency. [`.env.example`](.env.example) documents the one setting a deployment may wish to override:

| Variable | Default | Purpose |
| :--- | :---: | :--- |
| `CIVICWORKOS_SOLVER_TIME_LIMIT_SECONDS` | `60` | Bounds worst-case wall-clock time for a rebalance solve. eq:program is NP-hard and the framework gives no problem-size guidance |

---

## Simulation Testbed

> [!WARNING]
> The testbed in [`sim/`](sim/) is a **reduced-scope demonstration**, not the manuscript's evaluation study. It is a time-stepped sequential task processor rather than a priority-queue discrete-event engine; it runs over a short synthetic horizon rather than six sectors and ten simulated years; and it computes five of the protocol's thirteen metrics. Its numbers are not comparable to anything the manuscript reports, because the manuscript reports nothing from this study. See [docs/reproducibility.md](docs/reproducibility.md) and [docs/assumptions.md](docs/assumptions.md), A10.

### Dispatch Strategies

Five strategies are compared. All five are configurations of the same objective, differing in which terms and constraints are active:

| Strategy | Objective configuration | Constraints |
| :--- | :--- | :--- |
| `automation_first` | Maximises quality and productivity, preferring automation wherever policy permits; $w_9 = 0$ | Relaxed |
| `cost_performance` | Maximises $(Q, P)$ net of Cost and Energy only | Relaxed |
| `human_first` | Restricts $m$ to modes containing $H$ whenever available | Relaxed |
| `capability_matching` | Task–agent fit criterion from prior human–robot collaboration work; SCV with $w_9$ renormalised to zero | Relaxed |
| **`civicworkos`** | Full objective with active duals ($\lambda_k = 0.0454$) | **All of eq:program, plus $Z_1$–$Z_4$ enforcement** |

Only `civicworkos` is evaluated through the constrained `AllocationEngine`; the other four are unconstrained argmax over a strategy-specific score.

> [!NOTE]
> Because all five baselines are ablations of the authors' own objective, this comparison can show that the mechanism does what it was designed to do — it cannot show that it outperforms an independently designed alternative. The manuscript concedes this directly, calling the result *"a tautology about the objective, not a discovery about cities."*

### Multi-Seed Results

Five seeds (42–46), 200 synthetic tasks per seed, 1,000 tasks total, structural inspection service:

| Strategy | Productivity index | Operating cost index | Accumulated CAD | Capability formation index | $Z_4$ rate |
| :--- | :---: | :---: | :---: | :---: | :---: |
| `automation_first` | $67.52 \pm 0.02$ | $53.33 \pm 0.00$ | $79.45 \pm 0.06$ | $0.2217 \pm 0.0060$ | $0.000 \pm 0.000$ |
| `cost_performance` | $67.52 \pm 0.02$ | $53.33 \pm 0.00$ | $79.45 \pm 0.06$ | $0.2217 \pm 0.0060$ | $0.000 \pm 0.000$ |
| `human_first` | $29.90 \pm 0.09$ | $85.00 \pm 0.00$ | $0.00 \pm 0.00$ | $0.4030 \pm 0.0110$ | $0.000 \pm 0.000$ |
| `capability_matching` | $66.84 \pm 0.15$ | $54.05 \pm 0.16$ | $77.48 \pm 0.43$ | $0.2260 \pm 0.0057$ | $0.000 \pm 0.000$ |
| **`civicworkos`** | $29.95 \pm 0.12$ | $84.91 \pm 0.08$ | $\mathbf{0.17 \pm 0.13}$ | $\mathbf{0.4026 \pm 0.0107}$ | $0.287 \pm 0.015$ |

**Aggregate mode selection across all 1,000 tasks**

| Strategy | Mode distribution |
| :--- | :--- |
| `automation_first` | `H+A+R`: 1,000 |
| `cost_performance` | `H+A+R`: 1,000 |
| `human_first` | `H`: 1,000 |
| `capability_matching` | `H+A+R`: 922, `H+R`: 78 |
| `civicworkos` | `H`: 710, `H+R`: 3, `Z4_human_reserved`: 287 |

Productivity and operating-cost indices are normalised per *allocated* task, excluding $Z_4$ fallbacks, so the comparison is not skewed by routing volume. The qualitative pattern is that CivicWorkOS diverts statutory tasks to the $Z_4$ human reserve, sustaining capability formation at $0.4026$ — comparable to `human_first` — while accumulating near-zero debt, against $79.45$ for the automation-maximising baselines.

### Stress Scenario Catalogue

[`configs/scenarios/stress_scenarios.yaml`](configs/scenarios/stress_scenarios.yaml) reproduces the protocol's seven stress scenarios as a **design artifact**. [`sim/stress/`](sim/stress/) implements the scenario injectors; the scenarios are not wired into the demonstration loop above.

| # | Scenario | Kind | Injection |
| :---: | :--- | :---: | :--- |
| i | `ai_service_outage` | Acute | 100 % of AI-agent capacity removed for 72 h at year 5 |
| ii | `cyberattack_on_fleet_c2` | Acute | 100 % of robot-fleet capacity removed for 168 h; affected classes raised to $Z_3$ |
| iii | `robot_fleet_mechanical_failure` | Acute | 40 % of one fleet class removed for 30 days |
| iv | `emergency_demand_surge` | Acute | Arrival rate $\times 3$ for 14 days in emergency logistics and facilities |
| v | `retirement_wave` | Chronic | $r_k$ raised to 0.25 for two consecutive budget periods |
| vi | `rapid_ai_capability_improvement` | Chronic | AI quality and trust raised 20 % over three years |
| vii | `new_municipal_regulation` | Chronic | A new `prohibit` rule added at year 6 without redeploying the market |

---

## Quality Assurance

### Verification Gates

Three independent gates, in the order CI runs them:

```bash
# Gate 1 - Ground-truth oracle: recompute every published number
python scripts/verify_worked_example.py

# Gate 2 - Full automated test suite (196 tests, zero warnings)
pytest tests/ -v

# Gate 3 - Static analysis and type safety
ruff check src/ sim/ scripts/ tests/
mypy src/civicworkos
```

Current status on Python 3.11.9:

```text
196 passed in 2.09s
All checks passed!                              (ruff)
Success: no issues found in 36 source files     (mypy)
```

### Test Suite

**196 tests, all passing, zero warnings.**

| Suite | Tests | Coverage |
| :--- | :---: | :--- |
| [`tests/unit/`](tests/unit/) | 135 | SCV scoring, CAD components, HCPB formulation, access and transition constraints, 3R reserve, ledger invariants, policy twin, oversight zones, task twin, market agents, config loader, appeals, analytic debt model |
| [`tests/integration/`](tests/integration/) | 16 | End-to-end Algorithm 1 pipeline, CBC MIP rebalance solver, SHA-256 audit replay |
| [`tests/smoke/`](tests/smoke/) | 45 | CLI execution smoke tests and worked-example replication |

Run a single suite with `pytest tests/unit -v`, or the Make targets in [Developer Shortcuts](#developer-shortcuts).

Two testing policies are worth noting:

- **Deprecation warnings are errors.** [`pytest.ini`](pytest.ini) sets `filterwarnings = error::DeprecationWarning`. All datetime calls are timezone-aware (`datetime.now(timezone.utc)`).
- **Admissibility restoration branches are pinned.** [`tests/unit/test_admissibility.py`](tests/unit/test_admissibility.py) exercises both feasibility-restoration branches of eq:admis explicitly, so the non-naive filter semantics cannot regress into a naive one silently.

### Continuous Integration

[`.github/workflows/ci.yml`](.github/workflows/ci.yml) runs on every push and pull request to `main`, across a **Python 3.10 / 3.11 / 3.12 matrix**, in this order:

1. `ruff check src/ sim/ scripts/ tests/`
2. `mypy src/civicworkos`
3. `python scripts/verify_worked_example.py` — the ground-truth gate
4. `pytest tests/unit -v`
5. `pytest tests/integration -v`
6. `pytest tests/smoke -v`

Placing the ground-truth check ahead of the test suite is deliberate: a change that breaks fidelity to the published worked example is a regression regardless of what else still passes.

### Developer Shortcuts

[`Makefile`](Makefile) wraps the common workflows:

| Target | Action |
| :--- | :--- |
| `make install` / `make install-dev` | Editable install, with or without developer tooling |
| `make verify` | Ground-truth oracle — run first after touching `scoring`, `constraints.hcpb`, or `analytic` |
| `make test` / `test-unit` / `test-integration` / `test-smoke` | Test suites |
| `make lint` / `make format` / `make typecheck` | `ruff check`, `ruff format`, `mypy` |
| `make run-allocation` / `run-rebalance` / `run-simulation` / `sensitivity` | The four demonstration scripts |
| `make docker-build` / `make docker-run` | Container build and verification run |
| `make clean` | Remove caches and build artifacts |

---

## Repository Structure

<details>
<summary><strong>Full directory tree</strong></summary>

```text
CivicWorkOS/
├── src/civicworkos/               # Core library (36 modules, mypy-clean)
│   ├── analytic/                  # Closed-form debt dynamics (eq:cadmodel, fig:cad-trend)
│   ├── appeals/                   # Contestability and appeal windows
│   ├── audit/                     # SHA-256 tamper-evident evidentiary records
│   ├── config/                    # Pydantic schemas, YAML loader, UNSET sentinel
│   ├── constraints/               # HCPB (eq:hcpb and eq:hcpb-estimator), access (eq:accessshare and eq:access), resilience (eq:cs and eq:res3r)
│   ├── feedback/                  # Event bus for runtime outcome telemetry (eq:feedback)
│   ├── ledger/                    # Civic Capability Ledger, L_k(t) (eq:ledger)
│   ├── market/                    # Agent protocol + heuristic estimator backend
│   ├── online/                    # Algorithm 1: augmented Lagrangian allocation (eq:aug, eq:admis and eq:argmax)
│   ├── policy/                    # Policy Digital Twin, four-valued rule status (eq:policy)
│   ├── program/                   # City-wide multi-period MIP formulation (eq:program)
│   ├── scoring/                   # SCV (eq:scv) and CAD (eq:cad)
│   ├── solver/                    # PuLP/CBC integration and dual extraction
│   ├── twin/                      # Urban Task Digital Twin (eq:task and eq:ell)
│   └── zones/                     # Adaptive oversight zones Z1-Z4
├── sim/                           # Discrete-event testbed (synthetic demonstration data)
│   ├── calibration/               # Open-data metadata catalogue, synthetic task generator
│   ├── des/                       # Simulation engine and metric computation
│   ├── strategies/                # Five baseline dispatch strategies
│   └── stress/                    # Stress scenario injectors
├── configs/                       # Versioned declarative governance artifacts
│   ├── domains/                   # Per-domain HCPB, access, transition parameters
│   ├── groups/                    # Protected worker group taxonomy
│   ├── policy/                    # Statutory rule provenance metadata
│   ├── scenarios/                 # Stress scenario definitions
│   ├── services/                  # 3R Reserve parameters per critical service
│   └── weights/                   # Panel-ratified objective and debt weight vectors
├── scripts/                       # Standalone command-line utilities
│   ├── verify_worked_example.py   # Ground-truth oracle (CI gate 1)
│   ├── run_allocation.py          # Single-task online allocation + audit record
│   ├── run_rebalance.py           # City-wide MIP solve and dual price extraction
│   ├── run_simulation.py          # Multi-seed, multi-strategy benchmark
│   └── sensitivity_sweep.py       # Monte Carlo weight perturbation sweep
├── tests/                         # 196 automated tests
│   ├── unit/                      # 125 tests
│   ├── integration/               # 14 tests
│   └── smoke/                     # 25 tests
├── docs/                          # Architecture and operations documentation
├── .github/workflows/ci.yml       # CI: lint, typecheck, ground truth, tests (3.10-3.12)
├── .env.example                   # Optional runtime overrides (no secrets required)
├── pyproject.toml                 # Packaging metadata and tool configuration
├── requirements.txt               # Runtime dependency pins
├── requirements-dev.txt           # Developer dependency pins
├── pytest.ini                     # Pytest configuration (DeprecationWarning as error)
├── Dockerfile                     # Containerised execution environment
├── Makefile                       # Developer automation shortcuts
├── CITATION.cff                   # Machine-readable citation metadata
├── CHANGELOG.md                   # Version history
├── CODE_OF_CONDUCT.md             # Contributor Covenant
├── CONTRIBUTING.md                # Development standards and PR guidelines
├── SECURITY.md                    # Vulnerability reporting policy
└── LICENSE                        # MIT
```

</details>

---

## Documentation

| Document | Contents |
| :--- | :--- |
| [architecture.md](docs/architecture.md) | Architectural decisions, module relationships, and what was deliberately *not* built |
| [assumptions.md](docs/assumptions.md) | The complete A1–A11 catalogue of inventions, inferences, and approximations |
| [reproducibility.md](docs/reproducibility.md) | Reproducibility scorecard, determinism guarantees, and scope boundaries |
| [evaluation.md](docs/evaluation.md) | Benchmark protocols and metric definitions |
| [inference.md](docs/inference.md) | Online inference and dispatch execution paths |
| [training.md](docs/training.md) | Learning boundary and proxy estimators |
| [setup.md](docs/setup.md) | Detailed environment provisioning |
| [deployment.md](docs/deployment.md) | Municipal deployment guidance and security controls |
| [troubleshooting.md](docs/troubleshooting.md) | Solver diagnostics and common failure modes |

---

## Scope and Limitations

### Software Reproducibility versus Scientific Reproduction

The manuscript itself insists on this distinction, and so does this repository. **Software-pipeline reproducibility** — this code runs the same way every time, and its arithmetic matches the published worked example — is a different claim from **scientific result reproduction**, which is not available here because the article reports no measured results.

| Dimension | Scope in the manuscript | Status in this repository |
| :--- | :--- | :--- |
| **Core equations (eq:cad–15)** | Analytical definitions | Implemented and unit-tested in [`src/civicworkos/`](src/civicworkos/) |
| **MIP formulation (eq:program)** | City-wide periodic program | Implemented and solved via CBC in [`solver/`](src/civicworkos/solver/) |
| **Online rule (eq:aug, eq:admis and eq:argmax)** | Lagrangian augmented dispatch | Implemented with active duals in [`online/`](src/civicworkos/online/) |
| **Worked example (sec:worked)** | Analytical worked example | Reproduced within per-check tolerance by [`verify_worked_example.py`](scripts/verify_worked_example.py) |
| **Analytic debt model (sec:cadmodel)** | Closed form, eq:cadmodel | Reproduced exactly for all five fig:cad-trend parameter sets |
| **Evaluation study (sec:protocol)** | Six sectors, ten years, ≥30 seeds, 13 metrics — *not built* | Reduced-scope synthetic demonstration only, in [`sim/`](sim/) |
| **Empirical municipal data** | None collected | None collected here either; source metadata documented only |

The manuscript names seven intended open-data sources and states explicitly that no data from them has been retrieved or analysed. [`sim/calibration/sources.py`](sim/calibration/sources.py) documents them as metadata; it does not retrieve them.

Three parameters on which the entire capability mechanism depends — $\mathrm{learn}_i$, the hybrid $\phi_m$ values, and the real-world value of $h_k$ — have no known open data source and must be elicited from practitioners. **No simulation run, including every run in this repository, can substitute for that elicitation.**

### Engineering Assumptions

Every point at which this repository had to invent, infer, or approximate something the manuscript leaves unspecified is tagged `[INVENTED]` or `[REC]` in the relevant docstring and catalogued in [docs/assumptions.md](docs/assumptions.md). Each entry follows the same structure: *what was missing → what decision was made → why it is reasonable → how to change it later.*

| ID | Gap |
| :---: | :--- |
| **A1** | Debt-component estimators for $D_{\mathrm{fall}}$, $D_{\mathrm{acct}}$, $D_{\mathrm{dep}}$, $D_{\mathrm{trans}}$ — defined in prose, with no computation |
| **A2** | Elicitation instrument for $\mathrm{learn}_i$ |
| **A3** | Elicitation of the three hybrid $\phi_m$ shares |
| **A4** | Policy rule combination and representation language |
| **A5** | Worker group taxonomy is documentation, not a typed loader |
| **A6** | Assignee-group selection, $g(i,m)$ |
| **A7** | Per-task safety floor, $S^{\min}_i$ |
| **A8** | Just Transition Constraint not embedded in the MIP |
| **A9** | Single-driver scope of the analytic debt model (eq:cadmodel) |
| **A10** | Simulation testbed scope reduction |
| **A11** | Licence choice |

A9 is worth surfacing here, because it is the one assumption on this list that has since been **resolved in the manuscript rather than merely documented here.** Earlier drafts modelled debt accumulation with a single driver — the unmet developmental-practice fraction $\pi$ — while labelling its output "accumulated Civic Automation Debt", which eq:cad defines over five components. That single driver is $D^{skill}$ and nothing else. The capability budget drives $\pi_\infty 	o 1$ for skill formation and, through the resilience reserve, for fallback; it does nothing whatsoever for vendor dependency, which is a procurement variable the allocation mechanism does not control. Total CAD therefore should not have saturated the way the one-driver form implied, and this repository carried the discrepancy as a documented caveat rather than silently correcting the article.

eq:cadmodel now models all five components, each with its own asymptote and time constant, and tab:cadparams fixes those parameters for all six strategies so that fig:cad-trend is reproducible by substitution. `civicworkos.analytic.debt_model` implements that form. The consequence is reported above and is unfavourable to the framework: CivicWorkOS does not bound total debt, and Human-First accumulates less of it for the first thirteen years.

### Manuscript and Implementation Divergences

The tables in this README follow the **manuscript** as the authoritative source. Three points are recorded here where the current contents of `src/` and `configs/` differ, so each can be reconciled deliberately on whichever side proves to be in error:

| # | Item | This README (manuscript) | Current repository contents |
| :---: | :--- | :--- | :--- |
| 1 | Hybrid developmental shares $\phi_m$ | $\phi_{H+A} = 0.50$, $\phi_{H+R} = 0.70$, $\phi_{H+A+R} = 0.30$ | `configs/domains/structural_inspection.yaml` and `market.agents._DEFAULT_HYBRID_PHI` ship $0.75 / 0.70 / 0.55$ |
| 2 | SCV term glosses | $V_3 = P$ is public trust; $V_5 = \mathrm{Tr}$ is decision transparency | `ScoreWeights` names the fields `w3_productivity` and `w5_trust`; `TermVector` documents `P` as productivity and `Tr` as agent trust |
| 3 | Oversight zone designations | Autonomous Permissible, Supervised Operation, Real-Time Escalation, Human Statutory Fallback | `zones.Zone` names the members `Z1_AUTONOMOUS`, `Z2_AUGMENTED`, `Z3_HUMAN_AUTHORITY`, `Z4_HUMAN_RESERVED` |

Divergence 1 is numerically consequential: $\phi_m$ enters eq:phi ($D_{\mathrm{skill}} = 1 - \phi_m$), eq:hcpb (the HCPB left-hand side), and eq:aug (the augmented score), so it propagates into CAD, the capability budget, and the dispatch decision. Divergences 2 and 3 are nomenclature and do not change any computed value.

---

## Troubleshooting

<details>
<summary><strong><code>error: invalid command 'bdist_wheel'</code> during installation</strong></summary>

Install `wheel` into the active environment before installing the package:

```bash
pip install wheel
pip install -e . --no-build-isolation
```

</details>

<details>
<summary><strong>Slow or hanging MIP rebalance solves</strong></summary>

Solving eq:program over hundreds of *identical* task candidates makes CBC explore a combinatorially symmetric search space. `civicworkos.solver.rebalance` therefore applies a bounded default time limit of 60 seconds, configurable via `CIVICWORKOS_SOLVER_TIME_LIMIT_SECONDS`.

For production-scale instances, pass a commercial solver:

```python
from civicworkos.solver.rebalance import solve_rebalance
solve_rebalance(..., solver=your_configured_solver)
```

A large, highly symmetric instance interrupted before CBC proves optimality may return a different — but still feasible — integer solution across runs. See [docs/troubleshooting.md](docs/troubleshooting.md#slow-or-hanging-mip-solves).

</details>

<details>
<summary><strong>PowerShell blocks virtual environment activation</strong></summary>

If `Activate.ps1 cannot be loaded` appears, relax the execution policy for the current process only:

```powershell
Set-ExecutionPolicy -Scope Process -ExecutionPolicy Bypass
.venv\Scripts\Activate.ps1
```

</details>

<details>
<summary><strong><code>AllocationEngine.allocate()</code> always routes to Z4</strong></summary>

This is usually correct behaviour rather than a defect. Either filtering stage of eq:admis may legitimately empty the candidate set: a high-risk, high-criticality task raises `default_safety_floor()` above every mode's safety estimate, and a service already below its 3R threshold rejects modes that would worsen the reserve. Check `result.evidentiary_record` — every rejection is recorded with its reason (`safety_floor`, `resilience_clause`, or `capability_clause`).

</details>

<details>
<summary><strong>The evidentiary record hash differs between runs</strong></summary>

Expected. `EvidentiaryRecord.decided_at` defaults to the current UTC instant and is part of the hashed payload, binding a decision to the moment it was made. Pass an explicit `decided_at` for a stable digest. The allocation decision itself is fully deterministic.

</details>

Further diagnostics — CBC executable errors, Docker daemon failures, config validation — are in [docs/troubleshooting.md](docs/troubleshooting.md).

---

## Citation

If you use this reference implementation or the theoretical framework, please cite **both** the software and the source manuscript.

### Article

> Toqeer Ali Syed, Ali Akarma, Shahid Kamal, Salman Jan, Ahmad B. Alkhodre, and Arshad Jamal. **CivicWorkOS: A Capability-Preserving, Policy-Aware Multi-Agent Framework for Human-AI-Robot Work Allocation and Distributional Accountability in the AI City.** *Frontiers* (Hypothesis and Theory article). Submitted to the Research Topic *"Robots at Work: Who Wins, Who Loses in the AI City."*

### BibTeX

```bibtex
@article{syed2026civicworkos,
  title   = {CivicWorkOS: A Capability-Preserving, Policy-Aware Multi-Agent Framework
             for Human-AI-Robot Work Allocation and Distributional Accountability
             in the AI City},
  author  = {Syed, Toqeer Ali and Akarma, Ali and Kamal, Shahid and Jan, Salman
             and Alkhodre, Ahmad B. and Jamal, Arshad},
  journal = {Frontiers in Robotics and AI},
  note    = {Hypothesis and Theory article. Research Topic: Robots at Work:
             Who Wins, Who Loses in the AI City.
             Corresponding author: Shahid Kamal (shahid.kamal@mmu.edu.my)},
  year    = {2026}
}
```

Machine-readable software citation metadata is in [CITATION.cff](CITATION.cff).

---

## Contributing

Contributions are welcome, subject to one rule that overrides normal software practice: **fidelity to the source manuscript is a correctness requirement, not a style preference.**

1. **Fidelity.** Do not change the form of an equation to make it easier to implement. If the published form is genuinely ambiguous or incorrect, document the discrepancy and the fix in the same pull request — in both the code docstring and [docs/assumptions.md](docs/assumptions.md).
2. **Verification.** Every pull request must pass `pytest tests/ -v`, `ruff check src/ sim/ scripts/ tests/`, and `mypy src/civicworkos`. Run `python scripts/verify_worked_example.py` before *and* after your change; breaking it is a regression regardless of what else improves.
3. **Disclosure.** Label every invention. Any computation the manuscript does not specify must be marked `[INVENTED]` or `[REC]` in its docstring and catalogued in [docs/assumptions.md](docs/assumptions.md). An invented default must never read as though it came from the manuscript.
4. **Governance artifacts.** Changing a file under `configs/weights/` or `configs/domains/` means bumping its `version` and `effective_date`, not editing in place — these are modelled as signed policy acts.
5. **Scope.** This is a research reference implementation. Please do not add a database, message broker, web framework, or machine-learning model that the framework does not require, and never extend `sim/` in a way that implies it reproduces an evaluation study that was never run.

Reference the specific section or equation your change touches (for example, "eq:access", "sec:online") in the pull request description. Full guidelines are in [CONTRIBUTING.md](CONTRIBUTING.md) and [CODE_OF_CONDUCT.md](CODE_OF_CONDUCT.md); security disclosures follow [SECURITY.md](SECURITY.md).

---

## License

Released under the [MIT License](LICENSE).
