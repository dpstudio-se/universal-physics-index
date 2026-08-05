"""CLI entry point for upi-image-index."""

import argparse
import json
import sys
from pathlib import Path

from .core import extract_image_layers


def main() -> None:
    parser = argparse.ArgumentParser(
        prog="upi-image-index",
        description="5-layer image extraction with UPI status classification",
    )
    parser.add_argument("file", help="Path to image or text artifact")
    args = parser.parse_args()

    file_path = Path(args.file)
    if not file_path.exists():
        print(f"Error: File not found: {file_path}", file=sys.stderr)
        sys.exit(1)

    result = extract_image_layers(file_path)
    output = {
        "operation": "upi_image_index_5layer_extraction",
        "image_name": result.image_name,
        "content_hash_sha256": result.content_hash_sha256,
        "layers": {
            "layer1_pixel_facts": result.layer1_pixel_facts,
            "layer2_geometry": result.layer2_geometry,
            "layer3_text_symbols": result.layer3_text_symbols,
            "layer4_evidence_boundaries": result.layer4_evidence_boundaries,
            "layer5_symbolic_glossary": result.layer5_symbolic_glossary,
        },
    }
    print(json.dumps(output, indent=2))


if __name__ == "__main__":
    main()
