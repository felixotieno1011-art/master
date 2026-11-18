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

### 3.2 — Fingerprinting (The Digital Tattoo)
- Ran EFF Cover Your Tracks in Chrome (Incognito).
- **Result:** "Unique among 374,236 tested." Fingerprint is fully exposed.
- **Blocking:** Ads: No. Invisible Trackers: No.
- **The Leaks:** Screen size (410x912), Timezone (Africa/Nairobi), Fonts, WebGL (GPU hash), AudioContext (audio hardware math).
- **The Trap:** Incognito mode hides history from *me*, not from *trackers*. It does nothing against fingerprinting.
- **Canvas:** Chrome randomized it per-domain, but WebGL and Audio still give a unique signature.

### 3.3 — Poisoning the Tattoo (Fingerprint Defenses)
- You can't delete your hardware fingerprint. You have to **spoof** it.
- Pulled Firefox's `arkenfox/user.js` config to see the raw settings.
- The nuclear option: `user_pref("privacy.resistFingerprinting", true);`
- **What RFP does:** Lies about screen size (1000x1000), timezone (UTC), blocks Canvas/WebGL, restricts fonts.
- **The Trade-off:** Blending in breaks some websites. That's the price of the Shield.
- **Action for Android:** Use Brave (built-in randomizer) or Firefox (with RFP enabled).

### 3.3 — Fingerprint Defenses (Part 3 Wrap)
- You can't change hardware. You have to spoof it.
- Firefox `user.js` uses `privacy.resistFingerprinting` to lie about screen size, timezone, and canvas.
- **Tomorrow's Practical:** Install Brave (Wi-Fi), test `coveryourtracks.eff.org` in Brave vs. Phoenix. Expect Brave to randomize the fingerprint and block trackers; expect Phoenix to leak like a sieve.

### 3.4 — Browser Testing (Tomorrow's Homework)
- **Chrome (Incognito):** Unique fingerprint (1 in 374k). Zero protection.
- **Opera Mini:** Uses a proxy (hides IP), but scores "No" on EFF protection. Limited JS breaks tests.
- **Phoenix Browser:** Will likely score "Unique" and "No". Known to harvest data. (Good for a bad-example test).
- **Brave Browser:** The fix. Randomizes Canvas/WebGL, blocks trackers by default.
- **Action:** Install Brave tomorrow on Wi-Fi. Run EFF test on Phoenix (bad) vs. Brave (good). Compare.

### Pre-Download Checklist (Wi-Fi)
- Termux: installed openssh, privoxy, tor, proxychains-ng, autossh, termux-api.
- Codespace: pre-installed fluffy-barnacle (pip) for future cs-proxy/cs-wg use.
- Browser: Brave download pending (tomorrow).

### 4.1 — The Shield: Browser Baseline (Brave)
- Tested Brave on EFF Cover Your Tracks.
- **Result:** "Strong protection against Web tracking."
- **Ads/Trackers:** Blocked.
- **Fingerprint:** Randomized (Canvas & WebGL are fed fake data per domain).
- **The Leak:** Timezone (Africa/Nairobi), Screen Size (410x912), and Cookies remain. Brave cannot fake these without breaking websites.
- **Verdict:** Brave is the baseline Shield. It makes the tracker's job too expensive.

### 4.2 — Firefox Hardening (The Paranoia Route)
- Bypassed Android restrictions using `chrome://geckoview/content/config.xhtml`.
- Enabled `privacy.resistFingerprinting = true`.
- **The Lies Firefox tells:**
  - Timezone: Says "Atlantic/Reykjavik" (Iceland) instead of Nairobi.
  - Screen: Says 1095x2067 instead of my actual phone screen.
  - User-Agent: Says it's a Linux Desktop, not an Android phone.
  - Canvas/WebGL: Randomized.
- **The Result:** EFF still says "Unique" because a "Linux Desktop with Touch Support" is rare. But ad trackers get poisoned with useless data.
- **Side Effect:** Screen scrolling might feel laggy (locked to 60Hz).

### 5.0 — Termux Tor Proxy (The Local Pivot) — DONE
- Built a full HTTP-to-SOCKS5 tunnel on an unrooted Android.
- **Steps:**
  1. Started Tor: `tor &` (SOCKS listener on 127.0.0.1:9050).
  2. Wrote Privoxy config: listen on 8118, forward-socks5 to 9050.
  3. Started Privoxy: `privoxy $PREFIX/etc/privoxy/config &`.
  4. Set Android Wi-Fi Proxy to 127.0.0.1:8118.
- **Result:** Browser now routes through Tor. `check.torproject.org` confirms IP is a Tor exit node.
- **Gotchas:** 
  - Apps that ignore system proxies (like some social media apps) will still leak.
  - Tor is slow.
  - Mobile Data ignores this proxy entirely.

### 5.2 — The Seal is Complete
- Disabled WebRTC in browser settings.
- Re-tested ipleak.net.
- **Result:** Zero leaks. 
  - IPv4/IPv6: Germany (Tor exit).
  - WebRTC: Sealed (RTCPeerConnection not available).
  - DNS: 0 servers detected (handled by Tor).
- **Conclusion:** The Termux Tor Proxy + Browser Hardening is a fully functional ghost tunnel. 

### 7.1 — Chaff Traffic (The Noise Layer)
- Wrote `chaff.sh` in Termux.
- Uses a while loop, an array of benign sites (Wikipedia, BBC, etc.), and random sleep timers.
- **The point:** If a tracker sees 50 requests, they can't tell which 5 are your real browsing habits and which 45 are noise.
- **How to run it in background:** `./chaff.sh &` (Use `pkill chaff.sh` to stop it).

### 7.5 — The Free IP Rotator (Codespace Churn)
- **The Movie Trick:** IPs jumping across the world.
- **The Reality:** Paid proxy pools do this per-request. We do it per-session.
- **The Ghost Setup:** Delete Codespace -> Create new one in a different region -> Re-run `gh codespace ssh -D 1080` -> New IP.
- **Lesson:** You don't need a paid VPN to teleport. GitHub is your free teleporter.

### 7.2 — DNS Flooding (Poisoning the Phonebook)
- Wrote `dnsflood.sh` in Termux.
- Uses a loop to generate random fake domains (`fake-$RANDOM-$RANDOM.com`) and queries them using `dig`.
- **The point:** ISPs log every DNS request. By flooding the log with fake domains, the real browsing history is buried in noise.
- **Result:** Tracker sees 50 fake sites and 3 real ones. It becomes impossible to build an accurate profile.

### Session Wrap-Up (Nov 16)
- **Part 7:** Built Chaff script (fake web traffic) and DNS Flood script (fake lookups) to poison ISP logs.
- **Part 8 (Attempted):** Tried setting up Tor with obfs4 bridges inside Codespace. Hit a wall with the secret bridge lines. *Left for tomorrow.*
- **Realization:** You already built the core ghost tunnel (Termux + Codespace + Tor). The advanced stuff is just extra armor.

### 8.2 — MAC Randomization (Hardware Barcode)
- Wi-Fi routers log your device's MAC address to track physical presence.
- **The Fix:** Settings > Wi-Fi > Gear icon > Privacy/MAC type.
- Set to "Randomized MAC" (or "Non-persistent randomized MAC" on Android 12+).
- This changes your hardware ID every time you connect to a public network.

### 9.1 — Device Hardening (Passwords & 2FA)
- **The Vulnerability:** Reusing passwords (even just 2) means one breach compromises everything.
- **The Fix 1 (Passwords):** Install Bitwarden. Use it to generate unique 16-character passwords for every site.
- **The Fix 2 (2FA):** Never use SMS. Install Aegis Authenticator. Link it to Gmail, Bank, and Social Media.
- **The Goal:** Become un-profitable to hack. 

### 10.1 — OpSec (Where Ghosts Die)
- **The Rule:** Software can't save you from human error.
- **Cross-Contamination:** Logging into a real account (like Amazon or Facebook) while using a proxy/Tor instantly links your real name to the ghost IP. Game over.
- **The Flaw:** Mixing real identity (address, email) with ghost identity (fake IP).
- **The Fix:** Compartmentalize. Ghost mode = no personal logins. Real mode = turn off the proxy.

### 11.1 — Full-Stack Verification (The Drill)
- **Baseline (Tunnel Off):** Real ISP IP (105.166.5.38), DNS leaked `edns0-client-subnet`.
- **Ghost Mode (Tunnel On):** 
  - Started Codespace: `gh codespace ssh -c psychic-space-acorn-77rqqx495qxx3x6rv -- -D 1080`
  - Started Privoxy pointing to 1080.
  - **Result:** IP is now `4.240.39.192` (Microsoft Azure).
- **The Checklist:** Always verify your IP and DNS before doing sensitive browsing. 

### Bonus — Proxychains-ng (The Whip)
- **Problem:** Most CLI tools (nmap, git, ssh) ignore system proxies and leak your IP.
- **The Fix:** `proxychains4` intercepts the network calls and forces them through a proxy.
- **Config:** Edited `$PREFIX/etc/proxychains.conf` to set `socks5 127.0.0.1 1080`.
- **Test:** `proxychains4 curl -s https://ifconfig.me` returned the Microsoft IP (`4.240.39.192`).
- **Lesson:** Any tool prefixed with `proxychains4` is now forced through the Codespace tunnel.
