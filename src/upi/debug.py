"""Deterministic, index-wide UPI debugging and exploded-map generation."""

from __future__ import annotations

from collections import Counter
import json
from pathlib import Path
from typing import Any

from .validation import validate_record_boundaries


CORRECTIONS = {
    "UPI-E011": "Declare the reference_frame used by the normalization.",
    "UPI-E012": "Add a causal test or downgrade physical equivalence to a model definition.",
    "UPI-E013": "Declare a causal_test_method or remove the causal claim.",
    "UPI-E014": "Use experimental_observation/replication evidence or remove the experimental claim.",
    "UPI-D001": "Repair the JSON syntax and rerun the scanner.",
    "UPI-D002": "Add the required node, bridge, or theory discriminator fields.",
    "UPI-D003": "Correct the record so it validates against its declared UPI schema.",
    "UPI-D004": "Add falsification_conditions before treating the hypothesis as testable.",
}


def _schemas_dir() -> Path:
    return Path(__file__).resolve().parents[2] / "schemas"


def _record_type(data: dict[str, Any]) -> str | None:
    if {"source", "target", "relation"} <= data.keys():
        return "bridge"
    if {"address", "domain", "scope"} <= data.keys():
        return "theory"
    if {"address", "title", "status"} <= data.keys():
        return "node"
    return None


def _scale_signature(data: dict[str, Any]) -> dict[str, Any]:
    quantities = data.get("quantities", [])
    units = sorted(
        {
            str(quantity.get("unit"))
            for quantity in quantities
            if isinstance(quantity, dict) and quantity.get("unit")
        }
    )
    return {
        "scope": data.get("scope", "unspecified"),
        "units": units,
        "time_scale": data.get("time_scale", "unspecified"),
        "length_scale": data.get("length_scale", "unspecified"),
    }


def _finding(
    code: str,
    status: str,
    path: str,
    message: str,
    *,
    record_type: str | None = None,
    correction: str | None = None,
) -> dict[str, Any]:
    return {
        "code": code,
        "status": status,
        "path": path,
        "record_type": record_type,
        "message": message,
        "correction": correction or CORRECTIONS.get(code, "Inspect the recorded evidence."),
        "verification_type": "software_test",
    }


def _schema_errors(data: dict[str, Any], record_type: str, schemas_dir: Path) -> list[str]:
    try:
        import jsonschema
    except ImportError:
        return ["jsonschema module not installed"]

    schema_path = schemas_dir / f"{record_type}.schema.json"
    if not schema_path.exists():
        return [f"schema not found: {schema_path}"]

    schema = json.loads(schema_path.read_text(encoding="utf-8"))
    validator = jsonschema.Draft7Validator(schema)
    return [error.message for error in sorted(validator.iter_errors(data), key=str)]


def generate_debug_report(root: Path, schemas_dir: Path | None = None) -> dict[str, Any]:
    """Scan every JSON record below *root* and return a UPI debug report.

    The report is deterministic and AI-ready. It never mutates source records and
    never upgrades software validation to experimental evidence.
    """
    root = root.resolve()
    schemas_dir = (schemas_dir or _schemas_dir()).resolve()
    findings: list[dict[str, Any]] = []
    records: list[dict[str, Any]] = []
    status_counts: Counter[str] = Counter()
    type_counts: Counter[str] = Counter()

    for path in sorted(root.rglob("*.json")):
        relative_path = path.relative_to(root).as_posix()
        try:
            data = json.loads(path.read_text(encoding="utf-8"))
        except (OSError, UnicodeError, json.JSONDecodeError) as error:
            findings.append(_finding("UPI-D001", "ERR", relative_path, str(error)))
            continue

        if not isinstance(data, dict):
            findings.append(
                _finding("UPI-D002", "STOP", relative_path, "Top-level JSON must be an object.")
            )
            continue

        record_type = _record_type(data)
        if record_type is None:
            findings.append(
                _finding(
                    "UPI-D002",
                    "STOP",
                    relative_path,
                    "Could not classify record as node, bridge, or theory.",
                )
            )
            continue

        status = str(data.get("status", "STOP"))
        status_counts[status] += 1
        type_counts[record_type] += 1
        record_id = str(data.get("address") or f"{data.get('source')}->{data.get('target')}")
        records.append(
            {
                "id": record_id,
                "path": relative_path,
                "record_type": record_type,
                "status": status,
                "scale": _scale_signature(data),
                "evidence_count": len(data.get("evidence", [])),
                "equation_count": len(data.get("equations", data.get("fundamental_equations", []))),
            }
        )

        for error in _schema_errors(data, record_type, schemas_dir):
            findings.append(
                _finding("UPI-D003", "ERR", relative_path, error, record_type=record_type)
            )

        for error in validate_record_boundaries(data):
            code = error.split(":", 1)[0]
            findings.append(
                _finding(code, "ERR", relative_path, error, record_type=record_type)
            )

        if (
            record_type == "node"
            and status == "HYP"
            and not data.get("falsification_conditions")
        ):
            findings.append(
                _finding(
                    "UPI-D004",
                    "STOP",
                    relative_path,
                    "Hypothesis has no falsification_conditions.",
                    record_type=record_type,
                )
            )

    map_nodes: list[dict[str, Any]] = []
    map_edges: list[dict[str, str]] = []
    for index, record in enumerate(records):
        record_node = f"record:{index}"
        scale_node = f"scale:{index}"
        evidence_node = f"evidence:{index}"
        map_nodes.extend(
            [
                {**record, "id": record_node, "layer": "record"},
                {"id": scale_node, "layer": "scale", "value": record["scale"]},
                {
                    "id": evidence_node,
                    "layer": "evidence",
                    "count": record["evidence_count"],
                },
            ]
        )
        map_edges.extend(
            [
                {"source": record_node, "target": scale_node, "relation": "MEASURED_BY"},
                {"source": record_node, "target": evidence_node, "relation": "DERIVED_FROM"},
            ]
        )

    for index, finding in enumerate(findings):
        finding_node = f"finding:{index}"
        correction_node = f"correction:{index}"
        map_nodes.extend(
            [
                {"id": finding_node, "layer": "finding", **finding},
                {
                    "id": correction_node,
                    "layer": "correction",
                    "value": finding["correction"],
                },
            ]
        )
        map_edges.append(
            {"source": finding_node, "target": correction_node, "relation": "STOPS_AT"}
        )

    return {
        "schema_version": "0.1.0",
        "operation": "upi_debug_index",
        "root": str(root),
        "verification_type": "software_test",
        "claims_experimental_verification": False,
        "summary": {
            "files_scanned": len(list(root.rglob("*.json"))),
            "records_classified": len(records),
            "findings": len(findings),
            "status_counts": dict(sorted(status_counts.items())),
            "record_type_counts": dict(sorted(type_counts.items())),
        },
        "findings": findings,
        "exploded_map": {
            "layers": ["record", "scale", "evidence", "finding", "correction"],
            "nodes": map_nodes,
            "edges": map_edges,
            "confusion_guard": (
                "Shared equations or functions across scales do not establish shared physical mechanisms."
            ),
        },
    }


def render_debug_markdown(report: dict[str, Any]) -> str:
    """Render a compact human-readable view of a debug report."""
    summary = report["summary"]
    lines = [
        "# UPI debug report",
        "",
        f"- Files scanned: {summary['files_scanned']}",
        f"- Records classified: {summary['records_classified']}",
        f"- Findings: {summary['findings']}",
        f"- Verification: `{report['verification_type']}`",
        "",
        "## Findings",
        "",
    ]
    if not report["findings"]:
        lines.append("No schema or scientific-boundary findings.")
    for finding in report["findings"]:
        lines.extend(
            [
                f"### {finding['code']} · {finding['status']} · `{finding['path']}`",
                "",
                finding["message"],
                "",
                f"Correction: {finding['correction']}",
                "",
            ]
        )
    lines.extend(
        [
            "## Exploded-map guard",
            "",
            report["exploded_map"]["confusion_guard"],
            "",
        ]
    )
    return "\n".join(lines)
