"""Simulation testbed: Paper sec:protocol ("Evaluation Protocol and Pre-Registered
Predictions").

The paper's own status line for this section: "The protocol is a design
artifact; the platform it describes has not been built, and no result
from it appears anywhere in this paper." This package is a
reduced-scope reference implementation of that protocol, built to
exercise civicworkos's online rule and rebalancing solver end to end on
SYNTHETIC, CLEARLY-LABELED DEMO DATA -- never on the seven real
calibration sources the paper names as intended-but-unused
(Suppl. S4), and never presented as reproducing any paper result.

Scope reduction from Paper sec:protocol, documented (see
docs/assumptions.md A10): a time-stepped (monthly) loop rather than a
full priority-queue discrete-event engine; a short demo horizon
(months, not the paper's ten years) for smoke testing; and a subset of
the thirteen metrics computed directly from simulated data rather than
all thirteen. Nothing here should be cited as evidence about how
CivicWorkOS "performs" -- see the module-level docstrings in
sim.des, sim.strategies, and sim.stress for what each piece actually is.
"""
