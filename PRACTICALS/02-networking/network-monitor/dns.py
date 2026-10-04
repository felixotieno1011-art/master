"""DNS measurement + CGNAT detection."""
import subprocess
import re
import socket
import time


# ---- Test domains (use different TLDs to avoid caching) ----
TEST_DOMAINS = ["google.com", "cloudflare.com", "wikipedia.org"]

# ---- DNS servers to compare ----
DNS_SERVERS = {
    "default":  None,              # System default
    "Google":   "8.8.8.8",
    "Cloudflare": "1.1.1.1",
}


def _time_resolution(domain, nameserver=None, timeout=5):
    """Measure how long a DNS lookup takes. Return ms or None."""
    cmd = ["dig", "+short", "+time=3", "+tries=1"]
    if nameserver:
        cmd += [f"@{nameserver}"]
    cmd += [domain]

    try:
        start = time.time()
        result = subprocess.run(
            cmd, capture_output=True, text=True, timeout=timeout
        )
        elapsed = (time.time() - start) * 1000  # ms

        # dig returns 0 even on NXDOMAIN; check for actual answer
        if result.returncode == 0 and result.stdout.strip():
            return round(elapsed, 1)
        return None
    except Exception:
        return None


def resolve_default(domain):
    """Use Python's own resolver (the system default)."""
    try:
        start = time.time()
        socket.gethostbyname(domain)
        return round((time.time() - start) * 1000, 1)
    except Exception:
        return None


def dns_resolution_time(domain="google.com"):
    """Return ms to resolve domain using the system resolver, or None."""
    return resolve_default(domain)


def dns_comparison():
    """
    Compare DNS resolution across servers.
    Returns dict: {server_name: avg_ms or None}
    """
    results = {}
    for name, server in DNS_SERVERS.items():
        times = []
        for domain in TEST_DOMAINS:
            t = _time_resolution(domain, server)
            if t is not None:
                times.append(t)
        results[name] = round(sum(times) / len(times), 1) if times else None
    return results


def get_dns_servers():
    """Read DNS servers from /etc/resolv.conf (may be empty on Android)."""
    try:
        with open("/etc/resolv.conf") as f:
            servers = []
            for line in f:
                line = line.strip()
                if line.startswith("nameserver"):
                    servers.append(line.split()[1])
            return servers if servers else ["(system default)"]
    except Exception:
        return ["(not readable)"]


def detect_cgnat():
    """
    Return dict: {'local_ips': [...], 'public_ip': str, 'behind_cgnat': bool}
    CGNAT range is 100.64.0.0/10.
    """
    local_ips = []
    try:
        result = subprocess.run(
            ["ip", "addr"], capture_output=True, text=True, timeout=5
        )
        for m in re.finditer(r"inet\s+(\d+\.\d+\.\d+\.\d+)", result.stdout):
            ip = m.group(1)
            if not ip.startswith("127."):
                local_ips.append(ip)
    except Exception:
        try:
            result = subprocess.run(
                ["ifconfig"], capture_output=True, text=True, timeout=5
            )
            for m in re.finditer(r"inet\s+(?:addr:)?(\d+\.\d+\.\d+\.\d+)", result.stdout):
                ip = m.group(1)
                if not ip.startswith("127."):
                    local_ips.append(ip)
        except Exception:
            pass

    behind_cgnat = False
    for ip in local_ips:
        parts = ip.split(".")
        try:
            first, second = int(parts[0]), int(parts[1])
            # 100.64.0.0/10 means first == 100 and 64 <= second <= 127
            if first == 100 and 64 <= second <= 127:
                behind_cgnat = True
        except Exception:
            pass

    return {
        "local_ips":   local_ips,
        "behind_cgnat": behind_cgnat,
    }
