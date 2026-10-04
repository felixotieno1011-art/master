#!/usr/bin/env python3
# ============================================
# mini_load_balancer.py — Simulates load balancing
# with 4 algorithms + health checks
# ============================================

import time
import random

# ---- Define our "servers" ----
SERVERS = [
    {"name": "Server-1", "weight": 1, "healthy": True,  "connections": 0},
    {"name": "Server-2", "weight": 2, "healthy": True,  "connections": 0},
    {"name": "Server-3", "weight": 1, "healthy": True,  "connections": 0},
]

# ---- Track Round Robin state ----
rr_index = 0

# =====================================================
# Algorithm 1 — Round Robin
# =====================================================
def round_robin():
    global rr_index
    healthy = [s for s in SERVERS if s["healthy"]]
    if not healthy:
        return None
    server = healthy[rr_index % len(healthy)]
    rr_index += 1
    return server

# =====================================================
# Algorithm 2 — Least Connections
# =====================================================
def least_connections():
    healthy = [s for s in SERVERS if s["healthy"]]
    if not healthy:
        return None
    return min(healthy, key=lambda s: s["connections"])

# =====================================================
# Algorithm 3 — IP Hash (consistent based on client IP)
# =====================================================
def ip_hash(client_ip):
    healthy = [s for s in SERVERS if s["healthy"]]
    if not healthy:
        return None
    index = hash(client_ip) % len(healthy)
    return healthy[index]

# =====================================================
# Algorithm 4 — Weighted Round Robin
# =====================================================
def weighted_round_robin():
    healthy = [s for s in SERVERS if s["healthy"]]
    if not healthy:
        return None
    # Expand list based on weights
    pool = []
    for s in healthy:
        pool.extend([s] * s["weight"])
    return random.choice(pool)

# =====================================================
# Health Check (simulated)
# =====================================================
def health_check():
    """Randomly kill/revive servers to simulate outages."""
    for s in SERVERS:
        if s["healthy"] and random.random() < 0.05:  # 5% chance of going down
            s["healthy"] = False
            print(f"   ⚠  {s['name']} became UNHEALTHY")
        elif not s["healthy"] and random.random() < 0.3:  # 30% chance of reviving
            s["healthy"] = True
            print(f"   ✅ {s['name']} recovered")

# =====================================================
# Send a request using chosen algorithm
# =====================================================
def send_request(algorithm, client_id):
    if algorithm == "round_robin":
        server = round_robin()
    elif algorithm == "least_connections":
        server = least_connections()
    elif algorithm == "ip_hash":
        server = ip_hash(client_id)
    elif algorithm == "weighted":
        server = weighted_round_robin()
    else:
        server = round_robin()

    if server is None:
        print(f"   ❌ No healthy server for request from {client_id}")
        return

    server["connections"] += 1
    print(f"   [{algorithm:18s}] {client_id} → {server['name']}")
    # Simulate the connection finishing quickly
    server["connections"] -= 1

# =====================================================
# Run tests
# =====================================================
def test_algorithm(algorithm, count=6):
    print(f"\n{'=' * 60}")
    print(f"🎯 Algorithm: {algorithm.upper()}")
    print(f"{'=' * 60}")
    for i in range(1, count + 1):
        client_id = f"user-{i}"
        send_request(algorithm, client_id)

def main():
    print("=" * 60)
    print("🚦 MINI LOAD BALANCER — Simulation")
    print("=" * 60)
    print(f"\nRegistered servers:")
    for s in SERVERS:
        print(f"   • {s['name']}  (weight={s['weight']})")

    # Test each algorithm
    test_algorithm("round_robin", 6)
    test_algorithm("least_connections", 6)
    test_algorithm("ip_hash", 6)
    test_algorithm("weighted", 12)

    # Simulate a server dying
    print(f"\n{'=' * 60}")
    print("💀 Simulating Server-2 going DOWN")
    print(f"{'=' * 60}")
    SERVERS[1]["healthy"] = False

    test_algorithm("round_robin", 6)

    # Server revives
    print(f"\n{'=' * 60}")
    print("✅ Server-2 RECOVERED")
    print(f"{'=' * 60}")
    SERVERS[1]["healthy"] = True

    test_algorithm("round_robin", 3)

if __name__ == "__main__":
    main()
