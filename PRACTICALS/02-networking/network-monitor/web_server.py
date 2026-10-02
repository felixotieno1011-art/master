#!/usr/bin/env python3
"""Serve the HTML report live. Rebuilds on each request."""
import http.server
import socketserver
import subprocess
import sys
import os
from config import WEB_PORT, REPORT


class Handler(http.server.SimpleHTTPRequestHandler):
    def do_GET(self):
        # Rebuild HTML on every page load
        if self.path in ("/", "/report.html", "/index.html"):
            subprocess.run(
                [sys.executable, "report.py", "--html"],
                capture_output=True
            )
            self.path = "/" + REPORT

        return super().do_GET()

    def log_message(self, *args):
        pass   # quiet


def main():
    os.makedirs("reports", exist_ok=True)

    # Initial build
    subprocess.run([sys.executable, "report.py", "--html"],
                   capture_output=True)

    with socketserver.TCPServer(("", WEB_PORT), Handler) as httpd:
        print(f"🌐 Serving at http://localhost:{WEB_PORT}")
        print(f"   On LAN:    http://<your-ip>:{WEB_PORT}")
        print(f"   Press Ctrl+C to stop.")
        try:
            httpd.serve_forever()
        except KeyboardInterrupt:
            print("\n🛑 Server stopped.")


if __name__ == "__main__":
    main()
