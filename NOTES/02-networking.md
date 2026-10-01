## 2.1 The OSI Model

### What it is
A 7-layer model showing how data moves through a network.
Top to bottom: Application → Presentation → Session → Transport → Network → Data Link → Physical.

### Mnemonic (top → bottom)
All People Seem To Need Data Processing

### The 7 layers
7. Application  - apps (Chrome, WhatsApp)
6. Presentation - encryption/format (SSL, TLS, JSON)
5. Session      - manages connections
4. Transport    - packets delivery (TCP, UDP)
3. Network      - routing (IP addresses, routers)
2. Data Link    - local delivery (MAC, switches)
1. Physical     - actual waves/wires

### Real commands I ran
- curl -I https://google.com       -> Layer 7 (HTTP)
- openssl s_client -connect ...    -> Layer 6 (TLS certs)
- curl -v https://google.com       -> Layer 4 (TCP connection)
- traceroute google.com            -> Layer 3 (routers, path)
- ifconfig                         -> Layers 2/1 (MAC, interfaces)
- ping google.com                  -> All layers together

### Things I saw
- Google returned 301 (moved) — Layer 7
- TLS certificate chain: google -> GTS WR2 -> GlobalSign
- Traceroute: 7 hops to google, 400+ms on mobile data
- 4 interfaces: lo, rmnet1, rmnet5, wlan0
- WiFi IP: 192.168.1.114 (private)
- Mobile IP: 172.112.255.45 (public, from ISP)
- Ping TTL = 114, times 823ms then 434ms (warms up)

### My own words
OSI is a 7-layer model used to understand how data moves.
HTTP is on Layer 7. Routing is Layer 3.
