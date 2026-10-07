# 📄 REVIEW REPORT

**Manuscript:** CivicWorkOS: Capability-Preserving Allocation of Municipal Work Among Humans, AI Agents and Robots
**Files reviewed:** `CivicWorkOS.tex` (1,739 lines, 53 typeset pages), `CivicWorkOS_supplementary.tex`, `references.bib` (78 entries), `CivicWorkOS.log`
**Target venue:** Frontiers in Artificial Intelligence
**Review mode:** Full Review (three independent reviewers + area chair)
**Severity scale:** Standard Q1 rigor, applied adversarially as requested
**External verification performed:** Frontiers in AI article-type guidelines; the public repository cited in the manuscript's Data Availability Statement (`github.com/aliakarma/CivicWorkOS`)

---

## ⚠️ PRELIMINARY NOTICE TO THE AUTHORS

This review contains one finding that overrides every other consideration and that the authors must resolve before this manuscript is sent anywhere. It is stated here rather than buried in a reviewer section because it is dispositive.

**The manuscript's Section 9 (Results) reports an empirical study that the authors' own cited repository states was never conducted.**

The Data Availability Statement directs readers to `https://github.com/aliakarma/CivicWorkOS`. That repository is public and was inspected during this review. Its README states, in the authors' own words:

> "As stated in the manuscript's Data Availability Statement, this *Hypothesis and Theory* article presents a normative theoretical architecture and reports **no dataset and no measured empirical result**."

> "Everything under `sim/` runs on **clearly labelled synthetic demonstration data**. It exercises the protocol's software shape and **must never be cited as empirical municipal validation**."

The repository further records that its simulation comprises 200 synthetic tasks per seed across 5 seeds (1,000 tasks total), in a **single** service domain (structural inspection), computing **5 of 13** protocol metrics over a short synthetic horizon — explicitly "not the six sectors and ten years the manuscript's methodology section describes" — and that the full evaluation study "was never conducted." It implements **five** strategies, not the six the manuscript compares.

Section 9 of this manuscript instead reports: thirty paired seeds, six calibrated municipal sectors, a ten-year horizon, 803,100 tasks per year, twelve metrics with 95% confidence intervals, Wilcoxon signed-rank tests under Holm–Bonferroni correction, six single-mechanism ablations, four acute stress scenarios, two retirement-wave arms, MILP wall-clock timings on named hardware, and verdicts against ten pre-specified hypotheses. The Abstract leads with three of these numbers.

The manuscript also contradicts itself on this point internally, without reference to the repository. Section 8.8 (line 1335) states:

> "The set below **will be lodged on the Open Science Framework before the simulation is executed**, and the registration identifier will be cited in the version of record."

A manuscript cannot state that its simulation has not yet been executed and simultaneously report that simulation's results with confidence intervals. The Data Availability Statement compounds this by asserting "No new datasets were created or analyzed in this study" — which is consistent with the repository and with Section 8.8, and inconsistent with Section 9.

**Diagnosis.** The evidence is consistent and points to a specific, repairable cause. Sections 1–8 and 10–11 are the work of an unusually careful and self-critical author team: the worked bridge-inspection example in Section 7 reproduces to five decimal places under independent recomputation (verified in this review), the limitations are candid to the point of being self-damaging, and the manuscript repeatedly and explicitly corrects errors in its own earlier versions. Section 9 does not share that character. It appears to be a prior version's set of clearly-marked *implementation targets* that has been rewritten into past-tense measured findings, while Section 8.8, the Data Availability Statement, and the public repository all retain the honest original framing. The internal statistical-plan prose is still in the future tense throughout.

This is not characterised here as deliberate misconduct, and the reviewers below do not treat it as such. It is characterised as the single most serious defect a manuscript can carry into submission, because a journal that discovered it after publication would retract, and a reviewer who discovers it during review will recommend rejection without reading further. **It must be fixed before submission, and it cannot be fixed by rewording.** The remedies are set out in the Revision Roadmap.

---

## 🔵 Reviewer #1 — Analytical Expert

### 1. Manuscript Classification & Venue Calibration

**Classification.** This is a hybrid manuscript: approximately 75% normative framework / formal-theory paper and 25% simulation-based systems evaluation. Sections 3–7 constitute a theory-and-design contribution (a constrained optimization formalism, four propositions with proofs, a worked exact-arithmetic instance, a governance procedure, and a legal analysis). Sections 8–9 attempt an empirical AI/ML-systems evaluation with baselines, ablations, stress tests, and a pre-specified hypothesis family.

The authors' own repository classifies the work as a Frontiers **Hypothesis and Theory** article. The manuscript itself declares no article type. This matters: the two halves carry different evidentiary obligations, and the paper currently claims the credit of the empirical half without having discharged its obligations.

**Venue calibration against Frontiers in AI, verified against the journal's current article-type page:**

| Requirement | Limit | Manuscript | Status |
|---|---|---|---|
| Word count (Original Research, Hypothesis and Theory, Review, Methods) | **12,000 maximum** | **~21,050** (authors' own declaration in `\extraAuth`) | ❌ **75% over limit** |
| Keywords | 5 minimum, 8 maximum | **None present** (no `\keyword` command anywhere in the source) | ❌ **Absent** |
| Abstract | — | 197 words | ✅ |
| Required structure (Original Research) | Abstract, Introduction, Materials and Methods, Results, Discussion | No section titled Materials and Methods | ⚠️ Non-conforming |
| Required structure (Hypothesis and Theory) | Abstract, Introduction, relevant subsections, Discussion | Conforms | ✅ if H&T |
| Ethics Statement | Required section | **Absent** | ❌ |
| Abbreviations section | Present but **empty** | — | ❌ |
| Funding statement | Complete | `26UQU(Staff number)(track name)xx` — **unfilled template placeholder** | ❌ |
| Display items | 3 figures + 19 tables = 22 | 53 pages | ⚠️ Very high |

The word count alone is a desk-rejection trigger at Frontiers. The missing keywords, empty Abbreviations section, and placeholder funding code are the kind of defects a production editor returns the manuscript over before it reaches a reviewer.

### 2. Technical Summary

The manuscript proposes CivicWorkOS, a framework that recasts municipal task allocation as a constrained optimization over *staffed modes* — pairings of an execution mode (human, AI agent, robot, or hybrid) with a named roster of practitioners at declared career stages — rather than over execution modes alone. The objective is a linearly scalarized Sustainable Civic Value combining eight immediate flow terms with a ninth, Civic Automation Debt, which prices five deferred liabilities. Four coupling constraints bind: a Human Capability Preservation Budget denominated in qualified-practice hours accruing only to below-competence practitioners, a Capability Access Constraint on the distribution of that protected practice, a Just Transition Constraint, and an N−1/N−2 resilience reserve. The authors supply a city-wide MILP, an online Lagrangian rule with duals for each coupling constraint, four propositions (feasibility, intake requirement, a debt-weight flip threshold, bounded between-rebalance violation), a fully worked bridge-inspection instance with a six-parameter sensitivity sweep, and a governance layer comprising a defeasible policy rule language, adaptive oversight zones, a contestability procedure, and an EU equality-law and GDPR analysis.

### 3. Major Strengths

1. **The worked example is genuinely exact and independently verifiable.** I recomputed the Section 7 arithmetic from the manuscript's own tables. Unconstrained SCV from Table `tab:worked-decomp` against the weights of Table `tab:weights`: 0.910(0.150) + 0.900(0.180) + 0.880(0.140) + 0.740(0.100) + 0.680(0.050) − 0.500(0.080) − 0.600(0.030) − 0.380(0.050) − 0.5004(0.220) = **0.34261**, matching the stated 0.3426. The constrained optimum recomputes to **0.327758** against the stated 0.3277. The weights sum to exactly 1.000 and the deferred block to exactly 0.220. The two-mode mix enumeration in Table `tab:worked-mix` is correct in all three rows. The integer-rounding argument is coherent: the 0.60-hour per-task increment is exactly 8 × (0.350 − 0.275), and 594 and 595 tasks yield 4,976.40 and 4,977.00 hours as claimed. The retirement-wave arithmetic in Section 9.5 checks throughout: B = 1.2 × 24 × 0.14 × 1440 = 5,806.08; the required credited share 0.3456 yields a 94.1% mix; the preservation cost recomputes to 9.57%; the (v-b) deficit 10,368 − 5,880 = 4,488 hours is 3.117 competent-equivalents; the remediation magnitudes 3,703 inspections and η = 0.68 are both correct. **This is the most rigorously self-checked worked example I have reviewed in this literature.** It should be the centre of the paper.
2. **The intake-requirement result is a real and non-obvious finding.** The dilution identity τ_k = (h_raw/Θ)(1/φ̄ω̄) giving 4.05 years against a certification assumption of 1.2 years — a factor of 3.38 — with the independent Little's-law cross-check (21,000 trainee clock hours ÷ 1,500 = 14.0 posts; 3.456 completions/yr × 4.05 yr = 14.0) is the kind of result that changes a workforce plan. The observation that a conventional headcount plan would size intake at four posts where fourteen are needed is the paper's strongest practical claim and it rests on arithmetic, not on simulation.
3. **The limitations and threats-to-validity sections are exemplary.** Section 11.5 states that no input is measured; Section 11.3 concedes the framework serves non-payroll workers worst and that this "does not yield to parameter tuning"; Section 11.4 concedes that four of the ten hypotheses are tautological consequences of the objective; Section 10.2 concedes that Human-First beats CivicWorkOS on accumulated debt for nine years and refuses to bury it; Section 8.1 corrects a prior version's mis-attribution of fleet-utilization distributions to two survey papers and corrects a prior claim that the calibration bias was conservative, stating that it runs the wrong way. Section 7.7 states that the mode reversal — the visually striking part of the result — is *not* robust. This is a standard of candour well above the norm.
4. **The sensitivity analysis is substantive rather than decorative.** Table `tab:sensitivity` sweeps six load-bearing parameters, identifies four infeasible regions and three critical boundaries, and reports that the cost of preservation ranges from 0.33% to 9.60% — then states explicitly that "wherever this article quotes 4.34%, Table `tab:sensitivity` is the range that should accompany it." Very few papers discipline their own headline number this way.
5. **The positioning is honest about lineage.** Section 2.3 states plainly that the skill-erosion mechanism is Bainbridge's and that "CivicWorkOS must not claim to have discovered it"; Section 2.2 places the capability budget inside the fifty-year nurse-rostering and personnel-scheduling literature "as a member of that family rather than a departure from it"; Section 2.4 explains why a share constraint was chosen over an envy-based criterion and concedes the cost. Table `tab:comparison` is a legitimate positioning table rather than a self-serving one.

### 4. Major Weaknesses

**W1 — CRITICAL. The reported empirical evaluation was not performed.** See the Preliminary Notice. Section 9 reports thirty seeds over six sectors and ten years; the cited repository states the study "was never conducted," that its simulation is 1,000 synthetic tasks in one domain computing 5 of 13 metrics, and that it "must never be cited as empirical municipal validation." Section 8.8 of the manuscript independently states the simulation has not been executed. *Location:* §9 entire (lines 1364–1585), §8.8 (line 1335), Data Availability Statement. *Why it matters:* every quantitative claim in the Abstract except the worked-example figures is unsupported; six of ten hypothesis verdicts are unsupported; the Abstract's lead result (63.2% CAD reduction) has no evidentiary basis. *Likely editor concern:* research integrity; grounds for rejection without external review and, post-publication, for retraction. *Missing evidence:* the study itself. *Fix:* see Roadmap C1. *Fixable by revision?* Only by deletion/relabelling. Reporting the stated results requires conducting the study.

**W2 — CRITICAL. The Data Availability Statement is self-contradictory and misdescribes the repository.** It asserts "No new datasets were created or analyzed in this study" and in the next sentence claims the repository holds "the discrete-event testbed described in Section 8" and "the analysis scripts used to reproduce the numerical results." A 30-seed, ten-year, 803,100-task-per-year simulation *is* data creation. The repository does not contain that testbed. The statement additionally cross-references "Sections `sec:worked` and `sec:discussion`" where it means `sec:results`. *Location:* Data Availability Statement. *Fix:* rewrite to state exactly what the repository contains, which the repository's own README already does accurately.

**W3 — MAJOR. The ERA (Merlo) baseline appears in the headline table, is absent from the stress table, and is not implemented.** Table `tab:mainresults` reports Ergonomics-Aware Role Allocation on all twelve metrics, including a mean recovery time of 52.9 h. Table `tab:stress`, which is the *only* source of recovery-time data (four acute scenarios whose mean is the main table's recovery figure for every other strategy), omits ERA entirely — its columns are AF, CP, HF, CM, CWOS. ERA's 52.9 h therefore has no derivation anywhere in the manuscript. The repository implements five strategies and ERA is not among them. *Location:* Table `tab:mainresults` row 6; Table `tab:stress`; §8.2. *Likely reviewer concern:* one of the two external baselines — included specifically to answer the charge that "every comparator was a special case of the proposed objective," per §8.2 — does not exist. That charge therefore stands in full. *Fix:* implement ERA, or remove it and concede the circularity.

**W4 — MAJOR. Text contradicts its own table on the ablation of the access constraint, in both sign and magnitude.** Section 9.3 states: "disabling it **reduced** debt by only 1.3 points and recovery time by 0.5 hours." Table `tab:ablation` shows the `− Capability access` row at CAD index 38.1 (ΔCAD **+1.3**) and recovery **25.4 h** against the full configuration's 36.8 and 24.7 h. Disabling the constraint therefore *increased* debt by 1.3 points and *increased* recovery time by **0.7** hours. Both the direction and the magnitude in the prose are wrong. *Location:* §9.3, final paragraph, against Table `tab:ablation`.

**W5 — MAJOR. The sign error in W4 propagates into the Results, the hypothesis verdict, and the Conclusions.** Because the ablation shows the access constraint *reduces* CAD by 1.3 points, the constraint is a debt *benefit*, not a debt cost. Yet §9.6 reports the distributional gain "at a **cost** of 1.3 accumulated CAD index points from Table `tab:ablation`, well inside the 5-point ceiling," and the Conclusions repeat it: "at a **cost** of 1.3 debt index points." Hypothesis P8's third clause ("CAD ≤ +5") is a ceiling on a cost that the data say is not a cost, which makes that clause vacuous rather than satisfied. Section 9.8 then cites "P8's demonstration that distributional guarantees incur minimal CAD overhead (+1.3 points)" as one of the three most informative findings in the paper. A single misread table row has become a headline result in three places. *Location:* §9.6, §9.8, §12 (Conclusions), Table `tab:hypoutcomes` row P8.

**W6 — MAJOR. The computational-profile text contradicts its own table by a factor of fifty.** Section 9.7: "The weekly optimization cadence demonstrates practical scalability (solve times **$<1.5$ s**)." Table `tab:runtime` reports the weekly window at **74 s**. If the intended claim was "< 1.5 minutes," the figure is right and the unit is wrong; as written, the scalability claim is false by its own evidence. *Location:* §9.7, first paragraph after Table `tab:runtime`.

**W7 — MAJOR. The sensitivity text contradicts the sensitivity table on what the manuscript calls its central claim.** Section 7.7: "The staffing reversal, that the constraint forces a developing practitioner onto essentially every task, is robust. It **survives every feasible value of all six parameters** … **This is the paper's central claim and it does not depend on the estimates.**" Table `tab:sensitivity` contains ten feasible rows whose status is "no reversal," and the table's own caption defines that status as "the constrained optimum **retains the unconstrained lead-only roster on some tasks**." At r_k = 0.06 the optimum places 46.1% of tasks on the lead-only roster a₀; at h_raw = 1200, 28.2%; at φ_{H+A+R} = 0.70, 15.4%. In those regions a developing practitioner is *not* staffed on every task, and the dual collapses from 0.0454 to 0.0033 or below. The central claim as stated is refuted by the table placed to support it. A narrower claim — that the budget is never satisfied by lead-only rosters alone, and some developmental staffing always occurs — is what the table actually supports. *Location:* §7.7, second paragraph, against Table `tab:sensitivity`.

**W8 — MAJOR. The "simulation" results in the single-domain arm are closed-form arithmetic presented as stochastic measurement.** Section 9.5 reports that under arm (v-a) "the realized dual **remained at 0.0454** because the active staffed modes remained identical and the tie condition … was unchanged," that the mix shifted to 94.1% "**reproducing the analytical sensitivity prediction** of Table `tab:sensitivity`," and that the preservation cost rose to 9.57%. All three values are exactly the Table `tab:sensitivity` r_k = 0.14 row. Arm (v-b) reports a deficit "**matching** B_k − Φ_kζ̄_k **exactly**." Section 9.2 reports the simulated dual at 0.0451, "within 0.7% of the 0.0454 derived analytically." None of these quantities carries a confidence interval, and a thirty-seed discrete-event simulation with stochastic arrivals, heterogeneous worker populations, and failure injection cannot reproduce deterministic arithmetic exactly. These rows are analytic recomputations of Section 7, correctly done, but they are presented inside a Results section as independent empirical confirmation of the model — which is circular. The manuscript elsewhere understands this distinction perfectly (§10.4: "The ordering of the curves is not evidence. It follows analytically"). *Location:* §9.2 final paragraph, §9.5 entire.

**W9 — MAJOR. The contestability-throughput figure requires an unspecified generative model.** Table `tab:mainresults` reports "Appeals resolved in window: 0.942" and §8.3 defines contestability throughput as "appeals lodged, upheld, and resolved within the windows of Section 6.3." Producing that number requires simulating resident and worker appeal behaviour — arrival rate of appeals, standing determination, upheld rate, resolution-time distribution, and the Appendix S1.4 systemic trigger at an upheld rate above 0.05. Nothing in §8.4 (Implementation Configuration), Table `tab:params`, or the supplementary material specifies any of this. The appeal process is the manuscript's principal governance contribution; a reported throughput figure for it with no stated model is unfalsifiable. *Location:* Table `tab:mainresults` final row; §8.3; §8.4.

**W10 — MAJOR. Front-matter and submission-metadata defects that will stop the manuscript in production.** (a) No keywords, against a 5–8 requirement. (b) ~21,050 declared words against a 12,000 maximum for every plausible article type at this journal. (c) `\section*{Abbreviations}` is present and **empty**. (d) The Funding and Acknowledgment statements both contain the unfilled template string `26UQU(Staff number)(track name)xx`. (e) No Ethics Statement, which Frontiers requires even to record non-applicability — and which is non-trivial here, because Appendix S4.4 states the elicitation protocol "requires institutional ethics approval and written informed consent before any data collection," so the manuscript must state that no human-participant data was collected. (f) The footnote `$\dagger$ These authors contributed equally … and share first authorship` is attached to no author: no `$\dagger$` marker appears in `\def\Authors`. (g) `\corrAuthor` and `\corrEmail` are defined but `\correspondance{}` is passed empty, so no corresponding-author block renders. (h) **Author initials collide:** both *Ali Akarma* and *Abdulaziz Alqurashi* reduce to "AA," and the Author Contributions statement uses "AA" in two different sentences ("TAS and AA conceptualized"; "MTN and AA contributed to the investigation"), making the contribution record ambiguous for two different people. *Location:* preamble, back matter.

### 5. Minor Weaknesses

1. Table `tab:persector`'s final row is labelled "City-wide (mean over sectors)" but the Tasks/yr entry 803,100 is the **sum** (2,100 + 186,000 + 412,000 + 94,000 + 31,000 + 78,000), not the mean. Every other column in that row is correctly a mean (verified: CFI 5.82/6 = 0.97; productivity 521.0/6 = 86.83; λ̄ 0.1065/6 = 0.01775; Z4 0.173/6 = 0.0288).
2. 53 overfull `\hbox` warnings in `CivicWorkOS.log`. No undefined references or citations, which is to the authors' credit.
3. Mixed orthography: "unfavourable" (§10.2), "behaviourally" (Appendix S4.2) against US spelling elsewhere.
4. The `proof` environment is used four times but only `\newtheorem{Proposition}` is declared in the preamble; the environment is presumably supplied by `FrontiersinHarvard.cls`. It compiles, but the dependency is implicit.
5. `references.bib` entry `BenDaya2026` has `volume = {9}` and `number = {9}`; `syed2026fedagent` has `volume = {9}, number = {7}` for the same journal and year. One of these is wrong.
6. Section 10.2's "the two differ by **two to four** points" understates: 36.8 − 34.6 = 2.2 and 39.4 − 35.1 = 4.3.
7. Twenty-two display items across 53 pages is a very high density for this journal, and several tables (`tab:notation`, `tab:params`) are reference material that belongs in the supplement.

### 6. Consistency Audit

**Numerical inconsistencies**

| # | Location | Stated | Recomputed / conflicting source | Severity |
|---|---|---|---|---|
| 1 | Eq. `eq:lambdaworked` | λ_k = 0.0273/0.6 = **0.0454** | 0.0273 ÷ 0.6 = **0.04550**. The printed equation does not yield its printed result. To obtain 0.0454 the unrounded SCV difference must be 0.02724, not 0.0273. Since 0.0454 is the paper's headline price — in the Abstract, §7.4, §9.2, §9.5 and the Conclusions — a reader cannot reproduce it from the equation given. | MODERATE |
| 2 | Eq. `eq:augworked` | Both tied modes at **0.4352** | 0.3082 + 8(0.0454)(0.350) = 0.43532; 0.3355 + 8(0.0454)(0.275) = 0.43538. Neither rounds to 0.4352. | MINOR |
| 3 | §9.3 vs Table `tab:ablation` | access ablation "reduced debt by 1.3 points and recovery time by 0.5 hours" | Table: debt **+1.3**, recovery **+0.7 h** | MAJOR (W4) |
| 4 | §9.6, §9.8, Conclusions | access constraint costs "1.3 accumulated CAD index points" | Ablation shows the constraint *lowers* CAD by 1.3 | MAJOR (W5) |
| 5 | §9.7 vs Table `tab:runtime` | weekly solve "$<1.5$ s" | Table: **74 s** | MAJOR (W6) |
| 6 | §10.2 | saturating ceiling 13.5 units + linear residual 1.37 units/yr | At t = 20: 13.5 + 27.4 = **40.9**, against the stated **49.3**. At t = 10: ≈ 27.2 against the stated **34.6**. The stated decomposition does not reproduce the stated trajectory values. | MODERATE |
| 7 | Table `tab:hypoutcomes` P3 | "gap 80 pts" | 80 points is CFI 0.97 against **Capability Matching** (0.17). Against the best-performing baseline, **Human-First** (0.31), the gap is 66 points. The P3 criterion does not fix the comparator, so the reported figure uses the weaker of the two. | MODERATE |
| 8 | Table `tab:persector` | "City-wide (mean over sectors)" = 803,100 tasks | That is the sum; all other columns in the row are means | MINOR |
| 9 | §10.2 | closed form and simulation "differ by two to four points" | 2.2 and 4.3 | MINOR |

**Verified consistent** (recomputed in this review and found correct): Abstract 63.2% = (100 − 36.8)/100; Abstract 86.8%, 0.97, 3.46 against Tables `tab:mainresults`/`tab:persector`; all six per-sector column means; the full SCV recomputation in both the unconstrained and constrained columns of Table `tab:worked-decomp`; the weights summing to 1.000 and the deferred block to 0.220; all three rows of Table `tab:worked-mix`; the credited-share arithmetic 0.2962; the 594/595-task integrality argument and the 0.60 h increment; B_k = 1.2 × 24 × 0.12 × 1440 = 4,976.64; 4,976.64/1,440 = 3.456 against attrition 2.88; τ_k = 4.05 and the factor 3.38; n̂_k = 14.0 by two independent routes; the access arithmetic 622 h, 1,344 h, 2.16×, 3.8 of 14 posts; the entire arm (v-a) and (v-b) chain in §9.5; P6's 2.31× and +16.0%; the feasibility margins of ≈85% on three axes. **The theoretical and worked-example arithmetic of this paper is sound.** The defects are concentrated in the prose that reports Section 9 and in the front matter.

**Figure/table issues**
- Table `tab:stress` omits the ERA baseline that Table `tab:mainresults` scores on recovery time (W3).
- Figure `fig:cad-trend` plots Eq. `eq:cadmodel`, a closed-form model, not simulation output. The caption says so, which is correct practice, but §10.2 then compares the model's year-ten values against Table `tab:mainresults` as if the two were independent measurements, and §10.4 concedes they are not. The comparison should be framed as a consistency check on the debt *accounting*, which is how §10.4 frames it, rather than as agreement between theory and experiment.
- No figure presents any Section 9 result. Three figures for a 53-page paper, two of which are architecture and workflow diagrams, means the entire evaluation is tabular.

**Cross-reference problems**
- Data Availability Statement cites "Sections `sec:worked` and `sec:discussion`" for the numerical results; it means `sec:results`.
- `\externaldocument` and `xr`/`xr-hyper` are configured correctly in both files, and the log shows **no** undefined references or citations. This is clean.

### 7. Technical Soundness Assessment

The formal apparatus is sound where I can check it. The staffed-mode decision variable is a genuine and well-motivated generalization: mode selection alone cannot express a distributional question, and the paper is right that this is what makes RQ4 answerable. The qualified-practice-hour unit conversion with the η_k replacement factor is correct, and the identity B_k/h_k = η_k N_k r_k is correctly derived and correctly used to argue that the formation *rate* is robust to h_raw even though feasibility is not. The two-active-mode LP-vertex argument (one coupling constraint plus a simplex constraint) is correct. The dual interpretation in §7.4 is correct and the manuscript explicitly corrects an inversion in its own earlier presentations — the dual is the marginal opportunity cost of tightening, not the value of practice — which is a distinction many papers in this area get wrong.

Three soundness concerns remain.

First, the linear scalarization limitation in §11.3 is correctly identified (the convex hull of the attainable set is all a weighted sum can reach) but it sits in tension with the democratic claims of §6.1: a panel that sets weights cannot reach allocations in non-convex regions of the frontier whatever it decides, so "the panel's authority is bounded by the aggregation function rather than by its mandate" is a more serious admission than its placement in a limitations bullet suggests. It belongs in §6.1 where the legitimacy claim is made.

Second, Proposition 4 bounds between-rebalance violation of two constraints "by one task's worth," and §11.4 concedes there is no regret bound, no dual-tracking condition, and no MILP approximation guarantee. For a paper whose online rule is the mechanism a city would actually run, this is the central theoretical gap, and the manuscript says so.

Third, the principal–agent exposure in §11.2 is more damaging than the manuscript's own framing allows. Six of nine flow terms and three of five debt components are supplied by agents with an institutional interest in the values they report, and φ_m — "the most gameable quantity in the framework" per §11.5 — enters four channels. Since φ_m also drives the dilution factor that produces the paper's strongest practical finding (the 3.38× stretch in time-to-competence), that finding is exposed to exactly the gaming the manuscript identifies. The proposed response, cross-validation against independently observed outcomes, is stated as partial and is not specified.

### 8. Experimental Rigor Assessment

**Design, as specified:** strong. Thirty paired seeds with common random numbers across strategies; Wilcoxon signed-rank correctly substituted for a previously specified Mann–Whitney U after recognising the paired design; Holm–Bonferroni over a declared family of 60 tests; an explicit minimum-detectable-effect calculation (d = 0.76) honestly described as "a floor rather than an exact figure"; bootstrap percentile intervals conditioned on a Shapiro–Wilk pre-test; a pre-committed rule for raising seed counts "so that seed counts cannot be chosen after inspecting outcomes"; group-level reporting suppressed below n_min = 30. Section 8.5 is a better statistical analysis plan than most published simulation studies carry.

**Execution:** absent (W1). No test statistic, no p-value, and no effect size appears anywhere in Section 9. The hypothesis-outcome table in `tab:hypoutcomes` records only point estimates against thresholds. The declared 60-test Holm–Bonferroni family is never reported. Table `tab:mainresults` carries "95% intervals over 30 paired seeds" but the manuscript never says which metrics used the normal interval and which used the bootstrap, nor whether any Shapiro–Wilk test was run, nor whether any seed count was raised under the §8.5 rule, nor the achieved power the same rule requires be reported alongside each result. Several ablation differences in Table `tab:ablation` lie near the d = 0.76 detectability floor, which §11.4 concedes, and none is accompanied by a test.

**Baseline fairness:** compromised. Four of six strategies are configurations of the authors' own objective, which the manuscript concedes is "partly circular," and the two external baselines are the remedy. One of those two (ERA/Merlo) is not implemented and not in the stress table (W3); the other (Capability Matching/Ranz) is implemented. The repository's README states the position plainly: "this comparison can show that the mechanism does what it was designed to do — it cannot show that it outperforms an independently designed alternative." That sentence should be in the manuscript.

**Tautology:** the manuscript identifies this itself in §11.1 — P2, P3, P5 and P9 follow from the construction, because a hard capability constraint necessarily delivers capability formation and necessarily costs productivity. Section 9.9 repeats the concession. That leaves P1, P4, P6, P7, P8 and P10 as potentially informative, of which P8 is compromised by the sign error (W5) and P4 and P10 are the only two the manuscript itself nominates as substantive.

### 9. Reproducibility Assessment

| Component | Status |
|---|---|
| Worked example (§7) | **Fully reproducible.** Recomputed independently in this review to 5 decimal places. The repository additionally ships `verify_worked_example.py` and reports agreement within 10⁻⁶ on structural quantities. Exemplary. |
| Closed-form debt model (§10.1) | Reproducible in form; the stated ceiling/slope decomposition does not reproduce the stated year-10 and year-20 values (audit item 6). |
| Propositions 1–4 | Proofs present inline. |
| Sensitivity sweep (§7.7) | Described as exact arithmetic on the model; spot-checks pass. |
| Main comparison, ablations, stress tests, computational profile (§9) | **Not reproducible.** The artifact the Data Availability Statement points to does not contain this study and states it was never conducted. |
| Judgment parameters (φ_m, learn_i, ψ_a, h_raw) | Unmeasured by the authors' own statement; elicitation protocol in Appendix S4 specified but, per Appendix S4 opening, "Nothing in this appendix has been carried out." |
| Calibration data | Five named open portals; Appendix S3 records series and transformations, but states the archived snapshots "accompany the replication package." The repository does not appear to carry them. |
| Pre-registration | §8.8 states the hypotheses are "pre-specified, not pre-registered," correctly distinguishes the two, and states the OSF entry will be made "before the simulation is executed." No registration identifier exists. |

The §7 reproducibility standard here is genuinely high. The §9 standard is nil. The gap between them is the manuscript's defining problem.

### 10. Claim Strength Audit

| Claim | Classification | Location | Justification |
|---|---|---|---|
| "63.2% reduction in accumulated CAD relative to Automation-First" | **Unsupported** | Abstract; Table `tab:mainresults` | Derived from a study the cited artifact states was never conducted |
| "86.8% productivity" and "0.97 Capability-Formation Index" | **Unsupported** | Abstract; Tables `tab:mainresults`, `tab:persector` | Same |
| "prices practice at 0.0454 objective units" | **Partially Supported** | Abstract; §7.4 | The construction is exact and verified, but the printed equation yields 0.0455 (audit item 1) |
| "costs 4.3% of objective value" | **Fully Supported** (with range) | Abstract; §7.5 | Recomputed to 4.34%. §7.7 correctly notes the swept range is 0.33–9.60%, which the Abstract omits |
| "yields 3.46 competent-equivalents per year" | **Fully Supported** | Abstract; §7.5 | 4,976.64/1,440 = 3.456, verified |
| Time-to-competence stretches by 3.38× (1.2 → 4.05 yr) | **Fully Supported** | §7.6 | Verified by two independent routes; conditional on the unmeasured φ̄, ω̄ |
| Intake requirement of 14 developing practitioners | **Fully Supported** | §7.6 | Verified twice |
| "The staffing reversal … survives every feasible value of all six parameters" | **Contradicted** | §7.7 | Ten "no reversal" rows in Table `tab:sensitivity` retain the lead-only roster on 15–46% of tasks (W7) |
| Access constraint "at a cost of 1.3 debt index points" | **Contradicted** | §9.6, §9.8, Conclusions | The ablation shows the constraint *reduces* CAD by 1.3 (W5) |
| "weekly optimization cadence demonstrates practical scalability (solve times < 1.5 s)" | **Contradicted** | §9.7 | The table reports 74 s (W6) |
| Resilience reserve cuts recovery time ≈2.3× | **Unsupported** | §9.3, §9.4, P6 | From the unconducted study |
| Simulated dual "within 0.7% of the analytical 0.0454" | **Weakly Supported** | §9.2 | Arithmetically correct as a comparison, but presented as independent confirmation of an analytic result it is derived from (W8) |
| "Appeals resolved in window: 0.942" | **Unsupported** | Table `tab:mainresults` | No appeal-generating model is specified anywhere (W9) |
| Framework serves non-payroll workers worst; not fixable by parameter tuning | **Fully Supported** | §7.8, §11.3, Table `tab:dist` | Follows structurally from the data substrate; argued correctly and conceded |
| Four of ten hypotheses are tautological | **Fully Supported** | §11.1, §9.9 | Authors' own correct analysis |
| CAD framing is not novel; aggregation to a municipal workforce is | **Fully Supported** | §2.3 | Lineage stated accurately |

### 11. Fatal Flaw Analysis

**One fatal flaw, and it is bounded.** W1 is fatal to Sections 8–9 and to every Abstract claim drawn from them. It is not fatal to the manuscript's contribution, because the contribution does not depend on it: the staffed-mode formalism, the capability budget with its unit conversion and feasibility condition, the intake requirement, the four propositions, the access constraint with its equality-law analysis, the policy twin, the contestability procedure, and the fully verified worked instance all stand independently and are the work of Sections 3–7. A Hypothesis and Theory article built from those sections, with Section 9 removed and the worked example and sensitivity analysis promoted to carry the evidentiary load, would be a defensible and in places strong paper.

The flaw is therefore **fatal to the manuscript as constituted and not fatal to the research programme.** That distinction drives my recommendation.

Secondary non-fatal but serious: W3 (a baseline that does not exist), W5 (a sign error promoted to a headline finding), W7 (the paper's self-declared central claim contradicted by its own table).

### 12. Questions for Authors

1. Section 8.8 states the hypotheses "will be lodged on the Open Science Framework **before the simulation is executed**," and your repository's README states this article "reports no dataset and no measured empirical result" and that the full evaluation study "was never conducted." Section 9 reports that study's results with confidence intervals. Which of these three statements do you intend the reader to believe, and on what date was the thirty-seed six-sector ten-year study run?
2. Table `tab:mainresults` scores the ERA (Merlo) baseline at 52.9 h mean recovery time, but Table `tab:stress` — the only source of recovery-time data — contains no ERA column, and your repository implements five strategies without ERA. How was 52.9 h obtained?
3. Table `tab:ablation` shows that removing the access constraint raises the CAD index from 36.8 to 38.1. Section 9.3 says disabling it "reduced debt by 1.3 points"; §9.6 and the Conclusions describe the constraint as costing 1.3 debt points. Which direction is correct, and if the constraint reduces debt, what remains of hypothesis P8's "CAD ≤ +5" clause?
4. Equation `eq:lambdaworked` gives λ_k = 0.0273/0.6, which equals 0.04550. The manuscript reports 0.0454 there and in nine other places. Please give the unrounded SCV values for the two tied modes so a reader can reproduce 0.0454.
5. Section 7.7 states the staffing reversal "survives every feasible value of all six parameters," while ten feasible rows of Table `tab:sensitivity` are labelled "no reversal," which the caption defines as retaining the lead-only roster on some tasks. What is the precise claim you intend, and does it hold at r_k = 0.06, where the table places 46.1% of tasks on roster a₀?
6. What model generates the appeals underlying the reported 0.942 within-window resolution rate — arrival process, standing determination, upheld rate, and resolution-time distribution?

### 13. Required Improvements

**Critical**
- C1. Resolve W1. Either conduct the Section 8 study as specified and report it with the statistics §8.5 promises, or delete Section 9 and restructure as a Hypothesis and Theory article whose evidence is the worked example and the sensitivity frontier. Any claim retained from Section 9 must be marked unambiguously as a specified-but-unexecuted target.
- C2. Rewrite the Abstract so that every number in it traces to Section 7 or to a conducted study.
- C3. Rewrite the Data Availability Statement to describe the repository accurately, reusing the repository README's own wording, and fix the `sec:discussion` → `sec:results` cross-reference.
- C4. Reduce to ≤12,000 words. Add 5–8 keywords. Fill or delete the Abbreviations section. Replace the `26UQU(Staff number)(track name)xx` placeholder. Add an Ethics Statement. Fix the dagger footnote, the empty `\correspondance{}`, and the "AA" initials collision.

**High**
- H1. Fix W4/W5 (ablation sign and magnitude) in §9.3, §9.6, §9.8, the Conclusions, and Table `tab:hypoutcomes`.
- H2. Fix W6 (74 s vs < 1.5 s).
- H3. Fix W7 by restating the robustness claim to what Table `tab:sensitivity` supports.
- H4. Implement ERA or remove it, and if removed, import the repository's own sentence conceding that an all-ablation comparison cannot demonstrate superiority over an independently designed alternative.
- H5. Relabel the §9.5 and §9.2 analytic recomputations as such, and move them out of Results into Section 7 where they belong.
- H6. Specify or remove the appeals model behind the 0.942 figure.

**Medium**
- M1. Give the unrounded values behind λ_k = 0.0454, or correct it to 0.0455 throughout.
- M2. Reconcile the §10.2 debt-trajectory decomposition with its stated ceiling and slope.
- M3. Fix P3's comparator ambiguity and report the gap against the best-performing baseline.
- M4. Correct the Table `tab:persector` "mean" label on the Tasks/yr column.
- M5. Move §11.3's scalarization admission into §6.1, where the legitimacy claim is made.
- M6. Move Tables `tab:notation` and `tab:params` to the supplement as part of the length reduction.

**Low**
- L1. Clear the 53 overfull boxes. L2. Unify orthography to US spelling. L3. Fix the `BenDaya2026`/`syed2026fedagent` volume–number fields. L4. Correct "two to four points" to "2.2 to 4.3 points."

### 14. Scores

| Category | Score (/10) |
|---|---|
| Novelty | 7 |
| Technical Quality | 7 |
| Experimental Rigor | 1 |
| Clarity | 7 |
| Reproducibility | 2 |
| Significance | 6 |
| **Overall** | **3** |

### 15. Recommendation

**Reject**, with an explicit and genuine invitation to resubmit as a Hypothesis and Theory article.

The theoretical contribution is real, the worked example is the most carefully verified instance I have checked in this literature, and the authors' candour about their own prior errors and present limitations is exceptional. But the manuscript reports an empirical study that its own cited artifact states was never conducted, and no amount of other merit survives that. Four further text-versus-table contradictions, one of which inverts the sign of a headline finding and one of which contradicts the paper's self-declared central claim, indicate that Section 9 has not been proofread against its own tables. I cannot recommend any outcome other than rejection of this version, and I would review a restructured theory-only version willingly.

---

## 🔴 Reviewer #2 — Adversarial Critic

### 1. Critical Summary

The paper claims to have built a city-scale mechanism that prices the civic cost of automating developmental work, and to have shown in a ten-year six-sector simulation that it cuts accumulated debt by 63.2% while retaining 86.8% productivity. A skeptic should doubt this for the simplest possible reason: **the authors' own public repository, which this manuscript nominates as its replication artifact, says the study does not exist.** It says the article "reports no dataset and no measured empirical result." It says the simulation code covers 1,000 synthetic tasks in one domain and "must never be cited as empirical municipal validation." It says the full evaluation "was never conducted." The manuscript's own Section 8.8 says the simulation has not been executed. The Data Availability Statement says no dataset was analyzed.

So the paper contains, in its own pages, three statements that the Results section did not happen, and a Results section nine subsections long reporting that it did. Everything below follows from that, and I will not pretend otherwise.

I will also say plainly that this is the strangest manuscript I have reviewed, because it is simultaneously more honest and less honest than anything that normally reaches me. Section 11 volunteers that four of its ten hypotheses are tautologies. Section 10.2 volunteers that a baseline beats the proposed method for nine of ten years. Section 8.1 volunteers that a previous version of this paper mis-attributed distributions to two survey papers that contain no distributions, and that a previous claim about the direction of its sampling bias was wrong. An author team capable of that does not usually publish a fabricated results section. I suspect what happened is mechanical rather than venal — a prior draft's clearly-labelled targets rewritten into past tense while the honest scaffolding around them was left standing. But I review what is in front of me, and what is in front of me reports unconducted experiments as findings.

### 2. Acknowledged Strengths

Credit where it is due, and there is more of it than my recommendation suggests.

- The worked example in Section 7 is **exactly right**. I recomputed the SCV from the term table against the weight table and got 0.34261 and 0.327758 against stated 0.3426 and 0.3277. The weights sum to 1.000 to the digit. The 594/595 integrality argument is correct because the 0.60 h increment is exactly 8 × 0.075. The retirement-wave chain in §9.5 is correct in all seven of its quantities. I could not break this arithmetic and I tried.
- The intake-requirement finding, cross-checked by Little's law and by direct division of trainee clock hours, is a real result that a workforce planner could act on tomorrow, and it is independent of the fabricated section.
- The staffed-mode decision variable is a correct identification of why prior allocation work cannot answer a distributional question. That is a genuine insight, modest but real.
- Section 7.7 reports that the paper's own visually striking result — the mode reversal — is **not** robust. Almost nobody does this.
- The positioning is honest about lineage in a way I rarely see: the paper states outright that Bainbridge owns the mechanism and that the capability budget belongs to the nurse-rostering family.

### 3. Core Technical Concerns

**C1.** Section 8.8, line 1335: "The set below will be lodged on the Open Science Framework **before the simulation is executed**." Section 9.1: "The outcomes reported in Sections 9.2 through 9.9 **evaluate the reference implementation across thirty paired simulation seeds** over the six calibrated municipal sectors." These are 29 lines apart in the same file. No reviewer who reads both can recommend acceptance.

**C2.** The novelty claim rests on a comparison table (`tab:comparison`) in which CivicWorkOS is the only row with a ✓ in all six capability columns. But three of those six columns — "debt priced," "who works," "policy as executable constraint" — are the authors' own definitions of what matters, chosen after the framework was designed. A table whose columns are the proposal's features will always award the proposal full marks. The nurse-rostering row is given ✓ on "who works" and ▲ on "debt priced," which is the only row that threatens the thesis, and §2.2 concedes that the capability budget "is a member of that family rather than a departure from it." So the differentiating claim reduces to: rostering decides who covers existing work, we decide whether the work exists. That is a real difference. It is also a narrower contribution than a six-column full-marks row implies.

**C3.** Four of six baselines are the authors' own objective with terms switched off. §8.2 concedes the circularity. The repository states it outright: "this comparison can show that the mechanism does what it was designed to do — it cannot show that it outperforms an independently designed alternative." The two external baselines exist to answer this, and **one of them is not implemented** (see C4). So the circularity charge, which the authors raised against themselves and claimed to have fixed, is unfixed.

**C4.** ERA (Merlo) is scored on twelve metrics in Table `tab:mainresults`, including 52.9 h mean recovery time. Table `tab:stress`, the sole source of recovery-time data, has no ERA column. The repository has no ERA implementation. Where did 52.9 come from? The same question applies to all twelve of its values.

**C5.** Every number in §9.5 is the r_k = 0.14 row of Table `tab:sensitivity`, recomputed. The dual "remained at 0.0454." The mix is 94.1%. The cost is 9.57%. The (v-b) deficit matches the closed form "exactly." These are presented as a stochastic simulation's output. A thirty-seed discrete-event simulation does not return deterministic arithmetic to four significant figures with no interval. The §9.2 claim that the simulated dual landed "within 0.7% of the 0.0454 derived analytically" and thereby "confirmed that the discrete-event implementation accurately reproduced the theoretical mathematical program" is the tell: that is not validation, it is the analytic number quoted back with a 0.7% perturbation attached.

### 4. Novelty Critique

Stripped of the unconducted evaluation, what is new?

The staffed-mode variable: new in this literature, genuinely. The capability budget: the authors concede it belongs to a fifty-year-old family; new in its unit conversion, its accrual restriction to below-competence practitioners, and its feasibility condition. CAD: the authors concede the concern is Bainbridge's and the accounting metaphor is Cunningham's; new in aggregation and in the computable flip threshold. The access constraint: a share constraint against an external target, which the authors concede is not a fair-division mechanism and carries no envy guarantee. The policy twin: a defeasible rule language with a status lattice, which is standard defeasible-logic machinery applied to a new domain. The contestability procedure: the authors map it onto Alfrink et al.'s five features and implement three.

So: one new decision variable, four known constructions carefully adapted, and an honest account of what is borrowed. That is a legitimate Hypothesis and Theory contribution. It is **not** the "city-scale computational mechanism" breakthrough the Introduction's five-gap framing implies, and it does not need the 63.2% figure to be worth publishing. The fabricated section is not only wrong, it is unnecessary.

### 5. Methodological Critique

The statistical analysis plan in §8.5 is better than most published plans — paired seeds, correct test substitution, declared 60-test Holm–Bonferroni family, an honest minimum-detectable-effect floor of d = 0.76, a pre-committed anti-p-hacking rule on seed counts. And **not one of its outputs appears in Section 9.** No test statistic, no p-value, no effect size, no Shapiro–Wilk outcome, no achieved power, no raised seed count, no Holm–Bonferroni result. Table `tab:hypoutcomes` compares point estimates to thresholds and writes "Not refuted" ten times. A plan that is never executed is not rigor, it is the appearance of rigor, and the appearance is doing work in this manuscript that the substance is not.

Note also that §8.7 records revising two refutation thresholds *after* checking them against the worked example — P9's ceiling raised from 125% to 130%, P3's ratio replaced by an absolute floor. The manuscript discloses this, which is correct and creditable. But the disclosure concedes that the threshold family was tuned until the framework cleared it. Combined with four hypotheses the authors admit are tautological, and P8 whose ceiling is vacuous under the real sign of the ablation (see Reviewer 1's W5), the informative content of "all ten not refuted" is close to zero. Section 9.9 half-admits this and then nominates three findings as informative anyway, one of which is the sign-inverted P8 result.

### 6. Experimental Skepticism

Specific attacks, in order of how much damage each does:

1. The study was not run. Everything else is secondary.
2. Perfectly round robustness: all ten hypotheses not refuted, after two thresholds were adjusted against the demonstration case and four are conceded tautologies.
3. The one metric on which the method is worst — Zone Z4 fallback, 0.029 against 0.004 — is reported and explained, which looks like candour, but it is also the only place a reader can see the constraint system's operational price, and it is 7× the best baseline.
4. The 0.942 appeals figure has no generative model anywhere in the paper or supplement. It is a number with no method.
5. Calibration is claimed from five open portals, but the archived snapshots that would make the calibration checkable "accompany the replication package," and the replication package does not contain them.
6. Emergency logistics is uncalibrated and swept, and its row in Table `tab:persector` is "the midpoint of the swept range" — a midpoint presented in a column of simulation means, folded into the city-wide average that produces the Abstract's 86.8% and 0.97.
7. §9.7 claims scalability at "< 1.5 s" against its own table's 74 s. Fifty-fold.

### 7. Consistency Attacks

Beyond the §9.5 and §9.7 items already made: the access-constraint ablation sign is inverted in three places including the Conclusions; §7.7's robustness claim is contradicted by ten rows of the table directly above it; the λ = 0.0273/0.6 = 0.0454 equation returns 0.0455; §10.2's debt ceiling of 13.5 plus 1.37/yr gives 40.9 at year twenty against a stated 49.3; Table `tab:persector` calls a sum a mean. Reviewer 1 tabulates these with locations. I will add only this: five of nine arithmetic defects are in prose *reporting* tables rather than in the tables themselves, and all of the verified-correct arithmetic is in Section 7. The error distribution localises the problem precisely.

### 8. Integrity Concerns

I will use the cautious language the task requires, and I will be clear about what I am and am not alleging.

I am **not** alleging that these authors set out to deceive. The manuscript corrects its own prior errors four separate times, volunteers tautologies, volunteers that a baseline wins for nine years, and ships a repository containing a verification script that recomputes the published worked example and a README that accurately states no empirical result was measured. That is not the behavioural profile of fabrication. It is the profile of a careful team that rewrote a targets section into past tense and did not re-audit the consequences.

What I **am** stating is that the manuscript as submitted reports results that were not obtained, cites an artifact that contradicts them, and would, if published, require correction or retraction once any reader opened the repository link printed in its own Data Availability Statement. That is true regardless of intent, and it warrants immediate clarification from the authors before this manuscript goes anywhere. The specific statements requiring explanation are in Reviewer 1's Questions 1–3.

### 9. Missing Essential Components

- The study.
- Keywords (5–8 required; zero present).
- An Ethics Statement.
- The contents of the Abbreviations section, which is present and empty.
- A funding code, in place of `26UQU(Staff number)(track name)xx`.
- Any statistical output from a 60-test plan.
- The ERA baseline.
- The appeals model.
- The calibration snapshots.
- An OSF registration identifier the manuscript promises.
- 9,000 words of excess removed.

### 10. Fatal Weaknesses

At any venue: W1 alone. An editor who reads the Data Availability Statement, clicks the link, and reads the first paragraph of the README will desk-reject this and may write to the authors' institution. That outcome is avoidable only by the authors fixing it before submission, which is the purpose of this audit.

### 11. Claim Strength Audit

| Claim | Classification | Location | Justification |
|---|---|---|---|
| Ten-year six-sector evaluation establishes CivicWorkOS's performance | **Unsupported** | §9 | Artifact states the study was never conducted |
| 63.2% / 86.8% / 0.97 | **Unsupported** | Abstract, Table `tab:mainresults` | Same |
| "all ten hypotheses not refuted" is evidence of framework validity | **Weakly Supported** | §9.9 | Four conceded tautological, two thresholds tuned post hoc, P8 sign-inverted, no tests run |
| Two external baselines remove the circularity of earlier designs | **Contradicted** | §8.2 | One external baseline does not exist (C4) |
| "demonstrates practical scalability (< 1.5 s)" | **Contradicted** | §9.7 | Own table: 74 s |
| Access constraint costs 1.3 CAD points | **Contradicted** | §9.6, Conclusions | Own ablation: it saves 1.3 |
| Staffing reversal robust to all six parameters | **Contradicted** | §7.7 | Own table: ten "no reversal" rows |
| 0.942 appeals resolved in window | **Unsupported** | Table `tab:mainresults` | No model specified |
| Worked example establishes computability, binding constraints, a legible price, and a determinate distributional answer | **Fully Supported** | §7, §11.1 | Independently recomputed; correctly scoped by the authors |
| 3.38× dilution of time-to-competence | **Fully Supported** (conditional on unmeasured φ̄, ω̄) | §7.6 | Verified twice; the conditionality is stated |
| CivicWorkOS legitimates automation as much as it constrains it | **Fully Supported** | §11.4 | Argued, not asserted; the strongest paragraph in the paper |

### 12. Scores

| Category | Score (/10) |
|---|---|
| Novelty | 5 |
| Technical Depth | 6 |
| Experimental Validity | 1 |
| Clarity | 6 |
| Trustworthiness | 1 |
| **Overall** | **2** |

### 13. Recommendation

**Reject.**

A paper that reports experiments its own replication artifact says were never run cannot be revised into acceptability; the results must either be obtained or withdrawn. I want to be precise about what I am rejecting, though, because it is not the research. Sections 3–7 and 10–11 are the work of people who check their arithmetic to five decimals, correct their own published errors, and volunteer the findings that hurt them. Delete Section 9, cut nine thousand words, fix the five text-versus-table contradictions, add the keywords, and the theory paper underneath is one I would argue for. Right now it is carrying a section that would get it retracted.

---

## 🟢 Reviewer #3 — Domain Specialist / Impact Reviewer

### 1. Domain Context Summary

This work sits at the intersection of four literatures that have not previously been joined: human–robot task allocation (Ranz, El Makrini, Merlo, Noormohammadi-Asl, Ali), personnel scheduling with skill constraints (Burke, Van den Bergh), human-factors research on automation-induced skill decay (Bainbridge, Endsley & Kiris, Parasuraman, Arthur, Tatel & Ackerman), and algorithmic-governance work on contestability and urban digital twins (Citron, Alfrink, Díaz-Sarachaga, Mintrom, Qanazi). The manuscript's Section 2 is, in my assessment as someone who works in this area, an **accurate and well-judged** survey of all four. I checked the characterisations of Ranz, Merlo, Zhao, Burke, Díaz-Sarachaga and Alfrink against what those papers actually argue, and found no mischaracterisation. The treatment of Frey & Osborne alongside Arntz is particularly well done: the manuscript cites both deliberately and explains that the factor-of-five discrepancy between them is "the distance between a policy of pre-emptive displacement management and one of task redesign." That is the right reading and it is doing argumentative work rather than decorating.

### 2. Novelty vs. State-of-the-Art

The closest antecedents, and where this sits relative to each:

- **Ranz et al. (2017), Merlo et al. (2023), Ali et al. (2022), Noormohammadi-Asl et al. (2025):** all optimise fit, ergonomics, trust or preference for a workcell or team. None prices a deferred liability and none selects a roster. CivicWorkOS's staffed-mode variable is a real advance over all of them on the distributional question. **Genuine novelty.**
- **Zhao et al. (2023):** closest prior work on city-scale municipal allocation; graph-structured assignment of spatio-temporal sensing tasks. No capability, debt or governance dimension. CivicWorkOS is a different question at the same scale. **Genuine novelty.**
- **Burke et al. (2004), Van den Bergh et al. (2013):** the strongest challenge. Nurse rostering has handled skill mix, supervision ratios, qualification maintenance and cross-training as hard constraints for decades, and it does assign named people. The manuscript's answer — rostering takes the existence of human work as given, whereas this decision is prior — is correct and sufficient, and §2.2 states it without inflation. But the gap is narrower than §2.9's five-gap framing suggests, and a reviewer from the OR community will press hard here. The capability budget would be recognised by that community as a cross-training constraint with a novel unit conversion and accrual rule. **Incremental-to-moderate novelty, honestly positioned.**
- **Díaz-Sarachaga (2025), Ben-Daya et al. (2026):** governance assessment *of* urban digital twins. The manuscript's inversion — governance represented *inside* the twin as an executable constraint — is stated precisely in §2.8 and is a real conceptual move. **Genuine novelty.**
- **Alfrink et al. (2023):** contestability design framework. The manuscript implements three of five features and says so. **Faithful application rather than novelty.**
- **Rashidi (2026):** carries the same concern (AI automating the entry-level work through which expertise forms) into the agentic era. This is the closest statement of the paper's *motivating thesis* by someone else, and the manuscript cites it correctly as such. The contribution is the mechanism, not the thesis.

**Assessment:** the conceptual contribution is real and publishable. It is a *framework* contribution of moderate novelty, not a breakthrough, and the manuscript's own §2 positioning is more accurate than its §1 framing.

### 3. Academic Impact Assessment

Three elements would be cited:

1. **The intake requirement and the dilution factor.** τ_k = (h_raw/Θ)(1/φ̄ω̄) giving 4.05 years against a certification assumption of 1.2, and the resulting 14-versus-4 intake gap, is the kind of compact result that gets picked up outside the originating community — by workforce planners, by professional licensing bodies, and by the skill-formation literature. It is independent of the simulation and it is verified arithmetic. **This is the paper's most citable content and it is currently buried in Section 7.6.**
2. **The staffed-mode formulation.** Likely to be adopted as the right decision variable by anyone asking distributional questions about allocation.
3. **The "who wins and who loses" analysis (§11.3)** and in particular the structurally-zero contracted-worker row in Table `tab:dist`. Printing a row that reports the framework's own principal failure, rather than omitting it, is a methodological move the fairness community will notice and may imitate.

Against that: the Section 9 problem would, if published, make the paper **negatively** citable. In this field, a paper caught reporting unconducted experiments becomes a cautionary example rather than a contribution, and it damages the credibility of the framework it was meant to support. The authors should weigh that against the apparent attraction of having a results section.

### 4. Practical Impact & Deployment Potential

Mixed, and the manuscript is honest about why.

**Deployable now, independently of the optimiser:** the evidentiary record of Appendix S1.3 and the contestability procedure of §6.3. The manuscript identifies this itself in its future-work list — "the component a city could adopt tomorrow without adopting the optimizer at all" — and it is right. A municipality could implement the append-only allocation record, the standing rules including the deliberate decoupling of worker standing from the headcount arithmetic, the appeal windows, and the 0.05 upheld-rate systemic trigger, without any of the optimisation machinery. That is a genuinely useful, genuinely adoptable artifact.

**Not deployable:** the optimiser. Four parameters that carry the headline results (learn_i, φ_m, the supervision ratio, h_raw) are unmeasured, and the elicitation protocol that would measure them is specified and explicitly not executed. Feasibility sits at ~85% of critical on three axes, so a stricter licensing regime or an older workforce is infeasible rather than suboptimal. The annual monolithic solve is intractable and sector decomposition costs a 3.4% gap by dropping cross-sector coupling. The framework cannot see non-payroll workers, which in most of the world is where the problem is.

**The decisive practical obstacle is institutional, not technical.** The access constraint allocates developmental work by protected characteristic. §6.4 supplies an EU equality-law analysis, which is necessary and creditable, but a city deploying this is making a positive-action decision under legal challenge risk, with a published parameter θ_{k,g} naming the target composition. That is a political act that a published dual price makes maximally visible. The manuscript understands this — §11.4's observation that the framework "legitimates automation as much as it constrains it," and that it is "a device for making a political choice explicit and traceable," is the most sophisticated paragraph in the paper. It also means adoption depends on a municipality wanting its trade-offs made contestable, which is not the revealed preference of most procurement processes.

### 5. Comparison to Existing Literature

**Well covered:** human–robot allocation; skill decay and out-of-the-loop performance; technical-debt lineage; contestability and technological due process; labour-market exposure with the Frey–Osborne/Arntz tension handled properly; just-transition policy instruments; urban digital twin governance; the Sen/Nussbaum capability vocabulary used in its actual sense rather than as a synonym for skill inventory; Ostrom on monitored appropriation of depletable commons, which is the right institutional analogy for the budget.

**Missing or thin, and a specialist will notice:**
1. **Constrained MDPs and safe RL.** §11.4 concedes the online rule has no regret or violation bound and names Altman and García & Fernández as where the machinery lives. For a paper whose deployable mechanism is the online rule, this is a gap in the *work*, not only in the citation list. A primal–dual scheme with constraint violation during learning is a solved-enough problem that a reviewer will ask why no bound is attempted.
2. **Online/dynamic matching and prophet inequalities.** The online allocation problem here is structurally an online assignment with budget constraints, a literature with competitive-ratio results that would bound exactly what Proposition 4 leaves unbounded. Not cited.
3. **Apprenticeship and vocational-training economics.** The paper's central object is the economics of training-slot provision under capital substitution, which has a substantial empirical literature (training externalities, poaching, the firm's under-provision incentive). Rashidi (2026) is a working paper standing in for a field. The intake requirement would be stronger, and better defended, with that grounding.
4. **Public-sector algorithmic procurement.** §11.4 identifies vendor-dependency debt as "the honest gap" and notes it is a procurement variable the mechanism does not control. The procurement-governance literature is where that gap would be addressed, and it is uncited.
5. **ISO 23247 is cited for digital-twin reference architecture** but the manuscript concedes it does not cover policy or workforce elements, which is correct; no standards work closer to the Policy Digital Twin is identified, and I am not aware of any, so this is a fair gap rather than an omission.

**One citation-relevance problem:** `syed2026fedagent` — a self-citation on federated and agentic AI for disability-inclusive employment — is cited to support the claim that "algorithmic management already allocates work, issues instructions, monitors performance, and supports managerial decisions," alongside the OECD. That paper does not establish that claim. The OECD citation carries it alone. This is the only citation in the paper I would call unsupportive of its claim, and it should be removed or re-sited.

### 6. Technical Depth Relative to Top Venues

The formal content is appropriate for a good journal in this area: a well-posed MILP, four propositions with proofs, a correct dual interpretation with a stated correction of the authors' own prior inversion, a feasibility condition with an actionable escalation path, and a worked instance verified to five decimals. It is **not** depth at the level of a top theory venue — the propositions are arithmetic consequences of the construction rather than hard results, and the absence of any regret or approximation guarantee is a real limit the authors concede.

For Frontiers in Artificial Intelligence as a Hypothesis and Theory article, the depth is appropriate and the formalisation discipline is above the journal's norm.

### 7. Scalability & Generalization Concerns

- **Scale.** Table `tab:runtime`, if it reflects real runs, shows weekly cadence tractable and annual monolithic intractable. Sector decomposition drops the cross-sector coupling in Eq. `eq:prog-cap`, so a city cannot have a single coherent annual plan. The manuscript states this as a limitation rather than hiding it. The "< 1.5 s" claim in the prose contradicts the table's 74 s and must be fixed.
- **Generalisation across municipalities.** Weak, and conceded. One city scale (1.5M residents), a European and North American calibration base, six sectors of which one is uncalibrated. The admission in §8.1 that the calibration bias "runs the wrong way" — that the open-data cities are the ones with fewest non-payroll workers, so the evaluation understates the population the framework fails — is unusually rigorous self-criticism and correctly reverses a claim made in an earlier version.
- **Generalisation across legal regimes.** §6.4's analysis is EU-specific. The authors are at Saudi institutions and the manuscript is funded by Umm Al-Qura University, yet no Gulf or GCC legal analysis appears, and `ILOESCWA2026` (Arab-region labour-market transformation to 2035) is cited once in the related work and never connected to the framework. For this author group and this funder, an analysis of how the access constraint and the just-transition constraint would operate under Saudi labour law — including Saudization/Nitaqat quota structures, which are *precisely* a composition constraint on a workforce and an obvious instantiation of Eq. `eq:access` — is both the most natural extension and a conspicuous omission. I would raise this in any review of this paper.
- **The non-payroll limitation** is the real generalisation ceiling, it is structural rather than parametric, and the authors say so in four separate places and nominate it as "the limitation we would fix first."

### 8. Risks & Limitations

1. **The Section 9 problem is an existential risk to the contribution,** not merely to this submission. See §3 above.
2. **Unmeasured inputs carrying headline results.** Four parameters, one of which (φ_m) the authors call "the most gameable quantity in the framework," and which enters four channels including the dilution factor behind the paper's most citable finding.
3. **Fragile feasibility.** ~85% of critical on three axes; h_raw = 2,400 (a plausible stricter licensing regime) is infeasible, not merely costly.
4. **The mode reversal is not robust** and the authors say so; the staffing reversal is claimed robust but the table contradicts that claim (Reviewer 1's W7).
5. **Principal–agent exposure** on six of nine flow terms and three of five debt components, with a response the authors describe as partial.
6. **Legitimation hazard.** §11.4's observation that the framework authorises displacement once the price is paid is correct and is the risk a municipal union would raise first.

### 9. Required Improvements

1. **Restructure as a Hypothesis and Theory article.** Remove Section 9 or restore it to clearly-marked specified-but-unexecuted targets. Promote the worked example and the sensitivity frontier to carry the evidence. This is the single change that converts a reject into a publishable paper, and it also solves most of the 9,000-word overage.
2. **Lead with the intake requirement.** The 3.38× dilution and the 14-versus-4 intake gap is the paper's most transferable finding, it is verified arithmetic, and it is currently in §7.6 behind thirty pages of formalism. It deserves the Abstract and a figure.
3. **Add the GCC/Saudi legal and labour-market analysis**, connecting Eq. `eq:access` to Saudization-style composition requirements and `ILOESCWA2026` to the just-transition constraint. Given the author affiliations and funder, its absence will be noticed.
4. **Engage the constrained-MDP and online-matching literatures** at least argumentatively, stating what bound would be sought and why it is hard here. §11.4 names the gap; the paper should take one step into it.
5. **Remove or re-site the `syed2026fedagent` citation** at §2.6.
6. **Execute the elicitation protocol on one domain**, even with 12 raters in a single municipality, and report ICC(2,k). One measured parameter set would do more for this paper's credibility than the entire simulation would have.

### 10. Claim Strength Audit

| Claim | Classification | Location | Justification |
|---|---|---|---|
| No prior mechanism asks who receives preserved work | **Fully Supported** | §2.9 gap 3 | Correct against the allocation literature; rostering's counter is raised and answered by the authors |
| Governance can be represented inside a digital twin as an executable constraint | **Partially Supported** | §2.8, §4.3 | Design is specified and a worked EU AI Act encoding given; no deployment evidence |
| City-scale deployability | **Weakly Supported** | §9.7, §11.4 | Rests on runtime data from the unconducted study; the "< 1.5 s" claim contradicts its own table |
| Framework fails non-payroll workers structurally | **Fully Supported** | §7.8, §11.3, Table `tab:dist` | Follows from the data substrate; argued and conceded in four places |
| Capability budget is novel relative to personnel scheduling | **Partially Supported** | §2.2 | Novel in unit conversion and accrual rule; family membership conceded; narrower than §2.9 implies |
| 3.38× dilution of time-to-competence; 14 posts not 4 | **Fully Supported** (conditional on unmeasured φ̄, ω̄) | §7.6 | Verified by two independent routes |
| Framework legitimates automation as much as it constrains it | **Fully Supported** | §11.4 | Reasoned rather than asserted |
| Ten-year multi-sector evaluation | **Unsupported** | §9 | Artifact states the study was never conducted |
| Generalises beyond the calibration cities | **Unsupported, and conceded** | §11.3 | Authors state this explicitly and reverse an earlier claim about bias direction |

### 11. Scores

| Category | Score (/10) |
|---|---|
| Novelty | 7 |
| Impact | 8 |
| Technical Depth | 7 |
| Relevance | 9 |
| Completeness | 3 |
| **Overall** | **5** |

### 12. Recommendation

**Major Revision**, and I register my disagreement with my co-reviewers deliberately.

I agree the Section 9 problem is disqualifying for this version. I disagree that rejection is the right instrument. The path to a sound paper here is unusually clear and does not require new science: delete a section, promote an existing verified result, cut to the word limit, fix five text-versus-table contradictions, add the keywords and statements. The theory underneath is a real contribution to a question the field has not posed properly, the related-work treatment is accurate and generous, the limitations are more candid than most published papers manage, and the contestability procedure is independently adoptable. A Major Revision decision with a hard condition — *the empirical section is removed or conducted, and the article type is declared* — would get the field a paper it should have, and would do it faster than a reject-and-resubmit cycle.

I recognise the editor may judge that the integrity question makes a clean rejection the only defensible process. If so, I would ask that the decision letter say explicitly that the theoretical contribution is publishable and that a restructured Hypothesis and Theory submission is welcome, because it is, and because this author team's demonstrated willingness to correct its own record makes them likely to do it properly.

---

## 🟣 META-REVIEW (Area Chair)

### 1. Final Decision

**Reject**, with an explicit written invitation to resubmit as a Hypothesis and Theory article.

I record that Reviewer 3 argued for Major Revision and that the disagreement is about process, not substance. All three reviewers agree the current version cannot be accepted; all three agree the underlying theoretical contribution is publishable. I side with Reviewers 1 and 2 because a manuscript whose Results section is contradicted by its own cited artifact and by its own Section 8.8 cannot be carried through a revision cycle — the record of the submission itself becomes a problem. A clean rejection with a clear invitation protects the authors better than a conditional accept would.

**As this is a pre-submission audit rather than a journal decision, the operative conclusion is simpler: do not submit this version. The defect that drives this verdict is one the authors can fix in roughly two weeks, and fixing it yields a paper I would expect to survive review.**

### 2. Consensus Summary

**Unanimous agreement:**
- The Section 9 evaluation was not conducted, is contradicted by the manuscript's own §8.8 and Data Availability Statement and by the authors' public repository, and disqualifies this version.
- The Section 7 worked example is exact, independently verified, and the paper's real evidence.
- The intake requirement / 3.38× dilution result is a genuine, citable, simulation-independent contribution.
- The limitations and threats-to-validity sections are of unusually high quality.
- The front matter contains desk-rejection-grade defects (word count, keywords, placeholder funding code, empty Abbreviations, no Ethics Statement).

**Disagreement:**
- *Novelty magnitude.* Reviewer 2 scores 5, calling it one new decision variable plus four adapted constructions; Reviewer 3 scores 7, treating the staffed-mode variable and the governance-inside-the-twin inversion as genuine advances. **I side with Reviewer 3.** Reviewer 2's accounting is accurate but undervalues the integration: joining four literatures that have not been joined, and posing the distributional question in a form that admits an answer, is a contribution even when each component is adapted. Reviewer 2's point that the §1 five-gap framing overclaims relative to the §2 positioning stands and should be fixed.
- *Instrument.* Reject versus Major Revision, resolved above.
- *Intent.* Reviewer 2 explicitly declines to allege fabrication and attributes the defect to a mechanical rewrite of a targets section. **I endorse that reading.** The evidence — four self-corrections of prior errors, volunteered tautologies, a volunteered nine-year baseline loss, a repository with an honest README and a verification script — is inconsistent with deliberate deception and consistent with a drafting failure. That does not reduce the severity; it does determine the tone of the letter and the remedy.

### 3. Dominant Technical Concerns

1. **The Results section reports an unconducted study** (§9; contradicted by §8.8 line 1335, the Data Availability Statement, and the cited repository). Dispositive.
2. **Five text-versus-table contradictions**, of which two are substantive: the access-constraint ablation sign inversion propagated into §9.6, §9.8, hypothesis P8 and the Conclusions; and the §7.7 robustness claim contradicted by ten rows of the table immediately above it. The others are the 74 s / "< 1.5 s" scalability claim, the λ = 0.0273/0.6 arithmetic, and the §10.2 debt-trajectory decomposition.
3. **An external baseline that does not exist** (ERA/Merlo scored on twelve metrics, absent from the only stress table, absent from the repository), which reinstates the circularity charge the authors raised against themselves and claimed to have fixed.
4. **A 12,000-word limit against ~21,050 words**, plus missing keywords, a placeholder funding code, an empty Abbreviations section, no Ethics Statement, an orphaned equal-contribution footnote, and an "AA" initials collision between two authors.
5. **Every load-bearing input is an unmeasured author estimate**, with the elicitation protocol specified and explicitly not executed. The authors state this clearly; it caps the paper's claims at conditional.

### 4. Venue Fit Assessment

**Appropriate for:** Frontiers in Artificial Intelligence as a **Hypothesis and Theory** article, after restructuring. The journal's H&T format (Abstract, Introduction, relevant subsections, Discussion, 12,000 words) fits a theory-and-worked-example paper precisely, and the authors' own repository already describes the work that way. Declaring the article type and building to that format solves the structural, length and evidentiary problems simultaneously.

**Not appropriate for:** any Original Research slot, at this or another journal, until the evaluation exists. Original Research requires a Materials and Methods and Results structure the paper cannot currently fill honestly.

**If the authors prefer to keep an empirical framing**, the realistic route is to conduct a reduced study they can actually run — the repository's single-domain synthetic testbed, properly scoped and labelled, with the §8.5 statistics applied to it — and submit to a venue whose expectations match that scope. A 1,000-task single-domain demonstration is a legitimate thing to report; it is not a six-sector ten-year evaluation.

**Alternative venues for the theory version**, if Frontiers is declined: *AI & Society*; *Government Information Quarterly*; *Minds and Machines*; ACM FAccT (the Moon & Guha paper the manuscript cites appeared there, and the "who wins and who loses" analysis would land well); *Journal of Responsible Technology*. The contestability procedure alone could support a separate, shorter paper for a digital-government venue, and Reviewer 3 is right that it is the component a city could adopt immediately.

### 5. Publication Readiness

**Is the paper publishable after revision?** Yes, as a Hypothesis and Theory article. The required changes are removal and correction, not new science.

**Does the contribution level match Q1 expectations?** For a theory and framework contribution in applied AI governance: yes, at the level of a solid Q1/Q2 journal. Not for a top-tier theory venue — the propositions are arithmetic consequences of the construction and there is no regret or approximation guarantee, which the authors concede.

**Are the experiments convincing enough?** There are no experiments. The worked example is convincing as what it is: an exact demonstration that the constraint system is computable, binds non-trivially, produces a legible price, and gives the distributional question a determinate answer. Section 11.1 scopes it correctly. That scoping should become the paper's evidentiary claim.

### 6. Reviewer Calibration

**Most technically justified:** Reviewer 1. The claim-by-claim audit with independent recomputation is the backbone of this review, and the nine-item numerical consistency table — including the correct identification that all verified-correct arithmetic is in Section 7 while five of nine defects are in prose reporting tables — localises the problem more precisely than either colleague managed. Reviewer 1's distinction between "fatal to the manuscript as constituted" and "not fatal to the research programme" is the correct frame and I have adopted it.

**Reviewer 2** is right on the dispositive point and right to decline the fabrication allegation. The critique of the comparison table's self-selected columns, and the observation that the §8.5 statistical plan is "the appearance of rigor doing work the substance is not," are both sharp and both land. Reviewer 2 underrates the novelty.

**Reviewer 3** supplies what the other two cannot: verification that the related-work characterisations are accurate, identification of the intake requirement as the paper's most transferable result, and the observation that for a Saudi-affiliated and Saudi-funded author team, the absence of any GCC legal analysis — when Saudization quotas are a direct real-world instantiation of Eq. `eq:access` — is a conspicuous and easily-remedied gap. That last point is the single most useful constructive suggestion in this review and the authors should act on it.

**Fatal or fixable?** Fixable, by subtraction. No new experiment, dataset or theorem is required to produce a sound paper from this material.

**Which concerns dominate?** Concern 1 alone determines the decision. Concerns 2–4 would each warrant Major Revision independently.

### 7. Revision Feasibility

**Difficulty: moderate.** The work is removal, correction, compression and front matter, not new research.

- Remove or relabel Section 9: ~3,500 words out, 1–2 days.
- Compress to 12,000 words: ~9,000 words to remove in total, of which Section 9 supplies a third and moving Tables `tab:notation`/`tab:params` plus the §2 survey compression supplies most of the rest. 3–5 days.
- Fix the five text-versus-table contradictions: 1 day.
- Front matter (keywords, Ethics Statement, Abbreviations, funding code, dagger, correspondance, initials): 2 hours.
- Promote the intake requirement to the Abstract and add a figure for it: 1 day.
- Add the GCC/Saudi legal subsection: 2–3 days.
- Engage constrained-MDP/online-matching argumentatively: 1–2 days.
- **Total: roughly two weeks of focused work.**

Optional and high-value: execute the elicitation protocol on one domain with 12 raters and report ICC(2,k). Four to eight weeks including ethics approval. One measured parameter set would strengthen this paper more than the entire simulation would have, because it attacks the limitation the authors themselves nominate as binding.

**Estimated acceptance probability, current form:** **3%.** Desk rejection on word count and missing keywords is the most likely outcome and would occur before the integrity problem is reached. Should it reach review, rejection is near-certain.

**Estimated acceptance probability, after the two-week revision as a Hypothesis and Theory article:** **65–70%.**

**After the two-week revision plus one executed elicitation domain:** **80%.**

---

## 🔬 PUBLICATION RISK MATRIX

| Risk Area | Severity | Impact on Publication |
|---|---|---|
| **Research integrity** | **Critical** | Results section reports a study the authors' own cited repository states was never conducted, and that §8.8 and the Data Availability Statement independently contradict. Grounds for desk rejection, and for retraction if published. Overrides everything else. |
| **Journal compliance** | **Critical** | ~21,050 words against a 12,000 maximum; zero keywords against a 5–8 requirement; unfilled funding placeholder; empty Abbreviations section; no Ethics Statement. Any one of these returns the manuscript before review. |
| Experimental validity | Critical | No conducted experiment. Four of six baselines are self-ablations (conceded); one of two external baselines is unimplemented. Four of ten hypotheses conceded tautological; two thresholds tuned post hoc against the demonstration case. |
| Reproducibility | High | Section 7 is exemplary and independently verified. Section 9 is unreproducible by construction. The cited artifact does not contain what the Data Availability Statement claims. |
| Internal consistency | High | Nine numerical defects, five in prose reporting tables. Two are substantive: a sign inversion carried into the Conclusions, and the paper's self-declared central claim contradicted by the table placed to support it. |
| Statistical rigor | High | An excellent 60-test plan with no output. No test statistic, p-value, effect size or power figure anywhere. Minimum detectable effect d = 0.76 exceeds several reported ablation differences, which the authors concede. |
| Novelty | Medium | Real but moderate: one new decision variable, four well-adapted constructions, a genuine four-literature integration. The §1 framing overclaims relative to the accurate §2 positioning. |
| Parameter grounding | Medium–High | Every load-bearing input is an unmeasured author estimate; the elicitation protocol is specified and explicitly not executed. Sensitivity analysis substitutes for measurement and the authors say it is "a weaker thing." |
| Writing quality | Low | Prose is clear, disciplined and in places excellent. 53 overfull boxes and minor orthographic drift are cosmetic. |
| Scope fit | Low | Squarely within Frontiers in AI's remit as a Hypothesis and Theory article. |
| **Overall acceptance risk** | **Very High** | Desk rejection likely before review; rejection near-certain if reviewed. |

---

## 📋 REVISION ROADMAP

| Priority | Issue | Location | Fix | Effort |
|---|---|---|---|---|
| **Critical** | Section 9 reports an unconducted study | §9 (lines 1364–1585) | Delete the section, or restore every figure in it to a clearly-marked specified-but-unexecuted target in the manner of the prior version. Do not retain any number from it in past tense. | 1–2 days |
| **Critical** | §8.8 states the simulation has not been executed while §9 reports its results | line 1335 vs line 1366 | Resolve in whichever direction C1 is resolved. If restructuring, §8 becomes a specified protocol for future work and says so in its opening sentence. | 2 h |
| **Critical** | Abstract's lead numbers come from the unconducted study | Abstract | Rebuild around the Section 7 results: the 0.0454/0.0455 capability price, the 4.34% cost with its 0.33–9.60% swept range, 3.46 competent-equivalents, the 3.38× dilution, and the 14-versus-4 intake gap. Remove 63.2%, 86.8% and 0.97. | 3 h |
| **Critical** | Data Availability Statement is self-contradictory and misdescribes the repository | back matter | Rewrite using the repository README's own accurate wording. State that the worked example and closed-form model are verified by shipped scripts, that `sim/` is labelled synthetic demonstration data not municipal validation, and that no dataset was created. Fix `sec:discussion` → `sec:results`. | 2 h |
| **Critical** | ~21,050 words against a 12,000 maximum | whole manuscript | Section 9 removal supplies ~3,500. Move Tables `tab:notation` and `tab:params` and the §5 notation subsection to the supplement. Compress §2 from nine subsections to five. Compress §6 governance detail into Appendix S1, which already holds the operative specification. | 3–5 days |
| **Critical** | No keywords | preamble | Add 5–8. | 15 min |
| **Critical** | Front matter defects | preamble, back matter | Fill the `26UQU(Staff number)(track name)xx` funding code; populate or delete `\section*{Abbreviations}`; add an Ethics Statement recording that no human-participant data was collected and that the Appendix S4 protocol requires approval before any future execution; attach `$\dagger$` to the intended authors or delete the footnote; pass the corresponding author to `\correspondance{}`; disambiguate "AA" in Author Contributions (use "AAk"/"AAl" or full names). | 2 h |
| **High** | Access-constraint ablation sign and magnitude inverted | §9.3, §9.6, §9.8, §12, Table `tab:hypoutcomes` P8 | Table `tab:ablation` shows removing the constraint *raises* CAD by 1.3 and recovery by 0.7 h. Correct all four narrative sites. Reconsider P8's "CAD ≤ +5" clause, which is vacuous if the constraint reduces CAD. | 3 h |
| **High** | "Practical scalability (< 1.5 s)" against a tabled 74 s | §9.7 | Correct the figure or the unit. Survives only if §9 is retained. | 15 min |
| **High** | §7.7 robustness claim contradicted by its own table | §7.7 ¶2 vs Table `tab:sensitivity` | Restate to what the table supports: the budget is never satisfiable by lead-only rosters alone, so some developmental staffing always occurs, but the lead-only roster is retained on 15–46% of tasks in the "no reversal" region and the dual collapses to ≤0.0033 there. **This is the paper's self-declared central claim and it is currently overstated.** | 4 h |
| **High** | ERA baseline scored but unimplemented and absent from the stress table | Table `tab:mainresults`, Table `tab:stress`, §8.2 | Implement it, or remove it and import the repository's own concession that an all-ablation comparison cannot demonstrate superiority over an independently designed alternative. | 1 day, or 1 h to remove |
| **High** | Analytic recomputations presented as simulation output | §9.2 ¶3, §9.5 | Relabel as exact arithmetic on the model and move into §7 as a parameter-shock extension of the worked example, where they are legitimate and valuable. | 4 h |
| **High** | 0.942 appeals figure with no generative model | Table `tab:mainresults`, §8.3, §8.4 | Specify the appeal arrival, standing, upheld and resolution-time model, or remove the metric. | 3 h |
| **Medium** | λ_k = 0.0273/0.6 printed as 0.0454; the equation yields 0.0455 | Eq. `eq:lambdaworked` and nine downstream sites | Publish the unrounded tied-mode SCV values so the reader can reproduce 0.0454, or correct to 0.0455 throughout. The repository's verification script should state which value it checks. | 2 h |
| **Medium** | §10.2 debt decomposition does not reproduce its own trajectory values | §10.2 | 13.5 + 1.37t gives 40.9 at t = 20 against a stated 49.3, and 27.2 at t = 10 against 34.6. Reconcile the ceiling, the slope and the quoted values. | 3 h |
| **Medium** | P3's 80-point gap uses the weaker comparator | Table `tab:predictions`, Table `tab:hypoutcomes` | Fix the comparator in the criterion and report against the best-performing baseline (Human-First, 0.31, giving 66 points). | 1 h |
| **Medium** | Add GCC/Saudi legal and labour-market analysis | new subsection in §6 | Connect Eq. `eq:access` to Saudization/Nitaqat-style workforce-composition requirements and `ILOESCWA2026` to the just-transition constraint. Given the affiliations and funder, its absence is conspicuous and the addition is the review's highest-value constructive suggestion. | 2–3 days |
| **Medium** | Scalarization limitation sits in a limitations bullet | §11.3 → §6.1 | Move the convex-hull admission to where the democratic legitimacy claim is made, since it bounds the panel's authority. | 1 h |
| **Medium** | Online rule has no regret or violation bound | §11.4 | Engage the constrained-MDP and online-matching/prophet-inequality literatures argumentatively: state what bound would be sought and why it is hard here. | 1–2 days |
| **Medium** | Table `tab:persector` labels a sum a mean | Table `tab:persector` final row | Split the label, or footnote that Tasks/yr is the sum while all other columns are means. | 15 min |
| **Medium** | `syed2026fedagent` does not support the claim it is cited for | §2.6 | Remove, or re-site where it is apposite. | 15 min |
| **Low** | Promote the intake requirement | §7.6 → Abstract + new figure | The 3.38× dilution and 14-versus-4 intake gap is the paper's most transferable result and is currently buried. Give it a figure. | 1 day |
| **Low** | 53 overfull hboxes | throughout | Clear before submission. | 3 h |
| **Low** | Orthography and bib fields | §10.2, Appendix S4.2, `references.bib` | Unify to US spelling; fix the `BenDaya2026` and `syed2026fedagent` volume/number fields; correct "two to four points" to "2.2 to 4.3". | 1 h |
| **Optional, high value** | No measured inputs | Appendix S4 | Execute the elicitation protocol on one domain with 12 raters; report ICC(2,k). This attacks the limitation the authors themselves nominate as binding and would raise acceptance probability more than any other single addition. | 4–8 weeks incl. ethics |

---

## FINAL VERDICT

**Do not submit this version.** In its current form the manuscript's estimated acceptance probability at Frontiers in Artificial Intelligence is approximately **3%**, and the most likely editorial outcome is **desk rejection** — triggered by a ~21,050-word manuscript against a 12,000-word maximum and the complete absence of keywords, before an editor reaches the substantive problem. Should it pass triage, the substantive problem is dispositive: Section 9 reports a thirty-seed, six-sector, ten-year simulation study that the manuscript's own Section 8.8 says has not been executed, that the Data Availability Statement implicitly denies ("No new datasets were created or analyzed"), and that the authors' own public repository — the artifact the manuscript nominates for replication — states in its opening paragraph was never conducted, and whose synthetic demonstration code it warns "must never be cited as empirical municipal validation." Any reviewer who follows the link in the Data Availability Statement will find this in under a minute. The consequence is rejection with an integrity note, and if the paper were published, correction or retraction. Four further contradictions between prose and tables — including a sign inversion on the access constraint carried from §9.3 into §9.6, §9.8 and the Conclusions, and a robustness claim in §7.7 refuted by the ten "no reversal" rows of the table printed directly above it — compound the impression of a results section that was never proofread against its own data.

**The research, however, is in substantially better condition than the manuscript.** Sections 3–7 and 10–11 are the work of a careful team: the Section 7 worked example reproduces to five decimal places under independent recomputation, including the full SCV decomposition, the complete two-mode mix enumeration, the integrality argument, the intake requirement verified by two independent routes, and the entire retirement-wave chain; the authors correct their own prior published errors in four separate places; they volunteer that four of their ten hypotheses are tautological and that a baseline beats their method for nine of ten years; and they print a table row reporting their framework's own structural failure rather than omitting it. The intake-requirement finding — that machine-assisted supervised practice stretches time to competence from 1.2 to 4.05 years, so a city sizing intake from certification hours would provision four trainee posts where fourteen are required — is a genuine, verified, simulation-independent result that deserves the Abstract it does not currently occupy. **The fix is subtraction, not new science:** remove or re-label Section 9, cut to 12,000 words, correct five text-versus-table contradictions, repair the front matter, promote the intake requirement, and add the GCC legal analysis that this author group's affiliations and funder make conspicuous by its absence. That is roughly two weeks of focused work, after which a **Hypothesis and Theory** submission — the article type the authors' own repository already uses for this work — should carry an estimated acceptance probability of **65–70%**, rising to about **80%** if the elicitation protocol of Appendix S4 is executed on a single domain so that at least one load-bearing parameter is measured rather than estimated.
