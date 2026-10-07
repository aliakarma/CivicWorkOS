"""Unit tests for civicworkos.config: weight validation and the UNSET
sentinel required by Paper sec:feedback ("an unset theta_{k,g} or tau_g must
leave its constraint unbound and flagged, never silently defaulted").
"""

from __future__ import annotations

from pathlib import Path

import pytest

from civicworkos.config.loader import load_domain_config, load_weights_config
from civicworkos.config.schema import UNSET, Unset

REPO_ROOT = Path(__file__).resolve().parents[2]
CONFIGS = REPO_ROOT / "configs"


def test_default_weights_config_loads_and_validates():
    config = load_weights_config(CONFIGS / "weights" / "default.yaml")
    assert config.w9_cad == pytest.approx(0.22)
    assert config.alpha_skill == pytest.approx(0.28)


def test_weights_config_rejects_bad_sum(tmp_path):
    bad = tmp_path / "bad_weights.yaml"
    bad.write_text(
        "version: v1\neffective_date: 2026-01-01\nw1_quality: 0.5\nw9_cad: 0.5\n"
        "w2_safety: 0.5\nw3_productivity: 0\nw4_equity: 0\nw5_trust: 0\n"
        "w6_cost: 0\nw7_energy: 0\nw8_privacy: 0\n"
    )
    with pytest.raises(Exception, match="must sum to 1.0"):
        load_weights_config(bad)


def test_domain_config_loads_worked_example_fixture():
    """The shipped domain config must be the worked example's own inputs, so
    that B_k computed from it is the article's 4,976.64 hours (eq:bkworked)."""
    from civicworkos.constraints.hcpb import HCPBParameters, capability_budget
    from manuscript_values import WORKED

    w = WORKED
    config = load_domain_config(CONFIGS / "domains" / "structural_inspection.yaml")
    assert config.N_k == w["N_k"]
    assert config.r_k == pytest.approx(w["r_k"])
    assert config.h_k == pytest.approx(w["h_k"])
    assert config.eta_k == pytest.approx(w["eta_k"])
    assert config.theta_kg["women"] == pytest.approx(w["pool_women"])
    assert config.theta_kg["men"] == pytest.approx(1 - w["pool_women"])
    assert config.epsilon_k == pytest.approx(w["epsilon_k"])

    b_k = capability_budget(
        HCPBParameters(
            N_k=config.N_k, r_k=config.r_k, h_k=config.h_k,
            eta_k=config.eta_k, B_k_min=config.B_k_min,
        )
    )
    assert b_k == pytest.approx(4976.64, abs=1e-6)


def test_unset_sentinel_is_parsed_not_a_string_or_none():
    config = load_domain_config(CONFIGS / "domains" / "structural_inspection.yaml")
    assert isinstance(config.tau_g["men"], Unset)
    assert config.tau_g["men"] is UNSET
    assert config.tau_g["men"] != 0.0
    assert config.tau_g["men"] != None  # noqa: E711 -- must not be None either


def test_unset_parameters_are_flagged():
    config = load_domain_config(CONFIGS / "domains" / "structural_inspection.yaml")
    flagged = config.unset_parameters()
    assert "tau_men" in flagged
    assert "tau_women" in flagged
    assert not any(f.startswith("theta_") for f in flagged)  # theta_kg IS set in this fixture


def test_unset_bool_is_falsy_but_distinct_from_zero():
    assert bool(UNSET) is False
    assert UNSET != 0.0
    assert UNSET != 0
