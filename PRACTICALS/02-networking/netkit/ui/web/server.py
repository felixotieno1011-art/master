# ============================================
# NETKIT — ui/web/server.py
# Pure stdlib web server. No Flask, no pip.
# ============================================

import json
import os
import urllib.parse
from http.server import HTTPServer, BaseHTTPRequestHandler

from core import config, logger
from ui.web import routes


TEMPLATE_DIR = os.path.join(os.path.dirname(__file__), "templates")
STATIC_DIR = os.path.join(os.path.dirname(__file__), "static")


class Handler(BaseHTTPRequestHandler):

    # --- helpers ---
    def _send(self, code, body, ctype="text/html; charset=utf-8"):
        if isinstance(body, str):
            body = body.encode("utf-8")
        self.send_response(code)
        self.send_header("Content-Type", ctype)
        self.send_header("Content-Length", str(len(body)))
        self.end_headers()
        self.wfile.write(body)

    def _json(self, obj, code=200):
        self._send(code, json.dumps(obj), "application/json")

    def _read_template(self, name):
        path = os.path.join(TEMPLATE_DIR, name)
        if not os.path.exists(path):
            return f"<h1>Missing template: {name}</h1>"
        with open(path) as f:
            return f.read()

    def _read_static(self, name):
        # Prevent path traversal
        name = os.path.basename(name)
        path = os.path.join(STATIC_DIR, name)
        if not os.path.exists(path):
            return None
        with open(path, "rb") as f:
            return f.read()

    def log_message(self, fmt, *args):
        # Quieter logs
        print(f"  [web] {self.address_string()} — {fmt % args}")

    # --- routes ---
    def do_GET(self):
        parsed = urllib.parse.urlparse(self.path)
        path = parsed.path

        if path == "/" or path == "/index.html":
            self._send(200, self._read_template("index.html"))

        elif path == "/report":
            text = logger.get_report().read()
            html = self._read_template("report.html").replace(
                "{{REPORT}}", _escape(text)
            )
            self._send(200, html)

        elif path.startswith("/static/"):
            name = path[len("/static/"):]
            data = self._read_static(name)
            if data is None:
                self._send(404, "not found")
            else:
                ctype = "text/css" if name.endswith(".css") else \
                        "application/javascript" if name.endswith(".js") else \
                        "application/octet-stream"
                self._send(200, data, ctype)

        elif path == "/api/report":
            self._json({
                "text": logger.get_report().read(),
                "path": logger.get_report().path(),
            })

        elif path == "/api/tools":
            self._json(routes.list_tools())

        else:
            self._send(404, "<h1>404</h1>")

    def do_POST(self):
        parsed = urllib.parse.urlparse(self.path)
        path = parsed.path

        length = int(self.headers.get("Content-Length", 0))
        raw = self.rfile.read(length).decode("utf-8") if length else "{}"
        try:
            payload = json.loads(raw)
        except Exception:
            payload = {}

        if path.startswith("/api/run/"):
            tool_name = path[len("/api/run/"):]
            result = routes.run_tool(tool_name, payload)
            self._json(result)
        else:
            self._json({"ok": False, "error": "unknown endpoint"}, 404)


def _escape(text):
    return (text
            .replace("&", "&amp;")
            .replace("<", "&lt;")
            .replace(">", "&gt;"))


def start():
    host = config.WEB_HOST
    port = config.WEB_PORT
    server = HTTPServer((host, port), Handler)
    print()
    print(f"  🌐 NETKIT web UI running at:")
    print(f"     http://{host}:{port}")
    print(f"     (Ctrl+C to stop)")
    print()
    try:
        server.serve_forever()
    except KeyboardInterrupt:
        print("\n  🛑 Web server stopped.")
