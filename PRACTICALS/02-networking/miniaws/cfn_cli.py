#!/usr/bin/env python3
"""CloudFormation CLI."""
import sys
import utils
from core import cfn


def parse(args):
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


USAGE = """
CLOUDFORMATION COMMANDS:
  deploy --stack <name> --template <path>
  list-stacks
  describe-stack <name>
  delete-stack <name>
"""


def cmd(args):
    if not args or args[0] in ("-h", "--help", "help"):
        print(USAGE); return 1
    sub, rest = args[0], args[1:]
    flags = parse(rest)

    if sub == "deploy":
        stack = flags.get("stack"); template = flags.get("template")
        if not stack or not template:
            print(utils.err("--stack and --template required")); return 1
        print(f"🔄 Deploying stack '{stack}' from {template}")
        ok_, summary = cfn.deploy(stack, template)
        if "error" in summary:
            print(utils.err(summary["error"])); return 1
        for logical, rtype, status, pid, msg in summary["details"]:
            icon = "✅" if "COMPLETE" in status else "❌"
            print(f"  {icon} {logical:<20} {rtype:<28} {pid or '-'}")
        print()
        print(f"📊 Stack: {summary['status']} "
              f"({summary['created']} created, {summary['failed']} failed)")
        return 0 if ok_ else 1

    if sub == "list-stacks":
        stacks = cfn.list_stacks()
        if not stacks:
            print(utils.warn("no stacks")); return 0
        print(f"{'STACK':<25} {'STATUS':<20} {'CREATED':<22}")
        print("-" * 70)
        for s in stacks:
            print(f"{s['StackName']:<25} {s['StackStatus']:<20} {s['CreatedTime']:<22}")
        return 0

    if sub == "describe-stack":
        if not rest:
            print(utils.err("stack name required")); return 1
        s = cfn.get_stack(rest[0])
        if not s:
            print(utils.err(f"stack '{rest[0]}' not found")); return 1
        print(f"StackName:   {s['StackName']}")
        print(f"Status:      {s['StackStatus']}")
        print(f"CreatedTime: {s['CreatedTime']}")
        print(f"Template:    {s.get('TemplateFile')}")
        print(f"Resources:")
        for logical, info in s.get("Resources", {}).items():
            print(f"  {logical:<20} {info['Type']:<28} {info['PhysicalId'] or '-'}")
        if s.get("Outputs"):
            print(f"Outputs:")
            for k, v in s["Outputs"].items():
                print(f"  {k} = {v}")
        return 0

    if sub == "delete-stack":
        if not rest:
            print(utils.err("stack name required")); return 1
        ok_, msg = cfn.delete_stack(rest[0])
        print(utils.ok(msg) if ok_ else utils.err(msg))
        return 0 if ok_ else 1

    print(utils.err(f"unknown cloudformation subcommand: {sub}")); return 1


if __name__ == "__main__":
    sys.exit(cmd(sys.argv[1:]))
