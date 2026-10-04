"""Serve the MiniAzure portal over HTTP."""
import http.server
import os
import socketserver
import sys

from core import portal


PORT_PREFERRED = 9090
OUT_FILE = "reports/portal.html"


class Handler(http.server.BaseHTTPRequestHandler):
    def do_GET(self):
        try:
            html = portal.generate_html()
        except Exception as e:
            self.send_error(500, f"portal failed: {e}")
            return
        self.send_response(200)
        self.send_header("Content-Type", "text/html; charset=utf-8")
        self.send_header("Content-Length", str(len(html.encode())))
        self.end_headers()
        self.wfile.write(html.encode())

    def log_message(self, *args):
        sys.stderr.write(f"  [portal] {self.address_string()} {self.requestline}\n")


def serve():
    for candidate in [PORT_PREFERRED, 9091, 9092]:
        try:
            httpd = socketserver.TCPServer(("", candidate), Handler)
            print(f"☁️  MiniAzure Portal at http://localhost:{candidate}")
            print(f"   Press Ctrl+C to stop.")
            try:
                httpd.serve_forever()
            except KeyboardInterrupt:
                print("\n🛑 Portal stopped.")
                httpd.server_close()
                return
        except OSError:
            continue
    print("❌ No free port found (tried 9090-9092)")


if __name__ == "__main__":
    serve()
