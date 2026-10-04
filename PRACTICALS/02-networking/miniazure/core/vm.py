"""VM resource operations — like `az vm` in real Azure."""
import os
import re

import config
from utils import (
    ok, err, now_iso, short_id,
    read_json, write_json, delete_file, ensure_dir,
)
from core import vm_runtime
from core import resource_group as rg


NAME_RE = re.compile(r"^[a-zA-Z][a-zA-Z0-9-]{1,62}[a-zA-Z0-9]$")


def validate_name(name):
    if not name:
        return "name is required"
    if not NAME_RE.match(name):
        return ("name must be 3-64 chars, start with a letter, "
                "end with a letter or digit, contain letters/digits/hyphens only")
    return None


def validate_size(size):
    if size not in config.VALID_VM_SIZES:
        return (f"invalid size '{size}'. "
                f"valid: {', '.join(config.VALID_VM_SIZES.keys())}")
    return None


def _vm_path(name):
    return os.path.join(config.STATE_DIR, "vms", f"{name}.json")


def create(name, group, size="small", region=None):
    """Create (and start) a VM. Return (success, message)."""
    # Validate
    e = validate_name(name)
    if e:
        return False, e
    e = validate_size(size)
    if e:
        return False, e

    # Check VM name not used
    if os.path.exists(_vm_path(name)):
        return False, f"VM '{name}' already exists"

    # Check group exists
    group_data = rg.get(group)
    if not group_data:
        return False, f"resource group '{group}' not found. Create it first."

    region = region or group_data.get("location", config.DEFAULT_REGION)

    # Build state
    vm_size = config.VALID_VM_SIZES[size]
    data = {
        "id": f"/subscriptions/local/resourceGroups/{group}/providers/Microsoft.Compute/virtualMachines/{name}",
        "name": name,
        "type": "Microsoft.Compute/virtualMachines",
        "location": region,
        "resourceGroup": group,
        "size": size,
        "hardware": {
            "vcpus": vm_size["cpu"],
            "memoryMB": vm_size["ram_mb"],
            "diskGB": vm_size["disk_gb"],
        },
        "properties": {
            "provisioningState": "Succeeded",
        },
        "created": now_iso(),
    }

    ensure_dir(os.path.join(config.STATE_DIR, "vms"))
    write_json(_vm_path(name), data)

    # Start the process
    ok_, msg = vm_runtime.start(name)
    if not ok_:
        # Roll back metadata if the process failed
        delete_file(_vm_path(name))
        return False, f"VM created but failed to start: {msg}"

    return True, f"VM '{name}' created and running in group '{group}' (size {size})"


def list_all(group=None):
    """Return list of VM dicts. If group given, filter by group."""
    d = os.path.join(config.STATE_DIR, "vms")
    ensure_dir(d)
    vms = []
    for fname in sorted(os.listdir(d)):
        if not fname.endswith(".json"):
            continue
        data = read_json(os.path.join(d, fname))
        if not data:
            continue
        if group and data.get("resourceGroup") != group:
            continue
        vms.append(data)
    return vms


def get(name):
    return read_json(_vm_path(name))


def delete(name):
    """Stop and remove a VM."""
    data = get(name)
    if not data:
        return False, f"VM '{name}' not found"

    # Stop first
    vm_runtime.stop(name)
    vm_runtime.delete_runtime_files(name)

    # Remove metadata
    delete_file(_vm_path(name))
    return True, f"VM '{name}' deleted"


def start(name):
    if not get(name):
        return False, f"VM '{name}' not found"
    return vm_runtime.start(name)


def stop(name):
    if not get(name):
        return False, f"VM '{name}' not found"
    return vm_runtime.stop(name)


def restart(name):
    if not get(name):
        return False, f"VM '{name}' not found"
    vm_runtime.stop(name)
    return vm_runtime.start(name)


def status(name):
    """Return a dict with runtime status info."""
    data = get(name)
    if not data:
        return None
    running = vm_runtime.is_running(name)
    hb = vm_runtime.get_heartbeat(name)
    return {
        "name": name,
        "state": "RUNNING" if running else "STOPPED",
        "pid": hb.get("pid") if hb else None,
        "uptime_sec": int(hb.get("uptime", 0)) if hb else 0,
        "size": data.get("size"),
        "group": data.get("resourceGroup"),
    }


def read_proc_stats(pid):
    """Read real CPU/memory info from /proc/<pid>/."""
    if not pid:
        return None
    stat_path = f"/proc/{pid}/stat"
    status_path = f"/proc/{pid}/status"
    if not os.path.exists(status_path):
        return None
    info = {"pid": pid}
    try:
        with open(status_path) as f:
            for line in f:
                if line.startswith("VmRSS:"):
                    info["memory_kb"] = int(line.split()[1])
                elif line.startswith("State:"):
                    info["proc_state"] = line.split()[1]
        with open(stat_path) as f:
            fields = f.read().split()
            # Fields 14 & 15 are utime & stime (in clock ticks)
            info["utime_ticks"] = int(fields[13])
            info["stime_ticks"] = int(fields[14])
    except Exception:
        return None
    return info
