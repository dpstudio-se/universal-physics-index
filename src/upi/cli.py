"""Command-line interface for UPI."""

import json
import sys
from pathlib import Path

from . import (
    __version__,
    energy_from_frequency,
    frequency_from_mass,
    index8_from_frequency,
    index8_from_mass,
    mass_from_frequency,
    signal_match,
    validate_bridge_json,
    validate_node_json,
)
from .debug import generate_debug_report, render_debug_markdown
from .models import Address
from .schema_resources import schema_path


def print_json(data):
    """Print data as pretty JSON."""
    print(json.dumps(data, indent=2))


def frequency_to_mass(args):
    """Convert frequency to mass."""
    frequency_hz = float(args.frequency)
    mass_kg = mass_from_frequency(frequency_hz)
    result = {
        "operation": "frequency_to_mass",
        "input_frequency_hz": frequency_hz,
        "output_mass_kg": mass_kg,
        "equation": "m = h*f / c^2",
        "interpretation": (
            "Energy-equivalence calculation for the declared frequency; "
            "this is not the mass of an arbitrary oscillating object."
        ),
    }
    print_json(result)


def mass_to_frequency(args):
    """Convert mass to frequency."""
    mass_kg = float(args.mass)
    frequency_hz = frequency_from_mass(mass_kg)
    result = {
        "operation": "mass_to_frequency",
        "input_mass_kg": mass_kg,
        "output_frequency_hz": frequency_hz,
        "equation": "f = m*c^2 / h"
    }
    print_json(result)


def index8_cmd(args):
    """Calculate 8 Hz index."""
    if args.frequency:
        n8 = index8_from_frequency(float(args.frequency))
        result = {
            "operation": "index8_from_frequency",
            "input_frequency_hz": float(args.frequency),
            "output_n8": n8,
            "equation": "N8 = f / (8 Hz)"
        }
    elif args.mass:
        n8 = index8_from_mass(float(args.mass))
        result = {
            "operation": "index8_from_mass",
            "input_mass_kg": float(args.mass),
            "output_n8": n8,
            "equation": "N8 = m*c^2 / (8*h)"
        }
    else:
        print("Error: --frequency or --mass required", file=sys.stderr)
        sys.exit(1)
    print_json(result)


def normalize_cmd(args):
    """Normalize signal."""
    observed = float(args.observed)
    reference = float(args.reference)
    result_obj = signal_match(observed, reference, epsilon=float(args.epsilon) if args.epsilon else 1e-10)

    result = {
        "operation": "normalize_signal",
        "observed": observed,
        "reference": reference,
        "normalized_value": result_obj.normalized_value,
        "matches": result_obj.matches,
        "error": result_obj.error,
        "epsilon": result_obj.epsilon,
        "equation": "Z = z / z_ref"
    }
    print_json(result)


def validate_cmd(args):
    """Validate a JSON file against schema."""
    file_path = Path(args.file)

    if not file_path.exists():
        print(f"Error: File not found: {file_path}", file=sys.stderr)
        sys.exit(1)

    try:
        with open(file_path) as f:
            data = json.load(f)
    except json.JSONDecodeError as e:
        print(f"Error: Invalid JSON: {e}", file=sys.stderr)
        sys.exit(1)

    # Try to determine if it's a node or bridge based on content
    is_node = "address" in data and "status" in data and "title" in data
    is_bridge = "source" in data and "target" in data and "relation" in data

    if is_node:
        node_schema_path = schema_path("node")
        is_valid, errors = validate_node_json(data, node_schema_path)
        obj_type = "node"
    elif is_bridge:
        bridge_schema_path = schema_path("bridge")
        is_valid, errors = validate_bridge_json(data, bridge_schema_path)
        obj_type = "bridge"
    else:
        print("Error: Cannot determine if object is node or bridge", file=sys.stderr)
        sys.exit(1)

    result = {
        "file": str(file_path),
        "type": obj_type,
        "valid": is_valid,
        "errors": errors if not is_valid else []
    }
    print_json(result)

    if not is_valid:
        sys.exit(1)


def energy_from_freq_cmd(args):
    """Calculate energy from frequency."""
    frequency_hz = float(args.frequency)
    energy_j = energy_from_frequency(frequency_hz)
    result = {
        "operation": "energy_from_frequency",
        "input_frequency_hz": frequency_hz,
        "output_energy_j": energy_j,
        "equation": "E = h*f"
    }
    print_json(result)


def address_cmd(args):
    """Parse or create a UPI address."""
    if args.parse:
        try:
            addr = Address.from_string(args.parse)
            result = {
                "address_string": args.parse,
                "domain": addr.domain,
                "generation": addr.generation,
                "torus": addr.torus,
                "node": addr.node
            }
        except ValueError as e:
            print(f"Error: {e}", file=sys.stderr)
            sys.exit(1)
    else:
        addr = Address(args.domain, int(args.generation), args.torus, args.node)
        result = {
            "address_string": str(addr),
            "domain": addr.domain,
            "generation": addr.generation,
            "torus": addr.torus,
            "node": addr.node
        }
    print_json(result)


def debug_index_cmd(args):
    """Generate an automated UPI error report and exploded map."""
    root = Path(args.path)
    if not root.exists():
        print(f"Error: Path not found: {root}", file=sys.stderr)
        sys.exit(1)

    report = generate_debug_report(root, odins_eye=args.odins_eye)
    rendered = (
        render_debug_markdown(report)
        if args.format == "markdown"
        else json.dumps(report, indent=2)
    )
    if args.output:
        Path(args.output).write_text(rendered + "\n", encoding="utf-8")
    else:
        print(rendered)

    if args.strict and report["findings"]:
        sys.exit(1)


def main():
    """Main CLI entry point."""
    import argparse

    parser = argparse.ArgumentParser(
        prog="upi",
        description="Universal Physics Index CLI"
    )
    parser.add_argument("--version", action="version", version=f"%(prog)s {__version__}")

    subparsers = parser.add_subparsers(dest="command", help="Command to run")

    # frequency-to-mass
    fm = subparsers.add_parser("frequency-to-mass", help="Convert frequency to mass")
    fm.add_argument("frequency", type=float, help="Frequency in Hertz")
    fm.set_defaults(func=frequency_to_mass)

    # mass-to-frequency
    mf = subparsers.add_parser("mass-to-frequency", help="Convert mass to frequency")
    mf.add_argument("mass", type=float, help="Mass in kilograms")
    mf.set_defaults(func=mass_to_frequency)

    # index8
    i8 = subparsers.add_parser("index8", help="Calculate 8 Hz dimensionless index")
    i8.add_argument("--frequency", type=float, help="Frequency in Hertz")
    i8.add_argument("--mass", type=float, help="Mass in kilograms")
    i8.set_defaults(func=index8_cmd)

    # energy-from-frequency
    ef = subparsers.add_parser("energy-from-frequency", help="Calculate energy from frequency")
    ef.add_argument("frequency", type=float, help="Frequency in Hertz")
    ef.set_defaults(func=energy_from_freq_cmd)

    # normalize
    norm = subparsers.add_parser("normalize", help="Normalize signal Z = z / z_ref")
    norm.add_argument("--observed", type=float, required=True, help="Observed signal")
    norm.add_argument("--reference", type=float, required=True, help="Reference signal")
    norm.add_argument("--epsilon", type=float, help="Match tolerance")
    norm.set_defaults(func=normalize_cmd)

    # validate
    val = subparsers.add_parser("validate", help="Validate JSON against schema")
    val.add_argument("file", help="JSON file to validate")
    val.set_defaults(func=validate_cmd)

    # address
    addr = subparsers.add_parser("address", help="Parse or create UPI address")
    addr.add_argument("--parse", help="Parse UPI address string")
    addr.add_argument("--domain", help="Domain (for creation)")
    addr.add_argument("--generation", type=int, help="Generation (for creation)")
    addr.add_argument("--torus", help="Torus (for creation)")
    addr.add_argument("--node", help="Node identifier (for creation)")
    addr.set_defaults(func=address_cmd)

    # debug-index
    debug = subparsers.add_parser(
        "debug-index",
        help="Generate a UPI error report and exploded physics/code map",
    )
    debug.add_argument("path", nargs="?", default="data", help="Directory of UPI JSON records")
    debug.add_argument("--output", help="Write the report to a file")
    debug.add_argument("--format", choices=("json", "markdown"), default="json")
    debug.add_argument(
        "--odins-eye",
        action="store_true",
        help="Find hidden paths, conflicting identities, and mirrored records",
    )
    debug.add_argument(
        "--strict",
        action="store_true",
        help="Exit non-zero when the report contains findings",
    )
    debug.set_defaults(func=debug_index_cmd)

    args = parser.parse_args()

    if not hasattr(args, "func"):
        parser.print_help()
        sys.exit(1)

    try:
        args.func(args)
    except Exception as e:
        print(f"Error: {e}", file=sys.stderr)
        sys.exit(1)


if __name__ == "__main__":
    main()
