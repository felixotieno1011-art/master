### 8.3 HTTPS, TLS, Certificates — Phase B DONE ✅

Inspected real certificates from Google and GitHub.

### Core concepts
- HTTPS = HTTP wrapped in TLS
- TLS uses BOTH encryption types:
  - Asymmetric (public/private keys): safe but slow → exchanges session key
  - Symmetric (one shared key): fast but needs safe key exchange → encrypts data
  - Together: solve each other's weakness
- Certificate = digital ID card signed by a Certificate Authority (CA)
- Cert contains: subject, issuer, public key, validity dates, signature
- Short validity (~90 days) = less damage if stolen, forces renewal, auto-renewed
- CA:FALSE flag = this cert cannot sign other certs (prevents abuse)
- SAN (Subject Alternative Name) = one cert can cover many domains
- Trust chain: Root CA → Intermediate CA → Leaf cert
- Browser ships with a trust list of root CAs

### Real commands I ran
- openssl s_client -connect google.com:443 -servername google.com | openssl x509 -noout -text
- openssl s_client -connect github.com:443 ... -noout -subject -issuer -dates

### Things I saw
- Google's cert: issuer = Google Trust Services (own CA), subject = *.google.com
  SAN list covers *.android.com, *.youtube.com, g.co, goo.gl, etc.
  Key type: EC 256-bit (P-256), signature: ecdsa-with-SHA256
  Validity: Sep 18 → Dec 11 2026 (90 days)
- GitHub's cert: issuer = Sectigo Limited (commercial CA, UK)
  Subject = CN=github.com
- Both use ~90-day validity and ECDSA

### My own words (locked in)
- Symmetric and asymmetric solve each other's weakness
- CA:FALSE prevents a stolen cert from signing fake certs
- Short validity limits damage if a cert is stolen
- One cert can cover many domains via SAN
- Real certs are short-lived, auto-renewed, DV-level by default
- Reading certs = seeing the trust machinery of the internet
## 8.6 Ethical Hacking Intro — Phase B DONE ✅

Learned the 5 phases of penetration testing.
Ran full public recon on safaricom.co.ke.
Mapped my pos-lab attacks to the 5 phases.

### The 5 phases of a pentest
1. Reconnaissance — gather info (passive + active)
2. Scanning & Enumeration — ports, services, versions
3. Exploitation — break in
4. Post-exploitation — escalate, pivot, dump
5. Reporting — document findings + remediation

### Attack types by knowledge
- Black box  = no prior knowledge (external attacker sim)
- Grey box   = some knowledge (partial creds, partial map)
- White box  = full knowledge (source code, credentials)

### Attack types by target
- Web app, network, mobile, cloud, social engineering, physical

### Public recon on safaricom.co.ke (public info only)
- WHOIS: 23-year-old domain, self-registered, DNSSEC signed
- MX: Cisco IronPort (EU cloud email)
- SPF: ~all (soft fail)
- CAA: Amazon, DigiCert, GlobalSign, Google
- Atlassian Jira/Confluence: login-protected
- WAF stack: Akamai + CloudFront + Imperva
- HSTS: 1 year
- Curl blocked (bot detection)
- Verdict: professional-grade security

### pos-lab mapped to 5 phases
1. Reconnaissance → read docs/ (LABS.md, OWASP-MAP.md, CWE-MAP.md)
2. Scanning → grep server.js for routes (found /api/auth/login, /api/auth/me)
3. Exploitation → crack MD5, crack JWT secret, forge alg:none
4. Post-exploitation → used forged token to access /api/auth/me as boss
5. Reporting → notes in NOTES/12-cybersecurity.md

### My own words (locked in)
- Every pentest follows the same 5 phases
- Same techniques as a criminal, but with permission + scope + no harm
- Public recon (WHOIS, DNS, browser) is legal without permission
- Active scanning (ports, brute-force) requires permission
- Curl gets blocked by WAFs; browsers don't
- Safaricom has professional-grade security: multi-WAF, DNSSEC, CAA, HSTS
- The most important phase for the client is #5 (Reporting)
  — without the report, the pentest has no value
- You can't pentest what you don't know — recon is everything
## 8.6 Ethical Hacking Intro — Phase B DONE ✅

Learned the 5 phases of a pentest. Ran public recon on safaricom.co.ke.
Scanned pos-lab with nmap. Mapped my attacks to the 5 phases.

### The 5 phases
1. Reconnaissance
2. Scanning & Enumeration
3. Exploitation
4. Post-exploitation
5. Reporting

### Full recon done
- safaricom.co.ke: WHOIS, DNS, MX, SPF, CAA, Atlassian, WAF (Akamai + CloudFront + Imperva)
- Full report: PRACTICALS/12-cybersecurity/12.6-full-pentest/recon/safaricom-recon.md

### Full scan done
- nmap -p 22,80,443,3000,3001,... → only 3001 open (pos-lab)
- nmap -sV → X-Lab-Mode leaked, security headers compared
- SECURE mode: full headers (CSP, X-Frame, HSTS)
- VULN mode: 0 headers + CORS wildcard + no API versioning
- Full report: PRACTICALS/12-cybersecurity/12.6-full-pentest/scanning/pos-lab-scan.md

### pos-lab attacks mapped to phases
1. Reconnaissance → read docs/ (LABS.md, OWASP-MAP.md, CWE-MAP.md)
2. Scanning → grep server.js for routes
3. Exploitation → crack MD5, crack JWT secret, forge alg:none
4. Post-exploitation → used forged token to access /api/auth/me as boss
5. Reporting → notes in NOTES/12-cybersecurity.md

### My own words (locked in)
- Every pentest follows the same 5 phases
- Same techniques as a criminal, but with permission + scope + no harm
- Recon comes first — you can't attack what you don't know
- Public recon (WHOIS, DNS) = legal without permission
- Active scanning (ports, brute-force) = requires permission
- nmap -sV > curl -I for discovery (sends many probe types)
- X-Lab-Mode leaks the security posture
- Every vulnerability = one env var away
- The 5 phases will be explored deeply in 12.11-12.15
- The next topics will build on this
## 8.1 Web Security Basics — Phase B DONE ✅

Learned the attack surface of web apps. Understood the 5 principles.
Identified pos-lab's attack surface.

### Core concepts
- Web security = protecting every "door" of the app
- Attack surface = all entry points an attacker can try
- Every endpoint is a door. Every input is a risk.
- Every component has an attack surface:
  - HTML, CSS, JS, forms, APIs, login, uploads, database, cookies, server

### The 5 security principles
1. Input validation — never trust user input
2. Authentication — prove who you are
3. Authorization — prove what you're allowed to do
4. Session management — keep users logged in safely
5. Logging & monitoring — detect attacks

### Input validation — the #1 rule
"Never trust user input" means:
- Every piece of data from outside (URL, form, cookie, header, JSON, file)
  could be malicious
- Not "trust the person" — "assume the data is hostile"

### If you trust input — the damage
- SQL Injection → input becomes SQL commands
- XSS → input becomes JavaScript
- Command Injection → input becomes shell commands
- Path traversal → input becomes file paths
- Null / missing fields → crashes, corruption, auth bypass

### Real commands I ran
- ls ~/pos-lab/routes/

### Things I saw
- pos-lab has 9 route files (auth, products, sales, uploads, finance)
- Every route is a door
- Every endpoint accepts some input

### pos-lab's attack surface
| Endpoint | Input | Risk |
|----------|-------|------|
| /api/auth/login | username, password | Auth, rate limit |
| /api/products | search | SQLi (PROD-01) |
| /api/users/:id | user id | IDOR (PROD-03) |
| /api/sales | quantity, price | SALE-01 to 05 |
| /api/uploads | file | FILE-01 to 04 |
| /api/finance | amount | validation |

### My own words (locked in)
- Web security = protecting every door
- Attack surface = all entry points
- 5 principles: input validation, auth, authz, session, logging
- Every endpoint is a door
- Never trust input
- "Trust" in security = "assume the data is hostile"
- Input can become SQL, JS, shell, file paths
- Null / undefined input can crash apps or bypass auth
- SQLi is still the most common despite 20+ years of warnings
  because devs forget parameterized queries

### Connection to other topics
- 4.1 (HTML) — structure exposed to attackers
- 4.4 (JS) — XSS runs JS in user's browser
- 4.5 (DOM) — DOM manipulation is the XSS target
- 6.1 (Databases) — SQL injection target
- 7.5 (HTTPS) — prevents MITM
- 12.15 (Web Hacking) — hands-on exploitation
- pos-lab has all these vulnerabilities live
## 8.2 OWASP Top 10 — Phase B DONE ✅

Read pos-lab's OWASP map. Verified it against the actual code.
Found 2 documentation errors (A08 and A10 are covered but marked missing).

### What OWASP is
- OWASP = Open Worldwide Application Security Project
- Non-profit, free, community-driven
- Publishes the Top 10 + tools + guides
- owasp.org

### The OWASP Top 10 (2021)
| Rank | Category | Meaning |
|------|----------|---------|
| A01 | Broken Access Control | Users access things they shouldn't (IDOR) |
| A02 | Cryptographic Failures | Weak/missing crypto (MD5, no HTTPS) |
| A03 | Injection | Input becomes code (SQLi, XSS, command) |
| A04 | Insecure Design | Missing rate limits, weak logic |
| A05 | Security Misconfiguration | Missing headers, CORS *, verbose errors |
| A06 | Vulnerable and Outdated Components | Old libraries with CVEs |
| A07 | Auth Failures | Weak passwords, no MFA, predictable sessions |
| A08 | Software and Data Integrity Failures | Unsafe deserialization, unsigned updates |
| A09 | Logging & Monitoring Failures | No audit trail, no alerts |
| A10 | Server-Side Request Forgery (SSRF) | Server fetches arbitrary URLs |

### pos-lab coverage (corrected)
| Rank | Category | Covered? | pos-lab IDs |
|------|----------|---------|-------------|
| A01 | Broken Access Control | ✅ | PROD-03, SALE-02 |
| A02 | Cryptographic Failures | ✅ | AUTH-01, 02, 03, 06, SESS-03, HDR-03 |
| A03 | Injection | ✅ | PROD-01, PROD-02, LOG-01 |
| A04 | Insecure Design | ✅ | SALE-01, 02, 03, FILE-01, FILE-03 |
| A05 | Security Misconfiguration | ✅ | HDR-01, 02, 03, API-02, 04, FILE-03 |
| A06 | Vulnerable Components | ❌ | (none — zero dependencies) |
| A07 | Auth Failures | ✅ | AUTH-04, 05, SESS-01, 02 |
| A08 | Integrity Failures | ✅ | INTG-01 (routes/cart.js eval) |
| A09 | Logging & Monitoring | ✅ | LOG-01, 02, 03 |
| A10 | SSRF | ✅ | SSRF-01 (routes/ssrf.js) |

**Coverage: 9 of 10** (not 7 as the doc claimed).

### Documentation errors I found
The doc `docs/OWASP-MAP.md` says A08 and A10 are not covered.
BUT:
- `routes/ssrf.js` = SSRF lab (A10)
- `routes/cart.js` = eval-based deserialization (A08, INTG-01)

### Real commands I ran
- cat ~/pos-lab/docs/OWASP-MAP.md | head -80
- grep -rn "fetch(|http.get|https.get" routes/ lib/ middleware/
- grep -rn "eval(|new Function(|vm.run" routes/ lib/ middleware/

### Things I saw
- routes/ssrf.js line 61: fetch(url, ...) — SSRF exists
- routes/cart.js line 16: eval('(' + obj.slice(...) + ')') — eval deserialization
- routes/cart.js.bak says "INTG-01: vuln mode deserializes with eval()"
- The OWASP map is OUTDATED

### My own words (locked in)
- OWASP = Open Worldwide Application Security Project (non-profit)
- The Top 10 is updated every 3-4 years
- 2021 list: A01-A10
- pos-lab covers 9 of 10, but the doc says only 7
- Documentation can be wrong. Code is truth. Verify.
- A06 is genuinely missing (zero dependencies)
- I found A08 and A10 by grepping the code, not trusting the doc
- "Documentation is a claim. Code is the truth."
- The doc's "A10 not covered" was written before ssrf.js was added
- The doc's "A08 not covered" was written before cart.js was added
- The doc wasn't updated when the code changed
- Real-world lesson: docs drift from code. Always verify.

### Deep dives deferred to Part 12
- 12.15: Web hacking (SQLi, XSS, CSRF)
- 12.31: OWASP Top 10 deep dive
- 12.33: API Security Top 10
- 12.35: Container/K8s security

### The OWASP API Top 10 (2023) — pos-lab coverage
- 8 of 10 covered (BOLA, Auth, Property, Rate, Function, Business, Misconfig, Inventory)
- API7 (SSRF) — actually covered by ssrf.js too
- API10 (Unsafe Consumption) — genuinely missing
## 8.4 Secure Coding — Phase B DONE ✅

Learned the defender's playbook. Connected every fix to the
vulnerability it prevents. Saw pos-lab's secure code.

### The core rule
NEVER TRUST USER INPUT. Assume everything is malicious
until validated.

### The 7 rules of secure coding
1. Validate input — type, length, format. Reject if invalid.
2. Parameterize queries — use ? placeholders, never string concat
3. Escape output — textContent (not innerHTML), encode HTML entities
4. Use HTTPS — encrypt data in transit
5. Hash passwords — scrypt/bcrypt/argon2 (never MD5)
6. Least privilege — DB user only gets what it needs
7. Fail securely — don't leak errors, don't log secrets, use
   generic error messages (prevents enumeration)

### The pattern across all vulnerabilities
- SQLi = input becomes SQL code (bad: ${q}, good: ?)
- XSS = input becomes HTML/JS (bad: innerHTML, good: textContent)
- Weak passwords = input not processed with enough cost
  (bad: MD5, good: scrypt)
- Common thread: treat input as DATA, not CODE

### Real code I saw in pos-lab
- routes/products.js line 40: `if (vuln('PROD-01'))` = vulnerable version
- routes/products.js line 42: `WHERE name LIKE '%${q}%'` = string concat
- routes/products.js line 58: `// SECURE: parameterized query`
- routes/products.js line 62: `WHERE name LIKE ?` = safe

### Real commands I ran
- grep -n "PROD-01\|parameterized\|?" ~/pos-lab/routes/products.js

### Things I saw
- Both the vulnerable and secure versions live in the same file
- SECURE_MODE decides which one runs
- The vulnerability is ONE line of code
- The fix is ONE line of code
- The difference: `?` vs `${q}`
- Same pattern for XSS: textContent vs innerHTML
- Same pattern for passwords: scrypt vs md5

### Real-world cases
- Equifax 2017: 143M people, $575M fine, unpatched Apache Struts
- Fix was available for months
- One update would have prevented it
- This is why A06 (Vulnerable Components) exists in OWASP Top 10

### My own words (locked in)
- Never trust user input
- Every vulnerability comes from treating input as code
- SQLi, XSS, weak hashing: same class of mistake
- The fix is always "input is data, not code"
- Validate → parameterize → escape → hash → use HTTPS
- Fail securely: generic errors, no stack traces, no logs of secrets
- Least privilege: DB user only needs the minimum
- Secure coding = writing code that resists attacks by design
- Most real breaches come from a known vulnerability that wasn't patched

### The full secure coding checklist
- [ ] Input validated on every endpoint
- [ ] SQL uses ? parameters
- [ ] HTML uses textContent
- [ ] Passwords use scrypt/bcrypt
- [ ] HTTPS enforced (HSTS)
- [ ] DB user has least privilege
- [ ] Errors are generic (no stack traces)
- [ ] Passwords never logged
- [ ] Dependencies updated (npm audit)
- [ ] Rate limiting on login
- [ ] Session cookies HttpOnly, Secure, SameSite
- [ ] CSRF tokens on state-changing requests
## 8.7 Password Hashing & Crypto — Phase B DONE ✅

Measured hash speed on my phone. Understood salt vs pepper.
Learned the full modern password storage rules.

### The measurement (on my phone)
| Algorithm | Time for 1000 hashes | Per hash |
|-----------|---------------------|----------|
| MD5       | 49 ms               | 0.05 ms  |
| scrypt    | 152,200 ms (est.)   | 152 ms   |

**scrypt is ~3000x slower than MD5 per hash.**
- 1 million MD5 guesses: 49 seconds
- 1 million scrypt guesses: ~42 hours
- 14 million (RockYou) with scrypt: ~25 days
- Strong password (not in wordlist): millions of years

### The #1 rule
NEVER store passwords in plaintext.
Always store a slow, salted hash.

### The password storage stack (best practice)
1. Generate random salt (16+ bytes)
2. Add pepper (from .env, NOT the DB)
3. Hash with argon2id or bcrypt/scrypt
4. Store: algorithm$salt$hash
5. Never log passwords, never transmit plaintext

### Salt vs Pepper
| | Salt | Pepper |
|--|------|--------|
| Random? | Yes, unique per user | No, same for all |
| Stored where? | In the DB (with the hash) | Outside the DB (.env / secrets manager) |
| Defeats? | Rainbow tables, cross-user cracking | DB-only breaches |
| If lost? | Recoverable (it's in the hash) | All passwords invalid (must reset) |

### The hash algorithm timeline
| Algorithm | Year | Status for passwords |
|-----------|------|---------------------|
| MD5 | 1991 | 💀 Broken — 0.05 ms/hash |
| SHA-1 | 1995 | 💀 Broken |
| SHA-256 | 2001 | ⚠️ Too fast — not for passwords |
| bcrypt | 1999 | ✅ Good — 30+ years of use |
| scrypt | 2009 | ✅ Better — memory-hard |
| argon2 | 2015 | ✅ Best — winner of PHC |

**Modern recommendation: argon2id (or bcrypt).**

### The 7 rules of password storage
1. NEVER store plaintext
2. Use slow hashes (bcrypt/scrypt/argon2)
3. Use random salt per user (16+ bytes)
4. Optionally add pepper (stored outside DB)
5. Use constant-time compare (timingSafeEqual)
6. Never log passwords, never transmit plaintext
7. Validate policy: 12+ chars, breach check, no composition rules

### Timing attacks (subtle bug)
- Bad:  if (hash(input) === storedHash)
- Good: if (crypto.timingSafeEqual(hash(input), storedHash))
- === returns as soon as a difference is found
- timingSafeEqual takes the same time regardless
- Prevents character-by-character hash guessing

### Real commands I ran
- node -e "... MD5 1000 hashes ... scrypt 10 hashes ..."

### Things I saw
- MD5: 1000 hashes in 49 ms (0.05 ms each)
- scrypt: 10 hashes in 1522 ms (152 ms each)
- Ratio: ~3000× slower
- scrypt is the defense against DB leaks

### My own words (locked in)
- MD5 is fast → great for checksums, terrible for passwords
- scrypt is slow → perfect for passwords
- 3000× slower = attacker tries 3000× fewer passwords per second
- Salt = random data per user, stored in DB
- Pepper = secret data for all users, stored OUTSIDE DB
- Salt defeats rainbow tables
- Pepper defeats DB-only breaches
- Never store plaintext
- Never use MD5/SHA-1/SHA-256 for passwords
- bcrypt/scrypt/argon2 are the only acceptable options
- Use timingSafeEqual, not ===
- Long passwords > composition rules
- NIST 2017: no forced rotation, no composition rules
- Bill Burr (NIST 2003) publicly admitted his advice was wrong

### Real-world breach history
- LinkedIn 2012: 6.5M MD5 hashes leaked, all cracked in weeks
- Adobe 2013: 150M accounts, weak 3DES-ECB
- RockYou 2009: 32M plaintext passwords
- Every breach teaches the same lesson: never store weak hashes

### The complete secure login flow
1. User signs up with password
2. Server validates (12+ chars, breach check)
3. Server generates random salt (16 bytes)
4. Server adds pepper (from .env)
5. Server hashes with argon2id or scrypt
6. Server stores: algorithm$salt$hash
7. User logs in → server hashes input with stored salt + pepper
8. Server compares with timingSafeEqual
9. If match → session created (JWT or cookie)
## 8.8 Authentication Attacks — Phase B DONE ✅

Found username enumeration in pos-lab (AUTH-05).
Saw the session vulnerabilities (SESS-01 to SESS-04).

### The 6 authentication attacks
1. Username Enumeration — different errors reveal which users exist
2. Brute Force (online) — try many passwords on the login form
3. Credential Stuffing — reuse breached passwords on other sites
4. Session Hijacking — steal the session cookie
5. Session Fixation — attacker sets a known session ID
6. MFA Bypass — attack the second factor (SIM swap, OTP phishing)

### Username enumeration (AUTH-05) — I did this
Vulnerable mode:
- Real user + wrong password → "Wrong password"
- Fake user + any password → "User not found"
→ Attacker learns which users exist

Secure mode:
- Both → "Invalid credentials"
→ Attacker learns nothing

### Why enumeration matters
- Halves the attack surface
- Lets attacker focus brute force on valid users
- First step of a targeted attack

### Session vulnerabilities (pos-lab)
| ID | Vulnerability | Fix |
|----|--------------|-----|
| SESS-01 | Sessions never expire | Idle + absolute timeout |
| SESS-02 | No logout-all | revokeAllForUser() |
| SESS-03 | Predictable IDs (8 hex) | 32 random bytes (64 hex) |
| SESS-04 | Session fixation (client supplies ID) | Always generate server-side |

### Session security best practices
1. Random session IDs (32+ bytes, crypto-random)
2. HttpOnly cookie (XSS can't read)
3. Secure cookie (only HTTPS)
4. SameSite cookie (CSRF protection)
5. Idle timeout (24h)
6. Absolute timeout (30 days)
7. Revocation on logout (and on password change)
8. Logout-all endpoint
9. Bind session to user agent / IP (optional, breaks mobile)
10. Regenerate session ID on login (fixation fix)

### Real commands I ran
- sed -i 's/^SECURE_MODE=.*/SECURE_MODE=true/' .env
- node ~/pos-lab/db/init.js
- grep -n "createSession|sessionId|maxAge|expires" ~/pos-lab/lib/sessions.js

### Things I saw
- Vulnerable mode: "Wrong password" vs "User not found"
- Secure mode: both "Invalid credentials"
- 8-hex session IDs = 4 billion combinations (guessable in seconds)
- 64-hex session IDs = 10^77 combinations (impossible)
- Session fixation: client can supply session ID in vuln mode
- No logout-all in vuln mode

### My own words (locked in)
- Online attacks attack the login form
- Offline attacks attack stolen hashes
- Username enumeration = information leak via error messages
- Fix: same error message for both cases
- Credential stuffing = reuse leaked passwords
- Session hijacking = steal the cookie
- Session fixation = attacker supplies the session ID
- Predictable session IDs = guessable = account takeover
- No logout-all = can't kick out a stolen session
- Sessions must expire (idle + absolute)
- Every login should regenerate the session ID
- Every password change should invalidate all sessions
- MFA is the strongest defense against credential attacks
- Deepfake voice attack (2019) — €220K stolen by voice imitation

### Connection to other topics
- 12.17 (Password Attacks) — offline side
- 12.7 (Auth Failures) — concept
- 12.15 (Web Hacking) — XSS can steal cookies
- 12.18 (Social Engineering) — human factor
- pos-lab's session code in lib/sessions.js

## 8.9 Rate Limiting & DDoS — Phase B DONE ✅

Tested rate limiting on pos-lab login.
5 attempts allowed, then 429 Too Many Requests.
Understood DDoS and the defense stack.

### Rate limiting
- Only N requests per time window per identity
- Identity = IP, user, API key, or combination
- Exceeding it → HTTP 429 (Too Many Requests)
- Retry-After header tells when to try again
- Common: 5 attempts/min for login, 100 requests/min for API

### The rate limiter in pos-lab
- `makeRateLimiter({ max: 5, windowSeconds: 60 })`
- Key: `IP|username` (per user, per IP)
- Resets on successful login
- In-memory (zero dependencies)
- Sweep interval to prevent memory growth

### The test I ran
- 15 rapid login attempts with wrong password
- Attempts 1-5: 401 Unauthorized
- Attempts 6-15: 429 Too Many Requests
- The server blocked me after 5 failures

### Why rate limiting matters
- Brute force: 5 attempts/min = 10,000 passwords takes 33 hours
- Credential stuffing: limits reuse attempts
- Scraping: prevents bulk data extraction
- Detection: you can see the attack in logs

### DDoS (Distributed Denial of Service)
- Not one attacker — a botnet of 100,000+ compromised devices
- Types:
  1. Volumetric (UDP flood, ICMP flood, DNS amplification)
  2. Protocol (SYN flood, Ping of Death)
  3. Application layer (HTTP flood, Slowloris)
- Goal: exhaust bandwidth, connections, or CPU

### DDoS defense stack
- Layer 1: CDN (Cloudflare, Akamai) — absorbs volumetric
- Layer 2: Load balancer — distributes traffic
- Layer 3: WAF — blocks known attack patterns
- Layer 4: Rate limiting — throttles individual clients
- Layer 5: Application logic — rejects invalid requests fast
- Layer 6: Auto-scaling — adds capacity under load

### Real DDoS attacks
- 2016 Mirai botnet: 620 Gbps vs KrebsOnSecurity
- 2018 GitHub: 1.35 Tbps
- 2020 AWS: 2.3 Tbps
- Record keeps growing
- Cost for attacker: $10/hour on cloud services

### My own words (locked in)
- Rate limiting = throttle requests per identity
- 429 = Too Many Requests (HTTP status code)
- 5 login attempts per minute is standard
- Rate limiting doesn't make passwords unbreakable — it makes attacks slow enough to detect
- DDoS = many attackers, one target (botnet)
- Brute force = one attacker, many requests
- The difference is scale and distribution
- Defense in depth: CDN → LB → WAF → Rate limit → App → Auto-scale
- Every layer matters. Attackers try to break any one.
- Mirai botnet used default passwords on IoT devices
- The biggest DDoS records keep growing
- DDoS attacks are cheap for attackers, expensive for defenders

### Connection to other topics
- 12.17 (Password Attacks) — the reason we need rate limiting
- 8.8 (Authentication Attacks) — brute force on login
- 7.5 (Load Balancing) — part of DDoS defense
- 7.9 (Nginx/Reverse Proxy) — where rate limiting is often implemented
- 7.12 (Monitoring) — how you detect the attack
- pos-lab's limiter in middleware/ratelimit.js
## 8.5 Network Security — Phase B DONE ✅

Understood network defense layers.
Checked pos-lab's bind address (local vs public).
Explored firewalls, IDS/IPS, and segmentation.

### Core concepts
- **Firewall:** Controls incoming/outgoing traffic.
  - Stateless: checks packets one by one.
  - Stateful: remembers connections.
  - NGFW/WAF: inspects application layer (Cloudflare, Imperva).
  - Default Deny: block everything, allow only what's needed.
- **Network Segmentation:** Don't put everything on one network.
  - DMZ: public servers sit here.
  - Private Subnet: databases sit here, only web servers can talk to them.
  - Microsegmentation: even inside a subnet, restrict traffic.
- **IDS (Detection):** watches traffic, alerts admin, does NOT block.
- **IPS (Prevention):** inline, blocks attacks automatically.
- **VPN:** encrypted tunnel over the internet.
- **Zero Trust:** "Never trust, always verify." No inherent trust inside the network.

### The "Localhost vs Public" rule
- `127.0.0.1` (localhost) = safe. Only this device can connect.
- `0.0.0.0` = dangerous. Open to the whole network.
- pos-lab uses `process.env.HOST || '127.0.0.1'` (safe default).

### Real commands I ran
- `netstat -tuln` (failed: Android limitation)
- `grep -n "listen|127.0.0.1|0.0.0.0" ~/pos-lab/server.js`

### Things I saw
- pos-lab binds to `127.0.0.1` by default.
- To expose it, you must change `HOST` to `0.0.0.0`.
- Android blocks `netstat -tuln` (sandbox).

### My own words (locked in)
- Firewalls are the perimeter. Segmentation is the inside walls.
- IDS watches. IPS blocks.
- DMZ is where public servers go. DBs go in private subnets.
- Target was breached because HVAC was on the same network as POS.
- Zero Trust means even if you are inside, you must verify.
- Binding to `127.0.0.1` makes a server invisible to the network.
- Binding to `0.0.0.0` exposes it to everyone.
- Security is about layers (defense in depth).
- The weakest link is usually the human (phishing).
- Big companies get hacked because of third parties, zero-days, and misconfigurations.

### Real-world incident
- Target 2013: HVAC vendor credentials → network → POS → 40M credit cards.
- $18.5M settlement.
- The lesson: the air conditioning should not be on the same network as the credit card terminal.

### Connection to other topics
- 2.5 (Firewalls) — the concept
- 2.13 (IDS/IPS) — the deeper dive
- 7.5.4 (File Permissions) — similar "who can access what" concept
- 12.11/12.12 (Recon/Scanning) — the attacks this defends against
- 12.15 (Web Hacking) — what gets through the firewall
- 8.1 (Web Security) — application layer defense
