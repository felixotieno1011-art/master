#!/usr/bin/env python3
"""Route table CLI."""
import sys
import utils
from core import vpc as vpc_mod


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


def cmd_create(args):
    flags = parse(args)
    vpc_id = flags.get("vpc-id")
    name = flags.get("name") if isinstance(flags.get("name"), str) else None
    if not vpc_id:
        print(utils.err("usage: aws ec2 create-route-table --vpc-id <vpc-id> [--name <name>]"))
        return 1
    ok_, msg, rt_id = vpc_mod.create_route_table(vpc_id, name=name)
    print(utils.ok(msg) if ok_ else utils.err(msg))
    if ok_:
        print(f"   Route Table ID: {rt_id}")
    return 0 if ok_ else 1


def cmd_add_route(args):
    flags = parse(args)
    rt_id = flags.get("route-table-id")
    cidr = flags.get("destination-cidr-block")
    nat_id = flags.get("nat-gateway-id")
    igw_id = flags.get("gateway-id")
    if not rt_id or not cidr:
        print(utils.err("usage: --route-table-id --destination-cidr-block "
                        "[--nat-gateway-id | --gateway-id]"))
        return 1
    if nat_id:
        ok_, msg = vpc_mod.add_nat_route(rt_id, nat_id, cidr)
    elif igw_id:
        ok_, msg = vpc_mod.add_internet_route(rt_id, igw_id, cidr)
    else:
        print(utils.err("must specify --nat-gateway-id or --gateway-id"))
        return 1
    print(utils.ok(msg) if ok_ else utils.err(msg))
    return 0 if ok_ else 1


def cmd_associate(args):
    flags = parse(args)
    rt_id = flags.get("route-table-id")
    subnet_id = flags.get("subnet-id")
    if not rt_id or not subnet_id:
        print(utils.err("usage: --route-table-id <rt> --subnet-id <subnet>"))
        return 1
    ok_, msg = vpc_mod.associate_subnet(rt_id, subnet_id)
    print(utils.ok(msg) if ok_ else utils.err(msg))
    return 0 if ok_ else 1


def cmd_delete(args):
    # Support both:
    #   aws ec2 delete-route-table <rt-id>                    (positional)
    #   aws ec2 delete-route-table --route-table-id <rt-id>   (real AWS)
    flags = parse(args)
    rt_id = flags.get("route-table-id")
    if not rt_id:
        for a in args:
            if not a.startswith("--"):
                rt_id = a
                break
    if not rt_id:
        print(utils.err("usage: aws ec2 delete-route-table <rt-id> "
                        "OR --route-table-id <rt-id>"))
        return 1
    ok_, msg = vpc_mod.delete_route_table(rt_id)
    print(utils.ok(msg) if ok_ else utils.err(msg))
    return 0 if ok_ else 1


def cmd_delete_route(args):
    flags = parse(args)
    rt_id = flags.get("route-table-id")
    cidr = flags.get("destination-cidr-block")
    if not rt_id or not cidr:
        print(utils.err("usage: aws ec2 delete-route "
                        "--route-table-id <rt> --destination-cidr-block <cidr>"))
        return 1
    ok_, msg = vpc_mod.delete_route(rt_id, cidr)
    print(utils.ok(msg) if ok_ else utils.err(msg))
    return 0 if ok_ else 1


if __name__ == "__main__":
    if len(sys.argv) < 2:
        print("usage: rtb_cli.py <create|add-route|associate|delete> [options]")
        sys.exit(1)
    sub = sys.argv[1]
    args = sys.argv[2:]
    if sub == "create":       sys.exit(cmd_create(args))
    if sub == "delete-route": sys.exit(cmd_delete_route(args))
    if sub == "add-route":    sys.exit(cmd_add_route(args))
    if sub == "associate":    sys.exit(cmd_associate(args))
    if sub == "delete":       sys.exit(cmd_delete(args))
    print(f"unknown subcommand: {sub}")
    sys.exit(1)
