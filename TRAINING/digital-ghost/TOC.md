# Digital Ghost: Termux + Codespace Field Guide
### Table of Contents

**How to read this guide:** The four-layer model below explains *how tracking works*. Every hands-on module maps back to one of the four layers. Learn the mechanism, then build the countermeasure.

---

## The Four-Layer Mental Model

| # | Layer | What it is | Key tools | Core lesson |
|---|-------|-----------|-----------|-------------|
| 1 | **The Address Book** (DNS & Discovery) | How your device finds sites and trackers | `dig`, `tcpdump`, AdGuard Home | Trackers need DNS to resolve. Block the *name*, and their rotating IPs don't matter. Kill the name, kill the tracker. |
| 2 | **The Conversation** (What you send) | The data your device transmits after connecting | `curl -v` | HTTPS hides *content* but not *metadata* — SNI, User-Agent, IP are still exposed. |
| 3 | **The Name Tag** (Cookies & Fingerprints) | How sites recognize you on return | `curl -c`, EFF Cover Your Tracks | Cookies are explicit tags; fingerprints are implicit (fonts, timezone, screen size). Clearing cookies is not enough — randomize the fingerprint. |
| 4 | **The Shield** (Your privacy stack) | The defenses you deploy | AdGuard Home, Privacy Badger, Brave, VPN, Termux proxies, Codespace exits | Defend at *every* layer: block DNS, randomize browser, encrypt connection, rotate exit IP. |

---

## Part 0 — Foundations
- 0.1 What "ghost" actually means (threat model vs. checklist)
- 0.2 The Bore-Them Doctrine: cost asymmetry over invisibility
- 0.3 Hard limits: what unrooted Android/Termux cannot do
- 0.4 Two-machine split: Termux (local pivot) vs. Codespace (remote exit)
- 0.5 The Four-Layer Model (the map for the whole guide)

## Part 1 — The Address Book: DNS & Discovery  — Topic 1
- 1.1 How DNS resolution actually works (recursive -> authoritative)
- 1.2 `dig` in Termux: reading answer, authority, additional sections
- 1.3 `tcpdump` on Termux: watching your own DNS queries leave the device
- 1.4 AdGuard Home: self-hosted DNS sinkhole (run in Codespace, point phone at it)
- 1.5 Blocklist strategy: why blocking names beats chasing IPs
- 1.6 DoH/DoT with Quad9 / Cloudflare / Mullvad DNS — and the SNI caveat
- 1.7 Private DNS on Android: what it hides, what it leaks
- 1.8 Bridge to Part 2: DNS solved -> but TLS handshake still shouts your destination

## Part 2 — The Conversation: What You Send  — Topic 2
- 2.1 `curl -v` in Termux: reading request headers line by line
- 2.2 What HTTPS hides vs. what it leaks (SNI, User-Agent, IP, timing)
- 2.3 TLS handshake walkthrough: ClientHello, SNI, certificate
- 2.4 ECH (Encrypted Client Hello) — the real fix the DNS guides miss
- 2.5 User-Agent & header hygiene: what your browser broadcasts
- 2.6 Bridge to Part 3: headers scrubbed, but the site still recognizes *you*

## Part 3 — The Name Tag: Cookies & Fingerprints  — Topic 3
- 3.1 `curl -c` / `-b`: saving and replaying cookies by hand
- 3.2 Explicit tags: first-party vs. third-party cookies, supercookies, ETags
- 3.3 Implicit tags: EFF Cover Your Tracks — reading your own fingerprint report
- 3.4 Fingerprint surface: canvas, WebGL, fonts, timezone, screen, audio
- 3.5 Why clearing cookies fails; why randomizing beats spoofing
- 3.6 Bridge to Part 4: three attack layers known -> time to build the shield

## Part 4 — The Shield: Browser & Fingerprint Defense  — Topic 4
- 4.1 Privacy browser baseline (Brave / Librewolf) — necessary, not sufficient
- 4.2 Firefox `user.js` + `resistFingerprinting`
- 4.3 CanvasBlocker in "fake readout" mode (poisoning, not spoofing)
- 4.4 Per-persona profiles: fingerprint + IP class + cookie jar isolation
- 4.5 WebRTC leak protection + verification
- 4.6 Search engine swap: DuckDuckGo / Brave / Startpage
- 4.7 Compartmentalization rule: never log into real accounts in ghost sessions

## Part 5 — Termux: The Local Pivot
- 5.1 Termux setup & essential packages (`openssh`, `proxychains-ng`, `tor`, `privoxy`)
- 5.2 SSH dynamic forwarding: local SOCKS5 proxy (`ssh -D`)
- 5.3 SOCKS5 -> HTTP with Privoxy (Wi-Fi system proxy path)
- 5.4 Tor inside Termux: SOCKS proxy + Onion Services
- 5.5 `proxychains-ng` config (why `torsocks` is broken on Android 8+)
- 5.6 Per-app proxying: Firefox proxy settings vs. system-wide limits
- 5.7 Mobile data reality check: no system proxy
- 5.8 Native Android ghosting: MAC randomization (persistent vs. non-persistent)

## Part 6 — Codespace: The Rotating Exit
- 6.1 Why Codespace = fresh public IP per rebuild
- 6.2 `fluffy-barnacle` toolkit overview (`cs-proxy`, `cs-wg`, multi-hop)
- 6.3 `cs-proxy`: SOCKS5/HTTP exit with auto-reconnect
- 6.4 `cs-wg`: full WireGuard tunnel from Codespace
- 6.5 Tailscale exit node on Codespace (fork-and-run repo)
- 6.6 Chaining Codespaces across regions (multi-hop)
- 6.7 Heavy tooling in Codespace: nmap, nuclei, ffuf, Kali layers
- 6.8 Codespace OpSec: what GitHub sees, persistence limits, rebuild hygiene

## Part 7 — The Noise Layer (Bore-Them Doctrine in Practice)
- 7.1 Chaff traffic: decoy URL scheduling
- 7.2 DNS query flooding: making resolver logs statistically useless
- 7.3 Timing jitter: randomizing request intervals
- 7.4 Fingerprint poisoning across sessions
- 7.5 The Free IP Rotator (Codespace Churn)
- 7.5 Random (not round-robin) IP rotation
- 7.6 Feeding false positives to trackers

## Part 8 — Network-Layer Tricks (Mid-Expert Tier)
- 8.1 MTU/MSS + TCP window oddities vs. passive fingerprinting (p0f)
- 8.2 Packet padding via obfs4/meek bridges
- 8.3 Blocking tracker ASNs at the firewall (pfSense/OPNsense + pfBlockerNG)
- 8.4 ECH deep dive (echoes 2.4, now hands-on)

## Part 9 — Device & OS Hardening
- 9.1 Update hygiene & attack-surface reduction
- 9.2 Bitwarden + passkeys + hardware 2FA (YubiKey)
- 9.3 TOTP apps (Aegis / Ente Auth) vs. SMS
- 9.4 High-risk tier: Tails OS and GrapheneOS
- 9.5 VM snapshot-revert workflow

## Part 10 — OpSec: Where Ghosts Actually Die
- 10.1 Cross-contamination between personas
- 10.2 File-handling mistakes (download over Tor, open off-VPN)
- 10.3 Username / writing-style / timing correlation
- 10.4 Login patterns as deanonymizers
- 10.5 Your personal OpSec checklist

## Part 11 — Verification & Testing
- 11.1 IP / DNS / WebRTC leak test walkthrough
- 11.2 Fingerprint test sites — reading the results
- 11.3 Confirming Termux proxy carries traffic
- 11.4 Confirming Codespace exit IP rotation
- 11.5 Full-stack drill: Address Book -> Conversation -> Name Tag -> Shield

## Appendices
- A. Termux command reference (copy-paste ready)
- B. `proxychains-ng` config template
- C. Firefox `user.js` starter
- D. AdGuard Home quick-deploy (Codespace -> phone)
- E. Glossary (SNI, ECH, TUN, SOCKS5, exit node, supercookie)
- F. Reality check: what this stack does *not* protect against

---

**The one-sentence spine:**
> We use DNS to find trackers (Address Book), see what we send (Conversation), understand how they recognize us (Name Tag), and build a shield at every layer (Shield) — using Termux as the local pivot and Codespace as the rotating exit.

**Four-topic mapping:**
- Topic 1 (DNS) -> Part 1 + bits of Part 5 (AdGuard in Codespace)
- Topic 2 (Conversation) -> Part 2 + Part 8 (SNI/ECH)
- Topic 3 (Name Tag) -> Part 3 + Part 4 (fingerprint defense)
- Topic 4 (Shield) -> Parts 4-9 (the whole defensive stack)
