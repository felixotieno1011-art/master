# ============================================
# MINI CLOUD NETWORK — Felix's version
# Simulates AWS + Azure with VPCs, subnets, routers, firewalls
# ============================================

# ---------- 1. Define our clouds ----------
clouds = {
    "AWS": {
        "region": "us-east-1",
        "vpc": "10.0.0.0/16",
        "subnets": {
            "public":  {"cidr": "10.0.1.0/24"},
            "private": {"cidr": "10.0.2.0/24"},
        },
        "firewall": [
            {"port": 80,   "action": "allow", "from": "any"},
            {"port": 443,  "action": "allow", "from": "any"},
            {"port": 22,   "action": "allow", "from": "local"},
            {"port": 3306, "action": "deny",  "from": "any"},
        ],
    },
    "Azure": {
        "region": "east-us",
        "vpc": "192.168.0.0/16",
        "subnets": {
            "public":  {"cidr": "192.168.1.0/24"},
            "private": {"cidr": "192.168.2.0/24"},
        },
        "firewall": [
            {"port": 80,   "action": "allow", "from": "any"},
            {"port": 443,  "action": "allow", "from": "any"},
            {"port": 22,   "action": "allow", "from": "local"},
            {"port": 3306, "action": "deny",  "from": "any"},
        ],
    },
}

# ---------- 2. Helper: is an IP inside a CIDR? ----------
def ip_in_cidr(ip, cidr):
    """Returns True if ip is inside the CIDR range."""
    net, bits = cidr.split("/")
    bits = int(bits)

    def to_int(x):
        parts = x.split(".")
        return (int(parts[0]) << 24) + (int(parts[1]) << 16) + (int(parts[2]) << 8) + int(parts[3])

    ip_int = to_int(ip)
    net_int = to_int(net)
    mask = (0xFFFFFFFF << (32 - bits)) & 0xFFFFFFFF

    return (ip_int & mask) == (net_int & mask)

# ---------- 3. Check firewall rules ----------
def check_firewall(cloud_name, source_ip, dest_port):
    """Returns (allowed: bool, reason: str)."""
    cloud = clouds[cloud_name]
    is_local = source_ip.startswith("10.") or source_ip.startswith("192.168.")

    for rule in cloud["firewall"]:
        if rule["port"] == dest_port:
            if rule["from"] == "any":
                return rule["action"] == "allow", f"Rule: port {dest_port} from anywhere"
            if rule["from"] == "local" and is_local:
                return rule["action"] == "allow", f"Rule: port {dest_port} from local network"

    return False, "No matching rule (default deny)"

# ---------- 4. Route traffic between clouds ----------
def route_traffic(source_ip, dest_cloud, dest_port):
    """Simulates traffic going through the virtual router."""
    print(f"\n🌐 Traffic: {source_ip} → {dest_cloud}:{dest_port}")

    # Find which cloud the source IP belongs to (if any)
    source_cloud = None
    for name, cloud in clouds.items():
        if ip_in_cidr(source_ip, cloud["vpc"]):
            source_cloud = name
            break

    if source_cloud:
        print(f"   Source detected in: {source_cloud}")
    else:
        print(f"   Source is EXTERNAL (from internet)")

    # Apply destination cloud's firewall
    allowed, reason = check_firewall(dest_cloud, source_ip, dest_port)
    icon = "✅" if allowed else "❌"
    print(f"   {icon} {reason}")

    return allowed

# ---------- 5. Display the network topology ----------
def show_topology():
    print("\n" + "=" * 60)
    print("☁️  MINI CLOUD NETWORK — Topology")
    print("=" * 60)
    for name, cloud in clouds.items():
        print(f"\n☁️  Cloud: {name}  ({cloud['region']})")
        print(f"    VPC: {cloud['vpc']}")
        for sub_name, sub in cloud["subnets"].items():
            print(f"      ├─ {sub_name:8} {sub['cidr']}")
        print(f"    Firewall rules:")
        for rule in cloud["firewall"]:
            print(f"      • Port {rule['port']:5} : {rule['action']:5} from {rule['from']}")

# ---------- 6. Test scenarios ----------
def run_tests():
    print("\n" + "=" * 60)
    print("🧪 TESTING TRAFFIC SCENARIOS")
    print("=" * 60)

    tests = [
        # (source_ip, destination_cloud, destination_port, description)
        ("8.8.8.8",         "AWS",   443,  "Random user visiting AWS HTTPS"),
        ("10.0.1.50",       "AWS",   22,   "AWS server SSH-ing another AWS server"),
        ("203.0.113.99",    "AWS",   22,   "Hacker trying SSH from internet"),
        ("192.168.1.10",    "Azure", 3306, "Azure app trying Azure database (blocked by firewall)"),
        ("10.0.1.5",        "Azure", 443,  "AWS user visiting Azure HTTPS (cross-cloud!)"),
        ("198.51.100.5",    "Azure", 80,   "Random user hitting Azure HTTP"),
        ("10.0.2.77",       "AWS",   8000, "AWS private server hitting custom port"),
    ]

    allowed_count = 0
    denied_count = 0

    for src, cloud, port, desc in tests:
        print(f"\n📝 Scenario: {desc}")
        allowed = route_traffic(src, cloud, port)
        if allowed:
            allowed_count += 1
        else:
            denied_count += 1

    print("\n" + "=" * 60)
    print(f"📊 SUMMARY: {allowed_count} allowed, {denied_count} denied")
    print("=" * 60)

# ---------- 7. Main ----------
if __name__ == "__main__":
    print("🚀 Starting Mini Cloud Network...")
    show_topology()
    run_tests()
