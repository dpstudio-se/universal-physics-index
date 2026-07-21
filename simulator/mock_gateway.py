"""Minimal non-executing HTTP service for the local VR-ASI-1 simulator."""

from __future__ import annotations

import json
import os
from http import HTTPStatus
from http.server import BaseHTTPRequestHandler, HTTPServer
from typing import Any

MAX_BODY_BYTES = 1_048_576


class MockGatewayHandler(BaseHTTPRequestHandler):
    """Serve health checks and accept manifests for simulation only."""

    server_version = "UPISimulator/0.1"

    def _send_json(self, status: HTTPStatus, payload: dict[str, Any]) -> None:
        body = json.dumps(payload).encode("utf-8")
        self.send_response(status)
        self.send_header("Content-Type", "application/json")
        self.send_header("Content-Length", str(len(body)))
        self.end_headers()
        self.wfile.write(body)

    def do_GET(self) -> None:  # noqa: N802 - BaseHTTPRequestHandler API
        if self.path not in {"/", "/health"}:
            self._send_json(HTTPStatus.NOT_FOUND, {"error": "not_found"})
            return
        self._send_json(
            HTTPStatus.OK,
            {
                "status": "ok",
                "service": os.environ.get("SERVICE_NAME", "simulation"),
                "verification_type": "software_test",
            },
        )

    def do_POST(self) -> None:  # noqa: N802 - BaseHTTPRequestHandler API
        if self.path != "/plugins/register":
            self._send_json(HTTPStatus.NOT_FOUND, {"error": "not_found"})
            return
        length = int(self.headers.get("Content-Length", "0"))
        if length <= 0 or length > MAX_BODY_BYTES:
            self._send_json(HTTPStatus.BAD_REQUEST, {"error": "invalid_body_size"})
            return
        try:
            manifest = json.loads(self.rfile.read(length))
        except (json.JSONDecodeError, UnicodeDecodeError):
            self._send_json(HTTPStatus.BAD_REQUEST, {"error": "invalid_json"})
            return
        if not isinstance(manifest, dict) or not isinstance(manifest.get("pluginId"), str):
            self._send_json(HTTPStatus.BAD_REQUEST, {"error": "invalid_manifest"})
            return
        self._send_json(
            HTTPStatus.CREATED,
            {
                "status": "accepted_for_simulation",
                "pluginId": manifest["pluginId"],
                "executed": False,
            },
        )

    def log_message(self, format: str, *args: object) -> None:
        """Keep simulator output deterministic and free of request metadata."""


def main() -> None:
    """Run the simulator service on its declared container port."""
    port = int(os.environ.get("PORT", "8080"))
    HTTPServer(("0.0.0.0", port), MockGatewayHandler).serve_forever()


if __name__ == "__main__":
    main()
