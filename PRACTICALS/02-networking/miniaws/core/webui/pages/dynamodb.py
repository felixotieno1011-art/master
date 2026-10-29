"""DynamoDB pages — dashboard, tables, table detail, item browser, wizards."""
import html
import json
from datetime import datetime

from core import dynamodb as ddb


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


# ---------- JSON viewers (plain + DynamoDB typed) ----------

def _typed_json(item):
    """Convert plain dict → DynamoDB wire format ({k: {S: v}, ...})."""
    def _wrap(v):
        if isinstance(v, bool):
            return {"BOOL": v}
        if isinstance(v, (int, float)):
            return {"N": str(v)}
        if v is None:
            return {"NULL": True}
        if isinstance(v, str):
            return {"S": v}
        if isinstance(v, list):
            return {"L": [_wrap(x) for x in v]}
        if isinstance(v, dict):
            return {"M": {k: _wrap(x) for k, x in v.items()}}
        return {"S": str(v)}
    return {k: _wrap(v) for k, v in item.items()}


def _json_view(obj):
    """Pretty-print JSON with syntax coloring (same classes as IAM)."""
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
        tables = ddb.list_tables()
    except Exception as e:
        return f'<div class="aws-notice aws-notice-error">Error: {_esc(e)}</div>'

    total_items = sum(t.get("ItemCount", 0) for t in tables)

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
    <h1>DynamoDB Dashboard</h1>
    <div class="s3-page-actions">
      <a class="aws-button-primary" href="/dynamodb/tables/create">Create table</a>
    </div>
  </div>
  <div class="cw-tiles-grid">
    {_tile("Tables", len(tables), "/dynamodb/tables", "active NoSQL tables")}
    {_tile("Items", total_items, "/dynamodb/tables", "across all tables")}
    {_tile("Capacity mode", "On-demand", "/dynamodb/tables",
           "no provisioned throughput")}
  </div>
  <p class="aws-muted s3-footer-hint">
    <strong>Real AWS note:</strong> DynamoDB scales horizontally and offers
    on-demand or provisioned capacity. MiniAWS simulates the API shape,
    not real partition/sharding behavior.
  </p>
</section>"""


# ---------- Tables list ----------

def render_tables(qs=None):
    flash = _flash(qs)
    try:
        tables = ddb.list_tables()
    except Exception as e:
        return f'<div class="aws-notice aws-notice-error">Error: {_esc(e)}</div>'

    if not tables:
        return f"""
<section class="aws-section">
  {flash}
  <div class="s3-page-header">
    <h1>Tables <span class="aws-muted">(0)</span></h1>
    <div class="s3-page-actions">
      <a class="aws-button-primary" href="/dynamodb/tables/create">Create table</a>
    </div>
  </div>
  <div class="s3-empty">
    <p class="aws-muted">No tables yet. Click <strong>Create table</strong> to start.</p>
  </div>
</section>"""

    rows = []
    for t in tables:
        ks = (t.get("KeySchema") or [{}])[0]
        key = ks.get("AttributeName", "—")
        rows.append(f"""
        <tr>
          <td><a href="/dynamodb/tables/{_esc(t['TableName'])}">{_esc(t['TableName'])}</a></td>
          <td>{_esc(t.get('TableStatus','ACTIVE'))}</td>
          <td><code>{_esc(key)}</code> <span class="aws-muted">({_esc(t.get('key_type','S'))})</span></td>
          <td>{t.get('ItemCount', 0)}</td>
          <td>{_esc(_human_date(t.get('CreationDateTime')))}</td>
        </tr>""")

    return f"""
<section class="aws-section">
  {flash}
  <div class="s3-page-header">
    <h1>Tables <span class="aws-muted">({len(tables)})</span></h1>
    <div class="s3-page-actions">
      <a class="aws-button-primary" href="/dynamodb/tables/create">Create table</a>
    </div>
  </div>
  <table class="aws-table">
    <thead>
      <tr><th>Name</th><th>Status</th><th>Partition key</th>
          <th>Items</th><th>Creation date</th></tr>
    </thead>
    <tbody>{"".join(rows)}</tbody>
  </table>
</section>"""


# ---------- Table detail ----------

def render_table_detail(name, tab="overview", qs=None):
    t = ddb.get_table(name)
    if not t:
        return f'<div class="aws-notice aws-notice-error">Table not found: {_esc(name)}</div>'

    flash = _flash(qs)
    tabs = [
        ("overview", "Overview"),
        ("items", "Explore items"),
        ("indexes", "Indexes"),
        ("monitor", "Monitor"),
        ("capacity", "Capacity"),
        ("backups", "Backups"),
    ]
    tab_html = "".join(
        f'<a class="s3-tab {"active" if tid == tab else ""}" '
        f'href="/dynamodb/tables/{_esc(name)}{"" if tid == "overview" else "/items" if tid == "items" else "?tab=" + tid}">{label}</a>'
        for tid, label in tabs
    )

    ks = (t.get("KeySchema") or [{}])[0]
    key_name = ks.get("AttributeName", "—")
    ad = (t.get("AttributeDefinitions") or [{}])[0]
    key_type = ad.get("AttributeType", "S")

    if tab == "overview":
        content = f"""
<h2 class="ec2-section-title">General information</h2>
<table class="aws-table">
  <tbody>
    <tr><th style="width:35%;">Table name</th><td><code>{_esc(t['TableName'])}</code></td></tr>
    <tr><th>ARN</th><td><code>{_esc(t.get('TableArn','—'))}</code></td></tr>
    <tr><th>Status</th><td>{_esc(t.get('TableStatus','ACTIVE'))}</td></tr>
    <tr><th>Partition key</th><td><code>{_esc(key_name)}</code> ({_esc(key_type)})</td></tr>
    <tr><th>Sort key</th><td class="aws-muted">None (MiniAWS — single-key tables only)</td></tr>
    <tr><th>Items</th><td>{t.get('ItemCount', 0)}</td></tr>
    <tr><th>Capacity mode</th><td>On-demand</td></tr>
    <tr><th>Created</th><td>{_esc(_human_date(t.get('CreationDateTime')))}</td></tr>
  </tbody>
</table>
<div class="ec2-action-row" style="margin-top:16px;">
  <a class="aws-button-primary" href="/dynamodb/tables/{_esc(name)}/items">Explore items</a>
  <form method="POST" action="/dynamodb/tables/delete" style="display:inline"
        onsubmit="return confirm('Delete table {_esc(name)} and all {t.get('ItemCount',0)} items?')">
    <input type="hidden" name="table" value="{_esc(name)}">
    <button type="submit" class="aws-button-danger">Delete table</button>
  </form>
</div>"""
    elif tab == "indexes":
        content = ('<p class="aws-muted">Global / Local Secondary Indexes are not simulated '
                   'in MiniAWS (single-key tables).</p>')
    elif tab == "monitor":
        content = ('<p class="aws-muted">CloudWatch metrics for this table are simulated '
                   'via the main CloudWatch page.</p>')
    elif tab == "capacity":
        content = ('<p class="aws-muted">Capacity mode: On-demand. '
                   'Provisioned read/write capacity units not simulated.</p>')
    elif tab == "backups":
        content = ('<p class="aws-muted">Point-in-time recovery and on-demand backups '
                   'are not simulated.</p>')
    else:
        content = _items_content(t, name, qs or {})

    return f"""
<section class="aws-section">
  {flash}
  <div class="s3-page-header">
    <h1>{_esc(name)}</h1>
    <div class="s3-page-actions">
      <a class="aws-button-secondary" href="/dynamodb/tables">&#8592; Tables</a>
    </div>
  </div>
  <nav class="s3-tabs">{tab_html}</nav>
  {content}
</section>"""


# ---------- Item browser (Explore items) ----------

def _items_content(t, table_name, qs):
    items_dict = t.get("items") or {}
    items = list(items_dict.values())
    key_name = t.get("key_name") or (t.get("KeySchema") or [{}])[0].get("AttributeName", "id")

    if not items:
        return f"""
<div class="s3-page-header" style="margin-bottom:8px;">
  <h2 class="ec2-section-title" style="margin:0;">Items (0)</h2>
  <a class="aws-button-primary" href="/dynamodb/tables/{_esc(table_name)}/items/create">Create item</a>
</div>
<div class="s3-empty">
  <p class="aws-muted">This table is empty.</p>
  <a class="aws-button-secondary" href="/dynamodb/tables/{_esc(table_name)}/items/create">Create item</a>
</div>"""

    cards = []
    for item in items:
        key_val = item.get(key_name, "—")
        plain = _json_view(item)
        typed = _json_view(_typed_json(item))
        cards.append(f"""
        <div class="ddb-item-card">
          <div class="ddb-item-header">
            <span class="ddb-item-key"><code>{_esc(key_name)}</code> = <strong>{_esc(key_val)}</strong></span>
            <form method="POST" action="/dynamodb/tables/delete-item" style="display:inline"
                  onsubmit="return confirm('Delete item with {_esc(key_name)}={_esc(key_val)}?')">
              <input type="hidden" name="table" value="{_esc(table_name)}">
              <input type="hidden" name="key_value" value="{_esc(key_val)}">
              <button type="submit" class="aws-link-danger">Delete</button>
            </form>
          </div>
          <div class="ddb-json-toggle">
            <button type="button" class="s3-tab active" data-view="plain"
                    onclick="ddbToggle(this)">
              Plain JSON
            </button>
            <button type="button" class="s3-tab" data-view="typed"
                    onclick="ddbToggle(this)">
              DynamoDB typed JSON
            </button>
          </div>
          <div class="ddb-view ddb-view-plain" style="display:block;">{plain}</div>
          <div class="ddb-view ddb-view-typed" style="display:none;">{typed}</div>
        </div>""")

    return f"""
<div class="s3-page-header" style="margin-bottom:8px;">
  <h2 class="ec2-section-title" style="margin:0;">Items ({len(items)})</h2>
  <div class="s3-page-actions">
    <a class="aws-button-primary" href="/dynamodb/tables/{_esc(table_name)}/items/create">Create item</a>
  </div>
</div>
<p class="aws-muted s3-footer-hint">
  Toggle <strong>Plain JSON</strong> vs <strong>DynamoDB typed JSON</strong>
  to see the difference between what you typed and what DynamoDB would store on the wire.
</p>
{"".join(cards)}
<script>
  function ddbToggle(btn) {{
    const card = btn.closest('.ddb-item-card');
    const view = btn.dataset.view;
    card.querySelectorAll('.ddb-json-toggle .s3-tab').forEach(b =>
      b.classList.toggle('active', b.dataset.view === view));
    card.querySelectorAll('.ddb-view').forEach(v =>
      v.style.display = v.classList.contains('ddb-view-' + view) ? 'block' : 'none');
  }}
</script>"""


# ---------- Wizards ----------

def render_create_table(qs=None):
    flash = _flash(qs)
    return f"""
<section class="aws-section">
  {flash}
  <div class="wizard-header">
    <h1>Create table</h1>
    <p class="aws-muted">Same 2-step shape as real DynamoDB → Create table.</p>
  </div>
  <form id="ddb-create-form" method="POST" action="/dynamodb/tables/create">
    <div class="wizard-step-tabs">
      <div class="wizard-step active" data-step="1">1. Table details</div>
      <div class="wizard-step" data-step="2">2. Review</div>
    </div>

    <div class="wizard-panel active" data-step="1">
      <div class="wizard-field">
        <label for="table_name">Table name</label>
        <input id="table_name" name="table_name" type="text" required
               placeholder="Users" pattern="[a-zA-Z0-9._\\-]{{3,255}}">
        <p class="aws-muted wizard-hint">
          3–255 characters, letters/digits/dot/hyphen/underscore.
        </p>
      </div>
      <div class="wizard-field">
        <label for="key_name">Partition key</label>
        <input id="key_name" name="key_name" type="text" required
               placeholder="id">
      </div>
      <div class="wizard-field">
        <label for="key_type">Partition key type</label>
        <select id="key_type" name="key_type">
          <option value="S">String</option>
          <option value="N">Number</option>
          <option value="B">Binary (treated as String in MiniAWS)</option>
        </select>
      </div>
      <div class="wizard-field">
        <label>Sort key</label>
        <input type="text" disabled placeholder="(not simulated — single-key tables only)">
      </div>
      <div class="wizard-field">
        <label>Capacity mode</label>
        <select disabled><option>On-demand (simulated)</option></select>
      </div>
      <div class="wizard-actions">
        <button type="button" class="aws-button-primary" onclick="ddbStep(2)">Next</button>
        <a class="aws-button-secondary" href="/dynamodb/tables">Cancel</a>
      </div>
    </div>

    <div class="wizard-panel" data-step="2">
      <table class="aws-table" style="margin-bottom:16px;">
        <tbody>
          <tr><th style="width:35%;">Table name</th><td><code id="rev-name">—</code></td></tr>
          <tr><th>Partition key</th>
              <td><code id="rev-key">—</code> (<span id="rev-type">—</span>)</td></tr>
          <tr><th>Capacity mode</th><td>On-demand</td></tr>
        </tbody>
      </table>
      <div class="wizard-actions">
        <button type="submit" class="aws-button-primary">Create table</button>
        <button type="button" class="aws-button-secondary" onclick="ddbStep(1)">Back</button>
      </div>
    </div>
  </form>
  <script>
    function ddbStep(n) {{
      if (n === 2) {{
        const name = document.getElementById('table_name').value;
        const key = document.getElementById('key_name').value;
        if (!name || !key) {{ alert('Name and partition key required'); return; }}
        document.getElementById('rev-name').textContent = name;
        document.getElementById('rev-key').textContent = key;
        document.getElementById('rev-type').textContent =
          document.getElementById('key_type').value;
      }}
      document.querySelectorAll('#ddb-create-form .wizard-panel').forEach(p =>
        p.classList.toggle('active', p.dataset.step == n));
      document.querySelectorAll('.wizard-step').forEach(p =>
        p.classList.toggle('active', p.dataset.step == n));
    }}
  </script>
</section>"""


def render_create_item(table_name, qs=None):
    t = ddb.get_table(table_name)
    if not t:
        return f'<div class="aws-notice aws-notice-error">Table not found: {_esc(table_name)}</div>'
    flash = _flash(qs)
    key_name = t.get("key_name") or "id"
    sample_json = json.dumps({key_name: "1", "name": "Alice", "age": 42}, indent=2)
    return f"""
<section class="aws-section">
  {flash}
  <div class="wizard-header">
    <h1>Create item</h1>
    <p class="aws-muted">
      In real AWS you either use the item editor (attribute-by-attribute) or the JSON editor.
      MiniAWS uses the JSON editor — paste the full item as JSON.
    </p>
  </div>
  <form method="POST" action="/dynamodb/tables/create-item">
    <input type="hidden" name="table" value="{_esc(table_name)}">
    <div class="wizard-panel active">
      <div class="wizard-field">
        <label for="item_json">Item JSON</label>
        <textarea id="item_json" name="item_json" rows="12" required
                  style="width:100%; font-family:monospace; font-size:13px;
                         padding:10px; border:1px solid #d5dbdb; border-radius:3px;">{_esc(sample_json)}</textarea>
        <p class="aws-muted wizard-hint">
          Must contain the partition key <code>{_esc(key_name)}</code>.
          Item is upserted — if the key already exists, it is replaced.
        </p>
      </div>
      <div class="wizard-actions">
        <button type="submit" class="aws-button-primary">Create item</button>
        <a class="aws-button-secondary" href="/dynamodb/tables/{_esc(table_name)}/items">Cancel</a>
      </div>
    </div>
  </form>
</section>"""
