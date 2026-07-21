"""Deterministic repository-level integrity audit for UPI."""

from __future__ import annotations

import argparse
import json
from pathlib import Path
from typing import Any

from jsonschema import Draft7Validator
from jsonschema.exceptions import SchemaError

RECORD_SCHEMAS = ("node", "bridge", "theory")
CRITICAL_FILES = (
    "plugin.schema.json",
    "config/ports.json",
    "config/external_index_sources.json",
    ".env.example",
    "ARCHITECTURE.md",
)
PLUGIN_MANIFESTS = ("oden.json", "odens_eye.json")


def _load_json(path: Path) -> Any:
    return json.loads(path.read_text(encoding="utf-8"))


def _record_type(data: dict[str, Any]) -> str | None:
    if {"source", "target", "relation"} <= data.keys():
        return "bridge"
    if {"address", "title", "description", "status", "domain", "scope"} <= data.keys():
        return "theory"
    if {"address", "title", "status"} <= data.keys():
        return "node"
    return None


def _format_validation_error(path: Path, error: object) -> str:
    return f"{path.as_posix()}: {error}"


def audit_repo(root: Path = Path(".")) -> dict[str, Any]:
    """Return a deterministic audit report without mutating repository content."""
    root = root.resolve()
    report: dict[str, Any] = {
        "critical_conflicts": [],
        "missing_files": [],
        "port_conflicts": [],
        "schema_errors": [],
        "data_errors": [],
        "manifest_errors": [],
        "files_scanned": 0,
        "records_validated": 0,
        "verification_type": "software_test",
        "claims_experimental_verification": False,
    }

    for critical_file in CRITICAL_FILES:
        if not (root / critical_file).is_file():
            report["missing_files"].append(critical_file)

    schemas: dict[str, dict[str, Any]] = {}
    for schema_name in RECORD_SCHEMAS:
        schema_path = root / "schemas" / f"{schema_name}.schema.json"
        try:
            schema = _load_json(schema_path)
            if not isinstance(schema, dict):
                raise TypeError("schema top level must be an object")
            Draft7Validator.check_schema(schema)
            schemas[schema_name] = schema
        except (OSError, UnicodeError, json.JSONDecodeError, TypeError, SchemaError) as error:
            report["schema_errors"].append(
                _format_validation_error(schema_path.relative_to(root), error)
            )

    data_root = root / "data"
    if data_root.is_dir():
        for path in sorted(data_root.rglob("*.json")):
            relative_path = path.relative_to(root)
            if path.name.startswith("invalid_"):
                continue
            try:
                data = _load_json(path)
            except (OSError, UnicodeError, json.JSONDecodeError) as error:
                report["data_errors"].append(_format_validation_error(relative_path, error))
                continue
            if not isinstance(data, dict):
                report["data_errors"].append(
                    f"{relative_path.as_posix()}: top level must be an object"
                )
                continue
            record_kind = _record_type(data)
            if record_kind is None:
                report["data_errors"].append(
                    f"{relative_path.as_posix()}: unclassified data record; expected node, bridge, or theory"
                )
                continue
            schema = schemas.get(record_kind)
            if schema is None:
                report["data_errors"].append(
                    f"{relative_path.as_posix()}: {record_kind} schema is unavailable"
                )
                continue
            errors = sorted(Draft7Validator(schema).iter_errors(data), key=str)
            if errors:
                report["data_errors"].extend(
                    f"{relative_path.as_posix()}: {error.json_path or '$'} failed "
                    f"{error.validator} validation"
                    for error in errors
                )
                continue
            report["records_validated"] += 1

    ports_path = root / "config" / "ports.json"
    try:
        ports_data = _load_json(ports_path)
        ports = ports_data.get("ports", {}) if isinstance(ports_data, dict) else {}
        if not isinstance(ports, dict) or not ports:
            raise ValueError("ports must be a non-empty object")
        values = list(ports.values())
        invalid_port = any(
            isinstance(port, bool)
            or not isinstance(port, int)
            or not 1 <= port <= 65535
            for port in values
        )
        if invalid_port:
            report["port_conflicts"].append(
                "Every configured port must be an integer in 1..65535"
            )
        if len(values) != len(set(values)):
            report["port_conflicts"].append("Duplicate ports found in config/ports.json")
    except (OSError, UnicodeError, json.JSONDecodeError, ValueError) as error:
        report["critical_conflicts"].append(f"Error reading config/ports.json: {error}")

    source_manifest_path = root / "config" / "external_index_sources.json"
    try:
        source_manifest = _load_json(source_manifest_path)
        if not isinstance(source_manifest, dict):
            raise TypeError("source manifest top level must be an object")
        if source_manifest.get("operation") != "upi_external_source_manifest":
            raise ValueError("unexpected source manifest operation")
        sources = source_manifest.get("sources")
        if not isinstance(sources, list) or not sources:
            raise ValueError("source manifest requires a non-empty sources array")
        source_ids: list[str] = []
        for source in sources:
            if not isinstance(source, dict):
                raise ValueError("every source must be an object")
            source_id = source.get("source_id")
            if not isinstance(source_id, str) or not source_id:
                raise ValueError("every source requires a non-empty string source_id")
            source_ids.append(source_id)
        if len(source_ids) != len(set(source_ids)):
            raise ValueError("source_id values must be unique")
    except (OSError, UnicodeError, json.JSONDecodeError, TypeError, ValueError) as error:
        report["manifest_errors"].append(f"config/external_index_sources.json: {error}")

    plugin_schema_path = root / "plugin.schema.json"
    try:
        plugin_schema = _load_json(plugin_schema_path)
        if not isinstance(plugin_schema, dict):
            raise TypeError("plugin schema top level must be an object")
        Draft7Validator.check_schema(plugin_schema)
        validator = Draft7Validator(plugin_schema)
        for manifest_name in PLUGIN_MANIFESTS:
            manifest_path = root / manifest_name
            manifest = _load_json(manifest_path)
            errors = sorted(validator.iter_errors(manifest), key=str)
            report["manifest_errors"].extend(
                f"{manifest_name}: {error.json_path or '$'} failed {error.validator} validation"
                for error in errors
            )
    except (OSError, UnicodeError, json.JSONDecodeError, TypeError, SchemaError) as error:
        report["manifest_errors"].append(f"Plugin manifest validation failed: {error}")

    report["files_scanned"] = sum(1 for path in root.rglob("*") if path.is_file())
    blocking_fields = (
        "critical_conflicts",
        "missing_files",
        "port_conflicts",
        "schema_errors",
        "data_errors",
        "manifest_errors",
    )
    report["blocking_findings"] = sum(len(report[field]) for field in blocking_fields)
    return report


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--output", default="report.json")
    args = parser.parse_args()

    result = audit_repo()
    Path(args.output).write_text(json.dumps(result, indent=2) + "\n", encoding="utf-8")
    print(f"Audit complete. Report written to {args.output}")
    return 1 if result["blocking_findings"] else 0


if __name__ == "__main__":
    raise SystemExit(main())
