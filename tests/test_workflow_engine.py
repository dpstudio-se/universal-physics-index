"""Tests for autonomous workflow engine and optimal release gating."""

import json
import sys
from pathlib import Path

import pytest

sys.path.insert(0, str(Path(__file__).parent.parent / "src"))

from upi.workflow_engine import WorkflowEngine


def test_ingest_repo_audit_and_gate_blocks_missing_files_only():
    engine = WorkflowEngine(min_score=0.75, max_risk=0.35)
    report = {
        "critical_conflicts": [],
        "missing_files": ["config/ports.json"],
        "port_conflicts": [],
        "files_scanned": 10,
    }
    result = engine.run_from_report(report)
    assert result["summary"]["release_ready"] is False
    assert result["summary"]["accepted_count"] == 0
    assert result["summary"]["blocked_count"] == 1
    assert result["blocked"][0]["issue_id"].startswith("missing-")


def test_ingest_repo_audit_accepts_critical_fix_candidate():
    engine = WorkflowEngine(min_score=0.75, max_risk=0.35)
    report = {
        "critical_conflicts": ["Cannot parse config/ports.json"],
        "missing_files": [],
        "port_conflicts": [],
        "files_scanned": 25,
    }
    result = engine.run_from_report(report)
    assert result["summary"]["accepted_count"] == 1
    assert result["summary"]["blocked_count"] == 0
    assert result["summary"]["release_ready"] is True
    assert result["accepted"][0]["release_reason"] == "accepted-by-optimal-gate"


def test_run_from_report_file(tmp_path: Path):
    engine = WorkflowEngine(min_score=0.65, max_risk=0.4)
    report_path = tmp_path / "report.json"
    report_path.write_text(
        json.dumps(
            {
                "critical_conflicts": [],
                "missing_files": [],
                "port_conflicts": ["Duplicate ports found in config/ports.json"],
                "files_scanned": 20,
            }
        ),
        encoding="utf-8",
    )
    result = engine.run_from_report_file(report_path)
    assert result["summary"]["accepted_count"] == 1
    assert result["accepted"][0]["issue_id"].startswith("ports-")


def test_release_ready_when_no_findings():
    engine = WorkflowEngine(min_score=0.75, max_risk=0.35)
    report = {
        "critical_conflicts": [],
        "missing_files": [],
        "port_conflicts": [],
        "files_scanned": 100,
    }
    result = engine.run_from_report(report)
    assert result["summary"]["release_ready"] is True
    assert result["summary"]["accepted_count"] == 0
    assert result["summary"]["blocked_count"] == 0
