"""HTML dashboard for MiniAzure — browser portal."""
import html
import os
from datetime import datetime

import config
from core import resource_group as rg
from core import vm as vmm
from core import storage
from core import network as netw
from core import iam
from core import breakage
from core import monitor


def _esc(s):
    return html.escape(str(s))


def _gather():
    """Collect all state for the dashboard."""
    groups = rg.list_all()
    vms = vmm.list_all()
    accounts = storage.list_accounts()
    vnets = netw.list_vnets()
    users = iam.list_users()

    vms_data = []
    for v in vms:
        st = vmm.status(v["name"]) or {}
        diag = breakage.diagnose(v["name"]) or {"healthy": True, "issues": []}
        vms_data.append({
            "name": v["name"],
            "group": v.get("resourceGroup"),
            "size": v.get("size"),
            "state": st.get("state", "?"),
            "pid": st.get("pid"),
            "uptime": st.get("uptime_sec", 0),
            "ip": (v.get("network") or {}).get("ip"),
            "issues": [i["type"] for i in diag.get("issues", [])],
        })

    storage_data = []
    for a in accounts:
        containers = storage.list_containers(a["name"]) or []
        storage_data.append({
            "name": a["name"],
            "group": a.get("resourceGroup"),
            "region": a.get("location"),
            "containers": containers,
        })

    net_data = netw.show_topology()

    alerts = monitor.read_alerts(limit=10)
    audit = iam.read_audit(limit=10)

    return {
        "groups": groups,
        "vms": vms_data,
        "storage": storage_data,
        "networks": net_data,
        "users": users,
        "alerts": alerts,
        "audit": audit,
        "generated": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
    }


def _state_class(state):
    if state == "RUNNING":
        return "ok"
    if state == "STOPPED":
        return "warn"
    return "bad"


def generate_html():
    d = _gather()

    # --- VM rows ---
    vm_rows = ""
    for v in d["vms"]:
        issue_marker = ""
        if v["issues"]:
            issue_marker = f' <span class="bad">⚠ {len(v["issues"])} issue(s)</span>'
        vm_rows += f"""
        <tr>
          <td><b>{_esc(v['name'])}</b>{issue_marker}</td>
          <td>{_esc(v['group'] or '-')}</td>
          <td>{_esc(v['size'] or '-')}</td>
          <td><span class="{_state_class(v['state'])}">{_esc(v['state'])}</span></td>
          <td>{_esc(v['pid'] or '-')}</td>
          <td>{_esc(v['ip'] or '-')}</td>
          <td>{v['uptime']}s</td>
        </tr>"""
    if not vm_rows:
        vm_rows = '<tr><td colspan="7" class="dim">No VMs</td></tr>'

    # --- Group rows ---
    group_rows = ""
    for g in d["groups"]:
        group_rows += f"""
        <tr>
          <td><b>{_esc(g['name'])}</b></td>
          <td>{_esc(g.get('location'))}</td>
          <td class="dim small">{_esc(g.get('created'))}</td>
        </tr>"""
    if not group_rows:
        group_rows = '<tr><td colspan="3" class="dim">No resource groups</td></tr>'

    # --- Storage rows ---
    storage_rows = ""
    for a in d["storage"]:
        conts = ", ".join(a["containers"]) if a["containers"] else "(none)"
        storage_rows += f"""
        <tr>
          <td><b>{_esc(a['name'])}</b></td>
          <td>{_esc(a['group'] or '-')}</td>
          <td>{_esc(a['region'] or '-')}</td>
          <td class="dim small">{_esc(conts)}</td>
        </tr>"""
    if not storage_rows:
        storage_rows = '<tr><td colspan="4" class="dim">No storage accounts</td></tr>'

    # --- Network rows ---
    net_html = ""
    for vnet in d["networks"]:
        net_html += f'<div class="vnet">🌐 <b>{_esc(vnet["name"])}</b> <span class="dim">({_esc(vnet["cidr"])})</span></div>'
        for s in vnet["subnets"]:
            net_html += f'<div class="subnet">📦 {_esc(s["name"])} <span class="dim">{_esc(s["cidr"])}</span></div>'
            for vm in s["vms"]:
                net_html += f'<div class="vmnode">💻 {_esc(vm["name"])} <span class="ok">{_esc(vm["ip"])}</span></div>'
    if not net_html:
        net_html = '<p class="dim">No networks</p>'

    # --- Users rows ---
    user_rows = ""
    for u in d["users"]:
        user_rows += f"""
        <tr>
          <td><b>{_esc(u['name'])}</b></td>
          <td>{_esc(u['role'])}</td>
          <td class="dim small">{_esc(u.get('created'))}</td>
        </tr>"""

    # --- Alerts ---
    alert_lines = ""
    for a in d["alerts"]:
        cls = "bad" if "[ALERT" in a or "[WARN" in a else "dim"
        alert_lines += f'<div class="{cls} small">{_esc(a)}</div>'
    if not alert_lines:
        alert_lines = '<p class="dim">No alerts</p>'

    # --- Audit ---
    audit_lines = ""
    for a in d["audit"]:
        cls = "bad" if "[DENIED" in a else "dim"
        audit_lines += f'<div class="{cls} small">{_esc(a)}</div>'
    if not audit_lines:
        audit_lines = '<p class="dim">No audit entries</p>'

    # --- Summary numbers ---
    running = sum(1 for v in d["vms"] if v["state"] == "RUNNING")
    issues = sum(len(v["issues"]) for v in d["vms"])

    page = f"""<!DOCTYPE html>
<html lang="en">
<head>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width, initial-scale=1">
<title>MiniAzure Portal</title>
<style>
  * {{ box-sizing: border-box; }}
  body {{ font-family: system-ui, -apple-system, sans-serif;
         background: #0f172a; color: #e2e8f0; margin: 0;
         padding: 20px; line-height: 1.5; }}
  .container {{ max-width: 1000px; margin: auto; }}
  h1 {{ color: #38bdf8; margin: 0 0 4px 0; font-size: 28px; }}
  h2 {{ color: #38bdf8; margin-top: 28px; padding-bottom: 8px;
       border-bottom: 1px solid #334155; font-size: 18px; }}
  .meta {{ color: #94a3b8; font-size: 13px; margin-bottom: 20px; }}
  .card {{ background: #1e293b; border-radius: 12px;
          padding: 18px; margin: 14px 0; }}
  .stats {{ display: grid; gap: 12px;
           grid-template-columns: repeat(auto-fit, minmax(140px, 1fr)); }}
  .stat {{ background: #1e293b; border-radius: 10px;
          padding: 16px; text-align: center; }}
  .stat-num {{ font-size: 28px; font-weight: bold; color: #38bdf8; }}
  .stat-lbl {{ font-size: 12px; color: #94a3b8;
              text-transform: uppercase; margin-top: 4px; }}
  table {{ width: 100%; border-collapse: collapse; margin-top: 8px; }}
  th, td {{ text-align: left; padding: 9px 10px;
           border-bottom: 1px solid #334155; font-size: 14px; }}
  th {{ color: #94a3b8; font-weight: 600; font-size: 12px;
       text-transform: uppercase; }}
  tr:last-child td {{ border-bottom: none; }}
  .ok {{ color: #4ade80; font-weight: bold; }}
  .warn {{ color: #fbbf24; font-weight: bold; }}
  .bad {{ color: #f87171; font-weight: bold; }}
  .dim {{ color: #94a3b8; }}
  .small {{ font-size: 12px; }}
  .vnet {{ font-size: 16px; margin-top: 8px; }}
  .subnet {{ margin-left: 20px; }}
  .vmnode {{ margin-left: 40px; font-size: 14px; }}
  .footer {{ margin-top: 40px; color: #64748b; font-size: 12px;
            text-align: center; }}
</style>
</head>
<body>
<div class="container">
  <h1>☁️ MiniAzure Portal</h1>
  <p class="meta">Generated {d['generated']}</p>

  <div class="stats">
    <div class="stat"><div class="stat-num">{len(d['groups'])}</div>
      <div class="stat-lbl">Resource Groups</div></div>
    <div class="stat"><div class="stat-num">{len(d['vms'])}</div>
      <div class="stat-lbl">VMs</div></div>
    <div class="stat"><div class="stat-num">{running}</div>
      <div class="stat-lbl">Running</div></div>
    <div class="stat"><div class="stat-num">{len(d['storage'])}</div>
      <div class="stat-lbl">Storage Accounts</div></div>
    <div class="stat"><div class="stat-num">{len(d['networks'])}</div>
      <div class="stat-lbl">VNets</div></div>
    <div class="stat"><div class="stat-num {'bad' if issues else ''}">{issues}</div>
      <div class="stat-lbl">Active Issues</div></div>
  </div>

  <h2>💻 Virtual Machines</h2>
  <div class="card">
    <table>
      <thead>
        <tr><th>Name</th><th>Group</th><th>Size</th>
            <th>State</th><th>PID</th><th>IP</th><th>Uptime</th></tr>
      </thead>
      <tbody>{vm_rows}</tbody>
    </table>
  </div>

  <h2>🌐 Network Topology</h2>
  <div class="card">{net_html}</div>

  <h2>📦 Storage Accounts</h2>
  <div class="card">
    <table>
      <thead><tr><th>Name</th><th>Group</th><th>Region</th>
             <th>Containers</th></tr></thead>
      <tbody>{storage_rows}</tbody>
    </table>
  </div>

  <h2>📁 Resource Groups</h2>
  <div class="card">
    <table>
      <thead><tr><th>Name</th><th>Region</th><th>Created</th></tr></thead>
      <tbody>{group_rows}</tbody>
    </table>
  </div>

  <h2>👤 Users</h2>
  <div class="card">
    <table>
      <thead><tr><th>Name</th><th>Role</th><th>Created</th></tr></thead>
      <tbody>{user_rows}</tbody>
    </table>
  </div>

  <h2>🚨 Recent Alerts</h2>
  <div class="card">{alert_lines}</div>

  <h2>📋 Recent Audit Entries</h2>
  <div class="card">{audit_lines}</div>

  <p class="footer">MiniAzure v1.0 — portal.py</p>
</div>
</body>
</html>"""

    return page


def write_dashboard(path):
    """Write the dashboard HTML to a file."""
    ensure_dir = os.path.dirname(path)
    if ensure_dir:
        os.makedirs(ensure_dir, exist_ok=True)
    with open(path, "w") as f:
        f.write(generate_html())
    return path
