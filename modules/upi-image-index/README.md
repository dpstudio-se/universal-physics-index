# upi-image-index

`upi-image-index` is a standalone 5-layer image extraction engine with UPI status classification. It converts visual artifacts, diagrams, and image metadata into classified UPI nodes and evidence structures without promoting visual motifs into established physical laws.

## 5-Layer Extraction Architecture

| Layer | Name | Description | UPI Status |
|---|---|---|---|
| **Layer 1** | `PIXEL_FACTS` | File metadata, SHA-256 content hash, size, format, raw dimensions | `EST` |
| **Layer 2** | `GEOMETRY` | Aspect ratio, resolution, color channel structure, geometric contours | `DER` |
| **Layer 3** | `TEXT_SYMBOLS` | OCR extracted text, diagram labels, annotations, formula text | `DER` / `HYP` |
| **Layer 4** | `EVIDENCE_BOUNDARIES` | Falsifiable hypothesis extraction, missing mechanisms, stop reasons | `HYP` / `STOP` |
| **Layer 5** | `SYMBOLIC_GLOSSARY` | Visual motifs, naming context, documentation framing, art references | `SYM` |

## Non-Negotiable Boundary Rules

- **Visual motifs (`SYM`)** are framing elements only. They never confer physical evidence, experimental verification, or hidden software authority.
- Image metadata (file hash, byte size, format) is `EST` within the narrow source-fact domain.
- Structural relations derived from images are `DER`.
- Claims depicted in diagrams remain `STOP` or `HYP` until independently tested.
