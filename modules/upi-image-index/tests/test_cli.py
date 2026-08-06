"""Tests for image_index CLI module."""

from __future__ import annotations

import json
from pathlib import Path
from unittest.mock import patch

from image_index.cli import main


def run_cli(*args: str, expected_exit: int = 0) -> str:
    """Run CLI with given args; return captured stdout.

    For successful commands (expected_exit=0), the function may return
    normally (no SystemExit) or raise SystemExit(0) — both are accepted.
    For failure cases (expected_exit != 0), a SystemExit with that code is required.
    """
    import contextlib
    import io

    buf = io.StringIO()
    try:
        with contextlib.redirect_stdout(buf), patch("sys.argv", ["upi-img", *args]):
            main()
        actual_exit = 0  # returned normally
    except SystemExit as exc:
        actual_exit = exc.code if exc.code is not None else 0

    assert actual_exit == expected_exit, (
        f"Expected exit {expected_exit}, got {actual_exit}\nOutput: {buf.getvalue()}"
    )
    return buf.getvalue()


class TestHelpCommands:
    def test_global_help(self):
        output = run_cli("--help")
        assert "upi-img" in output.lower() or "image" in output.lower()

    def test_index_help(self):
        output = run_cli("index", "--help")
        assert "--address" in output or "address" in output

    def test_decode_help(self):
        output = run_cli("decode", "--help")
        assert "decode" in output.lower() or "node" in output.lower()

    def test_scan_help(self):
        output = run_cli("scan", "--help")
        assert "scan" in output.lower() or "directory" in output.lower()

    def test_shadow_help(self):
        output = run_cli("shadow", "--help")
        assert "shadow" in output.lower() or "analyze" in output.lower()


class TestDecodeCommand:
    def _make_minimal_node(self, tmp_path: Path) -> Path:
        node = {
            "address": "UPI<IMAGE,1,TEST,DECODE>",
            "title": "Decode test node",
            "description": "For CLI decode tests",
            "status": "SYM",
            "information_layer": "PUBLIC",
            "image_hash_sha256": "a" * 64,
            "extraction_layers": [
                {
                    "layer_type": "METADATA_EXIF",
                    "status": "EST",
                    "source": "manual_annotation",
                    "content_hash": "f" * 64,
                    "findings": ["size_bytes: 1234"],
                    "extractor_version": "0.1.0",
                    "verification_type": "software_test",
                    "claims_experimental_verification": False,
                }
            ],
            "generation": 1,
            "parent_hash": None,
            "prompt_fingerprint": None,
            "version": "0.1.0",
            "verification_type": "software_test",
            "claims_experimental_verification": False,
            "tags": [],
        }
        p = tmp_path / "test_node.json"
        p.write_text(json.dumps(node, indent=2))
        return p

    def test_decode_shows_address(self, tmp_path):
        node_path = self._make_minimal_node(tmp_path)
        output = run_cli("decode", str(node_path))
        assert "UPI<IMAGE,1,TEST,DECODE>" in output

    def test_decode_shows_layer_count(self, tmp_path):
        node_path = self._make_minimal_node(tmp_path)
        output = run_cli("decode", str(node_path))
        # Should mention the layer somehow
        assert "METADATA_EXIF" in output or "layer" in output.lower()

    def test_decode_missing_file_exits_nonzero(self, tmp_path):
        run_cli("decode", str(tmp_path / "nonexistent.json"), expected_exit=1)


class TestScanCommand:
    def test_scan_empty_dir(self, tmp_path):
        img_dir = tmp_path / "images"
        img_dir.mkdir()
        output = run_cli("scan", str(img_dir))
        # Should complete without error (exit 0) and mention 0 nodes or be empty
        assert isinstance(output, str)

    def test_scan_with_valid_node(self, tmp_path):
        img_dir = tmp_path / "images"
        img_dir.mkdir()
        node = {
            "address": "UPI<IMAGE,1,TEST,SCAN>",
            "title": "Scan test",
            "description": "For scan test",
            "status": "SYM",
            "information_layer": "PUBLIC",
            "image_hash_sha256": "b" * 64,
            "extraction_layers": [],
            "generation": 1,
            "parent_hash": None,
            "prompt_fingerprint": None,
            "version": "0.1.0",
            "verification_type": "software_test",
            "claims_experimental_verification": False,
            "tags": [],
        }
        (img_dir / "node.json").write_text(json.dumps(node))
        output = run_cli("scan", str(img_dir))
        # cmd_scan outputs a JSON summary: {"files_scanned": 1, "valid": 1, ...}
        result = json.loads(output)
        assert result["files_scanned"] == 1
        assert result["valid"] == 1
        assert result["findings"] == 0

    def test_scan_missing_dir_exits_nonzero(self, tmp_path):
        run_cli("scan", str(tmp_path / "nonexistent_dir"), expected_exit=1)


class TestEvolveCommand:
    def _make_two_nodes(self, tmp_path: Path):
        img_dir = tmp_path / "images"
        img_dir.mkdir()
        for i, (name, addr) in enumerate([
            ("torus.json", "UPI<IMAGE,1,TORUS,A>"),
            ("helix.json", "UPI<IMAGE,1,HELIX,B>"),
        ]):
            node = {
                "address": addr,
                "title": f"Node {i}",
                "description": "Test",
                "status": "SYM",
                "information_layer": "PUBLIC",
                "image_hash_sha256": str(i) * 64,
                "extraction_layers": [
                    {
                        "layer_type": "SYMBOLIC_ELEMENT",
                        "status": "SYM",
                        "source": "registry",
                        "content_hash": "e" * 64,
                        "findings": ["symbol: DNA", "symbol: TORUS"],
                        "extractor_version": "0.1.0",
                        "verification_type": "software_test",
                        "claims_experimental_verification": False,
                        "confusion_guard": "Pattern recognition only.",
                    }
                ],
                "generation": 1,
                "parent_hash": None,
                "prompt_fingerprint": None,
                "version": "0.1.0",
                "verification_type": "software_test",
                "claims_experimental_verification": False,
                "tags": ["dna", "torus"],
            }
            (img_dir / name).write_text(json.dumps(node))
        return img_dir

    def test_evolve_with_two_nodes(self, tmp_path):
        img_dir = self._make_two_nodes(tmp_path)
        output = run_cli("evolve", "--path", str(img_dir))
        # Should complete without crash and report something
        assert isinstance(output, str)

    def test_evolve_finds_form_similar(self, tmp_path):
        img_dir = self._make_two_nodes(tmp_path)
        output = run_cli("evolve", "--path", str(img_dir))
        # Both nodes share "dna" and "torus" tags — expect FORM_SIMILAR suggestion
        assert "FORM_SIMILAR" in output or "similar" in output.lower() or "match" in output.lower()
