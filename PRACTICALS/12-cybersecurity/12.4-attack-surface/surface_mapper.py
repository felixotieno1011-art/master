# ============================================
# Attack Surface Mapper
# Maps potential entry points of a target
# ============================================

import socket

# ---- Common ports and their services ----
COMMON_PORTS = {
    21: "FTP",
    22: "SSH",
    23: "Telnet",
    25: "SMTP",
    53: "DNS",
    80: "HTTP",
    110: "POP3",
    143: "IMAP",
    443: "HTTPS",
    3306: "MySQL",
    3389: "RDP",
    5432: "PostgreSQL",
    5900: "VNC",
    8080: "HTTP-Alt"
}

# ---- Known risk levels per service ----
RISK_LEVELS = {
    "FTP": "High (unencrypted, plaintext passwords)",
    "SSH": "Medium (encrypted but often brute-forced)",
    "Telnet": "Critical (unencrypted, ancient)",
    "SMTP": "Medium (often abused for spam)",
    "DNS": "Medium (amplification attacks)",
    "HTTP": "Medium (unencrypted)",
    "POP3": "High (often unencrypted)",
    "IMAP": "Medium (often unencrypted)",
    "HTTPS": "Low (encrypted properly)",
    "MySQL": "Critical (should NEVER be public)",
    "RDP": "Critical (common target for ransomware)",
    "PostgreSQL": "Critical (should NEVER be public)",
    "VNC": "High (often weak passwords)",
    "HTTP-Alt": "Medium (unencrypted)"
}

# ---- Scan a target ----
def scan_port(target, port, timeout=1):
    """Check if a port is open."""
    try:
        s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        s.settimeout(timeout)
        result = s.connect_ex((target, port))
        s.close()
        return result == 0
    except Exception:
        return False

def map_surface(target):
    print(f"\n🔍 MAPPING ATTACK SURFACE: {target}")
    print("=" * 60)

    open_ports = []
    total_checked = len(COMMON_PORTS)

    for port, service in COMMON_PORTS.items():
        if scan_port(target, port):
            risk = RISK_LEVELS.get(service, "Unknown")
            print(f"  ✅ Port {port:5} ({service:10}) → {risk}")
            open_ports.append((port, service, risk))
        else:
            # Only print closed ports if verbose; skip to reduce clutter
            pass

    print("\n" + "=" * 60)
    print(f"📊 ATTACK SURFACE REPORT")
    print("=" * 60)
    print(f"   Target:       {target}")
    print(f"   Ports checked: {total_checked}")
    print(f"   Open ports:   {len(open_ports)}")
    print()

    if not open_ports:
        print("   ✅ No open ports found (from common list)")
        print("   Attack surface: MINIMAL")
        return

    print("   🎯 EXPOSED SERVICES:")
    for port, service, risk in open_ports:
        print(f"      • Port {port} ({service}) — {risk}")

    # Classify attack surface size
    if len(open_ports) <= 2:
        size = "SMALL"
        advice = "Good. Keep it minimal."
    elif len(open_ports) <= 5:
        size = "MEDIUM"
        advice = "Review: are all these needed?"
    else:
        size = "LARGE"
        advice = "⚠️  Reduce! Close unused services."

    print(f"\n   📏 Surface size: {size}")
    print(f"   💡 Advice: {advice}")

    # Highlight critical services
    critical = [(p, s) for p, s, r in open_ports if "Critical" in r]
    if critical:
        print(f"\n   🚨 CRITICAL EXPOSURES:")
        for port, service in critical:
            print(f"      • Port {port} ({service}) — CLOSE THIS NOW")

# ---- Educational reference ----
def show_reference():
    print("\n📚 ATTACK SURFACE — REFERENCE")
    print("=" * 60)
    print("\n🎯 What is attack surface?")
    print("   The total sum of all ways an attacker could try to break in.")

    print("\n📊 4 types of attack surface:")
    print("   1. Network  - open ports, services")
    print("   2. Software - code, libraries, OS")
    print("   3. Human    - employees, users")
    print("   4. Physical - devices, buildings")

    print("\n🔑 Attack surface vs vector:")
    print("   Surface = all ways in")
    print("   Vector  = the way actually used")

    print("\n💡 How to reduce attack surface:")
    print("   • Close unused ports")
    print("   • Remove unused software")
    print("   • Disable unused accounts")
    print("   • Patch regularly")
    print("   • Use firewalls")
    print("   • Train employees")

# ---- Main menu ----
def main():
    while True:
        print("\n" + "=" * 60)
        print("🎯 ATTACK SURFACE MAPPER")
        print("=" * 60)
        print("1. Map a target")
        print("2. Attack surface reference")
        print("3. Exit")
        print("=" * 60)

        choice = input("\nChoose (1-3): ").strip()

        if choice == "1":
            target = input("Target (IP or hostname): ").strip()
            if not target:
                print("❌ No target.")
                continue
            try:
                ip = socket.gethostbyname(target)
                map_surface(ip)
            except Exception as e:
                print(f"❌ Cannot resolve {target}: {e}")
        elif choice == "2":
            show_reference()
        elif choice == "3":
            print("\n👋 Goodbye!")
            break
        else:
            print("❌ Invalid choice.")

if __name__ == "__main__":
    main()
