#!/usr/bin/env python3
# ============================================
# monitor.py v3.1 — With WiFi/Mobile detection
# ============================================

import subprocess
import re
import json
import urllib.request
from datetime import datetime

LOG_FILE = "network_log.txt"

TARGETS = {
    "Google DNS (8.8.8.8)":     "8.8.8.8",
    "Cloudflare (1.1.1.1)":     "1.1.1.1",
    "Quad9 (9.9.9.9)":          "9.9.9.9",
    "OpenDNS (208.67.222.222)": "208.67.222.222",
}
PING_COUNT = 5
PING_TIMEOUT = 3

# =====================================================
# DETECT CONNECTION TYPE
# =====================================================
def detect_connection_type():
    """Returns 'WIFI', 'MOBILE', or 'UNKNOWN'."""
    try:
        result = subprocess.run(["ifconfig"], capture_output=True, text=True, timeout=5)
        out = result.stdout

        wifi_active = False
        mobile_active = False

        if "wlan0:" in out:
            block = out.split("wlan0:")[1].split("\n\n")[0]
            if re.search(r"inet\s+192\.168\.", block):
                wifi_active = True

        for iface in ["rmnet1", "rmnet5", "rmnet0", "ccmni0", "rmnet_data0"]:
            if f"{iface}:" in out:
                block = out.split(f"{iface}:")[1].split("\n\n")[0]
                if re.search(r"inet\s+\d", block):
                    mobile_active = True
                    break

        if wifi_active:
            return "WIFI"
        elif mobile_active:
            return "MOBILE"
        else:
            return "UNKNOWN"
    except Exception:
        return "UNKNOWN"

# =====================================================
# ISP DETECTION
# =====================================================
def detect_isp():
    try:
        req = urllib.request.Request(
            "https://ipinfo.io/json",
            headers={"User-Agent": "NetworkMonitor/3"}
        )
        with urllib.request.urlopen(req, timeout=8) as r:
            data = json.loads(r.read().decode())
        return {
            "ip": data.get("ip", "unknown"),
            "hostname": data.get("hostname", "unknown"),
            "city": data.get("city", "unknown"),
            "region": data.get("region", "unknown"),
            "country": data.get("country", "unknown"),
            "org": data.get("org", "unknown"),
            "loc": data.get("loc", "unknown"),
        }
    except Exception as e:
        return {"error": str(e)}

# =====================================================
# ISP GATEWAY DETECTION
# =====================================================
def is_private_ip(ip):
    """Only 192.168.x, 10.x, 127.x are considered local. 100.x and 172.x are ISP CGNAT."""
    try:
        parts = [int(x) for x in ip.split(".")]
        if parts[0] == 10:
            return True
        if parts[0] == 192 and parts[1] == 168:
            return True
        if parts[0] == 127:
            return True
        return False
    except Exception:
        return False

def get_isp_gateway():
    """Get the first hop outside our local network."""
    try:
        result = subprocess.run(
            ["traceroute", "-m", "5", "-w", "2", "8.8.8.8"],
            capture_output=True, text=True, timeout=20
        )
        for line in result.stdout.split("\n"):
            line = line.strip()
            if not line or not line[0].isdigit():
                continue
            if line.startswith("1 "):
                continue
            match = re.search(r"\(([\d.]+)\)", line)
            if match:
                ip = match.group(1)
                if not is_private_ip(ip):
                    return ip
        return None
    except Exception:
        return None

# =====================================================
# PING HELPERS
# =====================================================
def ping_avg(target):
    try:
        result = subprocess.run(
            ["ping", "-c", str(PING_COUNT), "-W", str(PING_TIMEOUT), target],
            capture_output=True, text=True, timeout=30
        )
        match = re.search(r"rtt [^=]*=\s*[\d.]+/([\d.]+)/", result.stdout)
        return float(match.group(1)) if match else None
    except Exception:
        return None

# =====================================================
# LOGGING
# =====================================================
def log_session_start(isp_info, conn_type):
    timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    with open(LOG_FILE, "a") as f:
        f.write(f"\n{'=' * 60}\n")
        f.write(f"SESSION STARTED: {timestamp} [{conn_type}]\n")
        f.write(f"{'=' * 60}\n")
        if "error" in isp_info:
            f.write(f"ISP detection failed: {isp_info['error']}\n")
        else:
            f.write(f"ISP:      {isp_info['org']}\n")
            f.write(f"Location: {isp_info['city']}, {isp_info['region']}, {isp_info['country']}\n")
            f.write(f"Public IP: {isp_info['ip']}\n")
            f.write(f"Hostname:  {isp_info['hostname']}\n")
            f.write(f"Connection: {conn_type}\n")
        f.write(f"\n")

def log_run(results, conn_type):
    timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    with open(LOG_FILE, "a") as f:
        f.write(f"----- {timestamp} [{conn_type}] -----\n")
        for label, ping in results.items():
            if ping is None:
                f.write(f"{label}: FAILED\n")
            else:
                f.write(f"{label}: {ping:.0f} ms\n")
        f.write("\n")

# =====================================================
# DIAGNOSIS
# =====================================================
def diagnose(router_ping, gateway_ping, target_pings, conn_type):
    findings = []

    if conn_type == "WIFI" and router_ping is not None:
        if router_ping > 50:
            findings.append(("warn", f"Router latency high ({router_ping:.0f} ms)"))
        else:
            findings.append(("ok", f"Local network OK (router {router_ping:.0f} ms)"))

    if gateway_ping is None:
        findings.append(("warn", "ISP gateway unreachable — could not detect"))
    elif gateway_ping > 100:
        findings.append(("critical", f"ISP gateway SLOW ({gateway_ping:.0f} ms)"))
    elif gateway_ping > 50:
        findings.append(("warn", f"ISP gateway moderate ({gateway_ping:.0f} ms)"))
    else:
        findings.append(("ok", f"ISP edge OK ({gateway_ping:.0f} ms)"))

    slow_count = 0
    fast_count = 0
    for name, ping in target_pings.items():
        if ping is None:
            findings.append(("warn", f"{name}: UNREACHABLE"))
        elif ping > 300:
            findings.append(("critical", f"{name}: SLOW ({ping:.0f} ms)"))
            slow_count += 1
        elif ping > 150:
            findings.append(("warn", f"{name}: moderate ({ping:.0f} ms)"))
            slow_count += 1
        else:
            findings.append(("ok", f"{name}: OK ({ping:.0f} ms)"))
            fast_count += 1

    if slow_count == len(target_pings):
        verdict = "INTERNET-WIDE (all destinations slow)"
    elif fast_count == len(target_pings):
        verdict = "HEALTHY (all destinations fast)"
    elif slow_count > 0 and fast_count > 0:
        verdict = "ROUTE-SPECIFIC (only some destinations slow)"
    else:
        verdict = "UNCLEAR"

    return findings, verdict

# =====================================================
# MAIN RUN
# =====================================================
def run_once(isp_info, gateway_ip, run_number):
    conn_type = detect_connection_type()

    print("=" * 60)
    print(f"🌐 Network Monitor v3.1 — Run #{run_number}")
    print(f"   Connection: {conn_type}")
    print(f"   {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print("=" * 60)

    print(f"\n📍 Layer-by-layer ping test:")
    results = {}

    if conn_type == "WIFI":
        print(f"\n   [Layer 1] Router (192.168.1.1)...", end=" ", flush=True)
        router_ping = ping_avg("192.168.1.1")
        results["Router (192.168.1.1)"] = router_ping
        print(f"{router_ping:.0f} ms" if router_ping else "FAILED")
    else:
        print(f"\n   [Layer 1] Router... (not applicable on {conn_type})")
        router_ping = None

    if gateway_ip:
        print(f"   [Layer 2] ISP Gateway ({gateway_ip})...", end=" ", flush=True)
        gateway_ping = ping_avg(gateway_ip)
        results[f"ISP Gateway ({gateway_ip})"] = gateway_ping
        print(f"{gateway_ping:.0f} ms" if gateway_ping else "FAILED")
    else:
        gateway_ping = None
        print(f"   [Layer 2] ISP Gateway... (could not detect)")

    print(f"\n   [Layer 3] Public destinations:")
    target_pings = {}
    for name, ip in TARGETS.items():
        print(f"     {name}...", end=" ", flush=True)
        ping = ping_avg(ip)
        target_pings[name] = ping
        results[name] = ping
        print(f"{ping:.0f} ms" if ping else "FAILED")

    print(f"\n{'━' * 60}")
    print("🔍 DIAGNOSIS")
    print(f"{'━' * 60}")

    findings, verdict = diagnose(router_ping, gateway_ping, target_pings, conn_type)
    for level, message in findings:
        if level == "critical":
            print(f"  ❌ {message}")
        elif level == "warn":
            print(f"  ⚠  {message}")
        else:
            print(f"  ✓  {message}")

    print(f"\n  🎯 VERDICT: {verdict}")
    print(f"{'━' * 60}\n")

    log_run(results, conn_type)
    return results

# =====================================================
# MAIN
# =====================================================
def main():
    conn_type = detect_connection_type()

    print("\n📡 Detecting ISP...")
    isp_info = detect_isp()

    if "error" in isp_info:
        print(f"   ⚠  Could not detect ISP: {isp_info['error']}")
    else:
        print(f"   ✓ ISP:      {isp_info['org']}")
        print(f"   ✓ Location: {isp_info['city']}, {isp_info['country']}")
        print(f"   ✓ Public IP: {isp_info['ip']}")
        print(f"   ✓ Connection: {conn_type}")

    print(f"\n🛰  Finding ISP gateway...")
    gateway_ip = get_isp_gateway()
    if gateway_ip:
        print(f"   ✓ Gateway: {gateway_ip}")
    else:
        print(f"   ⚠  Could not detect ISP gateway")

    log_session_start(isp_info, conn_type)
    run_once(isp_info, gateway_ip, 1)

if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        print("\n\n🛑 Stopped by user (Ctrl+C).")
        print("📄 Progress saved to network_log.txt")
