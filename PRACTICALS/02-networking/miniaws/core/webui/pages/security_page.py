"""Security recommendations page — /security."""
import html
import urllib.parse

from core.webui import security


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


def render_security_page(qs=None):
    flash = _flash(qs)
    warnings = security.all_warnings()
    quota_checks = security.all_quota_checks()

    def _warning_card(w):
        dismissed = security.is_dismissed(w["key"])
        sev_cls = "security-card-critical" if w.get("severity") == "critical" else "security-card-warn"
        status = '<span class="billing-budget-status billing-over_budget">OPEN</span>' if not dismissed \
                 else '<span class="billing-budget-status billing-ok">DISMISSED</span>'
        dismiss_btn = "" if dismissed else f"""
<form method="POST" action="/security/dismiss" style="display:inline">
  <input type="hidden" name="key" value="{_esc(w['key'])}">
  <button type="submit" class="aws-button-secondary">Dismiss</button>
</form>"""

        return f"""
<div class="security-card {sev_cls}">
  <div class="security-card-header">
    <div>
      <div class="security-card-title">&#9888; {_esc(w['title'])}</div>
      <div class="security-card-status">{status}</div>
    </div>
  </div>
  <p style="font-size:13px; color:#16191f; margin:8px 0;">
    {_esc(w['body'])}
  </p>
  <div class="ec2-action-row">
    <a class="aws-button-secondary" href="{_esc(w.get('href','/'))}">{_esc(w.get('action','Fix'))}</a>
    {dismiss_btn}
  </div>
</div>"""

    warning_cards = "".join(_warning_card(w) for w in warnings) if warnings else \
        '<div class="aws-notice aws-notice-success">&#127881; No security warnings. Root MFA is enabled and no root access keys exist.</div>'

    quota_rows = ""
    for q in quota_checks:
        bar_color = "#d13212" if q["warn"] else "#037f0c"
        pct = min(q["pct"], 100)
        status = '<span class="billing-budget-status billing-over_budget">AT LIMIT</span>' if q["warn"] \
                 else '<span class="billing-budget-status billing-ok">OK</span>'
        quota_rows += f"""
        <tr>
          <td>{_esc(q['service'].upper())}</td>
          <td>{_esc(q['metric'])}</td>
          <td>{q['used']:,} of {q['limit']:,}</td>
          <td>
            <div class="billing-bar-track">
              <div class="billing-bar-fill" style="width:{pct:.1f}%; background:{bar_color};"></div>
            </div>
          </td>
          <td>{q['pct']:.1f}%</td>
          <td>{status}</td>
        </tr>"""

    return f"""
<section class="aws-section">
  {flash}
  <div class="s3-page-header">
    <h1>Security recommendations</h1>
  </div>
  <p class="aws-muted">
    These are the warnings real AWS shows on a fresh account. Fixing them
    removes the warning banner from every page in the console.
  </p>

  <h2 class="ec2-section-title">Critical warnings ({len(warnings)})</h2>
  {warning_cards}

  <h2 class="ec2-section-title">Service quotas</h2>
  <p class="aws-muted">
    Real AWS applies default limits per account per region. Approaching a limit
    slows down new resource creation and eventually returns an error like
    <code>VpcLimitExceeded</code>.
  </p>
  <table class="aws-table">
    <thead>
      <tr><th>Service</th><th>Resource</th><th>Used / Limit</th>
          <th>Usage</th><th>%</th><th>Status</th></tr>
    </thead>
    <tbody>{quota_rows}</tbody>
  </table>

  <div class="aws-notice aws-notice-info" style="margin-top:24px;">
    <strong>Real AWS note:</strong> quotas are region-scoped and can be increased
    by requesting a limit increase from the Support console. The VPC limit
    (5 per region by default) is one of the most common beginner surprises.
  </div>
</section>"""


# ---------- POST handler ----------

def handle(path, form, files=None):
    if path == "/security/dismiss":
        return _dismiss(form)
    return None


def _dismiss(form):
    key = (form.get("key") or "").strip()
    if not key:
        return ("redirect", "/security?error=missing+key")
    ok_, msg = security.dismiss(key)
    if ok_:
        return ("redirect", "/security?ok=" + urllib.parse.quote(msg))
    return ("redirect", "/security?error=" + urllib.parse.quote(msg))
