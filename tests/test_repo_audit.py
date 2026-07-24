import json
from pathlib import Path

import pytest

from repo_audit import SOURCE_MANIFEST_PATH, audit_repo


def write_required_scaffold(root: Path) -> None:
    (root / "config").mkdir()
    (root / "config" / "ports.json").write_text(
        json.dumps({"ports": {"angelica": 8080, "oden": 8081}}),
        encoding="utf-8",
    )
    (root / SOURCE_MANIFEST_PATH).write_text(
        json.dumps(
            {
                "operation": "upi_external_source_manifest",
                "sources": [{"source_id": "fixture"}],
            }
        ),
        encoding="utf-8",
    )
    for name in ("plugin.schema.json", ".env.example", "ARCHITECTURE.md"):
        (root / name).write_text("fixture", encoding="utf-8")


def test_audit_counts_files_not_directories(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    write_required_scaffold(tmp_path)
    nested = tmp_path / "nested"
    nested.mkdir()
    (nested / "record.json").write_text("{}", encoding="utf-8")
    monkeypatch.chdir(tmp_path)

    report = audit_repo()

    assert report["files_scanned"] == 6
    assert report["missing_files"] == []
    assert report["port_conflicts"] == []


def test_audit_names_the_config_path_on_parse_error(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    write_required_scaffold(tmp_path)
    (tmp_path / "config" / "ports.json").write_text("{", encoding="utf-8")
    monkeypatch.chdir(tmp_path)

    report = audit_repo()

    assert "config/ports.json" in report["critical_conflicts"][0]


def test_audit_reports_the_canonical_source_manifest_path(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    write_required_scaffold(tmp_path)
    (tmp_path / SOURCE_MANIFEST_PATH).write_text("{", encoding="utf-8")
    monkeypatch.chdir(tmp_path)

    report = audit_repo()

    assert SOURCE_MANIFEST_PATH.as_posix() in report["manifest_errors"][0]
