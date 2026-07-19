"""Validated, policy-aware loader for VR-ASI-1 plugin manifests."""

from __future__ import annotations

import json
import subprocess
from pathlib import Path
from typing import Any

from jsonschema import Draft7Validator

DEFAULT_SCHEMA_PATH = Path(__file__).with_name("plugin.schema.json")


def validate_manifest(
    manifest: dict[str, Any],
    *,
    schema_path: Path = DEFAULT_SCHEMA_PATH,
    allow_exec: bool = False,
) -> None:
    """Validate a manifest against its schema and the default sandbox policy."""
    schema = json.loads(schema_path.read_text(encoding="utf-8"))
    validator = Draft7Validator(schema)
    errors = sorted(validator.iter_errors(manifest), key=lambda error: list(error.path))
    if errors:
        details = "; ".join(
            f"{'.'.join(str(part) for part in error.path) or '$'}: {error.message}"
            for error in errors
        )
        raise ValueError(f"Invalid plugin manifest: {details}")

    if manifest["permissions"]["exec"] and not allow_exec:
        raise PermissionError(
            "Plugin shell execution is disabled by default; pass allow_exec=True explicitly"
        )


class AngelicaPluginLoader:
    """Load one plugin manifest and build a constrained container command."""

    def __init__(
        self,
        manifest_path: str | Path,
        *,
        schema_path: Path = DEFAULT_SCHEMA_PATH,
        allow_exec: bool = False,
    ) -> None:
        self.manifest_path = Path(manifest_path)
        self.manifest: dict[str, Any] = json.loads(
            self.manifest_path.read_text(encoding="utf-8")
        )
        validate_manifest(
            self.manifest,
            schema_path=schema_path,
            allow_exec=allow_exec,
        )

    def build_command(self) -> list[str]:
        """Return the Docker command without executing it."""
        resources = self.manifest.get("resources", {})
        permissions = self.manifest["permissions"]
        command = [
            "docker",
            "run",
            "-d",
            "--name",
            self.manifest["pluginId"],
            "--memory",
            resources.get("memory", "512Mi"),
            "--cpus",
            resources.get("cpu", "1.0"),
        ]
        if not permissions["network"]:
            command.extend(["--network", "none"])
        if not permissions["file"]:
            command.append("--read-only")
        command.append("vrasi1-plugin-base")
        return command

    def spawn(self, *, execute: bool = False) -> list[str]:
        """Build the sandbox command and optionally execute it."""
        command = self.build_command()
        if execute:
            subprocess.run(command, check=True)
        return command


if __name__ == "__main__":
    loader = AngelicaPluginLoader("oden.json")
    print(" ".join(loader.spawn()))
