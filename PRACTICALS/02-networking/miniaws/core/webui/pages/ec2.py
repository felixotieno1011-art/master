"""EC2 pages — instance list, launch wizard, instance detail (Phase 4)."""
import html
from datetime import datetime

import config
from core import ec2 as ec2_mod
from core.webui import aws_ref


def _esc(s):
    return html.escape(str(s))


def _human_date(iso):
    if not iso:
        return "—"
    try:
        dt = datetime.fromisoformat(str(iso).replace("Z", ""))
        return dt.strftime("%B %d, %Y, %H:%M:%S")
    except Exception:
        return str(iso)


def _flash(qs):
    okv = qs.get("ok") or []
    erv = qs.get("error") or []
    if okv:
        return f'<div class="aws-notice aws-notice-success">{html.escape(str(okv[0]))}</div>'
    if erv:
        return f'<div class="aws-notice aws-notice-error">{html.escape(str(erv[0]))}</div>'
    return ""


def _state_pill(state):
    s = (state or "unknown").lower()
    cls = {
        "running":     "pill-running",
        "stopped":     "pill-stopped",
        "terminated":  "pill-terminated",
        "pending":     "pill-stopped",
        "stopping":    "pill-stopped",
        "shutting-down": "pill-terminated",
    }.get(s, "pill-stopped")
    return f'<span class="ec2-pill {cls}">{_esc(s)}</span>'


# ---------- List ----------

def render_list(qs=None):
    flash = _flash(qs or {})
    try:
        instances = ec2_mod.list_all()
    except Exception as e:
        return f'<div class="aws-notice aws-notice-error">Error loading instances: {_esc(e)}</div>'

    # Default to showing non-terminated (real AWS default hides them)
    show_terminated = bool((qs or {}).get("show_terminated"))
    visible = instances if show_terminated else [
        i for i in instances if (i.get("state") or "").lower() != "terminated"
    ]
    terminated_count = len(instances) - len([i for i in instances
                                            if (i.get("state") or "").lower() != "terminated"])

    if not visible:
        rows_html = f"""
        <tr><td colspan="6" class="aws-muted" style="text-align:center; padding:24px;">
          No instances. Click <strong>Launch instance</strong> to create one.
        </td></tr>"""
    else:
        rows = []
        for inst in visible:
            iid = inst.get("instance_id", "—")
            name = (inst.get("name")
                    or (inst.get("tags") or {}).get("Name")
                    or "—")
            itype = inst.get("instance_type", "—")
            state = inst.get("state", "—")
            region = inst.get("region", "—")
            rows.append(f"""
            <tr>
              <td><a href="/ec2/instances/{_esc(iid)}">{_esc(name)}</a></td>
              <td><code>{_esc(iid)}</code></td>
              <td>{_state_pill(state)}</td>
              <td>{_esc(itype)}</td>
              <td>{_esc(region)}</td>
              <td>
                <form method="POST" action="/ec2/action" style="display:inline">
                  <input type="hidden" name="id" value="{_esc(iid)}">
                  <select name="action" onchange="if(this.value)this.form.submit()"
                          style="padding:4px 6px; font-size:12px; border:1px solid #d5dbdb; border-radius:3px;">
                    <option value="">Instance state ▾</option>
                    <option value="start">Start</option>
                    <option value="stop">Stop</option>
                    <option value="reboot">Reboot</option>
                    <option value="terminate">Terminate</option>
                  </select>
                </form>
              </td>
            </tr>""")
        rows_html = "".join(rows)

    toggle = ""
    if terminated_count:
        if show_terminated:
            toggle = f'<a class="aws-button-secondary" href="/ec2/instances">Hide terminated ({terminated_count})</a>'
        else:
            toggle = f'<a class="aws-button-secondary" href="/ec2/instances?show_terminated=1">Show terminated ({terminated_count})</a>'

    return f"""
<section class="aws-section">
  {flash}
  <div class="s3-page-header">
    <h1>Instances <span class="aws-muted">({len(visible)})</span></h1>
    <div class="s3-page-actions">
      <a class="aws-button-primary" href="/ec2/launch">Launch instance</a>
      {toggle}
    </div>
  </div>

  <table class="aws-table">
    <thead>
      <tr>
        <th>Name</th>
        <th>Instance ID</th>
        <th>Instance state</th>
        <th>Instance type</th>
        <th>Region</th>
        <th>Actions</th>
      </tr>
    </thead>
    <tbody>{rows_html}</tbody>
  </table>

  <p class="aws-muted s3-footer-hint">
    Matching real AWS: terminated instances are hidden by default.
    Use "Show terminated" to include them.
  </p>
</section>
"""


# ---------- Detail ----------

def render_detail(instance_id, qs=None):
    inst = ec2_mod.get(instance_id)
    if not inst:
        return f'<div class="aws-notice aws-notice-error">Instance not found: {_esc(instance_id)}</div>'

    flash = _flash(qs or {})
    state = inst.get("state", "—")
    name = (inst.get("name")
            or (inst.get("tags") or {}).get("Name")
            or "—")
    itype = inst.get("instance_type", "—")
    region = inst.get("region", "—")
    iid = inst.get("instance_id", "—")
    pid = inst.get("pid")

    spec = config.INSTANCE_TYPES.get(itype, {})
    tags = inst.get("tags") or {}
    tag_rows = "".join(
        f"<tr><td>{_esc(k)}</td><td>{_esc(v)}</td></tr>"
        for k, v in sorted(tags.items())
    ) or '<tr><td colspan="2" class="aws-muted">No tags</td></tr>'

    return f"""
<section class="aws-section">
  {flash}
  <div class="s3-page-header">
    <h1>{_esc(name)} <span class="ec2-pill-wrap">{_state_pill(state)}</span></h1>
    <div class="s3-page-actions">
      <a class="aws-button-secondary" href="/ec2/instances">&#8592; Instances</a>
    </div>
  </div>

  <div class="s3-tabs">
    <span class="s3-tab active">Details</span>
    <span class="s3-tab">Security</span>
    <span class="s3-tab">Networking</span>
    <span class="s3-tab">Storage</span>
    <span class="s3-tab">Tags</span>
    <span class="s3-tab">Monitoring</span>
  </div>

  <h2 class="ec2-section-title">Instance summary</h2>
  <table class="aws-table">
    <tbody>
      <tr><th style="width:35%;">Instance ID</th><td><code>{_esc(iid)}</code></td></tr>
      <tr><th>Instance state</th><td>{_state_pill(state)}</td></tr>
      <tr><th>Instance type</th><td>{_esc(itype)}
        {f'<span class="aws-muted">({spec.get("vcpus")} vCPU, {spec.get("memory_mb")} MB RAM)</span>' if spec else ''}
      </td></tr>
      <tr><th>Region</th><td>{_esc(region)}</td></tr>
      <tr><th>Private IP</th><td>{_esc(inst.get("private_ip", "—"))}</td></tr>
      <tr><th>Public IPv4</th><td>{_esc(inst.get("public_ip", "—"))}</td></tr>
      <tr><th>PID</th><td>{_esc(pid) if pid else '—'}</td></tr>
      <tr><th>Created</th><td>{_esc(_human_date(inst.get("created")))}</td></tr>
    </tbody>
  </table>

  <h2 class="ec2-section-title">Tags</h2>
  <table class="aws-table">
    <thead><tr><th>Key</th><th>Value</th></tr></thead>
    <tbody>{tag_rows}</tbody>
  </table>

  <h2 class="ec2-section-title">Instance state actions</h2>
  <div class="ec2-action-row">
    <form method="POST" action="/ec2/action" style="display:inline">
      <input type="hidden" name="id" value="{_esc(iid)}">
      <input type="hidden" name="action" value="start">
      <button type="submit" class="aws-button-secondary">Start instance</button>
    </form>
    <form method="POST" action="/ec2/action" style="display:inline">
      <input type="hidden" name="id" value="{_esc(iid)}">
      <input type="hidden" name="action" value="stop">
      <button type="submit" class="aws-button-secondary">Stop instance</button>
    </form>
    <form method="POST" action="/ec2/action" style="display:inline">
      <input type="hidden" name="id" value="{_esc(iid)}">
      <input type="hidden" name="action" value="reboot">
      <button type="submit" class="aws-button-secondary">Reboot instance</button>
    </form>
    <form method="POST" action="/ec2/action" style="display:inline"
          onsubmit="return confirm('Terminate {_esc(iid)}? This cannot be undone.')">
      <input type="hidden" name="id" value="{_esc(iid)}">
      <input type="hidden" name="action" value="terminate">
      <button type="submit" class="aws-button-danger">Terminate instance</button>
    </form>
  </div>
</section>
"""


# ---------- Launch wizard ----------

def render_launch(qs=None):
    flash = _flash(qs or {})
    type_opts = "".join(
        f'<option value="{_esc(t)}"{(" selected" if t == "t3.micro" else "")}>'
        f'{_esc(t)} &mdash; {spec["vcpus"]} vCPU, {spec["memory_mb"]} MB RAM'
        f'</option>'
        for t, spec in config.INSTANCE_TYPES.items()
    )
    return f"""
<section class="aws-section">
  {flash}
  <div class="wizard-header">
    <h1>Launch an instance</h1>
    <p class="aws-muted">Mirrors the real EC2 launch wizard (Name &rarr; AMI &rarr; Type &rarr; Network &rarr; Review).</p>
  </div>

  <form id="launch-form" method="POST" action="/ec2/launch">
    <div class="wizard-step-tabs">
      <div class="wizard-step active" data-step="1">1. Name and tags</div>
      <div class="wizard-step" data-step="2">2. Application and OS Image (AMI)</div>
      <div class="wizard-step" data-step="3">3. Instance type</div>
      <div class="wizard-step" data-step="4">4. Network &amp; security</div>
      <div class="wizard-step" data-step="5">5. Summary</div>
    </div>

    <div class="wizard-panel active" data-step="1">
      <div class="wizard-field">
        <label for="name">Name</label>
        <input id="name" name="name" type="text" required
               placeholder="my-web-server"
               pattern="[a-zA-Z][a-zA-Z0-9_\\-]{{0,63}}"
               title="Start with a letter; letters/digits/_/-; max 64 chars">
        <p class="aws-muted wizard-hint">
          The instance's <code>Name</code> tag. This is what you'll see in
          <code>aws ec2 describe-instances</code>.
        </p>
      </div>
      <div class="wizard-actions">
        <button type="button" class="aws-button-primary" onclick="launchStep(2)">Next</button>
        <a class="aws-button-secondary" href="/ec2/instances">Cancel</a>
      </div>
    </div>

    <div class="wizard-panel" data-step="2">
      <div class="aws-notice aws-notice-info">
        <strong>Simulated.</strong> MiniAWS does not run real OS images.
        Selecting an AMI here has no effect on <code>core/ec2.py</code>; the
        instance is created from your local simulator.
      </div>
      <div class="wizard-field">
        <label>Quick Start AMIs (UI only)</label>
        <select disabled>
          <option>Amazon Linux 2023 AMI (free tier eligible)</option>
          <option>Ubuntu Server 22.04 LTS</option>
          <option>Microsoft Windows Server 2022 Base</option>
        </select>
      </div>
      <div class="wizard-actions">
        <button type="button" class="aws-button-primary" onclick="launchStep(3)">Next</button>
        <button type="button" class="aws-button-secondary" onclick="launchStep(1)">Back</button>
      </div>
    </div>

    <div class="wizard-panel" data-step="3">
      <div class="wizard-field">
        <label for="instance_type">Instance type</label>
        <select id="instance_type" name="instance_type">
          {type_opts}
        </select>
        <p class="aws-muted wizard-hint">
          Real value. Passed to <code>core.ec2.create(name, instance_type=...)</code>.
        </p>
      </div>
      <div class="wizard-actions">
        <button type="button" class="aws-button-primary" onclick="launchStep(4)">Next</button>
        <button type="button" class="aws-button-secondary" onclick="launchStep(2)">Back</button>
      </div>
    </div>

    <div class="wizard-panel" data-step="4">
      <div class="aws-notice aws-notice-info">
        <strong>Simulated.</strong> Key pairs and security groups are not
        enforced in MiniAWS. The instance will start with defaults.
      </div>
      <div class="wizard-field">
        <label>Key pair</label>
        <select disabled><option>Proceed without a key pair</option></select>
      </div>
      <div class="wizard-field">
        <label>Security group</label>
        <select disabled><option>default (sg-default)</option></select>
      </div>
      <div class="wizard-actions">
        <button type="button" class="aws-button-primary" onclick="launchStep(5)">Next</button>
        <button type="button" class="aws-button-secondary" onclick="launchStep(3)">Back</button>
      </div>
    </div>

    <div class="wizard-panel" data-step="5">
      <table class="aws-table" style="margin-bottom:16px;">
        <tbody>
          <tr><th style="width:35%;">Name</th><td><code id="review-name">—</code></td></tr>
          <tr><th>Instance type</th><td><code id="review-type">t3.micro</code></td></tr>
          <tr><th>Region</th><td>{_esc(config.DEFAULT_REGION)} (current)</td></tr>
          <tr><th>AMI</th><td class="aws-muted">Amazon Linux 2023 (simulated)</td></tr>
          <tr><th>Key pair</th><td class="aws-muted">Proceed without (simulated)</td></tr>
        </tbody>
      </table>
      <div class="wizard-actions">
        <button type="submit" class="aws-button-primary">Launch instance</button>
        <button type="button" class="aws-button-secondary" onclick="launchStep(4)">Back</button>
      </div>
    </div>
  </form>

  <script>
    function launchStep(n) {{
      if (n === 5) {{
        document.getElementById('review-name').textContent =
          document.getElementById('name').value || '(no name)';
        document.getElementById('review-type').textContent =
          document.getElementById('instance_type').value;
      }}
      if (n === 2 && !document.getElementById('name').value) {{
        document.getElementById('name').focus();
        return;
      }}
      document.querySelectorAll('#launch-form .wizard-panel').forEach(p =>
        p.classList.toggle('active', p.dataset.step == n));
      document.querySelectorAll('.wizard-step').forEach(p =>
        p.classList.toggle('active', p.dataset.step == n));
    }}
  </script>
</section>
"""
