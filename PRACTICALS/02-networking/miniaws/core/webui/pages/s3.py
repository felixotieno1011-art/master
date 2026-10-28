"""S3 service pages — buckets list + bucket detail (read-only).

Real AWS S3 console layout:
  /s3                -> Buckets table
  /s3/<bucket>       -> Bucket detail with tabs (Objects is default)
  /s3/<bucket>/objects/<key> -> Object detail (Phase 2b)
"""
import html
from datetime import datetime

from core import s3 as s3_mod
from core.webui import aws_ref


def _esc(s):
    return html.escape(str(s))


def _human_size(n):
    """Format bytes the way the real S3 console does."""
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
        return dt.strftime("%B %d, %Y, %H:%M:%S (UTC%z)" if dt.tzinfo else
                           "%B %d, %Y, %H:%M:%S")
    except Exception:
        return str(iso)


def _flash_banner(msg, kind):
    if not msg:
        return ""
    cls = {"ok": "aws-notice-success", "error": "aws-notice-error"}.get(kind, "aws-notice-info")
    return f'<div class="aws-notice {cls}">{_esc(msg)}</div>'


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


def render_buckets(region_code):
    """Render the /s3 page — Buckets list, exact real-AWS layout."""
    try:
        buckets = s3_mod.ls_buckets() or []
    except Exception as e:
        return _flash_banner(f"Error loading buckets: {e}", "error")

    if not buckets:
        body = """
<section class="aws-section">
  <div class="s3-empty">
    <h2>Buckets</h2>
    <p class="aws-muted">You don't have any buckets yet.</p>
    <a class="aws-button-primary" href="/s3/create">Create bucket</a>
  </div>
</section>"""
        return body

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
  <div class="s3-page-header">
    <h1>Buckets <span class="aws-muted">({len(buckets)})</span></h1>
    <div class="s3-page-actions">
      <a class="aws-button-primary" href="/s3/create">Create bucket</a>
    </div>
  </div>

  <div class="s3-filter-bar">
    <input type="search" placeholder="Filter buckets by name" class="s3-filter-input" disabled>
    <span class="aws-muted" style="font-size:12px;">(filters are Phase 3)</span>
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
    creation time; the top-bar region does not restrict this list (same as real AWS).
  </p>
</section>
"""


def render_bucket(bucket_name, tab="objects", region_code="us-east-1"):
    """Render /s3/<bucket> with the requested tab (Objects default)."""
    meta = s3_mod.get_bucket(bucket_name)
    if not meta:
        return f'<div class="aws-notice aws-notice-error">Bucket not found: {_esc(bucket_name)}</div>'

    tabs_html = _bucket_detail_tabs(tab, bucket_name)

    if tab == "objects":
        try:
            objs = s3_mod.list_objects(bucket_name) or []
        except Exception as e:
            objs = []
            body = _flash_banner(f"Error listing objects: {e}", "error")
            return body + tabs_html

        if not objs:
            content = """
<div class="s3-empty">
  <p class="aws-muted">This bucket is empty.</p>
  <a class="aws-button-secondary" href="#" aria-disabled="true">Upload (Phase 3)</a>
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
    </tr>
  </thead>
  <tbody>{"".join(rows)}</tbody>
</table>
<p class="aws-muted s3-footer-hint">
  {len(objs)} object(s) in this bucket.
</p>"""
    else:
        content = f"""
<div class="aws-notice aws-notice-info">
  The <strong>{_esc(tab.title())}</strong> tab is a Phase 3 target — it will show the
  same shape as the real S3 tab (properties list, bucket policy JSON viewer,
  metrics sparkline, lifecycle rules, access points).
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

    return f"""
<section class="aws-section">
  <div class="s3-page-header">
    <h1>{_esc(bucket_name)}</h1>
    <div class="s3-page-actions">
      <a class="aws-button-secondary" href="/s3">&#8592; Buckets</a>
    </div>
  </div>
  {tabs_html}
  {content}
</section>
"""
