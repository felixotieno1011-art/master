#!/usr/bin/env python3
"""Security Group CLI."""
import sys
import utils
from core import sg


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
    name = flags.get("group-name") or flags.get("name")
    desc = flags.get("description") or ""
    vpc_id = flags.get("vpc-id") if isinstance(flags.get("vpc-id"), str) else None

    if not name:
        print(utils.err("usage: aws ec2 create-security-group "
                        "--group-name <name> --vpc-id <vpc> [--description <text>]"))
        return 1

    ok_, msg, sg_id = sg.create_security_group(name, description=desc, vpc_id=vpc_id)
    print(utils.ok(msg) if ok_ else utils.err(msg))
    if ok_:
        print(f"   Group ID: {sg_id}")
    return 0 if ok_ else 1


def cmd_list(args):
    flags = parse(args)
    vpc_id = flags.get("vpc-id") if isinstance(flags.get("vpc-id"), str) else None
    groups = sg.list_security_groups(vpc_id=vpc_id)

    if not groups:
        print(utils.warn("no security groups"))
        return 0

    for g in groups:
        name = (g.get("tags") or {}).get("Name", "-")
        print(f"Security Group: {g['groupId']}  ({name})")
        print(f"   Description: {g.get('description','-')}")
        print(f"   VPC:         {g.get('vpcId') or '(none)'}")
        print(f"   Inbound rules ({len(g.get('ipPermissions', []))}):")
        if not g.get("ipPermissions"):
            print("     (none — no inbound traffic allowed)")
        else:
            for r in g["ipPermissions"]:
                print(f"     {sg.format_rule(r)}")
        print(f"   Outbound rules ({len(g.get('ipPermissionsEgress', []))}):")
        for r in g.get("ipPermissionsEgress", []):
            print(f"     {sg.format_rule(r)}")
        print()
    return 0


def cmd_delete(args):
    if not args:
        print(utils.err("usage: aws ec2 delete-security-group <sg-id>"))
        return 1
    ok_, msg = sg.delete_security_group(args[0])
    print(utils.ok(msg) if ok_ else utils.err(msg))
    return 0 if ok_ else 1


def cmd_authorize_ingress(args):
    flags = parse(args)
    sg_id = flags.get("group-id")
    protocol = flags.get("protocol") or "tcp"
    port = flags.get("port")
    cidr = flags.get("cidr") or "0.0.0.0/0"

    if not sg_id or port is None:
        print(utils.err("usage: aws ec2 authorize-security-group-ingress "
                        "--group-id <sg> --protocol <tcp|udp|icmp> "
                        "--port <port> [--cidr <cidr>]"))
        return 1

    ok_, msg = sg.add_inbound_rule(sg_id, protocol, port, cidr=cidr)
    print(utils.ok(msg) if ok_ else utils.err(msg))
    return 0 if ok_ else 1


def cmd_revoke_ingress(args):
    flags = parse(args)
    sg_id = flags.get("group-id")
    protocol = flags.get("protocol") or "tcp"
    port = flags.get("port")
    cidr = flags.get("cidr") or "0.0.0.0/0"

    if not sg_id or port is None:
        print(utils.err("usage: aws ec2 revoke-security-group-ingress "
                        "--group-id <sg> --protocol <tcp> --port <port> [--cidr <cidr>]"))
        return 1

    ok_, msg = sg.remove_inbound_rule(sg_id, protocol, port, cidr=cidr)
    print(utils.ok(msg) if ok_ else utils.err(msg))
    return 0 if ok_ else 1


if __name__ == "__main__":
    if len(sys.argv) < 2:
        print("usage: sg_cli.py <create|list|delete|authorize-ingress|revoke-ingress>")
        sys.exit(1)
    sub = sys.argv[1]
    args = sys.argv[2:]

    if sub == "create":             sys.exit(cmd_create(args))
    if sub == "list":               sys.exit(cmd_list(args))
    if sub == "delete":             sys.exit(cmd_delete(args))
    if sub == "authorize-ingress":  sys.exit(cmd_authorize_ingress(args))
    if sub == "revoke-ingress":     sys.exit(cmd_revoke_ingress(args))

    print(f"unknown subcommand: {sub}")
    sys.exit(1)
