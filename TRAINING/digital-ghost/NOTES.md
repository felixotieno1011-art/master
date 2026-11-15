# Digital Ghost — Notes

Written **only after** a topic is finished. Distilled memory: one-liners,
gotchas, "remember we did this." No lesson content here — lessons live in
`00-…md` through `11-…md`.

---

## 0. Foundations
<!-- notes go here after 0.x is done -->

## 1. Address Book (DNS)
<!-- notes go here after 1.x is done -->

## 2. Conversation
## 3. Name Tag
## 4. Shield
## 5. Termux
## 6. Codespace
## 7. Noise
## 8. Network
## 9. Device
## 10. OpSec
## 11. Verification

### 0.1 — Done
- Ghost = unprofitable to track, not invisible.
- Threat model: ISP + advertisers + opportunistic hackers. Not a targeted human.
- Baseline captured: IPv4 41.81.114.42 / Safaricom / Nairobi; plus an IPv6 from ifconfig.me.
- **Gotcha:** you have TWO public identities (IPv4 + IPv6). Privacy that ignores IPv6 is half-done.

### 0.2 — Done
- Ghost = flip the equation: raise their tracking cost above their payoff.
- Two levers: lower payoff (block ads/trackers) + raise cost (noise, rotation, fingerprint poisoning).
- Judge every tool by: does it raise their cost or lower your payoff? If neither → theater.
- **Gotcha:** friction isn't free for you either. Tor = install + keep running. Pay only where it flips the equation.
- **Failure mode matters:** a tool that fails closed (like the proxy attempt) is safe; one that leaks on failure is worse than nothing.

### 1.1 — Done
- DNS asks "where is this site?" in PLAINTEXT, before HTTPS starts. ISP reads every domain.
- Ran `dig google.com` live. Result: `;; SERVER: 8.8.8.8` — my resolver is Google DNS, not Safaricom's.
- **Gotcha:** changing resolver (8.8.8.8) changes who ANSWERS, not who WATCHES. Safaricom still sees the query cross its network.
- Google returned two different IPs in one session (142.251.140.110 vs 142.251.47.14). IPs are unstable; names are stable → block the name.
- Real fix = encrypt the lookup (DoH/DoT) or tunnel it. That's 1.2.

### 1.1b — CGNAT reality check
- CGNAT = many users share one public IP.
- **For websites:** your IP becomes a blurry crowd. They can't tell which user you are → helps you.
- **For Safaricom:** no help at all. They keep logs mapping internal IP+port → your device. Still see your DNS + flows.
- CGNAT side-effects that help you: guilt-by-association makes sites afraid to block IPs; rate limits misfire; IP geolocation gets fuzzy.
- **Their counter:** sites stop trusting IP and lean harder on **fingerprints + behavior** (Topic 3). So CGNAT is free camouflage, not a shield.
- **Rule:** hiding from outsiders ≠ hiding from your carrier. Defend against the carrier (encrypt DNS/traffic), don't rely on CGNAT.

### 1.2 — DNS leak test (ECS)
- `dig +short txt o-o.myaddr.l.google.com @8.8.8.8` returned an **`edns0-client-subnet 41.81.114.0/24`** line.
  → Google forwards a slice of my IP to upstream resolvers. My neighborhood leaks even through Google DNS.
- Same query @1.1.1.1 returned **no ECS line** — Cloudflare doesn't forward my subnet.
- **Lesson:** "use 8.8.8.8" is not automatically private. Providers differ in behavior, not brand.
- ECS = EDNS Client Subnet: a resolver volunteering your subnet to speed up CDN answers. Speed for them, leak for you.
- Test rule: don't trust the brand; run the query and read the ECS line.
