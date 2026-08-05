"""Shadow-layer detector: statistical analysis of image file bytes.

Performs LSB distribution, chi-square uniformity, entropy estimation, and
magic-byte detection. All findings are statistical hypotheses (HYP) unless
confirmed by an independent specialised tool.

Raw byte values and pixel data are **never** included in findings; only
derived statistics and hash prefixes are reported.
"""

from __future__ import annotations

import hashlib
import math
from pathlib import Path
from typing import Any

from .classifier import build_extraction_layer

# ---------------------------------------------------------------------------
# Internal statistical helpers
# ---------------------------------------------------------------------------


def _lsb_byte_distribution(data: bytes, sample_size: int = 8192) -> dict[str, Any]:
    """Analyse least-significant-bit distribution of a byte sample.

    Returns:
        Dict with lsb_ratio, deviation_from_half, and sample statistics.
    """
    sample = data[:sample_size]
    total = len(sample)
    if total == 0:
        return {"sample_size": 0, "lsb_ones_count": 0, "lsb_zeros_count": 0,
                "lsb_ratio": 0.5, "deviation_from_half": 0.0}

    ones = sum(b & 1 for b in sample)
    zeros = total - ones
    lsb_ratio = ones / total
    return {
        "sample_size": total,
        "lsb_ones_count": ones,
        "lsb_zeros_count": zeros,
        "lsb_ratio": round(lsb_ratio, 6),
        "deviation_from_half": round(abs(lsb_ratio - 0.5), 6),
    }


def _byte_frequency_chi_square(data: bytes, sample_size: int = 4096) -> float:
    """Chi-square uniformity test on byte-value distribution.

    For a natural uncompressed image, byte values are not uniform.
    Near-perfect uniformity (low chi²) may indicate encryption or
    steganographic embedding and is flagged as HYP.

    Returns:
        Chi-square statistic (lower = more uniform).
    """
    sample = data[:sample_size]
    if not sample:
        return 0.0

    freq = [0] * 256
    for b in sample:
        freq[b] += 1

    expected = len(sample) / 256.0
    chi_sq = sum((f - expected) ** 2 / expected for f in freq)
    return round(chi_sq, 4)


def _entropy_estimate(data: bytes, sample_size: int = 8192) -> float:
    """Estimate Shannon entropy of a byte sample in bits per byte.

    Values near 8.0 indicate high entropy (compressed/encrypted data);
    values near 0.0 indicate very low diversity.
    """
    sample = data[:sample_size]
    if not sample:
        return 0.0

    freq = [0] * 256
    for b in sample:
        freq[b] += 1

    n = len(sample)
    entropy = 0.0
    for f in freq:
        if f > 0:
            p = f / n
            entropy -= p * math.log2(p)
    return round(entropy, 6)


def _check_magic_bytes(data: bytes) -> list[str]:
    """Detect primary and nested file-format signatures in raw bytes."""
    signatures: list[tuple[bytes, str]] = [
        (b"\xff\xd8\xff", "JPEG"),
        (b"\x89PNG\r\n", "PNG"),
        (b"GIF8", "GIF"),
        (b"BM", "BMP"),
        (b"RIFF", "RIFF/WEBP"),
        (b"PK\x03\x04", "ZIP"),
        (b"\x1f\x8b", "GZIP"),
        (b"%PDF", "PDF"),
        (b"IHDR", "PNG_IHDR_chunk"),
    ]

    findings: list[str] = []
    header = data[:16]
    rest = data[16:] if len(data) > 16 else b""

    for sig, name in signatures:
        if header.startswith(sig):
            findings.append(f"primary_format: {name}")
        elif sig in rest:
            findings.append(
                f"nested_signature: {name} — potential embedded content (HYP)"
            )
    return findings


# ---------------------------------------------------------------------------
# Public API
# ---------------------------------------------------------------------------


def analyze_shadow_layer(path: Path) -> dict[str, Any]:
    """Analyse an image file for potential hidden or shadow layers.

    Runs LSB analysis, chi-square test, entropy estimation, and magic-byte
    detection. Status is always HYP; promote only after independent
    verification with a dedicated steganography tool.

    Raw byte values are never exposed in findings — only derived statistics
    and a short hash prefix are reported.

    Args:
        path: Path to the image file.

    Returns:
        Extraction layer dict (layer_type=SHADOW_LAYER, status=HYP).
    """
    path = Path(path)
    findings: list[str] = []

    try:
        with open(path, "rb") as fh:
            data = fh.read()

        file_hash = hashlib.sha256(data).hexdigest()
        findings.append(f"file_hash_prefix: {file_hash[:16]}")
        findings.append(f"file_size_bytes: {len(data)}")

        # LSB
        lsb = _lsb_byte_distribution(data)
        findings.append(f"lsb_ratio: {lsb['lsb_ratio']}")
        findings.append(f"lsb_deviation_from_0.5: {lsb['deviation_from_half']}")
        if lsb["deviation_from_half"] > 0.05:
            findings.append(
                "lsb_anomaly: deviation > 0.05 — possible steganographic modification (HYP)"
            )
        else:
            findings.append("lsb_distribution: within expected range")

        # Chi-square
        chi_sq = _byte_frequency_chi_square(data)
        findings.append(f"chi_square_statistic: {chi_sq}")
        if chi_sq < 100.0:
            findings.append(
                "chi_square_low: near-uniform byte distribution — possible encryption or stego (HYP)"
            )

        # Entropy
        entropy = _entropy_estimate(data)
        findings.append(f"byte_entropy_bits_per_byte: {entropy}")
        if entropy > 7.8:
            findings.append(
                "entropy_high: > 7.8 bits/byte — consistent with compressed or encrypted payload (HYP)"
            )

        # Magic bytes
        magic_findings = _check_magic_bytes(data)
        findings.extend(magic_findings)
        nested_count = sum(1 for f in magic_findings if "nested" in f)
        if nested_count:
            findings.append(
                f"nested_format_count: {nested_count} — review with binwalk or zsteg (HYP)"
            )

        stop_reason = (
            "All shadow-layer findings are statistical hypotheses. "
            "Verify with stegdetect, zsteg, or binwalk before promoting to EST."
        )

    except OSError as exc:
        findings.append(f"read_error: {type(exc).__name__}")
        stop_reason = f"File could not be read: {type(exc).__name__}"

    return build_extraction_layer(
        layer_type="SHADOW_LAYER",
        findings=findings,
        source="stdlib_statistical_analysis",
        confidence=None,
        extractor_version="0.1.0",
        stop_reason=stop_reason,
    )
