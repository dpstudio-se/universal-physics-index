# upi-image-index

UPI-based image feature extraction and indexing module.

Extracts machine-readable observations from images across five layers — visible text,
geometric structure, symbolic elements, colour channels, and shadow hypotheses — and
stores each observation as a UPI-classified node JSON. Status follows the UPI evidence
model: `EST`, `DER`, `HYP`, `SYM`, `STOP`, `ERR`.

This module is **standalone**: it works without the parent `universal-physics-index`
package and can be extracted to its own private repository at any time.

## Install

```bash
# Basic (stdlib + jsonschema only)
pip install -e .

# With Pillow and pytesseract for full extraction
pip install -e ".[enhanced]"

# Development
pip install -e ".[dev]"
```

## Quick start

```bash
# Index an image (reads from vault/, writes JSON to data/images/)
upi-img index vault/my_image.png \
  --address "UPI<IMAGE,1,TORUS,MY_NODE>" \
  --title "My image" \
  --status SYM \
  --tokens "TF,DNA,TORUS"

# Show extracted layers for a node
upi-img decode data/images/<hash>.json --verbose

# Scan all indexed nodes for schema errors
upi-img scan data/images/

# Find FORM_SIMILAR patterns across nodes
upi-img evolve --path data/images/

# Run shadow-layer analysis on a raw image
upi-img shadow vault/my_image.png
```

## Structure

```
upi-image-index/
├── pyproject.toml
├── src/image_index/
│   ├── classifier.py      # UPI status classification
│   ├── extractor.py       # 5-layer feature extraction
│   ├── shadow.py          # Statistical shadow-layer analysis
│   ├── cli.py             # upi-img CLI
│   └── schemas/
│       └── image-node.schema.json
├── data/images/           # Index nodes (JSON only, no image files)
├── vault/                 # Raw images — never committed
└── tests/
```

## Vault

Store raw image files in `vault/`. This directory is `.gitignore`d; only metadata
hashes and extracted observations are committed. See `vault/README.md`.

## Evidence boundaries

| Layer type          | Default status | Requirement to promote      |
|---------------------|----------------|-----------------------------|
| `VISIBLE_TEXT`      | EST (≥0.95)    | Reproducible OCR            |
| `METADATA_EXIF`     | EST            | Direct file read            |
| `GEOMETRIC_STRUCTURE` | DER          | Pixel-level measurement     |
| `COLOR_CHANNEL`     | DER            | Pixel statistics            |
| `SYMBOLIC_ELEMENT`  | SYM            | Never auto-promotes         |
| `SHADOW_LAYER`      | HYP            | Independent stego tool      |

## Testing

```bash
cd modules/upi-image-index
pytest tests/ -v
```
