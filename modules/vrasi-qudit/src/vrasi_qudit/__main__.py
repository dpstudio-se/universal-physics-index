"""Command-line interface for the standalone VR-ASI qudit simulator."""

import argparse
import json
from collections.abc import Sequence
from dataclasses import asdict

from .core import search_torus_register


def _parse_int_list(value: str, name: str) -> tuple[int, ...]:
    try:
        values = tuple(int(item.strip()) for item in value.split(",") if item.strip())
    except ValueError as error:
        raise argparse.ArgumentTypeError(f"{name} must be comma-separated integers") from error
    if not values:
        raise argparse.ArgumentTypeError(f"{name} must not be empty")
    return values


def main(argv: Sequence[str] | None = None) -> int:
    parser = argparse.ArgumentParser(
        description="Run a classical multi-torus qudit search simulation",
    )
    parser.add_argument(
        "--dimensions",
        required=True,
        help="comma-separated torus dimensions, for example 4,5",
    )
    parser.add_argument(
        "--targets",
        required=True,
        help="comma-separated flattened target indices",
    )
    parser.add_argument("--iterations", type=int)
    parser.add_argument("--top-k", type=int, default=5)
    args = parser.parse_args(argv)

    dimensions = _parse_int_list(args.dimensions, "dimensions")
    targets = _parse_int_list(args.targets, "targets")
    result = search_torus_register(
        dimensions,
        targets,
        iterations=args.iterations,
        top_k=args.top_k,
    )
    print(json.dumps(asdict(result), sort_keys=True))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
