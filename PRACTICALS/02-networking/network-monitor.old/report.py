#!/usr/bin/env python3
# ============================================
# report.py v3.2 — Correct session parsing
# ============================================

import re
import statistics
from datetime import datetime

LOG_FILE = "network_log.txt"

def parse_log():
    with open(LOG_FILE, "r") as f:
        content = f.read()

    # Split on "SESSION STARTED:" — the ==== lines are decorative
    parts = content.split("SESSION STARTED:")
    sessions = []

    for part in parts[1:]:
        session = {"runs": [], "isp": {}, "conn": "UNKNOWN"}

        # Get connection type from the session header line
        conn_match = re.match(r"\s+[\d\-]+ [\d:]+ \[(WIFI|MOBILE|UNKNOWN)\]", part)
        if conn_match:
            session["conn"] = conn_match.group(1)

        # ISP info
        isp_match = re.search(r"ISP:\s+(.+)", part)
        session["isp"]["org"] = isp_match.group(1).strip() if isp_match else "Unknown"

        loc_match = re.search(r"Location:\s+(.+)", part)
        session["isp"]["location"] = loc_match.group(1).strip() if loc_match else "Unknown"

        ip_match = re.search(r"Public IP:\s+([\d.]+)", part)
        session["isp"]["ip"] = ip_match.group(1) if ip_match else "Unknown"

        # Each run starts with "----- timestamp [CONN] -----"
        run_pattern = re.compile(r"----- ([\d\-]+ [\d:]+)(?: \[(WIFI|MOBILE|UNKNOWN)\])? -----\n((?:.+\n)+?)(?=\n|-----|SESSION|$)")
        for match in run_pattern.finditer(part):
            ts = match.group(1).strip()
            run_conn = match.group(2) or session["conn"]
            body = match.group(3)

            run = {"time": ts, "conn": run_conn, "pings": {}}
            for line in body.strip().split("\n"):
                m = re.match(r"(.+?):\s+(\d+)\s*ms", line)
                if m:
                    run["pings"][m.group(1).strip()] = int(m.group(2))
                elif re.match(r"(.+?):\s+FAILED", line):
                    m2 = re.match(r"(.+?):\s+FAILED", line)
                    run["pings"][m2.group(1).strip()] = None

            if run["pings"]:
                session["runs"].append(run)

        if session["runs"]:
            sessions.append(session)

    return sessions

def stats(values):
    vals = [v for v in values if v is not None]
    if not vals:
        return None
    return {
        "count": len(vals),
        "avg": statistics.mean(vals),
        "min": min(vals),
        "max": max(vals),
        "stdev": statistics.stdev(vals) if len(vals) > 1 else 0,
    }

def print_stats(label, vals):
    s = stats(vals)
    if not s:
        print(f"     {label}: NO DATA")
        return
    print(f"     {label}:")
    print(f"        Average: {s['avg']:.0f} ms   (min {s['min']}, max {s['max']}, σ {s['stdev']:.0f}, n={s['count']})")

def report():
    print("=" * 65)
    print("📊 NETWORK REPORT v3.2")
    print(f"   Generated: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print("=" * 65)

    try:
        sessions = parse_log()
    except FileNotFoundError:
        print(f"\n❌ Log file '{LOG_FILE}' not found.")
        return

    if not sessions:
        print("\n❌ No sessions found.")
        print("   Raw log may be from old format or empty.")
        print("   Try: rm network_log.txt && python monitor.py")
        return

    all_wifi_runs = []
    all_mobile_runs = []

    for s_idx, session in enumerate(sessions):
        isp = session["isp"]
        runs = session["runs"]

        print(f"\n{'═' * 65}")
        print(f"📡 SESSION #{s_idx + 1}  —  {isp['org']}")
        print(f"   Location:  {isp['location']}")
        print(f"   Public IP: {isp['ip']}")
        print(f"   Runs:      {len(runs)}")
        if runs:
            print(f"   Period:    {runs[0]['time']} → {runs[-1]['time']}")
        print(f"{'═' * 65}")

        wifi_runs = [r for r in runs if r.get("conn") == "WIFI"]
        mobile_runs = [r for r in runs if r.get("conn") == "MOBILE"]

        all_wifi_runs.extend(wifi_runs)
        all_mobile_runs.extend(mobile_runs)

        for conn_label, conn_runs in [("📶 WiFi", wifi_runs), ("📱 Mobile Data", mobile_runs)]:
            if not conn_runs:
                continue
            print(f"\n   {conn_label} — {len(conn_runs)} runs")
            print(f"   {'-' * 60}")

            conn_pings = {}
            for run in conn_runs:
                for label, val in run["pings"].items():
                    conn_pings.setdefault(label, []).append(val)

            for label, vals in conn_pings.items():
                print_stats(label, vals)

    # WiFi vs Mobile comparison
    if all_wifi_runs and all_mobile_runs:
        print(f"\n{'═' * 65}")
        print(f"🔀 WiFi vs MOBILE — FULL COMPARISON")
        print(f"{'═' * 65}")

        wifi_pub = []
        for run in all_wifi_runs:
            for label, val in run["pings"].items():
                if "Router" not in label and "Gateway" not in label and val:
                    wifi_pub.append(val)

        mobile_pub = []
        for run in all_mobile_runs:
            for label, val in run["pings"].items():
                if "Router" not in label and "Gateway" not in label and val:
                    mobile_pub.append(val)

        if wifi_pub and mobile_pub:
            wifi_avg = statistics.mean(wifi_pub)
            mobile_avg = statistics.mean(mobile_pub)
            wifi_std = statistics.stdev(wifi_pub) if len(wifi_pub) > 1 else 0
            mobile_std = statistics.stdev(mobile_pub) if len(mobile_pub) > 1 else 0

            print(f"\n   WiFi public avg:    {wifi_avg:.0f} ms   (σ {wifi_std:.0f}, n={len(wifi_pub)})")
            print(f"   Mobile public avg:  {mobile_avg:.0f} ms   (σ {mobile_std:.0f}, n={len(mobile_pub)})")

            print(f"\n   Verdict:")
            if wifi_avg < mobile_avg:
                diff = mobile_avg - wifi_avg
                print(f"   🏆 WiFi is FASTER by {diff:.0f} ms")
            else:
                diff = wifi_avg - mobile_avg
                print(f"   🏆 Mobile Data is FASTER by {diff:.0f} ms")
                print(f"      → Use mobile data when possible.")

            if wifi_std > 500:
                print(f"   ⚠  WiFi is UNSTABLE (σ={wifi_std:.0f})")
            if mobile_std > 500:
                print(f"   ⚠  Mobile is UNSTABLE (σ={mobile_std:.0f})")
        print(f"{'═' * 65}")
    elif all_wifi_runs:
        print(f"\n   ℹ Only WiFi runs found. Run on mobile data to compare.")
    elif all_mobile_runs:
        print(f"\n   ℹ Only Mobile Data runs found. Run on WiFi to compare.")

    print(f"\n📁 Full log: {LOG_FILE}")

if __name__ == "__main__":
    report()
