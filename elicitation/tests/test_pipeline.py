"""Pipeline tests on SYNTHETIC ratings generated here, in memory, from a known truth.

The data are never written anywhere but pytest's tmp_path and are marked
`provenance: synthetic`. They exist to prove the pipeline recovers a known
generating process and refuses what it must refuse. They are not a result and
nothing in this file is evidence about municipal work.
"""

import json

import numpy as np
import pytest

import analyze

TASKS = [f"T{i:02d}" for i in range(1, 13)]
GROUPS = ["competent"] * 4 + ["developing"] * 4 + ["supervisor"] * 4


def make(path, *, phi_har=0.55, learn=0.8, ratio=1.0, h_raw=1800.0, noise=0.4,
         provenance="synthetic", ethics=None, n_raters=12, seed=3):
    """Ratings = task effect + rater noise around a known truth, both rounds."""
    rng = np.random.default_rng(seed)
    task_fx = rng.normal(0, 1.2, size=len(TASKS))      # real between-task spread
    task_fx[0] = 0.0       # the worked task sits at the generating value, so a
                           # random effect cannot clip it against the scale end
    lines = [f"# provenance: {provenance}"]
    if ethics:
        lines.append(f"# ethics-approval: {ethics}")
    lines.append("rater_id,group,round,parameter,item_id,value,rationale")
    clip = lambda v: float(np.clip(round(v), 0, 10))
    truth = {"H+A": 0.75, "H+R": 0.70, "H+A+R": phi_har}
    for r in range(n_raters):
        rid, g = f"R{r+1:02d}", GROUPS[r % 12]
        for rnd in (1, 2):
            sd = noise * (1.6 if rnd == 1 else 1.0)
            for t, tid in enumerate(TASKS):
                base = 10 * (learn if tid == "T01" else learn - 0.1) + task_fx[t]
                lines.append(f"{rid},{g},{rnd},learn,{tid},{clip(base + rng.normal(0, sd))},")
                for m, p in truth.items():
                    v = 10 * p + task_fx[t] + rng.normal(0, sd)
                    lines.append(f"{rid},{g},{rnd},phi,{m}|{tid},{clip(v)},")
            for c in range(4):
                lines.append(f"{rid},{g},{rnd},psi_ratio,C{c+1},"
                             f"{max(0.0, ratio + rng.normal(0, 0.1)):.2f},")
            lines.append(f"{rid},{g},{rnd},h_raw_doc,R1,{h_raw:.0f},")
            lines.append(f"{rid},{g},{rnd},h_raw_prac,R1,"
                         f"{h_raw * (1 + rng.normal(0, 0.05)):.0f},")
    path.write_text("\n".join(lines) + "\n", encoding="utf-8")
    return path


def run(tmp_path, **kw):
    f = make(tmp_path / "r.csv", **kw)
    out = tmp_path / "out"
    code = analyze.main([str(f), "--out", str(out), "--allow-synthetic",
                         "--reps", "300"])
    assert code == 0
    return out, json.loads((out / "SYNTHETIC-results.json").read_text())


def test_when_truth_equals_the_estimates_the_article_is_recovered(tmp_path):
    _, res = run(tmp_path)
    p = res["point"]
    assert p["learn"] == pytest.approx(0.80, abs=0.06)
    assert p["phi_H+A+R"] == pytest.approx(0.55, abs=0.06)
    assert p["psi_a1"] == pytest.approx(0.50, abs=0.03)
    assert p["h_raw"] == pytest.approx(1800, rel=0.05)
    # measured ~ estimated, so the re-solved dual should sit near the baseline
    assert res["scenarios"]["measured"]["feasible"]
    assert res["scenarios"]["measured"]["lam"] == pytest.approx(0.0454, abs=0.02)


def test_a_changed_truth_moves_the_resolved_outcome_as_the_sweep_says(tmp_path):
    """phi_{H+A+R} = 0.70 is the article's 'no reversal' row: dual ~0.0009."""
    _, res = run(tmp_path, phi_har=0.70)
    m = res["scenarios"]["measured"]
    assert m["feasible"]
    assert m["lam"] < 0.01                     # collapsed from 0.0454
    assert m["lead_only"] > 0.0                # lead-only roster retained


def test_infeasible_truth_is_reported_not_hidden(tmp_path):
    _, res = run(tmp_path, h_raw=2600.0)
    assert not res["scenarios"]["measured"]["feasible"]
    assert res["bootstrap"]["p_feasible"] < 0.5


def test_icc_decision_rule_is_applied(tmp_path):
    _, good = run(tmp_path, noise=0.3)
    assert good["agreement"]["learn"]["decision"] == "point value"
    sub = tmp_path / "noisy"
    sub.mkdir()
    _, bad = run(sub, noise=6.0)
    assert bad["agreement"]["learn"]["decision"] == "range"
    assert bad["agreement"]["learn"]["icc"] < 0.75


def test_h_raw_is_always_a_range_because_its_icc_is_undefined(tmp_path):
    _, res = run(tmp_path)
    a = res["agreement"]["h_raw"]
    assert a["icc"] is None and a["decision"] == "range"


# ----- the guards -----------------------------------------------------------

def test_refuses_synthetic_without_flag(tmp_path):
    f = make(tmp_path / "r.csv")
    assert analyze.main([str(f), "--out", str(tmp_path / "o")]) == 2
    assert not (tmp_path / "o").exists()


def test_refuses_real_data_without_ethics_reference(tmp_path):
    f = make(tmp_path / "r.csv", provenance="real")
    assert analyze.main([str(f), "--out", str(tmp_path / "o")]) == 2


def test_refuses_missing_provenance(tmp_path):
    f = make(tmp_path / "r.csv")
    f.write_text(f.read_text().replace("# provenance: synthetic\n", ""))
    assert analyze.main([str(f), "--out", str(tmp_path / "o"),
                         "--allow-synthetic"]) == 2


def test_real_data_with_approval_runs_and_is_not_watermarked(tmp_path):
    f = make(tmp_path / "r.csv", provenance="real", ethics="TEST-REF-0000")
    out = tmp_path / "o"
    assert analyze.main([str(f), "--out", str(out), "--reps", "100"]) == 0
    assert (out / "report.md").exists() and not (out / "SYNTHETIC-report.md").exists()
    assert "PackageError" not in (out / "rerun.tex").read_text()


def test_synthetic_outputs_are_watermarked_and_break_a_latex_build(tmp_path):
    out, _ = run(tmp_path)
    assert sorted(p.name for p in out.iterdir()) == [
        "SYNTHETIC-measured_vs_estimated.tex", "SYNTHETIC-report.md",
        "SYNTHETIC-rerun.tex", "SYNTHETIC-results.json"]
    for name in ("SYNTHETIC-measured_vs_estimated.tex", "SYNTHETIC-rerun.tex"):
        assert (out / name).read_text().startswith("\\PackageError")
    assert (out / "SYNTHETIC-report.md").read_text().startswith("> **SYNTHETIC")


@pytest.mark.parametrize("bad", [
    "R01,competent,2,learn,T01,11,",          # off the 0..10 scale
    "R01,competent,2,learn,T01,abc,",         # not a number
    "R01,nurse,2,learn,T01,5,",               # unknown group
    "R01,competent,3,learn,T01,5,",           # bad round
    "R01,competent,2,phi,T01,5,",             # phi item without a mode
    "R01,competent,2,h_raw_prac,R1,0,",       # non-positive hours
])
def test_malformed_rows_are_refused(tmp_path, bad):
    f = make(tmp_path / "r.csv")
    f.write_text(f.read_text() + bad + "\n")
    assert analyze.main([str(f), "--out", str(tmp_path / "o"),
                         "--allow-synthetic"]) == 2


def test_a_rater_in_two_groups_is_refused(tmp_path):
    f = make(tmp_path / "r.csv")
    f.write_text(f.read_text() + "R01,supervisor,2,learn,T02,5,\n")
    assert analyze.main([str(f), "--out", str(tmp_path / "o"),
                         "--allow-synthetic"]) == 2
