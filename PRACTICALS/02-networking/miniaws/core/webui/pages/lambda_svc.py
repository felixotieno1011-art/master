"""Lambda pages — dashboard, functions list, function detail, test invoke."""
import html
import json
import os
from datetime import datetime

from core import lambda_svc as lam


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


def _json_view(obj):
    """Pretty-print JSON with AWS-style coloring."""
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


# ---------- Dashboard ----------

def render_dashboard(qs=None):
    flash = _flash(qs)
    try:
        funcs = lam.list_functions()
    except Exception as e:
        return f'<div class="aws-notice aws-notice-error">Error: {_esc(e)}</div>'

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
    <h1>Lambda Dashboard</h1>
    <div class="s3-page-actions">
      <a class="aws-button-primary" href="/lambda/functions/create">Create function</a>
    </div>
  </div>
  <div class="cw-tiles-grid">
    {_tile("Functions", len(funcs), "/lambda/functions", "serverless Python functions")}
    {_tile("Runtime", "python3.11", "/lambda/functions", "default for new functions")}
    {_tile("Test invoke", "on-device", "/lambda/functions",
           "sandboxed subprocess, 10s timeout")}
  </div>
  <div class="aws-notice aws-notice-warn" style="margin-top:16px;">
    <strong>How MiniAWS runs your code:</strong> pasted Python runs locally in a
    <strong>subprocess with a 10-second timeout</strong>, in an isolated temp directory.
    It cannot reach the network. It can still read/write files on your device,
    so <strong>only paste code you trust</strong>.
  </div>
</section>"""


# ---------- Functions list ----------

def render_functions(qs=None):
    flash = _flash(qs)
    try:
        raw = lam.list_functions()
        # Defensive: filter anything that doesn't look like a real function
        # (e.g. lingering .last-invoke.json cache from a previous path scheme)
        funcs = [f for f in raw
                 if isinstance(f, dict) and "FunctionName" in f]
    except Exception as e:
        return f'<div class="aws-notice aws-notice-error">Error: {_esc(e)}</div>'

    if not funcs:
        return f"""
<section class="aws-section">
  {flash}
  <div class="s3-page-header">
    <h1>Functions <span class="aws-muted">(0)</span></h1>
    <div class="s3-page-actions">
      <a class="aws-button-primary" href="/lambda/functions/create">Create function</a>
    </div>
  </div>
  <div class="s3-empty">
    <p class="aws-muted">No functions yet. Click <strong>Create function</strong> to start.</p>
  </div>
</section>"""

    rows = "".join(f"""
    <tr>
      <td><a href="/lambda/functions/{_esc(f['FunctionName'])}">{_esc(f['FunctionName'])}</a></td>
      <td>{_esc(f.get('Runtime','—'))}</td>
      <td><code>{_esc(f.get('Handler','—'))}</code></td>
      <td>{_esc(f.get('State','Active'))}</td>
      <td>{f.get('CodeSize', 0)} B</td>
      <td>{_esc(_human_date(f.get('LastModified')))}</td>
    </tr>""" for f in funcs)

    return f"""
<section class="aws-section">
  {flash}
  <div class="s3-page-header">
    <h1>Functions <span class="aws-muted">({len(funcs)})</span></h1>
    <div class="s3-page-actions">
      <a class="aws-button-primary" href="/lambda/functions/create">Create function</a>
    </div>
  </div>
  <table class="aws-table">
    <thead>
      <tr><th>Function name</th><th>Runtime</th><th>Handler</th>
          <th>State</th><th>Code size</th><th>Last modified</th></tr>
    </thead>
    <tbody>{rows}</tbody>
  </table>
</section>"""


# ---------- Function detail ----------

def render_function_detail(name, tab="code", qs=None):
    f = lam.get_function(name)
    if not f:
        return f'<div class="aws-notice aws-notice-error">Function not found: {_esc(name)}</div>'

    flash = _flash(qs)
    tabs = [
        ("code", "Code"),
        ("test", "Test"),
        ("config", "Configuration"),
        ("monitor", "Monitor"),
        ("versions", "Versions"),
        ("aliases", "Aliases"),
    ]
    tab_html = "".join(
        f'<a class="s3-tab {"active" if tid == tab else ""}" '
        f'href="/lambda/functions/{_esc(name)}{"" if tid == "code" else "?tab=" + tid}">{label}</a>'
        for tid, label in tabs
    )

    if tab == "code":
        code_path = f.get("CodePath")
        code_content = ""
        if code_path and os.path.isfile(code_path):
            try:
                with open(code_path) as fp:
                    code_content = fp.read()
            except Exception:
                code_content = "(failed to read code file)"
        # Show code in a read-only <pre> with syntax coloring for keywords
        content = f"""
<h2 class="ec2-section-title">Code source</h2>
<div class="aws-notice aws-notice-info">
  Code is read-only from the browser. To update it, use the CLI:
  <code>aws lambda create-function --function-name {_esc(name)} --zip-file path/to/file.py</code>
</div>
<pre class="iam-json" style="max-height:480px;">{_esc(code_content) if code_content else '(empty)'}</pre>
<div class="ec2-action-row" style="margin-top:16px;">
  <a class="aws-button-primary" href="/lambda/functions/{_esc(name)}?tab=test">Test</a>
  <form method="POST" action="/lambda/functions/delete" style="display:inline"
        onsubmit="return confirm('Delete function {_esc(name)}?')">
    <input type="hidden" name="name" value="{_esc(name)}">
    <button type="submit" class="aws-button-danger">Delete function</button>
  </form>
</div>"""

    elif tab == "test":
        content = f"""
<h2 class="ec2-section-title">Test event</h2>
<form method="POST" action="/lambda/functions/invoke">
  <input type="hidden" name="name" value="{_esc(name)}">
  <div class="wizard-field">
    <label for="event_json">Event JSON (passed as <code>event</code> to your handler)</label>
    <textarea id="event_json" name="event_json" rows="6"
              style="width:100%; font-family:monospace; font-size:13px;
                     padding:10px; border:1px solid #d5dbdb; border-radius:3px;">{{"a": 3, "b": 4}}</textarea>
    <p class="aws-muted wizard-hint">
      Handler runs as <code>handler(event, context)</code> in a subprocess with a 10s timeout.
    </p>
  </div>
  <div class="wizard-actions">
    <button type="submit" class="aws-button-primary">Test</button>
    <a class="aws-button-secondary" href="/lambda/functions/{_esc(name)}?tab=code">View code</a>
  </div>
</form>
{_render_last_invoke(name)}"""

    elif tab == "config":
        content = f"""
<h2 class="ec2-section-title">General configuration</h2>
<table class="aws-table">
  <tbody>
    <tr><th style="width:35%;">Function name</th><td><code>{_esc(f['FunctionName'])}</code></td></tr>
    <tr><th>ARN</th><td><code>{_esc(f.get('FunctionArn','—'))}</code></td></tr>
    <tr><th>Runtime</th><td>{_esc(f.get('Runtime','—'))}</td></tr>
    <tr><th>Handler</th><td><code>{_esc(f.get('Handler','—'))}</code></td></tr>
    <tr><th>Code size</th><td>{f.get('CodeSize', 0)} B</td></tr>
    <tr><th>Memory</th><td>{f.get('MemorySize', 128)} MB</td></tr>
    <tr><th>Timeout</th><td>{f.get('Timeout', 3)} s</td></tr>
    <tr><th>Execution role</th><td><code>{_esc(f.get('Role','—'))}</code></td></tr>
    <tr><th>Version</th><td>{_esc(f.get('Version','$LATEST'))}</td></tr>
    <tr><th>State</th><td>{_esc(f.get('State','Active'))}</td></tr>
    <tr><th>Last modified</th><td>{_esc(_human_date(f.get('LastModified')))}</td></tr>
  </tbody>
</table>"""

    elif tab == "monitor":
        content = ('<p class="aws-muted">Real AWS shows CloudWatch Invocations / Errors / '
                   'Duration / Throttles metrics here. MiniAWS does not track Lambda metrics; '
                   'use the main CloudWatch page for simulated metrics.</p>')
    elif tab == "versions":
        content = (f'<p class="aws-muted">Version <code>{_esc(f.get("Version","$LATEST"))}</code> '
                   'is the only published version. Real AWS allows publishing numbered versions '
                   'and aliases.</p>')
    else:
        content = '<p class="aws-muted">No aliases (real AWS lets you point aliases like "prod" at versions).</p>'

    return f"""
<section class="aws-section">
  {flash}
  <div class="s3-page-header">
    <h1>{_esc(name)}</h1>
    <div class="s3-page-actions">
      <a class="aws-button-secondary" href="/lambda/functions">&#8592; Functions</a>
    </div>
  </div>
  <nav class="s3-tabs">{tab_html}</nav>
  {content}
</section>"""


def _render_last_invoke(name):
    """Show the last invocation result if it was stored in state."""
    # Cache lives OUTSIDE functions/ so list_functions() never parses it
    path = os.path.join(
        "state", "lambda", "invoke-cache", f"{name}.json"
    )
    if not os.path.isfile(path):
        return ""
    try:
        with open(path) as fp:
            r = json.load(fp)
    except Exception:
        return ""

    ok = r.get("ok")
    cls = "aws-notice-success" if ok else "aws-notice-error"
    duration = r.get("duration_ms", "—")
    exit_code = r.get("exit_code", "—")
    stdout = r.get("stdout", "")
    stderr = r.get("stderr", "")
    payload = r.get("payload")

    payload_html = _json_view(payload) if payload is not None else "<p class='aws-muted'>(no payload)</p>"

    return f"""
<h2 class="ec2-section-title">Last invocation result</h2>
<div class="aws-notice {cls}">
  <strong>{'✅ Success' if ok else '❌ Error'}</strong>
  &nbsp;·&nbsp; Duration: <strong>{duration} ms</strong>
  &nbsp;·&nbsp; Exit code: <strong>{exit_code}</strong>
</div>

<h3 class="ec2-section-title" style="font-size:13px;">Response payload</h3>
{payload_html}

{f'<h3 class="ec2-section-title" style="font-size:13px;">stdout</h3><pre class="iam-json">{_esc(stdout) or "(empty)"}</pre>' if stdout else ''}
{f'<h3 class="ec2-section-title" style="font-size:13px;">stderr</h3><pre class="iam-json">{_esc(stderr)}</pre>' if stderr else ''}
"""


# ---------- Create function wizard ----------

def render_create_function(qs=None):
    flash = _flash(qs)
    sample_code = '''def lambda_handler(event, context):
    a = event.get("a", 0)
    b = event.get("b", 0)
    print(f"adding {a} + {b}")
    return {"sum": a + b}
'''
    return f"""
<section class="aws-section">
  {flash}
  <div class="wizard-header">
    <h1>Create function</h1>
    <p class="aws-muted">Same 2-step shape as real Lambda → Create function → Author from scratch.</p>
  </div>
  <form id="lambda-create-form" method="POST" action="/lambda/functions/create">
    <div class="wizard-step-tabs">
      <div class="wizard-step active" data-step="1">1. Basic information</div>
      <div class="wizard-step" data-step="2">2. Code</div>
    </div>

    <div class="wizard-panel active" data-step="1">
      <div class="wizard-field">
        <label for="name">Function name</label>
        <input id="name" name="name" type="text" required
               placeholder="Adder" pattern="[a-zA-Z0-9_\\-]{{1,64}}">
        <p class="aws-muted wizard-hint">
          1–64 chars, letters / digits / <code>_</code> / <code>-</code>.
        </p>
      </div>
      <div class="wizard-field">
        <label for="runtime">Runtime</label>
        <select id="runtime" name="runtime">
          <option value="python3.11" selected>Python 3.11</option>
          <option value="python3.10">Python 3.10</option>
        </select>
        <p class="aws-muted wizard-hint">
          MiniAWS runs your handler with <code>exec()</code> inside a subprocess.
          Any Python version installed on your device works.
        </p>
      </div>
      <div class="wizard-field">
        <label for="handler">Handler</label>
        <input id="handler" name="handler" type="text"
               value="lambda_handler" required>
      </div>
      <div class="wizard-actions">
        <button type="button" class="aws-button-primary" onclick="lamStep(2)">Next</button>
        <a class="aws-button-secondary" href="/lambda/functions">Cancel</a>
      </div>
    </div>

    <div class="wizard-panel" data-step="2">
      <div class="aws-notice aws-notice-warn">
        <strong>⚠️ Sandbox:</strong> pasted code runs in a subprocess with
        a <strong>10-second timeout</strong>, no network access, and a
        temporary working directory. It can still write files on your device —
        <strong>only paste code you trust</strong>.
      </div>
      <div class="wizard-field">
        <label for="code">Function code (Python)</label>
        <textarea id="code" name="code" rows="14" required
                  style="width:100%; font-family:monospace; font-size:13px;
                         padding:10px; border:1px solid #d5dbdb; border-radius:3px;">{_esc(sample_code)}</textarea>
        <p class="aws-muted wizard-hint">
          Must define <code>def {_esc("lambda_handler")}(event, context)</code>.
        </p>
      </div>
      <div class="wizard-actions">
        <button type="submit" class="aws-button-primary">Create function</button>
        <button type="button" class="aws-button-secondary" onclick="lamStep(1)">Back</button>
      </div>
    </div>
  </form>
  <script>
    function lamStep(n) {{
      if (n === 2 && !document.getElementById('name').value) {{
        document.getElementById('name').focus(); return;
      }}
      document.querySelectorAll('#lambda-create-form .wizard-panel').forEach(p =>
        p.classList.toggle('active', p.dataset.step == n));
      document.querySelectorAll('.wizard-step').forEach(p =>
        p.classList.toggle('active', p.dataset.step == n));
    }}
  </script>
</section>"""
