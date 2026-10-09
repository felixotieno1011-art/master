# ============================================
# CIA Analyzer — Classify attacks by CIA pillar
# ============================================

# ---- Attack database ----
attacks = {
    "phishing": {
        "description": "Tricking users into giving credentials",
        "pillars": ["Confidentiality"],
        "example": "Fake login page steals passwords"
    },
    "ransomware": {
        "description": "Malware that encrypts your files for payment",
        "pillars": ["Integrity", "Availability"],
        "example": "Files locked until you pay"
    },
    "ddos": {
        "description": "Flooding a server to make it unavailable",
        "pillars": ["Availability"],
        "example": "Website down from fake traffic"
    },
    "sql_injection": {
        "description": "Injecting SQL into user inputs to manipulate DB",
        "pillars": ["Confidentiality", "Integrity"],
        "example": "Stealing or modifying database records"
    },
    "man_in_the_middle": {
        "description": "Intercepting traffic between two parties",
        "pillars": ["Confidentiality", "Integrity"],
        "example": "Reading or altering network traffic"
    },
    "insider_threat": {
        "description": "Employee misusing their access",
        "pillars": ["Confidentiality", "Integrity"],
        "example": "Employee copying customer data"
    },
    "physical_theft": {
        "description": "Stealing a device with data on it",
        "pillars": ["Confidentiality", "Availability"],
        "example": "Stolen laptop with unencrypted files"
    }
}

# ---- Classify a pillar ----
def get_attacks_by_pillar(pillar):
    """Return all attacks affecting a given pillar."""
    matching = []
    for name, info in attacks.items():
        if pillar in info["pillars"]:
            matching.append(name)
    return matching

# ---- Show all attacks ----
def show_all_attacks():
    print("\n🛡️  ALL KNOWN ATTACKS")
    print("=" * 60)
    for i, (name, info) in enumerate(attacks.items(), 1):
        pillars_str = " + ".join(info["pillars"])
        print(f"\n{i}. {name.upper()}")
        print(f"   Description: {info['description']}")
        print(f"   Affects:     {pillars_str}")
        print(f"   Example:     {info['example']}")

# ---- Filter by pillar ----
def filter_by_pillar():
    print("\n🔍 FILTER BY PILLAR")
    print("Options: Confidentiality, Integrity, Availability")
    pillar = input("Enter pillar: ").strip().capitalize()

    if pillar not in ["Confidentiality", "Integrity", "Availability"]:
        print("❌ Invalid pillar.")
        return

    matching = get_attacks_by_pillar(pillar)
    print(f"\n📊 Attacks affecting {pillar}: {len(matching)}")
    for name in matching:
        print(f"   • {name}")

# ---- Add custom attack ----
def add_attack():
    print("\n➕ ADD CUSTOM ATTACK")
    name = input("Attack name: ").strip().lower().replace(" ", "_")
    desc = input("Description: ").strip()
    pillars_input = input("Pillars (comma-separated): ").strip()
    pillars = [p.strip().capitalize() for p in pillars_input.split(",")]

    attacks[name] = {
        "description": desc,
        "pillars": pillars,
        "example": "User added"
    }
    print(f"✅ Added '{name}' affecting {pillars}")

# ---- Main menu ----
def main():
    while True:
        print("\n" + "=" * 60)
        print("🛡️  CIA ANALYZER")
        print("=" * 60)
        print("1. Show all attacks")
        print("2. Filter by pillar")
        print("3. Add custom attack")
        print("4. Exit")
        print("=" * 60)

        choice = input("\nChoose (1-4): ").strip()

        if choice == "1":
            show_all_attacks()
        elif choice == "2":
            filter_by_pillar()
        elif choice == "3":
            add_attack()
        elif choice == "4":
            print("\n👋 Goodbye!")
            break
        else:
            print("❌ Invalid choice.")

if __name__ == "__main__":
    main()

