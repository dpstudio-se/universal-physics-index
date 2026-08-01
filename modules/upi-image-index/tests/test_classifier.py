"""Tests for image_index.classifier module."""

from __future__ import annotations

from hashlib import sha256

import pytest

from image_index.classifier import (
    OCR_EST_THRESHOLD,
    ScientificStatus,
    build_extraction_layer,
    build_image_node,
    classify_layer,
    content_hash,
)


class TestScientificStatus:
    def test_all_values_accessible(self):
        for name in ("EST", "DER", "HYP", "STOP", "ERR", "SYM"):
            assert ScientificStatus(name).value == name

    def test_string_comparison(self):
        assert ScientificStatus.EST == "EST"
        assert ScientificStatus.SYM != "EST"


class TestContentHash:
    def test_returns_64_char_hex(self):
        h = content_hash("hello world")
        assert len(h) == 64
        assert all(c in "0123456789abcdef" for c in h)

    def test_deterministic(self):
        assert content_hash("abc") == content_hash("abc")

    def test_matches_stdlib_sha256(self):
        expected = sha256("test".encode("utf-8")).hexdigest()
        assert content_hash("test") == expected

    def test_different_inputs_differ(self):
        assert content_hash("a") != content_hash("b")


class TestClassifyLayer:
    def test_visible_text_high_confidence_is_est(self):
        status = classify_layer("VISIBLE_TEXT", "ocr", confidence=0.97)
        assert status == ScientificStatus.EST

    def test_visible_text_at_threshold_is_est(self):
        status = classify_layer("VISIBLE_TEXT", "ocr", confidence=OCR_EST_THRESHOLD)
        assert status == ScientificStatus.EST

    def test_visible_text_low_confidence_downgrades_to_der(self):
        status = classify_layer("VISIBLE_TEXT", "ocr", confidence=0.80)
        assert status == ScientificStatus.DER

    def test_metadata_exif_is_est(self):
        assert classify_layer("METADATA_EXIF", "file_stats") == ScientificStatus.EST

    def test_geometric_structure_is_der(self):
        assert classify_layer("GEOMETRIC_STRUCTURE", "pillow") == ScientificStatus.DER

    def test_color_channel_is_der(self):
        assert classify_layer("COLOR_CHANNEL", "pillow") == ScientificStatus.DER

    def test_symbolic_element_is_sym(self):
        assert classify_layer("SYMBOLIC_ELEMENT", "registry") == ScientificStatus.SYM

    def test_shadow_layer_is_hyp(self):
        assert classify_layer("SHADOW_LAYER", "stats") == ScientificStatus.HYP

    def test_unknown_layer_type_defaults_to_hyp(self):
        assert classify_layer("UNKNOWN_LAYER", "mystery") == ScientificStatus.HYP

    def test_no_confidence_does_not_downgrade_est(self):
        # Without confidence, EST layers should remain EST
        assert classify_layer("METADATA_EXIF", "file_stats", confidence=None) == ScientificStatus.EST


class TestBuildExtractionLayer:
    def test_basic_visible_text_layer(self):
        layer = build_extraction_layer(
            layer_type="VISIBLE_TEXT",
            findings=["ocr_token: hello", "ocr_token: world"],
            source="pytesseract_ocr",
            confidence=0.98,
        )
        assert layer["layer_type"] == "VISIBLE_TEXT"
        assert layer["status"] == "EST"
        assert layer["source"] == "pytesseract_ocr"
        assert len(layer["findings"]) == 2
        assert layer["claims_experimental_verification"] is False
        assert layer["verification_type"] == "software_test"

    def test_content_hash_is_64_hex(self):
        layer = build_extraction_layer("COLOR_CHANNEL", ["red_mean: 100"], "pillow")
        assert len(layer["content_hash"]) == 64
        assert all(c in "0123456789abcdef" for c in layer["content_hash"])

    def test_content_hash_is_deterministic(self):
        findings = ["lsb_ratio: 0.5", "entropy: 7.9"]
        h1 = build_extraction_layer("SHADOW_LAYER", findings, "stats")["content_hash"]
        h2 = build_extraction_layer("SHADOW_LAYER", findings, "stats")["content_hash"]
        assert h1 == h2

    def test_symbolic_layer_has_confusion_guard(self):
        layer = build_extraction_layer("SYMBOLIC_ELEMENT", ["symbol: DNA"], "registry")
        assert "confusion_guard" in layer
        assert "SYM" in layer["confusion_guard"]

    def test_hyp_layer_auto_gets_stop_reason(self):
        layer = build_extraction_layer("SHADOW_LAYER", ["lsb_ratio: 0.5"], "stats")
        assert "stop_reason" in layer
        assert len(layer["stop_reason"]) > 0

    def test_explicit_stop_reason_preserved(self):
        layer = build_extraction_layer(
            "SHADOW_LAYER", [], "none", stop_reason="Custom stop reason for test"
        )
        assert layer["stop_reason"] == "Custom stop reason for test"

    def test_empty_findings_valid(self):
        layer = build_extraction_layer("VISIBLE_TEXT", [], "none")
        assert layer["findings"] == []
        assert len(layer["content_hash"]) == 64  # sha256 of empty string


class TestBuildImageNode:
    _placeholder_hash = "a" * 64
    _sample_layers = [
        build_extraction_layer("METADATA_EXIF", ["size_bytes: 1000"], "file_stats", 1.0),
        build_extraction_layer("SHADOW_LAYER", ["lsb_ratio: 0.5"], "stats"),
    ]

    def test_required_fields_present(self):
        node = build_image_node(
            image_hash=self._placeholder_hash,
            upi_address="UPI<IMAGE,1,TEST,NODE>",
            title="Test node",
            description="A test image node",
            extraction_layers=self._sample_layers,
        )
        for field in ("address", "title", "description", "status",
                      "image_hash_sha256", "extraction_layers", "generation"):
            assert field in node, f"Missing field: {field}"

    def test_default_status_is_sym(self):
        node = build_image_node(
            image_hash=self._placeholder_hash,
            upi_address="UPI<IMAGE,1,TEST,NODE>",
            title="T",
            description="D",
            extraction_layers=[],
        )
        assert node["status"] == "SYM"

    def test_custom_status(self):
        node = build_image_node(
            image_hash=self._placeholder_hash,
            upi_address="UPI<IMAGE,1,TEST,NODE>",
            title="T",
            description="D",
            extraction_layers=[],
            primary_status=ScientificStatus.DER,
        )
        assert node["status"] == "DER"

    def test_generation_default(self):
        node = build_image_node(
            image_hash=self._placeholder_hash,
            upi_address="UPI<IMAGE,1,TEST,NODE>",
            title="T",
            description="D",
            extraction_layers=[],
        )
        assert node["generation"] == 1

    def test_tags_default_empty(self):
        node = build_image_node(
            image_hash=self._placeholder_hash,
            upi_address="UPI<IMAGE,1,TEST,NODE>",
            title="T",
            description="D",
            extraction_layers=[],
        )
        assert node["tags"] == []

    def test_claims_experimental_verification_false(self):
        node = build_image_node(
            image_hash=self._placeholder_hash,
            upi_address="UPI<IMAGE,1,TEST,NODE>",
            title="T",
            description="D",
            extraction_layers=[],
        )
        assert node["claims_experimental_verification"] is False
