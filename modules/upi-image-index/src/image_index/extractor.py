"""Multi-layer image feature extractor.

Operates with Python stdlib only. Enhanced extraction (colour statistics,
OCR, geometric analysis) is available when optional packages are installed:

    pip install "upi-image-index[enhanced]"   # Pillow + pytesseract

Each function returns a dict conforming to the extraction_layer schema. If a
required optional dependency is missing, the layer is returned with status
STOP and a clear ``stop_reason`` describing what must be installed.
"""

from __future__ import annotations

import hashlib
import math
from pathlib import Path
from typing import Any

from .classifier import ScientificStatus, build_extraction_layer, content_hash
from .shadow import analyze_shadow_layer


# ---------------------------------------------------------------------------
# Optional dependency helpers
# ---------------------------------------------------------------------------


def _pil() -> tuple[Any, Any] | tuple[None, None]:
    """Return (PIL.Image, PIL.ExifTags) or (None, None) if Pillow is absent."""
    try:
        from PIL import ExifTags, Image  # type: ignore[import]

        return Image, ExifTags
    except ImportError:
        return None, None


def _tesseract() -> Any | None:
    """Return pytesseract module or None if absent."""
    try:
        import pytesseract  # type: ignore[import]

        return pytesseract
    except ImportError:
        return None


# ---------------------------------------------------------------------------
# Symbolic vocabulary registry
# ---------------------------------------------------------------------------

_SYMBOL_REGISTRY: dict[str, str] = {
    "TF": "Tryckfrihetsförordningen (Swedish Freedom of the Press Act, 1766)",
    "RF": "Regeringsformen (Swedish Instrument of Government)",
    "YGL": "Yttrandefrihetsgrundlagen (Swedish Freedom of Expression Act)",
    "RO": "Riksdagsordningen (Swedish Riksdag Act)",
    "8 HZ": "8 Hz declared normalization reference coordinate (UPI DER)",
    "8HZ": "8 Hz declared normalization reference coordinate (UPI DER)",
    "DNA": "Deoxyribonucleic acid (biology) or metaphorical dual-helix architecture",
    "TORUS": "Toroidal topology (mathematical structure)",
    "KERNEL": "Core operating system component (computing)",
    "SCHUMANN": "Schumann resonance (~7.83 Hz Earth-ionosphere cavity mode, EST)",
    "LANDAUER": "Landauer principle: thermodynamic cost of irreversible bit erasure (EST)",
    "FRANK": "Frank (1953) autocatalytic symmetry-breaking model for homochirality (DER)",
    "VORTEX": "Vortical flow pattern (fluid dynamics) or SYM architecture name",
    "SOAI": "Soai reaction: autocatalytic asymmetric amplification (EST biochemistry)",
    "DIM": "Spatial dimension label (generic)",
    "BRANE": "M-theory brane (SYM/HYP in this context)",
    "Ω": "Omega — density parameter (cosmology EST) or symbolic completion marker (SYM)",
    "ε": "Epsilon — small perturbation term in Frank model equations (DER)",
    "φ": "Golden ratio φ ≈ 1.618 (mathematical EST) or symbolic phi",
    "Φ": "Phi — golden ratio or symbolic identifier (context-dependent)",
    "1766": "Year of Swedish Tryckfrihetsförordningen (historical EST)",
    "ROOTLOCK": "rootLock identifier in Vortex-DNA architecture (SYM)",
}


# ---------------------------------------------------------------------------
# Core extraction functions
# ---------------------------------------------------------------------------


def hash_file(path: Path) -> str:
    """Return the SHA-256 hex digest of a file's raw bytes.

    Args:
        path: Path to any readable file.

    Returns:
        64-character lowercase hex string.
    """
    path = Path(path)
    h = hashlib.sha256()
    with open(path, "rb") as fh:
        for chunk in iter(lambda: fh.read(65536), b""):
            h.update(chunk)
    return h.hexdigest()


def extract_metadata(path: Path) -> dict[str, Any]:
    """Extract file-level and, when Pillow is available, image metadata.

    Always succeeds (stdlib only). Adds EXIF and image dimensions when Pillow
    is installed.

    Args:
        path: Path to the image file.

    Returns:
        METADATA_EXIF extraction layer dict.
    """
    path = Path(path)
    stat = path.stat()
    findings: list[str] = [
        f"filename_hash: {content_hash(path.name)[:16]}",
        f"size_bytes: {stat.st_size}",
        f"extension: {path.suffix.lower()}",
    ]

    source = "file_stats"
    Image, ExifTags = _pil()
    if Image and ExifTags:
        try:
            with Image.open(path) as img:
                w, h = img.size
                findings.append(f"image_format: {img.format}")
                findings.append(f"image_mode: {img.mode}")
                findings.append(f"width_px: {w}")
                findings.append(f"height_px: {h}")
                source = "file_stats_and_pillow"
                exif_data = getattr(img, "_getexif", lambda: None)()
                if exif_data:
                    for tag_id, value in exif_data.items():
                        tag = ExifTags.TAGS.get(tag_id, str(tag_id))
                        if isinstance(value, (str, int, float)):
                            findings.append(f"exif_{tag}: (present)")
        except Exception:
            pass

    return build_extraction_layer(
        layer_type="METADATA_EXIF",
        findings=findings,
        source=source,
        confidence=1.0,
        extractor_version="0.1.0",
    )


def extract_visible_text(path: Path) -> dict[str, Any]:
    """Extract visible text via OCR (requires Pillow + pytesseract).

    Without optional dependencies this returns a STOP layer with installation
    instructions.

    Args:
        path: Path to the image file.

    Returns:
        VISIBLE_TEXT extraction layer dict.
    """
    pytesseract = _tesseract()
    Image, _ = _pil()

    if not (pytesseract and Image):
        return build_extraction_layer(
            layer_type="VISIBLE_TEXT",
            findings=[],
            source="none",
            extractor_version="0.1.0",
            stop_reason=(
                "Pillow and pytesseract required for OCR. "
                "Install with: pip install \"upi-image-index[enhanced]\""
            ),
        )

    try:
        with Image.open(path) as img:
            data = pytesseract.image_to_data(
                img, output_type=pytesseract.Output.DICT
            )
            pairs = [
                (t.strip(), float(c))
                for t, c in zip(data["text"], data["conf"])
                if t.strip() and float(c) > 60
            ]
            unique_tokens = sorted({t for t, _ in pairs})
            confidences = [c for _, c in pairs]
            mean_conf = (
                sum(confidences) / len(confidences) / 100.0 if confidences else 0.0
            )
            findings = [f"ocr_token: {t}" for t in unique_tokens]
            return build_extraction_layer(
                layer_type="VISIBLE_TEXT",
                findings=findings,
                source="pytesseract_ocr",
                confidence=round(min(1.0, max(0.0, mean_conf)), 6),
                extractor_version="0.1.0",
            )
    except Exception as exc:
        return build_extraction_layer(
            layer_type="VISIBLE_TEXT",
            findings=[f"ocr_error: {type(exc).__name__}"],
            source="pytesseract_ocr",
            confidence=0.0,
            extractor_version="0.1.0",
            stop_reason=f"OCR failed: {type(exc).__name__}. Check Tesseract installation.",
        )


def extract_color_channels(path: Path) -> dict[str, Any]:
    """Extract per-channel RGB statistics (requires Pillow).

    Args:
        path: Path to the image file.

    Returns:
        COLOR_CHANNEL extraction layer dict.
    """
    Image, _ = _pil()
    if not Image:
        return build_extraction_layer(
            layer_type="COLOR_CHANNEL",
            findings=[],
            source="none",
            extractor_version="0.1.0",
            stop_reason="Pillow required. Install with: pip install Pillow",
        )

    try:
        with Image.open(path) as img:
            rgb = img.convert("RGB")
            channels = rgb.split()
            channel_names = ("red", "green", "blue")
            findings: list[str] = []
            means: list[float] = []

            for ch_img, ch_name in zip(channels, channel_names):
                pixels = list(ch_img.getdata())
                n = len(pixels)
                mean = sum(pixels) / n
                means.append(mean)
                std = math.sqrt(sum((p - mean) ** 2 for p in pixels) / n)
                findings.append(f"{ch_name}_mean: {round(mean, 3)}")
                findings.append(f"{ch_name}_std: {round(std, 3)}")

            luminance = round(
                0.299 * means[0] + 0.587 * means[1] + 0.114 * means[2], 3
            )
            findings.append(f"luminance_approx: {luminance}")
            findings.append("reference_frame: 2D image plane, sRGB colour space")

            return build_extraction_layer(
                layer_type="COLOR_CHANNEL",
                findings=findings,
                source="pillow_rgb_stats",
                confidence=1.0,
                extractor_version="0.1.0",
            )
    except Exception as exc:
        return build_extraction_layer(
            layer_type="COLOR_CHANNEL",
            findings=[f"error: {type(exc).__name__}"],
            source="pillow_rgb_stats",
            confidence=0.0,
            extractor_version="0.1.0",
            stop_reason=f"Colour extraction failed: {type(exc).__name__}",
        )


def extract_geometric_structure(path: Path) -> dict[str, Any]:
    """Measure pixel-level geometric properties (requires Pillow).

    Computes left-right and top-bottom symmetry scores as proxies for
    geometric regularity. Reference frame is always the 2D image plane.

    Args:
        path: Path to the image file.

    Returns:
        GEOMETRIC_STRUCTURE extraction layer dict.
    """
    Image, _ = _pil()
    if not Image:
        return build_extraction_layer(
            layer_type="GEOMETRIC_STRUCTURE",
            findings=[],
            source="none",
            extractor_version="0.1.0",
            stop_reason="Pillow required. Install with: pip install Pillow",
        )

    try:
        with Image.open(path) as img:
            gray = img.convert("L")
            w, h = gray.size
            pixels = list(gray.getdata())
            n = len(pixels)
            mean_lum = sum(pixels) / n

            # Approximate left-right symmetry via mean comparison
            left = [pixels[y * w + x] for y in range(h) for x in range(w // 2)]
            right = [pixels[y * w + (w - 1 - x)] for y in range(h) for x in range(w // 2)]
            lr_sym = 1.0 - abs(sum(left) / len(left) - sum(right) / len(right)) / (
                max(sum(left) / len(left), sum(right) / len(right)) + 1e-9
            )

            # Approximate top-bottom symmetry
            mid = n // 2
            top = pixels[:mid]
            bottom = pixels[n - mid:]
            tb_sym = 1.0 - abs(sum(top) / len(top) - sum(bottom) / len(bottom)) / (
                max(sum(top) / len(top), sum(bottom) / len(bottom)) + 1e-9
            )

            findings = [
                f"width_px: {w}",
                f"height_px: {h}",
                f"aspect_ratio: {round(w / h, 4)}",
                f"mean_luminance: {round(mean_lum, 3)}",
                f"lr_symmetry_score: {round(lr_sym, 4)}",
                f"tb_symmetry_score: {round(tb_sym, 4)}",
                "reference_frame: 2D image plane projection",
            ]

            return build_extraction_layer(
                layer_type="GEOMETRIC_STRUCTURE",
                findings=findings,
                source="pillow_pixel_analysis",
                confidence=0.70,
                extractor_version="0.1.0",
            )
    except Exception as exc:
        return build_extraction_layer(
            layer_type="GEOMETRIC_STRUCTURE",
            findings=[f"error: {type(exc).__name__}"],
            source="pillow_pixel_analysis",
            confidence=0.0,
            extractor_version="0.1.0",
            stop_reason=f"Geometric analysis failed: {type(exc).__name__}",
        )


def extract_symbolic_elements(known_tokens: list[str]) -> dict[str, Any]:
    """Map text tokens against the UPI symbolic vocabulary registry.

    Runs on already-extracted text tokens (e.g. from OCR or manual
    annotation), not directly on image pixels. No optional dependencies.

    Args:
        known_tokens: Text tokens extracted from or associated with the image.

    Returns:
        SYMBOLIC_ELEMENT extraction layer dict (always SYM status).
    """
    findings: list[str] = []
    matched_keys: list[str] = []

    for token in known_tokens:
        upper = token.strip().upper()
        for key, meaning in _SYMBOL_REGISTRY.items():
            key_upper = key.upper()
            if key_upper in upper or upper in key_upper:
                entry = f"symbol: {key} → {meaning}"
                if entry not in findings:
                    findings.append(entry)
                    matched_keys.append(key)

    if not findings:
        findings.append("no_registered_symbols_matched")

    return build_extraction_layer(
        layer_type="SYMBOLIC_ELEMENT",
        findings=findings,
        source="symbol_registry_match",
        confidence=0.8 if matched_keys else 0.0,
        extractor_version="0.1.0",
    )


def extract_all_layers(
    path: Path,
    manual_text_tokens: list[str] | None = None,
) -> list[dict[str, Any]]:
    """Run all five extraction layers on an image file.

    Layer order:
    1. METADATA_EXIF — always available
    2. VISIBLE_TEXT  — requires Pillow + pytesseract
    3. COLOR_CHANNEL — requires Pillow
    4. GEOMETRIC_STRUCTURE — requires Pillow
    5. SYMBOLIC_ELEMENT — uses ``manual_text_tokens`` (no image deps)
    6. SHADOW_LAYER  — stdlib statistical analysis

    Args:
        path: Path to the image file (must exist).
        manual_text_tokens: Optional list of text tokens to use for symbol
            extraction when OCR is unavailable or supplemental.

    Returns:
        List of six extraction layer dicts.

    Raises:
        FileNotFoundError: If ``path`` does not exist.
    """
    path = Path(path)
    if not path.exists():
        raise FileNotFoundError(f"Image file not found: {path}")

    return [
        extract_metadata(path),
        extract_visible_text(path),
        extract_color_channels(path),
        extract_geometric_structure(path),
        extract_symbolic_elements(manual_text_tokens or []),
        analyze_shadow_layer(path),
    ]
