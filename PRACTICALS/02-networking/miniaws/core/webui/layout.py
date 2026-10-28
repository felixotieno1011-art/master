"""AWS Console shell — top bar, sidebar, breadcrumb. One function, used by every page."""
import html

from core.webui import aws_ref


def _esc(s):
    return html.escape(str(s))


def _header(active_service, region_label):
    region_code, _ = region_label
    region_opts = "".join(
        f'<option value="{_esc(code)}"{" selected" if code == region_code else ""}>'
        f'{_esc(label)}</option>'
        for code, label in aws_ref.REGIONS
    )
    return f"""
<header class="aws-header">
  <div class="aws-header-left">
    <a class="aws-logo" href="/" title="MiniAWS Console">aws</a>
    <nav class="aws-topnav">
      <a href="/">Services</a>
      <a href="#">Search</a>
      <a href="#">Documentation</a>
    </nav>
  </div>
  <div class="aws-header-right">
    <label class="aws-region">
      <span class="aws-region-prefix">Region</span>
      <select id="aws-region-select" data-active="{_esc(region_code)}">
        {region_opts}
      </select>
    </label>
    <a href="#" class="aws-header-icon" title="Notifications">&#128276;</a>
    <a href="#" class="aws-header-icon" title="Help">&#63;</a>
    <a href="/sts" class="aws-header-icon" title="Account">&#128100;</a>
  </div>
</header>
"""


def _breadcrumb(items):
    if not items:
        return ""
    parts = []
    for i, item in enumerate(items):
        label, href = (item + (None,))[:2] if isinstance(item, tuple) else (item, None)
        if href and i < len(items) - 1:
            parts.append(f'<a href="{_esc(href)}">{_esc(label)}</a>')
        else:
            parts.append(f'<span>{_esc(label)}</span>')
    return f'<nav class="aws-breadcrumb">{" &rsaquo; ".join(parts)}</nav>'


def _sidebar(active_service, path):
    nav = aws_ref.SERVICE_NAV.get(active_service, [])
    if not nav:
        return "<aside class='aws-sidebar'></aside>"
    rows = []
    for label, href in nav:
        cls = "active" if path == href else ""
        rows.append(f'<li><a class="{cls}" href="{_esc(href)}">{_esc(label)}</a></li>')
    return f"""
<aside class="aws-sidebar">
  <h2 class="aws-sidebar-title">{_esc(dict((s[0], s[1]) for s in aws_ref.SERVICES).get(active_service, "AWS"))}</h2>
  <ul class="aws-sidebar-list">{''.join(rows)}</ul>
</aside>
"""


def page(title, content_html, active_service="", breadcrumb=None,
         region=("us-east-1", "US East (N. Virginia)"), path="/"):
    """Render the full console page shell around content_html."""
    bc = _breadcrumb(breadcrumb or [("AWS Console", "/")])
    return f"""<!doctype html>
<html lang="en">
<head>
  <meta charset="utf-8">
  <meta name="viewport" content="width=device-width, initial-scale=1">
  <title>{_esc(title)} | {_esc(dict((s[0], s[1]) for s in aws_ref.SERVICES).get(active_service, "AWS"))} | MiniAWS</title>
  <link rel="stylesheet" href="/static/aws.css">
</head>
<body>
  {_header(active_service, region)}
  {bc}
  <div class="aws-body">
    {_sidebar(active_service, path)}
    <main class="aws-main">
      {content_html}
    </main>
  </div>
</body>
</html>"""
