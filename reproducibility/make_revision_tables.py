#!/usr/bin/env python3
"""LaTeX blocks for the analyses added in revision.

Reads data/revision.json and data/weights_sensitivity.json and writes one block
per table to generated/. With --splice it also replaces the matching
``% BEGIN GENERATED`` blocks in the private manuscript sources in Paper/.
"""

from __future__ import annotations

import json
import sys
from pathlib import Path

HERE = Path(__file__).resolve().parent
DATA, OUT = HERE / "data", HERE / "generated"
PAPER = HERE.parent / "Paper"
DOM = (("INS", "Structural inspection"), ("SAN", "Maintenance and sanitation"), ("CAS", "Citizen-service casework"))
EQR = "efficiency_quota_recency"
NAMES = {"static": "Static", "efficiency": "Efficiency", "civicworkos": "CivicWorkOS",
         "civicworkos_nolearn": "No learning", "civicworkos_noretention": "No retention",
         "efficiency_recency": "Efficiency + recency", EQR: "Efficiency + quota + recency"}


def neg(text: str) -> str:
    return text.replace("-", "$-$")


def num(value: float, fmt: str) -> str:
    text = format(value, fmt)
    if text.startswith("-") and float(text.replace(",", "")) == 0.0:   # a rounded -0.0 prints as 0.0
        text = text[1:]
    return neg(text)


def pm(d: dict, fmt: str, scale: float = 1.0) -> str:
    return f"{num(d['mean'] * scale, fmt)} [{num(d['ci_low'] * scale, fmt)}, {num(d['ci_high'] * scale, fmt)}]"


def pt(d: dict, fmt: str, scale: float = 1.0) -> str:
    return num(d["mean"] * scale, fmt)


def diff(d: dict, fmt: str, scale: float = 1.0) -> str:
    sign = "+" if d["diff"] >= 0 else ""
    return f"{sign}{num(d['diff'] * scale, fmt)} [{num(d['ci_low'] * scale, fmt)}, {num(d['ci_high'] * scale, fmt)}]"


def budget(R) -> str:
    out = []
    for p in ("civicworkos", "civicworkos_nolearn"):
        B = R["budget"][p]
        out.append(f"\\multicolumn{{8}}{{@{{}}l}}{{\\textit{{{NAMES[p]}}}}}\\\\")
        for key, label in DOM:
            x = B[key]
            years = " & ".join(f"{y['mean']:.2f}" for y in x["attainment_by_year"])
            out.append(f"{label} & {pt(x['lambda_mean'], ',.0f')} & {pt(x['budget_mean'], ',.0f')} & "
                       f"{pm(x['attainment'], '.2f')} & {years} & {100 * x['share_of_years_met']:.0f}" + r"\\")
        a = B["all"]
        out.append(f"All domains & {pt(a['lambda_total'], ',.0f')} & {pt(a['budget_total'], ',.0f')} & "
                   f"{pm(a['attainment'], '.2f')} & & & & " + r"\\")
    return "\n".join(out)


def domains(R) -> str:
    D = R["per_domain"]["routine"]
    out = []
    for key, label in DOM:
        out.append(f"\\multicolumn{{8}}{{@{{}}l}}{{\\textit{{{label}}}}}\\\\")
        for p in ("static", "efficiency", EQR, "civicworkos"):
            x = D[p][key]
            out.append(f"{NAMES[p]} & {pm(x['completion'], '.1f', 100)} & {pm(x['cost_per_completed'], '.2f')} & "
                       f"{pm(x['overload'], '.2f', 100)} & {pt(x['certified_end'], '.1f')} & {pt(x['current_end'], '.1f')} & "
                       f"{pt(x['graduations'], '.1f')} & {pt(x['incidents_per_1000'], '.1f')}" + r"\\")
    return "\n".join(out)


def payroll(R) -> str:
    P = R["payroll"]
    out = []
    for p in ("static", "efficiency", "efficiency_recency", EQR, "civicworkos", "civicworkos_nolearn", "civicworkos_noretention"):
        r, s, d = P["routine"][p], P["surge"][p], P["disruption"][p]
        out.append(f"{NAMES[p]} & {pm(r['assigned_hours_index'], '.1f')} & {pm(r['fixed_payroll_index'], '.1f')} & "
                   f"{pm(r['full_day_index'], '.1f')} & {pt(s['fixed_payroll_index'], '.1f')} & "
                   f"{pt(d['fixed_payroll_index'], '.1f')} & {pt(r['mean_workload'], '.3f')} & "
                   f"{pt(r['payroll_share_idle'], '.0f', 100)}" + r"\\")
    return "\n".join(out)


def stop_breakeven(T, phase: str, comparator: str, scenario: str = "disruption") -> float:
    """Stop hazard at which CivicWorkOS's expected incidents per injected fault equal the comparator's."""
    H = T["fault_injection"][scenario]
    cw = H["civicworkos"][phase]["hazard_per_1000"]
    c = H[comparator][phase]["hazard_per_1000"]["0.03"]["mean"]
    lo, hi = cw["0.03"]["mean"], cw["0.5"]["mean"]
    return 0.03 + (c - lo) * 0.47 / (hi - lo)


def takeover(R) -> str:
    T = R["takeover"]
    E, F = T["common_exposure"], T["fault_injection"]["disruption"]
    pols = ("static", "efficiency", "efficiency_recency", EQR, "civicworkos", "civicworkos_nolearn")
    out = [r"\multicolumn{7}{@{}l}{\textit{A. Disruption window, per 1,000 arrived window tasks (same denominator for every policy)}}\\",
           r"\textbf{Policy} & \textbf{Recovered} & \textbf{Failed takeover} & \textbf{Stopped} & \textbf{Incidents} & "
           r"\textbf{Window completion (\%)} & \\",
           r"\midrule"]
    for p in pols:
        x = E[p]
        out.append(f"{NAMES[p]} & {pm(x['recovered_per_1000'], '.1f')} & {pm(x['failed_takeover_per_1000'], '.1f')} & "
                   f"{pm(x['stopped_per_1000'], '.1f')} & {pm(x['incidents_per_1000_window'], '.1f')} & "
                   f"{pt(x['completion_window'], '.1f', 100)} & " + r"\\")
    out += [r"\midrule",
            r"\multicolumn{7}{@{}l}{\textit{B. Common fault-injection test, disruption scenario: expected share of injected faults}}\\",
            r"\textbf{Policy} & \textbf{Recovered, start} & \textbf{Stopped, start} & \textbf{Recovered, end} & "
            r"\textbf{Stopped, end} & \textbf{Window, end} & \textbf{Equal-hazard stop, end}\\",
            r"\midrule"]
    for p in pols:
        s, e = F[p]["start"], F[p]["end"]
        be = "---" if p == "civicworkos" or e["stop"]["mean"] > 0.0 else f"{stop_breakeven(T, 'end', p):.2f}"
        out.append(f"{NAMES[p]} & {pm(s['recovered'], '.3f')} & {pt(s['stop'], '.3f')} & {pm(e['recovered'], '.3f')} & "
                   f"{pt(e['stop'], '.3f')} & {pt(e['recovered_window'], '.3f')} & {be}" + r"\\")
    out += [r"\midrule",
            r"\multicolumn{7}{@{}l}{\textit{C. Hazard-adjusted incidents per 1,000 window tasks, by assumed hazard of a missed deadline ($h_{def}$; stop hazard 0.03)}}\\",
            r"\textbf{Policy} & $h_{def}=0$ & 0.03 & 0.05 & 0.10 & 0.15 & 0.30\\",
            r"\midrule"]
    H = T["deferral_hazard"]["0.03"]
    for p in pols:
        cells = " & ".join(pt(H[str(h)]["levels"][p], ".1f") for h in (0.0, 0.03, 0.05, 0.1, 0.15, 0.3))
        out.append(f"{NAMES[p]} & {cells}" + r"\\")
    return "\n".join(out)


def fault_domains(R) -> str:
    F = R["takeover"]["fault_injection"]["routine"]
    out = []
    for p in ("static", "efficiency", EQR, "civicworkos"):
        s, e = F[p]["start"]["by_domain"], F[p]["end"]["by_domain"]
        cells = " & ".join(f"{s[k]['mean']:.3f} & {e[k]['mean']:.3f}" for k, _ in DOM)
        out.append(f"{NAMES[p]} & {cells}" + r"\\")
    return "\n".join(out)


WORLD_NAMES = {"base": "Reference world", "power": "Power-law forgetting", "partial_0.50": "Partial restoration, 0.50",
               "partial_0.25": "Partial restoration, 0.25", "cloglog": "Asymmetric link (cloglog)",
               "cauchit": "Heavy-tailed link (cauchit)", "load_ar_0.15": "Momentary workload, s.d.\\ 0.15",
               "load_ar_0.30": "Momentary workload, s.d.\\ 0.30",
               "load_ar_0.30_t0.5": "Momentary workload, s.d.\\ 0.30, half tracked",
               "load_outcome": "Workload lowers outcomes", "combined": "Combined"}


def world(R) -> str:
    W = R["world"]
    out = []
    for v, label in WORLD_NAMES.items():
        x = W[v]["routine"]
        cw, ef, eq = x["civicworkos"], x["efficiency"], x["eqr"]
        nl = pt(x["no_learning"]["overload_share"], ".2f", 100) if "no_learning" in x else "---"
        out.append(f"{label} & {pt(cw['current_share_end'], '.2f')} & {pt(ef['current_share_end'], '.2f')} & "
                   f"{pt(eq['current_share_end'], '.2f')} & {diff(x['minus_efficiency']['certified_end'], '.1f')} & "
                   f"{pt(cw['overload_share'], '.2f', 100)} & {pt(ef['overload_share'], '.2f', 100)} & "
                   f"{pt(eq['overload_share'], '.2f', 100)} & {nl} & {pt(cw['completion_rate'], '.1f', 100)} & "
                   f"{pt(cw['cost_index'], '.1f')}" + r"\\")
    return "\n".join(out)


def world_disruption(R) -> str:
    W = R["world"]
    out = []
    for v in ("base", "power", "partial_0.50", "cauchit", "combined"):
        x = W[v]["disruption"]
        cw, ef, eq = x["civicworkos"], x["efficiency"], x["eqr"]
        out.append(f"{WORLD_NAMES[v]} & {pt(cw['current_share_end'], '.2f')} & {pt(eq['current_share_end'], '.2f')} & "
                   f"{pt(cw['takeover_success_window'], '.3f')} & {pt(ef['takeover_success_window'], '.3f')} & "
                   f"{pt(eq['takeover_success_window'], '.3f')} & {pt(cw['incidents_per_1000_window'], '.1f')} & "
                   f"{pt(ef['incidents_per_1000_window'], '.1f')} & {pt(eq['incidents_per_1000_window'], '.1f')} & "
                   f"{pt(cw['completion_rate_window'], '.1f', 100)}" + r"\\")
    return "\n".join(out)


RESTORE_TRUTH = {"led_true_0.50": "$\\varphi^{led}=0.50$", "led_true_0.60": "$\\varphi^{led}=0.60$",
                 "led_true_0.70": "$\\varphi^{led}=0.70$", "led_true_1.00": "$\\varphi^{led}=1.00$",
                 "graded_linear": "Graded, linear", "graded_quadratic": "Graded, quadratic"}
RESTORE_BOTH = {"led_both_0.50": "$\\varphi^{led}=0.50$", "led_both_0.60": "$\\varphi^{led}=0.60$",
                "led_both_0.70": "$\\varphi^{led}=0.70$", "led_both_1.00": "$\\varphi^{led}=1.00$"}


def restoration(R) -> str:
    X = R["restoration"]

    def row(label, r):
        cw, ef, eq = r["civicworkos"], r["efficiency"], r["eqr"]
        return (f"{label} & {pm(cw['current_share_end'], '.2f')} & {pm(ef['current_share_end'], '.2f')} & "
                f"{pm(eq['current_share_end'], '.2f')} & {pt(cw['current_end'], '.1f')} & {pt(ef['current_end'], '.1f')} & "
                f"{pt(eq['current_end'], '.1f')} & {pt(cw['completion_rate'], '.1f', 100)} & {pt(cw['cost_index'], '.1f')}" + r"\\")

    out = [row("Reference, $\\varphi^{led}=0.30$", X["base"]), r"\midrule",
           r"\multicolumn{9}{@{}l}{\textit{Truth only: the allocator still schedules and logs at $\varphi^{led}=0.30$}}\\"]
    out += [row(lbl, X["truth_only"][v]) for v, lbl in RESTORE_TRUTH.items()]
    out += [r"\midrule", r"\multicolumn{9}{@{}l}{\textit{Truth and allocator share the threshold}}\\"]
    out += [row(lbl, X["allocator_informed"][v]) for v, lbl in RESTORE_BOTH.items()]
    return "\n".join(out)


ADD_NAMES = {"eqr_floor": "+ lower-bound safety floor", "eqr_gate": "+ oversight gate", "eqr_ceiling": "+ workload ceiling",
             "eqr_ready": "+ readiness-gated takeover", "eqr_budget": "+ budget stage", "eqr_all": "+ all five"}
DROP_NAMES = {"cw_nofloor": "$-$ lower-bound floor", "cw_nogate": "$-$ oversight gate", "cw_noceiling": "$-$ workload ceiling",
              "cw_noready": "$-$ readiness test", "cw_nobudget": "$-$ budget stage"}


def add_one(R) -> str:
    A = R["add_one"]
    r0, d0 = A["routine"], A["disruption"]

    def row(label, r, d):
        return (f"{label} & {pt(r['current_share_end'], '.2f')} & {pt(r['current_end'], '.1f')} & {pt(r['graduations'], '.1f')} & "
                f"{pt(r['overload_share'], '.2f', 100)} & {pt(r['completion_rate'], '.1f', 100)} & "
                f"{pt(r['cost_index'], '.1f')} & {pt(r['fixed_payroll_index'], '.1f')} & "
                f"{pt(d['takeover_success_window'], '.3f')} & {pt(d['incidents_per_1000_window'], '.1f')} & "
                f"{pt(d['completion_rate_window'], '.1f', 100)}" + r"\\")

    out = [r"\multicolumn{11}{@{}l}{\textit{Add one to Efficiency + quota + recency}}\\", row("Base", r0["base"], d0["base"])]
    out += [row(lbl, r0["add_one"][p]["levels"], d0["add_one"][p]["levels"]) for p, lbl in ADD_NAMES.items()]
    out += [r"\midrule", r"\multicolumn{11}{@{}l}{\textit{Drop one from CivicWorkOS}}\\",
            row("CivicWorkOS", r0["civicworkos"], d0["civicworkos"])]
    out += [row(lbl, r0["drop_one"][p]["levels"], d0["drop_one"][p]["levels"]) for p, lbl in DROP_NAMES.items()]
    return "\n".join(out)


def uncertainty(R) -> str:
    U = R["uncertainty"]
    rows = [("routine", "Task completion (\\%)", "completion_rate", ".1f", 100),
            ("routine", "Current practitioners, end", "current_end", ".1f", 1),
            ("routine", "Certifications", "graduations", ".1f", 1),
            ("routine", "Overloaded days (\\%)", "overload_share", ".2f", 100),
            ("routine", "Incidents per 1,000", "incidents_per_1000", ".2f", 1),
            ("routine", "Takeover success, all", "takeover_success_rate", ".3f", 1),
            ("routine", "Minimal-risk stops", "mrc", ".1f", 1),
            ("disruption", "Window completion (\\%)", "completion_rate_window", ".1f", 100),
            ("disruption", "Takeover success, window", "takeover_success_window", ".3f", 1),
            ("disruption", "Incidents per 1,000 window tasks", "incidents_per_1000_window", ".2f", 1)]
    out = []
    for sc, label, m, fmt, scale in rows:
        x = U[sc]
        out.append(f"{label} & {pt(x['civicworkos'][m], fmt, scale)} & {pt(x['levels'][m], fmt, scale)} & "
                   f"{diff(x['civicworkos_minus'][m], fmt, scale)}" + r"\\")
    return "\n".join(out)


def fresh(R) -> str:
    F = R["fresh_seeds"]
    out = []
    for a, b in zip(F["tests_reference"], F["tests_fresh"]):
        comp = NAMES.get(a["comparison"], a["comparison"])
        out.append(f"{a['id']} & {a['scenario']} & {comp} & {num(a['estimate'], '+.3f')} & "
                   f"{num(b['estimate'], '+.3f')} [{num(b['ci_low'], '.3f')}, {num(b['ci_high'], '.3f')}] & "
                   f"{'yes' if a['supported'] else 'no'} & {'yes' if b['supported'] else 'no'}" + r"\\")
    return "\n".join(out)


LHS_ROWS = (("routine_share_minus_eff", "Current share, CivicWorkOS minus Efficiency", ".2f"),
            ("routine_share_minus_eqr", "Current share, CivicWorkOS minus Eff.\\ + quota + recency", ".2f"),
            ("routine_certified_minus_eff", "Certified, CivicWorkOS minus Efficiency", ".1f"),
            ("routine_certified_minus_eqr", "Certified, CivicWorkOS minus Eff.\\ + quota + recency", ".1f"),
            ("routine_overload_minus_eff", "Overload (points), CivicWorkOS minus Efficiency", ".2f"),
            ("routine_overload_minus_eqr", "Overload (points), CivicWorkOS minus Eff.\\ + quota + recency", ".2f"),
            ("routine_completion_minus_eff", "Completion (points), CivicWorkOS minus Efficiency", ".1f"),
            ("routine_completion_minus_eqr", "Completion (points), CivicWorkOS minus Eff.\\ + quota + recency", ".1f"),
            ("routine_cost_index_cw", "Cost index, CivicWorkOS", ".1f"),
            ("routine_fixed_payroll_index_cw", "Fixed-payroll index, CivicWorkOS", ".1f"),
            ("takeover_window_minus_eff", "Window takeover success, CivicWorkOS minus Efficiency", ".3f"),
            ("takeover_window_minus_eqr", "Window takeover success, CivicWorkOS minus Eff.\\ + quota + recency", ".3f"),
            ("incidents_window_minus_eff", "Window incidents, CivicWorkOS minus Efficiency", ".1f"),
            ("incidents_window_minus_eqr", "Window incidents, CivicWorkOS minus Eff.\\ + quota + recency", ".1f"))
PARAM_TEX = {"gamma": "$\\beta_0$", "tau_ret": "$\\tau^{ret}$", "tau_ret_cv": "$\\tau^{ret}$ s.d.", "rate_cv": "rate s.d.",
             "load_sd": "load s.d.", "theta_comp": "$\\vartheta^{comp}$", "residual": "$\\vartheta^{res}$",
             "human_led_share": "$\\varphi^{led}$", "omega_trainee": "$\\omega$", "avail_h": "$\\bar d$",
             "overtime_factor": "overtime", "workload_margin": "$\\varrho^{L}$", "takeover_headroom": "$\\varrho^{to}$",
             "machine_drift_sd": "drift s.d.", "fault_rate": "fault rate", "t_detect": "$T^{det}$", "t_reach": "$T^{reach}$",
             "t_sa": "$T^{sa}$", "ootl_factor": "$\\chi^{ootl}$", "overload_sa_factor": "$\\chi^{L}$", "value": "value",
             "wage_trainee": "trainee wage", "incident_cost": "incident cost", "p_incident_failure": "$p$(inc.\\,fail)",
             "p_incident_takeover_failure": "$p$(inc.\\,takeover)", "p_incident_mrc": "$p$(inc.\\,stop)",
             "variance_scale": "variance scale", "probe_prob": "probe rate", "probe_sd": "probe s.d.",
             "telemetry_prob": "telemetry rate", "telemetry_sd": "telemetry s.d.", "workload_sensor_prob": "sensor rate",
             "workload_sensor_sd": "sensor s.d.", "eta": "$\\eta_k$", "oversight_p_sd": "$u^{max}$", "readiness_z": "$z$",
             "retention_guard": "$g^{ret}$", "supervision_recovery": "$\\kappa^{sup}$", "attrition": "$r_k$",
             "machine_price_mult": "machine price", "hybrid_phi_shift": "hybrid $\\phi_m$"}


def lhs(R) -> str:
    L = R["lhs"]
    crit = L["critical_abs_spearman_0.05"]
    out = []
    for key, label, fmt in LHS_ROWS:
        x = L["outcomes"][key]
        top = [f"{PARAM_TEX[n]} ({num(r, '+.2f')})" for n, r in x["top_spearman"][:2] if abs(r) >= crit]
        out.append(f"{label} & {num(x['min'], fmt)} & {num(x['median'], fmt)} & {num(x['max'], fmt)} & "
                   f"{100 * x['share_positive']:.0f} & {', '.join(top) if top else '---'}" + r"\\")
    return "\n".join(out)


WEIGHT_NAMES = {"default": "Default weights", "equal": "Equal weights", "rank_order_centroid": "Rank-order centroids of the default order",
                "debt_free": "No debt weight ($w_9=0$), others rescaled", "safety_doubled": "Safety weight doubled, rescaled",
                "cost_doubled": "Cost weight doubled, rescaled"}
DIST_NAMES = {"dirichlet_c50": "Dirichlet, concentration 50", "dirichlet_c20": "Dirichlet, concentration 20",
              "uniform_simplex": "Uniform on the simplex"}


def weights(W) -> str:
    out = [r"\multicolumn{5}{@{}l}{\textit{Named weight vectors}}\\"]
    for k, label in WEIGHT_NAMES.items():
        x = W["named"][k]
        mode = x["unconstrained"].replace("+", "{+}").replace("/a", "/a_")
        mix = "both $a_1$ modes" if x["optimum"] == ["H+A+R/a1", "H+R/a1"] else ", ".join(x["optimum"])
        out.append(f"{label} & ${mode}$ & {mix} & {100 * x['a1_share']:.1f} & {x['cost_percent']:.2f}" + r"\\")
    out += [r"\midrule", r"\multicolumn{5}{@{}l}{\textit{Random weight vectors, 100,000 draws each (median cost, with the central 95\% range)}}\\"]
    for k, label in DIST_NAMES.items():
        x = W["distributions"][k]
        c = x["cost_percent"]
        out.append(f"{label} & {100 * x['share_unconstrained_lead_only']:.1f}\\% lead-only & "
                   f"{100 * x['share_baseline_mix']:.1f}\\% both $a_1$ modes & {100 * x['a1_share_min']:.1f}--100.0 & "
                   f"{c['median']:.2f} [{c['p2.5']:.2f}, {c['p97.5']:.2f}]" + r"\\")
    return "\n".join(out)


EXTRA_NAMES = {"base": "Reference", "demand_minus_0.10": "Hybrid $\\varpi_m-0.10$", "demand_plus_0.10": "Hybrid $\\varpi_m+0.10$",
               "dur_har_0.70": "$H{+}A{+}R$ duration $\\times0.70$", "dur_har_0.90": "$H{+}A{+}R$ duration $\\times0.90$",
               "bonus_0.00": "$H{+}A{+}R$ bonus 0.00", "bonus_0.10": "$H{+}A{+}R$ bonus 0.10",
               "theta0_0.20": "$\\vartheta_0=0.20$", "theta0_0.40": "$\\vartheta_0=0.40$"}


def extra(R) -> str:
    X = R["extra_oat"]
    return "\n".join(f"{label} & {diff(X[v]['current_share_end'], '.2f')} & {diff(X[v]['completion_rate'], '.1f', 100)} & "
                     f"{diff(X[v]['overload_share'], '.2f', 100)} & {pm(X[v]['cost_index'], '.1f')}" + r"\\"
                     for v, label in EXTRA_NAMES.items())


def revision_main(R) -> str:
    """The main article's summary table: routine unless stated, means over 30 paired seeds."""
    W, X, P, T, D = R["world"], R["restoration"], R["payroll"]["routine"], R["takeover"], R["per_domain"]["routine"]
    E, F = T["common_exposure"], T["fault_injection"]["disruption"]
    H = T["deferral_hazard"]["0.03"]
    PAIR = ("civicworkos", "efficiency", EQR)

    def share(row):
        return " & ".join(pt(row[k]["current_share_end"], ".2f") for k in ("civicworkos", "efficiency", "eqr"))

    def load(row):
        return " & ".join(pt(row[k]["overload_share"], ".2f", 100) for k in ("civicworkos", "efficiency", "eqr"))

    def head(text):
        return f"\\multicolumn{{4}}{{@{{}}l}}{{\\textit{{{text}}}}}\\\\"

    out = [head("Current share of certified practitioners, end"),
           f"Reference & {share(W['base']['routine'])}\\\\",
           f"Power-law forgetting & {share(W['power']['routine'])}\\\\",
           f"Partial restoration, 0.25 of the gap & {share(W['partial_0.25']['routine'])}\\\\",
           f"Heavy-tailed outcome link & {share(W['cauchit']['routine'])}\\\\",
           f"True $\\varphi^{{led}}=0.60$, allocator unchanged & {share(X['truth_only']['led_true_0.60'])}\\\\",
           f"True $\\varphi^{{led}}\\ge0.70$, allocator unchanged & {share(X['truth_only']['led_true_0.70'])}\\\\",
           f"$\\varphi^{{led}}\\ge0.70$, allocator informed & {share(X['allocator_informed']['led_both_0.70'])}\\\\",
           f"Graded restoration, quadratic & {share(X['truth_only']['graded_quadratic'])}\\\\",
           head("Overloaded practitioner-days (\\%)"),
           f"Reference & {load(W['base']['routine'])}\\\\",
           f"Momentary workload, s.d.\\ 0.15 & {load(W['load_ar_0.15']['routine'])}\\\\",
           f"Momentary workload, s.d.\\ 0.30 & {load(W['load_ar_0.30']['routine'])}\\\\",
           head("Service cost index (efficiency $=100$)"),
           "Wages for assigned hours (reference) & " + " & ".join(pt(P[p]["assigned_hours_index"], ".1f") for p in PAIR) + "\\\\",
           "Fixed payroll & " + " & ".join(pt(P[p]["fixed_payroll_index"], ".1f") for p in PAIR) + "\\\\",
           head("Disruption window, per 1,000 arrived tasks"),
           "Failed takeovers & " + " & ".join(pt(E[p]["failed_takeover_per_1000"], ".1f") for p in PAIR) + "\\\\",
           "Minimal-risk stops & " + " & ".join(pt(E[p]["stopped_per_1000"], ".1f") for p in PAIR) + "\\\\",
           "Incidents, $h_{def}=0$ (reference) & " + " & ".join(pt(H["0.0"]["levels"][p], ".1f") for p in PAIR) + "\\\\",
           "Incidents, $h_{def}=0.05$ & " + " & ".join(pt(H["0.05"]["levels"][p], ".1f") for p in PAIR) + "\\\\",
           "Incidents, $h_{def}=0.15$ & " + " & ".join(pt(H["0.15"]["levels"][p], ".1f") for p in PAIR) + "\\\\",
           head("Common fault-injection test: expected share of faults recovered"),
           "Start of day & " + " & ".join(pt(F[p]["start"]["recovered"], ".3f") for p in PAIR) + "\\\\",
           "End of day & " + " & ".join(pt(F[p]["end"]["recovered"], ".3f") for p in PAIR) + "\\\\",
           head("Task completion in structural inspection (\\%)"),
           "Routine operations & " + " & ".join(pt(D[p]["INS"]["completion"], ".1f", 100) for p in PAIR) + "\\\\"]
    return "\n".join(out)


def splice(path: Path, marker: str, content: str) -> None:
    import re
    raw = path.read_bytes()
    newline = "\r\n" if b"\r\n" in raw else "\n"
    text = raw.decode("utf-8").replace("\r\n", "\n")
    pat = re.compile(rf"(% BEGIN GENERATED {marker}\n)(.*?)(^[ \t]*% END GENERATED {marker})", re.S | re.M)
    if not pat.search(text):
        raise SystemExit(f"marker {marker} not found in {path.name}")
    text = pat.sub(lambda m: m.group(1) + content + "\n" + m.group(3), text)
    path.write_bytes(text.replace("\n", newline).encode("utf-8"))


def main() -> int:
    R = json.loads((DATA / "revision.json").read_text(encoding="utf-8"))
    W = json.loads((DATA / "weights_sensitivity.json").read_text(encoding="utf-8"))
    frags = {"REVBUDGET": budget(R), "REVDOMAINS": domains(R), "REVPAYROLL": payroll(R), "REVTAKEOVER": takeover(R),
             "REVFAULTDOM": fault_domains(R), "REVWEIGHTS": weights(W)}
    if "world" in R:
        frags["REVWORLD"] = world(R)
        frags["REVWORLDDIS"] = world_disruption(R)
    if "restoration" in R:
        frags["REVRESTORE"] = restoration(R)
    if "add_one" in R:
        frags["REVADDONE"] = add_one(R)
        frags["REVUNCERT"] = uncertainty(R)
    if "fresh_seeds" in R:
        frags["REVFRESH"] = fresh(R)
    if "lhs" in R:
        frags["REVLHS"] = lhs(R)
    if "extra_oat" in R:
        frags["REVOAT"] = extra(R)
    if all(k in R for k in ("world", "restoration")):
        frags["REVMAIN"] = revision_main(R)
    OUT.mkdir(parents=True, exist_ok=True)
    for k, v in frags.items():
        (OUT / f"{k}.tex").write_text(v + "\n", encoding="utf-8")
    if "--splice" in sys.argv:
        for k, v in frags.items():
            if k == "REVMAIN":
                splice(PAPER / "CivicWorkOS.tex", k, v)
            else:
                splice(PAPER / "CivicWorkOS_supplementary.tex", k, v)
    print("wrote", ", ".join(frags))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
