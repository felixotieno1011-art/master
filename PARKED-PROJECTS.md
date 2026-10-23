# 🅿️ Parked Projects — Special Treatment Needed

Projects that need **specific conditions** we don't have yet (hardware, money, dedicated time, or a real machine).

**Not just "paused topics"** — these are **real projects** waiting for the right moment.

**Last reviewed:** 2026-10-20

---

## 1️⃣ Real VPN (WireGuard / OpenVPN) 🔒

**Status:** 🅿️ PARKED — needs a VPS

**Why parked:**
- Needs a real server (VPS ~$5/month)
- Needs kernel-level TUN/TAP (blocked on Android)
- Needs root or a real Linux machine

**What we already did on phone:**
- ✅ Built `mini_proxy.py` (HTTP forwarding)
- ✅ Built `mini_tunnel.py` (base64 wrapping)
- ✅ Understood proxy vs VPN vs tunneling conceptually

**Resume at:** After getting a VPS (DigitalOcean, Hetzner, Contabo)

**Future plan:**
1. Rent VPS ($5/month)
2. Install WireGuard server
3. Connect from phone
4. Add second device (laptop)
5. Real encrypted tunnel between them

**Estimated time:** 1 weekend after VPS arrives

---

## 2️⃣ Cloud Computing Deep Dive ☁️

**Status:** 🅿️ PARKED — needs dedicated time (2–3 weeks)

**Why parked:**
- Bigger than a single topic
- Deserves its own focused block
- Real cloud consoles need accounts (card signup)

**What we already understand:**
- Cloud = rented computers in data centers
- Big 3: AWS, Azure, GCP
- Regions + Availability Zones (redundancy)
- VPCs, subnets, public/private split
- Firebase runs on GCP

**What we want to learn deeply:**
- Real AWS console (EC2, S3, IAM, RDS, Lambda)
- Real Azure (VMs, Resource Groups, Storage)
- Real GCP (Compute, Cloud Storage, BigQuery)
- Multi-cloud networking
- Cost optimization
- Kubernetes, Terraform, CI/CD

**Resume at:** Topic 7.10 (Cloud Platforms) — real hands-on then
**Optional:** Build mini-AWS/Azure/GCP simulators first

**Estimated time:** 2–3 weeks dedicated

---

## 3️⃣ Deploy pos-lab to a Real Server 🚀

**Status:** 🅿️ PARKED — needs a VPS

**Why parked:**
- Needs public IP (phone has private IP behind Safaricom)
- Needs open port (80/443)
- Needs a domain pointing at it

**What we already know:**
- ✅ Docker basics (7.6)
- ✅ Hosting options (7.4)
- ✅ Domain + DNS + HTTPS (7.5)
- ✅ Linux server basics (7.1)
- ✅ Permissions (7.2, 7.5.4)
- ✅ pos-lab runs locally

**The plan when VPS arrives:**
1. Rent VPS (~$5/month)
2. SSH in from phone
3. Install Node.js + Git
4. Clone pos-lab from GitHub
5. Run `node server.js`
6. Set up Nginx reverse proxy (7.9)
7. Point domain at VPS
8. Get HTTPS cert (Let's Encrypt)
9. Test from a friend's phone in Mombasa

**Milestone unlocked when deployed:** "First deployed app" ✅

**Estimated time:** 1 weekend

---

## 4️⃣ Real Certificate Authority (Private CA) 🏛️

**Status:** 🅿️ PARKED — needs deeper crypto understanding

**Why parked:**
- Part 12 crypto topics are still in progress (12.10 PKI not yet done)
- Needs real key infrastructure
- Needs a lab with multiple machines

**What we already did:**
- ✅ Signed messages with RSA (12.9)
- ✅ Verified signatures
- ✅ Saw real certificates (7.5, 8.3)
- ✅ Understood JWT signing (12.7)

**What we want to build:**
- Own root CA (self-signed)
- Own intermediate CA
- Issue certs for `localhost`, `poslab.local`, etc.
- Trust own CA on devices
- Full certificate chain

**Resume at:** After completing 12.10 (PKI)

**Estimated time:** 1–2 days

---

## 5️⃣ Health Monitor on Linux (Real Test) 📊

**Status:** 🅿️ PARKED — needs a Linux machine

**Why parked:**
- Built and tested only on Android/Termux (7.5.8 project)
- Need to test on real Linux to verify portability

**What we already did:**
- ✅ Built portable `health-monitor.sh` (7.5.8 project)
- ✅ Works on Android
- ⚠️ **Untested on Linux**

**What we want:**
- Run on a real Linux machine (laptop or VPS)
- Verify `/proc/loadavg` works
- Verify disk path is `/` not `/data`
- Add cron job (run every hour, log to file)
- Maybe add colored output
- Add to GitHub with README

**Resume at:** When you get a laptop or VPS

**Estimated time:** 1 hour

---

## 🎯 How to use this file

**When you get a laptop, VPS, or dedicated time:**
1. Read this file
2. Pick a parked project
3. Check "What we already did" — don't redo it
4. Follow the plan
5. When done → move it out of this file (or mark ✅ COMPLETE)

**When you start a new long project that needs special conditions:**
- Add it here with the same format
- "Why parked" + "What we already did" + "Resume at" + "Plan"

---

## 📅 Review schedule

**Review this file every 4 weeks** (or when you get new hardware/money).

**Keep it short.** If a parked project is older than 6 months and still no progress → consider deleting or restructuring.

---

## 📌 Related files

- `TOC.md` — active learning plan
- `PROGRESS.md` — progress tracker
- `JOURNAL.md` — daily log
- `MASTER-RULES.md` — how I learn
- `STOP-POINT.txt` — where I stopped last session
## 6️⃣ SASE & Zero Trust Deep Dive 🏢

**Status:** 🅿️ PARKED — needs dedicated enterprise research

**Why parked:**
- SASE is a massive enterprise architecture, not a single tool.
- Requires understanding Identity Providers (Okta, Azure AD), SD-WAN, and Cloud Exchanges.
- Best learned when you have a corporate network or a cloud lab to simulate.

**What we already know (from 8.11):**
- Zero Trust = "Never trust, always verify."
- SASE = Cloud-delivered security (FWaaS, ZTNA, CASB, SWG).
- Replaces the old VPN and Castle-and-Moat model.

**What we want to learn deeply:**
- How ZTNA (Zero Trust Network Access) actually replaces VPNs.
- How Cloudflare Zero Trust (free tier) can secure a local network.
- How Identity Providers (IdP) talk to SASE providers (SAML, OIDC).
- The difference between Zscaler, Palo Alto Prisma, and Cloudflare One.

**Resume at:** When building a cloud lab or when applying for a Cloud Security / Network Security role.
