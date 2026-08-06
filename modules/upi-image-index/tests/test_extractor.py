"""Tests for image_index.extractor module."""

from __future__ import annotations

import hashlib

import pytest
from image_index.extractor import (
    extract_all_layers,
    extract_metadata,
    extract_symbolic_elements,
    hash_file,
)


class TestHashFile:
    def test_sha256_matches_stdlib(self, tmp_path):
        f = tmp_path / "test.txt"
        content = b"hello world"
        f.write_bytes(content)
        expected = hashlib.sha256(content).hexdigest()
        assert hash_file(f) == expected

    def test_returns_64_char_hex(self, tmp_path):
        f = tmp_path / "f.bin"
        f.write_bytes(bytes(range(256)))
        h = hash_file(f)
        assert len(h) == 64
        assert all(c in "0123456789abcdef" for c in h)

    def test_different_files_differ(self, tmp_path):
        f1 = tmp_path / "a.bin"
        f2 = tmp_path / "b.bin"
        f1.write_bytes(b"aaa")
        f2.write_bytes(b"bbb")
        assert hash_file(f1) != hash_file(f2)

    def test_large_file_works(self, tmp_path):
        f = tmp_path / "large.bin"
        f.write_bytes(bytes(range(256)) * 1000)  # 256 KB
        h = hash_file(f)
        assert len(h) == 64


class TestExtractMetadata:
    def test_returns_est_layer(self, tmp_path):
        f = tmp_path / "test.png"
        f.write_bytes(b"\x89PNG\r\n" + bytes(100))
        layer = extract_metadata(f)
        assert layer["layer_type"] == "METADATA_EXIF"
        assert layer["status"] in ("EST", "DER")  # EST normally, DER on low confidence

    def test_findings_contains_size(self, tmp_path):
        f = tmp_path / "test.bin"
        f.write_bytes(bytes(50))
        layer = extract_metadata(f)
        findings_str = "\n".join(layer["findings"])
        assert "size_bytes" in findings_str

    def test_findings_contains_extension(self, tmp_path):
        f = tmp_path / "image.jpg"
        f.write_bytes(b"\xff\xd8\xff" + bytes(50))
        layer = extract_metadata(f)
        findings_str = "\n".join(layer["findings"])
        assert ".jpg" in findings_str

    def test_missing_file_graceful(self, tmp_path):
        missing = tmp_path / "nonexistent.png"
        # extract_metadata raises FileNotFoundError for missing files — that's expected
        with pytest.raises((FileNotFoundError, OSError)):
            extract_metadata(missing)


class TestExtractSymbolicElements:
    def test_dna_token_detected(self):
        layer = extract_symbolic_elements(["DNA", "HELIX", "TORUS"])
        findings_str = "\n".join(layer["findings"])
        assert "DNA" in findings_str or "symbol" in findings_str

    def test_always_sym_status(self):
        layer = extract_symbolic_elements(["DNA"])
        assert layer["status"] == "SYM"

    def test_has_confusion_guard(self):
        layer = extract_symbolic_elements(["φ"])
        assert "confusion_guard" in layer
        assert len(layer["confusion_guard"]) > 0

    def test_no_known_symbols_returns_layer(self):
        layer = extract_symbolic_elements(["COMPLETELY_UNKNOWN_TOKEN_XYZ"])
        assert layer["layer_type"] == "SYMBOLIC_ELEMENT"
        assert layer["status"] == "SYM"

    def test_empty_tokens(self):
        layer = extract_symbolic_elements([])
        assert layer["layer_type"] == "SYMBOLIC_ELEMENT"
        assert layer["status"] == "SYM"

    def test_soai_detected(self):
        layer = extract_symbolic_elements(["SOAI", "SOAI-REAKTIONEN"])
        findings_str = "\n".join(layer["findings"])
        # Should match SOAI in registry
        assert "SOAI" in findings_str

    def test_8hz_detected(self):
        layer = extract_symbolic_elements(["8 HZ", "8 Hz Entrainment"])
        findings_str = "\n".join(layer["findings"])
        assert "8 HZ" in findings_str or "8 Hz" in findings_str or "Hz" in findings_str


class TestExtractAllLayers:
    def test_returns_list_of_layers(self, tmp_path):
        f = tmp_path / "test.bin"
        f.write_bytes(bytes(range(256)) * 4)
        layers = extract_all_layers(f, manual_text_tokens=["DNA"])
        assert isinstance(layers, list)
        assert len(layers) >= 1  # at minimum, METADATA_EXIF

    def test_always_includes_metadata_layer(self, tmp_path):
        f = tmp_path / "test.bin"
        f.write_bytes(bytes(100))
        layers = extract_all_layers(f)
        types = [lay["layer_type"] for lay in layers]
        assert "METADATA_EXIF" in types

    def test_shadow_layer_always_included(self, tmp_path):
        f = tmp_path / "test.bin"
        f.write_bytes(bytes(range(256)) * 4)
        layers = extract_all_layers(f)
        types = [lay["layer_type"] for lay in layers]
        assert "SHADOW_LAYER" in types

    def test_symbolic_layer_included_when_tokens_given(self, tmp_path):
        f = tmp_path / "test.bin"
        f.write_bytes(bytes(100))
        layers = extract_all_layers(f, manual_text_tokens=["DNA", "TORUS"])
        types = [lay["layer_type"] for lay in layers]
        assert "SYMBOLIC_ELEMENT" in types

    def test_all_layers_have_required_fields(self, tmp_path):
        f = tmp_path / "test.bin"
        f.write_bytes(bytes(100))
        layers = extract_all_layers(f, manual_text_tokens=["DNA"])
        for layer in layers:
            for field in ("layer_type", "status", "findings", "content_hash", "extractor_version"):
                assert field in layer, f"Layer {layer.get('layer_type')} missing {field}"
