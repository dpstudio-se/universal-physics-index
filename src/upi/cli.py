"""Command-line interface."""

from __future__ import annotations

import argparse
import json
from .physics import frequency_from_mass, index8_from_mass, mass_from_frequency


def main() -> None:
    parser = argparse.ArgumentParser(prog="upi")
    sub = parser.add_subparsers(dest="command", required=True)

    f2m = sub.add_parser("frequency-to-mass")
    f2m.add_argument("frequency_hz", type=float)

    m2f = sub.add_parser("mass-to-frequency")
    m2f.add_argument("mass_kg", type=float)

    i8 = sub.add_parser("index8")
    i8.add_argument("--mass", type=float, required=True)

    args = parser.parse_args()

    if args.command == "frequency-to-mass":
        payload = {"frequency_hz": args.frequency_hz, "mass_kg": mass_from_frequency(args.frequency_hz)}
    elif args.command == "mass-to-frequency":
        payload = {"mass_kg": args.mass_kg, "frequency_hz": frequency_from_mass(args.mass_kg)}
    else:
        payload = {"mass_kg": args.mass, "N8": index8_from_mass(args.mass)}

    print(json.dumps(payload, indent=2, sort_keys=True))


if __name__ == "__main__":
    main()
