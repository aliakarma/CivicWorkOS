"""Re-solve the worked bridge-inspection allocation under alternative inputs.

This is the "re-run the worked example with the measured values beside the
estimated ones" step of Phase 9a. It is the same linear programme as
`sec:solving`, restated for arbitrary values of the four judgment parameters
(`learn_i`, `phi_m`, the supervision ratio behind `psi_a`, `h_raw_k`) plus the
three structural parameters the sensitivity sweep varies (`r_k`, `eta_k`).

Nothing is restated here. Every baseline constant is read from
`manuscript_values`, which re-exports `Paper/Frontiers/audit_numbers.py`, so
this module cannot drift from the manuscript the way finding N2 did. Its
correctness is established by `tests/test_model.py`, which requires it to
reproduce, from the model alone, the baseline (lambda_k = 0.045353, 4.34%,
tau_k = 4.05, n_hat_k = 14.0) and the printed rows of the one-at-a-time
sensitivity table `tab:sensitivity`.

The programme, with x_m the share of tasks on admissible staffed mode m:

    max  sum_m x_m SCV_m
    s.t. sum_m x_m = 1,   sum_m x_m phi_m psi_a >= B_k / Phi_k,   x >= 0

where a mode is admissible iff its safety term meets the floor S_min =
risk * crit. The capability price is lambda_k = -(d mean-SCV / d required
share) / ell_i, the dual of the budget row expressed per qualified-practice
hour. The LP relaxation is solved; integrality moves the objective by ~6e-6
in the baseline (`sec:solving`) and is not modelled.
"""

from __future__ import annotations

import dataclasses
import sys
from dataclasses import dataclass
from pathlib import Path

import numpy as np
from scipy.optimize import linprog

_ROOT = Path(__file__).resolve().parents[1]
if str(_ROOT) not in sys.path:
    sys.path.insert(0, str(_ROOT))

from manuscript_values import MODES, WORKED  # noqa: E402

EXEC_MODES = ("H", "H+A", "H+R", "H+A+R")


def exec_mode(name: str) -> str:
    """'H+A+R/a1' -> 'H+A+R'."""
    return name.split("/")[0]


def roster(name: str) -> str:
    return name.split("/")[1]


def psi_from_ratio(n_developing: float) -> float:
    """Developmental eligibility of a lead plus n developing practitioners.

    The article's roster a1 is "a competent lead with one developing inspector
    on an equal split", psi = 1/2, and two trainees per lead give 2/3 (the
    psi = 0.67 row of `tab:sensitivity` and the `sec:shocks` arithmetic). Both
    are n / (n + 1), so a supervision ratio elicited as "developing
    practitioners per competent lead" maps to psi by that expression.
    """
    if n_developing < 0:
        raise ValueError("supervision ratio cannot be negative")
    return n_developing / (n_developing + 1.0)


@dataclass(frozen=True)
class Inputs:
    """Overrides to the manuscript baseline. None keeps the printed value."""
    learn: float | None = None
    h_raw: float | None = None
    r_k: float | None = None
    eta_k: float | None = None
    phi: tuple[tuple[str, float], ...] = ()      # (('H+A+R', 0.6), ...)
    psi_a1: float | None = None

    def phi_dict(self) -> dict[str, float]:
        return dict(self.phi)

    @staticmethod
    def make(learn=None, h_raw=None, r_k=None, eta_k=None, phi=None, psi_a1=None):
        return Inputs(learn, h_raw, r_k, eta_k,
                      tuple(sorted((phi or {}).items())), psi_a1)


@dataclass(frozen=True)
class Result:
    feasible: bool
    B_k: float
    required_share: float          # B_k / Phi_k
    zeta_bar: float                # largest credited share among admissible modes
    lam: float | None              # capability price per hour; None if infeasible
    cost_of_preservation: float | None
    mix: dict[str, float]          # staffed mode -> share of tasks
    lead_only_share: float | None  # share on a0 rosters at the optimum
    phi_bar: float | None
    tau_k: float | None            # years to competence
    n_hat_k: float | None          # intake requirement
    certification_years: float     # h_raw / Theta
    h_k: float


def _modes(inp: Inputs):
    phi = inp.phi_dict()
    unknown = set(phi) - set(EXEC_MODES)
    if unknown:
        raise ValueError(f"unknown execution mode(s): {sorted(unknown)}")
    if "H" in phi:
        raise ValueError("phi_H is 1 by definition (the human forms the "
                         "determination) and is not elicited")
    out = {}
    for name, m in MODES.items():
        repl = {}
        if exec_mode(name) in phi:
            repl["phi"] = phi[exec_mode(name)]
        if roster(name) == "a1" and inp.psi_a1 is not None:
            repl["psi"] = inp.psi_a1
        out[name] = dataclasses.replace(m, **repl) if repl else m
    return out


def solve(inp: Inputs = Inputs()) -> Result:
    w = WORKED
    learn = w["learn"] if inp.learn is None else inp.learn
    h_raw = w["h_raw_k"] if inp.h_raw is None else inp.h_raw
    r_k = w["r_k"] if inp.r_k is None else inp.r_k
    eta = w["eta_k"] if inp.eta_k is None else inp.eta_k
    if not (0.0 < learn <= 1.0):
        raise ValueError("learn_i must lie in (0, 1]")

    ell = learn * w["d_i"]
    Phi = w["n_k"] * ell
    h_k = learn * h_raw
    B_k = max(w["B_min"], eta * w["N_k"] * r_k * h_k)
    req = B_k / Phi

    modes = _modes(inp)
    admissible = {n: m for n, m in modes.items() if m.S >= w["S_min"] - 1e-12}
    names = list(admissible)
    scv = np.array([admissible[n].scv for n in names])
    cred = np.array([admissible[n].credited for n in names])
    zeta_bar = float(cred.max())
    cert_years = h_raw / w["Theta_k"]

    if req > zeta_bar + 1e-12:
        return Result(False, B_k, req, zeta_bar, None, None, {}, None, None,
                      None, None, cert_years, h_k)

    n = len(names)
    res = linprog(c=-scv, A_ub=[-cred], b_ub=[-req],
                  A_eq=[np.ones(n)], b_eq=[1.0],
                  bounds=[(0, None)] * n, method="highs")
    if not res.success:  # pragma: no cover - guarded by the feasibility test
        raise RuntimeError(f"LP failed: {res.message}")

    x = np.where(res.x < 1e-12, 0.0, res.x)
    mean_scv = float(scv @ x)
    unc = float(scv.max())
    # d(mean SCV)/d(required share) <= 0; |.| = lambda * ell.
    marg = float(res.ineqlin.marginals[0])
    lam = max(0.0, -marg / ell) if abs(marg) > 1e-12 else 0.0
    mix = {nm: float(xi) for nm, xi in zip(names, x) if xi > 1e-9}
    lead_only = sum(v for k, v in mix.items() if roster(k) == "a0")
    phi_bar = float(sum(admissible[k].phi * v for k, v in mix.items()))
    tau = cert_years / (phi_bar * w["omega_bar"])
    n_hat = eta * w["N_k"] * r_k * tau
    return Result(True, B_k, req, zeta_bar, lam, (unc - mean_scv) / unc, mix,
                  lead_only, phi_bar, tau, n_hat, cert_years, h_k)
