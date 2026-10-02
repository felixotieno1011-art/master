"""Measure latency, packet loss, jitter."""
import subprocess
import re
import statistics
from config import PING_COUNT, PING_TIMEOUT


def _run_ping(target, count):
    """Run ping and return raw stdout, or '' on failure."""
    try:
        result = subprocess.run(
            ["ping", "-c", str(count), "-W", str(PING_TIMEOUT), target],
            capture_output=True, text=True, timeout=count * PING_TIMEOUT + 5
        )
        return result.stdout
    except Exception:
        return ""


def ping_stats(target, count=PING_COUNT):
    """Return dict: avg, min, max, loss, jitter. All may be None."""
    out = _run_ping(target, count)

    result = {"avg": None, "min": None, "max": None,
              "loss": 100.0, "jitter": None}

    if not out:
        return result

    # Example: rtt min/avg/max/mdev = 44.123/45.678/47.890/1.234 ms
    m = re.search(
        r"rtt [^=]*=\s*([\d.]+)/([\d.]+)/([\d.]+)/([\d.]+)",
        out
    )
    if m:
        result["min"]    = float(m.group(1))
        result["avg"]    = float(m.group(2))
        result["max"]    = float(m.group(3))
        result["jitter"] = float(m.group(4))   # mdev = jitter

    # Packet loss
    m = re.search(r"([\d.]+)%\s*packet loss", out)
    if m:
        result["loss"] = float(m.group(1))

    return result


def ping_avg(target, count=PING_COUNT):
    """Backward-compatible: return just the average, or None."""
    return ping_stats(target, count)["avg"]
