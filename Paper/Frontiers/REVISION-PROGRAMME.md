# CivicWorkOS — Reviewer Response and Revision Programme

**Manuscript:** *CivicWorkOS: Capability-Preserving Allocation of Municipal Work Among Humans, AI Agents and Robots*
**Source of record:** `Paper/Frontiers/CivicWorkOS.tex` (1,739 lines · 21,048 body words · 53 pages · 3 figures · 19 tables)
**Review of record:** `Paper/Frontiers/peer-review.md` (3 reviewers + area chair; verdict **Reject**, resubmit as *Hypothesis and Theory*)
**Target venue:** Frontiers in Artificial Intelligence — **Hypothesis and Theory** (12,000 words, 5–8 keywords)
**Document status:** working programme. Update the status column of §4 as each item closes.

---

## 0. How to use this document

This is a phase-gated programme, not a to-do list. Each phase has:

- a **goal** stated as a condition the manuscript must reach,
- **work items** with the exact file, line region and action,
- **success criteria** written as mechanically checkable gates,
- **effort** (author hours) and **compute** (machine seconds/minutes) estimates.

**Rule: do not start phase *n+1* until every gate in phase *n* passes.** The reason is specific to this manuscript. The defects are not independent — the sign error in the ablation prose has already propagated into three downstream sections, and the length reduction will be wasted work if it is done before the integrity decision determines which sections survive. Fixing in dependency order is what keeps the two-week estimate honest.

Phases 0–8 are the critical path and are sequential. Phase 9 is optional, runs in parallel from the start of Phase 1, and is the single highest-value addition to the paper.

---

## 1. Executive summary

The reviewers converge on one dispositive finding and a cluster of repairable ones.

**The dispositive finding.** Section 8 (Results) reports a thirty-seed, six-sector, ten-year, 803,100-task-per-year simulation with confidence intervals. Three independent statements inside your own project say that study does not exist:

| Source | Statement |
|---|---|
| `CivicWorkOS.tex` line 1335 | "The set below will be lodged on the Open Science Framework **before the simulation is executed**" |
| `CivicWorkOS.tex` line 1720 (Data Availability) | "**No new datasets were created or analyzed** in this study" |
| `README.md` lines 20–22 | "reports **no dataset and no measured empirical result**"; `sim/` is "clearly labelled synthetic demonstration data" that "**must never be cited as empirical municipal validation**" |
| `sim/des/engine.py` lines 1–28 | "a REDUCED-SCOPE stand-in … a TIME-STEPPED sequential task processor, not a priority-queue discrete-event engine … runs over a short demo horizon … computes a SUBSET of the paper's thirteen metrics" |

An editor who clicks the link in your Data Availability Statement reaches this in under a minute. The outcome is desk rejection with an integrity note, and post-publication it is a retraction. **This must be resolved before anything else in the manuscript is touched.**

**The repairable cluster.** Nine numerical defects, of which five sit in prose that reports a table rather than in the table itself; a baseline (ERA/Merlo) scored on twelve metrics that is implemented nowhere; a 21,048-word manuscript against a 12,000-word ceiling; zero keywords; an unfilled funding placeholder; an empty Abbreviations section; no Ethics Statement.

**What survives intact, and it is substantial.** Every piece of arithmetic in Section 6 (the worked bridge-inspection allocation) and in the Section 6.8 sensitivity sweep was independently recomputed by Reviewer 1 and again during the preparation of this document. It is correct to five decimal places. The intake requirement — machine-assisted supervised practice stretches time to competence from 1.2 to 4.05 years, so a city sizing intake from certification hours provisions four trainee posts where fourteen are required — is verified by two independent routes, is independent of the simulation, and is the paper's most citable result. It is currently buried in §6.6 and absent from the Abstract.

**The fix is subtraction, not new science.** All three reviewers say so explicitly. The area chair's estimate is two weeks of focused work for a 65–70% acceptance probability, rising to ~80% with one executed elicitation domain. This programme implements that path, and adds four defects the reviewers did not reach (§5).

---

## 2. The strategic fork — decide this before Phase 1

Everything downstream depends on one choice. Make it explicitly, with co-authors, and record the decision at the top of §4.

### Route A — Hypothesis and Theory restructure *(recommended)*

Delete Section 8 entirely. Reduce Section 7 (Evaluation Protocol) to a short "specified protocol, not executed" subsection inside Discussion/Future Work. Promote the worked example and the sensitivity frontier to carry the whole evidentiary load. Declare the article type as *Hypothesis and Theory*.

- **Time to submission-ready:** ~12 working days.
- **Acceptance probability:** 65–70% (reviewer estimate), 80% with Phase 9a.
- **Why recommended:** it is the article type your own repository already declares; it matches the evidence you actually hold; it solves the integrity problem, a third of the length problem, and the baseline-circularity problem in one move; and it is the only route where the paper's strongest result (the intake requirement) becomes the headline rather than a buried subsection.

### Route B — Conduct the study as specified

Build the six-sector, ten-year, thirty-seed discrete-event testbed; implement the ERA baseline; implement the appeals-generating model; execute the Section 7.5 statistical plan in full; report test statistics, p-values, effect sizes, Shapiro–Wilk outcomes, achieved power and the 60-test Holm–Bonferroni family.

- **Time to submission-ready:** 10–16 weeks (see §6, Phase 9b for the engineering breakdown and the compute model).
- **Honest assessment:** `sim/` is roughly 500 lines of a deliberately reduced-scope stand-in. It has no stress injection wired into the loop, no appeals model, no ERA strategy, no multi-sector calibration, and computes 5 of 13 metrics. The gap to the specified study is a substantial engineering project, not a configuration change.
- **Choose this only if** a co-author can commit 6–10 focused engineering weeks and the paper's value genuinely depends on an empirical claim. It does not — Reviewer 2's judgment is that "the fabricated section is not only wrong, it is unnecessary."

### Route C — Reduced, honestly scoped empirical study

Run what the repository can actually support: single-domain (structural inspection), synthetic-but-labelled, 5 implemented strategies, the subset of metrics the engine computes, with the Section 7.5 statistics applied to it, reported as a software-behaviour demonstration rather than municipal validation.

- **Time:** +3–4 weeks on top of Route A.
- **Use as a fallback** if an editor or co-author insists on an empirical component. It is a legitimate thing to report. It is not a six-sector ten-year evaluation and must never be described as one.

**This programme is written for Route A, with Route B/C deltas marked where they differ.**

---

## 3. Section-numbering map — read this before touching anything

**The reviewers' section numbers are off by one relative to your compiled document.** The review was written against an earlier draft that carried two extra top-level sections. If you navigate by the reviewers' numbers you will edit the wrong section. Verified against `CivicWorkOS.aux`:

| Reviewer says | Your compiled number | Label | `.tex` lines |
|---|---|---|---|
| §7 Worked example | **§6** | `sec:worked` | 950–1196 |
| §7.7 Sensitivity | **§6.8** | `sec:sensitivity` | 1132–1196 |
| §8 Evaluation protocol | **§7** | `sec:expsetup` | 1197–1360 |
| §8.5 Statistical plan | **§7.5** | `sec:statplan` | 1312–1322 |
| §8.8 "before the simulation is executed" | **§7.7** | `sec:predictions` | 1330–1360 |
| §9 Results | **§8** | `sec:results` | 1361–1583 |
| §9.3 Ablations | **§8.4** | `sec:ablation` | 1436–1463 |
| §9.5 Retirement wave | **§8.6** | `sec:retirement` | 1489–1499 |
| §9.6 Distributional | **§8.7** | `sec:distresults` | 1500–1524 |
| §9.7 Computational profile | **§8.8** | `sec:runtime` | 1525–1552 |
| §9.8 Hypothesis outcomes | **§8.9** | `sec:hypoutcomes` | 1553–1583 |
| §10 Discussion | **§9** | `sec:discussion` | 1584–1697 |
| §10.2 Debt trajectory | **§9.1** | `sec:cadmodel` (¶ at 1638–1646) | 1587–1647 |
| §11 Limitations | **§9.5** | `sec:limitations` | 1681–1695 |
| §12 Conclusions | **§10** | `sec:conclusion` | 1698–1710 |

Throughout the rest of this document, **section numbers are your compiled numbers**, with the reviewers' number in brackets where it helps cross-reference the review.

The same drift affects the repository: `README.md` and `scripts/verify_worked_example.py` cite "§5.3 worked example" and "§7.1 / Fig. 3", which is a *third* numbering from a still earlier draft. Phase 3 fixes this.

---

## 4. Master issue register

Every reviewer finding, plus the four this document adds, mapped to a phase. Keep the Status column current — it is the project's single source of truth.

> **Route decision: Route A — Hypothesis and Theory restructure.** Recorded 2026-10-07. This is the route this programme is written for and the one the repository already declares. Section 8 is deleted rather than hedged; Section 7 is dissolved into a specified-but-unexecuted protocol (main text §9.6, full specification in supplement Appendix S2); the worked allocation of §6 and the closed-form debt model of §9.1 carry the evidence.
>
> **Phase 0 closed.** Branch `revision/frontiers-hnt`, tag `pre-revision-frontiers`. Harness: `check.sh` (build, length, front matter, integrity greps, artifact — each gate tagged with the phase that closes it) and `audit_numbers.py` (160 comparisons; 152 PASS, 8 registered defects awaiting Phase 2).
>
> **Phase 1 closed.** All Phase 1 gates green. Main text 21,048 → 19,390 body words, 53 → 46 pages, 19 → 13 tables. Both documents build with zero undefined references.
>
> **Phase 2 closed.** All Phase 2 gates green: `check.sh 2` reports 15 passed / 0 failed, `audit_numbers.py` exits 0 with 187 PASS and 0 FAIL. The register grew from 160 to 189 comparisons. The two remaining KNOWN entries are the pre-deletion records of M4 and M5, whose sites Phase 1 removed with Section 8; they are an audit trail, not outstanding work. The substantive change is M3: Figure 3's coordinates previously had no stated provenance and could not be recovered from any declared parameter set, so Phase 2 adds Table 11 (`tab:cadparams`), which fixes $(c_j, \pi_{j,\infty}, \tau_j)$ for all five CAD components of all six strategies, and replots the figure from it. All 116 plotted coordinates are now checked against Equation (47). Word count rose 19,390 → 19,636, which Phase 4 absorbs.

| ID | Severity | Issue | Location (compiled) | Phase | Status |
|---|---|---|---|---|---|
| **C1** | Critical | §8 reports an unconducted study | §8, lines 1361–1583 | 1 | ☑ Closed. §8 deleted entire (388 lines). `removed_sections.tex` keeps the audit trail. |
| **C2** | Critical | §7.7 says the simulation is unexecuted while §8 reports it | line 1335 vs 1367 | 1 | ☑ Closed. The future-tense statement now governs: §9.6 and App. S2 both say the protocol is unexecuted and that OSF lodgement precedes execution. |
| **C3** | Critical | Abstract's lead numbers (63.2%, 86.8%, 0.97) come from C1 | lines 108–110 | 1 | ☑ Closed. Abstract rebuilt on §6; 63.2/86.8/0.97 gone; leads with the intake result. |
| **C4** | Critical | Data Availability Statement self-contradictory; misdescribes repo; wrong cross-ref | lines 1718–1720 | 1 | ☑ Closed. DAS rewritten; cross-refs corrected to sec:worked/sensitivity/shocks/cadmodel/protocol. |
| **C5** | Critical | 21,048 words against a 12,000 ceiling | whole document | 4 | ☐ |
| **C6** | Critical | No keywords (5–8 required) | preamble | 5 | ☐ |
| **C7** | Critical | Funding/Acknowledgment placeholder `26UQU(Staff number)(track name)xx` | lines 1716, 1728 | 5 | ☐ |
| **C8** | Critical | No Ethics Statement | back matter | 5 | ☐ |
| **C9** | Critical | `\section*{Abbreviations}` present and empty | line 1712 | 5 | ☐ |
| **C10** | Critical | Article type never declared | preamble | 1 | ☑ Closed. Declared in `\extraAuth` and in a preamble header comment. |
| **H1** | High | Access-constraint ablation: sign **and** magnitude wrong in prose | §8.4 line 1460 | 2 | ☑ Closed by removal (§8.4 deleted). |
| **H2** | High | H1 propagated: "at a cost of 1.3 CAD points" | §8.7 line 1521, §8.9 line 1580, §10 line 1705 | 2 | ☑ Closed by removal; the Conclusions sentence now reports the 622→1,344 hour access arithmetic instead. |
| **H3** | High | P8's "CAD ≤ +5" clause vacuous under the real sign | Table `tab:predictions` l.1352, `tab:hypoutcomes` l.1573 | 2 | ☑ Closed by removal; P8 survives only as a specified, untested hypothesis in App. S2.7. |
| **H4** | High | "solve times < 1.5 s" against a tabled 74 s | §8.8 line 1549 | 2 | ☑ Closed by removal (tab:runtime deleted). §4 and §9.5 now state that no solver profile has been measured. |
| **H5** | High | §6.8 robustness claim contradicted by 10 rows of its own table | §6.8 vs `tab:sensitivity` l.1139 | 2 | ☑ Closed. "Survives every feasible value"/"does not depend on the estimates" replaced with the claim the table supports: developmental staffing occurs at every feasible value, but across the **eight** feasible "no reversal" rows the lead-only roster is retained on 1.3–46.1% of tasks and the dual falls to 0.0005–0.0033. (The programme said ten rows; the table has eight.) Range pinned in `audit_numbers.py`. |
| **H6** | High | ERA (Merlo) scored on 12 metrics; absent from `tab:stress`; unimplemented | `tab:mainresults` l.1388, `tab:stress` l.1475, §7.2 l.1231 | 1 | ☑ Closed. ERA removed with §8; retained only as a specified comparator in App. S2.2, with the circularity concession stated there and in §9.6. |
| **H7** | High | Analytic recomputations presented as simulation output | §8.3 l.1432, §8.6 l.1489–1497 | 1 | ☑ Closed. Retirement arithmetic relocated to new §6.9 as exact arithmetic; the "simulated dual 0.0451" sentence deleted. |
| **H8** | High | "Appeals resolved in window: 0.942" with no generative model | `tab:mainresults` l.1398 | 1 | ☑ Closed. 0.942 removed. App. S2.3 now states that no appeals throughput is reportable without a generative model, and names the four components such a model needs. |
| **M1** | Medium | `eq:lambdaworked`: 0.0273/0.6 = 0.04550, printed as 0.0454 (10 sites) | §6.4 + downstream | 2 | ☑ Closed by Option A. The equation now carries 0.308240, 0.335452 and 0.027212, so it reproduces its own quotient, λ_k = 0.045353. The headline 0.0454 is preserved at all 15 sites and stated as λ_k to four decimals. 0.0455 appears nowhere. |
| **M2** | Medium | `eq:augworked`: tied modes compute to 0.43532 / 0.43538, printed 0.4352 | §6.4 | 2 | ☑ Closed. At the exact λ_k the two augmented values are equal to machine precision — the discrepancy was an artifact of substituting the rounded 0.0454. Printed as 0.435229, with a sentence stating that the equality is exact by construction because λ_k is *defined* by the tie. Tie residual checked at 1e-12. |
| **M3** | Medium | §9.1 debt decomposition: 13.5 + 1.37t gives 40.9 at t=20, stated 49.3 | §9.1 lines 1640–1644 | 2 | ☑ Closed, and wider than the programme scoped it. The figure's coordinates fitted no declared parameterisation at all, so the fix is a stated one: new `tab:cadparams` gives $(c_j,\pi_{j,\infty},\tau_j)$ per component per strategy; the figure is replotted from Eq. (47) over 0–20 years in two panels. Recomputed values: bounded part **17.98** (11.34 of it skill formation), residual slope **1.45**/yr (1.08 of it vendor dependency), Human-First slope 2.38 (now derived, not asserted), crossover **t = 13.23** at 36.73, C(20) = 46.89 vs 52.89. All checked in `audit_numbers.py`, including every plotted coordinate. |
| **M4** | Medium | P3's 80-pt gap uses the weaker comparator (CM 0.17, not HF 0.31 → 66 pts) | `tab:hypoutcomes` l.1568 | 2 | ☑ Closed by removal (tab:hypoutcomes deleted). Recorded in audit_numbers.py as a pre-deletion baseline check. |
| **M5** | Medium | `tab:persector` final row labels a sum ("mean over sectors", 803,100) | line 1427 | 2 | ☑ Closed by removal (tab:persector deleted). Recorded in audit_numbers.py: the column mean is 133,850, not 803,100. |
| **M6** | Medium | Scalarization/convex-hull admission belongs where legitimacy is claimed | §9.5 l.1687 → §5.1 | 6 | ☐ |
| **M7** | Medium | No GCC/Saudi legal analysis despite affiliations, funder, and `ILOESCWA2026` | new §5.x | 6 | ☐ |
| **M8** | Medium | Online rule: no regret/violation bound; CMDP + online-matching unengaged | §9.5 l.1688 | 6 | ☐ |
| **M9** | Medium | `syed2026fedagent` does not support the claim it is cited for | §2.6 | 7 | ☐ |
| **M10** | Medium | Tables `tab:notation`, `tab:params` are reference material in the main text | lines 857, 1255 | 4 | ☐ |
| **L1** | Low | 53 overfull `\hbox` warnings | throughout | 7 | ☐ |
| **L2** | Low | Mixed orthography ("unfavourable" l.1638, "behaviourally") | §9.1, App. S4.2 | 7 | ☐ |
| **L3** | Low | `BenDaya2026` / `syed2026fedagent` volume–number collision | `references.bib` | 7 | ☐ |
| **L4** | Low | "differ by two to four points" → 2.2 and 4.3 | §9.1 line 1644 | 2 | ☑ Closed by removal in Phase 1 — the closed-form/simulation comparison paragraph does not survive Route A. Verified absent. |
| **L5** | Low | Orphaned `$\dagger$` equal-contribution footnote | line 105 | 5 | ☐ |
| **L6** | Low | `\correspondance{}` passed empty | line 97 | 5 | ☐ |
| **L7** | Low | "AA" initials collide (Ali Akarma / Abdulaziz Alqurashi) | line 1724 | 5 | ☐ |
| **L8** | Low | Intake requirement buried; deserves Abstract + a figure | §6.6 → Abstract | 6 | ☐ |
| **N1** | **Critical (new)** | `README.md` author list does not match the manuscript | `README.md` line 5 | 3 | ☐ |
| **N2** | **High (new)** | `verify_worked_example.py` verifies a *different* worked example (B_k = 2,073.6 vs the manuscript's 4,976.64) | `scripts/verify_worked_example.py` | 3 | ☐ |
| **N3** | **High (new)** | The verification gate does not run: `pulp` is not installed; the script aborts at the constrained-optimum stage | repo environment | 3 | ☐ |
| **N4** | Medium (new) | Repo and README cite a third section numbering (§5.3, §7.1) | `README.md`, `scripts/`, `sim/` docstrings | 3 | ☐ |
| **N5** | **High (new)** | Every in-text citation prints its authors twice (`Author~\cite{key}` under Frontiers-Harvard renders "Author Author (year)"); parenthetical citations render unbracketed | ~30 sites throughout `CivicWorkOS.tex` | 7 | ☐ |

---

## 5. Four findings the review did not reach

These were found while preparing this programme, by running your own repository against your own manuscript. They matter because the reviewers credited the repository as "exemplary" reproducibility — a credit that does not survive inspection in its current state.

**N1 — The README names different authors than the manuscript.**
`README.md` line 5 credits "Toqeer Ali Syed, Ali Akarma, Shahid Kamal, Salman Jan, Ahmad B. Alkhodre, and Arshad Jamal". The manuscript's `\def\Authors` names "Toqeer Ali Syed, Ali Akarma, Raghda M. Alqurashi, Muhammad Tayyab Naqash, Abdulaziz Alqurashi". Four of six names differ. A reviewer or editor who notices this will ask who the authors are, and the question is not one you want on the record alongside C1. Fix before anything is submitted.

**N2 — The verification script verifies a prior version of the paper.**
Running `python scripts/verify_worked_example.py` prints `[PASS] B_k (Eq. 9): expected=2073.600000 actual=2073.600000`. The manuscript (line 1024) computes `B_k = max(2000, 1.2 × 24 × 0.12 × 1440) = 4,976.64`. The script's expected value corresponds to an `h_k` of 600 rather than 1,440 — an earlier draft's parameterisation. So the artifact that reviewers praised as proving the worked example reproducible is, in fact, confirming numbers the submitted paper does not contain. **The one genuinely strong reproducibility claim in the whole submission is currently broken.** This is cheap to fix and expensive to leave.

**N3 — The verification gate aborts partway.**
The script fails with `ModuleNotFoundError: No module named 'pulp'` at the constrained-optimum stage. The README advertises it as the first CI gate and claims 164 passing tests. Any reviewer following the README's "run this first after cloning" instruction hits a traceback. Pin `pulp` in `requirements.txt` and verify the full script exits 0.

**N4 — A third section numbering in the repository.**
`README.md`, `scripts/verify_worked_example.py` and the `sim/` docstrings reference "Paper Sec. 5.3", "Sec. 6.1", "Sec. 6.2", "Sec. 7.2", "Eq. 15", "Eq. 16", "report Sec. 20.13". None of these match the compiled manuscript (§3). The repository reads as documentation for a paper that no longer exists.


**N5 — Every citation prints its authors twice.**
`FrontiersinHarvard.cls` loads `natbib`, in which `\cite` is the *textual* form and renders as “Author (year)”. The manuscript writes `Author~\cite{key}` throughout, so the first page reads “Choi and Yoon Choi and Yoon (2025) demonstrate…” and “Shariatpour et al. Shariatpour et al. (2026) describe…”. The same construction appears at roughly thirty sites. Where no author name precedes the citation, the opposite error occurs: `district~\cite{AcemogluRestrepo2020,Eloundou2024}` renders the citation unbracketed in running prose where it should be parenthetical. The repair is mechanical but must be done case by case, because the two cases take opposite fixes: delete the redundant prose name and keep `\cite` where the sentence uses the author as its subject, and switch to `\citep` where the citation is an aside. This is the most visible defect remaining in the document and it is on page one. Scheduled for Phase 7 with the rest of the bibliography work.

---

## 6. The phases

### Phase 0 — Freeze, baseline, instrument

**Goal.** A reproducible starting point, a measured baseline for every quantity this programme will change, and the automated checks that will prove each later phase actually closed its gates.

**Work items**

1. Commit the current state on a branch (`git checkout -b revision/frontiers-hnt`). `Paper/` is currently untracked — add it. Tag the pre-revision commit so `latexdiff` has an anchor.
2. Record the baseline: `texcount -inc -total -q CivicWorkOS.tex` → **21,048** body words; 53 pages; 3 figures; 19 tables; 53 overfull boxes; 0 undefined references or citations.
3. Write `Paper/Frontiers/check.sh` (or `check.ps1`), a single script that runs and reports:
   - `latexmk -pdf -interaction=nonstopmode` → must exit 0
   - `texcount -inc -total -q` → must report ≤ 12,000
   - `grep -c Overfull CivicWorkOS.log` → target 0
   - `grep -ci 'undefined' CivicWorkOS.log` → must be 0
   - `grep -c 'keyword' CivicWorkOS.tex` → must be ≥ 1
   - a placeholder scan: `grep -nE '26UQU\(|\(Staff number\)|XXXX|TODO|TBD' CivicWorkOS.tex` → must be empty
   - `python scripts/verify_worked_example.py` → must exit 0
4. Write `Paper/Frontiers/audit_numbers.py`: a standalone script that recomputes, from the manuscript's own stated inputs, every number this programme touches — the SCV decomposition, the tied-mode augmented values, λ_k, the 594/595 integrality argument, B_k, the credited share, τ_k and n̂_k by both routes, the per-sector column means, the ablation deltas, the stress-table means, and the §9.1 debt trajectory. It prints PASS/FAIL per check. This is the instrument that prevents a repeat of the current situation, where five of nine defects are in prose that misreports a correct table.

**Success criteria (all must hold)**

- ☐ Branch created; `Paper/` tracked; pre-revision commit tagged.
- ☐ `check.sh` runs end to end and reports the baseline numbers above without crashing.
- ☐ `audit_numbers.py` reproduces, to 1e-4, at minimum: unconstrained SCV = 0.34261, constrained SCV = 0.327758, weights sum = 1.000, deferred block = 0.220, B_k = 4,976.64, credited share = 0.2962, 3.456 competent-equivalents, τ_k = 4.05 yr, n̂_k = 14.0 by two routes, per-sector means (CFI 0.97, productivity 86.83, λ̄ 0.01775, Z4 0.0288), stress means (CWOS 24.70, AF 61.45).
- ☐ `audit_numbers.py` **fails** on the known-bad items (λ_k printed 0.0454 vs computed 0.04550; §9.1 trajectory 13.5 + 1.37·20 = 40.9 vs stated 49.3). A harness that passes everything on day one is not measuring anything.

**Effort:** 4–6 hours (most of it writing `audit_numbers.py`).
**Compute:** one full LaTeX build ≈ **60 s** (measured on this machine: `latexmk -pdf` cold-to-warm, 53 pages with TikZ/pgfplots). `texcount` < 2 s. `audit_numbers.py` < 1 s. Total machine time for the phase: **under 3 minutes**.

---

### Phase 1 — Integrity remediation (the dispositive fix)

**Goal.** No sentence anywhere in the manuscript reports a result that was not obtained. Every surviving number traces to Section 6's exact arithmetic, to the closed-form model of §9.1, or to a conducted study.

This phase is the whole decision. Do it first, do it completely, and do not soften it.

**Work items (Route A)**

1. **Delete §8 entirely** (lines 1361–1583), including Tables `tab:mainresults`, `tab:persector`, `tab:ablation`, `tab:stress`, `tab:dist`, `tab:runtime`, `tab:hypoutcomes`. This closes C1, H1–H4, H6, H8, M4, M5 by removal.
   - **Rescue before deleting:** Table `tab:dist` (distributional outcomes, lines 1505–1519) is cited by Reviewer 3 as a methodological contribution — the structurally-zero contracted-worker row. Recast it as an *analytical* consequence of the worked example's access arithmetic (622 h vs 1,344 h, §6.7) rather than a simulated year-10 result, strip the `±` intervals, and move it into §6.7. It is a derivation, and as a derivation it is sound.
2. **Convert §7 (Evaluation Protocol, lines 1197–1360) into a specified-but-unexecuted protocol.** Two options:
   - *Preferred:* compress to a single ~500-word subsection in Discussion titled "A Specified Evaluation Protocol" whose opening sentence is unambiguous — e.g. *"The protocol below is specified and pre-registered in form, and has not been executed. It is stated here so that the evaluation this framework requires is reproducible by others and auditable against a fixed plan."* Move Tables `tab:sectors`, `tab:params`, `tab:predictions` and the full statistical plan to the supplement.
   - *Alternative:* keep §7 in place with the same opening sentence and move the detail to the supplement. Costs ~700 more words.
3. **Resolve C2.** Line 1335's future tense becomes the governing statement, not a contradiction. Keep the pre-specified/pre-registered distinction — it is correct and creditable — and state that the OSF entry will carry the identifier when the study is run.
4. **Rebuild the Abstract (C3).** Remove 63.2%, 86.8%, 0.97. Build around Section 6. Draft:

   > Cities are moving from sensing infrastructure to agentic operation, in which AI agents perform administrative work and robots perform physical work. Allocation research optimizes fit, throughput, and ergonomics; labor research examines displacement; neither prices the developmental practice through which cities form future practitioners. We present CivicWorkOS, which makes municipal allocation a governed decision over *staffed modes* — pairings of an execution mode with a named roster at declared career stages — rather than a human-versus-machine choice. Civic Automation Debt prices five deferred liabilities, and four constraints bind the objective: a Human Capability Preservation Budget denominated in qualified-practice hours accruing only to practitioners below independent competence, a Capability Access Constraint governing who receives protected practice, a Just Transition Constraint, and an N−1/N−2 resilience reserve. We give the city-wide program, an online Lagrangian rule with bounded between-rebalance violation, a feasibility condition, and an intake requirement for when the budget is unattainable. An exact bridge-inspection instance, reproducible by direct arithmetic from the reported values, prices protected practice at 0.0455 objective units per hour, costs 4.34% of annual objective value (0.33–9.60% across the swept parameter frontier), and yields 3.46 competent-equivalents a year against attrition of 2.88. The same arithmetic produces a result no headcount plan surfaces: machine-assisted supervised practice stretches time to competence by a factor of 3.38, from 1.2 to 4.05 years, so a city sizing intake from certification hours provisions four trainee posts where fourteen are required.

   Count it: target 200–230 words. Check the venue's abstract limit before finalising.
5. **Rewrite the Data Availability Statement (C4)**, reusing the repository README's own accurate wording. Draft:

   > No new datasets were created or analyzed in this study. All parameter values, the worked allocation of Section~\ref{sec:worked}, and the sensitivity analysis of Section~\ref{sec:sensitivity} are fully specified in this article and can be reproduced from the reported values by direct arithmetic. The author-provided reference implementation, which recomputes every checkable number this article publishes and reports the agreement check by check, is available at https://github.com/aliakarma/CivicWorkOS. Code under `sim/` in that repository runs on clearly labelled synthetic demonstration data; it exercises the software shape of the protocol specified in Section~\ref{sec:expsetup} and must not be cited as empirical municipal validation. The evaluation protocol of Section~\ref{sec:expsetup} has not been executed.

   Note the cross-reference fix: the current text cites `sec:worked` and `sec:discussion` where it means `sec:results`.
6. **Remove ERA (H6).** With §8 deleted, ERA disappears from the results tables. It remains described in §7.2 as a comparator in the specified protocol — that is legitimate, because a specified protocol may name a baseline it has not yet run. Add the repository's own concession to §7.2: *"An evaluation in which four of six comparators are configurations of the proposed objective can show that the mechanism does what it was designed to do; it cannot show that it outperforms an independently designed alternative. The two external baselines are specified for that reason and the comparison is incomplete until they are run."*
7. **Relocate H7.** The §8.6 retirement-wave arithmetic (lines 1489–1497) is correct, valuable, and analytic. Move it into §6 as a parameter-shock extension of the worked example — "§6.9 Two Parameter Shocks: Stability and Infeasibility" — with every quantity labelled as exact arithmetic on the model, not as simulation output. The same applies to §8.3's "simulated dual 0.0451 within 0.7% of 0.0454" (line 1432): delete it, since under Route A there is no simulated dual.
8. **Remove H8.** The 0.942 appeals figure goes with §8. Do not reintroduce it anywhere without a specified appeal-arrival, standing, upheld-rate and resolution-time model.
9. **Declare the article type (C10).** Add to the preamble/cover note: *Hypothesis and Theory*.
10. **Sweep for orphans.** After deletion, every `\ref` to a removed label, and every past-tense claim about results, must go. Search aggressively:
    - `grep -nE 'ref\{(tab:mainresults|tab:persector|tab:ablation|tab:stress|tab:runtime|tab:hypoutcomes|sec:results|sec:mainresults|sec:persector|sec:ablation|sec:stressresults|sec:retirement|sec:distresults|sec:runtime|sec:hypoutcomes)\}' CivicWorkOS.tex`
    - `grep -nE '\b(achieved|demonstrated|observed|measured|reported|confirmed|was not refuted|simulated|across thirty|30 paired|paired seeds)\b' CivicWorkOS.tex`
    - Known downstream sites to clean: §9.1 line 1642 ("the same finding the Capability-Formation Index of 0.31 reports in Table `tab:mainresults`"), line 1644 (the closed-form/simulation agreement paragraph — under Route A there is nothing to agree with, so this paragraph goes), §9.2 line 1655 (cites `sec:results`), §9.3 line 1662 (cites `tab:stress`), §9.4 line 1679 (statistical validity paragraph describing a conducted comparison), §10 line 1705 ("at a cost of 1.3 debt index points").
    - Figure `fig:cad-trend` survives — its caption already states it plots Eq. `eq:cadmodel`, which is correct practice. Reframe the surrounding prose as a property of the debt accounting, which is what §9.4's "the ordering of the curves is not evidence" already says correctly.

**Route B delta:** skip items 1, 2, 6–8; instead execute Phase 9b first and return here with real data.
**Route C delta:** replace item 1 with a new, much smaller §8 reporting the single-domain synthetic demonstration, under a section title and opening paragraph that state its scope in the first sentence.

**Success criteria**

- ☐ `grep -ci 'undefined' CivicWorkOS.log` returns 0 after a clean three-pass build (no dangling `\ref` to deleted labels).
- ☐ No sentence in the manuscript reports a quantity that is not (a) exact arithmetic on stated inputs, (b) a value of the closed-form model `eq:cadmodel`, or (c) an explicitly labelled unexecuted target. Verify by reading the full text once, end to end, with this single question in mind. Budget two hours for it; it is the most important reading pass in the project.
- ☐ Every number in the Abstract appears in §6 or §9.1 and is reproduced by `audit_numbers.py`.
- ☐ The Data Availability Statement, the repository README, and §7's opening sentence all say the same thing about what was and was not done. Read the three side by side and confirm they are mutually consistent.
- ☐ The strings `63.2`, `86.8`, `0.97` (as a CFI), `0.942`, `52.9`, and `thirty paired` appear nowhere in the manuscript.
- ☐ Article type declared.

**Effort:** 10–14 hours (1.5–2 days). The deletion is fast; the orphan sweep and the end-to-end read are what take the time, and they are not optional.
**Compute:** 4–6 full builds × 60 s ≈ **6 minutes**.

---

### Phase 2 — Numerical consistency repair

**Goal.** Every number in prose matches the table, equation or figure it reports, and `audit_numbers.py` passes clean.

Note that Phase 1 has already removed the hosts of H1–H4, M4 and M5 under Route A. What remains are defects in material that survives. Under Routes B/C, all of H1–H4 must be fixed in place.

**Work items**

1. **M1 — λ_k.** `eq:lambdaworked` prints λ_k = 0.0273/0.6 and reports 0.0454. The quotient is 0.04550. To obtain 0.0454 the unrounded SCV difference must be 0.02724. Choose one and apply it to all ten sites:
   - *Option A (recommended):* publish the unrounded tied-mode SCV values to five decimals so the division reproduces exactly, and state them in the equation's surrounding text. This preserves the headline 0.0454 and makes it checkable.
   - *Option B:* correct to **0.0455** throughout, in the Abstract, §6.4, §6.9, §10, and the repository's verification script.
   - Sites to update (Route A): Abstract; `eq:lambdaworked` and its paragraph; §6.4 dual discussion; §6.8 `tab:sensitivity` caption/rows where 0.0454 is the reference; the relocated §6.9 parameter-shock text; §10 Conclusions line 1705.
2. **M2 — `eq:augworked`.** The tied augmented values compute to 0.43532 and 0.43538, neither of which rounds to the printed 0.4352. Recompute at full precision and print to the precision that is actually correct, or print both to five decimals and state the tie tolerance explicitly. Whichever you choose must be consistent with the λ_k decision in M1.
3. **M3 — §9.1 debt decomposition.** The text states a saturating ceiling of 13.5 index units plus a linear residual of 1.37 units/yr, and quotes 34.6 at year ten and 49.3 at year twenty. Those are inconsistent: 13.5 + 1.37·10 = 27.2 and 13.5 + 1.37·20 = 40.9. Against the figure's own plotted CivicWorkOS value of 34.60 at t = 10, with τ_skill = 4.05, the saturating component contributes 13.5(1 − e^(−10/4.05)) = 12.36, leaving a residual of 22.24, i.e. an implied slope of **2.22** units/yr, not 1.37. Recompute the decomposition from `eq:cadmodel` with the actual per-component parameters, correct the ceiling, slope and quoted values together, and add all three to `audit_numbers.py` so they can never drift apart again. Do the same for the Human-First crossover at t = 9.34 and the year-twenty 59.0 figure.
4. **L4 — §9.1 line 1644.** Under Route A the closed-form/simulation comparison paragraph is deleted entirely by Phase 1. If any version of it survives, "two to four points" must read "2.2 and 4.3 points."
5. **H5 — §6.8 robustness claim.** This one is substantive and survives every route. The text claims the staffing reversal "survives every feasible value of all six parameters" and calls it "the paper's central claim". Table `tab:sensitivity` contains ten feasible rows labelled "no reversal", which its own caption defines as the constrained optimum retaining the lead-only roster on some tasks — 46.1% of tasks at r_k = 0.06, 28.2% at h_raw = 1200, 15.4% at φ = 0.70, with the dual collapsing from 0.0454 to ≤ 0.0033. Replace with the claim the table supports:

   > The capability budget is never satisfiable by lead-only rosters alone, so some developmental staffing occurs at every feasible parameter value we swept. What is *not* robust is the strength of that effect. Across the ten feasible rows that Table~\ref{tab:sensitivity} labels "no reversal", the constrained optimum retains the lead-only roster on 15.4% to 46.1% of tasks and the dual falls to 0.0033 or below. The qualitative conclusion — that a binding capability budget always places developing practitioners on some of the work — holds across the frontier; the magnitude of the price, and therefore the magnitude of the reallocation, does not. Section~\ref{sec:sensitivity} is the range that should accompany any single quoted figure.

   This is a real reduction in the strength of the paper's self-declared central claim. It is also the honest version, and the manuscript's own table is what forces it. Reviewer 1 flagged it; Reviewer 2 flagged it; it will be flagged again if left.
6. **M4, M5** (Routes B/C only): fix P3's comparator to the best-performing baseline (Human-First at 0.31 → a 66-point gap, not 80); split or footnote the `tab:persector` final-row label so Tasks/yr is identified as a sum while the other columns are means.
7. **H1–H3** (Routes B/C only): the ablation shows removing the access constraint *raises* CAD by 1.3 and recovery by 0.7 h. Correct §8.4, §8.7, §8.9 and §10, and reconsider P8's "CAD ≤ +5" clause, which is vacuous if the constraint is a debt benefit rather than a cost.
8. **H4** (Routes B/C only): "< 1.5 s" → the table's 74 s, or "< 1.5 minutes" if that was the intent. The scalability conclusion survives either way; the stated figure does not.

**Success criteria**

- ☑ `audit_numbers.py` exits 0 with every check PASS. 187 PASS, 0 FAIL, 189 comparisons. The §9.1 trajectory checks are in, and go further than item 3 asked: slope, bounded part, per-component residual split, crossover, C(20), and all 116 plotted coordinates.
- ☑ Manual pass done table by table over the eleven surviving tables. `tab:worked-decomp` (direction and sign of all nine terms, including that a rise in the Cost row is a worsening), `tab:dist` (622 / 1,344 / 2.16× / 3.8-of-14), `tab:sensitivity` (85% headroom on three axes, 0.33–9.60% range, eight "no reversal" rows), `tab:weights` (0.062 skill, 0.044 transition, 0.180 safety), `tab:worked-terms` and `tab:worked-mix` (covered by the audit's 60 worked-example checks), `tab:cadparams` (both computed columns). One residual inconsistency found and fixed outside the register: the cost of preservation was quoted as "4.3%" at two prose sites against 4.34% everywhere else.
- ☑ `grep` returns one value: 0.0454 at 15 sites, plus the single six-decimal 0.045353 inside `eq:lambdaworked`. No 0.0455 anywhere.
- ☑ Neither phrase appears in either document. A `check.sh` gate now enforces this, together with gates on 0.0455, the six-decimal numerator, the superseded debt constants, and the presence of `tab:cadparams`.

**Effort:** 8–10 hours (1–1.5 days). Item 3 (the debt-model recomputation) is the long pole — budget 3 hours for it alone.
**Compute:** `audit_numbers.py` < 1 s per run; 3–4 builds ≈ **4 minutes**.

---

### Phase 3 — Repository and manuscript reconciliation

**Goal.** A reviewer who follows the Data Availability link finds a repository that describes this paper, credits these authors, and whose first-gate verification script passes against the numbers this paper prints.

This phase is not cosmetic. The repository is the artifact that triggered the review's dispositive finding; it is also, once corrected, the paper's strongest reproducibility asset.

**Work items**

1. **N1 — Author list.** Correct `README.md` line 5 and `CITATION.cff` to the manuscript's author list and order. Verify `CITATION.cff` parses (`cffconvert --validate`, or any YAML linter).
2. **N2 — Verification script.** Update `scripts/verify_worked_example.py` so its expected values are the manuscript's: B_k = 4,976.64 (h_k = 1,440, η_k = 1.2, N_k = 24, r_k = 0.12), credited share 0.2962, Φ_k ζ̄_k = 5,880, unconstrained SCV 0.34261, constrained 0.327758, 594/595 integrality at 4,976.40 / 4,977.00 hours, 3.456 competent-equivalents, τ_k = 4.05, n̂_k = 14.0, the access arithmetic at 622 h / 1,344 h / 2.16×, and whichever λ_k value Phase 2 settled on. Where `audit_numbers.py` and this script overlap, make one import the other rather than maintaining two copies of the same constants — divergence between them is exactly how N2 arose.
3. **N3 — Environment.** Add `pulp` to `requirements.txt` with a pinned version. Confirm `python scripts/verify_worked_example.py` runs to completion and exits 0 on a clean virtualenv built from `requirements.txt` alone.
4. **N4 — Section references.** Update every "Paper Sec. X" and "Eq. N" reference in `README.md`, `scripts/*.py`, `sim/**/*.py` docstrings and `docs/*.md` to the final compiled numbering. Do this *after* Phase 4, since the length reduction will renumber sections again — or, better, reference sections by name rather than number so this never recurs.
5. **README scope statement.** It is already accurate and honest, which is to your credit — the review says so. Keep it. Align it with the manuscript's new Data Availability Statement so the two read as one position stated twice, not two positions.
6. **Remove the unverified CI claims** or make them true: the README advertises "164 passed" and "CI passing" badges. Confirm `pytest` actually passes on a clean environment, or adjust the badges.
7. **Archive the calibration snapshots** the manuscript promises ("the archived snapshots with retrieval timestamps accompany the replication package", line 1224). Either ship them or delete the sentence. Reviewer 2 lists this among the missing essentials.

**Success criteria**

- ☐ `git clone` into a clean directory → `pip install -r requirements.txt` → `python scripts/verify_worked_example.py` exits **0** with every check PASS against the manuscript's printed values. Run this from an empty virtualenv, not your development environment.
- ☐ `pytest` exits 0 and the reported test count matches the README badge.
- ☐ `grep -rn "Sec\. [0-9]" README.md scripts/ sim/ docs/` returns only references that match the compiled manuscript.
- ☐ README author list, `CITATION.cff`, and `\def\Authors` are byte-identical in names and order.
- ☐ Either the calibration snapshots are in the repository, or no sentence in the manuscript claims they are.

**Effort:** 6–8 hours (1 day).
**Compute:** clean-environment install ≈ 2–4 min; `pytest` suite — measure it, likely under 60 s for 164 unit tests; verification script < 5 s with `pulp` present. Total **under 10 minutes**.

---

### Phase 4 — Length reduction to ≤ 12,000 words

**Goal.** `texcount -inc -total -q` reports ≤ 12,000 body words with the argument intact.

**Measured baseline and target budget.** Current body-word distribution, measured per top-level section:

| Section | Current | Target | Δ | How |
|---|---:|---:|---:|---|
| 1 Introduction + Contributions | 665 | 700 | +35 | Slight expansion to carry the intake result into the framing; soften the five-gap overclaim Reviewer 2 and the area chair both flag |
| 2 Related Work | 2,633 | 1,200 | −1,433 | Nine subsections → five: merge 2.1+2.2 (allocation and scheduling), keep 2.3 (skill erosion, the lineage statement earns its space), merge 2.4+2.5 (fair division and contestability), merge 2.6+2.7 (algorithmic management and labour), keep 2.8+2.9 condensed. Reviewer 3 verified this survey is accurate — compress it, do not weaken it |
| 3 Framework | 3,538 | 1,900 | −1,638 | Move the operationalization detail of §3.1, the full policy-rule language of §3.4, and the layer-by-layer prose of §3.2/3.3 to the supplement; keep the definitions the optimization program needs |
| 4 Architecture, Program, Algorithm | 3,213 | 1,700 | −1,513 | Move Table `tab:notation` (M10), the §4.9 notation subsection, and the four proofs to the supplement, keeping proposition statements inline. Keep the dual interpretation in §4.7 — it is load-bearing and the manuscript's correction of its own prior inversion is worth the words |
| 5 Governance | 1,984 | 1,300 | −684 | Compress §5.4 (DPIA) into the supplement, which already holds the operative specification; keep §5.3 legality; add the new GCC subsection from Phase 6 within this budget |
| 6 Worked Allocation + Sensitivity | 2,375 | 2,500 | +125 | **Grow this.** It is now the paper's entire evidence base, and it absorbs the relocated parameter-shock arithmetic from Phase 1 and the `tab:dist` recast |
| 7 Evaluation Protocol | 2,227 | 500 | −1,727 | Phase 1 reduces this to a specified-protocol subsection; Tables `tab:sectors`, `tab:params`, `tab:predictions` and the statistical plan move to the supplement |
| 8 Results | 1,332 | 0 | −1,332 | Deleted in Phase 1 |
| 9 Discussion | 2,141 | 1,500 | −641 | Move the `eq:cadode`/`eq:cadmodel` derivation to the supplement, keep the figure and the three conclusions; keep §9.3 (who wins and who loses) nearly intact — Reviewer 3 identifies it as a contribution |
| 10 Conclusions | 507 | 450 | −57 | Tighten; remove the "1.3 debt index points" sentence (H2) |
| Back matter | 221 | 280 | +59 | Ethics Statement added |
| **Total** | **21,048** | **~12,030** | **−9,018** | |

That lands at the line. Build in margin by taking a further ~300 words out of §3 and §4, which are the two sections with the most relocatable material. Target **11,700** so that Phase 6's additions do not push you back over.

**Work items**

1. Execute the budget section by section, **measuring after each one**: `texcount -inc -sum -q CivicWorkOS.tex | grep -E 'Section:'`. Do not compress by eye.
2. Everything removed goes to `CivicWorkOS_supplementary.tex`, not to the bin. The `xr`/`xr-hyper` cross-referencing is already configured correctly in both files and the log shows no undefined references — that machinery is working, so use it.
3. **Confirm the counting convention before you trust the number.** Check Frontiers' current Hypothesis and Theory page for whether the limit counts tables, captions, references and back matter. Your declared 21,050 matches `texcount`'s body-text total of 21,048, so you have been counting body text — verify that is the right basis. If captions count, you have another 1,046 words to find.
4. Update `\extraAuth` with the new word, figure and table counts.
5. Reduce display items. Twenty-two across 53 pages is flagged as very high by Reviewer 1; after Phase 1 removes seven tables you will be at 12, which is comfortable. Keep `tab:comparison`, `tab:worked-terms`, `tab:worked-mix`, `tab:worked-decomp`, `tab:sensitivity`, `tab:weights`, the recast `tab:dist`, the zone tables, and the three figures.

**Success criteria**

- ☐ `texcount -inc -total -q CivicWorkOS.tex` ≤ **11,800** (margin below the 12,000 ceiling).
- ☐ `\extraAuth` word/figure/table counts match the measured values exactly.
- ☐ Supplementary builds cleanly and `grep -ci undefined` on **both** logs returns 0.
- ☐ Page count ≤ ~30 (sanity check that the reduction is real and not absorbed by float reflow).
- ☐ A co-author who did not do the cutting reads the compressed §2 and §3 and confirms no argument was lost. This gate needs a human; nothing mechanical catches a deleted premise.

**Effort:** 24–32 hours (3–4 days). This is the single largest phase. Compression is slower than writing.
**Compute:** `texcount` after each section ≈ 2 s × ~20 runs; 10–15 full builds of main + supplement ≈ **20 minutes** total.

---

### Phase 5 — Front matter and Frontiers compliance

**Goal.** Nothing in the submission package can be returned by a production editor before the manuscript reaches a reviewer.

**Work items**

1. **C6 — Keywords.** Add 5–8. Proposed set (8): `human–AI–robot task allocation`, `municipal automation governance`, `capability preservation`, `civic automation debt`, `workforce skill formation`, `algorithmic contestability`, `urban digital twin`, `constrained optimization`. Use the class's `\keyword{}` command — check `FrontiersinHarvard.cls` for the exact macro name and the required separator.
2. **C7 — Funding.** Replace `26UQU(Staff number)(track name)xx` in **both** the Acknowledgment (line 1716) and the Funding statement (line 1728) with the real grant code. This requires the actual code from Umm Al-Qura — request it now, at the start of the programme, not at the end; it is the item most likely to block submission on administrative latency.
3. **C8 — Ethics Statement.** Required even to record non-applicability, and non-trivial here because Appendix S4.4 states the elicitation protocol "requires institutional ethics approval and written informed consent before any data collection." Draft:

   > **Ethics Statement.** This study involved no human participants, no animal subjects, and no personal data. All parameter values reported are the authors' structured estimates, and all results are analytical. The expert-elicitation protocol specified in Appendix S4 has not been executed; its execution would require institutional ethics approval and written informed consent from participating practitioners, as that appendix states. Ethical review and approval were therefore not required for this work in accordance with institutional and national requirements.
4. **C9 — Abbreviations.** Either populate (CAD, CWOS, SCV, HCPB, CFI, MILP, LP, DES, PSI, EU AI Act, GDPR, ICC) or delete `\section*{Abbreviations}` at line 1712. Populating is better: the manuscript uses a dozen acronyms heavily.
5. **L5 — Dagger footnote.** Line 105 declares shared first authorship but no `$\dagger$` appears in `\def\Authors`. Either attach it to the intended authors or delete the footnote. Decide with co-authors; an unattached equal-contribution claim is worse than none.
6. **L6 — Corresponding author.** `\corrAuthor` and `\corrEmail` are defined at lines 84–85 but `\correspondance{}` at line 97 is passed empty, so no corresponding-author block renders. Pass them through. Likewise `\address{}` at line 96 is empty while `\def\Address` is populated.
7. **L7 — Initials collision.** Ali Akarma and Abdulaziz Alqurashi both reduce to "AA", and "AA" appears in two different sentences of the Author Contributions (line 1724), making the record ambiguous for two people. Use distinct initials (AAk / AAlq) or full names, and state the convention.
8. **Required structure.** Confirm the Hypothesis and Theory structure: Abstract, Introduction, relevant subsections, Discussion. Your structure conforms once §8 is removed — verify against the journal's current article-type page rather than against this note.
9. **Cover letter.** Draft it now (see §10 of this document). For a resubmission following a serious pre-submission audit, the cover letter should state the article type, the word count, and that the evaluation protocol is specified and unexecuted. Volunteering that last point is far stronger than having it discovered.

**Success criteria**

- ☐ `grep -nE '26UQU\(|\(Staff number\)|\(track name\)|xx\b|TODO|TBD|XXXX' CivicWorkOS.tex` returns **nothing**.
- ☐ `grep -c 'keyword' CivicWorkOS.tex` ≥ 1, and the rendered PDF shows 5–8 keywords.
- ☐ The compiled PDF's first page shows: title, full author list with affiliations, a corresponding-author block with name and email, keywords, abstract, and the word/figure/table counts.
- ☐ Abbreviations section is either populated or absent — not present and empty.
- ☐ Ethics Statement present.
- ☐ Author Contributions contains no ambiguous initials; every initial maps to exactly one author.
- ☐ A co-author other than the submitting author reads the full front and back matter and signs off.

**Effort:** 3–4 hours of editing, plus however long the grant-code request takes. Start the request on day one.
**Compute:** 2–3 builds ≈ **3 minutes**.

---

### Phase 6 — Substantive strengthening

**Goal.** The paper is not merely defensible but better than the version that was reviewed. Every item here was requested by a reviewer and each raises the acceptance probability independently.

**Work items**

1. **L8 — Promote the intake requirement.** All three reviewers independently identify this as the paper's most citable, most transferable, simulation-independent result, and all three note it is buried in §6.6. Actions:
   - It is already in the Abstract after Phase 1.
   - Add it to the Contributions list in §1.1 as a named contribution, not a sub-clause.
   - **Add a figure.** The paper currently has three figures, two of which are architecture and workflow diagrams. A plot of time-to-competence τ_k = (h_raw/Θ)(1/φ̄ω̄) against the automation share φ̄, with the certification assumption of 1.2 years as a horizontal reference, the operating point at 4.05 years marked, and a right-hand axis showing the implied intake n̂_k rising from 4 to 14 posts, would make the result legible in one glance. Draw it in pgfplots (already loaded) so it is vector and consistent with `fig:cad-trend`.
   - Reference it in the Conclusions, where it already appears, and make it the last substantive sentence of the Introduction.
2. **M7 — GCC / Saudi legal and labour-market analysis.** The area chair calls this "the single most useful constructive suggestion in this review". The argument is simple and strong: Saudization/Nitaqat is a composition constraint on a workforce — a direct, real-world, legally mandated instantiation of Eq. `eq:access`. A new subsection in §5 (~600–800 words) should:
   - State that the EU analysis of §5.3 is one jurisdiction's treatment and name the GCC as a second with materially different structure.
   - Map Eq. `eq:access` onto quota-based workforce-composition regimes, noting what transfers (an external target composition θ_{k,g} set by policy rather than by the mechanism; a published, auditable share) and what does not (the EU positive-action proportionality test has no direct analogue).
   - Connect `ILOESCWA2026` — currently cited once in related work and never used — to the Just Transition Constraint, which is where it belongs.
   - Note the implication for the access constraint's political economy: in a regime where composition targets are already law, the constraint is less a novel positive-action decision than an existing obligation made computable and contestable. That is a genuinely interesting reframing and it strengthens the deployability argument.
3. **M8 — Engage the constrained-MDP and online-matching literatures.** §9.5 already names Altman and García & Fernández as where the machinery lives. Reviewer 3 asks you to take one step in. ~400 words:
   - State the bound that would be sought: a regret bound for Eq. `eq:argmax` against the offline optimum, and a cumulative constraint-violation bound over the horizon, in the style of primal–dual CMDP results.
   - State why it is hard *here* specifically: the duals are updated at a rebalance cadence rather than per-decision; the constraint is a budget over a period rather than a per-step cost; the staffed-mode action space is combinatorial; and the capability stock is a state variable the constraint depends on, which breaks the stationarity most results assume.
   - Add the online-matching / prophet-inequality framing Reviewer 3 names: this is structurally online assignment with budget constraints, where competitive-ratio results bound exactly what Proposition 4 leaves open.
   - Cite 3–5 works. Stating precisely why you cannot yet prove something is a respectable contribution; gesturing at a literature is not.
4. **M6 — Move the scalarization admission.** The convex-hull limitation currently sits as a bullet in §9.5 (line 1687). It bounds the Weight Review Panel's authority, so it belongs in §5.1 where the democratic legitimacy claim is made. One paragraph, moved and slightly expanded: a panel that sets weights cannot reach allocations in non-convex regions of the frontier whatever it decides, so "the panel's authority is bounded by the aggregation function rather than by its mandate" is a constraint on the legitimacy claim, not a technical footnote.
5. **Soften the §1 five-gap framing.** Reviewer 2 and the area chair both note that §1 overclaims relative to §2's accurate positioning — §2.2 concedes the capability budget "is a member of that family rather than a departure from it", while §2.9's five-gap framing implies a larger departure. Bring §1 into line with §2. This costs nothing and removes an easy target.
6. **Add Reviewer 3's additional literatures** where they fit within budget: apprenticeship and vocational-training economics (training externalities, poaching, firm under-provision) to support the intake requirement, and public-sector algorithmic procurement to address the vendor-dependency gap §9.1 nominates as "the honest gap". Two or three citations each, integrated into argument rather than listed.

**Success criteria**

- ☐ The intake requirement appears in: the Abstract, the Contributions list, a dedicated figure, §6.6, and the Conclusions. A reader who sees only the Abstract and the figures comes away with it.
- ☐ The new GCC subsection is present, cites `ILOESCWA2026` in the Just Transition context, and names at least one specific composition-regime instrument.
- ☐ §9.5's online-rule bullet now states a specific target bound and at least three specific obstacles, and cites the CMDP and online-matching literatures.
- ☐ §5.1 contains the convex-hull limitation; §9.5 cross-references rather than duplicates it.
- ☐ `texcount` still ≤ 11,800 after all additions. If not, return to the §3/§4 reserve identified in Phase 4.
- ☐ A co-author with no prior exposure to the GCC subsection reads it and confirms the legal characterisation is accurate. Do not ship a legal claim unverified — §5.3's EU analysis is credited by reviewers precisely because it is careful.

**Effort:** 24–32 hours (3–4 days). The GCC subsection (2–3 days on its own if the legal research is done properly) is the long pole; the figure is ~4 hours.
**Compute:** 8–10 builds ≈ **10 minutes**.

---

### Phase 7 — Language, bibliography, typography

**Goal.** Nothing cosmetic remains that a copy-editor or a reviewer would remark on.

**Work items**

1. **L1 — 53 overfull `\hbox` warnings.** Work through them from the log: `grep -n 'Overfull' CivicWorkOS.log`. Most will be long URLs, long table cells, and unhyphenatable technical terms. Fixes in order of preference: rephrase, add `\-` hyphenation hints, adjust `\tabcolsep` or column widths, and only as a last resort `\sloppy` locally.
2. **L2 — Orthography.** Unify to US spelling. Known sites: "unfavourable" (line 1638), "behaviourally" (Appendix S4.2). Sweep: `grep -nE '\b\w+(our|ise|isation|ised|ising|yse|ysed)\b' CivicWorkOS.tex CivicWorkOS_supplementary.tex` and triage the hits (it will catch false positives like "four" and "analyse" vs "analyze" — review each).
3. **L3 — Bibliography.** `BenDaya2026` has `volume = {9}, number = {9}` while `syed2026fedagent` has `volume = {9}, number = {7}` for the same journal and year. One is wrong — check both against the publisher record. While you are in the file, verify DOIs resolve and that no entry has a placeholder.
4. **M9 — `syed2026fedagent`.** Reviewer 3, a domain specialist, states this is the only citation in the paper that does not support the claim it is attached to: it is cited at §2.6 alongside the OECD for the claim that "algorithmic management already allocates work, issues instructions, monitors performance, and supports managerial decisions", and it does not establish that. It is also a self-citation, which makes it a worse place to be wrong. Remove it or re-site it where it is apposite.
5. **Theorem environment dependency.** The `proof` environment is used four times but only `\newtheorem{Proposition}` is declared; `proof` is presumably supplied by `FrontiersinHarvard.cls`. It compiles, but make the dependency explicit with a comment, or declare it yourself, so a production system that swaps the class does not break silently.
6. **Full read-through for register.** One uninterrupted pass for tense consistency (Phase 1's deletions will have left past-tense fragments), for the candour the reviewers praised (keep it — §9.3, §9.5 and the §7.1 calibration self-correction are repeatedly singled out as strengths), and for any remaining sentence that overclaims.

**Success criteria**

- ☐ `grep -c 'Overfull' CivicWorkOS.log` returns **0** for both main and supplementary.
- ☐ `grep -ci undefined` on both logs returns 0.
- ☐ No British spellings remain (manual triage of the regex sweep complete).
- ☐ Every `.bib` entry used in the manuscript has consistent, verified volume/number/DOI fields.
- ☐ `syed2026fedagent` either removed or attached to a claim it supports.
- ☐ Read-through complete and sign-off recorded.

**Effort:** 6–8 hours (1 day). The overfull boxes are tedious rather than hard.
**Compute:** 15–25 builds while chasing boxes ≈ **25 minutes**.

---

### Phase 8 — Verification sweep, track-changes, and response letter

**Goal.** A submission package that can be defended line by line, and a response document that shows every reviewer point addressed.

**Work items**

1. **Full gate run.** Execute `check.sh` and `audit_numbers.py` from a clean build directory. Every gate green.
2. **Clean-clone verification.** From an empty directory: clone the repository, install from `requirements.txt` alone, run `verify_worked_example.py` and `pytest`. Both exit 0.
3. **`latexdiff` against the pre-revision tag.** `latexdiff-vc --git --pdf -r <pre-revision-tag> CivicWorkOS.tex`. This is both a self-check (does the diff show what you think you changed?) and, if the journal requests it, a submission artifact.
4. **Independent read.** A co-author who has not done the editing reads the compiled PDF cover to cover with `peer-review.md` open beside it, confirming each registered item is closed. This is the gate that catches what the greps cannot.
5. **Response-to-reviewers document.** Structure in §10 below. Even for a fresh submission rather than a formal resubmission, writing it is worth the day: it forces you to confirm every item, and if the journal asks, it is ready.
6. **Final `texcount`, final page count, final `\extraAuth`.**
7. **Submission package assembly:** main `.tex` + `.bbl`, supplementary `.tex`, figures, cover letter, response document, any required forms.

**Success criteria**

- ☐ Every item in the §4 register marked closed, with a one-line note of how.
- ☐ All `check.sh` gates green on a clean build.
- ☐ Clean-clone repository verification exits 0.
- ☐ `latexdiff` PDF generated and reviewed; no unintended changes.
- ☐ Independent co-author sign-off recorded.
- ☐ Response document complete, one entry per reviewer item, each with a location reference into the revised manuscript.
- ☐ Word count ≤ 12,000; keywords 5–8; all statements present; no placeholders.

**Effort:** 10–12 hours (1.5 days), of which the response document is about half.
**Compute:** `latexdiff` + two builds ≈ **3 minutes**; clean-clone install and test ≈ **5 minutes**.

---

### Phase 9 (optional, parallel) — The evidence upgrade

Start this on the same day as Phase 1 if you intend to do it at all. It runs independently of Phases 1–8 and merges at Phase 6.

#### 9a — Execute the elicitation protocol on one domain *(strongly recommended)*

Reviewer 3 and the area chair both single this out: *"One measured parameter set would do more for this paper's credibility than the entire simulation would have."* It attacks the limitation you yourself nominate as binding — that every load-bearing input is an unmeasured author estimate — and it raises the area chair's acceptance estimate from 65–70% to ~80%.

**Scope.** Appendix S4's protocol, run on structural inspection only, with ~12 raters in a single municipality or a single professional body. Report ICC(2,k) against the appendix's stated reliability target. Report the elicited values for φ_m, learn_i, ψ_a and h_raw against the estimates currently in Table `tab:worked-terms`, and re-run the worked example with the measured values beside the estimated ones.

**Why it is worth it even if the numbers move.** If the elicited φ̄ differs from your estimate, the sensitivity sweep already tells you what happens — that is what §6.8 is for. A paper that says "we estimated, then we measured, and here is the difference" is in a different class from one that says "we estimated, and here is a sweep."

**Timeline:** 4–8 weeks, dominated by institutional ethics approval (2–6 weeks depending on institution) and rater recruitment. The analysis itself is a day.
**Effort:** ~40 hours spread across the window (protocol submission, recruitment, sessions, analysis, writing).
**Compute:** negligible — ICC on 12 raters × a dozen items is instantaneous. Budget **under a minute** of machine time.
**Gate:** ICC(2,k) reported; measured values tabulated against estimates; the worked example recomputed under measured inputs; the Limitations bullet "No measured inputs" revised to reflect what is now measured and what is not.

#### 9b — Conduct the specified study (Route B only)

For completeness, the engineering breakdown, measured against what `sim/` actually contains today (~500 lines across engine, strategies, stress and calibration):

| Work package | Content | Effort |
|---|---|---|
| Replace the time-stepped loop with a real DES | Priority-queue event engine, arrival processes per sector, multi-year horizon | 2–3 weeks |
| Six-sector calibration | Fit arrival rates and volume distributions to the five named open portals; archive snapshots | 2 weeks |
| Complete the metric set | 8 of 13 metrics are unimplemented: safety incidents, energy, recovery time, Π_{k,g}, Δ_g, service-equity dispersion, realized dual over time, contestability throughput | 2 weeks |
| Implement ERA (Merlo) | AND/OR-graph role allocation with ergonomic risk estimation, mapped to the nine task dimensions (H6) | 1 week |
| Implement the appeals model | Arrival, standing determination, upheld rate, resolution-time distribution, the 0.05 systemic trigger (H8) | 1 week |
| Wire stress injection into the loop | Four acute scenarios + three chronic, currently defined but not connected | 1 week |
| Statistical pipeline | Wilcoxon signed-rank, Holm–Bonferroni over the declared 60-test family, bootstrap CIs with Shapiro–Wilk pre-test, achieved-power reporting, the seed-raising rule | 1 week |
| OSF pre-registration | Lodge before execution, as §7.7 promises | 2 days |
| Execution, analysis, writing | | 2 weeks |
| **Total** | | **10–14 weeks** |

**Compute model.** Do not guess the runtime — measure it and extrapolate. The dominant cost is the MILP, not the DES. Procedure:
1. Time one weekly rebalance solve at the stated scale (15,400 tasks, 2.2×10⁵ binaries). The manuscript's own Table `tab:runtime` claims 74 s on a 32-core/128 GB machine; treat that as a target to verify, not a given.
2. Per seed per sector per strategy: 520 weekly windows over 10 years. At 74 s/solve that is ~10.7 hours of solver time per (seed, strategy) for the city-wide stream.
3. Full grid: 6 strategies × 30 seeds ≈ 180 runs → **~1,900 core-hours** sequential, before stress scenarios and ablations.
4. Plus 6 ablation configurations × 30 seeds, and 4 acute scenarios × 5 strategies × 30 seeds.
5. Embarrassingly parallel across seeds: on 32 cores, wall clock ≈ **3–7 days** for the main grid, plus 2–4 days for ablations and stress. Budget **1–2 weeks of continuous compute**, and verify the solver licence permits parallel instances.

This is the honest number, and it is the reason Route A is recommended.

---

## 7. The verification harness

Two scripts, written in Phase 0, used in every phase. They are the structural fix for the defect pattern the review identified — *five of nine numerical errors were in prose reporting a correct table*.

**`check.sh` — build and compliance gates**

| Gate | Command | Pass condition |
|---|---|---|
| Builds | `latexmk -pdf -interaction=nonstopmode` | exit 0 |
| No dangling refs | `grep -ci undefined CivicWorkOS.log` | 0 |
| Word count | `texcount -inc -total -q CivicWorkOS.tex` | ≤ 12,000 |
| Typography | `grep -c Overfull CivicWorkOS.log` | 0 |
| Keywords | `grep -c keyword CivicWorkOS.tex` | ≥ 1 |
| No placeholders | `grep -nE '26UQU\(\|\(Staff number\)\|TODO\|TBD\|XXXX'` | no output |
| No deleted-section refs | `grep -nE 'ref\{(tab:mainresults\|tab:ablation\|tab:stress\|tab:runtime\|tab:hypoutcomes\|sec:results)\}'` | no output |
| No past-tense results language | `grep -nE '\b(thirty paired\|30 paired\|was not refuted\|simulated dual)\b'` | no output |
| Artifact verifies | `python scripts/verify_worked_example.py` | exit 0 |

**`audit_numbers.py` — arithmetic gates.** Every number the manuscript prints that can be derived from stated inputs, recomputed and compared at 1e-4. At minimum the list in Phase 0's success criteria, extended in Phase 2 with the §9.1 trajectory values. Share its constants with `scripts/verify_worked_example.py` by import — one definition, two consumers. Two copies of the same constants is how N2 happened.

**Run both at the end of every working session.** Not at the end of every phase — every session. The cost is seconds; the thing it prevents cost this manuscript a rejection.

---

## 8. Schedule

Critical path, assuming one author working focused days. Phase 9a runs in parallel from day 1.

| Day | Phase | Output |
|---|---|---|
| 1 | 0 | Branch, baseline, harness. **Also: request the grant code; start the ethics application if doing 9a.** |
| 2–3 | 1 | §8 deleted, Abstract rebuilt, Data Availability rewritten, orphans swept, article type declared |
| 4 | 2 | All arithmetic reconciled; `audit_numbers.py` green |
| 5 | 3 | Repository matches the manuscript; clean-clone verification passes |
| 6–9 | 4 | ≤ 11,800 words; supplement absorbs the relocated material |
| 9 (half) | 5 | Front matter complete |
| 10–13 | 6 | Intake figure, GCC subsection, CMDP engagement, §1 reframing |
| 14 | 7 | Zero overfull boxes, orthography, bibliography |
| 15–16 | 8 | Gates, latexdiff, independent read, response document, package |

**Total: 16 working days** — slightly above the area chair's two-week estimate, because this programme adds Phase 3 (which the review did not reach) and takes Phase 6 seriously rather than treating it as optional polish.

**Total machine compute across Phases 0–8: well under two hours.** Essentially all of it is LaTeX. The project is bounded by author attention, not by computation. (Route B inverts this: 10–14 weeks of engineering and 1–2 weeks of continuous solver time.)

---

## 9. Risk register and the do-not-do list

| Risk | Why it bites | Mitigation |
|---|---|---|
| **Softening C1 by rewording rather than removing** | A hedged sentence over a fabricated number is still a fabricated number, and it reads worse — it shows the authors knew | Phase 1 gate: no quantity survives that is not exact arithmetic, a closed-form model value, or an explicitly labelled unexecuted target |
| **Grant code arrives late** | Blocks submission after all technical work is done | Request on day 1 |
| **Ethics approval latency (9a)** | 2–6 weeks, outside your control | Start on day 1 or decide now not to do 9a |
| **Length reduction eats the argument** | Compression under deadline removes premises, not just words | Phase 4 gate requires an independent co-author read of the compressed sections |
| **Re-introducing a deleted number** | §8's figures appear in the Abstract, Discussion and Conclusions; one missed site reinstates the whole problem | The `check.sh` grep gates for `63.2`, `86.8`, `0.942`, `52.9`, `thirty paired` |
| **Repository drifts again** | It has already drifted twice (two obsolete section numberings, a stale worked example, a stale author list) | Reference sections by name not number; share constants between the two verification scripts by import |
| **The GCC legal claim is wrong** | A careless legal characterisation in a paper whose §5.3 is praised for care would be a conspicuous own goal | Phase 6 gate requires co-author verification of the legal content |
| **Over-correcting the candour** | §9.3, §9.5 and the §7.1 self-corrections are repeatedly named as strengths; a defensive rewrite would remove the thing reviewers admire | Keep every volunteered limitation. The only changes to those sections are the ones this register names |

**Do not:**

- Submit anywhere before Phase 1 and Phase 3 are both complete. The repository is part of the submission whether or not you think of it that way.
- Keep any §8 number "with a caveat".
- Describe `sim/` as validation, in the manuscript, the README, a cover letter, or a talk.
- Remove the self-critical passages. They are the reason all three reviewers believe the defect was mechanical rather than deliberate, and that belief is why the invitation to resubmit exists.
- Let Phase 4 start before Phase 1 finishes. Compressing text you are about to delete is the easiest way to lose three days.

---

## 10. The response document

Even for a fresh submission, write it. Structure:

**1. Opening statement (one paragraph).** State plainly what the audit found and what you did: that a prior draft's specified-but-unexecuted evaluation targets had been rewritten into past tense; that the section has been removed; that the article is now submitted as Hypothesis and Theory with the worked example and sensitivity frontier carrying the evidence; and that the repository and Data Availability Statement now state the same thing as each other and as the manuscript. Do not minimise and do not over-apologise. A factual, specific account is the strongest available position, and it matches the reviewers' own reading that this was a drafting failure.

**2. Summary-of-changes table.** One row per register ID from §4, with columns: ID · reviewer item · action taken · location in the revised manuscript.

**3. Per-reviewer responses.** Reviewers 1, 2, 3 and the area chair, in order, each item quoted and answered. Three items need particular care:

- **Reviewer 1's Questions 1–3** are the integrity questions. Answer them directly and without hedging. Q1: the study was not run; the section has been removed; the date is "never". Q2: ERA's twelve values had no derivation; it has been removed from all results and retained only as a specified comparator. Q3: the ablation showed the constraint *reduces* CAD; that section is deleted and the claim does not appear in the revised paper.
- **Reviewer 1's W7 / Phase 2 item 5.** State that the robustness claim has been narrowed to what Table `tab:sensitivity` supports, and quote the new wording. Concede that this weakens the paper's self-declared central claim, and say why the narrower claim is still the right one.
- **Reviewer 3's GCC point.** Thank them specifically. It is the most constructive suggestion in the review and acting on it visibly is worth more than the subsection itself.

**4. What was not changed, and why.** There will be a few — perhaps the decision not to conduct the study, perhaps a literature the word limit excludes. State them with reasons. A response that claims to have done everything is less credible than one that says no twice with an argument.

---

## 11. Final pre-submission checklist

Run this immediately before upload. Every box, no exceptions.

**Integrity**
- ☐ No reported result that was not obtained
- ☐ Manuscript, Data Availability Statement, and repository README mutually consistent
- ☐ Article type declared: Hypothesis and Theory
- ☐ Every Abstract number traces to §6 or §9.1 and is reproduced by `audit_numbers.py`

**Compliance**
- ☐ ≤ 12,000 words (measured, with the counting basis confirmed against the journal's current page)
- ☐ 5–8 keywords present and rendered
- ☐ Ethics Statement present
- ☐ Funding and Acknowledgment carry the real grant code
- ☐ Abbreviations populated or absent
- ☐ Corresponding author block renders with name and email
- ☐ Author Contributions free of ambiguous initials
- ☐ Equal-contribution footnote attached or removed
- ☐ `\extraAuth` counts match reality

**Consistency**
- ☐ `audit_numbers.py` all PASS
- ☐ Every prose sentence reporting a table checked against that table for direction, magnitude and unit
- ☐ λ_k value consistent at every site
- ☐ §6.8 robustness claim matches `tab:sensitivity`

**Artifact**
- ☐ Clean clone → install → `verify_worked_example.py` exits 0 against the manuscript's numbers
- ☐ `pytest` exits 0 and matches the README badge
- ☐ Author list identical across manuscript, README and `CITATION.cff`
- ☐ All repository section references match the compiled manuscript
- ☐ Calibration snapshots shipped, or no claim that they are

**Build**
- ☐ Main and supplementary both build clean
- ☐ 0 undefined references, 0 undefined citations, 0 overfull boxes
- ☐ `latexdiff` reviewed

**Human**
- ☐ Independent co-author read against `peer-review.md`, every register item confirmed closed
- ☐ All co-authors have approved the submitted version and the response document
