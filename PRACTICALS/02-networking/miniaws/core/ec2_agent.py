#!/usr/bin/env python3
"""The simulated EC2 instance process."""
import json
import os
import signal
import sys
import time
from datetime import datetime


INSTANCE_ID = os.environ.get("MINIAWS_INSTANCE_ID", "unknown")
STATE_DIR   = os.environ.get("MINIAWS_EC2_STATE_DIR", "/tmp")
HEARTBEAT   = os.path.join(STATE_DIR, f"{INSTANCE_ID}.heartbeat")
LOG_FILE    = os.path.join(STATE_DIR, f"{INSTANCE_ID}.log")


def log(msg):
    ts = datetime.now().strftime("%H:%M:%S")
    try:
        with open(LOG_FILE, "a") as f:
            f.write(f"[{ts}] {msg}\n")
    except Exception:
        pass


def heartbeat(start_time):
    data = {
        "instance_id": INSTANCE_ID,
        "pid": os.getpid(),
        "time": datetime.now().isoformat(timespec="seconds"),
        "uptime_sec": time.time() - start_time,
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
    start_time = time.time()

    signal.signal(signal.SIGTERM, on_term)
    signal.signal(signal.SIGINT, on_term)

    log(f"EC2 instance {INSTANCE_ID} starting (pid {os.getpid()})")
    log("instance is running")
    heartbeat(start_time)

    while True:
        heartbeat(start_time)
        time.sleep(1)


if __name__ == "__main__":
    main()
