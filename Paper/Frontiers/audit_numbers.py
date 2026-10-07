#!/usr/bin/env python3
"""audit_numbers.py -- arithmetic gate for the CivicWorkOS manuscript.

Recomputes, from the manuscript's own stated inputs, every number the article
prints that is derivable by exact arithmetic, and compares each against the
printed value.  Written for the Frontiers Hypothesis-and-Theory revision
(Paper/Frontiers/REVISION-PROGRAMME.md, Phase 0).

Why this exists.  Of the nine numerical defects the peer review identified,
five were in prose that misreported a correct table.  No build check catches
that class of error; only recomputation does.  Run this at the end of every
working session:

    python audit_numbers.py            # full report
    python audit_numbers.py --quiet    # failures only
    python audit_numbers.py --known    # include defects awaiting Phase 2

Exit status is 0 when every non-known-defect check passes.

The single source of truth for the shared constants is WORKED (below).
scripts/verify_worked_example.py imports from this module rather than keeping
its own copy -- divergence between two copies of the same constants is exactly
how finding N2 arose.
"""

from __future__ import annotations

import argparse
import math
import sys
from dataclasses import dataclass, field

# --------------------------------------------------------------------------
# Manuscript inputs.  Every value below is quoted verbatim from CivicWorkOS.tex.
# --------------------------------------------------------------------------

# Objective weights, Sec. "Implementation Configuration" / eq:scv.
# Order: Q, S, P, Eq_srv, Tr, Cost, En, Pr, CAD.  The last four are penalties.
W = {"Q": 0.15, "S": 0.18, "P": 0.14, "Eq": 0.10, "Tr": 0.05,
     "Cost": 0.08, "En": 0.03, "Pr": 0.05, "CAD": 0.22}

# Debt weights (alpha, beta, gamma, delta, epsilon), eq:cad.
WD = {"skill": 0.28, "fall": 0.22, "acct": 0.18, "dep": 0.12, "trans": 0.20}

PENALTIES = ("Cost", "En", "Pr")


@dataclass(frozen=True)
class Mode:
    """One staffed mode: an execution mode paired with a roster."""
    name: str
    Q: float
    S: float
    P: float
    Eq: float
    Tr: float
    Cost: float
    En: float
    Pr: float
    phi: float          # human share phi_m
    psi: float          # developmental eligibility psi_a
    D_fall: float
    D_acct: float
    D_dep: float
    D_trans: float

    @property
    def credited(self) -> float:
        """phi_m * psi_a -- the credited developmental share."""
        return self.phi * self.psi

    @property
    def D_skill(self) -> float:
        return 1.0 - self.credited

    @property
    def cad(self) -> float:
        """Civic Automation Debt, eq:cad."""
        return (WD["skill"] * self.D_skill + WD["fall"] * self.D_fall
                + WD["acct"] * self.D_acct + WD["dep"] * self.D_dep
                + WD["trans"] * self.D_trans)

    @property
    def flows(self) -> float:
        """Weighted flow terms only -- the eight non-CAD terms of eq:scv."""
        return (W["Q"] * self.Q + W["S"] * self.S + W["P"] * self.P
                + W["Eq"] * self.Eq + W["Tr"] * self.Tr
                - W["Cost"] * self.Cost - W["En"] * self.En
                - W["Pr"] * self.Pr)

    @property
    def scv(self) -> float:
        """Sustainable Civic Value, eq:scv."""
        return self.flows - W["CAD"] * self.cad

    def augmented(self, lam: float, ell: float) -> float:
        """Capability-augmented objective, eq:aug."""
        return self.scv + lam * ell * self.credited


# Table tab:worked-terms, all eight staffed modes.
MODES = {m.name: m for m in [
    Mode("H/a0",       0.72, 0.55, 0.40, 0.70, 0.80, 0.85, 0.20, 0.10,
         1.00, 0.00, 0.00, 0.00, 0.00, 0.00),
    Mode("H/a1",       0.69, 0.53, 0.35, 0.70, 0.78, 0.95, 0.20, 0.10,
         1.00, 0.50, 0.00, 0.00, 0.00, 0.00),
    Mode("H+A/a0",     0.86, 0.60, 0.62, 0.72, 0.74, 0.62, 0.28, 0.25,
         0.75, 0.00, 0.15, 0.07, 0.30, 0.10),
    Mode("H+A/a1",     0.83, 0.58, 0.57, 0.72, 0.72, 0.72, 0.28, 0.25,
         0.75, 0.50, 0.15, 0.07, 0.30, 0.10),
    Mode("H+R/a0",     0.80, 0.88, 0.70, 0.70, 0.72, 0.58, 0.55, 0.30,
         0.70, 0.00, 0.25, 0.05, 0.35, 0.20),
    Mode("H+R/a1",     0.77, 0.86, 0.65, 0.70, 0.70, 0.68, 0.55, 0.30,
         0.70, 0.50, 0.25, 0.05, 0.35, 0.20),
    Mode("H+A+R/a0",   0.91, 0.90, 0.88, 0.74, 0.68, 0.50, 0.60, 0.38,
         0.55, 0.00, 0.35, 0.13, 0.50, 0.30),
    Mode("H+A+R/a1",   0.88, 0.88, 0.83, 0.74, 0.66, 0.60, 0.60, 0.38,
         0.55, 0.50, 0.35, 0.13, 0.50, 0.30),
]}

# Domain and task parameters, Sec. sec:workedsetup and sec:binds.
WORKED = dict(
    # Task T_i: one cycle of fatigue-crack assessment on a steel girder span.
    cog=0.80, phy=0.60, emp=0.10, risk=0.70, auth=0.90,
    priv=0.20, urg=0.40, learn=0.80, crit=0.90,
    d_i=10.0,            # task duration, clock hours
    ell_i=8.0,           # developmental content, eq:ell = learn * d_i
    S_min=0.63,          # safety floor = risk * crit
    # Domain k: structural inspection of bridges and major structures.
    n_k=2100,            # inspection events per year
    Phi_k=16800.0,       # qualified-practice hours per year = n_k * ell_i
    N_k=24,              # competent practitioners
    r_k=0.12,            # annual attrition
    eta_k=1.2,           # replacement factor
    B_min=2000.0,        # floor on the budget
    h_raw_k=1800.0,      # supervised clock hours to certification
    h_k=1440.0,          # qualified-practice hours, eq:hconv = learn * h_raw
    zeta_bar=0.35,       # roster-guard cap = phi_{H+R} * 0.5
    Theta_k=1500.0,      # domain clock hours per trainee-year
    omega_bar=0.5,       # human-work share of the developing practitioner
    # Composition figures, Sec. sec:whoworked.
    incumbent_women=0.125,
    pool_women=0.32,
    epsilon_k=0.05,
    # Active modes at the constrained optimum.
    mode_lo="H+R/a1",    # higher credited share, lower SCV
    mode_hi="H+A+R/a1",  # lower credited share, higher SCV
    mode_unc="H+A+R/a0", # unconstrained winner
    w9_default=0.22,
)

TOL = 1e-4   # agreement tolerance for printed values


# --------------------------------------------------------------------------
# Check harness
# --------------------------------------------------------------------------

@dataclass
class Check:
    label: str
    printed: float | None
    computed: float
    tol: float = TOL
    site: str = ""
    known_defect: str = ""   # non-empty => expected to fail, phase that fixes it
    note: str = ""

    @property
    def delta(self) -> float:
        if self.printed is None:
            return 0.0
        return abs(self.computed - self.printed)

    @property
    def passed(self) -> bool:
        if self.printed is None:
            return True
        return self.delta <= self.tol


@dataclass
class Section:
    title: str
    checks: list = field(default_factory=list)

    def add(self, *a, **kw) -> None:
        self.checks.append(Check(*a, **kw))


def build() -> list:
    """Recompute everything.  Returns the list of sections."""
    w = WORKED
    ell = w["ell_i"]
    lo, hi, unc = MODES[w["mode_lo"]], MODES[w["mode_hi"]], MODES[w["mode_unc"]]
    out = []

    # -- Weight vectors -------------------------------------------------
    s = Section("Weight vectors (sec:config, eq:scv, eq:cad)")
    s.add("objective weights sum to one", 1.000, sum(W.values()), tol=1e-9,
          site="l.1250")
    s.add("debt weights sum to one", 1.000, sum(WD.values()), tol=1e-9,
          site="l.1250")
    s.add("deferred block total w9", 0.220, W["CAD"], tol=1e-9,
          site="tab:params, l.1307")
    out.append(s)

    # -- Task and domain primitives -------------------------------------
    s = Section("Task profile and domain scale (sec:workedsetup)")
    s.add("ell_i = learn_i * d_i", 8.0, w["learn"] * w["d_i"],
          site="eq:ell, l.957")
    s.add("S_min = risk * crit", 0.63, w["risk"] * w["crit"],
          site="l.961")
    s.add("Phi_k = n_k * ell_i", 16800.0, w["n_k"] * ell, tol=1e-6,
          site="l.967")
    s.add("h_k = learn * h_raw", 1440.0, w["learn"] * w["h_raw_k"], tol=1e-6,
          site="eq:hconv, l.1019")
    s.add("zeta_bar = phi_{H+R} * psi_{a1}", 0.35,
          MODES["H+R/a1"].phi * MODES["H+R/a1"].psi, site="l.965")
    out.append(s)

    # -- CAD per staffed mode ------------------------------------------
    printed_cad = {"H/a0": 0.2800, "H/a1": 0.1400, "H+A/a0": 0.3816,
                   "H+A/a1": 0.2766, "H+R/a0": 0.4260, "H+R/a1": 0.3280,
                   "H+A+R/a0": 0.5004, "H+A+R/a1": 0.4234}
    s = Section("CAD by staffed mode (tab:worked-terms, eq:cad)")
    for name, printed in printed_cad.items():
        s.add(f"CAD {name}", printed, MODES[name].cad, site="tab:worked-terms")
    out.append(s)

    # -- credited share and D_skill ------------------------------------
    printed_credit = {"H/a0": 0.000, "H/a1": 0.500, "H+A/a0": 0.000,
                      "H+A/a1": 0.375, "H+R/a0": 0.000, "H+R/a1": 0.350,
                      "H+A+R/a0": 0.000, "H+A+R/a1": 0.275}
    s = Section("Credited developmental share phi_m psi_a (tab:worked-terms)")
    for name, printed in printed_credit.items():
        s.add(f"phi*psi {name}", printed, MODES[name].credited,
              site="tab:worked-terms")
    out.append(s)

    # -- SCV per staffed mode ------------------------------------------
    printed_scv = {"H/a0": 0.2324, "H/a1": 0.2391, "H+A/a0": 0.2783,
                   "H+A/a1": 0.2773, "H+R/a0": 0.3108, "H+R/a1": 0.3082,
                   "H+A+R/a0": 0.3426, "H+A+R/a1": 0.3355}
    s = Section("SCV by staffed mode (tab:worked-terms, eq:scv)")
    for name, printed in printed_scv.items():
        s.add(f"SCV {name}", printed, MODES[name].scv, site="tab:worked-terms")
    s.add("unconstrained SCV (H+A+R/a0)", 0.34261, unc.scv, tol=1e-5,
          site="l.1012, Abstract", note="to five decimals")
    out.append(s)

    # -- the w9 flip threshold -----------------------------------------
    s = Section("Deferred-weight flip threshold (eq:w9worked, prop:price)")
    d_flow = MODES["H+A+R/a0"].flows - MODES["H+A+R/a1"].flows
    d_cad = MODES["H+A+R/a0"].cad - MODES["H+A+R/a1"].cad
    s.add("roster gap at w9 = 0", 0.0241, d_flow, site="l.1013")
    s.add("w9* flip threshold", 0.313, d_flow / d_cad, tol=5e-4,
          site="eq:w9worked")
    gap22 = d_flow - w["w9_default"] * d_cad
    s.add("roster gap at w9 = 0.22", 0.0072, gap22, site="l.1013")
    s.add("fraction of gap the price closes", 0.70,
          (d_flow - gap22) / d_flow, tol=5e-3, site="l.1013")
    out.append(s)

    # -- the capability budget ------------------------------------------
    s = Section("The capability budget binds (sec:binds)")
    B_k = max(w["B_min"], w["eta_k"] * w["N_k"] * w["r_k"] * w["h_k"])
    s.add("B_k", 4976.64, B_k, tol=1e-6, site="eq:bkworked")
    req = B_k / w["Phi_k"]
    s.add("required mean credited share", 0.2962, req, site="l.1026")
    s.add("Phi_k * zeta_bar", 5880.0, w["Phi_k"] * w["zeta_bar"], tol=1e-6,
          site="l.1026, prop:feasibility")
    s.add("feasibility margin B_k / (Phi zeta)", None,
          B_k / (w["Phi_k"] * w["zeta_bar"]), site="prop:feasibility",
          note="0.846 -> 15% headroom, l.1194")
    out.append(s)

    # -- the two-mode mix ----------------------------------------------
    s = Section("The constrained optimum (tab:worked-mix, sec:solving)")
    # x = share on the higher-credit mode such that the mean hits req exactly
    x = (req - hi.credited) / (lo.credited - hi.credited)
    s.add("share on H+R/a1", 0.2830, x, site="tab:worked-mix, l.1058")
    s.add("share on H+A+R/a1", 0.7170, 1.0 - x, site="tab:worked-mix")
    mean_scv = x * lo.scv + (1 - x) * hi.scv
    s.add("constrained mean SCV (LP)", 0.327750, mean_scv, tol=1e-6,
          site="tab:worked-mix, l.1070")
    s.add("mean credited share at optimum", 0.2962,
          x * lo.credited + (1 - x) * hi.credited, site="tab:worked-mix")

    # Integrality.
    n_lo_frac = x * w["n_k"]
    s.add("fractional task count in H+R/a1", 594.3, n_lo_frac, tol=0.05,
          site="l.1070", known_defect="Phase 2",
          note="exact value is 594.40; manuscript prints 594.3")
    hours = lambda n: n * ell * lo.credited + (w["n_k"] - n) * ell * hi.credited
    s.add("hours delivered by 594 tasks", 4976.40, hours(594), tol=1e-6,
          site="l.1070")
    s.add("hours delivered by 595 tasks", 4977.00, hours(595), tol=1e-6,
          site="l.1070")
    s.add("budget shortfall at 594 tasks", 0.24, B_k - hours(594), tol=1e-6,
          site="l.1070")
    x595 = 595 / w["n_k"]
    mean_595 = x595 * lo.scv + (1 - x595) * hi.scv
    s.add("integer-optimum mean SCV", 0.327742, mean_595, tol=1e-6,
          site="l.1070", known_defect="Phase 2",
          note="exact value is 0.3277436")
    s.add("integrality gap", 7.8e-6, mean_scv - mean_595, tol=1e-7,
          site="l.1070", known_defect="Phase 2",
          note="exact gap is 6.09e-6")
    out.append(s)

    # -- the dual ------------------------------------------------------
    s = Section("The capability price (eq:lambdaworked)")
    # The tie between the two active staffed modes fixes lambda_k:
    #   SCV_lo + lambda*ell*zeta_lo = SCV_hi + lambda*ell*zeta_hi
    num = hi.scv - lo.scv
    den = ell * (lo.credited - hi.credited)
    lam = num / den
    s.add("SCV difference (numerator)", 0.0273, num, tol=5e-5,
          site="eq:lambdaworked", known_defect="Phase 2 (M1)",
          note="exact value is 0.027212; the equation displays it rounded to "
               "0.0273, and 0.0273/0.6 = 0.04550 does not reproduce the "
               "0.0454 the same equation reports")
    s.add("denominator ell*(zeta_lo - zeta_hi)", 0.6, den, tol=1e-9,
          site="eq:lambdaworked")
    s.add("lambda_k from exact SCVs", 0.0454, lam, tol=5e-5,
          site="eq:lambdaworked, Abstract, l.1705")
    s.add("lambda_k from the PRINTED numerator 0.0273", 0.0454, 0.0273 / 0.6,
          tol=5e-5, site="eq:lambdaworked", known_defect="Phase 2 (M1)",
          note="0.0273/0.6 = 0.04550; the displayed intermediate is rounded, "
               "so the equation as printed does not reproduce its own result")

    # Augmented values, eq:augworked.
    s.add("augmented SCV H+R/a1", 0.4352, lo.augmented(lam, ell), tol=5e-5,
          site="eq:augworked")
    s.add("augmented SCV H+A+R/a1", 0.4352, hi.augmented(lam, ell), tol=5e-5,
          site="eq:augworked")
    s.add("tie residual between the two active modes", 0.0,
          abs(lo.augmented(lam, ell) - hi.augmented(lam, ell)), tol=1e-12,
          site="eq:augworked")
    s.add("augmented SCV H+A+R/a0", 0.3426,
          MODES["H+A+R/a0"].augmented(lam, ell), site="eq:augworked")
    s.add("augmented SCV H+R/a0", 0.3108,
          MODES["H+R/a0"].augmented(lam, ell), site="eq:augworked")
    out.append(s)

    # -- the cost of preservation --------------------------------------
    s = Section("What preservation costs (sec:costs)")
    unc_year = unc.scv * w["n_k"]
    con_year = mean_scv * w["n_k"]
    s.add("unconstrained annual objective", 719.5, unc_year, tol=0.05,
          site="l.1075")
    s.add("constrained annual objective", 688.3, con_year, tol=0.05,
          site="l.1075")
    s.add("annual cost of the constraint", 31.2, unc_year - con_year, tol=0.05,
          site="l.1075")
    s.add("relative cost of preservation", 0.0434,
          (unc_year - con_year) / unc_year, tol=5e-5, site="l.1075, Abstract")
    s.add("average price per practice hour", 0.0063,
          (unc_year - con_year) / B_k, tol=5e-5, site="l.1075")
    s.add("average price below marginal (convexity)", None,
          lam - (unc_year - con_year) / B_k, site="l.1075",
          note="must be positive")

    # Term-by-term decomposition, tab:worked-decomp.
    printed_decomp = {
        "Q": (0.9100, 0.8489, -0.0672), "S": (0.9000, 0.8743, -0.0285),
        "P": (0.8800, 0.7791, -0.1147), "Eq": (0.7400, 0.7287, -0.0153),
        "Tr": (0.6800, 0.6713, -0.0128), "Cost": (0.5000, 0.6226, +0.2453),
        "En": (0.6000, 0.5858, -0.0236), "Pr": (0.3800, 0.3574, -0.0596),
    }
    for term, (p_unc, p_con, p_chg) in printed_decomp.items():
        c_unc = getattr(unc, term)
        c_con = x * getattr(lo, term) + (1 - x) * getattr(hi, term)
        s.add(f"decomp {term} unconstrained", p_unc, c_unc,
              site="tab:worked-decomp")
        s.add(f"decomp {term} constrained", p_con, c_con,
              site="tab:worked-decomp")
        s.add(f"decomp {term} change", p_chg, (c_con - c_unc) / c_unc,
              tol=5e-4, site="tab:worked-decomp")
    cad_con = x * lo.cad + (1 - x) * hi.cad
    s.add("decomp CAD unconstrained", 0.5004, unc.cad, site="tab:worked-decomp")
    s.add("decomp CAD constrained", 0.3964, cad_con, site="tab:worked-decomp")
    s.add("decomp CAD change", -0.2078, (cad_con - unc.cad) / unc.cad,
          tol=5e-4, site="tab:worked-decomp")
    s.add("decomp SCV change", -0.0434, (mean_scv - unc.scv) / unc.scv,
          tol=5e-4, site="tab:worked-decomp")
    out.append(s)

    # -- replenishment -------------------------------------------------
    s = Section("Replenishment and net formation (sec:costs)")
    s.add("competent-equivalents formed per year", 3.456, B_k / w["h_k"],
          tol=1e-6, site="l.1103, Abstract")
    s.add("annual attrition in practitioners", 2.88, w["N_k"] * w["r_k"],
          tol=1e-9, site="l.1103, Abstract")
    s.add("net gain in practitioners per year", 0.576,
          B_k / w["h_k"] - w["N_k"] * w["r_k"], tol=1e-6, site="l.1103")
    s.add("identity B_k/h_k = eta N r", 0.0,
          abs(B_k / w["h_k"] - w["eta_k"] * w["N_k"] * w["r_k"]), tol=1e-9,
          site="l.1103")
    out.append(s)

    # -- the intake requirement ----------------------------------------
    s = Section("Pipeline arithmetic and the intake requirement (sec:pipeline)")
    trainee_hours = w["n_k"] * w["d_i"]
    s.add("trainee clock hours consumed per year", 21000.0, trainee_hours,
          tol=1e-6, site="l.1108")
    s.add("qualified-practice hours accrued per clock hour", 0.237,
          B_k / trainee_hours, tol=5e-4, site="l.1108")
    phi_bar = x * lo.phi + (1 - x) * hi.phi
    s.add("phi_bar_k at the optimum", 0.5925, phi_bar, tol=5e-5,
          site="l.1108, eq:tauworked")
    tau = (w["h_raw_k"] / w["Theta_k"]) / (phi_bar * w["omega_bar"])
    s.add("1/(phi_bar * omega_bar) dilution multiplier", 3.376,
          1.0 / (phi_bar * w["omega_bar"]), tol=5e-4, site="eq:tauworked")
    s.add("tau_k, years to competence", 4.05, tau, tol=5e-3,
          site="eq:tauworked, Abstract")
    s.add("certification-implied duration h_raw/Theta", 1.20,
          w["h_raw_k"] / w["Theta_k"], tol=1e-9, site="l.1117, Abstract")
    s.add("dilution factor tau_k / (h_raw/Theta)", 3.38,
          tau / (w["h_raw_k"] / w["Theta_k"]), tol=5e-3,
          site="l.1117, Abstract, l.1705")
    n_hat = w["eta_k"] * w["N_k"] * w["r_k"] * tau
    s.add("intake requirement n_hat_k", 14.0, n_hat, tol=5e-2,
          site="eq:intakeworked, Abstract")
    s.add("n_hat_k, route 2: trainee hours / Theta_k", 14.0,
          trainee_hours / w["Theta_k"], tol=1e-9, site="l.1114")
    s.add("n_hat_k, route 3: Little's law", 14.0, (B_k / w["h_k"]) * tau,
          tol=5e-2, site="l.1114")
    s.add("two routes agree (identity)", 0.0,
          abs(n_hat - trainee_hours / w["Theta_k"]), tol=5e-2, site="l.1114")
    s.add("naive intake from the certification figure", 4.0,
          w["eta_k"] * w["N_k"] * w["r_k"] * (w["h_raw_k"] / w["Theta_k"]),
          tol=0.15, site="l.1117, Abstract", note="4.147 -> 'four trainees'")
    out.append(s)

    # -- who receives the protected work -------------------------------
    s = Section("Capability access arithmetic (sec:whoworked)")
    blind = w["incumbent_women"] * B_k
    s.add("composition-blind hours to the group", 622.0, blind, tol=0.1,
          site="l.1125")
    s.add("composition-blind competent-equivalents", 0.432, blind / w["h_k"],
          tol=5e-4, site="l.1125")
    floor = w["pool_women"] - w["epsilon_k"]
    s.add("required share Pi_{k,g}", 0.27, floor, tol=1e-9, site="l.1128")
    constrained_hours = floor * B_k
    s.add("constrained hours to the group", 1344.0, constrained_hours, tol=0.5,
          site="l.1128, sec:whowins")
    s.add("constrained competent-equivalents", 0.933,
          constrained_hours / w["h_k"], tol=5e-4, site="l.1128")
    s.add("access multiplier", 2.16, constrained_hours / blind, tol=5e-3,
          site="l.1128")
    s.add("developmental posts under the constraint", 3.8, floor * n_hat,
          tol=0.05, site="l.1128")
    s.add("developmental posts composition-blind", 1.8,
          w["incumbent_women"] * n_hat, tol=0.06, site="l.1128",
          note="1.750 rounds to the printed 1.8")

    # Table tab:dist, recast in Phase 1 as exact arithmetic.  Every cell is
    # B_k apportioned by a share, so the two blocks must each total B_k and
    # 3.456 competent-equivalents.
    men_blind = (1 - w["incumbent_women"]) * B_k
    men_con = (1 - floor) * B_k
    s.add("tab:dist men, blind share", 0.875, 1 - w["incumbent_women"],
          tol=1e-9, site="tab:dist")
    s.add("tab:dist men, blind hours", 4354.56, men_blind, tol=0.01,
          site="tab:dist")
    s.add("tab:dist men, blind c.eq.", 3.024, men_blind / w["h_k"], tol=5e-4,
          site="tab:dist")
    s.add("tab:dist women, blind hours", 622.08, blind, tol=0.01,
          site="tab:dist")
    s.add("tab:dist women, blind c.eq.", 0.432, blind / w["h_k"], tol=5e-4,
          site="tab:dist")
    s.add("tab:dist men, constrained share", 0.730, 1 - floor, tol=1e-9,
          site="tab:dist")
    s.add("tab:dist men, constrained hours", 3632.95, men_con, tol=0.01,
          site="tab:dist")
    s.add("tab:dist men, constrained c.eq.", 2.523, men_con / w["h_k"],
          tol=5e-4, site="tab:dist")
    s.add("tab:dist women, constrained hours", 1343.69, constrained_hours,
          tol=0.01, site="tab:dist")
    s.add("tab:dist women, constrained c.eq.", 0.933,
          constrained_hours / w["h_k"], tol=5e-4, site="tab:dist")
    s.add("tab:dist blind block totals to B_k", 4976.64, men_blind + blind,
          tol=0.01, site="tab:dist")
    s.add("tab:dist constrained block totals to B_k", 4976.64,
          men_con + constrained_hours, tol=0.01, site="tab:dist")
    s.add("tab:dist blind c.eq. total", 3.456, (men_blind + blind) / w["h_k"],
          tol=1e-6, site="tab:dist")
    s.add("tab:dist constrained c.eq. total", 3.456,
          (men_con + constrained_hours) / w["h_k"], tol=1e-6, site="tab:dist")
    out.append(s)

    # -- the retirement-wave parameter shocks --------------------------
    s = Section("Parameter shocks: stability and infeasibility")
    B_14 = w["eta_k"] * w["N_k"] * 0.14 * w["h_k"]
    s.add("B_k at r_k = 0.14", 5806.08, B_14, tol=1e-6, site="sec:retirement")
    req14 = B_14 / w["Phi_k"]
    x14 = (req14 - hi.credited) / (lo.credited - hi.credited)
    s.add("share on H+R/a1 at r_k = 0.14", 0.941, x14, tol=5e-4,
          site="sec:retirement, tab:sensitivity")
    mean14 = x14 * lo.scv + (1 - x14) * hi.scv
    s.add("cost of preservation at r_k = 0.14", 0.0957,
          (unc.scv - mean14) / unc.scv, tol=5e-4,
          site="sec:retirement, tab:sensitivity")
    s.add("operating point as share of feasibility ceiling", 0.99,
          B_14 / (w["Phi_k"] * w["zeta_bar"]), tol=5e-3, site="sec:retirement")
    # Critical attrition: B_k(r) = Phi * zeta_bar.
    r_crit = (w["Phi_k"] * w["zeta_bar"]) / (w["eta_k"] * w["N_k"] * w["h_k"])
    s.add("critical attrition rate r_k^crit", 0.1418, r_crit, tol=5e-5,
          site="tab:sensitivity, sec:shocks")
    s.add("required credited share at r_k = 0.14", 0.3456, req14, tol=1e-6,
          site="sec:shocks")
    B_25 = w["eta_k"] * w["N_k"] * 0.25 * w["h_k"]
    s.add("B_k at r_k = 0.25", 10368.0, B_25, tol=1e-6, site="sec:retirement")
    s.add("deficit at r_k = 0.25", 4488.0, B_25 - w["Phi_k"] * w["zeta_bar"],
          tol=1e-6, site="sec:retirement, tab:predictions")
    s.add("deficit in competent-equivalents", 3.12,
          (B_25 - w["Phi_k"] * w["zeta_bar"]) / w["h_k"], tol=5e-3,
          site="sec:retirement")
    s.add("required share at r_k = 0.25", 0.617, B_25 / w["Phi_k"], tol=5e-4,
          site="sec:retirement")
    s.add("task stream that closes the deficit", 3703,
          B_25 / (ell * w["zeta_bar"]), tol=1.0, site="sec:retirement")
    s.add("eta_k that closes the deficit", 0.68,
          (w["Phi_k"] * w["zeta_bar"]) / (w["N_k"] * 0.25 * w["h_k"]),
          tol=5e-3, site="sec:shocks")
    # Two developing practitioners per lead: an equal three-way split gives
    # the trainees two thirds of the human work.
    zeta_two = MODES["H+R/a1"].phi * (2.0 / 3.0)
    s.add("zeta_bar with two trainees per lead", 0.467, zeta_two, tol=5e-4,
          site="sec:shocks")
    s.add("residual deficit with two trainees per lead", 2528.0,
          B_25 - w["Phi_k"] * zeta_two, tol=1.0, site="sec:shocks")
    # Critical certification requirement, h_raw.
    h_raw_crit = ((w["Phi_k"] * w["zeta_bar"])
                  / (w["eta_k"] * w["N_k"] * w["r_k"] * w["learn"]))
    s.add("critical h_raw_k", 2127.0, h_raw_crit, tol=1.0,
          site="tab:sensitivity")
    out.append(s)

    # -- the debt trajectory -------------------------------------------
    s = Section("Debt trajectory (sec:cadmodel, eq:cadmodel) -- KNOWN DEFECT")
    ceiling, slope = 13.5, 1.37
    s.add("stated ceiling + slope*t at t = 10", 34.60, ceiling + slope * 10,
          tol=0.05, site="l.1640, fig:cad-trend", known_defect="Phase 2 (M3)",
          note="13.5 + 13.7 = 27.2 against the plotted 34.60")
    s.add("stated ceiling + slope*t at t = 20", 49.3, ceiling + slope * 20,
          tol=0.05, site="l.1642", known_defect="Phase 2 (M3)",
          note="13.5 + 27.4 = 40.9 against the stated 49.3")
    sat10 = ceiling * (1 - math.exp(-10 / tau))
    s.add("implied residual slope from the plotted 34.60", 1.37,
          (34.60 - sat10) / 10, tol=0.05, site="l.1640",
          known_defect="Phase 2 (M3)",
          note=f"saturating part contributes {sat10:.2f} at t=10, "
               f"leaving slope {(34.60 - sat10) / 10:.2f}")
    s.add("Human-First residual slope at t = 20", 2.38, (59.0 - 35.08) / 10,
          tol=0.05, site="fig:cad-trend caption, l.1642",
          known_defect="Phase 2 (M3)")
    out.append(s)

    # -- Section 8 pre-deletion baseline -------------------------------
    # Phase 1 of the revision programme deletes Section 8 in full, because it
    # reports a study that was never executed.  These checks are retained as a
    # record of what the deleted tables contained, and specifically to document
    # defect M5: the final row of tab:persector was labelled "mean over
    # sectors" while its Tasks/yr cell held a sum.  Once Section 8 is gone
    # these have no site in the manuscript and are reported as INFO.
    s = Section("Section 8 pre-deletion baseline (DELETED in Phase 1)")
    per_sector = {          # tab:persector, CFI / productivity / dual / Z4
        "Infrastructure inspection":      (2100,   0.99, 84.1, 0.0451, 0.041),
        "Waste collection":               (186000, 0.98, 91.7, 0.0092, 0.011),
        "Citizen-service administration": (412000, 0.96, 88.3, 0.0064, 0.019),
        "Public-transport operations":    (94000,  0.97, 87.6, 0.0138, 0.024),
        "Emergency logistics":            (31000,  0.94, 82.4, 0.0207, 0.052),
        "Municipal facility management":   (78000,  0.98, 86.9, 0.0113, 0.026),
    }
    rows = list(per_sector.values())
    n = len(rows)
    s.add("tab:persector Tasks/yr column SUM", 803100, sum(r[0] for r in rows),
          tol=1.0, site="tab:persector l.1427",
          note="the row is labelled 'mean over sectors'; this cell is a sum")
    s.add("tab:persector Tasks/yr column MEAN", 803100,
          sum(r[0] for r in rows) / n, tol=1.0,
          site="tab:persector l.1427", known_defect="removed with Section 8",
          note="defect M5: the mean is 133,850, not 803,100 -- one row mixed "
               "a sum with five means")
    s.add("tab:persector CFI mean", 0.97, sum(r[1] for r in rows) / n,
          tol=5e-3, site="tab:persector")
    s.add("tab:persector productivity mean", 86.8,
          sum(r[2] for r in rows) / n, tol=5e-2, site="tab:persector")
    s.add("tab:persector dual mean", 0.0178, sum(r[3] for r in rows) / n,
          tol=5e-5, site="tab:persector")
    s.add("tab:persector Z4 mean", 0.029, sum(r[4] for r in rows) / n,
          tol=5e-4, site="tab:persector")
    stress_cwos = [21.3, 38.6, 18.2, 20.7]
    stress_af = [68.4, 96.7, 42.9, 37.8]
    s.add("tab:stress CWOS mean", 24.7, sum(stress_cwos) / 4, tol=5e-2,
          site="tab:stress")
    s.add("tab:stress AF mean", 61.5, sum(stress_af) / 4, tol=5e-2,
          site="tab:stress")
    s.add("tab:stress mean ratio", 0.402,
          (sum(stress_cwos) / 4) / (sum(stress_af) / 4), tol=5e-3,
          site="tab:stress")
    s.add("P3 gap against the WEAKEST comparator (CM 0.17)", 80,
          (0.97 - 0.17) * 100, tol=1.0, site="tab:hypoutcomes l.1568")
    s.add("P3 gap against the BEST comparator (HF 0.31)", 80,
          (0.97 - 0.31) * 100, tol=1.0, site="tab:hypoutcomes l.1568",
          known_defect="removed with Section 8",
          note="defect M4: the stated 80-point gap uses Capability Matching; "
               "the best-performing comparator is Human-First, giving 66")
    out.append(s)

    return out


# --------------------------------------------------------------------------
# Reporting
# --------------------------------------------------------------------------

def main() -> int:
    ap = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    ap.add_argument("--quiet", action="store_true",
                    help="print only failures and the summary")
    ap.add_argument("--known", action="store_true",
                    help="show detail for checks flagged as known defects")
    args = ap.parse_args()

    sections = build()
    n_pass = n_fail = n_known = n_info = 0
    failures = []

    for sec in sections:
        header_printed = False
        for c in sec.checks:
            if c.printed is None:
                n_info += 1
                status, mark = "INFO", "  ·"
            elif c.passed:
                n_pass += 1
                status, mark = "PASS", "  +"
            elif c.known_defect:
                n_known += 1
                status, mark = "KNOWN", "  !"
            else:
                n_fail += 1
                status, mark = "FAIL", "  X"
                failures.append((sec.title, c))

            show = (status in ("FAIL",)
                    or (not args.quiet and status in ("PASS", "INFO"))
                    or (status == "KNOWN" and (args.known or not args.quiet)))
            if not show:
                continue
            if not header_printed:
                print(f"\n{sec.title}")
                print("-" * len(sec.title))
                header_printed = True
            if c.printed is None:
                print(f"{mark} {status:5s} {c.label:48s} = {c.computed:.6g}")
            else:
                print(f"{mark} {status:5s} {c.label:48s} "
                      f"printed {c.printed:<12.6g} computed {c.computed:<12.6g} "
                      f"delta {c.delta:.2e}")
            if c.note and (status != "PASS" or not args.quiet):
                print(f"            note: {c.note}")
            if c.site and status in ("FAIL", "KNOWN"):
                print(f"            site: {c.site}")

    total = n_pass + n_fail + n_known
    print("\n" + "=" * 72)
    print(f"audit_numbers.py: {n_pass} PASS  {n_fail} FAIL  "
          f"{n_known} KNOWN-DEFECT  {n_info} INFO  ({total} comparisons)")
    if failures:
        print("\nUnexpected failures:")
        for title, c in failures:
            print(f"  - [{title}] {c.label}: printed {c.printed}, "
                  f"computed {c.computed:.6g}  ({c.site})")
    if n_known:
        print(f"\n{n_known} check(s) fail as expected and are registered as "
              f"defects awaiting Phase 2.  Re-run with --known for detail.")
    print("=" * 72)
    return 1 if failures else 0


if __name__ == "__main__":
    sys.exit(main())
