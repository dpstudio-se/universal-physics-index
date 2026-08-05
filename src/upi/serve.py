"""Inside-Out Server & Web AI Bridge Launcher for UPI."""

from __future__ import annotations

import argparse
import json
import urllib.error
import urllib.request
from http.server import HTTPServer, SimpleHTTPRequestHandler
from pathlib import Path
from typing import Any

from .kernel import get_kernel
from upi_odysseus_bridge import (
    OdysseusIntentExecutor,
    get_odysseus_tools_manifest,
)

PUBLIC_DIR = Path(__file__).resolve().parents[2] / "modules" / "upi-puter-ui" / "public"


class UPIInsideOutHandler(SimpleHTTPRequestHandler):
    """HTTP Request Handler serving Puter UI, Odysseus AI Bridge, Kernel APIs, and AI Proxy."""

    def __init__(self, *args: Any, **kwargs: Any) -> None:
        super().__init__(*args, directory=str(PUBLIC_DIR), **kwargs)

    def _send_json(self, data: dict[str, Any], status_code: int = 200) -> None:
        payload = json.dumps(data, indent=2, ensure_ascii=False).encode("utf-8")
        self.send_response(status_code)
        self.send_header("Content-Type", "application/json; charset=utf-8")
        self.send_header("Access-Control-Allow-Origin", "*")
        self.send_header("Access-Control-Allow-Methods", "GET, POST, OPTIONS")
        self.send_header("Access-Control-Allow-Headers", "Content-Type")
        self.send_header("Content-Length", str(len(payload)))
        self.end_headers()
        self.wfile.write(payload)

    def do_OPTIONS(self) -> None:
        self.send_response(200)
        self.send_header("Access-Control-Allow-Origin", "*")
        self.send_header("Access-Control-Allow-Methods", "GET, POST, OPTIONS")
        self.send_header("Access-Control-Allow-Headers", "Content-Type")
        self.end_headers()

    def do_GET(self) -> None:
        if self.path == "/api/kernel/status":
            kernel = get_kernel()
            self._send_json(kernel.generate_kernel_status())
            return

        if self.path == "/api/odysseus/tools":
            self._send_json({"tools": get_odysseus_tools_manifest()})
            return

        if self.path == "/api/sunet/topology":
            kernel = get_kernel()
            self._send_json(kernel.inspect_sunet())
            return

        super().do_GET()

    def do_POST(self) -> None:
        content_length = int(self.headers.get("Content-Length", 0))
        body_bytes = self.rfile.read(content_length)
        payload = json.loads(body_bytes.decode("utf-8")) if body_bytes else {}

        if self.path == "/api/odysseus/execute":
            tool_name = payload.get("tool")
            args = payload.get("arguments", {})
            res = OdysseusIntentExecutor.execute_tool(tool_name, args)
            self._send_json(res)
            return

        if self.path == "/api/odysseus/intent":
            prompt = payload.get("prompt", "")
            res = OdysseusIntentExecutor.parse_and_execute_intent(prompt)
            self._send_json(res)
            return

        if self.path == "/api/ai/chat":
            import os
            prompt = payload.get("prompt", "")
            provider = payload.get("provider", "heuristic")
            api_key = payload.get("api_key", "").strip()
            local_endpoint = payload.get("endpoint", "http://localhost:11434/api/generate")

            tool_res = OdysseusIntentExecutor.parse_and_execute_intent(prompt)

            if provider == "gemini":
                key = api_key or os.getenv("GEMINI_API_KEY", "")
                if not key:
                    self._send_json({
                        "provider": "gemini",
                        "status": "HYP",
                        "warning": "GEMINI_API_KEY not provided. Set GEMINI_API_KEY environment variable or enter key in web UI.",
                        "odysseus_tool_result": tool_res
                    })
                    return
                try:
                    url = f"https://generativelanguage.googleapis.com/v1beta/models/gemini-1.5-flash:generateContent?key={key}"
                    req_body = json.dumps({"contents": [{"parts": [{"text": f"You are Odysseus AI controlling Universal Physics Index. User query: {prompt}"}]}]}).encode("utf-8")
                    req = urllib.request.Request(url, data=req_body, headers={"Content-Type": "application/json"})
                    with urllib.request.urlopen(req, timeout=10) as resp:
                        res_data = json.loads(resp.read().decode("utf-8"))
                        text = res_data["candidates"][0]["content"]["parts"][0]["text"]
                        self._send_json({
                            "provider": "gemini",
                            "model": "gemini-1.5-flash",
                            "ai_response": text,
                            "odysseus_tool_result": tool_res
                        })
                        return
                except Exception as exc:
                    self._send_json({
                        "provider": "gemini_fallback",
                        "status": "HYP",
                        "error": f"Gemini API error: {exc}",
                        "odysseus_tool_result": tool_res
                    })
                    return

            if provider == "grok":
                key = api_key or os.getenv("GROK_API_KEY") or os.getenv("XAI_API_KEY", "")
                if not key:
                    self._send_json({
                        "provider": "grok",
                        "status": "HYP",
                        "warning": "GROK_API_KEY not provided. Set GROK_API_KEY environment variable or enter key in web UI.",
                        "odysseus_tool_result": tool_res
                    })
                    return
                try:
                    url = "https://api.x.ai/v1/chat/completions"
                    req_body = json.dumps({
                        "model": "grok-beta",
                        "messages": [
                            {"role": "system", "content": "You are Odysseus AI controlling Universal Physics Index."},
                            {"role": "user", "content": prompt}
                        ]
                    }).encode("utf-8")
                    req = urllib.request.Request(url, data=req_body, headers={
                        "Content-Type": "application/json",
                        "Authorization": f"Bearer {key}"
                    })
                    with urllib.request.urlopen(req, timeout=10) as resp:
                        res_data = json.loads(resp.read().decode("utf-8"))
                        text = res_data["choices"][0]["message"]["content"]
                        self._send_json({
                            "provider": "grok",
                            "model": "grok-beta",
                            "ai_response": text,
                            "odysseus_tool_result": tool_res
                        })
                        return
                except Exception as exc:
                    self._send_json({
                        "provider": "grok_fallback",
                        "status": "HYP",
                        "error": f"xAI Grok API error: {exc}",
                        "odysseus_tool_result": tool_res
                    })
                    return

            if provider == "copilot":
                key = api_key or os.getenv("COPILOT_API_KEY") or os.getenv("OPENAI_API_KEY", "")
                if not key:
                    self._send_json({
                        "provider": "copilot",
                        "status": "HYP",
                        "warning": "COPILOT_API_KEY / OPENAI_API_KEY not provided. Set environment variable or enter key in web UI.",
                        "odysseus_tool_result": tool_res
                    })
                    return
                try:
                    url = "https://api.openai.com/v1/chat/completions"
                    req_body = json.dumps({
                        "model": payload.get("model", "gpt-4o"),
                        "messages": [
                            {"role": "system", "content": "You are Odysseus AI controlling Universal Physics Index."},
                            {"role": "user", "content": prompt}
                        ]
                    }).encode("utf-8")
                    req = urllib.request.Request(url, data=req_body, headers={
                        "Content-Type": "application/json",
                        "Authorization": f"Bearer {key}"
                    })
                    with urllib.request.urlopen(req, timeout=10) as resp:
                        res_data = json.loads(resp.read().decode("utf-8"))
                        text = res_data["choices"][0]["message"]["content"]
                        self._send_json({
                            "provider": "copilot",
                            "model": payload.get("model", "gpt-4o"),
                            "ai_response": text,
                            "odysseus_tool_result": tool_res
                        })
                        return
                except Exception as exc:
                    self._send_json({
                        "provider": "copilot_fallback",
                        "status": "HYP",
                        "error": f"Copilot / OpenAI API error: {exc}",
                        "odysseus_tool_result": tool_res
                    })
                    return

            if provider == "local_ollama":
                try:
                    req_data = json.dumps({
                        "model": payload.get("model", "llama3"),
                        "prompt": f"You are Odysseus AI controlling Universal Physics Index. Respond to user: {prompt}",
                        "stream": False
                    }).encode("utf-8")

                    req = urllib.request.Request(local_endpoint, data=req_data, headers={"Content-Type": "application/json"})
                    with urllib.request.urlopen(req, timeout=5) as resp:
                        res_json = json.loads(resp.read().decode("utf-8"))
                        reply_text = res_json.get("response", "")
                        self._send_json({
                            "provider": "local_ollama",
                            "model": payload.get("model", "llama3"),
                            "ai_response": reply_text,
                            "odysseus_tool_result": tool_res
                        })
                        return
                except Exception as exc:
                    self._send_json({
                        "provider": "local_ollama_fallback",
                        "status": "HYP",
                        "warning": f"Could not reach Local AI at {local_endpoint}: {exc}",
                        "odysseus_tool_result": tool_res
                    })
                    return

            # Default Heuristic Router
            self._send_json({
                "provider": "heuristic_router",
                "status": "DER",
                "odysseus_tool_result": tool_res
            })
            return

        self._send_json({"error": "Endpoint not found"}, status_code=404)


def run_server(port: int = 4000, open_browser: bool = True) -> None:
    """Start inside-out UPI server."""
    server_address = ("", port)
    httpd = HTTPServer(server_address, UPIInsideOutHandler)
    url = f"http://localhost:{port}"

    print(f"🌌 Universal Physics Index (UPI) Inside-Out Server running at {url}")
    print(f"📁 Serving Web UI from: {PUBLIC_DIR}")
    print("🤖 Odysseus AI Protocol Bridge API active at /api/odysseus/")
    print("⚡ AI Proxy Gateway active at /api/ai/chat")

    if open_browser:
        import webbrowser
        webbrowser.open(url)

    try:
        httpd.serve_forever()
    except KeyboardInterrupt:
        print("\nStopping UPI Inside-Out Server.")
        httpd.server_close()


def main() -> None:
    parser = argparse.ArgumentParser(description="UPI Inside-Out Server & Web UI Launcher")
    parser.add_argument("--port", type=int, default=4000, help="Port to listen on (default 4000)")
    parser.add_argument("--no-browser", action="store_true", help="Do not automatically open web browser")
    args = parser.parse_args()

    run_server(port=args.port, open_browser=not args.no_browser)


if __name__ == "__main__":
    main()
