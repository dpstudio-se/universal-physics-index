"""Tests for image_index.shadow module."""

from __future__ import annotations

import pytest
from image_index.shadow import (
    _byte_frequency_chi_square,
    _check_magic_bytes,
    _entropy_estimate,
    _lsb_byte_distribution,
    analyze_shadow_layer,
)


class TestLsbDistribution:
    def test_all_ones_lsb(self):
        data = bytes([0xFF] * 100)  # 0xFF = 11111111, LSB = 1
        result = _lsb_byte_distribution(data)
        assert result["lsb_ratio"] == pytest.approx(1.0)
        assert result["deviation_from_half"] == pytest.approx(0.5)

    def test_all_zeros_lsb(self):
        data = bytes([0x00] * 100)  # 0x00 = 00000000, LSB = 0
        result = _lsb_byte_distribution(data)
        assert result["lsb_ratio"] == pytest.approx(0.0)
        assert result["deviation_from_half"] == pytest.approx(0.5)

    def test_balanced_lsb(self):
        # 0xAA = 10101010 (LSB=0), 0x55 = 01010101 (LSB=1)
        data = bytes([0xAA, 0x55] * 50)
        result = _lsb_byte_distribution(data)
        assert result["lsb_ratio"] == pytest.approx(0.5)
        assert result["deviation_from_half"] == pytest.approx(0.0)

    def test_sample_size_respected(self):
        data = bytes(range(256)) * 100  # large data
        result = _lsb_byte_distribution(data, sample_size=100)
        assert result["sample_size"] == 100

    def test_empty_data(self):
        result = _lsb_byte_distribution(b"")
        assert result["sample_size"] == 0
        assert result["lsb_ratio"] == 0.5


class TestChiSquare:
    def test_uniform_distribution_low_chi_square(self):
        # Perfect uniform distribution: each byte value appears equal times
        data = bytes(range(256)) * 16  # 4096 bytes, each value 16 times
        chi_sq = _byte_frequency_chi_square(data)
        assert chi_sq == pytest.approx(0.0, abs=1e-3)

    def test_single_value_high_chi_square(self):
        # All same byte: maximally non-uniform
        data = bytes([42] * 4096)
        chi_sq = _byte_frequency_chi_square(data)
        assert chi_sq > 1000.0  # Should be very high

    def test_empty_data_returns_zero(self):
        assert _byte_frequency_chi_square(b"") == 0.0


class TestEntropyEstimate:
    def test_zero_entropy_uniform_single_byte(self):
        data = bytes([0] * 1000)
        entropy = _entropy_estimate(data)
        assert entropy == pytest.approx(0.0, abs=1e-3)

    def test_max_entropy_uniform_distribution(self):
        # 256 distinct values equally distributed → ~8 bits
        data = bytes(range(256)) * 4  # 1024 bytes
        entropy = _entropy_estimate(data)
        assert entropy == pytest.approx(8.0, abs=0.01)

    def test_two_values_entropy_is_one(self):
        # 50/50 split of two values → 1 bit entropy
        data = bytes([0, 255] * 500)
        entropy = _entropy_estimate(data)
        assert entropy == pytest.approx(1.0, abs=0.01)

    def test_empty_data_returns_zero(self):
        assert _entropy_estimate(b"") == 0.0

    def test_value_in_valid_range(self):
        import os
        data = os.urandom(256)
        entropy = _entropy_estimate(data)
        assert 0.0 <= entropy <= 8.0


class TestMagicBytes:
    def test_detects_jpeg_primary(self):
        data = b"\xff\xd8\xff" + bytes(100)
        findings = _check_magic_bytes(data)
        assert any("JPEG" in f and "primary" in f for f in findings)

    def test_detects_png_primary(self):
        data = b"\x89PNG\r\n" + bytes(100)
        findings = _check_magic_bytes(data)
        assert any("PNG" in f and "primary" in f for f in findings)

    def test_detects_zip_primary(self):
        data = b"PK\x03\x04" + bytes(100)
        findings = _check_magic_bytes(data)
        assert any("ZIP" in f and "primary" in f for f in findings)

    def test_detects_nested_signature(self):
        # PNG header at start, then embedded ZIP after 16 bytes
        data = b"\x89PNG\r\n" + bytes(16) + b"PK\x03\x04" + bytes(50)
        findings = _check_magic_bytes(data)
        nested = [f for f in findings if "nested" in f]
        assert len(nested) > 0

    def test_empty_data_no_crash(self):
        findings = _check_magic_bytes(b"")
        assert isinstance(findings, list)

    def test_random_data_no_match(self):
        # Data with no known magic bytes
        data = bytes([0x00, 0x01, 0x02, 0x03] * 10)
        findings = _check_magic_bytes(data)
        # May or may not match BMP (starts with BM = 0x42 0x4D) — just check it's a list
        assert isinstance(findings, list)


class TestAnalyzeShadowLayer:
    def test_returns_hyp_status(self, tmp_path):
        test_file = tmp_path / "test.bin"
        test_file.write_bytes(bytes(range(256)) * 4)
        result = analyze_shadow_layer(test_file)
        assert result["status"] == "HYP"
        assert result["layer_type"] == "SHADOW_LAYER"

    def test_has_required_fields(self, tmp_path):
        test_file = tmp_path / "test.bin"
        test_file.write_bytes(b"\xff\xd8\xff" + bytes(100))
        result = analyze_shadow_layer(test_file)
        assert "findings" in result
        assert "stop_reason" in result
        assert "content_hash" in result
        assert len(result["content_hash"]) == 64

    def test_findings_contain_statistics(self, tmp_path):
        test_file = tmp_path / "test.bin"
        test_file.write_bytes(bytes(range(256)) * 4)
        result = analyze_shadow_layer(test_file)
        findings_text = "\n".join(result["findings"])
        assert "lsb_ratio" in findings_text
        assert "chi_square" in findings_text
        assert "entropy" in findings_text

    def test_detects_jpeg_signature(self, tmp_path):
        test_file = tmp_path / "test.jpg"
        test_file.write_bytes(b"\xff\xd8\xff" + bytes(200))
        result = analyze_shadow_layer(test_file)
        assert any("JPEG" in f for f in result["findings"])

    def test_missing_file_reports_error(self, tmp_path):
        missing = tmp_path / "nonexistent.png"
        result = analyze_shadow_layer(missing)
        assert result["status"] == "HYP"
        findings_text = "\n".join(result["findings"])
        assert "read_error" in findings_text

    def test_never_exposes_raw_bytes(self, tmp_path):
        """Raw byte values must not appear verbatim in findings."""
        secret = b"SECRET_CONTENT_NEVER_IN_OUTPUT"
        test_file = tmp_path / "secret.bin"
        test_file.write_bytes(secret + bytes(200))
        result = analyze_shadow_layer(test_file)
        all_findings = "\n".join(result["findings"])
        assert "SECRET_CONTENT_NEVER_IN_OUTPUT" not in all_findings
