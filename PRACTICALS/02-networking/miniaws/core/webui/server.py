"""WebUI HTTP server — Phase 1. Port 7001. Old console (:7000) untouched."""
import http.server
import socketserver
import sys
from pathlib import Path
from urllib.parse import urlsplit, parse_qs

PROJ = Path(__file__).resolve().parent.parent.parent
sys.path.insert(0, str(PROJ))

from core.webui import aws_ref, layout, home, search, session
from core.webui.pages import s3 as s3_pages


PORT_PREFERRED = 7001


def _home_html(region_code):
    return layout.page(
        "Console Home",
        home.render(region_code),
        active_service="",
        breadcrumb=[("AWS Console", "/"), ("Console Home", None)],
        region=session.region_tuple(region_code),
        path="/",
    )


def _search_html(q, region_code):
    matches, _exact = search.find(q)
    if matches:
        tiles = "".join(
            f'<a class="service-tile" href="{session.with_region(href, region_code)}">'
            f'<div class="service-tile-icon">{sid[:2].upper()}</div>'
            f'<div class="service-tile-body"><div class="service-tile-name">{name}</div>'
            f'<div class="service-tile-desc">{desc}</div></div></a>'
            for sid, name, desc, href in matches
        )
        body = f"""
<section class="aws-section">
  <h1>Search results for &ldquo;{q}&rdquo;</h1>
  <p class="aws-muted">{len(matches)} match(es)</p>
  <div class="service-grid">{tiles}</div>
</section>"""
    else:
        body = f"""
<section class="aws-section">
  <h1>No results for &ldquo;{q}&rdquo;</h1>
  <p class="aws-muted">Try S3, EC2, Lambda, IAM, CloudWatch, DynamoDB, VPC, or STS.</p>
</section>"""
    return layout.page(
        f"Search: {q}",
        body,
        breadcrumb=[("AWS Console", "/"), ("Search", None), (q or "(empty)", None)],
        region=session.region_tuple(region_code),
        path="/search",
    )


def _placeholder_service(sid, name, region_code):
    return f"""
<section class="aws-section">
  <h1>{name}</h1>
  <div class="aws-notice aws-notice-info">
    Phase 1 shell is live. The {name} workspace (tables, create-wizards,
    detail pages) arrives in Phase 2&ndash;3.
  </div>
  <p class="aws-muted">
    Left-rail items mirror the real console layout. Region:
    <code>{region_code}</code> &mdash; change it with the dropdown above.
  </p>
</section>
"""


class Handler(http.server.BaseHTTPRequestHandler):

    def do_GET(self):
        split = urlsplit(self.path)
        path = split.path.rstrip("/") or "/"
        qs = parse_qs(split.query)

        try:
            region_code = session.region_from_query(qs)
            if "region" in qs and qs["region"][0] == region_code:
                if region_code != session.current_region():
                    session.set_region(region_code)

            if path == "/static/aws.css":
                return self._serve_static("aws.css", "text/css")

            if path == "/":
                return self._send_html(_home_html(region_code))

            if path == "/search":
                q = (qs.get("q") or [""])[0]
                return self._send_html(_search_html(q, region_code))

            if path == "/s3":
                session.record_visit("s3")
                return self._send_html(
                    layout.page(
                        "Buckets",
                        s3_pages.render_buckets(region_code),
                        active_service="s3",
                        breadcrumb=[("AWS Console", "/"), ("S3", "/s3"), ("Buckets", None)],
                        region=session.region_tuple(region_code),
                        path="/s3",
                    )
                )

            if path.startswith("/s3/"):
                bucket_name = path[4:].split("/", 1)[0]
                tab = (qs.get("tab") or ["objects"])[0]
                session.record_visit("s3")
                return self._send_html(
                    layout.page(
                        bucket_name,
                        s3_pages.render_bucket(bucket_name, tab=tab, region_code=region_code),
                        active_service="s3",
                        breadcrumb=[("AWS Console", "/"), ("S3", "/s3"),
                                    ("Buckets", "/s3"), (bucket_name, None)],
                        region=session.region_tuple(region_code),
                        path=path,
                    )
                )

            for sid, name, _desc, href in aws_ref.SERVICES:
                if path == href or path.startswith(href + "/"):
                    session.record_visit(sid)
                    return self._send_html(
                        layout.page(
                            name,
                            _placeholder_service(sid, name, region_code),
                            active_service=sid,
                            breadcrumb=[("AWS Console", "/"), (name, href), ("Overview", None)],
                            region=session.region_tuple(region_code),
                            path=path,
                        )
                    )

            return self._send_html(
                layout.page(
                    "Not Found",
                    "<h1>404 &mdash; page not found</h1>",
                    breadcrumb=[("AWS Console", "/"), ("404", None)],
                    region=session.region_tuple(region_code),
                    path=path,
                ),
                status=404,
            )
        except Exception:
            import traceback
            return self._send_html(
                f"<h1>Error</h1><pre>{traceback.format_exc()}</pre>", status=500
            )

    def _serve_static(self, filename, content_type):
        p = Path(__file__).parent / "static" / filename
        body = p.read_bytes()
        self.send_response(200)
        self.send_header("Content-Type", f"{content_type}; charset=utf-8")
        self.send_header("Content-Length", str(len(body)))
        self.end_headers()
        self.wfile.write(body)

    def _send_html(self, html, status=200):
        body = html.encode("utf-8")
        self.send_response(status)
        self.send_header("Content-Type", "text/html; charset=utf-8")
        self.send_header("Content-Length", str(len(body)))
        self.end_headers()
        self.wfile.write(body)

    def log_message(self, fmt, *args):
        sys.stderr.write(f"  [webui] {self.address_string()} {self.requestline}\n")


def serve():
    for candidate in [PORT_PREFERRED, 7002, 7003]:
        try:
            httpd = socketserver.TCPServer(("", candidate), Handler)
        except OSError:
            continue
        print(f"🅰️  MiniAWS WebUI at http://localhost:{candidate}")
        print(f"   Old console (:7000) untouched.")
        try:
            httpd.serve_forever()
        except KeyboardInterrupt:
            print("\n🛑 WebUI stopped.")
            httpd.server_close()
        return
    print("❌ No free port (tried 7001, 7002, 7003)")


if __name__ == "__main__":
    serve()
