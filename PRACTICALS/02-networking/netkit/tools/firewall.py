# ============================================
# NETKIT — tools/firewall.py
# ============================================

from core import config, logger, utils


def firewall_check(target):
    if not target:
        return {"ok": False, "error": "No target provided"}

    ip = utils.resolve(target)
    if not ip:
        return {"ok": False, "error": f"Cannot resolve {target}"}

    allowed = []
    blocked = []

    for port, name in config.FIREWALL_PORTS.items():
        if utils.check_port(ip, port):
            allowed.append({"port": port, "name": name})
        else:
            blocked.append({"port": port, "name": name})

    result = {
        "ok": True,
        "target": target,
        "ip": ip,
        "allowed": allowed,
        "blocked": blocked,
    }

    logger.get_report().log(
        "FIREWALL",
        f"{target} — allowed: {[a['port'] for a in allowed]}",
        result,
    )
    return result
