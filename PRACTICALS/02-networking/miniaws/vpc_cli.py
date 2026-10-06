#!/usr/bin/env python3
"""VPC commands — invoked as: python cli.py vpc <subcmd> OR standalone."""
import sys
import utils
from core import vpc


def cmd_vpc(args):
    if not args:
        print("""
VPC COMMANDS:
  vpc create-vpc --cidr-block <cidr>
  vpc describe-vpcs
  vpc delete-vpc <vpc-id>
  vpc create-subnet --vpc-id <vpc> --cidr-block <cidr> [--name <name>]
  vpc describe-subnets [--vpc-id <vpc>]
  vpc delete-subnet <subnet-id>
  vpc create-internet-gateway [--name <name>]
  vpc describe-internet-gateways
  vpc attach-internet-gateway --igw-id <igw> --vpc-id <vpc>
  vpc detach-internet-gateway --igw-id <igw> --vpc-id <vpc>
  vpc delete-internet-gateway <igw-id>
  vpc describe-route-tables [--vpc-id <vpc>]
  vpc add-internet-route --rt-id <rt> --igw-id <igw>
  vpc associate-subnet --rt-id <rt> --subnet-id <subnet>
""")
        return 1
    sub, rest = args[0], args[1:]
    flags = _parse(rest)

    if sub == "create-vpc":
        cidr = flags.get("cidr-block")
        if not cidr:
            print(utils.err("--cidr-block required")); return 1
        ok_, msg = vpc.create_vpc(cidr)
        print(utils.ok(msg) if ok_ else utils.err(msg))
        return 0 if ok_ else 1

    if sub == "describe-vpcs":
        vs = vpc.list_vpcs()
        if not vs:
            print(utils.warn("no VPCs")); return 0
        print(f"{'VPC ID':<24} {'CIDR':<18} {'REGION':<14} {'STATE':<12}")
        print("-" * 70)
        for v in vs:
            print(f"{v['vpcId']:<24} {v['cidrBlock']:<18} {v['region']:<14} {v['state']:<12}")
        return 0

    if sub == "delete-vpc":
        # Support both syntaxes:
        #   aws ec2 delete-vpc <id>
        #   aws ec2 delete-vpc --vpc-id <id>
        target = None
        if "--vpc-id" in rest:
            idx = rest.index("--vpc-id")
            if idx + 1 < len(rest):
                target = rest[idx + 1]
        elif rest:
            target = rest[0]

        if not target:
            print(utils.err("usage: aws ec2 delete-vpc <vpc-id> OR --vpc-id <vpc-id>"))
            return 1
        ok_, msg = vpc.delete_vpc(target)
        print(utils.ok(msg) if ok_ else utils.err(msg))
        return 0 if ok_ else 1

    if sub == "create-subnet":
        vpc_id = flags.get("vpc-id"); cidr = flags.get("cidr-block")
        name = flags.get("name") if isinstance(flags.get("name"), str) else None
        if not vpc_id or not cidr:
            print(utils.err("--vpc-id and --cidr-block required")); return 1
        ok_, msg = vpc.create_subnet(vpc_id, cidr, name=name)
        print(utils.ok(msg) if ok_ else utils.err(msg))
        return 0 if ok_ else 1

    if sub == "describe-subnets":
        vpc_id = flags.get("vpc-id") if isinstance(flags.get("vpc-id"), str) else None
        subs = vpc.list_subnets(vpc_id=vpc_id)
        if not subs:
            print(utils.warn("no subnets")); return 0
        print(f"{'SUBNET ID':<26} {'VPC':<24} {'CIDR':<18} {'NAME':<14}")
        print("-" * 84)
        for s in subs:
            name = (s.get("tags") or {}).get("Name", "-")
            print(f"{s['subnetId']:<26} {s['vpcId']:<24} {s['cidrBlock']:<18} {name:<14}")
        return 0

    if sub == "delete-subnet":
        target = None
        if "--subnet-id" in rest:
            idx = rest.index("--subnet-id")
            if idx + 1 < len(rest):
                target = rest[idx + 1]
        elif rest:
            target = rest[0]

        if not target:
            print(utils.err("usage: aws ec2 delete-subnet <subnet-id> OR --subnet-id <subnet-id>"))
            return 1
        ok_, msg = vpc.delete_subnet(target)
        print(utils.ok(msg) if ok_ else utils.err(msg))
        return 0 if ok_ else 1

    if sub == "create-internet-gateway":
        name = flags.get("name") if isinstance(flags.get("name"), str) else None
        ok_, msg = vpc.create_internet_gateway(name=name)
        print(utils.ok(msg) if ok_ else utils.err(msg))
        return 0 if ok_ else 1

    if sub == "describe-internet-gateways":
        igws = vpc.list_internet_gateways()
        if not igws:
            print(utils.warn("no internet gateways")); return 0
        print(f"{'IGW ID':<26} {'REGION':<14} {'ATTACHED TO':<30}")
        print("-" * 72)
        for g in igws:
            att = ", ".join(g.get("attachments", [])) or "-"
            print(f"{g['internetGatewayId']:<26} {g['region']:<14} {att:<30}")
        return 0

    if sub == "attach-internet-gateway":
        igw_id = flags.get("igw-id"); vpc_id = flags.get("vpc-id")
        if not igw_id or not vpc_id:
            print(utils.err("--igw-id and --vpc-id required")); return 1
        ok_, msg = vpc.attach_internet_gateway(igw_id, vpc_id)
        print(utils.ok(msg) if ok_ else utils.err(msg))
        return 0 if ok_ else 1

    if sub == "detach-internet-gateway":
        igw_id = flags.get("igw-id"); vpc_id = flags.get("vpc-id")
        if not igw_id or not vpc_id:
            print(utils.err("--igw-id and --vpc-id required")); return 1
        ok_, msg = vpc.detach_internet_gateway(igw_id, vpc_id)
        print(utils.ok(msg) if ok_ else utils.err(msg))
        return 0 if ok_ else 1

    if sub == "delete-internet-gateway":
        if not rest:
            print(utils.err("igw-id required")); return 1
        ok_, msg = vpc.delete_internet_gateway(rest[0])
        print(utils.ok(msg) if ok_ else utils.err(msg))
        return 0 if ok_ else 1

    if sub == "describe-route-tables":
        vpc_id = flags.get("vpc-id") if isinstance(flags.get("vpc-id"), str) else None
        rts = vpc.list_route_tables(vpc_id=vpc_id)
        if not rts:
            print(utils.warn("no route tables")); return 0
        for rt in rts:
            print(f"Route Table: {rt['routeTableId']}  (VPC {rt['vpcId']}) {'[MAIN]' if rt.get('isMain') else ''}")
            for r in rt.get("routes", []):
                print(f"   {r['destinationCidrBlock']:<18} -> {r['gatewayId']}")
            for a in rt.get("associations", []):
                print(f"   associated: {a}")
        return 0

    if sub == "add-internet-route":
        rt_id = flags.get("rt-id"); igw_id = flags.get("igw-id")
        if not rt_id or not igw_id:
            print(utils.err("--rt-id and --igw-id required")); return 1
        ok_, msg = vpc.add_internet_route(rt_id, igw_id)
        print(utils.ok(msg) if ok_ else utils.err(msg))
        return 0 if ok_ else 1

    if sub == "associate-subnet":
        rt_id = flags.get("rt-id"); subnet_id = flags.get("subnet-id")
        if not rt_id or not subnet_id:
            print(utils.err("--rt-id and --subnet-id required")); return 1
        ok_, msg = vpc.associate_subnet(rt_id, subnet_id)
        print(utils.ok(msg) if ok_ else utils.err(msg))
        return 0 if ok_ else 1

    print(utils.err(f"unknown vpc subcommand: {sub}")); return 1


def _parse(args):
    flags = {}
    i = 0
    while i < len(args):
        a = args[i]
        if a.startswith("--"):
            if "=" in a:
                k, v = a[2:].split("=", 1); flags[k] = v
            else:
                k = a[2:]
                if i + 1 < len(args) and not args[i + 1].startswith("--"):
                    flags[k] = args[i + 1]; i += 1
                else:
                    flags[k] = True
        i += 1
    return flags


def main():
    args = sys.argv[1:]
    if not args or args[0] in ("-h", "--help", "help"):
        return cmd_vpc([])
    return cmd_vpc(args)


if __name__ == "__main__":
    sys.exit(main())
