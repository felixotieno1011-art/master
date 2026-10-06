"""NAT Gateway — outbound-only internet for private subnets."""
import os

import config
from utils import (
    now_iso, new_id, make_arn,
    read_json, write_json, delete_file, ensure_dir,
)
from core import account
from core import vpc as vpc_mod


NAT_DIR = os.path.join(config.STATE_DIR, "vpc", "nats")


def _nat_path(nat_id):
    return os.path.join(NAT_DIR, f"{nat_id}.json")


def _ensure_dir():
    ensure_dir(NAT_DIR)


def create_nat_gateway(subnet_id):
    """Create a NAT Gateway in the given (public) subnet."""
    subnet = vpc_mod.get_subnet(subnet_id)
    if not subnet:
        return False, f"subnet {subnet_id} not found", None

    vpc_id = subnet["vpcId"]

    # Check that the subnet is actually public
    # (has a route to an IGW)
    rts = vpc_mod.list_route_tables(vpc_id=vpc_id)
    is_public = False
    for rt in rts:
        for r in rt.get("routes", []):
            if r.get("destinationCidrBlock") == "0.0.0.0/0":
                gw = r.get("gatewayId", "")
                if gw.startswith("igw-"):
                    is_public = True
                    break
        if is_public:
            break

    if not is_public:
        return False, (f"subnet {subnet_id} is not public "
                       "(no route to an Internet Gateway). "
                       "NAT Gateways must live in a public subnet."), None

    region = account.get_region()
    account_id = account.get_account_id()

    nat_id = new_id("nat")
    data = {
        "natGatewayId": nat_id,
        "arn": make_arn("ec2", region, account_id, f"natgateway/{nat_id}"),
        "subnetId": subnet_id,
        "vpcId": vpc_id,
        "region": region,
        "state": "available",
        "createTime": now_iso(),
        # In real AWS, a NAT Gateway also has an Elastic IP (public IP).
        # We simulate by assigning a fake one.
        "publicIp": "203.0.113.10",
    }
    _ensure_dir()
    write_json(_nat_path(nat_id), data)
    return True, f"created NAT Gateway {nat_id} in subnet {subnet_id}", nat_id


def list_nat_gateways():
    _ensure_dir()
    out = []
    if not os.path.isdir(NAT_DIR):
        return out
    for f in sorted(os.listdir(NAT_DIR)):
        if f.endswith(".json"):
            d = read_json(os.path.join(NAT_DIR, f))
            if d:
                out.append(d)
    return out


def get_nat_gateway(nat_id):
    return read_json(_nat_path(nat_id))


def delete_nat_gateway(nat_id):
    if not get_nat_gateway(nat_id):
        return False, f"NAT Gateway {nat_id} not found"
    delete_file(_nat_path(nat_id))
    return True, f"deleted NAT Gateway {nat_id}"


def cascade_delete_for_subnet(subnet_id):
    """Delete any NAT Gateways living in the given subnet."""
    count = 0
    for n in list_nat_gateways():
        if n.get("subnetId") == subnet_id:
            delete_file(_nat_path(n["natGatewayId"]))
            count += 1
    return count
