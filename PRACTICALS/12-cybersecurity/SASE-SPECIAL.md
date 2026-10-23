# 🏢 SASE & Zero Trust — Special Deep Dive

## The Core Problem
The "Castle and Moat" model is dead. If a hacker steals an employee's password, the firewall thinks they are an employee. The hacker is now "inside" and trusted.

## The Zero Trust Solution
"Never trust, always verify."
- **Verify Explicitly:** Check identity, device health, and location on every request.
- **Least Privilege:** Give the minimum access needed (JIT/JEA).
- **Assume Breach:** Design as if the attacker is already inside.

## What is SASE?
SASE (Secure Access Service Edge) is the cloud service that enforces Zero Trust.
Instead of routing traffic back to a company firewall (VPN), traffic goes to the nearest Cloud Provider (like Cloudflare or Zscaler).

### The 5 Pillars of SASE:
1. **FWaaS** — Firewall as a Service (in the cloud).
2. **SWG** — Secure Web Gateway (blocks bad websites/malware).
3. **CASB** — Cloud Access Security Broker (secures SaaS apps).
4. **ZTNA** — Zero Trust Network Access (replaces VPN).
5. **SD-WAN** — Smart routing for branch offices.

## The Money (Why it's big)
- Companies don't build SASE; they rent it (like Netflix).
- Providers (Cloudflare, Zscaler, Palo Alto) charge $30-$100 per user/month.
- It saves companies from buying 5 separate security tools.
- Engineers who know SASE make $150k+ because it's complex.

## How to build a lab (Future)
- Sign up for **Cloudflare Zero Trust** (Free tier for 50 users).
- Install the WARP client on a phone.
- Connect to a local SSH server (like Termux) through Cloudflare.
- Prove that the server has no open ports to the internet, yet you can access it securely.
