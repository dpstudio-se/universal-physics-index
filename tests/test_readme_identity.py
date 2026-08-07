"""Protect top-level README identity from wholesale replacement.

Anchors live in config/readme_identity.json. If you intentionally change
project identity strings, update that file in the same change and keep
this test green.
"""

from __future__ import annotations

import json
import re
from pathlib import Path

import pytest

ROOT = Path(__file__).resolve().parents[1]
IDENTITY_PATH = ROOT / "config" / "readme_identity.json"


@pytest.fixture(scope="module")
def identity() -> dict:
    assert IDENTITY_PATH.is_file(), f"Missing identity anchors: {IDENTITY_PATH}"
    data = json.loads(IDENTITY_PATH.read_text(encoding="utf-8"))
    assert "files" in data and data["files"], "identity config must list files"
    return data


def _read(path: Path) -> str:
    assert path.is_file(), f"Missing protected file: {path}"
    return path.read_text(encoding="utf-8")


def _first_heading(text: str) -> str | None:
    for line in text.splitlines():
        stripped = line.strip()
        if stripped.startswith("#"):
            return stripped
    return None


def _headings(text: str) -> list[str]:
    return [ln.strip() for ln in text.splitlines() if ln.strip().startswith("#")]


@pytest.mark.parametrize("file_key", ["README.md", "README.sv.md"])
def test_readme_file_exists_and_size(identity: dict, file_key: str) -> None:
    spec = identity["files"][file_key]
    path = ROOT / spec["path"]
    raw = path.read_bytes()
    assert spec["min_bytes"] <= len(raw) <= spec["max_bytes"], (
        f"{file_key} size {len(raw)} outside [{spec['min_bytes']}, {spec['max_bytes']}]. "
        "Wholesale wipe/replace is blocked; see docs/README_IDENTITY.md"
    )


@pytest.mark.parametrize("file_key", ["README.md", "README.sv.md"])
def test_readme_required_h1(identity: dict, file_key: str) -> None:
    spec = identity["files"][file_key]
    text = _read(ROOT / spec["path"])
    h1 = _first_heading(text)
    assert h1 == spec["required_h1"], (
        f"{file_key} H1 must be exactly {spec['required_h1']!r}, got {h1!r}. "
        "Do not replace the project README with a ToE manifesto or other title."
    )
    for forbidden in spec.get("forbidden_as_h1", []):
        assert h1 != forbidden
        # Also ban forbidden titles appearing as any top-level H1 elsewhere
        assert forbidden not in _headings(text), (
            f"{file_key} must not use forbidden H1 {forbidden!r}"
        )


@pytest.mark.parametrize("file_key", ["README.md", "README.sv.md"])
def test_readme_required_substrings(identity: dict, file_key: str) -> None:
    spec = identity["files"][file_key]
    text = _read(ROOT / spec["path"])
    missing = [s for s in spec["required_substrings"] if s not in text]
    assert not missing, (
        f"{file_key} missing required identity anchors: {missing}. "
        "Update config/readme_identity.json only if the change is intentional "
        "and reviewed (docs/README_IDENTITY.md)."
    )


@pytest.mark.parametrize("file_key", ["README.md", "README.sv.md"])
def test_readme_required_sections(identity: dict, file_key: str) -> None:
    spec = identity["files"][file_key]
    text = _read(ROOT / spec["path"])
    missing = [s for s in spec.get("required_sections", []) if s not in text]
    assert not missing, f"{file_key} missing required sections: {missing}"


def test_readme_md_toe_only_in_example_section(identity: dict) -> None:
    """Speculative ToE prose may exist only under an 'Example only' section."""
    spec = identity["files"]["README.md"]
    text = _read(ROOT / spec["path"])
    policy = spec.get("toe_content_policy") or {}
    marker = policy.get("allowed_only_under_heading_containing", "Example only")
    forbidden_bits = policy.get("forbidden_outside_example", [])
    if not forbidden_bits:
        return

    lines = text.splitlines()
    in_example = False
    leaked: list[str] = []
    for line in lines:
        stripped = line.strip()
        if stripped.startswith("## "):
            in_example = marker.lower() in stripped.lower()
        if in_example:
            continue
        for bit in forbidden_bits:
            if bit in line:
                leaked.append(bit)
    assert not leaked, (
        "ToE manifesto phrases appeared outside the Example-only section: "
        f"{sorted(set(leaked))}. Keep exploratory ToE text collapsible/example "
        "or in data/examples + docs — not as the main README identity."
    )


def test_readme_md_not_solely_toe_manifesto() -> None:
    text = _read(ROOT / "README.md")
    first = _first_heading(text) or ""
    assert "THEORY OF EVERYTHING" not in first.upper()
    assert not re.match(
        r"^#\s*THE UNIFIED BLUEPRINT",
        text.lstrip(),
        flags=re.IGNORECASE,
    )


def test_identity_config_self_consistent(identity: dict) -> None:
    for key, spec in identity["files"].items():
        assert spec["path"] == key or spec["path"].endswith(key)
        assert spec["required_h1"].startswith("# ")
        assert isinstance(spec["required_substrings"], list)
        path = ROOT / spec["path"]
        assert path.is_file()
