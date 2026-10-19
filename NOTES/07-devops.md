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
## 7.5.3 Memory Management — Phase B DONE ✅

Explored memory usage on phone. Saw virtual memory vs real RAM.
Understood swap, OOM killer, and why phones kill apps.

### Core concepts
- Memory management = OS allocates, tracks, reclaims RAM
- Virtual memory = each process thinks it has GBs of memory
  → in reality, only some pages are in real RAM
- Paging = RAM divided into pages (4 KB); inactive pages swapped to disk
- Swap = storage used as fake RAM when real RAM fills. 10-100x slower than RAM.
- OOM killer = when RAM + swap fill, OS kills processes (Android = background apps)
- Heap = dynamic allocations (new, malloc)
- Stack = function calls, local variables

### Key metrics
- VSZ = virtual memory size (address space). Mostly unallocated.
- RSS = Resident Set Size. Actual RAM in use. THIS is what matters.
- NLWP = number of threads (from 7.5.2)

### Real commands I ran
- free -h
- ps aux --sort=-%mem | head -6
- cat /proc/self/status | grep -E "VmRSS|VmSize|VmSwap"
- cat /proc/meminfo | grep -i swap
- cat /proc/swaps (permission denied on Android)

### Things I saw
- Total RAM: 3.7 Gi | Used: 2.8 Gi | Free: 92 Mi
- Available: 943 Mi
- Swap: 4.0 Gi total | 1.6 Gi used | 2.4 Gi free (40% of swap used!)
- SwapCached: 165 MB (recently swapped pages, cached back in RAM)
- My bash shell: VmSize = 2.2 GB (virtual), VmRSS = 3.5 MB (real)
- ps aux shows only 4 processes (Termux sandbox)
- Node process VSZ ~2.2 GB but RSS ~5 MB

### My own words (locked in)
- VSZ = virtual (mostly empty), RSS = real RAM (what matters)
- Swap = fake RAM from storage. Slow. Used when RAM fills.
- 1.6 GB swap = phone under memory pressure
- When RAM + swap both fill → OOM killer kills processes
- Android kills background apps to free memory for foreground
- That's why opening a heavy app sometimes closes others
- Virtual memory lets each app think it has a whole computer
- The OS juggles real RAM behind the scenes
- Fake phone scam = same trust-boundary issue:
  the settings app lied about storage, nothing verified it
- "Verify, don't trust" applies to memory too:
  free -h tells the truth, not "system says 128 GB"
## 7.5.4 File Systems & Permissions — Phase B DONE ✅

Tested permissions on pos-lab files, changed them with chmod,
and saw the difference between private (600) and public (644).

### Core concepts
- File system = how the OS organizes files (names, folders, metadata)
- Permissions = who can read, write, execute each file
- Every file has 3 permission groups:
  - User (owner) — created the file
  - Group — a team of users
  - Other — everyone else
- Each group has 3 bits:
  - r = read (4)
  - w = write (2)
  - x = execute (1)
- A permission string has 10 characters:
  - First char: type (- file, d dir, l symlink)
  - Next 9: rwx for user, group, other
- Octal notation: sum of bits per group
  - rwx = 7, r-x = 5, rw- = 6, --- = 0
  - rw------- = 600
  - rw-r--r-- = 644

### The core rule
| Permission | Octal | Meaning | Use |
|-----------|:-----:|---------|-----|
| -rw------- | 600 | Owner read+write only | Secrets (.env, .pem, .db) |
| -rw-r--r-- | 644 | Owner full, everyone read | Public files (README, HTML, images) |
| -rwx------ | 700 | Owner full only | Private scripts |
| -rwxr-xr-x | 755 | Owner full, everyone read+exec | Public scripts (/bin/) |
| -rwxrwxrwx | 777 | Everyone full | NEVER USE |

### Why 777 is dangerous
- Anyone can read → secrets exposed
- Anyone can write → attacker can modify/replace
- Anyone can execute → attacker can run their own code
- 777 is a red flag in every audit

### Real commands I ran
- ls -l ~/pos-lab/.env ~/pos-lab/keys/*.pem
- chmod 644 public-readme.md
- chmod 600 public-readme.md
- ls -l private.txt public.txt
- find ~/pos-lab -type f -perm -o=r (no output = no world-readable)
- find ~/pos-lab -type f -perm -o=w (no output = no world-writable)

### Things I saw
- All pos-lab files are -rw------- (Termux's default umask 077)
- Even README.md and jwt-public.pem are 600
- No world-readable or world-writable files
- After chmod 644: -rw-r--r--
- After chmod 600: back to -rw-------
- private.txt (600) vs public.txt (644) side by side

### My own words (locked in)
- rwx = read/write/execute
- 3 groups = user, group, other
- 600 = only I can read/write
- 644 = I read/write, everyone else can read
- 777 = everyone full access = disaster
- Termux uses umask 077 = very strict by default
- On a real server: 600 for secrets, 644 for public files
- On your phone it's all 600 — fine for single-user, wrong for a web server
- Never put 777 on anything
- Test: after chmod, ls -l confirms the change
- If a web server can't read a file (600 when it needs 644), the site breaks
- If a file is 777, an attacker can own it

### Security connection
- 600 on .env and .pem = private keys protected
- 644 on README.md = public info readable
- 777 on anything = critical finding in any pentest
- This is exactly what file permissions audits check
- Real breaches have happened because of world-writable files
## 7.2 Linux Permissions & Users — Phase B DONE ✅

Explored users, groups, sudo, and chown on Termux/Android.
Hit real limits (no sudo, no /tmp, no chown without root).

### Core concepts
- Linux users = identities that own files, run processes, log in
- 3 types:
  - root (UID 0) — superuser, unlimited power
  - system users — created by OS for services (sshd, www-data)
  - regular users — human users (u0_a333)
- 3 types of groups:
  - primary group — each user has one
  - secondary groups — extra memberships
  - system groups — created by OS
- Key commands: whoami, id, groups, sudo, su, useradd,
  usermod, userdel, passwd, chown, chmod
- sudo = run one command as root (logged, safest)
- su - = become root fully (needs root password)
- sudo -i = become root fully (via sudo)

### The 3 layers of Android security
1. Unix permissions (rwx — 7.5.4)
2. Android sandbox (each app = own user/UID)
3. SELinux (even root restricted)

### Real commands I ran
- whoami → u0_a333
- id → uid=10333, gid=10333, 6 groups, SELinux context
- groups → u0_a333, ext_obb_rw, inet, everybody,
  u0_a333_cache, all_a333
- cat /etc/passwd → empty (Android doesn't use /etc/passwd)
- sudo -l → "No superuser binary detected. Are you rooted?"
- touch /tmp/testfile.txt → failed (no /tmp on Android)
- touch $PREFIX/tmp/testfile.txt → worked
- chown root:root $PREFIX/tmp/testfile.txt → "Operation not permitted"

### Things I saw
- UID=10333, GID=10333, 6 groups
- SELinux context: u:r:untrusted_app_27:s0:c77,c257,c512,c768
  = "untrusted app" label — one more restriction layer
- /etc/passwd doesn't exist on Android
- /tmp doesn't exist; $PREFIX/tmp is the Android temp
- No sudo (phone not rooted)
- chown blocked (not root, and SELinux as backup)
- File permissions (chmod) work fine — that's the Unix layer

### My own words (locked in)
- UID = user ID, GID = group ID
- u0_a333 = my Termux user (UID 10333)
- Each Android app has its own UID → own sandbox
- No app can read another app's files
- sudo requires root. Android phones are not rooted by default.
- No sudo = no chown, no useradd, no system file access
- /etc/passwd doesn't exist on Android
- /tmp doesn't exist; use $PREFIX/tmp
- chown failed for 2 reasons:
  1. Not root (primary)
  2. SELinux (secondary)
- chmod works (own files, Unix permissions)
- chown doesn't (need root)
- Security in depth: Unix permissions + sandbox + SELinux
- On a real Linux server:
  - /etc/passwd exists
  - /tmp exists
  - sudo exists (if admin)
  - chown works (with sudo)
- Different environment = different defaults
- Same concept (rwx, users, groups) but different implementation

### Real Linux vs Android
| Feature | Normal Linux | Android |
|---------|-------------|---------|
| /etc/passwd | ✅ | ❌ |
| /tmp | ✅ | ❌ (use $PREFIX/tmp) |
| sudo | ✅ (if admin) | ❌ (unless rooted) |
| useradd | ✅ (with sudo) | ❌ |
| chown | ✅ (with sudo) | ❌ (blocked) |
| rwx permissions | ✅ | ✅ |
| SELinux | Optional | 🔴 Enforced |
