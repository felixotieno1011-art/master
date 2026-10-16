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
## 12.5 Security Mindset

### What it is
Habitually thinking about how systems can be broken.
Not "how does this work?" but "how can this break?"

### Two mindsets
- Normal: "Does it work?"
- Security: "Does it work ONLY as intended?"

### 6 principles
1. Think like an attacker
2. Trust nothing, verify everything
3. Assume breach
4. Defense in depth
5. Principle of least privilege
6. Fail securely

### Attacker's 5 questions
1. How would I break in?
2. What would I steal?
3. What would I change?
4. What would I destroy?
5. What would I hide?

### Weird things radar (signs of attack)
- Logins at odd hours
- Many failed attempts
- Large data transfers at midnight
- Port scans on your server

### Layers of attack
Data → Access control → Login → Network → Server → Physical → Human
Attackers attack the weakest layer.

### My own words
- Security mindset = thinking like a thief
- Don't assume, test/verify
- Always notice possible entry points
- Cyber café analysis:
  * Attack surface = network + 11 PCs + physical
  * Highest value = admin PC (customer data)
  * Weakest layer = untrained guard

### Real quote
"Security is a process, not a product." — Bruce Schneier
### 12.18 Social Engineering — Phase B DONE ✅

Analyzed a fake Safaricom/M-Pesa SMS. Identified attack type,
emotion, red flags, and safe version.

### Core concepts
- Social Engineering = hacking the HUMAN, not the machine
- Types: phishing, spear phishing, vishing, smishing, pretexting,
  baiting, tailgating, quid pro quo
- Attackers exploit: urgency, fear, authority, helpfulness, greed
- Defense: slow down, verify, never share PIN/password

### Real analysis I did
- Fake Safaricom SMS asking for PIN via *106*123#
- Caught: fear + urgency, fake USSD, PIN request, fake number

### My own words (locked in)
- Safaricom never hurries someone — urgency is a scam tell
- The target isn't the system — it's the person with the keys
- No real company asks for your PIN or password, ever
- Fear + urgency = the classic one-two punch
## 12.6 Cryptography Basics — Phase B DONE ✅

Ran MD5 cracker against pos-lab DB. Cracked 3 passwords.
Flipped to scrypt. Same cracker → 0 cracks.

### Core concepts
- Cryptography = securing info so only intended readers can access
- Plaintext  = readable message
- Ciphertext = scrambled version
- Key        = the secret that locks/unlocks
- Encrypt    = plaintext → ciphertext
- Decrypt    = ciphertext → plaintext
- Symmetric  = one key (fast, hard to share)
- Asymmetric = two keys, public + private (slow, solves sharing)

### Encryption vs Hashing
- Encryption = REVERSIBLE (with the key)
- Hashing    = ONE-WAY (cannot reverse)
- Encryption = for sending secrets
- Hashing    = for storing passwords / verifying integrity

### Real commands I ran
- node tests/crack-md5.js --all      → cracked 3 passwords in 10 ms
- sed -i 's/SECURE_MODE=.*/SECURE_MODE=true/' .env
- node db/init.js                     → rebuilt DB with scrypt
- node tests/crack-md5.js --all      → 0 cracks

### Things I saw
- MD5 mode: boss123, manager123, seller123 all CRACKED in <10 ms each
- scrypt mode: all three "not applicable" — dictionary attack fails
- Only change: SECURE_MODE=true in .env, then rebuild DB
- Hashing code in db/init.js: hashMd5() vs hashScrypt()
- scrypt adds randomBytes(16) salt → unique hash per user

### The four-line proof
1. Cracked 3 passwords from MD5
2. Flipped SECURE_MODE=true
3. Rebuilt DB with scrypt
4. Same cracker → 0 cracks

### My own words (locked in)
- Encryption = 2-way (encrypt + decrypt with key)
- Hashing = 1-way (cannot reverse)
- scrypt is SLOW ON PURPOSE — every guess costs ~100 ms
- MD5 is FAST — great for checksums, terrible for passwords
- Salt = random data added before hashing
  → same password produces different hashes each time
  → kills rainbow tables and cross-user comparisons
- The algorithm IS the security. Not the code around it. Just the math.
- You can flip a whole app from vulnerable to secure by changing
  how ONE function works.
## 12.6 Cryptography Basics — Phase B DONE ✅

Cracked MD5 hashes with pos-lab's cracker. Flipped to scrypt. Same
cracker → 0 cracks.

### Core concepts
- Cryptography = securing info so only intended readers can access
- Plaintext  = readable message
- Ciphertext = scrambled version
- Key        = the secret that locks/unlocks
- Encrypt    = plaintext → ciphertext
- Decrypt    = ciphertext → plaintext
- Symmetric  = one key (fast, hard to share)
- Asymmetric = two keys, public + private (slow, solves sharing)

### Encryption vs Hashing
- Encryption = REVERSIBLE (with key) — for sending secrets
- Hashing    = ONE-WAY (cannot reverse) — for storing passwords
- Cracking ≠ reversing. Cracking = guessing + verifying.
- John the Ripper guesses passwords, hashes each, compares to target.
- Target hash is fixed. Guesses change. Match = crack.

### Salts explained
- Without salt (MD5): same password → same hash for all users
  → crack once → unlock thousands
- With salt (scrypt): each user gets unique random salt
  → same password → different hash per user
  → John must crack each individually
  → rainbow tables useless
- The salt is stored IN the hash (not secret)
- John reads the salt from the target, uses it for each guess
- Salt's job: make each hash unique + defeat precomputed tables

### Real commands I ran
- node tests/crack-md5.js --all  → cracked 3 passwords in 10 ms
- sed -i 's/SECURE_MODE=.*/SECURE_MODE=true/' .env
- node db/init.js                 → rebuild DB with scrypt
- node tests/crack-md5.js --all  → 0 cracks

### Things I saw
- MD5 mode: boss123, manager123, seller123 all CRACKED in <10 ms
- scrypt mode: all three "not applicable" — dictionary attack fails
- Hashing code in db/init.js:
    hashMd5() uses createHash('md5'), no salt
    hashScrypt() uses randomBytes(16) salt + scryptSync
    hashPassword() dispatches: isSecure() ? scrypt : md5
- Only change needed: SECURE_MODE=true + rebuild DB

### My own words (locked in)
- Encryption = 2-way. Hashing = 1-way.
- Crack = guess + hash + compare. Never "reverse the hash."
- John the Ripper doesn't unhash. It guesses passwords, hashes them,
  compares to the target. Match = found.
- Cracking works because humans choose predictable passwords
  (words, names, patterns, dates). Random passwords don't get cracked.
- Salt = random data added before hashing → same password produces
  different hashes per user → kills rainbow tables → forces individual cracking
- scrypt is slow on purpose (~100 ms per guess). That's the whole point.
- MD5 is fast — great for checksums, terrible for passwords
- The algorithm IS the security. Code around it doesn't matter.
- Nothing is "unhackable." Everything is "expensive enough."
- "John is dangerous" = it's OFFLINE (silent, no detection, no rate limit).
  Hydra is ONLINE (loud, logged, blocked).
