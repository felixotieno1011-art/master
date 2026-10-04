"""HTTP server that serves S3 objects.

URL format: http://localhost:8000/<bucket>/<key>
Also accepts: /<bucket>?list  -> returns JSON of objects
"""
import http.server
import json
import socketserver
import sys

from core import s3


PORT_PREFERRED = 8000


class S3Handler(http.server.BaseHTTPRequestHandler):
    def do_GET(self):
        # Strip leading slash
        path = self.path.lstrip("/")
        if not path:
            self._send_json({"error": "URL format: /<bucket>/<key>"}, 400)
            return

        # /bucket?list  -> list objects
        if "?" in path:
            path, query = path.split("?", 1)
            if query == "list":
                objs = s3.list_objects(path)
                if objs is None:
                    self._send_json({"error": f"bucket '{path}' not found"}, 404)
                    return
                self._send_json({"bucket": path, "objects": objs}, 200)
                return

        if "/" not in path:
            # Just a bucket name
            meta = s3.get_bucket(path)
            if not meta:
                self._send_json({"error": f"bucket '{path}' not found"}, 404)
                return
            self._send_json(meta, 200)
            return

        bucket, key = path.split("/", 1)
        obj_path = s3.get_object_path(bucket, key)
        if not obj_path:
            self.send_error(404, f"object not found: {bucket}/{key}")
            return

        try:
            with open(obj_path, "rb") as f:
                data = f.read()
        except Exception as e:
            self.send_error(500, f"read error: {e}")
            return

        self.send_response(200)
        self.send_header("Content-Type", s3._guess_content_type(key))
        self.send_header("Content-Length", str(len(data)))
        self.end_headers()
        self.wfile.write(data)

    def _send_json(self, obj, status=200):
        data = json.dumps(obj, indent=2).encode()
        self.send_response(status)
        self.send_header("Content-Type", "application/json")
        self.send_header("Content-Length", str(len(data)))
        self.end_headers()
        self.wfile.write(data)

    def log_message(self, *args):
        sys.stderr.write(f"  [s3] {self.address_string()} {self.requestline}\n")


def serve():
    for candidate in [PORT_PREFERRED, 8001, 8002]:
        try:
            httpd = socketserver.TCPServer(("", candidate), S3Handler)
            print(f"🪣 S3 server running at http://localhost:{candidate}")
            print(f"   URL format: http://localhost:{candidate}/<bucket>/<key>")
            print(f"   List:       http://localhost:{candidate}/<bucket>?list")
            print(f"   Press Ctrl+C to stop.")
            try:
                httpd.serve_forever()
            except KeyboardInterrupt:
                print("\n🛑 S3 server stopped.")
                httpd.server_close()
                return
        except OSError:
            continue
    print("❌ No free port (tried 8000-8002)")


if __name__ == "__main__":
    serve()
