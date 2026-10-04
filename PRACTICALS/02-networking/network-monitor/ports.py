"""Check common TCP ports on public hosts."""
import socket
import time


# ---- Ports to test ----
# (port, label)
PORTS = [
    (80,  "HTTP"),
    (443, "HTTPS"),
    (53,  "DNS"),
]

# ---- Hosts to test against ----
TEST_HOSTS = {
    "Google":     "google.com",
    "Cloudflare": "cloudflare.com",
}


def check_port(host, port, timeout=3):
    """
    Try to connect to (host, port).
    Return dict: {'open': bool, 'ms': float|None}
    """
    try:
        start = time.time()
        sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        sock.settimeout(timeout)
        result = sock.connect_ex((host, port))
        elapsed = round((time.time() - start) * 1000, 1)
        sock.close()

        if result == 0:
            return {"open": True, "ms": elapsed}
        return {"open": False, "ms": None}
    except Exception:
        return {"open": False, "ms": None}


def check_all_ports():
    """
    Return dict:
    {
      'Google': {'80': {'open': True, 'ms': 45}, '443': {...}, '53': {...}},
      'Cloudflare': {...},
    }
    """
    results = {}
    for name, host in TEST_HOSTS.items():
        results[name] = {}
        for port, label in PORTS:
            r = check_port(host, port)
            results[name][str(port)] = {
                "label": label,
                "open":  r["open"],
                "ms":    r["ms"],
            }
    return results
