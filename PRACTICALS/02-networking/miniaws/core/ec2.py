"""EC2 instance model — AWS's virtual machines."""
import os
import re

import config
from utils import (
    now_iso, new_id, make_arn,
    read_json, write_json, delete_file, ensure_dir,
)
from core import ec2_runtime
from core import account


NAME_RE = re.compile(r"^[a-zA-Z][a-zA-Z0-9_-]{0,63}$")


def validate_name(name):
    if not name:
        return "name is required"
    if not NAME_RE.match(name):
        return "name must start with a letter, use letters/digits/_/-, max 64 chars"
    return None


def validate_instance_type(t):
    if t not in config.INSTANCE_TYPES:
        valid = ", ".join(config.INSTANCE_TYPES.keys())
        return f"invalid instance type '{t}'. valid: {valid}"
    return None


def _instances_dir():
    d = os.path.join(config.STATE_DIR, "ec2", "instances")
    ensure_dir(d)
    return d


def _instance_path(instance_id):
    return os.path.join(_instances_dir(), f"{instance_id}.json")


def create(name, instance_type="t3.micro", tags=None):
    e = validate_name(name)
    if e: return False, e, None
    e = validate_instance_type(instance_type)
    if e: return False, e, None

    if not account.is_initialized():
        return False, "account not initialized. Run: aws configure", None

    region = account.get_region()
    account_id = account.get_account_id()

    instance_id = new_id("i")
    resource_tags = {"Name": name}
    if tags:
        resource_tags.update(tags)
    for k, v in account.get_tags().items():
        resource_tags.setdefault(k, v)

    t = config.INSTANCE_TYPES[instance_type]

    data = {
        "instance_id": instance_id,
        "arn": make_arn("ec2", region, account_id, f"instance/{instance_id}"),
        "instance_type": instance_type,
        "region": region,
        "state": "pending",
        "hardware": {
            "vcpus": t["vcpus"],
            "memory_mb": t["memory_mb"],
            "disk_gb": t["disk_gb"],
        },
        "tags": resource_tags,
        "launched": now_iso(),
        "account_id": account_id,
    }

    write_json(_instance_path(instance_id), data)

    ok_, msg = ec2_runtime.start(instance_id)
    if not ok_:
        data["state"] = "terminated"
        write_json(_instance_path(instance_id), data)
        return False, f"instance creation failed: {msg}", instance_id

    data["state"] = "running"
    write_json(_instance_path(instance_id), data)

    return True, f"launched EC2 instance {instance_id} ({instance_type})", instance_id


def list_all(region=None):
    d = _instances_dir()
    out = []
    for fname in sorted(os.listdir(d)):
        if not fname.endswith(".json"):
            continue
        data = read_json(os.path.join(d, fname))
        if not data:
            continue
        if region and data.get("region") != region:
            continue
        out.append(data)
    return out


def get(instance_id):
    return read_json(_instance_path(instance_id))


def find_by_name(name):
    for i in list_all():
        if (i.get("tags") or {}).get("Name") == name:
            return i
    return None


def resolve(identifier):
    if identifier.startswith("i-"):
        return get(identifier)
    return find_by_name(identifier)


def terminate(instance_id):
    data = get(instance_id)
    if not data:
        return False, f"instance {instance_id} not found"
    if data.get("state") == "terminated":
        return False, f"instance {instance_id} is already terminated"
    ec2_runtime.stop(instance_id)
    ec2_runtime.delete_runtime_files(instance_id)
    data["state"] = "terminated"
    data["terminated"] = now_iso()
    write_json(_instance_path(instance_id), data)
    return True, f"terminated instance {instance_id}"


def start(instance_id):
    data = get(instance_id)
    if not data:
        return False, f"instance {instance_id} not found"
    if data.get("state") == "terminated":
        return False, "cannot start a terminated instance"
    ok_, msg = ec2_runtime.start(instance_id)
    if ok_:
        data["state"] = "running"
        write_json(_instance_path(instance_id), data)
    return ok_, msg


def stop(instance_id):
    data = get(instance_id)
    if not data:
        return False, f"instance {instance_id} not found"
    ok_, msg = ec2_runtime.stop(instance_id)
    if ok_:
        data["state"] = "stopped"
        write_json(_instance_path(instance_id), data)
    return ok_, msg


def reboot(instance_id):
    data = get(instance_id)
    if not data:
        return False, f"instance {instance_id} not found"
    ec2_runtime.stop(instance_id)
    ok_, msg = ec2_runtime.start(instance_id)
    if ok_:
        data["state"] = "running"
        write_json(_instance_path(instance_id), data)
        return True, f"rebooted instance {instance_id}"
    return False, f"reboot failed: {msg}"


def status(instance_id):
    data = get(instance_id)
    if not data:
        return None
    running = ec2_runtime.is_running(instance_id)
    hb = ec2_runtime.get_heartbeat(instance_id)
    return {
        "instance_id": instance_id,
        "state": data.get("state", "unknown"),
        "runtime_running": running,
        "pid": hb.get("pid") if hb else None,
        "uptime_sec": int(hb.get("uptime_sec", 0)) if hb else 0,
        "instance_type": data.get("instance_type"),
        "region": data.get("region"),
        "name": (data.get("tags") or {}).get("Name"),
    }


def read_proc_stats(pid):
    if not pid:
        return None
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
    except Exception:
        return None
    return info
