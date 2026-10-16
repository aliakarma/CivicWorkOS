# Phase 9 status log

Times are local (AST). This log is append-only.

## Scope decision (2026-10-08 00:30)

Phase 9 has two halves. Neither can be "completed" by software alone, and the reasons differ.

| Half | What it needs | Can it run unattended? |
|---|---|---|
| **9a** Execute the elicitation protocol (App. S4) | ~12 real raters, institutional ethics approval, informed consent | **No.** The data are human judgments. Generating them would reproduce defect C1. |
| **9b** Conduct the specified study | Route B (10-14 weeks of engineering), OSF lodgement *before* execution | **No, and not wanted.** Route A was recorded 2026-10-07. Running it would make "the protocol has not been executed" false in the DAS, the README and App. S2. |

Everything in 9a that does **not** need a human was built here, so that the day
ratings exist the whole comparison is one command. No ratings exist. Nothing in
this directory is a result.

There is no long-running compute in this phase (the largest job is a 2,000-rep
bootstrap of a 4x8 linear programme, seconds). The hourly-check mechanism was
therefore not needed; progress is logged below instead.

## Log

- 00:30 Scope decision recorded. Starting the build.
- 00:38 Built and verified: `icc.py` (ICC(2,k), matches the six-target, four-judge example in Shrout & Fleiss 1979: .29 / .62), `model.py` (re-solves the worked example; reproduces the baseline and 18 printed rows of `tab:sensitivity`), `analyze.py` (pipeline with provenance, ethics and synthetic guards). 48 tests pass. Four mutations (drop ethics guard, drop synthetic guard, break ICC(2,k), drop safety floor) were each caught by a test.
- 00:38 LaTeX fragments compile; a synthetic fragment deliberately errors the build (checked, pdflatex exit 1).
- 00:42 Gates added to check.sh (3, each injection-tested); check.sh = 40 passed / 2 failed (C7, N6 only). audit 199 PASS, verify 82/82, pytest 196, check_repo 3/3: no regression. Programme note written. Work staged, not committed. Nothing is running; nothing left to monitor.
