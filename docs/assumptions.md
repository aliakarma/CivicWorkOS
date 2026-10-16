# Assumptions

Every point at which this repository had to invent, infer, or approximate
something the source paper leaves unspecified. Referenced from code
docstrings by ID (e.g. "see docs/assumptions.md A7"). Each entry follows:
**what was missing → what decision was made → why it's reasonable → how to
change it later.**

## A1 — Debt-component estimators (`D_fall`, `D_acct`, `D_dep`, `D_trans`)

- **Missing:** The paper defines each in one prose sentence (sec:problem) but gives
  no computation for any of them (only `D_skill = 1 - phi_m` is a formula).
- **Decision:** `civicworkos.market.agents.HeuristicMarket` computes all four
  from a fixed per-mode "archetype" vector, perturbed by the task's demand
  dimensions via simple, documented linear rules.
- **Why reasonable:** It is deterministic, bounded to `[0,1]`, and lets the
  online rule and simulation testbed run end to end without a real elicitation
  pipeline. It makes no claim to resemble any real estimator.
- **How to change:** Implement `civicworkos.market.contracts.MarketProtocol`
  with a real estimator (e.g. backed by a survey instrument or a calibrated
  model) and pass it to `AllocationEngine` in place of `HeuristicMarket`. Do
  not modify `HeuristicMarket` to look more "realistic" — that would invite
  the exact false confidence the pre-release audit warns against ("no one currently
  knows how to produce" these numbers).

## A2 — `learn_i` elicitation

- **Missing:** The paper says `learn_i` comes from "a structured judgment of
  developmental value for a junior practitioner" (sec:layer1) with no instrument,
  rater, scale anchors, or inter-rater agreement target.
- **Decision:** `TaskProfile.learn` is a plain `[0,1]` field with no
  elicitation logic; callers supply it directly (literal tab:worked-terms values in
  the oracle test, `HeuristicMarket`-independent random values in the demo
  generator).
- **Why reasonable:** Building an elicitation instrument would be pure
  invention with no paper basis at all — worse than not building one.
- **How to change:** Municipal Pilot (Phase 11, the pre-release audit) is the paper's own
  stated route: elicit `learn_i` from practising inspectors under
  human-subjects oversight, and record provenance per `[REC]` guidance in
  the report.

## A3 — Hybrid `phi_m` elicitation

- **Missing:** Same problem as A2, for the three hybrid-mode developmental
  shares (`phi_{H+A}, phi_{H+R}, phi_{H+A+R}`).
- **Decision:** `civicworkos.constraints.hcpb.phi_for_mode` requires the
  caller to supply a `hybrid_phi: dict[str, float]` per domain; there is no
  built-in default inside the paper-fidelity modules. `HeuristicMarket` (a
  separately-invented module) does carry an illustrative fallback
  (`_DEFAULT_HYBRID_PHI`, matching the worked example's own values) for demo
  convenience only.
- **Why reasonable:** Keeps the fidelity boundary sharp: `civicworkos.constraints`
  never silently invents a number; `civicworkos.market` (explicitly labeled
  Category C) does.
- **How to change:** Same as A2 — municipal pilot elicitation.

## A4 — Policy rule combination and representation

- **Missing:** The paper describes eq:policy's four-valued output and says rules
  are "machine-checkable predicates" (sec:policytwin) but gives no rule language, and
  no rule for combining multiple applicable rules on the same (task, mode).
- **Decision:** `civicworkos.policy.digital_twin.PolicyRule` wraps an
  arbitrary Python predicate `(task, mode) -> status | None`; when several
  rules apply, `PolicyStatus.most_restrictive` takes the most restrictive of
  the returned statuses (prohibit > restrict > allow-with-oversight > allow).
- **Why reasonable:** A rule base whose purpose is to enforce legal/safety
  floors should never have one rule silently relax another's restriction.
- **How to change:** Replace the Python-predicate rule representation with a
  declarative DSL if the deployment needs non-engineers to author rules
  (the pre-release audit's recommendation); keep the most-restrictive combination
  semantics, which is independent of representation.

## A5 — Worker group taxonomy is documentation, not a typed loader

- **Missing:** Nothing missing in the paper (the four-way taxonomy is stated,
  sec:problem) — this is a scope decision.
- **Decision:** `configs/groups/taxonomy.yaml` documents the taxonomy;
  per-domain group lists (`groups:`) and targets (`theta_kg:`) are configured
  directly in `configs/domains/*.yaml` rather than through a separate typed
  group-taxonomy loader.
- **Why reasonable:** A generic taxonomy loader adds a layer of indirection
  with no behavior this repository currently needs; domain configs are
  already the unit at which access/transition constraints are evaluated.
- **How to change:** If group definitions need to be shared and validated
  across many domain configs, promote `taxonomy.yaml` to a
  `civicworkos.config` Pydantic model and have `DomainConfig.groups`
  validate against it.

## A6 — Assignee-group selection (`assignee(i,m)`, `g(i,m)`)

- **Missing:** eq:accessshare and eq:aug's `nu` term need the group of the human
  performing a task at decision time; the paper never says how the assignee
  within a mode is chosen (the pre-release audit item 4).
- **Decision:** `civicworkos.online.algorithm1.select_assignee_group` is a
  greedy heuristic: assign to whichever configured group is furthest BELOW
  its `theta_{k,g}` target share. The MIP builder
  (`civicworkos.program.city_program`) instead accepts an
  exogenously-supplied `CandidatePair.assignee_group` per (task, mode) pair,
  since assignment-at-solve-time inside the MIP itself would require
  rostering as an additional decision variable the paper does not model.
- **Why reasonable:** The greedy heuristic is the natural policy the access
  constraint's own dual price is meant to incentivize, and is cheap to
  compute online.
- **How to change:** Replace with a real rostering system's output; the
  `assignee_group` field/parameter is the integration point.

## A7 — Safety floor `S^min_i`

- **Missing:** Eq. 16d and eq:admis's first clause use `S^min_i` without
  defining how it is set per task.
- **Decision:** `civicworkos.online.algorithm1.default_safety_floor` scales a
  floor with task risk and criticality
  (`min(0.95, 0.30 + 0.35*risk + 0.25*crit)`), calibrated to sit within
  `HeuristicMarket`'s typical `[0.4, 0.9]` safety-estimate range so that
  moderate-risk demo tasks are neither trivially always-admissible nor
  always routed to Z4.
- **Why reasonable:** It is fully overridable (`safety_floor_fn` parameter on
  `AllocationEngine`) and does not pretend to be paper-derived — every
  integration/unit test that checks a specific numeric outcome either passes
  its own `safety_estimate`/`safety_min` directly (`tests/unit/test_admissibility.py`)
  or explicitly disables this default (`tests/integration/test_algorithm1_pipeline.py`).
- **How to change:** Supply a domain- or jurisdiction-specific
  `safety_floor_fn` reflecting real regulatory minimums.

## A8 — Just Transition Constraint (eq:justtransition) not embedded in the MIP

- **Missing:** `Delta_g` (net displacement) needs a baseline allocation of
  ALL task-hours (not only protected-practice hours) to every worker group,
  which needs an assignee mapping for every mode — not only the `phi_m > 0`
  modes eq:access needs. The paper does not specify this either, and stacking a
  second invented assignee-mapping on top of A6 would compound uncertainty
  inside the solver's own constraints.
- **Decision:** `civicworkos.program.city_program` implements Eq. 16a-b,
  16e (HCPB), 16f (access, linearized per A6), 16h (3R reserve), and 16i
  (resource capacity) as MIP constraints. eq:justtransition / 16g is provided as a
  standalone, POST-HOC checker
  (`civicworkos.constraints.access.JustTransitionConstraint.is_satisfied`)
  a caller applies to a realized allocation, rather than as a solver
  constraint.
- **Why reasonable:** Keeps the MIP's invented assumptions to the minimum
  needed to reproduce the worked example, and keeps the eq:justtransition gap visible
  rather than buried inside solver output nobody would think to question.
- **How to change:** Define an explicit, documented assignee-for-every-mode
  policy and add a linearized `Delta_g(x) <= tau_g` constraint following the
  same pattern as the access constraint.

## A9 — Debt model component scope (eq:cadmodel) — RESOLVED

- **Status:** Closed. This entry is kept because it records a divergence that
  was real for several releases and has now been resolved on the manuscript's
  side rather than worked around on ours.
- **What the divergence was:** Earlier drafts of the article modelled debt
  accumulation with a single driver (`pi`, the unmet fraction of required
  developmental practice) while labelling the output "accumulated Civic
  Automation Debt", which eq:cad defines over five components. That single
  driver is `D_skill` and nothing else. The capability budget drives
  `pi_inf -> 1` for skill formation, and the resilience reserve does the same
  for fallback, but nothing in the framework touches `D_dep`: vendor
  dependency is a procurement variable the allocation mechanism does not
  control. Total CAD should therefore not have saturated the way the
  one-driver form implied.
- **What we did at the time:** `civicworkos.analytic.debt_model` implemented
  the article's own form exactly, with the over-claim documented in the module
  docstring and here, rather than silently generalising it. Silently "fixing"
  a published model produces numbers that no longer match the published
  figure, which defeats the purpose of an oracle and misrepresents what the
  article claims.
- **How it was resolved:** eq:cadmodel now sums over all five components, each
  with its own `pi_j_inf` and `tau_j`, and tab:cadparams fixes those
  parameters for all six strategies so every point of fig:cad-trend is
  recoverable by substitution. `debt_model` implements that form:
  `accumulated_debt` takes a per-component strategy and the debt weights, and
  `residual_slope` / `bounded_ceiling` separate the unbounded part from the
  saturating one.
- **What it cost the framework's claim:** The honest version is narrower. A
  capability budget converts *skill* debt from unbounded to bounded and says
  nothing about the other four components except through weights that
  competing terms can outvote. CivicWorkOS does not bound total debt: 1.45
  index units a year accrue without limit, 1.08 of them vendor dependency. And
  Human-First accumulates less total debt until year 13.23. Both facts are
  now in the article and are asserted by
  `tests/unit/test_analytic_debt_model.py::test_residual_slope_is_zero_only_when_every_component_replenishes`
  and `tests/smoke/test_worked_example.py::test_no_strategy_bounds_total_debt`,
  so neither can quietly regress.

## A10 — Simulation testbed scope reduction

- **Missing:** Nothing missing in specification (sec:protocol is unusually
  complete) — this is a resource/scope decision for a repository built to
  validate the software pipeline, not to run the paper's unbuilt study.
- **Decision:** `civicworkos.sim` (well, `sim/` at the repository root) is a
  time-stepped sequential processor over a configurable, short list of
  SYNTHETIC tasks (`sim.calibration.sources.synthetic_demo_tasks`), not a
  priority-queue discrete-event engine over six sectors and ten years with
  ≥30 seeds. It computes 5 of the paper's 13 metrics.
- **Why reasonable:** Building the full protocol (real calibration data the
  paper itself says does not exist, per Suppl. S4; the full statistical plan,
  which the pre-release audit identifies as internally inconsistent in the paper
  itself) is Phase 10-11 work requiring a municipal partner and
  human-subjects oversight — outside what a repository construction pass can
  or should fabricate.
- **How to change:** See `sim/des/engine.py`'s module docstring for exactly
  which metrics are and are not computed, and extend incrementally; do not
  claim any result from `sim/` reproduces a paper number — see
  `docs/reproducibility.md`.

## A11 — License choice

- **Missing:** The paper's own report notes "License: Not specified."
- **Decision:** MIT, applied to this repository's engineering implementation
  only (see `LICENSE`'s note on scope).
- **Why reasonable:** Permissive default appropriate for a research reference
  implementation with no stated licensing constraint from the source.
- **How to change:** Repository maintainers may relicense; this is a pure
  engineering-judgment default, not a paper-derived requirement.

## A12 — The credited share `phi_m * psi_a` is carried in a single `phi_m` field

- **Missing:** Nothing missing in the article. This is an implementation shape
  that does not match the specification's shape, recorded so the mismatch is
  deliberate rather than discovered later.
- **What the article says:** sec:problem makes the decision variable a *staffed
  mode* — an execution mode paired with a roster at a declared career stage,
  written `H+A+R/a1`. Two derived quantities follow: the developmental
  eligibility `psi_a` (eq:psi), the share of human work performed by
  practitioners still being formed, and the credited developmental share
  `phi_m * psi_a`, which is what `D_skill` is defined against (eq:dskill) and
  what eq:hcpb, eq:aug and eq:admis all accrue.
- **What the code does:** `civicworkos.online.algorithm1` and
  `civicworkos.program.city_program` both multiply by a single `phi_m` field,
  with no separate `psi_a`. Every caller is therefore required to pass the
  *credited* share into that field, and every caller in this repository does;
  the field keeps its historical name.
- **Why this matters more than it looks:** `phi_m` and `phi_m * psi_a` differ by
  a factor of two in the worked example, and they differ by *everything* at the
  competent career stage, where `psi_a = 0` credits nothing however high the
  human share. Passing a bare `phi_m` makes the capability budget look
  satisfiable when it is not, and makes the staffed modes that credit no
  practice — the `a0` rows of tab:worked-terms, including the unconstrained
  winner — appear to contribute to it.
- **Why reasonable for now:** The arithmetic is identical once the credited
  share is what enters the field, and that is what the gates check: the LP in
  `tests/smoke`, the general MIP in `tests/integration/test_rebalance_solver.py`
  and `scripts/verify_worked_example.py` all recover the article's `lambda_k` of
  0.045353 through different code paths.
- **How to change:** Add `psi_a` to `AgentEstimate` and `CandidatePair` as a
  separate field and multiply explicitly, so that the type system carries the
  distinction instead of a naming convention and a comment. The mode-name
  handling is already roster-aware — `PolicyDigitalTwin.status` and
  `task_delta_resilience` both validate the execution-mode family and ignore the
  roster suffix — so a staffed-mode decision variable needs no further
  plumbing there.
