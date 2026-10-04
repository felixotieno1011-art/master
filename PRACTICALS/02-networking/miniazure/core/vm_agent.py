#!/usr/bin/env python3
"""The simulated VM process.

A real VM is a running process on a physical host.
In MiniAzure, this is that process.

It loops forever, updates its heartbeat file, and exits on SIGTERM.
"""
import json
import os
import signal
import sys
import time
from datetime import datetime

# Set by the launcher before this module runs.
# We expect: MINIAZURE_VM_NAME and MINIAZURE_VM_STATE_DIR
VM_NAME = os.environ.get("MINIAZURE_VM_NAME", "unknown")
STATE_DIR = os.environ.get("MINIAZURE_VM_STATE_DIR", "/tmp")
HEARTBEAT = os.path.join(STATE_DIR, f"{VM_NAME}.heartbeat")
LOG_FILE = os.path.join(STATE_DIR, f"{VM_NAME}.log")


def log(msg):
    """Append to the VM's log file."""
    ts = datetime.now().strftime("%H:%M:%S")
    try:
        with open(LOG_FILE, "a") as f:
            f.write(f"[{ts}] {msg}\n")
    except Exception:
        pass


def heartbeat():
    """Write current process status."""
    data = {
        "pid": os.getpid(),
        "time": datetime.now().isoformat(timespec="seconds"),
        "uptime": time.time() - START,
    }
    try:
        tmp = HEARTBEAT + ".tmp"
        with open(tmp, "w") as f:
            json.dump(data, f)
        os.replace(tmp, HEARTBEAT)
    except Exception:
        pass


def on_term(signum, frame):
    log(f"Received signal {signum}, shutting down")
    try:
        os.remove(HEARTBEAT)
    except Exception:
        pass
    sys.exit(0)


def main():
    global START
    START = time.time()

    # Register signal handlers so `kill` is graceful
    signal.signal(signal.SIGTERM, on_term)
    signal.signal(signal.SIGINT, on_term)

    log(f"VM '{VM_NAME}' starting (pid {os.getpid()})")
    log("VM ready")

    # Write an initial heartbeat immediately
    heartbeat()

    # Loop forever
    while True:
        heartbeat()
        time.sleep(1)


if __name__ == "__main__":
    main()
