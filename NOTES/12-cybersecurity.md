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
