"""The manuscript's printed values, loaded from one definition.

Finding N2 of the revision programme (`Paper/Frontiers/REVISION-PROGRAMME.md`,
Phase 3) was that `scripts/verify_worked_example.py` and
`tests/smoke/test_worked_example.py` each carried their own copy of the worked
example's inputs, and both copies had drifted to an earlier draft's
parameterisation: they verified ``B_k = 2073.6`` against a manuscript that
computes ``B_k = 4976.64``, and they exited 0 while doing so. An artifact that
passes against numbers the article does not contain is worse than no artifact,
because it certifies the wrong paper.

The fix is structural rather than numerical. `Paper/Frontiers/audit_numbers.py`
is the single source of truth for every constant the manuscript states, and it
is the file that runs as a gate on the manuscript itself. This module loads it
by path and re-exports what the repository's checks need, so there is exactly
one place where a manuscript value is written down. When the article changes,
`audit_numbers.py` changes, and the script and the test suite follow without
being touched.

The division of labour between the two gates:

* `audit_numbers.py` asks whether the *manuscript* is internally consistent --
  whether each printed number follows from the inputs the article states.
* `scripts/verify_worked_example.py` and `tests/smoke/` ask whether *this code*
  reproduces those printed numbers -- whether `civicworkos.scoring`,
  `civicworkos.constraints` and `civicworkos.analytic` compute what the article
  publishes.

Both are needed: the first catches prose that misreports a correct table, which
is where five of the nine numerical defects the peer review found were living;
the second catches an implementation that has drifted from the specification.
"""

from __future__ import annotations

import importlib.util
import sys
from pathlib import Path
from types import ModuleType

_REPO_ROOT = Path(__file__).resolve().parent
AUDIT_NUMBERS_PATH = _REPO_ROOT / "Paper" / "Frontiers" / "audit_numbers.py"


def _load_audit_numbers() -> ModuleType:
    """Import `Paper/Frontiers/audit_numbers.py` by path.

    It lives beside the manuscript rather than inside the installed package,
    because it is an instrument for auditing the article and has no place in a
    library a third party would import. Loading it by path keeps that boundary
    while still giving the repository's checks one definition to read from.
    """
    if not AUDIT_NUMBERS_PATH.is_file():
        raise FileNotFoundError(
            f"cannot find the manuscript audit module at {AUDIT_NUMBERS_PATH}. "
            "It is the single source of truth for every value the article "
            "prints; without it no check in this repository can be trusted to "
            "be comparing against the submitted manuscript."
        )
    spec = importlib.util.spec_from_file_location(
        "civicworkos_audit_numbers", AUDIT_NUMBERS_PATH
    )
    if spec is None or spec.loader is None:  # pragma: no cover - defensive
        raise ImportError(f"could not build an import spec for {AUDIT_NUMBERS_PATH}")
    module = importlib.util.module_from_spec(spec)
    sys.modules[spec.name] = module
    spec.loader.exec_module(module)
    return module


_audit = _load_audit_numbers()

# --- Weights (eq:scv, eq:cad) ---------------------------------------------
W = _audit.W                       # objective weights w1..w9, keyed by term
WD = _audit.WD                     # debt weights alpha..epsilon

# --- The worked bridge-inspection instance (sec:worked) -------------------
MODES = _audit.MODES               # the eight staffed modes of tab:worked-terms
WORKED = _audit.WORKED             # task, domain and composition parameters
Mode = _audit.Mode                 # the staffed-mode dataclass

# --- The debt trajectory (eq:cadmodel, tab:cadparams, fig:cad-trend) ------
CAD_W = _audit.CAD_W               # the same debt weights, keyed by component
CAD_STRATEGIES = _audit.CAD_STRATEGIES   # (c_j, pi_j_inf, tau_j) per strategy
CAD_PRINTED = _audit.CAD_PRINTED   # the printed residual-slope and C(10) columns

__all__ = [
    "AUDIT_NUMBERS_PATH",
    "CAD_PRINTED",
    "CAD_STRATEGIES",
    "CAD_W",
    "MODES",
    "Mode",
    "W",
    "WD",
    "WORKED",
]
