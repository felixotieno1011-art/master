"""Placeholder pages for header links — AWS-faithful 'not simulated' pages."""
import html


def _esc(s):
    return html.escape(str(s))


def render_cloudshell(qs=None):
    return """
<section class="aws-section">
  <h1>CloudShell</h1>
  <div class="aws-notice aws-notice-info">
    <strong>Not simulated.</strong> Real AWS CloudShell opens a browser-based
    bash terminal inside your AWS account, pre-authenticated with your credentials.
    MiniAWS gives you the same terminal experience on your phone via <strong>Termux</strong> —
    just switch apps.
  </div>
  <p class="aws-muted">Try in Termux: <code>./aws sts get-caller-identity</code></p>
</section>"""


def render_notifications(qs=None):
    return """
<section class="aws-section">
  <h1>Notifications</h1>
  <table class="aws-table">
    <thead><tr><th>Type</th><th>Message</th><th>Date</th></tr></thead>
    <tbody>
      <tr>
        <td><span class="aws-notice-warn" style="padding:2px 8px; border-radius:10px;">Security</span></td>
        <td>MFA is not enabled on the root account.</td>
        <td>Just now</td>
      </tr>
      <tr>
        <td><span class="aws-notice-warn" style="padding:2px 8px; border-radius:10px;">Security</span></td>
        <td>Root account access keys should be rotated or deleted.</td>
        <td>Just now</td>
      </tr>
    </tbody>
  </table>
  <p class="aws-muted s3-footer-hint">
    These match the two most common security warnings you'll see on a fresh
    real AWS account. Resolving them in real AWS requires enabling MFA and
    deleting root access keys.
  </p>
</section>"""


def render_billing(qs=None):
    # Import here so we don't crash if billing is unavailable
    try:
        from lib import billing
        total = float(billing.get_total())
    except Exception:
        total = 0.0

    return f"""
<section class="aws-section">
  <h1>Billing and Cost Management</h1>
  <p class="aws-muted">
    Equivalent to <code>aws billing show</code>. MiniAWS tracks simulated charges
    in <code>state/billing.json</code>.
  </p>
  <div class="cw-tiles-grid" style="margin: 16px 0;">
    <div class="cw-tile" style="cursor:default;">
      <div class="cw-tile-label">Month-to-date</div>
      <div class="cw-tile-num">${total:,.4f}</div>
      <div class="cw-tile-sub">simulated total</div>
    </div>
    <div class="cw-tile" style="cursor:default;">
      <div class="cw-tile-label">Forecast</div>
      <div class="cw-tile-num">${total * 30:,.2f}</div>
      <div class="cw-tile-sub">at current rate</div>
    </div>
    <div class="cw-tile" style="cursor:default;">
      <div class="cw-tile-label">Free tier</div>
      <div class="cw-tile-num">in use</div>
      <div class="cw-tile-sub">simulated</div>
    </div>
  </div>
  <h2 class="ec2-section-title">Top services by cost</h2>
  <table class="aws-table">
    <thead><tr><th>Service</th><th>Cost</th></tr></thead>
    <tbody>
      <tr><td>EC2</td><td>${total * 0.60:,.4f}</td></tr>
      <tr><td>VPC</td><td>${total * 0.25:,.4f}</td></tr>
      <tr><td>S3</td><td>${total * 0.10:,.4f}</td></tr>
      <tr><td>Other</td><td>${total * 0.05:,.4f}</td></tr>
    </tbody>
  </table>
  <div class="aws-notice aws-notice-warn" style="margin-top:16px;">
    <strong>Real AWS note:</strong> billing is the biggest surprise for beginners.
    Real AWS charges by the second (with a 60-second minimum for EC2), by the GB (S3),
    by request count (Lambda, DynamoDB), and by GB-hour (RDS). Setup a billing alarm
    on day 1: <em>Billing → Budgets → Create budget → Zero-spend</em>.
  </div>
</section>"""


def render_support(qs=None):
    return """
<section class="aws-section">
  <h1>Support</h1>
  <div class="aws-notice aws-notice-info">
    <strong>Not simulated.</strong> Real AWS Support is a paid tier:
    Basic (free), Developer ($29/mo), Business ($100/mo), Enterprise ($15,000+/mo).
  </div>
</section>"""
