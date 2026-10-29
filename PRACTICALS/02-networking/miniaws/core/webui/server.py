"""WebUI HTTP server — Phase 1+2+3+4+5. Port 7001. Old console (:7000) untouched."""
import http.server
import socketserver
import sys
from pathlib import Path
from urllib.parse import urlsplit, parse_qs, unquote as urllib_parse_unquote

PROJ = Path(__file__).resolve().parent.parent.parent
sys.path.insert(0, str(PROJ))

from core.webui import aws_ref, layout, home, search, session
from core.webui.pages import s3 as s3_pages
from core.webui.pages import s3_actions, s3_wizard
from core.webui.pages import ec2 as ec2_pages
from core.webui.pages import ec2_actions
from core.webui.pages import vpc as vpc_pages
from core.webui.pages import vpc_actions
from core.webui.pages import cloudwatch as cw_pages
from core.webui.pages import cloudwatch_actions
from core.webui.pages import iam as iam_pages
from core.webui.pages import iam_actions
from core.webui.pages import sts as sts_pages
from core.webui.pages import dynamodb as ddb_pages
from core.webui.pages import dynamodb_actions


PORT_PREFERRED = 7001


def _page(path, content, active_service, breadcrumb, region_code, title=None):
    return layout.page(
        title or active_service.capitalize() or "Console",
        content,
        active_service=active_service,
        breadcrumb=breadcrumb,
        region=session.region_tuple(region_code),
        path=path,
    )


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
                return self._send_html(_page(
                    "/", home.render(region_code), "",
                    [("AWS Console", "/"), ("Console Home", None)], region_code,
                    "Console Home"))

            if path == "/search":
                q = (qs.get("q") or [""])[0]
                return self._send_html(self._render_search(q, region_code))

            # ---- S3 ----
            if path == "/s3":
                session.record_visit("s3")
                return self._send_html(_page("/s3",
                    s3_pages.render_buckets(region_code, qs=qs), "s3",
                    [("AWS Console", "/"), ("S3", "/s3"), ("Buckets", None)],
                    region_code, "Buckets"))

            if path == "/s3/create":
                session.record_visit("s3")
                return self._send_html(_page("/s3/create",
                    s3_wizard.render_create_bucket(region_code), "s3",
                    [("AWS Console", "/"), ("S3", "/s3"), ("Buckets", "/s3"),
                     ("Create bucket", None)], region_code, "Create bucket"))

            if path.startswith("/s3/") and path.endswith("/upload"):
                bname = path[4:].split("/", 1)[0]
                session.record_visit("s3")
                return self._send_html(_page(path,
                    s3_wizard.render_upload(bname), "s3",
                    [("AWS Console", "/"), ("S3", "/s3"), ("Buckets", "/s3"),
                     (bname, None), ("Upload", None)], region_code,
                    f"Upload to {bname}"))

            if path.startswith("/s3/"):
                bname = path[4:].split("/", 1)[0]
                tab = (qs.get("tab") or ["objects"])[0]
                session.record_visit("s3")
                return self._send_html(_page(path,
                    s3_pages.render_bucket(bname, tab=tab, region_code=region_code, qs=qs),
                    "s3",
                    [("AWS Console", "/"), ("S3", "/s3"), ("Buckets", "/s3"),
                     (bname, None)], region_code, bname))

            # ---- EC2 ----
            if path == "/ec2" or path == "/ec2/instances":
                session.record_visit("ec2")
                return self._send_html(_page("/ec2/instances",
                    ec2_pages.render_list(qs=qs), "ec2",
                    [("AWS Console", "/"), ("EC2", "/ec2"), ("Instances", None)],
                    region_code, "Instances"))

            if path == "/ec2/launch":
                session.record_visit("ec2")
                return self._send_html(_page("/ec2/launch",
                    ec2_pages.render_launch(qs=qs), "ec2",
                    [("AWS Console", "/"), ("EC2", "/ec2"), ("Instances", "/ec2/instances"),
                     ("Launch an instance", None)], region_code, "Launch an instance"))

            if path.startswith("/ec2/instances/"):
                iid = path[len("/ec2/instances/"):]
                session.record_visit("ec2")
                return self._send_html(_page(path,
                    ec2_pages.render_detail(iid, qs=qs), "ec2",
                    [("AWS Console", "/"), ("EC2", "/ec2"), ("Instances", "/ec2/instances"),
                     (iid, None)], region_code, iid))

            # ---- VPC (order matters: specific paths before generic) ----
            if path == "/vpc" or path == "/vpc/":
                session.record_visit("vpc")
                return self._send_html(_page("/vpc",
                    vpc_pages.render_vpcs(qs=qs), "vpc",
                    [("AWS Console", "/"), ("VPC", "/vpc"), ("Your VPCs", None)],
                    region_code, "Your VPCs"))

            if path == "/vpc/create":
                session.record_visit("vpc")
                return self._send_html(_page("/vpc/create",
                    vpc_pages.render_create_vpc(qs=qs), "vpc",
                    [("AWS Console", "/"), ("VPC", "/vpc"), ("Your VPCs", "/vpc"),
                     ("Create VPC", None)], region_code, "Create VPC"))

            if path == "/vpc/subnets":
                session.record_visit("vpc")
                return self._send_html(_page("/vpc/subnets",
                    vpc_pages.render_subnets(qs=qs), "vpc",
                    [("AWS Console", "/"), ("VPC", "/vpc"), ("Subnets", None)],
                    region_code, "Subnets"))

            if path == "/vpc/subnets/create":
                vid = (qs.get("vpc_id") or [None])[0]
                return self._send_html(_page("/vpc/subnets/create",
                    vpc_pages.render_create_subnet(vpc_id=vid, qs=qs), "vpc",
                    [("AWS Console", "/"), ("VPC", "/vpc"), ("Subnets", "/vpc/subnets"),
                     ("Create subnet", None)], region_code, "Create subnet"))

            if path.startswith("/vpc/subnets/"):
                sid = path[len("/vpc/subnets/"):]
                return self._send_html(_page(path,
                    vpc_pages.render_subnet_detail(sid, qs=qs), "vpc",
                    [("AWS Console", "/"), ("VPC", "/vpc"), ("Subnets", "/vpc/subnets"),
                     (sid, None)], region_code, sid))

            if path == "/vpc/route-tables":
                return self._send_html(_page("/vpc/route-tables",
                    vpc_pages.render_route_tables(qs=qs), "vpc",
                    [("AWS Console", "/"), ("VPC", "/vpc"), ("Route tables", None)],
                    region_code, "Route tables"))

            if path.startswith("/vpc/route-tables/"):
                rid = path[len("/vpc/route-tables/"):]
                return self._send_html(_page(path,
                    vpc_pages.render_route_table_detail(rid, qs=qs), "vpc",
                    [("AWS Console", "/"), ("VPC", "/vpc"),
                     ("Route tables", "/vpc/route-tables"), (rid, None)],
                    region_code, rid))

            if path == "/vpc/igws":
                return self._send_html(_page("/vpc/igws",
                    vpc_pages.render_igws(qs=qs), "vpc",
                    [("AWS Console", "/"), ("VPC", "/vpc"), ("Internet gateways", None)],
                    region_code, "Internet gateways"))

            if path == "/vpc/igws/create":
                return self._send_html(_page("/vpc/igws/create",
                    vpc_pages.render_create_igw(qs=qs), "vpc",
                    [("AWS Console", "/"), ("VPC", "/vpc"),
                     ("Internet gateways", "/vpc/igws"),
                     ("Create internet gateway", None)], region_code,
                    "Create internet gateway"))

            if path == "/vpc/nats":
                return self._send_html(_page("/vpc/nats",
                    vpc_pages.render_nats(qs=qs), "vpc",
                    [("AWS Console", "/"), ("VPC", "/vpc"), ("NAT gateways", None)],
                    region_code, "NAT gateways"))

            if path == "/vpc/nats/create":
                vid = (qs.get("vpc_id") or [None])[0]
                return self._send_html(_page("/vpc/nats/create",
                    vpc_pages.render_create_nat(vpc_id=vid, qs=qs), "vpc",
                    [("AWS Console", "/"), ("VPC", "/vpc"), ("NAT gateways", "/vpc/nats"),
                     ("Create NAT gateway", None)], region_code, "Create NAT gateway"))

            if path == "/vpc/security-groups":
                return self._send_html(_page("/vpc/security-groups",
                    vpc_pages.render_sgs(qs=qs), "vpc",
                    [("AWS Console", "/"), ("VPC", "/vpc"), ("Security groups", None)],
                    region_code, "Security groups"))

            if path == "/vpc/security-groups/create":
                vid = (qs.get("vpc_id") or [None])[0]
                return self._send_html(_page("/vpc/security-groups/create",
                    vpc_pages.render_create_sg(vpc_id=vid, qs=qs), "vpc",
                    [("AWS Console", "/"), ("VPC", "/vpc"),
                     ("Security groups", "/vpc/security-groups"),
                     ("Create security group", None)], region_code,
                    "Create security group"))

            if path.startswith("/vpc/security-groups/"):
                sid = path[len("/vpc/security-groups/"):]
                return self._send_html(_page(path,
                    vpc_pages.render_sg_detail(sid, qs=qs), "vpc",
                    [("AWS Console", "/"), ("VPC", "/vpc"),
                     ("Security groups", "/vpc/security-groups"), (sid, None)],
                    region_code, sid))

            # VPC detail — must be last among /vpc/* routes
            if path.startswith("/vpc/"):
                vid = path[5:].split("/", 1)[0]
                tab = (qs.get("tab") or ["details"])[0]
                session.record_visit("vpc")
                return self._send_html(_page(path,
                    vpc_pages.render_vpc_detail(vid, tab=tab, qs=qs), "vpc",
                    [("AWS Console", "/"), ("VPC", "/vpc"), ("Your VPCs", "/vpc"),
                     (vid, None)], region_code, vid))

            # ---- CloudWatch ----
            if path == "/cloudwatch":
                session.record_visit("cloudwatch")
                return self._send_html(_page("/cloudwatch",
                    cw_pages.render_overview(qs=qs), "cloudwatch",
                    [("AWS Console", "/"), ("CloudWatch", "/cloudwatch"), ("Overview", None)],
                    region_code, "CloudWatch"))

            if path == "/cloudwatch/alarms":
                session.record_visit("cloudwatch")
                return self._send_html(_page("/cloudwatch/alarms",
                    cw_pages.render_alarms(qs=qs), "cloudwatch",
                    [("AWS Console", "/"), ("CloudWatch", "/cloudwatch"), ("Alarms", None)],
                    region_code, "Alarms"))

            if path == "/cloudwatch/alarms/create":
                session.record_visit("cloudwatch")
                return self._send_html(_page("/cloudwatch/alarms/create",
                    cw_pages.render_create_alarm(qs=qs), "cloudwatch",
                    [("AWS Console", "/"), ("CloudWatch", "/cloudwatch"),
                     ("Alarms", "/cloudwatch/alarms"), ("Create alarm", None)],
                    region_code, "Create alarm"))

            if path.startswith("/cloudwatch/alarms/"):
                name = path[len("/cloudwatch/alarms/"):]
                session.record_visit("cloudwatch")
                return self._send_html(_page(path,
                    cw_pages.render_alarm_detail(name, qs=qs), "cloudwatch",
                    [("AWS Console", "/"), ("CloudWatch", "/cloudwatch"),
                     ("Alarms", "/cloudwatch/alarms"), (name, None)],
                    region_code, name))

            if path == "/cloudwatch/metrics":
                session.record_visit("cloudwatch")
                return self._send_html(_page("/cloudwatch/metrics",
                    cw_pages.render_metrics(qs=qs), "cloudwatch",
                    [("AWS Console", "/"), ("CloudWatch", "/cloudwatch"), ("Metrics", None)],
                    region_code, "Metrics"))

            if path.startswith("/cloudwatch/metrics/"):
                rest = path[len("/cloudwatch/metrics/"):]
                parts = rest.split("/", 1)
                if len(parts) == 2:
                    ns, metric = parts
                    return self._send_html(_page(path,
                        cw_pages.render_metric_detail(ns, metric, qs=qs), "cloudwatch",
                        [("AWS Console", "/"), ("CloudWatch", "/cloudwatch"),
                         ("Metrics", "/cloudwatch/metrics"), (f"{ns}/{metric}", None)],
                        region_code, metric))

            if path == "/cloudwatch/log-groups":
                session.record_visit("cloudwatch")
                return self._send_html(_page("/cloudwatch/log-groups",
                    cw_pages.render_log_groups(qs=qs), "cloudwatch",
                    [("AWS Console", "/"), ("CloudWatch", "/cloudwatch"), ("Log groups", None)],
                    region_code, "Log groups"))

            if path == "/cloudwatch/log-groups/create":
                session.record_visit("cloudwatch")
                return self._send_html(_page("/cloudwatch/log-groups/create",
                    cw_pages.render_create_log_group(qs=qs), "cloudwatch",
                    [("AWS Console", "/"), ("CloudWatch", "/cloudwatch"),
                     ("Log groups", "/cloudwatch/log-groups"), ("Create log group", None)],
                    region_code, "Create log group"))

            if path.startswith("/cloudwatch/log-groups/"):
                name = urllib_parse_unquote(path[len("/cloudwatch/log-groups/"):])
                session.record_visit("cloudwatch")
                return self._send_html(_page(path,
                    cw_pages.render_log_group_detail(name, qs=qs), "cloudwatch",
                    [("AWS Console", "/"), ("CloudWatch", "/cloudwatch"),
                     ("Log groups", "/cloudwatch/log-groups"), (name, None)],
                    region_code, name))

            # ---- IAM ----
            if path == "/iam" or path == "/iam/dashboard":
                session.record_visit("iam")
                return self._send_html(_page("/iam",
                    iam_pages.render_dashboard(qs=qs), "iam",
                    [("AWS Console", "/"), ("IAM", "/iam"), ("Dashboard", None)],
                    region_code, "IAM Dashboard"))

            if path == "/iam/users":
                session.record_visit("iam")
                return self._send_html(_page("/iam/users",
                    iam_pages.render_users(qs=qs), "iam",
                    [("AWS Console", "/"), ("IAM", "/iam"), ("Users", None)],
                    region_code, "Users"))

            if path == "/iam/users/create":
                session.record_visit("iam")
                return self._send_html(_page("/iam/users/create",
                    iam_pages.render_create_user(qs=qs), "iam",
                    [("AWS Console", "/"), ("IAM", "/iam"), ("Users", "/iam/users"),
                     ("Create user", None)], region_code, "Create user"))

            if path.startswith("/iam/users/"):
                name = path[len("/iam/users/"):]
                tab = (qs.get("tab") or ["permissions"])[0]
                session.record_visit("iam")
                return self._send_html(_page(path,
                    iam_pages.render_user_detail(name, tab=tab, qs=qs), "iam",
                    [("AWS Console", "/"), ("IAM", "/iam"), ("Users", "/iam/users"),
                     (name, None)], region_code, name))

            if path == "/iam/groups":
                session.record_visit("iam")
                return self._send_html(_page("/iam/groups",
                    iam_pages.render_groups(qs=qs), "iam",
                    [("AWS Console", "/"), ("IAM", "/iam"), ("Groups", None)],
                    region_code, "Groups"))

            if path == "/iam/groups/create":
                session.record_visit("iam")
                return self._send_html(_page("/iam/groups/create",
                    iam_pages.render_create_group(qs=qs), "iam",
                    [("AWS Console", "/"), ("IAM", "/iam"), ("Groups", "/iam/groups"),
                     ("Create group", None)], region_code, "Create group"))

            if path.startswith("/iam/groups/"):
                name = path[len("/iam/groups/"):]
                session.record_visit("iam")
                return self._send_html(_page(path,
                    iam_pages.render_group_detail(name, qs=qs), "iam",
                    [("AWS Console", "/"), ("IAM", "/iam"), ("Groups", "/iam/groups"),
                     (name, None)], region_code, name))

            if path == "/iam/policies":
                session.record_visit("iam")
                return self._send_html(_page("/iam/policies",
                    iam_pages.render_policies(qs=qs), "iam",
                    [("AWS Console", "/"), ("IAM", "/iam"), ("Policies", None)],
                    region_code, "Policies"))

            if path == "/iam/policies/create":
                session.record_visit("iam")
                return self._send_html(_page("/iam/policies/create",
                    iam_pages.render_create_policy(qs=qs), "iam",
                    [("AWS Console", "/"), ("IAM", "/iam"), ("Policies", "/iam/policies"),
                     ("Create policy", None)], region_code, "Create policy"))

            if path.startswith("/iam/policies/"):
                name = path[len("/iam/policies/"):]
                session.record_visit("iam")
                return self._send_html(_page(path,
                    iam_pages.render_policy_detail(name, qs=qs), "iam",
                    [("AWS Console", "/"), ("IAM", "/iam"), ("Policies", "/iam/policies"),
                     (name, None)], region_code, name))

            if path == "/iam/access-keys":
                session.record_visit("iam")
                return self._send_html(_page("/iam/access-keys",
                    iam_pages.render_access_keys(qs=qs), "iam",
                    [("AWS Console", "/"), ("IAM", "/iam"), ("Access keys", None)],
                    region_code, "Access keys"))

            if path == "/iam/audit":
                session.record_visit("iam")
                return self._send_html(_page("/iam/audit",
                    iam_pages.render_audit(qs=qs), "iam",
                    [("AWS Console", "/"), ("IAM", "/iam"), ("Audit log", None)],
                    region_code, "Audit log"))

            # ---- STS ----
            if path == "/sts" or path == "/sts/get-caller-identity":
                return self._send_html(_page("/sts",
                    sts_pages.render_get_caller_identity(qs=qs), "sts",
                    [("AWS Console", "/"), ("STS", "/sts"), ("Get caller identity", None)],
                    region_code, "Get caller identity"))

            # ---- DynamoDB ----
            if path == "/dynamodb":
                session.record_visit("dynamodb")
                return self._send_html(_page("/dynamodb",
                    ddb_pages.render_dashboard(qs=qs), "dynamodb",
                    [("AWS Console", "/"), ("DynamoDB", "/dynamodb"), ("Dashboard", None)],
                    region_code, "DynamoDB Dashboard"))

            if path == "/dynamodb/tables":
                session.record_visit("dynamodb")
                return self._send_html(_page("/dynamodb/tables",
                    ddb_pages.render_tables(qs=qs), "dynamodb",
                    [("AWS Console", "/"), ("DynamoDB", "/dynamodb"), ("Tables", None)],
                    region_code, "Tables"))

            if path == "/dynamodb/tables/create":
                session.record_visit("dynamodb")
                return self._send_html(_page("/dynamodb/tables/create",
                    ddb_pages.render_create_table(qs=qs), "dynamodb",
                    [("AWS Console", "/"), ("DynamoDB", "/dynamodb"),
                     ("Tables", "/dynamodb/tables"), ("Create table", None)],
                    region_code, "Create table"))

            # items CREATE route must come before items list / table detail
            if path.endswith("/items/create") and path.startswith("/dynamodb/tables/"):
                tname = path[len("/dynamodb/tables/"):-len("/items/create")]
                session.record_visit("dynamodb")
                return self._send_html(_page(path,
                    ddb_pages.render_create_item(tname, qs=qs), "dynamodb",
                    [("AWS Console", "/"), ("DynamoDB", "/dynamodb"),
                     ("Tables", "/dynamodb/tables"), (tname, None),
                     ("Create item", None)], region_code, "Create item"))

            if path.endswith("/items") and path.startswith("/dynamodb/tables/"):
                tname = path[len("/dynamodb/tables/"):-len("/items")]
                session.record_visit("dynamodb")
                return self._send_html(_page(path,
                    ddb_pages.render_table_detail(tname, tab="items", qs=qs), "dynamodb",
                    [("AWS Console", "/"), ("DynamoDB", "/dynamodb"),
                     ("Tables", "/dynamodb/tables"), (tname, None), ("Explore items", None)],
                    region_code, tname))

            if path.startswith("/dynamodb/tables/"):
                tname = path[len("/dynamodb/tables/"):]
                tab = (qs.get("tab") or ["overview"])[0]
                session.record_visit("dynamodb")
                return self._send_html(_page(path,
                    ddb_pages.render_table_detail(tname, tab=tab, qs=qs), "dynamodb",
                    [("AWS Console", "/"), ("DynamoDB", "/dynamodb"),
                     ("Tables", "/dynamodb/tables"), (tname, None)],
                    region_code, tname))

            # ---- Other services: placeholder ----
            for sid, name, _desc, href in aws_ref.SERVICES:
                if path == href or path.startswith(href + "/"):
                    session.record_visit(sid)
                    return self._send_html(_page(path,
                        f'<section class="aws-section"><h1>{name}</h1>'
                        f'<div class="aws-notice aws-notice-info">'
                        f'{name} workspace arrives in a later phase.</div></section>',
                        sid, [("AWS Console", "/"), (name, href), ("Overview", None)],
                        region_code, name))

            return self._send_html(_page(path,
                "<h1>404 &mdash; page not found</h1>", "",
                [("AWS Console", "/"), ("404", None)], region_code, "Not Found"),
                status=404)
        except Exception:
            import traceback
            return self._send_html(
                f"<h1>Error</h1><pre>{traceback.format_exc()}</pre>", status=500)

    def _render_search(self, q, region_code):
        matches, _exact = search.find(q)
        if matches:
            tiles = "".join(
                f'<a class="service-tile" href="{session.with_region(href, region_code)}">'
                f'<div class="service-tile-icon">{sid[:2].upper()}</div>'
                f'<div class="service-tile-body"><div class="service-tile-name">{name}</div>'
                f'<div class="service-tile-desc">{desc}</div></div></a>'
                for sid, name, desc, href in matches
            )
            body = (f'<section class="aws-section"><h1>Search results for '
                    f'&ldquo;{q}&rdquo;</h1><p class="aws-muted">{len(matches)} match(es)</p>'
                    f'<div class="service-grid">{tiles}</div></section>')
        else:
            body = (f'<section class="aws-section"><h1>No results for '
                    f'&ldquo;{q}&rdquo;</h1><p class="aws-muted">Try S3, EC2, VPC, '
                    f'DynamoDB, Lambda, IAM, CloudWatch, STS.</p></section>')
        return layout.page(f"Search: {q}", body,
            breadcrumb=[("AWS Console", "/"), ("Search", None), (q or "(empty)", None)],
            region=session.region_tuple(region_code), path="/search")

    def do_POST(self):
        split = urlsplit(self.path)
        path = split.path.rstrip("/") or "/"
        try:
            length = int(self.headers.get("Content-Length", 0))
            ctype = (self.headers.get("Content-Type") or "").lower()

            form = {}
            files = {}
            if ctype.startswith("multipart/form-data"):
                raw = self.rfile.read(length)
                boundary = ctype.split("boundary=", 1)[1].strip().strip('"')
                form, files = _parse_multipart(raw, boundary)
            else:
                raw = self.rfile.read(length).decode("utf-8", "replace")
                parsed = parse_qs(raw, keep_blank_values=True)
                form = {k: v[0] for k, v in parsed.items()}

            result = None
            if path.startswith("/s3"):
                result = s3_actions.handle(path, form, files)
            elif path.startswith("/ec2"):
                result = ec2_actions.handle(path, form, files)
            elif path.startswith("/vpc"):
                result = vpc_actions.handle(path, form, files)
            elif path.startswith("/cloudwatch"):
                result = cloudwatch_actions.handle(path, form, files)
            elif path.startswith("/iam"):
                result = iam_actions.handle(path, form, files)
            elif path.startswith("/dynamodb"):
                result = dynamodb_actions.handle(path, form, files)

            if result is None:
                return self._send_html(
                    f"<h1>404 — no action for POST {path}</h1>", status=404)
            kind, payload = result
            if kind == "redirect":
                self.send_response(303)
                self.send_header("Location", payload)
                self.end_headers()
                return
            return self._send_html(payload)
        except Exception:
            import traceback
            return self._send_html(
                f"<h1>Error</h1><pre>{traceback.format_exc()}</pre>", status=500)

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


def _parse_multipart(raw, boundary):
    result_form = {}
    result_files = {}
    sep = b"--" + boundary.encode()
    parts = raw.split(sep)
    for part in parts:
        part = part.strip(b"\r\n")
        if not part or part == b"--":
            continue
        head_end = part.find(b"\r\n\r\n")
        if head_end == -1:
            continue
        headers_blob = part[:head_end].decode("utf-8", "replace")
        body = part[head_end + 4:]
        if body.endswith(b"\r\n"):
            body = body[:-2]
        name = None
        filename = None
        ctype = "application/octet-stream"
        for line in headers_blob.split("\r\n"):
            low = line.lower()
            if low.startswith("content-disposition:"):
                for piece in line.split(";")[1:]:
                    piece = piece.strip()
                    if piece.startswith("name="):
                        name = piece.split("=", 1)[1].strip('"')
                    elif piece.startswith("filename="):
                        filename = piece.split("=", 1)[1].strip('"')
            elif low.startswith("content-type:"):
                ctype = line.split(":", 1)[1].strip()
        if name is None:
            continue
        if filename is not None:
            result_files[name] = (filename, ctype, body)
        else:
            result_form[name] = body.decode("utf-8", "replace")
    return result_form, result_files


def serve():
    import os as _os
    import time as _time
    for candidate in [PORT_PREFERRED, 7002, 7003]:
        try:
            httpd = socketserver.TCPServer(("", candidate), Handler)
        except OSError:
            continue
        print(f"🅰️  MiniAWS WebUI at http://localhost:{candidate}")
        print(f"   server.py mtime: {_time.ctime(_os.path.getmtime(__file__))}")
        print(f"   pid: {_os.getpid()}")
        print(f"   old console (:7000) untouched")
        try:
            httpd.serve_forever()
        except KeyboardInterrupt:
            print("\n🛑 WebUI stopped.")
            httpd.server_close()
        return
    print("❌ No free port (tried 7001-7003)")


if __name__ == "__main__":
    serve()
