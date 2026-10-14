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
