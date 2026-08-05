# upi-image-index Architecture (PR #31)

The `upi-image-index` module ([modules/upi-image-index](file:///c:/Users/Admin/universal-physics-index/modules/upi-image-index)) implements a 5-layer extraction pipeline with explicit UPI status classification (`EST`, `DER`, `HYP`, `STOP`, `SYM`).

## 5-Layer Pipeline

```text
Raw Image Artifact / Diagram
 -> Layer 1 (EST): Pixel Facts, Byte Size, SHA-256 Hash
 -> Layer 2 (DER): Structural Geometry, Color Channels, Contours
 -> Layer 3 (DER/HYP): Text & Symbol OCR Extraction, Formula Labels
 -> Layer 4 (HYP/STOP): Falsifiable Claims, Evidence Boundaries, Stop Reasons
 -> Layer 5 (SYM): Visual Motifs, Naming Context, Symbolic Glossary
```

## Non-Negotiable Scientific Boundaries

1. **Layer 1 (`EST`)**: File metadata (name, size, SHA-256 content hash) is established as a source fact.
2. **Layer 2 (`DER`)**: Derived aspect ratio, geometry, and bounding boxes.
3. **Layer 3 (`DER`/`HYP`)**: Text and labels extracted from diagrams.
4. **Layer 4 (`STOP`)**: Diagram claims require independent experimental verification before physical claim promotion.
5. **Layer 5 (`SYM`)**: Visual motifs (torus, resonance, spirals) serve as symbolic framing only and never confer physical evidence, experimental verification, or hidden software authority.
