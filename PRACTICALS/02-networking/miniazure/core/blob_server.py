"""HTTP server that serves uploaded blobs.

Runs on port 8080 (falls back to 8081-8083 if busy).
URL format:  http://host:port/<account>/<container>/<blob>
"""
import http.server
import os
import socketserver
import sys

from core import storage


PORT_PREFERRED = 8080


class BlobHandler(http.server.BaseHTTPRequestHandler):
    def do_GET(self):
        # Parse: /account/container/blob
        parts = [p for p in self.path.split("/") if p]
        if len(parts) != 3:
            self.send_error(400, "URL must be /<account>/<container>/<blob>")
            return

        account, container, blob = parts
        path = storage.get_blob_path(account, container, blob)
        if not path:
            self.send_error(404, f"blob not found: {account}/{container}/{blob}")
            return

        try:
            with open(path, "rb") as f:
                data = f.read()
        except Exception as e:
            self.send_error(500, f"failed to read blob: {e}")
            return

        content_type = storage._guess_content_type(blob)
        self.send_response(200)
        self.send_header("Content-Type", content_type)
        self.send_header("Content-Length", str(len(data)))
        self.end_headers()
        self.wfile.write(data)

    def log_message(self, *args):
        sys.stderr.write(f"  [blob] {self.address_string()} {self.requestline}\n")


def serve(port=None):
    port = port or PORT_PREFERRED
    for candidate in [port, 8081, 8082, 8083]:
        try:
            httpd = socketserver.TCPServer(("", candidate), BlobHandler)
            print(f"🌐 Blob server running at http://localhost:{candidate}")
            print(f"   URL format: http://localhost:{candidate}/<account>/<container>/<blob>")
            print(f"   Press Ctrl+C to stop.")
            try:
                httpd.serve_forever()
            except KeyboardInterrupt:
                print("\n🛑 Blob server stopped.")
                httpd.server_close()
                return
        except OSError:
            continue
    print("❌ No free port found (tried 8080-8083)")


if __name__ == "__main__":
    serve()
