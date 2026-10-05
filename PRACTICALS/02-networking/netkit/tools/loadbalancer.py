# ============================================
# NETKIT — tools/loadbalancer.py
# ============================================

import hashlib
from core import logger


def load_balancer_sim(num_requests, algorithm="roundrobin"):
    try:
        num_requests = int(num_requests)
    except (ValueError, TypeError):
        return {"ok": False, "error": "Invalid number"}

    servers = ["Server-1", "Server-2", "Server-3"]
    counts = {s: 0 for s in servers}
    connections = {s: 0 for s in servers}
    assignments = []

    for i in range(num_requests):
        if algorithm == "leastconn":
            server = min(servers, key=lambda s: connections[s])
            connections[server] += 1
        elif algorithm == "iphash":
            client_ip = f"10.0.0.{(i % 254) + 1}"
            h = int(hashlib.md5(client_ip.encode()).hexdigest(), 16)
            server = servers[h % len(servers)]
        else:
            server = servers[i % len(servers)]

        counts[server] += 1
        assignments.append({"request": i + 1, "server": server})

    result = {
        "ok": True,
        "algorithm": algorithm,
        "total": num_requests,
        "counts": counts,
        "assignments": assignments,
    }

    logger.get_report().log(
        "LB-SIM",
        f"{num_requests} requests via {algorithm} — {counts}",
        result,
    )
    return result
