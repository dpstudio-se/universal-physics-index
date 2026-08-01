"""Deterministic, index-wide UPI debugging and exploded-map generation."""

from __future__ import annotations

import json
from collections import Counter
from hashlib import sha256
from pathlib import Path
from typing import Any

from .schema_resources import schemas_dir as packaged_schemas_dir
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
    "UPI-O001": "Keep one canonical record or document why both mirrored paths are required.",
    "UPI-O002": "Resolve the conflicting records or assign distinct UPI identities.",
    "UPI-O003": "Review whether the hidden path is intentional and document its purpose.",
    "UPI-O004": "Review the semantic overlap; merge, distinguish, or link the records explicitly.",
}
VALID_STATUSES = {"EST", "DER", "HYP", "STOP", "ERR", "SYM"}


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


def _redacted_scale_signature(data: dict[str, Any]) -> dict[str, Any]:
    scale = _scale_signature(data)
    return {
        "scope_declared": scale["scope"] != "unspecified",
        "unit_count": len(scale["units"]),
        "time_scale_declared": scale["time_scale"] != "unspecified",
        "length_scale_declared": scale["length_scale"] != "unspecified",
    }


def _list_count(value: Any) -> int:
    return len(value) if isinstance(value, list) else 0


def _canonical_hash(data: dict[str, Any]) -> str:
    encoded = json.dumps(
        data,
        ensure_ascii=False,
        separators=(",", ":"),
        sort_keys=True,
    ).encode("utf-8")
    return sha256(encoded).hexdigest()


def _semantic_signature(data: dict[str, Any]) -> str | None:
    title = " ".join(str(data.get("title", "")).lower().split())
    equations = data.get("equations", data.get("fundamental_equations", []))
    if not title or not isinstance(equations, list):
        return None
    normalized_equations = sorted(" ".join(str(item).lower().split()) for item in equations)
    if not normalized_equations:
        return None
    return json.dumps([title, normalized_equations], separators=(",", ":"))


def _record_identity(data: dict[str, Any], record_type: str) -> str:
    if record_type == "bridge":
        return f"{data.get('source')}->{data.get('target')}:{data.get('relation')}"
    return str(data.get("address"))


def _text_hash(value: str) -> str:
    return sha256(value.encode("utf-8")).hexdigest()


def _group_by(items: list[dict[str, Any]], key: str) -> list[list[dict[str, Any]]]:
    grouped: dict[str, list[dict[str, Any]]] = {}
    for item in items:
        value = item.get(key)
        if value:
            grouped.setdefault(str(value), []).append(item)
    return [group for group in grouped.values() if len(group) > 1]


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
    return [
        f"{error.json_path or '$'} failed {error.validator} validation."
        for error in sorted(validator.iter_errors(data), key=str)
    ]


def generate_debug_report(
    root: Path,
    schemas_dir: Path | None = None,
    *,
    odins_eye: bool = False,
) -> dict[str, Any]:
    """Scan every JSON record below *root* and return a UPI debug report.

    The report is deterministic and AI-ready. It never mutates source records and
    never upgrades software validation to experimental evidence.
    """
    root = root.resolve()
    schemas_dir = (schemas_dir or packaged_schemas_dir()).resolve()
    findings: list[dict[str, Any]] = []
    records: list[dict[str, Any]] = []
    status_counts: Counter[str] = Counter()
    type_counts: Counter[str] = Counter()
    inspection_records: list[dict[str, Any]] = []
    json_paths = sorted(root.rglob("*.json"))

    for path in json_paths:
        relative_path = path.relative_to(root).as_posix()
        if odins_eye and any(part.startswith(".") for part in Path(relative_path).parts):
            findings.append(
                _finding(
                    "UPI-O003",
                    "EST",
                    relative_path,
                    "JSON record is stored below a hidden path.",
                )
            )
        try:
            data = json.loads(path.read_text(encoding="utf-8"))
        except (OSError, UnicodeError, json.JSONDecodeError) as parse_error:
            findings.append(_finding("UPI-D001", "ERR", relative_path, str(parse_error)))
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
        reported_status = status if not odins_eye or status in VALID_STATUSES else "INVALID"
        status_counts[reported_status] += 1
        type_counts[record_type] += 1
        identity = _record_identity(data, record_type)
        content_hash = _canonical_hash(data)
        records.append(
            {
                "identity_hash": _text_hash(identity),
                "path": relative_path,
                "record_type": record_type,
                "status": reported_status,
                "scale": (
                    _redacted_scale_signature(data) if odins_eye else _scale_signature(data)
                ),
                "evidence_count": _list_count(data.get("evidence")),
                "equation_count": _list_count(
                    data.get("equations", data.get("fundamental_equations"))
                ),
            }
        )
        inspection_records.append(
            {
                "path": relative_path,
                "identity": identity,
                "content_hash": content_hash,
                "semantic_signature": _semantic_signature(data),
            }
        )

        for schema_error in _schema_errors(data, record_type, schemas_dir):
            findings.append(
                _finding("UPI-D003", "ERR", relative_path, schema_error, record_type=record_type)
            )

        for boundary_error in validate_record_boundaries(data):
            code = boundary_error.split(":", 1)[0]
            findings.append(
                _finding(code, "ERR", relative_path, boundary_error, record_type=record_type)
            )

        if record_type == "node" and status == "HYP" and not data.get("falsification_conditions"):
            findings.append(
                _finding(
                    "UPI-D004",
                    "STOP",
                    relative_path,
                    "Hypothesis has no falsification_conditions.",
                    record_type=record_type,
                )
            )

    mirror_groups: list[dict[str, Any]] = []
    shadow_groups: list[dict[str, Any]] = []
    semantic_groups: list[dict[str, Any]] = []
    if odins_eye:
        for group in _group_by(inspection_records, "content_hash"):
            paths = sorted(item["path"] for item in group)
            content_hash = group[0]["content_hash"]
            mirror_groups.append({"content_hash": content_hash, "paths": paths})
            findings.append(
                _finding(
                    "UPI-O001",
                    "EST",
                    paths[0],
                    f"Exact mirror detected across {len(paths)} paths: {', '.join(paths)}.",
                )
            )

        for group in _group_by(inspection_records, "identity"):
            hashes = sorted({item["content_hash"] for item in group})
            if len(hashes) < 2:
                continue
            paths = sorted(item["path"] for item in group)
            identity_hash = _text_hash(group[0]["identity"])
            shadow_groups.append(
                {"identity_hash": identity_hash, "content_hashes": hashes, "paths": paths}
            )
            findings.append(
                _finding(
                    "UPI-O002",
                    "ERR",
                    paths[0],
                    f"Shadow conflict: identity hash {identity_hash} has different content at "
                    f"{', '.join(paths)}.",
                )
            )

        exact_mirror_paths = {path for group in mirror_groups for path in group["paths"]}
        for group in _group_by(inspection_records, "semantic_signature"):
            paths = sorted(item["path"] for item in group)
            semantic_hashes = {item["content_hash"] for item in group}
            if len(semantic_hashes) < 2 or set(paths) <= exact_mirror_paths:
                continue
            semantic_groups.append({"paths": paths})
            findings.append(
                _finding(
                    "UPI-O004",
                    "HYP",
                    paths[0],
                    f"Possible semantic mirror across {len(paths)} paths: {', '.join(paths)}.",
                )
            )

    map_nodes: list[dict[str, Any]] = []
    map_edges: list[dict[str, str]] = []
    for index, record in enumerate(records):
        record_node = f"record:{index}"
        scale_node = f"scale:{index}"
        map_nodes.extend(
            [
                {**record, "id": record_node, "layer": "record"},
                {"id": scale_node, "layer": "scale", "value": record["scale"]},
            ]
        )
        map_edges.append(
            {"source": record_node, "target": scale_node, "relation": "MEASURED_BY"}
        )
        if record["evidence_count"] > 0:
            evidence_node = f"evidence:{index}"
            map_nodes.append(
                {
                    "id": evidence_node,
                    "layer": "evidence",
                    "count": record["evidence_count"],
                }
            )
            map_edges.append(
                {"source": record_node, "target": evidence_node, "relation": "DERIVED_FROM"}
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

    if odins_eye:
        record_nodes_by_path = {
            record["path"]: f"record:{index}" for index, record in enumerate(records)
        }
        relation_groups: list[tuple[str, str, list[dict[str, Any]]]] = [
            ("mirror", "FORM_SIMILAR", mirror_groups),
            ("shadow", "CONTRADICTS", shadow_groups),
            ("mirror", "FORM_SIMILAR", semantic_groups),
        ]
        relation_index = 0
        for layer, relation, groups in relation_groups:
            for relation_group in groups:
                relation_node = f"{layer}:{relation_index}"
                relation_index += 1
                map_nodes.append({"id": relation_node, "layer": layer, **relation_group})
                for path in relation_group["paths"]:
                    if path in record_nodes_by_path:
                        map_edges.append(
                            {
                                "source": record_nodes_by_path[path],
                                "target": relation_node,
                                "relation": relation,
                            }
                        )

    return {
        "schema_version": "0.1.0",
        "operation": "upi_debug_index",
        "root": "." if odins_eye else str(root),
        "verification_type": "software_test",
        "claims_experimental_verification": False,
        "summary": {
            "files_scanned": len(json_paths),
            "records_classified": len(records),
            "findings": len(findings),
            "status_counts": dict(sorted(status_counts.items())),
            "record_type_counts": dict(sorted(type_counts.items())),
        },
        "findings": findings,
        "odins_eye": {
            "enabled": odins_eye,
            "mode": "local_read_only",
            "secret_values_exposed": False,
            "source_values_redacted": odins_eye,
            "mirror_groups": mirror_groups,
            "shadow_groups": shadow_groups,
            "semantic_mirror_groups": semantic_groups,
        },
        "exploded_map": {
            "layers": [
                "record",
                "scale",
                "evidence",
                "finding",
                "correction",
                *(["shadow", "mirror"] if odins_eye else []),
            ],
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
