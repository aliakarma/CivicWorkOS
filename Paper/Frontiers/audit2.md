# Forensic Academic Writing Audit (Second Pass): CivicWorkOS and Supplementary Material

**Audited files (working copies, post-`report.md` revision):**
- `CivicWorkOS.tex` (1,330 lines), cited below as **M** + line number
- `CivicWorkOS_supplementary.tex` (592 lines), cited below as **S** + line number
- Figures `images/arch.png` and `images/runtime.png` (inspected visually against captions)

**Context files read:** `audit.md` (first audit, Gemini), `report.md` (fix report), `cover-letter.md`.
**Tools run:** `count_words.py --detail` (journal basis 11,898), `audit_numbers.py` (199 PASS, 0 FAIL, 2 known-defect), `check_repo.py` (3 PASS), LaTeX logs (0 undefined references; natbib "multiply defined" warnings from `xr`).

**Important note on which file was audited.** The request named `submission/CivicWorkOS.tex`. That copy (and `CivicWorkOS-submission.zip`) is dated 8 Oct 00:16, *before* the first audit and the `report.md` fixes; it differs from the root `CivicWorkOS.tex` throughout (for example, its abstract still says "prices protected practice at 0.0454"). This audit therefore covers the **root working copies**, which are the current manuscript. The stale `submission/` folder is itself logged as Issue I-001.

This document diagnoses only. It does not rewrite any passage. Appendix A at the end checks every claim in `report.md` against the current text.

---

## 1. Executive Diagnostic

**Overall state.** The first revision fixed many local wording problems (colloquialisms, the old abstract wording about pricing, the unlinearized access constraint, missing Δ_g definition). It also introduced or left behind a second layer of problems. Several fixes were made in one place and not carried through to the places that depend on them. Wording from the revision process (talk of "earlier versions", "repairs", "category errors") now sits inside the article itself. Two of the article's headline numbers rest on assumptions the text states inconsistently.

**Clarity.** Most paragraphs are readable sentence by sentence. Three problems recur. (a) Long sentences pack several claims into one, for example M605, M787 and M1117. (b) Terms are used before they are defined: δ^disp, n^min, the "decade" of retention, the Workforce Development Agent, the names of the strategies in Figure 4. (c) Referents are ambiguous: "the constraint" (M118), "that second half" (M134), "the price" (M887 against M935).

**Natural academic voice.** The text has a distinctive and often good voice: direct, skeptical, willing to state negative results. It is undercut in two ways. Aphorisms close paragraphs ("which is the most a design can offer", "and should be judged as such"). New enumerative scaffolds have replaced the ones the first audit removed ("demonstrates four primary operational consequences", "Three analytical properties emerge", "partition across four distinct municipal constituencies").

**Technical precision.** This is the most serious area. Problems found:
- Certification hours are called both "supervised" and "solo unassisted", and the 3.38 dilution factor depends on which is meant.
- The zero-covariance condition in Proposition 2 is stated over ℓ_i, which is in hours, where learn_i, a rate, is needed.
- The statement of Proposition 4 does not match its proof.
- The online-rule error is said to be "bounded by the integrality gap", which is not what an integrality gap bounds.
- The policy join is described as authority-ranked, while the formal join ignores authority.
- The text says "what survives ... is exactly the human capacity" for an N−1 criterion, which is false whenever more than one automation component exists.
- Symbols are heavily reused: τ, κ, ρ, δ, π and ε each carry two or three meanings.

**Reasoning structure.** The seven research questions are never answered one by one. Gap 3 ("no allocation mechanism ... asks who receives the work") conflicts with Table 1, which marks nurse rostering as deciding who works. The causal story for dilution credits automation with a factor that is mostly (2.0 of 3.38) due to sharing the work with a lead.

**Evidence/claim alignment.** Main problems:
- The figure of 3.46 competent-equivalents against 2.88 attrition is η_k = 1.2 by construction, yet the abstract and conclusion present it as a result.
- A 24.5% rise in a *normalized cost score* is retold as "a quarter of the inspection budget".
- The conclusion quotes 4.34% without the range the paper itself says must accompany it.
- The ordering of the debt curves follows from chosen parameters, but the text says it follows "from the mechanisms".
- The worked access-constraint result breaks the framework's own minimum-cell rule: there are 3 women and n^min = 30, and S572 itself says a cell of three people identifies them.

**AI-rewrite patterns.** Moderate overall. The strongest signatures:
- Revision-history leakage (13 locations).
- Generic replacement phrases written by the fix pass ("To resolve procedural circularity", "ensuring lawful affirmative encouragement", "prices exposure ex ante at runtime").
- New enumerative scaffolding.
- Over-asserted compliance language ("Compliance ... is maintained", "To guarantee balanced institutional representation").

**Terminology.** "Price" is still polysemous in 20+ places, including a section heading and two adjacent paragraphs that use it for different objects. This means the first audit's I-20 is *not* resolved. Further mismatches: "Weight Review Panel" vs "Workforce Review Panel"; "intake" vs "cohort" vs "posts" vs "hiring target"; "ten hypotheses" (main) vs "six hypotheses plus four structural properties" (supplement); "Capability Matching / Ergonomics-Aware Role Allocation" (Figure 4) vs "the external baselines of Ranz and Merlo" (Section 7.4).

**Paragraph and section structure.** Related Work §2.4–2.5 is dense chains of citations. §5.2 (contestability) is a single overloaded paragraph. §7.5 lists "four constituencies", but the fourth is not a constituency. The Discussion never maps its results back to RQ1–RQ7.

**Highest risks before submission:** I-001 (stale submission package), I-002 (certification/dilution ambiguity behind "four vs fourteen"), I-003 (worked example violates n^min and the disclosure rule), I-004 (legal compliance asserted), I-005 (λ "rises" vs λ constant), I-006 (cost index treated as budget share).

---

## 2. Coverage Verification

| Item | Record |
|---|---|
| First manuscript line reviewed | M1 (`\documentclass`) |
| Last manuscript line reviewed | M1330 (`\end{document}`) |
| Supplementary lines reviewed | S1–S592 |
| Total line range reviewed | M1–1330 and S1–592 (1,922 lines), read sequentially in full |
| Sections reviewed (main) | Title, metadata, abstract, keywords; §1 Introduction, §1.1 Contributions; §2.1–2.6 Related Work and Gap, RQ list; §3 Framework (problem statement, staffed modes, CAD, Layers 1–6); §4.1–4.8 Architecture, workflow, SCV, weights, program, online rule, Propositions 1–4, AOZ; §5.1–5.5 Governance, contestability, legality, GCC, DPIA; §6.1–6.10 worked allocation, sensitivity, shocks; §7.1–7.7 Discussion, protocol, who wins, threats, limitations; §8 Conclusions; Abbreviations, Acknowledgment, Ethics, Data Availability, Author Contributions, Funding, COI |
| Sections reviewed (supplementary) | S1 Contestability; S2 Protocol (testbed, baselines, metrics, configuration, statistics, stress, hypotheses); S3 Stress schedules; S4 Calibration; S5 Elicitation; S6 Extended related work; S7 Framework detail (groups, D-terms, task vector, policy encoding, gating, conflict order, channels, market); S8 Proofs, anchors, duals, notation; S9 DPIA; S10 Shocks |
| Equations reviewed | Main: 46 numbered (eq:modeset … eq:cadmodel) + 2 unnumbered (ζ̄ definition, Prop. 1) + inline Δ_g (M415); Supplement: 1 numbered (eq:anchors) + inline expressions in proofs |
| Theorems/propositions | Propositions 1–4 (M658–723) and their proofs (S492–502) |
| Algorithms | Algorithm 1 (M618–649), every line |
| Tables reviewed | Main: 10 (tab:comparison, weights, zones, zonetrans, worked-terms, worked-mix, worked-decomp, dist, sensitivity, cadparams); Supplement: 7 numbered (app-windows, app-sectors, app-params, app-predictions, app-stress, app-calib, notation) + 1 unnumbered policy-encoding table (S440–454). Arithmetic in the worked tables was spot-recomputed (SCV, CAD, mixes, λ_k, τ_k, n̂_k, shocks, C(10), residual slopes); all matched except I-140 |
| Figures/captions reviewed | Fig. 1 (arch.png + caption), Fig. 2 (runtime.png + caption), Fig. 3 (TikZ intake curve + caption), Fig. 4 (TikZ debt trajectories + caption) |
| Reference section reviewed | Citation *language* reviewed at every in-text citation (attribution, scope, verbs). `references.bib` (88 entries) was **not** line-verified; bibliographic verification was not requested. Two cited-work characterizations are flagged "verify" (I-087, I-157) rather than asserted wrong |
| Back matter | Reviewed in full |
| Unreviewed regions | **NONE** in the two .tex files. Preamble lines M1–96 and S1–33 were inspected for content only (no prose). `removed_sections.tex`, `CivicWorkOS-diff.tex`, and `submission/*.tex` were not audited line by line (see I-001) |

---

## 3. Critical Issues

**Issue I-001**
- Location: `submission/CivicWorkOS.tex`, `submission/CivicWorkOS_supplementary.tex`, `CivicWorkOS-submission.zip` (whole files)
- Section: Submission package
- Severity: Critical | Priority: P1
- Category: Cross-document consistency
- Original passage: `submission/CivicWorkOS.tex`, line 131: "prices protected practice at 0.0454 objective units per hour"
- Problem: The `submission/` folder and the zip predate the first audit and every `report.md` fix. `diff` shows differences from the root copy in the abstract, introduction, contributions and beyond.
- Why it matters: If the package is uploaded as it stands, none of the revisions reach the journal, and the version submitted contains the errors the first audit flagged as critical.
- Underlying pattern: P-04 (fix propagation failure)
- What to restore/check: Regenerate `submission/` and the zip from the root copies after this audit's fixes, then diff to confirm.
- Related issues: I-082, I-083

**Issue I-002**
- Location: M390–392, M973–985, M1025, M118, M136, M1289; S331
- Section: §3 Layer 4 (HCPB); §6.6 Pipeline arithmetic; Fig. 3; Abstract; Conclusion
- Severity: Critical | Priority: P1
- Category: Technical meaning preservation / Evidence–claim
- Original passage: "Certification schemes count \textit{raw supervised clock hours} $h^{raw}_k$ under solo unassisted practice" (M390); "reached only when $\bar\phi_k\bar\omega_k = 1$, that is, solo unassisted practice" (M1025); "raters supply the supervised clock hours the certification route requires" (S331)
- Problem: Certification hours are described as *supervised* and as *solo unassisted* in the same sentence. The dilution factor 1/(φ̄ω̄) = 1/(0.5925 × 0.5) splits into 1.69 from machine assistance and 2.0 from sharing human work with a lead (ω̄ = 0.5). If certification hours are already supervised hours, worked alongside a lead as the word "supervised" suggests, then ω̄ = 0.5 is already inside h^raw. The factor would then double-count supervision, and τ_k, n̂_k and "four vs fourteen" all change. Under the strict reading, even a fully human apprenticeship (H/a_1) takes 2.4 years, not 1.2.
- Why it matters: "Four trainee posts where fourteen are required" is the cover letter's "central result" and appears in the abstract, introduction and conclusion. A domain reviewer from certification or licensing will ask which reading applies.
- Underlying pattern: P-05 (causal attribution and scope); P-15 (formal precision)
- What to restore/check: Decide whether h^raw counts hours worked as sole operator or hours under supervision. Make M390, M1025 and S331 say the same thing, and report the two dilution components separately wherever 3.38 is quoted.
- Related issues: I-025, I-014, I-016

**Issue I-003**
- Location: M1034–1055 (Table 8), M823; S188, S419–421, S572
- Section: §6.7 Who receives the protected work; S7.1; S9
- Severity: Critical | Priority: P1
- Category: Evidence–claim / Cross-section consistency
- Original passage: "Suppose the 24 incumbents are 21 men and three women" (M1034); "$n^{min}$ & 30 practitioners per cell per domain" (S188); "Cells below $n^{min}$ are reported descriptively with their sample size and are not the subject of a binding constraint" (S421); "Publishing per-cell practice shares for a cell of three people identifies those three people" (S572)
- Problem: Under the framework's own rules, a domain of 24 practitioners has no cell (not even the whole domain) that meets n^min = 30, so no binding access constraint may be applied. Yet Table 8 applies a binding constraint to the 3-woman cell and publishes its shares. The supplement uses "a cell of three people" as its example of an unacceptable disclosure. S421 also says the worked example "uses a single marginal partition", while the M1039 caption says groups are "the marginal partition on gender and contract status" (two attributes).
- Why it matters: The paper's main distributional demonstration (622 → 1,344 hours, "more than doubles", repeated in the conclusion) violates the minimum-cell rule and the disclosure rule the paper itself sets out.
- Underlying pattern: P-04; P-07
- What to restore/check: Reconcile n^min with the worked example (a different illustrative headcount, an explicit exception, or a statement that the example ignores n^min for exposition). Make "single marginal partition" match the table's groups.
- Related issues: I-021, I-072

**Issue I-004**
- Location: M800 (enumerate item 2); M805; `report.md` I-14
- Section: §5.3 Lawfulness of the Capability Access Constraint
- Severity: Critical | Priority: P1
- Category: Claim strength / Legal precision / AI-paraphrase risk
- Original passage: "Compliance with the individual-assessment principle of \textit{Marschall} is maintained because the dual operates only over candidate rosters that have already satisfied the strict competency, safety ($S_{i,m,a} \ge S^{min}_i$), and policy admissibility filters ... ensuring lawful affirmative encouragement."
- Problem: (a) The sentence asserts legal compliance. M805 says proportionality "a municipality's legal office must make and no framework can make for it". (b) S^min_i = risk_i·crit_i is a *task* safety floor; it says nothing about the *individual* candidate. The Marschall saving clause requires an objective assessment of each candidate that can override the preference. Passing a safety filter is not that assessment. (c) `report.md` says this fix states that compliance "strictly requires an administrative hard merit floor ... that dual multipliers cannot override". The current text says something stronger and different.
- Why it matters: A legal reviewer will treat this as a misreading of Marschall. It also contradicts the paper's own caution four sentences later.
- Underlying pattern: P-06 (legal overclaim)
- What to restore/check: Restore conditional language. Separate the task safety floor from individual merit assessment. Make the text match what `report.md` says was done.
- Related issues: I-063, I-064, I-062

**Issue I-005**
- Location: S222, S281, S245 (P7) vs M1124, S583; S227
- Section: S2.6 Stress protocol; S3; Table S4 (P7) vs §6.10 Shock one; S10
- Severity: Critical | Priority: P1
- Category: Cross-section consistency / Technical meaning
- Original passage: "raising $r_k$ raises $B_k$ through Equation~\eqref{eq:hcpb-estimator}, hence $\lambda_k$" (S222); "which raises the dual price $\lambda_k$" (S281); "In arm (v-a), $\lambda_k$ rises and allocation shifts" (S245) vs "$\lambda_k$ stays at 0.0454 and only the mix moves" (M1124) and "the price of an hour does not move" (S583)
- Problem: The supplement states three times that raising attrition raises λ_k. The paper's own exact arithmetic for the same arm shows λ_k unchanged. P7 builds the rise into a pre-specified prediction, and S227 says "Every threshold has been checked against the worked example".
- Why it matters: This misdescribes how the model behaves and leaves a pre-specified hypothesis that the paper's own model contradicts.
- Underlying pattern: P-04
- What to restore/check: Restate the mechanism as the mix moving and λ moving only when the active pair changes. Revise P7 and its refutation criterion to match.
- Related issues: I-095

**Issue I-006**
- Location: M966, M955, M497; S158, S247, S253
- Section: §6.5 What preservation costs; Table S4 (P9)
- Severity: Critical | Priority: P1
- Category: Evidence–claim / Statistical language
- Original passage: "Preservation costing 4.34\% of objective value and costing a quarter of the inspection budget reflect the same underlying reality, but the second framing is the one a finance committee will contest."
- Problem: The "+24.53%" in Table 7 is the change in a *normalized cost score* in [0,1], rescaled "against a trailing twelve-month window" (M497). A ratio of rescaled scores is not a ratio of money, so "a quarter of the inspection budget" does not follow. The same conflation drives P9's "124.5% of Automation-First".
- Why it matters: It turns a dimensionless index into a fiscal claim aimed at policymakers. The speculative coda about a finance committee adds rhetoric without evidence.
- Underlying pattern: P-07 (assumption stated as fact); P-12
- What to restore/check: State that the change is in the normalized cost index, or give the cost model needed to convert it to money.
- Related issues: I-084

---

## 4. High-Priority Issues

**Issue I-007**
- Location: M118; M224; compared with M166, M214 (Table 1), S358
- Section: Abstract; §2.6 Research Gap
- Severity: High | Priority: P1
- Category: Novelty / Cross-section consistency
- Original passage: "Allocation research optimizes fit, throughput, and ergonomics; labor research examines displacement; neither prices the developmental practice" (M118); "no allocation mechanism we know of asks who receives the work that is preserved" (M224)
- Problem: M166 and S358 concede that rostering has handled "constrained training-hour allocation for fifty years" with "qualification maintenance as hard constraints". Table 1 marks nurse rostering ✓ for "Who works" and partial for "Debt priced". The abstract's "neither" and Gap 3's "no allocation mechanism" are stronger than the paper's own positioning.
- Why it matters: Reviewers attack novelty claims that the related-work section itself undercuts.
- Underlying pattern: P-07; scope inflation
- What to restore/check: Scope the gap to municipal human–AI–robot allocation and say what rostering lacks (the prior human/machine decision).
- Related issues: I-042

**Issue I-008**
- Location: M226–236; §6–§8
- Section: §2.6 RQ list; Discussion; Conclusion
- Severity: High | Priority: P1
- Category: Structural / Reasoning
- Original passage: "These gaps motivate seven research questions, addressed in Sections~\ref{sec:framework} to~\ref{sec:discussion}."
- Problem: The five gaps are not mapped to the seven RQs, and no later section says which RQ it answers or how. RQ6 ("Can a resilience reserve preserve critical services under automation failure?") and RQ7 can only be answered by the unexecuted protocol (S220). RQ2's double-counting question is answered by definition (M296).
- Why it matters: A Hypothesis and Theory paper should tell readers which RQs are answered analytically, which are only specified, and which stay open.
- Underlying pattern: Structural (missing closure)
- What to restore/check: Add a gap→RQ→section→status mapping, either in §7.2 or as a table.
- Related issues: I-076

**Issue I-009**
- Location: M284; compared with M296, M495, M145
- Section: §3.1 Civic Automation Debt
- Severity: High | Priority: P1
- Category: Terminology / Technical meaning
- Original passage: "We define \textit{Civic Automation Debt} (CAD) as an instantaneous operational penalty that quantifies deferred institutional liabilities"
- Problem: Twelve lines later CAD components are defined as "marginal proxies for changes in municipal stocks", *as opposed to* "operational flows" (M296). At M495 "the ninth is a change in municipal stocks". Calling CAD "instantaneous operational" contradicts the flow/stock separation that RQ2 and the double-counting argument depend on. The sentence was inserted by the I-09 fix.
- Why it matters: The defining sentence of the paper's central construct contradicts its own measurement-domain argument.
- Underlying pattern: P-04; AI-paraphrase risk
- What to restore/check: Use one characterization (per-task marginal proxy for a stock change) at M284, M296 and M495.
- Related issues: I-109

**Issue I-010**
- Location: M435
- Section: §3 Layer 5 Resilience Reserve
- Severity: High | Priority: P1
- Category: Mathematical–prose alignment
- Original passage: "so what survives an AI-service outage or a fleet compromise is exactly the human capacity in the second term of~\eqref{eq:cs}"
- Problem: Eq. (res-def) removes only the n_s *largest* automation components. With more than n_s components, the surviving automation stays in Res. The prose holds only when every automation component is lost.
- Why it matters: It overstates what the N−1/N−2 criterion protects and misdescribes the equation directly above it.
- Underlying pattern: P-15
- What to restore/check: Add the condition, or describe the surviving capacity correctly.
- Related issues: I-047

**Issue I-011**
- Location: M368; S468
- Section: §3 Layer 3 Policy Digital Twin; S7.6 Conflict order
- Severity: High | Priority: P1
- Category: Mathematical–prose alignment
- Original passage: "a lower-ranked rule can never relax a higher-ranked one" (M368); "a rule may be overridden only by a rule of strictly higher $\mathrm{authority}$" (S468)
- Problem: Eq. (policy) is a pure lattice join: the most restrictive status wins *regardless of authority*. Under a join, no rule of any rank can relax another. The prose suggests a higher-ranked rule can relax a lower one, which the formalism does not allow. The authority field therefore plays no role in Eq. (policy).
- Why it matters: The decision semantics of the Policy Digital Twin are left ambiguous.
- Underlying pattern: P-15
- What to restore/check: Either formalize authority-ordered override or state that authority only orders tie-breaking and provenance.
- Related issues: I-053, I-067

**Issue I-012**
- Location: M585; S523; compared with M651, M1237
- Section: §4.6 Online allocation; S8.3 Duals
- Severity: High | Priority: P1
- Category: Technical precision / Claim strength
- Original passage: "so~\eqref{eq:aug} approximates the relaxed program with error bounded by the integrality gap the solver reports"
- Problem: The integrality gap bounds the difference between the LP and IP optimal *values*. It does not bound the error of a per-arrival greedy rule run on stale duals. M651 ("exact only when the duals are exact and the state has not drifted") and M1237 (stale prices, covering constraint, non-stationarity) contradict the "bounded by" claim.
- Why it matters: This is a formal-sounding guarantee the paper elsewhere says it does not have.
- Underlying pattern: P-15
- What to restore/check: Limit the statement to what the integrality gap actually measures.
- Related issues: I-015

**Issue I-013**
- Location: M605; S435–456; `report.md` I-11
- Section: §4.6 Admissibility test
- Severity: High | Priority: P1
- Category: Reader orientation / Evidence–claim
- Original passage: "practical implementations smooth the threshold using a hysteresis band around $\bar{B}_k(t)$ or a proportional-integral filter on $\delta_k(t)$ (Appendix~\ref{app:framework-policy})"
- Problem: Appendix S7.4 (app:framework-policy) contains only the Article 14 encoding, with no hysteresis or PI content, so the cross-reference leads nowhere. The smoothing is also outside Proposition 4 and the admissibility test (Eq. admis), and "practical implementations" implies implementations exist. The 90-word sentence quotes the full disjunction inline.
- Why it matters: The reader is told a vulnerability is handled when the handling is not specified anywhere.
- Underlying pattern: P-04; P-15
- What to restore/check: Either specify the smoothing where the reference points, or describe it as an unanalyzed option.
- Related issues: I-015

**Issue I-014**
- Location: M681, M694; S496
- Section: §4.7 Proposition 2 and proof
- Severity: High | Priority: P1
- Category: Mathematical precision
- Original passage: "zero covariance across the assigned task stream ($\mathbb{E}[\ell_i\phi_m\omega_{a,w}] = \overline{learn}_k\bar\phi_k\bar\omega_k$)"
- Problem: (a) ℓ_i = learn_i·d_i is in hours per task, while learn̄_k is a per-clock-hour rate, so the two sides have different units. The accrual rate per clock hour needs the condition on learn_i, d-weighted. (b) Pairwise zero covariance is not sufficient for E[XYZ] = E[X]E[Y]E[Z] across three variables. (c) `report.md` says the condition is over "ψ_a", but the text uses ω_{a,w}.
- Why it matters: This is the proposition that produces 3.38 and 4.05 years.
- Underlying pattern: P-15
- What to restore/check: Restate the condition on learn_i with the correct independence or factorization assumption, and align `report.md`.
- Related issues: I-002, I-056

**Issue I-015**
- Location: M715–725; S502; S583
- Section: §4.8 Proposition 4 and proof
- Severity: High | Priority: P1
- Category: Mathematical–prose alignment
- Original passage: "let $\bar\delta_g=\max_{i,m,a}\delta^{disp}_g(i,m,a)$ ... $\Delta_g \leq \tau_g + \bar\delta_g$" (M715–717) vs proof "Where the estimate $\delta^{disp}_g$ used at decision time is revised after execution by at most $\bar\delta_g$" (S502)
- Problem: The statement defines δ̄_g as the largest one-task displacement increment. The proof uses it as the largest *revision of an estimate*. These are different quantities, and the revision bound is assumed rather than derived. The proof also does not cover the Zone Z4 fallback (M610, Alg. line 641), which skips the admissibility brackets, so "the resource bound is exact" is unproved when Z4 consumes human hours. S583 overstates the result as bounding "the drift between rebalances".
- Why it matters: The online-enforcement claim at M725 rests on a statement whose proof argues something else.
- Underlying pattern: P-15
- What to restore/check: Align the definition with the proof and handle the Z4 path explicitly.
- Related issues: I-050, I-012

**Issue I-016**
- Location: M118, M968, M1289
- Section: Abstract; §6.5; Conclusion
- Severity: High | Priority: P1
- Category: Evidence–claim (tautology as finding)
- Original passage: "yields 3.46 competent-equivalents a year against attrition of 2.88" (M118); "Constraint satisfaction converts net cohort loss into net workforce replenishment" (M968)
- Problem: B_k/h_k = η_k N_k r_k (M968 states the identity), so 3.456 = 1.2 × 2.88 by the choice η_k = 1.2. Replenishment exceeding attrition is an input, not a result of the analysis.
- Why it matters: The abstract and conclusion present a parameter choice as evidence.
- Underlying pattern: P-12
- What to restore/check: Present the figure as a consequence of meeting the budget at η = 1.2.
- Related issues: I-022

**Issue I-017**
- Location: M836, M902, M905
- Section: §6.1, §6.4
- Severity: High | Priority: P1
- Category: Methods / Hidden assumption
- Original passage: "generating $n_k = 2{,}100$ inspection events per year of mean duration 10 hours and mean learning value 0.80" (M836); "admits at most two nonzero variables at an LP vertex" (M902)
- Problem: The LP aggregation treats all 2,100 inspections as identical to T_i, with the same term vector, rosters, S and ℓ, but the text gives only *means* for duration and learning value. The two-mode vertex argument and the integer rounding (594 vs 595 tasks) need homogeneity, which is never stated.
- Why it matters: Readers cannot tell whether the worked optimum generalizes to a heterogeneous stream.
- Underlying pattern: Hidden assumption
- What to restore/check: State the homogeneity assumption explicitly.
- Related issues: I-135

**Issue I-018**
- Location: M887, M935, M1289; `report.md` I-20
- Section: §6.2, §6.4, Conclusion
- Severity: High | Priority: P1
- Category: Terminology / Causal reasoning
- Original passage: "on these inputs the reversal is produced by the hard constraint, not the price" (M887); "The capability price reverses the winner" (M935); "A capability marginal opportunity cost of 0.0454 objective units per protected-practice hour reverses the winning staffed mode" (M1289)
- Problem: "The price" means w_9 at M887 and λ_k at M935. The conclusion then makes the dual, which is a *consequence* of the binding constraint, the *cause* of the reversal. This blurs the price-vs-constraint distinction that Proposition 3 and §4.6 were written to make.
- Why it matters: The conclusion misstates the paper's own mechanism.
- Underlying pattern: P-02
- What to restore/check: Attribute the reversal to the binding constraint, as M887 does, and reserve one term for each of w_9 and λ_k.
- Related issues: I-019, P-02 locations

**Issue I-019**
- Location: S360, S475 vs M926
- Section: S6.2; S7.7
- Severity: High | Priority: P1
- Category: Cross-section consistency
- Original passage: "whereas the objective here prices the future value of the practice itself" (S360); "how much developmental practice is worth" (S475) vs "not the value of an hour of practice, which the framework neither estimates nor needs" (M926)
- Problem: The supplement says the framework values practice. The main text explicitly denies that it does.
- Why it matters: This contradicts the first audit's I-03 fix, which the main text carries.
- Underlying pattern: P-02; P-04
- What to restore/check: Make the supplement match M926.
- Related issues: I-018

**Issue I-020**
- Location: M1117 ("Second, ...")
- Section: §6.9 Sensitivity
- Severity: High | Priority: P1
- Category: Robustness claim / Scope
- Original passage: "the \textit{mode} reversal is not robust: it requires $\phi_{H+A+R} \leq 0.55$ and $\psi_{a_1} \leq 0.5$"
- Problem: Table 9 shows no reversal also at h^raw ∈ {1200, 1500}, r_k ∈ {0.06, 0.09} and η_k = 0.8, all with the φ and ψ values at baseline. The reversal requires B_k/Φ_k > φ_{H+A+R}·ψ_{a_1}, so it also depends on the budget side. The sentence lists only two of the conditions and so understates how fragile the result is.
- Why it matters: It misreports the paper's own robustness table.
- Underlying pattern: P-15 (incomplete condition)
- What to restore/check: State the full condition.
- Related issues: I-073

**Issue I-021**
- Location: M1036, M1034, M400
- Section: §6.7; §3 Layer 4b
- Severity: High | Priority: P1
- Category: Hidden assumption / Causal chain
- Original passage: "2.16 times the composition-blind rate, achieved without changing $B_k$, the weights, or any estimate, and meaning 3.8 of the 14 developing posts"
- Problem: The access constraint governs *practice among developing practitioners*. Having 3.8 of 14 developing posts held by women requires *recruiting* those trainees, which is a hiring decision outside x. "Achieved without changing ... any estimate" hides that change. The composition-blind baseline in turn assumes recruitment "through the channels that produced the incumbents" (M1034, M400), which is asserted rather than supported.
- Why it matters: The distributional headline depends on an unmodeled recruitment step.
- Underlying pattern: P-07
- What to restore/check: Make the recruitment assumption explicit in both scenarios.
- Related issues: I-003, I-046, I-071

**Issue I-022**
- Location: M1230; S227, S240, S243
- Section: §7.2; Table S4
- Severity: High | Priority: P1
- Category: Reasoning / Claim strength
- Original passage: "any $SCV$-maximizing policy necessarily sacrifices some operational productivity and budget efficiency to preserve human capability; this trade-off is a structural analytical property ... (reflected in properties P2, P3, P5, and P9)"; "which Section~\ref{sec:sensitivity} bounds analytically between 0.33\% and 9.60\%"
- Problem: (a) The SCV loss can fall on any term. If a developmental mode has higher P, there is no productivity loss, so "necessarily ... productivity" is false in general. (b) The trade-off comes from the binding constraints, not from "−w_9 CAD enters the objective". (c) P2 (≥80% of productivity) and P5 (HCPB ablation dominates every other ablation) are *magnitude* claims, which is exactly what this same paragraph calls "the substantive question", yet they are labeled [Structural]. (d) A one-at-a-time sweep does not "bound" the cost: joint variation can exceed 9.60%, and the infeasible region is excluded. (e) "Whether the system remains satisfiable at municipal scale" is not addressed by a single-domain sweep.
- Why it matters: The paragraph meant to mark the epistemic boundary ends up blurring it.
- Underlying pattern: P-12; P-15
- What to restore/check: Separate the sign (structural) from the threshold (empirical). Use "ranges over the swept values" instead of "bounds".
- Related issues: I-016, I-030

**Issue I-023**
- Location: M1146, M1149, M1213, M1221, M1223
- Section: §7.1 Debt model; Table 10; Fig. 4
- Severity: High | Priority: P1
- Category: Evidence–claim / Epistemic boundary
- Original passage: "\textit{The ordering of the curves is not evidence.} It follows analytically from the mechanisms each strategy enforces" (M1223); "because Human-First never closes its skill gap" (M1221)
- Problem: The ordering follows from the π_{j,∞}, τ_j and c_j values the authors chose. Table 10's caption says so ("illustrative choices"). Human-First's π_skill = 0.15 and the baselines' π values are assigned, not derived. Saying the ordering follows "from the mechanisms" and giving a reason ("never closes its skill gap") present an assumption as a derivation, so the crossover at 13.23 is a product of the inputs.
- Why it matters: `report.md` §D lists the crossover among "negative findings". It is a parameter choice, not a finding.
- Underlying pattern: P-12
- What to restore/check: Attribute the ordering to the tabulated parameters and justify each π value.
- Related issues: I-075, I-078

**Issue I-024**
- Location: M1289 vs M1117; also M940
- Section: Conclusion; §6.5
- Severity: High | Priority: P1
- Category: Cross-section consistency / Claim strength
- Original passage: "costs 4.34\% of annual objective value" (M1289) vs "wherever this article quotes 4.34\%, Table~\ref{tab:sensitivity} is the range that should accompany it" (M1117)
- Problem: The conclusion, and §6.5 at M940, quote 4.34% without the range, breaking the paper's own stated rule. The abstract does include the range.
- Why it matters: It invites the charge of reporting a single point estimate selectively.
- Underlying pattern: P-04
- What to restore/check: Add the 0.33–9.60% range wherever 4.34% is quoted.
- Related issues: —

**Issue I-025**
- Location: M147, M694, M985, M1289
- Section: Contributions; §4.7; §6.6; Conclusion
- Severity: High | Priority: P1
- Category: Scope creep / Causal attribution
- Original passage: "demonstrate that automation slows the development of each practitioner" (M147); "A city cannot see the dilution factor without this framework" (M694); "No headcount plan surfaces this ... A city that automates more aggressively forms each practitioner more slowly" (M985); "a city automating its junior work does not merely form fewer practitioners, it forms each remaining one more slowly" (M1289)
- Problem: Observed scope: one worked domain with illustrative inputs, where 2.0 of the 3.38 factor comes from shared supervision. Claimed scope: automation in general, for all cities, and the claim that no plan or other method can see the effect. M136 phrases it correctly ("machine assistance and shared supervision"). The later restatements drop that qualification.
- Why it matters: The paper's most quotable finding is over-generalized and over-attributed to automation.
- Underlying pattern: P-05
- What to restore/check: Carry M136's two-cause framing and the single-domain scope into M147, M985 and M1289. Drop "cannot"/"no headcount plan" or support them.
- Related issues: I-002

**Issue I-026**
- Location: S129, S286 vs M827, M836
- Section: Table S2; S4; §6
- Severity: High | Priority: P1
- Category: Cross-document consistency / Evidence
- Original passage: "Infrastructure inspection & 2{,}100 & ... & Calibrated" (S129); "no result reported in this article depends on any of them" (S286) vs "The inputs are illustrative expert estimates rather than measurements" (M827)
- Problem: The worked example's n_k = 2,100 is the same figure the supplement labels "Calibrated ... fitted to the named open municipal series". The main text calls it illustrative, and S286 says no result depends on these figures, but the whole worked case depends on 2,100.
- Why it matters: The evidential status of an input is described in two incompatible ways.
- Underlying pattern: P-04
- What to restore/check: Choose one status for 2,100 and make all three locations agree.
- Related issues: —

**Issue I-027**
- Location: S149 vs S147, S241
- Section: S2.2 Baselines; Table S4 (P3)
- Severity: High | Priority: P1
- Category: Experimental design / Claim strength
- Original passage: "both would be given the availability-ordered roster that Human-First uses. Neither adaptation advantages CivicWorkOS"
- Problem: A roster chosen by availability, with no developmental eligibility, credits zero practice in the worked domain. P3's worked value is "1.00 against 0.00" for Capability Matching. The adaptation therefore structurally guarantees that CivicWorkOS wins on the capability metrics.
- Why it matters: The fairness claim about the planned comparison is contradicted by the protocol's own table.
- Underlying pattern: P-07
- What to restore/check: Acknowledge the advantage, or specify a roster rule for the baselines that does not build in the result.
- Related issues: I-084

**Issue I-028**
- Location: M926
- Section: §6.4
- Severity: High | Priority: P1
- Category: AI-rewrite pattern (revision-history leakage)
- Original passage: "earlier presentations inverted the reading"
- Problem: The text refers to unpublished earlier drafts. A first-submission reader has no earlier version to compare against.
- Why it matters: The article reads as a response to reviewers and suggests an error history to editors without informing the reader.
- Underlying pattern: P-01
- What to restore/check: Move the revision history to the cover letter or response document.
- Related issues: I-029, I-045, I-091–I-100

**Issue I-029**
- Location: M1244
- Section: §7.4 Protocol
- Severity: High | Priority: P1
- Category: AI-rewrite pattern (revision-history leakage)
- Original passage: "an earlier version of this article wrongly called that bias conservative"
- Problem: Same as I-028. This sentence also introduces "calibration portals", which the main text never defines.
- Why it matters: Same as I-028.
- Underlying pattern: P-01
- What to restore/check: Same as I-028.
- Related issues: I-028

---

## 5. Medium-Priority Issues

**Issue I-030** · M151, M1246 vs S227 · Contributions; §7.4; S2.7 · Medium · P1 · Cross-section consistency
- Original passage: "ten pre-specified hypotheses and refutation criteria" (M151)
- Problem: The supplement now lists six empirical hypotheses and four structural or calibrated properties. The main text was not updated after the first audit's I-02 fix.
- Why it matters: Readers see two different counts of what is being tested.
- Underlying pattern: P-04
- What to restore/check: Use one count and one label throughout.
- Related issues: I-022

**Issue I-031** · M118 · Abstract · Medium · P2 · Referent
- Original passage: "the constraint reveals a marginal opportunity cost of 0.0454"
- Problem: Four constraints were named two sentences earlier, so "the constraint" has no clear referent. "Reveals" also implies discovery of something pre-existing.
- Why it matters: Readers cannot tell which constraint the 0.0454 belongs to.
- Underlying pattern: P-03 (ambiguous referent)
- What to restore/check: Name the HCPB.
- Related issues: —

**Issue I-032** · M130 · Introduction · Medium · P2 · Claim strength
- Original passage: "Every task-allocation decision produces winners and losers, yet cities make these determinations without any mechanism that records who bears the burden."
- Problem: Two universal claims ("every", "without any") with no support.
- Why it matters: Rhetorical overreach in the opening paragraph invites skepticism.
- Underlying pattern: P-07
- What to restore/check: Scope the claims or cite support.
- Related issues: —

**Issue I-033** · M132–134 · Introduction · Medium · P2 · Referent / Information order
- Original passage: "We treat that second half as constitutive."
- Problem: "That second half" refers to a clause in the previous one-sentence paragraph, and "constitutive" of what is never said.
- Why it matters: The reader has to reconstruct the referent across a paragraph break.
- Underlying pattern: P-03
- What to restore/check: Name the referent and the object of "constitutive".
- Related issues: —

**Issue I-034** · M134 · Introduction · Medium · P2 · Evidence
- Original passage: "nor the developmental work that transforms a novice into an expert is distributed evenly"; "remains invisible both to standard operational productivity metrics and to conventional post-deployment equity audits"
- Problem: The claim of uneven distribution has no citation. The invisibility claim is a generalization. "Allocations occur on a single ... task at a time" is ungrammatical.
- Why it matters: Unsupported empirical claims early in the paper weaken its credibility.
- Underlying pattern: P-07
- What to restore/check: Add citations or scope the claims; fix the grammar.
- Related issues: —

**Issue I-035** · M144 · Contributions · Medium · P2 · Technical word choice
- Original passage: "renders distributional questions mathematically tractable"
- Problem: In this paper "tractable" means computationally solvable (M562, M1273). Here the intended sense is "expressible".
- Why it matters: The word collides with its technical use elsewhere.
- Underlying pattern: Terminology
- What to restore/check: Use a word meaning "expressible".
- Related issues: —

**Issue I-036** · M148 · Contributions · Medium · P2 · Claim strength
- Original passage: "preventing a budget sized from the incumbent workforce from reproducing its demographic composition"
- Problem: The constraint is elastic (slack ς) and depends on recruitment (I-021). It can limit or expose reproduction, not prevent it.
- Why it matters: The contribution promises more than the mechanism delivers.
- Underlying pattern: P-07
- What to restore/check: Weaken "preventing" to what the constraint actually does.
- Related issues: I-021

**Issue I-037** · M166 · §2.1 · Medium · P2 · Reasoning
- Original passage: "Second, conventional rostering optimizes immediate coverage, whereas our formulation penalizes deferred capability loss and bounds developmental practice directly through constraints."
- Problem: The same paragraph says rostering already carries "qualification maintenance as hard constraints", so bounding practice through constraints is not a difference.
- Why it matters: The stated distinction from prior work does not hold as written.
- Underlying pattern: Novelty
- What to restore/check: Restate the second difference so it is a real one.
- Related issues: I-007

**Issue I-038** · M171 · §2.2 · Medium · P1 · Citation attribution / Math–prose
- Original passage: "which skill-decay meta-analyses~\citep{Arthur1998,TatelAckerman2025} operationalize into the practice intervals calibrating $D^{skill}$"
- Problem: D^skill = 1 − φ_mψ_a (Eq. dskill) has no practice-interval term. M1264 concedes that retention functions are *absent*. The meta-analyses also do not operationalize Zuboff's distinction.
- Why it matters: The citation is used to claim a calibration the model does not have.
- Underlying pattern: P-07
- What to restore/check: Use conditional wording, as S367 does ("would use").
- Related issues: —

**Issue I-039** · M173 · §2.2 · Medium · P2 · Causal compression
- Original passage: "this warrants treating fallback capacity separately from present competence, as $D^{fall}$ does"
- Problem: The municipal scale of the question does not imply the fallback/competence split. S369 derives it from the Bainbridge literature; the main text lost that step.
- Why it matters: The conclusion appears without its premise.
- Underlying pattern: P-08 (compression)
- What to restore/check: Restore the missing step.
- Related issues: —

**Issue I-040** · M187 · §2.4 · Medium · P2 · Citation scope / Density
- Original passage: "exposure falls unevenly, on platform workers outside municipal protections~\citep{Wood2019,DeStefano2016} and on the poorest residents~\citep{Eubanks2018}"
- Problem: Eubanks concerns errors in automated public-service decisions affecting recipients. That is a different "exposure" from job exposure, but the sentence merges them. The paragraph chains ten citations in four sentences.
- Why it matters: Two different notions of exposure are presented as one finding.
- Underlying pattern: P-14
- What to restore/check: Separate the two notions; thin the citation chain.
- Related issues: —

**Issue I-041** · M194 · §2.5 · Medium · P2 · Paragraph purpose
- Original passage: "Resilience is a related but distinct concept, used inconsistently across the infrastructure literature~\citep{Mentges2023}; response networks recover faster..."
- Problem: The paragraph mixes robot policy, trust, workforce readiness, digital twins and resilience. The resilience sentence has no link to what comes before it.
- Why it matters: The paragraph has no single point.
- Underlying pattern: P-14
- What to restore/check: Give the paragraph one purpose and move or connect the resilience sentence.
- Related issues: —

**Issue I-042** · M224 · §2.6 · Medium · P2 · Evidence / Voice
- Original passage: "reproduces its composition ... under the honorable name of preserving expertise, converting a protective mechanism into an exclusionary barrier"
- Problem: A predicted effect is stated as fact, wrapped in rhetorical irony.
- Why it matters: Rhetoric stands in for evidence at the point where the gap is argued.
- Underlying pattern: P-07; P-09
- What to restore/check: State the effect as a prediction.
- Related issues: I-007

**Issue I-043** · M315 vs S433 · §3 Layer 1 · Medium · P1 · Units
- Original passage: "criticality, and execution time in hours, each normalized to $[0,1]$"
- Problem: d_i is in hours (d_i = 10 at M832). If it were normalized, ℓ_i = learn_i·d_i would not be in qualified-practice hours. S433 correctly normalizes only nine dimensions.
- Why it matters: The units of the budget's denominator become ambiguous.
- Underlying pattern: P-15
- What to restore/check: Exclude d_i from the normalization statement.
- Related issues: —

**Issue I-044** · M352–362 · §3 Layer 3 · Medium · P2 · AI-paraphrase / Terminology
- Original passage: "To resolve procedural circularity between rule evaluation and roster generation ... a mode-level screening twin ... a candidate roster-guard filter"
- Problem: The opening clause responds to a reviewer, not to the reader. P_mode is a status function, not a "twin". 𝒢_roster returns a status, not a filter.
- Why it matters: Revision-response language and loose naming obscure what the objects are.
- Underlying pattern: P-01; P-13
- What to restore/check: Name the objects for what they are.
- Related issues: I-053

**Issue I-045** · M385 · §3 Layer 4 · Medium · P2 · Revision leakage
- Original passage: "The factor $\psi_a$ is the substantive repair"
- Problem: "Repair" of what? The word presupposes an earlier, flawed version.
- Why it matters: Same leakage as I-028.
- Underlying pattern: P-01
- What to restore/check: Describe what ψ_a does instead.
- Related issues: I-028

**Issue I-046** · M400 · §3 Layer 4b · Medium · P2 · Assumption as fact
- Original passage: "because developing practitioners are recruited through the pipelines that produced the incumbents, a composition-blind budget reproduces the incumbent composition"
- Problem: An empirical premise is stated as fact without a citation.
- Why it matters: The access constraint's motivation rests on an unsupported claim.
- Underlying pattern: P-07
- What to restore/check: Cite or hedge.
- Related issues: I-021

**Issue I-047** · M442, M554 · §3 Layer 5; Program · Medium · P1 · Math–prose
- Original passage: "starving a domain of human practice degrades $F_k(t)$ and eventually breaches~\eqref{eq:res3r}"; "$Res^{(n_s)}_s(\mathbf{x})$"
- Problem: Res is defined through F_k(t), which depends on x only through career-stage changes over years. Res(x) is never defined as a function of the window's decisions. "Eventually breaches" is unconditional, although a breach depends on how large the human contribution is relative to ρ_s.
- Why it matters: The program has a constraint whose dependence on the decision variable is undefined.
- Underlying pattern: P-15
- What to restore/check: Define Res(x) and make the breach claim conditional.
- Related issues: I-010

**Issue I-048** · M417, M437–439, M602, M574, M683, M1134–1137, M1235; S528 · Notation · Medium · P1 · Notation collision
- Original passage: "Two collisions present in earlier presentations have been removed" (S528)
- Problem: Several symbols carry more than one meaning:
  - τ_g is the displacement ceiling, τ_k the formation time, τ_j the debt time constant.
  - κ(i) maps a task to its domain; κ_s is the servable share.
  - ρ is a policy rule; ρ_s is a reserve threshold.
  - δ is a CAD weight, δ_k the catch-up increment, δ^disp_g the displacement increment.
  - π_{a,g} is a group share; π_j is replenishment.
  - ε is a CAD weight, ε_k the access tolerance, and the "(1−ε)-competitive" ratio.
  - Λ_k takes the arguments (ΔT), (x), (t) and (t⁺|m,a).
  - Res^{(n)} is used in S528 and S553, Res^{(n_s)} in the main text.
- Why it matters: Readers must disambiguate symbols from context. S528's "collisions removed" claim is misleading.
- Underlying pattern: P-03
- What to restore/check: Give each concept its own symbol and correct S528.
- Related issues: I-075, I-161

**Issue I-049** · M454 vs S480 · Layer 6; S7.8 · Medium · P2 · Consistency
- Original passage: "five \textit{capability agents} estimate the flow terms and five \textit{civic agents} the stock changes"
- Problem: Civic agents estimate the flow terms Pr and Eq^srv. No agent is assigned D^acct, D^dep, Q, P or Tr.
- Why it matters: The agent partition described in the main text does not match the supplement's list.
- Underlying pattern: P-04
- What to restore/check: Align the partition and assign every term to an agent.
- Related issues: I-101

**Issue I-050** · M574, M715 · §4.6, §4.8 · Medium · P1 · Reader orientation
- Original passage: "$\sum_{g}\varrho_g\,\delta^{disp}_g(i,m,a)$"
- Problem: δ^disp is used in Eq. (aug) and Proposition 4 but never defined, in the main text or the notation table.
- Why it matters: A symbol central to Proposition 4 has no definition.
- Underlying pattern: P-03
- What to restore/check: Define δ^disp_g.
- Related issues: I-015

**Issue I-051** · M581–582 · Eq. deltares · Medium · P2 · Math precision
- Original passage: "$(m,a) \text{ generalized across } s$"
- Problem: The counterfactual is undefined. The left-hand side lacks the index i that the right-hand side uses (d_i).
- Why it matters: The equation cannot be evaluated as written.
- Underlying pattern: P-15
- What to restore/check: Define the counterfactual and fix the indexing.
- Related issues: —

**Issue I-052** · M562 · §4.5 · Medium · P2 · Claim strength
- Original passage: "which Section~\ref{sec:legality} shows to be a legal requirement"
- Problem: §5.3 argues a position; it does not "show" a requirement.
- Why it matters: A legal argument is presented as a demonstration.
- Underlying pattern: P-06
- What to restore/check: Use "argues".
- Related issues: I-004

**Issue I-053** · M630 vs M362–366 · Algorithm 1 · Medium · P2 · Algorithm–equation alignment
- Original passage: "\If{$z = \textit{restrict}$} \State prune $\mathcal{A}_{i,m}$ using roster guards"
- Problem: Eq. (policy) joins 𝒢_roster for every (m,a), but the algorithm evaluates roster guards only when the mode-level status is *restrict*. A roster-level *prohibit* under a mode-level *allow* is caught only later, by the admissibility test.
- Why it matters: The algorithm and the equation it claims to implement differ.
- Underlying pattern: P-04
- What to restore/check: Align the algorithm with Eq. (policy).
- Related issues: I-054

**Issue I-054** · M651 · §4.6 · Medium · P2 · Stale count
- Original passage: "Algorithm~\ref{alg:scv} performs at most seven policy queries"
- Problem: Seven was the mode-level count. Since 𝒢_roster was added, queries scale with the number of rosters.
- Why it matters: A complexity claim no longer matches the algorithm.
- Underlying pattern: P-04
- What to restore/check: Recount.
- Related issues: I-053

**Issue I-055** · M662 · Proposition 1 · Medium · P2 · Circular definition
- Original passage: "$(m,a)$ admissible for some $i\in\mathcal{T}_k$"
- Problem: Admissibility (Eq. admis) includes the budget guard on B_k, so ζ̄ depends on the budget that the proposition tests.
- Why it matters: The feasibility condition is defined in terms of itself.
- Underlying pattern: P-15
- What to restore/check: Define ζ̄ over policy- and safety-admissible modes only.
- Related issues: —

**Issue I-056** · M147, M686–691, M985, M1289 · Proposition 2 · Medium · P2 · Terminology
- Original passage: "translate the budget into an explicit hiring target" (M147); "intake cohort" (M686); "trainee posts" (M985)
- Problem: n̂_k is a stock (a cohort held in steady state). "Intake" and "hiring target" suggest an annual flow, which is η N r = 3.456 a year.
- Why it matters: A reader could read 14 as a yearly hiring number.
- Underlying pattern: Terminology drift
- What to restore/check: Use one term that clearly denotes a stock.
- Related issues: —

**Issue I-057** · M699, M703–708 · §4.8, Proposition 3 · Medium · P2 · Math–prose
- Original passage: "identifies the exact boundary where debt pricing actively alters allocation versus where hard constraints govern"; "any difference in the realized allocation is attributable to the constraints"
- Problem: The proposition is stated for the arg max of SCV, but online selection uses SCṼ with the duals. The attribution sentence is an interpretation, not part of what is proved. "A framework named after a priced construct" is inaccurate: the framework is named CivicWorkOS.
- Why it matters: The proposition is presented as covering the online rule, which it does not.
- Underlying pattern: P-15
- What to restore/check: State the scope (SCV, not SCṼ) and separate the interpretation from the result.
- Related issues: I-018

**Issue I-058** · M778 · §5.1 · Medium · P2 · AI-rewrite / Claim strength
- Original passage: "To guarantee balanced institutional representation, the panel structure mandates participation from three groups"
- Problem: Panel membership cannot "guarantee" balance. Residents, whose service equity is in the objective, are not among the mandated groups.
- Why it matters: A governance claim is overstated and has a visible gap.
- Underlying pattern: P-06
- What to restore/check: Soften "guarantee" and address resident representation.
- Related issues: —

**Issue I-059** · M497, M780, M1271 · §4.3, §5.1, Limitations · Medium · P2 · Technical precision
- Original passage: "lies on the convex hull of the attainable set"
- Problem: Weighted sums reach supported points on the boundary of the convex hull. With binary variables the attainable set is discrete. The idea is also repeated three times (useful reinforcement, but the wording is imprecise each time).
- Why it matters: An expert reader will notice the imprecision.
- Underlying pattern: P-15
- What to restore/check: Use the precise statement once and refer back to it.
- Related issues: —

**Issue I-060** · M787 · §5.2 · Medium · P2 · Density / Paragraph structure
- Original passage: the whole paragraph (about 330 words: standing, windows, record, remedy, trigger, aphorism)
- Problem: One paragraph carries four sub-specifications and two rhetorical claims ("is measuring something it has not built").
- Why it matters: Readers cannot hold all four parts at once.
- Underlying pattern: P-08
- What to restore/check: Give each element its own paragraph.
- Related issues: —

**Issue I-061** · M789 · §5.2 · Medium · P2 · Unsupported claim
- Original passage: "gain most of the accountability benefit before any optimization is built"
- Problem: A quantitative-sounding claim with no basis.
- Why it matters: It reads as a result when it is a guess.
- Underlying pattern: P-07
- What to restore/check: Hedge or remove the quantity.
- Related issues: I-147

**Issue I-062** · M794–796 · §5.3 · Medium · P2 · Legal precision
- Original passage: "A mechanism that allocates scarce developmental work against a composition target defined over gender or district"; "Directive 2000/78/EC ... and Directive 2006/54/EC ... prohibit direct discrimination"
- Problem: Directive 2000/78 does not cover sex, and district is not a protected ground under either directive. The cited cases predate 2006/54 (they were decided under 76/207/EEC).
- Why it matters: Legal reviewers will check scope and dates.
- Underlying pattern: P-06
- What to restore/check: Check which directive covers which ground and state the case-law basis accurately.
- Related issues: I-064

**Issue I-063** · M801 · §5.3 item 3 · Medium · P1 · Claim strength
- Original passage: "a municipality is never placed in a situation where the only feasible solution requires an unlawful allocation"
- Problem: Only the access constraint has slack. The HCPB, reserve and policy constraints can still force assignments. "Never" covers the whole program.
- Why it matters: An absolute legal-safety claim is wider than the mechanism behind it.
- Underlying pattern: P-06
- What to restore/check: Scope the claim to the access constraint.
- Related issues: I-004

**Issue I-064** · M802 · §5.3 item 4 · Medium · P1 · Legal precision (verify)
- Original passage: "a target on \textit{contract status}, which is not a protected ground under either directive; nor is career stage"
- Problem: EU law protects fixed-term and part-time workers against less favorable treatment (Directives 1999/70/EC and 97/81/EC). Career stage is closely tied to age, which Directive 2000/78 protects, so indirect age discrimination is possible.
- Why it matters: The "no exposure" claim may not survive legal review.
- Underlying pattern: P-06
- What to restore/check: Verify against those directives and qualify the claim.
- Related issues: I-062

**Issue I-065** · M816 · §5.4 · Medium · P2 · Misattribution
- Original passage: "which is the gap $\psi_a$ closes in~\eqref{eq:hcpb}"
- Problem: ψ_a credits developing practitioners, not nationals. The national-succession gap is closed by Eq. (access) with g ranging over nationality, as the next sentence says.
- Why it matters: The mechanism is credited to the wrong term.
- Underlying pattern: P-15
- What to restore/check: Attribute the effect to the access constraint.
- Related issues: —

**Issue I-066** · M818, M1257 · §5.4, §7.5 · Medium · P2 · Information order
- Original passage: "The population~\eqref{eq:justtransition} cannot see is therefore large"
- Problem: That the Just Transition Constraint covers only payroll workers is first revealed here. Its definition at M415–420 gives no such restriction.
- Why it matters: The reader learns of a central limitation only after the definition has been accepted.
- Underlying pattern: Information order
- What to restore/check: State the payroll-only scope at the definition.
- Related issues: I-072

**Issue I-067** · M832 vs S446–456, S470 · §6.1 · Medium · P1 · Cross-document consistency
- Original passage: "the Policy Digital Twin returns \textit{prohibit} for every mode lacking a licensed human under the encoding of Section~\ref{sec:policytwin}"
- Problem: The cited encoding returns *restrict*, and S456 stresses "not prohibited outright". The result (removal) is the same, but the stated mechanism contradicts the appendix.
- Why it matters: The worked example cites an encoding that says the opposite.
- Underlying pattern: P-04
- What to restore/check: Make the worked example use the appendix's status.
- Related issues: I-011, I-068

**Issue I-068** · M834 · §6.1 · Medium · P2 · Reader orientation
- Original passage: "Because $risk_i = 0.70$, the roster guard allows one developing practitioner per lead"
- Problem: No supervision-ratio guard tied to risk is defined or encoded anywhere (S446–451 encodes only licensing).
- Why it matters: A key input to ζ̄ = 0.35 has no source.
- Underlying pattern: P-03
- What to restore/check: Encode or define the supervision-ratio rule.
- Related issues: I-067

**Issue I-069** · M291, M844 caption; S428 · Eq. cad; Table 5 · Medium · P2 · Math–table alignment
- Original passage: "Only $D^{skill}$ depends on the roster; the other four debt components are mode-level."
- Problem: Eq. (cad), S428 and the first audit's I-21 fix index D^trans by roster a.
- Why it matters: The caption contradicts the equation.
- Underlying pattern: P-04
- What to restore/check: Align the caption with the indexing, or explain why D^trans is roster-invariant in this case.
- Related issues: —

**Issue I-070** · M926 · §6.4 · Medium · P3 · Circular reasoning
- Original passage: "Substituting into~\eqref{eq:aug} reproduces the ranking without solving the program"
- Problem: λ_k was obtained from the program's optimum (the tie condition).
- Why it matters: The "without solving" claim is circular.
- Underlying pattern: P-08
- What to restore/check: Describe this as a consistency check.
- Related issues: —

**Issue I-071** · M1036 · §6.7 · Medium · P2 · Non sequitur
- Original passage: "because protected practice is scarce at the optimum the access constraint binds with equality"
- Problem: The constraint binds because the composition-blind share (0.125) is below θ − ε (0.27), not because practice is scarce.
- Why it matters: The stated reason is not the actual reason.
- Underlying pattern: P-08
- What to restore/check: Give the correct reason.
- Related issues: I-021

**Issue I-072** · M1039 caption · Table 8 · Medium · P2 · Caption accuracy
- Original passage: "The contracted row is not a result and not a modeling choice ... ineligible as roster members under~\eqref{eq:accessshare}"
- Problem: Excluding non-payroll workers from 𝒲_k *is* a modeling choice. M1060 calls it a "property of the data substrate". Eligibility is defined by 𝒲_k, not by Eq. (accessshare).
- Why it matters: The caption denies a choice the model makes and cites the wrong equation.
- Underlying pattern: P-04
- What to restore/check: Acknowledge the choice and cite the right definition.
- Related issues: I-003, I-066

**Issue I-073** · M1068 caption · Table 9 · Medium · P2 · Definition error
- Original passage: "``No reversal'' means ... so the capability price does not change the staffing decision"
- Problem: In the "no reversal" rows, 53.9–98.7% of tasks *do* change roster (M1117). What does not change is the *mode*.
- Why it matters: The legend misdefines the table's key category.
- Underlying pattern: P-02
- What to restore/check: Define it as "mode reversal".
- Related issues: I-020

**Issue I-074** · M1117 · §6.9 · Medium · P2 · AI scaffold / Scope
- Original passage: "The sensitivity analysis demonstrates four primary operational consequences across the parameter space: First,"
- Problem: This is a scaffold that replaces the one removed in the first audit's I-23. "Demonstrates ... across the parameter space" overstates a one-at-a-time sweep. The paragraph runs about 300 words.
- Why it matters: The scaffold returns in a new form, and the claim overstates the analysis.
- Underlying pattern: P-08
- What to restore/check: Drop the scaffold, describe the sweep accurately, and split the paragraph.
- Related issues: I-079

**Issue I-075** · M1134, M1146, M1213 · §7.1 · Medium · P2 · Conceptual mapping
- Original passage: "with $\tau_{skill}=4.05$ years taken from Proposition~\ref{prop:intake}"
- Problem: τ_k is a pipeline delay (time to competence). τ_j is an exponential time constant. Equating them is a modeling choice presented as a derivation ("Only τ_skill = 4.05 is derived").
- Why it matters: Readers may take the debt curve's timing as derived when it is assumed.
- Underlying pattern: P-12
- What to restore/check: State that the identification is an assumption.
- Related issues: I-023, I-048

**Issue I-076** · M1228 · §7.2 · Medium · P2 · Claim strength
- Original passage: "computable on a realistic domain ... the distributional question has a determinate answer with~\eqref{eq:access} and none without it"
- Problem: The inputs are illustrative, so "realistic" is unsupported. Without the constraint the paper *does* give a determinate answer (622 hours) under its recruitment assumption.
- Why it matters: The summary of what is established is stronger than §6.
- Underlying pattern: P-07
- What to restore/check: Align with what §6 shows.
- Related issues: I-008

**Issue I-077** · M1237 · §7.3 · Medium · P2 · Stale after fix
- Original passage: "Fourth, the access constraint is a ratio"
- Problem: Eq. (prog-access) is now linearized (M550, M562).
- Why it matters: The text contradicts the program as currently written.
- Underlying pattern: P-04
- What to restore/check: Update to the linearized form.
- Related issues: I-085

**Issue I-078** · M1242 vs Fig. 4 legend, Table 10 · §7.4 · Medium · P2 · Terminology
- Original passage: "with the external baselines of \citet{Ranz2017} and \citet{Merlo2023}"
- Problem: Figure 4 and Table 10 use the names "Capability Matching" and "Ergonomics-Aware Role Allocation". The mapping to Ranz and Merlo appears only in S147. Figure 4 also gives these unimplemented baselines debt parameters.
- Why it matters: Readers cannot match the figure's strategies to the text.
- Underlying pattern: Terminology drift
- What to restore/check: Use one name per strategy and give the mapping in the main text.
- Related issues: I-023

**Issue I-079** · M1251–1259 · §7.5 · Medium · P2 · Scaffold / Structure
- Original passage: "The distributional impacts of the framework partition across four distinct municipal constituencies:" ... "The fourth answer concerns automation itself"
- Problem: The fourth item is not a constituency, and the list switches from "constituencies" to "answer".
- Why it matters: The scaffold promises a structure the section does not follow.
- Underlying pattern: P-08
- What to restore/check: Drop or fix the framing.
- Related issues: I-074

**Issue I-080** · M1253 · §7.5 · Medium · P2 · Epistemic boundary
- Original passage: "The clearest winners are residents ... constraint~\eqref{eq:res3r} makes an AI-service outage a degradation rather than an interruption"
- Problem: A design intent is stated as a realized outcome, although nothing has been deployed or tested.
- Why it matters: It blurs the line between design and evidence.
- Underlying pattern: P-07
- What to restore/check: Make it conditional.
- Related issues: —

**Issue I-081** · M1287 · Conclusion · Medium · P1 · New claims / Overclaim
- Original passage: "Its central proposition is that human expertise, fallback competence, accountability, and democratic control are renewable but depletable civic resources"; "the formal results that say when the system is satisfiable"
- Problem: "Democratic control" is not one of the five CAD components and appears for the first time here. "Proposition" collides with the formal Propositions. Proposition 1 gives only a *necessary* condition, so it does not "say when the system is satisfiable".
- Why it matters: The conclusion introduces a new claim and overstates a formal result.
- Underlying pattern: P-15
- What to restore/check: Remove the new item and state the necessary-condition scope.
- Related issues: —

**Issue I-082** · M108; `cover-letter.md`; `report.md` §E · Front matter · Medium · P1 · Metadata consistency
- Original passage: "\textbf{Word count:} 11,507"
- Problem: `count_words.py` now gives 11,898 on the journal basis, which `report.md` also cites. The cover letter repeats 11,507.
- Why it matters: The declared word count does not match the measured one.
- Underlying pattern: P-11
- What to restore/check: Update both to the measured count.
- Related issues: I-001

**Issue I-083** · M1300–1302, M1316–1319 · Acknowledgment / Funding · Medium · P1 · Back matter
- Original passage: "The research work was funded by Umm Al-Qura University, Saudi Arabia under code number: 26UQU(Staff number)(track name)xx."
- Problem: The placeholder is still in place (known open item). The same sentence appears in both Acknowledgment and Funding. The TeX comment and sentence differ from what `report.md` §F quotes ("[AUTHOR INPUT REQUIRED ...]", "The authors thank the Deanship ...").
- Why it matters: The back matter is unfinished and the report misdescribes it.
- Underlying pattern: P-11
- What to restore/check: Insert the grant code, de-duplicate the two sections, and correct the report.
- Related issues: —

**Issue I-084** · S158, S241 · S2.3 Metrics; P3 · Medium · P1 · Metric definition
- Original passage: "the \textit{Capability-Formation Index}, $\Lambda_k/B_k$ summed over domains"; P3: "at least 0.95, and exceeds that of Capability Matching by at least 40 index points on a 0--100 scale"
- Problem: A sum over domains is not bounded by 1, so the 0.95 threshold is ill-defined. P3 then mixes a 0–1 scale and a 0–100 scale.
- Why it matters: A pre-specified hypothesis has an undefined threshold.
- Underlying pattern: P-15
- What to restore/check: Define the index (mean, not sum) and use one scale.
- Related issues: I-027

**Issue I-085** · S191 · Table S3 · Medium · P2 · Stale after fix
- Original passage: "Access slack penalty & $M$ & $10^{3}$ objective units per unit share"
- Problem: ς is now in qualified-practice hours (M562), so M is per hour.
- Why it matters: The parameter table's unit no longer matches the program.
- Underlying pattern: P-04
- What to restore/check: Update the unit.
- Related issues: I-077

**Issue I-086** · S239 · P1 · Medium · P2 · Hypothesis consistency
- Original passage: "0.79 (single task class, no accumulation)"
- Problem: The worked value is above the 0.5 refutation threshold, but S227 says divergences are "recorded in the hypothesis itself", and P1 records none. Figure 4 gives a different ratio (31.51/100 = 0.315) for the same quantity.
- Why it matters: Two worked values exist for one hypothesis, and one of them would refute it.
- Underlying pattern: P-04
- What to restore/check: Reconcile the two values and record the divergence.
- Related issues: —

**Issue I-087** · S395 · S6.7 · Medium · P2 · Citation attribution (verify)
- Original passage: "finding far more occupations with at least half their tasks exposed to LLM-enabled automation than to robotics alone"
- Problem: Confirm that Eloundou et al. make this comparison with robotics.
- Why it matters: The citation may be credited with a finding it does not report.
- Underlying pattern: Citation scope
- What to restore/check: Check against the source.
- Related issues: —

**Issue I-088** · S451 · S7.4 · Medium · P2 · Terminology
- Original passage: "Panel decision WRP-2026-014 (Workforce Review Panel)"
- Problem: Everywhere else the body is the "Weight Review Panel".
- Why it matters: Two names for one governing body.
- Underlying pattern: Terminology drift
- What to restore/check: Use one name.
- Related issues: —

**Issue I-089** · S475 · S7.7 · Medium · P2 · Generalization
- Original passage: "and the Lagrangian channel is numerically the largest"
- Problem: This holds in the worked case (0.127 vs 0.022) but is stated as a general property.
- Why it matters: A case result is presented as a law.
- Underlying pattern: P-05
- What to restore/check: Scope it to the worked case.
- Related issues: I-019

**Issue I-090** · S583 · S10 · Medium · P2 · Overstatement of a formal result
- Original passage: "Proposition~\ref{prop:violation} bounds the drift between rebalances by one task's worth"
- Problem: Proposition 4 bounds only displacement and resources, not drift in general.
- Why it matters: The formal result is described as broader than it is.
- Underlying pattern: P-15
- What to restore/check: Name the two quantities it bounds.
- Related issues: I-015

**Issues I-091 to I-100: Revision-history leakage in the supplement and late main text.** All: Medium · P1 · AI-rewrite / Revision leakage · Pattern P-01 · Related: I-028, I-029, I-045. For each, the problem is that the sentence narrates the manuscript's revision history to the reader; the check is to state the current fact without that history and move the history to the response document.

| ID | Location | Original passage |
|---|---|---|
| I-091 | S140 | "Earlier presentations of this protocol attributed its fleet-utilization distributions to two survey papers ... This is not a conservative bias, as an earlier version of this article claimed." |
| I-092 | S162 | "Excluding these two from the hypothesis family repairs a defect in earlier versions of this protocol" |
| I-093 | S169 | "Earlier versions of this configuration specified hyperparameters for an optional learned surrogate that was never used" |
| I-094 | S211 | "Earlier versions of this plan specified the Mann--Whitney $U$ test" |
| I-095 | S222 | "the single-arm design used in earlier versions of this protocol was arithmetically impossible ... as an earlier version of this protocol did" |
| I-096 | S227 | "P8 and P10 have been restated so that they are falsifiable ... And P1's refutation criterion no longer uses overlapping confidence intervals" |
| I-097 | S461 | "Earlier presentations of this framework paired the Just Transition Constraint ... That was a category error." |
| I-098 | S528 | "Two collisions present in earlier presentations have been removed ... The single-assignee function of earlier presentations" |
| I-099 | S360 | "which is exactly what Section~\ref{sec:hcpb} repairs relative to earlier presentations of this framework" |
| I-100 | M1219 | "would repeat the category error Section~\ref{sec:access} corrects for reskilling coverage" |

**Issue I-101** · M1264 · §7.6 Threats · Medium · P2 · Reader orientation / Format
- Original passage: "comes from the agent whose interest is a larger budget"; "One city scale"
- Problem: The agent is named only in S480. "One city scale" is unclear. The line ends with a stray tab, and no blank line precedes `\subsection`.
- Why it matters: The threat cannot be understood from the main text alone.
- Underlying pattern: P-03
- What to restore/check: Name the agent, clarify the phrase, fix the formatting.
- Related issues: I-049

**Issue I-102** · Fig. 2 (runtime.png) vs M472 · Figure 2 · Medium · P2 · Figure–caption alignment
- Original passage: Caption: "The dashed edge returns outcomes to the Policy Digital Twin"
- Problem: In the image the dashed feedback edge leaves the "No (m,a) left?" diamond, before any execution, not the "Update State" box. The box label "Price Each (m,a)" keeps the "price" polysemy. A "decision" icon has no edge attached.
- Why it matters: The figure shows feedback occurring before execution.
- Underlying pattern: P-02; P-04
- What to restore/check: Move the feedback edge to originate after execution and fix the labels.
- Related issues: —

**Issue I-103** · Fig. 1 (arch.png) vs M397, M447 · Figure 1 · Medium · P3 · Figure–text alignment
- Original passage: Image label "Layer 4: Budget, Access & Transition Constraints"; text has "Layer 4" and "Layer 4b"
- Problem: The figure merges Layers 4 and 4b. The caption names η_k flowing from the Policy Twin, but no labeled edge shows it.
- Why it matters: Minor mismatch between figure and text.
- Underlying pattern: P-04
- What to restore/check: Align the layer numbering and the labeled edges.
- Related issues: —

---

## 6. Low-Priority Issues

All Low issues are P3 unless marked otherwise. Format: ID · location · category: *quoted text*. Problem, then what to check.

**Front matter, introduction and related work**
- **I-104** · M118 · Terminology: *"four constraints bind the objective"*. "Bind" has a technical meaning (active at the optimum) that the paper uses later (§6.3). Use a neutral verb here.
- **I-105** · M145 · Unsupported claim: *"with which they are routinely conflated"*. "Routinely" needs a citation or hedging.
- **I-106** · M171 · Verb strength: *"\citet{Shneiderman2020} demonstrates"*. The source is a conceptual argument, so "argues" fits better.
- **I-107** · M173 · Paragraph purpose: the Rashidi sentence is a dangling final sentence with no link to the paragraph.
- **I-108** · M189, S399 · AI phrasing: *"prices exposure ex ante at runtime rather than compensating ex post"*. Jargon stacking introduced by the first audit's I-16 fix. "Ex ante at runtime" is semantically muddled, and the comparison sets up a straw man (Sen, Nussbaum and Ostrom never aimed to be decision procedures).

**Framework and architecture (§3–§4)**
- **I-109** · M284 · Repetition: the five liabilities are listed twice in consecutive sentences. Clearly redundant.
- **I-110** · M296 and throughout · Reference style: Eq. (scv) is cited before it is defined (forward reference). Equation references use three forms: "Equation~" (22), "equation~" (44), and bare "of~\eqref". Choose one.
- **I-111** · M320 · Paragraph purpose: the ISO 23247 sentence reads as a reviewer-response insertion in Layer 1. Its link to ℓ_i is unclear.
- **I-112** · M337 · Metaphor: *"decays on the same clock as the pipeline"*. Compressed. State the mechanism (competent practitioners leave without replacement).
- **I-113** · M373 · Idiom: *"because a budget whose units do not close cannot be audited"*.
- **I-114** · M395 vs M189 · Terminology: "renewable common-pool resource" here, "depletable shared resources" at M189. *"revised by the resource's own users"*: it is unclear who the users of developmental practice are.
- **I-115** · M420 · Referent: *"which stops the framework concentrating displacement"*. "Which" could mean the ILO guidelines or the ceiling.
- **I-116** · M447 · Caption: *"the ten agents are drawn inside the market because they constitute it"*. Explains the drawing rather than the system.
- **I-117** · M462 · Claim strength: *"a policy-level error cannot defeat a hardware-level safety interlock"*. Absolute claim.
- **I-118** · M495 · Ambiguous count: *"six depend on the roster"*. Six of the flow terms; seven of the nine terms overall.
- **I-119** · M497 · Compression: *"since against a rolling window a decaying pipeline would keep scoring mid-range"*. Unpack the causal step.
- **I-120** · M499, M504, M507 · Voice and wording: heading *"What They Actually Carry"* is colloquial; *"as a block and as no component"* is awkward; the caption claims *"largest single block"* when it is the only block named.
- **I-121** · M567 vs M579 · Redundancy: the dual-to-constraint mapping is stated twice within 12 lines. The second copy was added by the first audit's I-33 fix and is clearly redundant.
- **I-122** · M610–616 · Punctuation: Eq. (feedback) ends with a comma followed by "Algorithm ...".
- **I-123** · M624 · Reader orientation: the safety floor S^min_i = risk_i·crit_i is first defined inside the algorithm.
- **I-124** · M677 · Anthropomorphism / rhetoric: *"binds harder than it appears"*, *"the hazardous tasks the budget most wants"*, *"a hiring lever, which the next proposition supplies"*. Proposition 2 gives a requirement, not a lever.
- **I-125** · M711 · Category error: *"A domain with $w_9 \ll w_9^\star$ is the division of labor the framework intends"*. Also, w_9^⋆ is defined per task, not per domain.
- **I-126** · M725 · Unclear sentence: *"One task of overshoot is an operational bound"*.
- **I-127** · M768 · Placement: the pointer to the notation table sits at the end of the AOZ subsection.

**Governance (§5)**
- **I-128** · M776 · Idiom: *"fails visibly when those authorities have not spoken"*.
- **I-129** · M794, M810 · Unsupported superlatives: *"which is the most developed"*, *"because its regime is the best studied"*.
- **I-130** · M805, M823, M1259 · Aphoristic closers: *"A composition-blind budget ... cannot be challenged at all"*, *"which is the most a design can offer"*, *"and should be judged as such"*.
- **I-131** · M814 · Model mismatch: *"mirroring the elastic slack ... enforced through administrative sanctions"*. In the program the slack is penalized through M in the objective, not by sanctions.
- **I-132** · M823 · Reader orientation: *"retained for a decade"* is never justified. The n^min rule is cited but never defined in the main text.

**Worked allocation (§6)**
- **I-133** · M864 · Table label: *"Stock-change terms, settled later"* also heads φ_m and ψ_a, which are parameters. *"settled later"* is the colloquial phrase the first audit's I-31 targeted.
- **I-134** · M897 · Precision: *"Proposition~\ref{prop:feasibility} holds with little room"*. It is the condition (Eq. feas) that holds; a proposition always holds. The margin is about 18%.
- **I-135** · M905 · Completeness: the caption claims the enumeration is complete but omits the feasible single-mode option H+R/a_1 alone (mean SCV 0.3082).
- **I-136** · M966 · Precision: *"both above the floor"*. Only safety has a floor; quality does not.
- **I-137** · M1029 · Referent / overreach: *"explains why no employer corrects this unprompted"*. "This" is ambiguous. *"without appearing in any training budget"* overgeneralizes.
- **I-138** · M1034 · Rhetoric: *"not merely preserved but re-founded, one replacement cycle at a time"*.
- **I-139** · M1060 · Verb: *"as documented in the contracted-labor row"*. The row is hypothetical.
- **I-140** · M1124 vs M1087, M1093 · Number consistency (P1): text says 9.56%, the table says 9.57%. Recomputed: 9.566%. Same in S583.
- **I-141** · M1117 · Number consistency: *"roughly 15\% headroom"*. 85% of the critical value means about 18% headroom upward. Also at M1291.
- **I-142** · M1122, S581 · Prediction stated as fact: *"a city will meet both"*, *"a municipal deployment will encounter both"*.
- **I-143** · M1126, S587 · Clarity: the stream supports 14 trainee posts, which coincides with n̂_k = 14 at baseline. Note the coincidence (every task carries one trainee) so readers do not conflate the two numbers.

**Discussion and conclusion (§7–§8)**
- **I-144** · M1213 · Caption accuracy: *"almost all of it unformed skill"*. In Human-First all of the residual slope is skill.
- **I-145** · M1255 · Overclaim: *"the losers are precisely the under-represented groups"*.
- **I-146** · M1285 · Generic AI opening: *"The AI era requires a richer question"*. *"Governed portfolio"* is a new term, never used before the conclusion.
- **I-147** · M1293 · Overclaim: *"which a city could adopt tomorrow without the optimizer"*.
- **I-148** · M1298 · Abbreviations: AOZ, PDT and WRP each appear only in the abbreviation list and never in the text.
- **I-149** · M368, M1230 · Typography: two em-dash pairs remain, although `report.md` I-34 says dashes were standardized.

**Supplement**
- **I-150** · S47 vs S69 · Internal contradiction: S47 says *"the value given here governs"*; S69 says the body *"reproduces them exactly"*. The body does not give the rights-affecting or worker windows numerically.
- **I-151** · S77, S84 · Conceptual conflation: "rights-affecting" is triggered by auth_i ≥ 0.7, which is a legal-authority requirement, not a rights impact. The worked bridge task (auth = 0.90) would count as rights-affecting.
- **I-152** · S158 vs S269 · Metric definition: recovery is defined as restoring "κ_s of capacity" in one place and "κ_s D^peak_s" in the other.
- **I-153** · S209 · Terminology: *"negotiation timing"*. The market is a single-round sealed call with no negotiation.
- **I-154** · S351 · Attribution: *"establishing that allocation should depend on task--agent fit"*. A normative claim credited to the source.
- **I-155** · S358 · Unsupported figure: *"for fifty years"*.
- **I-156** · S371 · Colloquialism: *"settled later, by someone else"* survives in the supplement (main-text instance removed by the first audit's I-31).
- **I-157** · S383 · Citation (verify): *"five system features and six development practices"* (Alfrink et al.).
- **I-158** · S414 · Inaccurate scope: *"Nothing here is required to follow the optimization program"*. The main text relies on this appendix for the D-terms, the gating predicate and (supposedly) the smoothing.
- **I-159** · S482 · Metaphor inflation: *"auctioneer"*, *"awards"*, *"sealed-bid"* for what M454 calls an elicitation mechanism, not a strategic game.
- **I-160** · S510 · Equation annotation: the D^skill anchor says *"against the task's own full developmental content ℓ_i"*, but ℓ_i does not appear in 1 − φψ.
- **I-161** · S530–561 · Notation table incomplete: missing ς, M, P_mode, 𝒢_roster, Θ_k, φ̄_k, ω̄_k, δ^disp_g, Δ^res, D^tot, n^rem, H_g^base, U^used, ζ_w, E_k, φ^{Z3}, n_m, ϖ_g, and the debt-model symbols c_j, π_j, τ_j, C(t).
- **I-162** · S587 · Generalization from one case: *"a workforce plan that treats it as a hiring problem will spend a recruitment budget and still lose the capability"*.

**Build hygiene**
- **I-163** · CivicWorkOS.log · natbib "Citation ... multiply defined" warnings for every key, because `xr` imports the supplement's `\bibcite` entries. This is cosmetic, but check that Frontiers' build does not flag it.
- **I-164** · M195, M824, M1264 · Missing blank line before `\subsection`/`\section`, which may merge with the previous paragraph in some builds.

---

## 7. Recurring Manuscript-Wide Patterns

| ID | Pattern | Freq. | Sections | Typical examples | Likely source | Why it matters | Repair strategy |
|---|---|---|---|---|---|---|---|
| P-01 | Revision-history leakage ("earlier versions/presentations", "repair", "category error", "To resolve circularity") | 15 | §3, §6.4, §7, S2, S6, S7, S8 | I-028, I-029, I-044, I-045, I-091–I-100 | AI rewrite (response-to-reviewer text merged into the article) | Breaks the reader's frame and exposes a history of errors to editors without benefit to readers | Search for "earlier", "repair", "category error", "version"; keep the current fact and move the history to the response document |
| P-02 | "Price" polysemy (w_9, λ_k, dual "prices", agents "price", "price of the constraint system", "worth") | 22+ | All | I-018, I-019, I-073, I-102; M454, M467, M472, M567, M696, M699, M887, M935, M940, M1068, M1228, M1259 | Mixed (incomplete fix of the first audit's I-20) | Confuses the paper's central distinction between price and constraint | Make a terminology map and apply it globally, including headings and figure labels |
| P-03 | Notation used before definition, ambiguous referents, symbol collisions | 14 | §1, §3–§7, S8 | I-031, I-033, I-048, I-050, I-068, I-101, I-115, I-123, I-132 | Mixed | Readers must reconstruct meaning from context | One symbol per concept; define at first use; complete the notation table |
| P-04 | A fix applied in one place but not propagated (stale counts, units, labels, cross-references) | 20 | Throughout | I-001, I-005, I-009, I-013, I-024, I-026, I-030, I-053, I-054, I-067, I-069, I-072, I-077, I-085, I-086, I-102, I-103 | Revision process | Internal contradictions undermine trust in the formal content | For each fixed item, search every dependent location in both files |
| P-05 | Generalizing from one worked case to cities or automation in general; dilution credited to automation alone | 7 | Contributions, §4.7, §6.6, Conclusion, S7.7, S10 | I-025, I-089, I-162 | Reasoning compression | The headline finding is over-attributed | Carry the two-cause, single-domain scope everywhere the finding is restated |
| P-06 | Legal and compliance overclaim | 7 | §5.1, §5.3 | I-004, I-052, I-058, I-062, I-063, I-064 | AI rewrite (assertive compliance register) | Legal reviewers will challenge | Use conditional and design-intent language; verify grounds |
| P-07 | Assumption or prediction stated as fact | 14 | §1, §2.6, §3, §5, §6, §7 | I-021, I-032, I-034, I-036, I-042, I-046, I-061, I-076, I-080 | Mixed | Blurs evidence vs. inference | Mark each as assumption, prediction or design intent |
| P-08 | Enumerative scaffolding, compressed causal chains, overloaded paragraphs | 9 | §2.2, §5.2, §6.4, §6.7, §6.9, §7.1, §7.5 | I-039, I-060, I-070, I-071, I-074, I-079 | AI rewrite (scaffolds re-introduced after the first audit's I-23) | Structure is announced rather than delivered | State findings directly; split paragraphs |
| P-09 | Aphoristic or rhetorical closers | 8 | §2.6, §5, §6.5, §6.7, §7.5 | I-042, I-130, I-138; M966 ("finance committee will contest") | Authorial voice amplified by rewriting | Rhetoric stands in for evidence at paragraph ends | Keep the claim, drop the flourish |
| P-10 | Defensive "not simulated / nothing measured" repetition | 7 | M827, M1025, M1122, M1213; S114, S286, S579 | (classified as useful reinforcement in captions; redundant in M1122 and S579) | Partial fix of the first audit's I-27 | Mild repetition | State once per section and once per figure |
| P-11 | Metadata and back-matter inconsistency | 3 | Front matter, back matter, cover letter | I-082, I-083, I-148 | Process | Visible to editors at desk review | Recount and de-duplicate |
| P-12 | Inputs or tautologies presented as results | 6 | Abstract, §6.5, §7.1, §7.2, Conclusion | I-006, I-016, I-022, I-023, I-075 | Reasoning | Overstates the evidence | Present them as consequences of chosen inputs |
| P-13 | Metaphor inflation for mechanisms ("twin", "filter", "market", "auctioneer", "buys") | 5 | §3 Layer 3, §6.5 heading, S7.8 | I-044, I-159; M937 "What It Buys", M1289 "what this buys" | AI rewrite | Mechanisms sound like something they are not | Name mechanisms literally |
| P-14 | Dense citation chains with one claim per citation | 3 | §2.4, §2.5 | I-040, I-041 | Compression of the supplementary survey | Synthesis is lost | Synthesize: what prior work assumes and lacks |
| P-15 | Formal results described more strongly than proven (necessary vs sufficient, "bounds", "exactly", "governed") | 14 | §3–§8, S8, S10 | I-010–I-015, I-020, I-022, I-043, I-047, I-051, I-055, I-057, I-059, I-081, I-090 | Mixed | The core credibility risk for a theory paper | Restate each formal claim as narrowly as what is proven |
| P-16 | Mixed equation-reference style | ~70 occurrences | Throughout | I-110 | Mechanical | Minor polish | Choose one form |

---

## 8. AI-Rewrite Signature Analysis

| Signature | Level | Evidence |
|---|---|---|
| Generic academic phrasing | Mild | M1285 "The AI era requires a richer question"; M134 "the consequences extend well beyond headcount reduction" |
| Abstraction inflation | Mild | M968 "Constraint satisfaction converts net cohort loss into net workforce replenishment" |
| Nominalization | Mild | M284, M968; most of the text is verb-driven |
| Excessive hedging | Absent | The text tends the other way |
| Excessive certainty | Moderate | I-004, I-012, I-025, I-058, I-063, I-117, I-147 |
| Formulaic transitions | Mild | "Furthermore," (M136); "Consequently," (M136) |
| Repetitive sentence structures | Moderate | "X, not Y" and "is not X but Y" constructions (M132, M887, M1223, M1230, S253) |
| Artificial paragraph scaffolding | Moderate | M1117, M1217, M1251, M1291 (I-074, I-079) |
| Over-compression | Moderate | M173, M187, M497, M605, M1117 |
| Loss of causal explanation | Moderate | I-039, I-071, I-018 (cause and effect inverted in the conclusion) |
| Loss of authorial voice | Mild | The voice survives; the fix-inserted sentences (M320, M352, M800, M778) read in a different, blander register |
| Terminology drift | Strong | I-018, I-048, I-056, I-078, I-088, P-02 |
| Claim inflation | Moderate | I-004, I-016, I-022, I-076 |
| Scope inflation | Moderate | I-007, I-025, I-089 |
| Qualification removal | Moderate | M136 keeps "and shared supervision"; M147, M985 and M1289 drop it (I-025) |
| Excessive symmetry / parallelism | Mild | M1253–1259 "winners ... second group ... third group ... fourth answer" |
| Redundant summaries | Mild | I-109, I-121; M1124 repeated verbatim in S583 (acceptable for an appendix) |
| Unnatural sophistication | Mild | I-108 "ex ante at runtime"; M800 "ensuring lawful affirmative encouragement" |
| Generic "significance" statements | Mild | M816 "which strengthens the case for deploying it" |
| Loss of concrete actors | Mild | Mostly repaired by the first audit's I-30; M1029 "no employer corrects this" |
| Excessive passive voice | Absent | — |
| Unnecessary meta-language | Strong | Revision-history meta-commentary (P-01, 15 sites) |

---

## 9. Authorial Voice Loss

The original voice is unusually direct and self-critical: "The cost is that our constraint offers no envy guarantee" (M178), "Human-First beats CivicWorkOS on this metric for thirteen years" (M1221), "This is the limitation we would fix first" (M1277). This should be **preserved**.

The voice is weakened in three ways:
1. **Fix-pass sentences in a different register.** M320 (ISO), M352 ("To resolve procedural circularity"), M778 ("To guarantee balanced institutional representation"), M800 ("ensuring lawful affirmative encouragement") and M189/S399 ("ex ante at runtime") are blander and more assertive than the surrounding prose. They read like inserted repairs rather than the author's reasoning.
2. **Skepticism turned against earlier drafts instead of claims.** The paper's skepticism now partly targets its own past versions (P-01) instead of the present claims. Meanwhile some present claims went uncaught (I-004, I-012, I-016, I-022).
3. **Aphorism in place of argument.** Paragraph-final maxims (P-09) are the author's style pushed too far. One per section reads as voice; the current frequency reads as rhetoric.

---

## 10. Scientific Reasoning Loss

Comparisons below use the visible prior version (`submission/CivicWorkOS.tex`, the first audit's quotations) where available. No original was invented.

1. **Causal attribution of dilution.** The earlier introduction framed it as "machine assistance and shared supervision stretch formation" (submission L147). The current introduction (M136) keeps that framing, but the contributions, §6.6 and the conclusion attribute dilution to automation alone (I-025). Combined with the certification ambiguity (I-002), readers may believe automation alone multiplies formation time by 3.38.
2. **Price vs. constraint.** §4.6 and M887 carefully separate the debt weight from the binding constraint. The conclusion (M1289) reverses the direction of cause (I-018).
3. **Theory–experiment boundary.** M1223 tries to say that Figure 4 "is not evidence", but then grounds the ordering in "mechanisms", which brings back the impression of evidence (I-023).
4. **Structural vs. empirical.** The first audit's I-02 fix labels magnitude thresholds as structural (I-022), which inverts the paper's own distinction ("the substantive question lies in the empirical magnitudes").
5. **Formal guarantees.** The integrality-gap sentence (I-012) and the Proposition 4 proof mismatch (I-015) suggest guarantees that §7.3 says the paper does not have.
6. **Legal reasoning.** The first version of the Marschall analysis (per the first audit's I-14) asserted too much. The fix asserts compliance *more* directly while citing a safety floor as merit assessment (I-004).
7. **Negative-result preservation.** Preserved and should stay: M1221 (Human-First wins for 13 years), M1117 (reversal not robust), M1219 (vendor debt unbounded), M1257 (non-payroll workers unseen), M1244 (external baselines unimplemented). The risk is that I-016 and I-024 make the positive results look stronger than these caveats allow.

---

## 11. Section-by-Section Diagnosis

**Title, Abstract, Keywords (M101–122)**
- Main writing problem: ambiguous "the constraint" (I-031); loose "bind" (I-104).
- Structural problem: none. Problem → gap → approach → results → impact is all present.
- AI-rewrite problem: none significant.
- Scientific-communication risk: the novelty overclaim "neither prices" (I-007); 3.46 vs 2.88 presented as a result (I-016); the 3.38 figure depends on I-002.
- Repair areas: I-007, I-016, I-002.

**§1 Introduction and Contributions (M125–154)**
- Main writing problem: universal claims (I-032, I-034); the "second half" referent (I-033).
- Structural problem: one-sentence paragraph at M132.
- AI-rewrite problem: mild generic phrasing.
- Risk: contributions overstate (I-025, I-030, I-035, I-036).
- Repair areas: contribution verbs and scope.

**§2 Related Work and Gap (M156–236)**
- Main writing problem: citation chains (I-040, I-041).
- Structural problem: gaps not mapped to RQs (I-008).
- AI-rewrite problem: I-108.
- Risk: Gap 3 vs Table 1 (I-007); D^skill calibration claim (I-038).
- Repair areas: novelty scope; gap→RQ map.

**§3 Framework (M238–454)**
- Main writing problem: CAD definition contradiction (I-009); d_i normalization (I-043).
- Structural problem: payroll-only scope revealed late (I-066).
- AI-rewrite problem: I-044, I-045.
- Risk: I-010, I-011, I-047.
- Repair areas: definitions and math–prose alignment.

**§4 Program, online rule, Propositions, AOZ (M456–768)**
- Main writing problem: density at M605.
- Structural problem: algorithm vs equation (I-053, I-054).
- AI-rewrite problem: duplicate dual mapping (I-121).
- Risk: I-012, I-013, I-014, I-015, I-055, I-057.
- Repair areas: restate every formal claim as narrowly as proven.

**§5 Governance and Law (M770–823)**
- Main writing problem: overloaded contestability paragraph (I-060).
- Structural problem: none.
- AI-rewrite problem: compliance register (I-004, I-058).
- Risk: legal accuracy (I-004, I-062, I-063, I-064).
- Repair areas: legal claims.

**§6 Worked Allocation (M824–1126)**
- Main writing problem: price polysemy (I-018).
- Structural problem: hidden homogeneity (I-017).
- AI-rewrite problem: scaffold at M1117 (I-074).
- Risk: I-002, I-003, I-006, I-020, I-021.
- Repair areas: assumptions and the n^min conflict.

**§7 Discussion (M1128–1278)**
- Main writing problem: scaffolds (I-079).
- Structural problem: RQs not answered (I-008).
- AI-rewrite problem: revision leakage (I-029, I-100).
- Risk: I-022, I-023, I-077.
- Repair areas: epistemic boundary in §7.1–7.2.

**§8 Conclusion and back matter (M1282–1330)**
- Main writing problem: generic opening (I-146).
- Structural problem: new claims (I-081).
- AI-rewrite problem: none significant.
- Risk: I-018, I-024, I-025, I-016; the placeholder (I-083).
- Repair areas: align the conclusion with §6–§7.

**Supplement S1–S2 (Contestability, Protocol)**
- Main writing problem: revision leakage (I-091 to I-096).
- Structural problem: none.
- AI-rewrite problem: meta-commentary.
- Risk: I-005, I-026, I-027, I-084, I-086.
- Repair areas: hypotheses table.

**Supplement S3–S6 (Stress, Calibration, Elicitation, Related Work)**
- Main writing problem: I-151, I-155.
- Risk: I-019, I-087.
- Repair areas: "worth" wording; verify citations.

**Supplement S7–S10 (Framework detail, Proofs, DPIA, Shocks)**
- Main writing problem: the notation table (I-161).
- Structural problem: the smoothing reference leads nowhere (I-013).
- Risk: I-003 (the S572 contradiction), I-011, I-014, I-015, I-048, I-067.
- Repair areas: proofs and encodings.

---

## 12. Highest-Leverage Repair Plan

Diagnosis only; no rewriting here.

1. **Fix the submission package (I-001)** after all other repairs, and re-run `check_repo.py`, `audit_numbers.py` and `count_words.py`.
2. **Restore technical meaning in the headline result:** settle the certification-hours reading and split the 3.38 factor into its two causes (I-002, I-014, I-025).
3. **Resolve internal contradictions about model behavior:** the λ_k response to shocks (I-005); the price-vs-constraint cause (I-018, I-019); CAD as flow or stock (I-009); the policy join vs authority (I-011); prohibit vs restrict (I-067).
4. **Restate formal results exactly as proven:** I-010, I-012, I-013, I-015, I-047, I-051, I-055, I-057, I-081, I-090.
5. **Reconcile the worked distributional example** with n^min and the disclosure rule, and make the recruitment assumption explicit (I-003, I-021, I-071, I-072).
6. **Restore claim strength and scope:** I-004, I-006, I-007, I-016, I-020, I-022, I-023, I-024, I-026, I-027, I-063, I-064.
7. **Remove revision-history leakage** across both files (P-01).
8. **Unify terminology and notation:** P-02 and P-03; I-048, I-056, I-078, I-088; the notation table.
9. **Repair structure:** gap→RQ→answer map (I-008); split overloaded paragraphs (I-060, I-074); remove scaffolds (P-08).
10. **Metadata and polish:** I-082, I-083, the Low issues.

---

## 13. Global Editing Rules for This Manuscript

1. Reserve "price" for one object (or none). Use separate fixed terms for w_9, λ_k, other duals, and agent estimates.
2. Give each concept one symbol. τ, κ, ρ, δ, π, ε and Λ arguments must not carry more than one meaning.
3. Say "necessary condition", "ranges over the swept values", "under assumption X". Never "says when", "bounds" or "exactly" unless proven.
4. Whenever 3.38, 4.05 or "four vs fourteen" appears, name both causes (machine assistance and shared supervision) and the single domain.
5. Whenever 4.34% appears, add 0.33–9.60%.
6. Do not present η-driven or parameter-driven quantities (3.46 vs 2.88, the Figure 4 ordering, the 13.23 crossover) as findings.
7. Legal text describes design intent and open questions; it never asserts compliance.
8. The manuscript describes the current work only. Revision history belongs in the response letter.
9. After any fix, search both .tex files for every dependent count, unit, label and cross-reference.
10. Define each symbol and rule (δ^disp, n^min, the supervision-ratio guard, the retention period) before or at first use in the main text.
11. End paragraphs on the claim, not on a maxim.

---

## 14. Master Issue Index

| ID | Lines | Section | Category | Sev. | Pri. | Pattern |
|---|---|---|---|---|---|---|
| I-001 | submission/* | Package | Cross-document | Critical | P1 | P-04 |
| I-002 | M390, M973–985, M1025; S331 | §3, §6.6 | Technical meaning | Critical | P1 | P-05, P-15 |
| I-003 | M1034–1055; S188, S421, S572 | §6.7, S7.1, S9 | Evidence / consistency | Critical | P1 | P-04, P-07 |
| I-004 | M800, M805 | §5.3 | Legal claim strength | Critical | P1 | P-06 |
| I-005 | S222, S245, S281 vs M1124 | S2, S3, §6.10 | Consistency | Critical | P1 | P-04 |
| I-006 | M966; S247, S253 | §6.5, S2 | Evidence–claim | Critical | P1 | P-07, P-12 |
| I-007 | M118, M224 | Abstract, §2.6 | Novelty | High | P1 | P-07 |
| I-008 | M226–236 | §2.6, §7 | Structure | High | P1 | — |
| I-009 | M284 | §3.1 | Terminology | High | P1 | P-04 |
| I-010 | M435 | Layer 5 | Math–prose | High | P1 | P-15 |
| I-011 | M368; S468 | Layer 3, S7.6 | Math–prose | High | P1 | P-15 |
| I-012 | M585; S523 | §4.6, S8.3 | Technical precision | High | P1 | P-15 |
| I-013 | M605 | §4.6 | Cross-reference | High | P1 | P-04, P-15 |
| I-014 | M681; S496 | Prop. 2 | Math precision | High | P1 | P-15 |
| I-015 | M715–725; S502 | Prop. 4 | Math–prose | High | P1 | P-15 |
| I-016 | M118, M968, M1289 | Abstract, §6.5, §8 | Tautology as finding | High | P1 | P-12 |
| I-017 | M836, M902 | §6.1, §6.4 | Hidden assumption | High | P1 | — |
| I-018 | M887, M935, M1289 | §6, §8 | Terminology / causality | High | P1 | P-02 |
| I-019 | S360, S475 | S6.2, S7.7 | Consistency | High | P1 | P-02 |
| I-020 | M1117 | §6.9 | Robustness claim | High | P1 | P-15 |
| I-021 | M1036 | §6.7 | Hidden assumption | High | P1 | P-07 |
| I-022 | M1230; S227 | §7.2, S2.7 | Claim strength | High | P1 | P-12, P-15 |
| I-023 | M1146, M1221–1223 | §7.1 | Evidence boundary | High | P1 | P-12 |
| I-024 | M1289, M940 | §8, §6.5 | Consistency | High | P1 | P-04 |
| I-025 | M147, M694, M985, M1289 | Contrib., §6.6, §8 | Scope creep | High | P1 | P-05 |
| I-026 | S129, S286 | S2, S4 | Consistency | High | P1 | P-04 |
| I-027 | S149 | S2.2 | Design fairness | High | P1 | P-07 |
| I-028 | M926 | §6.4 | Revision leakage | High | P1 | P-01 |
| I-029 | M1244 | §7.4 | Revision leakage | High | P1 | P-01 |
| I-030 | M151, M1246 | Contrib., §7.4 | Consistency | Medium | P1 | P-04 |
| I-031 | M118 | Abstract | Referent | Medium | P2 | P-03 |
| I-032 | M130 | §1 | Claim strength | Medium | P2 | P-07 |
| I-033 | M132–134 | §1 | Referent | Medium | P2 | P-03 |
| I-034 | M134 | §1 | Evidence | Medium | P2 | P-07 |
| I-035 | M144 | §1.1 | Word choice | Medium | P2 | — |
| I-036 | M148 | §1.1 | Claim strength | Medium | P2 | P-07 |
| I-037 | M166 | §2.1 | Reasoning | Medium | P2 | — |
| I-038 | M171 | §2.2 | Citation / math | Medium | P1 | P-07 |
| I-039 | M173 | §2.2 | Compression | Medium | P2 | P-08 |
| I-040 | M187 | §2.4 | Citation scope | Medium | P2 | P-14 |
| I-041 | M194 | §2.5 | Paragraph purpose | Medium | P2 | P-14 |
| I-042 | M224 | §2.6 | Evidence / voice | Medium | P2 | P-07, P-09 |
| I-043 | M315 | Layer 1 | Units | Medium | P1 | P-15 |
| I-044 | M352–362 | Layer 3 | AI paraphrase | Medium | P2 | P-01, P-13 |
| I-045 | M385 | Layer 4 | Revision leakage | Medium | P2 | P-01 |
| I-046 | M400 | Layer 4b | Assumption as fact | Medium | P2 | P-07 |
| I-047 | M442, M554 | Layer 5, Program | Math–prose | Medium | P1 | P-15 |
| I-048 | many; S528 | Notation | Collision | Medium | P1 | P-03 |
| I-049 | M454; S480 | Layer 6 | Consistency | Medium | P2 | P-04 |
| I-050 | M574, M715 | §4.6, §4.8 | Undefined symbol | Medium | P1 | P-03 |
| I-051 | M581 | §4.6 | Math precision | Medium | P2 | P-15 |
| I-052 | M562 | §4.5 | Claim strength | Medium | P2 | P-06 |
| I-053 | M630 | Alg. 1 | Algorithm–equation | Medium | P2 | P-04 |
| I-054 | M651 | §4.6 | Stale count | Medium | P2 | P-04 |
| I-055 | M662 | Prop. 1 | Circular definition | Medium | P2 | P-15 |
| I-056 | M147, M686, M985 | Prop. 2 | Terminology | Medium | P2 | — |
| I-057 | M699–708 | Prop. 3 | Math–prose | Medium | P2 | P-15 |
| I-058 | M778 | §5.1 | Claim strength | Medium | P2 | P-06 |
| I-059 | M497, M780, M1271 | §4.3, §5.1 | Precision | Medium | P2 | P-15 |
| I-060 | M787 | §5.2 | Density | Medium | P2 | P-08 |
| I-061 | M789 | §5.2 | Unsupported claim | Medium | P2 | P-07 |
| I-062 | M794–796 | §5.3 | Legal precision | Medium | P2 | P-06 |
| I-063 | M801 | §5.3 | Claim strength | Medium | P1 | P-06 |
| I-064 | M802 | §5.3 | Legal precision | Medium | P1 | P-06 |
| I-065 | M816 | §5.4 | Misattribution | Medium | P2 | P-15 |
| I-066 | M818, M1257 | §5.4, §7.5 | Information order | Medium | P2 | — |
| I-067 | M832 | §6.1 | Consistency | Medium | P1 | P-04 |
| I-068 | M834 | §6.1 | Orientation | Medium | P2 | P-03 |
| I-069 | M844 | Table 5 | Math–table | Medium | P2 | P-04 |
| I-070 | M926 | §6.4 | Circularity | Medium | P3 | P-08 |
| I-071 | M1036 | §6.7 | Non sequitur | Medium | P2 | P-08 |
| I-072 | M1039 | Table 8 | Caption accuracy | Medium | P2 | P-04 |
| I-073 | M1068 | Table 9 | Definition | Medium | P2 | P-02 |
| I-074 | M1117 | §6.9 | Scaffold / scope | Medium | P2 | P-08 |
| I-075 | M1134, M1146 | §7.1 | Conceptual mapping | Medium | P2 | P-12 |
| I-076 | M1228 | §7.2 | Claim strength | Medium | P2 | P-07 |
| I-077 | M1237 | §7.3 | Stale | Medium | P2 | P-04 |
| I-078 | M1242 | §7.4 | Terminology | Medium | P2 | — |
| I-079 | M1251–1259 | §7.5 | Scaffold | Medium | P2 | P-08 |
| I-080 | M1253 | §7.5 | Epistemic boundary | Medium | P2 | P-07 |
| I-081 | M1287 | §8 | New claims | Medium | P1 | P-15 |
| I-082 | M108 | Front matter | Metadata | Medium | P1 | P-11 |
| I-083 | M1300–1319 | Back matter | Placeholder | Medium | P1 | P-11 |
| I-084 | S158, S241 | S2.3 | Metric definition | Medium | P1 | P-15 |
| I-085 | S191 | Table S3 | Stale unit | Medium | P2 | P-04 |
| I-086 | S239 | Table S4 | Consistency | Medium | P2 | P-04 |
| I-087 | S395 | S6.7 | Citation (verify) | Medium | P2 | — |
| I-088 | S451 | S7.4 | Terminology | Medium | P2 | — |
| I-089 | S475 | S7.7 | Generalization | Medium | P2 | P-05 |
| I-090 | S583 | S10 | Overstatement | Medium | P2 | P-15 |
| I-091 | S140 | S2.1 | Revision leakage | Medium | P1 | P-01 |
| I-092 | S162 | S2.3 | Revision leakage | Medium | P1 | P-01 |
| I-093 | S169 | S2.4 | Revision leakage | Medium | P1 | P-01 |
| I-094 | S211 | S2.5 | Revision leakage | Medium | P1 | P-01 |
| I-095 | S222 | S2.6 | Revision leakage | Medium | P1 | P-01 |
| I-096 | S227 | S2.7 | Revision leakage | Medium | P1 | P-01 |
| I-097 | S461 | S7.5 | Revision leakage | Medium | P1 | P-01 |
| I-098 | S528 | S8.4 | Revision leakage | Medium | P1 | P-01 |
| I-099 | S360 | S6.2 | Revision leakage | Medium | P1 | P-01 |
| I-100 | M1219 | §7.1 | Revision leakage | Medium | P1 | P-01 |
| I-101 | M1264 | §7.6 | Orientation | Medium | P2 | P-03 |
| I-102 | Fig. 2 | §4.2 | Figure–caption | Medium | P2 | P-02, P-04 |
| I-103 | Fig. 1 | §3 | Figure–text | Medium | P3 | P-04 |
| I-104 | M118 | Abstract | Terminology | Low | P3 | — |
| I-105 | M145 | §1.1 | Unsupported | Low | P3 | P-07 |
| I-106 | M171 | §2.2 | Verb | Low | P3 | — |
| I-107 | M173 | §2.2 | Paragraph purpose | Low | P3 | — |
| I-108 | M189; S399 | §2.4, S6.7 | AI phrasing | Low | P3 | P-13 |
| I-109 | M284 | §3.1 | Repetition | Low | P3 | — |
| I-110 | M296 and throughout | — | Reference style | Low | P3 | P-16 |
| I-111 | M320 | Layer 1 | Paragraph purpose | Low | P3 | P-01 |
| I-112 | M337 | Layer 2 | Metaphor | Low | P3 | P-08 |
| I-113 | M373 | Layer 4 | Idiom | Low | P3 | P-09 |
| I-114 | M395 | Layer 4 | Terminology | Low | P3 | — |
| I-115 | M420 | Layer 4b | Referent | Low | P3 | P-03 |
| I-116 | M447 | Fig. 1 | Caption | Low | P3 | — |
| I-117 | M462 | §4.1 | Claim strength | Low | P3 | P-07 |
| I-118 | M495 | §4.3 | Ambiguous count | Low | P3 | — |
| I-119 | M497 | §4.3 | Compression | Low | P3 | P-08 |
| I-120 | M499–507 | §4.4 | Voice / caption | Low | P3 | — |
| I-121 | M567, M579 | §4.6 | Redundancy | Low | P3 | — |
| I-122 | M610–616 | §4.6 | Punctuation | Low | P3 | — |
| I-123 | M624 | Alg. 1 | Orientation | Low | P3 | P-03 |
| I-124 | M677 | §4.7 | Rhetoric | Low | P3 | P-09 |
| I-125 | M711 | §4.8 | Category error | Low | P3 | — |
| I-126 | M725 | §4.8 | Unclear | Low | P3 | — |
| I-127 | M768 | §4.9 | Placement | Low | P3 | — |
| I-128 | M776 | §5.1 | Idiom | Low | P3 | P-09 |
| I-129 | M794, M810 | §5.3, §5.4 | Unsupported | Low | P3 | P-07 |
| I-130 | M805, M823, M1259 | §5, §7.5 | Aphorism | Low | P3 | P-09 |
| I-131 | M814 | §5.4 | Model mismatch | Low | P3 | — |
| I-132 | M823 | §5.5 | Orientation | Low | P3 | P-03 |
| I-133 | M864 | Table 5 | Label | Low | P3 | — |
| I-134 | M897 | §6.3 | Precision | Low | P3 | P-15 |
| I-135 | M905 | Table 6 | Completeness | Low | P3 | — |
| I-136 | M966 | §6.5 | Precision | Low | P3 | — |
| I-137 | M1029 | §6.6 | Referent | Low | P3 | P-03 |
| I-138 | M1034 | §6.7 | Rhetoric | Low | P3 | P-09 |
| I-139 | M1060 | §6.7 | Verb | Low | P3 | — |
| I-140 | M1124; S583 | §6.10 | Number consistency | Low | P1 | P-04 |
| I-141 | M1117, M1291 | §6.9, §8 | Number | Low | P3 | — |
| I-142 | M1122; S581 | §6.10, S10 | Prediction as fact | Low | P3 | P-07 |
| I-143 | M1126; S587 | §6.10 | Clarity | Low | P3 | — |
| I-144 | M1213 | Fig. 4 | Caption | Low | P3 | — |
| I-145 | M1255 | §7.5 | Overclaim | Low | P3 | P-07 |
| I-146 | M1285 | §8 | Generic opening | Low | P3 | — |
| I-147 | M1293 | §8 | Overclaim | Low | P3 | P-07 |
| I-148 | M1298 | Abbreviations | Metadata | Low | P3 | P-11 |
| I-149 | M368, M1230 | — | Typography | Low | P3 | — |
| I-150 | S47, S69 | S1 | Contradiction | Low | P3 | — |
| I-151 | S77, S84 | S1.2 | Conflation | Low | P3 | — |
| I-152 | S158 | S2.3 | Metric definition | Low | P3 | — |
| I-153 | S209 | S2.5 | Terminology | Low | P3 | P-13 |
| I-154 | S351 | S6.1 | Attribution | Low | P3 | — |
| I-155 | S358 | S6.2 | Unsupported | Low | P3 | — |
| I-156 | S371 | S6.3 | Colloquial | Low | P3 | — |
| I-157 | S383 | S6.5 | Citation (verify) | Low | P3 | — |
| I-158 | S414 | S7 | Scope | Low | P3 | — |
| I-159 | S482 | S7.8 | Metaphor | Low | P3 | P-13 |
| I-160 | S510 | S8.2 | Annotation | Low | P3 | — |
| I-161 | S530–561 | S8.4 | Notation table | Low | P3 | P-03 |
| I-162 | S587 | S10 | Generalization | Low | P3 | P-05 |
| I-163 | log | Build | Hygiene | Low | P3 | — |
| I-164 | M195, M824, M1264 | — | Formatting | Low | P3 | — |

Totals: 6 Critical, 23 High, 74 Medium, 61 Low (164 issues).

---

## 15. Completeness Check

- Every section of both files was inspected: **yes** (M1–1330, S1–592, read sequentially).
- Every line: **yes**. Preamble lines were checked for content only.
- Equations: **yes** (46 + 2 unnumbered in the main text, 1 + inline in the supplement). Worked arithmetic was spot-recomputed, and `audit_numbers.py` passes.
- Captions: **yes**, all 4 figures (both raster images opened) and all 17 numbered tables + 1 unnumbered table.
- References: citation **language** reviewed; `references.bib` entries **not** verified (not requested). Two "verify" flags were raised instead of assertions.
- Recurring patterns searched after the first example: **yes** (grep for "price", "earlier", "repair", "simulat", em dashes, abbreviations, equation-reference style).
- Local vs. global problems: both are covered (Sections 3–6 vs. 7–10).
- Writing vs. scientific problems: distinguished by category.
- Rewriting avoided: **yes**. No passage was rewritten.
- Missing information invented: **no**. Where a source must be checked, the issue says "verify".
- Coverage claim: complete for the two root .tex files. `submission/*.tex`, `removed_sections.tex` and `CivicWorkOS-diff.tex` were not audited line by line (I-001 explains why).

---

## Appendix A: Do the `report.md` Claims Match the Current Manuscript?

Status key: **ALIGNED** = the claim is true of the current text. **PARTIAL** = the fix was made but is incomplete or creates a new inconsistency. **NOT ALIGNED** = the report's description does not match the text.

| Report item | Report claim (short) | Status | Evidence in current text |
|---|---|---|---|
| Header | `check_repo` 3 passed; `audit_numbers` 199 passed; 11,898 words | ALIGNED (re-run today) | But the manuscript front matter and cover letter still say 11,507 (I-082) |
| I-01 | Access constraint linearized; slack in hours; dual term corrected | PARTIAL | M550, M562, M573 correct. Stale: M1237 "is a ratio" (I-077); S191 M "per unit share" (I-085) |
| I-02 | P2, P3, P5, P9 reclassified as structural | PARTIAL | S227 and Table S4 labels done. M151 still says "ten pre-specified hypotheses" (I-030). P2 and P5 are magnitude claims mislabeled structural (I-022) |
| I-03 | Abstract "marginal opportunity cost" | ALIGNED | M118. Remaining issue: "the constraint" referent (I-031) |
| I-04 | P_mode / 𝒢_roster decomposition in the equation and Algorithm 1 | PARTIAL | M352–367, M627–630. Algorithm applies 𝒢_roster only under *restrict* (I-053); "seven policy queries" is stale (I-054) |
| I-05 | Res notation standardized to Res^{(n_s)}_s; allocation → F_k link | PARTIAL | Main uses Res^{(n_s)}; supplement S528 and S553 use Res^{(n)}. Res(x) still undefined (I-047) |
| I-06 | Abstract intake wording | ALIGNED (abstract) / NOT ALIGNED (cover letter) | M118 correct. `cover-letter.md` still says "an intake requirement for when the budget cannot be met" |
| I-07 | Zero-covariance over ℓ_i, φ_m, **ψ_a** | PARTIAL | Text uses ω_{a,w}, not ψ_a. Unit mismatch ℓ_i vs learn̄ (I-014) |
| I-08 | Propositions 3 and 4 framed as diagnostics | ALIGNED | M699, M711. Proof-statement mismatch remains (I-015) |
| I-09 | CAD per-task marginal proxy vs stock trajectories | PARTIAL | M296 correct. M284 calls CAD "instantaneous operational penalty" (I-009) |
| I-10 | Δ_g defined explicitly | ALIGNED | M415 |
| I-11 | Chattering acknowledged; hysteresis/PI smoothing specified | PARTIAL | M605 mentions it. The cited appendix has no smoothing content (I-013) |
| I-12 | Grant placeholder kept with "% [AUTHOR INPUT REQUIRED ...]"; text "The authors thank the Deanship ..." | NOT ALIGNED (description) | Actual comment: "% [HUMAN REVIEW REQUIRED ... (Open item C7)]"; actual sentence: "The research work was funded by Umm Al-Qura University ..." (I-083). The open-item status itself is accurate |
| I-13 | P3 and P9 labeled calibrated benchmarks | ALIGNED | S241, S247, S253 |
| I-14 | Marschall: "legal compliance strictly requires an administrative hard merit floor that dual multipliers cannot override" | NOT ALIGNED | M800 asserts "Compliance ... is maintained" and treats the task safety floor as merit screening (I-004) |
| I-15 | ISO 23247 reframed | ALIGNED | M320 (placement issue I-111) |
| I-16 | "Tuesday morning" trope replaced | ALIGNED | M189, S399; the replacement phrase is awkward (I-108) |
| I-17 | Seven-step causal chain unpacked | ALIGNED | M134–136 |
| I-18 | Nominal chains de-nominalized | PARTIAL | M284 still lists the five liabilities twice (I-109) |
| I-19 | Referents clarified | ALIGNED for the cited lines | New referent issues elsewhere: I-031, I-033, I-115, I-137 |
| I-20 | "Price" polysemy standardized | NOT ALIGNED | 22+ remaining uses, including heading M696, M887 vs M935, S360, S475, Fig. 2 label (P-02, I-018, I-019) |
| I-21 | D^trans roster dependence confirmed | PARTIAL | Table 5 caption (M844) says only D^skill depends on the roster (I-069) |
| I-22 | 110-word sentence split | ALIGNED | M778 (new "To guarantee" overclaim, I-058) |
| I-23 | Formulaic transition skeletons removed | PARTIAL | Old phrases gone; new scaffolds at M1117, M1217, M1251, M1291 (I-074, I-079) |
| I-24 | Notation standardized; AOZ, PDT, WRP added to abbreviations | PARTIAL | The three abbreviations are never used in the text (I-148); Res superscript inconsistent |
| I-25 | Generalization scope clarified | PARTIAL | M136 scoped; M147, M985, M1289 generalize (I-025) |
| I-26 | Defensive aside removed | ALIGNED | — |
| I-27 | "Nothing simulated" repetitions pruned | PARTIAL | Still at M827, M1025, M1122, M1213; S114, S286, S579 (P-10) |
| I-28 | Literature synthesized and linked to constructs | PARTIAL | M171 ties skill-decay studies to D^skill, which the formula does not support (I-038) |
| I-29 | Self-dramatizing meta-commentary removed | PARTIAL | Specific phrases gone; "What It Buys" heading (M937) and "what this buys" (M1289) remain |
| I-30 | Institutional actors restored | ALIGNED | M778 |
| I-31 | Colloquial idioms replaced | PARTIAL | "settled later, by someone else" remains at S371; "settled later" at M864 |
| I-32 | Captions streamlined | PARTIAL | Interpretive captions remain: Table 2 (M507), Table 8 (M1039) |
| I-33 | Dual mapping added after Eq. (aug) | ALIGNED, but redundant | It duplicates M567 (I-121) |
| I-34 | Dashes standardized | PARTIAL | Em dashes at M368 and M1230 (I-149) |
| §C P-03 | Zero-covariance assumption "declared" | PARTIAL | See I-014 |
| §D | "Equations (1)–(35)" audited | NOT ALIGNED | The main text has 46 numbered equations |
| §D | Negative findings preserved: "unassisted machine performance advantage (4.34% cost saving)" | NOT ALIGNED (mischaracterized) | 4.34% is the *cost of preservation*, not a machine "cost saving" |
| §D | "requirement of an administrative merit floor to satisfy Marschall" preserved | NOT ALIGNED | No such statement in the text (I-004) |
| §D | Crossover at 13.23 listed as a negative finding | PARTIAL | It is produced by chosen parameters, not a finding (I-023) |
| §E | Journal-basis count 11,898 | ALIGNED with the script | Manuscript and cover letter disagree (I-082) |
| §F | Only one open item (grant code) | NOT ALIGNED | The stale submission package (I-001) and the Critical items above are also open |

**Other claims checked against the paper (cover letter):**
- "The main text is 11,507 words": does not match the current count (I-082).
- "It prices the developmental practice ... through a Human Capability Preservation Budget": the HCPB is a constraint, not a price, and the main text (M926) disclaims valuing practice.
- "Its central result ... four trainee posts where fourteen are required": depends on I-002.
- "Every number it prints is exact arithmetic on stated inputs": consistent with the text and `audit_numbers.py`, except the 9.56/9.57 rounding (I-140).
- "The repository recomputes every checkable number": not verified here (no repository access was used).
