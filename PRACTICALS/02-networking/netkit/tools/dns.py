# ============================================
# NETKIT — tools/dns.py
# ============================================

import socket
from core import logger, utils


def dns_lookup(domain):
    if not domain:
        return {"ok": False, "error": "No domain provided"}

    ip = utils.resolve(domain)
    ok = ip is not None

    result = {"ok": ok, "domain": domain, "ip": ip}

    logger.get_report().log(
        "DNS",
        f"{domain} → {ip}" if ok else f"{domain} — FAILED",
        result,
    )
    return result
