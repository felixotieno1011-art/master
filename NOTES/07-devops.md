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
## 7.5.5 Env Vars & Shells — Phase B DONE ✅

Explored environment variables step by step on Termux.
Set, exported, unset. Proved child processes inherit.

### Core concepts
- Environment variable = named value available to programs
- The OS gives every process a set of variables (its environment)
- Child processes inherit from the parent (only if exported)
- The shell is the interpreter that runs commands and passes variables

### Key variables (on my phone)
| Variable | Value |
|----------|-------|
| HOME | /data/data/com.termux/files/home |
| USER | (empty on Termux) |
| LOGNAME | (empty on Termux) |
| PWD | current directory |
| SHELL | /data/data/com.termux/files/usr/bin/bash |
| PREFIX | /data/data/com.termux/files/usr |
| PATH | colon-separated command search paths |
| LANG | en_US.UTF-8 |
| TERMUX_VERSION | 0.118.3 |
| ANDROID_API_LEVEL | 33 |

### Key commands
- env → list all env vars
- printenv → same as env
- echo $VAR → show one
- VAR=value → set (current shell only)
- export VAR=value → set + pass to children
- unset VAR → delete
- which cmd → find where a command lives
- $PATH → where the shell searches for commands

### The full cycle I ran
1. echo $HOME → shows home path
2. echo $USER → empty (Termux quirk)
3. whoami → u0_a333 (system call, not env var)
4. echo $PWD / pwd → both match
5. echo $SHELL / echo $0 → both bash
6. echo $PATH → long colon-separated list
7. export MY_TEST=hello
8. echo $MY_TEST → hello
9. bash -c 'echo "Child sees: $MY_TEST"' → hello (child inherited)
10. unset MY_TEST
11. echo "Parent sees: $MY_TEST" → empty
12. bash -c 'echo ...' → empty (child didn't inherit after unset)
13. env | head -20 → full environment list

### Things I saw
- USER and LOGNAME are empty on Termux (env var not set)
- whoami still works (asks the kernel, not the env)
- $PWD and pwd both match
- $PATH has /home/bin repeated 6 times (config bug, not critical)
- Termux commands all live in $PREFIX/bin
- LD_PRELOAD=libtermux-exec-ld-preload.so
  → this is the magic that makes /bin, /usr work on Android
- EXTERNAL_STORAGE=/sdcard
- ANDROID_API_LEVEL=33 (Android 13)

### My own words (locked in)
- $PATH = list of folders the shell searches for commands
- export = pass the variable to child processes
- unset = remove from shell + future children
- Env vars are COPIES, not live links
  → already-running children keep their old copy
- $USER can be empty. whoami is more reliable (asks kernel).
- $PWD can be stale. pwd is more reliable.
- $SHELL = login shell. $0 = program running right now.
- $PREFIX = Termux install root
- LD_PRELOAD is Termux's magic (makes Linux paths work on Android)
- Env vars can leak secrets → /proc/<pid>/environ
- Never export PASSWORD= on a shared system
- .env files are safer than exports for apps

### Security insight
- PATH hijacking: write to an early $PATH folder → shadow real commands
- Env var leaks: /proc/<pid>/environ shows all vars
- Real breaches happen when API keys are exported instead of loaded from files
- "Never trust env vars blindly" = the same pattern as $USER and $PWD
## 7.5.6 System Monitoring — Phase B DONE ✅

Ran uptime, free, df, and ps on phone. Saw real system metrics.
Load 26 on 8 cores, RAM 3.7 GiB, disk 87% full.

### The 5 core monitoring tools
| Tool | Shows |
|------|-------|
| uptime | Load average + uptime |
| free -h | RAM + swap usage |
| df -h | Disk usage per partition |
| ps aux --sort=-%cpu | Top CPU consumers |
| top | Live updating view |

### What I measured on my phone
**Uptime:**
- Up 4 days, 5:34
- Load average: 25.71, 26.30, 26.32
- On 8 cores = ~3x overloaded

**Memory (free -h):**
- Total: 3.7 GiB (not 4 GB — GB vs GiB + reserved)
- Used: 2.8 GiB
- Free: 71 MiB (very low)
- Buff/cache: 1.0 GiB (reclaimable)
- Available: 869 MiB (real usable)
- Swap: 4.0 GiB total, 1.7 GiB used (43% — memory pressure)

**Disk (df -h):**
- /data = 51 GB total, 44 GB used, 6.7 GB free (87% full) ← the real one
- / = 3.3 GB, 100% full (NORMAL for Android, read-only)
- /cache = 193M, 9% full
- /storage/emulated = same as /data (via FUSE)
- 20+ /apex/* partitions — ignore, system packages

**Processes:**
- Only 4 visible (Termux sandbox)
- Top CPU = my own ps and head commands (100% only because running)
- Real CPU hogs hidden by Android sandbox

### The 5 key metrics
1. CPU usage — %user, %sys, %idle
2. Memory — total, used, free, buff/cache, available, swap
3. Load average — processes waiting (want < 2 × cores)
4. Disk usage — used %, >90% is a problem
5. Disk I/O — busy %, read/write rates

### My own words (locked in)
- Load average 26 on 8 cores = overloaded (about 3x)
- Fix: restart, kill background apps, stop unused services
- RAM 3.7 GiB not 4 GB because: GB vs GiB (280MB) + reserved (kernel, GPU, modem)
- / at 100% is NORMAL for Android — system partition is read-only
- /data at 87% is what matters — this is my real writable space
- If /data hits 100%, apps crash
- Termux can only see its own processes
- Android hides the rest (sandbox)
- Need root to see Android's full process list
- Buff/cache can be reclaimed → available is the real number
- Swap at 43% = memory pressure → restart helps

### Commands I ran
- uptime → load avg 25.71, 26.30, 26.32
- ps aux --sort=-%cpu | head -10 → only my own processes
- free -h → 3.7Gi total, 2.8Gi used, 71Mi free, 869Mi available
- df -h → /data at 87%, / at 100% (normal)

### Security insight
- High load + hidden processes = sandbox at work
- You can't see what's eating CPU without root
- That's why Android security is layered
- On a real server: ps aux shows all processes
- The classic debugging flow: uptime → top → ps → kill
- 50 years old, still works
## 7.5.7 System Design Basics — Phase B DONE ✅

Learned the architecture of big systems. Understood why
horizontal scaling wins over vertical. Mapped the building blocks.

### Scaling
- Vertical (scale up)  = bigger machine. Simple. Expensive. Limit.
- Horizontal (scale out) = more machines. Cheap. Fault-tolerant. The real answer.

### The building blocks
- Load balancer  = distributes traffic across many servers
  Examples: Nginx, HAProxy, AWS ALB, Cloudflare
- Cache          = stores frequent answers fast
  Examples: Redis, Memcached, CDN
- Database       = source of truth, often the bottleneck
  Solutions: replication, sharding, read/write split
- Queue          = async processing
  Examples: RabbitMQ, Kafka, AWS SQS
- CDN            = serves static files near users
  Examples: Cloudflare, Akamai, AWS CloudFront

### Typical architecture
User → DNS → CDN → Load Balancer → Server cluster
     → Cache → Database

### pos-lab vs real systems
- pos-lab: 1 server, 1 SQLite file, no scale
- Real: 100s of servers, load balanced, cached, replicated
- pos-lab works for 1 user. Would fail at 100.
- WhatsApp: 450M users on ~50 engineers because they built for horizontal scale

### The full stack (real world)
- DNS: where is example.com?
- CDN: serve static files from nearby
- Load Balancer: distribute requests
- App servers: run the actual code (many)
- Cache: Redis for fast reads
- Database: PostgreSQL/MySQL with replicas
- Queue: Kafka/SQS for async work
- Object storage: S3 for files

### My own words (locked in)
- Vertical = bigger machine. Horizontal = more machines.
- Horizontal is the real answer for web scale
- Load balancer = distributes traffic, removes single point of failure
- Cache = fast answers for frequent questions, reduces DB load
- Cache != login (that's session data — also cached, but not the primary use)
- Supercomputer = wrong for web scale (expensive, single point of failure, geography)
- Hundreds of thousands of commodity servers = correct
- WhatsApp: 450M users on ~50 engineers, built for horizontal scale
- The architecture choice you make at 1,000 users determines whether you
  can handle 1 billion
- Small pieces that work together > one big thing that works alone

### Why supercomputer is wrong
- Expensive ($100M+)
- Single point of failure (one crash = everything down)
- Geography (can't be near users in Kenya AND Brazil)
- Can't add capacity gradually
- Hard to upgrade
- Web scale needs MANY machines, not ONE big one

### Real-world examples
- Google: DNS returns many IPs (load balancing at DNS level)
- Cloudflare: CDN + WAF + DDoS protection
- Redis: cache for sessions and hot data
- Kafka: event streaming for async work
- AWS: the "servers you don't own" — managed infrastructure

### Connection to earlier topics
- 7.6 (Docker): containers are the "many small things"
- 7.9 (Nginx): reverse proxy + load balancer
- 7.11 (Kubernetes): orchestrates many containers
- 6.3 (SQL Joins): database at scale
- 12.7 (HTTPS): every hop encrypted
- 7.5.6 (Monitoring): load avg, RAM, disk — the metrics you track
## 7.5.8 Computer Architecture Intro — Phase B DONE ✅

Explored CPU, clock speed, and cache on phone.
Completed Part 7.5.

### The core components
- CPU = Central Processing Unit, the brain
  - Fetch → Decode → Execute → Store → Repeat
- ALU = Arithmetic Logic Unit (does math and logic)
- Control Unit = directs the operation
- Registers = tiny ultra-fast storage (16-64 of them)
- Cache = L1/L2/L3, fast memory near CPU
- RAM = fast but volatile (code + data live here)
- Storage = permanent but slow (SSD/HDD)
- Bus = wires carrying data between components
- Clock = ticks billions of times per second

### The memory hierarchy
| Layer | Size | Speed |
|-------|------|-------|
| Registers | ~64 bytes | < 1 ns |
| L1 cache | 32-256 KB | 1-2 ns |
| L2 cache | 256 KB - 4 MB | 3-10 ns |
| L3 cache | 4-64 MB | 10-40 ns |
| RAM | 4-128 GB | 60-100 ns |
| SSD | 100 GB - 4 TB | 10-100 µs |
| HDD | 500 GB - 20 TB | 1-20 ms |

Each step down = 10x slower, 10x bigger.

### What I saw on my phone
- CPU: ARM Cortex-A53 (CPU part 0xd03)
- Cores: 8 (visible 3 in `head -30`)
- Architecture: ARMv8 = 64-bit = aarch64
- Features: fp, asimd, aes, sha1, sha2, crc32
  → hardware-accelerated crypto! (fast HTTPS)
- Current clock: 2,139,000 kHz = 2.139 GHz
- Max clock: 2,301,000 kHz = 2.301 GHz
- Cache: hidden from Termux (Android sandbox)
- RAM: 3.7 GiB
- Storage: 51 GB (/data)

### Real commands I ran
- cat /proc/cpuinfo | head -30
- cat /sys/devices/system/cpu/cpu0/cpufreq/scaling_cur_freq
  → 2139000 (current, 2.139 GHz)
- cat /sys/devices/system/cpu/cpu0/cpufreq/cpuinfo_max_freq
  → 2301000 (max, 2.301 GHz)
- Attempted: cat /sys/devices/system/cpu/cpu0/cache/*
  → "No such file or directory" (Android hides cache)

### My own words (locked in)
- CPU = brain, ALU = math, registers = tiny fast storage
- Clock speed = how many cycles per second
- 2.14 GHz = 2.14 billion cycles/sec
- 8 cores = 8 brains working in parallel
- Memory hierarchy: registers > L1 > L2 > L3 > RAM > disk
- Cache faster than RAM because it's physically closer
- Cache = workbench. RAM = warehouse.
- Hardware crypto (aes/sha) makes HTTPS fast
- Android hides CPU internals from apps (security)
- Same pattern as /etc/passwd and /tmp
- Android is NOT normal Linux
- Real Linux servers let you see all CPU info via /sys
- 8-core ARM Cortex-A53 is a 2014-era mid-range design

### Real-world implications
- 2 billion operations/sec is normal on phones today
- ARM is the most common CPU architecture in the world
  (every phone, many servers)
- Hardware crypto explains why HTTPS is so fast
- CPU cache is why "hot loops" are fast and "cold" ones are slow
- Android's sandbox hides CPU info to prevent side-channel attacks
  (Spectre, Meltdown)

### Compare to earlier topics
- 7.5.1 (OS) — OS runs on this CPU
- 7.5.2 (Processes) — 8 cores run many processes in parallel
- 7.5.3 (Memory) — RAM lives here, cache is even faster
- 7.5.4 (Permissions) — CPU doesn't care, kernel enforces
- 7.5.5 (Env Vars) — passed from one process to another via OS
- 7.5.6 (Monitoring) — load average counts processes waiting for CPU
- 7.5.7 (System Design) — horizontal scale uses many CPUs
- All these connect to the CPU underneath

### Part 7.5 COMPLETE ✅
- 7.5.1 What is an OS ✅
- 7.5.2 Processes vs Threads ✅
- 7.5.3 Memory Management ✅
- 7.5.4 File Systems & Permissions ✅
- 7.5.5 Env Vars & Shells ✅
- 7.5.6 System Monitoring ✅
- 7.5.7 System Design Basics ✅
- 7.5.8 Computer Architecture Intro ✅

8 of 8. Part 7.5 DONE.
## 7.5.8 Project — Portable System Health Monitor — DONE ✅

Built a working Bash script that monitors system health.
Works on Android (tested) and should work on Linux (untested).

### What the script does
- Detects environment (Termux vs Linux)
- Checks CPU cores + load average
- Checks RAM + swap usage
- Checks disk usage (/data on Android, / on Linux)
- Shows top 3 CPU-consuming processes
- Warns if any metric exceeds threshold

### Environment-aware thresholds
| Metric | Android | Linux |
|--------|---------|-------|
| Load | > cores × 2 | > cores × 1 |
| Available RAM | < 500 MB | < 200 MB |
| Swap | > 50% | > 30% |
| Disk | > 85% | > 90% |

### What I learned building it
1. Scripts are text files with commands (not compiled programs)
2. Shebang (#!) tells the OS which interpreter to use
3. Variables, conditionals, loops work in bash — just like Python
4. Android blocks some /proc files (/proc/loadavg) → need fallbacks
5. /proc/cpuinfo works, /proc/loadavg doesn't → use `uptime` instead
6. `~/bin` = where user programs live
7. `~/.bashrc` = where aliases + env vars live (NOT scripts)
8. Alias vs script: alias = shortcut, script = commands
9. `.bashrc` with `bash script.sh` = floods every shell
10. `.bashrc` with `alias cmd='...'` = only runs when typed

### Real commands I ran
- bash health-monitor.sh (multiple times, debugging)
- chmod +x health-monitor.sh
- cp health-monitor.sh ~/bin/health
- health (from any directory)

### Bugs I found and fixed
1. `/proc/loadavg` permission denied on Android
   → fallback to `uptime` command
2. Load value had trailing comma (`28.51,`)
   → `tr -d ' ,'` removes spaces and commas
3. `COMMAND` header in top processes list
   → added `|COMMAND` to the grep exclusion

### The script's structure
- SPEC at the top (comments)
- Environment detection (if/else)
- CPU section (cores, load, threshold)
- Memory section (RAM, swap, percentages, warnings)
- Disk section (partition, usage, warning)
- Top processes section (excludes own commands)

### My own words (locked in)
- A script = a text file with commands, executed top to bottom
- Shebang (#!) = which interpreter (bash, python, node)
- Scripts are easier to write/read/change than compiled programs
- `~/bin` = where user programs live
- `.bashrc` = where aliases + env vars live
- Alias ≠ script. Alias = shortcut. Script = commands.
- `.bashrc` runs on shell start. Put aliases there, NOT scripts.
- `bash script.sh` in .bashrc = floods every new shell
- `alias health='...'` in .bashrc = only runs when typed
- Both approaches work (alias vs ~/bin). I chose ~/bin.
- Shell scripts are real tools — every sysadmin uses them
- "Works on my machine" ≠ "works everywhere"
- Testing matters (tested Android, not Linux yet)

### Files
- ~/master/PRACTICALS/07-devops/7.5.8-architecture/health-monitor/health-monitor.sh
- ~/bin/health (copy, executable)

### When I get a laptop
- Test the script on Linux
- Check if /proc/loadavg works (should)
- Verify disk check uses /
- Add to cron (run every hour, log to file)
- Maybe add colored output
## 7.4 Hosting Options — Phase B DONE ✅

Learned where apps live. Understood domain vs hosting distinction.
Compared 6 hosting types.

### Core concepts
- Hosting = running your server on a device the internet can reach
- Domain = the name (typed in browser)
- DNS = link between domain and hosting IP
- Three separate things, all needed for www.mysite.com to work
- Running != hosting. Hosting = running + publicly reachable.

### The 6 hosting types
| Type | What | Cost | Best for |
|------|------|------|----------|
| Own device | Phone, home PC | Free | Local testing |
| VPS | Rent a virtual server | $5-20/mo | Small-medium apps, learning |
| Cloud | AWS/GCP/Azure | $10-$1000s | Scale, enterprises |
| PaaS | Push code, done | Free/$7+ | MVPs, fast deploys |
| Serverless | Functions on demand | Pay per request | APIs, event processing |
| Managed services | Databases, queues | $10-100 | Every production app |

### Why your phone can't host (yet)
1. Your phone has a private IP (behind Safaricom NAT)
2. Safaricom blocks incoming connections
3. No port forwarding on mobile networks
4. No public IP
= Only devices on the same WiFi can reach it.

### What "public hosting" actually needs
1. Public IP address (VPS or cloud gives you this)
2. Open ports (80/443)
3. Domain pointing at the IP (DNS)
= Then the world can reach you.

### Domain vs Hosting
- Domain: a NAME (e.g. poslab.com)
- Registrar: sells you the name ($10-15/year)
- Hosting: a SERVER (e.g. VPS at $5/month)
- DNS: link between them
- Domain alone = "site can't be reached"
- Hosting alone = "no name, only IP"
- Both = www.poslab.com works

### DNS infrastructure (bonus)
- .com operated by Verisign
- .ke operated by KeNIC
- .org operated by PIR
- ICANN coordinates all TLDs
- Building your own TLD = $185K+ application, millions in infrastructure
- Only companies do it (.google, .aws, .bmw)

### Private networks
- You CAN build your own DNS on your own devices
- hosts file on each device (/etc/hosts)
- mDNS (.local) works on local WiFi automatically
- dnsmasq in Termux for a real local DNS server
- Free, no ICANN needed
- Cannot be reached from the internet

### Real-world decision for pos-lab
- Best: VPS $5/month (DigitalOcean, Hetzner, Contabo)
- Alternative: Render free tier (sleeps after inactivity)
- Not: serverless (SQLite won't work)
- Why: Node + SQLite needs persistent storage + full control
- VPS = you learn real server management
- PaaS = zero maintenance, faster deploy

### Real commands I ran
- cat /etc/hosts
- Explored hosting options conceptually (no actual deployment yet)

### My own words (locked in)
- Domain = name. Hosting = reachable server. DNS = link.
- You can't host on your phone without a public IP + port forwarding
- VPS = $5/month, full root access, learning path
- PaaS = fastest to deploy, least control
- Serverless = pay per request, no persistent storage
- Cloud = powerful but complex, easy to overspend
- For pos-lab: VPS is the right choice
- Building your own TLD: impossible for individuals, possible for $185K+ companies
- But you CAN build a private .local DNS for your own devices (free)
- The real internet needs ICANN-approved TLDs. Private networks don't.

### The jump from "running" to "hosted"
- Running = localhost, only you
- Hosted = public IP + open port + DNS
- Once hosted, anyone with the URL can reach it
- That's the difference between a demo and a product

## 7.10 Cloud Platforms — Phase B DONE ✅

Learned the Big 3 (AWS, GCP, Azure). Understood Regions, AZs, IAM, and the Shared Responsibility Model.

### The Big 3
| Platform | Market Share | Known for |
|----------|--------------|-----------|
| AWS | ~32% | First, most services, most complex |
| Azure | ~23% | Enterprise, Windows integration |
| GCP | ~10% | Data/ML, Kubernetes, BigQuery |

### Core concepts
- **Regions:** Geographic areas (e.g., us-east-1, af-south-1)
- **Availability Zones (AZs):** Isolated data centers within a region. Deploy across 2+ AZs for high availability.
- **Compute:** EC2 (AWS), VMs (Azure), Compute Engine (GCP), Lambda/Functions (serverless)
- **Storage:** S3 (AWS), Blob Storage (Azure), Cloud Storage (GCP)
- **Databases:** RDS (AWS), DynamoDB (NoSQL), BigQuery (GCP)
- **Networking:** VPC (private network), Subnets, Security Groups (firewalls), Load Balancers
- **IAM (Identity & Access Management):** Who can do what. The most important cloud concept.

### The Shared Responsibility Model
- **Cloud Provider:** Physical security, hardware, hypervisor.
- **You (the customer):** Operating system, app code, data, IAM config, network config.
- "AWS secures the cloud. You secure what's in the cloud."

### Real commands I ran
- grep -rn "JWT_SECRET\|secret" ~/pos-lab/.env

### Things I saw
- pos-lab stores `JWT_SECRET` in `.env` (fine locally, bad in cloud)
- On AWS, this should be in AWS Secrets Manager
- The secret was 64 hex characters (256-bit) — strong, but stored poorly

### My own words (locked in)
- Cloud = renting someone else's computers
- VPS = one server. Cloud = many services (compute, storage, DB, network)
- Regions/AZs = geographic isolation for fault tolerance
- IAM = the most important cloud concept (and the biggest breach vector)
- Secrets should NEVER be in `.env` on a cloud server
- Use AWS Secrets Manager, not `.env`
- The Shared Responsibility Model: provider secures the building, you secure the doors
- Capital One 2019: SSRF on an EC2 server → over-permissioned IAM role → S3 breach (106M records)
- AWS was secure. Capital One's config wasn't.

### Cloud architecture (pos-lab on AWS)
- User → Route 53 (DNS) → CloudFront (CDN) → Application Load Balancer → EC2 instances (2 AZs) → RDS (database)
- Static files → S3 (served via CloudFront)
- Secrets → AWS Secrets Manager
- Monitoring → CloudWatch

## 7.7 Docker Compose — Phase B DONE ✅

Learned Docker Compose by running it in a GitHub Codespace (cloud Linux VM).
Ran a multi-container app with one command.

### What I learned about YAML
- YAML is a configuration file format (not a programming language).
- It uses indentation (spaces) to define structure.
- It is used by Docker Compose to plan the containers.

### The difference between Dockerfile, Image, and Compose
- **Dockerfile:** The recipe to build ONE container.
- **Image:** The frozen, built file.
- **docker-compose.yml (YAML):** The party planner that runs MULTIPLE containers together.

### How to send a project to a friend
1. Send the code.
2. Send the Dockerfile.
3. Send the docker-compose.yml.
4. Friend runs `docker compose up`.
= It works on every machine.

### Real commands I ran (in GitHub Codespace)
- `docker run hello-world`
- `docker run -it ubuntu bash` (entered a real Linux container!)
- `ls /workspaces` (proved it was isolated)
- `apt update` (proved it had internet)
- `docker compose up -d` (started Postgres + Nginx)
- `docker compose ps`

### Things I saw
- `docker run ubuntu bash` put me in `root@7b3c18cdc806:/#`
- `ls /workspaces` failed inside the container (isolation)
- `apt update` downloaded 26 MB (it's a real OS)
- `docker compose up -d` created a network, volume, and two containers instantly
- One command (`docker compose up -d`) did the work of 10 commands.

### My own words (locked in)
- YAML is just settings, not logic.
- Docker Compose runs multiple containers together.
- Containers are isolated from the host.
- Docker images are frozen templates.
- Containers are running instances.
- You send the Dockerfile and Compose file to your friend, not a converted program.
- The cloud VM (Codespace) is the only way to run Docker on a phone.
- Docker Compose is used in real jobs to run databases and apps together.

### The difference between running it locally vs Codespace
- Termux can't run Docker (Android kernel blocks it).
- GitHub Codespace is a cloud Linux VM with Docker pre-installed.
- We SSH'd into it via `gh codespace ssh`.
- Now we can run real Docker commands from the phone.
## 7.9 Nginx / Reverse Proxy — Phase B DONE ✅

Understood how Nginx sits between the frontend and the backend.
Wrote a real nginx.conf file.

### Core concepts
- Nginx = a high-performance web server and reverse proxy.
- Reverse Proxy = sits in front of the backend, forwards requests to it.
- Forward Proxy = sits in front of the client (e.g., VPN).
- Nginx listens on ports 80 (HTTP) and 443 (HTTPS).
- The backend listens on a private port (e.g., 3001) and is NOT exposed to the internet.
- Nginx handles SSL/TLS (the backend doesn't have to).

### The 4 superpowers of Nginx
1. Reverse Proxy — forwards requests to the backend.
2. SSL/TLS Termination — decrypts HTTPS, sends HTTP to the backend.
3. Load Balancing — distributes traffic across multiple backends.
4. Static File Serving — serves images, CSS, HTML directly (fast).

### The architecture
User → Nginx (80/443) → Backend (3001) → Database
- The user never touches the backend directly.
- Nginx is the front door.

### Real commands I ran
- (Conceptual) Created `nginx.conf` with upstream and proxy_pass.
- Understood that Nginx doesn't run natively on Termux.

### Things I saw
- `upstream pos_backend { server 127.0.0.1:3001; ... }` defines the backend group.
- `proxy_pass http://pos_backend` sends traffic to the group.
- `location /static/` serves static files directly.

### My own words (locked in)
- Nginx is not the backend. It's the traffic cop in front of it.
- The backend is hidden behind Nginx.
- Nginx handles SSL, load balancing, and static files.
- Mobile apps also use reverse proxies (API Gateways).
- API Gateways add rate limiting, API keys, and versioning.
- The user only sees the domain. They never see the port or the backend IP.
- Nginx is used by Netflix, Cloudflare, and 30% of the web.

### Connection to other topics
- 7.5 (Domain/DNS/HTTPS) — Nginx holds the SSL cert.
- 7.5.7 (System Design) — Nginx is the load balancer.
- 7.7 (Docker) — Nginx can run in a container.
- 7.10 (Cloud) — Nginx runs on EC2/VPS.
- 8.5 (Network Security) — Nginx is the perimeter.
- 8.9 (Rate Limiting) — API Gateways do this.
- 8.10 (Secure API) — API Gateways enforce auth.
- 4.4/4.6 (Frontend) — Nginx serves the frontend files.
## 7.9 Nginx / Reverse Proxy — Phase B DONE ✅

Installed Nginx in a GitHub Codespace. Configured it to proxy traffic to a Python backend.

### Core concepts
- Nginx = a reverse proxy and web server.
- The backend is hidden behind Nginx.
- Nginx listens on 80/443. Backend listens on a private port (3001).
- Nginx handles SSL, static files, and load balancing.
- `proxy_pass` is the directive that forwards traffic.

### The architecture
User → Nginx (port 80) → Backend (port 3001)
- The user never talks to the backend directly.

### Real commands I ran
- `sudo apt install nginx -y`
- `python3 backend.py &` (started the backend)
- `sudo nano /etc/nginx/sites-available/default` (configured the proxy)
- `sudo nginx -t` (tested the config)
- `sudo nginx` (started Nginx)
- `curl -s http://127.0.0.1` (hit Nginx, not the backend)
- `sudo tail -5 /var/log/nginx/access.log` (saw the request)

### Things I saw
- `nginx: master process` + `worker processes` (the server is running).
- The `curl` request returned the backend's HTML.
- The backend logged the request (`GET / 200`).
- Nginx logged the request in `/var/log/nginx/access.log`.
- When the Codespace closed, I lost the connection to Nginx.

### My own words (locked in)
- Nginx is the front door. The backend is hidden inside.
- The user only knows the domain/port 80. They never know about 3001.
- Nginx handles the SSL certificate (we didn't do SSL today, but that's next).
- If the backend dies, Nginx returns 502 (Bad Gateway).
- Nginx is fast. It can serve static files without touching the backend.
- Nginx runs as a master process and worker processes.
- The access log is how you see traffic.
- This is how real production servers are set up.
- Nginx is used by Netflix, Cloudflare, and 30% of the web.

### Connection to other topics
- 7.5 (Domain/DNS/HTTPS) — Nginx is where the SSL cert lives.
- 7.5.7 (System Design) — Nginx is the load balancer.
- 7.7 (Docker) — Nginx runs in a container.
- 7.10 (Cloud) — Nginx runs on EC2/VPS.
- 8.5 (Network Security) — Nginx is the perimeter.
- 8.9 (Rate Limiting) — Nginx can rate limit.
- 5.1 (Backend) — Nginx sits in front of it.
- 12.11–12.15 (Attacks) — Nginx stops a lot of them (WAF).

## 7.9 Nginx Practical & Metasploit Intro — DONE ✅

Ran Nginx as a reverse proxy in a GitHub Codespace.
Installed the real Metasploit Framework in the cloud.
Understood the difference between my mini-msf and the real tool.

### The Nginx practical (in Codespace)
- Installed Nginx (`sudo apt install nginx -y`).
- Wrote a Python backend running on port 3001.
- Configured Nginx (`/etc/nginx/sites-available/default`) to proxy port 80 to port 3001.
- Tested with `curl http://127.0.0.1` → returned the backend HTML.
- Verified with `sudo tail -5 /var/log/nginx/access.log` → saw the request logged by Nginx.
- Confirmed Nginx hides the backend (the backend is on 3001, the public is on 80).

### The Metasploit practical (in Codespace)
- Installed Metasploit (`curl ... | bash`).
- Opened `msfconsole` (the real Metasploit, 2,677 exploits).
- Used `db_nmap` to scan 127.0.0.1 (ports 80, 443) → found nothing (closed).
- Used `auxiliary/scanner/ssh/ssh_version` → got "Connection refused" (no SSH on port 22).
- Lesson: Metasploit can only exploit what is actually open.

### Why we used the Codespace
- Termux (Android) cannot run Docker or Nginx or Metasploit.
- The Codespace is a real Linux machine in the cloud.
- Termux SSH'd into it (`gh codespace ssh`).
- The cloud did the heavy lifting. Termux was the remote control.

### Real commands I ran
- `sudo apt install nginx nmap`
- `sudo nginx -t` (config test)
- `sudo nginx` (start)
- `python3 backend.py &`
- `curl http://127.0.0.1`
- `msfconsole`
- `db_nmap -sV -p 80,443 127.0.0.1`
- `use auxiliary/scanner/ssh/ssh_version`
- `set RHOSTS 127.0.0.1`
- `run`

### Things I saw
- Nginx logged the request (`GET / 200`).
- The backend was hidden behind Nginx.
- Metasploit found no open ports (80/443 closed in that moment).
- Metasploit couldn't scan SSH (ECONNREFUSED).
- Metasploit has 2,677 exploits (my mini-msf had 1).
- The core mechanism is the same: scan, select, set, run.

### My own words (locked in)
- Nginx is the front door. The backend is hidden.
- The Codespace is a free cloud Linux machine.
- Termux is the remote control. The cloud does the work.
- Metasploit is just a huge collection of modules (like my mini-msf).
- `db_nmap` stores scan results in the Metasploit database.
- If a port is closed, Metasploit cannot exploit it.
- My mini-msf has 1 exploit. Metasploit has 2,677.
- The workflow is identical: use, set, run, sessions.
- I am not scared of Metasploit anymore.

### Connection to other topics
- 7.6 (Docker) — ran in the Codespace.
- 7.9 (Nginx) — the practical.
- 12.13 (Vuln assessment) — scanning for open ports.
- 12.14 (Exploitation) — Metasploit vs my mini-msf.
- 5.1 (Backend) — the Python backend that Nginx proxied.
- 12.11/12.12 (Recon/Scanning) — nmap.
- 12.19 (Blue Team) — logs in Nginx.
## 7.8 CI/CD Pipelines — Phase B DONE ✅

Understood CI/CD and how it connects to Docker.
Learned YAML syntax (it's just JSON without brackets).

### Core concepts
- **CI (Continuous Integration):** Automatically run tests, lint, and build on every push.
- **CD (Continuous Deployment):** Automatically deploy the built artifact to the server.
- **Pipeline:** The sequence of steps (checkout → test → build → push → deploy).
- **GitHub Actions:** The CI/CD tool built into GitHub (uses `.github/workflows/*.yml`).

### The connection to Docker
- Docker builds the container.
- CI/CD builds the container automatically on push.
- CI/CD pushes the container to a registry (Docker Hub).
- CI/CD tells the server to pull and run the new container.

### YAML syntax rules
1. **Indentation = structure.** Use spaces, NEVER tabs. (2 spaces is standard).
2. **Colon + space** for key-value: `name: Felix` (NOT `name:Felix`).
3. **Dash + space** for lists:
   ```yaml
   - item1
   - item2

## 7.11 Kubernetes Basics — Phase B DONE ✅

Deployed a real Kubernetes cluster in a Codespace using `kind`.
Saw Pods, Deployments, and self-healing in action.

### Core concepts
- **Kubernetes (K8s)** = container orchestration platform.
- **Node** = a server in the cluster.
- **Pod** = the smallest unit (wraps one or more containers).
- **Cluster** = all the nodes + the control plane.
- **Deployment** = the object that says "I want X replicas of this image."
- **kubectl** = the CLI tool to talk to the cluster.

### The Desired State (Reconciliation Loop)
- You say: "I want 5 Pods."
- Kubernetes checks: "I only see 4."
- Kubernetes creates 1 new Pod.
- This happens automatically, forever.

### Real commands I ran
- `kind create cluster --name pos-cluster`
- `kubectl get nodes`
- `kubectl create deployment nginx --image=nginx:alpine`
- `kubectl get pods`
- `kubectl describe pod nginx-...`
- `kubectl scale deployment busybox --replicas=5`
- `kubectl delete pod busybox-...` (proved self-healing)
- `kubectl get pods -w`
- `kind delete cluster --name pos-cluster`

### Things I saw
- Cluster created in 60 seconds (control plane + node).
- `kubectl get nodes` showed the node `Ready`.
- `kubectl create deployment` created a Pod.
- `kubectl get pods` showed `ContainerCreating`, then `ErrImagePull` (network issue).
- `kubectl scale` created 5 Pods.
- Deleting a Pod caused Kubernetes to immediately create a replacement.
- `kubectl get pods -w` showed the live updates.

### The network limitation
- The Kubernetes cluster inside the Codespace couldn't reach Docker Hub.
- `ErrImagePull` / `ImagePullBackOff` showed the image download failed.
- This is a Codespace networking limitation, not a Kubernetes failure.
- The orchestration worked perfectly (self-healing, scaling).

### My own words (locked in)
- Kubernetes is the conductor. Docker containers are the musicians.
- You don't tell Kubernetes "start this." You tell it "I want this."
- The Desired State is the magic. It always tries to reach it.
- Self-healing: delete a Pod, it creates a new one.
- Scaling: `replicas=5` creates 5 Pods.
- Pods are ephemeral. They die and are replaced. You don't care about individual Pods, only the desired count.
- The network issue (ErrImagePull) is a real-world problem. In a real cluster, the network works.
- `kubectl` is the remote control. `kind` is the local Kubernetes.

### Connection to other topics
- 7.6 (Docker) — containers.
- 7.7 (Docker Compose) — multi-container locally.
- 7.8 (CI/CD) — pipelines deploy to Kubernetes.
- 7.9 (Nginx) — the Ingress controller is Nginx.
- 7.10 (Cloud) — EKS (AWS), GKE (Google), AKS (Azure).
- 7.5.7 (System Design) — horizontal scaling in action.
- 7.5.2 (Threads) — Pods run on nodes (processes).

## 7.12 Monitoring & Logging — Phase B DONE ✅

Learned the difference between metrics and logs.
Collected real system metrics manually on Android.

### Core concepts
- **Metrics** = numbers that track system health over time.
  - CPU, memory, disk, requests/sec, response time, error rate.
  - Collected by **Prometheus**. Visualized by **Grafana**.
  - Agent on each server: **Node Exporter**.
- **Logs** = text records of what happened.
  - Errors, logins, warnings, requests.
  - Collected by **ELK** (Elasticsearch, Logstash, Kibana) or **Loki**.
- **Alerting** = notify when a metric crosses a threshold.
  - Alertmanager, PagerDuty, Slack.

### The architecture
Server 1 ─┐
Server 2 ─┼─> Prometheus (pull metrics) ─> Grafana (dashboard)
Server 3 ─┘

Server 1 ─┐
Server 2 ─┼─> Logstash (ship logs) ─> Elasticsearch (store) ─> Kibana (view)
Server 3 ─┘

### Real commands I ran
- `vmstat 1 5` (failed: Android sandbox)
- `cat /proc/loadavg` (failed: Permission denied)
- `free -m` (worked)
- `df -h ~` (worked)

### Things I saw
- RAM: 3777 MB total, 2788 used, 988 available.
- Swap: 4095 MB total, 1279 used.
- Disk: 51G total, 43G used, 85% full.
- Android blocks `/proc/loadavg` and `vmstat`.
- But `free` and `df` work.

### My own words (locked in)
- Metrics = numbers. Logs = text.
- Prometheus collects metrics. Grafana visualizes them.
- ELK collects and visualizes logs.
- Monitoring without alerting is useless (nobody sees it).
- Android blocks some `/proc` files. That's why we need Linux servers or Codespaces for full monitoring.
- Metrics tell you "what." Logs tell you "why."
- You need both.
- A sysadmin's job is 50% monitoring, 50% logs.
- In Kubernetes, Prometheus is the standard for metrics.
- In production, Grafana dashboards show CPU, memory, disk, network, and app metrics all in one place.

### Connection to other topics
- 7.5.6 (System Monitoring) — the basics (`top`, `free`, `df`).
- 7.11 (Kubernetes) — Prometheus runs as a Pod.
- 7.10 (Cloud) — CloudWatch is AWS's monitoring tool.
- 8.9 (Rate Limiting) — alerts on too many failed logins.
- 12.19 (Blue Team) — SIEM uses logs for security.
- 12.26 (Forensics) — logs are evidence.

## 7.13 Environment Management — Phase B DONE ✅

Learned how to manage configuration and secrets across environments.
Checked pos-lab's `.gitignore` and created a `.env.example`.

### Core concepts
- **Environment** = the context where the code runs (dev, staging, prod).
- **Same code, different config.**
- **12-Factor App** = a methodology. Factor #3: "Store config in the environment."
- **Never hardcode secrets** in the code.
- **Never commit `.env`** to Git.

### The .env workflow
1. Create `.env` (with real secrets).
2. Add `.env` to `.gitignore`.
3. Create `.env.example` (with placeholders).
4. Commit `.env.example` (safe, no secrets).
5. In production, use a **secrets manager** (AWS Secrets Manager, Vault).

### The 3 environments
- **Dev:** Your machine. Fake data. Debug on.
- **Staging:** A copy of prod. Test before prod.
- **Prod:** Real users. Real data. Debug off. Monitoring on.

### Real commands I ran
- `cat ~/pos-lab/.gitignore` (saw `.env`, `*.db`, `*.log` are ignored)
- `nano ~/pos-lab/.env.example` (created the example file)
- `git status -s` (failed: pos-lab is not a Git repo)

### Things I saw
- pos-lab's `.gitignore` already ignores `.env`, `*.db`, `*.log`.
- Created `.env.example` with placeholders.
- `git status` failed because pos-lab isn't a Git repo.

### My own words (locked in)
- Secrets go in `.env`. Never in code.
- `.env` goes in `.gitignore`. Never in Git.
- `.env.example` shows what variables are needed (no secrets).
- Same code, different config (dev/staging/prod).
- If a secret is in Git, it's leaked forever (even if you delete it).
- Rotate any secret that was ever committed.
- Production uses secrets managers, not `.env`.
- pos-lab is not a Git repo. That's fine (it's a local lab).
- The 12-Factor App is the industry standard.

### Connection to other topics
- 5.8 (Env Vars & Config) — the backend uses `.env`.
- 7.5.5 (Env Vars & Shells) — how env vars work.
- 7.8 (CI/CD) — GitHub Actions uses secrets.
- 7.10 (Cloud) — AWS Secrets Manager.
- 7.11 (Kubernetes) — Kubernetes Secrets.
- 8.4 (Secure Coding) — never hardcode secrets.
- 8.10 (Secure API) — the JWT secret in `.env`.
- 12.17 (Password Attacks) — why secrets matter.

## 7.14 Infrastructure as Code (IaC) — Phase B DONE ✅

Installed Terraform. Wrote a `.tf` file to create a Docker container.
Ran the full lifecycle: init, plan, apply, destroy.

### Core concepts
- **IaC** = managing infrastructure with code, not manual clicks.
- **Declarative:** You say *what* you want, not *how* to do it.
- **Terraform** = the industry standard tool (by HashiCorp).
- **State file** (`terraform.tfstate`) = records what Terraform has created.
- **Providers** = plugins that let Terraform talk to AWS, Docker, Azure, etc.

### The lifecycle
1. `terraform init` — download providers.
2. `terraform plan` — preview changes (dry run).
3. `terraform apply` — create/update infrastructure.
4. `terraform destroy` — tear it all down.

### Real commands I ran
- `terraform init`
- `terraform plan`
- `terraform apply`
- `curl http://127.0.0.1:8081` (verified Nginx)
- `terraform destroy`
- `docker ps -a | grep ...` (found leftover containers)
- `docker rm -f ...` (removed leftovers)

### Things I saw
- `terraform plan` showed `Plan: 2 to add, 0 to change, 0 to destroy.`
- `terraform apply` created the image and the container.
- `curl` returned the Nginx welcome page.
- `terraform destroy` failed because a leftover `codespace-app-1` container was using the image.
- Removed the leftover containers.
- `terraform destroy` then succeeded.

### My own words (locked in)
- IaC = write code, not clicks.
- Declarative = you describe the end state. Terraform figures out how to get there.
- The state file is the source of truth. Terraform knows what it created.
- Terraform can't clean up containers it didn't create. Leftovers block cleanup.
- `terraform destroy` is the reverse of `apply`.
- `terraform plan` is the dry run. Always plan before apply.
- This is how companies build 100 servers in 3 minutes.
- If you click, you will make mistakes. If you code, the machine does it perfectly.
- Terraform works with AWS, Azure, GCP, Docker, Kubernetes, and more.
- The state file should be committed to Git (but not always, depending on the team's workflow).

### Connection to other topics
- 7.4 (Hosting) — Terraform creates the servers.
- 7.6 (Docker) — Terraform created a Docker container.
- 7.10 (Cloud) — Terraform is used to provision AWS/Azure/GCP.
- 7.11 (Kubernetes) — Terraform can create Kubernetes clusters.
- 7.8 (CI/CD) — Terraform runs in the CI/CD pipeline.
- 7.13 (Env Management) — Terraform uses variables for secrets.
- 12.19 (Blue Team) — IaC makes infrastructure reproducible and auditable.
