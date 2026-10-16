# Contributing to CivicWorkOS

This repository is an author reference implementation of the research
paper's formalism (see [README.md](README.md) and
[docs/paper_implementation_mapping.md](docs/paper_implementation_mapping.md)).
Contributions are welcome, with one rule that overrides normal software
practice: **fidelity to the source paper is a correctness requirement, not a
style preference.**

## Before you contribute

1. Read [docs/assumptions.md](docs/assumptions.md). If your change touches
   an equation, constraint, or algorithm from the paper, check whether it is
   already documented there as [PAPER] (directly specified), [INFER]
   (reasonable engineering inference), or an outright invention this
   repository made to fill a gap.
2. Run the ground-truth check before and after your change:
   ```
   python scripts/verify_worked_example.py
   ```
   Every number it prints must still reproduce the paper's sec:worked worked
   example and sec:cadmodel / fig:cad-trend analytic model. A change that breaks this
   check is a regression regardless of what else it improves.

## How this repository cites the article

Docstrings and documentation refer to the manuscript by its **LaTeX label** --
`sec:worked`, `eq:cad`, `tab:cadparams`, `fig:cad-trend`, `prop:intake` -- and
never by section or equation number. Labels are stable across revisions;
numbers are not. The repository twice ended up documenting a paper that no
longer existed because section and equation numbers had moved underneath it, so
numbered citations are now treated as a defect. Every label cited here resolves
in `Paper/Frontiers/CivicWorkOS.tex`, and `Paper/Frontiers/check.sh` fails the
build if one does not.

References to **"the pre-release audit"** mean an internal review of this
implementation against the manuscript, conducted before release. It is not
distributed with the repository, so it is cited by name rather than by section
number; the design rationale it prompted is recorded inline where it applies and
in `docs/assumptions.md`.

## Rules for equation-level code

- **Do not silently change the form of an equation** (every numbered equation in
  `src/civicworkos/`) to make it easier to implement. If the paper's form is
  genuinely ambiguous or broken (see `docs/assumptions.md` for the ones
  already found), document the discrepancy and the fix in the same PR, in
  both the code docstring and `docs/assumptions.md`.
- **Label every invention.** If you add a computation the paper does not
  specify (an estimator, a default parameter, a linearization), mark it
  `[INVENTED]` or `[REC]` in the docstring, in the same style as
  `civicworkos.market.agents` or `civicworkos.constraints.resilience`. Never
  let an invented default read as if it came from the paper.
- **Keep the two normalization regimes separate** (`civicworkos.scoring`):
  windowed vs. absolute-anchor normalization must not be merged into one code
  path — this is a documented, paper-mandated separation, not an accident of
  the current implementation.

## Tests

- Any change to `civicworkos.scoring`, `civicworkos.constraints.hcpb`, or
  `civicworkos.analytic` must keep `tests/smoke/test_worked_example.py`
  green.
- New behavior needs a unit test; new cross-module wiring needs an
  integration test. See `tests/unit/test_admissibility.py` for the style
  expected of anything touching eq:admis — both feasibility-restoration
  branches must stay explicitly exercised.
- Run the full suite before opening a PR:
  ```
  pytest tests/ -v
  ruff check src/ sim/ scripts/ tests/
  mypy src/civicworkos
  ```

## Scope discipline

This is a research reference implementation, not a production system. Please
do not add:
- A database, message broker, or web framework the paper does not require
  (see `docs/architecture.md` for what is and isn't justified).
- A machine-learning model. The paper contains exactly one optional,
  unspecified learned surrogate (sec:weights) and nothing else is trained —
  see `docs/training.md`.
- Fabricated experimental results. `civicworkos.sim` runs on synthetic,
  clearly-labeled demo data; it must never be extended to imply it
  reproduces the paper's (nonexistent) evaluation study.

## Commit / PR style

- Reference the specific paper section or equation your change touches
  (e.g. "eq:access", "sec:online") in the PR description.
- If you change a governance-artifact config under `configs/weights/` or
  `configs/domains/`, bump its `version` and `effective_date` fields rather
  than editing in place — these are modeled as signed policy acts
  (Paper sec:feedback), not code constants.
