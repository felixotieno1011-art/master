# ============================================
# NETKIT — ui/web/routes.py
# Maps tool name → tool function. Single source of truth.
# ============================================

from tools import (
    ping, dns, portscan, traceroute,
    firewall, loadbalancer, ids,
)


def list_tools():
    """Metadata for the dashboard cards."""
    return [
        {"id": "ping",         "label": "Ping Test",           "desc": "Check host reachability"},
        {"id": "dns",          "label": "DNS Lookup",          "desc": "Resolve domain to IP"},
        {"id": "portscan",     "label": "Port Scan",           "desc": "Probe common TCP ports"},
        {"id": "traceroute",   "label": "Traceroute",          "desc": "Trace route to target"},
        {"id": "firewall",     "label": "Firewall Check",      "desc": "Test firewall rules"},
        {"id": "loadbalancer", "label": "Load Balancer Sim",   "desc": "Simulate LB algorithms"},
        {"id": "ids",          "label": "IDS Detect",          "desc": "Detect port scans"},
    ]


def run_tool(name, payload):
    """Dispatch to the right tool. Payload comes from JSON body."""
    try:
        if name == "ping":
            return ping.ping_test(payload.get("target", "").strip())

        if name == "dns":
            return dns.dns_lookup(payload.get("domain", "").strip())

        if name == "portscan":
            ports = payload.get("ports")
            return portscan.port_scan(payload.get("target", "").strip(), ports)

        if name == "traceroute":
            return traceroute.traceroute_test(payload.get("target", "").strip())

        if name == "firewall":
            return firewall.firewall_check(payload.get("target", "").strip())

        if name == "loadbalancer":
            n = payload.get("count", 12)
            algo = payload.get("algorithm", "roundrobin")
            return loadbalancer.load_balancer_sim(n, algo)

        if name == "ids":
            return ids.ids_detect()

        return {"ok": False, "error": f"Unknown tool: {name}"}

    except Exception as e:
        return {"ok": False, "error": f"{type(e).__name__}: {e}"}
