#!/usr/bin/env python3
# ============================================
# mini_ids.py — Detects port scans (like a real IDS)
# Anomaly-based: detects "weird" behavior
# ============================================

import time
from collections import defaultdict
from datetime import datetime

# ---- Configuration ----
PORT_SCAN_THRESHOLD = 5     # If 1 IP hits 5+ ports in 10s → alert
TIME_WINDOW = 10            # seconds to consider

# ---- Track activity ----
recent_activity = defaultdict(list)   # {ip: [(timestamp, port), ...]}
alerted_ips = set()                    # don't spam alerts for same IP

def clean_old_entries(now):
    """Remove entries older than TIME_WINDOW."""
    for ip in list(recent_activity.keys()):
        recent_activity[ip] = [
            (t, p) for (t, p) in recent_activity[ip]
            if now - t < TIME_WINDOW
        ]
        if not recent_activity[ip]:
            del recent_activity[ip]
            alerted_ips.discard(ip)

def log_connection(source_ip, dest_port):
    """Record a connection attempt."""
    now = time.time()
    recent_activity[source_ip].append((now, dest_port))

    # Clean up old data
    clean_old_entries(now)

    # Check for port scan behavior
    ports_hit = set(p for (t, p) in recent_activity[source_ip])
    if len(ports_hit) >= PORT_SCAN_THRESHOLD:
        if source_ip not in alerted_ips:
            alerted_ips.add(source_ip)
            timestamp = datetime.now().strftime("%H:%M:%S")
            print(f"🚨 [{timestamp}] PORT SCAN DETECTED!")
            print(f"   Source IP: {source_ip}")
            print(f"   Ports hit: {sorted(ports_hit)}")
            print(f"   In window: {TIME_WINDOW}s\n")
    else:
        # Normal connection, log quietly
        timestamp = datetime.now().strftime("%H:%M:%S")
        print(f"✓ [{timestamp}] {source_ip} → port {dest_port}")

# =====================================================
# Simulate traffic (instead of real network capture,
# which needs root on Android)
# =====================================================
def simulate_normal_traffic():
    """Simulate a normal user making a few connections."""
    print("=" * 60)
    print("📊 SCENARIO 1: Normal user (browser, app)")
    print("=" * 60)
    print("A normal user makes a few requests.\n")

    # One user makes 3 requests to different sites
    log_connection("192.168.1.50", 443)   # HTTPS to google
    time.sleep(0.3)
    log_connection("192.168.1.50", 443)   # HTTPS to github
    time.sleep(0.3)
    log_connection("192.168.1.50", 80)    # HTTP request

    print("\n✅ Normal activity. No alerts.\n")

def simulate_port_scan():
    """Simulate an attacker scanning many ports quickly."""
    print("=" * 60)
    print("📊 SCENARIO 2: Attacker scanning ports")
    print("=" * 60)
    print("An attacker tries many ports in quick succession.\n")

    attacker_ip = "203.0.113.99"
    for port in [22, 80, 443, 3306, 5432, 8080]:
        log_connection(attacker_ip, port)
        time.sleep(0.2)   # fast

    print("\n🚨 Alert triggered! IDS caught the scan.\n")

def simulate_slow_scan():
    """Simulate a slow scan (evading detection)."""
    print("=" * 60)
    print("📊 SCENARIO 3: Slow scan (trying to evade)")
    print("=" * 60)
    print("An attacker spreads attempts across time to avoid detection.\n")

    attacker_ip = "198.51.100.42"
    for port in [22, 80]:
        log_connection(attacker_ip, port)
        time.sleep(0.3)

    print("   [Attacker waits 11 seconds to reset the window]")
    time.sleep(11)   # longer than TIME_WINDOW, so old data expires

    for port in [443, 3306]:
        log_connection(attacker_ip, port)

    print("\n⚠  Slow scan completed without triggering alert.")
    print("   (This is called 'low and slow' scanning.)\n")

# =====================================================
# Main
# =====================================================
def main():
    print("\n" + "=" * 60)
    print("🕵️  MINI IDS — Intrusion Detection System")
    print("=" * 60)
    print(f"Config: alert if 1 IP hits {PORT_SCAN_THRESHOLD}+ ports in {TIME_WINDOW}s\n")
    time.sleep(1)

    simulate_normal_traffic()
    time.sleep(1)

    simulate_port_scan()
    time.sleep(1)

    simulate_slow_scan()

    print("=" * 60)
    print("📋 SUMMARY")
    print("=" * 60)
    print("• Normal user: 3 ports → no alert")
    print("• Fast scan: 6 ports in 1.2s → ALERT ✅")
    print("• Slow scan: 2 ports, wait, 2 ports → no alert ❌")
    print()
    print("💡 Lesson: fast scans are caught. Slow scans evade.")
    print("   Real IDS also uses long-term analysis for slow scans.")
    print("=" * 60)

if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        print("\n🛑 Stopped.")
