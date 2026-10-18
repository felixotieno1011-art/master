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
