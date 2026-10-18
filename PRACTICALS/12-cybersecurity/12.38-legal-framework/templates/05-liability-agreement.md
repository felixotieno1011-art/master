# LIABILITY AGREEMENT

**Date:** 18 October 2026

**Parties:**
- **Client:** Felix Otieno (Owner)
- **Tester:** Felix Otieno

*(Self-agreement: for real jobs, this would be between two
different entities. Same structure, different parties.)*

## 1. Acknowledgment of risk

The Client acknowledges that penetration testing may:

- Temporarily degrade service availability
- Crash test systems
- Modify test data (recoverable via db/init.js)
- Trigger alerts or automated defenses
- In rare cases, cause permanent damage

The Client accepts these risks as part of the engagement.

## 2. Liability cap

The Tester's total liability for any damages is limited to:

- **Zero** — for self-owned labs (no separate liability)
- **Actual damages** — for real engagements (included in contract)
- **Insurance coverage** — recommended for real engagements

## 3. What the Tester is responsible for

- Testing within the agreed Scope Document
- Following the Rules of Engagement
- Reporting findings accurately
- Not disclosing information outside the NDA
- Using only authorized methods

## 4. What the Tester is NOT responsible for

- Existing vulnerabilities not found during the engagement
- Damage caused by the Client's own actions
- Third-party systems outside the scope
- Data already exposed before testing began

## 5. Recovery plan

For pos-lab specifically:
- Reset the database: `node db/init.js`
- Restore from backup: `~/pos-lab/backups/`
- Rebuild the server: stop with Ctrl+C, restart with `node server.js`

## 6. Insurance (real-world engagements)

For real client engagements, the Tester should have:
- **Professional liability insurance** (E&O coverage)
- **Cyber liability insurance**
- Amounts typically $1M–$5M depending on the client

For personal labs (like pos-lab), no insurance is needed.

## 7. Signatures

_________________________________
Felix Otieno (Client)
18 October 2026

_________________________________
Felix Otieno (Tester)
18 October 2026
