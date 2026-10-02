"""All terminal output — headers, sections, results."""
from datetime import datetime

from utils import (
    BOLD, RESET, GRAY, GREEN, YELLOW, RED, BLUE,
    fmt_ms, fmt_loss, fmt_mbps, hr
)
import config


def header(run_number, conn):
    print()
    print(f"{BOLD}{'=' * 60}{RESET}")
    print(f"{BOLD}🌐 Network Monitor v4.0 — Run #{run_number}{RESET}")
    print(f"   Connection: {conn}")
    print(f"   {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print(f"{BOLD}{'=' * 60}{RESET}")


def section(title):
    print()
    print(f"{BOLD}{BLUE}{title}{RESET}")
    print(hr())


def isp_info(isp, conn):
    print(f"{BOLD}📡 Detecting network...{RESET}")
    if "error" in isp:
        print(f"   {YELLOW}⚠  ISP detection failed: {isp['error']}{RESET}")
    else:
        print(f"   ✓ ISP:      {isp['isp']}")
        print(f"   ✓ Location: {isp['city']}, {isp['country']}")
        print(f"   ✓ Public IP: {isp['ip']}")
        print(f"   ✓ Connection: {conn}")


def gateway_line(gateway_ip):
    print()
    print(f"{BOLD}🛰  Finding ISP gateway...{RESET}")
    if gateway_ip:
        print(f"   ✓ Gateway: {gateway_ip}")
    else:
        print(f"   {GRAY}⚠  Not detected (normal on MOBILE){RESET}")


def ping_line(label, ip, stats):
    """Print one target's ping result inline."""
    print(f"   {label:<14} ({ip})...", end=" ", flush=True)
    print(f"{fmt_ms(stats['avg'])}   loss {fmt_loss(stats['loss'])}")


def speed_line(label, mbps):
    print(f"   {label}...", end=" ", flush=True)
    print(fmt_mbps(mbps))


def verdict_line(level, message):
    icon  = {"ok": "✓", "warn": "⚠", "critical": "❌"}[level]
    color = {"ok": GREEN, "warn": YELLOW, "critical": RED}[level]
    print(f"   {color}{icon} {message}{RESET}")


def footer():
    print()
    print(f"{GRAY}Logged to {config.LOG_TXT} and {config.LOG_CSV}{RESET}")
    print(f"{BOLD}{'=' * 60}{RESET}")
    print()
