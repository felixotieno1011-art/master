=== INCIDENT REPORT ===

## Summary
Brute-force attack on /admin, succeeded after 200+ failed attempts.
Attacker IP: 203.0.113.45
Compromised account: admin
First success: 2026-11-02 03:13:45
Contained: 2026-11-02 03:20:00 (disabled + IP blocked)
Dwell time: ~6 minutes (success to containment)

## Root Cause
No rate limit or account lockout on /admin login.
200 failed attempts went undetected by app-level controls.

## What Went Well
- SIEM alert fired
- Containment within 6 minutes
- Account disabled, not deleted (evidence preserved)

## What Went Wrong
- No lockout after N failed logins
- No MFA on admin account
- Attacker had 8.5 hours of admin access before containment

## Actions
1. Add rate limiting + lockout to /admin (see 8.9)
2. Enforce MFA on admin accounts
3. Alert on successful login from new IP
4. Update IR playbook with this scenario
