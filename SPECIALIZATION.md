# 🎯 SPECIALIZATION — Backend · DevOps/AWS · Cybersecurity

**Mode:** Build → Drill → Review → Defend. Theory only when asked.
**Rule:** Tick only when built AND pushed to GitHub. Curriculum topics tick
only when a build touches them. No detours.

Legend: 🎯 build · 🔁 break-fix · 🧐 review · 🗣️ defend · 📱 phone · 💻 codespaces

---

## 🟢 TRACK 1 — BACKEND (build the artifact)

### Builds
- [ ] 🎯 B1. Secure API skeleton — 2 resources, runs locally 💻
- [ ] 🎯 B2. Add JWT auth (register/login/protected route) 💻
- [ ] 🎯 B3. Add DB + one migration 💻
- [ ] 🎯 B4. Add validation + proper error responses 💻
- [ ] 🎯 B5. Add one fun feature (shortener / leaderboard / your tool) 💻
- [ ] 🎯 B6. Add tests — prove unauthorized is rejected 💻
- [ ] 🎯 B7. README: what it does + one decision explained 📱

### Drills
- [ ] 🔁 D1. Break auth — remove expiry, observe 💻
- [ ] 🔁 D2. Break DB — bad migration, recover 💻
- [ ] 🔁 D3. Break validation — send garbage, fix crash 💻

### Review & Defend
- [ ] 🧐 R1. Review B1–B7 repo 📱
- [ ] 🗣️ F1. Explain auth flow to a non-technical person 📱
- [ ] 🗣️ F2. Scenario: token stolen — what limits damage? 📱💻
- [ ] 🗣️ F3. Scenario: traffic 10x — where does it break? 📱

---

## 🔵 TRACK 2 — DEVOPS / AWS (deploy the artifact)

### Builds
- [ ] 🎯 B8. Dockerfile for the API 💻
- [ ] 🎯 B9. Compose: API + DB + Redis running together 💻
- [ ] 🎯 B10. Terraform: provision infra (IAM, VPC, compute) 💻
- [ ] 🎯 B11. CI/CD: build → test → deploy on push 💻
- [ ] 🎯 B12. Monitoring + health checks + rollback 💻
- [ ] 🎯 B13. Public deploy — API reachable on the internet 💻

### Drills
- [ ] 🔁 D4. Break the pipeline — failing test blocks deploy 💻
- [ ] 🔁 D5. Rollback drill — bad deploy, recover 💻
- [ ] 🔁 D6. Kill the DB connection — observe, fix 💻

### Review & Defend
- [ ] 🧐 R2. Review B8–B13 📱
- [ ] 🗣️ F4. Explain "how my app gets to the internet" 📱
- [ ] 🗣️ F5. Scenario: health check passes, users get 500s 📱💻
- [ ] 🗣️ F6. Scenario: design for high availability 📱

---

## 🔴 TRACK 3 — CYBERSECURITY (attack & harden your artifact)

### Builds
- [ ] 🎯 B14. Threat model your deployed API (STRIDE) 📱
- [ ] 🎯 B15. Dependency/CVE scan + fix findings 💻
- [ ] 🎯 B16. Manual attack pass: SQLi, XSS, auth bypass 💻
- [ ] 🎯 B17. IAM least-privilege review + fix 💻
- [ ] 🎯 B18. Hardening checklist applied 💻
- [ ] 🎯 B19. Security report: findings, severity, fixes 📱

### Drills
- [ ] 🔁 D7. Find the attacker in logs 💻
- [ ] 🔁 D8. Break your own rate limit — fix it 💻
- [ ] 🔁 D9. Leak a secret on purpose — detect + rotate 💻

### Review & Defend
- [ ] 🧐 R3. Review B14–B19 📱
- [ ] 🗣️ F7. Explain highest-risk path + how to detect it 📱
- [ ] 🗣️ F8. Explain one finding to a non-technical boss 📱

---

## 🏁 INTEGRATION

- [ ] 🎯 I1. One repo: API + Terraform + CI/CD + security report 💻
- [ ] 🎯 I2. Architecture diagram + decision log 📱
- [ ] 🎯 I3. Public writeup: built → deployed → secured 🎯
- [ ] 🗣️ I4. Mock interview across all three 📱

---

## 🔗 Curriculum mapping (tick TOC.md when these builds touch them)
- B3  → 6.5 ORMs, 6.7 Migrations
- B6  → 5.16 API Testing
- B10 → 7.14 IaC (deeper)
- B12 → 7.12 Monitoring (deeper)
- B14–B19 → 12.24 IR, 12.36 Secure Architecture, 12.46 Portfolio
