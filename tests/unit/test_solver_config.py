"""Unit test for the CIVICWORKOS_SOLVER_TIME_LIMIT_SECONDS env override."""

from __future__ import annotations

import pytest

from civicworkos.solver.rebalance import _default_time_limit_seconds


def test_default_time_limit_without_env_var(monkeypatch):
    monkeypatch.delenv("CIVICWORKOS_SOLVER_TIME_LIMIT_SECONDS", raising=False)
    assert _default_time_limit_seconds() == 60


def test_default_time_limit_respects_env_var(monkeypatch):
    monkeypatch.setenv("CIVICWORKOS_SOLVER_TIME_LIMIT_SECONDS", "5")
    assert _default_time_limit_seconds() == 5


def test_default_time_limit_rejects_non_integer(monkeypatch):
    monkeypatch.setenv("CIVICWORKOS_SOLVER_TIME_LIMIT_SECONDS", "not-a-number")
    with pytest.raises(ValueError, match="must be an integer"):
        _default_time_limit_seconds()
