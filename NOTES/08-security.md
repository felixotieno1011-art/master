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
