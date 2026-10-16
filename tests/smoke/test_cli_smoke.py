"""Smoke tests: every script in scripts/ actually runs end to end and
exits 0. These invoke the scripts as subprocesses (as a user would),
not by importing their internals, so they also catch import-path and
packaging regressions.
"""

from __future__ import annotations

import subprocess
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]


def _run(*args: str, timeout: int = 60) -> subprocess.CompletedProcess:
    return subprocess.run(
        [sys.executable, *args],
        cwd=ROOT,
        capture_output=True,
        text=True,
        timeout=timeout,
    )


def test_verify_worked_example_script_passes():
    result = _run("scripts/verify_worked_example.py")
    assert result.returncode == 0, result.stdout + result.stderr
    assert "reproduce the manuscript's printed values within" in result.stdout
    # Guard against the failure mode of finding N2: a gate that exits 0 having
    # checked nothing, or having checked an earlier draft's parameterisation.
    assert "[FAIL]" not in result.stdout
    assert "printed=4976.640000" in result.stdout


def test_run_allocation_script_runs():
    result = _run("scripts/run_allocation.py")
    assert result.returncode == 0, result.stdout + result.stderr
    assert "Selected mode:" in result.stdout


def test_run_rebalance_script_runs():
    result = _run("scripts/run_rebalance.py", "8")
    assert result.returncode == 0, result.stdout + result.stderr
    assert "Status: Optimal" in result.stdout


def test_run_simulation_script_runs():
    result = _run("scripts/run_simulation.py", "40", "7", timeout=60)
    assert result.returncode == 0, result.stdout + result.stderr
    assert "SYNTHETIC DEMO DATA" in result.stdout
    assert "civicworkos" in result.stdout


def test_sensitivity_sweep_script_runs():
    result = _run("scripts/sensitivity_sweep.py", "100", "0.3")
    assert result.returncode == 0, result.stdout + result.stderr
    assert "Argmax-flip rate" in result.stdout
