"""CLI entry point for upi-aeco."""

import argparse
import json
import sys

from .core.evolution_loop import evolution_cycle
from .core.observer import observe


def main() -> None:
    parser = argparse.ArgumentParser(
        prog="upi-aeco",
        description="UPI-AECΩ Autonomous Evolution Core Omega CLI",
    )
    subparsers = parser.add_subparsers(dest="command", help="Available subcommands")

    # Command: run
    run_parser = subparsers.add_parser("run", help="Run an evolution cycle")
    run_parser.add_argument(
        "--version-id",
        default="v0.1.0-initial",
        help="Initial version ID for evolution cycle",
    )

    # Command: status
    subparsers.add_parser("status", help="Observe current self-model snapshot")

    args = parser.parse_args()

    if args.command == "run":
        res = evolution_cycle(args.version_id)
        print(json.dumps(res, indent=2))
    elif args.command == "status":
        model = observe()
        print(json.dumps(model, indent=2))
    else:
        parser.print_help()
        sys.exit(1)


if __name__ == "__main__":
    main()
