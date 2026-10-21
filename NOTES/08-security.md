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
