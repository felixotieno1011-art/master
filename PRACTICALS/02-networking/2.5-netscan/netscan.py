# ============================================
# NETSCAN — Network Health Scanner
# Built by Felix, Oct 2026
# ============================================

import subprocess
import socket
import time
import re

# ------------------------------------------
# Helper functions (small tools we'll use)
# ------------------------------------------

def run(cmd):
    """Run a shell command and return its output."""
    try:
        result = subprocess.run(cmd, shell=True, capture_output=True, text=True, timeout=15)
        return result.stdout + result.stderr
    except Exception as e:
        return f"Error: {e}"

def header(text):
    """Print a nice section header."""
    print("\n" + "─" * 50)
    print(f"  {text}")
    print("─" * 50)

def check_icon(condition):
    """Return ✅ or ⚠️ based on condition."""
    return "✅" if condition else "⚠️ "

# ------------------------------------------
# Step 1: Get my own IP
# ------------------------------------------

def get_my_ip():
    print("\n📍 YOUR DEVICE")
    out = run("ifconfig wlan0 2>/dev/null | grep inet")
    match = re.search(r"inet (\d+\.\d+\.\d+\.\d+)", out)
    if match:
        ip = match.group(1)
        print(f"   IP:        {ip}")
        print(f"   Interface: wlan0 (WiFi)")
        print(f"   Status:    ✅ Connected")
        return ip
    print("   ❌ Not on WiFi")
    return None

# ------------------------------------------
# Step 2: Find the gateway (router)
# ------------------------------------------

def find_gateway(my_ip):
    if not my_ip:
        return None
    # Assume gateway is x.x.x.1 on same network
    parts = my_ip.split(".")
    gateway = f"{parts[0]}.{parts[1]}.{parts[2]}.1"
    return gateway

# ------------------------------------------
# Step 3: Test the router
# ------------------------------------------

def test_router(gateway):
    header("🌐 GATEWAY (Router)")
    print(f"   IP:        {gateway}")

    # Ping test
    out = run(f"ping -c 3 {gateway}")
    times = re.findall(r"time=([\d.]+)", out)
    if times:
        avg = sum(float(t) for t in times) / len(times)
        icon = "✅" if avg < 30 else "⚠️ "
        print(f"   Ping:      {icon} {avg:.1f}ms")
    else:
        print(f"   Ping:      ❌ No response")

    # Port checks
    for port, service in [(80, "admin HTTP"), (443, "admin HTTPS"), (53, "DNS")]:
        out = run(f"timeout 2 bash -c 'echo > /dev/tcp/{gateway}/{port}' 2>&1")
        if "Error" not in out and "refused" not in out.lower():
            print(f"   Port {port:<5} {service:15} ✅ Open")
        else:
            print(f"   Port {port:<5} {service:15} ❌ Closed")

# ------------------------------------------
# Step 4: Scan for other devices
# ------------------------------------------

def scan_devices(my_ip):
    header("📡 DEVICES ON NETWORK")
    if not my_ip:
        return 0

    # Build network range (assume /24)
    parts = my_ip.split(".")
    network = f"{parts[0]}.{parts[1]}.{parts[2]}.0/24"
    print(f"   Scanning {network}...")

    out = run(f"nmap -sn {network} 2>/dev/null")
    devices = re.findall(r"Nmap scan report for (\S+)", out)
    print(f"   Found:     {len(devices)} devices")
    for d in devices:
        print(f"   - {d}")
    return len(devices)

# ------------------------------------------
# Step 5: Test internet + speed
# ------------------------------------------

def test_internet():
    header("🌍 INTERNET")

    # Ping public DNS servers
    for name, ip in [("Google DNS", "8.8.8.8"), ("Cloudflare", "1.1.1.1")]:
        out = run(f"ping -c 2 {ip}")
        times = re.findall(r"time=([\d.]+)", out)
        if times:
            avg = sum(float(t) for t in times) / len(times)
            icon = "✅" if avg < 150 else "⚠️ "
            print(f"   {name} ({ip}):  {icon} {avg:.0f}ms")
        else:
            print(f"   {name} ({ip}):  ❌ No response")

    # Speed test (5MB download)
    print(f"   Speed test...")
    start = time.time()
    run("curl -s -o /dev/null https://speed.cloudflare.com/__down?bytes=5000000")
    duration = time.time() - start
    mbps = (5 / duration) * 8 if duration > 0 else 0
    icon = "✅" if mbps > 5 else "⚠️ " if mbps > 1 else "❌"
    print(f"   Download:  {icon} {mbps:.1f} Mbps ({duration:.1f}s for 5MB)")
    return mbps

# ------------------------------------------
# Step 6: Diagnose problems
# ------------------------------------------

def diagnose(device_count, speed):
    header("🔍 DIAGNOSIS")
    problems = []

    if speed < 1:
        problems.append("Very SLOW internet (<1 Mbps)")
        problems.append("  Likely: network congestion or weak WiFi")
        problems.append("  Try: move closer to router, or test again later")
    elif speed < 5:
        problems.append("Slow internet (<5 Mbps)")
        problems.append("  Likely: too many devices or ISP throttling")

    if device_count > 10:
        problems.append(f"{device_count} devices on network — could cause congestion")

    if not problems:
        print("   ✅ Your network looks healthy!")
    else:
        for p in problems:
            print(f"   ⚠️  {p}")

# ------------------------------------------
# Main
# ------------------------------------------

def main():
    print("╔" + "═" * 48 + "╗")
    print("║  🔍 NETWORK HEALTH REPORT" + " " * 24 + "║")
    print("║  Generated: " + time.strftime("%Y-%m-%d %H:%M") + " " * 24 + "║")
    print("╚" + "═" * 48 + "╝")

    my_ip = get_my_ip()
    gateway = find_gateway(my_ip)

    if gateway:
        test_router(gateway)

    device_count = scan_devices(my_ip)
    speed = test_internet()

    diagnose(device_count, speed)

    print("\n" + "─" * 50)
    print("  Report complete ✅")
    print("─" * 50 + "\n")

if __name__ == "__main__":
    main()
