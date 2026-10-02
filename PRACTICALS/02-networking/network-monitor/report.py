#!/usr/bin/env python3
"""Read logs, produce terminal report + HTML report."""
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


# ---------- HTML helpers ----------

def color_class_latency(v):
    if v is None: return "bad"
    if v < 100:   return "ok"
    if v < 200:   return "warn"
    return "bad"


def color_class_speed(v):
    if v is None: return "bad"
    if v >= 5:    return "ok"
    if v >= 2:    return "warn"
    return "bad"


def color_class_loss(v):
    if v is None: return "bad"
    if v <= 1:    return "ok"
    if v <= 5:    return "warn"
    return "bad"


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

    # Verdict
    near_avgs = [v for v in (g, c, q) if v is not None]
    avg_lat = sum(near_avgs) / len(near_avgs) if near_avgs else None

    if gl is not None and gl > 5:
        verdict_cls, verdict_icon, verdict_text = (
            "bad", "❌", f"PACKET LOSS ({gl:.1f}%) — connection unstable")
    elif dl is not None and dl < 2:
        verdict_cls, verdict_icon, verdict_text = (
            "bad", "❌", f"SLOW DOWNLOAD ({dl:.2f} Mbps)")
    elif avg_lat is None:
        verdict_cls, verdict_icon, verdict_text = (
            "bad", "❌", "No reachable targets")
    elif avg_lat < 100:
        verdict_cls, verdict_icon, verdict_text = (
            "ok", "✓", f"HEALTHY (avg {avg_lat:.0f} ms to major DNS)")
    elif avg_lat < 200:
        verdict_cls, verdict_icon, verdict_text = (
            "warn", "⚠", f"MODERATE (avg {avg_lat:.0f} ms)")
    else:
        verdict_cls, verdict_icon, verdict_text = (
            "bad", "❌", f"SLOW (avg {avg_lat:.0f} ms)")

    # Latest run rows
    def row(label, ms, loss, jitter):
        if ms is None:
            val = '<span class="bad">FAIL</span>'
        else:
            cls = color_class_latency(ms)
            val = f'<span class="{cls}">{ms:.0f} ms</span>'
        loss_s = "—"
        if loss is not None:
            lcls = color_class_loss(loss)
            loss_s = f'<span class="{lcls}">{loss:.1f}%</span>'
        jit_s = f"{jitter:.0f} ms" if jitter is not None else "—"
        return f"""
        <tr>
          <td><b>{label}</b></td>
          <td>{val}</td>
          <td>{loss_s}</td>
          <td>{jit_s}</td>
        </tr>"""

    latest_rows = ""
    latest_rows += row("Google DNS", g, gl, gj)
    latest_rows += row("Cloudflare", c, None, None)
    latest_rows += row("Quad9",      q, None, None)
    if od is not None:
        latest_rows += row("OpenDNS", od, None, None)

    # Speed panel
    dl_s = f'{dl:.2f} Mbps' if dl is not None else 'FAILED'
    ul_s = f'{ul:.2f} Mbps' if ul is not None else 'FAILED'
    dl_cls = color_class_speed(dl)
    ul_cls = color_class_speed(ul)

    # All-runs table
    all_rows_html = ""
    for r in reversed(rows):
        def cell(v, kind="lat"):
            fv = f(v)
            if fv is None: return "—"
            cls = color_class_latency(fv) if kind == "lat" else color_class_speed(fv)
            suffix = " ms" if kind == "lat" else ""
            return f'<span class="{cls}">{fv:.0f}{suffix}</span>'
        ts_short = r.get("timestamp", "")[:19].replace("T", " ")
        all_rows_html += f"""
        <tr>
          <td>{ts_short}</td>
          <td>{cell(r.get('google_avg'))}</td>
          <td>{cell(r.get('cloudflare_avg'))}</td>
          <td>{cell(r.get('quad9_avg'))}</td>
          <td>{cell(r.get('download_mbps'), 'speed')}</td>
        </tr>"""

    # Summary table
    summary = isp_summary(rows)
    summary_rows = ""
    for isp, s in summary.items():
        lat = s["avg_latency"]
        loss = s["avg_loss"]
        dl_a = s["avg_download"]
        ul_a = s["avg_upload"]
        summary_rows += f"""
        <tr>
          <td>{html.escape(isp)}</td>
          <td>{s['runs']}</td>
          <td class="{color_class_latency(lat)}">{f'{lat:.0f} ms' if lat is not None else '—'}</td>
          <td class="{color_class_loss(loss)}">{f'{loss:.1f}%' if loss is not None else '—'}</td>
          <td class="{color_class_speed(dl_a)}">{f'{dl_a:.2f} Mbps' if dl_a is not None else '—'}</td>
          <td class="{color_class_speed(ul_a)}">{f'{ul_a:.2f} Mbps' if ul_a is not None else '—'}</td>
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
             font-size: 16px; font-weight: bold; margin: 14px 0; }}
  .verdict.ok {{ background: rgba(74, 222, 128, 0.15);
                color: #4ade80; border-left: 4px solid #4ade80; }}
  .verdict.warn {{ background: rgba(251, 191, 36, 0.15);
                  color: #fbbf24; border-left: 4px solid #fbbf24; }}
  .verdict.bad {{ background: rgba(248, 113, 113, 0.15);
                 color: #f87171; border-left: 4px solid #f87171; }}
  .speed-pair {{ display: flex; gap: 20px; flex-wrap: wrap; }}
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

  <div class="verdict {verdict_cls}">
    {verdict_icon} {verdict_text}
  </div>

  <h2>⚡ Latest Run</h2>
  <div class="card">
    <table>
      <thead>
        <tr><th>Target</th><th>Latency</th><th>Loss</th><th>Jitter</th></tr>
      </thead>
      <tbody>
        {latest_rows}
      </tbody>
    </table>

    <div class="speed-pair" style="margin-top:16px">
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

  <h2>📊 ISP Summary</h2>
  <div class="card">
    <table>
      <thead>
        <tr>
          <th>ISP</th><th>Runs</th><th>Latency</th>
          <th>Loss</th><th>Download</th><th>Upload</th>
        </tr>
      </thead>
      <tbody>
        {summary_rows}
      </tbody>
    </table>
  </div>

  <h2>📋 All Runs</h2>
  <div class="card">
    <table>
      <thead>
        <tr>
          <th>Time</th><th>Google</th><th>Cloudflare</th>
          <th>Quad9</th><th>Download</th>
        </tr>
      </thead>
      <tbody>
        {all_rows_html}
      </tbody>
    </table>
  </div>

  <p class="footer">Network Monitor v4.0 — report.py</p>
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
