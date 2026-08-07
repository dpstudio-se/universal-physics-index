#!/usr/bin/env python3
"""Toy RK4 integrator for a 2-variable ODE pair (software demo only).

Status: SYM / software illustration — NOT a validated G2-manifold Ricci flow,
NOT Planck-scale physics, and NOT evidence for any Theory of Everything.

Commit a915735 previously shipped this path with fabricated constants
(OMEGA_1766, TF_1766, PLANCK_LENGTH_POW6) presented as physical. Those claims
are withdrawn. This rewrite keeps a small, testable RK4 demo so the path is
not empty, with explicit non-authority language.

verification_type: software_test (when covered by unit tests)
"""

from __future__ import annotations

import argparse
import csv
import math
from pathlib import Path

# Dimensionless demo coefficients only — not physical constants.
DEMO_ALPHA = 1.0e-3
DEMO_BETA = 1.0e-3
DEMO_GAMMA = 1.0e-6


def rhs(tau: float, a: float, T: float) -> tuple[float, float]:
    """Right-hand side of the toy coupled system da/dtau, dT/dtau.

    Chosen for stable-ish short trajectories in a demo regime.
    No claim of equivalence to geometric Ricci flow on a G2 manifold.
    """
    _ = tau  # autonomous system; tau reserved for non-autonomous extensions
    da = -DEMO_ALPHA * (a**3) * (T**2)
    dT = -DEMO_BETA * (a**2) * T + DEMO_GAMMA * a * (T**3)
    return da, dT


def rk4_step(tau: float, a: float, T: float, d_tau: float) -> tuple[float, float]:
    """One classical RK4 step for the 2-D state (a, T)."""
    k1_a, k1_T = rhs(tau, a, T)
    k2_a, k2_T = rhs(tau + 0.5 * d_tau, a + 0.5 * d_tau * k1_a, T + 0.5 * d_tau * k1_T)
    k3_a, k3_T = rhs(tau + 0.5 * d_tau, a + 0.5 * d_tau * k2_a, T + 0.5 * d_tau * k2_T)
    k4_a, k4_T = rhs(tau + d_tau, a + d_tau * k3_a, T + d_tau * k3_T)

    a_next = a + (d_tau / 6.0) * (k1_a + 2.0 * k2_a + 2.0 * k3_a + k4_a)
    T_next = T + (d_tau / 6.0) * (k1_T + 2.0 * k2_T + 2.0 * k3_T + k4_T)
    return a_next, T_next


def run_rk4_simulation(
    *,
    a0: float = 2.0,
    T0: float = 0.5,
    d_tau: float = 1.0e-4,
    steps: int = 5_000,
    sample_every: int = 50,
    output: Path | None = None,
) -> list[tuple[float, float, float]]:
    """Integrate the toy system and optionally write CSV.

    Returns rows of (tau, a, T) including the initial state.
    """
    if d_tau <= 0.0 or steps <= 0 or sample_every <= 0:
        raise ValueError("d_tau, steps, and sample_every must be positive")
    if not math.isfinite(a0) or not math.isfinite(T0):
        raise ValueError("a0 and T0 must be finite")

    tau = 0.0
    a = float(a0)
    T = float(T0)
    rows: list[tuple[float, float, float]] = [(tau, a, T)]

    for i in range(1, steps + 1):
        a, T = rk4_step(tau, a, T, d_tau)
        tau = i * d_tau
        if not (math.isfinite(a) and math.isfinite(T)):
            raise FloatingPointError(f"non-finite state at step {i}: a={a}, T={T}")
        if i % sample_every == 0 or i == steps:
            rows.append((tau, a, T))

    out = output or Path("ricci_flow_trajectory_rk4.csv")
    with out.open("w", newline="", encoding="utf-8") as fh:
        fh.write("# SYM toy RK4 demo — not physical Ricci flow / not Omega-1766\n")
        writer = csv.writer(fh)
        writer.writerow(["tau", "scale_factor_a", "torsion_T"])
        writer.writerows(rows)

    return rows


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(
        description=(
            "Toy RK4 demo (software only). Not G2 Ricci-flow physics; "
            "not Omega-1766; not a ToE claim."
        )
    )
    parser.add_argument("--steps", type=int, default=5_000)
    parser.add_argument("--dt", type=float, default=1.0e-4, dest="d_tau")
    parser.add_argument("--a0", type=float, default=2.0)
    parser.add_argument("--T0", type=float, default=0.5)
    parser.add_argument(
        "-o",
        "--output",
        type=Path,
        default=Path("ricci_flow_trajectory_rk4.csv"),
    )
    args = parser.parse_args(argv)

    rows = run_rk4_simulation(
        a0=args.a0,
        T0=args.T0,
        d_tau=args.d_tau,
        steps=args.steps,
        output=args.output,
    )
    print(
        f"Wrote {len(rows)} samples to {args.output} "
        f"(toy RK4 demo only; verification_type=software_test)."
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
