# Rules of Engagement — pos-lab

## Parties
- **Tester:** Felix Otieno
- **Owner of system:** Felix Otieno (self-owned training lab)
- **Purpose:** Learn security concepts on an intentionally vulnerable system

## Authorization
This is a **self-owned lab**, built and documented as
"intentionally vulnerable by design, built for training."
The tester is the system owner. No third-party authorization required.

## Scope
- **Allowed:** All routes, all endpoints, all code in ~/pos-lab
- **Allowed methods:** Any technique — including exploits, brute force,
  token forgery, and hash cracking
- **Database:** Local SQLite file (db/pos.db) — test data only
- **No real users:** The three accounts (boss/manager/seller) are fake

## Timing
- **When:** Any time (personal lab)
- **Network:** Local only (127.0.0.1:3001) — never exposed publicly

## Exclusions
- **Never:** Expose the lab to the public internet with real data
- **Never:** Use learned techniques on systems I do not own or have
  written permission to test
- **Never:** Share credentials, hashes, or findings outside personal
  learning notes

## Reporting
- Findings are recorded in:
  - ~/master/NOTES/12-cybersecurity.md
  - ~/pos-lab/docs/ (when authoring new material)
- No external disclosure is planned or permitted without the owner's consent
  (the owner is me — but the rule stands for future collaboration)

## Liability
- **Self-owned.** Damages are limited to personal time and data.
- Restore from backup if needed (db/init.js rebuilds the DB)

## Emergency contact
- **Tester:** Felix (self)
- **Rollback:** `node db/init.js` resets the database
- **Recovery:** backups folder in ~/pos-lab/backups/

## Signature
- **Tester:** Felix Otieno — 2026-10-18
- **Owner:** Felix Otieno (self)
