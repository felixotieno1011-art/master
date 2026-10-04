#!/usr/bin/env python3
"""MiniAWS CLI — account, region, tag, ec2, s3."""
import sys
import json

import utils
from core import account
from core import ec2
from core import s3


USAGE = """
miniaws — a tiny local version of the AWS CLI

ACCOUNT:
  account init [--id <12-digit-id>]
  account show

REGION:
  region list | region set <region> | region get

TAG:
  tag set <key> <value> | tag list | tag delete <key>

EC2:
  ec2 run-instances --name <name> [--type <t3.micro>]
  ec2 describe-instances
  ec2 describe-instance <id-or-name>
  ec2 start-instances | stop-instances | reboot-instances | terminate-instances <id>
  ec2 logs <id-or-name>

S3:
  s3 mb s3://<bucket>
  s3 ls                       (list buckets)
  s3 ls s3://<bucket>/        (list objects)
  s3 cp <local_file> s3://<bucket>/<key>
  s3 cp s3://<bucket>/<key> <local_file>
  s3 rm s3://<bucket>/<key>
  s3 rb s3://<bucket> [--force]

S3 SERVER:
  python -m core.s3_server
"""


def parse_flags(args):
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


# ---------- ACCOUNT ----------

def cmd_account(args):
    if not args:
        print(USAGE); return 1
    sub, rest = args[0], args[1:]
    if sub == "init":
        flags = parse_flags(rest)
        account_id = flags.get("id") if isinstance(flags.get("id"), str) else None
        ok_, msg = account.init_account(account_id)
        print(utils.ok(msg) if ok_ else utils.err(msg))
        return 0 if ok_ else 1
    if sub == "show":
        s = account.summary()
        print(f"Account ID:  {s['account_id']}")
        print(f"Region:      {s['region']}  ({s['region_name']})")
        print(f"Initialized: {s['initialized'] or '-'}")
        if s["tags"]:
            print(f"Tags:")
            for k, v in s["tags"].items():
                print(f"  {k} = {v}")
        else:
            print(f"Tags:        (none)")
        return 0
    print(utils.err(f"unknown account subcommand: {sub}")); return 1


# ---------- REGION ----------

def cmd_region(args):
    if not args:
        print(USAGE); return 1
    sub, rest = args[0], args[1:]
    if sub == "list":
        regions = account.list_regions()
        current = account.get_region()
        print_row(["REGION", "NAME"], [18, 40])
        print("-" * 60)
        for code, name in regions.items():
            marker = " *" if code == current else ""
            print_row([code, name + marker], [18, 40])
        return 0
    if sub == "set":
        if not rest:
            print(utils.err("usage: region set <region>")); return 1
        ok_, msg = account.set_region(rest[0])
        print(utils.ok(msg) if ok_ else utils.err(msg))
        return 0 if ok_ else 1
    if sub == "get":
        print(account.get_region()); return 0
    print(utils.err(f"unknown region subcommand: {sub}")); return 1


# ---------- TAG ----------

def cmd_tag(args):
    if not args:
        print(USAGE); return 1
    sub, rest = args[0], args[1:]
    if sub == "set":
        if len(rest) < 2:
            print(utils.err("usage: tag set <key> <value>")); return 1
        ok_, msg = account.set_tag(rest[0], rest[1])
        print(utils.ok(msg) if ok_ else utils.err(msg))
        return 0 if ok_ else 1
    if sub == "list":
        tags = account.get_tags()
        if not tags:
            print(utils.warn("no tags")); return 0
        print_row(["KEY", "VALUE"], [20, 40])
        print("-" * 62)
        for k, v in tags.items():
            print_row([k, v], [20, 40])
        return 0
    if sub == "delete":
        if not rest:
            print(utils.err("usage: tag delete <key>")); return 1
        ok_, msg = account.delete_tag(rest[0])
        print(utils.ok(msg) if ok_ else utils.err(msg))
        return 0 if ok_ else 1
    print(utils.err(f"unknown tag subcommand: {sub}")); return 1


# ---------- EC2 ----------

def cmd_ec2(args):
    if not args:
        print(USAGE); return 1
    sub, rest = args[0], args[1:]
    if sub == "run-instances":
        flags = parse_flags(rest)
        name = flags.get("name")
        itype = flags.get("type") or "t3.micro"
        if not name:
            print(utils.err("--name is required")); return 1
        ok_, msg, iid = ec2.create(name, instance_type=itype)
        print(utils.ok(msg) if ok_ else utils.err(msg))
        return 0 if ok_ else 1
    if sub == "describe-instances":
        instances = ec2.list_all()
        if not instances:
            print(utils.warn("no instances")); return 0
        print_row(["INSTANCE ID", "NAME", "TYPE", "STATE", "REGION", "PID"],
                  [20, 14, 12, 10, 14, 8])
        print("-" * 80)
        for i in instances:
            st = ec2.status(i["instance_id"]) or {}
            print_row([
                i["instance_id"],
                (i.get("tags") or {}).get("Name", "-"),
                i.get("instance_type"),
                st.get("state") or i.get("state"),
                i.get("region"),
                st.get("pid") or "-",
            ], [20, 14, 12, 10, 14, 8])
        return 0
    if sub == "describe-instance":
        if not rest:
            print(utils.err("usage: ec2 describe-instance <id-or-name>")); return 1
        inst = ec2.resolve(rest[0])
        if not inst:
            print(utils.err(f"instance '{rest[0]}' not found")); return 1
        st = ec2.status(inst["instance_id"]) or {}
        print(f"Instance ID:   {inst['instance_id']}")
        print(f"ARN:           {inst['arn']}")
        print(f"Type:          {inst['instance_type']}")
        print(f"Region:        {inst['region']}")
        print(f"State:         {st.get('state')}")
        print(f"PID:           {st.get('pid') or '-'}")
        print(f"Uptime:        {st.get('uptime_sec', 0)}s")
        print(f"Hardware:      {inst['hardware']['vcpus']} vCPU, "
              f"{inst['hardware']['memory_mb']} MB RAM, {inst['hardware']['disk_gb']} GB disk")
        print(f"Tags:")
        for k, v in (inst.get("tags") or {}).items():
            print(f"   {k} = {v}")
        return 0
    if sub in ("start-instances", "stop-instances", "reboot-instances", "terminate-instances"):
        if not rest:
            print(utils.err(f"usage: ec2 {sub} <id-or-name>")); return 1
        inst = ec2.resolve(rest[0])
        if not inst:
            print(utils.err(f"instance '{rest[0]}' not found")); return 1
        iid = inst["instance_id"]
        if sub == "start-instances":     ok_, msg = ec2.start(iid)
        elif sub == "stop-instances":    ok_, msg = ec2.stop(iid)
        elif sub == "reboot-instances":  ok_, msg = ec2.reboot(iid)
        else:                            ok_, msg = ec2.terminate(iid)
        print(utils.ok(msg) if ok_ else utils.err(msg))
        return 0 if ok_ else 1
    if sub == "logs":
        if not rest:
            print(utils.err("usage: ec2 logs <id-or-name>")); return 1
        inst = ec2.resolve(rest[0])
        if not inst:
            print(utils.err(f"instance '{rest[0]}' not found")); return 1
        print(ec2.ec2_runtime.get_log(inst["instance_id"], lines=30) or "(no logs)")
        return 0
    print(utils.err(f"unknown ec2 subcommand: {sub}")); return 1


# ---------- S3 ----------

def cmd_s3(args):
    if not args:
        print(USAGE); return 1
    sub, rest = args[0], args[1:]

    if sub == "mb":
        if not rest:
            print(utils.err("usage: s3 mb s3://<bucket>")); return 1
        bucket, _ = s3.parse_s3_uri(rest[0])
        if not bucket:
            print(utils.err("expected s3://<bucket>")); return 1
        ok_, msg = s3.mb_bucket(bucket)
        print(utils.ok(msg) if ok_ else utils.err(msg))
        return 0 if ok_ else 1

    if sub == "ls":
        if not rest:
            buckets = s3.ls_buckets()
            if not buckets:
                print(utils.warn("no buckets")); return 0
            print_row(["BUCKET", "REGION", "CREATED"], [24, 14, 20])
            print("-" * 60)
            for b in buckets:
                print_row([b["name"], b.get("region", "?"), b.get("created", "?")],
                          [24, 14, 20])
            return 0
        bucket, key = s3.parse_s3_uri(rest[0])
        if not bucket:
            print(utils.err("expected s3://<bucket>/[prefix]")); return 1
        objs = s3.list_objects(bucket, prefix=key or "")
        if objs is None:
            print(utils.err(f"bucket '{bucket}' not found")); return 1
        if not objs:
            print(utils.warn(f"bucket '{bucket}' is empty")); return 0
        print(f"OBJECTS in s3://{bucket}/")
        print_row(["KEY", "SIZE", "UPLOADED"], [40, 12, 20])
        print("-" * 74)
        for o in objs:
            print_row([o["key"], o["size"], o["uploaded"]], [40, 12, 20])
        return 0

    if sub == "cp":
        if len(rest) < 2:
            print(utils.err("usage: s3 cp <local> s3://<bucket>/<key>  OR  s3 cp s3://<bucket>/<key> <local>")); return 1
        src, dst = rest[0], rest[1]

        if not src.startswith("s3://") and dst.startswith("s3://"):
            # Upload
            bucket, key = s3.parse_s3_uri(dst)
            if not bucket or not key:
                print(utils.err("dest must be s3://<bucket>/<key>")); return 1
            ok_, msg = s3.put_object(bucket, key, src)
            print(utils.ok(f"upload: {msg}") if ok_ else utils.err(msg))
            return 0 if ok_ else 1

        if src.startswith("s3://") and not dst.startswith("s3://"):
            # Download
            bucket, key = s3.parse_s3_uri(src)
            path = s3.get_object_path(bucket, key)
            if not path:
                print(utils.err(f"object not found: s3://{bucket}/{key}")); return 1
            import shutil
            shutil.copy(path, dst)
            print(utils.ok(f"download: {dst}"))
            return 0

        if src.startswith("s3://") and dst.startswith("s3://"):
            # S3 to S3
            sb, sk = s3.parse_s3_uri(src)
            db, dk = s3.parse_s3_uri(dst)
            ok_, msg = s3.cp_object(sb, sk, db, dk)
            print(utils.ok(msg) if ok_ else utils.err(msg))
            return 0 if ok_ else 1

        print(utils.err("at least one of src/dst must be s3://...")); return 1

    if sub == "rm":
        if not rest:
            print(utils.err("usage: s3 rm s3://<bucket>/<key>")); return 1
        bucket, key = s3.parse_s3_uri(rest[0])
        if not bucket or not key:
            print(utils.err("expected s3://<bucket>/<key>")); return 1
        ok_, msg = s3.rm_object(bucket, key)
        print(utils.ok(msg) if ok_ else utils.err(msg))
        return 0 if ok_ else 1

    if sub == "rb":
        if not rest:
            print(utils.err("usage: s3 rb s3://<bucket> [--force]")); return 1
        bucket, _ = s3.parse_s3_uri(rest[0])
        if not bucket:
            print(utils.err("expected s3://<bucket>")); return 1
        flags = parse_flags(rest[1:])
        force = bool(flags.get("force"))
        ok_, msg = s3.rb_bucket(bucket, force=force)
        print(utils.ok(msg) if ok_ else utils.err(msg))
        return 0 if ok_ else 1

    print(utils.err(f"unknown s3 subcommand: {sub}")); return 1


# ---------- MAIN ----------

def main():
    args = sys.argv[1:]
    if not args or args[0] in ("-h", "--help", "help"):
        print(USAGE); return 0

    cmd = args[0]
    if cmd == "account":  return cmd_account(args[1:])
    if cmd == "region":   return cmd_region(args[1:])
    if cmd == "tag":      return cmd_tag(args[1:])
    if cmd == "ec2":      return cmd_ec2(args[1:])
    if cmd == "s3":       return cmd_s3(args[1:])

    print(utils.err(f"unknown command: {cmd}"))
    print(USAGE)
    return 1


if __name__ == "__main__":
    sys.exit(main())
