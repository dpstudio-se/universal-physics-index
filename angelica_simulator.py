"""Minimal Angelica HTTP service used only by the repository simulator."""

from __future__ import annotations

import json
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer
from typing import Any

from angelica_loader import validate_manifest

MAX_REQUEST_BYTES = 1024 * 1024


class AngelicaSimulatorHandler(BaseHTTPRequestHandler):
    """Serve health checks and validate plugin-registration requests."""

    server_version = "AngelicaSimulator/0.1"

    def _write_json(self, status: int, body: dict[str, Any]) -> None:
        encoded = json.dumps(body).encode("utf-8")
        self.send_response(status)
        self.send_header("Content-Type", "application/json")
        self.send_header("Content-Length", str(len(encoded)))
        self.end_headers()
        self.wfile.write(encoded)

    def do_GET(self) -> None:
        if self.path == "/health":
            self._write_json(200, {"status": "ok"})
            return
        self._write_json(404, {"error": "not_found"})

    def do_POST(self) -> None:
        if self.path != "/plugins/register":
            self._write_json(404, {"error": "not_found"})
            return
        if self.headers.get_content_type() != "application/json":
            self._write_json(415, {"error": "application/json required"})
            return

        try:
            content_length = int(self.headers.get("Content-Length", "0"))
        except ValueError:
            self._write_json(400, {"error": "invalid Content-Length"})
            return
        if content_length <= 0 or content_length > MAX_REQUEST_BYTES:
            self._write_json(413, {"error": "invalid request size"})
            return

        try:
            manifest = json.loads(self.rfile.read(content_length))
            if not isinstance(manifest, dict):
                raise ValueError("manifest must be a JSON object")
            validate_manifest(manifest)
        except (json.JSONDecodeError, PermissionError, ValueError) as error:
            self._write_json(400, {"error": str(error)})
            return

        self._write_json(201, {"pluginId": manifest["pluginId"], "status": "registered"})

    def log_message(self, format: str, *args: object) -> None:
        # Keep simulator output deterministic and avoid echoing request contents.
        print(f"{self.address_string()} - {format % args}")


def create_server(
    host: str = "0.0.0.0",
    port: int = 8080,
) -> ThreadingHTTPServer:
    """Create the simulator server without starting its event loop."""
    return ThreadingHTTPServer((host, port), AngelicaSimulatorHandler)


if __name__ == "__main__":
    create_server().serve_forever()
