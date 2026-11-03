"""High-performance Localhost Web Server and REST API for SOUNDARYA."""

from __future__ import annotations
import os
import sys
import json
import logging
from pathlib import Path
from urllib.parse import urlparse, parse_qs
from http.server import HTTPServer, BaseHTTPRequestHandler
from dataclasses import asdict

from app.core.config import config
from app.core.engine import core_engine
from app.system.monitor import system_monitor
from app.system.app_launcher import app_launcher
from app.memory.memory_manager import memory_manager

logger = logging.getLogger("Soundarya.WebServer")

WEB_DIR = Path(__file__).resolve().parent / "web"


class SoundaryaHTTPHandler(BaseHTTPRequestHandler):
    def log_message(self, format: str, *args: any) -> None:
        """Silent logging for clean terminal output."""
        return

    def _send_json(self, data: any, status_code: int = 200) -> None:
        payload = json.dumps(data, default=str).encode("utf-8")
        self.send_response(status_code)
        self.send_header("Content-Type", "application/json")
        self.send_header("Content-Length", str(len(payload)))
        self.send_header("Access-Control-Allow-Origin", "*")
        self.send_header("Access-Control-Allow-Headers", "Content-Type")
        self.send_header("Access-Control-Allow-Methods", "GET, POST, OPTIONS")
        self.end_headers()
        self.wfile.write(payload)

    def do_OPTIONS(self) -> None:
        self.send_response(200)
        self.send_header("Access-Control-Allow-Origin", "*")
        self.send_header("Access-Control-Allow-Headers", "Content-Type")
        self.send_header("Access-Control-Allow-Methods", "GET, POST, OPTIONS")
        self.end_headers()

    def do_GET(self) -> None:
        parsed_url = urlparse(self.path)
        path = parsed_url.path
        query = parse_qs(parsed_url.query)

        # 1. Root Single Page Application
        if path == "/" or path == "/index.html":
            index_path = WEB_DIR / "index.html"
            if index_path.exists():
                content = index_path.read_bytes()
                self.send_response(200)
                self.send_header("Content-Type", "text/html; charset=utf-8")
                self.send_header("Content-Length", str(len(content)))
                self.end_headers()
                self.wfile.write(content)
            else:
                self.send_error(404, "index.html not found")
            return

        # 2. Telemetry API
        if path == "/api/telemetry":
            metrics = system_monitor.get_metrics()
            self._send_json(asdict(metrics))
            return

        # 3. Apps API
        if path == "/api/apps":
            rescan = query.get("rescan", ["false"])[0].lower() == "true"
            if rescan:
                app_launcher.scan_installed_applications()
            apps = app_launcher.repo.list_apps()
            self._send_json(apps)
            return

        # 4. Memories API
        if path == "/api/memories":
            search_query = query.get("q", [""])[0]
            if search_query:
                memories = memory_manager.mem_repo.search_memories(search_query)
            else:
                memories = memory_manager.mem_repo.list_memories(limit=100)
            self._send_json(memories)
            return

        self.send_error(404, "Not Found")

    def do_POST(self) -> None:
        parsed_url = urlparse(self.path)
        path = parsed_url.path
        content_length = int(self.headers.get("Content-Length", 0))
        body = self.rfile.read(content_length)

        try:
            payload = json.loads(body.decode("utf-8")) if body else {}
        except Exception:
            payload = {}

        # 1. Process Natural Language Command
        if path == "/api/command":
            cmd = payload.get("command", "").strip()
            if not cmd:
                self._send_json({"success": False, "reply": "No command provided."}, 400)
                return

            reply = core_engine.process_command(cmd, speak_output=False)
            self._send_json({
                "success": True,
                "command": cmd,
                "reply": reply,
                "state": core_engine.state.value
            })
            return

        # 2. Launch Specific Application
        if path == "/api/launch":
            app_name = payload.get("app_name", "").strip()
            success, msg = app_launcher.launch_app(app_name)
            self._send_json({"success": success, "message": msg})
            return

        # 3. Add Memory
        if path == "/api/memories":
            title = payload.get("title", "")
            content = payload.get("content", "")
            category = payload.get("category", "note")
            mem_id = memory_manager.remember_fact(content=content, category=category, title=title or None)
            self._send_json({"success": True, "memory_id": mem_id})
            return

        self.send_error(404, "Not Found")


def run_server(port: int = 8080) -> None:
    server_address = ("127.0.0.1", port)
    httpd = HTTPServer(server_address, SoundaryaHTTPHandler)
    print(f"◈ SOUNDARYA Localhost Server is ONLINE:")
    print(f"◈ URL: http://localhost:{port}")
    print(f"◈ Press Ctrl+C to stop.")
    try:
        httpd.serve_forever()
    except KeyboardInterrupt:
        print("\n◈ Server stopped.")
        httpd.server_close()


if __name__ == "__main__":
    port = int(sys.argv[1]) if len(sys.argv) > 1 else 8080
    run_server(port)
