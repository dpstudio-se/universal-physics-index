#!/usr/bin/env python3
"""Optional plot helper for toy Ricci-demo CSV output.

Status: SYM visualization helper only. Requires pandas/matplotlib if used.
Does not establish physical meaning of the trajectory.
"""

from __future__ import annotations

import argparse
from pathlib import Path


def plot_trajectory(csv_path: Path, output: Path | None = None) -> None:
    try:
        import matplotlib.pyplot as plt
        import pandas as pd
    except ImportError as exc:  # pragma: no cover - optional deps
        raise SystemExit(
            "plot_ricci_flow requires pandas and matplotlib (optional extras)."
        ) from exc

    df = pd.read_csv(csv_path, comment="#")
    fig, ax = plt.subplots(figsize=(8, 5))
    ax.plot(df["tau"], df["scale_factor_a"], label="a (toy scale)")
    ax.plot(df["tau"], df["torsion_T"], label="T (toy torsion-like)")
    ax.set_xlabel("tau (demo time)")
    ax.set_ylabel("state")
    ax.set_title("Toy RK4/Euler trajectory (not physical Ricci flow)")
    ax.legend()
    ax.grid(True, alpha=0.3)
    out = output or csv_path.with_suffix(".png")
    fig.tight_layout()
    fig.savefig(out, dpi=120)
    plt.close(fig)
    print(f"Wrote {out}")


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description="Plot toy Ricci-demo CSV.")
    parser.add_argument(
        "csv_path",
        type=Path,
        nargs="?",
        default=Path("ricci_flow_trajectory_rk4.csv"),
    )
    parser.add_argument("-o", "--output", type=Path, default=None)
    args = parser.parse_args(argv)
    plot_trajectory(args.csv_path, args.output)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
