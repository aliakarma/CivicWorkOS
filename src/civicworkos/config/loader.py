"""YAML loaders for the governance-artifact configs of civicworkos.config.schema.

The literal YAML string "UNSET" is parsed into the `Unset` sentinel, not
into `None` or a numeric default -- so a panel that has not yet set
theta_{k,g} or tau_g gets a flagged, unbound constraint rather than a
silently-defaulted one (Paper Sec. 5.1; see schema.py's docstring).
"""

from __future__ import annotations

from pathlib import Path

import yaml

from civicworkos.config.schema import UNSET, DomainConfig, Unset, WeightsConfig


def _parse_maybe_unset(value: float | str) -> float | Unset:
    if isinstance(value, str) and value.strip().upper() == "UNSET":
        return UNSET
    return float(value)


def load_weights_config(path: str | Path) -> WeightsConfig:
    """Load and validate a versioned weights config (w1..w9, alpha..epsilon)."""
    with open(path, encoding="utf-8") as f:
        raw = yaml.safe_load(f)
    return WeightsConfig(**raw)


def load_domain_config(path: str | Path) -> DomainConfig:
    """Load and validate a versioned per-domain config, honoring UNSET."""
    with open(path, encoding="utf-8") as f:
        raw = yaml.safe_load(f)

    theta_kg = {g: _parse_maybe_unset(v) for g, v in (raw.get("theta_kg") or {}).items()}
    tau_g = {g: _parse_maybe_unset(v) for g, v in (raw.get("tau_g") or {}).items()}

    return DomainConfig(
        domain=raw["domain"],
        version=raw["version"],
        effective_date=raw["effective_date"],
        N_k=raw["N_k"],
        r_k=raw["r_k"],
        h_k=raw["h_k"],
        eta_k=raw["eta_k"],
        B_k_min=raw["B_k_min"],
        hybrid_phi=dict(raw.get("hybrid_phi") or {}),
        groups=list(raw.get("groups") or []),
        theta_kg=theta_kg,
        epsilon_k=raw.get("epsilon_k", 0.05),
        tau_g=tau_g,
        chi_min=raw.get("chi_min", 0.0),
    )
