"""Deterministic repository checks for the VR-ASI-1 scaffold."""

from __future__ import annotations

import argparse
import json
from pathlib import Path
from typing import Any

from jsonschema import Draft7Validator

CRITICAL_FILES = (
    "plugin.schema.json",
    "config/ports.json",
    ".env.example",
    "ARCHITECTURE.md",
    "Dockerfile.simulator",
    "docker-compose.simulator.yml",
    "angelica_simulator.py",
    "mock_server.py",
)
PLUGIN_MANIFESTS = ("oden.json", "odens_eye.json")
IGNORED_DIRECTORIES = {".git", ".mypy_cache", ".pytest_cache", ".ruff_cache", ".venv", "build", "dist"}


def audit_repo(root: Path = Path(".")) -> dict[str, Any]:
    """Audit required files, ports, and plugin manifests below *root*."""
    root = root.resolve()
    report: dict[str, Any] = {
        "critical_conflicts": [],
        "missing_files": [],
        "port_conflicts": [],
        "manifest_errors": [],
        "files_scanned": 0,
    }

    for relative_path in (*CRITICAL_FILES, *PLUGIN_MANIFESTS):
        if not (root / relative_path).is_file():
            report["missing_files"].append(relative_path)

    try:
        ports = json.loads((root / "config/ports.json").read_text(encoding="utf-8")).get(
            "ports", {}
        )
        port_values = list(ports.values())
        if len(port_values) != len(set(port_values)):
            report["port_conflicts"].append("Duplicate ports found in config/ports.json")
    except (OSError, ValueError, AttributeError) as error:
        report["critical_conflicts"].append(
            f"Error reading config/ports.json: {error}"
        )

    try:
        schema = json.loads((root / "plugin.schema.json").read_text(encoding="utf-8"))
        Draft7Validator.check_schema(schema)
        validator = Draft7Validator(schema)
        for manifest_name in PLUGIN_MANIFESTS:
            manifest = json.loads((root / manifest_name).read_text(encoding="utf-8"))
            for schema_error in sorted(validator.iter_errors(manifest), key=str):
                path = ".".join(str(part) for part in schema_error.path) or "$"
                report["manifest_errors"].append(
                    f"{manifest_name}:{path}: {schema_error.message}"
                )
    except (OSError, ValueError) as error:
        report["critical_conflicts"].append(f"Error validating plugin manifests: {error}")

    report["files_scanned"] = sum(
        1
        for path in root.rglob("*")
        if path.is_file() and not IGNORED_DIRECTORIES.intersection(path.relative_to(root).parts)
    )
    return report


def audit_failed(report: dict[str, Any]) -> bool:
    """Return whether an audit report contains blocking findings."""
    return any(
        report[key]
        for key in (
            "critical_conflicts",
            "missing_files",
            "port_conflicts",
            "manifest_errors",
        )
    )


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--root", type=Path, default=Path("."))
    parser.add_argument("--output", type=Path, default=Path("report.json"))
    args = parser.parse_args()

    result = audit_repo(args.root)
    args.output.write_text(json.dumps(result, indent=2) + "\n", encoding="utf-8")
    print(f"Audit complete. Report written to {args.output}")
    return int(audit_failed(result))


if __name__ == "__main__":
    raise SystemExit(main())
