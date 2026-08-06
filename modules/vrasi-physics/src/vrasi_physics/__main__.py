"""Command-line entry point for the VR-ASI physics kernel."""

import argparse
import json
from collections.abc import Sequence
from dataclasses import asdict

from .core import DEFAULT_REFERENCE_FREQUENCY_HZ, evaluate_frequency


def main(argv: Sequence[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description="Evaluate the VR-ASI frequency model")
    parser.add_argument("frequency_hz", type=float)
    parser.add_argument(
        "--reference-hz",
        type=float,
        default=DEFAULT_REFERENCE_FREQUENCY_HZ,
        help="explicit normalization reference (default: 8 Hz)",
    )
    args = parser.parse_args(argv)
    print(
        json.dumps(
            asdict(evaluate_frequency(args.frequency_hz, args.reference_hz)),
            sort_keys=True,
        )
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
