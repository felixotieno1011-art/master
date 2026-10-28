"""IAM pages — dashboard, users, groups, policies, access keys, audit."""
import html
import json
from datetime import datetime

from core import iam as iam_mod
from core import account


def _esc(s):
    return html.escape(str(s))


def _human_date(iso):
    if not iso:
        return "—"
    try:
        dt = datetime.fromisoformat(str(iso).replace("Z", ""))
        return dt.strftime("%Y-%m-%d %H:%M:%S")
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


# ---------- JSON viewer with syntax tokens ----------

def _json_view(obj):
    """Pretty-print a JSON object with AWS-style syntax coloring (spans only)."""
    def _wrap(kind, text):
        return f'<span class="iam-json-{kind}">{_esc(text)}</span>'

    def _render(o, indent=0):
        pad = "  " * indent
        if isinstance(o, dict):
            if not o:
                return _wrap("punct", "{}")
            parts = []
            for k, v in o.items():
                parts.append(
                    f'{pad}  {_wrap("key", json.dumps(k))}: {_render(v, indent + 1)}'
                )
            body = ",\n".join(parts)
            return f"{_wrap('punct', '{')}\n{body}\n{pad}{_wrap('punct', '}')}"
        if isinstance(o, list):
            if not o:
                return _wrap("punct", "[]")
            parts = [f"{pad}  {_render(item, indent + 1)}" for item in o]
            body = ",\n".join(parts)
            return f"{_wrap('punct', '[')}\n{body}\n{pad}{_wrap('punct', ']')}"
        if isinstance(o, str):
            return _wrap("str", json.dumps(o))
        if isinstance(o, bool):
            return _wrap("bool", "true" if o else "false")
        if o is None:
            return _wrap("null", "null")
        return _wrap("num", json.dumps(o))

    return f'<pre class="iam-json">{_render(obj)}</pre>'


# ---------- Dashboard ----------

def render_dashboard(qs=None):
    flash = _flash(qs)
    try:
        users = iam_mod.list_users()
        groups = iam_mod.list_groups()
        policies = iam_mod.list_policies()
        current = iam_mod.get_current_user()
    except Exception as e:
        return f'<div class="aws-notice aws-notice-error">Error: {_esc(e)}</div>'

    user_count = len(users)
    mfa_adoption = "0%"

    def _tile(label, val, href, sub=""):
        return f"""
        <a class="cw-tile" href="{href}">
          <div class="cw-tile-label">{label}</div>
          <div class="cw-tile-num">{val}</div>
          <div class="cw-tile-sub">{sub}</div>
        </a>"""

    return f"""
<section class="aws-section">
  {flash}
  <div class="s3-page-header">
    <h1>IAM Dashboard</h1>
  </div>

  <h2 class="ec2-section-title">IAM resources</h2>
  <div class="cw-tiles-grid">
    {_tile("Users", user_count, "/iam/users", "individual identities")}
    {_tile("Groups", len(groups), "/iam/groups", "teams with shared policies")}
    {_tile("Policies", len(policies), "/iam/policies", "managed JSON documents")}
  </div>

  <h2 class="ec2-section-title">Account security</h2>
  <table class="aws-table">
    <tbody>
      <tr><th style="width:40%;">Current user</th>
          <td><code>{_esc(current or '(none — log in)')}</code></td></tr>
      <tr><th>Account ID</th>
          <td><code>{_esc(account.get_account_id() or '(not initialized)')}</code></td></tr>
      <tr><th>Account tags</th>
          <td>{_esc(account.get_tags() or '—')}</td></tr>
      <tr><th>MFA (simulated)</th><td>{mfa_adoption}</td></tr>
    </tbody>
  </table>
  <p class="aws-muted s3-footer-hint">
    Note: MiniAWS tracks identity via <code>aws iam login &lt;user&gt;</code>.
    Real AWS uses signing credentials on each API call.
  </p>
</section>"""


# ---------- Users ----------

def render_users(qs=None):
    flash = _flash(qs)
    try:
        users = iam_mod.list_users()
    except Exception as e:
        return f'<div class="aws-notice aws-notice-error">Error: {_esc(e)}</div>'

    rows = "".join(f"""
    <tr>
      <td><a href="/iam/users/{_esc(u['userName'])}">{_esc(u['userName'])}</a></td>
      <td><code>{_esc(u.get('path','/'))}</code></td>
      <td>{_esc(_human_date(u.get('created')))}</td>
      <td>{len(u.get('attachedPolicies') or [])}</td>
      <td>{len(u.get('groups') or [])}</td>
    </tr>""" for u in users) or \
        '<tr><td colspan="5" class="aws-muted" style="text-align:center; padding:24px;">No users. Click <em>Create user</em>.</td></tr>'

    return f"""
<section class="aws-section">
  {flash}
  <div class="s3-page-header">
    <h1>Users <span class="aws-muted">({len(users)})</span></h1>
    <div class="s3-page-actions">
      <a class="aws-button-primary" href="/iam/users/create">Create user</a>
    </div>
  </div>
  <table class="aws-table">
    <thead>
      <tr><th>User name</th><th>Path</th><th>Creation time</th>
          <th>Policies</th><th>Groups</th></tr>
    </thead>
    <tbody>{rows}</tbody>
  </table>
</section>"""


def render_user_detail(name, tab="permissions", qs=None):
    u = iam_mod.get_user(name)
    if not u:
        return f'<div class="aws-notice aws-notice-error">User not found: {_esc(name)}</div>'

    flash = _flash(qs)
    tabs = [
        ("permissions", "Permissions"),
        ("groups", "Groups"),
        ("tags", "Tags"),
        ("security", "Security credentials"),
        ("accessadvisor", "Access Advisor"),
    ]
    tab_html = "".join(
        f'<a class="s3-tab {"active" if tid == tab else ""}" '
        f'href="/iam/users/{_esc(name)}{"" if tid == "permissions" else "?tab=" + tid}">{label}</a>'
        for tid, label in tabs
    )

    if tab == "permissions":
        attached = u.get("attachedPolicies") or []
        rows = "".join(f"""
        <tr>
          <td><a href="/iam/policies/{_esc(p)}"><code>{_esc(p)}</code></a></td>
          <td>AWS managed</td>
          <td>
            <form method="POST" action="/iam/users/detach-policy" style="display:inline"
                  onsubmit="return confirm('Detach {_esc(p)} from {_esc(name)}?')">
              <input type="hidden" name="username" value="{_esc(name)}">
              <input type="hidden" name="policy" value="{_esc(p)}">
              <button type="submit" class="aws-link-danger">Detach</button>
            </form>
          </td>
        </tr>""" for p in attached) or \
            '<tr><td colspan="3" class="aws-muted">No policies attached.</td></tr>'

        attach_form = f"""
<form method="POST" action="/iam/users/attach-policy" class="wizard-field"
      style="margin-top:16px; max-width:500px;">
  <input type="hidden" name="username" value="{_esc(name)}">
  <label for="policy">Attach policy</label>
  <select id="policy" name="policy">
    {_policy_options(attached)}
  </select>
  <button type="submit" class="aws-button-secondary" style="margin-top:8px;">
    Attach policy
  </button>
</form>"""

        content = f"""
<h2 class="ec2-section-title">Permissions policies</h2>
<table class="aws-table">
  <thead><tr><th>Policy name</th><th>Type</th><th>Actions</th></tr></thead>
  <tbody>{rows}</tbody>
</table>
{attach_form}
"""
    elif tab == "groups":
        groups = u.get("groups") or []
        if groups:
            rows = "".join(
                f'<tr><td><a href="/iam/groups/{_esc(g)}">{_esc(g)}</a></td></tr>'
                for g in groups
            )
            content = f'<table class="aws-table"><tbody>{rows}</tbody></table>'
        else:
            content = '<p class="aws-muted">Not a member of any group.</p>'
    elif tab == "tags":
        tags = u.get("tags") or {}
        tag_rows = "".join(f"<tr><td>{_esc(k)}</td><td>{_esc(v)}</td></tr>"
                           for k, v in sorted(tags.items())) or \
                   '<tr><td colspan="2" class="aws-muted">No tags</td></tr>'
        content = f"""
<table class="aws-table">
  <thead><tr><th>Key</th><th>Value</th></tr></thead>
  <tbody>{tag_rows}</tbody>
</table>"""
    elif tab == "security":
        try:
            keys_doc = iam_mod.list_access_keys(name)
            keys = keys_doc if isinstance(keys_doc, list) else \
                   (keys_doc.get("keys") if isinstance(keys_doc, dict) else [])
        except Exception:
            keys = []
        key_rows = "".join(f"""
        <tr>
          <td><code>{_esc(k.get('accessKeyId','—'))}</code></td>
          <td>{_esc(k.get('status', 'Active'))}</td>
          <td>{_esc(_human_date(k.get('created', '')))}</td>
          <td>
            <form method="POST" action="/iam/users/delete-access-key" style="display:inline"
                  onsubmit="return confirm('Delete this access key?')">
              <input type="hidden" name="username" value="{_esc(name)}">
              <input type="hidden" name="access_key" value="{_esc(k.get('accessKeyId',''))}">
              <button type="submit" class="aws-link-danger">Delete</button>
            </form>
          </td>
        </tr>""" for k in keys) or \
            '<tr><td colspan="4" class="aws-muted">No access keys.</td></tr>'
        content = f"""
<div class="aws-notice aws-notice-warn">
  <strong>Real AWS note:</strong> Access keys grant programmatic access and
  should be rotated frequently. In MiniAWS they are simulated.
</div>
<div class="s3-page-header" style="margin-bottom:8px;">
  <h2 class="ec2-section-title" style="margin:0;">Access keys ({len(keys)})</h2>
  <form method="POST" action="/iam/users/create-access-key" style="display:inline">
    <input type="hidden" name="username" value="{_esc(name)}">
    <button type="submit" class="aws-button-primary">Create access key</button>
  </form>
</div>
<table class="aws-table">
  <thead><tr><th>Access key ID</th><th>Status</th><th>Created</th><th>Actions</th></tr></thead>
  <tbody>{key_rows}</tbody>
</table>
"""
    else:  # access advisor
        content = ('<p class="aws-muted">Access Advisor shows last-accessed services per policy. '
                   'Real AWS renders this from CloudTrail. MiniAWS does not track it.</p>')

    return f"""
<section class="aws-section">
  {flash}
  <div class="s3-page-header">
    <h1>{_esc(name)}</h1>
    <div class="s3-page-actions">
      <a class="aws-button-secondary" href="/iam/users">&#8592; Users</a>
      <form method="POST" action="/iam/users/delete" style="display:inline"
            onsubmit="return confirm('Delete user {_esc(name)}?')">
        <input type="hidden" name="username" value="{_esc(name)}">
        <button type="submit" class="aws-button-danger">Delete user</button>
      </form>
    </div>
  </div>

  <table class="aws-table" style="margin-bottom:16px;">
    <tbody>
      <tr><th style="width:30%;">User name</th><td><code>{_esc(u['userName'])}</code></td></tr>
      <tr><th>ARN</th><td><code>{_esc(u.get('arn','—'))}</code></td></tr>
      <tr><th>User ID</th><td><code>{_esc(u.get('userId','—'))}</code></td></tr>
      <tr><th>Path</th><td><code>{_esc(u.get('path','/'))}</code></td></tr>
      <tr><th>Created</th><td>{_esc(_human_date(u.get('created')))}</td></tr>
    </tbody>
  </table>

  <nav class="s3-tabs">{tab_html}</nav>
  {content}
</section>"""


def _policy_options(exclude=None):
    exclude = set(exclude or [])
    opts = []
    for p in iam_mod.list_policies():
        name = p.get("policyName") or p.get("name")
        if name and name not in exclude:
            opts.append(f'<option value="{_esc(name)}">{_esc(name)}</option>')
    return "".join(opts) or '<option value="">(no policies available)</option>'


# ---------- Groups ----------

def render_groups(qs=None):
    flash = _flash(qs)
    try:
        groups = iam_mod.list_groups()
    except Exception as e:
        return f'<div class="aws-notice aws-notice-error">Error: {_esc(e)}</div>'

    rows = "".join(f"""
    <tr>
      <td><a href="/iam/groups/{_esc(g.get('groupName', g.get('name','')))}">
        {_esc(g.get('groupName', g.get('name','')))}</a></td>
      <td>{_esc(_human_date(g.get('created')))}</td>
      <td>{len(g.get('attachedPolicies') or [])}</td>
    </tr>""" for g in groups) or \
        '<tr><td colspan="3" class="aws-muted" style="text-align:center; padding:24px;">No groups.</td></tr>'

    return f"""
<section class="aws-section">
  {flash}
  <div class="s3-page-header">
    <h1>Groups <span class="aws-muted">({len(groups)})</span></h1>
    <div class="s3-page-actions">
      <a class="aws-button-primary" href="/iam/groups/create">Create group</a>
    </div>
  </div>
  <table class="aws-table">
    <thead><tr><th>Group name</th><th>Created</th><th>Policies</th></tr></thead>
    <tbody>{rows}</tbody>
  </table>
</section>"""


def render_group_detail(name, qs=None):
    g = iam_mod.get_group(name)
    if not g:
        return f'<div class="aws-notice aws-notice-error">Group not found: {_esc(name)}</div>'
    flash = _flash(qs)
    members = g.get("members") or g.get("users") or []
    attached = g.get("attachedPolicies") or []
    member_rows = "".join(
        f'<tr><td><a href="/iam/users/{_esc(m)}">{_esc(m)}</a></td></tr>'
        for m in members
    ) or '<tr><td class="aws-muted">No members.</td></tr>'
    policy_rows = "".join(
        f'<tr><td><a href="/iam/policies/{_esc(p)}"><code>{_esc(p)}</code></a></td></tr>'
        for p in attached
    ) or '<tr><td class="aws-muted">No policies attached.</td></tr>'

    return f"""
<section class="aws-section">
  {flash}
  <div class="s3-page-header">
    <h1>{_esc(name)}</h1>
    <div class="s3-page-actions">
      <a class="aws-button-secondary" href="/iam/groups">&#8592; Groups</a>
    </div>
  </div>
  <table class="aws-table" style="margin-bottom:16px;">
    <tbody>
      <tr><th style="width:30%;">Group name</th><td><code>{_esc(name)}</code></td></tr>
      <tr><th>ARN</th><td><code>{_esc(g.get('arn','—'))}</code></td></tr>
      <tr><th>Created</th><td>{_esc(_human_date(g.get('created')))}</td></tr>
    </tbody>
  </table>
  <h2 class="ec2-section-title">Members ({len(members)})</h2>
  <table class="aws-table"><tbody>{member_rows}</tbody></table>
  <h2 class="ec2-section-title">Attached policies ({len(attached)})</h2>
  <table class="aws-table"><tbody>{policy_rows}</tbody></table>
</section>"""


# ---------- Policies ----------

def render_policies(qs=None):
    flash = _flash(qs)
    try:
        policies = iam_mod.list_policies()
    except Exception as e:
        return f'<div class="aws-notice aws-notice-error">Error: {_esc(e)}</div>'

    rows = "".join(f"""
    <tr>
      <td><a href="/iam/policies/{_esc(p['policyName'])}">{_esc(p['policyName'])}</a></td>
      <td>AWS managed</td>
      <td><code>{_esc(p.get('arn','—'))}</code></td>
      <td>{len(p.get('document', {}).get('Statement', []) or [])}</td>
    </tr>""" for p in policies) or \
        '<tr><td colspan="4" class="aws-muted" style="text-align:center; padding:24px;">No policies.</td></tr>'

    return f"""
<section class="aws-section">
  {flash}
  <div class="s3-page-header">
    <h1>Policies <span class="aws-muted">({len(policies)})</span></h1>
    <div class="s3-page-actions">
      <a class="aws-button-primary" href="/iam/policies/create">Create policy</a>
    </div>
  </div>
  <table class="aws-table">
    <thead><tr><th>Policy name</th><th>Type</th><th>ARN</th><th>Statements</th></tr></thead>
    <tbody>{rows}</tbody>
  </table>
</section>"""


def render_policy_detail(name, qs=None):
    p = iam_mod.get_policy(name)
    if not p:
        return f'<div class="aws-notice aws-notice-error">Policy not found: {_esc(name)}</div>'
    flash = _flash(qs)
    doc = p.get("document") or {}
    doc_html = _json_view(doc)
    stmts = doc.get("Statement") or []
    stmt_count = len(stmts) if isinstance(stmts, list) else 1

    return f"""
<section class="aws-section">
  {flash}
  <div class="s3-page-header">
    <h1>{_esc(name)}</h1>
    <div class="s3-page-actions">
      <a class="aws-button-secondary" href="/iam/policies">&#8592; Policies</a>
      <form method="POST" action="/iam/policies/delete" style="display:inline"
            onsubmit="return confirm('Delete policy {_esc(name)}?')">
        <input type="hidden" name="policy" value="{_esc(name)}">
        <button type="submit" class="aws-button-danger">Delete policy</button>
      </form>
    </div>
  </div>

  <table class="aws-table" style="margin-bottom:16px;">
    <tbody>
      <tr><th style="width:30%;">Policy name</th><td><code>{_esc(p['policyName'])}</code></td></tr>
      <tr><th>ARN</th><td><code>{_esc(p.get('arn','—'))}</code></td></tr>
      <tr><th>Statements</th><td>{stmt_count}</td></tr>
      <tr><th>Created</th><td>{_esc(_human_date(p.get('created')))}</td></tr>
    </tbody>
  </table>

  <h2 class="ec2-section-title">Policy document</h2>
  {doc_html}
</section>"""


# ---------- Access keys overview + audit log ----------

def render_access_keys(qs=None):
    flash = _flash(qs)
    users = iam_mod.list_users()
    rows = []
    for u in users:
        name = u.get("userName")
        try:
            ks = iam_mod.list_access_keys(name)
            keys = ks if isinstance(ks, list) else (ks.get("keys") if isinstance(ks, dict) else [])
        except Exception:
            keys = []
        for k in keys:
            rows.append(f"""
            <tr>
              <td><a href="/iam/users/{_esc(name)}?tab=security">{_esc(name)}</a></td>
              <td><code>{_esc(k.get('accessKeyId','—'))}</code></td>
              <td>{_esc(k.get('status','Active'))}</td>
              <td>{_esc(_human_date(k.get('created','')))}</td>
            </tr>""")

    body = "".join(rows) or \
        '<tr><td colspan="4" class="aws-muted" style="text-align:center; padding:24px;">No access keys.</td></tr>'

    return f"""
<section class="aws-section">
  {flash}
  <div class="s3-page-header">
    <h1>Access keys <span class="aws-muted">({len(rows)})</span></h1>
  </div>
  <table class="aws-table">
    <thead><tr><th>User</th><th>Access key ID</th><th>Status</th><th>Created</th></tr></thead>
    <tbody>{body}</tbody>
  </table>
</section>"""


def render_audit(qs=None):
    flash = _flash(qs)
    try:
        raw = iam_mod.read_audit(limit=200)
    except Exception as e:
        return f'<div class="aws-notice aws-notice-error">Error: {_esc(e)}</div>'

    # `read_audit` returns either a list of dicts (structured) or list of strings
    # (raw audit.log lines). Handle both.
    events = raw if isinstance(raw, list) else []

    def _row(ev):
        if isinstance(ev, dict):
            ts = ev.get("timestamp", "—")
            user = ev.get("user", "—")
            action = ev.get("action", "—")
            detail = ev.get("detail", "—")
            okmark = "\u2705" if ev.get("success", True) else "\u274c"
            return (
                f'<tr>'
                f'<td style="white-space:nowrap;">{_esc(ts)}</td>'
                f'<td><code>{_esc(user)}</code></td>'
                f'<td>{_esc(action)}</td>'
                f'<td>{_esc(detail)}</td>'
                f'<td>{okmark}</td>'
                f'</tr>'
            )
        # Raw line
        return (
            f'<tr><td colspan="5" style="font-family:monospace; font-size:12px; '
            f'word-break:break-all;">{_esc(ev)}</td></tr>'
        )

    if events:
        rows = "".join(_row(ev) for ev in events)
    else:
        rows = '<tr><td colspan="5" class="aws-muted" style="text-align:center; padding:24px;">No audit events.</td></tr>'

    return f"""
<section class="aws-section">
  {flash}
  <div class="s3-page-header">
    <h1>Audit log <span class="aws-muted">({len(events)} events)</span></h1>
  </div>
  <p class="aws-muted">Every IAM action is recorded in <code>state/iam/audit.log</code>.</p>
  <table class="aws-table">
    <thead><tr><th>Event</th></tr></thead>
    <tbody>{rows}</tbody>
  </table>
</section>"""


def render_create_user(qs=None):
    flash = _flash(qs)
    policies = iam_mod.list_policies()
    policy_checks = "".join(f"""
    <label class="iam-checkbox">
      <input type="checkbox" name="policies" value="{_esc(p['policyName'])}">
      <span><code>{_esc(p['policyName'])}</code></span>
    </label>""" for p in policies) or \
        '<p class="aws-muted">No policies available.</p>'

    return f"""
<section class="aws-section">
  {flash}
  <div class="wizard-header">
    <h1>Create user</h1>
    <p class="aws-muted">Same 2-step shape as real IAM → Users → Create user.</p>
  </div>
  <form id="user-form" method="POST" action="/iam/users/create">
    <div class="wizard-step-tabs">
      <div class="wizard-step active" data-step="1">1. User details</div>
      <div class="wizard-step" data-step="2">2. Set permissions</div>
    </div>

    <div class="wizard-panel active" data-step="1">
      <div class="wizard-field">
        <label for="username">User name</label>
        <input id="username" name="username" type="text" required
               placeholder="alice" pattern="[a-zA-Z0-9][a-zA-Z0-9._\\-]{{0,63}}">
      </div>
      <div class="wizard-field">
        <label>Provide user access to the AWS Management Console</label>
        <select disabled><option>Not supported in MiniAWS (login via CLI)</option></select>
      </div>
      <div class="wizard-actions">
        <button type="button" class="aws-button-primary" onclick="iamUserStep(2)">Next</button>
        <a class="aws-button-secondary" href="/iam/users">Cancel</a>
      </div>
    </div>

    <div class="wizard-panel" data-step="2">
      <div class="wizard-field">
        <label>Set permissions (optional)</label>
        <p class="aws-muted wizard-hint">Attach policies directly. Real AWS suggests groups first.</p>
        <div class="iam-checkbox-list">{policy_checks}</div>
      </div>
      <div class="wizard-actions">
        <button type="submit" class="aws-button-primary">Create user</button>
        <button type="button" class="aws-button-secondary" onclick="iamUserStep(1)">Back</button>
      </div>
    </div>
  </form>
  <script>
    function iamUserStep(n) {{
      if (n === 2 && !document.getElementById('username').value) {{
        document.getElementById('username').focus(); return;
      }}
      document.querySelectorAll('#user-form .wizard-panel').forEach(p =>
        p.classList.toggle('active', p.dataset.step == n));
      document.querySelectorAll('.wizard-step').forEach(p =>
        p.classList.toggle('active', p.dataset.step == n));
    }}
  </script>
</section>"""


def render_create_policy(qs=None):
    flash = _flash(qs)
    sample = json.dumps({
        "Version": "2012-10-17",
        "Statement": [
            {"Effect": "Allow", "Action": "s3:GetObject", "Resource": "*"}
        ]
    }, indent=2)
    return f"""
<section class="aws-section">
  {flash}
  <div class="wizard-header">
    <h1>Create policy</h1>
    <p class="aws-muted">Real IAM uses a visual editor + JSON editor. MiniAWS uses the JSON editor.</p>
  </div>
  <form method="POST" action="/iam/policies/create">
    <div class="wizard-panel active">
      <div class="wizard-field">
        <label for="name">Policy name</label>
        <input id="name" name="name" type="text" required
               placeholder="MyCustomPolicy"
               pattern="[a-zA-Z0-9][a-zA-Z0-9._\\-]{{0,127}}">
      </div>
      <div class="wizard-field">
        <label for="document">Policy document (JSON)</label>
        <textarea id="document" name="document" rows="14" required
                  style="width:100%; font-family:monospace; font-size:13px;
                         padding:10px; border:1px solid #d5dbdb; border-radius:3px;">{sample}</textarea>
        <p class="aws-muted wizard-hint">
          Must include <code>Version</code> and <code>Statement[]</code>. Each statement
          requires <code>Effect</code> (<code>Allow</code>/<code>Deny</code>), <code>Action</code>, and <code>Resource</code>.
        </p>
      </div>
      <div class="wizard-actions">
        <button type="submit" class="aws-button-primary">Create policy</button>
        <a class="aws-button-secondary" href="/iam/policies">Cancel</a>
      </div>
    </div>
  </form>
</section>"""


def render_create_group(qs=None):
    flash = _flash(qs)
    return f"""
<section class="aws-section">
  {flash}
  <div class="wizard-header"><h1>Create group</h1></div>
  <form method="POST" action="/iam/groups/create">
    <div class="wizard-panel active">
      <div class="wizard-field">
        <label for="name">Group name</label>
        <input id="name" name="name" type="text" required
               placeholder="Developers"
               pattern="[a-zA-Z0-9][a-zA-Z0-9._\\-]{{0,127}}">
      </div>
      <div class="wizard-actions">
        <button type="submit" class="aws-button-primary">Create group</button>
        <a class="aws-button-secondary" href="/iam/groups">Cancel</a>
      </div>
    </div>
  </form>
</section>"""
