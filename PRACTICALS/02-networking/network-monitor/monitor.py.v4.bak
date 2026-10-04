#!/usr/bin/env python3
"""Network Monitor v4.0 — main flow only."""
from detect import detect_isp, detect_connection_type, get_isp_gateway
from ping   import ping_stats
from speed  import download_speed_mbps, upload_speed_mbps
from verdict import compute as compute_verdict

import config
import logger
import display


def run_once(run_number, isp, gateway_ip):
    logger.ensure_dirs()

    conn = detect_connection_type()
    isp_name = isp.get("isp", "unknown") if "error" not in isp else "unknown"

    display.header(run_number, conn)

    results = {"pings": {}, "download": None, "upload": None}
    gateway_stats = None

    # --- Layer 2: gateway ---
    display.section("📍 Layer 2 — ISP Gateway")
    if gateway_ip:
        print(f"   Pinging {gateway_ip}...", end=" ", flush=True)
        gateway_stats = ping_stats(gateway_ip)
        results["pings"][f"Gateway ({gateway_ip})"] = gateway_stats
        from utils import fmt_ms
        print(fmt_ms(gateway_stats["avg"]))
    else:
        print("   (not available on this connection)")

    # --- Layer 3: near targets ---
    display.section("🌍 Layer 3 — Public DNS (near)")
    near_stats = {}
    for name, ip in config.TARGETS_NEAR.items():
        s = ping_stats(ip)
        near_stats[name] = s
        results["pings"][name] = s
        display.ping_line(name, ip, s)

    # --- Layer 3b: far targets ---
    display.section("🌏 Layer 3b — Far targets (informational)")
    for name, ip in config.TARGETS_FAR.items():
        s = ping_stats(ip)
        results["pings"][name] = s
        display.ping_line(name, ip, s)

    # --- Layer 4: speed ---
    display.section("🚀 Layer 4 — Bandwidth")
    dl = download_speed_mbps()
    results["download"] = dl
    display.speed_line("Download", dl)

    ul = upload_speed_mbps()
    results["upload"] = ul
    display.speed_line("Upload", ul)

    # --- Verdict ---
    display.section("🔍 Diagnosis")
    level, msg = compute_verdict(conn, gateway_stats, near_stats, dl)
    display.verdict_line(level, msg)

    # --- Log ---
    logger.run_txt(conn, isp_name, results)
    logger.run_csv(conn, isp_name, results)
    display.footer()

    return results


def main():
    logger.ensure_dirs()

    print()
    conn = detect_connection_type()
    isp = detect_isp()
    display.isp_info(isp, conn)

    gateway = get_isp_gateway()
    display.gateway_line(gateway)

    logger.session_start(isp, conn)
    run_once(1, isp, gateway)


if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        from utils import GRAY, RESET
        print(f"\n\n{GRAY}🛑 Stopped. Progress saved.{RESET}")
