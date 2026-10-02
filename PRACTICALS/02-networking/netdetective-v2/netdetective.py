#!/usr/bin/env python3
# ============================================
# NETWORK DETECTIVE v2.1 — Bug-fixed
# ============================================

import socket
import subprocess
import time
import urllib.request
import urllib.error
import re
from datetime import datetime

LOOP_EVERY = 15
SPEEDTEST_EVERY_N_LOOPS = 4
LOG_FILE = "netdetective.log"
TARGETS = ["8.8.8.8", "1.1.1.1", "9.9.9.9"]
DNS_TARGET = "github.com"
HTTP_TARGET = "https://github.com"
ROUTER_IP = "192.168.1.1"

class C:
    GREEN="\033[92m"; RED="\033[91m"; YELLOW="\033[93m"
    BLUE="\033[94m"; BOLD="\033[1m"; END="\033[0m"

def log(line):
    with open(LOG_FILE, "a") as f:
        f.write(f"{datetime.now().isoformat()} | {line}\n")

def run(cmd, timeout=5):
    try:
        r = subprocess.run(cmd, capture_output=True, text=True, timeout=timeout)
        return r.returncode == 0, r.stdout + r.stderr
    except Exception as e:
        return False, str(e)

# ============ TESTS ============

def test_local_ip():
    try:
        s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        s.settimeout(2)
        s.connect(("8.8.8.8", 80))
        ip = s.getsockname()[0]
        s.close()
        return True, ip
    except Exception as e:
        return False, str(e)

def test_router():
    ok_, out = run(["ping", "-c", "1", "-W", "2", ROUTER_IP], timeout=4)
    if ok_ and "time=" in out:
        t = out.split("time=")[1].split()[0]
        return True, f"{ROUTER_IP} ({t} ms)"
    return False, "Cannot reach router"

def test_router_latency():
    ok_, out = run(["ping", "-c", "5", "-W", "2", ROUTER_IP], timeout=10)
    if not ok_:
        return False, "Router ping failed"
    m = re.search(r"rtt [^=]*= ([\d.]+)/([\d.]+)", out)
    if m:
        avg = float(m.group(2))
        if avg > 50:
            return False, f"avg {avg} ms (HIGH)"
        return True, f"avg {avg:.1f} ms"
    return True, "OK"

def test_internet_ping():
    working = []
    for t in TARGETS:
        ok_, _ = run(["ping", "-c", "1", "-W", "2", t], timeout=4)
        if ok_:
            working.append(t)
    if working:
        return True, f"{len(working)}/{len(TARGETS)} reachable"
    return False, "No internet ping reachable (ICMP may be blocked)"

def test_tcp_connect():
    try:
        s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        s.settimeout(3)
        s.connect(("8.8.8.8", 53))
        s.close()
        return True, "TCP:53 to 8.8.8.8 OK"
    except Exception as e:
        return False, f"TCP failed: {e}"

def test_dns():
    try:
        ip = socket.gethostbyname(DNS_TARGET)
        return True, f"{DNS_TARGET} → {ip}"
    except Exception as e:
        return False, f"DNS failed: {e}"

def test_dns_speed():
    start = time.time()
    try:
        socket.gethostbyname(DNS_TARGET)
        ms = (time.time() - start) * 1000
        if ms < 100:
            return True, f"{ms:.0f} ms (fast)"
        elif ms < 300:
            return True, f"{ms:.0f} ms (OK)"
        else:
            return False, f"{ms:.0f} ms (SLOW)"
    except Exception:
        return False, "DNS speed test failed"

def test_http():
    try:
        req = urllib.request.Request(HTTP_TARGET, headers={"User-Agent": "NetDetective/2.1"})
        with urllib.request.urlopen(req, timeout=5) as r:
            return True, f"HTTP {r.status}"
    except urllib.error.HTTPError as e:
        return False, f"HTTP error {e.code}"
    except Exception as e:
        return False, f"HTTP failed: {e}"

def test_traceroute():
    ok_, out = run(["traceroute", "-m", "5", "-w", "2", "8.8.8.8"], timeout=20)
    # FIXED: strip leading spaces before checking digit
    hops = [l for l in out.split("\n") if l.strip() and l.strip()[0].isdigit()]
    if not hops:
        return False, "Traceroute returned no hops"

    # FIXED: parse latency from hop 2+ (ISP)
    isp_latencies = []
    for line in hops[1:]:  # skip hop 1 (router)
        # find all "XXX ms" patterns
        times = re.findall(r"([\d.]+)\s*ms", line)
        for t in times:
            try:
                isp_latencies.append(float(t))
            except ValueError:
                pass

    if isp_latencies:
        avg_isp = sum(isp_latencies) / len(isp_latencies)
        if avg_isp > 500:
            return False, f"{len(hops)} hops, ISP latency {avg_isp:.0f} ms (VERY HIGH)"
        elif avg_isp > 200:
            return False, f"{len(hops)} hops, ISP latency {avg_isp:.0f} ms (HIGH)"
        return True, f"{len(hops)} hops, ISP avg {avg_isp:.0f} ms"

    return True, f"{len(hops)} hops"

def test_speedtest():
    ok_, out = run(["speedtest-cli", "--simple", "--secure"], timeout=45)
    if ok_:
        lines = [l.strip() for l in out.strip().split("\n") if l.strip()]
        result = " | ".join(lines)
        slow = False
        for line in lines:
            if "Download" in line:
                try:
                    speed = float(line.split(":")[1].split()[0])
                    if speed < 5:
                        slow = True
                except Exception:
                    pass
        return (not slow), result
    return False, "Speedtest failed or timed out"

def test_wifi():
    # FIXED: use `ifconfig` (no args), search for wlan0
    ok_, out = run(["ifconfig"], timeout=3)
    if "wlan0" in out and "inet" in out:
        # extract wlan0 IP
        try:
            block = out.split("wlan0:")[1].split("\n\n")[0]
            m = re.search(r"inet\s+([\d.]+)", block)
            if m:
                return True, f"wlan0 active ({m.group(1)})"
        except Exception:
            pass
        return True, "wlan0 present"
    return False, "wlan0 not found"

def test_mobile():
    ok_, out = run(["ifconfig"], timeout=3)
    for iface in ["rmnet1", "rmnet5", "rmnet0", "ccmni0", "rmnet_data0"]:
        if iface in out:
            try:
                block = out.split(f"{iface}:")[1].split("\n\n")[0]
                m = re.search(r"inet\s+([\d.]+)", block)
                if m:
                    return True, f"{iface} active ({m.group(1)})"
            except Exception:
                pass
    return False, "No mobile data interface"

# ============ DIAGNOSIS ============

def diagnose(r):
    findings = []

    # Critical: no IP
    if not r["local_ip"][0]:
        findings.append(("critical", "NO local IP — WiFi or mobile data disconnected."))
        return findings

    # Router
    if not r["router"][0]:
        findings.append(("critical", "Cannot reach router — WiFi may be off or router down."))
    elif not r["router_latency"][0]:
        findings.append(("warn", f"Router latency high: {r['router_latency'][1]}"))

    # Traceroute check
    if not r["traceroute"][0]:
        findings.append(("warn", f"Network path issue: {r['traceroute'][1]}"))

    # Internet
    if not r["internet_ping"][0] and not r["tcp_connect"][0]:
        findings.append(("critical", "Cannot reach internet — ISP may be down."))
    elif not r["internet_ping"][0] and r["tcp_connect"][0]:
        findings.append(("info", "ICMP ping blocked by ISP (normal). TCP works."))

    # DNS
    if not r["dns"][0]:
        findings.append(("critical", "DNS broken — sites won't load by name. Try 1.1.1.1."))
    elif not r["dns_speed"][0]:
        findings.append(("warn", f"DNS slow: {r['dns_speed'][1]}. Try 1.1.1.1."))

    # HTTP
    if not r["http"][0] and r["dns"][0] and r["tcp_connect"][0]:
        findings.append(("warn", "HTTP failed but DNS/TCP work — target website may be down."))

    # Interfaces
    if not r["wifi"][0] and not r["mobile"][0]:
        findings.append(("critical", "NEITHER WiFi NOR mobile data detected — you're offline!"))
    elif not r["wifi"][0]:
        findings.append(("info", "WiFi not active (you may be on mobile data)."))
    elif not r["mobile"][0]:
        findings.append(("info", "Mobile data not active (you may be on WiFi)."))

    # Speed
    if r["speedtest"][1] and "Download" in r["speedtest"][1]:
        try:
            for part in r["speedtest"][1].split("|"):
                if "Download" in part:
                    sp = float(part.split(":")[1].split()[0])
                    if sp < 1:
                        findings.append(("critical", f"Download VERY slow ({sp} Mbps) — congestion or weak signal."))
                    elif sp < 5:
                        findings.append(("warn", f"Download slow ({sp} Mbps)."))
        except Exception:
            pass

    if not findings:
        findings.append(("ok", "No problems detected. Network is healthy."))

    return findings

# ============ MAIN ============

def run_once(n):
    now = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    print(f"\n{C.BOLD}{'═'*60}{C.END}")
    print(f"{C.BOLD}  🕵️  NETWORK DETECTIVE v2.1 — Run #{n}{C.END}")
    print(f"{C.BOLD}  {now}{C.END}")
    print(f"{C.BOLD}{'═'*60}{C.END}")

    tests = [
        ("local_ip",       "Local IP...............", test_local_ip),
        ("router",         "Router reachable.......", test_router),
        ("router_latency", "Router latency.........", test_router_latency),
        ("internet_ping",  "Internet ping..........", test_internet_ping),
        ("tcp_connect",    "TCP connect (port 53)..", test_tcp_connect),
        ("dns",            "DNS resolution.........", test_dns),
        ("dns_speed",      "DNS response time......", test_dns_speed),
        ("http",           "HTTP request...........", test_http),
        ("traceroute",     "Traceroute (5 hops)....", test_traceroute),
        ("wifi",           "WiFi interface.........", test_wifi),
        ("mobile",         "Mobile data interface..", test_mobile),
    ]

    if n % SPEEDTEST_EVERY_N_LOOPS == 0:
        tests.append(("speedtest", "Speed test............", test_speedtest))

    results = {}
    for key, label, func in tests:
        try:
            success, message = func()
        except Exception as e:
            success, message = False, f"Crashed: {e}"

        results[key] = (success, message)
        icon = f"{C.GREEN}✓{C.END}" if success else f"{C.RED}✗{C.END}"
        print(f"  {icon} {label} {message}")

    # default missing
    for key in ["speedtest"]:
        if key not in results:
            results[key] = (True, "skipped this loop")

    # Diagnosis
    print(f"\n{C.BOLD}{'━'*60}{C.END}")
    print(f"{C.BOLD}🔍 DIAGNOSIS{C.END}")
    print(f"{C.BOLD}{'━'*60}{C.END}")

    findings = diagnose(results)
    for level, msg in findings:
        if level == "critical": icon = f"{C.RED}❌{C.END}"
        elif level == "warn":   icon = f"{C.YELLOW}⚠{C.END}"
        elif level == "info":   icon = f"{C.BLUE}ℹ{C.END}"
        else:                   icon = f"{C.GREEN}✓{C.END}"
        print(f"  {icon}  {msg}")

    print(f"{C.BOLD}{'━'*60}{C.END}\n")
    log(f"Run #{n} — {len(findings)} findings")
    for lvl, m in findings:
        log(f"  [{lvl}] {m}")

if __name__ == "__main__":
    print(f"\n{C.BOLD}🕵️  NETWORK DETECTIVE v2.1{C.END}")
    print(f"   Loop: {LOOP_EVERY}s | Log: {LOG_FILE}")
    print(f"   Ctrl+C to stop\n")

    n = 1
    try:
        while True:
            run_once(n)
            n += 1
            print(f"⏳ Next in {LOOP_EVERY}s...")
            time.sleep(LOOP_EVERY)
    except KeyboardInterrupt:
        print(f"\n🛑 Stopped after {n-1} runs. Log: {LOG_FILE}")
