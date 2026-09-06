# Training

**There is nothing to train, in the machine-learning sense, in this
repository — and this is faithful to the paper, not a gap in the
implementation.**

## What the paper says

Report §4.8, quoted directly: *"Nothing, in the ML sense, except the
optional surrogate of Paper §6.4."* CivicWorkOS is a weighted-sum objective
(Eq. 2, Eq. 15), a mixed-integer program (Eq. 16), and a Lagrangian
relaxation of that program (Eq. 17-19) — an optimization-and-governance
framework, not a learned model.

The manuscript's ONE training-adjacent mention (§6.4):

> "An optional learned surrogate for the AI Capability Broker's quality and
> trust predictions, if used, is a small model trained for 50 epochs at
> batch size 256 with a 10⁻³ initial learning rate on synthetic execution
> logs."

That is the entire specification. No architecture, layer count, input/output
dimensions, parameter count, optimizer, scheduler, loss function,
regularization, or validation strategy is given. **This repository does not
implement that surrogate**, because doing so would mean inventing an
architecture and presenting it as if it were the paper's — exactly the kind
of unlabeled invention this repository's engineering discipline (see
[assumptions.md](assumptions.md)) is built to avoid.

## What "training" means for this repository instead

The closest analogue to a training/calibration step is **parameter
elicitation**, and it is explicitly a governance act, not a model-fitting
procedure:

- `w1..w9` and `alpha..epsilon` (Eq. 2, Eq. 15 weights) are panel-set design
  defaults (`configs/weights/default.yaml`), not fitted from data. Paper
  §6.4: *"These are design defaults for the panel... to revise, not fitted
  estimates."*
- `learn_i` and hybrid `phi_m` require practitioner elicitation the paper
  names but does not design an instrument for (`docs/assumptions.md` A2-A3).
  The paper's own proposed path is a municipal pilot with human-subjects
  oversight (report Phase 11), not a training run.
- `N_k, r_k, h_k` come from municipal HR/pension/licensing records — real
  administrative data, not a training corpus.

## If you build the optional surrogate anyway

If a deployment decides to build the §6.4 surrogate, treat it as new work
outside this repository's paper-fidelity claim:

1. Implement it behind `civicworkos.market.contracts.MarketProtocol`, as a
   drop-in for (part of) `HeuristicMarket`'s AI Capability Broker estimates.
2. Document its architecture, training data, and validation in a new file
   (e.g. `docs/surrogate_model.md`) — do not fold it into this document,
   since it would not be reproducing anything the paper specifies.
3. Never claim the 50-epoch/batch-256/lr-1e-3 hyperparameters from §6.4
   validate your architecture choice; they are the paper's only stated
   numbers and say nothing about model shape.
