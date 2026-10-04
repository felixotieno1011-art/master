#!/usr/bin/env python3
"""Network Monitor v4.1 — 7 layers."""
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

    results = {"pings": {}, "download": None, "upload": None,
               "dns": None, "ports": None, "http": None}
    gateway_stats = None

    display.section("📍 Layer 2 — ISP Gateway")
    if gateway_ip:
        from utils import fmt_ms
        print(f"   Pinging {gateway_ip}...", end=" ", flush=True)
        gateway_stats = ping_stats(gateway_ip)
        results["pings"][f"Gateway ({gateway_ip})"] = gateway_stats
        print(fmt_ms(gateway_stats["avg"]))
    else:
        print("   (not available on this connection)")

    display.section("🌍 Layer 3 — Public DNS (near)")
    near_stats = {}
    for name, ip in config.TARGETS_NEAR.items():
        s = ping_stats(ip)
        near_stats[name] = s
        results["pings"][name] = s
        display.ping_line(name, ip, s)

    display.section("🌏 Layer 3b — Far targets (informational)")
    for name, ip in config.TARGETS_FAR.items():
        s = ping_stats(ip)
        results["pings"][name] = s
        display.ping_line(name, ip, s)

    display.section("🚀 Layer 4 — Bandwidth")
    dl = download_speed_mbps()
    results["download"] = dl
    display.speed_line("Download", dl)
    ul = upload_speed_mbps()
    results["upload"] = ul
    display.speed_line("Upload", ul)

    if config.ENABLE_DNS:
        display.section("🧭 Layer 5 — DNS")
        try:
            from dns import dns_comparison, dns_resolution_time
            system_ms = dns_resolution_time("google.com")
            comparison = dns_comparison()
            results["dns"] = {"system": system_ms, "servers": comparison}
            print(f"   System default: {system_ms} ms" if system_ms else "   System default: FAILED")
            for server_name, ms in comparison.items():
                print(f"   {server_name:<12} {ms} ms" if ms else f"   {server_name:<12} FAILED")
        except Exception as e:
            print(f"   ⚠ DNS test error: {e}")

    if config.ENABLE_HTTP:
        display.section("🌐 Layer 6 — HTTP Response")
        try:
            from http_test import test_all_sites
            http_results = test_all_sites()
            results["http"] = http_results
            for site, r in http_results.items():
                status = r.get("status")
                ttfb   = r.get("ttfb_ms")
                if status is None:
                    print(f"   {site:<12} FAIL   {r.get('error','')}")
                else:
                    ttfb_str = f"{ttfb:.0f} ms" if ttfb else "—"
                    print(f"   {site:<12} HTTP {status}   {ttfb_str}")
        except Exception as e:
            print(f"   ⚠ HTTP test error: {e}")

    if config.ENABLE_PORTS:
        display.section("🔌 Layer 7 — Port Reachability")
        try:
            from ports import check_all_ports
            port_results = check_all_ports()
            results["ports"] = port_results
            for host, host_ports in port_results.items():
                statuses = []
                for port, data in host_ports.items():
                    mark = "✓" if data["open"] else "✗"
                    statuses.append(f"{mark}{port}")
                print(f"   {host:<12} {' '.join(statuses)}")
        except Exception as e:
            print(f"   ⚠ Port test error: {e}")

    display.section("🔍 Diagnosis")
    level, msg = compute_verdict(conn, gateway_stats, near_stats, dl)
    display.verdict_line(level, msg)

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
