"""AWS Console shell — top bar, sidebar, breadcrumb. One function, used by every page."""
from core.webui import security
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
    <button class="aws-hamburger" onclick="awsToggleSidebar()" title="Menu">&#9776;</button>
    <a class="aws-logo" href="/" title="MiniAWS Console">aws</a>
    <nav class="aws-topnav">
      <a href="/">Services</a>
    </nav>
    <form class="aws-search" method="GET" action="/search">
      <input id="aws-search-input" type="search" name="q" value=""
             placeholder="Search for services, features, docs" autocomplete="off">
    </form>
  </div>
  <div class="aws-header-right">
    <a href="/cloudshell" class="aws-header-icon" title="CloudShell">&#62;_</a>
    <a href="https://docs.aws.amazon.com/" target="_blank" rel="noopener"
       class="aws-header-icon" title="Documentation">&#128214;</a>
    <a href="/notifications" class="aws-header-icon aws-icon-badge" title="Notifications">
      &#128276;<span class="aws-badge">2</span>
    </a>
    <a href="/support" class="aws-header-icon" title="Support">?</a>
    <div class="aws-account-menu">
      <button class="aws-account-btn" onclick="awsToggleAccount()" title="Account">
        &#128100; <span class="aws-caret">&#9662;</span>
      </button>
      <div class="aws-account-dropdown" id="aws-account-dropdown" style="display:none;">
        <div class="aws-account-header">
          <div class="aws-account-name">Account: {region_code.split('-')[0] if region_code else 'us'}</div>
        </div>
        <a href="/sts">Account</a>
        <a href="/notifications">Notifications <span class="aws-badge-inline">2</span></a>
        <a href="/billing">Billing and Cost Management</a>
        <a href="/iam">Security credentials</a>
        <a href="/sts">Sign out</a>
      </div>
    </div>
    <form class="aws-region" method="GET" action="">
      <select name="region" onchange="this.form.submit()" title="Region">
        {region_opts}
      </select>
    </form>
  </div>
</header>
<script>
  function awsToggleAccount() {{
    var d = document.getElementById('aws-account-dropdown');
    d.style.display = (d.style.display === 'none' || !d.style.display) ? 'block' : 'none';
  }}
  function awsToggleSidebar() {{
    document.body.classList.toggle('aws-sidebar-open');
  }}
  // Close account dropdown on outside click
  document.addEventListener('click', function(e) {{
    var dd = document.getElementById('aws-account-dropdown');
    if (!dd) return;
    if (dd.style.display === 'block' && !e.target.closest('.aws-account-menu')) {{
      dd.style.display = 'none';
    }}
  }});
</script>
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


def _security_banner():
    """Render dismissible MFA / root-key warnings."""
    try:
        warnings = security.active_banners()
    except Exception:
        return ""
    if not warnings:
        return ""
    parts = []
    for w in warnings:
        key = w.get("key", "")
        sev = w.get("severity", "warn")
        cls = "security-banner-critical" if sev == "critical" else "security-banner-warn"
        parts.append(f"""
<div class="security-banner {cls}">
  <div class="security-banner-body">
    <strong>⚠️ {_esc(w.get("title", ""))}</strong>
    <p style="margin:4px 0 8px; font-size:13px;">{_esc(w.get("body", "")[:200])}...</p>
    <a class="aws-button-secondary" href="{_esc(w.get("href", "/"))}" style="font-size:12px;">
      {_esc(w.get("action", "Learn more"))}
    </a>
  </div>
  <form method="POST" action="/security/dismiss" style="margin-left:auto;">
    <input type="hidden" name="key" value="{_esc(key)}">
    <button type="submit" class="security-banner-dismiss" title="Dismiss">&#x2715;</button>
  </form>
</div>""")
    return f'<div class="security-banners">{"".join(parts)}</div>'


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
  {_security_banner()}
  <div class="aws-body">
    {_sidebar(active_service, path)}
    <main class="aws-main">
      {content_html}
    </main>
  </div>
<script src="/static/aws.js" defer></script>
</body>
</html>"""
