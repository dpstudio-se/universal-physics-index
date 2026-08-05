"""UPI status classification for image extraction layers.

This module is intentionally standalone: it does not import the parent
`universal-physics-index` package so that `upi-image-index` can be installed
and used independently.
"""

from __future__ import annotations

from enum import Enum
from hashlib import sha256
from typing import Any


class ScientificStatus(str, Enum):
    """Scientific status labels — mirrors UPI core; kept local for standalone use.

    EST = established (reproducible, source-confirmed)
    DER = derived from declared assumptions
    HYP = falsifiable hypothesis, unverified
    STOP = blocked; named evidence missing
    ERR = contradicted or superseded
    SYM = symbolic / conceptual only
    """

    EST = "EST"
    DER = "DER"
    HYP = "HYP"
    STOP = "STOP"
    ERR = "ERR"
    SYM = "SYM"


# Default status for each extraction layer type
LAYER_STATUS_MAP: dict[str, ScientificStatus] = {
    "VISIBLE_TEXT": ScientificStatus.EST,
    "METADATA_EXIF": ScientificStatus.EST,
    "GEOMETRIC_STRUCTURE": ScientificStatus.DER,
    "COLOR_CHANNEL": ScientificStatus.DER,
    "SYMBOLIC_ELEMENT": ScientificStatus.SYM,
    "SHADOW_LAYER": ScientificStatus.HYP,
}

# Minimum OCR confidence to retain EST status for VISIBLE_TEXT
OCR_EST_THRESHOLD: float = 0.95


def content_hash(data: str) -> str:
    """Return the SHA-256 hex digest of a UTF-8 encoded string."""
    return sha256(data.encode("utf-8")).hexdigest()


def classify_layer(
    layer_type: str,
    source: str,  # noqa: ARG001 — reserved for future source-specific overrides
    confidence: float | None = None,
) -> ScientificStatus:
    """Assign UPI status to an extraction layer result.

    Args:
        layer_type: One of the recognised LAYER_STATUS_MAP keys.
        source: Extraction method name (reserved for future use).
        confidence: Optional confidence score in [0.0, 1.0].

    Returns:
        ScientificStatus appropriate for this layer and confidence.
    """
    base = LAYER_STATUS_MAP.get(layer_type, ScientificStatus.HYP)

    # Downgrade VISIBLE_TEXT / METADATA_EXIF if confidence is too low
    if base == ScientificStatus.EST and confidence is not None:
        if confidence < OCR_EST_THRESHOLD:
            return ScientificStatus.DER

    return base


def build_extraction_layer(
    layer_type: str,
    findings: list[str],
    source: str,
    confidence: float | None = None,
    extractor_version: str = "0.1.0",
    stop_reason: str | None = None,
) -> dict[str, Any]:
    """Build a single extraction layer record.

    Args:
        layer_type: Layer type constant (e.g. "VISIBLE_TEXT").
        findings: List of human-readable observation strings. Values are
            stored as-is; raw pixel values must never be included.
        source: Name of the extraction method.
        confidence: Optional confidence score.
        extractor_version: Semver string of the extractor.
        stop_reason: Required when status resolves to STOP or HYP; describes
            what is missing for promotion to a higher status.

    Returns:
        Dict conforming to the extraction_layer definition in image-node.schema.json.
    """
    status = classify_layer(layer_type, source, confidence)

    # HYP layers always need a stop_reason
    if status == ScientificStatus.HYP and not stop_reason:
        stop_reason = (
            "Independent verification required to promote this layer beyond HYP. "
            "Use a dedicated tool (e.g. stegdetect, zsteg, binwalk) for confirmation."
        )

    findings_text = "\n".join(findings)
    layer: dict[str, Any] = {
        "layer_type": layer_type,
        "status": status.value,
        "source": source,
        "content_hash": content_hash(findings_text),
        "findings": findings,
        "extractor_version": extractor_version,
        "verification_type": "software_test",
        "claims_experimental_verification": False,
    }

    if confidence is not None:
        layer["confidence"] = round(float(confidence), 6)

    if stop_reason:
        layer["stop_reason"] = stop_reason

    if status == ScientificStatus.SYM:
        layer["confusion_guard"] = (
            "Symbol matches are pattern recognition, not physical evidence. "
            "SYM status never auto-promotes to DER or EST by accumulation."
        )

    return layer


def build_image_node(
    image_hash: str,
    upi_address: str,
    title: str,
    description: str,
    extraction_layers: list[dict[str, Any]],
    primary_status: ScientificStatus = ScientificStatus.SYM,
    generation: int = 1,
    parent_hash: str | None = None,
    prompt_fingerprint: str | None = None,
    tags: list[str] | None = None,
    information_layer: str = "PRIVATE",
) -> dict[str, Any]:
    """Build a complete image-node record.

    The source image file is referenced only by its SHA-256 hash. File paths
    are never stored in the node.

    Args:
        image_hash: SHA-256 hex digest of the source image file.
        upi_address: UPI address string, e.g. ``UPI<IMAGE,1,TORUS,NODE>``.
        title: Short human-readable title.
        description: Longer description of the image and its content.
        extraction_layers: List of layer dicts from ``build_extraction_layer``.
        primary_status: Overall node status (typically SYM for image nodes).
        generation: Counter incremented on each re-analysis of the same image.
        parent_hash: SHA-256 of the previous generation's node content, or None.
        prompt_fingerprint: SHA-256 of the extraction prompt used, or None.
        tags: Optional tag list for FORM_SIMILAR discovery.
        information_layer: PRIVATE, PUBLIC, or ACADEMIC.

    Returns:
        Dict conforming to image-node.schema.json.
    """
    return {
        "address": upi_address,
        "title": title,
        "description": description,
        "status": primary_status.value,
        "information_layer": information_layer,
        "image_hash_sha256": image_hash,
        "extraction_layers": extraction_layers,
        "generation": generation,
        "parent_hash": parent_hash,
        "prompt_fingerprint": prompt_fingerprint,
        "verification_type": "software_test",
        "claims_experimental_verification": False,
        "confusion_guard": (
            "Image indexing establishes software-extracted observations only. "
            "Pattern matches, geometric detections, and shadow hypotheses require "
            "independent verification before promotion beyond HYP or SYM."
        ),
        "tags": tags or [],
        "version": "0.1.0",
    }
