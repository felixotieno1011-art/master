# 📘 Part 7 — DevOps & Deployment

Notes for every topic in Part 7. One section per topic, in TOC order.

---

## 7.1 Linux Server Basics — Phase B DONE ✅

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

---

## 7.3 Process Management — Phase B DONE ✅

Ran ps, started background jobs, killed them, learned signals.

### Core concepts
- Process = a running program. Every process has a PID.
- PID = unique ID number. Job number (%1) = shell-local label.
- Daemon = background process, no terminal, survives.
- Foreground process dies when terminal closes (SIGHUP).
- Process states: R=running, S=sleeping, D=uninterruptible, T=stopped, Z=zombie
- kill PID = SIGTERM = polite "please stop, clean up"
- kill -9 PID = SIGKILL = force, cannot be ignored
- Always try SIGTERM first, SIGKILL only if it won't stop.

### Signals I know
- SIGINT (2)  = Ctrl+C
- SIGTERM (15) = polite kill
- SIGKILL (9)  = force kill
- SIGHUP (1)   = terminal closed
- SIGSTOP (19) = pause
- SIGCONT (18) = resume

### Real commands I ran
- ps aux | head -5       → list processes
- ps aux | grep -c "."   → count processes
- sleep 300 &            → run in background
- jobs / jobs -l         → list background jobs
- kill %1                → kill by job number

### Things I saw
- Termux shows only ~5 processes (Android sandbox)
- A real Linux server shows 100-300 processes
- sleep 300 & gave [1] 25274 → job number + PID
- kill %1 → job terminated

### My own words (locked in)
- Process = running program, PID = its identity
- kill = polite, kill -9 = force (nuclear option)
- Termux only shows MY processes — Android hides the rest
- Every process has a PID (for kernel) and possibly a job number (for shell)
- Foreground dies when terminal closes. Daemon survives.

---

## 7.5 Domain, DNS, HTTPS — Phase B DONE ✅

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

---

## 7.5.1 What is an OS — Phase B DONE ✅

Explored my phone's kernel, RAM, CPU, filesystem.

### Core concepts
- OS = software that manages hardware + provides services to programs
- Kernel = core of the OS, middle layer between programs and hardware
- OS = kernel + shell + drivers + utilities + userland
- 5 jobs of an OS:
  1. Process management (run, schedule, kill)
  2. Memory management (RAM allocation)
  3. File system (reads, writes, permissions)
  4. Device drivers (talk to hardware)
  5. Security (users, permissions, isolation)
- Android = Linux kernel + Google userspace
- Layers: Hardware → Drivers → Kernel → Apps → UI

### My system summary
- 📱 Samsung Galaxy A03
- 🧠 Linux kernel 4.19.191
- 🔧 ARM 64-bit (aarch64), 8 cores
- 💾 3.7 GB RAM + 4 GB swap
- 📦 Android 13
- 🐚 Termux shell on top

### Real commands I ran
- uname -r       → kernel version
- uname -a       → kernel + chip + OS
- free -h        → RAM + swap usage
- cat /proc/cpuinfo → CPU details
- getprop ro.build.version.release → Android version

### Things I saw
- Kernel: 4.19.191, built for Samsung (A037F = Galaxy A03)
- RAM: 3.7Gi total, 2.7Gi used, 75Mi free, 1.0Gi available
- Swap: 4.0Gi (storage used as fake RAM — slow!)
- CPU: ARMv8, 8 cores, hardware crypto (aes, sha1, sha2)
- Android 13

### My own words (locked in)
- Kernel = middle between programs and hardware
- OS = the whole system (kernel + shell + utilities + drivers)
- Android uses the Linux kernel
- Swap = storage used as fake RAM when real RAM is full
- Multiple CPU cores = multiple processors in cpuinfo
- Every program asks the OS for permission to touch CPU, RAM, or disk
- Linux kernel is the most popular kernel on earth
  (Android + servers + supercomputers)

---

## 7.6 Docker & Containers — Phase B DONE ✅

Wrote a real Dockerfile for shop.py. Learned image vs container.

### Core concepts
- Docker = package app + dependencies + OS into a standard unit
- Image = frozen blueprint (like a Python class)
- Container = running instance of image (like an object)
- Dockerfile = recipe for building the image
- Solves: "it works on my machine" problem
- Ships: app, libraries, OS, config, exact versions
- Isolation: each container has own filesystem, network, processes
- Container vs VM: containers share OS kernel (fast, small),
  VMs have their own OS (slow, huge)

### My Dockerfile
FROM python:3.12
WORKDIR /app
COPY shop.py .
CMD ["python", "shop.py"]

### Real commands I know
- docker build -t name .      → build image from Dockerfile
- docker run name             → run container from image
- docker ps                   → list running containers
- docker images               → list images
- docker pull python:3.12     → download image from registry

### Things I saw
- Docker cannot run natively on Termux (Android blocks kernel features)
- Dockerfile I wrote is valid — will work on a real Linux machine
- udocker tries to work around Android limits but fails
- pkg list-all shows docker-cli, docker-compose, udocker available
  but they can't fully run on Android

### My own words (locked in)
- Docker solves "it works on my machine" by shipping the whole environment
- Image = class, container = object (same pattern as Python 3.11)
- Dockerfile: FROM → WORKDIR → COPY → RUN → CMD
- Container is NOT a VM — shares host kernel, starts in seconds
- Cannot run Docker on Termux natively — platform limit, not skill gap
- The Dockerfile I wrote will run on any real Linux machine
## 7.5.2 Processes vs Threads — Phase B DONE ✅

Ran ps -eLf on a running pos-lab node server. Saw one process with
7 threads in action.

### Core concepts
- Process = running program. Own memory. Own PID.
- Thread = unit of execution inside a process. Shares memory with siblings.
- One process can have many threads.
- PID = process ID. LWP = thread ID (Lightweight Process).
- NLWP = number of threads in the process.

### Process vs thread comparison
| Feature | Process | Thread |
|---------|---------|--------|
| Memory | Own | Shared |
| Startup | Slow | Fast |
| Isolation | High | Low |
| Crash impact | Only itself | Whole process |
| Communication | IPC (sockets, pipes) | Shared memory (fast) |
| Context switch | Slow | Fast |
| Number in typical app | 1-10 | 10-1000 |

### Rule of thumb
- Processes = safety (isolation)
- Threads = speed (shared memory, no copying)
- Modern apps use both

### Real commands I ran
- ps -eLf | head -20 (in Termux, only showed my processes)
- ps -eLf | grep node (with pos-lab running)

### Things I saw
- Without pos-lab running: only bash, sshd, ps, head (each NLWP=1)
- With pos-lab: ONE PID (19885) with 7 LWP lines (19885, 19887-19893)
- NLWP = 7 → Node process has 7 threads
- Termux sandbox hides most system processes

### My own words (locked in)
- Process = running program. Thread = worker inside it.
- Threads share memory → fast but risky. Processes isolated → safe but slow.
- Threads are FASTER to create than processes.
- Node.js is "single-threaded" for JavaScript, but uses 7+ threads
  internally (event loop, worker pool, V8 GC, etc.)
- Main thread runs my JS. Worker threads do I/O and crypto.
- That's why scrypt was slow in 12.6 — it ran on a worker, main thread waited.
- The NLWP column in ps tells you how many threads a process has.
- LWP = thread ID. PID = process ID. Same process → same PID, different LWP.
