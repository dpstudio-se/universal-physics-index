import json
from pathlib import Path

import jsonschema
import pytest

from angelica_loader import AngelicaPluginLoader

ROOT = Path(__file__).parents[1]


@pytest.mark.parametrize("manifest_name", ["oden.json", "odens_eye.json"])
def test_simulation_manifests_are_default_deny(manifest_name: str) -> None:
    manifest = json.loads((ROOT / manifest_name).read_text(encoding="utf-8"))
    schema = json.loads((ROOT / "plugin.schema.json").read_text(encoding="utf-8"))

    jsonschema.Draft7Validator(schema).validate(manifest)
    assert manifest["mode"] == "simulation"
    assert manifest["enabled"] is False
    assert manifest["permissions"] == {"defaultDeny": True, "capabilities": []}


def test_simulation_manifest_cannot_build_spawn_command() -> None:
    loader = AngelicaPluginLoader(ROOT / "oden.json")

    with pytest.raises(RuntimeError, match="cannot be spawned"):
        loader.build_spawn_command()


def test_executable_manifest_requires_local_entrypoint(tmp_path: Path) -> None:
    manifest = json.loads((ROOT / "oden.json").read_text(encoding="utf-8"))
    manifest.update({"mode": "executable", "enabled": True, "entryPoint": "missing.py"})
    path = tmp_path / "plugin.json"
    path.write_text(json.dumps(manifest), encoding="utf-8")

    with pytest.raises(FileNotFoundError, match="entryPoint not found"):
        AngelicaPluginLoader(path)
