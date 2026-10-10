# Revision Report: Repair of CivicWorkOS Against the Second Forensic Audit (`audit2.md`)

**Files revised:** `CivicWorkOS.tex` (main), `CivicWorkOS_supplementary.tex` (supplement), `cover-letter.md`, `count_words.py` (one-line change; see I-083).
**Package regenerated:** `submission/` and `CivicWorkOS-submission.zip`, via `make_package.sh`.
**Pre-revision copies kept for comparison:** session scratchpad (`orig_main.tex`, `orig_supp.tex`).
**Verification run after the final edit:**
- `audit_numbers.py`: 199 PASS, 0 FAIL, 2 KNOWN-DEFECT. The two known defects are pre-existing audit-trail records of deleted text.
- `check_repo.py`: 3 passed.
- Both documents build with 0 undefined references, including from the clean `submission/` directory.
- `count_words.py`: 11,961 words on the journal basis.

Line references below are to the **original** files, as the audit cites them (M = main, S = supplement).

---

## A. Repair Completed

I revised the manuscript and supplement against every issue in `audit2.md`. The audit was the repair specification and the manuscript was the authority on content. I added no data, experiments, results or citations. Wherever a printed number was involved, I recomputed it before changing any wording around it.

| Count | Status |
|---|---|
| **164** | Audit issues identified (6 Critical, 23 High, 74 Medium, 61 Low) |
| **156** | Fixed |
| **3** | Merged into another fix (I-099, I-109, I-149) |
| **5** | Not fixed: require author input (I-049, I-083, I-102, I-157, I-163) |
| **0** | Not safely fixable without unsupported information |
| **0** | Not applicable after review |

Some "Fixed" items also carry a confirmation the authors should make: I-002, I-023, I-026, I-048, I-062, I-064, I-068 and I-132. Section F lists these. In each case the text is now internally consistent and does not overclaim. What remains is a fact only the authors can supply.

I also fixed one contradiction the audit did not list. S140 says the calibration bias favors the framework, while S308 said it "runs against the framework". Both now say it favors the framework, which is also what the main text (M1244) says.

---

## B. Audit Resolution Matrix

### Critical and High (I-001 to I-029)

| ID | Status | Location | What Changed |
|---|---|---|---|
| I-001 | FIXED | `submission/`, zip | Regenerated with `make_package.sh` after all edits; clean build verified; `diff` shows that `submission/*.tex` match the root files exactly |
| I-002 | FIXED (author to confirm) | M390, M395, M892, M985, M1025, S331, abstract, intro, conclusion | Certification hours are now defined once as unshared, unassisted logged practice, which is the reading the arithmetic already used. "Supervised" no longer contradicts it. The 3.38 factor is split everywhere into 1.69 (machine assistance) × 2.0 (sharing with a lead). §6.6 states the alternative reading by exact arithmetic: τ = 2.03 years, n̂ = 7.0. The elicitation instrument (S331) now asks which reading a scheme uses |
| I-003 | FIXED | M1034, Table 8 caption, S421, S572 | The text now says that no cell of a 24-person domain meets n^min = 30, so a deployment would report the shares descriptively, and that the worked example sets the rule aside for exposition only. S421 now says "marginal groups on gender and contract status", which matches the table. S572 points to the stated exception |
| I-004 | FIXED | M800 | Compliance is no longer asserted. The text says the admissibility filters are task-level, not individual, that *Marschall* needs an individual merit floor the dual cannot override, and that such a floor could be encoded as a *restrict* guard whose content the framework does not supply |
| I-005 | FIXED | S222, S245 (P7), S281 | All three now say the mix shifts and λ_k changes only if the active pair of modes changes, which is consistent with M1124 |
| I-006 | FIXED | M966, S253 | "A quarter of the inspection budget" and the finance-committee line are removed. The +24.5% is described as a change in a rescaled score, not money. P9's 124.5% is described as a ratio of scores |
| I-007 | FIXED | Abstract, M224 | Rostering is acknowledged (it allocates training hours after the human/machine decision). The gap is scoped to the prior decision |
| I-008 | FIXED | M226, §7.2 | Added the gap→RQ mapping. §7.2 now states for each RQ whether it is answered by specification, by construction, analytically for one domain, or only by the unexecuted protocol |
| I-009 | FIXED | M284 | CAD is defined as a per-task penalty whose components are marginal proxies for stock changes, which matches M296 and M495 |
| I-010 | FIXED | M435 | The surviving human capacity is now stated as the condition under which all automation components are lost |
| I-011 | FIXED | M347, M368, S468 | The join ignores authority. Authority now governs amendment and retirement through the panel, not evaluation |
| I-012 | FIXED | M585, S523 | The integrality gap is described as a gap between optimal values, not as an error bound on the online rule |
| I-013 | FIXED | M605 | The dead cross-reference and "practical implementations" are removed. Smoothing is described as an option that is neither specified nor analyzed |
| I-014 | FIXED | Prop. 2, S496 | The condition is restated on duration-weighted means of learn_i, φ_m and ω, which fixes the units. The proposition notes that pairwise zero covariance is not sufficient |
| I-015 | FIXED | Prop. 4, S502 | δ̄_g is redefined as the largest upward estimate revision, matching the proof. The statement adds sequential observation and Z4 assumptions, and the resource bound now covers admitted tasks only. The proof was rewritten to match |
| I-016 | FIXED | Abstract, M968, conclusion | 3.46 vs 2.88 is presented as a consequence of η = 1.2 through the identity |
| I-017 | FIXED | §6.1 | The homogeneity assumption is stated, along with what depends on it |
| I-018 | FIXED | M887, M935, M1289 | The reversal is attributed to the binding constraint acting through its dual. w_9 is the "debt weight" throughout |
| I-019 | FIXED | S360, S475 | The claims that practice is "worth" something or has a "future value" are removed, which matches M926 |
| I-020 | FIXED | M1117 | Gives the full reversal condition, B_k/Φ_k > φ_{H+A+R}ψ_{a1} = 0.275. I checked it against every row of Table 9 |
| I-021 | FIXED | M1034, M1036 | Recruitment is now an explicit assumption in both scenarios. The 3.8-of-14 figure is described as a hiring decision outside **x** |
| I-022 | FIXED | M1230, S227, Table S4 | The sign of the trade-off is labeled structural and its magnitude empirical. "Bounds" is replaced by "ranges over the one-at-a-time sweep". P2 and P5 are relabeled as hypotheses |
| I-023 | FIXED (author to confirm) | M1221, M1223, Table 10 caption | The ordering and the 13.23 crossover are attributed to the tabulated parameters. Human-First's 0.15 is justified from the text. The baseline values are labeled as the authors' reading (see F) |
| I-024 | FIXED | M940, conclusion | The 0.33–9.60% range is added wherever 4.34% is quoted |
| I-025 | FIXED | M147, M694, M985, M1289 | The two causes and the single domain are carried into every restatement. "No headcount plan" and "a city cannot see" are removed |
| I-026 | FIXED (author to confirm) | S129, S286 | The inspection volume of 2,100 is relabeled "Illustrative; to be calibrated". S286 says the worked example uses it |
| I-027 | FIXED | S149 | The text now acknowledges that availability-ordered rosters favor CivicWorkOS on the capability metrics |
| I-028 | FIXED | M926 | "Earlier presentations inverted the reading" removed |
| I-029 | FIXED | M1244 | Revision history removed. "Calibration portals" replaced with "open-data portals the protocol calibrates against" |

### Medium (I-030 to I-103)

| ID | Status | Location | What Changed |
|---|---|---|---|
| I-030 | FIXED | M151, M1246, S227 | One count everywhere: ten criteria, eight hypotheses and two calibrated benchmarks |
| I-031 | FIXED | Abstract | "The constraint reveals" → "the capability budget binds with" |
| I-032 | FIXED | M130 | Universals scoped to "we know of no municipal allocation mechanism" |
| I-033 | FIXED | M132–134 | Referent named. The one-sentence paragraph merged |
| I-034 | FIXED | M134 | Uneven distribution of developmental work hedged. Invisibility claim scoped to a task-level productivity objective. Grammar fixed |
| I-035 | FIXED | M144 | "Tractable" → "expressible" |
| I-036 | FIXED | M148 | "Preventing" → "reproduces its composition only by recorded decision" |
| I-037 | FIXED | M166 | The second difference from rostering restated so it is a real difference (sized from attrition to replace leavers) |
| I-038 | FIXED | M171 | Meta-analyses "would calibrate D^skill if it were extended with a retention term" |
| I-039 | FIXED | M173 | Restored the Bainbridge premise for the fallback/competence split |
| I-040 | FIXED | M187 | Job exposure separated from residents' exposure to decision errors |
| I-041 | FIXED | M194 | Resilience sentence moved to its own paragraph, linked to Layer 5 |
| I-042 | FIXED | M224 | Stated as an expectation. Irony removed |
| I-043 | FIXED | M315 | d_i excluded from the normalization statement |
| I-044 | FIXED | M352–362 | "Resolve procedural circularity", "twin" and "filter" replaced with mode-level and roster-level status functions |
| I-045 | FIXED | M385 | "Substantive repair" → what ψ_a does |
| I-046 | FIXED | M400 | Recruitment premise made conditional |
| I-047 | FIXED | M442, M554 | Res(**x**) defined through F_k after the window's assignments. Breach made conditional |
| I-048 | FIXED (partial; see F) | Notation throughout, S528 | κ(i) → k(i); reserve threshold ρ_s → R^min_s; debt-model π_j → p_j; "(1−ε)-competitive" → "(1−o(1))"; Res^(n) → Res^(n_s). The false "collisions removed" claim is replaced by a note on deliberately shared letters. τ_g and κ_s are kept because Figure 1 prints them |
| I-049 | NOT FIXED: AUTHOR INPUT | M454, S480 | The main-text flow/stock partition was corrected. S480 now states that Q, P, Tr, D^acct and D^dep have no assigned agent. Assigning them is a design decision |
| I-050 | FIXED | Eq. (aug) | δ^disp_g defined at first use. Added to the notation table |
| I-051 | FIXED | Eq. (deltares) | Index i added (and propagated). The counterfactual is defined |
| I-052 | FIXED | M562 | "Shows to be a legal requirement" → "argues is legally necessary" |
| I-053 | FIXED | Algorithm 1 | Roster-level prohibit is now applied for every roster; restrict additionally filters |
| I-054 | FIXED | M651 | Query count restated per roster |
| I-055 | FIXED | Prop. 1 | ζ̄ is defined over policy- and safety-admissible modes only |
| I-056 | FIXED | Throughout | One stock term: "trainee cohort" / "developing posts". The annual flow ηNr is stated in Prop. 2. The figure axis and section heading are updated |
| I-057 | FIXED | Prop. 3 | Scope limited to SCV. The interpretation moved outside the proposition. "Named after a priced construct" removed |
| I-058 | FIXED | M778 | "To guarantee" removed. Resident representation is addressed as an open design question |
| I-059 | FIXED | M497, M780, M1271 | Precise statement (supported points; discrete set) given once in §5.1, and referred to elsewhere |
| I-060 | FIXED | M787 | Split into standing/windows, record, and remedy paragraphs. Aphorism removed |
| I-061 | FIXED | M789 | "Most of the accountability benefit" removed |
| I-062 | FIXED (verify) | M794–796 | 2006/54 now covers sex and 2000/78 its own grounds. District is noted as not a protected ground. The cases are stated as decided under 76/207/EEC |
| I-063 | FIXED | M801 | "Never" is now scoped to the access constraint. The other constraints are noted as able to require staffing |
| I-064 | FIXED (verify) | M802 | The no-exposure claim is withdrawn. Directives 1999/70/EC and 97/81/EC and possible indirect age discrimination are noted |
| I-065 | FIXED | M816 | The national-succession gap is attributed to the access constraint, not ψ_a |
| I-066 | FIXED | M253, M415, M420 | The payroll-only scope is stated at the definitions of W_k and Δ_g |
| I-067 | FIXED | M832 | The worked example uses the appendix's *restrict* status and null-roster logic |
| I-068 | FIXED (author to confirm) | M834 | The supervision rule is stated as an assumed restrict guard. No threshold was invented |
| I-069 | FIXED | Table 5 caption | Says D^trans is roster-indexed but equal across both rosters here |
| I-070 | FIXED | M926 | "Without solving" → "a consistency check" |
| I-071 | FIXED | M1036 | Correct reason given (0.125 < 0.27 floor) |
| I-072 | FIXED | Table 8 caption | Acknowledged as a modeling choice. Eligibility attributed to W_k |
| I-073 | FIXED | Table 9 caption | Defines "mode reversal" and "no reversal" |
| I-074 | FIXED | M1117 | Scaffold removed. Split into three paragraphs. One-at-a-time scope and joint-variation caveat stated |
| I-075 | FIXED | M1134, M1146, Table 10, Fig. 4 | τ_skill is "set equal to" τ_k by assumption, not "derived" |
| I-076 | FIXED | M1228 | "Realistic" → "illustrative". "None without it" → "set by recruitment" |
| I-077 | FIXED | M1237 (now summarized) | "Is a ratio" → coefficients of both signs; neither packing nor covering |
| I-078 | FIXED | M1242, Table 10 caption | Mapping given (Capability Matching after Ranz; Ergonomics-Aware Role Allocation after Merlo). The unimplemented baseline rows are flagged |
| I-079 | FIXED | M1251–1259 | "Four constituencies" scaffold removed. The fourth item reframed |
| I-080 | FIXED | M1253 | Made conditional on the reserve being sized and maintained |
| I-081 | FIXED | M1287 | "Democratic control" removed. "Proposition" → "claim". Necessary-condition scope stated |
| I-082 | FIXED | M108, cover letter | 11,507 → measured 11,961 in both |
| I-083 | NOT FIXED: AUTHOR INPUT | M1300–1319 | Duplicate removed: the Acknowledgment section that repeated the funding sentence was deleted. `count_words.py` now treats Acknowledgment as optional. **The grant-code placeholder in Funding remains** |
| I-084 | FIXED | S158, P3 | CFI defined as a mean over domains. P3 uses the 0–1 scale throughout |
| I-085 | FIXED | Table S3 | M is in objective units per qualified-practice hour of shortfall |
| I-086 | FIXED | P1 | Worked value given as 0.315 (debt model, year 10), with 0.79 per-task value marked as reference only |
| I-087 | FIXED | S395 | Unverifiable robotics comparison removed; neutral description kept. Restore it if verified against Eloundou et al. |
| I-088 | FIXED | S451 | "Weight Review Panel" |
| I-089 | FIXED | S475 | Scoped to the worked case, with its numbers (0.127 vs 0.022, recomputed) |
| I-090 | FIXED | S583 | Names the two quantities Prop. 4 bounds |
| I-091 | FIXED | S140 | Revision history removed. Bias direction stated as a present fact |
| I-092 | FIXED | S162 | Present-tense reason for the exclusion |
| I-093 | FIXED | S169 | Surrogate history removed |
| I-094 | FIXED | S211 | Test choice justified without history |
| I-095 | FIXED | S222 | History removed (merged with the I-005 fix in the same sentence) |
| I-096 | FIXED | S227 | "Have been restated" / "no longer" → present-tense statements |
| I-097 | FIXED | S461 | "Category error" history → present statement of where χ_g sits |
| I-098 | FIXED | S528 | "Collisions removed" history → notation note (see I-048) |
| I-099 | MERGED (I-019) | S360 | Rewritten in the same sentence as I-019 |
| I-100 | FIXED | M1219 | "Repeat the category error" → "as reskilling coverage is" |
| I-101 | FIXED | M1264 | Workforce Development Agent named. "One city scale" clarified. Stray tab and missing blank line fixed |
| I-102 | NOT FIXED: AUTHOR INPUT | Fig. 2 | Caption fixed: "scores"; the feedback edge is described as post-execution. **The raster image still draws the dashed edge from the diamond and labels the box "Price Each".** It needs regenerating from its source |
| I-103 | FIXED | Fig. 1 caption | The caption says the "Layer 4" box covers Layers 4 and 4b, and that the η_k/θ/guard flows are not drawn as separate edges |

### Low (I-104 to I-164)

| ID | Status | Location | What Changed |
|---|---|---|---|
| I-104 | FIXED | Abstract | "Bind the objective" → "restrict the allocation" |
| I-105 | FIXED | M145 | "Routinely conflated" removed |
| I-106 | FIXED | M171 | "Demonstrates" → "argues" |
| I-107 | FIXED | M173 | Rashidi sentence moved to where it connects |
| I-108 | FIXED | M189, S399 | "Ex ante at runtime" straw man → "We borrow their concepts, not a decision procedure" |
| I-109 | MERGED (I-009) | M284 | Duplicate list removed in the I-009 rewrite |
| I-110 | FIXED | Throughout | All 36 lowercase "equation~" changed to "Equation~". The forward reference to Eq. (scv) is now signposted. Object-named forms ("constraint (n)", "program (n)") are kept by design |
| I-111 | FIXED | M320 | ISO sentence reduced and tied to learn_i |
| I-112 | FIXED | M337 | Mechanism stated (competent leavers not replaced) |
| I-113 | FIXED | M373 | Idiom → "one auditable unit" |
| I-114 | FIXED | M395, M189 | "Renewable but depletable shared resource" in both places. Ambiguous "users" removed |
| I-115 | FIXED | M420 | Referent made explicit (the ceiling) |
| I-116 | FIXED | Fig. 1 caption | Explains the system, not the drawing |
| I-117 | FIXED | M462 | "Cannot defeat" → "still meets" |
| I-118 | FIXED | M495 | "Six of the eight flow terms, and the debt term" |
| I-119 | FIXED | M497 | Rolling-window causal step unpacked |
| I-120 | FIXED | M499–507 | Heading "Default Weights and Effective Weights". Skill formation "ranks sixth". Caption corrected |
| I-121 | FIXED | M579 | Duplicate dual mapping removed |
| I-122 | FIXED | Eq. (feedback) | Comma → period |
| I-123 | FIXED | M562 | S^min_i defined with the program |
| I-124 | FIXED | M677 | Rhetoric removed. Example tied to §6.1. "Hiring lever" removed |
| I-125 | FIXED | M711 | Reworded per task |
| I-126 | FIXED | M725 | Clarified |
| I-127 | FIXED | M768 → §3.1 | Notation pointer moved to the start of §3 |
| I-128 | FIXED | M776 | Idiom → literal |
| I-129 | FIXED | M794, M810 | Superlatives removed |
| I-130 | FIXED | M805, M823, M1259 | All three aphoristic closers rewritten |
| I-131 | FIXED | M814 | Program penalty contrasted with Nitaqat sanctions |
| I-132 | FIXED (author to confirm) | M823, M280 | n^min defined in the main text. "A decade" → "multi-year formation periods" (see F) |
| I-133 | FIXED | Table 5 | Row label "Developmental shares and stock-change terms" |
| I-134 | FIXED | M897 | "Condition (feas) is met with about 18% to spare" (5,880/4,976.64 = 1.18) |
| I-135 | FIXED | Table 6 caption | Single-mode options noted (H+R/a₁ alone, SCV 0.3082) |
| I-136 | FIXED | M966 | Floor attributed to safety only |
| I-137 | FIXED | M1029 | "Explains why no employer" → "suggests why an employer may not". Overgeneralization scoped |
| I-138 | FIXED | M1034 | Rhetoric removed |
| I-139 | FIXED | M1060 | "Documented" → "shows by construction" |
| I-140 | FIXED | M1124, S583 | 9.56% → 9.57% (recomputed 9.566%; matches Table 9) |
| I-141 | FIXED | M1117, conclusion | "15%" → "about 18%" headroom |
| I-142 | FIXED | M1122, S581 | "Will meet both" → "could meet either" |
| I-143 | FIXED | §6.6, M1126, S587 | The 14 = 14 coincidence noted |
| I-144 | FIXED | Fig. 4 caption | "All of it unformed skill" |
| I-145 | FIXED | M1255 | Stated as the worked-domain numbers |
| I-146 | FIXED | M1285 | Generic opening replaced. "Governed portfolio" removed |
| I-147 | FIXED | M1293 | "Tomorrow" removed |
| I-148 | FIXED | Abbreviations | AOZ, PDT and WRP removed |
| I-149 | MERGED (I-011, I-022) | M368, M1230 | Both em dashes removed in those rewrites. A global search finds none in prose |
| I-150 | FIXED | S69 | Caption no longer claims the body reproduces every value |
| I-151 | FIXED | S84 | auth_i/priv_i declared a proxy for rights impact. Bridge-task consequence stated |
| I-152 | FIXED | S158 | Recovery defined against R^min_s = κ_s D^peak_s |
| I-153 | FIXED | S209 | "Negotiation timing" → "agent response timing" |
| I-154 | FIXED | S351 | "Establishing" → "arguing" |
| I-155 | FIXED | S358 | "Fifty years" → "long" |
| I-156 | FIXED | S371 | Colloquialism replaced |
| I-157 | NOT FIXED: AUTHOR INPUT | S383 | Needs checking against Alfrink et al.; left unchanged |
| I-158 | FIXED | S414 | Scope states what the main text relies on |
| I-159 | FIXED | S482, M454 | Auction vocabulary replaced (call for estimates; allocator selects) |
| I-160 | FIXED | Eq. (anchors) | Annotation now uses ℓ_i correctly |
| I-161 | FIXED | Notation table | Added ς, M, P_mode, G_roster, n_m, ζ_w, E_k, n^rem, Θ_k, the learn/φ/ω means, H^base, δ^disp, δ̄, ϖ, Δ^res, D^tot, U^used, φ^Z3, C, C_j, c_j, p_j, τ_j |
| I-162 | FIXED | S587 | Scoped to the domain; "will spend" → "would recruit trainees the stream cannot form" |
| I-163 | NOT FIXED: AUTHOR INPUT | Build log | `xr` "multiply defined" natbib warnings remain (74, cosmetic). The package builds cleanly. Whether to keep `xr` in the Frontiers upload is a production decision |
| I-164 | FIXED | M195, M824, M1264 | Blank lines added before the headings |

---

## C. Global Patterns Repaired

The second, manuscript-wide sweep covered each pattern in both files.

- **P-01 Revision-history leakage.** Search terms: earlier, repair, version, category error, formerly, no longer, restated. All 15 sites are fixed. The one remaining hit (S61, "does not repair the exclusion") is ordinary usage.
- **P-02 "Price" polysemy.** One term per object:
  - w_9 is the *debt weight*.
  - λ_k is the *dual* or *marginal opportunity cost*.
  - Duals in general are *dual multipliers*.
  - Agents *score*.
  - The constraint system has an *operational cost*.

  Headings were renamed in §4.8, §6.2, §6.4 and §6.5, as were the Table 1 column and RQ2. "Price" survives only in the label `prop:price` and in the quoted Figure 2 label.
- **P-03 Undefined symbols and referents.** δ^disp, n^min, the supervision rule, S^min and the Workforce Development Agent are now defined at or before first main-text use. Ambiguous "this", "that second half" and "which" are fixed.
- **P-04 Fixes not propagated.** The hypothesis count, M's unit, the access-constraint form, prohibit vs restrict, λ behavior under shock, the 9.57% figure and the word count now agree across both files and the cover letter.
- **P-05 Over-generalization of dilution.** Every restatement of 3.38 / 4.05 / "four vs fourteen" (abstract, intro, contributions, §4.7, §6.6, conclusion, cover letter) now names both causes and the single domain.
- **P-06 Legal overclaim.** No compliance is asserted. Grounds and directives are corrected. Exposure is stated as needing analysis.
- **P-07 Assumptions stated as fact.** Recruitment, uneven distribution, the reserve outcome and the panel's balance are each marked as an assumption, expectation or design intent.
- **P-08 / P-09 Scaffolds and aphorisms.** Removed: "four primary operational consequences", "Three analytical properties", "four constituencies", the finance-committee coda, "re-founded", "most a design can offer" and "judged as such".
- **P-10 Defensive repetition.** Redundant "not simulation" sentences are removed from §6.10 and the Data Availability statement. Caption-level disclaimers are kept.
- **P-11 Metadata.** Word count, duplicated back matter and abbreviations are fixed.
- **P-12 Inputs presented as results.** 3.46 vs 2.88, the Figure 4 ordering, the 13.23 crossover and τ_skill are now presented as consequences of the chosen inputs.
- **P-13 Metaphor inflation.** "Twin", "filter", "auctioneer", "awards", "sealed-bid", "What It Buys" and "what this buys" are replaced with literal names.
- **P-14 Citation chains.** §2.4 now separates the two notions of exposure. The §2.5 resilience sentence is linked. The §2.3 MoonGuha sentence is consolidated into §5.2, where it is used.
- **P-15 Formal claims stronger than proved.** Propositions 1–4, the integrality gap, the "bounds" wording and "says when satisfiable" are each restated as narrowly as the proof supports.
- **P-16 Equation-reference style.** Unified (see I-110).

---

## D. Scientific Meaning Preservation

I checked the third-pass meaning comparison against the pre-revision copies.

- **Equations.** No equation's mathematics changed. Symbol renames: κ(i)→k(i), ρ_s→R^min_s, π_j→p_j, Res^(n)→Res^(n_s). Index additions: Δ^res gains i, and Prop. 4's resource sum is over admitted tasks. Eq. (feedback) punctuation fixed.
- **Theorem statements.** Props. 1, 2 and 4 were restated where the audit showed the statement did not match the proof or the units. Each restatement is narrower or equal to what was proved; none is stronger:
  - Prop. 1: ζ̄ excludes the budget guard.
  - Prop. 2: duration-weighted factorization.
  - Prop. 4: δ̄ as estimate revision, plus sequential observation, Z4 and admitted-task scope.

  Prop. 3 is unchanged except that the interpretation now sits outside it.
- **Assumptions.** Five previously implicit assumptions are now stated:
  - task homogeneity;
  - recruitment channel;
  - the supervision rule;
  - the reading of certification hours;
  - the τ_skill = τ_k identification.
- **Numerical results.** No printed value changed except 9.56% → 9.57%, a rounding correction. I recomputed the new derived figures:
  - 1.69 × 2.0 = 3.38;
  - 2.03 years and n̂ = 7.0 under the alternative reading;
  - 0.275 reversal threshold, checked against all Table 9 rows;
  - 18% headroom;
  - 0.315 = 31.51/100;
  - 0.127 vs 0.022.

  `audit_numbers.py`: 199 PASS, 0 FAIL.
- **Statistical claims.** The protocol remains unexecuted. No statistical result is claimed.
- **Experimental conditions.** Unchanged. P2 and P5 were relabeled from "structural" to hypothesis, which is the audit-required reclassification.
- **Limitations and negative results.** All are preserved: Human-First wins for 13 years, the mode reversal is not robust, vendor debt is unbounded, non-payroll workers are invisible, the baselines are unimplemented, and the calibration bias favors the framework. Several are strengthened: the new alternative-reading caveat, the n^min exception, the cost-index caveat, and the admission that the baselines favor CivicWorkOS.
- **Contribution claims.** Narrowed where the audit required (novelty gap, dilution scope, "preventing" composition reproduction). No contribution was added.

**Areas needing author confirmation:** see F.

---

## E. Page-Limit Verification

- **Target format:** Frontiers in Artificial Intelligence, Hypothesis and Theory, using `FrontiersinHarvard.cls` and `frontiers_suppmat.cls` unchanged. I made no change to margins, font sizes, spacing or float sizes.
- **Applicable limit:** 12,000 words. Source: `REVISION-PROGRAMME.md`. The venue sets no page limit for this article type.
- **Counting basis:** `count_words.py`, which counts texcount body words and excludes the abstract and funding. Captions and headings are outside texcount's text count.
- **Word counts:**
  - Before revision: 11,898.
  - After the audit repairs, before compression: 13,062 (over the limit).
  - **Final: 11,961.** Within the limit, with 39 words to spare. The `\extraAuth` field and cover letter state this figure.
- **Page counts:** main PDF 36 pages, supplement 24 pages. Supplementary material is outside the word limit.
- **Abstract:** 291 words by texcount, up from 261. The venue's abstract limit is not stated in the supplied materials; confirm before upload.

**Compression was required: about 1,100 words.** It came from three places.

*Moved to the supplement, with a short main-text summary left in place:*
- The full online-guarantee discussion, now S8 "What a Guarantee for the Online Rule Would Require".
- The liability-by-zone paragraph, now S1 "Liability by Zone".
- The Gulf Just Transition paragraph, now in S7.

*Rewritten more tightly without dropping any claim:*
- contributions, conclusion, §5.1, §5.3, §5.4, §6.6, §6.7 and §6.10;
- the §7.4 protocol summary and §7.5;
- the Data Availability statement.

*Removed as duplication:* the CAD-stocks restatement (§3.1), the dilution-property sentence duplicated in §4.7 and §6.6, and the MoonGuha sentence duplicated in §2.3.

No equation, result, condition, limitation or citation was removed from the article. Every cited key in the moved text is still cited in the main text.

---

## F. Remaining Issues

1. **Grant code (I-083).** The Funding statement contains a placeholder: "26UQU(Staff number)(track name)xx". The real Umm Al-Qura grant number is needed. I removed the duplicated Acknowledgment section. Add one back only if there is something to acknowledge besides the funding.
2. **Figure 2 image (I-102).** `images/runtime.png` draws the dashed feedback edge from the "No (m,a) left?" diamond, which is before execution, and labels a box "Price Each". The caption now describes the intended semantics, but the image needs regenerating from its source. No source file is in the repository. Figure 1's "τ_g" and "κ_s" labels are also why those two symbols were not renamed (I-048). If Figure 1 is redrawn, consider renaming them.
3. **Agent assignments (I-049).** Q, P, Tr, D^acct and D^dep have no estimating agent in S7.8. Which agent owns each is a design decision.
4. **Citation checks.** (a) I-157: confirm that Alfrink et al. (2023) describe "five system features and six development practices". (b) I-087: I removed the claim that Eloundou et al. compare LLM exposure with robotics; restore it only if the paper makes that comparison.
5. **Certification-hours reading (I-002).** The arithmetic assumes certification counts unshared, unassisted practice hours. Please confirm this for the inspector scheme the example represents. If the scheme counts hours worked beside a lead, the headline becomes 2.03 years and seven posts (stated in §6.6), and the abstract, introduction, conclusion and cover letter would need the smaller figures.
6. **Legal text (I-062, I-064).** The corrected attributions should be checked by the authors' legal adviser:
   - Directive 2006/54/EC as the recast of 76/207/EEC;
   - Directive 2000/78/EC grounds;
   - Directives 1999/70/EC and 97/81/EC;
   - indirect age discrimination.
7. **Table 10 baseline parameters (I-023).** The replenishment values for Capability Matching (0.35/0.30) and Ergonomics-Aware Role Allocation (0.40/0.45) are now labeled as the authors' reading of unimplemented methods, but no rationale is given for those specific values. Add one sentence of rationale per row, or accept the label.
8. **Calibration status (I-026).** Only the inspection row was relabeled. Please confirm whether the other "Calibrated" sector volumes in Table S2 were actually fitted to the named series, since the protocol has not been run.
9. **Supervision rule and retention period (I-068, I-132).** The one-trainee-per-lead rule is now an explicit assumption with no invented threshold. The ledger retention period is "multi-year formation periods" rather than the unexplained "decade". Supply a specific rule or period if one is intended.
10. **Build warnings (I-163).** The `xr` cross-document setup produces 74 cosmetic natbib "multiply defined" warnings. Decide whether Frontiers' production system should receive the main file with `\externaldocument`.
11. **Documents outside the audit scope that are now stale:**
    - `CivicWorkOS-diff.pdf`, which is included in the submission zip, is the latexdiff from the earlier phase and does not show these repairs.
    - `response-to-reviewers.md` was not updated.
    - `report.md` contains descriptions that audit2 Appendix A found misaligned; this report supersedes them.

    Regenerate the diff and update the response document before upload if both are to be submitted.

Nothing has been committed. All changes are in the working tree for your review.
