# Elicitation (Phase 9a): readiness kit

**Status: not executed. This directory contains no data and no result.**
The protocol in the supplement's elicitation appendix has not been run, and the
article says so. This kit exists so that when real, ethics-approved ratings
exist, the comparison the programme calls for ("estimated, then measured, and
here is the difference") is one command.

| Path | What it is |
|---|---|
| `packet/` | Ethics application draft, information sheet, consent form, recruitment message, rater booklet, item bank, pre-specified analysis plan, data format. Everything bracketed `[LIKE THIS]` needs a person. |
| `icc.py` | ICC(2,k) and ICC(2,1); the 0.75 decision rule. Matches the published Shrout and Fleiss example. |
| `model.py` | Re-solves the worked allocation under alternative inputs. Reproduces the baseline and 18 printed rows of the sensitivity table. |
| `analyze.py` | Ratings CSV in; agreement, intervals, re-solved outcomes and LaTeX fragments out. |
| `tests/` | 48 tests. Run: `python -m pytest elicitation/tests` |
| `PHASE9-STATUS.md` | Append-only progress log. |

## Use, once real ratings exist

    python elicitation/analyze.py ratings.csv --out elicitation/out

The file must declare `# provenance: real` and `# ethics-approval: <reference>`
(see `packet/data-format.md`). Without them the script refuses.

## Guards against reintroducing defect C1

* Synthetic ratings are refused unless `--allow-synthetic`; their outputs are
  prefixed `SYNTHETIC-`, git-ignored, and their LaTeX fragments begin with a
  `\PackageError`, so a build that includes one fails.
* `Paper/Frontiers/check.sh` fails if either manuscript source mentions a
  synthetic output, and fails if the manuscript still says the protocol "has not
  been run" once a real `out/results.json` exists (or the reverse).

## Not done, and why

* **No ratings were collected or simulated for any result.** They require raters and approval.
* **Phase 9b (execute the specified study) was not started.** It is Route B; Route A was recorded 2026-10-07, and running it would falsify the Data Availability Statement, the README and the supplement, which all say the protocol has not been executed.
