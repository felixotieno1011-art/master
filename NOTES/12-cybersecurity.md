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
## 12.7 Symmetric vs Asymmetric Encryption — Phase B DONE ✅

Cracked an HS256 JWT secret. Tested forged alg:none tokens.
Verified RS256 can't be cracked with a wordlist.

### Core concepts
- Symmetric   = 1 shared key (fast, key sharing hard)
  Example: HS256 with 'secret', AES
- Asymmetric  = 2 keys (public + private)
  Example: RS256 with RSA keypair
  Public key = shareable, verifies
  Private key = secret, signs
- HS256 signs AND verifies with the same secret
  → every verifier can also forge
  → breaks down when multiple services verify
- RS256 signs with private, verifies with public
  → verification does not leak forging power
  → safe even if the public key is published

### Attacks demonstrated on pos-lab
1. AUTH-06: alg:none — attacker sends a JWT with alg:none
   → server accepts it → forged token
   → (vuln mode only)
2. AUTH-02: HS256 weak secret
   → 'secret' cracked in 9.51 ms → forge any token
3. Secure (RS256) — same cracker → ❌ not found

### Real commands I ran
- curl POST /api/auth/login → extract pos_token from Set-Cookie
- node tests/crack-jwt.js "<jwt>" → crack the HS256 secret
- echo -n '{"alg":"none"...}' | base64 → forge alg:none token
- curl -b "pos_token=$FORGED" /api/auth/me → hit API as boss

### Things I saw
- Vuln HS256 token: {"alg":"HS256"} → secret 'secret' cracked in 9.51 ms
- Secure RS256 token: {"alg":"RS256"} → ❌ not found in 19 candidates
- Forged alg:none token → server accepted it → became boss
  (in vuln mode; blocked in secure mode)
- pos-lab switches between HS256 and RS256 by SECURE_MODE

### My own words (locked in)
- HS256 = one shared secret → works for one server, breaks for many
- RS256 = private key signs, public key verifies → forgery requires
  the private key, which never leaves the server
- Modern crypto uses BOTH: asymmetric exchanges a key,
  symmetric encrypts the bulk
- A weak secret breaks even a strong algorithm
- JWT algorithm must be enforced by the server, not read from the token
  (that's the alg-confusion bug, AUTH-03)
- "Verify" without forgery power is the whole point of asymmetric crypto
## 12.8 Hashing (MD5, SHA, bcrypt) — Phase B DONE ✅

Compared MD5 vs scrypt in pos-lab. Cracked MD5 in 12 ms.
Cracker failed on scrypt.

### Core concepts
- Hashing = one-way function. Input → fixed-size fingerprint.
- Properties:
  - Deterministic: same input → same hash
  - One-way: cannot reverse
  - Avalanche: 1 byte change → totally different hash
  - Fixed size: output is always the same length

### Hash algorithms
- MD5 (128 bits)  — BROKEN. Fast. Do not use for passwords.
- SHA-1 (160 bits) — BROKEN (2017, "SHAttered").
- SHA-256 (256 bits) — Secure for checksums. Fast.
- SHA-512 (512 bits) — Same, larger output.
- bcrypt — Slow by design. Good for passwords.
- scrypt — Slow + memory-hard. Better.
- argon2 — Best (2026 standard).

### Two uses, different algorithms
1. Integrity checksums (did the file change?)
   - Fast hash OK: MD5, SHA-256
   - Public info, no secret
2. Password storage (verify without storing)
   - Must be SLOW: scrypt, bcrypt, argon2
   - Secret — never share
   - Fast hash = fatal (attackers try billions/sec)

### Anatomy of a scrypt hash
  scrypt$9bd82df4cb4a5cfc77acbb2872ec0f79$c01caaf63d4dea25...
         └────────── salt ──────────┘ └────── hash ──────┘
  Three parts: prefix (algorithm) + salt + hash

### Real commands I ran
- echo -n "hello" | md5sum
- echo -n "hello" | sha256sum
- echo -n "hello" | sha512sum
- node tests/crack-md5.js --all
- sed -i 's/SECURE_MODE=.../' .env
- node db/init.js
- sqlite3 db/pos.db "SELECT username, password_hash FROM users"

### Things I saw
- md5("hello") twice → identical (5d41402abc4b2a76b9719d911017c592)
- md5("hellO")    → completely different (06612c0d9c73d47a7042afd7024d7c82)
- Output lengths: MD5=32, SHA-256=64, SHA-512=128 hex chars
- VULN mode (MD5): 3 passwords cracked in 12 ms total
- SECURE mode (scrypt): 0 cracked, dictionary attack "not applicable"
- MD5 hash format: md5$<32hex>
- scrypt hash format: scrypt$<salt32hex>$<hash128hex>
- Three users in same DB → each got a DIFFERENT salt
  (so same password would produce different hashes)

### My own words (locked in)
- Hashing ≠ encryption. One-way. Cannot be unhashed.
- Same input → same hash (deterministic)
- One-byte change → totally different hash (avalanche)
- MD5 is broken for passwords. Fast = attacker's best friend.
- scrypt is slow ON PURPOSE. That's its security.
- Salt = random data per user → same password = different hash per user
- The salt is stored IN the hash (prefixed).
- Fast hashes are fine for checksums; fatal for passwords.
- Different algorithms for different requirements.
## 12.37 Cyber Laws — Phase B DONE ✅

Learned Kenya's Computer Misuse and Cybercrimes Act (2018).
Understood authorization = the line between legal and criminal.

### Core concepts
- Cyber law = laws governing computers, networks, digital behavior
- The ONE test: authorization
  - Own it → ✅ legal
  - Signed permission → ✅ legal
  - Neither → ❌ cybercrime
- Authorized access = explicit, in writing (contract, bug bounty, scope doc)
- Exceeding authorized access = having SOME permission but going beyond it
- "For education" is NOT a legal defense
- "It was public" is NOT a legal defense
- "For a good cause" is NOT a legal defense

### Kenya's Computer Misuse and Cybercrimes Act, 2018
- § 3  Unauthorized access → KSh 3M fine or 2 years prison
- § 4  Unauthorized access + intent to commit crime → 5 years
- § 5  Unauthorized interference with data → 5 years
- § 6  Unauthorized interference with a system → 5 years
- § 7  Unauthorized disclosure of data → 3 years
- § 14 Cyber harassment → 10 years
- § 16 Identity theft → 10 years
- § 22 Failure to report a cybercrime → 5 years

### Same concept worldwide
- US — Computer Fraud and Abuse Act (CFAA), 1986
- UK — Computer Misuse Act, 1990
- Nigeria — Cybercrimes Act, 2015
- South Africa — Cybercrimes Act, 2020
- International — Budapest Convention, 2001

### The legal pentest setup
1. Signed contract (or accepted bug bounty policy)
2. Defined scope (which URLs/IPs)
3. Time window
4. Exclusions
5. Emergency contact
6. Liability limits

### Real commands I ran
- cat ~/pos-lab/README.md
- grep -i "legal\|authoriz\|permission" ~/pos-lab/docs/*.md

### Things I saw
- pos-lab says: "Built for training" → my permission to attack it
- Docs use "authorization" in code sense (CWE-639, BOLA, etc.)
- But that's not the same as LEGAL authorization

### My own words (locked in)
- The ONE difference between pentester and cybercriminal = written permission
- Own it or get signed permission. Stay in scope. Don't cause harm.
- "Friend said yes" is weaker than a signed contract
- Even for friends, get it in writing
- Bug bounty platforms exist because companies sometimes sue good-faith
  researchers. Pre-negotiated legal terms protect BOTH sides.
- If in doubt → ask first. Or don't touch.
- It was "mine" → legal to crack pos-lab
- It was "someone else's" → crime in every country
- Cyber law is more complex than technical security — get a lawyer
  if you're doing it professionally
## 12.38 Ethical Hacking Legal Framework — Phase B DONE ✅

Wrote a real Rules of Engagement for pos-lab. Understood the full
legal paperwork stack.

### The five documents before any pentest
1. Authorization letter — permission from an officer
2. Scope document — what you can test
3. NDA — keep everything confidential
4. Rules of Engagement (RoE) — how you test
5. Insurance / liability agreement — who pays if it breaks

Plus: proposal/contract (the business relationship)

### What each protects
- Authorization → your legal right to test
- Scope → what you touch (limits)
- NDA → the company's secrets
- RoE → how you do it (timing, methods, emergency contact)
- Insurance → liability if something breaks

### The five ethical principles
1. Authorization — always have written permission
2. Scope — never go outside agreed limits
3. No harm — don't break things on purpose
4. Confidentiality — never leak findings
5. Responsible disclosure — report to owner first, not public

### Responsible disclosure — the 90-day rule
1. Find bug → report privately
2. Give ~90 days to fix
3. Coordinate disclosure
4. Publish after fix (with permission)
5. If ignored 90 days → may disclose publicly (legal risks vary)

Popularized by Google Project Zero.

### My own words (locked in)
- The technique is the same for pentester and criminal.
  The paperwork is what makes it legal.
- Five documents: authorization, scope, NDA, RoE, insurance
- RoE is the "how" — timing, methods, emergency, exclusions
- Responsible disclosure: private first, public only after fix
- 90 days is the industry standard, not a law
- "Friend said yes" < signed authorization
- Even for friends, even for your own systems — write it down
- Self-owned = no third-party authorization needed (but document it)
- "For education" is not a legal defense. Authorization is.

### Real commands I ran
- cat ~/pos-lab/README.md
- nano ~/master/PRACTICALS/12-cybersecurity/12.38-legal-framework/pos-lab-ROE.md

### Things I saw
- pos-lab README explicitly says "intentionally vulnerable by design,
  built for training" — that's its authorization statement
- I wrote a full RoE for pos-lab
- The document names tester, owner, scope, timing, exclusions,
  reporting, liability, emergency contact, signature

### Compare — real-world incidents
- Kevin Mitnick: 5 years prison (1990s hacking)
- Became a paid security consultant using the SAME techniques
- Difference: paperwork, permission, signed contracts
- Bug bounty hunters sometimes get threatened/sued even for
  good-faith reporting — that's why platforms like HackerOne exist
  (pre-negotiated legal terms)
## 12.38 Ethical Hacking Legal Framework — Phase B DONE ✅

Wrote a real Rules of Engagement for pos-lab. Created a full
template pack for future engagements.

### The five documents before any pentest
1. Authorization letter — signed permission from an officer
2. Scope document — what you can test
3. NDA — keep everything confidential
4. Rules of Engagement (RoE) — how you test
5. Insurance / liability agreement — who pays if it breaks

### What each protects
- Authorization → your legal right to test
- Scope → what you touch (limits)
- NDA → the company's secrets
- RoE → how you do it (timing, methods, emergency)
- Insurance → liability if something breaks

### The five ethical principles
1. Authorization — always have written permission
2. Scope — never go outside agreed limits
3. No harm — don't break things on purpose
4. Confidentiality — never leak findings
5. Responsible disclosure — report to owner first, not public

### Responsible disclosure — the 90-day rule
1. Find bug → report privately
2. Give ~90 days to fix
3. Coordinate disclosure
4. Publish after fix (with permission)
5. If ignored 90 days → may disclose publicly (legal risks vary)

### Files I created (in ~/master/PRACTICALS/12-cybersecurity/12.38-legal-framework/)
- pos-lab-ROE.md — working RoE for this lab
- templates/01-authorization-letter.md
- templates/02-scope-document.md
- templates/03-nda.md
- templates/04-rules-of-engagement.md
- templates/05-liability-agreement.md

### All committed to GitHub
Commit: 701fb2b "12.38: five legal framework templates"
All 6 files confirmed via git ls-files.

### Real commands I ran
- git add -A
- git commit -m "12.38: five legal framework templates"
- git push origin main
- git ls-files | grep "12.38"

### Things I saw
- 5 templates + pos-lab-ROE all tracked in git
- Committed to origin/main successfully
- Templates are reusable for any future engagement

### My own words (locked in)
- The technique is the same for pentester and criminal.
  The paperwork is what makes it legal.
- Five documents: authorization, scope, NDA, RoE, insurance
- RoE is the "how" — timing, methods, emergency, exclusions
- Responsible disclosure: private first, public only after fix
- 90 days is the industry standard, not a law
- "Friend said yes" < signed authorization
- Even for friends, even for your own systems — write it down
- Self-owned = no third-party authorization needed (but document it)
- "For education" is not a legal defense. Authorization is.
- I now have a REUSABLE legal template pack for any future job
## 12.39 Compliance (ISO 27001, PCI-DSS) — Phase B DONE ✅

Read pos-lab's COMPLIANCE.md: 37 vulnerabilities mapped to
PCI-DSS, HIPAA, SOC 2, GDPR.

### The 4 major frameworks
| Framework | Protects | Who needs it | Penalty |
|-----------|----------|--------------|---------|
| PCI-DSS | Credit card data | Anyone touching card data | $5K-$100K/month, lost card privileges |
| HIPAA | Health data | US healthcare | $100-$50K per violation |
| GDPR | EU personal data | Anyone with EU users | Up to 4% global revenue or €20M |
| SOC 2 | Service controls | SaaS, cloud providers | No fine (customers demand it) |
| ISO 27001 | Info security program | Any org (voluntary) | No fine (customers demand it) |

### What pos-lab taught me
- COMPLIANCE.md maps every vulnerability to compliance failures
- One vuln = multiple framework failures
  - AUTH-01 (MD5) → PCI-DSS 3.5 + HIPAA 312(d) + SOC 2 CC6.1 + GDPR Art.32
  - PROD-01 (SQLi) → PCI-DSS 6.2 + HIPAA 312(c) + SOC 2 CC6.1 + GDPR Art.32
- Secure mode of pos-lab = "compliance-shaped" (every control satisfied)
- Vuln mode = every framework fails

### The most important sentence
"Compliance ≠ security. You can pass every audit and still get breached."
- Compliance is a FLOOR, not a CEILING
- Audit = checklist (may be outdated)
- Secure = actual practice
- Passing audit + getting breached = common (Equifax, Target, etc.)

### Real commands I ran
- cat ~/pos-lab/docs/COMPLIANCE.md

### Things I saw
- 4 frameworks mapped (PCI-DSS v4.0, HIPAA Security Rule, SOC 2, GDPR)
- 37 lab vulnerabilities × 4 frameworks = huge cross-reference table
- Every vuln fails at least one framework
- The doc ends with references to all 4 official sources

### My own words (locked in)
- Compliance = the business side of security
- PCI-DSS = credit cards (Visa/Mastercard enforce it)
- HIPAA = US health data (HHS enforces it)
- GDPR = EU personal data (up to 4% global revenue fine)
- SOC 2 = trust controls (no law, but customers demand it)
- ISO 27001 = info security program (voluntary, market-driven)
- One vulnerability can fail multiple compliance requirements
- Compliance ≠ security. It's a floor.
- Audits prove PROCESS, not perfect code
- Real post-breach reports: "we passed audit, but had an IDOR"
- Compliance + attack skills = professional-ready

### The compliance map (from the doc)
- Every vuln in the lab maps to specific compliance requirements
- Example: SQLi (PROD-01) violates 4 frameworks simultaneously
- This is the business impact of every vulnerability you exploit
- A pentester who can say "this fails PCI-DSS 6.2" wins the CTO's attention
