"""Billing console — month-to-date, cost chart, top services, budgets."""
import html
from collections import defaultdict
from datetime import datetime, timedelta

from core.webui import aws_ref
from core.webui import billing_store


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


def _load_events():
    try:
        from lib import billing as _billing
        data = _billing._load()
        return data.get("events", []), float(data.get("total", 0.0))
    except Exception:
        return [], 0.0


def _service_from_key(key):
    """'ec2.run-instances.t3.micro' → 'ec2'"""
    return (key or "").split(".")[0] or "other"


def _human_date(iso):
    if not iso:
        return "—"
    try:
        dt = datetime.fromisoformat(str(iso).replace("Z", ""))
        return dt.strftime("%Y-%m-%d %H:%M")
    except Exception:
        return str(iso)


def _daily_by_service(events, days=30):
    """Return {date_str: {service: amount}} for the last `days` days."""
    today = datetime.now().date()
    start = today - timedelta(days=days - 1)
    buckets = defaultdict(lambda: defaultdict(float))

    for e in events:
        ts = e.get("time", "")
        try:
            d = datetime.fromisoformat(ts).date()
        except Exception:
            continue
        if d < start or d > today:
            continue
        svc = _service_from_key(e.get("key"))
        buckets[d.strftime("%Y-%m-%d")][svc] += float(e.get("amount", 0))

    # Fill in missing days
    ordered = []
    for i in range(days):
        day = (start + timedelta(days=i)).strftime("%Y-%m-%d")
        ordered.append((day, dict(buckets.get(day, {}))))
    return ordered


def _stacked_chart(events, days=30, width=720, height=240):
    """Stacked bar chart of daily cost by service — real Cost Explorer style."""
    daily = _daily_by_service(events, days=days)

    # Compute max daily total across all days for y-axis scaling
    totals = [sum(day_data.values()) for _, day_data in daily]
    if not totals or max(totals) == 0:
        return '<div class="aws-muted" style="padding:24px;">No billable activity in the last 30 days.</div>'
    vmax = max(totals) or 1.0

    # Service ordering: use aws_ref.SERVICE_COLORS keys that appear
    seen_services = set()
    for _, day_data in daily:
        seen_services.update(day_data.keys())
    service_order = [s for s in aws_ref.SERVICE_COLORS.keys() if s in seen_services]
    # Any extra services not in colors dict → gray
    for s in seen_services:
        if s not in service_order:
            service_order.append(s)

    pad_l, pad_r, pad_t, pad_b = 56, 12, 16, 32
    plot_w = width - pad_l - pad_r
    plot_h = height - pad_t - pad_b
    bar_w = plot_w / days
    gap = max(1, bar_w * 0.15)

    bars = []
    for i, (day, day_data) in enumerate(daily):
        x = pad_l + i * bar_w + gap / 2
        y_base = pad_t + plot_h
        cumulative = 0.0
        for svc in service_order:
            amt = day_data.get(svc, 0)
            if amt <= 0:
                continue
            h = (amt / vmax) * plot_h
            color = aws_ref.service_color(svc)["primary"]
            y_top = y_base - (cumulative + amt) / vmax * plot_h
            bar_h = (amt / vmax) * plot_h
            bars.append(
                f'<rect x="{x:.1f}" y="{y_top:.1f}" width="{bar_w - gap:.1f}" '
                f'height="{bar_h:.1f}" fill="{color}" '
                f'><title>{_esc(day)} · {_esc(svc)}: ${amt:.4f}</title></rect>'
            )
            cumulative += amt

    # Y-axis gridlines + labels
    y_ticks = []
    for frac in (0, 0.25, 0.5, 0.75, 1.0):
        y = pad_t + plot_h * (1 - frac)
        val = vmax * frac
        y_ticks.append(
            f'<line x1="{pad_l}" y1="{y:.1f}" x2="{width - pad_r}" y2="{y:.1f}" '
            f'stroke="#e9ebed" stroke-width="1"/>'
            f'<text x="{pad_l - 6}" y="{y + 4:.1f}" font-size="10" '
            f'fill="#687078" text-anchor="end">${val:.2f}</text>'
        )

    # X-axis first/last dates
    x_labels = (
        f'<text x="{pad_l}" y="{height - 8}" font-size="10" fill="#687078">'
        f'{_esc(daily[0][0])}</text>'
        f'<text x="{width - pad_r}" y="{height - 8}" font-size="10" '
        f'fill="#687078" text-anchor="end">{_esc(daily[-1][0])}</text>'
    )

    # Legend
    legend_parts = []
    for svc in service_order:
        color = aws_ref.service_color(svc)["primary"]
        total = sum(d.get(svc, 0) for _, d in daily)
        legend_parts.append(
            f'<span class="billing-legend-item">'
            f'<span class="billing-legend-swatch" style="background:{color};"></span>'
            f'{_esc(svc.upper())} <span class="aws-muted">${total:.4f}</span></span>'
        )

    svg = f'''
<svg viewBox="0 0 {width} {height}" class="billing-chart"
     xmlns="http://www.w3.org/2000/svg" style="width:100%; height:auto;">
  {"".join(y_ticks)}
  {"".join(bars)}
  {x_labels}
</svg>
<div class="billing-legend">{"".join(legend_parts)}</div>'''

    return svg


def _top_services(events):
    """Return list of {service, cost, pct} sorted desc."""
    totals = defaultdict(float)
    for e in events:
        totals[_service_from_key(e.get("key"))] += float(e.get("amount", 0))
    grand = sum(totals.values()) or 1.0
    rows = []
    for svc, amt in sorted(totals.items(), key=lambda x: -x[1]):
        rows.append({
            "service": svc,
            "cost": amt,
            "pct": (amt / grand) * 100.0,
        })
    return rows


# ---------- Main billing page ----------

def render_billing(qs=None):
    flash = _flash(qs)
    events, total = _load_events()

    # Forecast
    now = datetime.now()
    days_elapsed = max(now.day, 1)
    import calendar
    days_in_month = calendar.monthrange(now.year, now.month)[1]
    forecast = (total / days_elapsed) * days_in_month

    chart = _stacked_chart(events, days=30)
    top = _top_services(events)
    budgets = billing_store.budget_status()

    top_rows = "".join(f"""
    <tr>
      <td>{_esc(row['service'].upper())}</td>
      <td>${row['cost']:.4f}</td>
      <td>{row['pct']:.1f}%</td>
      <td>
        <div class="billing-bar-track">
          <div class="billing-bar-fill" style="width:{row['pct']:.1f}%;
               background:{aws_ref.service_color(row['service'])['primary']};"></div>
        </div>
      </td>
    </tr>""" for row in top) or \
        '<tr><td colspan="4" class="aws-muted">No charges yet.</td></tr>'

    if budgets:
        budget_rows = "".join(f"""
        <tr>
          <td>{_esc(b['name'])}</td>
          <td>${b['amount']:.2f}</td>
          <td>${b['actual']:.4f}</td>
          <td>{b['percentage']:.1f}%</td>
          <td><span class="billing-budget-status billing-{b['status'].lower()}">{_esc(b['status'])}</span></td>
          <td>
            <form method="POST" action="/billing/budgets/delete" style="display:inline"
                  onsubmit="return confirm('Delete budget {_esc(b['name'])}?')">
              <input type="hidden" name="name" value="{_esc(b['name'])}">
              <button type="submit" class="aws-link-danger">Delete</button>
            </form>
          </td>
        </tr>""" for b in budgets)
        budget_block = f"""
<div class="s3-page-header" style="margin-bottom:8px;">
  <h2 class="ec2-section-title" style="margin:0;">Budgets ({len(budgets)})</h2>
  <a class="aws-button-primary" href="/billing/budgets/create">Create budget</a>
</div>
<table class="aws-table">
  <thead><tr><th>Name</th><th>Budget</th><th>Actual</th><th>%</th><th>Status</th><th>Actions</th></tr></thead>
  <tbody>{budget_rows}</tbody>
</table>"""
    else:
        budget_block = """
<div class="s3-page-header" style="margin-bottom:8px;">
  <h2 class="ec2-section-title" style="margin:0;">Budgets</h2>
  <a class="aws-button-primary" href="/billing/budgets/create">Create budget</a>
</div>
<div class="s3-empty">
  <p class="aws-muted">You don't have any budgets yet.</p>
  <p class="aws-muted">Real AWS recommends setting a budget on day 1 so you get
  alerted if spending spikes unexpectedly.</p>
</div>"""

    return f"""
<section class="aws-section">
  {flash}
  <div class="s3-page-header">
    <h1>Billing and Cost Management</h1>
    <div class="s3-page-actions">
      <a class="aws-button-secondary" href="/billing/costs">Cost Explorer</a>
      <a class="aws-button-secondary" href="/billing/free-tier">Free tier</a>
    </div>
  </div>

  <div class="cw-tiles-grid" style="margin:16px 0;">
    <div class="cw-tile" style="cursor:default;">
      <div class="cw-tile-label">Month-to-date</div>
      <div class="cw-tile-num">${total:,.4f}</div>
      <div class="cw-tile-sub">{len(events)} billable events</div>
    </div>
    <div class="cw-tile" style="cursor:default;">
      <div class="cw-tile-label">Forecast</div>
      <div class="cw-tile-num">${forecast:,.2f}</div>
      <div class="cw-tile-sub">if usage continues</div>
    </div>
    <div class="cw-tile" style="cursor:default;">
      <div class="cw-tile-label">Free tier</div>
      <div class="cw-tile-num">active</div>
      <div class="cw-tile-sub"><a href="/billing/free-tier">see details</a></div>
    </div>
  </div>

  <h2 class="ec2-section-title">Cost per day (last 30 days)</h2>
  {chart}

  <h2 class="ec2-section-title">Top services by cost</h2>
  <table class="aws-table">
    <thead><tr><th>Service</th><th>Cost</th><th>% of total</th><th>Share</th></tr></thead>
    <tbody>{top_rows}</tbody>
  </table>

  {budget_block}

  <div class="aws-notice aws-notice-warn" style="margin-top:24px;">
    <strong>Why this page matters in real AWS:</strong>
    Unlike MiniAWS, real AWS charges by the second, by the GB, by the request,
    and by the hour. The three most expensive beginner mistakes:
    <ol style="margin:8px 0 0 20px; padding-left:0;">
      <li><strong>NAT gateway left on</strong> — ~$0.045/hour = <strong>$32/month</strong> (look at your VPC cost above!)</li>
      <li><strong>EC2 instance left running</strong> — a t3.micro 24/7 is ~$7.50/month</li>
      <li><strong>Elastic IP not attached</strong> — ~$0.005/hour = $3.60/month</li>
    </ol>
  </div>
</section>"""


# ---------- Cost Explorer ----------

def render_costs(qs=None):
    flash = _flash(qs)
    events, total = _load_events()

    # Group by service → count events, sum cost
    by_svc = defaultdict(lambda: {"count": 0, "cost": 0.0, "actions": defaultdict(int)})
    for e in events:
        svc = _service_from_key(e.get("key"))
        amt = float(e.get("amount", 0))
        by_svc[svc]["count"] += 1
        by_svc[svc]["cost"] += amt
        by_svc[svc]["actions"][e.get("key")] += 1

    grand = sum(v["cost"] for v in by_svc.values()) or 1.0

    svc_blocks = []
    for svc, d in sorted(by_svc.items(), key=lambda x: -x[1]["cost"]):
        color = aws_ref.service_color(svc)["primary"]
        action_rows = "".join(
            f'<tr><td><code>{_esc(action)}</code></td><td>{n}</td>'
            f'<td>${amt:.6f}</td></tr>'
            for action, n in sorted(d["actions"].items(), key=lambda x: -x[1])[:10]
        ) if False else ""
        # Rebuild action rows properly with per-action amounts
        action_amounts = defaultdict(float)
        for e in events:
            if _service_from_key(e.get("key")) == svc:
                action_amounts[e.get("key")] += float(e.get("amount", 0))
        action_rows = "".join(
            f'<tr>'
            f'<td><code>{_esc(action)}</code></td>'
            f'<td>{d["actions"][action]}</td>'
            f'<td>${action_amounts[action]:.6f}</td>'
            f'</tr>'
            for action in sorted(action_amounts, key=lambda a: -action_amounts[a])[:10]
        )

        svc_blocks.append(f"""
<h2 class="ec2-section-title">
  <span style="display:inline-block; width:12px; height:12px;
               background:{color}; border-radius:2px; margin-right:8px;
               vertical-align:middle;"></span>
  {_esc(svc.upper())} — ${d['cost']:.4f} ({d['cost'] / grand * 100:.1f}%, {d['count']} events)
</h2>
<table class="aws-table">
  <thead><tr><th>Action key</th><th>Count</th><th>Cost</th></tr></thead>
  <tbody>{action_rows}</tbody>
</table>""")

    return f"""
<section class="aws-section">
  {flash}
  <div class="s3-page-header">
    <h1>Cost Explorer</h1>
    <div class="s3-page-actions">
      <a class="aws-button-secondary" href="/billing">&#8592; Billing</a>
    </div>
  </div>
  <p class="aws-muted">Every billable action in <code>state/billing.json</code>,
  grouped by service.</p>

  <div class="cw-tiles-grid" style="margin:16px 0;">
    <div class="cw-tile" style="cursor:default;">
      <div class="cw-tile-label">Total charges</div>
      <div class="cw-tile-num">${total:,.4f}</div>
    </div>
    <div class="cw-tile" style="cursor:default;">
      <div class="cw-tile-label">Events</div>
      <div class="cw-tile-num">{len(events)}</div>
    </div>
    <div class="cw-tile" style="cursor:default;">
      <div class="cw-tile-label">Services with charges</div>
      <div class="cw-tile-num">{len([s for s in by_svc if by_svc[s]['cost'] > 0])}</div>
    </div>
  </div>

  {"".join(svc_blocks) if svc_blocks else '<div class="s3-empty"><p class="aws-muted">No charges yet.</p></div>'}
</section>"""


# ---------- Free tier ----------

FREE_TIER_LIMITS = [
    # (service, metric, limit, unit, count_from_key)
    ("EC2", "Instance hours (t3.micro)", 750, "hours/month", "ec2."),
    ("S3", "PUT requests", 2000, "PUT/month", "s3.upload"),
    ("S3", "Buckets created", 100, "buckets/month", "s3.mb-bucket"),
    ("Lambda", "Invocations", 1000000, "invocations/month", "lambda.invoke"),
    ("DynamoDB", "Write units", 2500000, "writes/month", "dynamodb.write"),
    ("CloudWatch", "Custom metrics", 10, "metrics/month", "cloudwatch.metric"),
]


def render_free_tier(qs=None):
    flash = _flash(qs)
    events, _ = _load_events()

    # Count usage per metric
    counts = defaultdict(int)
    for e in events:
        key = e.get("key", "")
        for _, metric, _, _, prefix in FREE_TIER_LIMITS:
            if key == prefix or key.startswith(prefix):
                counts[metric] += int(e.get("quantity", 1))

    rows = []
    any_exceeded = False
    for service, metric, limit, unit, prefix in FREE_TIER_LIMITS:
        used = counts.get(metric, 0)
        exceeded = used > limit
        if exceeded:
            any_exceeded = True
        status = '<span class="billing-budget-status billing-over_budget">EXCEEDED</span>' if exceeded \
                 else '<span class="billing-budget-status billing-ok">WITHIN LIMIT</span>'
        pct = (used / limit * 100) if limit else 0
        bar_color = "#d13212" if exceeded else "#037f0c"
        rows.append(f"""
        <tr>
          <td>{_esc(service)}</td>
          <td>{_esc(metric)}</td>
          <td>{used:,} of {limit:,} {_esc(unit)}</td>
          <td>
            <div class="billing-bar-track">
              <div class="billing-bar-fill"
                   style="width:{min(pct, 100):.1f}%; background:{bar_color};"></div>
            </div>
          </td>
          <td>{status}</td>
        </tr>""")

    warning = ""
    if any_exceeded:
        warning = """
<div class="aws-notice aws-notice-warn">
  <strong>⚠️ Free tier exceeded</strong> on at least one metric. Real AWS
  would now charge you for the overage on that service.
</div>"""

    return f"""
<section class="aws-section">
  {flash}
  <div class="s3-page-header">
    <h1>Free Tier</h1>
    <div class="s3-page-actions">
      <a class="aws-button-secondary" href="/billing">&#8592; Billing</a>
    </div>
  </div>
  {warning}
  <p class="aws-muted">
    Real AWS gives every new account 12 months of free tier usage
    on common services, plus some always-free limits. These are the
    monthly limits most relevant to a beginner.
  </p>
  <table class="aws-table">
    <thead>
      <tr><th>Service</th><th>Usage type</th><th>Used / Limit</th>
          <th>Progress</th><th>Status</th></tr>
    </thead>
    <tbody>{"".join(rows)}</tbody>
  </table>

  <div class="aws-notice aws-notice-info" style="margin-top:24px;">
    <strong>Real AWS note:</strong> free tier limits reset on the 1st of each month
    (UTC). Real AWS also has 12-month limits for new accounts — after 12 months,
    even a "free tier eligible" resource starts billing.
    <br><br>
    Always confirm a resource is free tier eligible before launching.
    Check <a href="https://aws.amazon.com/free/" target="_blank" rel="noopener">
    aws.amazon.com/free</a> for the current limits.
  </div>
</section>"""


# ---------- Budget wizard ----------

def render_create_budget(qs=None):
    flash = _flash(qs)
    return f"""
<section class="aws-section">
  {flash}
  <div class="wizard-header">
    <h1>Create budget</h1>
    <p class="aws-muted">Same 2-step shape as real AWS → Budgets → Create budget.</p>
  </div>
  <form method="POST" action="/billing/budgets/create">
    <div class="wizard-panel active">
      <div class="wizard-field">
        <label for="name">Budget name</label>
        <input id="name" name="name" type="text" required
               placeholder="Monthly spending" pattern="[a-zA-Z0-9 _\\-]{{1,63}}">
      </div>
      <div class="wizard-field">
        <label>Budget type</label>
        <select disabled><option>Cost budget (recommended)</option></select>
        <p class="aws-muted wizard-hint">Only cost budgets are simulated.</p>
      </div>
      <div class="wizard-field">
        <label for="amount">Monthly budget amount (USD)</label>
        <input id="amount" name="amount" type="number" step="0.01" min="0.01"
               required placeholder="5.00">
      </div>
      <div class="wizard-field">
        <label>Alert threshold</label>
        <select disabled><option>80% of budget (simulated)</option></select>
      </div>
      <div class="wizard-actions">
        <button type="submit" class="aws-button-primary">Create budget</button>
        <a class="aws-button-secondary" href="/billing">Cancel</a>
      </div>
    </div>
  </form>
</section>"""
