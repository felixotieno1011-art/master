# Mini Firewall — Simulates how a firewall decides to allow/block traffic

# Firewall rules (allow/deny based on source IP and port)
RULES = [
    {"action": "allow", "source": "any", "port": 80,   "reason": "Public HTTP"},
    {"action": "allow", "source": "any", "port": 443,  "reason": "Public HTTPS"},
    {"action": "allow", "source": "192.168.1.0/24", "port": 22,  "reason": "SSH only from local"},
    {"action": "deny",  "source": "any", "port": 22,   "reason": "SSH from internet"},
    {"action": "deny",  "source": "any", "port": 3306, "reason": "MySQL never exposed"},
    {"action": "deny",  "source": "any", "port": 8000, "reason": "Custom port blocked"},
]

def is_local(ip):
    return ip.startswith("192.168.1.")

def check_packet(src_ip, dst_port):
    """Simulates a firewall looking at a packet."""
    for rule in RULES:
        source_match = (
            rule["source"] == "any"
            or (rule["source"] == "192.168.1.0/24" and is_local(src_ip))
        )
        if source_match and rule["port"] == dst_port:
            return rule["action"], rule["reason"]
    return "deny", "No matching rule — default deny"

# Simulate incoming packets
test_packets = [
    ("8.8.8.8",           443, "Random internet user visiting my site"),
    ("192.168.1.50",      22,  "My laptop trying SSH"),
    ("203.0.113.99",      22,  "Hacker trying SSH from Russia"),
    ("192.168.1.60",      3306,"My phone trying database"),
    ("198.51.100.5",      80,  "Random user visiting HTTP page"),
    ("198.51.100.5",      8000,"Random user hitting my custom port"),
]

print("=" * 70)
print("MINI FIREWALL — Testing incoming packets")
print("=" * 70)

for src, port, description in test_packets:
    action, reason = check_packet(src, port)
    icon = "✅" if action == "allow" else "❌"
    print(f"\n{icon} {action.upper()}: {src} -> port {port}")
    print(f"   ({description})")
    print(f"   Reason: {reason}")
