"""Validate plugin manifests without executing them."""

from __future__ import annotations

import json
from pathlib import Path
from typing import Any

import jsonschema


class AngelicaPluginLoader:
    """Load and validate a default-deny plugin manifest."""

    def __init__(self, manifest_path: str | Path):
        self.manifest_path = Path(manifest_path).resolve()
        self.manifest: dict[str, Any] = json.loads(
            self.manifest_path.read_text(encoding="utf-8")
        )
        self.validate()

    def validate(self) -> None:
        """Validate schema, mode and executable entrypoint boundaries."""
        schema_path = Path(__file__).resolve().parent / "plugin.schema.json"
        schema = json.loads(schema_path.read_text(encoding="utf-8"))
        jsonschema.Draft7Validator(schema).validate(self.manifest)

        if self.manifest["mode"] != "executable":
            return

        entrypoint = (self.manifest_path.parent / self.manifest["entryPoint"]).resolve()
        if not entrypoint.is_relative_to(self.manifest_path.parent):
            raise PermissionError("Plugin entryPoint must remain inside the manifest directory")
        if not entrypoint.is_file():
            raise FileNotFoundError(f"Plugin entryPoint not found: {entrypoint.name}")

    def build_spawn_command(self) -> list[str]:
        """Build, but never execute, a command for an enabled executable plugin."""
        if self.manifest["mode"] != "executable" or not self.manifest["enabled"]:
            raise RuntimeError("Simulation or disabled plugin cannot be spawned")
        return [
            "docker",
            "run",
            "--rm",
            "--name",
            self.manifest["pluginId"],
            "--memory",
            self.manifest["resources"]["memory"],
            "vrasi1-plugin-base",
        ]


if __name__ == "__main__":
    loader = AngelicaPluginLoader("oden.json")
    print(f"Validated {loader.manifest['pluginId']} in {loader.manifest['mode']} mode")
