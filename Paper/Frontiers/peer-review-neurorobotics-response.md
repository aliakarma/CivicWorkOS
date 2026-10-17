# Response to the Simulated Review (Frontiers in Neurorobotics)

Companion to `peer-review-neurorobotics.md`. Each item of the Revision Roadmap, with what was changed and where. Section numbers refer to the revised `CivicWorkOS.tex`; "S" numbers to the Supplementary Material.

| # | Priority | Issue | Resolution | Location |
|---|---|---|---|---|
| 1 | Critical | Evaluated policy differs from specified policy (objective, duals) | New paragraph states the three testbed simplifications: a three-term instance of SCV (quality via $\hat p$, cost, expected incident loss) without the debt term, justified by Proposition 3; the budget enforced by the staged catch-up test instead of a dual; consequential decisions as a per-task flag. Everything else in Algorithm 1 is stated as implemented as specified. Also recorded as assumption A13. | §5.2; `docs/assumptions.md` A13 |
| 2 | High | Retention clock described as learned, implemented on the nominal curve | Text now says the interval is computed from the logged practice record on the nominal curve (auditable from records), and the learned estimate decides whether a practitioner is current. | §3.6 |
| 3 | High | Oversight gate uses a flag in the testbed | §3.7 states that an existing consequential classification replaces $crit_i\,auth_i$; §5.2 states the testbed's flag. | §3.7, §5.2 |
| 4 | High | Multimodal contribution not isolated | New exploratory ablation: CivicWorkOS learning from task outcomes only, all three scenarios, 30 paired seeds (Table 9A). Removing the channels degrades completion, overload, retention, takeover, and estimation error. Caveat that idealized channels make the effect an upper bound. | §6.2 "Exploratory Analyses", Table 9 |
| 5 | High | No robustness of simulated results | New exploratory sensitivity: $\tau^{ret}$ ×0.5 and ×2, machine prices ×3 (Table 9B). Retention advantage stays 0.35–0.46; completion penalty 1.0–1.8 points; cost index falls to 144.3 when machine prices triple. | §6.2, Table 9 |
| 6 | High | Partial circularity of H1/H8 | New paragraph separates what is true by construction (currency under a schedule designed for it) from what the execution adds (attainability under workload and safety limits with learned estimates; the emergent findings). | §7.1 |
| 7 | High | Learner accuracy not evidenced ("data-efficient") | Added read-only estimation-error metrics (proficiency MAE at end; machine-reliability MAE overall and in window); reporting seeds rerun and verified bit-identical on every previously reported metric. Unsupported "few outcomes per week" phrasing removed. | Tables 7, 9, S2–S4; §3.4, §7.4 |
| 8 | Medium | Proposition 1 proof step | Proof restated: fixed $\vartheta^\infty_w$ case, then the non-decreasing general case, showing sufficiency. | S2.1 |
| 9 | Medium | Development-seed disclosure | States that development outputs included policy comparisons, so the implementation was debugged with them in view, and what guards the reporting run. | S1.4 |
| 10 | Medium | Front matter, Data Availability | Word count filled from the journal-basis counter; table count corrected; DAS distinguishes tracked summaries from regenerable per-run records and names the exploratory script. | front matter, DAS |
| 11 | Medium | Learning cost, sensor idealization | $O(|a|+2)$ per update stated; idealized, unbiased channels stated with how a deployment would calibrate them. | §3.4 |
| 12 | Low | Table 1 subjectivity | Caption now says "as the authors read each work". | Table 1 |
| 13 | Low | Software versions | Python 3.10.11, NumPy 1.26.2, SciPy 1.11.4. | §5.5 |

## Integrity of the re-run

Adding the estimation-error metrics required re-running the 450 reporting runs. The metrics are read-only (they never enter a decision), and every metric reported before the change was compared run by run against the original records (`results/protocol_runs_original.jsonl`); all were identical. No hypothesis, threshold, seed, or model parameter changed, and `DEVIATIONS` in `configs/protocol/hypotheses.yaml` remains empty.
