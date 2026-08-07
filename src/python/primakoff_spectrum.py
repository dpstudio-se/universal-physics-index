#!/usr/bin/env python3
"""Toy spectral curve generator (software demo only).

Previously this file mixed Primakoff-like language with unvalidated
\"Torstone\" / kHz claims. Those physical claims are withdrawn.

This rewrite emits a simple dimensionless spectrum shape for plotting demos.
Status: SYM. verification_type when tested: software_test.
"""

from __future__ import annotations

import argparse
import csv
import math
from pathlib import Path


def spectrum(x: float, peak: float = 1.0, width: float = 0.25) -> float:
    """Smooth positive bump; not a particle-physics cross-section."""
    return math.exp(-0.5 * ((x - peak) / width) ** 2)


def generate_spectrum(
    *,
    n: int = 200,
    x_min: float = 0.0,
    x_max: float = 2.0,
    output: Path | None = None,
) -> list[tuple[float, float]]:
    if n < 2 or x_max <= x_min:
        raise ValueError("need n >= 2 and x_max > x_min")
    rows: list[tuple[float, float]] = []
    for i in range(n):
        x = x_min + (x_max - x_min) * i / (n - 1)
        rows.append((x, spectrum(x)))

    out = output or Path("toy_spectrum.csv")
    with out.open("w", newline="", encoding="utf-8") as fh:
        fh.write("# SYM toy spectrum — not Primakoff / not Torstone physics\n")
        writer = csv.writer(fh)
        writer.writerow(["x", "amplitude"])
        writer.writerows(rows)
    return rows


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(
        description="Toy spectrum CSV (software only; not Primakoff physics)."
    )
    parser.add_argument("-n", type=int, default=200)
    parser.add_argument("-o", "--output", type=Path, default=Path("toy_spectrum.csv"))
    args = parser.parse_args(argv)
    rows = generate_spectrum(n=args.n, output=args.output)
    print(f"Wrote {len(rows)} points to {args.output} (toy spectrum only).")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
