"""Serve the MiniAWS Console over HTTP with clickable pages + forms."""
import http.server
import socketserver
import sys
import urllib.parse

from core import console


PORT_PREFERRED = 7000


class Handler(http.server.BaseHTTPRequestHandler):

    def do_GET(self):
        try:
            full_path = self.path
            path = full_path.split("?")[0].rstrip("/")
            query = full_path.split("?", 1)[1] if "?" in full_path else ""
            qs = urllib.parse.parse_qs(query)

            if path == "":
                flash_msg = None
                flash_type = None
                if "ok" in qs:
                    flash_msg = qs["ok"][0]
                    flash_type = "ok"
                elif "error" in qs:
                    flash_msg = qs["error"][0]
                    flash_type = "error"
                html = console.generate_html(flash_msg=flash_msg, flash_type=flash_type)
            elif path.startswith("/vpc/"):
                html = console.render_vpc_detail(path[5:])
            elif path.startswith("/subnet/"):
                html = console.render_subnet_detail(path[8:])
            elif path.startswith("/ec2/"):
                html = console.render_ec2_detail(path[5:])
            elif path.startswith("/s3/"):
                html = console.render_s3_detail(path[4:])
            elif path.startswith("/iam/"):
                html = console.render_iam_detail(path[5:])
            elif path.startswith("/alarm/"):
                html = console.render_alarm_detail(path[7:])
            elif path.startswith("/metric/"):
                parts = path[8:].split("/", 1)
                if len(parts) == 2:
                    html = console.render_metric_detail(parts[0], parts[1])
                else:
                    html = console.render_not_found(path)
            elif path.startswith("/loggroup/"):
                html = console.render_loggroup_detail(path[10:])
            elif path.startswith("/routetable/"):
                html = console.render_routetable_detail(path[12:])
            elif path.startswith("/nat/"):
                html = console.render_nat_detail(path[5:])
            elif path.startswith("/securitygroup/"):
                html = console.render_sg_detail(path[15:])
            else:
                html = console.render_not_found(path)
        except Exception:
            import traceback
            html = f"<h1>Error</h1><pre>{traceback.format_exc()}</pre>"

        self._send_html(html)

    def do_POST(self):
        """Handle form submissions via console_actions."""
        from core import console_actions
        try:
            length = int(self.headers.get("Content-Length", 0))
            body = self.rfile.read(length).decode("utf-8")
            data = urllib.parse.parse_qs(body)
            # parse_qs returns lists: {"cidr": ["10.0.0.0/16"]}
            form = {k: v[0] for k, v in data.items()}

            path = self.path.split("?")[0].rstrip("/")
            result = console_actions.handle(path, form)

            if result is None:
                self._redirect("/?error=Unknown+action")
                return

            if result[0] == "redirect":
                self._redirect(result[1])
            else:
                self._send_html(result[1])
        except Exception:
            import traceback
            html = f"<h1>Error</h1><pre>{traceback.format_exc()}</pre>"
            self._send_html(html, status=500)

    # ---------- Actions ----------

    def _redirect(self, location):
        self.send_response(303)
        self.send_header("Location", location)
        self.end_headers()

    def _send_html(self, html, status=200):
        self.send_response(status)
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
            print(f"   Interactive: create VPCs from the browser!")
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
