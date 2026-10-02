#!/usr/bin/env python3
# ============================================
# NETWORK DETECTIVE
# Tests network layer-by-layer to find what's broken
# ============================================

import socket
import subprocess
import sys
import time
import urllib.request
from datetime import datetime

# ---------- CONFIG ----------
TARGET_SITE = "github.com"
TARGET_PING = "8.8.8.8"  # Google's public DNS (always reachable)
LOOP_EVERY = None  # Set to 10 for continuous monitoring every 10 sec

# ---------- TEST 1: Local IP (DHCP Layer) ----------
def test_local_ip():
    """Check if we got a local IP from the router."""
    try:
        s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        s.settimeout(2)
        s.connect(("8.8.8.8", 80))  # doesn't actually send, just picks route
        local_ip = s.getsockname()
        s.close()
        return True, f"Local IP is {local_ip}"
    except Exception as e:
        return False, f"No local IP found: {e}"

# ---------- TEST 2: Ping the internet (Routing/NAT) ----------
def test_ping():
    """Can we reach the outside world?"""
    try:
        result = subprocess.run(
            ["ping", "-c", "1", "-W", "2", TARGET_PING],
            capture_output=True, text=True, timeout=5
        )
        if result.returncode == 0:
            # extract time
            for line in result.stdout.split("\n"):
                if "time=" in line:
                    time_part = line.split("time=")[1].split()[0]
                    return True, f"Ping to {TARGET_PING} succeeded ({time_part})"
            return True, f"Ping to {TARGET_PING} succeeded"
        else:
            return False, f"CRITICAL: Connected to router, but packets cannot reach the internet."
    except subprocess.TimeoutExpired:
        return False, f"CRITICAL: Ping to {TARGET_PING} timed out — ISP may be down."
    except Exception as e:
        return False, f"Ping error: {e}"

# ---------- TEST 3: DNS Resolution (Application Layer) ----------
def test_dns():
    """Can we translate a domain name to an IP?"""
    try:
        ip = socket.gethostbyname(TARGET_SITE)
        return True, f"{TARGET_SITE} resolves to {ip}"
    except Exception as e:
        return False, f"CRITICAL: DNS is not working — cannot resolve {TARGET_SITE} ({e})"

# ---------- TEST 4: HTTP Request (Application Layer) ----------
def test_http():
    """Can we actually get a web page?"""
    try:
        url = f"https://{TARGET_SITE}"
        req = urllib.request.Request(url, headers={"User-Agent": "NetDetective/1.0"})
        with urllib.request.urlopen(req, timeout=5) as response:
            return True, f"Target website response status: {response.status}"
    except urllib.error.HTTPError as e:
        return False, f"Website responded with error: {e.code}"
    except Exception as e:
        return False, f"CRITICAL: Cannot reach {TARGET_SITE} ({e})"

# ---------- RUN ALL TESTS ----------
def run_audit():
    timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    print(f"\n--- Network Audit: {timestamp} ---")

    tests = [
        ("Layer 3 (IP/DHCP)",              test_local_ip),
        ("Layer 3/4 (Routing/NAT)",        test_ping),
        ("Application Layer (DNS)",        test_dns),
        ("Application Layer (HTTP)",       test_http),
    ]

    all_ok = True
    for label, test_func in tests:
        try:
            ok, message = test_func()
        except Exception as e:
            ok, message = False, f"Test crashed: {e}"

        icon = "✓" if ok else "✗"
        print(f" [ {icon} ] {label}: {message}")

        if not ok:
            all_ok = False

    return all_ok

# ---------- MAIN ----------
if __name__ == "__main__":
    print("🕵️  Network Detective starting...")
    print(f"   Target site: {TARGET_SITE}")
    print(f"   Ping target: {TARGET_PING}")

    if LOOP_EVERY:
        print(f"   Continuous mode: every {LOOP_EVERY} seconds (Ctrl+C to stop)")
        try:
            while True:
                run_audit()
                time.sleep(LOOP_EVERY)
        except KeyboardInterrupt:
            print("\n\n🛑 Stopped by user. Goodbye.")
    else:
        run_audit()
        print("\n✅ Audit complete.")
