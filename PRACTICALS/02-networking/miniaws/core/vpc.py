"""VPC, Subnets, Internet Gateway, Route Tables — AWS's network model.

Storage layout:
  state/vpc/vpcs/<vpc-id>.json
  state/vpc/subnets/<subnet-id>.json
  state/vpc/igws/<igw-id>.json
  state/vpc/route_tables/<rtb-id>.json
"""
import os
import ipaddress

import config
from utils import (
    now_iso, new_id, make_arn,
    read_json, write_json, delete_file, ensure_dir,
)
from core import account


VPC_DIR          = os.path.join(config.STATE_DIR, "vpc")
VPCS_DIR         = os.path.join(VPC_DIR, "vpcs")
SUBNETS_DIR      = os.path.join(VPC_DIR, "subnets")
IGWS_DIR         = os.path.join(VPC_DIR, "igws")
ROUTE_TABLES_DIR = os.path.join(VPC_DIR, "route_tables")


def _parse_cidr(cidr):
    try:
        return ipaddress.ip_network(cidr, strict=False)
    except Exception:
        return None


# ---------- VPC ----------

def _vpc_path(vpc_id):
    return os.path.join(VPCS_DIR, f"{vpc_id}.json")


def create_vpc(cidr_block):
    net = _parse_cidr(cidr_block)
    if not net:
        return False, f"invalid CIDR: {cidr_block}"
    if net.prefixlen > 24:
        return False, f"VPC CIDR too small ({cidr_block}). Use /16 to /24."
    if not account.is_initialized():
        return False, "account not initialized"

    # Overlap check against existing VPCs in this region
    region = account.get_region()
    for v in list_vpcs():
        if v.get("region") != region:
            continue
        existing = _parse_cidr(v["cidrBlock"])
        if existing and existing.overlaps(net):
            return False, (f"CIDR {cidr_block} overlaps with "
                           f"vpc {v['vpcId']} ({v['cidrBlock']})")

    vpc_id = new_id("vpc")
    account_id = account.get_account_id()

    data = {
        "vpcId": vpc_id,
        "arn": make_arn("ec2", region, account_id, f"vpc/{vpc_id}"),
        "cidrBlock": str(net),
        "region": region,
        "state": "available",
        "isDefault": False,
        "tags": {},
        "created": now_iso(),
    }
    ensure_dir(VPCS_DIR)
    write_json(_vpc_path(vpc_id), data)

    # AWS auto-creates a main route table for each VPC
    _create_main_route_table(vpc_id, region)

    return True, f"created VPC {vpc_id} ({net})"


def list_vpcs():
    ensure_dir(VPCS_DIR)
    out = []
    for f in sorted(os.listdir(VPCS_DIR)):
        if f.endswith(".json"):
            d = read_json(os.path.join(VPCS_DIR, f))
            if d:
                out.append(d)
    return out


def get_vpc(vpc_id):
    return read_json(_vpc_path(vpc_id))


def delete_vpc(vpc_id):
    v = get_vpc(vpc_id)
    if not v:
        return False, f"VPC {vpc_id} not found"

    # Refuse if subnets exist
    for s in list_subnets(vpc_id=vpc_id):
        return False, f"VPC has subnets (e.g. {s['subnetId']}). Delete them first."

    # Cascade delete: remove route tables belonging to this VPC
    if os.path.isdir(ROUTE_TABLES_DIR):
        for fname in os.listdir(ROUTE_TABLES_DIR):
            if not fname.endswith(".json"):
                continue
            rt_path = os.path.join(ROUTE_TABLES_DIR, fname)
            rt = read_json(rt_path)
            if rt and rt.get("vpcId") == vpc_id:
                delete_file(rt_path)

    delete_file(_vpc_path(vpc_id))
    return True, f"deleted VPC {vpc_id}"


# ---------- Subnet ----------

def _subnet_path(subnet_id):
    return os.path.join(SUBNETS_DIR, f"{subnet_id}.json")


def create_subnet(vpc_id, cidr_block, name=None):
    vpc = get_vpc(vpc_id)
    if not vpc:
        return False, f"VPC {vpc_id} not found"

    net = _parse_cidr(cidr_block)
    if not net:
        return False, f"invalid CIDR: {cidr_block}"

    vpc_net = _parse_cidr(vpc["cidrBlock"])
    if not net.subnet_of(vpc_net):
        return False, f"subnet {cidr_block} not inside VPC range {vpc['cidrBlock']}"

    # Overlap check with other subnets in same VPC
    for s in list_subnets(vpc_id=vpc_id):
        existing = _parse_cidr(s["cidrBlock"])
        if existing and existing.overlaps(net):
            return False, (f"subnet {cidr_block} overlaps with "
                           f"{s['subnetId']} ({s['cidrBlock']})")

    region = account.get_region()
    account_id = account.get_account_id()
    subnet_id = new_id("subnet")

    tags = {"Name": name} if name else {}

    data = {
        "subnetId": subnet_id,
        "arn": make_arn("ec2", region, account_id, f"subnet/{subnet_id}"),
        "vpcId": vpc_id,
        "cidrBlock": str(net),
        "region": region,
        "availabilityZone": f"{region}a",
        "availableIpCount": max(0, net.num_addresses - 5),  # AWS reserves 5
        "state": "available",
        "mapPublicIpOnLaunch": False,
        "tags": tags,
        "created": now_iso(),
    }
    ensure_dir(SUBNETS_DIR)
    write_json(_subnet_path(subnet_id), data)
    return True, f"created subnet {subnet_id} ({net}) in VPC {vpc_id}"


def list_subnets(vpc_id=None):
    ensure_dir(SUBNETS_DIR)
    out = []
    for f in sorted(os.listdir(SUBNETS_DIR)):
        if f.endswith(".json"):
            d = read_json(os.path.join(SUBNETS_DIR, f))
            if d and (not vpc_id or d.get("vpcId") == vpc_id):
                out.append(d)
    return out


def get_subnet(subnet_id):
    return read_json(_subnet_path(subnet_id))


def delete_subnet(subnet_id):
    if not get_subnet(subnet_id):
        return False, f"subnet {subnet_id} not found"
    delete_file(_subnet_path(subnet_id))
    return True, f"deleted subnet {subnet_id}"


# ---------- Internet Gateway ----------

def _igw_path(igw_id):
    return os.path.join(IGWS_DIR, f"{igw_id}.json")


def create_internet_gateway(name=None):
    if not account.is_initialized():
        return False, "account not initialized"
    region = account.get_region()
    account_id = account.get_account_id()
    igw_id = new_id("igw")

    data = {
        "internetGatewayId": igw_id,
        "arn": make_arn("ec2", region, account_id, f"internet-gateway/{igw_id}"),
        "region": region,
        "state": "available",
        "attachments": [],   # list of vpc_ids
        "tags": {"Name": name} if name else {},
        "created": now_iso(),
    }
    ensure_dir(IGWS_DIR)
    write_json(_igw_path(igw_id), data)
    return True, f"created internet gateway {igw_id}"


def list_internet_gateways():
    ensure_dir(IGWS_DIR)
    out = []
    for f in sorted(os.listdir(IGWS_DIR)):
        if f.endswith(".json"):
            d = read_json(os.path.join(IGWS_DIR, f))
            if d:
                out.append(d)
    return out


def get_internet_gateway(igw_id):
    return read_json(_igw_path(igw_id))


def attach_internet_gateway(igw_id, vpc_id):
    igw = get_internet_gateway(igw_id)
    if not igw:
        return False, f"internet gateway {igw_id} not found"
    vpc = get_vpc(vpc_id)
    if not vpc:
        return False, f"VPC {vpc_id} not found"
    if vpc_id in igw.get("attachments", []):
        return False, f"IGW {igw_id} already attached to {vpc_id}"
    igw.setdefault("attachments", []).append(vpc_id)
    write_json(_igw_path(igw_id), igw)
    return True, f"attached IGW {igw_id} to VPC {vpc_id}"


def detach_internet_gateway(igw_id, vpc_id):
    igw = get_internet_gateway(igw_id)
    if not igw:
        return False, f"internet gateway {igw_id} not found"
    if vpc_id not in igw.get("attachments", []):
        return False, f"IGW {igw_id} not attached to {vpc_id}"
    igw["attachments"].remove(vpc_id)
    write_json(_igw_path(igw_id), igw)
    return True, f"detached IGW {igw_id} from VPC {vpc_id}"


def delete_internet_gateway(igw_id):
    igw = get_internet_gateway(igw_id)
    if not igw:
        return False, f"internet gateway {igw_id} not found"
    if igw.get("attachments"):
        return False, f"IGW still attached to {igw['attachments']}"
    delete_file(_igw_path(igw_id))
    return True, f"deleted internet gateway {igw_id}"


# ---------- Route Tables ----------

def _rt_path(rt_id):
    return os.path.join(ROUTE_TABLES_DIR, f"{rt_id}.json")


def _create_main_route_table(vpc_id, region):
    """AWS auto-creates a main route table when a VPC is created."""
    rt_id = new_id("rtb")
    data = {
        "routeTableId": rt_id,
        "vpcId": vpc_id,
        "region": region,
        "isMain": True,
        "routes": [
            {"destinationCidrBlock": "local", "gatewayId": "local", "state": "active"},
        ],
        "associations": [],
        "created": now_iso(),
    }
    ensure_dir(ROUTE_TABLES_DIR)
    write_json(_rt_path(rt_id), data)
    return rt_id


def get_route_table(rt_id):
    return read_json(_rt_path(rt_id))


def find_main_route_table(vpc_id):
    """Find the main (auto-created) route table for a VPC."""
    for f in sorted(os.listdir(ROUTE_TABLES_DIR)) if os.path.isdir(ROUTE_TABLES_DIR) else []:
        if not f.endswith(".json"):
            continue
        d = read_json(os.path.join(ROUTE_TABLES_DIR, f))
        if d and d.get("vpcId") == vpc_id and d.get("isMain"):
            return d
    return None


def list_route_tables(vpc_id=None):
    ensure_dir(ROUTE_TABLES_DIR)
    out = []
    for f in sorted(os.listdir(ROUTE_TABLES_DIR)):
        if f.endswith(".json"):
            d = read_json(os.path.join(ROUTE_TABLES_DIR, f))
            if d and (not vpc_id or d.get("vpcId") == vpc_id):
                out.append(d)
    return out


def add_internet_route(rt_id, igw_id):
    """Add 0.0.0.0/0 route via the given IGW."""
    rt = get_route_table(rt_id)
    if not rt:
        return False, f"route table {rt_id} not found"
    # Remove existing default route if any
    rt["routes"] = [r for r in rt["routes"]
                    if r.get("destinationCidrBlock") != "0.0.0.0/0"]
    rt["routes"].append({
        "destinationCidrBlock": "0.0.0.0/0",
        "gatewayId": igw_id,
        "state": "active",
    })
    write_json(_rt_path(rt_id), rt)
    return True, f"added route 0.0.0.0/0 -> {igw_id}"


def associate_subnet(rt_id, subnet_id):
    rt = get_route_table(rt_id)
    if not rt:
        return False, f"route table {rt_id} not found"
    if not get_subnet(subnet_id):
        return False, f"subnet {subnet_id} not found"
    if subnet_id in rt.get("associations", []):
        return False, f"subnet {subnet_id} already associated"
    rt.setdefault("associations", []).append(subnet_id)
    write_json(_rt_path(rt_id), rt)
    return True, f"associated subnet {subnet_id} with route table {rt_id}"


def create_route_table(vpc_id, name=None):
    """Create a new (non-main) route table for a VPC."""
    v = get_vpc(vpc_id)
    if not v:
        return False, f"VPC {vpc_id} not found", None

    region = account.get_region()
    rt_id = new_id("rtb")

    data = {
        "routeTableId": rt_id,
        "vpcId": vpc_id,
        "region": region,
        "isMain": False,
        "routes": [
            {"destinationCidrBlock": "local", "gatewayId": "local", "state": "active"},
        ],
        "associations": [],
        "tags": {"Name": name} if name else {},
        "created": now_iso(),
    }
    ensure_dir(ROUTE_TABLES_DIR)
    write_json(_rt_path(rt_id), data)
    return True, f"created route table {rt_id}", rt_id


def add_nat_route(rt_id, nat_id):
    """Add a 0.0.0.0/0 route via the given NAT Gateway."""
    rt = get_route_table(rt_id)
    if not rt:
        return False, f"route table {rt_id} not found"

    from core import nat
    if not nat.get_nat_gateway(nat_id):
        return False, f"NAT Gateway {nat_id} not found"

    # Remove existing default route if any
    rt["routes"] = [r for r in rt["routes"]
                    if r.get("destinationCidrBlock") != "0.0.0.0/0"]
    rt["routes"].append({
        "destinationCidrBlock": "0.0.0.0/0",
        "gatewayId": nat_id,
        "state": "active",
    })
    write_json(_rt_path(rt_id), rt)
    return True, f"added route 0.0.0.0/0 -> {nat_id}"


def delete_route_table(rt_id):
    """Delete a route table. Refuses if it's the main one."""
    rt = get_route_table(rt_id)
    if not rt:
        return False, f"route table {rt_id} not found"
    if rt.get("isMain"):
        return False, f"cannot delete the main route table"
    delete_file(_rt_path(rt_id))
    return True, f"deleted route table {rt_id}"
