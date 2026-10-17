# 📄 REVIEW REPORT

**Manuscript:** *CivicWorkOS: Capability-Preserving Adaptive Task Allocation Among Humans, AI Agents, and Robots in Municipal Services*
**Target:** Frontiers in Neurorobotics, Methods article, Research Topic "Data-driven Neurorobotics: Multimodal Learning, Adaptive Intelligence, and Reproducible Human–Robot Interaction"
**Mode / severity:** Full Review, Standard
**Materials read:** `CivicWorkOS.tex`, `CivicWorkOS_supplementary.tex`, `references.bib`, rendered PDF figures, `sim/protocol/*.py`, `configs/protocol/hypotheses.yaml`, `Paper/Frontiers/data/*.json`. Missing: no real human or robot data exist (by design); this bounds every empirical claim.

---

## 🔵 Reviewer #1 — Analytical Expert

**1. Classification and venue calibration.** Methods paper (method + reproducible protocol + synthetic validation) with a theoretical component (four propositions plus one new). For a Frontiers Methods article the bar is: method fully specified, validation replicable, limitations stated. The Research Topic explicitly invites reproducible evaluation protocols and software pipelines, which this manuscript supplies.

**2. Technical summary.** The paper models human proficiency as a stock that credited practice builds and gaps in human-led work erode (Eqs. 9–10), learns latent proficiency, machine reliability, task requirement, and workload response with Gaussian assumed-density filtering and Kalman updates (Eqs. 14–16), and constrains allocation by a supervised-practice budget, a recency (retention) constraint, and a workload ceiling (Eqs. 19–21), with uncertainty-gated oversight (Eq. 23) and readiness-constrained takeover (Eqs. 24–25). It reports an exact worked allocation and a 450-run synthetic reference execution with eight pre-specified hypotheses, four supported.

**3. Major strengths.**
1. Pre-specification with a disjoint development seed range and an empty-deviations log (§5.4, Suppl. S1.4) is unusually careful; failed hypotheses are reported in the main table (Table 8) rather than buried.
2. Proposition 1 gives a closed-form, checkable link between a decay model and a schedulable constraint; the worked-domain arithmetic (62.7 days vs 2.86 days) is correct and explains when retention binds.
3. Every simulation number is generated from JSON and cross-checked by an audit script (§5.5); common random numbers make the paired design valid.

**4. Major weaknesses.**
1. **Objective in the testbed differs from the objective in the method.** §3.5 defines the nine-term SCV with CAD, and Algorithm 1 scores with Eq. 27 including duals. The testbed (`engine.py`, `choose`) scores candidates by expected value `10(0.5+0.5 crit) p̂ − cost − 30·0.15·risk(1−p̂)`, with no CAD term and no duals; the budget enters only via the catch-up stage. §5.2 does not say this. A reader will assume the evaluated policy is Algorithm 1 as written.
2. **Retention constraint is described as using a learned interval, but is implemented on the nominal curve.** §3.6 states Eq. 21 is "evaluated with the learned $\bar e_w$"; `recency_need` uses the nominal learning curve and nominal $\tau^{ret}$, with the learned offset entering only the readiness test. Either the text or the code must change.
3. **Oversight gate parameterization mismatch.** Eq. 23 gates on $crit_i\,auth_i<q^{Z3}$; the testbed uses a per-task consequential flag (Table 3 "consequential share"). The supplementary table lists "flag" but the main text does not explain the substitution.
4. **Proof of Proposition 1 contains a false step.** Suppl. S2.1 opens "Between human-led tasks $\vartheta^\infty_w$ is constant"; non-human-led tasks still add credit (Eq. 9 credits $\ell_i\phi_m\omega_{a,w}$ on every task), so $\vartheta^\infty_w$ can rise. The conclusion survives (it only lengthens the interval, as the final sentence notes), but the proof should be stated for the non-decreasing case directly.

**5. Minor weaknesses.**
1. Front matter says "Number of tables: 9" (there are 8) and "Word count: WORDCOUNT" (placeholder).
2. Data Availability says the "outputs of the reference execution are openly available", but `runs.jsonl` is not tracked (`.gitignore` excludes `results/`); only summaries are in `Paper/Frontiers/data/`.
3. The per-task cost of the learning update is not stated (the Methods article should give it).
4. Table 1 ticks for prior work (e.g., Chen et al. 2018 "learned") are the authors' reading; say so.

**6. Consistency audit.**
- *Numerical*: all prose simulation numbers checked against `summary.json` — consistent (audit: 0 failures). Worked-example numbers consistent with Tables 4–6.
- *Figures/tables*: Figure 4 legend and axes correct; Table 7 matches JSON. Front-matter table count wrong (minor 1).
- *Cross-references*: no undefined references in either build.

**7. Technical soundness.** The ADF update (Eq. 15) is the standard probit moment-matching update; the predictive probability uses MacKay's moderation; both are correctly implemented (`estimation.py`). Concern 1 above is a specification-implementation gap, not an error in the mathematics.

**8. Experimental rigor.** 30 paired seeds, Wilcoxon + Holm over 12 tests, rank-biserial effect sizes, t-intervals: adequate. Weakness: a single parameterization. The cost and completion trade-offs depend on wage-to-machine price ratios and on $\tau^{ret}$, and no sensitivity of the simulated results to these is reported.

**9. Reproducibility.** Strong: one command, seeds, config dump, runtime stated (12.7 min, 12 cores). Python version and package versions should be stated in the article.

**10. Claim strength audit.**

| Claim | Classification | Location | Justification |
|---|---|---|---|
| Preservation keeps more practitioners current (27.5 vs 9.6) | Fully Supported | §6.2, Table 7–8 | H1 supported with large effect, CRN design |
| Learned workload ceiling prevents overload | Partially Supported | §6.2 Workload | Supported vs efficiency; attribution to the *physiological* channel is not isolated (the no-learning ablation removes outcome learning too) |
| Learning "detected the degraded machines" | Partially Supported | §7.3 | Inferred from takeover counts; detection latency not measured |
| Method is "data-efficient at a few outcomes per week" | Weakly Supported | §3.4, §7.4 | No learning-curve / estimation-error result is reported |
| Readiness rule improves takeover | Partially Supported | §6.2 | Better than efficiency (+0.078) but below static; H3 not supported |

**11. Fatal flaws.** None. Weaknesses 1–3 are disclosure/consistency issues fixable in text.

**12. Questions.** (a) Which objective does the evaluated CivicWorkOS policy maximize? (b) How much of the workload result is due to the physiological channel rather than outcome learning? (c) How do the cost and retention results move with $\tau^{ret}$ and with the wage/machine price ratio?

**13. Required improvements.** Critical: specify the testbed objective and its relation to Eq. 27 (W1). High: reconcile Eq. 21 text with implementation (W2); explain gate substitution (W3); fix Proposition 1 proof (W4); add channel ablation and parameter sensitivity. Medium: front matter, DAS, learning cost, Table 1 note. Low: software versions.

**14. Scores.** Novelty 6 · Technical Quality 7 · Experimental Rigor 7 · Clarity 7 · Reproducibility 9 · Significance 6 · **Overall 7**

**15. Recommendation: Minor Revision.** The method and protocol are sound and unusually transparent; the gaps are between what is specified and what is evaluated, and they are fixable with text and a modest additional analysis.

---

## 🔴 Reviewer #2 — Adversarial Critic

**1. Critical summary.** The paper sells a "multimodal, adaptive, neurorobotic" allocator, but every multimodal signal is a Gaussian draw around the true latent value, the "robots" and "AI agents" are scalar reliabilities, and the headline benefit (retention) follows almost by construction from a rule that forces human-led tasks.

**2. Acknowledged strengths.** Honest reporting of four failed hypotheses, including one (H7) that cuts against the method; open, deterministic pipeline; correct closed-form propositions.

**3. Core technical concerns.**
1. *Circularity of H1/H8.* The retention constraint (Eq. 21) schedules human-led tasks exactly so that the decay model (Eq. 10) does not cross $\vartheta^{comp}$; H1 then measures whether proficiency stayed above $\vartheta^{comp}$. The result tests the implementation, not a discovery. The manuscript should say so plainly.
2. *Multimodal claims rest on idealized sensors* (§3.4): unbiased, Gaussian, fixed variance. Real EEG/HRV workload indices are biased, drift, and are person-specific (the paper cites Dehais et al. 2020 for this). No result shows what the channels contribute beyond outcome learning.
3. *Cost.* CivicWorkOS costs 73% more per completed task (Table 7). The paper reframes this as "the price of preservation", but no analysis shows the result is not an artifact of chosen prices (machine 0.08–0.30 vs human 1.0).

**4. Novelty critique.** Components are established (BKT/IRT-style learner models, ADF, adaptive automation, takeover-time models, rostering constraints). Novelty is in integration and in making proficiency decay an allocation constraint. That is a legitimate Methods contribution, but Table 1's all-tick row for CivicWorkOS invites skepticism given that its multimodal component is simulated.

**5. Methodological critique.** The evaluated policy is not Algorithm 1 as specified (no duals, no SCV/CAD); the reader cannot tell which elements drive results.

**6. Experimental skepticism.** One synthetic configuration; parameters "set on development seeds to place the routine scenario at a plausible operating point" is not stated, but four implementation fixes were made after viewing development outputs (Suppl. S1.4), which means the design was not blind to policy comparisons. Say so.

**7. Consistency attacks.** Eq. 21 "learned $\bar e_w$" vs nominal implementation; Eq. 23 vs consequential flag; table count; "WORDCOUNT".

**8. Integrity concerns.** None of misconduct. The development-phase corrections are disclosed, which is commendable, but the disclosure should state that development runs included policy comparisons.

**9. Missing essential components.** Channel ablation; sensitivity of simulated results; estimation-accuracy evidence for the learner.

**10. Fatal weaknesses.** None fatal; the circularity framing and the idealized-sensor issue would draw a Major Revision from a strict reviewer if left unaddressed.

**11. Claim strength audit.**

| Claim | Classification | Location | Justification |
|---|---|---|---|
| "multimodal observations ... inform allocation" | Weakly Supported | Abstract, §3.4 | Channels are simulated; contribution not isolated |
| Retention result is evidence for the method | Partially Supported | §6.2 | Partly true by construction of Eq. 21 vs Eq. 10 |
| Cost of preservation is "1.73 times" | Fully Supported (for this testbed) | §8 | Correct, but price-dependent and should be bounded by sensitivity |

**12. Scores.** Novelty 5 · Technical Depth 6 · Experimental Validity 6 · Clarity 7 · Trustworthiness 8 · **Overall 6**

**13. Recommendation: Major Revision** — not for flaws, but because the paper's neurorobotics framing (multimodal learning) is the least evidenced part.

---

## 🟢 Reviewer #3 — Domain Specialist

**1. Domain context.** Sits between adaptive automation (Kaber & Endsley 2004), neuroergonomics (Dehais 2020; Aricò 2016), learner modeling (Corbett & Anderson 1994; Pelánek 2017), competence-aware autonomy (Basich 2020), and HRI task allocation (Gombolay 2015; Chen 2018). The long-horizon view of human proficiency is the distinctive contribution.

**2. Novelty vs SOTA.** Adaptive-automation work adapts to momentary state; this paper adapts to long-run proficiency and couples it to takeover readiness. I am not aware of an allocation method that does this with a released protocol. The "certified is not current" finding is useful to the HRI community.

**3. Academic impact.** Moderate-to-good: the protocol and testbed are reusable; the retention constraint is likely to be cited in human–automation teaming.

**4. Practical impact.** Plausible for municipalities with practice logs; physiological monitoring raises labor-relations and privacy barriers (Suppl. S4.3 addresses this well).

**5. Literature.** Good coverage. Could mention human-in-the-loop learning for shared autonomy and trust-calibrated takeover, but not required.

**6. Technical depth.** Appropriate for Frontiers Methods.

**7. Scalability and generalization.** Single synthetic city of 32 certified practitioners. The learning update is $O$(roster size) per task, which the paper should state; the city-wide MIP's scalability is honestly left open.

**8. Risks.** Over-reading the synthetic results; surveillance risk of physiological channels.

**9. Required improvements.** Show the value of multimodal channels (ablation); show robustness of headline effects to $\tau^{ret}$ and prices; make explicit which components of the method the testbed exercises.

**10. Claim strength audit.**

| Claim | Classification | Location | Justification |
|---|---|---|---|
| Certification is not readiness | Fully Supported (in model) | §7.2 | No-retention ablation isolates it |
| Learning trades completion for safety under disruption | Fully Supported | §6.2, §7.3 | Incidents 5.0 vs 31.0; completion 71.9 vs 93.5 |
| Relevance to neurorobotics | Partially Supported | §7.4 | Depends on the multimodal component, currently idealized |

**11. Scores.** Novelty 7 · Impact 7 · Technical Depth 7 · Relevance 6 · Completeness 7 · **Overall 7**

**12. Recommendation: Minor Revision.**

---

## 🟣 META-REVIEW (Area Chair)

**1. Final decision: Minor Revision** (one reviewer at Major).

**2. Consensus.** All agree the method is sound, transparently evaluated, and reproducible, and that the failed hypotheses are honestly reported. Disagreement is about how much the neurorobotics framing is earned: R2 sees the multimodal part as idealized; R1 and R3 see it as an acceptable Methods-level abstraction if its contribution is measured and its idealization stated.

**3. Dominant concerns.**
1. The evaluated policy must be specified exactly (objective, duals, retention clock, oversight gate) and reconciled with §§3–4.
2. The contribution of the multimodal channels must be isolated (ablation: learning from outcomes only).
3. Robustness of the headline effects to the retention time constant and to price ratios (exploratory sensitivity).
4. Partial circularity of the retention result must be stated.
5. Front-matter, proof, and DAS corrections.

**4. Venue fit.** Good fit for the Research Topic (reproducible protocol, adaptive learning, HRI analytics). Methods is the right article type.

**5. Publication readiness.** Publishable after the revisions above; no new real-world data is required for a Methods article, provided the idealization is stated.

**6. Reviewer calibration.** R1 is most technically justified; R2's circularity point is valid and cheap to address; none of the concerns is fatal.

**7. Revision feasibility.** Moderate. Current acceptance probability ≈ 55%; after revision ≈ 75%.

---

## 🔬 PUBLICATION RISK MATRIX

| Risk Area | Severity | Impact on Publication |
|---|---|---|
| Novelty | Medium | Integration novelty; must be framed as such |
| Experimental Validity | Medium | Single synthetic configuration; spec–implementation gaps |
| Reproducibility | Low | Exemplary pipeline |
| Statistical Rigor | Low | Paired nonparametric tests with Holm control |
| Writing Quality | Low | Clear; small front-matter errors |
| Overall Acceptance Risk | Medium | Driven by neurorobotics-relevance evidence |

---

## 📋 REVISION ROADMAP

| Priority | Issue | Location | Fix Description | Estimated Effort |
|---|---|---|---|---|
| Critical | Evaluated policy ≠ specified policy | §5.2, §4.2, Algorithm 1 | State the testbed objective (expected value as a three-term instance of SCV; capability terms via constraints, justified by Prop. 3); state that duals are replaced by the staged catch-up rule | hours |
| High | Retention clock: learned vs nominal | §3.6 Eq. 21 text | Say the interval is computed from the logged practice record on the nominal curve; learned estimates enter the readiness/current tests | hour |
| High | Oversight gate substitution | §3.7, §5.2 | Explain that the testbed draws a per-task consequential flag standing for $crit_i\,auth_i\ge q^{Z3}$ | hour |
| High | Multimodal contribution not isolated | §5.2, §6.2 | Add exploratory ablation: CivicWorkOS learning from outcomes only | ~1 day incl. runs |
| High | No robustness of simulated results | §6.2 | Exploratory sensitivity to $\tau^{ret}$ (×0.5, ×2) and to machine prices (×3) | ~1 day incl. runs |
| High | Partial circularity of H1/H8 | §7.1/§7.2 | State it explicitly and say what is *not* circular (formation, surge capacity, takeover, cost) | hour |
| Medium | Prop. 1 proof step | Suppl. S2.1 | Restate for non-decreasing $\vartheta^\infty_w$ | hour |
| Medium | Dev-seed disclosure | Suppl. S1.4, §5.4 | State development runs included policy comparisons | minutes |
| Medium | Front matter, DAS | front matter, DAS | Real word count; 8 tables; raw runs regenerate, summaries tracked | minutes |
| Medium | Learning cost, idealized sensors | §3.4 | State $O$(roster) per update; state sensor idealization | minutes |
| Low | Table 1 subjectivity | Table 1 caption | "authors' reading" | minutes |
| Low | Software versions | §5.5 | Python 3.10, NumPy, SciPy versions | minutes |

---

## FINAL VERDICT

In its current form the manuscript is a sound and unusually transparent Methods contribution whose main exposure is the gap between the method as specified and the policy as evaluated, and the thin evidence for its multimodal component. The most likely editorial outcome is **Minor Revision** (≈55% acceptance now).

After specifying the evaluated policy exactly, isolating the multimodal channels by ablation, adding an exploratory robustness analysis, and stating the partial circularity of the retention result, acceptance probability rises to about **75%**.
