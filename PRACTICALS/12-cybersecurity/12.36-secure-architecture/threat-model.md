# Threat Model — Mini Pos-Lab

## 1. Assets (what we're protecting)
- Customer data (names, phones)
- Order data (what was bought, how much)
- Admin credentials
- Payment secrets (HMAC key)
- The database itself

## 2. Trust boundaries (where trust changes)
- Browser → Web Server
- Web Server → Database
- Payment Provider → Webhook
- (add any more you see)

## 3. Threats (STRIDE)
For each boundary, list threats:
- **S**poofing — impersonating a user or service
- **T**ampering — modifying data in transit or at rest
- **R**epudiation — denying an action happened
- **I**nformation disclosure — leaking data
- **D**enial of service — making it unavailable
- **E**levation of privilege — gaining more access than allowed

## 4. Current controls (what already exists)
- HMAC on webhook (5.15)
- Idempotency (5.15)
- JWT/session on browser (5.6)
- Input validation (5.7)
- (add more)

## 5. Proposed architecture change (ONE)
Pick the biggest weakness and propose a fix that reduces blast radius.
