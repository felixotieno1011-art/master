# ============================================
# NETKIT — tools/ids.py
# Port scan detection. Now collects ALL alerts.
# ============================================

from collections import defaultdict
from core import config, logger


def ids_detect(traffic=None):
    """traffic: list of (ip, port) tuples. Default = built-in demo."""
    if traffic is None:
        traffic = [
            ("192.168.1.50", 443),
            ("192.168.1.50", 443),
            ("203.0.113.99", 22),
            ("203.0.113.99", 80),
            ("203.0.113.99", 443),
            ("203.0.113.99", 3306),
            ("203.0.113.99", 5432),
            ("203.0.113.99", 8080),
        ]

    activity = defaultdict(set)
    log_lines = []

    for ip, port in traffic:
        activity[ip].add(port)
        log_lines.append(f"{ip} → port {port}")

    alerts = []
    for ip, ports in activity.items():
        if len(ports) >= config.IDS_SCAN_THRESHOLD:
            alerts.append({"ip": ip, "ports": sorted(ports)})

    result = {
        "ok": True,
        "traffic": log_lines,
        "alerts": alerts,
        "clean": len(alerts) == 0,
    }

    for a in alerts:
        logger.get_report().log(
            "IDS",
            f"Port scan from {a['ip']} — ports {a['ports']}",
            a,
        )
    if not alerts:
        logger.get_report().log("IDS", "No threats detected", {})

    return result
