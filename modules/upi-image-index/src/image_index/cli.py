"""Command-line interface for upi-image-index.

Commands
--------
upi-img index   <image>        Index an image file → data/images/<hash>.json
upi-img decode  <node.json>    Show extraction layers for a node
upi-img scan    [directory]    Validate all indexed nodes against schema
upi-img evolve  [--path dir]   Propose FORM_SIMILAR bridges across nodes
upi-img shadow  <image>        Run shadow-layer analysis on an image
"""

from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path

# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------


def _schema_path() -> Path:
    return Path(__file__).parent / "schemas" / "image-node.schema.json"


def _print_json(data: object) -> None:
    print(json.dumps(data, indent=2, ensure_ascii=False))


# ---------------------------------------------------------------------------
# Command implementations
# ---------------------------------------------------------------------------


def cmd_index(args: argparse.Namespace) -> None:
    """Index an image file and write a UPI image-node JSON."""
    from image_index.classifier import ScientificStatus, build_image_node
    from image_index.extractor import extract_all_layers, hash_file

    image_path = Path(args.image)
    if not image_path.exists():
        print(f"Error: image not found: {image_path}", file=sys.stderr)
        sys.exit(1)

    output_dir = Path(args.output) if args.output else Path("data/images")
    output_dir.mkdir(parents=True, exist_ok=True)

    print(f"Hashing {image_path.name} ...", file=sys.stderr)
    image_hash = hash_file(image_path)

    tokens = [t.strip() for t in args.tokens.split(",")] if args.tokens else []
    print(f"Extracting layers (tokens: {tokens or 'none'}) ...", file=sys.stderr)
    layers = extract_all_layers(image_path, manual_text_tokens=tokens)

    upi_address = args.address or f"UPI<IMAGE,1,UNKNOWN,{image_hash[:16].upper()}>"
    title = args.title or image_path.stem
    description = args.description or f"Image indexed from {image_path.name}"
    status = ScientificStatus(args.status) if args.status else ScientificStatus.SYM
    tag_list = [t.strip() for t in args.tags.split(",")] if args.tags else []

    node = build_image_node(
        image_hash=image_hash,
        upi_address=upi_address,
        title=title,
        description=description,
        extraction_layers=layers,
        primary_status=status,
        generation=int(args.generation),
        tags=tag_list,
    )

    output_file = output_dir / f"{image_hash[:32]}.json"
    output_file.write_text(
        json.dumps(node, indent=2, ensure_ascii=False) + "\n", encoding="utf-8"
    )
    print(f"Indexed:  {output_file}")
    print(f"Address:  {upi_address}")
    print(f"Status:   {status.value}")
    print(f"Hash:     {image_hash[:32]}...")
    print(f"Layers:   {len(layers)}")


def cmd_scan(args: argparse.Namespace) -> None:
    """Scan indexed image-node JSON files for schema errors."""
    try:
        import jsonschema
    except ImportError:
        print("Error: jsonschema not installed. Run: pip install jsonschema", file=sys.stderr)
        sys.exit(1)

    data_dir = Path(args.path)
    schema_file = _schema_path()

    if not data_dir.exists():
        print(f"Error: directory not found: {data_dir}", file=sys.stderr)
        sys.exit(1)

    if not schema_file.exists():
        print(f"Error: schema not found: {schema_file}", file=sys.stderr)
        sys.exit(1)

    schema = json.loads(schema_file.read_text(encoding="utf-8"))
    validator = jsonschema.Draft7Validator(schema)

    json_files = sorted(data_dir.rglob("*.json"))
    findings: list[dict] = []
    valid_count = 0

    for jf in json_files:
        try:
            data = json.loads(jf.read_text(encoding="utf-8"))
        except json.JSONDecodeError as exc:
            findings.append({"file": jf.name, "code": "INVALID_JSON", "message": str(exc)})
            continue

        errors = list(validator.iter_errors(data))
        if errors:
            for err in errors:
                findings.append({
                    "file": jf.name,
                    "code": "SCHEMA_ERROR",
                    "path": list(err.absolute_path),
                    "message": err.message,
                })
        else:
            valid_count += 1

    _print_json({
        "files_scanned": len(json_files),
        "valid": valid_count,
        "findings": len(findings),
        "details": findings,
    })

    if findings:
        sys.exit(1)


def cmd_decode(args: argparse.Namespace) -> None:
    """Show extraction layers for an image-node JSON file."""
    node_path = Path(args.node)
    if not node_path.exists():
        print(f"Error: node not found: {node_path}", file=sys.stderr)
        sys.exit(1)

    try:
        data = json.loads(node_path.read_text(encoding="utf-8"))
    except json.JSONDecodeError as exc:
        print(f"Error: invalid JSON: {exc}", file=sys.stderr)
        sys.exit(1)

    layers = data.get("extraction_layers", [])
    img_hash = data.get("image_hash_sha256", "N/A")

    print(f"Address:    {data.get('address', 'N/A')}")
    print(f"Title:      {data.get('title', 'N/A')}")
    print(f"Status:     {data.get('status', 'N/A')}")
    print(f"Generation: {data.get('generation', 'N/A')}")
    print(f"Image hash: {img_hash[:32]}{'...' if len(img_hash) > 32 else ''}")
    print(f"\nExtraction layers ({len(layers)}):")

    for layer in layers:
        layer_type = layer.get("layer_type", "UNKNOWN")
        status = layer.get("status", "?")
        n_findings = len(layer.get("findings", []))
        stop = ""
        if "stop_reason" in layer:
            stop = f" | STOP: {layer['stop_reason'][:60]}..."
        print(f"  {layer_type:<25}  {status:4}  findings={n_findings}{stop}")
        if args.verbose:
            for finding in layer.get("findings", []):
                print(f"      • {finding}")


def cmd_evolve(args: argparse.Namespace) -> None:
    """Search for FORM_SIMILAR patterns across all indexed image nodes."""
    data_dir = Path(args.path)
    if not data_dir.exists():
        print(f"Error: directory not found: {data_dir}", file=sys.stderr)
        sys.exit(1)

    nodes: list[dict] = []
    for jf in sorted(data_dir.rglob("*.json")):
        try:
            d = json.loads(jf.read_text(encoding="utf-8"))
            nodes.append(d)
        except Exception:
            continue

    if len(nodes) < 2:
        print("Need at least 2 indexed nodes to search for FORM_SIMILAR patterns.")
        return

    proposals: list[dict] = []
    for i, a in enumerate(nodes):
        for j, b in enumerate(nodes):
            if j <= i:
                continue
            shared_tags = sorted(set(a.get("tags", [])) & set(b.get("tags", [])))
            if shared_tags:
                proposals.append({
                    "relation": "FORM_SIMILAR",
                    "status": "HYP",
                    "source": a.get("address"),
                    "target": b.get("address"),
                    "shared_tags": shared_tags,
                    "confusion_guard": (
                        "Shared tags indicate possible similarity. "
                        "Independent evidence required before promotion beyond HYP. "
                        "Save as bridge JSON after manual review."
                    ),
                })

    if not proposals:
        print("No FORM_SIMILAR proposals found (no shared tags).")
        return

    _print_json({"proposals": proposals, "count": len(proposals)})
    print(
        f"\n{len(proposals)} proposal(s). Review each manually; save as bridge JSON if confirmed.",
        file=sys.stderr,
    )


def cmd_shadow(args: argparse.Namespace) -> None:
    """Run shadow-layer analysis on a raw image file."""
    from image_index.shadow import analyze_shadow_layer

    image_path = Path(args.image)
    if not image_path.exists():
        print(f"Error: image not found: {image_path}", file=sys.stderr)
        sys.exit(1)

    result = analyze_shadow_layer(image_path)
    _print_json(result)


# ---------------------------------------------------------------------------
# Entry point
# ---------------------------------------------------------------------------


def main() -> None:
    parser = argparse.ArgumentParser(
        prog="upi-img",
        description="UPI Image Index — extract, classify, and index image observations",
    )
    parser.add_argument("--version", action="version", version="upi-image-index 0.1.0")
    sub = parser.add_subparsers(dest="command")

    # index
    p_index = sub.add_parser("index", help="Index an image file")
    p_index.add_argument("image", help="Path to image file (kept in vault/, never committed)")
    p_index.add_argument("--output", help="Output directory (default: data/images)")
    p_index.add_argument("--address", help="UPI address, e.g. UPI<IMAGE,1,TORUS,NODE>")
    p_index.add_argument("--title", help="Node title")
    p_index.add_argument("--description", help="Node description")
    p_index.add_argument(
        "--status",
        choices=["EST", "DER", "HYP", "SYM", "STOP", "ERR"],
        default="SYM",
    )
    p_index.add_argument("--tokens", help="Comma-separated text tokens for symbol extraction")
    p_index.add_argument("--tags", help="Comma-separated tags")
    p_index.add_argument("--generation", type=int, default=1, help="Generation counter")
    p_index.set_defaults(func=cmd_index)

    # decode
    p_decode = sub.add_parser("decode", help="Show extraction layers for a node JSON")
    p_decode.add_argument("node", help="Path to image-node JSON file")
    p_decode.add_argument("-v", "--verbose", action="store_true", help="Show all findings")
    p_decode.set_defaults(func=cmd_decode)

    # scan
    p_scan = sub.add_parser("scan", help="Validate all image-node JSON files against schema")
    p_scan.add_argument("path", nargs="?", default="data/images", help="Directory to scan")
    p_scan.set_defaults(func=cmd_scan)

    # evolve
    p_evolve = sub.add_parser("evolve", help="Find FORM_SIMILAR patterns across nodes")
    p_evolve.add_argument("--path", default="data/images", help="Directory of indexed nodes")
    p_evolve.set_defaults(func=cmd_evolve)

    # shadow
    p_shadow = sub.add_parser("shadow", help="Run shadow-layer analysis on an image file")
    p_shadow.add_argument("image", help="Path to image file")
    p_shadow.set_defaults(func=cmd_shadow)

    args = parser.parse_args()
    if not hasattr(args, "func"):
        parser.print_help()
        sys.exit(1)

    try:
        args.func(args)
    except Exception as exc:
        print(f"Error: {exc}", file=sys.stderr)
        sys.exit(1)


if __name__ == "__main__":
    main()
