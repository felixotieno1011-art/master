#!/usr/bin/env python3
"""NAT Gateway CLI."""
import sys
import utils
from core import nat

def parse(args):
    flags = {}
    i = 0
    while i < len(args):
        a = args[i]
        if a.startswith("--"):
            if "=" in a:
                k, v = a[2:].split("=", 1)
                flags[k] = v
            else:
                k = a[2:]
                if i + 1 < len(args) and not args[i + 1].startswith("--"):
                    flags[k] = args[i + 1]
                    i += 1
                else:
                    flags[k] = True
        i += 1
    return flags

def print_row(cells, widths):
    print(" ".join(str(c).ljust(w) for c, w in zip(cells, widths)))

def cmd_create(args):
    flags = parse(args)
    subnet = flags.get("subnet-id")
    if not subnet:
        print(utils.err("usage: aws ec2 create-nat-gateway --subnet-id <subnet-id>"))
        return 1
    ok_, msg, nat_id = nat.create_nat_gateway(subnet)
    print(utils.ok(msg) if ok_ else utils.err(msg))
    return 0 if ok_ else 1

def cmd_list(args):
    nats = nat.list_nat_gateways()
    if not nats:
        print(utils.warn("no NAT Gateways"))
        return 0
    print_row(["NAT ID", "SUBNET", "VPC", "STATE", "PUBLIC IP"],
              [22, 22, 22, 12, 16])
    print("-" * 94)
    for n in nats:
        print_row([n["natGatewayId"], n["subnetId"], n["vpcId"],
                   n["state"], n.get("publicIp", "-")],
                  [22, 22, 22, 12, 16])
    return 0

def cmd_delete(args):
    # Support both:
    #   aws ec2 delete-nat-gateway <nat-id>                     (positional)
    #   aws ec2 delete-nat-gateway --nat-gateway-id <nat-id>    (real AWS)
    flags = parse(args)
    nat_id = flags.get("nat-gateway-id")
    if not nat_id:
        for a in args:
            if not a.startswith("--"):
                nat_id = a
                break
    if not nat_id:
        print(utils.err("usage: aws ec2 delete-nat-gateway <nat-id> "
                        "OR --nat-gateway-id <nat-id>"))
        return 1
    ok_, msg = nat.delete_nat_gateway(nat_id)
    print(utils.ok(msg) if ok_ else utils.err(msg))
    return 0 if ok_ else 1

if __name__ == "__main__":
    if len(sys.argv) < 2:
        print("usage: nat_cli.py <create|list|delete> [options]")
        sys.exit(1)
    sub = sys.argv[1]
    args = sys.argv[2:]
    if sub == "create":
        sys.exit(cmd_create(args))
    if sub == "list":
        sys.exit(cmd_list(args))
    if sub == "delete":
        sys.exit(cmd_delete(args))
    print(f"unknown subcommand: {sub}")
    sys.exit(1)
