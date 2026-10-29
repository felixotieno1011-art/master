"""IAM Roles pages — list, detail (5 tabs), create wizard (4 steps)."""
import html
import json

from core import iam as iam_mod
from core.webui import iam_roles as roles_mod


def _esc(s):
    return html.escape(str(s))


def _flash(qs):
    okv = (qs or {}).get("ok") or []
    erv = (qs or {}).get("error") or []
    if okv:
        return f'<div class="aws-notice aws-notice-success">{html.escape(str(okv[0]))}</div>'
    if erv:
        return f'<div class="aws-notice aws-notice-error">{html.escape(str(erv[0]))}</div>'
    return ""


def _json_view(obj):
    """Same syntax-highlighted JSON renderer used elsewhere."""
    def _wrap(kind, text):
        return f'<span class="iam-json-{kind}">{_esc(text)}</span>'

    def _render(o, indent=0):
        pad = "  " * indent
        if isinstance(o, dict):
            if not o:
                return _wrap("punct", "{}")
            parts = [
                f'{pad}  {_wrap("key", json.dumps(k))}: {_render(v, indent + 1)}'
                for k, v in o.items()
            ]
            return f"{_wrap('punct', '{')}\n" + ",\n".join(parts) + f"\n{pad}{_wrap('punct', '}')}"
        if isinstance(o, list):
            if not o:
                return _wrap("punct", "[]")
            parts = [f"{pad}  {_render(item, indent + 1)}" for item in o]
            return f"{_wrap('punct', '[')}\n" + ",\n".join(parts) + f"\n{pad}{_wrap('punct', ']')}"
        if isinstance(o, str):
            return _wrap("str", json.dumps(o))
        if isinstance(o, bool):
            return _wrap("bool", "true" if o else "false")
        if o is None:
            return _wrap("null", "null")
        return _wrap("num", json.dumps(o))

    return f'<pre class="iam-json">{_render(obj)}</pre>'


# ---------- Roles list ----------

def render_roles(qs=None):
    flash = _flash(qs)
    roles = roles_mod.list_roles()

    if not roles:
        return f"""
<section class="aws-section">
  {flash}
  <div class="s3-page-header">
    <h1>Roles <span class="aws-muted">(0)</span></h1>
    <div class="s3-page-actions">
      <a class="aws-button-primary" href="/iam/roles/create">Create role</a>
    </div>
  </div>
  <div class="s3-empty">
    <p class="aws-muted">No roles yet. Click <strong>Create role</strong> to start.</p>
  </div>
</section>"""

    rows = "".join(f"""
    <tr>
      <td><a href="/iam/roles/{_esc(r['roleName'])}">{_esc(r['roleName'])}</a></td>
      <td><code>{_esc(r.get('trusted_principal','—'))}</code></td>
      <td>{len(r.get('attachedPolicies') or [])}</td>
      <td>{_esc(r.get('created','—'))}</td>
    </tr>""" for r in roles)

    return f"""
<section class="aws-section">
  {flash}
  <div class="s3-page-header">
    <h1>Roles <span class="aws-muted">({len(roles)})</span></h1>
    <div class="s3-page-actions">
      <a class="aws-button-primary" href="/iam/roles/create">Create role</a>
    </div>
  </div>
  <table class="aws-table">
    <thead>
      <tr><th>Role name</th><th>Trusted entity</th>
          <th>Attached policies</th><th>Created</th></tr>
    </thead>
    <tbody>{rows}</tbody>
  </table>
</section>"""


# ---------- Role detail ----------

def render_role_detail(name, tab="permissions", qs=None):
    r = roles_mod.get_role(name)
    if not r:
        return f'<div class="aws-notice aws-notice-error">Role not found: {_esc(name)}</div>'

    flash = _flash(qs)

    tabs = [
        ("permissions", "Permissions"),
        ("trust", "Trust relationships"),
        ("tags", "Tags"),
        ("activity", "Last activity"),
    ]
    tab_html = "".join(
        f'<a class="s3-tab {"active" if tid == tab else ""}" '
        f'href="/iam/roles/{_esc(name)}{"" if tid == "permissions" else "?tab=" + tid}">{label}</a>'
        for tid, label in tabs
    )

    if tab == "permissions":
        content = _tab_permissions(r, name, qs or {})
    elif tab == "trust":
        content = _tab_trust(r)
    elif tab == "tags":
        content = _tab_tags(r)
    else:
        content = ('<p class="aws-muted">Last activity requires IAM Access Analyzer '
                   '(not simulated). Real AWS shows when this role was last used '
                   'and by which principal.</p>')

    return f"""
<section class="aws-section">
  {flash}
  <div class="s3-page-header">
    <h1>{_esc(name)}</h1>
    <div class="s3-page-actions">
      <a class="aws-button-secondary" href="/iam/roles">&#8592; Roles</a>
      <form method="POST" action="/iam/roles/delete" style="display:inline"
            onsubmit="return confirm('Delete role {_esc(name)}?')">
        <input type="hidden" name="name" value="{_esc(name)}">
        <button type="submit" class="aws-button-danger">Delete role</button>
      </form>
    </div>
  </div>

  <table class="aws-table" style="margin-bottom:16px;">
    <tbody>
      <tr><th style="width:30%;">Role name</th><td><code>{_esc(r['roleName'])}</code></td></tr>
      <tr><th>ARN</th><td><code>{_esc(r.get('arn','—'))}</code></td></tr>
      <tr><th>Role ID</th><td><code>{_esc(r.get('roleId','—'))}</code></td></tr>
      <tr><th>Description</th><td>{_esc(r.get('description',''))}</td></tr>
      <tr><th>Trusted entity</th><td><code>{_esc(r.get('trusted_principal','—'))}</code></td></tr>
      <tr><th>Created</th><td>{_esc(r.get('created','—'))}</td></tr>
    </tbody>
  </table>

  <nav class="s3-tabs">{tab_html}</nav>
  {content}
</section>"""


def _tab_permissions(r, name, qs):
    attached = r.get("attachedPolicies") or []
    rows = "".join(f"""
    <tr>
      <td><a href="/iam/policies/{_esc(p)}"><code>{_esc(p)}</code></a></td>
      <td>AWS managed</td>
      <td>
        <form method="POST" action="/iam/roles/detach-policy" style="display:inline"
              onsubmit="return confirm('Detach {_esc(p)}?')">
          <input type="hidden" name="role" value="{_esc(name)}">
          <input type="hidden" name="policy" value="{_esc(p)}">
          <button type="submit" class="aws-link-danger">Detach</button>
        </form>
      </td>
    </tr>""" for p in attached) or \
        '<tr><td colspan="3" class="aws-muted">No policies attached.</td></tr>'

    # Attach form
    try:
        all_policies = [p.get("policyName") for p in iam_mod.list_policies()]
    except Exception:
        all_policies = []
    available = [p for p in all_policies if p and p not in attached]
    opts = "".join(f'<option value="{_esc(p)}">{_esc(p)}</option>' for p in available) or \
           '<option value="">(no policies available)</option>'

    attach_form = f"""
<form method="POST" action="/iam/roles/attach-policy" class="wizard-field"
      style="margin-top:16px; max-width:500px;">
  <input type="hidden" name="role" value="{_esc(name)}">
  <label for="policy">Attach policy</label>
  <select id="policy" name="policy">{opts}</select>
  <button type="submit" class="aws-button-secondary" style="margin-top:8px;">
    Attach policy
  </button>
</form>"""

    return f"""
<h2 class="ec2-section-title">Permissions policies</h2>
<table class="aws-table">
  <thead><tr><th>Policy name</th><th>Type</th><th>Actions</th></tr></thead>
  <tbody>{rows}</tbody>
</table>
{attach_form}"""


def _tab_trust(r):
    trust = r.get("assumeRolePolicyDocument") or {}
    translated = roles_mod.translate_trust_policy(trust)
    json_html = _json_view(trust)

    who_html = ""
    if translated:
        items = []
        for stmt in translated:
            for who in stmt["who"]:
                items.append(f"<li>{_esc(who)} <span class='aws-muted'>via {_esc(stmt['via'])}</span></li>")
        who_html = f"""
<div class="iam-trust-summary">
  <div class="iam-trust-title">Who can assume this role</div>
  <ul class="iam-trust-list">{"".join(items)}</ul>
</div>"""

    return f"""
<div class="aws-notice aws-notice-info">
  <strong>Trust policy</strong> — the JSON that tells AWS who is allowed to
  <em>assume</em> this role. This is the single most important field of a role.
  Below is the JSON and its plain-English translation.
</div>

{who_html}

<h2 class="ec2-section-title">Trust policy JSON</h2>
{json_html}"""


def _tab_tags(r):
    tags = r.get("tags") or {}
    tag_rows = "".join(f"<tr><td>{_esc(k)}</td><td>{_esc(v)}</td></tr>"
                       for k, v in sorted(tags.items())) or \
               '<tr><td colspan="2" class="aws-muted">No tags</td></tr>'
    return f"""
<h2 class="ec2-section-title">Tags</h2>
<table class="aws-table">
  <thead><tr><th>Key</th><th>Value</th></tr></thead>
  <tbody>{tag_rows}</tbody>
</table>"""


# ---------- Create role wizard ----------

def render_create_role(qs=None):
    flash = _flash(qs)

    # Policy checkboxes
    try:
        all_policies = [p.get("policyName") for p in iam_mod.list_policies()]
    except Exception:
        all_policies = []
    policy_checks = "".join(f"""
    <label class="iam-checkbox">
      <input type="checkbox" name="policies" value="{_esc(p)}">
      <span><code>{_esc(p)}</code></span>
    </label>""" for p in all_policies if p) or \
        '<p class="aws-muted">No policies available.</p>'

    return f"""
<section class="aws-section">
  {flash}
  <div class="wizard-header">
    <h1>Create role</h1>
    <p class="aws-muted">
      Same 4-step shape as real IAM → Roles → Create role.
    </p>
  </div>
  <form id="role-create-form" method="POST" action="/iam/roles/create">
    <div class="wizard-step-tabs">
      <div class="wizard-step active" data-step="1">1. Trusted entity</div>
      <div class="wizard-step" data-step="2">2. Principal</div>
      <div class="wizard-step" data-step="3">3. Add permissions</div>
      <div class="wizard-step" data-step="4">4. Name &amp; review</div>
    </div>

    <!-- Step 1: Choose entity type -->
    <div class="wizard-panel active" data-step="1">
      <div class="wizard-field">
        <label>Trusted entity type</label>
        <p class="aws-muted wizard-hint">Who will assume this role?</p>
        <div class="iam-entity-grid">
          <label class="iam-entity-card">
            <input type="radio" name="entity_type" value="service" checked
                   onchange="roleUpdateStep2()">
            <div>
              <div class="iam-entity-title">AWS service</div>
              <div class="iam-entity-desc">EC2, Lambda, ECS, etc.</div>
            </div>
          </label>
          <label class="iam-entity-card">
            <input type="radio" name="entity_type" value="account"
                   onchange="roleUpdateStep2()">
            <div>
              <div class="iam-entity-title">AWS account</div>
              <div class="iam-entity-desc">Cross-account access</div>
            </div>
          </label>
          <label class="iam-entity-card">
            <input type="radio" name="entity_type" value="web_identity"
                   onchange="roleUpdateStep2()">
            <div>
              <div class="iam-entity-title">Web identity</div>
              <div class="iam-entity-desc">OIDC (Cognito, Google, etc.)</div>
            </div>
          </label>
          <label class="iam-entity-card">
            <input type="radio" name="entity_type" value="saml"
                   onchange="roleUpdateStep2()">
            <div>
              <div class="iam-entity-title">SAML 2.0</div>
              <div class="iam-entity-desc">Enterprise SSO</div>
            </div>
          </label>
        </div>
      </div>
      <div class="wizard-actions">
        <button type="button" class="aws-button-primary" onclick="roleStep(2)">Next</button>
        <a class="aws-button-secondary" href="/iam/roles">Cancel</a>
      </div>
    </div>

    <!-- Step 2: Principal (per entity type) -->
    <div class="wizard-panel" data-step="2">
      <div id="principal-service" class="principal-block">
        <div class="wizard-field">
          <label for="principal-service-select">AWS service</label>
          <select id="principal-service-select" name="principal_service" onchange="roleUpdatePreview()">
            <option value="ec2.amazonaws.com">EC2</option>
            <option value="lambda.amazonaws.com">Lambda</option>
            <option value="ecs-tasks.amazonaws.com">ECS tasks</option>
            <option value="rds.amazonaws.com">RDS</option>
            <option value="glue.amazonaws.com">Glue</option>
            <option value="sagemaker.amazonaws.com">SageMaker</option>
            <option value="batch.amazonaws.com">Batch</option>
            <option value="cloudformation.amazonaws.com">CloudFormation</option>
            <option value="elasticbeanstalk.amazonaws.com">Elastic Beanstalk</option>
          </select>
        </div>
      </div>

      <div id="principal-account" class="principal-block" style="display:none;">
        <div class="wizard-field">
          <label for="principal-account-input">AWS account ID</label>
          <input id="principal-account-input" name="principal_account" type="text"
                 placeholder="123456789012" pattern="[0-9]{12}">
          <p class="aws-muted wizard-hint">12-digit AWS account ID.</p>
        </div>
      </div>

      <div id="principal-web_identity" class="principal-block" style="display:none;">
        <div class="wizard-field">
          <label for="principal-web-input">Web identity provider</label>
          <input id="principal-web-input" name="principal_web"
                 type="text" placeholder="accounts.google.com">
          <p class="aws-muted wizard-hint">OIDC provider URL or ARN.</p>
        </div>
      </div>

      <div id="principal-saml" class="principal-block" style="display:none;">
        <div class="wizard-field">
          <label for="principal-saml-input">SAML provider ARN</label>
          <input id="principal-saml-input" name="principal_saml"
                 type="text" placeholder="arn:aws:iam::123456789012:saml-provider/Okta">
        </div>
      </div>

      <div class="wizard-actions">
        <button type="button" class="aws-button-primary" onclick="roleStep(3)">Next</button>
        <button type="button" class="aws-button-secondary" onclick="roleStep(1)">Back</button>
      </div>
    </div>

    <!-- Step 3: Add permissions -->
    <div class="wizard-panel" data-step="3">
      <div class="wizard-field">
        <label>Attach policies (optional)</label>
        <p class="aws-muted wizard-hint">
          Real AWS shows 1,000+ managed policies here.
          MiniAWS lists whatever is in <code>state/iam/policies/</code>.
        </p>
        <div class="iam-checkbox-list">{policy_checks}</div>
      </div>
      <div class="wizard-actions">
        <button type="button" class="aws-button-primary" onclick="roleStep(4)">Next</button>
        <button type="button" class="aws-button-secondary" onclick="roleStep(2)">Back</button>
      </div>
    </div>

    <!-- Step 4: Name & review -->
    <div class="wizard-panel" data-step="4">
      <div class="wizard-field">
        <label for="role_name">Role name</label>
        <input id="role_name" name="name" type="text" required
               placeholder="MyEC2Role"
               pattern="[a-zA-Z0-9][a-zA-Z0-9_+=,.@\\-]{{1,63}}">
      </div>
      <div class="wizard-field">
        <label for="description">Description (optional)</label>
        <input id="description" name="description" type="text"
               placeholder="Allows EC2 instances to call AWS services">
      </div>

      <h3 class="ec2-section-title" style="font-size:14px;">Trust policy preview</h3>
      <pre id="trust-preview" class="iam-json" style="max-height:200px;">{{}}</pre>

      <div class="wizard-actions">
        <button type="submit" class="aws-button-primary">Create role</button>
        <button type="button" class="aws-button-secondary" onclick="roleStep(3)">Back</button>
      </div>
    </div>
  </form>

  <script>
    function roleStep(n) {{
      document.querySelectorAll('#role-create-form .wizard-panel').forEach(p =>
        p.classList.toggle('active', p.dataset.step == n));
      document.querySelectorAll('.wizard-step').forEach(p =>
        p.classList.toggle('active', p.dataset.step == n));
      if (n === 2) roleUpdateStep2();
      if (n === 4) roleUpdatePreview();
    }}

    function roleCurrentEntity() {{
      const el = document.querySelector('#role-create-form input[name="entity_type"]:checked');
      return el ? el.value : 'service';
    }}

    function roleUpdateStep2() {{
      const t = roleCurrentEntity();
      document.querySelectorAll('.principal-block').forEach(b => b.style.display = 'none');
      const block = document.getElementById('principal-' + t);
      if (block) block.style.display = 'block';
    }}

    function roleUpdatePreview() {{
      const t = roleCurrentEntity();
      let principal = '{{}}';
      if (t === 'service') {{
        const s = document.getElementById('principal-service-select').value;
        principal = '{{"Service": "' + s + '"}}';
      }} else if (t === 'account') {{
        const a = document.getElementById('principal-account-input').value;
        principal = '{{"AWS": "arn:aws:iam::' + a + ':root"}}';
      }} else if (t === 'web_identity') {{
        const w = document.getElementById('principal-web-input').value;
        principal = '{{"Federated": "' + w + '"}}';
      }} else if (t === 'saml') {{
        const s = document.getElementById('principal-saml-input').value;
        principal = '{{"Federated": "' + s + '"}}';
      }}
      const action = t === 'web_identity' ? 'sts:AssumeRoleWithWebIdentity'
                    : t === 'saml' ? 'sts:AssumeRoleWithSAML'
                    : 'sts:AssumeRole';
      const policy = {{
        Version: '2012-10-17',
        Statement: [{{
          Effect: 'Allow',
          Principal: JSON.parse(principal),
          Action: action,
        }}],
      }};
      document.getElementById('trust-preview').textContent =
        JSON.stringify(policy, null, 2);
    }}
  </script>
</section>"""


# ---------- Assume role preview (read-only simulation) ----------

def render_assume_role(name, qs=None):
    """Simulates the AWS 'Switch role' page. Shows what would change."""
    r = roles_mod.get_role(name)
    if not r:
        return f'<div class="aws-notice aws-notice-error">Role not found: {_esc(name)}</div>'

    from core import account
    trust = r.get("assumeRolePolicyDocument") or {}
    translated = roles_mod.translate_trust_policy(trust)

    current = account.get_account_id()
    role_arn = r.get("arn", "")
    policies = r.get("attachedPolicies") or []

    who_lines = "".join(
        f"<li>{_esc(w)} <span class='aws-muted'>via {_esc(stmt['via'])}</span></li>"
        for stmt in translated for w in stmt["who"]
    )

    return f"""
<section class="aws-section">
  <div class="s3-page-header">
    <h1>Assume role: {_esc(name)}</h1>
    <div class="s3-page-actions">
      <a class="aws-button-secondary" href="/iam/roles/{_esc(name)}">&#8592; Back</a>
    </div>
  </div>

  <div class="aws-notice aws-notice-info">
    <strong>Preview only.</strong> Real AWS STS <code>AssumeRole</code> returns
    temporary credentials that let you <em>act as</em> this role. MiniAWS does not
    change your session (all actions still use the current account), but shows
    what the credentials would look like.
  </div>

  <table class="aws-table" style="margin-bottom:16px;">
    <tbody>
      <tr><th style="width:30%;">Account</th><td><code>{_esc(current or '—')}</code></td></tr>
      <tr><th>Role ARN</th><td><code>{_esc(role_arn)}</code></td></tr>
      <tr><th>Effective identity</th><td><code>arn:aws:sts::{_esc(current or '000000000000')}:assumed-role/{_esc(name)}/session</code></td></tr>
      <tr><th>Duration</th><td>1 hour (simulated)</td></tr>
      <tr><th>Permissions</th><td>{', '.join(f'<code>{_esc(p)}</code>' for p in policies) or '<span class="aws-muted">none</span>'}</td></tr>
    </tbody>
  </table>

  <h2 class="ec2-section-title">Who can assume this role</h2>
  <ul class="iam-trust-list">{who_lines or '<li class="aws-muted">No trust statements.</li>'}</ul>

  <h2 class="ec2-section-title">Temporary credentials (what real STS returns)</h2>
  <pre class="iam-json">{
  "Credentials": {
    "AccessKeyId": "ASIA...(redacted)",
    "SecretAccessKey": "********(redacted)",
    "SessionToken": "IQoJb3JpZ2luX2Vj...(long JWT-like token)",
    "Expiration": "2026-10-29T14:30:00Z"
  },
  "AssumedRoleUser": {
    "AssumedRoleId": "AROA...:{_esc(name)}",
    "Arn": "arn:aws:sts::{_esc(current or '000000000000')}:assumed-role/{_esc(name)}/session"
  }
}</pre>
  <p class="aws-muted s3-footer-hint">
    In real AWS, these credentials let you call AWS APIs as the role.
    The <code>SessionToken</code> is required when using temporary credentials.
  </p>
</section>"""
