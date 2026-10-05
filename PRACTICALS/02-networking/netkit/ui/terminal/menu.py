# ============================================
# NETKIT — ui/terminal/menu.py
# Interactive menu loop.
# ============================================

from . import banner, render
from .banner import C, paint
from core import logger
from tools import (
    ping, dns, portscan, traceroute,
    firewall, loadbalancer, ids,
)


def ask(prompt):
    return input(paint(prompt, C.BOLD)).strip()


def pause():
    input(paint("\nPress Enter to return to menu...", C.DIM))


def print_menu():
    print(paint("Choose an option:", C.BOLD))
    print()
    options = [
        ("1", "Ping Test"),
        ("2", "Port Scan"),
        ("3", "DNS Lookup"),
        ("4", "Traceroute"),
        ("5", "Firewall Check"),
        ("6", "Load Balancer Sim"),
        ("7", "IDS Port Scan Detect"),
        ("8", "Show Report"),
        ("0", "Exit"),
    ]
    for num, label in options:
        print(f"  {paint(num + ')', C.CYAN)} {label}")
    print()


def run_choice(choice):
    if choice == "1":
        render.header("Ping Test")
        target = ask("Host to ping: ")
        if not target:
            print(render.fail("No target."))
        else:
            render.render_ping(ping.ping_test(target))

    elif choice == "2":
        render.header("Port Scan")
        target = ask("Target (host or IP): ")
        if not target:
            print(render.fail("No target."))
        else:
            render.render_portscan(portscan.port_scan(target))

    elif choice == "3":
        render.header("DNS Lookup")
        domain = ask("Domain: ")
        if not domain:
            print(render.fail("No domain."))
        else:
            render.render_dns(dns.dns_lookup(domain))

    elif choice == "4":
        render.header("Traceroute")
        target = ask("Target: ")
        if not target:
            print(render.fail("No target."))
        else:
            render.render_traceroute(traceroute.traceroute_test(target))

    elif choice == "5":
        render.header("Firewall Check")
        target = ask("Target: ")
        if not target:
            print(render.fail("No target."))
        else:
            render.render_firewall(firewall.firewall_check(target))

    elif choice == "6":
        render.header("Load Balancer Sim")
        n = ask("How many requests? ")
        algo = ask("Algorithm (roundrobin/leastconn/iphash): ").lower() or "roundrobin"
        render.render_loadbalancer(loadbalancer.load_balancer_sim(n, algo))

    elif choice == "7":
        render.header("IDS — Port Scan Detect")
        render.render_ids(ids.ids_detect())

    elif choice == "8":
        render.header("Current Report")
        text = logger.get_report().read()
        if text:
            render.render_report(text)
            print(paint(f"\nSaved at: {logger.get_report().path()}", C.DIM))
        else:
            print(render.warn("No report yet."))

    elif choice == "0":
        print()
        print(render.ok("Goodbye!"))
        return False

    else:
        print(render.fail("Invalid choice."))

    return True


def loop():
    banner.print_banner()
    running = True
    while running:
        print_menu()
        choice = ask("Choose (0-8): ")
        running = run_choice(choice)
        if running:
            pause()
        print()
