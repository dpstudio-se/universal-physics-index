"""Command-line interface for validation and reference calculations."""

from __future__ import annotations

import argparse
import json
import sys
from dataclasses import asdict
from importlib.metadata import version
from pathlib import Path
from typing import Any, Sequence

from .models import FrequencyType, Status
from .physics import frequency_from_mass, mass_from_frequency, normalize_value, normalized_match
from .validation import load_json, validate_record


def _emit(payload: Any, as_json: bool) -> None:
    if as_json:
        print(json.dumps(payload, indent=2, sort_keys=True))
    elif isinstance(payload, dict):
        print("\n".join(f"{key}: {value}" for key, value in payload.items()))
    elif isinstance(payload, list):
        print("\n".join(str(item) for item in payload))
    else:
        print(payload)


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(prog="upi")
    parser.add_argument("--json", action="store_true", help="emit JSON")
    sub = parser.add_subparsers(dest="command", required=True)
    for name in ("validate", "inspect"):
        command = sub.add_parser(name)
        command.add_argument("file", type=Path)
    normalize = sub.add_parser("normalize")
    normalize.add_argument("value", type=float)
    normalize.add_argument("--reference", type=float, required=True)
    normalize.add_argument("--tolerance", type=float)
    derive_mass = sub.add_parser("derive-mass", aliases=["frequency-to-mass"])
    derive_mass.add_argument("--frequency", dest="frequency", type=float, required=True)
    derive_frequency = sub.add_parser("derive-frequency", aliases=["mass-to-frequency"])
    derive_frequency.add_argument("--mass", dest="mass", type=float, required=True)
    sub.add_parser("list-statuses")
    sub.add_parser("list-frequency-types")
    sub.add_parser("schema")
    sub.add_parser("version")
    return parser


def main(argv: Sequence[str] | None = None) -> int:
    args = build_parser().parse_args(argv)
    try:
        if args.command in {"validate", "inspect"}:
            record = load_json(args.file)
            issues = validate_record(record)
            if args.command == "inspect":
                _emit({"record": record, "issues": [asdict(issue) for issue in issues]}, args.json)
            else:
                _emit(
                    {"valid": not issues, "issues": [asdict(issue) for issue in issues]},
                    args.json,
                )
            return 1 if issues else 0
        if args.command == "normalize":
            z = normalize_value(args.value, args.reference)
            payload = {"value": args.value, "reference": args.reference, "Z": z}
            if args.tolerance is not None:
                payload["matches_reference"] = normalized_match(
                    args.value, args.reference, args.tolerance
                )
            _emit(payload, args.json)
        elif args.command in {"derive-mass", "frequency-to-mass"}:
            _emit(
                {
                    "frequency_hz": args.frequency,
                    "mass_equivalent_kg": mass_from_frequency(args.frequency),
                    "interpretation": (
                        "Mass-equivalent of photon energy hf under E=mc^2; not the mass of an "
                        "arbitrary oscillating object."
                    ),
                },
                args.json,
            )
        elif args.command in {"derive-frequency", "mass-to-frequency"}:
            _emit({"mass_kg": args.mass, "rest_mass_frequency_hz": frequency_from_mass(args.mass)}, args.json)
        elif args.command == "list-statuses":
            _emit([item.value for item in Status], args.json)
        elif args.command == "list-frequency-types":
            _emit([item.value for item in FrequencyType], args.json)
        elif args.command == "schema":
            _emit(str(Path("schemas/node.schema.json")), args.json)
        else:
            _emit(version("universal-physics-index"), args.json)
        return 0
    except (OSError, ValueError, ZeroDivisionError, json.JSONDecodeError) as exc:
        _emit({"error": str(exc)}, True if args.json else False)
        return 2


if __name__ == "__main__":
    sys.exit(main())
