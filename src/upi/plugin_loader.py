"""Validate plugin manifests without executing them."""

from __future__ import annotations

import json
from pathlib import Path
from typing import Any

import jsonschema


class AngelicaPluginLoader:
    """Load and validate a default-deny plugin manifest."""

    def __init__(self, manifest_path: str | Path, schema_path: str | Path | None = None):
        self.manifest_path = Path(manifest_path).resolve()
        self.schema_path = (
            Path(schema_path).resolve()
            if schema_path is not None
            else self.manifest_path.parent / "plugin.schema.json"
        )
        self.manifest: dict[str, Any] = json.loads(
            self.manifest_path.read_text(encoding="utf-8")
        )
        self.validate()

    def validate(self) -> None:
        """Validate schema, mode and executable entrypoint boundaries."""
        schema = json.loads(self.schema_path.read_text(encoding="utf-8"))
        jsonschema.Draft7Validator(schema).validate(self.manifest)

        if self.manifest["mode"] != "executable":
            return

        entrypoint = (self.manifest_path.parent / self.manifest["entryPoint"]).resolve()
        if not entrypoint.is_relative_to(self.manifest_path.parent):
            raise PermissionError("Plugin entryPoint must remain inside the manifest directory")
        if not entrypoint.is_file():
            raise FileNotFoundError(f"Plugin entryPoint not found: {entrypoint.name}")

    def build_spawn_command(self) -> list[str]:
        """Fail closed because this validation layer cannot enforce runtime capabilities."""
        if self.manifest["mode"] != "executable" or not self.manifest["enabled"]:
            raise RuntimeError("Simulation or disabled plugin cannot be spawned")
        raise RuntimeError(
            "Executable plugin spawning is not implemented; manifest validation "
            "does not provide a runtime security boundary"
        )
