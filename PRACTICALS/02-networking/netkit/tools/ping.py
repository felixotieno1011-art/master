# ============================================
# NETKIT — tools/ping.py
# ============================================

import re
from core import config, logger, utils


def ping_test(target, count=None):
    """Ping a host. Returns dict with result."""
    if not target:
        return {"ok": False, "error": "No target provided"}

    count = count or config.PING_COUNT
    cmd = ["ping", "-c", str(count), "-W", str(config.PING_TIMEOUT), target]
    out, err, ok = utils.safe_run(cmd, config.PING_TOTAL_TIMEOUT)

    result = {
        "ok": ok,
        "target": target,
        "reachable": ok,
        "min_ms": None,
        "avg_ms": None,
        "max_ms": None,
        "raw": out,
    }

    if ok:
        m = re.search(
            r"rtt [^=]*=\s*([\d.]+)/([\d.]+)/([\d.]+)",
            out
        )
        if m:
            result["min_ms"] = float(m.group(1))
            result["avg_ms"] = float(m.group(2))
            result["max_ms"] = float(m.group(3))

    logger.get_report().log(
        "PING",
        f"{target} — {'reachable' if ok else 'NOT reachable'}"
        + (f", avg {result['avg_ms']} ms" if result["avg_ms"] else ""),
        {"target": target, "reachable": ok, "avg_ms": result["avg_ms"]},
    )
    return result
