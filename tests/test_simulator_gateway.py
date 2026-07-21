import json
import threading
from http.server import HTTPServer
from urllib.error import HTTPError
from urllib.request import Request, urlopen

from simulator.mock_gateway import MockGatewayHandler


def start_server() -> tuple[HTTPServer, threading.Thread, str]:
    server = HTTPServer(("127.0.0.1", 0), MockGatewayHandler)
    thread = threading.Thread(target=server.serve_forever, daemon=True)
    thread.start()
    host, port = server.server_address
    return server, thread, f"http://{host}:{port}"


def test_gateway_health_and_non_executing_registration() -> None:
    server, thread, base_url = start_server()
    try:
        with urlopen(f"{base_url}/health", timeout=2) as response:
            health = json.load(response)
        request = Request(
            f"{base_url}/plugins/register",
            data=json.dumps({"pluginId": "oden-core"}).encode(),
            headers={"Content-Type": "application/json"},
            method="POST",
        )
        with urlopen(request, timeout=2) as response:
            registration = json.load(response)

        assert health["verification_type"] == "software_test"
        assert registration == {
            "status": "accepted_for_simulation",
            "pluginId": "oden-core",
            "executed": False,
        }
    finally:
        server.shutdown()
        thread.join(timeout=2)
        server.server_close()


def test_gateway_rejects_invalid_manifest() -> None:
    server, thread, base_url = start_server()
    request = Request(
        f"{base_url}/plugins/register",
        data=b"{}",
        headers={"Content-Type": "application/json"},
        method="POST",
    )
    try:
        try:
            urlopen(request, timeout=2)
        except HTTPError as error:
            assert error.code == 400
        else:
            raise AssertionError("invalid manifest was accepted")
    finally:
        server.shutdown()
        thread.join(timeout=2)
        server.server_close()
