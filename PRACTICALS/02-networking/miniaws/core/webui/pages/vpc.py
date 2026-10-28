"""VPC service pages — VPCs, subnets, route tables, IGWs, NATs, SGs (Phase 5)."""
import html
from datetime import datetime

from core import vpc as vpc_mod
from core import sg as sg_mod
from core import nat as nat_mod


def _esc(s):
    return html.escape(str(s))


def _name(rec):
    """Extract tags.Name the way cli.py does."""
    return (rec.get("tags") or {}).get("Name") or "—"


def _human_date(iso):
    if not iso:
        return "—"
    try:
        dt = datetime.fromisoformat(str(iso).replace("Z", ""))
        return dt.strftime("%B %d, %Y, %H:%M:%S")
    except Exception:
        return str(iso)


def _flash(qs):
    okv = (qs or {}).get("ok") or []
    erv = (qs or {}).get("error") or []
    if okv:
        return f'<div class="aws-notice aws-notice-success">{html.escape(str(okv[0]))}</div>'
    if erv:
        return f'<div class="aws-notice aws-notice-error">{html.escape(str(erv[0]))}</div>'
    return ""


def _state_pill(state):
    s = (state or "unknown").lower()
    cls = {"available": "pill-running", "attached": "pill-running",
           "detached": "pill-stopped", "pending": "pill-stopped",
           "deleting": "pill-terminated", "deleted": "pill-terminated"}.get(s, "pill-stopped")
    return f'<span class="ec2-pill {cls}">{_esc(s)}</span>'


def _tabs(active, vpc_id):
    tabs = [
        ("details",   "Details"),
        ("cidr",      "CIDR blocks"),
        ("subnets",   "Subnets"),
        ("rts",       "Route tables"),
        ("igws",      "Internet gateways"),
        ("sgs",       "Security groups"),
        ("tags",      "Tags"),
    ]
    parts = []
    for tid, label in tabs:
        cls = "active" if tid == active else ""
        href = f"/vpc/{vpc_id}" if tid == "details" else f"/vpc/{vpc_id}?tab={tid}"
        parts.append(f'<a class="s3-tab {cls}" href="{href}">{label}</a>')
    return f'<nav class="s3-tabs">{"".join(parts)}</nav>'


def _vpc_resource_map(vpc_id, subnets, rts, igws, sgs):
    """Tiny SVG diagram — matches the 'Resource map' sidebar of real VPC console."""
    igw_attached = [i for i in igws if vpc_id in (i.get("attachments") or [])]
    igw_label = _name(igw_attached[0]) if igw_attached else "(no IGW)"
    return f"""
<div class="vpc-map">
  <div class="vpc-map-title">Resource map</div>
  <svg viewBox="0 0 280 220" xmlns="http://www.w3.org/2000/svg" width="100%">
    <rect x="8" y="8" width="264" height="204" rx="6" fill="#f1f8ff" stroke="#0073bb" stroke-dasharray="4 2"/>
    <text x="16" y="26" font-size="11" fill="#0073bb" font-weight="600">VPC {_esc(vpc_id[:13])}…</text>
    <rect x="90" y="38" width="100" height="24" rx="4" fill="#fff8e6" stroke="#f2cd5c"/>
    <text x="140" y="54" font-size="10" text-anchor="middle" fill="#16191f">IGW: {_esc(igw_label)}</text>
    <line x1="140" y1="62" x2="140" y2="90" stroke="#687078" stroke-dasharray="2 2"/>
    <rect x="110" y="90" width="60" height="24" rx="4" fill="#ffffff" stroke="#0073bb"/>
    <text x="140" y="106" font-size="10" text-anchor="middle" fill="#16191f">VPC</text>
    <line x1="140" y1="114" x2="140" y2="130" stroke="#687078"/>
    <line x1="60" y1="130" x2="220" y2="130" stroke="#687078"/>
    <line x1="60" y1="130" x2="60" y2="150" stroke="#687078"/>
    <line x1="140" y1="130" x2="140" y2="150" stroke="#687078"/>
    <line x1="220" y1="130" x2="220" y2="150" stroke="#687078"/>
    <rect x="20" y="150" width="80" height="26" rx="3" fill="#e6f4e7" stroke="#7ad17e"/>
    <text x="60" y="167" font-size="10" text-anchor="middle" fill="#16191f">{len(subnets)} subnet(s)</text>
    <rect x="100" y="150" width="80" height="26" rx="3" fill="#ffffff" stroke="#d5dbdb"/>
    <text x="140" y="167" font-size="10" text-anchor="middle" fill="#16191f">{len(rts)} route table(s)</text>
    <rect x="180" y="150" width="80" height="26" rx="3" fill="#fbeae7" stroke="#f5b7ab"/>
    <text x="220" y="167" font-size="10" text-anchor="middle" fill="#16191f">{len(sgs)} SG(s)</text>
  </svg>
</div>"""


# ---------- VPCs list ----------

def render_vpcs(qs=None):
    flash = _flash(qs)
    try:
        vpcs = vpc_mod.list_vpcs()
    except Exception as e:
        return f'<div class="aws-notice aws-notice-error">Error: {_esc(e)}</div>'

    if not vpcs:
        rows_html = '<tr><td colspan="6" class="aws-muted" style="text-align:center; padding:24px;">No VPCs. Click Create VPC.</td></tr>'
    else:
        rows_html = "".join(f"""
            <tr>
              <td><a href="/vpc/{_esc(v['vpcId'])}">{_esc(v['vpcId'])}</a></td>
              <td>{_esc(_name(v))}</td>
              <td>{_esc(v.get('state','—'))}</td>
              <td><code>{_esc(v.get('cidrBlock','—'))}</code></td>
              <td>{'Yes' if v.get('isDefault') else 'No'}</td>
              <td>{_esc(v.get('region','—'))}</td>
            </tr>""" for v in vpcs)

    return f"""
<section class="aws-section">
  {flash}
  <div class="s3-page-header">
    <h1>Your VPCs <span class="aws-muted">({len(vpcs)})</span></h1>
    <div class="s3-page-actions">
      <a class="aws-button-primary" href="/vpc/create">Create VPC</a>
    </div>
  </div>

  <table class="aws-table">
    <thead>
      <tr>
        <th>VPC ID</th>
        <th>Name</th>
        <th>State</th>
        <th>IPv4 CIDR</th>
        <th>Default VPC</th>
        <th>Region</th>
      </tr>
    </thead>
    <tbody>{rows_html}</tbody>
  </table>
</section>"""


# ---------- VPC detail (with 6 tabs) ----------

def render_vpc_detail(vpc_id, tab="details", qs=None):
    v = vpc_mod.get_vpc(vpc_id)
    if not v:
        return f'<div class="aws-notice aws-notice-error">VPC not found: {_esc(vpc_id)}</div>'

    flash = _flash(qs)
    tabs_html = _tabs(tab, vpc_id)

    subnets = [s for s in vpc_mod.list_subnets() if s.get("vpcId") == vpc_id]
    rts     = [r for r in vpc_mod.list_route_tables() if r.get("vpcId") == vpc_id]
    igws    = vpc_mod.list_internet_gateways()
    my_igws = [i for i in igws if vpc_id in (i.get("attachments") or [])]
    try:
        sgs = [s for s in sg_mod.list_security_groups() if s.get("vpcId") == vpc_id]
    except Exception:
        sgs = []

    if tab == "details":
        content = f"""
<h2 class="ec2-section-title">VPC details</h2>
<table class="aws-table">
  <tbody>
    <tr><th style="width:30%;">VPC ID</th><td><code>{_esc(v['vpcId'])}</code></td></tr>
    <tr><th>ARN</th><td><code>{_esc(v.get('arn','—'))}</code></td></tr>
    <tr><th>State</th><td>{_state_pill(v.get('state'))}</td></tr>
    <tr><th>IPv4 CIDR</th><td><code>{_esc(v.get('cidrBlock'))}</code></td></tr>
    <tr><th>Region</th><td>{_esc(v.get('region'))}</td></tr>
    <tr><th>Default VPC</th><td>{'Yes' if v.get('isDefault') else 'No'}</td></tr>
    <tr><th>Tenancy</th><td>Default</td></tr>
    <tr><th>DNS hostnames</th><td>Enabled</td></tr>
    <tr><th>DNS resolution</th><td>Enabled</td></tr>
    <tr><th>Created</th><td>{_esc(_human_date(v.get('created')))}</td></tr>
  </tbody>
</table>

<h2 class="ec2-section-title">Actions</h2>
<div class="ec2-action-row">
  <a class="aws-button-secondary" href="/vpc/subnets/create?vpc_id={_esc(vpc_id)}">Create subnet</a>
  <a class="aws-button-secondary" href="/vpc/igws/create">Create internet gateway</a>
  <a class="aws-button-secondary" href="/vpc/nats/create?vpc_id={_esc(vpc_id)}">Create NAT gateway</a>
  <a class="aws-button-secondary" href="/vpc/sgs/create?vpc_id={_esc(vpc_id)}">Create security group</a>
  <form method="POST" action="/vpc/delete" style="display:inline"
        onsubmit="return confirm('Delete VPC {_esc(vpc_id)}? Must be empty first.')">
    <input type="hidden" name="vpc_id" value="{_esc(vpc_id)}">
    <button type="submit" class="aws-button-danger">Delete VPC</button>
  </form>
</div>"""

    elif tab == "cidr":
        content = f"""
<table class="aws-table">
  <thead><tr><th>CIDR block</th><th>State</th><th>Association</th></tr></thead>
  <tbody>
    <tr>
      <td><code>{_esc(v.get('cidrBlock'))}</code></td>
      <td>{_state_pill(v.get('state'))}</td>
      <td>Primary</td>
    </tr>
  </tbody>
</table>"""

    elif tab == "subnets":
        rows = "".join(f"""
        <tr>
          <td><a href="/vpc/subnets/{_esc(s['subnetId'])}">{_esc(s['subnetId'])}</a></td>
          <td>{_esc(_name(s))}</td>
          <td>{_esc(s.get('availabilityZone','—'))}</td>
          <td><code>{_esc(s.get('cidrBlock','—'))}</code></td>
          <td>{s.get('availableIpCount', '—')}</td>
          <td>{_state_pill(s.get('state'))}</td>
        </tr>""" for s in subnets) or '<tr><td colspan="6" class="aws-muted">No subnets in this VPC.</td></tr>'
        content = f"""
<div class="s3-page-header" style="margin-bottom:8px;">
  <h2 class="ec2-section-title" style="margin:0;">Subnets ({len(subnets)})</h2>
  <a class="aws-button-primary" href="/vpc/subnets/create?vpc_id={_esc(vpc_id)}">Create subnet</a>
</div>
<table class="aws-table">
  <thead>
    <tr><th>Subnet ID</th><th>Name</th><th>Availability Zone</th>
        <th>IPv4 CIDR</th><th>Available IPv4</th><th>State</th></tr>
  </thead>
  <tbody>{rows}</tbody>
</table>"""

    elif tab == "rts":
        rows = "".join(f"""
        <tr>
          <td><a href="/vpc/route-tables/{_esc(r['routeTableId'])}">{_esc(r['routeTableId'])}</a></td>
          <td>{'Yes' if r.get('isMain') else 'No'}</td>
          <td>{len(r.get('routes') or [])}</td>
          <td>{len(r.get('associations') or [])}</td>
        </tr>""" for r in rts) or '<tr><td colspan="4" class="aws-muted">No route tables.</td></tr>'
        content = f"""
<h2 class="ec2-section-title">Route tables ({len(rts)})</h2>
<table class="aws-table">
  <thead><tr><th>Route table ID</th><th>Main</th><th>Routes</th><th>Explicit subnet associations</th></tr></thead>
  <tbody>{rows}</tbody>
</table>"""

    elif tab == "igws":
        rows = "".join(f"""
        <tr>
          <td>{_esc(i['internetGatewayId'])}</td>
          <td>{_esc(_name(i))}</td>
          <td>{_state_pill(i.get('state'))}</td>
          <td>{_esc(', '.join(i.get('attachments') or []) or '—')}</td>
          <td>
            <form method="POST" action="/vpc/igws/detach" style="display:inline"
                  onsubmit="return confirm('Detach IGW?')">
              <input type="hidden" name="igw_id" value="{_esc(i['internetGatewayId'])}">
              <input type="hidden" name="vpc_id" value="{_esc(vpc_id)}">
              <button type="submit" class="aws-link-danger">Detach</button>
            </form>
          </td>
        </tr>""" for i in my_igws) or '<tr><td colspan="5" class="aws-muted">No internet gateway attached.</td></tr>'
        content = f"""
<h2 class="ec2-section-title">Internet gateways ({len(my_igws)})</h2>
<table class="aws-table">
  <thead><tr><th>IGW ID</th><th>Name</th><th>State</th><th>Attached VPC</th><th>Actions</th></tr></thead>
  <tbody>{rows}</tbody>
</table>
<div style="margin-top:12px;">
  <a class="aws-button-secondary" href="/vpc/igws/create">Create internet gateway</a>
</div>"""

    elif tab == "sgs":
        rows = "".join(f"""
        <tr>
          <td><a href="/vpc/security-groups/{_esc(s['groupId'])}">{_esc(s['groupId'])}</a></td>
          <td>{_esc(s.get('groupName','—'))}</td>
          <td>{_esc(s.get('description','—'))}</td>
          <td>{len(s.get('ipPermissions') or [])}</td>
          <td>{len(s.get('ipPermissionsEgress') or [])}</td>
        </tr>""" for s in sgs) or '<tr><td colspan="5" class="aws-muted">No security groups in this VPC.</td></tr>'
        content = f"""
<div class="s3-page-header" style="margin-bottom:8px;">
  <h2 class="ec2-section-title" style="margin:0;">Security groups ({len(sgs)})</h2>
  <a class="aws-button-primary" href="/vpc/sgs/create?vpc_id={_esc(vpc_id)}">Create security group</a>
</div>
<table class="aws-table">
  <thead>
    <tr><th>SG ID</th><th>Name</th><th>Description</th><th>Inbound rules</th><th>Outbound rules</th></tr>
  </thead>
  <tbody>{rows}</tbody>
</table>"""

    else:  # tags
        tags = v.get("tags") or {}
        tag_rows = "".join(f"<tr><td>{_esc(k)}</td><td>{_esc(vv)}</td></tr>"
                           for k, vv in sorted(tags.items())) or \
                   '<tr><td colspan="2" class="aws-muted">No tags</td></tr>'
        content = f"""
<h2 class="ec2-section-title">Tags</h2>
<table class="aws-table">
  <thead><tr><th>Key</th><th>Value</th></tr></thead>
  <tbody>{tag_rows}</tbody>
</table>"""

    resource_map = _vpc_resource_map(vpc_id, subnets, rts, my_igws, sgs)

    return f"""
<section class="aws-section">
  {flash}
  <div class="s3-page-header">
    <h1>{_esc(vpc_id)} <span class="aws-muted">{_esc(_name(v))}</span></h1>
    <div class="s3-page-actions">
      <a class="aws-button-secondary" href="/vpc">&#8592; Your VPCs</a>
    </div>
  </div>
  <div class="vpc-detail-grid">
    <div class="vpc-detail-main">
      {tabs_html}
      {content}
    </div>
    <div class="vpc-detail-side">{resource_map}</div>
  </div>
</section>"""


# ---------- Subnets (standalone list) ----------

def render_subnets(qs=None):
    flash = _flash(qs)
    try:
        subs = vpc_mod.list_subnets()
    except Exception as e:
        return f'<div class="aws-notice aws-notice-error">Error: {_esc(e)}</div>'

    if not subs:
        rows_html = '<tr><td colspan="6" class="aws-muted" style="text-align:center; padding:24px;">No subnets.</td></tr>'
    else:
        rows_html = "".join(f"""
        <tr>
          <td><a href="/vpc/subnets/{_esc(s['subnetId'])}">{_esc(s['subnetId'])}</a></td>
          <td>{_esc(_name(s))}</td>
          <td>{_esc(s.get('vpcId','—'))}</td>
          <td>{_esc(s.get('availabilityZone','—'))}</td>
          <td><code>{_esc(s.get('cidrBlock','—'))}</code></td>
          <td>{s.get('availableIpCount','—')}</td>
          <td>{_state_pill(s.get('state'))}</td>
        </tr>""" for s in subs)

    return f"""
<section class="aws-section">
  {flash}
  <div class="s3-page-header">
    <h1>Subnets <span class="aws-muted">({len(subs)})</span></h1>
    <div class="s3-page-actions">
      <a class="aws-button-primary" href="/vpc/subnets/create">Create subnet</a>
    </div>
  </div>
  <table class="aws-table">
    <thead>
      <tr><th>Subnet ID</th><th>Name</th><th>VPC</th><th>AZ</th>
          <th>IPv4 CIDR</th><th>Available IPv4</th><th>State</th></tr>
    </thead>
    <tbody>{rows_html}</tbody>
  </table>
</section>"""


def render_subnet_detail(subnet_id, qs=None):
    s = vpc_mod.get_subnet(subnet_id)
    if not s:
        return f'<div class="aws-notice aws-notice-error">Subnet not found: {_esc(subnet_id)}</div>'
    flash = _flash(qs)
    return f"""
<section class="aws-section">
  {flash}
  <div class="s3-page-header">
    <h1>{_esc(subnet_id)} <span class="aws-muted">{_esc(_name(s))}</span></h1>
    <div class="s3-page-actions">
      <a class="aws-button-secondary" href="/vpc/subnets">&#8592; Subnets</a>
    </div>
  </div>
  <table class="aws-table">
    <tbody>
      <tr><th style="width:30%;">Subnet ID</th><td><code>{_esc(s['subnetId'])}</code></td></tr>
      <tr><th>ARN</th><td><code>{_esc(s.get('arn','—'))}</code></td></tr>
      <tr><th>Name</th><td>{_esc(_name(s))}</td></tr>
      <tr><th>VPC</th><td><a href="/vpc/{_esc(s.get('vpcId',''))}">{_esc(s.get('vpcId','—'))}</a></td></tr>
      <tr><th>Availability Zone</th><td>{_esc(s.get('availabilityZone','—'))}</td></tr>
      <tr><th>IPv4 CIDR</th><td><code>{_esc(s.get('cidrBlock','—'))}</code></td></tr>
      <tr><th>Available IPv4</th><td>{s.get('availableIpCount','—')}</td></tr>
      <tr><th>Map public IP</th><td>{'Yes' if s.get('mapPublicIpOnLaunch') else 'No'}</td></tr>
      <tr><th>State</th><td>{_state_pill(s.get('state'))}</td></tr>
      <tr><th>Region</th><td>{_esc(s.get('region','—'))}</td></tr>
      <tr><th>Created</th><td>{_esc(_human_date(s.get('created')))}</td></tr>
    </tbody>
  </table>
  <div class="ec2-action-row" style="margin-top:16px;">
    <form method="POST" action="/vpc/subnets/delete" style="display:inline"
          onsubmit="return confirm('Delete subnet {_esc(subnet_id)}?')">
      <input type="hidden" name="subnet_id" value="{_esc(subnet_id)}">
      <button type="submit" class="aws-button-danger">Delete subnet</button>
    </form>
  </div>
</section>"""


# ---------- Route tables ----------

def render_route_tables(qs=None):
    flash = _flash(qs)
    try:
        rts = vpc_mod.list_route_tables()
    except Exception as e:
        return f'<div class="aws-notice aws-notice-error">Error: {_esc(e)}</div>'

    rows = "".join(f"""
    <tr>
      <td><a href="/vpc/route-tables/{_esc(r['routeTableId'])}">{_esc(r['routeTableId'])}</a></td>
      <td>{_esc(r.get('vpcId','—'))}</td>
      <td>{'Yes' if r.get('isMain') else 'No'}</td>
      <td>{len(r.get('routes') or [])}</td>
      <td>{len(r.get('associations') or [])}</td>
    </tr>""" for r in rts) or '<tr><td colspan="5" class="aws-muted" style="text-align:center; padding:24px;">No route tables.</td></tr>'

    return f"""
<section class="aws-section">
  {flash}
  <div class="s3-page-header">
    <h1>Route tables <span class="aws-muted">({len(rts)})</span></h1>
  </div>
  <table class="aws-table">
    <thead>
      <tr><th>Route table ID</th><th>VPC</th><th>Main</th><th>Routes</th><th>Associations</th></tr>
    </thead>
    <tbody>{rows}</tbody>
  </table>
</section>"""


def render_route_table_detail(rt_id, qs=None):
    r = vpc_mod.get_route_table(rt_id)
    if not r:
        return f'<div class="aws-notice aws-notice-error">Route table not found: {_esc(rt_id)}</div>'
    flash = _flash(qs)

    route_rows = "".join(f"""
    <tr>
      <td><code>{_esc(rt.get('destinationCidrBlock','—'))}</code></td>
      <td><code>{_esc(rt.get('gatewayId','—'))}</code></td>
      <td>{_esc(rt.get('state','—'))}</td>
    </tr>""" for rt in (r.get("routes") or []))

    assoc_rows = "".join(f"""
    <tr><td>{_esc(a.get('subnetId') or a.get('main') or '—')}</td>
        <td>{_esc(a.get('associationState') or a.get('state') or 'associated')}</td></tr>"""
        for a in (r.get("associations") or []))

    return f"""
<section class="aws-section">
  {flash}
  <div class="s3-page-header">
    <h1>{_esc(rt_id)} <span class="aws-muted">{'[MAIN]' if r.get('isMain') else ''}</span></h1>
    <div class="s3-page-actions">
      <a class="aws-button-secondary" href="/vpc/route-tables">&#8592; Route tables</a>
    </div>
  </div>

  <table class="aws-table" style="margin-bottom:16px;">
    <tbody>
      <tr><th style="width:30%;">Route table ID</th><td><code>{_esc(r['routeTableId'])}</code></td></tr>
      <tr><th>VPC</th><td><a href="/vpc/{_esc(r.get('vpcId',''))}">{_esc(r.get('vpcId','—'))}</a></td></tr>
      <tr><th>Region</th><td>{_esc(r.get('region','—'))}</td></tr>
      <tr><th>Main</th><td>{'Yes' if r.get('isMain') else 'No'}</td></tr>
    </tbody>
  </table>

  <h2 class="ec2-section-title">Routes</h2>
  <table class="aws-table">
    <thead><tr><th>Destination</th><th>Target</th><th>Status</th></tr></thead>
    <tbody>{route_rows or '<tr><td colspan="3" class="aws-muted">No routes.</td></tr>'}</tbody>
  </table>

  <h2 class="ec2-section-title">Subnet associations</h2>
  <table class="aws-table">
    <thead><tr><th>Subnet ID</th><th>State</th></tr></thead>
    <tbody>{assoc_rows or '<tr><td colspan="2" class="aws-muted">No explicit associations.</td></tr>'}</tbody>
  </table>
</section>"""


# ---------- IGWs ----------

def render_igws(qs=None):
    flash = _flash(qs)
    try:
        igws = vpc_mod.list_internet_gateways()
    except Exception as e:
        return f'<div class="aws-notice aws-notice-error">Error: {_esc(e)}</div>'

    rows = "".join(f"""
    <tr>
      <td><code>{_esc(i['internetGatewayId'])}</code></td>
      <td>{_esc(_name(i))}</td>
      <td>{_state_pill(i.get('state'))}</td>
      <td>{_esc(', '.join(i.get('attachments') or []) or '—')}</td>
      <td>
        <form method="POST" action="/vpc/igws/delete" style="display:inline"
              onsubmit="return confirm('Delete IGW?')">
          <input type="hidden" name="igw_id" value="{_esc(i['internetGatewayId'])}">
          <button type="submit" class="aws-link-danger">Delete</button>
        </form>
      </td>
    </tr>""" for i in igws) or '<tr><td colspan="5" class="aws-muted" style="text-align:center; padding:24px;">No internet gateways.</td></tr>'

    return f"""
<section class="aws-section">
  {flash}
  <div class="s3-page-header">
    <h1>Internet gateways <span class="aws-muted">({len(igws)})</span></h1>
    <div class="s3-page-actions">
      <a class="aws-button-primary" href="/vpc/igws/create">Create internet gateway</a>
    </div>
  </div>
  <table class="aws-table">
    <thead>
      <tr><th>IGW ID</th><th>Name</th><th>State</th><th>Attached VPC</th><th>Actions</th></tr>
    </thead>
    <tbody>{rows}</tbody>
  </table>
</section>"""


# ---------- NATs ----------

def render_nats(qs=None):
    flash = _flash(qs)
    try:
        nats = nat_mod.list_nat_gateways()
    except Exception as e:
        return f'<div class="aws-notice aws-notice-error">Error: {_esc(e)}</div>'

    rows = "".join(f"""
    <tr>
      <td><code>{_esc(n['natGatewayId'])}</code></td>
      <td>{_esc(n.get('vpcId','—'))}</td>
      <td>{_esc(n.get('subnetId','—'))}</td>
      <td>{_state_pill(n.get('state'))}</td>
      <td><code>{_esc(n.get('publicIp','—'))}</code></td>
      <td>
        <form method="POST" action="/vpc/nats/delete" style="display:inline"
              onsubmit="return confirm('Delete NAT gateway?')">
          <input type="hidden" name="nat_id" value="{_esc(n['natGatewayId'])}">
          <button type="submit" class="aws-link-danger">Delete</button>
        </form>
      </td>
    </tr>""" for n in nats) or '<tr><td colspan="6" class="aws-muted" style="text-align:center; padding:24px;">No NAT gateways.</td></tr>'

    return f"""
<section class="aws-section">
  {flash}
  <div class="s3-page-header">
    <h1>NAT gateways <span class="aws-muted">({len(nats)})</span></h1>
    <div class="s3-page-actions">
      <a class="aws-button-primary" href="/vpc/nats/create">Create NAT gateway</a>
    </div>
  </div>
  <table class="aws-table">
    <thead>
      <tr><th>NAT gateway ID</th><th>VPC</th><th>Subnet</th><th>State</th><th>Public IP</th><th>Actions</th></tr>
    </thead>
    <tbody>{rows}</tbody>
  </table>
</section>"""


# ---------- Security groups ----------

def render_sgs(qs=None):
    flash = _flash(qs)
    try:
        sgs = sg_mod.list_security_groups()
    except Exception as e:
        return f'<div class="aws-notice aws-notice-error">Error: {_esc(e)}</div>'

    rows = "".join(f"""
    <tr>
      <td><a href="/vpc/security-groups/{_esc(s['groupId'])}">{_esc(s['groupId'])}</a></td>
      <td>{_esc(s.get('groupName','—'))}</td>
      <td>{_esc(s.get('description','—'))}</td>
      <td>{_esc(s.get('vpcId','—'))}</td>
      <td>{len(s.get('ipPermissions') or [])}</td>
      <td>{len(s.get('ipPermissionsEgress') or [])}</td>
    </tr>""" for s in sgs) or '<tr><td colspan="6" class="aws-muted" style="text-align:center; padding:24px;">No security groups.</td></tr>'

    return f"""
<section class="aws-section">
  {flash}
  <div class="s3-page-header">
    <h1>Security groups <span class="aws-muted">({len(sgs)})</span></h1>
    <div class="s3-page-actions">
      <a class="aws-button-primary" href="/vpc/sgs/create">Create security group</a>
    </div>
  </div>
  <table class="aws-table">
    <thead>
      <tr><th>SG ID</th><th>Name</th><th>Description</th><th>VPC</th>
          <th>Inbound rules</th><th>Outbound rules</th></tr>
    </thead>
    <tbody>{rows}</tbody>
  </table>
</section>"""


def render_sg_detail(sg_id, qs=None):
    s = sg_mod.get_security_group(sg_id)
    if not s:
        return f'<div class="aws-notice aws-notice-error">SG not found: {_esc(sg_id)}</div>'
    flash = _flash(qs)

    def _perm_rows(perms):
        if not perms:
            return '<tr><td colspan="4" class="aws-muted">No rules.</td></tr>'
        out = []
        for p in perms:
            proto = p.get("ipProtocol", "—")
            frm = p.get("fromPort", "All")
            to = p.get("toPort", "All")
            cidrs = ", ".join(r.get("CidrIp", "—") for r in (p.get("ipRanges") or [])) or "—"
            out.append(f"<tr><td>{_esc(proto)}</td><td>{_esc(frm)}</td><td>{_esc(to)}</td><td><code>{_esc(cidrs)}</code></td></tr>")
        return "".join(out)

    inbound = _perm_rows(s.get("ipPermissions") or [])
    outbound = _perm_rows(s.get("ipPermissionsEgress") or [])

    return f"""
<section class="aws-section">
  {flash}
  <div class="s3-page-header">
    <h1>{_esc(s.get('groupName'))} <span class="aws-muted">{_esc(sg_id)}</span></h1>
    <div class="s3-page-actions">
      <a class="aws-button-secondary" href="/vpc/security-groups">&#8592; Security groups</a>
    </div>
  </div>

  <table class="aws-table" style="margin-bottom:16px;">
    <tbody>
      <tr><th style="width:30%;">Security group ID</th><td><code>{_esc(s['groupId'])}</code></td></tr>
      <tr><th>Name</th><td>{_esc(s.get('groupName'))}</td></tr>
      <tr><th>Description</th><td>{_esc(s.get('description',''))}</td></tr>
      <tr><th>VPC</th><td><a href="/vpc/{_esc(s.get('vpcId',''))}">{_esc(s.get('vpcId','—'))}</a></td></tr>
      <tr><th>Region</th><td>{_esc(s.get('region','—'))}</td></tr>
    </tbody>
  </table>

  <h2 class="ec2-section-title">Inbound rules</h2>
  <table class="aws-table">
    <thead><tr><th>Protocol</th><th>From port</th><th>To port</th><th>Source</th></tr></thead>
    <tbody>{inbound}</tbody>
  </table>

  <h2 class="ec2-section-title">Outbound rules</h2>
  <table class="aws-table">
    <thead><tr><th>Protocol</th><th>From port</th><th>To port</th><th>Destination</th></tr></thead>
    <tbody>{outbound}</tbody>
  </table>
</section>"""


# ---------- Wizards ----------

def render_create_vpc(qs=None):
    flash = _flash(qs)
    return f"""
<section class="aws-section">
  {flash}
  <div class="wizard-header">
    <h1>Create VPC</h1>
    <p class="aws-muted">Same shape as the real EC2 → Your VPCs → Create VPC wizard.</p>
  </div>
  <form id="vpc-create-form" method="POST" action="/vpc/create">
    <div class="wizard-step-tabs">
      <div class="wizard-step active" data-step="1">1. VPC settings</div>
      <div class="wizard-step" data-step="2">2. Review</div>
    </div>

    <div class="wizard-panel active" data-step="1">
      <div class="wizard-field">
        <label>Resources to create</label>
        <select disabled><option>VPC only</option></select>
      </div>
      <div class="wizard-field">
        <label for="cidr">IPv4 CIDR block</label>
        <input id="cidr" name="cidr" type="text" required
               value="10.0.0.0/16" placeholder="10.0.0.0/16">
        <p class="aws-muted wizard-hint">
          Between /16 and /24. Real AWS default: <code>10.0.0.0/16</code>.
        </p>
      </div>
      <div class="wizard-field">
        <label>Tenancy</label>
        <select disabled><option>Default</option></select>
        <p class="aws-muted wizard-hint">Simulated — MiniAWS runs Default tenancy.</p>
      </div>
      <div class="wizard-actions">
        <button type="button" class="aws-button-primary" onclick="vpcStep(2)">Next</button>
        <a class="aws-button-secondary" href="/vpc">Cancel</a>
      </div>
    </div>

    <div class="wizard-panel" data-step="2">
      <table class="aws-table" style="margin-bottom:16px;">
        <tbody>
          <tr><th style="width:35%;">CIDR block</th><td><code id="review-cidr">—</code></td></tr>
          <tr><th>Tenancy</th><td>Default (simulated)</td></tr>
          <tr><th>DNS hostnames</th><td>Enabled</td></tr>
          <tr><th>DNS resolution</th><td>Enabled</td></tr>
        </tbody>
      </table>
      <div class="wizard-actions">
        <button type="submit" class="aws-button-primary">Create VPC</button>
        <button type="button" class="aws-button-secondary" onclick="vpcStep(1)">Back</button>
      </div>
    </div>
  </form>
  <script>
    function vpcStep(n) {{
      if (n === 2) {{
        document.getElementById('review-cidr').textContent =
          document.getElementById('cidr').value;
      }}
      document.querySelectorAll('#vpc-create-form .wizard-panel').forEach(p =>
        p.classList.toggle('active', p.dataset.step == n));
      document.querySelectorAll('.wizard-step').forEach(p =>
        p.classList.toggle('active', p.dataset.step == n));
    }}
  </script>
</section>"""


def render_create_subnet(vpc_id=None, qs=None):
    flash = _flash(qs)
    vpcs = vpc_mod.list_vpcs()
    vpc_opts = "".join(
        f'<option value="{_esc(v["vpcId"])}"'
        f'{(" selected" if vpc_id == v["vpcId"] else "")}>'
        f'{_esc(v["vpcId"])} ({_esc(v.get("cidrBlock",""))})</option>'
        for v in vpcs
    )
    return f"""
<section class="aws-section">
  {flash}
  <div class="wizard-header"><h1>Create subnet</h1></div>
  <form id="subnet-create-form" method="POST" action="/vpc/subnets/create">
    <div class="wizard-panel active">
      <div class="wizard-field">
        <label for="vpc_id">VPC ID</label>
        <select id="vpc_id" name="vpc_id" required>{vpc_opts}</select>
      </div>
      <div class="wizard-field">
        <label for="cidr">IPv4 subnet CIDR block</label>
        <input id="cidr" name="cidr" type="text" required
               value="10.0.1.0/24" placeholder="10.0.1.0/24">
      </div>
      <div class="wizard-field">
        <label for="name">Subnet name (optional)</label>
        <input id="name" name="name" type="text" placeholder="public-1">
      </div>
      <div class="wizard-actions">
        <button type="submit" class="aws-button-primary">Create subnet</button>
        <a class="aws-button-secondary" href="/vpc/subnets">Cancel</a>
      </div>
    </div>
  </form>
</section>"""


def render_create_igw(qs=None):
    flash = _flash(qs)
    return f"""
<section class="aws-section">
  {flash}
  <div class="wizard-header"><h1>Create internet gateway</h1></div>
  <form method="POST" action="/vpc/igws/create">
    <div class="wizard-panel active">
      <div class="wizard-field">
        <label for="name">Name tag (optional)</label>
        <input id="name" name="name" type="text" placeholder="main-igw">
      </div>
      <div class="wizard-actions">
        <button type="submit" class="aws-button-primary">Create internet gateway</button>
        <a class="aws-button-secondary" href="/vpc/igws">Cancel</a>
      </div>
    </div>
  </form>
</section>"""


def render_create_sg(vpc_id=None, qs=None):
    flash = _flash(qs)
    vpcs = vpc_mod.list_vpcs()
    vpc_opts = "".join(
        f'<option value="{_esc(v["vpcId"])}"'
        f'{(" selected" if vpc_id == v["vpcId"] else "")}>'
        f'{_esc(v["vpcId"])} ({_esc(v.get("cidrBlock",""))})</option>'
        for v in vpcs
    )
    return f"""
<section class="aws-section">
  {flash}
  <div class="wizard-header"><h1>Create security group</h1></div>
  <form method="POST" action="/vpc/sgs/create">
    <div class="wizard-panel active">
      <div class="wizard-field">
        <label for="name">Security group name</label>
        <input id="name" name="name" type="text" required placeholder="web-tier-sg">
      </div>
      <div class="wizard-field">
        <label for="description">Description</label>
        <input id="description" name="description" type="text"
               placeholder="Allow inbound HTTP">
      </div>
      <div class="wizard-field">
        <label for="vpc_id">VPC</label>
        <select id="vpc_id" name="vpc_id" required>{vpc_opts}</select>
      </div>
      <div class="wizard-actions">
        <button type="submit" class="aws-button-primary">Create security group</button>
        <a class="aws-button-secondary" href="/vpc/security-groups">Cancel</a>
      </div>
    </div>
  </form>
</section>"""


def render_create_nat(vpc_id=None, qs=None):
    flash = _flash(qs)
    subs = vpc_mod.list_subnets()
    sub_opts = "".join(
        f'<option value="{_esc(s["subnetId"])}"'
        f'{(" selected" if vpc_id and s.get("vpcId") == vpc_id else "")}>'
        f'{_esc(s["subnetId"])} (VPC {_esc(s.get("vpcId",""))})</option>'
        for s in subs
    )
    return f"""
<section class="aws-section">
  {flash}
  <div class="wizard-header"><h1>Create NAT gateway</h1></div>
  <form method="POST" action="/vpc/nats/create">
    <div class="wizard-panel active">
      <div class="wizard-field">
        <label for="subnet_id">Subnet</label>
        <select id="subnet_id" name="subnet_id" required>{sub_opts}</select>
        <p class="aws-muted wizard-hint">
          In real AWS the subnet must be public. MiniAWS does not enforce this.
        </p>
      </div>
      <div class="wizard-actions">
        <button type="submit" class="aws-button-primary">Create NAT gateway</button>
        <a class="aws-button-secondary" href="/vpc/nats">Cancel</a>
      </div>
    </div>
  </form>
</section>"""
