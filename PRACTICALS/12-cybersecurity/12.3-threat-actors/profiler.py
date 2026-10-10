# ============================================
# Threat Actor Profiler
# Classify attackers based on clues
# ============================================

# ---- Actor database ----
actors = {
    "script_kiddie": {
        "name": "Script Kiddie",
        "motivation": "Fun / curiosity",
        "skill": "Low",
        "resources": "Low",
        "typical_targets": "Random, easy targets",
        "threat_level": 1,
        "indicators": ["uses known tools", "attacks randomly", "seeks attention"]
    },
    "cybercriminal": {
        "name": "Cybercriminal",
        "motivation": "Money",
        "skill": "Medium-High",
        "resources": "High",
        "typical_targets": "Banks, hospitals, individuals with money",
        "threat_level": 4,
        "indicators": ["ransomware", "financial fraud", "organized", "patient"]
    },
    "hacktivist": {
        "name": "Hacktivist",
        "motivation": "Political / social",
        "skill": "Medium-High",
        "resources": "Medium",
        "typical_targets": "Governments, corporations",
        "threat_level": 2,
        "indicators": ["public defacement", "DDoS", "claims responsibility", "leaks data"]
    },
    "nation_state": {
        "name": "Nation-State (APT)",
        "motivation": "Espionage / sabotage",
        "skill": "Elite",
        "resources": "Unlimited",
        "typical_targets": "Governments, critical infrastructure",
        "threat_level": 5,
        "indicators": ["zero-day exploits", "years-long persistence", "custom malware", "no public claims"]
    },
    "insider": {
        "name": "Insider Threat",
        "motivation": "Revenge / money / ideology",
        "skill": "Varies",
        "resources": "Has access already",
        "typical_targets": "Own employer",
        "threat_level": 4,
        "indicators": ["misuses credentials", "unusual access patterns", "data exfiltration"]
    },
    "competitor": {
        "name": "Competitor (Corporate Espionage)",
        "motivation": "Business advantage",
        "skill": "Medium",
        "resources": "Company budget",
        "typical_targets": "Rival companies",
        "threat_level": 3,
        "indicators": ["steals IP", "targets specific data", "legal cover"]
    }
}

# ---- Helper functions ----
def show_all_actors():
    print("\n" + "=" * 60)
    print("🎭 THREAT ACTORS — All Known Types")
    print("=" * 60)
    for key, actor in actors.items():
        print(f"\n📌 {actor['name']}")
        print(f"   Motivation:      {actor['motivation']}")
        print(f"   Skill level:     {actor['skill']}")
        print(f"   Resources:       {actor['resources']}")
        print(f"   Typical targets: {actor['typical_targets']}")
        print(f"   Threat level:    {'⭐' * actor['threat_level']}")

def match_indicators():
    """Ask user for clues, find matching actor."""
    print("\n🔍 THREAT ACTOR PROFILER")
    print("I'll ask you questions. Answer y/n.\n")

    scoreboard = {key: 0 for key in actors.keys()}

    questions = [
        ("Are they using publicly available tools (nmap, metasploit, etc.)?",
         ["script_kiddie"]),
        ("Do they demand money in exchange for unlocking data?",
         ["cybercriminal"]),
        ("Have they made a public statement or political claim?",
         ["hacktivist"]),
        ("Are they extremely patient — attacking for weeks/months/years?",
         ["nation_state"]),
        ("Do they already have legitimate access to the systems?",
         ["insider"]),
        ("Are they stealing specific business data (not just anything)?",
         ["competitor"]),
        ("Have they used a brand-new exploit nobody knows about?",
         ["nation_state"]),
        ("Did they attack random, low-value targets?",
         ["script_kiddie"]),
        ("Do they cause destruction or data leaks publicly?",
         ["hacktivist"]),
        ("Have they targeted employees with unusual trust?",
         ["insider", "cybercriminal"]),
    ]

    for i, (question, matches) in enumerate(questions, 1):
        answer = input(f"{i}. {question} (y/n): ").strip().lower()
        if answer == "y":
            for m in matches:
                scoreboard[m] += 1

    # Find the highest score
    print("\n" + "=" * 60)
    print("🎯 MOST LIKELY THREAT ACTOR")
    print("=" * 60)

    sorted_scores = sorted(scoreboard.items(), key=lambda x: -x[1])
    top_key, top_score = sorted_scores[0]

    if top_score == 0:
        print("⚠️  Not enough indicators given.")
        return

    top_actor = actors[top_key]
    print(f"\n📌 {top_actor['name']}")
    print(f"   Confidence: {top_score}/{len(questions)} indicators matched")
    print(f"\n   Motivation:      {top_actor['motivation']}")
    print(f"   Skill level:     {top_actor['skill']}")
    print(f"   Threat level:    {'⭐' * top_actor['threat_level']}")
    print(f"   Typical targets: {top_actor['typical_targets']}")

    # Show runner-ups
    print("\n   Other possibilities:")
    for key, score in sorted_scores[1:3]:
        if score > 0:
            print(f"   • {actors[key]['name']} ({score} matches)")

# ---- Main menu ----
def main():
    while True:
        print("\n" + "=" * 60)
        print("🎭 THREAT ACTOR PROFILER")
        print("=" * 60)
        print("1. Show all threat actors")
        print("2. Profile a threat (answer questions)")
        print("3. Exit")
        print("=" * 60)

        choice = input("\nChoose (1-3): ").strip()

        if choice == "1":
            show_all_actors()
        elif choice == "2":
            match_indicators()
        elif choice == "3":
            print("\n👋 Goodbye!")
            break
        else:
            print("❌ Invalid choice.")

if __name__ == "__main__":
    main()
