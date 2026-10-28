"""CloudWatch pages — overview, alarms, metrics with sparkline, log groups."""
import html
from datetime import datetime

from core import cloudwatch as cw


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


def _alarm_pill(state):
    s = (state or "INSUFFICIENT_DATA").upper()
    cls = {"OK": "cw-pill-ok", "ALARM": "cw-pill-alarm",
           "INSUFFICIENT_DATA": "cw-pill-insufficient"}.get(s, "cw-pill-insufficient")
    return f'<span class="cw-pill {cls}">{_esc(s)}</span>'


def _human_date(iso):
    if not iso:
        return "—"
    try:
        dt = datetime.fromisoformat(str(iso).replace("Z", ""))
        return dt.strftime("%Y-%m-%d %H:%M:%S")
    except Exception:
        return str(iso)


# ---------- SVG sparkline (real CloudWatch-style) ----------

def _sparkline(datapoints, width=640, height=180, threshold=None):
    """Render datapoints as an SVG line chart with fill-under."""
    if not datapoints:
        return '<div class="aws-muted">No datapoints.</div>'

    values = [float(d.get("value", 0)) for d in datapoints]
    vmin, vmax = min(values), max(values)
    if vmax == vmin:
        vmax = vmin + 1
        vmin = vmin - 1

    pad_l, pad_r, pad_t, pad_b = 48, 12, 12, 28
    plot_w = width - pad_l - pad_r
    plot_h = height - pad_t - pad_b

    n = len(values)
    def px(i):
        return pad_l + (plot_w * i / max(n - 1, 1))
    def py(v):
        return pad_t + plot_h * (1 - (v - vmin) / (vmax - vmin))

    points = " ".join(f"{px(i):.1f},{py(v):.1f}" for i, v in enumerate(values))
    area = f"M{px(0):.1f},{py(values[0]):.1f} " + \
           " ".join(f"L{px(i):.1f},{py(v):.1f}" for i, v in enumerate(values)) + \
           f" L{px(n-1):.1f},{pad_t+plot_h:.1f} L{px(0):.1f},{pad_t+plot_h:.1f} Z"

    # Threshold line
    thresh_svg = ""
    if threshold is not None and vmin <= float(threshold) <= vmax:
        ty = py(float(threshold))
        thresh_svg = (f'<line x1="{pad_l}" y1="{ty:.1f}" x2="{width-pad_r}" y2="{ty:.1f}" '
                      f'stroke="#d13212" stroke-width="1" stroke-dasharray="4 2"/>'
                      f'<text x="{width-pad_r-4}" y="{ty-4:.1f}" font-size="10" '
                      f'fill="#d13212" text-anchor="end">threshold {threshold}</text>')

    # Y-axis labels (min/mid/max)
    mid = (vmin + vmax) / 2
    y_labels = "".join(
        f'<text x="{pad_l-6}" y="{py(val)+4:.1f}" font-size="10" '
        f'fill="#687078" text-anchor="end">{val:.1f}</text>'
        for val in (vmax, mid, vmin)
    )

    # X-axis first/last timestamps
    first_ts = datapoints[0].get("timestamp", "")[-8:-3] or ""
    last_ts = datapoints[-1].get("timestamp", "")[-8:-3] or ""
    x_labels = (
        f'<text x="{pad_l}" y="{height-8}" font-size="10" fill="#687078">{_esc(first_ts)}</text>'
        f'<text x="{width-pad_r}" y="{height-8}" font-size="10" fill="#687078" '
        f'text-anchor="end">{_esc(last_ts)}</text>'
    )

    # Dots on each datapoint
    dots = "".join(
        f'<circle cx="{px(i):.1f}" cy="{py(v):.1f}" r="2" fill="#0073bb"/>'
        for i, v in enumerate(values)
    )

    return f"""
<svg class="cw-chart" viewBox="0 0 {width} {height}" xmlns="http://www.w3.org/2000/svg"
     style="width:100%; height:auto;">
  <line x1="{pad_l}" y1="{pad_t}" x2="{pad_l}" y2="{pad_t+plot_h}"
        stroke="#d5dbdb" stroke-width="1"/>
  <line x1="{pad_l}" y1="{pad_t+plot_h}" x2="{width-pad_r}" y2="{pad_t+plot_h}"
        stroke="#d5dbdb" stroke-width="1"/>
  {thresh_svg}
  <path d="{area}" fill="#0073bb" fill-opacity="0.12"/>
  <polyline points="{points}" fill="none" stroke="#0073bb" stroke-width="2"/>
  {dots}
  {y_labels}
  {x_labels}
</svg>"""


# ---------- Overview ----------

def render_overview(qs=None):
    flash = _flash(qs)
    try:
        alarms = cw.list_alarms()
        metrics = cw.list_metrics()
        log_groups = cw.describe_log_groups()
    except Exception as e:
        return f'<div class="aws-notice aws-notice-error">Error: {_esc(e)}</div>'

    alarm_in_state = sum(1 for a in alarms
                         if (a.get("stateValue") or "").upper() == "ALARM")
    dp_total = sum(m.get("datapoints", 0) for m in metrics)

    def _tile(label, val, sub, href):
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
    <h1>CloudWatch overview</h1>
  </div>
  <div class="cw-tiles-grid">
    {_tile("Alarms", len(alarms),
           f"{alarm_in_state} in ALARM" if alarm_in_state else "all OK",
           "/cloudwatch/alarms")}
    {_tile("Metrics", len(metrics), f"{dp_total} datapoints", "/cloudwatch/metrics")}
    {_tile("Log groups", len(log_groups),
           f"{sum(g.get('event_count', 0) for g in log_groups)} events",
           "/cloudwatch/log-groups")}
  </div>

  <h2 class="ec2-section-title">Recent alarms</h2>
  {_alarms_table(alarms[:5], show_actions=False)}
</section>"""


def _alarms_table(alarms, show_actions=True):
    if not alarms:
        return '<p class="aws-muted">No alarms.</p>'
    rows = []
    for a in alarms:
        name = a.get("alarmName", "—")
        state = a.get("stateValue", "—")
        rows.append(f"""
        <tr>
          <td><a href="/cloudwatch/alarms/{_esc(name)}">{_esc(name)}</a></td>
          <td>{_alarm_pill(state)}</td>
          <td>{_esc(a.get('namespace','—'))}</td>
          <td>{_esc(a.get('metricName','—'))}</td>
          <td>{_esc(a.get('statistic','—'))}</td>
          <td>{a.get('threshold','—')}</td>
          <td>{_esc(a.get('comparisonOperator','—'))}</td>
          {'<td>-</td>' if not show_actions else f"""<td>
            <form method="POST" action="/cloudwatch/alarms/delete" style="display:inline"
                  onsubmit="return confirm('Delete alarm {_esc(name)}?')">
              <input type="hidden" name="name" value="{_esc(name)}">
              <button type="submit" class="aws-link-danger">Delete</button>
            </form>
          </td>"""}
        </tr>""")
    return f"""
<table class="aws-table">
  <thead>
    <tr>
      <th>Alarm name</th><th>State</th><th>Namespace</th><th>Metric</th>
      <th>Statistic</th><th>Threshold</th><th>Comparison</th>
      {'<th>Actions</th>' if show_actions else ''}
    </tr>
  </thead>
  <tbody>{"".join(rows)}</tbody>
</table>"""


def render_alarms(qs=None):
    flash = _flash(qs)
    try:
        alarms = cw.list_alarms()
    except Exception as e:
        return f'<div class="aws-notice aws-notice-error">Error: {_esc(e)}</div>'

    return f"""
<section class="aws-section">
  {flash}
  <div class="s3-page-header">
    <h1>Alarms <span class="aws-muted">({len(alarms)})</span></h1>
    <div class="s3-page-actions">
      <a class="aws-button-primary" href="/cloudwatch/alarms/create">Create alarm</a>
      <form method="POST" action="/cloudwatch/alarms/evaluate" style="display:inline">
        <button type="submit" class="aws-button-secondary">Evaluate now</button>
      </form>
    </div>
  </div>
  {_alarms_table(alarms)}
</section>"""


def render_alarm_detail(name, qs=None):
    alarm = None
    for a in cw.list_alarms():
        if a.get("alarmName") == name:
            alarm = a
            break
    if not alarm:
        return f'<div class="aws-notice aws-notice-error">Alarm not found: {_esc(name)}</div>'

    flash = _flash(qs)

    # Fetch metric datapoints for chart
    try:
        d = cw._get_datapoints(alarm["namespace"], alarm["metricName"])
    except Exception:
        d = []
    chart = _sparkline(d, threshold=alarm.get("threshold"))

    return f"""
<section class="aws-section">
  {flash}
  <div class="s3-page-header">
    <h1>{_esc(name)} <span style="margin-left:8px;">{_alarm_pill(alarm.get('stateValue'))}</span></h1>
    <div class="s3-page-actions">
      <a class="aws-button-secondary" href="/cloudwatch/alarms">&#8592; Alarms</a>
    </div>
  </div>

  <table class="aws-table" style="margin-bottom:16px;">
    <tbody>
      <tr><th style="width:30%;">State reason</th><td>{_esc(alarm.get('stateReason','—'))}</td></tr>
      <tr><th>Namespace</th><td><code>{_esc(alarm.get('namespace'))}</code></td></tr>
      <tr><th>Metric</th><td><a href="/cloudwatch/metrics/{_esc(alarm.get('namespace'))}/{_esc(alarm.get('metricName'))}"><code>{_esc(alarm.get('metricName'))}</code></a></td></tr>
      <tr><th>Statistic</th><td>{_esc(alarm.get('statistic'))}</td></tr>
      <tr><th>Threshold</th><td>{alarm.get('threshold')}</td></tr>
      <tr><th>Comparison</th><td>{_esc(alarm.get('comparisonOperator'))}</td></tr>
      <tr><th>Evaluation periods</th><td>{alarm.get('evaluationPeriods', 1)}</td></tr>
      <tr><th>Created</th><td>{_esc(_human_date(alarm.get('created')))}</td></tr>
      <tr><th>State updated</th><td>{_esc(_human_date(alarm.get('stateUpdated')))}</td></tr>
    </tbody>
  </table>

  <h2 class="ec2-section-title">Metric graph — {_esc(alarm.get('metricName'))}</h2>
  {chart}

  <div class="ec2-action-row" style="margin-top:16px;">
    <form method="POST" action="/cloudwatch/alarms/delete" style="display:inline"
          onsubmit="return confirm('Delete alarm {_esc(name)}?')">
      <input type="hidden" name="name" value="{_esc(name)}">
      <button type="submit" class="aws-button-danger">Delete alarm</button>
    </form>
  </div>
</section>"""


# ---------- Metrics ----------

def render_metrics(qs=None):
    flash = _flash(qs)
    try:
        metrics = cw.list_metrics()
    except Exception as e:
        return f'<div class="aws-notice aws-notice-error">Error: {_esc(e)}</div>'

    rows = "".join(f"""
    <tr>
      <td><a href="/cloudwatch/metrics/{_esc(m['namespace'])}/{_esc(m['metricName'])}"><code>{_esc(m['namespace'])}</code></a></td>
      <td><code>{_esc(m['metricName'])}</code></td>
      <td>{m.get('datapoints', 0)}</td>
      <td>{_esc(m.get('unit', 'None'))}</td>
    </tr>""" for m in metrics) or \
        '<tr><td colspan="4" class="aws-muted" style="text-align:center; padding:24px;">No metrics. Publish one with <code>aws cloudwatch put-metric-data</code>.</td></tr>'

    return f"""
<section class="aws-section">
  {flash}
  <div class="s3-page-header">
    <h1>All metrics <span class="aws-muted">({len(metrics)})</span></h1>
  </div>
  <table class="aws-table">
    <thead><tr><th>Namespace</th><th>Metric</th><th>Datapoints</th><th>Unit</th></tr></thead>
    <tbody>{rows}</tbody>
  </table>
</section>"""


def render_metric_detail(namespace, metric_name, qs=None):
    datapoints = cw._get_datapoints(namespace, metric_name)
    if not datapoints:
        return f'<div class="aws-notice aws-notice-error">No datapoints for {_esc(namespace)}/{_esc(metric_name)}</div>'

    try:
        stats = cw.get_metric_statistics(namespace, metric_name, stat="Average")
    except Exception:
        stats = {}

    chart = _sparkline(datapoints)

    last_n = datapoints[-10:]
    rows = "".join(f"""
    <tr>
      <td>{_esc(dp.get('timestamp','—'))}</td>
      <td>{dp.get('value','—')}</td>
    </tr>""" for dp in reversed(last_n))

    return f"""
<section class="aws-section">
  <div class="s3-page-header">
    <h1>{_esc(metric_name)} <span class="aws-muted">({_esc(namespace)})</span></h1>
    <div class="s3-page-actions">
      <a class="aws-button-secondary" href="/cloudwatch/metrics">&#8592; Metrics</a>
    </div>
  </div>

  <table class="aws-table" style="margin-bottom:16px;">
    <tbody>
      <tr><th style="width:30%;">Namespace</th><td><code>{_esc(namespace)}</code></td></tr>
      <tr><th>Metric name</th><td><code>{_esc(metric_name)}</code></td></tr>
      <tr><th>Datapoints</th><td>{len(datapoints)}</td></tr>
      {f'<tr><th>Average</th><td>{stats.get("value")}</td></tr>' if stats else ''}
      {f'<tr><th>Sample count</th><td>{stats.get("sampleCount")}</td></tr>' if stats else ''}
    </tbody>
  </table>

  <h2 class="ec2-section-title">Metric graph</h2>
  {chart}

  <h2 class="ec2-section-title">Recent datapoints</h2>
  <table class="aws-table">
    <thead><tr><th>Timestamp</th><th>Value</th></tr></thead>
    <tbody>{rows}</tbody>
  </table>
</section>"""


# ---------- Log groups ----------

def render_log_groups(qs=None):
    flash = _flash(qs)
    try:
        groups = cw.describe_log_groups()
    except Exception as e:
        return f'<div class="aws-notice aws-notice-error">Error: {_esc(e)}</div>'

    rows = "".join(f"""
    <tr>
      <td><a href="/cloudwatch/log-groups/{_esc(g['log_group'] if 'log_group' in g else g.get('logGroupName', g.get('name','')))}">
        <code>{_esc(g.get('log_group') or g.get('logGroupName') or g.get('name',''))}</code></a></td>
      <td>{g.get('event_count', g.get('storedBytes', '—'))}</td>
      <td>Never expire</td>
    </tr>""" for g in groups) or \
        '<tr><td colspan="3" class="aws-muted" style="text-align:center; padding:24px;">No log groups.</td></tr>'

    return f"""
<section class="aws-section">
  {flash}
  <div class="s3-page-header">
    <h1>Log groups <span class="aws-muted">({len(groups)})</span></h1>
    <div class="s3-page-actions">
      <a class="aws-button-primary" href="/cloudwatch/log-groups/create">Create log group</a>
    </div>
  </div>
  <table class="aws-table">
    <thead><tr><th>Log group name</th><th>Events</th><th>Retention</th></tr></thead>
    <tbody>{rows}</tbody>
  </table>
</section>"""


def render_log_group_detail(name, qs=None):
    flash = _flash(qs)
    try:
        events = cw.get_log_events(name, limit=100)
    except Exception:
        events = []

    rows = "".join(f"""
    <tr>
      <td style="width:200px; white-space:nowrap;">{_esc(ev.get('timestamp','—'))}</td>
      <td style="font-family:monospace; font-size:12px;">{_esc(ev.get('message',''))}</td>
    </tr>""" for ev in (events if isinstance(events, list) else [])) or \
        '<tr><td colspan="2" class="aws-muted">No events.</td></tr>'

    return f"""
<section class="aws-section">
  {flash}
  <div class="s3-page-header">
    <h1><code>{_esc(name)}</code></h1>
    <div class="s3-page-actions">
      <a class="aws-button-secondary" href="/cloudwatch/log-groups">&#8592; Log groups</a>
    </div>
  </div>
  <h2 class="ec2-section-title">Log events ({len(events) if isinstance(events, list) else 0})</h2>
  <table class="aws-table">
    <thead><tr><th>Timestamp</th><th>Message</th></tr></thead>
    <tbody>{rows}</tbody>
  </table>
</section>"""


# ---------- Wizards ----------

def render_create_alarm(qs=None):
    flash = _flash(qs)
    metrics = cw.list_metrics()
    metric_opts = "".join(
        f'<option value="{_esc(m["namespace"])}|{_esc(m["metricName"])}">'
        f'{_esc(m["namespace"])} / {_esc(m["metricName"])}</option>'
        for m in metrics
    ) or '<option value="">(no metrics available — publish one first)</option>'

    return f"""
<section class="aws-section">
  {flash}
  <div class="wizard-header">
    <h1>Create alarm</h1>
    <p class="aws-muted">Same 4-step shape as the real CloudWatch alarm wizard.</p>
  </div>
  <form id="alarm-form" method="POST" action="/cloudwatch/alarms/create">
    <div class="wizard-step-tabs">
      <div class="wizard-step active" data-step="1">1. Specify metric</div>
      <div class="wizard-step" data-step="2">2. Conditions</div>
      <div class="wizard-step" data-step="3">3. Notifications</div>
      <div class="wizard-step" data-step="4">4. Name &amp; review</div>
    </div>

    <div class="wizard-panel active" data-step="1">
      <div class="wizard-field">
        <label>Metric</label>
        <select id="metric" required>{metric_opts}</select>
        <p class="aws-muted wizard-hint">Namespace / Metric to monitor.</p>
      </div>
      <div class="wizard-field">
        <label>Statistic</label>
        <select id="statistic" name="statistic">
          <option value="Average">Average</option>
          <option value="Sum">Sum</option>
          <option value="Minimum">Minimum</option>
          <option value="Maximum">Maximum</option>
        </select>
      </div>
      <div class="wizard-actions">
        <button type="button" class="aws-button-primary" onclick="cwStep(2)">Next</button>
        <a class="aws-button-secondary" href="/cloudwatch/alarms">Cancel</a>
      </div>
    </div>

    <div class="wizard-panel" data-step="2">
      <div class="wizard-field">
        <label>Comparison operator</label>
        <select id="comparison" name="comparison">
          <option value="GreaterThanThreshold">Greater than threshold</option>
          <option value="GreaterThanOrEqualToThreshold">Greater/equal threshold</option>
          <option value="LessThanThreshold">Less than threshold</option>
          <option value="LessThanOrEqualToThreshold">Less/equal threshold</option>
        </select>
      </div>
      <div class="wizard-field">
        <label for="threshold">Threshold value</label>
        <input id="threshold" name="threshold" type="number" step="0.1" value="80" required>
      </div>
      <div class="wizard-field">
        <label for="periods">Evaluation periods</label>
        <input id="periods" name="periods" type="number" min="1" value="1">
      </div>
      <div class="wizard-actions">
        <button type="button" class="aws-button-primary" onclick="cwStep(3)">Next</button>
        <button type="button" class="aws-button-secondary" onclick="cwStep(1)">Back</button>
      </div>
    </div>

    <div class="wizard-panel" data-step="3">
      <div class="aws-notice aws-notice-info">
        <strong>Simulated.</strong> In real AWS you would add SNS topics, auto-scaling
        actions, or EC2 actions here. MiniAWS records only the alarm definition.
      </div>
      <div class="wizard-actions">
        <button type="button" class="aws-button-primary" onclick="cwStep(4)">Next</button>
        <button type="button" class="aws-button-secondary" onclick="cwStep(2)">Back</button>
      </div>
    </div>

    <div class="wizard-panel" data-step="4">
      <div class="wizard-field">
        <label for="alarm_name">Alarm name</label>
        <input id="alarm_name" name="name" type="text" required placeholder="HighCPUAlarm">
      </div>
      <table class="aws-table" style="margin-bottom:16px;">
        <tbody>
          <tr><th style="width:35%;">Metric</th><td><code id="rev-metric">—</code></td></tr>
          <tr><th>Statistic</th><td><span id="rev-stat">—</span></td></tr>
          <tr><th>Condition</th><td><code id="rev-cond">—</code></td></tr>
          <tr><th>Periods</th><td><span id="rev-periods">—</span></td></tr>
        </tbody>
      </table>
      <div class="wizard-actions">
        <button type="submit" class="aws-button-primary">Create alarm</button>
        <button type="button" class="aws-button-secondary" onclick="cwStep(3)">Back</button>
      </div>
    </div>
  </form>
  <script>
    function cwStep(n) {{
      if (n === 4) {{
        document.getElementById('rev-metric').textContent =
          document.getElementById('metric').value.replace('|', ' / ');
        document.getElementById('rev-stat').textContent =
          document.getElementById('statistic').value;
        document.getElementById('rev-cond').textContent =
          document.getElementById('comparison').value + ' ' +
          document.getElementById('threshold').value;
        document.getElementById('rev-periods').textContent =
          document.getElementById('periods').value;
      }}
      document.querySelectorAll('#alarm-form .wizard-panel').forEach(p =>
        p.classList.toggle('active', p.dataset.step == n));
      document.querySelectorAll('.wizard-step').forEach(p =>
        p.classList.toggle('active', p.dataset.step == n));
    }}
    // Wire up the metric <option> to split into namespace|metric at submit time
    document.getElementById('alarm-form').addEventListener('submit', function() {{
      const val = document.getElementById('metric').value;
      const [ns, m] = val.split('|');
      // Create hidden inputs so the server gets namespace + metric separately
      ['namespace', 'metric_name'].forEach((k, i) => {{
        const h = document.createElement('input');
        h.type = 'hidden';
        h.name = k;
        h.value = i === 0 ? ns : m;
        this.appendChild(h);
      }});
    }});
  </script>
</section>"""


def render_create_log_group(qs=None):
    flash = _flash(qs)
    return f"""
<section class="aws-section">
  {flash}
  <div class="wizard-header"><h1>Create log group</h1></div>
  <form method="POST" action="/cloudwatch/log-groups/create">
    <div class="wizard-panel active">
      <div class="wizard-field">
        <label for="name">Log group name</label>
        <input id="name" name="name" type="text" required
               placeholder="/aws/lambda/my-function">
        <p class="aws-muted wizard-hint">Real AWS uses forward slashes — e.g. <code>/aws/lambda/x</code>.</p>
      </div>
      <div class="wizard-actions">
        <button type="submit" class="aws-button-primary">Create log group</button>
        <a class="aws-button-secondary" href="/cloudwatch/log-groups">Cancel</a>
      </div>
    </div>
  </form>
</section>"""
