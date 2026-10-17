#!/usr/bin/env python3
"""Generate the article's simulation tables and trajectory figure from data/.

Reads the outputs that ``scripts/run_protocol.py --paper`` copies into
``Paper/Frontiers/data/`` and writes LaTeX fragments into ``data/generated/``.
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
OUT = DATA / "generated"

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
            crit = f"margin {t['margin']:+.2f}" if t["direction"] == "noninferior_lower" else f"ratio $\\le$ {t['margin']:.2f}"
        else:
            crit = f"$\\ge$ {t['threshold']:.2f}" if t["threshold"] is not None else "sign"
        is_ratio = t["metric"] == "cost_per_completed_ratio_to_efficiency"
        fmt = ".3f" if is_ratio or abs(t["estimate"]) < 2 else ".2f"
        sign = "" if is_ratio else "+"
        est = f"{t['estimate']:{sign}{fmt}} [{t['ci_low']:{sign}{fmt}}, {t['ci_high']:{sign}{fmt}}]"
        p = t["p_holm"]
        ptxt = "$<10^{-7}$" if p < 1e-7 else f"{p:.1e}".replace("e-0", "e$-$").replace("e-", "e$-$")
        est = est.replace("-", "$-$")
        crit = crit.replace("-", "$-$")
        rtxt = f"{t['effect_r']:+.2f}".replace("-", "$-$")
        verdict = "supported" if t["supported"] else "not supported"
        scen = t["scenario"]
        out.append(f"{t['id']} & {HNAMES[t['id']]} & {scen} & {comp} & {crit} & {est} & {ptxt} & {rtxt} & {verdict}\\\\")
    return "\n".join(out)


def trajectory_plot(scenario: str) -> str:
    lines = (DATA / f"trajectory_{scenario}.dat").read_text(encoding="utf-8").splitlines()
    header = lines[0].split()
    rows = [list(map(float, ln.split())) for ln in lines[1:]]
    styles = {"static": "civicamber, thick, densely dotted", "efficiency": "civicgray, thick, dashed",
              "civicworkos": "civicteal, very thick", "civicworkos_nolearn": "civicblue, thick, dashdotted",
              "civicworkos_noretention": "civicred, thick, dotted"}
    out = []
    for p in POLICIES:
        col = header.index(f"{p}_curr")
        pts = "".join(f"({int(r[0])},{r[col]:.2f})" for r in rows if int(r[0]) % 25 == 0 or int(r[0]) == 5)
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
            r"\multicolumn{4}{@{}l}{\textit{B. Sensitivity, routine operations: CivicWorkOS minus efficiency-focused}}\\",
            r"\textbf{Variant} & \textbf{Current share, end} & \textbf{Completion (points)} & \textbf{Cost index (efficiency $=100$)}\\",
            r"\midrule"]
    for v, lab in names.items():
        b = exp["sensitivity"][v]
        ci = b["cost_index"]
        cost = f"{ci['mean']:.1f} [{ci['ci_low']:.1f}, {ci['ci_high']:.1f}]"
        out.append(f"{lab} & {fmt_ci(b['current_share_end'], '.2f')} & {fmt_ci(b['completion_rate'], '.1f', 100)} & {cost}"
                   + r"\\")
    return "\n".join(out)


def splice(path: Path, marker: str, content: str) -> None:
    text = path.read_text(encoding="utf-8")
    pat = re.compile(rf"(% BEGIN GENERATED {marker}\n)(.*?)(^[ \t]*% END GENERATED {marker})", re.S | re.M)
    if not pat.search(text):
        raise SystemExit(f"marker {marker} not found in {path.name}")
    text = pat.sub(lambda m: m.group(1) + content + "\n" + m.group(3), text)
    path.write_text(text, encoding="utf-8")


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
        "EXPTABLE": exp_table(exp),
    }
    for k, v in frags.items():
        (OUT / f"{k}.tex").write_text(v + "\n", encoding="utf-8")
    if "--splice" in sys.argv:
        main_tex, supp_tex = HERE / "CivicWorkOS.tex", HERE / "CivicWorkOS_supplementary.tex"
        for k in ("SIMTABLE", "HYPTABLE", "TRAJROUTINE", "TRAJDISRUPTION", "EXPTABLE"):
            splice(main_tex, k, frags[k])
        for k in ("EXTROUTINE", "EXTSURGE", "EXTDISRUPTION"):
            splice(supp_tex, k, frags[k])
    print("wrote", ", ".join(frags))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
