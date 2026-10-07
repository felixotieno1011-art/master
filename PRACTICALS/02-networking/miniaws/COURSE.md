# AWS Learning Course — Master TOC

## Course Rules

1. **Analogy first, then real English** — every concept gets both
2. **Assume I know nothing** — every term defined from scratch
3. **Cross-references** — every concept linked to past/future chapters
4. **CONFIRM gate** — can't answer the confirm question? We redo the chapter.
5. **TEACH gate** — if you can't teach it to a friend, you haven't learned it.
6. **Practical every chapter** — real AWS syntax
7. **No moving on without understanding**

## Chapter Format

Every chapter has:
- 🎬 Precap
- 🔗 Connections (backward + forward)
- 📜 History
- 🎭 Analogy
- 📖 Real English
- 🎯 One-liner
- 🌍 Real-life application
- 😂 Comedy break
- 🤔 "What do you think?" (predict before running)
- 🧠 "Assume I know nothing" (define every term)
- 💻 Practical (real AWS syntax)
- ✅ Check
- ❓ Confirm (must answer correctly)
- 🔄 Recap
- 💭 Reflect (thinking question)
- 📌 Cross-reference (past chapters referenced)

---

## Part 1 — Networking Fundamentals

| # | Chapter | Status | Key concepts |
|---|---------|--------|--------------|
| 1 | What is a Network? | ⏳ Next | Packets, IP addresses, ping, round-trip time |
| 2 | CIDR and IP Ranges | ⏳ | `10.0.0.0/16`, slash notation, `2^(32-slash)` |
| 3 | VPCs and Subnets | ⏳ | Private network, subnets as slices |
| 4 | Public vs Private Subnets | ⏳ | Route to IGW, 3-step connect process |
| 5 | NAT Gateways | ⏳ | Outbound-only internet for private subnets |
| 6 | Route Tables Deep Dive | ⏳ | Longest-prefix match, peering, VPN, TGW |
| 7 | Security Groups | ⏳ | Per-instance firewalls, stateful |
| 8 | Subnet Math | ⏳ | AWS reserves 5 IPs per subnet |
| 9 | Networking Capstone | ⏳ | Full 3-tier VPC architecture |

## Part 2 — Cloud Computing

| # | Chapter | Status | Key concepts |
|---|---------|--------|--------------|
| 10 | AWS Account Model | ⏳ | Accounts, regions, tags |
| 11 | Compute (EC2) | ⏳ | Instances, AMIs, lifecycle |
| 12 | Storage (S3) | ⏳ | Buckets, objects, keys, URLs |
| 13 | Identity (IAM) | ⏳ | Users, groups, policies, roles |
| 14 | Monitoring (CloudWatch) | ⏳ | Metrics, alarms, logs |
| 15 | IaC (CloudFormation) | ⏳ | Templates, stacks, Ref |
| 16 | Capstone: 3-Tier App | ⏳ | Full deployment |

---

## Cross-Reference Map

| Concept | First taught | Reinforced in |
|---------|--------------|---------------|
| IP addresses | Ch 1 | Ch 2, 3, 4 |
| CIDR | Ch 2 | Ch 3, 4, 8 |
| VPC | Ch 3 | Ch 4, 5, 6, 9 |
| Subnet | Ch 3 | Ch 4, 5, 8 |
| Public/private | Ch 4 | Ch 5, 6, 9 |
| Route tables | Ch 4 | Ch 5, 6, 9 |
| IGW | Ch 4 | Ch 5, 6 |
| NAT | Ch 5 | Ch 6, 9 |
| Security Groups | Ch 7 | Ch 9, 16 |
| Reserved IPs | Ch 8 | Ch 9 |
| IAM | Ch 13 | Ch 16 |

---

## Progress

**Chapters complete:** 0 of 16
**Current position:** About to start Chapter 1
**Last updated:** 2026-10-06
