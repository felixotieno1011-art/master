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

### 1.2b — Tool failure note
- `dnsleaktest.com` couldn't open in browser (likely site-side DNS/EDNS issues, common with certain ISP resolvers).
- **Lesson:** leak-testing tools themselves can fail. Always have 2-3 alternatives (browserleaks.com/dns, ipleak.net, ipcheck.ing).
- The `dig` ECS result from 1.2 is already solid evidence; browser test is confirmation, not the only proof.

### 1.2c — Browser Leak Test (ipleak.net) — Evidence
- **Dual Identity:** Site sees BOTH my IPv4 (196.104.0.187) and IPv6 (2c0f:fe38...). Both Safaricom.
- **CGNAT confirmed:** WebRTC exposed private IP `10.45.253.240`. Carrier knows exactly which internal IP I am.
- **WebRTC Leak:** WebRTC grabbed my real IPv6 even without a proxy. (Must disable in Part 4).
- **Network behavior:** Browser defaulted to IPv6. IPv4 fallback timed out (CGNAT overload).
- **Conclusion:** My baseline is fully exposed. Time to build the Shield.

### 2.1 — Done (The Conversation)
- Used `curl -v https://example.com` to see the raw HTTP/2 headers.
- **Headers sent:** `Host`, `User-Agent: curl/8.22.0`, `Accept: */*`.
- **The Leak:** The connection line showed my real IPv6 (`2c0f:...`). The server knows exactly who and where I am.
- **Lesson:** HTTPS encrypts the body, but `Host` and `User-Agent` are plaintext. Browsers send a massive, unique User-Agent string. Tools like `curl` send a tiny one.
- **Next:** How SNI leaks the domain name *even before* the HTTP request is sent.

### 2.2 — SNI (Server Name Indication) — PROVED
- `tcpdump` failed due to Android CAP_NET_RAW restrictions.
- Pivoted to `openssl s_client -connect neverssl.com:443 -servername neverssl.com`.
- **Proof:** The server returned `subject=CN=neverssl.com`, issued by Amazon.
- **The Leak:** The `-servername` flag is sent in PLAINTEXT during the TLS handshake. Without it, shared servers don't know which cert to give.
- **Real-world impact:** Even with HTTPS, the ISP sees the exact domain (e.g., health site, bank) in the SNI field.

### 2.3 — ECH (Encrypted Client Hello)
- Tested via Cloudflare trace (`crypto.cloudflare.com/cdn-cgi/trace`).
- Result: **`sni=encrypted`**. My browser successfully negotiated ECH.
- **What ECH hides:** The domain name in the TLS handshake. Safaricom can no longer see *what* site I'm visiting (if it supports ECH).
- **What ECH DOES NOT hide:** 
  - My IP (`ip=2c0f:...`, `loc=KE`).
  - My User-Agent (`uag=Mozilla/5.0...`).
- **The Catch:** ECH is opt-in on the server side. If a site doesn't support it, it falls back to plaintext SNI.
- **Part 2 Conclusion:** HTTPS hides the content, SNI leaks the domain, ECH fixes SNI. But IP and User-Agent still leak.

### 3.1 — Cookies (The VIP Wristband)
- Cookies are state. They are how a stateless web remembers you.
- Ran `curl -c cookies.txt https://httpbin.org/cookies/set?ghost=true`.
- `set-cookie: ghost=true; Secure; Path=/` — server sets the wristband.
- Stored locally in a Netscape Cookie File format (legacy, but universal).
- **First-party cookies:** Fine (keep you logged in).
- **Third-party cookies:** Tracking. Ad networks drop them to follow you across different sites.
- **Gotcha:** Clearing cookies isn't enough. If you come back, they give you a *new* cookie, but they match it to your old profile using a **fingerprint** (Next lesson).

### 3.1b — Real Cookie Evidence (Reddit)
- Command: `curl -v -c real_cookies.txt https://www.reddit.com`
- Result: `set-cookie: edgebucket=sibA6xFzwruQ0pmtUD; Domain=reddit.com; Max-Age=63071999; Path=/; secure`
- **The Math:** `Max-Age=63071999` seconds = **2 years**. 
- **The Domain:** `.reddit.com` (leading dot) means it's shared across all Reddit subdomains.
- **Lesson:** Real cookies are long-lived IDs. They persist long after you close the browser.
