# Sensor-realism grid: rationale and limits

Exploratory analysis added after internal pre-specification (submission phase P4). The
definitions, settings and decision rule are fixed in
`configs/protocol/exploratory_p4.yaml`; results are in the `sensor_realism`
block of `reproducibility/data/exploratory.json`.

## What the testbed's physiological channel is

Each simulated practitioner has a latent workload response `iota_w`
(`load_mult` in `sim/protocol/engine.py`), drawn as `max(0.6, 1 + 0.15 z)`, so
its between-person standard deviation is about 0.15. In the reference
execution, on 70% of worked days with demand above 0.5 h, the allocator
receives an unbiased reading `iota_w + e_t`, `e_t ~ N(0, 0.10^2)`, and
updates its belief with a scalar Kalman filter. Skill probes read true
proficiency with s.d. 0.08 on 30% of human-involved tasks.

The P4 sweep degrades this channel in three ways:

| Setting | Change | Meaning in testbed units |
|---|---|---|
| bias 0.05 / 0.10 / 0.15 | persistent per-person bias `b_i ~ N(0, sd^2)` added to every reading; the filter does not know `b_i` | one third, two thirds, and all of the between-person spread of `iota_w`. With unlimited readings the estimate converges to `iota_w + b_i`, so the estimate-truth correlation across people falls to about 0.95, 0.83 and 0.71 |
| noise 0.20 / 0.30 | per-reading s.d. doubled or tripled (the filter knows the new s.d.) | a single day's reading error exceeds the whole between-person spread |
| availability 0.35 | readings on half as many worked days | sensor not worn, or windows rejected for signal quality |
| combined | bias 0.10, noise 0.20, availability 0.35 on the physiological channel; probes with bias s.d. 0.05, noise 0.16, availability 0.15; telemetry noise 0.20, availability 0.25 | every multimodal channel degraded at once |

Biases come from their own generators, `np.random.default_rng([seed, 7919, 1])`
(physiological) and `[seed, 7919, 2]` (probes), and are drawn only when their
s.d. is above zero. At the defaults all 450 reference runs reproduce byte for
byte.

## What the published decoders report

- **Tufts fNIRS2MW** (Huang et al., 2021, NeurIPS Datasets and Benchmarks;
  benchmark results, Findings 1 to 3, pp. 7-8, and the accuracy-by-pool-size figure). 68 participants.
  Binary classification of 0-back against 2-back windows, balanced labels, so
  chance is 50%. Generic classifiers tested on never-seen subjects reach 66.9%
  mean accuracy with 16 training subjects and 72.2% with 64 (random forest).
  Generic classifiers outperform subject-specific and fine-tuned ones on
  average, but per-subject accuracy ranges from 30% to 100%, and 20 of 68
  subjects do at least 5 points better with a subject-specific model.
- **STEW** (Lim, Sourina and Wang, 2018, IEEE TNSRE 26(11):2106-2114; abstract,
  PubMed 30281467). 48 subjects, EEG during the SIMKAP multitasking test.
  Support vector regression on features selected by neighborhood component
  analysis gives 69% accuracy for three workload levels derived from a
  nine-point rating, Cohen's kappa 0.46. The abstract does not state whether
  evaluation was within or across subjects; the full text was not accessed, so
  no cross-subject claim is drawn from STEW.

## How the grid relates to those numbers

There is no defensible numerical mapping. The published accuracies are for
classifying task-induced workload *levels* (0-back against 2-back, or three
rating bands) from short recording windows. The testbed's channel instead
measures a person's *workload response multiplier*, a quantity no public
corpus labels. Converting an accuracy into a noise or bias s.d. on that
multiplier would need the separation of the classified levels in testbed units,
which the testbed does not define. The grid is therefore an **illustrative
stress test informed by these studies**, not an empirically calibrated
channel. The studies inform it qualitatively:

1. *Cross-subject decoding is modest.* Generic accuracy of 67-72% on a
   balanced binary task (fNIRS2MW) and 69% on three levels (STEW) are well
   short of the near-perfect reading the reference channel provides. Under an
   equal-variance Gaussian reading, 72.2% binary accuracy corresponds to a
   sensitivity of d' = 2 Phi^-1(0.722), about 1.18. That is a statement about
   the decoders' task, not about `iota_w`. The noise settings put a single
   reading's error above the whole between-person spread.
2. *Error is person-specific.* A per-subject accuracy range of 30% to 100%
   under one generic model implies that the decoder's error is largely
   systematic for a given person, which repeated readings do not average away.
   This motivates the persistent bias term. The bias grid spans one third of
   to all of the true between-person spread.
3. *Availability* (0.35) has no anchor in either study. It is an assumption
   about wear time and signal-quality rejection in field use.

These limits belong in any statement of the results: the sweep shows how the
learned workload ceiling degrades as the channel degrades, and where its
advantage over planning on the nominal model ends, in testbed units only.
