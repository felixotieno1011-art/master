# ============================================
# NETKIT — tools/portscan.py
# ============================================

from core import config, logger, utils


def port_scan(target, ports=None):
    if not target:
        return {"ok": False, "error": "No target provided"}

    ip = utils.resolve(target)
    if not ip:
        return {"ok": False, "error": f"Cannot resolve {target}"}

    ports = ports or config.COMMON_PORTS
    open_ports = []
    closed_ports = []

    for port in ports:
        if utils.check_port(ip, port):
            open_ports.append(port)
        else:
            closed_ports.append(port)

    result = {
        "ok": True,
        "target": target,
        "ip": ip,
        "scanned": ports,
        "open": open_ports,
        "closed": closed_ports,
    }

    logger.get_report().log(
        "SCAN",
        f"{target} ({ip}) — {len(open_ports)} open: {open_ports}",
        result,
    )
    return result
