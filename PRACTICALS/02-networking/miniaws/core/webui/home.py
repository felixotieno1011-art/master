"""Console Home — what console.aws.amazon.com lands on."""
import html

from core import account
from core.webui import aws_ref, session

try:
    from lib import billing as _billing
    _BILLING_OK = True
except Exception:
    _BILLING_OK = False


def _esc(s):
    return html.escape(str(s))


def _tile(sid, name, desc, href, region_code):
    color = aws_ref.service_color(sid)
    # Use up to 2 initials (EC, S3, LA, DY, IA, CL, VP, ST) but prefer
    # recognizable 2-3 char abbreviations
    short = {"s3": "S3", "ec2": "EC", "lambda": "LA", "dynamodb": "DY",
             "iam": "IA", "cloudwatch": "CW", "vpc": "VP", "sts": "ST"}.get(
        sid, sid[:2].upper())
    return f"""
    <a class="service-tile" href="{_esc(session.with_region(href, region_code))}"
       style="border-left: 4px solid {color['primary']};">
      <div class="service-tile-icon"
           style="background: {color['bg']}; color: {color['primary']};
                  border: 2px solid {color['primary']};">{_esc(short)}</div>
      <div class="service-tile-body">
        <div class="service-tile-name">{_esc(name)}</div>
        <div class="service-tile-desc">{_esc(desc)}</div>
      </div>
    </a>"""


def _cost_panel():
    if not _BILLING_OK:
        return '<div class="aws-muted">Billing module unavailable.</div>'
    try:
        total = float(_billing.get_total())
    except Exception:
        total = 0.0
    return f"""
    <div class="home-cost">
      <div class="home-cost-label">Month-to-date</div>
      <div class="home-cost-value">${total:,.4f}</div>
    </div>"""


def _account_panel():
    s = account.summary()
    acct = s.get("account_id") or "(not initialized)"
    region_code = s.get("region", "us-east-1")
    region_human = s.get("region_name", region_code)
    return f"""
    <div class="home-account">
      <div class="home-account-row">
        <span class="home-account-label">Account</span>
        <span class="home-account-value"><code>{_esc(acct)}</code></span>
      </div>
      <div class="home-account-row">
        <span class="home-account-label">Region</span>
        <span class="home-account-value">{_esc(region_human)} <code class="aws-muted">({_esc(region_code)})</code></span>
      </div>
    </div>"""


def render(region_code):
    recent = session.recent_services()

    recent_block = ""
    if recent:
        recent_block = f"""
        <section class="aws-section">
          <h2>Recently visited</h2>
          <div class="service-grid">
            {''.join(_tile(sid, name, desc, href, region_code) for sid, name, desc, href in recent)}
          </div>
        </section>"""

    all_tiles = "".join(
        _tile(sid, name, desc, href, region_code)
        for sid, name, desc, href in aws_ref.SERVICES
    )

    return f"""
<section class="aws-section home-hero">
  <div class="home-hero-left">
    <h1>Welcome to MiniAWS</h1>
    <p class="aws-muted">
      A local, offline teaching simulator of the AWS Console.
      Same service names, same layout, same actions &mdash; no bill.
    </p>
  </div>
  <div class="home-hero-right">
    {_cost_panel()}
    {_account_panel()}
  </div>
</section>

{recent_block}

<section class="aws-section">
  <h2>All services</h2>
  <div class="service-grid">{all_tiles}</div>
</section>
"""
