# Analysis plan (to be fixed before any data are collected)

Lodge this file with the ethics application and on OSF before the first rater
is contacted. Every rule below is implemented in `elicitation/analyze.py` and
cannot be changed after seeing data without a dated, recorded deviation.

## 1. Design

Structural inspection only. At least 12 raters, four from each of three groups
(App. S4, `app:elicit-participants`): competent practitioners with five or more
years of practice, developing practitioners, and supervisors who sign off
progression. Two rounds on a Delphi pattern. Only round-two ratings are
analysed for the result; round one is reported for convergence.

## 2. Parameters, items and aggregation

| Parameter | Items rated | Point value |
|---|---|---|
| `learn_i` | 12 task specifications (`items.csv`), T01 is the article's worked task | mean over raters of the T01 rating / 10 |
| `phi_m` for `H+A`, `H+R`, `H+A+R` | each mode shown against each of the 12 tasks | mean over raters and tasks of the rating / 10, per mode |
| supervision ratio -> `psi_a1` | 4 task classes | `n/(n+1)` at the mean elicited ratio `n` |
| `h_raw_k` | 1 certification route | median over raters of the hours required *in practice* |

`phi_H = 1` by definition. The documented hours are collected as well and the
ratio practised/documented is reported (App. S4 calls the divergence
reportable); the model uses the practised figure.

`psi_a1 = n/(n+1)` is the article's own mapping: one trainee on an equal split
gives 1/2 (roster `a1`), two give 2/3 (`sec:shocks`).

## 3. Agreement

ICC(2,k), two-way random effects, absolute agreement, on round-two ratings,
raters as columns and the items of a parameter as rows. Targets with any
missing rating are dropped and counted. A target-bootstrap 95% interval is
reported (2,000 resamples, seed 20261008). **Threshold 0.75** (App. S4): a
parameter at or above it is reported as a point value; below it, as a range.

## 4. Intervals

Stratified rater bootstrap (resample raters within each group, 2,000
resamples, same seed): 95% percentile interval for every point value.

## 5. Re-solving the worked example

`elicitation/model.py`, the same linear programme as `sec:solving`, validated
against the article's baseline and the printed rows of `tab:sensitivity`.
Reported: (a) the estimated inputs, (b) all four parameters at their measured
values, (c) each parameter alone at its measured value, (d) for any parameter
reported as a range, the lower and upper end, and (e) the joint rater-bootstrap
distribution of the dual, cost of preservation, years to competence, intake
requirement and the share of resamples in which Proposition `prop:feasibility`
holds. Outcomes are reported whichever way they fall; an infeasible result is
a result.

## 6. A known limitation of the instrument, stated in advance

`h_raw_k` is a single quantity for a domain, so it has one target and ICC is
undefined for it. It is reported as the bootstrap interval of the rater median
and is always labelled a range. The supervision ratio has four targets, and
ICC over four classes is unstable when the classes truly do not differ; if
that happens the interval, not the point ICC, is the honest report. Both are
stated here so neither can be read as a finding about the raters.

## 7. What this study does not establish

It measures what a sample of practitioners in one domain judge these
quantities to be. It does not validate the framework, does not measure
outcomes, and does not generalise to other domains or municipalities. The
Limitations bullet "No measured inputs" is revised only for the four
parameters elicited; `Phi_k`, `N_k`, `r_k`, `eta_k`, `Theta_k`, `omega_bar`
and every non-capability term of `tab:worked-terms` remain author estimates.
