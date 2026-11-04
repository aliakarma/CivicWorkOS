#!/usr/bin/env python3
"""Generate the article's simulation tables and trajectory figure from data/.

Reads the outputs that ``scripts/run_protocol.py --paper`` copies into
``reproducibility/data/`` and writes LaTeX fragments into
``reproducibility/generated/``.
The fragments are pasted verbatim into the manuscript between marker
comments by ``--splice``; ``audit_numbers.py`` then checks every simulation
number in the manuscript against the same JSON. No simulation number in the
article is typed by hand.

    python make_sim_tables.py            # write fragments
    python make_sim_tables.py --splice   # also splice them into the .tex files
"""

from __future__ import annotations

import json
import re
import sys
from pathlib import Path

HERE = Path(__file__).resolve().parent
DATA = HERE / "data"
OUT = HERE / "generated"

POLICIES = ["static", "efficiency", "civicworkos", "civicworkos_nolearn", "civicworkos_noretention"]
SHORT = {"static": "Static", "efficiency": "Efficiency", "civicworkos": "CivicWorkOS",
         "civicworkos_nolearn": "No learning", "civicworkos_noretention": "No retention"}
HNAMES = {
    "H1": "Retention: current share at end is higher",
    "H2": "Formation: more certified practitioners at end",
    "H3": "Takeover success in the disruption window is higher",
    "H4": "Cost per completed task at most 115\\% of efficiency",
    "H5": "Completion within 2 points of efficiency",
    "H6": "Overload share is lower",
    "H7": "Learning raises disruption-window completion",
    "H8": "Retention mechanism raises current share",
}


def load():
    summary = json.loads((DATA / "summary.json").read_text(encoding="utf-8"))
    tests = json.loads((DATA / "hypotheses.json").read_text(encoding="utf-8"))
    return summary, tests


def cell(summary, sc, pol, metric, fmt, scale=1.0, ci=False):
    d = summary[sc][pol][metric]
    m = d["mean"] * scale
    if ci:
        return f"{m:{fmt}} [{d['ci_low'] * scale:{fmt}}, {d['ci_high'] * scale:{fmt}}]"
    return f"{m:{fmt}}"


def main_table(summary) -> str:
    rows = [
        ("routine", "Task completion (\\%)", "completion_rate", ".1f", 100),
        ("routine", "Service cost index (efficiency $=100$)", "cost_index", ".1f", 1),
        ("routine", "Overloaded practitioner-days (\\%)", "overload_share", ".2f", 100),
        ("routine", "Current share of certified, end", "current_share_end", ".2f", 1),
        ("routine", "Current practitioners, end", "current_end", ".1f", 1),
        ("routine", "Certified practitioners, end", "certified_end", ".1f", 1),
        ("routine", "Certifications over the horizon", "graduations", ".1f", 1),
        ("routine", "Takeover success, all faults", "takeover_success_rate", ".3f", 1),
        ("routine", "Incidents per 1,000 tasks", "incidents_per_1000", ".2f", 1),
        ("routine", "Proficiency estimate error (MAE), end", "proficiency_mae_end", ".3f", 1),
        ("surge", "Completion of window tasks (\\%)", "completion_rate_window", ".1f", 100),
        ("surge", "Overloaded practitioner-days (\\%)", "overload_share", ".2f", 100),
        ("disruption", "Completion of window tasks (\\%)", "completion_rate_window", ".1f", 100),
        ("disruption", "Takeover requests in window", "takeover_requests_window", ".1f", 1),
        ("disruption", "Takeover success in window", "takeover_success_window", ".3f", 1),
        ("disruption", "Incidents per 1,000 window tasks", "incidents_per_1000_window", ".1f", 1),
        ("disruption", "Reliability estimate error in window (MAE)", "machine_mae_window", ".3f", 1),
    ]
    head = {"routine": "Routine operations (three years)", "surge": "Demand surge (30-day window)",
            "disruption": "Automation disruption (20-day window)"}
    out = []
    last = None
    for sc, label, metric, fmt, scale in rows:
        if sc != last:
            if last is not None:
                out.append("\\midrule")
            out.append(f"\\multicolumn{{6}}{{@{{}}l}}{{\\textit{{{head[sc]}}}}}\\\\")
            last = sc
        vals = " & ".join(cell(summary, sc, p, metric, fmt, scale) for p in POLICIES)
        out.append(f"{label} & {vals}\\\\")
    return "\n".join(out)


def ext_table(summary, sc) -> str:
    rows = [
        ("Task completion (\\%)", "completion_rate", ".1f", 100),
        ("Window completion (\\%)", "completion_rate_window", ".1f", 100),
        ("Service cost index", "cost_index", ".1f", 1),
        ("Overloaded days (\\%)", "overload_share", ".2f", 100),
        ("Mean workload index", "mean_workload", ".3f", 1),
        ("Certified, end", "certified_end", ".1f", 1),
        ("Current, end", "current_end", ".1f", 1),
        ("Current share, end", "current_share_end", ".3f", 1),
        ("Mean proficiency of certified, end", "mean_proficiency_end", ".3f", 1),
        ("Certifications", "graduations", ".1f", 1),
        ("Trainee credit (h/yr)", "trainee_credit_per_year", ".0f", 1),
        ("Takeover success, all", "takeover_success_rate", ".3f", 1),
        ("Takeover success, window", "takeover_success_window", ".3f", 1),
        ("Takeover time (min)", "takeover_time_mean", ".2f", 1),
        ("Minimal-risk stops", "mrc", ".1f", 1),
        ("Incidents per 1,000", "incidents_per_1000", ".2f", 1),
        ("Incidents per 1,000, window", "incidents_per_1000_window", ".2f", 1),
        ("Proficiency estimate MAE, end", "proficiency_mae_end", ".3f", 1),
        ("Reliability estimate MAE", "machine_mae", ".3f", 1),
        ("Reliability estimate MAE, window", "machine_mae_window", ".3f", 1),
    ]
    out = []
    for label, metric, fmt, scale in rows:
        if summary[sc][POLICIES[0]][metric]["n"] == 0:
            continue
        vals = " & ".join(cell(summary, sc, p, metric, fmt, scale, ci=True) for p in POLICIES)
        out.append(f"{label} & {vals}\\\\")
    return "\n".join(out)


def hyp_table(tests) -> str:
    out = []
    for t in tests:
        comp = SHORT[t["comparison"]]
        if t["direction"].startswith("noninferior"):
            crit = (f"margin {t['margin']:+.2f}" if t["direction"] == "noninferior_lower"
                    else f"ratio $\\le$ {t['margin']:.2f}")
        else:
            crit = f"$\\ge$ {t['threshold']:.2f}" if t["threshold"] is not None else "sign"
        is_ratio = t["metric"] == "cost_per_completed_ratio_to_efficiency"
        fmt = ".3f" if is_ratio or abs(t["estimate"]) < 2 else ".2f"
        sign = "" if is_ratio else "+"
        est = f"{t['estimate']:{sign}{fmt}} [{t['ci_low']:{sign}{fmt}}, {t['ci_high']:{sign}{fmt}}]"
        p = t["p_holm"]
        if t["direction"].startswith("noninferior"):
            # decided on the interval alone (sec:stats); the test stays in the Holm family
            # stacked so the cell is no wider than a printed p-value
            ptxt = "\\begin{tabular}[c]{@{}c@{}}n/a\\\\(CI\\\\decision)\\end{tabular}"
        else:
            ptxt = "$<10^{-7}$" if p < 1e-7 else f"{p:.1e}".replace("e-0", "e$-$").replace("e-", "e$-$")
        est = est.replace("-", "$-$")
        crit = crit.replace("-", "$-$")
        rtxt = f"{t['effect_r']:+.2f}".replace("-", "$-$")
        verdict = "supported" if t["supported"] else "not supported"
        scen = t["scenario"]
        out.append(f"{t['id']} & {HNAMES[t['id']]} & {scen} & {comp} & {crit} & {est} & "
                   f"{ptxt} & {rtxt} & {verdict}\\\\")
    return "\n".join(out)


def trajectory_plot(scenario: str) -> str:
    lines = (DATA / f"trajectory_{scenario}.dat").read_text(encoding="utf-8").splitlines()
    header = lines[0].split()
    rows = [list(map(float, ln.split())) for ln in lines[1:]]
    styles = {"static": "civicamber, thick, densely dotted", "efficiency": "civicgray, thick, dashed",
              "civicworkos": "civicteal, very thick", "civicworkos_nolearn": "civicblue, thick, dashdotted",
              "civicworkos_noretention": "civicred, thick, dotted"}
    shown = [r for r in rows if int(r[0]) % 25 == 0 or int(r[0]) == 5]
    out = []
    if f"{POLICIES[0]}_curr_lo" in header:
        # per-point 95% t-interval over the 30 seeds, drawn under the means;
        # "forget plot" keeps the bands out of the legend (needs pgfplots fillbetween)
        for p in POLICIES:
            color = styles[p].split(",")[0]
            for side in ("lo", "hi"):
                col = header.index(f"{p}_curr_{side}")
                pts = "".join(f"({int(r[0])},{r[col]:.2f})" for r in shown)
                out.append(f"\\addplot[draw=none, forget plot, name path={scenario}{p}{side}] coordinates {{{pts}}};")
            out.append(f"\\addplot[{color}, fill opacity=0.15, draw=none, forget plot] "
                       f"fill between[of={scenario}{p}hi and {scenario}{p}lo];")
    for p in POLICIES:
        col = header.index(f"{p}_curr")
        pts = "".join(f"({int(r[0])},{r[col]:.2f})" for r in shown)
        out.append(f"\\addplot[{styles[p]}] coordinates {{{pts}}};")
    return "\n".join(out)


def fmt_ci(d, fmt, scale=1.0, signed=True):
    sg = "+" if signed else ""
    txt = (f"{d['diff'] * scale:{sg}{fmt}} [{d['ci_low'] * scale:{sg}{fmt}}, {d['ci_high'] * scale:{sg}{fmt}}]")
    return txt.replace("-", "$-$")


def exp_table(exp) -> str:
    oo = exp["outcome_only"]
    rows = [
        ("routine", r"Task completion (\%)", "completion_rate", ".1f", 100),
        ("routine", r"Overloaded practitioner-days (\%)", "overload_share", ".2f", 100),
        ("routine", "Current practitioners, end", "current_end", ".1f", 1),
        ("routine", "Proficiency estimate error (MAE), end", "proficiency_mae_end", ".3f", 1),
        ("disruption", r"Completion of window tasks (\%)", "completion_rate_window", ".1f", 100),
        ("disruption", "Takeover success in window", "takeover_success_window", ".3f", 1),
        ("disruption", "Incidents per 1,000 window tasks", "incidents_per_1000_window", ".1f", 1),
        ("disruption", "Reliability estimate error in window (MAE)", "machine_mae_window", ".3f", 1),
    ]
    out = [r"\multicolumn{4}{@{}l}{\textit{A. Multimodal channels removed (learning from task outcomes only)}}\\",
           r"\textbf{Metric} & \textbf{CivicWorkOS} & \textbf{Outcomes only} & \textbf{Difference [95\% CI]}\\",
           r"\midrule"]
    for sc, label, metric, fmt, scale in rows:
        d = oo[sc][metric]
        sclab = "" if sc == "routine" else " (disruption)"
        out.append(f"{label}{sclab} & {d['a_mean'] * scale:{fmt}} & {d['b_mean'] * scale:{fmt}} & "
                   f"{fmt_ci(d, fmt, scale)}" + r"\\")
    names = {"base": "Baseline", "tau_half": r"$\tau^{ret}\times0.5$", "tau_double": r"$\tau^{ret}\times2$",
             "machine_price_x3": r"Machine prices $\times3$"}
    out += [r"\midrule",
            r"\multicolumn{4}{@{}l}{\textit{B. Sensitivity, routine operations: "
            r"CivicWorkOS minus efficiency-focused}}\\",
            r"\textbf{Variant} & \textbf{Current share, end} & \textbf{Completion (points)} & "
            r"\textbf{Cost index (efficiency $=100$)}\\",
            r"\midrule"]
    for v, lab in names.items():
        b = exp["sensitivity"][v]
        ci = b["cost_index"]
        cost = f"{ci['mean']:.1f} [{ci['ci_low']:.1f}, {ci['ci_high']:.1f}]"
        out.append(f"{lab} & {fmt_ci(b['current_share_end'], '.2f')} & "
                   f"{fmt_ci(b['completion_rate'], '.1f', 100)} & {cost}"
                   + r"\\")
    return "\n".join(out)


# ---------------------------------------------------------------------------
# Exploratory blocks added after internal pre-specification (P4 data, P5 tables)
# ---------------------------------------------------------------------------

BASE_NAMES = {"efficiency": "Efficiency", "efficiency_quota": "Efficiency + quota",
              "efficiency_recency": "Efficiency + recency", "efficiency_quota_recency": "Efficiency + quota + recency",
              "civicworkos": "CivicWorkOS", "static": "Static", "civicworkos_nolearn": "No learning"}
SENSOR_NAMES = {"baseline": "Reference channel", "bias_0.05": "Bias s.d.\\ 0.05", "bias_0.10": "Bias s.d.\\ 0.10",
                "bias_0.15": "Bias s.d.\\ 0.15", "noise_0.20": "Noise s.d.\\ 0.20", "noise_0.30": "Noise s.d.\\ 0.30",
                "avail_0.35": "Availability 0.35", "combined": "Combined"}
TAKEOVER_NAMES = {"base": "Reference", "ootl_0.3": "$\\chi^{ootl}=0.3$", "ootl_1.0": "$\\chi^{ootl}=1.0$",
                  "t_sa_6": "$T^{sa}=6$ min", "t_sa_10": "$T^{sa}=10$ min",
                  "ins_budget_20": "Inspection $T^{safe}=20$ min"}
MODEL_NAMES = {"base": "Reference", "phi_hybrid_minus_0.10": "Hybrid $\\varphi_m-0.10$",
               "phi_hybrid_plus_0.10": "Hybrid $\\varphi_m+0.10$", "gamma_6": "$\\gamma=6$", "gamma_10": "$\\gamma=10$",
               "fault_0.01": "Fault rate 0.01", "fault_0.04": "Fault rate 0.04"}


def lvl(d, fmt, scale=1.0, ci=True):
    txt = f"{d['mean'] * scale:{fmt}}"
    if ci:
        txt += f" [{d['ci_low'] * scale:{fmt}}, {d['ci_high'] * scale:{fmt}}]"
    return txt.replace("-", "$-$")


def pt(d, fmt, scale=1.0):
    """Point estimate only."""
    return lvl(d, fmt, scale, ci=False)


def baselines_panel(exp) -> str:
    """Panel C of the exploratory table: rule-based baselines, routine operations."""
    b = exp["baselines"]["scenarios"]["routine"]
    out = [r"\midrule",
           r"\multicolumn{4}{@{}l}{\textit{C. Rule-based baselines, routine operations "
           r"(added after internal pre-specification; learning on in all)}}\\",
           r"\textbf{Policy} & \textbf{Current share, end} & \textbf{Overloaded days (\%)} & "
           r"\textbf{Cost index (efficiency $=100$)}\\",
           r"\midrule"]
    for p in ("efficiency", "efficiency_quota", "efficiency_recency", "efficiency_quota_recency", "civicworkos"):
        L = b["levels"][p]
        cost = L.get("cost_index", {"mean": 100.0, "ci_low": 100.0, "ci_high": 100.0})
        cost_txt = "100.0" if p == "efficiency" else lvl(cost, ".1f")
        out.append(f"{BASE_NAMES[p]} & {lvl(L['current_share_end'], '.2f')} & {lvl(L['overload_share'], '.2f', 100)} & "
                   f"{cost_txt}" + r"\\")
    return "\n".join(out)


def supp_baselines(exp) -> str:
    rows = [("Task completion (\\%)", "completion_rate", ".1f", 100),
            ("Certifications", "graduations", ".1f", 1),
            ("Current practitioners, end", "current_end", ".1f", 1),
            ("Current share, end", "current_share_end", ".2f", 1),
            ("Overloaded days (\\%)", "overload_share", ".2f", 100),
            ("Cost index", "cost_index", ".1f", 1),
            ("Takeover success, all", "takeover_success_rate", ".3f", 1),
            ("Window completion (\\%)", "completion_rate_window", ".1f", 100),
            ("Takeover success, window", "takeover_success_window", ".3f", 1),
            ("Incidents per 1,000, window", "incidents_per_1000_window", ".1f", 1)]
    pols = ("efficiency", "efficiency_quota", "efficiency_recency", "efficiency_quota_recency", "civicworkos")
    out = []
    heads = (("routine", "Routine operations"), ("surge", "Demand surge"), ("disruption", "Automation disruption"))
    for sc, head in heads:
        L = exp["baselines"]["scenarios"][sc]["levels"]
        out.append(f"\\multicolumn{{6}}{{@{{}}l}}{{\\textit{{{head}}}}}\\\\")
        for label, metric, fmt, scale in rows:
            if L["civicworkos"][metric]["n"] == 0:
                continue
            cells = []
            for p in pols:
                if metric == "cost_index" and p == "efficiency":
                    cells.append("100.0")
                else:
                    cells.append(lvl(L[p][metric], fmt, scale))
            out.append(f"{label} & " + " & ".join(cells) + r"\\")
        if sc != "disruption":
            out.append(r"\midrule")
    return "\n".join(out)


def supp_sensor(exp) -> str:
    S = exp["sensor_realism"]["scenarios"]
    out = []
    for sc, head in (("routine", "Routine operations"), ("disruption", "Automation disruption")):
        R = S[sc]
        out.append(f"\\multicolumn{{7}}{{@{{}}l}}{{\\textit{{{head}}}}}\\\\")
        ref = R["baseline"]
        out.append(f"{SENSOR_NAMES['baseline']} & {pt(ref['overload_share'], '.2f', 100)} & --- & "
                   f"{pt(ref['load_mae_end'], '.3f', 1)} & {pt(ref['proficiency_mae_end'], '.3f', 1)} & "
                   f"{pt(ref['current_end'], '.1f', 1)} & "
                   f"{pt(ref['takeover_success_window'], '.3f', 1) if sc == 'disruption' else '---'}" + r"\\")
        for v, E in R["settings"].items():
            L, d = E["levels"], E["minus_no_learning"]["overload_share"]
            towin = lvl(L["takeover_success_window"], ".3f", 1, False) if sc == "disruption" else "---"
            out.append(f"{SENSOR_NAMES[v]} & {pt(L['overload_share'], '.2f', 100)} & {fmt_ci(d, '.2f', 100)} & "
                       f"{pt(L['load_mae_end'], '.3f', 1)} & {pt(L['proficiency_mae_end'], '.3f', 1)} & "
                       f"{pt(L['current_end'], '.1f', 1)} & {towin}" + r"\\")
        nl, ef = R["no_learning"], R["efficiency"]
        out.append(f"No learning (reference) & {pt(nl['overload_share'], '.2f', 100)} & --- & "
                   f"{pt(nl['load_mae_end'], '.3f', 1)} & {pt(nl['proficiency_mae_end'], '.3f', 1)} & "
                   f"{pt(nl['current_end'], '.1f', 1)} & "
                   f"{pt(nl['takeover_success_window'], '.3f', 1) if sc == 'disruption' else '---'}" + r"\\")
        out.append(f"Efficiency (reference) & {pt(ef['overload_share'], '.2f', 100)} & --- & --- & "
                   f"{pt(ef['proficiency_mae_end'], '.3f', 1)} & {pt(ef['current_end'], '.1f', 1)} & "
                   f"{pt(ef['takeover_success_window'], '.3f', 1) if sc == 'disruption' else '---'}" + r"\\")
        if sc == "routine":
            out.append(r"\midrule")
    return "\n".join(out)


def sensor_figure(exp) -> str:
    """Figure: overload against the sensor setting, routine and disruption, with reference lines."""
    S = exp["sensor_realism"]["scenarios"]
    order = ["baseline", "bias_0.05", "bias_0.10", "bias_0.15", "noise_0.20", "noise_0.30", "avail_0.35", "combined"]
    out = []
    marks = {"routine": "civicteal, mark=*", "disruption": "civicred, mark=square*"}
    shift = {"routine": -0.12, "disruption": 0.12}   # side by side at each setting
    for sc in ("routine", "disruption"):
        R = S[sc]
        pts = []
        for i, v in enumerate(order):
            d = R["baseline"]["overload_share"] if v == "baseline" else R["settings"][v]["levels"]["overload_share"]
            m, lo, hi = 100 * d["mean"], 100 * d["ci_low"], 100 * d["ci_high"]
            pts.append(f"({i + shift[sc]:.2f},{m:.3f}) +- (0,{max(hi - m, m - lo):.3f})")
        out.append(f"\\addplot[{marks[sc]}, only marks, error bars/.cd, y dir=both, y explicit] "
                   f"coordinates {{{' '.join(pts)}}};")
    for sc, style in (("routine", "civicblue, dashdotted, thick"), ("disruption", "civicblue, dotted, thick")):
        nl = 100 * S[sc]["no_learning"]["overload_share"]["mean"]
        out.append(f"\\addplot[{style}, domain=-0.5:7.5, samples=2] {{{nl:.3f}}};")
    for sc, style in (("routine", "civicgray, dashed, thick"), ("disruption", "civicgray, densely dashed, thick")):
        ef = 100 * S[sc]["efficiency"]["overload_share"]["mean"]
        out.append(f"\\addplot[{style}, domain=-0.5:7.5, samples=2] {{{ef:.3f}}};")
    return "\n".join(out)


def supp_takeover(exp) -> str:
    T = exp["takeover_sweep"]["disruption"]
    out = []
    for v, E in T.items():
        cw, st = E["civicworkos"], E["static"]
        sa, sw = E["civicworkos_stops_all_run"], E["civicworkos_stops_window"]
        share = sa["ootl_share_pooled"]
        out.append(f"{TAKEOVER_NAMES[v]} & {pt(cw['takeover_success_window'], '.3f', 1)} & "
                   f"{pt(st['takeover_success_window'], '.3f', 1)} & "
                   f"{fmt_ci(E['civicworkos_minus_static']['takeover_success_window'], '.3f')} & "
                   f"{sa['mrc']['mean']:.1f} & {sw['mrc']['mean']:.1f} & {sa['seq_workload']['mean']:.1f} & "
                   f"{sa['seq_time']['mean']:.1f} & {sa['seq_competence']['mean']:.1f} & {100 * share:.0f}" + r"\\")
    return "\n".join(out)


def no_negative_zero(text: str) -> str:
    """Print a rounded -0.0 as 0.0 (new exploratory tables only)."""
    return re.sub(r"\$-\$(0\.0+)(?=[,\]\s&]|\\\\)", r"\1", text)


def supp_model(exp) -> str:
    return no_negative_zero(_supp_model(exp))


def _supp_model(exp) -> str:
    M = exp["model_sensitivity"]["variants"]
    out = []
    for v, B in M.items():
        ci = B["cost_index"]
        out.append(f"{MODEL_NAMES[v]} & {fmt_ci(B['current_share_end'], '.2f')} & "
                   f"{fmt_ci(B['completion_rate'], '.1f', 100)} & {fmt_ci(B['overload_share'], '.2f', 100)} & "
                   f"{ci['mean']:.1f} [{ci['ci_low']:.1f}, {ci['ci_high']:.1f}]" + r"\\")
    return "\n".join(out)


def supp_derived(exp) -> str:
    D = exp["derived"]
    cpc = D["cost_per_current"]["routine"]
    js = D["joint_safety_completion"]["disruption"]
    out = [r"\multicolumn{4}{@{}l}{\textit{A. Cost per current practitioner at the end of routine operations "
           r"(cost units per practitioner)}}\\",
           r"\textbf{Policy} & \textbf{Level [95\% CI]} & \textbf{CivicWorkOS minus policy} & "
           r"\textbf{Incremental cost per added current}\\",
           r"\midrule"]
    for p in ("civicworkos", "efficiency", "static", "civicworkos_nolearn", "efficiency_quota", "efficiency_recency",
              "efficiency_quota_recency"):
        L = cpc["levels"][p]
        if p == "civicworkos":
            out.append(f"{BASE_NAMES[p]} & {lvl(L, ',.0f')} & --- & ---" + r"\\")
            continue
        d, inc = cpc["civicworkos_minus"][p], cpc["incremental"][p]
        ratio = inc["ratio_of_paired_means"]
        lo, hi = inc["bootstrap_ci"]
        inc_txt = "---" if ratio is None or inc["mean_current_diff"] <= 0 else f"{ratio:,.0f} [{lo:,.0f}, {hi:,.0f}]"
        out.append(f"{BASE_NAMES[p]} & {lvl(L, ',.0f')} & {fmt_ci(d, ',.0f')} & {inc_txt}" + r"\\")
    out += [r"\midrule",
            r"\multicolumn{4}{@{}l}{\textit{B. Incident-free completion of disruption-window tasks (\%)}}\\",
            r"\textbf{Policy} & \textbf{Level [95\% CI]} & \textbf{CivicWorkOS minus policy} & "
            r"\textbf{Window completion (\%)}\\",
            r"\midrule"]
    for p in ("civicworkos", "civicworkos_nolearn", "efficiency", "static", "efficiency_quota", "efficiency_recency",
              "efficiency_quota_recency"):
        diff = "---" if p == "civicworkos" else fmt_ci(js["civicworkos_minus"][p], ".1f", 100)
        out.append(f"{BASE_NAMES[p]} & {lvl(js['levels'][p], '.1f', 100)} & {diff} & "
                   f"{pt(js['completion_window_levels'][p], '.1f', 100)}" + r"\\")
    return "\n".join(out)


def splice(path: Path, marker: str, content: str) -> None:
    raw = path.read_bytes()
    newline = "\r\n" if b"\r\n" in raw else "\n"
    text = raw.decode("utf-8").replace("\r\n", "\n")
    pat = re.compile(rf"(% BEGIN GENERATED {marker}\n)(.*?)(^[ \t]*% END GENERATED {marker})", re.S | re.M)
    if not pat.search(text):
        raise SystemExit(f"marker {marker} not found in {path.name}")
    text = pat.sub(lambda m: m.group(1) + content + "\n" + m.group(3), text)
    path.write_bytes(text.replace("\n", newline).encode("utf-8"))


def main() -> int:
    summary, tests = load()
    exp = json.loads((DATA / "exploratory.json").read_text(encoding="utf-8"))
    OUT.mkdir(parents=True, exist_ok=True)
    frags = {
        "SIMTABLE": main_table(summary),
        "HYPTABLE": hyp_table(tests),
        "TRAJROUTINE": trajectory_plot("routine"),
        "TRAJDISRUPTION": trajectory_plot("disruption"),
        "EXTROUTINE": ext_table(summary, "routine"),
        "EXTSURGE": ext_table(summary, "surge"),
        "EXTDISRUPTION": ext_table(summary, "disruption"),
        "EXPTABLE": exp_table(exp) + ("\n" + baselines_panel(exp) if "baselines" in exp else ""),
    }
    p4_main, p4_supp = [], []
    if all(k in exp for k in ("baselines", "sensor_realism", "takeover_sweep", "model_sensitivity", "derived")):
        # exploratory blocks added after internal pre-specification (P4)
        frags["SENSORFIG"] = sensor_figure(exp)
        frags["SUPPBASELINES"] = supp_baselines(exp)
        frags["SUPPSENSOR"] = supp_sensor(exp)
        frags["SUPPTAKEOVER"] = supp_takeover(exp)
        frags["SUPPMODEL"] = supp_model(exp)
        frags["SUPPDERIVED"] = supp_derived(exp)
        p4_main = ["SENSORFIG"]
        p4_supp = ["SUPPBASELINES", "SUPPSENSOR", "SUPPTAKEOVER", "SUPPMODEL", "SUPPDERIVED"]
    for k, v in frags.items():
        (OUT / f"{k}.tex").write_text(v + "\n", encoding="utf-8")
    if "--splice" in sys.argv:
        # --splice is a private mode for the Paper/ manuscript sources.
        private = HERE.parent / "Paper"
        main_tex = private / "CivicWorkOS.tex"
        supp_tex = private / "CivicWorkOS_supplementary.tex"
        if not main_tex.is_file() or not supp_tex.is_file():
            raise SystemExit("--splice requires both private manuscript sources in Paper/; "
                             "public fragments have been generated without splicing")
        for k in ("SIMTABLE", "HYPTABLE", "TRAJROUTINE", "TRAJDISRUPTION", "EXPTABLE", *p4_main):
            splice(main_tex, k, frags[k])
        for k in ("EXTROUTINE", "EXTSURGE", "EXTDISRUPTION", *p4_supp):
            splice(supp_tex, k, frags[k])
    print("wrote", ", ".join(frags))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
