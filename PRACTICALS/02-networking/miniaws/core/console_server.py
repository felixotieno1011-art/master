"""Serve the MiniAWS Console over HTTP."""
import http.server
import socketserver
import sys

from core import console


PORT_PREFERRED = 7000


class Handler(http.server.BaseHTTPRequestHandler):
    def do_GET(self):
        try:
            html = console.generate_html()
        except Exception as e:
            self.send_error(500, f"console failed: {e}")
            return
        self.send_response(200)
        self.send_header("Content-Type", "text/html; charset=utf-8")
        self.send_header("Content-Length", str(len(html.encode())))
        self.end_headers()
        self.wfile.write(html.encode())

    def log_message(self, *args):
        sys.stderr.write(f"  [console] {self.address_string()} {self.requestline}\n")


def serve():
    for candidate in [PORT_PREFERRED, 7001, 7002]:
        try:
            httpd = socketserver.TCPServer(("", candidate), Handler)
            print(f"🅰️  MiniAWS Console at http://localhost:{candidate}")
            print(f"   Press Ctrl+C to stop.")
            try:
                httpd.serve_forever()
            except KeyboardInterrupt:
                print("\n🛑 Console stopped.")
                httpd.server_close()
                return
        except OSError:
            continue
    print("❌ No free port (tried 7000-7002)")


if __name__ == "__main__":
    serve()
