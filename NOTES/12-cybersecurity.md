,# 🔐 PART 12 — CYBERSECURITY & ETHICAL HACKING

Notes for Phase 2 — started 2026-10-09

====================================================
Module 1 — Security Foundations
====================================================

## 12.1 What is Cybersecurity?

- Cybersecurity = protecting computers, networks, and data from attacks
- 3 parts: Protect, Detect, Respond
- CIA Triad (the foundation):
  * Confidentiality — only authorized users can access data
  * Integrity — data stays accurate and unmodified
  * Availability — data accessible when needed
- Threat actors: script kiddies, cybercriminals, hacktivists, nation-states, insiders, competitors

## 12.2 CIA Triad (deep dive)

- Confidentiality = keeps data secret (encryption, access control)
- Integrity = keeps data correct (hashing, signatures)
- Availability = keeps data accessible (backups, redundancy)
- Real attacks mapped:
  * Phishing → Confidentiality
  * Ransomware → Integrity + Availability
  * DDoS → Availability
  * SQL Injection → Confidentiality + Integrity
  * MITM → Confidentiality + Integrity
  * Insider theft → Confidentiality
  * Disk failure → Availability
- Built: cia_analyzer.py (classifies attacks by CIA pillar)

## 12.3 Threat Actors & Attack Types

### 6 Threat Actors
1. Script Kiddie  - Fun, low skill, random targets
2. Cybercriminal  - Money, organized, high threat (⭐⭐⭐⭐)
3. Hacktivist     - Ideology, medium threat (⭐⭐)
4. Nation-State   - Espionage, elite, max threat (⭐⭐⭐⭐⭐)
5. Insider        - Revenge/money, hardest to detect
6. Competitor     - Business advantage

### 5 Attack Vectors
1. Phishing          - tricking humans
2. Malware           - malicious software
3. Social Engineering - psychological manipulation
4. Exploits          - attacking vulnerabilities
5. Physical          - direct access

### Key terms
- Threat Actor = WHO attacks
- Attack Vector = HOW they attack
- APT = Advanced Persistent Threat

### Real examples
- Lazarus Group (North Korea) - 15+ years, $3B stolen
- LockBit - major ransomware gang
- Anonymous - hacktivist collective

### My own words
- Threat actor = who performs hack
- Attack vector = what they use to attack
- Nation-states have highest sophistication
- Insiders hardest to detect (legitimate access)
- Attribution is HARD (false flags exist)

### Built: profiler.py
Classifies attackers based on clues/indicators.
## 12.4 Attack Surface & Vectors

### Attack Surface
- Total sum of all ways an attacker could break in
- Bigger surface = more opportunities to attack
- 4 types:
  * Network  - open ports, exposed services
  * Software - code, libraries, OS
  * Human    - employees, users
  * Physical - devices, buildings

### Attack Surface vs Attack Vector
- Surface = ALL possible ways in
- Vector  = the ONE way actually used

### How to reduce attack surface
- Close unused ports
- Remove unused software
- Disable unused accounts
- Patch regularly
- Use firewalls
- Train employees

### Golden rule
"If you don't need it, turn it off."

### Why smaller is safer
Fewer ways in = easier to defend. Attackers need only ONE gap.

### Built: surface_mapper.py
Scans a target for open ports, classifies risk level.
Special host for practice: scanme.nmap.org
