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

# ---------- Elastic IPs (EIP) ----------

ELASTIC_IPS_DIR = os.path.join(config.STATE_DIR, "ec2", "elastic_ips")


def _eip_path(allocation_id):
    return os.path.join(ELASTIC_IPS_DIR, f"{allocation_id}.json")


def _ensure_eip_dir():
    ensure_dir(ELASTIC_IPS_DIR)


def _fake_public_ip():
    """Generate a deterministic-looking public IP that won't collide."""
    import random
    # AWS uses pools like 54.x, 52.x, 18.x, 3.x
    prefixes = ["54.184", "52.12", "18.234", "3.17", "13.57"]
    p = random.choice(prefixes)
    return f"{p}.{random.randint(1, 254)}.{random.randint(1, 254)}"


def allocate_address(tags=None):
    """Allocate an Elastic IP. Returns (ok, msg, allocation_id)."""
    if not account.is_initialized():
        return False, "account not initialized", None
    _ensure_eip_dir()

    allocation_id = new_id("eipalloc")
    region = account.get_region()
    account_id = account.get_account_id()

    data = {
        "AllocationId": allocation_id,
        "Domain": "vpc",
        "PublicIp": _fake_public_ip(),
        "Region": region,
        "AccountId": account_id,
        "InstanceId": None,
        "AssociationId": None,
        "AssociateTime": None,
        "Tags": tags or {},
        "AllocatedAt": now_iso(),
    }
    write_json(_eip_path(allocation_id), data)
    return True, f"allocated EIP {data['PublicIp']} (id: {allocation_id})", allocation_id


def list_addresses():
    """Return all EIPs."""
    _ensure_eip_dir()
    out = []
    if not os.path.isdir(ELASTIC_IPS_DIR):
        return out
    for f in sorted(os.listdir(ELASTIC_IPS_DIR)):
        if f.endswith(".json"):
            d = read_json(os.path.join(ELASTIC_IPS_DIR, f))
            if d:
                out.append(d)
    return out


def get_address(allocation_id):
    return read_json(_eip_path(allocation_id))


def find_address_by_ip(public_ip):
    for eip in list_addresses():
        if eip.get("PublicIp") == public_ip:
            return eip
    return None


def associate_address(allocation_id, instance_id):
    """Attach an EIP to an instance."""
    eip = get_address(allocation_id)
    if not eip:
        return False, f"EIP {allocation_id} not found"
    if eip.get("InstanceId"):
        return False, f"EIP {allocation_id} is already associated with {eip['InstanceId']}"
    inst = get(instance_id)
    if not inst:
        return False, f"instance {instance_id} not found"
    if (inst.get("state") or "").lower() not in ("running", "pending"):
        return False, f"cannot associate EIP with instance in state '{inst.get('state')}'"
    # Real AWS: each instance can have one EIP
    for other in list_addresses():
        if other.get("InstanceId") == instance_id:
            return False, f"instance {instance_id} already has EIP {other.get('PublicIp')}"

    eip["InstanceId"] = instance_id
    eip["AssociationId"] = new_id("eipassoc")
    eip["AssociateTime"] = now_iso()
    write_json(_eip_path(allocation_id), eip)
    return True, f"associated {eip['PublicIp']} with {instance_id}"


def disassociate_address(allocation_id):
    eip = get_address(allocation_id)
    if not eip:
        return False, f"EIP {allocation_id} not found"
    if not eip.get("InstanceId"):
        return False, f"EIP {allocation_id} is not associated"
    eip["InstanceId"] = None
    eip["AssociationId"] = None
    eip["AssociateTime"] = None
    write_json(_eip_path(allocation_id), eip)
    return True, f"disassociated EIP {allocation_id}"


def release_address(allocation_id):
    eip = get_address(allocation_id)
    if not eip:
        return False, f"EIP {allocation_id} not found"
    if eip.get("InstanceId"):
        return False, f"cannot release EIP {allocation_id} — still associated with {eip['InstanceId']}. Disassociate first."
    delete_file(_eip_path(allocation_id))
    return True, f"released EIP {allocation_id} ({eip.get('PublicIp')})"
