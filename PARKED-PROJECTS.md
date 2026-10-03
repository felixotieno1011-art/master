## Real VPN (WireGuard/OpenVPN)
- Status: PARKED — needs hardware we don't have
- Why parked:
  * Needs a real server (VPS ~$5/month)
  * Needs kernel-level TUN/TAP (blocked on Android)
  * Needs root or a real Linux machine
- What we DID do on phone:
  * Built mini_proxy.py (HTTP forwarding)
  * Built mini_tunnel.py (base64 wrapping)
  * Understood proxy vs VPN vs tunneling conceptually
- Resume at: After Topic 7.1 (Linux Server Basics)
- Future plan:
  * Rent a VPS (DigitalOcean $5/month)
  * Set up WireGuard server + client
  * Connect from phone
