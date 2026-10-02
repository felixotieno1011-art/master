"""Detect: ISP info, connection type, ISP gateway. Cross-platform."""
import subprocess
import re
import json
import urllib.request


def detect_isp():
    """Return dict with ip, isp, city, region, country."""
    try:
        req = urllib.request.Request(
            "https://ipinfo.io/json",
            headers={"User-Agent": "NetworkMonitor/4"}
        )
        with urllib.request.urlopen(req, timeout=8) as r:
            data = json.loads(r.read().decode())
        return {
            "ip":      data.get("ip", "unknown"),
            "isp":     data.get("org", "unknown"),
            "city":    data.get("city", "unknown"),
            "region":  data.get("region", "unknown"),
            "country": data.get("country", "unknown"),
        }
    except Exception as e:
        return {"error": str(e)}


def detect_connection_type():
    """Return 'WIFI', 'MOBILE', or 'UNKNOWN'. Works on Termux and Linux."""
    out = ""

    # Try 'ip addr' first (modern Linux), then 'ifconfig' (Termux)
    for cmd in (["ip", "addr"], ["ifconfig"]):
        try:
            result = subprocess.run(cmd, capture_output=True,
                                    text=True, timeout=5)
            if result.returncode == 0 and result.stdout:
                out = result.stdout
                break
        except FileNotFoundError:
            continue

    if not out:
        return "UNKNOWN"

    # WiFi: wlan0 (Termux) or wlp* (Linux laptops)
    wifi = False
    if "wlan0" in out or "wlp" in out:
        if re.search(r"inet\s+(192\.168|10)\.", out):
            wifi = True

    # Mobile: rmnet*, ccmni*, wwan*
    mobile = False
    for iface in ["rmnet0", "rmnet1", "rmnet5", "ccmni0", "wwan0"]:
        if iface in out:
            # Look for an IP in the next ~300 chars after the interface name
            block = out.split(iface, 1)[1][:300]
            if re.search(r"inet\s+\d", block):
                mobile = True
                break

    if wifi:
        return "WIFI"
    if mobile:
        return "MOBILE"
    return "UNKNOWN"


def is_private_ip(ip):
    """Return True for 10.x, 192.168.x, 127.x (CGNAT 100.x and 172.x are NOT local)."""
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
    """Return first non-private hop toward 8.8.8.8, or None."""
    for cmd in (["traceroute", "-m", "5", "-w", "2", "8.8.8.8"],
                ["tracepath", "-m", "5", "8.8.8.8"]):
        try:
            result = subprocess.run(cmd, capture_output=True,
                                    text=True, timeout=20)
            for line in result.stdout.split("\n"):
                line = line.strip()
                if not line or not line[0].isdigit():
                    continue
                if line.startswith("1 "):
                    continue
                m = re.search(r"\(?([\d.]+)\)?", line)
                if m:
                    ip = m.group(1)
                    if ip.count(".") == 3 and not is_private_ip(ip):
                        return ip
            return None
        except FileNotFoundError:
            continue
        except Exception:
            return None
    return None
