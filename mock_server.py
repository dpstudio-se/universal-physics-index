"""Small HTTP mock used by the Docker Compose simulator."""

from __future__ import annotations

import argparse
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer


class MockHandler(BaseHTTPRequestHandler):
    """Return deterministic responses without reflecting request data."""

    def _write_response(self, status: int, body: bytes) -> None:
        self.send_response(status)
        self.send_header("Content-Type", "text/plain")
        self.send_header("Content-Length", str(len(body)))
        self.end_headers()
        self.wfile.write(body)

    def do_GET(self) -> None:
        self._write_response(200, b"Mock Response OK")

    def do_POST(self) -> None:
        self._write_response(201, b"Mock POST OK")

    def log_message(self, format: str, *args: object) -> None:
        print(f"{self.address_string()} - {format % args}")


def create_server(port: int) -> ThreadingHTTPServer:
    """Create a mock server bound to all container interfaces."""

    return ThreadingHTTPServer(("0.0.0.0", port), MockHandler)


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("port", type=int)
    arguments = parser.parse_args()
    create_server(arguments.port).serve_forever()
