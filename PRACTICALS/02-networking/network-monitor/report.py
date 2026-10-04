#!/usr/bin/env python3
"""Read logs, produce terminal report + HTML report.
Plain English + numbers together. Nothing removed.
"""
import csv
import html
import os
import statistics
import sys
from datetime import datetime

import config


# ---------- Data loading ----------

def load_csv():
    if not os.path.exists(config.LOG_CSV):
        return []
    rows = []
    with open(config.LOG_CSV) as f:
        for row in csv.DictReader(f):
            rows.append(row)
    return rows


def to_float(v):
    try:
        return float(v) if v not in ("", None) else None
    except Exception:
        return None


def group_by_isp(rows):
    groups = {}
    for r in rows:
        isp = r.get("isp", "unknown")
        groups.setdefault(isp, []).append(r)
    return groups


def isp_summary(rows):
    out = {}
    for isp, items in group_by_isp(rows).items():
        def vals(key):
            return [to_float(r.get(key)) for r in items
                    if to_float(r.get(key)) is not None]
        g = vals("google_avg")
        c = vals("cloudflare_avg")
        q = vals("quad9_avg")
        d = vals("download_mbps")
        u = vals("upload_mbps")
        losses = vals("google_loss")

        all_avg = g + c + q
        out[isp] = {
            "runs":         len(items),
            "avg_latency":  statistics.mean(all_avg) if all_avg else None,
            "avg_loss":     statistics.mean(losses) if losses else None,
            "avg_download": statistics.mean(d) if d else None,
            "avg_upload":   statistics.mean(u) if u else None,
        }
    return out


# ---------- Color helpers ----------

def cls_latency(v):
    if v is None: return "bad"
    if v < 100:   return "ok"
    if v < 200:   return "warn"
    return "bad"


def cls_speed(v):
    if v is None: return "bad"
    if v >= 5:    return "ok"
    if v >= 2:    return "warn"
    return "bad"


def cls_loss(v):
    if v is None: return "bad"
    if v <= 1:    return "ok"
    if v <= 5:    return "warn"
    return "bad"


def cls_dns(v):
    if v is None: return "bad"
    if v < 80:    return "ok"
    if v < 200:   return "warn"
    return "bad"


def cls_ttfb(v):
    if v is None: return "bad"
    if v < 500:   return "ok"
    if v < 1500:  return "warn"
    return "bad"


# ---------- Plain-English + number ----------
# Each function returns (css_class, number_string, explanation_string)

def human_latency(ms):
    if ms is None:
        return ("bad", "N/A", "No response — could not reach the internet")
    num = f"{ms:.0f} ms"
    if ms < 60:
        return ("ok", num, "Excellent — everything feels instant")
    if ms < 150:
        return ("ok", num, "Good — normal browsing speed")
    if ms < 300:
        return ("warn", num, "Slow — websites feel sluggish")
    return ("bad", num, "Very slow — likely hard to use")


def human_download(mbps):
    if mbps is None:
        return ("bad", "N/A", "Not measured")
    num = f"{mbps:.2f} Mbps"
    if mbps >= 25:
        return ("ok", num, "Great — 4K streaming, multiple devices at once")
    if mbps >= 10:
        return ("ok", num, "Good — HD streaming and video calls work well")
    if mbps >= 5:
        return ("warn", num, "OK — basic browsing, SD video, one device")
    return ("bad", num, "Slow — one device at a time, no HD video")


def human_upload(mbps):
    if mbps is None:
        return ("warn", "N/A", "Not measured")
    num = f"{mbps:.2f} Mbps"
    if mbps >= 5:
        return ("ok", num, "Great — HD video calls, cloud backup work")
    if mbps >= 2:
        return ("ok", num, "OK — video calls work fine")
    if mbps >= 1:
        return ("warn", num, "Slow — video calls may lag, uploads take time")
    return ("bad", num, "Very slow — sending files or video will be painful")


def human_dns(ms):
    if ms is None:
        return ("bad", "N/A", "Not measured")
    num = f"{ms:.0f} ms"
    if ms < 50:
        return ("ok", num, "Fast — websites start loading quickly")
    if ms < 150:
        return ("ok", num, "OK — acceptable speed")
    return ("warn", num, "Slow — every new site waits before loading")


def human_loss(pct):
    if pct is None:
        return ("ok", "0%", "No packet loss detected")
    num = f"{pct:.1f}%"
    if pct < 1:
        return ("ok", num, "Perfect — no drops")
    if pct < 5:
        return ("warn", num, "Minor drops — voice/video calls may glitch")
    return ("bad", num, "Frequent drops — calls and games will fail")


# ---------- Terminal report ----------

def print_terminal_report(rows):
    if not rows:
        print("❌ No data in logs/network_log.csv")
        print("   Run: python monitor.py")
        return

    print("=" * 65)
    print("📊 NETWORK REPORT")
    print(f"   Generated: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print(f"   Total runs: {len(rows)}")
    print("=" * 65)

    for isp, s in isp_summary(rows).items():
        print()
        print(f"📡 {isp}")
        print(f"   Runs:      {s['runs']}")
        if s["avg_latency"] is not None:
            print(f"   Latency:   {s['avg_latency']:.0f} ms (avg)")
        if s["avg_loss"] is not None:
            print(f"   Loss:      {s['avg_loss']:.1f}%")
        if s["avg_download"] is not None:
            print(f"   Download:  {s['avg_download']:.2f} Mbps")
        if s["avg_upload"] is not None:
            print(f"   Upload:    {s['avg_upload']:.2f} Mbps")

    summary = isp_summary(rows)
    if len(summary) >= 2:
        print()
        print("=" * 65)
        print("🏆 ISP COMPARISON")
        print("=" * 65)
        ranked = sorted(
            [(isp, s) for isp, s in summary.items()
             if s["avg_latency"] is not None],
            key=lambda x: x[1]["avg_latency"]
        )
        for i, (isp, s) in enumerate(ranked, 1):
            print(f"   {i}. {isp:<35} {s['avg_latency']:.0f} ms")


# ---------- HTML report ----------

def generate_html(rows):
    if not rows:
        return None

    latest = rows[-1]

    def f(v):
        try:
            return float(v) if v not in ("", None) else None
        except Exception:
            return None

    g   = f(latest.get("google_avg"))
    c   = f(latest.get("cloudflare_avg"))
    q   = f(latest.get("quad9_avg"))
    od  = f(latest.get("opendns_avg"))
    dl  = f(latest.get("download_mbps"))
    ul  = f(latest.get("upload_mbps"))
    gl  = f(latest.get("google_loss"))
    gj  = f(latest.get("google_jitter"))
    ts  = latest.get("timestamp", "")

    dns_def  = f(latest.get("dns_default_ms"))
    dns_g    = f(latest.get("dns_google_ms"))
    dns_cf   = f(latest.get("dns_cloudflare_ms"))
    http_g   = f(latest.get("http_google_ttfb"))
    http_cf  = f(latest.get("http_cloudflare_ttfb"))
    http_w   = f(latest.get("http_wikipedia_ttfb"))

    # Overall verdict
    near_avgs = [v for v in (g, c, q) if v is not None]
    avg_lat = sum(near_avgs) / len(near_avgs) if near_avgs else None

    if gl is not None and gl > 5:
        vcls, vicon, vtext = ("bad", "❌", "Unstable connection — high packet loss")
    elif dl is not None and dl < 2:
        vcls, vicon, vtext = ("bad", "❌", "Very slow internet")
    elif avg_lat is None:
        vcls, vicon, vtext = ("bad", "❌", "No internet connection")
    elif avg_lat < 100 and (dl or 0) >= 10:
        vcls, vicon, vtext = ("ok", "✓", "Your internet is working well")
    elif avg_lat < 200:
        vcls, vicon, vtext = ("warn", "⚠", "Your internet works but is slow")
    else:
        vcls, vicon, vtext = ("bad", "❌", "Your connection is very slow")

    # Plain-English cards (number + explanation, both shown)
    def card(icon, title, result):
        css, num, txt = result
        return f"""
        <div class="plain-item {css}">
          <div class="plain-icon">{icon}</div>
          <div class="plain-title">{title}</div>
          <div class="plain-number">{num}</div>
          <div class="plain-text">{txt}</div>
        </div>"""

    summary_cards = '<div class="plain">'
    summary_cards += card("⚡", "Speed of response",  human_latency(avg_lat))
    summary_cards += card("⬇️", "Download speed",      human_download(dl))
    summary_cards += card("⬆️", "Upload speed",        human_upload(ul))
    summary_cards += card("🧭", "DNS (web address lookup)", human_dns(dns_cf))
    summary_cards += card("📶", "Connection stability", human_loss(gl))
    summary_cards += "</div>"

    # Latency rows
    def lat_row(label, ms, loss, jitter):
        if ms is None:
            val = '<span class="bad">FAIL</span>'
        else:
            val = f'<span class="{cls_latency(ms)}">{ms:.0f} ms</span>'
        loss_s = "—"
        if loss is not None:
            loss_s = f'<span class="{cls_loss(loss)}">{loss:.1f}%</span>'
        jit_s = f"{jitter:.0f} ms" if jitter is not None else "—"
        return f"<tr><td><b>{label}</b></td><td>{val}</td><td>{loss_s}</td><td>{jit_s}</td></tr>"

    latency_rows = ""
    latency_rows += lat_row("Google DNS", g, gl, gj)
    latency_rows += lat_row("Cloudflare", c, None, None)
    latency_rows += lat_row("Quad9",      q, None, None)
    if od is not None:
        latency_rows += lat_row("OpenDNS", od, None, None)

    # DNS rows
    def dns_row(label, ms):
        if ms is None:
            return f'<tr><td><b>{label}</b></td><td><span class="bad">FAIL</span></td></tr>'
        return f'<tr><td><b>{label}</b></td><td><span class="{cls_dns(ms)}">{ms:.0f} ms</span></td></tr>'

    dns_rows = ""
    dns_rows += dns_row("Safaricom default", dns_def)
    dns_rows += dns_row("Google 8.8.8.8",    dns_g)
    dns_rows += dns_row("Cloudflare 1.1.1.1", dns_cf)

    # HTTP rows
    def http_row(label, ms):
        if ms is None:
            return f'<tr><td><b>{label}</b></td><td><span class="bad">FAIL</span></td></tr>'
        return f'<tr><td><b>{label}</b></td><td><span class="{cls_ttfb(ms)}">{ms:.0f} ms</span></td></tr>'

    http_rows = ""
    http_rows += http_row("Google",     http_g)
    http_rows += http_row("Cloudflare", http_cf)
    http_rows += http_row("Wikipedia",  http_w)

    # Speed panel
    dl_s = f'{dl:.2f} Mbps' if dl is not None else 'N/A'
    ul_s = f'{ul:.2f} Mbps' if ul is not None else 'N/A'
    dl_cls = cls_speed(dl)
    ul_cls = cls_speed(ul)

    # ISP summary
    summary = isp_summary(rows)
    summary_rows = ""
    for isp, s in summary.items():
        lat = s["avg_latency"]; loss = s["avg_loss"]
        dl_a = s["avg_download"]; ul_a = s["avg_upload"]
        summary_rows += f"""
        <tr>
          <td>{html.escape(isp)}</td>
          <td>{s['runs']}</td>
          <td class="{cls_latency(lat)}">{f'{lat:.0f} ms' if lat is not None else '—'}</td>
          <td class="{cls_loss(loss)}">{f'{loss:.1f}%' if loss is not None else '—'}</td>
          <td class="{cls_speed(dl_a)}">{f'{dl_a:.2f} Mbps' if dl_a is not None else '—'}</td>
          <td class="{cls_speed(ul_a)}">{f'{ul_a:.2f} Mbps' if ul_a is not None else '—'}</td>
        </tr>"""

    # All runs
    all_rows_html = ""
    for r in reversed(rows):
        def cell(v, kind="lat"):
            fv = f(v)
            if fv is None: return "—"
            if kind == "lat":   cls = cls_latency(fv); suffix = " ms"
            elif kind == "speed": cls = cls_speed(fv); suffix = ""
            elif kind == "dns": cls = cls_dns(fv); suffix = " ms"
            else: cls = cls_latency(fv); suffix = " ms"
            return f'<span class="{cls}">{fv:.0f}{suffix}</span>'

        ts_short = r.get("timestamp", "")[:19].replace("T", " ")
        all_rows_html += f"""
        <tr>
          <td>{ts_short}</td>
          <td>{cell(r.get('google_avg'))}</td>
          <td>{cell(r.get('cloudflare_avg'))}</td>
          <td>{cell(r.get('quad9_avg'))}</td>
          <td>{cell(r.get('dns_cloudflare_ms'), 'dns')}</td>
          <td>{cell(r.get('download_mbps'), 'speed')}</td>
        </tr>"""

    page = f"""<!DOCTYPE html>
<html lang="en">
<head>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width, initial-scale=1">
<title>Network Report</title>
<style>
  * {{ box-sizing: border-box; }}
  body {{ font-family: system-ui, -apple-system, sans-serif;
         background: #0f172a; color: #e2e8f0; margin: 0;
         padding: 20px; line-height: 1.5; }}
  .container {{ max-width: 900px; margin: auto; }}
  h1 {{ color: #38bdf8; margin: 0 0 4px 0; font-size: 26px; }}
  h2 {{ color: #38bdf8; margin-top: 28px; padding-bottom: 8px;
       border-bottom: 1px solid #334155; font-size: 18px; }}
  .meta {{ color: #94a3b8; font-size: 13px; margin-bottom: 20px; }}
  .card {{ background: #1e293b; border-radius: 12px;
          padding: 18px; margin: 14px 0; }}
  table {{ width: 100%; border-collapse: collapse; margin-top: 8px; }}
  th, td {{ text-align: left; padding: 9px 10px;
           border-bottom: 1px solid #334155; font-size: 14px; }}
  th {{ color: #94a3b8; font-weight: 600; font-size: 12px;
       text-transform: uppercase; letter-spacing: 0.5px; }}
  tr:last-child td {{ border-bottom: none; }}
  .ok {{ color: #4ade80; font-weight: bold; }}
  .warn {{ color: #fbbf24; font-weight: bold; }}
  .bad {{ color: #f87171; font-weight: bold; }}
  .verdict {{ padding: 16px 20px; border-radius: 10px;
             font-size: 18px; font-weight: bold; margin: 14px 0; }}
  .verdict.ok {{ background: rgba(74, 222, 128, 0.15);
                color: #4ade80; border-left: 4px solid #4ade80; }}
  .verdict.warn {{ background: rgba(251, 191, 36, 0.15);
                  color: #fbbf24; border-left: 4px solid #fbbf24; }}
  .verdict.bad {{ background: rgba(248, 113, 113, 0.15);
                 color: #f87171; border-left: 4px solid #f87171; }}

  /* Plain-English cards — number + explanation */
  .plain {{ display: grid; gap: 10px;
           grid-template-columns: 1fr; margin: 14px 0; }}
  @media (min-width: 600px) {{
    .plain {{ grid-template-columns: 1fr 1fr; }}
  }}
  .plain-item {{ background: #1e293b; padding: 16px;
                border-radius: 10px; border-left: 4px solid #475569; }}
  .plain-item.ok   {{ border-left-color: #4ade80; }}
  .plain-item.warn {{ border-left-color: #fbbf24; }}
  .plain-item.bad  {{ border-left-color: #f87171; }}
  .plain-icon {{ font-size: 22px; margin-bottom: 6px; }}
  .plain-title {{ font-size: 12px; text-transform: uppercase;
                 color: #94a3b8; letter-spacing: 0.5px;
                 margin-bottom: 4px; }}
  .plain-number {{ font-size: 24px; font-weight: bold;
                  margin-bottom: 4px; }}
  .plain-text {{ font-size: 14px; color: #cbd5e1; }}
  .plain-item.ok   .plain-number {{ color: #4ade80; }}
  .plain-item.warn .plain-number {{ color: #fbbf24; }}
  .plain-item.bad  .plain-number {{ color: #f87171; }}

  .speed-pair {{ display: flex; gap: 20px; flex-wrap: wrap; margin-top: 16px; }}
  .speed-item {{ flex: 1; min-width: 120px; }}
  .speed-label {{ font-size: 12px; color: #94a3b8;
                 text-transform: uppercase; margin-bottom: 4px; }}
  .speed-value {{ font-size: 22px; font-weight: bold; }}
  .footer {{ margin-top: 40px; color: #64748b; font-size: 12px;
            text-align: center; }}
</style>
</head>
<body>
<div class="container">
  <h1>🌐 Network Report</h1>
  <p class="meta">
    {ts[:19].replace("T", " ")} ·
    {len(rows)} runs · {len(summary)} ISP(s)
  </p>

  <div class="verdict {vcls}">
    {vicon} {vtext}
  </div>

  <h2>💡 What This Means</h2>
  {summary_cards}

  <h2>⚡ Latest Run — Latency</h2>
  <div class="card">
    <table>
      <thead><tr><th>Target</th><th>Latency</th><th>Loss</th><th>Jitter</th></tr></thead>
      <tbody>{latency_rows}</tbody>
    </table>
    <div class="speed-pair">
      <div class="speed-item">
        <div class="speed-label">Download</div>
        <div class="speed-value {dl_cls}">{dl_s}</div>
      </div>
      <div class="speed-item">
        <div class="speed-label">Upload</div>
        <div class="speed-value {ul_cls}">{ul_s}</div>
      </div>
    </div>
  </div>

  <h2>🧭 Latest Run — DNS</h2>
  <div class="card">
    <table>
      <thead><tr><th>DNS Server</th><th>Resolution Time</th></tr></thead>
      <tbody>{dns_rows}</tbody>
    </table>
  </div>

  <h2>🌐 Latest Run — HTTP</h2>
  <div class="card">
    <table>
      <thead><tr><th>Site</th><th>Time to First Byte</th></tr></thead>
      <tbody>{http_rows}</tbody>
    </table>
  </div>

  <h2>📊 ISP Summary</h2>
  <div class="card">
    <table>
      <thead>
        <tr><th>ISP</th><th>Runs</th><th>Latency</th>
            <th>Loss</th><th>Download</th><th>Upload</th></tr>
      </thead>
      <tbody>{summary_rows}</tbody>
    </table>
  </div>

  <h2>📋 All Runs</h2>
  <div class="card">
    <table>
      <thead>
        <tr><th>Time</th><th>Google</th><th>Cloudflare</th>
            <th>Quad9</th><th>DNS (CF)</th><th>Download</th></tr>
      </thead>
      <tbody>{all_rows_html}</tbody>
    </table>
  </div>

  <p class="footer">Network Monitor v4.2 — report.py</p>
</div>
</body>
</html>"""

    os.makedirs("reports", exist_ok=True)
    with open(config.REPORT, "w") as f:
        f.write(page)
    return config.REPORT


# ---------- Entry ----------

def main():
    rows = load_csv()
    if "--html" in sys.argv:
        path = generate_html(rows)
        if path:
            print(f"✅ HTML report written: {path}")
            print(f"   Open with:  termux-open {path}")
        else:
            print("❌ No data — run monitor.py first")
    else:
        print_terminal_report(rows)


if __name__ == "__main__":
    main()
