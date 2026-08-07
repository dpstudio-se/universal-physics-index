#!/usr/bin/env python3
"""Coarser Euler toy walk for the same demo ODE family as g2_ricci_flow_rk4_sim.

Status: SYM / software illustration only.
Not validated geometric Ricci flow, not Torstone physics, not ToE evidence.
"""

from __future__ import annotations

import argparse
import csv
import math
import sys
from pathlib import Path

_THIS_DIR = Path(__file__).resolve().parent
if str(_THIS_DIR) not in sys.path:
    sys.path.insert(0, str(_THIS_DIR))

from g2_ricci_flow_rk4_sim import rhs  # noqa: E402


def run_simulation(
    *,
    a0: float = 2.0,
    T0: float = 0.5,
    d_tau: float = 1.0e-4,
    steps: int = 5_000,
    sample_every: int = 100,
    output: Path | None = None,
) -> list[tuple[float, float, float]]:
    if d_tau <= 0.0 or steps <= 0:
        raise ValueError("d_tau and steps must be positive")

    tau = 0.0
    a = float(a0)
    T = float(T0)
    rows: list[tuple[float, float, float]] = [(tau, a, T)]

    for i in range(1, steps + 1):
        da, dT = rhs(tau, a, T)
        a += d_tau * da
        T += d_tau * dT
        tau = i * d_tau
        if not (math.isfinite(a) and math.isfinite(T)):
            raise FloatingPointError(f"non-finite state at step {i}")
        if i % sample_every == 0 or i == steps:
            rows.append((tau, a, T))

    out = output or Path("ricci_flow_trajectory.csv")
    with out.open("w", newline="", encoding="utf-8") as fh:
        fh.write("# SYM Euler toy demo — not physical G2 Ricci flow\n")
        writer = csv.writer(fh)
        writer.writerow(["tau", "scale_factor_a", "torsion_T"])
        writer.writerows(rows)

    return rows


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description="Toy Euler demo (software only).")
    parser.add_argument("--steps", type=int, default=5_000)
    parser.add_argument("--dt", type=float, default=1.0e-4, dest="d_tau")
    parser.add_argument("-o", "--output", type=Path, default=Path("ricci_flow_trajectory.csv"))
    args = parser.parse_args(argv)
    rows = run_simulation(d_tau=args.d_tau, steps=args.steps, output=args.output)
    print(f"Wrote {len(rows)} samples to {args.output} (Euler toy demo only).")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
