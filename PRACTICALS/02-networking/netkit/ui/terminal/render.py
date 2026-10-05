# ============================================
# NETKIT — ui/terminal/render.py
# Turn tool result dicts into pretty terminal output.
# ============================================

from .banner import C, paint


def ok(text):    return paint(f"✅ {text}", C.GREEN)
def fail(text):  return paint(f"❌ {text}", C.RED)
def warn(text):  return paint(f"⚠️  {text}", C.YELLOW)
def info(text):  return paint(text, C.CYAN)
def bold(text):  return paint(text, C.BOLD)


def header(title):
    print()
    print(bold(paint(f"── {title} " + "─" * max(0, 45 - len(title)), C.CYAN)))


def render_ping(r):
    if not r.get("ok"):
        print(fail(r.get("error", "ping failed")))
        return
    print(ok(f"{r['target']} is reachable"))
    if r["avg_ms"] is not None:
        print(f"   Min: {r['min_ms']} ms")
        print(f"   Avg: {r['avg_ms']} ms")
        print(f"   Max: {r['max_ms']} ms")


def render_dns(r):
    if not r.get("ok"):
        print(fail(r.get("error", f"cannot resolve {r.get('domain')}")))
        return
    print(ok(f"{r['domain']} → {r['ip']}"))


def render_portscan(r):
    if not r.get("ok"):
        print(fail(r.get("error", "scan failed")))
        return
    print(info(f"Target: {r['target']} ({r['ip']})"))
    for port in r["scanned"]:
        if port in r["open"]:
            print("   " + ok(f"Port {port} OPEN"))
        else:
            print("   " + fail(f"Port {port} closed"))
    print()
    print(bold(f"Found {len(r['open'])} open port(s): {r['open']}"))


def render_traceroute(r):
    if not r.get("ok"):
        print(fail(r.get("error", "traceroute failed")))
        return
    print(r.get("raw", "").rstrip())


def render_firewall(r):
    if not r.get("ok"):
        print(fail(r.get("error", "firewall check failed")))
        return
    print(info(f"Target: {r['target']} ({r['ip']})"))
    for item in r["allowed"]:
        print("   " + ok(f"{item['port']} ({item['name']}) ALLOWED"))
    for item in r["blocked"]:
        print("   " + fail(f"{item['port']} ({item['name']}) BLOCKED"))
    print()
    print(bold(f"Allowed: {len(r['allowed'])}  Blocked: {len(r['blocked'])}"))


def render_loadbalancer(r):
    if not r.get("ok"):
        print(fail(r.get("error", "sim failed")))
        return
    print(info(f"Algorithm: {r['algorithm']}   Requests: {r['total']}"))
    print()
    for server, count in r["counts"].items():
        bar = "█" * count
        print(f"   {server}: {count:3d}  {paint(bar, C.GREEN)}")


def render_ids(r):
    if not r.get("ok"):
        print(fail(r.get("error", "IDS failed")))
        return
    for line in r["traffic"]:
        print(f"   {line}")
    if r["clean"]:
        print()
        print(ok("No threats detected"))
    else:
        print()
        for alert in r["alerts"]:
            print(fail(f"ALERT: Port scan from {alert['ip']}"))
            print(f"   Ports hit: {alert['ports']}")


def render_report(text):
    print()
    print(text)
