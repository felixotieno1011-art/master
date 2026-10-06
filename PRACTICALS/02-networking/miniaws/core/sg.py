"""Security Groups — per-instance firewalls."""
import os

import config
from utils import (
    now_iso, new_id, make_arn,
    read_json, write_json, delete_file, ensure_dir,
)
from core import account


SG_DIR = os.path.join(config.STATE_DIR, "ec2", "security_groups")


def _sg_path(sg_id):
    return os.path.join(SG_DIR, f"{sg_id}.json")


def _ensure():
    ensure_dir(SG_DIR)


def create_security_group(name, description="", vpc_id=None):
    """Create a new security group."""
    if not name:
        return False, "name required", None

    # Check duplicate name in same VPC
    for sg in list_security_groups(vpc_id=vpc_id):
        if (sg.get("tags") or {}).get("Name") == name:
            return False, f"security group '{name}' already exists", None

    region = account.get_region()
    account_id = account.get_account_id()
    sg_id = new_id("sg")

    data = {
        "groupId": sg_id,
        "arn": make_arn("ec2", region, account_id, f"security-group/{sg_id}"),
        "groupName": name,
        "description": description or f"SG for {name}",
        "vpcId": vpc_id,
        "region": region,
        "ipPermissions": [],           # inbound rules
        "ipPermissionsEgress": [       # outbound rules (default: all)
            {
                "ipProtocol": "-1",
                "fromPort": -1,
                "toPort": -1,
                "ipRanges": [{"CidrIp": "0.0.0.0/0"}],
            }
        ],
        "tags": {"Name": name},
        "created": now_iso(),
    }
    _ensure()
    write_json(_sg_path(sg_id), data)
    return True, f"created security group {sg_id} ({name})", sg_id


def list_security_groups(vpc_id=None):
    _ensure()
    out = []
    if not os.path.isdir(SG_DIR):
        return out
    for f in sorted(os.listdir(SG_DIR)):
        if f.endswith(".json"):
            d = read_json(os.path.join(SG_DIR, f))
            if d and (not vpc_id or d.get("vpcId") == vpc_id):
                out.append(d)
    return out


def get_security_group(sg_id):
    return read_json(_sg_path(sg_id))


def delete_security_group(sg_id):
    sg = get_security_group(sg_id)
    if not sg:
        return False, f"security group {sg_id} not found"
    delete_file(_sg_path(sg_id))
    return True, f"deleted security group {sg_id} ({sg.get('groupName','?')})"


def add_inbound_rule(sg_id, protocol, port, cidr="0.0.0.0/0"):
    """Add an inbound rule: allow <protocol> on <port> from <cidr>."""
    sg = get_security_group(sg_id)
    if not sg:
        return False, f"security group {sg_id} not found"

    try:
        port = int(port)
    except (ValueError, TypeError):
        return False, f"port must be a number"

    if protocol not in ("tcp", "udp", "icmp"):
        return False, f"protocol must be tcp, udp, or icmp"

    # Check for duplicate rule
    for rule in sg["ipPermissions"]:
        if (rule.get("ipProtocol") == protocol
                and rule.get("fromPort") == port
                and rule.get("toPort") == port
                and any(r.get("CidrIp") == cidr for r in rule.get("ipRanges", []))):
            return False, f"rule already exists: {protocol}/{port} from {cidr}"

    sg["ipPermissions"].append({
        "ipProtocol": protocol,
        "fromPort": port,
        "toPort": port,
        "ipRanges": [{"CidrIp": cidr}],
    })
    write_json(_sg_path(sg_id), sg)
    return True, f"added rule: {protocol}/{port} from {cidr}"


def remove_inbound_rule(sg_id, protocol, port, cidr="0.0.0.0/0"):
    """Remove an inbound rule."""
    sg = get_security_group(sg_id)
    if not sg:
        return False, f"security group {sg_id} not found"

    try:
        port = int(port)
    except (ValueError, TypeError):
        return False, f"port must be a number"

    original = len(sg["ipPermissions"])
    sg["ipPermissions"] = [
        r for r in sg["ipPermissions"]
        if not (r.get("ipProtocol") == protocol
                and r.get("fromPort") == port
                and r.get("toPort") == port
                and any(c.get("CidrIp") == cidr for c in r.get("ipRanges", [])))
    ]

    if len(sg["ipPermissions"]) == original:
        return False, f"rule not found: {protocol}/{port} from {cidr}"

    write_json(_sg_path(sg_id), sg)
    return True, f"removed rule: {protocol}/{port} from {cidr}"


def format_rule(rule):
    """Human-readable rule."""
    proto = rule.get("ipProtocol", "?")
    fport = rule.get("fromPort", -1)
    toport = rule.get("toPort", -1)
    cidrs = ", ".join(r.get("CidrIp", "?") for r in rule.get("ipRanges", []))

    if fport == -1:
        port_str = "all"
    elif fport == toport:
        port_str = str(fport)
    else:
        port_str = f"{fport}-{toport}"

    return f"{proto} {port_str} from {cidrs}"
