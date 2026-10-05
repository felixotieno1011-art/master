/## 2.1 The OSI Model

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
## 2.2 TCP/IP Model

### The 4 layers (top → bottom)
4. Application
3. Transport
2. Internet
1. Network Access

### Mnemonic
All Trucks In Nairobi

### OSI vs TCP/IP
- OSI = 7 layers, teaching tool only
- TCP/IP = 4 layers, what the internet actually uses
- OSI merges into TCP/IP:
  * App + Presentation + Session → Application
  * Transport → Transport
  * Network → Internet
  * Data Link + Physical → Network Access

### TCP vs UDP
- TCP = careful, reliable, ordered (downloading files, websites)
- UDP = fast, no retransmit, no order (live streams, games, DNS)

### TCP 3-way handshake
1. SYN     -> "Hey, you there?"
2. SYN-ACK -> "Yeah, and you?"
3. ACK     -> "Cool, let's talk"

### Real commands I ran
- curl -v https://google.com       -> saw TCP + TLS + HTTP/2 in action
- dig +stats google.com            -> DNS uses UDP (udp:512), 6 IPs
- netstat -t                      -> shows active TCP connections

### My own words
- TCP/IP has 4 layers
- Live streams use UDP (speed not reliability)
- Handshake is 3 steps: SYN, SYN-ACK, ACK
- Mobile data hides your IP behind the ISP
## 2.3 IP Addressing

### IPv4
- 4 numbers (0-255 each)
- 32 bits total (4 × 8 bits)
- ~4.3 billion addresses total
- Ran out in 2011

### IPv6
- 8 groups of hex digits
- 128 bits total
- 340 undecillion addresses (basically unlimited)

### Private IP ranges (memorize these)
- 10.x.x.x.x        (big companies)
- 172.16-31.x.x     (medium networks)
- 192.168.x.x       (home WiFi) - mine: 192.168.1.114
- 127.x.x.x         (localhost)

### Subnetting
- /24 = 24 network bits, 8 device bits → 254 devices
- /26 = 26 network bits, 6 device bits → 62 devices
- /30 = 30 network bits, 2 device bits → 2 devices (point-to-point)
- Slicing a big network into smaller ones

### My WiFi findings
- WiFi IP: 192.168.1.114
- Router: 192.168.1.1
- Devices on WiFi: router, my phone, 192.168.1.189 (unknown)
- Router ports: 53 (DNS), 80 (HTTP), 443 (HTTPS)
- Latency to router: 8ms
- Latency to internet: 40ms+
- WiFi speed (tested): ~0.5 Mbps (slow!)
- Mobile data IPs: 100.x.x.x (ISP CGNAT)

### Commands I ran
- ifconfig                          -> see interfaces
- nmap -sn 192.168.1.0/24          -> scan all devices
- nmap -F 192.168.1.1              -> scan router ports
- traceroute 8.8.8.8               -> path to internet
- ping 192.168.1.1                 -> test router
- Built subnet-calc.py (Python)    -> my own subnet calculator
## 2.4 Routers, Switches, Hubs

### The 3 devices
- ROUTER:  Layer 3, connects DIFFERENT networks, uses IP addresses
- SWITCH:  Layer 2, connects SAME network, uses MAC addresses
- HUB:     Layer 1, sends to EVERYONE (dumb), extinct

### Real-world analogy
- Hub = megaphone (shouts to everyone)
- Switch = local posta office (delivers locally)
- Router = main post office (routes between cities)

### My home "router" has 5-7 jobs
- Router (connects to internet)
- Switch (connects my devices)
- WiFi Access Point (broadcasts WiFi)
- Firewall (basic protection)
- DHCP server (assigns IPs)
- DNS cache (speeds up lookups)
- Modem (sometimes)

### Key distinction
- Switch = stays INSIDE the network
- Router = connects OUTSIDE to other networks

### Commands I ran
- ip route / netstat -rn     -> routing table (blocked on Android)
- ip neigh / arp -a          -> ARP table (blocked on Android)
- traceroute -m 3 8.8.8.8    -> showed router as hop 1
- nmap -sn 192.168.1.0/24    -> 3 devices on WiFi
- curl -I http://192.168.1.1 -> 501 Not Implemented (no HEAD support)
- curl -s http://192.168.1.1 -> encrypted garbage (HTTPS only)

### Discovery
- My router prefers HTTPS (port 443) for admin
- It returned encrypted bytes on HTTP (port 80)
- HTTP response was garbled = encrypted TLS data
## 2.5 Firewalls & Network Security

### What is a firewall
A filter between two networks that decides which traffic is allowed or blocked.

### 3 types
1. Packet Filter  - checks each packet alone (IP, port)
2. Stateful       - remembers connections, smarter
3. Application    - inspects apps (deep packet inspection)
4. Next-Gen (NGFW) - everything + AI

### Ports (important)
- 22  = SSH (remote terminal)
- 53  = DNS
- 80  = HTTP
- 443 = HTTPS
- 3306, 5432 = databases
- 8000, 3000 = custom apps

### Firewall actions
- ALLOW = let through
- DENY  = reject (attacker knows)
- DROP  = silently ignore (attacker doesn't know)

### My router's firewall behavior
- Blocks all INBOUND by default
- Allows all OUTBOUND
- Remembers connections (stateful)
- This is why you can browse freely but hackers can't reach you

### Commands I ran
- iptables -L                     -> blocked by Android (no root)
- curl http://google.com:22       -> timed out (DROP, not REJECT)
- bash /dev/tcp/google.com/PORT   -> probed Google's ports
- Built mini-firewall.py           -> simulated firewall rules

### Google's firewall probe results
- Port 80:  OPEN (public)
- Port 443: OPEN (public)
- Port 22:  BLOCKED (SSH not exposed)
- Port 3306: BLOCKED (MySQL not exposed)
- Port 8000: BLOCKED (custom not exposed)

### Key insight
DROP is more secure than REJECT because the attacker learns nothing.
## 2.6 DNS, DHCP, NAT

### DNS (Domain Name System)
- Translates names to IPs
- google.com → 142.250.x.x
- Command: dig google.com +short
- Caches answers (TTL = how long to remember)

### DNS Hierarchy
- Root servers (13 worldwide, named a-m.root-servers.net)
- TLD servers (.com, .org, .ke)
- Authoritative servers (Google's own)
- Resolver caches queries

### DHCP (Dynamic Host Configuration Protocol)
- Gives your device an IP automatically
- DORA process:
  * Discover: "Anyone got an IP for me?"
  * Offer: "I'll give you 192.168.1.114"
  * Request: "Yes please"
  * Ack: "Confirmed"
- Without DHCP, you'd type IP manually

### NAT (Network Address Translation)
- Lets many devices share one public IP
- Your local IP: 192.168.1.114
- Your public IP: 102.0.100.84 (Airtel) / 41.90.193.104 (Safaricom)
- Carrier-Grade NAT (CGNAT): mobile ISP uses this, hides many users behind one IP

### Interesting findings
- Different DNS servers return different Google IPs (GeoDNS)
- My phone on mobile data: 41.90.193.104 (Safaricom)
- DNS trace showed root servers + .com servers + Google servers
- DNSSEC signatures present (RRSIG)

### Commands
- nslookup google.com       -> basic lookup
- dig google.com +short     -> clean answer
- dig @8.8.8.8 google.com   -> ask specific DNS
- dig google.com +trace     -> follow full DNS path
- curl https://ipinfo.io/ip -> my public IP
- ifconfig wlan0            -> local WiFi IP
### My own words for 2.6
- DNS    = phonebook (name → IP)
- DHCP   = automatically assigns IP addresses (via router)
- NAT    = translates private IPs to public IP
- Why NAT: protects our specific IP + conserves IP addresses
## 2.7 VPNs, Proxies & Tunneling

### The 3 concepts (my words)
- PROXY   = replaces my IP for ONE app/site
- VPN     = replaces my IP AND encrypts my data (for ALL apps)
- TUNNEL  = wraps my message inside another envelope

### Real-life analogies
- Proxy  = friend goes to buy shoes in my place
- VPN    = bodyguard walks with me everywhere, covers my face
- Tunnel = putting a letter inside another envelope

### The difference
| Feature        | Proxy      | VPN        | Tunnel     |
|----------------|------------|------------|------------|
| Hides IP       | ✅ (1 site)| ✅ (all)   | ❌         |
| Encrypts       | ❌         | ✅         | ✅         |
| Scope          | 1 app      | all apps   | any data   |
| Analogy        | friend     | bodyguard  | envelope   |

### What I built
- mini_proxy.py  — forwards HTTP requests (middleman)
- mini_tunnel.py — wraps messages in base64 (envelope)

### Real tools
- Proxies:   Squid, mitmproxy, Charles
- VPNs:      WireGuard, OpenVPN, NordVPN
- Tunnels:   SSH tunnel, Cloudflare Tunnel, ngrok

### Commands I ran
- curl -x http://localhost:8888 http://example.com   -> proxy
- python mini_proxy.py                                -> ran proxy
- python mini_tunnel.py server / client "msg"         -> tunnel
- base64 file.txt                                     -> wrapped data
- base64 -d < <(base64 file.txt)                     -> unwrapped data
## 2.8 Wireless Networking

### WiFi uses radio waves
- 2.4 GHz = slower, longer range, more interference
- 5 GHz   = faster, shorter range, cleaner
- 6 GHz   = fastest, shortest, newest (WiFi 6E)

### Channels
- WiFi networks broadcast on channels
- 2.4 GHz has 14 channels, only 1, 6, 11 don't overlap
- 5 GHz has many more channels → cleaner
- If two networks use the same channel = interference

### Security standards
- WEP   = broken, don't use
- WPA   = weak, old
- WPA2  = good, current standard (AES encryption)
- WPA3  = best, newest, stronger handshake

### Why WiFi gets slow
- Congestion: many devices share one channel, take turns
- Interference: microwave, Bluetooth, walls
- Distance from router = weaker signal
- Same channel as neighbors = waiting

### Signal strength (RSSI)
- -30 dBm = perfect
- -50 dBm = excellent
- -60 dBm = good
- -70 dBm = fair
- -80 dBm = poor
- -90 dBm = unusable
### My own words for 2.8
- 2.4 GHz = slower, longer range
- 5 GHz   = faster, shorter range
- WiFi slows when devices CONGEST the channel
### 2.9 — Final understanding
- ping     = reachability + latency + packet loss
- mtr      = continuous traceroute + ping
- dig      = DNS resolution details
- nmap     = port scanning + host discovery
- curl     = HTTP test + response codes
- traceroute = one-shot path

### Diagnosed github.com today
- DNS: 20.87.245.0 ✅ (Azure-hosted)
- Ping: 105 ms, 0% loss ✅
- HTTP: 200 OK ✅
- Edge server: southafricanorth
- Same redirect pattern as google (301)
g## 2.11 Network Protocols

### The essential protocols
- HTTP/HTTPS  : ports 80/443  - websites
- FTP         : ports 20/21   - file transfer (unencrypted, old)
- SFTP        : over SSH      - file transfer (encrypted, modern)
- SSH         : port 22       - remote control of servers (encrypted)
- SMTP        : ports 25/587/465 - send email
- IMAP        : port 143      - receive email (modern)
- POP3        : port 110      - receive email (old)
- Telnet      : port 23       - old remote shell (unencrypted, dead)
- SNMP        : port 161      - network monitoring

### Port cheat sheet (memorize these)
22  = SSH
23  = Telnet
25  = SMTP
53  = DNS
80  = HTTP
110 = POP3
143 = IMAP
443 = HTTPS
587 = SMTP submission

### Why SSH matters
- It's THE dev tool for controlling servers
- Used every single day
- Encrypted, secure
- Can also: transfer files (SCP/SFTP), tunnel traffic

### Real tests I ran
- github.com:22   SSH     ✅ Open (but auth denied without key)
- github.com:80   HTTP    ✅ Open
- github.com:443  HTTPS   ✅ Open
- smtp.gmail.com:25 SMTP  ✅ Open
- ftp.gnu.org:21  FTP     ✅ Open

### SSH test result
- Connected to GitHub's SSH on port 22 ✅
- Server reset connection because no SSH key configured
- This is expected behavior
- GitHub edge region: southafricanorth (same server as HTTP)
### My own words for 2.11
- SSH  = remote Linux terminal access from far away (port 22)
- FTP  = old file transfer (unencrypted)
- SFTP = modern file transfer over SSH (encrypted)
- SMTP = sends emails
- The most important dev protocol: SSH
## 2.12 Load Balancing

### What it does
Sits in front of servers, distributes incoming requests across them.

### The 4 algorithms
1. Round Robin       - Server 1 → 2 → 3 → 1 → 2 → 3
2. Least Connections - Server with fewest active connections
3. IP Hash           - Same user → same server (sticky sessions)
4. Weighted          - Bigger servers get more traffic

### Why it matters
- No single server gets overwhelmed
- If a server dies, others keep working (failover)
- Can scale to millions of users

### Health checks
- LB periodically tests each server ("you alive?")
- If server fails → marked DOWN → traffic rerouted
- When recovered → added back automatically

### Layer 4 vs Layer 7
- Layer 4: Transport (TCP/UDP), fast, blind
- Layer 7: Application (HTTP), slower, smart (can route by URL)

### Real tools
- Nginx, HAProxy, AWS ELB/ALB/NLB, Azure LB, GCP LB

### I built
- load_balancer.py — simulation with all 4 algorithms + failover
- mini_lb.py       — real HTTP load balancer with round-robin
- Saw backend-A → B → C → A → B → C cycling perfectly
### My own words for 2.12
- Load balancer = decides which server gets each request
- Algorithms: Round Robin, Least Connections, IP Hash, Weighted
- Layer 4 = TCP/UDP (blind), Layer 7 = HTTP (smart)
- Health check = "are you alive?" test
- Why: scale to millions + survive server failures
### My own words for 2.13
- IDS detects, IPS detects + prevents
- Signature = known patterns
- Anomaly = unusual behavior
- My mini-IDS: catches port scans with a 10s window
- Slow scans evade (stayed under threshold)
- Real security uses firewall + IDS + IPS together
