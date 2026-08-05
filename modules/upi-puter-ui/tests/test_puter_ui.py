"""Unit tests for upi-puter-ui module."""

from __future__ import annotations

import json
from pathlib import Path

from upi_puter_ui.server import PUBLIC_DIR

MODULE_DIR = Path(__file__).resolve().parents[1]
MANIFEST_PATH = MODULE_DIR / "puter.manifest.json"


def test_puter_manifest_validity() -> None:
    """Verify puter.manifest.json exists and has valid Puter App fields."""
    assert MANIFEST_PATH.exists()
    manifest = json.loads(MANIFEST_PATH.read_text(encoding="utf-8"))

    assert manifest["name"] == "Universal Physics Index — OdinOS"
    assert manifest["index"] == "public/index.html"
    assert "fs" in manifest["permissions"]
    assert "kv" in manifest["permissions"]
    assert "ai" in manifest["permissions"]


def test_public_directory_structure() -> None:
    """Verify required HTML, CSS, and JS web assets exist."""
    assert PUBLIC_DIR.exists()
    assert (PUBLIC_DIR / "index.html").exists()
    assert (PUBLIC_DIR / "style.css").exists()
    assert (PUBLIC_DIR / "app.js").exists()


def test_index_html_contains_puter_and_boundary_rules() -> None:
    """Verify index.html includes Puter.js SDK and scientific boundary tags."""
    content = (PUBLIC_DIR / "index.html").read_text(encoding="utf-8")
    assert "js.puter.com/v2" in content
    assert "EST" in content
    assert "DER" in content
    assert "SYM" in content
    assert "software_test" in content
