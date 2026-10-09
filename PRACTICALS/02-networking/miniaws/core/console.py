"""MiniAWS Console — mobile-optimized browser dashboard."""
import html
import os
from datetime import datetime

from core import account, ec2, s3, vpc, iam, cloudwatch, nat, sg, lambda_svc, dynamodb, nat, sg


def _esc(s):
    return html.escape(str(s))


# ---------- Shared CSS (mobile-first) ----------

BASE_CSS = """
* { box-sizing: border-box; }
body {
  background: #0f141c;
  color: #eaeded;
  font-family: -apple-system, BlinkMacSystemFont, "Segoe UI", Roboto, sans-serif;
  margin: 0; padding: 0; font-size: 14px;
  -webkit-font-smoothing: antialiased;
}
header {
  background: #161b22; border-bottom: 1px solid #2b303a;
  padding: 12px 16px; display: flex; justify-content: space-between;
  align-items: center; position: sticky; top: 0; z-index: 100;
}
.aws-badge {
  background: #ff9900; color: #0f141c; font-weight: 900;
  padding: 2px 6px; border-radius: 4px; font-size: 11px;
  letter-spacing: 0.5px; margin-right: 8px;
}
.header-meta { font-size: 10px; color: #a1a8b3; font-family: monospace; margin-top: 2px; }
main { padding: 16px; max-width: 100%; box-sizing: border-box; }
h2 {
  font-size: 11px; text-transform: uppercase; letter-spacing: 1px;
  color: #a1a8b3; margin: 20px 0 10px 0;
}
.metrics-grid { display: grid; grid-template-columns: repeat(2, 1fr); gap: 10px; }
.metric-card {
  background: #161b22; border: 1px solid #2b303a; padding: 12px;
  border-radius: 8px; display: flex; flex-direction: column;
  justify-content: space-between; min-height: 70px;
}
.metric-label { font-size: 11px; font-weight: 500; color: #a1a8b3; text-transform: uppercase; }
.metric-value-row { display: flex; align-items: baseline; justify-content: space-between; margin-top: 4px; }
.metric-num { font-size: 22px; font-weight: 600; color: #f1f2f4; }
.metric-num.dim { color: #6c7685; }
.badge-sub {
  font-size: 10px; font-weight: bold; color: #037f0c;
  background: #122918; padding: 2px 6px; border-radius: 4px;
  border: 1px solid #194021;
}
.resource-card {
  background: #161b22; border: 1px solid #2b303a; border-radius: 8px;
  margin-bottom: 12px; overflow: hidden;
  box-shadow: 0 4px 6px rgba(0,0,0,0.2);
}
.card-header {
  background: #1c232d; padding: 10px 12px; border-bottom: 1px solid #2b303a;
  display: flex; justify-content: space-between; align-items: center;
}
.resource-title { font-weight: bold; color: #f1f2f4; word-break: break-all; }
.resource-title a { color: #529cca; text-decoration: none; }
.resource-type { font-size: 11px; font-family: monospace; color: #8791a1; margin-left: 6px; }
.status-pill {
  font-size: 11px; font-weight: bold; padding: 2px 8px;
  border-radius: 12px; display: inline-flex; align-items: center;
  white-space: nowrap;
}
.status-pill::before {
  content: ""; width: 6px; height: 6px; border-radius: 50%;
  margin-right: 6px;
}
.status-running { color: #037f0c; background: #122918; border: 1px solid #194021; }
.status-running::before { background: #037f0c; }
.status-stopped { color: #b7791f; background: #2c2412; border: 1px solid #4e3d14; }
.status-stopped::before { background: #b7791f; }
.status-terminated { color: #d13212; background: #2c1512; border: 1px solid #4e1c14; }
.status-terminated::before { background: #d13212; }
.status-ok { color: #037f0c; background: #122918; border: 1px solid #194021; }
.status-ok::before { background: #037f0c; }
.status-alarm { color: #d13212; background: #2c1512; border: 1px solid #4e1c14; }
.status-alarm::before { background: #d13212; }
.status-info { color: #529cca; background: #192534; border: 1px solid #233852; }
.status-info::before { background: #529cca; }
.card-body {
  padding: 12px; display: grid;
  grid-template-columns: repeat(2, 1fr); gap: 12px 8px;
}
.data-label { font-size: 11px; color: #8791a1; margin: 0 0 2px 0; }
.data-value { font-size: 13px; margin: 0; font-weight: 500; color: #f1f2f4; word-break: break-all; }
.font-code { font-family: monospace; color: #529cca; word-break: break-all; }
.dim { color: #6c7685; }
.terminated-fade { opacity: 0.6; }
.empty-msg { padding: 16px; color: #8791a1; font-style: italic; font-size: 13px; }
.detail-row {
  display: flex; justify-content: space-between; padding: 8px 0;
  border-bottom: 1px solid #2b303a; font-size: 13px;
}
.detail-row:last-child { border-bottom: none; }
.detail-label { color: #8791a1; }
.detail-value { color: #f1f2f4; font-weight: 500; word-break: break-all; text-align: right; }
a { color: #529cca; text-decoration: none; }
a:hover { text-decoration: underline; }
.back {
  display: inline-block; color: #529cca; text-decoration: none;
  margin-bottom: 16px; font-weight: 600; font-size: 13px;
}
pre {
  background: #0a0f1a; padding: 12px; border-radius: 8px;
  overflow-x: auto; font-size: 11px; color: #cbd5e1;
}

/* ---------- Forms ---------- */
.form-card {
  background: #161b22; border: 1px solid #2b303a; border-radius: 8px;
  padding: 16px; margin: 12px 0;
}
.form-card h3 {
  margin: 0 0 12px 0; font-size: 14px; color: #ff9900;
  text-transform: uppercase; letter-spacing: 0.5px;
}
.form-row { display: flex; gap: 8px; align-items: center; flex-wrap: wrap; }
.form-row label { font-size: 13px; color: #a1a8b3; min-width: 80px; }
.form-row input[type=text] {
  flex: 1; min-width: 180px; padding: 8px 10px;
  background: #0a0f1a; border: 1px solid #2b303a; border-radius: 6px;
  color: #eaeded; font-size: 13px; font-family: monospace;
}
.form-row input[type=text]:focus { outline: none; border-color: #529cca; }
.form-row button {
  background: #ff9900; color: #0f141c; border: none;
  padding: 8px 16px; border-radius: 6px; font-weight: bold;
  font-size: 13px; cursor: pointer;
}
.form-row button:hover { background: #ffad33; }
.form-row button:active { background: #e08800; }
/* ---------- Alerts ---------- */
.alert {
  padding: 12px 16px; border-radius: 8px; margin: 12px 0;
  font-size: 13px;
}
.alert.ok { background: #122918; color: #4ade80; border-left: 4px solid #4ade80; }
.alert.error { background: #2c1512; color: #f87171; border-left: 4px solid #f87171; }

/* ---------- Create section (details/summary) ---------- */
details.create-section {
  background: #161b22; border: 1px solid #2b303a; border-radius: 8px;
  padding: 10px 14px; margin: 12px 0;
}
details.create-section summary {
  cursor: pointer; color: #ff9900; font-weight: bold;
  font-size: 13px; user-select: none;
}
details.create-section[open] summary { margin-bottom: 8px; }

/* ---------- Delete buttons ---------- */
.btn-delete {
  background: #2c1512; color: #f87171; border: 1px solid #4e1c14;
  padding: 4px 8px; border-radius: 6px; font-size: 12px;
  cursor: pointer; margin-left: 8px;
}
.btn-delete:hover { background: #4e1c14; }
.btn-delete-large {
  background: #2c1512; color: #f87171; border: 1px solid #4e1c14;
  padding: 8px 14px; border-radius: 6px; font-size: 13px;
  font-weight: bold; cursor: pointer; margin: 12px 0;
}
.btn-delete-large:hover { background: #4e1c14; }

/* --- Contract-layer UI additions (Browser Batch 1) --- */
.err-block { display: flex; align-items: center; gap: 8px;
  background: #2c1512; border: 1px solid #4e1c14; border-radius: 8px;
  padding: 10px 12px; margin: 8px 0; }
.err-chip { background: #4e1c14; color: #fbbf24; font-family: monospace;
  font-size: 11px; padding: 2px 8px; border-radius: 6px; font-weight: bold;
  letter-spacing: 0.3px; }
.err-text { color: #f8b4b4; font-size: 12px; font-family: monospace;
  word-break: break-all; }
.cli-chip { background: #1a2530; color: #a1a8b3; border: 1px solid #2b303a;
  padding: 6px 10px; border-radius: 6px; font-family: monospace; font-size: 11px;
  cursor: pointer; text-align: left; max-width: 100%; overflow: hidden;
  text-overflow: ellipsis; white-space: nowrap; display: inline-block;
  margin: 8px 0; }
.cli-chip:hover { background: #223040; color: #eaeded; }
.cli-chip.copied { background: #122918; color: #52d869; border-color: #194021; }
.cli-chip-label { color: #ff9900; font-weight: bold; margin-right: 4px; }
.json-panel { margin: 12px 0; background: #161b22; border: 1px solid #2b303a;
  border-radius: 8px; overflow: hidden; }
.json-panel summary { padding: 10px 14px; cursor: pointer; color: #a1a8b3;
  font-size: 12px; user-select: none; }
.json-panel summary:hover { background: #1a2129; color: #eaeded; }
.json-panel[open] summary { border-bottom: 1px solid #2b303a; }
.json-pre { margin: 0; padding: 12px 14px; background: #0d1117;
  color: #a5d6ff; font-family: monospace; font-size: 11px; overflow-x: auto;
  line-height: 1.5; }
"""

# JavaScript injected into every page. Plain string (NOT an f-string)
# so JS braces { } are safe here.
BASE_JS = """
(function() {
  function loadJson(el) {
    var src = el.dataset.src;
    if (!src || el.dataset.loaded === '1') return;
    el.dataset.loaded = '1';
    fetch(src).then(function(r){ return r.text(); })
              .then(function(t){ el.textContent = t; })
              .catch(function(e){ el.textContent = 'error: ' + e; });
  }
  document.addEventListener('DOMContentLoaded', function() {
    document.querySelectorAll('.json-panel').forEach(function(panel) {
      panel.addEventListener('toggle', function() {
        if (panel.open) {
          var pre = panel.querySelector('.json-pre');
          if (pre) loadJson(pre);
        }
      });
    });
    document.addEventListener('click', function(ev) {
      var el = ev.target.closest('.cli-chip');
      if (!el) return;
      var cmd = el.dataset.cmd;
      if (!cmd) return;
      navigator.clipboard.writeText(cmd).then(function() {
        el.classList.add('copied');
        setTimeout(function() { el.classList.remove('copied'); }, 1000);
      });
    });
  });
})();
"""


def _page(title, body_html, subtitle=""):
    """Full page wrapper."""
    return f"""<!DOCTYPE html>
<html lang="en">
<head>
  <meta charset="UTF-8">
  <meta name="viewport" content="width=device-width, initial-scale=1.0">
  <title>{_esc(title)}</title>
  <style>{BASE_CSS}</style>
</head>
<body>
  <header>
    <div style="display:flex;align-items:center;">
      <span class="aws-badge">AWS</span>
      <div>
        <div style="font-weight:bold;font-size:14px;color:#f1f2f4;">MiniAWS Console</div>
        <div class="header-meta">{_esc(subtitle)}</div>
      </div>
    </div>
  </header>
  <main>
    {body_html}
  </main>
  <script>{BASE_JS}</script>
</body>
</html>"""


import re as _re
import json as _json


_ERROR_CODE_RE = _re.compile(r"\(([A-Z][A-Za-z0-9._]+)\)")


def _split_aws_error(msg):
    if not isinstance(msg, str):
        msg = str(msg)
    m = _ERROR_CODE_RE.search(msg)
    if not m:
        return None, msg
    return m.group(1), msg


def _render_error(msg):
    code, text = _split_aws_error(msg)
    if code:
        return (
            f'<div class="err-block">'
            f'<span class="err-chip">{_esc(code)}</span>'
            f'<span class="err-text">{_esc(text)}</span>'
            f'</div>'
        )
    return f'<div class="err-block"><span class="err-text">{_esc(text)}</span></div>'


def _cli_chip(cmd):
    safe = _esc(cmd).replace("'", "&#39;")
    return (
        f'<button class="cli-chip" '
        f'data-cmd="{safe}" title="Click to copy">'
        f'<span class="cli-chip-label">aws</span> '
        f'<span class="cli-chip-cmd">{_esc(cmd)}</span>'
        f'</button>'
    )


def _json_panel(kind, ident):
    return (
        f'<details class="json-panel">'
        f'<summary>Raw JSON (aws ... --output json)</summary>'
        f'<pre class="json-pre" '
        f'data-src="/api/json/{_esc(kind)}/{_esc(ident)}">'
        f'loading…</pre>'
        f'</details>'
    )


def _status_class(state):
    s = (state or "").lower()
    if s in ("running", "available", "ok"):
        return "status-running"
    if s in ("stopped", "stopping", "insufficient_data"):
        return "status-stopped"
    if s in ("terminated", "alarm", "failed"):
        return "status-terminated"
    return "status-info"


# ---------- Gather real state ----------

def _gather():
    """Read all state from MiniAWS services."""
    acct = account.summary()

    inst_list = ec2.list_all()
    bucket_list = s3.ls_buckets()
    vpc_list = vpc.list_vpcs()
    subnet_list = vpc.list_subnets()
    igw_list = vpc.list_internet_gateways()
    user_list = iam.list_users()
    alarm_list = cloudwatch.list_alarms()
    metric_list = cloudwatch.list_metrics()
    loggroups = cloudwatch.describe_log_groups()
    route_table_list = vpc.list_route_tables()
    nat_list = nat.list_nat_gateways()
    sg_list = sg.list_security_groups()
    lambda_list = lambda_svc.list_functions()
    dynamodb_list = dynamodb.list_tables()

    instances = []
    for i in inst_list:
        st = ec2.status(i["instance_id"]) or {}
        instances.append({
            "id": i["instance_id"],
            "name": (i.get("tags") or {}).get("Name", "-"),
            "type": i.get("instance_type", "-"),
            "state": st.get("state") or i.get("state", "-"),
            "region": i.get("region", "-"),
            "pid": st.get("pid"),
            "uptime": f"{st.get('uptime_sec', 0)}s",
        })

    buckets = []
    for b in bucket_list:
        objs = s3.list_objects(b["name"]) or []
        buckets.append({
            "name": b["name"],
            "region": b.get("region", "-"),
            "objects": len(objs),
            "created": b.get("created", "-"),
        })

    vpcs = []
    for v in vpc_list:
        subs = [s for s in subnet_list if s["vpcId"] == v["vpcId"]]
        igws = [g for g in igw_list if v["vpcId"] in g.get("attachments", [])]
        vpcs.append({
            "id": v["vpcId"],
            "cidr": v["cidrBlock"],
            "region": v.get("region", "-"),
            "subnets": subs,
            "igw_count": len(igws),
        })

    return {
        "account": acct,
        "instances": instances,
        "buckets": buckets,
        "vpcs": vpcs,
        "users": user_list,
        "alarms": alarm_list,
        "metrics": metric_list,
        "loggroups": loggroups,
        "route_tables": route_table_list,
        "nats": nat_list,
        "security_groups": sg_list,
        "lambdas": lambda_list,
        "dynamodb_tables": dynamodb_list,
        "generated": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
    }


# ---------- Main dashboard ----------

def generate_html(flash_msg=None, flash_type=None):
    d = _gather()
    acct = d["account"]

    running = sum(1 for i in d["instances"] if i["state"] == "running")
    firing = sum(1 for a in d["alarms"] if a["stateValue"] == "ALARM")

    # EC2 cards
    ec2_html = ""
    for i in d["instances"]:
        is_run = i["state"] == "running"
        fade = "" if is_run else " terminated-fade"
        status_cls = _status_class(i["state"])
        ec2_html += f"""
        <div class="resource-card{fade}">
          <div class="card-header">
            <div>
              <span class="resource-title">{_esc(i['name'])}</span>
              <span class="resource-type">{_esc(i['type'])}</span>
            </div>
            <span class="status-pill {status_cls}">{_esc(i['state'])}</span>
          </div>
          <div class="card-body">
            <div>
              <p class="data-label">Instance ID</p>
              <p class="data-value font-code"><a href="/ec2/{i['id']}">{_esc(i['id'])}</a></p>
            </div>
            <div>
              <p class="data-label">Region</p>
              <p class="data-value">{_esc(i['region'])}</p>
            </div>
            <div>
              <p class="data-label">Uptime</p>
              <p class="data-value">{_esc(i['uptime'])}</p>
            </div>
            <div>
              <p class="data-label">PID</p>
              <p class="data-value">{_esc(i['pid'] or '-')}</p>
            </div>
          </div>
        </div>"""
    if not ec2_html:
        ec2_html = '<div class="resource-card"><div class="empty-msg">No EC2 instances</div></div>'

    # S3 cards
    s3_html = ""
    for b in d["buckets"]:
        s3_html += f"""
        <div class="resource-card">
          <div class="card-header">
            <div><span class="resource-title"><a href="/s3/{b['name']}">{_esc(b['name'])}</a></span></div>
            <span class="status-pill status-ok">{b['objects']} obj</span>
          </div>
          <div class="card-body">
            <div><p class="data-label">Region</p><p class="data-value">{_esc(b['region'])}</p></div>
            <div><p class="data-label">Created</p><p class="data-value dim">{_esc(b['created'])}</p></div>
          </div>
        </div>"""
    if not s3_html:
        s3_html = '<div class="resource-card"><div class="empty-msg">No S3 buckets</div></div>'

    # VPC cards
    vpc_html = ""
    for v in d["vpcs"]:
        subs_str = ", ".join(s["subnetId"][:16] + "…" for s in v["subnets"]) or "no subnets"
        vpc_html += f"""
        <div class="resource-card">
          <div class="card-header">
            <div><span class="resource-title"><a href="/vpc/{v['id']}">{_esc(v['id'])}</a></span></div>
            <span class="status-pill status-ok">{len(v['subnets'])} subnets</span>
          </div>
          <div class="card-body">
            <div><p class="data-label">CIDR</p><p class="data-value">{_esc(v['cidr'])}</p></div>
            <div><p class="data-label">Region</p><p class="data-value">{_esc(v['region'])}</p></div>
            <div><p class="data-label">IGW</p><p class="data-value">{'attached' if v['igw_count'] else 'none'}</p></div>
            <div><p class="data-label">Subnets</p><p class="data-value dim">{_esc(subs_str)}</p></div>
          </div>
        </div>"""
    if not vpc_html:
        vpc_html = '<div class="resource-card"><div class="empty-msg">No VPCs</div></div>'

    # IAM cards
    iam_html = ""
    for u in d["users"]:
        iam_html += f"""
        <div class="resource-card">
          <div class="card-header">
            <div><span class="resource-title"><a href="/iam/{u['userName']}">{_esc(u['userName'])}</a></span></div>
            <span class="status-pill status-info">{len(u.get('attachedPolicies', []))} policies</span>
          </div>
          <div class="card-body">
            <div style="grid-column: 1 / -1;"><p class="data-label">ARN</p><p class="data-value font-code">{_esc(u['arn'])}</p></div>
            <div><p class="data-label">Groups</p><p class="data-value">{len(u.get('groups', []))}</p></div>
            <div><p class="data-label">Created</p><p class="data-value dim">{_esc(u.get('created','-'))}</p></div>
          </div>
        </div>"""
    if not iam_html:
        iam_html = '<div class="resource-card"><div class="empty-msg">No IAM users</div></div>'

    # Alarms
    alarm_html = ""
    for a in d["alarms"]:
        cls = _status_class(a["stateValue"])
        alarm_html += f"""
        <div class="resource-card">
          <div class="card-header">
            <div><span class="resource-title"><a href="/alarm/{a['alarmName']}">{_esc(a['alarmName'])}</a></span>
            <span class="resource-type">{_esc(a['metricName'])}</span></div>
            <span class="status-pill {cls}">{_esc(a['stateValue'])}</span>
          </div>
          <div class="card-body">
            <div style="grid-column:1/-1;"><p class="data-label">Reason</p><p class="data-value dim">{_esc(a.get('stateReason','-'))}</p></div>
          </div>
        </div>"""
    if not alarm_html:
        alarm_html = '<div class="resource-card"><div class="empty-msg">No alarms</div></div>'

    # Metrics
    metrics_html = ""
    for m in d["metrics"][:15]:
        key = f"{m['namespace']}/{m['metricName']}"
        metrics_html += f"""
        <div class="resource-card">
          <div class="card-header">
            <div><span class="resource-title"><a href="/metric/{m['namespace']}/{m['metricName']}">{_esc(m['metricName'])}</a></span>
            <span class="resource-type">{_esc(m['namespace'])}</span></div>
            <span class="status-pill status-info">{m['datapoints']} pts</span>
          </div>
        </div>"""
    if not metrics_html:
        metrics_html = '<div class="resource-card"><div class="empty-msg">No metrics</div></div>'

    # Log groups
    logs_html = ""
    for g in d["loggroups"]:
        logs_html += f"""
        <div class="resource-card">
          <div class="card-header">
            <div><span class="resource-title"><a href="/loggroup/{g['logGroupName']}">{_esc(g['logGroupName'])}</a></span></div>
            <span class="status-pill status-info">{g['events']} events</span>
          </div>
        </div>"""
    if not logs_html:
        logs_html = '<div class="resource-card"><div class="empty-msg">No log groups</div></div>'

    # Route tables
    rt_html = ""
    for rt in d.get("route_tables", []):
        n_routes = len(rt.get("routes", []))
        is_main = rt.get("isMain", False)
        badge = "status-ok" if is_main else "status-info"
        label = "MAIN" if is_main else "custom"
        rt_html += f"""
        <div class="resource-card">
          <div class="card-header">
            <div><span class="resource-title"><a href="/routetable/{rt['routeTableId']}">{_esc(rt['routeTableId'])}</a></span>
            <span class="resource-type">{_esc(rt.get('vpcId','-'))}</span></div>
            <span class="status-pill {badge}">{label}</span>
          </div>
          <div class="card-body">
            <div><p class="data-label">Routes</p><p class="data-value">{n_routes}</p></div>
            <div><p class="data-label">Region</p><p class="data-value">{_esc(rt.get('region','-'))}</p></div>
          </div>
        </div>"""
    if not rt_html:
        rt_html = '<div class="resource-card"><div class="empty-msg">No route tables</div></div>'

    # NAT Gateways
    nat_html = ""
    for n in d.get("nats", []):
        nat_html += f"""
        <div class="resource-card">
          <div class="card-header">
            <div><span class="resource-title"><a href="/nat/{n['natGatewayId']}">{_esc(n['natGatewayId'])}</a></span>
            <span class="resource-type">{_esc(n.get('subnetId','-'))}</span></div>
            <span class="status-pill status-ok">{_esc(n.get('state','-'))}</span>
          </div>
          <div class="card-body">
            <div><p class="data-label">Public IP</p><p class="data-value">{_esc(n.get('publicIp','-'))}</p></div>
            <div><p class="data-label">VPC</p><p class="data-value font-code">{_esc(n.get('vpcId','-'))}</p></div>
          </div>
        </div>"""
    if not nat_html:
        nat_html = '<div class="resource-card"><div class="empty-msg">No NAT Gateways</div></div>'

    # Security Groups
    sg_html = ""
    for g in d.get("security_groups", []):
        name = (g.get("tags") or {}).get("Name", "-")
        n_rules = len(g.get("ipPermissions", []))
        sg_html += f"""
        <div class="resource-card">
          <div class="card-header">
            <div><span class="resource-title"><a href="/securitygroup/{g['groupId']}">{_esc(name)}</a></span>
            <span class="resource-type">{_esc(g['groupId'])}</span></div>
            <span class="status-pill status-info">{n_rules} in</span>
          </div>
          <div class="card-body">
            <div><p class="data-label">VPC</p><p class="data-value font-code">{_esc(g.get('vpcId','-'))}</p></div>
            <div><p class="data-label">Description</p><p class="data-value dim">{_esc(g.get('description','-'))}</p></div>
          </div>
        </div>"""
    if not sg_html:
        sg_html = '<div class="resource-card"><div class="empty-msg">No security groups</div></div>'

    # Lambda functions
    lambda_html = ""
    for fn in d.get("lambdas", []):
        lambda_html += f"""
        <div class="resource-card">
          <div class="card-header">
            <div>
              <span class="resource-title"><a href="/lambda/{fn['FunctionName']}">{_esc(fn['FunctionName'])}</a></span>
              <span class="resource-type">{_esc(fn.get('Runtime','-'))}</span>
            </div>
            <span class="status-pill status-ok">{_esc(fn.get('State','-'))}</span>
          </div>
          <div class="card-body">
            <div><p class="data-label">Handler</p><p class="data-value font-code">{_esc(fn.get('Handler','-'))}</p></div>
            <div><p class="data-label">Code Size</p><p class="data-value">{fn.get('CodeSize',0)} bytes</p></div>
          </div>
        </div>"""
    if not lambda_html:
        lambda_html = '<div class="resource-card"><div class="empty-msg">No Lambda functions</div></div>'

    # DynamoDB tables
    ddb_html = ""
    for tbl in d.get("dynamodb_tables", []):
        key_name = tbl["KeySchema"][0]["AttributeName"] if tbl.get("KeySchema") else "-"
        ddb_html += f"""
        <div class="resource-card">
          <div class="card-header">
            <div>
              <span class="resource-title"><a href="/dynamodb/{tbl['TableName']}">{_esc(tbl['TableName'])}</a></span>
              <span class="resource-type">key: {_esc(key_name)}</span>
            </div>
            <span class="status-pill status-ok">{tbl.get('ItemCount',0)} items</span>
          </div>
          <div class="card-body">
            <div><p class="data-label">Status</p><p class="data-value">{_esc(tbl.get('TableStatus','-'))}</p></div>
            <div><p class="data-label">Created</p><p class="data-value dim">{_esc(tbl.get('CreationDateTime','-'))}</p></div>
          </div>
        </div>"""
    if not ddb_html:
        ddb_html = '<div class="resource-card"><div class="empty-msg">No DynamoDB tables</div></div>'

    alert_html = ""
    if flash_msg:
        variant = "ok" if flash_type == "ok" else "error"
        icon = "✅" if flash_type == "ok" else "❌"
        # Use .alert class with proper variant
        variant = "ok" if flash_type == "ok" else "error"
        alert_html = f'<div class="alert {variant}">{icon} {_esc(flash_msg)}</div>'

    body = f"""
    {alert_html}
    <h2>Service Overview</h2>
    <div class="metrics-grid">
      <div class="metric-card">
        <span class="metric-label">EC2 Instances</span>
        <div class="metric-value-row">
          <span class="metric-num">{len(d['instances'])}</span>
          <span class="badge-sub">{running} running</span>
        </div>
      </div>
      <div class="metric-card">
        <span class="metric-label">S3 Buckets</span>
        <div class="metric-value-row"><span class="metric-num {'dim' if not d['buckets'] else ''}">{len(d['buckets'])}</span></div>
      </div>
      <div class="metric-card">
        <span class="metric-label">VPCs</span>
        <div class="metric-value-row"><span class="metric-num {'dim' if not d['vpcs'] else ''}">{len(d['vpcs'])}</span></div>
      </div>
      <div class="metric-card">
        <span class="metric-label">IAM Users</span>
        <div class="metric-value-row"><span class="metric-num {'dim' if not d['users'] else ''}">{len(d['users'])}</span></div>
      </div>
      <div class="metric-card">
        <span class="metric-label">Alarms Firing</span>
        <div class="metric-value-row"><span class="metric-num {'dim' if not firing else ''}">{firing}</span></div>
      </div>
      <div class="metric-card">
        <span class="metric-label">Log Groups</span>
        <div class="metric-value-row"><span class="metric-num {'dim' if not d['loggroups'] else ''}">{len(d['loggroups'])}</span></div>
      </div>
    </div>

    <h2>EC2 Instances</h2>
    {ec2_html}

    <details class="create-section">
      <summary>➕ Create S3 Bucket</summary>
      <div class="form-card" style="margin-top:8px">
        <form method="POST" action="/create-s3" class="form-row">
          <label for="bucket">Name:</label>
          <input type="text" id="bucket" name="bucket" placeholder="my-bucket" required>
          <button type="submit">Create</button>
        </form>
        <p class="data-label" style="margin-top:8px">Bucket names must be unique, lowercase, 3-63 chars.</p>
      </div>
    </details>

    <h2>S3 Buckets</h2>
    {s3_html}

    <details class="create-section">
      <summary>➕ Create VPC</summary>
      <div class="form-card" style="margin-top:8px">
        <form method="POST" action="/create-vpc" class="form-row">
          <label for="cidr">CIDR:</label>
          <input type="text" id="cidr" name="cidr" placeholder="10.0.0.0/16" required>
          <button type="submit">Create</button>
        </form>
        <p class="data-label" style="margin-top:8px">
          Example: <code>10.0.0.0/16</code> (65,536 IPs) or <code>10.5.0.0/24</code> (256 IPs)
        </p>
      </div>
    </details>

    <h2>VPCs</h2>
    {vpc_html}

    <h2>IAM Users</h2>
    {iam_html}

    <h2>CloudWatch Alarms</h2>
    {alarm_html}

    <h2>CloudWatch Metrics</h2>
    {metrics_html}

    <h2>CloudWatch Log Groups</h2>
    {logs_html}

    <h2>Route Tables</h2>
    {rt_html}

    <h2>NAT Gateways</h2>
    {nat_html}

    <details class="create-section">
      <summary>➕ Create Security Group</summary>
      <div class="form-card" style="margin-top:8px">
        <form method="POST" action="/create-sg" class="form-row">
          <label for="name">Name:</label>
          <input type="text" id="name" name="name" placeholder="web-sg" required>
          <label for="desc">Desc:</label>
          <input type="text" id="desc" name="description" placeholder="For web servers">
          <button type="submit">Create</button>
        </form>
      </div>
    </details>

    <h2>Security Groups</h2>
    {sg_html}

    <details class="create-section">
      <summary>➕ Create Lambda Function</summary>
      <div class="form-card" style="margin-top:8px">
        <form method="POST" action="/create-lambda">
          <div class="form-row" style="margin-bottom:8px">
            <label for="fn-name">Name:</label>
            <input type="text" id="fn-name" name="name" placeholder="hello" required>
          </div>
          <label for="fn-code" class="data-label">Python code (must define lambda_handler):</label>
          <textarea id="fn-code" name="code" rows="6" class="form-textarea" required>def lambda_handler(event, context):
    return {{"statusCode": 200, "body": "Hello from Lambda!"}}</textarea>
          <div style="margin-top:8px">
            <button type="submit" class="form-button-primary">Create Function</button>
          </div>
        </form>
      </div>
    </details>

    <h2>Lambda Functions</h2>
    {lambda_html}

    <details class="create-section">
      <summary>➕ Create DynamoDB Table</summary>
      <div class="form-card" style="margin-top:8px">
        <form method="POST" action="/create-table" class="form-row">
          <label for="tbl">Table:</label>
          <input type="text" id="tbl" name="table_name" placeholder="Users" required>
          <label for="key">Key:</label>
          <input type="text" id="key" name="key_name" placeholder="id" required>
          <label for="ktype">Type:</label>
          <select id="ktype" name="key_type">
            <option value="S">String</option>
            <option value="N">Number</option>
          </select>
          <button type="submit">Create</button>
        </form>
      </div>
    </details>

    <h2>DynamoDB Tables</h2>
    {ddb_html}
    """

    subtitle = f"{acct['account_id']} · {acct['region']} · {d['generated']}"
    return _page("MiniAWS Console", body, subtitle=subtitle)


# ---------- Detail pages ----------

def _detail_page(title, subtitle, body_html):
    return _page(title, f'<a class="back" href="/">← Back to Console</a>\n{body_html}', subtitle=subtitle)



def render_routetable_detail(rt_id):
    from core import vpc as vpc_mod
    rt = vpc_mod.get_route_table(rt_id)
    if not rt:
        return _detail_page("Route Table Not Found", rt_id,
                            f'<div class="resource-card"><div class="empty-msg">No route table: {_esc(rt_id)}</div></div>')

    route_rows = ""
    for r in rt.get("routes", []):
        gw = r.get("gatewayId", "-")
        gw_link = gw
        if gw.startswith("igw-"):
            gw_link = f'<span class="font-code">{_esc(gw)}</span> (IGW)'
        elif gw.startswith("nat-"):
            gw_link = f'<a href="/nat/{gw}" class="font-code">{_esc(gw)}</a> (NAT)'
        elif gw == "local":
            gw_link = '<span class="dim">local</span>'
        route_rows += f"""
        <div class="detail-row">
          <span class="detail-label font-code">{_esc(r.get('destinationCidrBlock','-'))}</span>
          <span class="detail-value">{gw_link}</span>
        </div>"""

    assoc_rows = ""
    for s in rt.get("associations", []):
        assoc_rows += f'<div class="detail-row"><span class="detail-label font-code">{_esc(s)}</span><span class="detail-value"><a href="/subnet/{s}">subnet</a></span></div>'

    body = f"""
    <div class="resource-card">
      <div class="card-body" style="grid-template-columns:1fr;">
        <div class="detail-row"><span class="detail-label">Route Table ID</span><span class="detail-value font-code">{_esc(rt['routeTableId'])}</span></div>
        <div class="detail-row"><span class="detail-label">VPC</span><span class="detail-value font-code"><a href="/vpc/{rt['vpcId']}">{_esc(rt['vpcId'])}</a></span></div>
        <div class="detail-row"><span class="detail-label">Region</span><span class="detail-value">{_esc(rt.get('region','-'))}</span></div>
        <div class="detail-row"><span class="detail-label">Main</span><span class="detail-value">{'yes' if rt.get('isMain') else 'no'}</span></div>
      </div>
    </div>
    <h2>Routes ({len(rt.get('routes',[]))})</h2>
    <div class="resource-card"><div class="card-body" style="grid-template-columns:1fr;">{route_rows or '<div class="empty-msg">No routes</div>'}</div></div>
    <h2>Associated Subnets ({len(rt.get('associations',[]))})</h2>
    <div class="resource-card"><div class="card-body" style="grid-template-columns:1fr;">{assoc_rows or '<div class="empty-msg">None</div>'}</div></div>
    """
    return _detail_page(f"Route Table {rt_id}", rt_id, body)


def render_nat_detail(nat_id):
    from core import nat as nat_mod
    n = nat_mod.get_nat_gateway(nat_id)
    if not n:
        return _detail_page("NAT Gateway Not Found", nat_id,
                            f'<div class="resource-card"><div class="empty-msg">No NAT: {_esc(nat_id)}</div></div>')

    body = f"""
    <div class="resource-card">
      <div class="card-body" style="grid-template-columns:1fr;">
        <div class="detail-row"><span class="detail-label">NAT ID</span><span class="detail-value font-code">{_esc(n['natGatewayId'])}</span></div>
        <div class="detail-row"><span class="detail-label">Subnet</span><span class="detail-value font-code"><a href="/subnet/{n.get('subnetId','')}">{_esc(n.get('subnetId','-'))}</a></span></div>
        <div class="detail-row"><span class="detail-label">VPC</span><span class="detail-value font-code"><a href="/vpc/{n.get('vpcId','')}">{_esc(n.get('vpcId','-'))}</a></span></div>
        <div class="detail-row"><span class="detail-label">Region</span><span class="detail-value">{_esc(n.get('region','-'))}</span></div>
        <div class="detail-row"><span class="detail-label">State</span><span class="detail-value">{_esc(n.get('state','-'))}</span></div>
        <div class="detail-row"><span class="detail-label">Public IP</span><span class="detail-value">{_esc(n.get('publicIp','-'))}</span></div>
        <div class="detail-row"><span class="detail-label">Created</span><span class="detail-value dim">{_esc(n.get('createTime','-'))}</span></div>
      </div>
    </div>
    """
    return _detail_page(f"NAT Gateway {nat_id}", nat_id, body)


def render_sg_detail(sg_id):
    from core import sg as sg_mod
    g = sg_mod.get_security_group(sg_id)
    if not g:
        return _detail_page("Security Group Not Found", sg_id,
                            f'<div class="resource-card"><div class="empty-msg">No SG: {_esc(sg_id)}</div></div>')

    name = (g.get("tags") or {}).get("Name", "-")

    inbound = ""
    for r in g.get("ipPermissions", []):
        inbound += f'<div class="detail-row"><span class="detail-label">{_esc(sg_mod.format_rule(r))}</span><span class="detail-value status-ok">ALLOW IN</span></div>'

    outbound = ""
    for r in g.get("ipPermissionsEgress", []):
        outbound += f'<div class="detail-row"><span class="detail-label">{_esc(sg_mod.format_rule(r))}</span><span class="detail-value status-info">ALLOW OUT</span></div>'

    body = f"""
    <div class="resource-card">
      <div class="card-body" style="grid-template-columns:1fr;">
        <div class="detail-row"><span class="detail-label">Group ID</span><span class="detail-value font-code">{_esc(g['groupId'])}</span></div>
        <div class="detail-row"><span class="detail-label">Name</span><span class="detail-value">{_esc(name)}</span></div>
        <div class="detail-row"><span class="detail-label">VPC</span><span class="detail-value font-code"><a href="/vpc/{g.get('vpcId','')}">{_esc(g.get('vpcId','-'))}</a></span></div>
        <div class="detail-row"><span class="detail-label">Description</span><span class="detail-value dim">{_esc(g.get('description','-'))}</span></div>
      </div>
    </div>
    <h2>Inbound Rules ({len(g.get('ipPermissions',[]))})</h2>
    <div class="resource-card"><div class="card-body" style="grid-template-columns:1fr;">{inbound or '<div class="empty-msg">No inbound rules — all traffic blocked</div>'}</div></div>
    <h2>Outbound Rules ({len(g.get('ipPermissionsEgress',[]))})</h2>
    <div class="resource-card"><div class="card-body" style="grid-template-columns:1fr;">{outbound or '<div class="empty-msg">No outbound rules</div>'}</div></div>
    """
    return _detail_page(f"Security Group {name}", sg_id, body)


def render_not_found(path):
    return _detail_page("Not Found", "404", f'<div class="resource-card"><div class="empty-msg">No page for: {_esc(path)}</div></div>')


def render_vpc_detail(vpc_id):
    v = vpc.get_vpc(vpc_id)
    if not v:
        return _detail_page("VPC Not Found", vpc_id, f'<div class="resource-card"><div class="empty-msg">No VPC with ID: {_esc(vpc_id)}</div></div>')

    subnets = vpc.list_subnets(vpc_id=vpc_id)
    rts = [rt for rt in vpc.list_route_tables() if rt.get("vpcId") == vpc_id]
    igws = [g for g in vpc.list_internet_gateways() if vpc_id in g.get("attachments", [])]

    subnet_cards = ""
    for s in subnets:
        name = (s.get("tags") or {}).get("Name", "-")
        subnet_cards += f"""
        <div class="resource-card">
          <div class="card-header">
            <div><span class="resource-title"><a href="/subnet/{s['subnetId']}">{_esc(s['subnetId'])}</a></span>
            <span class="resource-type">{_esc(name)}</span></div>
            <form method="POST" action="/delete-subnet" style="display:inline" onsubmit="return confirm('Delete subnet {s['subnetId']}?')">
              <input type="hidden" name="subnet_id" value="{s['subnetId']}">
              <button type="submit" class="btn-delete">🗑</button>
            </form>
          </div>
          <div class="card-body">
            <div><p class="data-label">CIDR</p><p class="data-value font-code">{_esc(s['cidrBlock'])}</p></div>
            <div><p class="data-label">AZ</p><p class="data-value dim">{_esc(s.get('availabilityZone','-'))}</p></div>
          </div>
        </div>"""
    if not subnet_cards:
        subnet_cards = '<div class="resource-card"><div class="empty-msg">No subnets</div></div>'

    info_rows = f"""
    <div class="resource-card">
      <div class="card-body" style="grid-template-columns:1fr;">
        <div class="detail-row"><span class="detail-label">VPC ID</span><span class="detail-value font-code">{_esc(v['vpcId'])}</span></div>
        <div class="detail-row"><span class="detail-label">CIDR</span><span class="detail-value font-code">{_esc(v['cidrBlock'])}</span></div>
        <div class="detail-row"><span class="detail-label">Region</span><span class="detail-value">{_esc(v.get('region','-'))}</span></div>
        <div class="detail-row"><span class="detail-label">State</span><span class="detail-value">{_esc(v.get('state','-'))}</span></div>
        <div class="detail-row"><span class="detail-label">Created</span><span class="detail-value dim">{_esc(v.get('created','-'))}</span></div>
      </div>
    </div>"""

    igw_rows = ""
    for g in igws:
        igw_rows += f'<div class="detail-row"><span class="detail-label">IGW</span><span class="detail-value font-code">{_esc(g["internetGatewayId"])}</span></div>'
    igw_card = f'<div class="resource-card"><div class="card-body" style="grid-template-columns:1fr;">{igw_rows}</div></div>' if igw_rows else '<div class="resource-card"><div class="empty-msg">No IGW attached</div></div>'

    rt_cards = ""
    for rt in rts:
        rows = "".join(
            f'<div class="detail-row"><span class="detail-label">{_esc(r["destinationCidrBlock"])}</span>'
            f'<span class="detail-value font-code">→ {_esc(r["gatewayId"])}</span></div>'
            for r in rt.get("routes", [])
        )
        rt_cards += f'<div class="resource-card"><div class="card-header"><span class="resource-title">{_esc(rt["routeTableId"])}</span></div><div class="card-body" style="grid-template-columns:1fr;">{rows}</div></div>'

    body = f"""
    <form method="POST" action="/delete-vpc" style="display:inline" onsubmit="return confirm('Delete VPC {vpc_id}? This cannot be undone.')">
      <input type="hidden" name="vpc_id" value="{vpc_id}">
      <button type="submit" class="btn-delete-large">🗑 Delete this VPC</button>
    </form>

    <h2>Info</h2>{info_rows}

    <details class="create-section">
      <summary>➕ Create Subnet</summary>
      <div class="form-card" style="margin-top:8px">
        <form method="POST" action="/create-subnet" class="form-row">
          <input type="hidden" name="vpc_id" value="{vpc_id}">
          <label for="sub-cidr">CIDR:</label>
          <input type="text" id="sub-cidr" name="cidr" placeholder="10.0.1.0/24" required>
          <label for="sub-name">Name:</label>
          <input type="text" id="sub-name" name="name" placeholder="public-1">
          <button type="submit">Create</button>
        </form>
        <p class="data-label" style="margin-top:8px">
          Must be inside the VPC's range: <code>{_esc(v['cidrBlock'])}</code>
        </p>
      </div>
    </details>

    <h2>Subnets ({len(subnets)})</h2>{subnet_cards}
    <h2>Internet Gateway</h2>{igw_card}
    <h2>Route Tables</h2>{rt_cards or '<div class="resource-card"><div class="empty-msg">No route tables</div></div>'}
    """
    prefix = _cli_chip(f"aws ec2 describe-vpcs") + _json_panel("vpc", vpc_id)
    return _detail_page(f"VPC {vpc_id}", vpc_id, prefix + body)


def render_subnet_detail(subnet_id):
    s = vpc.get_subnet(subnet_id)
    if not s:
        return _detail_page("Subnet Not Found", subnet_id, f'<div class="resource-card"><div class="empty-msg">No subnet: {_esc(subnet_id)}</div></div>')

    body = f"""
    <div class="resource-card">
      <div class="card-body" style="grid-template-columns:1fr;">
        <div class="detail-row"><span class="detail-label">Subnet ID</span><span class="detail-value font-code">{_esc(s['subnetId'])}</span></div>
        <div class="detail-row"><span class="detail-label">CIDR</span><span class="detail-value font-code">{_esc(s['cidrBlock'])}</span></div>
        <div class="detail-row"><span class="detail-label">VPC</span><span class="detail-value font-code"><a href="/vpc/{s['vpcId']}">{_esc(s['vpcId'])}</a></span></div>
        <div class="detail-row"><span class="detail-label">AZ</span><span class="detail-value">{_esc(s.get('availabilityZone','-'))}</span></div>
        <div class="detail-row"><span class="detail-label">Name</span><span class="detail-value">{(s.get('tags') or {}).get('Name','-')}</span></div>
        <div class="detail-row"><span class="detail-label">State</span><span class="detail-value">{_esc(s.get('state','-'))}</span></div>
      </div>
    </div>
    """
    return _detail_page(f"Subnet {subnet_id}", subnet_id, body)


def render_ec2_detail(instance_id):
    i = ec2.get(instance_id)
    if not i:
        return _detail_page("Instance Not Found", instance_id, f'<div class="resource-card"><div class="empty-msg">No instance: {_esc(instance_id)}</div></div>')

    st = ec2.status(instance_id) or {}
    tags_html = "".join(
        f'<div class="detail-row"><span class="detail-label">{_esc(k)}</span><span class="detail-value">{_esc(v)}</span></div>'
        for k, v in (i.get("tags") or {}).items()
    )

    body = f"""
    <div class="resource-card">
      <div class="card-body" style="grid-template-columns:1fr;">
        <div class="detail-row"><span class="detail-label">Instance ID</span><span class="detail-value font-code">{_esc(i['instance_id'])}</span></div>
        <div class="detail-row"><span class="detail-label">Type</span><span class="detail-value">{_esc(i.get('instance_type','-'))}</span></div>
        <div class="detail-row"><span class="detail-label">State</span><span class="detail-value">{_esc(st.get('state','-'))}</span></div>
        <div class="detail-row"><span class="detail-label">PID</span><span class="detail-value font-code">{_esc(st.get('pid','-'))}</span></div>
        <div class="detail-row"><span class="detail-label">Uptime</span><span class="detail-value">{st.get('uptime_sec', 0)}s</span></div>
        <div class="detail-row"><span class="detail-label">Region</span><span class="detail-value">{_esc(i.get('region','-'))}</span></div>
      </div>
    </div>
    <h2>Tags</h2>
    <div class="resource-card"><div class="card-body" style="grid-template-columns:1fr;">{tags_html or '<div class="empty-msg">No tags</div>'}</div></div>
    """
    prefix = _cli_chip(f"aws ec2 describe-instances --instance-ids {instance_id}") + _json_panel("ec2", instance_id)
    return _detail_page(f"EC2 {instance_id}", instance_id, prefix + body)


def render_s3_detail(bucket_name):
    b = s3.get_bucket(bucket_name)
    if not b:
        return _detail_page("Bucket Not Found", bucket_name, f'<div class="resource-card"><div class="empty-msg">No bucket: {_esc(bucket_name)}</div></div>')

    objs = s3.list_objects(bucket_name) or []
    obj_rows = "".join(
        f'<div class="detail-row"><span class="detail-label font-code">{_esc(o["key"])}</span>'
        f'<span class="detail-value dim">{o["size"]} bytes</span></div>'
        for o in objs
    )

    body = f"""
    <div class="resource-card">
      <div class="card-body" style="grid-template-columns:1fr;">
        <div class="detail-row"><span class="detail-label">Bucket</span><span class="detail-value">{_esc(b['name'])}</span></div>
        <div class="detail-row"><span class="detail-label">Region</span><span class="detail-value">{_esc(b.get('region','-'))}</span></div>
        <div class="detail-row"><span class="detail-label">Created</span><span class="detail-value dim">{_esc(b.get('created','-'))}</span></div>
        <div class="detail-row"><span class="detail-label">Objects</span><span class="detail-value">{len(objs)}</span></div>
      </div>
    </div>
    <h2>Objects</h2>
    <div class="resource-card"><div class="card-body" style="grid-template-columns:1fr;">{obj_rows or '<div class="empty-msg">Empty bucket</div>'}</div></div>
    """
    prefix = _cli_chip(f"aws s3 ls s3://{bucket_name}/") + _json_panel("s3", bucket_name)
    return _detail_page(f"S3 {bucket_name}", bucket_name, prefix + body)


def render_iam_detail(username):
    u = iam.get_user(username)
    if not u:
        return _detail_page("User Not Found", username, f'<div class="resource-card"><div class="empty-msg">No user: {_esc(username)}</div></div>')

    pol_rows = "".join(
        f'<div class="detail-row"><span class="detail-label">{_esc(p)}</span><span class="detail-value">attached</span></div>'
        for p in u.get("attachedPolicies", [])
    )
    grp_rows = "".join(
        f'<div class="detail-row"><span class="detail-label">{_esc(g)}</span><span class="detail-value">member</span></div>'
        for g in u.get("groups", [])
    )

    body = f"""
    <div class="resource-card">
      <div class="card-body" style="grid-template-columns:1fr;">
        <div class="detail-row"><span class="detail-label">Username</span><span class="detail-value">{_esc(u['userName'])}</span></div>
        <div class="detail-row"><span class="detail-label">ARN</span><span class="detail-value font-code" style="font-size:11px">{_esc(u['arn'])}</span></div>
        <div class="detail-row"><span class="detail-label">Created</span><span class="detail-value dim">{_esc(u.get('created','-'))}</span></div>
      </div>
    </div>
    <h2>Policies ({len(u.get('attachedPolicies', []))})</h2>
    <div class="resource-card"><div class="card-body" style="grid-template-columns:1fr;">{pol_rows or '<div class="empty-msg">No policies</div>'}</div></div>
    <h2>Groups ({len(u.get('groups', []))})</h2>
    <div class="resource-card"><div class="card-body" style="grid-template-columns:1fr;">{grp_rows or '<div class="empty-msg">Not in any group</div>'}</div></div>
    """
    prefix = _cli_chip(f"aws iam get-user --user-name {username}") + _json_panel("iam", username)
    return _detail_page(f"IAM {username}", username, prefix + body)


def render_alarm_detail(alarm_name):
    alarms = cloudwatch.list_alarms()
    a = next((x for x in alarms if x["alarmName"] == alarm_name), None)
    if not a:
        return _detail_page("Alarm Not Found", alarm_name, f'<div class="resource-card"><div class="empty-msg">No alarm: {_esc(alarm_name)}</div></div>')

    body = f"""
    <div class="resource-card">
      <div class="card-body" style="grid-template-columns:1fr;">
        <div class="detail-row"><span class="detail-label">Alarm</span><span class="detail-value">{_esc(a['alarmName'])}</span></div>
        <div class="detail-row"><span class="detail-label">Namespace</span><span class="detail-value">{_esc(a['namespace'])}</span></div>
        <div class="detail-row"><span class="detail-label">Metric</span><span class="detail-value">{_esc(a['metricName'])}</span></div>
        <div class="detail-row"><span class="detail-label">Statistic</span><span class="detail-value">{_esc(a['statistic'])}</span></div>
        <div class="detail-row"><span class="detail-label">Threshold</span><span class="detail-value">{_esc(a['threshold'])}</span></div>
        <div class="detail-row"><span class="detail-label">Comparison</span><span class="detail-value">{_esc(a['comparisonOperator'])}</span></div>
        <div class="detail-row"><span class="detail-label">State</span><span class="detail-value">{_esc(a['stateValue'])}</span></div>
        <div class="detail-row"><span class="detail-label">Reason</span><span class="detail-value dim">{_esc(a.get('stateReason','-'))}</span></div>
      </div>
    </div>
    """
    return _detail_page(f"Alarm {alarm_name}", alarm_name, body)


def render_metric_detail(namespace, metric_name):
    stats = cloudwatch.get_metric_statistics(namespace, metric_name, stat="Average")
    if not stats:
        return _detail_page("Metric Not Found", f"{namespace}/{metric_name}", f'<div class="resource-card"><div class="empty-msg">No metric</div></div>')

    dps = stats["datapoints"]
    rows = "".join(
        f'<div class="detail-row"><span class="detail-label font-code">{_esc(d["timestamp"][:19])}</span>'
        f'<span class="detail-value">{d["value"]}</span></div>'
        for d in dps[-30:]
    )

    body = f"""
    <div class="resource-card">
      <div class="card-body" style="grid-template-columns:1fr;">
        <div class="detail-row"><span class="detail-label">Namespace</span><span class="detail-value">{_esc(namespace)}</span></div>
        <div class="detail-row"><span class="detail-label">Metric</span><span class="detail-value">{_esc(metric_name)}</span></div>
        <div class="detail-row"><span class="detail-label">Average</span><span class="detail-value">{stats['value']}</span></div>
        <div class="detail-row"><span class="detail-label">Samples</span><span class="detail-value">{stats['sampleCount']}</span></div>
      </div>
    </div>
    <h2>Datapoints</h2>
    <div class="resource-card"><div class="card-body" style="grid-template-columns:1fr;">{rows or '<div class="empty-msg">No data</div>'}</div></div>
    """
    return _detail_page(f"Metric {metric_name}", f"{namespace}/{metric_name}", body)


def render_loggroup_detail(name):
    events = cloudwatch.get_log_events(name, limit=100)
    if events is None:
        return _detail_page("Log Group Not Found", name, f'<div class="resource-card"><div class="empty-msg">No log group: {_esc(name)}</div></div>')

    lines = "".join(
        f'<div style="font-family:monospace;font-size:11px;padding:6px 0;border-bottom:1px solid #2b303a;word-break:break-all">{_esc(e)}</div>'
        for e in events
    )

    body = f"""
    <div class="resource-card">
      <div class="card-body" style="grid-template-columns:1fr;">
        <div class="detail-row"><span class="detail-label">Log Group</span><span class="detail-value">{_esc(name)}</span></div>
        <div class="detail-row"><span class="detail-label">Events</span><span class="detail-value">{len(events)}</span></div>
      </div>
    </div>
    <h2>Recent Events</h2>
    <div class="resource-card"><div class="card-body" style="grid-template-columns:1fr;">{lines or '<div class="empty-msg">Empty</div>'}</div></div>
    """
    return _detail_page(f"Logs {name}", name, body)


# ---------- Save dashboard to file ----------

def write_dashboard(path):
    d = os.path.dirname(path)
    if d:
        os.makedirs(d, exist_ok=True)
    with open(path, "w") as f:
        f.write(generate_html())
    return path
