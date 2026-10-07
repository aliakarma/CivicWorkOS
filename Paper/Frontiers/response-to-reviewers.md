# Response to Reviewers

**Manuscript:** *CivicWorkOS: Capability-Preserving Allocation of Municipal Work Among Humans, AI Agents and Robots*
**Article type:** Hypothesis and Theory, Frontiers in Artificial Intelligence
**Revised main text:** 11,491 words on the journal's counting basis (11,769 by `texcount`, which includes the abstract, acknowledgment and funding statement), 4 figures, 10 tables. A 22-page Supplementary Material document accompanies it.

Section, table and figure numbers below are those of the **revised** manuscript. The review was written against a draft with two more top-level sections, so its numbering is one or two higher than ours. Where it helps, the reviewers' number is given in brackets, for example "§6.8 [R: §7.7]".

---

## 1. Opening statement

The review found that the submitted draft's Results section reported a thirty-seed, six-sector, ten-year simulation study that was never run. The reviewers were right. That section was a prior draft's set of specified evaluation targets, which had been rewritten into the past tense. Meanwhile the surrounding text, the Data Availability Statement and the public repository all kept the original and correct position: the protocol had not been executed. We have removed the section in full. No number from it survives anywhere in the article, in the past tense or with a caveat. The article is now declared a Hypothesis and Theory article. Its evidence is the exact worked allocation of §6, the sensitivity frontier of §6.8, the two parameter shocks of §6.9 and the closed-form debt model of §7.1. The evaluation protocol is kept in specified form (§7.4; full specification in Appendix S2). It opens by stating that it has not been executed. The manuscript, the Data Availability Statement and the repository README now say the same thing about what was and was not done.

We also corrected the arithmetic defects the reviewers found, brought the manuscript under the word limit, completed the front and back matter, and acted on the constructive suggestions. Those suggestions are the intake requirement as a headline result with its own figure, a GCC legal analysis, the online-rule bound and the scalarization admission. Section 2 lists every item and where it was addressed. Section 4 lists what we did not change, and why.

During the revision we found six further defects that the review did not reach. They are reported in Section 2 as N1–N6. Five concern the reproducibility artifact the reviewers credited; N5 concerns how citations rendered.

---

## 2. Summary of changes

| ID | Reviewer item | Action taken | Location in revision |
|---|---|---|---|
| C1 | R1 W1; R2 C1; R3 §8.1; AC concern 1: Results report an unconducted study | Section deleted in full, along with its seven tables (`tab:mainresults`, `tab:persector`, `tab:ablation`, `tab:stress`, `tab:dist` as a simulated result, `tab:runtime`, `tab:hypoutcomes`). The protocol is kept as a specified-but-unexecuted plan. | §7.4; Appendix S2 |
| C2 | R1 W1; R2 C1: "will be lodged … before the simulation is executed" vs reported results | The future-tense statement now governs. §7.4 and Appendix S2 both say the protocol has not been executed and that OSF lodgement precedes execution. | §7.4; App. S2.7 |
| C3 | R1 C2: Abstract leads with 63.2%, 86.8%, 0.97 | Abstract rebuilt. Every number in it traces to §6, and it leads with the intake requirement. | Abstract |
| C4 | R1 W2: Data Availability Statement self-contradictory, misdescribes repository, wrong cross-reference | Rewritten in the repository README's own terms, with cross-references corrected. It states that `sim/` is synthetic demonstration data and that the protocol has not been executed. | Data Availability Statement |
| C5 | R1 W10(b); AC: ~21,050 words against 12,000 | 11,491 words on the journal's basis. Relocated material is in the Supplement (S6–S10). | whole manuscript |
| C6 | R1 W10(a): no keywords | Eight keywords. | p. 1 |
| C7 | R1 W10(d): funding placeholder | **Open at the time of writing:** the grant code is awaited from Umm Al-Qura University. See Section 4. | Funding; Acknowledgment |
| C8 | R1 W10(e): no Ethics Statement | Added. It records that no human participants or personal data were involved and that the elicitation protocol of App. S5 would require approval before execution. | Ethics Statement |
| C9 | R1 W10(c): empty Abbreviations | Populated with the ten acronyms the main text uses. | Abbreviations |
| C10 | R1 §1: article type undeclared | Declared as Hypothesis and Theory on the title page. | p. 1 |
| H1 | R1 W4: access-ablation sign and magnitude wrong in prose | Closed by removal: the ablation section no longer exists. | — |
| H2 | R1 W5: "at a cost of 1.3 CAD points" in three places | Closed by removal. The Conclusions now report the access arithmetic (622 h vs 1,344 h) instead. | §8 |
| H3 | R1 W5: P8's "CAD ≤ +5" clause vacuous | Closed by removal. P8 survives only as an untested specified hypothesis. | App. S2.7 |
| H4 | R1 W6: "< 1.5 s" vs a tabled 74 s | Closed by removal: the runtime table is deleted. The revision states that no solver profile has been measured. | §7.7 |
| H5 | R1 W7; R3 §8.4: robustness claim contradicted by `tab:sensitivity` | Narrowed to what Table 9 supports (wording quoted in §3). | §6.8 |
| H6 | R1 W3; R2 C3–C4: ERA scored but unimplemented | Removed from all reported values. Kept only as a specified comparator, with the circularity concession stated in the main text. | §7.4; App. S2.2 |
| H7 | R1 W8; R2 C5: analytic recomputations presented as simulation output | The retirement-wave arithmetic was moved to a new subsection, labeled as exact arithmetic on the model. The "simulated dual 0.0451" sentence was deleted. | §6.9; App. S10 |
| H8 | R1 W9; R2 §6.4: appeals figure 0.942 without a generative model | Removed. App. S2.3 states that no appeals throughput can be reported without such a model and names the four components it would need. | App. S2.3 |
| M1 | R1 audit 1: 0.0273/0.6 printed as 0.0454 | The equation now carries the unrounded tied-mode values (0.308240, 0.335452, difference 0.027212), so it reproduces its own quotient, λ = 0.045353. 0.0454 is used consistently at all 15 sites. | Eq. (lambdaworked), §6.4 |
| M2 | R1 audit 2: tied augmented values do not round to 0.4352 | At the exact λ the two values are equal by construction, since λ is defined by the tie. Printed as 0.435229. | §6.4 |
| M3 | R1 audit 6; R2 §7: debt decomposition does not reproduce its values | The figure's coordinates did not follow from any stated parameter set. New Table 10 fixes (c_j, π_j,∞, τ_j) for all five components of all six strategies, and Figure 4 is replotted from Eq. (cadmodel). Bounded part 17.98, residual slope 1.45/yr, crossover t = 13.23, C(20) = 46.89 vs 52.89. | §7.1; Table 10; Fig. 4 |
| M4 | R1 audit 7: P3 gap uses the weaker comparator | Closed by removal. | — |
| M5 | R1 minor 1: `tab:persector` labels a sum a mean | Closed by removal. | — |
| M6 | R1 §7; AC: scalarization admission belongs where legitimacy is claimed | Moved to §5.1 and expanded. The Limitations entry now points there. | §5.1 |
| M7 | R3 §7, §9.3; AC: no GCC/Saudi analysis | New subsection mapping the Civil Service Law nationality rule and Nitaqat onto Eq. (access), and `ILOESCWA2026` onto Eq. (justtransition). Co-author verification of the legal characterization is pending. | §5.4 |
| M8 | R1 §7; R3 §5.1–2: no regret/violation bound; CMDP and online matching unengaged | New subsection states the target bound and four obstacles, and engages both literatures. | §7.3 |
| M9 | R3 §5: `syed2026fedagent` does not support its claim | Removed at both sites. | §2.4; App. S6 |
| M10 | R1 minor 7: reference tables in main text | Notation and parameter tables moved to the Supplement. | App. S8.4; App. S2.4 |
| L1 | R1 minor 2: 53 overfull boxes | No overfull box comes from the content. The remainder reproduce in an empty document on the unmodified journal class. | — |
| L2 | R1 minor 3: mixed orthography | US spelling throughout. | — |
| L3 | R1 minor 5: `BenDaya2026`/`syed2026fedagent` volume–number | Not a collision: Crossref gives 9(9):136 and 9(7):106, two issues of one volume. The fields were corrected so the article number prints. | References |
| L4 | R1 minor 6: "two to four points" | Closed by removal: the paragraph compared the closed form against the deleted simulation. | — |
| L5 | R1 W10(f): orphaned dagger | Attached to the two equal-contribution authors. | p. 1 |
| L6 | R1 W10(g): empty `\correspondance{}` | The corresponding-author block was already rendering. The class prints it from `\corrAuthor`/`\corrEmail`, and the official template leaves that argument empty. Verified on the compiled PDF. | p. 1 |
| L7 | R1 W10(h): "AA" initials collide | AAk and AAl, with the convention stated. Contribution roles were also corrected to match a theory article. | Author Contributions |
| L8 | R1 S2; R3 §3.1, §9.2; AC: intake requirement buried | Now in the Abstract, the Contributions list, the closing sentence of the Introduction, §6.6, the Conclusions, and a new Figure 3. | Abstract; §1.1; §6.6; Fig. 3; §8 |
| N1 | *(found in revision)* README credited a different author list | README and `CITATION.cff` rebuilt on the manuscript's author list. A repository check now fails on any divergence. | repository |
| N2 | *(found in revision)* verification script checked a superseded worked example (B_k = 2,073.6, not 4,976.64) | The drift was in three scripts and the domain configuration. The repository now imports the manuscript's constants from one source, so no file restates a printed value. 82 checks pass. | repository |
| N3 | *(found in revision)* verification aborted on a missing dependency | Dependency repinned. Verified from an empty environment built from `requirements.txt` alone. | repository |
| N4 | *(found in revision)* repository cited a third section numbering | Every reference converted to LaTeX labels, which a repository check resolves against the compiled manuscript. | repository |
| N5 | *(found in revision)* author-subject citations printed authors twice | 77 converted to textual citations and 91 to parenthetical. | throughout |
| N6 | *(found in revision)* the Data Availability link opens the repository's default branch, which predated the revised README and scripts | The revised repository will be merged into the default branch before submission, so the link opens the version this article describes. **Open at the time of writing.** | repository |

---

## 3. Responses to each reviewer

### Reviewer 1

We thank Reviewer 1 for the independent recomputation that anchors the whole review. It established which parts of the paper were sound and located the defects precisely.

**W1 / Question 1.** *"Which of these three statements do you intend the reader to believe, and on what date was the thirty-seed six-sector ten-year study run?"*
The study was not run, and it has not been run since. The statement in the former §8.8 that the hypotheses would be lodged "before the simulation is executed", the Data Availability Statement and the repository README were correct. The Results section was not. It has been removed in full (C1, C2). The protocol is kept in specified form only, and §7.4 opens: "The protocol described in this subsection is specified in full and *has not been executed*."

**W2.** The Data Availability Statement has been rewritten (C4). It now says that no dataset was created or analyzed. It says that every value in §6, §6.8, §6.9 and §7.1 can be reproduced from the article by direct arithmetic, and that the repository recomputes each checkable number. It says that `sim/` runs on labeled synthetic demonstration data and must not be cited as municipal validation, and that the protocol has not been executed. The cross-references point to the sections that hold the numbers.

**W3 / Question 2.** *"How was 52.9 h obtained?"*
It had no derivation. The same is true of all twelve ERA values. They have been removed. ERA is kept only as a specified comparator in the unexecuted protocol (App. S2.2). The concession the reviewer asked us to import is in the main text at §7.4: "An evaluation in which four of six comparators are configurations of the proposed objective can show that the mechanism does what it was designed to do; it cannot show that it outperforms an independently designed alternative. The two external baselines are specified for that reason, and the comparison is incomplete until they are run; neither is implemented at the time of writing."

**W4, W5 / Question 3.** The reviewer read the ablation table correctly: the reported row had removal of the access constraint *raising* the debt index. Because that table came from the unconducted study, its direction cannot be asserted either way, so the ablation, every sentence derived from it and P8's verdict have all been removed. The Conclusions now report the effect of the access constraint through the exact access arithmetic of §6.7: 622 h against 1,344 h of protected practice, a factor of 2.16. P8 survives only as an untested specified hypothesis in App. S2.7.

**W6.** Removed with the runtime table. §7.7 now says that no solver profile has been measured and that no claim depends on where Program (program) stops being tractable.

**W7 / Question 5.** The robustness claim has been narrowed to what Table 9 supports. The revised §6.8 reads:

> "the qualitative staffing result holds across the frontier and its magnitude does not. No lead-only roster delivers any credit and the budget is strictly positive, so some developmental staffing occurs at every feasible parameter value we swept; but across the eight feasible rows labeled 'no reversal' the constrained optimum retains the lead-only roster on between 1.3% and 46.1% of tasks, and the dual falls from 0.0454 to between 0.0005 and 0.0033."

This weakens what the earlier draft called its central claim, and we accept that. The narrower claim is the right one for two reasons. It is what the table shows. And it is still the claim the framework needs: a binding capability budget always puts developing practitioners on some of the work. The strength of that effect, and the price that drives it, depend on parameters that have not been measured. The reviewer's count of ten "no reversal" rows reflects the earlier table. The revised table has eight, and the range quoted above covers all of them, including the 1.3% row at φ = 0.60.

**W8.** The retirement-wave arithmetic was correct and valuable, but it was in the wrong section. It is now §6.9, "Two Parameter Shocks", with every quantity presented as exact arithmetic on the model; the full chain is in App. S10. The sentence comparing a "simulated dual" of 0.0451 with the analytic 0.0454 has been deleted, because under the revised scope there is no simulated dual.

**W9 / Question 6.** No appeals model existed, so the 0.942 figure has been removed. App. S2.3 says that no contestability throughput can be reported without a generative model of appeals. It names the four components such a model needs: arrival process, standing determination, upheld rate and resolution-time distribution.

**W10.** (a)–(h) are addressed under C5–C9, L5–L7. Item (d), the funding code, is still open (Section 4). On item (g): the corresponding-author block was in fact rendering. The Frontiers class prints it from `\corrAuthor` and `\corrEmail`, and the official template leaves `\correspondance{}` empty. Passing the values there would print the name twice. We confirmed this on the compiled PDF.

**Question 4 / audit items 1–2.** The equation now prints the unrounded tied-mode values to six decimals (0.308240 and 0.335452, difference 0.027212), so 0.027212 / 0.6 = 0.045353, which the text reports as 0.0454. At this exact value the two augmented scores are equal, because λ is *defined* as the value that equalizes them. The earlier mismatch (0.43532 vs 0.43538) came from substituting the rounded 0.0454. Both are now printed as 0.435229.

**Audit item 6.** The reviewer's arithmetic was right, and the problem went further. The figure's coordinates matched no stated parameter set. The revision adds Table 10, which states the replenishment parameters for every component of every strategy, and replots Figure 4 from Eq. (cadmodel). The prose values are now derived from that table. A bounded part of 17.98 (11.34 from skill formation) plus a residual slope of 1.45 per year gives C(20) = 46.89. Human-First, with slope 2.38, accrues less debt until t = 13.23. Every plotted coordinate is checked by the repository's audit script.

**Soundness concern 1 (scalarization).** Moved to §5.1, where the Weight Review Panel's legitimacy is claimed. There it now states that the panel's authority is bounded by the aggregation function rather than by its mandate. It adds that the hard constraints already act as ε-constraints, which reaches part of what a weighted sum alone cannot.

**Soundness concern 2 (online rule).** See M8: new §7.3.

**Soundness concern 3 (principal–agent exposure of φ_m).** Not resolved; see Section 4.

**Minor 1–7** are addressed under M5, L1–L4 and M10. On minor 4: the four proofs became prose in App. S8, so no `proof` environment remains. The real implicit dependency was `\newtheorem` on the class's `amsthm`, which is now loaded explicitly.

### Reviewer 2

We thank Reviewer 2 for the adversarial reading, and in particular for declining to allege fabrication while being precise about what the manuscript, as submitted, actually claimed.

**C1.** Resolved as described for R1 W1: the two passages 29 lines apart no longer coexist.

**C2 (self-selected comparison columns).** Partly addressed. §2.6 now states that the gaps are "gaps of integration more than of method: each construction we use has a precedent above, and what is missing is their joining at municipal scale". The nurse-rostering lineage is stated in App. S6.2 and summarized in §2.1. Table 1 itself is unchanged; see Section 4.

**C3, C4.** See R1 W3. The circularity charge is now stated by us in the main text, not answered by a baseline that does not exist.

**C5.** See R1 W8. The reviewer's description is right: the §9.5 numbers were the r_k = 0.14 row of the sensitivity table, recomputed. They are now presented as exactly that.

**§4 Novelty.** We agree with the reviewer's accounting: one new decision variable and four adapted constructions. The Introduction has been brought into line with §2. The area chair's view, which we share, is that the four-literature integration is itself the contribution. We have not claimed more than that.

**§5 Methodology.** The statistical plan is now explicitly a plan (App. S2.5). Since nothing has been executed, the post hoc threshold revisions to P3 and P9 are no longer reported against outcomes. App. S2.7 discloses them as part of the specification's history. The tautology concession for P2, P3, P5 and P9 stays in the main text (§7.2).

**§6 items 3–7.** The Z4 fallback figure, the appeals figure, the calibration snapshots, the emergency-logistics midpoint and the runtime claim all went with the Results section. On the snapshots: none exist. App. S4 now says so, names each series and its issuing body, and records that no reported result depends on them.

**§9 Missing components.** All are addressed, except the study (deliberately not conducted; Section 4), the ERA baseline and appeals model (specified, not implemented), the OSF identifier (which will exist when the study is run), and the funding code (open).

### Reviewer 3

We thank Reviewer 3 for checking our related work against the sources, and for the suggestions that most improved the paper.

**§3.1, §9.2: lead with the intake requirement.** Done (L8). It now appears in the Abstract's final sentence, as a named item in the Contributions list, as the closing substantive sentence of the Introduction, in §6.6, and in the Conclusions. The new Figure 3 plots time to competence against the automation share for two supervision levels. It marks the 1.2-year certification assumption and the 4.05-year operating point, and its right-hand axis gives the implied intake (4.1 → 14.0 posts). §6.6 now grounds the result in the training-economics literature (Acemoglu and Pischke; Wolter and Ryan).

**§7, §9.3: GCC and Saudi analysis.** This was the most useful single suggestion in the review, and we are grateful for it. New §5.4 treats the Saudi Civil Service Law's nationality rule and the Nitaqat bands as a second jurisdiction with a materially different structure from the EU analysis of §5.3. It maps them onto Eq. (access). What transfers is a policy-set target composition, publication, and a graded penalty equivalent to elastic slack. What does not transfer is the EU proportionality test. The subsection also takes up the reframing the reviewer anticipated: Nitaqat counts *posts*, whereas Eq. (access) counts *formation*. So where composition targets are already law, the constraint is an existing obligation made computable and contestable, rather than a new positive-action decision. `ILOESCWA2026` is now connected to Eq. (justtransition): the migrant contracted workforce is the population the payroll ceiling misses. The Personal Data Protection Law is named for the ledger.

**§5.1–2, §9.4: constrained MDPs and online matching.** New §7.3 states the bound that would be sought: O(√T) regret against the offline optimum together with O(√T) cumulative constraint violation. It cites the primal–dual and online-allocation literatures (Devanur and Hayes; Balseiro, Lu and Mirrokni; Mehta et al.; Altman; Paternain et al.). It checks the small-request condition at the worked instance (2.8 / 4,976.64 = 5.6 × 10⁻⁴). It then names four obstacles specific to this setting: duals updated at rebalance cadence rather than per decision, a covering rather than a packing budget, an endogenous credited share ψ_a, and a ratio constraint over a combinatorial action space. We do not prove the bound, and §7.3 says so.

**§5.3–4: apprenticeship economics and procurement.** Apprenticeship economics is now cited in support of the intake requirement (§6.6). Public-sector procurement is cited once, at the vendor-dependency gap (Mulligan and Bamberger). We could not verify a second candidate source and did not add an unverified one.

**§5, §9.5: `syed2026fedagent`.** Removed at both sites. The OECD citation carries the claim alone.

**§9.6: execute the elicitation protocol.** Not done in this revision; see Section 4.

### Area chair

The revision follows the route the meta-review recommends: a Hypothesis and Theory article whose evidence is the worked allocation and its sensitivity frontier, with the Results section removed rather than reworded. The dominant concerns are closed as follows. Concern 1 by removal (C1–C4). Concern 2 by correction (M1–M3, H5) and by removal (H1–H4). Concern 3 by removal and by concession (H6). Concern 4 by compression and the completed front matter (C5–C10, L5–L7), except the funding code. Concern 5, unmeasured inputs, is unchanged, and the manuscript continues to say so (§7.7).

---

## 4. What was not changed, and why

1. **The specified study was not conducted.** The theoretical contribution does not depend on it, and all three reviewers judged it unnecessary for a Hypothesis and Theory article. Running it as specified is a substantial engineering project, not a configuration change. The protocol remains fully specified in Appendix S2, so others can run it and audit the run against a fixed plan.

2. **The elicitation protocol (Appendix S5) was not executed.** We agree with Reviewer 3 and the area chair that one measured parameter set would strengthen the paper more than any other addition. It requires institutional ethics approval and rater recruitment, which take longer than this revision allowed. Every load-bearing input therefore remains an author estimate, and §7.7 says so first among the limitations.

3. **The online rule still has no proved regret or violation bound.** §7.3 states the target bound and explains why the standard results do not transfer directly. Proving it is a separate piece of work.

4. **Principal–agent exposure of φ_m (R1 soundness concern 3) is not resolved.** It is the most gameable quantity in the framework, and it drives the dilution factor behind the intake result. That result is therefore conditional on φ̄ and ω̄, as the reviewers' own claim audits classify it. The cross-validation response is still only partly specified. We kept the limitation as stated rather than claim a remedy we have not designed.

5. **Table 1 is unchanged.** Its columns are the dimensions a distributional claim requires, and the surrounding text now states that the differentiation is one of integration rather than method. A reader who rejects those columns as the right axes will still find the lineage stated plainly in §2 and App. S6.

6. **The ERA baseline and the appeals model are specified, not implemented.** This follows from item 1.

7. **The funding code is still missing at the time of writing.** It has been requested from Umm Al-Qura University and will be inserted in the Funding and Acknowledgment statements before submission.

8. **The repository's default branch has not yet been updated (N6).** The revised repository is complete and verified on its revision branch. It will be merged into the default branch before submission.
