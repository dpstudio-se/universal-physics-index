"""Software tests for the toy RK4 demo (not physical validation)."""

from __future__ import annotations

import importlib.util
import sys
from pathlib import Path

import pytest

ROOT = Path(__file__).resolve().parents[1]
MODULE_PATH = ROOT / "src" / "python" / "g2_ricci_flow_rk4_sim.py"


def _load_module():
    spec = importlib.util.spec_from_file_location("g2_ricci_flow_rk4_sim", MODULE_PATH)
    assert spec and spec.loader
    mod = importlib.util.module_from_spec(spec)
    sys.modules[spec.name] = mod
    spec.loader.exec_module(mod)
    return mod


@pytest.fixture(scope="module")
def sim():
    return _load_module()


def test_module_rejects_omega_1766_authority(sim) -> None:
    """a915735 pollution: fabricated Omega constants must not be reintroduced as code.

    Mentions in withdrawal/disclaimer text are allowed; bindings and axiom claims are not.
    """
    assert not hasattr(sim, "OMEGA_1766")
    assert not hasattr(sim, "TF_1766")
    assert not hasattr(sim, "PLANCK_LENGTH_POW6")
    src = MODULE_PATH.read_text(encoding="utf-8")
    # No assignment / definition of fabricated constants
    assert "OMEGA_1766 =" not in src
    assert "TF_1766 =" not in src
    assert "PLANCK_LENGTH_POW6 =" not in src
    assert "Axiom 1766" not in src


def test_rk4_runs_finite(sim, tmp_path: Path) -> None:
    out = tmp_path / "traj.csv"
    rows = sim.run_rk4_simulation(steps=200, sample_every=50, output=out)
    assert out.is_file()
    assert len(rows) >= 2
    for tau, a, T in rows:
        assert math_isfinite(tau) and math_isfinite(a) and math_isfinite(T)


def test_rk4_step_matches_manual_half(sim) -> None:
    a1, T1 = sim.rk4_step(0.0, 2.0, 0.5, 1e-4)
    assert abs(a1 - 2.0) < 0.1
    assert abs(T1 - 0.5) < 0.1


def math_isfinite(x: float) -> bool:
    import math

    return math.isfinite(x)
