"""CivicWorkOS: a policy-aware multi-agent work-allocation framework.

Reference implementation of the formalism in Syed et al.,
"CivicWorkOS: A Capability-Preserving, Policy-Aware Multi-Agent Framework
for Human-AI-Robot Work Allocation and Distributional Accountability in
the AI City" (Frontiers, Hypothesis and Theory article).

The source manuscript reports no implementation, no dataset, and no
measured result (see its Data Availability Statement). This package is
an author reference implementation developed by Ali Akarma (co-author of
the manuscript) to make the formalism computable and testable. It provides
a verified reference implementation of the paper's mathematical framework.

See docs/paper_implementation_mapping.md for the equation-by-equation
correspondence and docs/assumptions.md for every point at which this
package had to invent something the paper left unspecified.
"""

__version__ = "0.1.0"

MODES = ("H", "A", "R", "H+A", "H+R", "A+R", "H+A+R")
"""The seven execution modes of Paper Eq. 1: M = {H, A, R, H+A, H+R, A+R, H+A+R}."""
