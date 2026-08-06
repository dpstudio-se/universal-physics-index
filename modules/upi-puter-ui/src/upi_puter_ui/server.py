"""HTTP server implementation for the upi-puter-ui module with Odysseus AI Protocol Bridge."""

from __future__ import annotations

import argparse
import http.server
import json
import socketserver
import webbrowser
from pathlib import Path
from typing import Any

from upi_odysseus_bridge import (
    OdysseusIntentExecutor,
    OdysseusToolRegistry,
    execute_odysseus_tool,
)

from upi.physics import dna_sequence_to_frequencies
from upi.qudit import search_torus_register

PUBLIC_DIR = Path(__file__).resolve().parents[2] / "public"


class UPIPuterUIHandler(http.server.SimpleHTTPRequestHandler):
    """HTTP Request Handler serving static web assets, Puter API, and Odysseus AI endpoints."""

    def __init__(self, *args: Any, **kwargs: Any) -> None:
        super().__init__(*args, directory=str(PUBLIC_DIR), **kwargs)

    def do_GET(self) -> None:
        if self.path.startswith("/api/health"):
            self._send_json({
                "status": "EST",
                "service": "upi-puter-ui",
                "odysseus_bridge": "active",
                "version": "0.1.0",
                "verification_type": "software_test",
                "reference_freq_hz": 8.0
            })
            return

        if self.path.startswith("/api/odysseus/tools"):
            tools = OdysseusToolRegistry.get_manifest()
            self._send_json({
                "protocol": "Odysseus AI Agent Protocol v1.0",
                "status": "DER",
                "tools": tools
            })
            return

        super().do_GET()

    def do_POST(self) -> None:
        content_length = int(self.headers.get("Content-Length", 0))
        body_bytes = self.rfile.read(content_length)

        try:
            payload = json.loads(body_bytes.decode("utf-8")) if body_bytes else {}
        except json.JSONDecodeError:
            self._send_json({"error": "Invalid JSON body"}, status=400)
            return

        if self.path == "/api/sonify":
            sequence = payload.get("sequence", "ATGC")
            ref_a4 = float(payload.get("reference_a4_hz", 440.0))
            traces = dna_sequence_to_frequencies(sequence, reference_a4_hz=ref_a4)
            self._send_json({
                "operation": "dna_sonification",
                "status": "DER",
                "sequence": sequence,
                "reference_a4_hz": ref_a4,
                "traces": traces
            })
            return

        if self.path == "/api/qudit-search":
            dims = tuple(payload.get("dimensions", [4, 5]))
            targets = tuple(payload.get("targets", [7]))
            iterations = int(payload.get("iterations", 2))
            res = search_torus_register(dims, targets, iterations=iterations)
            self._send_json({
                "operation": "qudit_torus_search",
                "status": "DER",
                "verification_type": "software_test",
                "dimensions": res.dimensions,
                "total_states": res.total_states,
                "target_indices": list(res.target_indices),
                "success_probability": res.success_probability,
                "interpretation": "classical_state_vector_qudit_simulator"
            })
            return

        if self.path == "/api/odysseus/execute":
            tool_name = payload.get("tool")
            arguments = payload.get("arguments", {})
            if not tool_name:
                self._send_json({"error": "Missing 'tool' in request body"}, status=400)
                return
            result = execute_odysseus_tool(tool_name, arguments)
            self._send_json(result)
            return

        if self.path == "/api/odysseus/intent":
            prompt = payload.get("prompt", "")
            result = OdysseusIntentExecutor.parse_and_execute_intent(prompt)
            self._send_json(result)
            return

        self._send_json({"error": "Endpoint not found"}, status=404)

    def _send_json(self, data: dict[str, Any], status: int = 200) -> None:
        body = json.dumps(data, indent=2).encode("utf-8")
        self.send_response(status)
        self.send_header("Content-Type", "application/json")
        self.send_header("Content-Length", str(len(body)))
        self.send_header("Access-Control-Allow-Origin", "*")
        self.end_headers()
        self.wfile.write(body)


def run_server(host: str = "127.0.0.1", port: int = 8080, open_browser: bool = False) -> None:
    """Run the upi-puter-ui HTTP server."""
    handler = UPIPuterUIHandler
    with socketserver.TCPServer((host, port), handler) as httpd:
        url = f"http://{host}:{port}/"
        print(f"🚀 UPI Puter + Odysseus AI Gateway running at {url}")
        if open_browser:
            webbrowser.open(url)
        try:
            httpd.serve_forever()
        except KeyboardInterrupt:
            print("\nShutting down UPI Puter UI server.")
            httpd.server_close()


def main() -> None:
    parser = argparse.ArgumentParser(description="UPI & OdinOS Puter.js + Odysseus AI Module Server")
    parser.add_argument("--host", default="127.0.0.1", help="Host address to bind (default 127.0.0.1)")
    parser.add_argument("--port", type=int, default=8080, help="Port to bind (default 8080)")
    parser.add_argument("--open", action="store_true", help="Automatically open web browser")
    args = parser.parse_args()

    run_server(host=args.host, port=args.port, open_browser=args.open)


if __name__ == "__main__":
    main()
