# ============================================
# NETKIT — tools/traceroute.py
# ============================================

from core import config, logger, utils


def traceroute_test(target):
    if not target:
        return {"ok": False, "error": "No target provided"}

    if not utils.tool_exists("traceroute"):
        return {"ok": False, "error": "traceroute not installed"}

    cmd = [
        "traceroute",
        "-m", str(config.TRACEROUTE_MAX_HOPS),
        "-w", str(config.TRACEROUTE_TIMEOUT),
        target,
    ]
    out, err, ok = utils.safe_run(cmd, config.TRACEROUTE_TOTAL_TIMEOUT)

    result = {"ok": ok, "target": target, "raw": out}

    logger.get_report().log(
        "TRACEROUTE",
        f"{target} — {'completed' if ok else 'failed'}",
        {"target": target, "ok": ok},
    )
    return result
