"""Break/fix scenarios.

Each scenario has:
  - a name (type)
  - a way to inject it
  - a way to detect it (diagnosis)
  - a way to fix it
"""
import os

import config
from utils import now_iso, read_json, write_json, ensure_dir
from core import vm as vmm


BREAKAGE_DIR = os.path.join(config.STATE_DIR, "breakage")


# All scenario types we support
SCENARIOS = {
    "disk-full": {
        "symptom": "VM disk is full",
        "detect": "Disk usage over 90%",
        "fix":    "Clean up and resize disk",
    },
    "memory-leak": {
        "symptom": "Memory usage growing continuously",
        "detect": "Memory usage over 85%",
        "fix":    "Restart the service",
    },
    "service-down": {
        "symptom": "Process is not responding to heartbeat",
        "detect": "No heartbeat for over 10 seconds",
        "fix":    "Restart the process",
    },
    "high-cpu": {
        "symptom": "CPU usage near 100%",
        "detect": "CPU usage over 90%",
        "fix":    "Throttle or restart",
    },
    "network-partition": {
        "symptom": "VM cannot reach network",
        "detect": "Subnet attachment is lost",
        "fix":    "Re-attach to subnet",
    },
}


def _break_path(vm_name):
    return os.path.join(BREAKAGE_DIR, f"{vm_name}.json")


def _load_breaks(vm_name):
    data = read_json(_break_path(vm_name))
    return data if data else {"vm": vm_name, "breaks": []}


def _save_breaks(vm_name, data):
    ensure_dir(BREAKAGE_DIR)
    write_json(_break_path(vm_name), data)


def inject(vm_name, break_type):
    """Break a VM by injecting a scenario. Return (success, message)."""
    if break_type not in SCENARIOS:
        valid = ", ".join(SCENARIOS.keys())
        return False, f"unknown break type '{break_type}'. valid: {valid}"

    if not vmm.get(vm_name):
        return False, f"VM '{vm_name}' not found"

    data = _load_breaks(vm_name)
    # already broken?
    for b in data["breaks"]:
        if b["type"] == break_type and not b.get("resolved"):
            return False, f"VM '{vm_name}' already has '{break_type}'"

    entry = {
        "type":      break_type,
        "symptom":   SCENARIOS[break_type]["symptom"],
        "injected":  now_iso(),
        "resolved":  None,
    }
    data["breaks"].append(entry)
    _save_breaks(vm_name, data)
    return True, f"injected '{break_type}' into '{vm_name}'"


def list_breaks(vm_name):
    """Return all breaks for a VM."""
    data = _load_breaks(vm_name)
    return data["breaks"]


def diagnose(vm_name):
    """
    Run diagnostics on a VM.
    Return dict: {'vm': name, 'state': 'RUNNING|STOPPED',
                  'issues': [{'type','symptom','detected_at'}],
                  'healthy': bool}
    """
    if not vmm.get(vm_name):
        return None

    st = vmm.status(vm_name)
    breaks = list_breaks(vm_name)
    active = [b for b in breaks if not b.get("resolved")]

    issues = []
    for b in active:
        issues.append({
            "type": b["type"],
            "symptom": b["symptom"],
            "detected_at": b["injected"],
        })

    # Additional runtime checks
    if st["state"] != "RUNNING":
        issues.append({
            "type": "not-running",
            "symptom": f"VM state is {st['state']}",
            "detected_at": now_iso(),
        })

    return {
        "vm": vm_name,
        "state": st["state"],
        "uptime_sec": st["uptime_sec"],
        "issues": issues,
        "healthy": len(issues) == 0,
    }


def resolve(vm_name, break_type):
    """Mark a specific break as resolved."""
    data = _load_breaks(vm_name)
    found = False
    for b in data["breaks"]:
        if b["type"] == break_type and not b.get("resolved"):
            b["resolved"] = now_iso()
            found = True
    if not found:
        return False, f"no active '{break_type}' on '{vm_name}'"
    _save_breaks(vm_name, data)
    return True, f"resolved '{break_type}' on '{vm_name}'"


def auto_fix(vm_name):
    """
    Attempt to fix all active breaks.
    Return (success, [messages]).
    """
    breaks = [b for b in list_breaks(vm_name) if not b.get("resolved")]
    if not breaks:
        return True, ["nothing to fix"]

    messages = []
    for b in breaks:
        btype = b["type"]
        if btype == "service-down":
            vmm.restart(vm_name)
            messages.append(f"restarted VM '{vm_name}' for service-down")
        elif btype == "memory-leak":
            vmm.restart(vm_name)
            messages.append(f"restarted VM '{vm_name}' to clear memory")
        elif btype == "disk-full":
            messages.append("cleaned logs, resized disk (simulated)")
        elif btype == "high-cpu":
            vmm.restart(vm_name)
            messages.append(f"throttled + restarted VM '{vm_name}'")
        elif btype == "network-partition":
            messages.append("re-attached subnet (simulated)")
        # Mark as resolved
        resolve(vm_name, btype)
    return True, messages


def all_breaks_summary():
    """Return list of all broken VMs with active issues."""
    ensure_dir(BREAKAGE_DIR)
    out = []
    for fname in sorted(os.listdir(BREAKAGE_DIR)):
        if not fname.endswith(".json"):
            continue
        vm_name = fname[:-5]
        active = [b for b in list_breaks(vm_name) if not b.get("resolved")]
        if active:
            out.append({
                "vm": vm_name,
                "issues": [b["type"] for b in active],
            })
    return out
