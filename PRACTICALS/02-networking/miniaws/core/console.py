"""AWS Console — browser dashboard for MiniAWS."""
import html
import os
from datetime import datetime

from core import account, ec2, s3, vpc, iam, cloudwatch


def _esc(s):
    return html.escape(str(s))


def _gather():
    """Collect all state for the dashboard."""
    acct = account.summary()
    instances = ec2.list_all()
    buckets = s3.ls_buckets()
    vpcs = vpc.list_vpcs()
    subnets = vpc.list_subnets()
    igws = vpc.list_internet_gateways()
    rts = vpc.list_route_tables()
    users = iam.list_users()
    groups = iam.list_groups()
    policies = iam.list_policies()
    alarms = cloudwatch.list_alarms()
    metrics = cloudwatch.list_metrics()
    log_groups = cloudwatch.describe_log_groups()

    # EC2 runtime state
    inst_data = []
    for i in instances:
        st = ec2.status(i["instance_id"]) or {}
        inst_data.append({
            "id": i["instance_id"],
            "name": (i.get("tags") or {}).get("Name", "-"),
            "type": i.get("instance_type"),
            "state": st.get("state") or i.get("state"),
            "region": i.get("region"),
            "pid": st.get("pid"),
            "uptime": st.get("uptime_sec", 0),
        })

    # S3 with object counts
    bucket_data = []
    for b in buckets:
        objs = s3.list_objects(b["name"]) or []
        bucket_data.append({
            "name": b["name"],
            "region": b.get("region"),
            "objects": len(objs),
            "created": b.get("created", "?"),
        })

    # VPCs with subnet counts
    vpc_data = []
    for v in vpcs:
        vpc_data.append({
            "id": v["vpcId"],
            "cidr": v["cidrBlock"],
            "region": v["region"],
            "subnets": [s for s in subnets if s["vpcId"] == v["vpcId"]],
        })

    return {
        "account": acct,
        "instances": inst_data,
        "buckets": bucket_data,
        "vpcs": vpc_data,
        "igws": igws,
        "rts": rts,
        "users": users,
        "groups": groups,
        "policies": policies,
        "alarms": alarms,
        "metrics": metrics,
        "log_groups": log_groups,
        "generated": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
    }


def _state_class(state):
    if state == "running" or state == "available" or state == "OK":
        return "ok"
    if state == "stopped" or state == "INSUFFICIENT_DATA":
        return "warn"
    return "bad"


def generate_html():
    d = _gather()

    # EC2 rows
    ec2_rows = ""
    for i in d["instances"]:
        ec2_rows += f"""
        <tr>
          <td><b>{_esc(i['id'])}</b></td>
          <td>{_esc(i['name'])}</td>
          <td>{_esc(i['type'])}</td>
          <td><span class="{_state_class(i['state'])}">{_esc(i['state'])}</span></td>
          <td>{_esc(i['region'])}</td>
          <td>{i['uptime']}s</td>
        </tr>"""
    if not ec2_rows:
        ec2_rows = '<tr><td colspan="6" class="dim">No instances</td></tr>'

    # S3 rows
    s3_rows = ""
    for b in d["buckets"]:
        s3_rows += f"""
        <tr>
          <td><b>{_esc(b['name'])}</b></td>
          <td>{_esc(b['region'])}</td>
          <td>{b['objects']}</td>
          <td class="dim small">{_esc(b['created'])}</td>
        </tr>"""
    if not s3_rows:
        s3_rows = '<tr><td colspan="4" class="dim">No buckets</td></tr>'

    # VPC rows
    vpc_rows = ""
    for v in d["vpcs"]:
        sub_list = ", ".join(f"{s['subnetId'][:12]}... ({s['cidrBlock']})" for s in v["subnets"]) or "(none)"
        vpc_rows += f"""
        <tr>
          <td><b>{_esc(v['id'])}</b></td>
          <td>{_esc(v['cidr'])}</td>
          <td>{_esc(v['region'])}</td>
          <td class="dim small">{_esc(sub_list)}</td>
        </tr>"""
    if not vpc_rows:
        vpc_rows = '<tr><td colspan="4" class="dim">No VPCs</td></tr>'

    # IAM users
    user_rows = ""
    for u in d["users"]:
        user_rows += f"""
        <tr>
          <td><b>{_esc(u['userName'])}</b></td>
          <td class="dim small">{_esc(u['arn'])}</td>
          <td>{len(u.get('attachedPolicies', []))}</td>
          <td>{len(u.get('groups', []))}</td>
        </tr>"""
    if not user_rows:
        user_rows = '<tr><td colspan="4" class="dim">No users</td></tr>'

    # Alarms
    alarm_rows = ""
    for a in d["alarms"]:
        alarm_rows += f"""
        <tr>
          <td><b>{_esc(a['alarmName'])}</b></td>
          <td>{_esc(a['metricName'])}</td>
          <td><span class="{_state_class(a['stateValue'])}">{_esc(a['stateValue'])}</span></td>
          <td class="dim small">{_esc(a.get('stateReason',''))[:60]}</td>
        </tr>"""
    if not alarm_rows:
        alarm_rows = '<tr><td colspan="4" class="dim">No alarms</td></tr>'

    # Metrics summary
    metric_rows = ""
    for m in d["metrics"][:20]:
        metric_rows += f"""
        <tr>
          <td>{_esc(m['namespace'])}</td>
          <td><b>{_esc(m['metricName'])}</b></td>
          <td>{m['datapoints']}</td>
          <td>{_esc(m['unit'])}</td>
        </tr>"""
    if not metric_rows:
        metric_rows = '<tr><td colspan="4" class="dim">No metrics</td></tr>'

    # Log groups
    log_rows = ""
    for g in d["log_groups"]:
        log_rows += f"""
        <tr>
          <td><b>{_esc(g['logGroupName'])}</b></td>
          <td>{g['events']}</td>
          <td>{g['storedBytes']}</td>
        </tr>"""
    if not log_rows:
        log_rows = '<tr><td colspan="3" class="dim">No log groups</td></tr>'

    # Stats
    running = sum(1 for i in d["instances"] if i["state"] == "running")
    in_alarm = sum(1 for a in d["alarms"] if a["stateValue"] == "ALARM")

    page = f"""<!DOCTYPE html>
<html lang="en">
<head>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width, initial-scale=1">
<title>MiniAWS Console</title>
<style>
  * {{ box-sizing: border-box; }}
  body {{ font-family: system-ui, -apple-system, sans-serif;
         background: #0f172a; color: #e2e8f0; margin: 0;
         padding: 20px; line-height: 1.5; }}
  .container {{ max-width: 1000px; margin: auto; }}
  h1 {{ color: #ff9900; margin: 0 0 4px 0; font-size: 28px; }}
  h2 {{ color: #38bdf8; margin-top: 28px; padding-bottom: 8px;
       border-bottom: 1px solid #334155; font-size: 18px; }}
  .meta {{ color: #94a3b8; font-size: 13px; margin-bottom: 20px; }}
  .card {{ background: #1e293b; border-radius: 12px;
          padding: 18px; margin: 14px 0; }}
  .stats {{ display: grid; gap: 12px;
           grid-template-columns: repeat(auto-fit, minmax(140px, 1fr)); }}
  .stat {{ background: #1e293b; border-radius: 10px;
          padding: 16px; text-align: center; }}
  .stat-num {{ font-size: 28px; font-weight: bold; color: #ff9900; }}
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
  .footer {{ margin-top: 40px; color: #64748b; font-size: 12px;
            text-align: center; }}
</style>
</head>
<body>
<div class="container">
  <h1>🅰️ MiniAWS Console</h1>
  <p class="meta">
    Account {d['account']['account_id']} ·
    Region {d['account']['region']} ·
    Generated {d['generated']}
  </p>

  <div class="stats">
    <div class="stat"><div class="stat-num">{len(d['instances'])}</div>
      <div class="stat-lbl">EC2 Instances</div></div>
    <div class="stat"><div class="stat-num">{running}</div>
      <div class="stat-lbl">Running</div></div>
    <div class="stat"><div class="stat-num">{len(d['buckets'])}</div>
      <div class="stat-lbl">S3 Buckets</div></div>
    <div class="stat"><div class="stat-num">{len(d['vpcs'])}</div>
      <div class="stat-lbl">VPCs</div></div>
    <div class="stat"><div class="stat-num">{len(d['users'])}</div>
      <div class="stat-lbl">IAM Users</div></div>
    <div class="stat"><div class="stat-num {'bad' if in_alarm else ''}">{in_alarm}</div>
      <div class="stat-lbl">Alarms Firing</div></div>
  </div>

  <h2>💻 EC2 Instances</h2>
  <div class="card">
    <table>
      <thead><tr><th>Instance ID</th><th>Name</th><th>Type</th>
             <th>State</th><th>Region</th><th>Uptime</th></tr></thead>
      <tbody>{ec2_rows}</tbody>
    </table>
  </div>

  <h2>🪣 S3 Buckets</h2>
  <div class="card">
    <table>
      <thead><tr><th>Bucket</th><th>Region</th><th>Objects</th><th>Created</th></tr></thead>
      <tbody>{s3_rows}</tbody>
    </table>
  </div>

  <h2>🌐 VPCs</h2>
  <div class="card">
    <table>
      <thead><tr><th>VPC ID</th><th>CIDR</th><th>Region</th><th>Subnets</th></tr></thead>
      <tbody>{vpc_rows}</tbody>
    </table>
  </div>

  <h2>👤 IAM Users</h2>
  <div class="card">
    <table>
      <thead><tr><th>User</th><th>ARN</th><th>Policies</th><th>Groups</th></tr></thead>
      <tbody>{user_rows}</tbody>
    </table>
  </div>

  <h2>🚨 CloudWatch Alarms</h2>
  <div class="card">
    <table>
      <thead><tr><th>Alarm</th><th>Metric</th><th>State</th><th>Reason</th></tr></thead>
      <tbody>{alarm_rows}</tbody>
    </table>
  </div>

  <h2>📊 CloudWatch Metrics</h2>
  <div class="card">
    <table>
      <thead><tr><th>Namespace</th><th>Metric</th><th>Datapoints</th><th>Unit</th></tr></thead>
      <tbody>{metric_rows}</tbody>
    </table>
  </div>

  <h2>📝 CloudWatch Log Groups</h2>
  <div class="card">
    <table>
      <thead><tr><th>Log Group</th><th>Events</th><th>Bytes</th></tr></thead>
      <tbody>{log_rows}</tbody>
    </table>
  </div>

  <p class="footer">MiniAWS v1.0 — console.py</p>
</div>
</body>
</html>"""
    return page


def write_dashboard(path):
    import os
    d = os.path.dirname(path)
    if d:
        os.makedirs(d, exist_ok=True)
    with open(path, "w") as f:
        f.write(generate_html())
    return path
