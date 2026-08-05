"""Command-line interface for UPI."""

import json
import sys
from pathlib import Path

from . import (
    EPSILON_Z_DEFAULT,
    __version__,
    energy_from_frequency,
    frequency_from_mass,
    index8_from_frequency,
    index8_from_mass,
    mass_from_frequency,
    signal_match,
    validate_bridge_json,
    validate_json_schema,
    validate_node_json,
)
from .debug import generate_debug_report, render_debug_markdown
from .models import Address
from .schema_resources import schema_path


def print_json(data):
    """Print data as pretty JSON."""
    print(json.dumps(data, indent=2, ensure_ascii=False))


def frequency_to_mass(args):
    """Convert frequency to mass-energy equivalent."""
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
    """Convert invariant rest mass to frequency."""
    mass_kg = float(args.mass)
    frequency_hz = frequency_from_mass(mass_kg)
    result = {
        "operation": "mass_to_frequency",
        "input_mass_kg": mass_kg,
        "output_frequency_hz": frequency_hz,
        "equation": "f = m*c^2 / h",
    }
    print_json(result)


def index8_cmd(args):
    """Calculate the dimensionless 8 Hz reference index."""
    if args.frequency is not None:
        frequency_hz = float(args.frequency)
        result = {
            "operation": "index8_from_frequency",
            "input_frequency_hz": frequency_hz,
            "output_n8": index8_from_frequency(frequency_hz),
            "equation": "N8 = f / (8 Hz)",
        }
    elif args.mass is not None:
        mass_kg = float(args.mass)
        result = {
            "operation": "index8_from_mass",
            "input_mass_kg": mass_kg,
            "output_n8": index8_from_mass(mass_kg),
            "equation": "N8 = m*c^2 / (8*h)",
        }
    else:  # pragma: no cover - argparse enforces the mutually exclusive group
        raise ValueError("--frequency or --mass required")
    print_json(result)


def normalize_cmd(args):
    """Normalize a signal and compare it with one."""
    observed = float(args.observed)
    reference = float(args.reference)
    epsilon = float(args.epsilon) if args.epsilon is not None else EPSILON_Z_DEFAULT
    result_obj = signal_match(observed, reference, epsilon=epsilon)

    result = {
        "operation": "normalize_signal",
        "observed": observed,
        "reference": reference,
        "normalized_value": result_obj.normalized_value,
        "matches": result_obj.matches,
        "error": result_obj.error,
        "epsilon": result_obj.epsilon,
        "equation": "Z = z / z_ref",
    }
    print_json(result)


def validate_cmd(args):
    """Validate a JSON file against its routed UPI schema."""
    file_path = Path(args.file)

    if not file_path.exists():
        print(f"Error: File not found: {file_path}", file=sys.stderr)
        sys.exit(1)

    try:
        with open(file_path, encoding="utf-8") as f:
            data = json.load(f)
    except (OSError, UnicodeError) as error:
        print(f"Error: Could not read JSON file: {error}", file=sys.stderr)
        sys.exit(1)
    except json.JSONDecodeError as error:
        print(f"Error: Invalid JSON: {error}", file=sys.stderr)
        sys.exit(1)

    if not isinstance(data, dict):
        print("Error: Top-level JSON value must be an object", file=sys.stderr)
        sys.exit(1)

    is_bridge = {"source", "target", "relation"} <= data.keys()
    is_theory = {"address", "title", "description", "status", "domain", "scope"} <= data.keys()
    is_node = {"address", "status", "title"} <= data.keys()

    if is_bridge:
        is_valid, errors = validate_bridge_json(data, schema_path("bridge"))
        obj_type = "bridge"
    elif is_theory:
        is_valid, errors = validate_json_schema(data, schema_path("theory"))
        obj_type = "theory"
    elif is_node:
        is_valid, errors = validate_node_json(data, schema_path("node"))
        obj_type = "node"
    else:
        print("Error: Cannot determine if object is node, bridge, or theory", file=sys.stderr)
        sys.exit(1)

    result = {
        "file": str(file_path),
        "type": obj_type,
        "valid": is_valid,
        "errors": errors if not is_valid else [],
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
        "equation": "E = h*f",
    }
    print_json(result)


def address_cmd(args):
    """Parse or create a UPI address."""
    if args.parse is not None:
        addr = Address.from_string(args.parse)
    else:
        missing = [
            name
            for name in ("domain", "generation", "torus", "node")
            if getattr(args, name) is None
        ]
        if missing:
            raise ValueError(
                "Address creation requires --domain, --generation, --torus, and --node"
            )
        addr = Address(args.domain, args.generation, args.torus, args.node)

    result = {
        "address_string": str(addr),
        "domain": addr.domain,
        "generation": addr.generation,
        "torus": addr.torus,
        "node": addr.node,
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


def auto_map_cmd(args):
    """Auto-map LLM context text or file into UPI Physics Engine & DNA Memory."""
    from .auto_mapper import LLMContextAutoMapper

    mapper = LLMContextAutoMapper()

    if args.file:
        file_path = Path(args.file)
        if not file_path.exists():
            print(f"Error: File not found: {file_path}", file=sys.stderr)
            sys.exit(1)
        content = file_path.read_text(encoding="utf-8")
        if file_path.suffix == ".json":
            try:
                data = json.loads(content)
                if isinstance(data, list):
                    res = mapper.map_structured_context(data)
                elif isinstance(data, dict):
                    res = mapper.map_structured_context([data])
                else:
                    res = mapper.map_text_context(str(data))
            except json.JSONDecodeError:
                res = mapper.map_text_context(content)
        else:
            res = mapper.map_text_context(content)
    elif args.text:
        res = mapper.map_text_context(args.text)
    else:
        print("Error: --text or --file required for auto-map", file=sys.stderr)
        sys.exit(1)

    output = {
        "operation": "auto_map_llm_context",
        "nodes_extracted": res.nodes_extracted,
        "nodes_written": res.nodes_written,
        "bridges_written": res.bridges_written,
        "dna_classification": res.dna_classification,
        "physics_evaluations": res.physics_evaluations,
        "odin_report": res.odin_report,
    }
    print_json(output)


def odin_status_cmd(args):
    """Generate OdinOS Core Kernel status report."""
    from .odin_kernel import OdinCoreKernel

    kernel = OdinCoreKernel()
    print_json(kernel.generate_status_report())


def odin_eval_cmd(args):
    """Evaluate V_odin formula and TF1776 transparency scan."""
    from .odin_kernel import OdinCoreKernel

    kernel = OdinCoreKernel()
    freq = float(args.frequency) if args.frequency else 8.0
    formula_res = kernel.evaluate_odin_formula(freq)
    text = args.text if args.text else ""
    tf1776_res = kernel.run_selfish_gene_loop(text)

    output = {
        "formula_evaluation": formula_res,
        "tf1776_report": {
            "transparency_score": tf1776_res.transparency_score,
            "censorship_detected": tf1776_res.censorship_detected,
            "iterations_run": tf1776_res.iterations_run,
            "audit_findings": tf1776_res.audit_findings,
        },
    }
    print_json(output)


def aeco_run_cmd(args):
    """Run UPI-AECΩ evolution cycle."""
    sys.path.insert(0, str(Path(__file__).parent.parent.parent / "modules" / "upi-aeco" / "src"))
    from upi_aeco.core.evolution_loop import evolution_cycle

    version_id = getattr(args, "version_id", "v0.1.0-initial")
    result = evolution_cycle(version_id)
    print_json(result)


def aeco_status_cmd(args):
    """View UPI-AECΩ self-model snapshot."""
    sys.path.insert(0, str(Path(__file__).parent.parent.parent / "modules" / "upi-aeco" / "src"))
    from upi_aeco.core.observer import observe

    model = observe()
    print_json(model)


def main():
    """Main CLI entry point."""
    import argparse

    parser = argparse.ArgumentParser(
        prog="upi",
        description="Universal Physics Index CLI",
    )
    parser.add_argument("--version", action="version", version=f"%(prog)s {__version__}")

    subparsers = parser.add_subparsers(dest="command", help="Command to run")

    fm = subparsers.add_parser("frequency-to-mass", help="Convert frequency to mass")
    fm.add_argument("frequency", type=float, help="Frequency in Hertz")
    fm.set_defaults(func=frequency_to_mass)

    mf = subparsers.add_parser("mass-to-frequency", help="Convert mass to frequency")
    mf.add_argument("mass", type=float, help="Mass in kilograms")
    mf.set_defaults(func=mass_to_frequency)

    i8 = subparsers.add_parser("index8", help="Calculate 8 Hz dimensionless index")
    i8_input = i8.add_mutually_exclusive_group(required=True)
    i8_input.add_argument("--frequency", type=float, help="Frequency in Hertz")
    i8_input.add_argument("--mass", type=float, help="Mass in kilograms")
    i8.set_defaults(func=index8_cmd)

    ef = subparsers.add_parser("energy-from-frequency", help="Calculate energy from frequency")
    ef.add_argument("frequency", type=float, help="Frequency in Hertz")
    ef.set_defaults(func=energy_from_freq_cmd)

    norm = subparsers.add_parser("normalize", help="Normalize signal Z = z / z_ref")
    norm.add_argument("--observed", type=float, required=True, help="Observed signal")
    norm.add_argument("--reference", type=float, required=True, help="Reference signal")
    norm.add_argument("--epsilon", type=float, help="Match tolerance")
    norm.set_defaults(func=normalize_cmd)

    val = subparsers.add_parser("validate", help="Validate JSON against schema")
    val.add_argument("file", help="JSON file to validate")
    val.set_defaults(func=validate_cmd)

    addr = subparsers.add_parser("address", help="Parse or create a UPI address")
    addr.add_argument("--parse", help="Parse UPI address string")
    addr.add_argument("--domain", help="Domain (for creation)")
    addr.add_argument("--generation", type=int, help="Generation (for creation)")
    addr.add_argument("--torus", help="Torus (for creation)")
    addr.add_argument("--node", help="Node identifier (for creation)")
    addr.set_defaults(func=address_cmd)

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

    # auto-map
    auto_map = subparsers.add_parser(
        "auto-map",
        help="Auto-map LLM context text or file into UPI Physics Engine & DNA Memory",
    )
    auto_map.add_argument("--text", help="Raw LLM context text to map")
    auto_map.add_argument("--file", help="File containing LLM context text or JSON")
    auto_map.set_defaults(func=auto_map_cmd)

    # odin-status
    odin_status = subparsers.add_parser(
        "odin-status",
        help="Generate OdinOS Core Kernel Tripp/Trapp/Trull/Torus status report",
    )
    odin_status.set_defaults(func=odin_status_cmd)

    # odin-eval
    odin_eval = subparsers.add_parser(
        "odin-eval",
        help="Evaluate Odin formula and TF1776 transparency scan",
    )
    odin_eval.add_argument("--frequency", type=float, help="Frequency in Hz (default 8 Hz)")
    odin_eval.add_argument("--text", help="Context text for TF1776 transparency scan")
    odin_eval.set_defaults(func=odin_eval_cmd)

    # aeco-run
    aeco_run = subparsers.add_parser(
        "aeco-run",
        help="Run UPI-AECΩ Autonomous Evolution Core Omega cycle",
    )
    aeco_run.add_argument("--version-id", default="v0.1.0-initial", help="Initial version ID")
    aeco_run.set_defaults(func=aeco_run_cmd)

    # aeco-status
    aeco_status = subparsers.add_parser(
        "aeco-status",
        help="View UPI-AECΩ self-model observation snapshot",
    )
    aeco_status.set_defaults(func=aeco_status_cmd)

    args = parser.parse_args()

    if not hasattr(args, "func"):
        parser.print_help()
        sys.exit(1)

    try:
        args.func(args)
    except Exception as error:
        print(f"Error: {error}", file=sys.stderr)
        sys.exit(1)


if __name__ == "__main__":
    main()
