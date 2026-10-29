"""S3 service pages — buckets list + bucket detail + wizard hooks (Phase 3)."""
import html
from datetime import datetime

from core import s3 as s3_mod
from core.webui import aws_ref
from core.webui import table_filter as tf


def _esc(s):
    return html.escape(str(s))


def _human_size(n):
    try:
        n = int(n)
    except Exception:
        return "—"
    if n < 1024:
        return f"{n} B"
    for unit in ("KB", "MB", "GB", "TB"):
        n /= 1024.0
        if n < 1024:
            return f"{n:.1f} {unit}"
    return f"{n:.1f} PB"


def _human_date(iso):
    if not iso:
        return "—"
    try:
        dt = datetime.fromisoformat(str(iso).replace("Z", ""))
        return dt.strftime("%B %d, %Y, %H:%M:%S" if not dt.tzinfo else
                           "%B %d, %Y, %H:%M:%S %z")
    except Exception:
        return str(iso)


def _flash_banner(msg, kind):
    if not msg:
        return ""
    cls = {"ok": "aws-notice-success", "error": "aws-notice-error"}.get(kind, "aws-notice-info")
    return f'<div class="aws-notice {cls}">{_esc(msg)}</div>'


def render_flash_from_query(qs):
    """Read ?ok=... or ?error=... from a parse_qs dict (list of values per key)."""
    ok_vals = qs.get("ok") or []
    err_vals = qs.get("error") or []
    if ok_vals:
        return f'<div class="aws-notice aws-notice-success">{html.escape(str(ok_vals[0]))}</div>'
    if err_vals:
        return f'<div class="aws-notice aws-notice-error">{html.escape(str(err_vals[0]))}</div>'
    return ""


def _bucket_detail_tabs(active, bucket):
    tabs = [
        ("objects",     "Objects"),
        ("properties",  "Properties"),
        ("permissions", "Permissions"),
        ("metrics",     "Metrics"),
        ("management",  "Management"),
        ("access",      "Access points"),
    ]
    parts = []
    for tab_id, label in tabs:
        cls = "active" if tab_id == active else ""
        href = f"/s3/{_esc(bucket)}" if tab_id == "objects" else f"/s3/{_esc(bucket)}?tab={tab_id}"
        parts.append(f'<a class="s3-tab {cls}" href="{href}">{label}</a>')
    return f'<nav class="s3-tabs">{"".join(parts)}</nav>'



def _quota_banner(service):
    try:
        from core.webui import security
        q = security.quota_check(service)
    except Exception:
        return ""
    if not q or not q.get("warn"):
        return ""
    pct = q["pct"]
    return f"""<div class="aws-notice aws-notice-warn">
  <strong>&#9888; Approaching service quota:</strong> You have <strong>{q["used"]} of {q["limit"]}</strong>
  {q["metric"].lower()} ({pct:.0f}%).
</div>"""


def render_buckets(region_code, qs=None):
    """Render /s3 — buckets list."""
    flash = render_flash_from_query(qs or {})
    try:
        buckets = s3_mod.ls_buckets() or []
    except Exception as e:
        return _flash_banner(f"Error loading buckets: {e}", "error")

    buckets = tf.apply_filter(buckets, qs or {}, {"region": tf.by_region})

    if not buckets:
        return f"""
<section class="aws-section">
  {flash}
  <div class="s3-empty">
    <h2>Buckets</h2>
    <p class="aws-muted">You don't have any buckets yet.</p>
    <a class="aws-button-primary" href="/s3/create">Create bucket</a>
  </div>
</section>"""

    rows = []
    for b in buckets:
        name = b.get("name", "—")
        b_region = b.get("region", "—")
        created = _human_date(b.get("created") or b.get("creation_date"))
        rows.append(f"""
        <tr>
          <td class="s3-name-cell"><a href="/s3/{_esc(name)}">{_esc(name)}</a></td>
          <td>{_esc(b_region)}</td>
          <td>{_esc(created)}</td>
          <td class="s3-empty-col">—</td>
        </tr>""")

    return f"""
<section class="aws-section">
  {flash}
  {_quota_banner("s3")}
  <div class="s3-page-header">
    <h1>Buckets <span class="aws-muted">({len(buckets)})</span></h1>
    <div class="s3-page-actions">
      <a class="aws-button-primary" href="/s3/create">Create bucket</a>
    </div>
  </div>

  <div class="s3-filter-bar">
    <input type="search" placeholder="Filter buckets by name" class="s3-filter-input" disabled>
    <span class="aws-muted" style="font-size:12px;">(filter is Phase 4)</span>
  </div>

  <table class="aws-table">
    <thead>
      <tr>
        <th>Name</th>
        <th>AWS Region</th>
        <th>Creation date</th>
        <th>Public access</th>
      </tr>
    </thead>
    <tbody>{"".join(rows)}</tbody>
  </table>

  <p class="aws-muted s3-footer-hint">
    S3 stores data as objects within buckets. Buckets are region-scoped at
    creation; the top-bar region does not restrict this list (same as real AWS).
  </p>
</section>
"""


def render_bucket(bucket_name, tab="objects", region_code="us-east-1", qs=None):
    """Render /s3/<bucket> with the requested tab."""
    meta = s3_mod.get_bucket(bucket_name)
    if not meta:
        return f'<div class="aws-notice aws-notice-error">Bucket not found: {_esc(bucket_name)}</div>'

    flash = render_flash_from_query(qs or {})
    tabs_html = _bucket_detail_tabs(tab, bucket_name)

    if tab == "objects":
        try:
            objs = s3_mod.list_objects(bucket_name) or []
        except Exception as e:
            return _flash_banner(f"Error listing objects: {e}", "error") + tabs_html

        if not objs:
            content = """
<div class="s3-empty">
  <p class="aws-muted">This bucket is empty.</p>
  <a class="aws-button-secondary" href="#">Upload (use the Upload button above)</a>
</div>"""
        else:
            rows = []
            for o in objs:
                key = o.get("key") or o.get("Key") or "—"
                size = _human_size(o.get("size", o.get("Size", 0)))
                modified = _human_date(o.get("last_modified") or o.get("LastModified"))
                ctype = o.get("content_type") or "—"
                storage = o.get("storage_class", "Standard")
                rows.append(f"""
                <tr>
                  <td class="s3-name-cell"><a href="/s3/{_esc(bucket_name)}?key={_esc(key)}">{_esc(key)}</a></td>
                  <td>{_esc(ctype)}</td>
                  <td>{_esc(modified)}</td>
                  <td class="s3-size-cell">{_esc(size)}</td>
                  <td>{_esc(storage)}</td>
                  <td>
                    <form method="POST" action="/s3/delete-object" style="display:inline"
                          onsubmit="return confirm('Delete object {_esc(key)}?')">
                      <input type="hidden" name="bucket" value="{_esc(bucket_name)}">
                      <input type="hidden" name="key" value="{_esc(key)}">
                      <button type="submit" class="aws-link-danger">Delete</button>
                    </form>
                  </td>
                </tr>""")
            content = f"""
<table class="aws-table">
  <thead>
    <tr>
      <th>Name</th>
      <th>Type</th>
      <th>Last modified</th>
      <th>Size</th>
      <th>Storage class</th>
      <th>Actions</th>
    </tr>
  </thead>
  <tbody>{"".join(rows)}</tbody>
</table>
<p class="aws-muted s3-footer-hint">{len(objs)} object(s) in this bucket.</p>"""
    else:
        content = f"""
<div class="aws-notice aws-notice-info">
  The <strong>{_esc(tab.title())}</strong> tab is a Phase 4 target.
</div>
<table class="aws-table">
  <thead><tr><th>Property</th><th>Value</th></tr></thead>
  <tbody>
    <tr><td>Bucket name</td><td><code>{_esc(meta.get("name"))}</code></td></tr>
    <tr><td>ARN</td><td><code>{_esc(meta.get("arn"))}</code></td></tr>
    <tr><td>Region</td><td>{_esc(meta.get("region"))}</td></tr>
    <tr><td>Creation date</td><td>{_esc(_human_date(meta.get("created")))}</td></tr>
    <tr><td>Account ID</td><td><code>{_esc(meta.get("account_id"))}</code></td></tr>
    <tr><td>Endpoint</td><td><code>{_esc(meta.get("url"))}</code></td></tr>
  </tbody>
</table>"""

    delete_form = f"""
      <form method="POST" action="/s3/delete-bucket" style="display:inline"
            onsubmit="return confirm('Delete bucket {_esc(bucket_name)}? It must be empty first.')">
        <input type="hidden" name="bucket" value="{_esc(bucket_name)}">
        <button type="submit" class="aws-button-danger">Delete bucket</button>
      </form>"""

    upload_btn = (
        f'<a class="aws-button-primary" href="/s3/{_esc(bucket_name)}/upload">Upload</a>'
        if tab == "objects" else ""
    )

    return f"""
<section class="aws-section">
  {flash}
  <div class="s3-page-header">
    <h1>{_esc(bucket_name)}</h1>
    <div class="s3-page-actions">
      {upload_btn}
      {delete_form}
      <a class="aws-button-secondary" href="/s3">&#8592; Buckets</a>
    </div>
  </div>
  {tabs_html}
  {content}
</section>
"""
