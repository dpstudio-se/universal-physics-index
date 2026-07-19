import json
import threading
import urllib.error
import urllib.request
from pathlib import Path

import pytest

from angelica_loader import AngelicaPluginLoader, validate_manifest
from angelica_simulator import create_server
from mock_server import create_server as create_mock_server
from repo_audit import audit_failed, audit_repo

REPOSITORY_ROOT = Path(__file__).parents[1]
PLUGIN_SCHEMA = REPOSITORY_ROOT / "plugin.schema.json"


@pytest.mark.parametrize("name", ["oden.json", "odens_eye.json"])
def test_repository_plugin_manifests_are_valid(name: str) -> None:
    loader = AngelicaPluginLoader(REPOSITORY_ROOT / name, schema_path=PLUGIN_SCHEMA)

    assert loader.manifest["pluginId"]


@pytest.mark.parametrize(
    ("field", "value"),
    [
        ("network", "host"),
        ("mounts", "/"),
    ],
)
def test_manifest_rejects_invalid_permission_shapes(field: str, value: object) -> None:
    manifest = json.loads((REPOSITORY_ROOT / "odens_eye.json").read_text(encoding="utf-8"))
    manifest["permissions"][field] = value

    with pytest.raises(ValueError, match="Invalid plugin manifest"):
        validate_manifest(manifest, schema_path=PLUGIN_SCHEMA)


def test_manifest_rejects_parent_directory_entrypoint() -> None:
    manifest = json.loads((REPOSITORY_ROOT / "odens_eye.json").read_text(encoding="utf-8"))
    manifest["entryPoint"] = "../escape.py"

    with pytest.raises(ValueError, match="entryPoint"):
        validate_manifest(manifest, schema_path=PLUGIN_SCHEMA)


def test_exec_permission_requires_explicit_policy_override() -> None:
    manifest = json.loads((REPOSITORY_ROOT / "odens_eye.json").read_text(encoding="utf-8"))
    manifest["permissions"]["exec"] = True

    with pytest.raises(PermissionError, match="disabled by default"):
        validate_manifest(manifest, schema_path=PLUGIN_SCHEMA)

    validate_manifest(manifest, schema_path=PLUGIN_SCHEMA, allow_exec=True)


def test_disabled_capabilities_harden_container_command(tmp_path: Path) -> None:
    manifest = json.loads((REPOSITORY_ROOT / "odens_eye.json").read_text(encoding="utf-8"))
    manifest["permissions"]["network"] = False
    manifest["permissions"]["file"] = False
    manifest_path = tmp_path / "plugin.json"
    manifest_path.write_text(json.dumps(manifest), encoding="utf-8")

    command = AngelicaPluginLoader(manifest_path, schema_path=PLUGIN_SCHEMA).build_command()

    assert command[command.index("--network") + 1] == "none"
    assert "--read-only" in command
    assert "host" not in command


def test_simulator_health_and_registration_contract() -> None:
    server = create_server("127.0.0.1", 0)
    thread = threading.Thread(target=server.serve_forever, daemon=True)
    thread.start()
    base_url = f"http://127.0.0.1:{server.server_port}"

    try:
        with urllib.request.urlopen(f"{base_url}/health") as response:
            assert response.status == 200

        manifest = (REPOSITORY_ROOT / "oden.json").read_bytes()
        request = urllib.request.Request(
            f"{base_url}/plugins/register",
            data=manifest,
            headers={"Content-Type": "application/json"},
            method="POST",
        )
        with urllib.request.urlopen(request) as response:
            assert response.status == 201
            assert json.load(response)["pluginId"] == "oden-core"
    finally:
        server.shutdown()
        server.server_close()
        thread.join(timeout=5)


def test_simulator_rejects_wrong_content_type() -> None:
    server = create_server("127.0.0.1", 0)
    thread = threading.Thread(target=server.serve_forever, daemon=True)
    thread.start()
    request = urllib.request.Request(
        f"http://127.0.0.1:{server.server_port}/plugins/register",
        data=b"{}",
        method="POST",
    )

    try:
        with pytest.raises(urllib.error.HTTPError) as captured:
            urllib.request.urlopen(request)
        assert captured.value.code == 415
    finally:
        server.shutdown()
        server.server_close()
        thread.join(timeout=5)


def test_mock_server_supports_get_and_post() -> None:
    server = create_mock_server(0)
    thread = threading.Thread(target=server.serve_forever, daemon=True)
    thread.start()
    base_url = f"http://127.0.0.1:{server.server_port}"

    try:
        with urllib.request.urlopen(base_url) as response:
            assert response.status == 200

        request = urllib.request.Request(base_url, data=b"{}", method="POST")
        with urllib.request.urlopen(request) as response:
            assert response.status == 201
    finally:
        server.shutdown()
        server.server_close()
        thread.join(timeout=5)


def test_simulator_script_has_bounded_requests_and_cleanup() -> None:
    script = (REPOSITORY_ROOT / "run_sim_tests.sh").read_text(encoding="utf-8")

    assert "trap cleanup EXIT" in script
    assert "--connect-timeout 2 --max-time 5" in script
    assert 'Content-Type: application/json' in script
    assert "--data-binary @oden.json" in script


def test_architecture_uses_repository_manifest_names() -> None:
    architecture = (REPOSITORY_ROOT / "ARCHITECTURE.md").read_text(encoding="utf-8")

    assert "`plugin.json`" not in architecture
    assert "`oden.json`" in architecture
    assert "`odens_eye.json`" in architecture


def test_audit_error_names_full_ports_path(tmp_path: Path) -> None:
    report = audit_repo(tmp_path)

    assert any(
        "config/ports.json" in message for message in report["critical_conflicts"]
    )


def test_repository_platform_audit_is_clean() -> None:
    report = audit_repo(REPOSITORY_ROOT)

    assert not audit_failed(report)
    assert report["manifest_errors"] == []
    assert report["port_conflicts"] == []
