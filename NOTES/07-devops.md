### 7.1 Linux Server Basics — Phase B DONE ✅

Explored my own phone's Linux system with real commands.

### Core concepts
- Linux = free, open-source OS. Kernel by Linus Torvalds, 1991.
- Runs most servers, all Android phones, all top 500 supercomputers
- The layers: Hardware → Kernel → Shell → Programs → Daemons
- Kernel = core, talks to hardware through drivers
- Shell = where you type commands (bash in Termux)
- Daemon = background service (sshd, cron, nginx)
- Filesystem structure: / /home /etc /var /tmp /usr

### Real commands I ran
- whoami        → u0_a333 (my Linux user)
- uname -a      → Linux 4.19.191 aarch64 Android
- ls -la        → list files with permissions
- df -h         → disk usage
- df -h /data   → real writable space
- ps aux | head → running processes
- uptime        → how long running + load

### Things I saw
- Kernel: Linux 4.19.191, chip: aarch64 (ARM 64-bit)
- Root / is 100% full (system partition, read-only)
- /data has 51G total, 44G used, 7.1G free (87% full)
- sshd is running → I can SSH into my own phone
- ps shows: bash, sshd, ps, head

### My own words (locked in)
- My phone IS a Linux server. Termux runs in the Linux kernel.
- aarch64 = CPU type (ARM, 64-bit). Affects what software installs.
- / = system, read-only. /data = my writable space.
- Kernel sits between hardware and programs — not "in" hardware.
- I'm learning to run the thing I'm learning on.
### 7.5 Domain, DNS, HTTPS — Phase B DONE ✅

Explored DNS, TLS certificates, HTTP vs HTTPS on real sites.

### Core concepts
- Domain = the name you own (rented yearly from a registrar)
- DNS = the phonebook. Maps domain → IP.
  Record types: A (IP), CNAME (alias), MX (mail), TXT (verify), NS (nameservers)
- HTTPS = HTTP wrapped in TLS encryption
- TLS certificate = ID card for the server. Signed by a Certificate Authority.
  Let's Encrypt = free.
- CDN = caches content globally (Cloudflare, etc.)

### Real commands I ran
- nslookup google.com         → name to IP
- nslookup -type=A google.com 8.8.8.8  → multiple IPs
- openssl s_client ...        → read the certificate
- curl -I http://example.com  → port 80, no encryption
- curl -I https://example.com → port 443, TLS encrypted

### Things I saw
- Google returns MANY IPs (192.178.204.139, .113, .101...), rotating each lookup
- Non-authoritative answer = cached, not source of truth
- Google's cert: subject=*.google.com, issuer=Google Trust Services
- Cert valid 90 days (Sep 18 → Dec 11 2026)
- HTTP/1.1 vs HTTP/2 (HTTPS gets HTTP/2)
- Both example.com responses served by Cloudflare CDN

### My own words (locked in)
- DNS maps name → IP, returns many IPs for load balancing
- Certificate shows: what it covers (CN), who signed it (issuer), valid dates
- Wildcard (*) covers all subdomains
- HTTP/1.1 = old. HTTP/2 = modern, comes with HTTPS.
- To let the world reach my app: host it publicly, buy a domain,
  point DNS at the server, get an HTTPS cert.
- The S in HTTPS = TLS encryption on top of HTTP
