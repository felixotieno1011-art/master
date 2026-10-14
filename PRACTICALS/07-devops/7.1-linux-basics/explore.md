# 7.1 Linux Server Basics — Exploration

## SPEC
1. whoami — my user
2. uname -a — kernel info
3. ls -la — list files
4. df -h — disk usage
5. ps aux | head — running processes

## Results

### whoami
u0_a333
What it means: my Linux username — my phone user ID

### uname -a
Linux localhost 4.19.191 aarch64 Android
What it means: Linux kernel, ARM 64-bit chip (aarch64), running Android

### ls -la
(empty folder — just . and ..)
What it means: I'm in a new empty directory

### df -h
/dev/block/dm-4  3.3G  3.3G  5.3M  100%  /
What it means: root filesystem is 100% full (normal for Android)
My real writable space is under /data — check with `df -h /data`

### ps aux | head
bash, sshd, ps, head
What it means: my shell, the SSH daemon, and my own commands running
### whoami
u0_a333
What it means: my Linux username — the user ID Android gives Termux

### df -h /data
/dev/block/dm-45  51G  44G  7.1G  87%  /data/user/0
What it means: my REAL writable space. 51 GB total, 7.1 GB free, 87% used.
Note: / (root) showed 100% full — that's the system partition,
read-only for me. My space is /data.
