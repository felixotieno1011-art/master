#!/usr/bin/env python3
"""Billing bridge — find newest resource and record_start.

Called by the `aws` wrapper after a create command succeeds.
Reads state/ to find the newest resource of the given type.
"""
import sys
import os
import json
from pathlib import Path

proj = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(proj))

from lib import billing


def newest_ec2_instance():
    """Return the newest EC2 instance ID + type from state."""
    d = os.path.join(str(proj), "state", "ec2", "instances")
    if not os.path.isdir(d):
        return None, None
    files = sorted(
        (f for f in os.listdir(d) if f.endswith(".json")),
        key=lambda f: os.path.getmtime(os.path.join(d, f)),
        reverse=True,
    )
    for f in files:
        with open(os.path.join(d, f)) as fp:
            data = json.load(fp)
        return data.get("instance_id"), data.get("instance_type")
    return None, None


def newest_nat_gateway():
    d = os.path.join(str(proj), "state", "vpc", "nats")
    if not os.path.isdir(d):
        return None
    files = sorted(
        (f for f in os.listdir(d) if f.endswith(".json")),
        key=lambda f: os.path.getmtime(os.path.join(d, f)),
        reverse=True,
    )
    if files:
        with open(os.path.join(d, files[0])) as fp:
            return json.load(fp).get("natGatewayId")
    return None


def newest_igw():
    d = os.path.join(str(proj), "state", "vpc", "igws")
    if not os.path.isdir(d):
        return None
    files = sorted(
        (f for f in os.listdir(d) if f.endswith(".json")),
        key=lambda f: os.path.getmtime(os.path.join(d, f)),
        reverse=True,
    )
    if files:
        with open(os.path.join(d, files[0])) as fp:
            return json.load(fp).get("internetGatewayId")
    return None


def newest_eip():
    d = os.path.join(str(proj), "state", "ec2", "elastic_ips")
    if not os.path.isdir(d):
        return None
    files = sorted(
        (f for f in os.listdir(d) if f.endswith(".json")),
        key=lambda f: os.path.getmtime(os.path.join(d, f)),
        reverse=True,
    )
    if files:
        with open(os.path.join(d, files[0])) as fp:
            return json.load(fp).get("AllocationId")
    return None


def main(argv):
    if len(argv) < 2:
        return 1
    action = argv[1]
    if action == "ec2":
        rid, itype = newest_ec2_instance()
        if rid:
            rate = billing.PRICING.get(f"ec2.run-instances.{itype}", 0.0104)
            billing.record_start(rid, "ec2", rate)
            return 0
    elif action == "nat":
        rid = newest_nat_gateway()
        if rid:
            billing.record_start(rid, "vpc", 0.045)
            return 0
    elif action == "igw":
        rid = newest_igw()
        if rid:
            billing.record_start(rid, "vpc", 0.045)
            return 0
    elif action == "eip":
        rid = newest_eip()
        if rid:
            billing.record_start(rid, "ec2", 0.005)
            return 0
    return 0


if __name__ == "__main__":
    sys.exit(main(sys.argv))
