# Runbook: Termux SOCKS Proxy (`ssh -D` + Privoxy)

**Layer:** Part 5.2-5.3 (local pivot) -> feeds Part 4 (Shield)
**Goal:** Route phone browser traffic through a remote host without root.
**Limits:** Wi-Fi only (no system proxy on mobile data). Per-app, not whole-device.

---

## 0. Prereqs
- Termux (F-Droid build, not Play Store)
- An SSH-accessible remote host (VPS, Codespace SSH, home server)
- Phone on Wi-Fi

## 1. Install packages
```bash
pkg update && pkg upgrade -y
pkg install openssh privoxy curl -y
