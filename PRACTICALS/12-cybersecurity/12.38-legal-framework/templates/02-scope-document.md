# SCOPE DOCUMENT — pos-lab Security Assessment

## 1. Purpose
This document defines the boundary of permitted testing for
the pos-lab security assessment.

## 2. In-scope systems

| Type | Target |
|------|--------|
| Application | ~/pos-lab (source code) |
| Server | http://127.0.0.1:3001 |
| Database | ~/pos-lab/db/pos.db (SQLite) |
| API | /api/* (all endpoints) |
| UI | /public/* (all pages) |

## 3. In-scope methods

- ✅ All OWASP Top 10 classes (SQLi, XSS, CSRF, IDOR, etc.)
- ✅ Authentication and session attacks
- ✅ JWT forgery, token cracking, algorithm confusion
- ✅ Password cracking (MD5, scrypt)
- ✅ File upload attacks
- ✅ API abuse (CORS, verbose errors, pagination, rate limiting)
- ✅ Privilege escalation
- ✅ Business logic abuse

## 4. Out-of-scope

- ❌ Any real user data (all users in pos-lab are fake)
- ❌ Any system outside ~/pos-lab
- ❌ Any real external service
- ❌ Any production system (even if credentials are known)
- ❌ The Tester's own `~/master/` learning repository
- ❌ The host operating system (~/pos-lab runs in a sandbox)

## 5. Data handling

- Test data only. Real data is not present.
- Findings are stored in the learning notes (see Reporting).
- Credentials, hashes, and tokens must never be shared externally.

## 6. Contact

**Tester:** Felix Otieno
**Owner:** Felix Otieno (self)

**Signed:** 18 October 2026
