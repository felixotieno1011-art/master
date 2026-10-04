"""Background monitoring — health checks + alerts."""
import os
import time

import config
from utils import now_iso, read_json, write_json, ensure_dir
from core import vm as vmm
from core import breakage


MONITOR_DIR    = os.path.join(config.STATE_DIR, "monitor")
STATE_FILE     = os.path.join(MONITOR_DIR, "state.json")
ALERTS_FILE    = os.path.join(MONITOR_DIR, "alerts.log")
SNAPSHOTS_FILE = os.path.join(MONITOR_DIR, "snapshots.json")


def _load_state():
    return read_json(STATE_FILE) or {"running": False, "started": None, "checks": 0}


def _save_state(data):
    ensure_dir(MONITOR_DIR)
    write_json(STATE_FILE, data)


def _append_alert(level, msg):
    ensure_dir(MONITOR_DIR)
    with open(ALERTS_FILE, "a") as f:
        f.write(f"{now_iso()} [{level:<7}] {msg}\n")


def read_alerts(limit=30):
    if not os.path.exists(ALERTS_FILE):
        return []
    with open(ALERTS_FILE) as f:
        lines = f.readlines()
    return [l.rstrip() for l in lines[-limit:]]


def _record_snapshot(snapshot):
    snaps = read_json(SNAPSHOTS_FILE) or []
    snaps.append(snapshot)
    snaps = snaps[-200:]
    write_json(SNAPSHOTS_FILE, snaps)


def check_once():
    timestamp = now_iso()
    vms = vmm.list_all()

    snapshot = {"time": timestamp, "vms": [], "issues": 0}

    for v in vms:
        name = v["name"]
        status = vmm.status(name) or {}
        diag = breakage.diagnose(name) or {"healthy": True, "issues": []}

        vm_snap = {
            "name": name,
            "state": status.get("state", "UNKNOWN"),
            "pid": status.get("pid"),
            "uptime_sec": status.get("uptime_sec", 0),
            "issues": [i["type"] for i in diag.get("issues", [])],
        }
        snapshot["vms"].append(vm_snap)

        if vm_snap["state"] != "RUNNING":
            _append_alert("WARN", f"VM '{name}' is {vm_snap['state']}")
            snapshot["issues"] += 1

        for issue in vm_snap["issues"]:
            _append_alert("ALERT", f"VM '{name}' has issue '{issue}'")
            snapshot["issues"] += 1

    _record_snapshot(snapshot)
    return snapshot


def start_loop(interval_sec=15, max_iterations=None):
    state = _load_state()
    state["running"] = True
    state["started"] = now_iso()
    state["interval"] = interval_sec
    state["checks"] = 0
    _save_state(state)
    _append_alert("INFO", f"monitor started (interval {interval_sec}s)")

    iteration = 0
    try:
        while True:
            snapshot = check_once()
            iteration += 1
            state["checks"] = iteration
            state["last_check"] = snapshot["time"]
            _save_state(state)

            issues = snapshot["issues"]
            print(f"[{snapshot['time']}] check #{iteration}: "
                  f"{len(snapshot['vms'])} VMs, {issues} issue(s)")

            if max_iterations and iteration >= max_iterations:
                break
            time.sleep(interval_sec)
    except KeyboardInterrupt:
        print("\n🛑 Monitor stopped by user.")
    finally:
        state = _load_state()
        state["running"] = False
        state["stopped"] = now_iso()
        _save_state(state)
        _append_alert("INFO", "monitor stopped")


def status():
    state = _load_state()
    return {
        "running": state.get("running", False),
        "started": state.get("started"),
        "stopped": state.get("stopped"),
        "checks": state.get("checks", 0),
        "interval": state.get("interval"),
        "last_check": state.get("last_check"),
    }


def stop_marker():
    state = _load_state()
    state["running"] = False
    state["stopped"] = now_iso()
    _save_state(state)


def recent_snapshots(limit=5):
    snaps = read_json(SNAPSHOTS_FILE) or []
    return snaps[-limit:]
