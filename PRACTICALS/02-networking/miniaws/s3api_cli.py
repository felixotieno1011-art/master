#!/usr/bin/env python3
"""S3 API CLI — low-level commands matching aws s3api syntax."""
import json
import sys
import utils
from core import s3api


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


def cmd_list_buckets(args):
    data = s3api.list_buckets()
    # Default output: JSON (real s3api defaults to JSON)
    if "--output" in args and "table" in args:
        buckets = data.get("Buckets", [])
        if not buckets:
            print(utils.warn("no buckets"))
            return 0
        print(f"{'BUCKET':<30} {'CREATED':<25}")
        print("-" * 55)
        for b in buckets:
            print(f"{b['Name']:<30} {b.get('CreationDate',''):<25}")
    else:
        print(json.dumps(data, indent=2))
    return 0


def cmd_create_bucket(args):
    flags = parse(args)
    name = flags.get("bucket")
    if not name:
        print(utils.err("usage: aws s3api create-bucket --bucket <name> [--region <r>]"))
        return 1
    ok_, msg = s3api.create_bucket(name)
    print(utils.ok(msg) if ok_ else utils.err(msg))
    return 0 if ok_ else 1


def cmd_list_objects(args):
    flags = parse(args)
    bucket = flags.get("bucket")
    prefix = flags.get("prefix") or ""
    if not bucket:
        print(utils.err("usage: aws s3api list-objects --bucket <name> [--prefix <p>]"))
        return 1
    ok_, result = s3api.list_objects(bucket, prefix=prefix)
    if not ok_:
        print(utils.err(result))
        return 1

    if "--output" in args and "table" in args:
        contents = result.get("Contents", [])
        if not contents:
            print(utils.warn("no objects"))
            return 0
        print(f"{'KEY':<40} {'SIZE':<12} {'MODIFIED':<25}")
        print("-" * 77)
        for o in contents:
            print(f"{o['Key']:<40} {o['Size']:<12} {o.get('LastModified',''):<25}")
    else:
        print(json.dumps(result, indent=2))
    return 0


def cmd_put_object(args):
    flags = parse(args)
    bucket = flags.get("bucket")
    key = flags.get("key")
    body = flags.get("body")
    if not bucket or not key or not body:
        print(utils.err("usage: aws s3api put-object --bucket <b> --key <k> --body <file>"))
        return 1
    ok_, msg = s3api.put_object(bucket, key, body)
    if ok_:
        print(utils.ok(f"uploaded. URL: {msg}"))
    else:
        print(utils.err(msg))
    return 0 if ok_ else 1


def cmd_delete_object(args):
    flags = parse(args)
    bucket = flags.get("bucket")
    key = flags.get("key")
    if not bucket or not key:
        print(utils.err("usage: aws s3api delete-object --bucket <b> --key <k>"))
        return 1
    ok_, msg = s3api.delete_object(bucket, key)
    print(utils.ok(msg) if ok_ else utils.err(msg))
    return 0 if ok_ else 1


def cmd_delete_bucket(args):
    flags = parse(args)
    bucket = flags.get("bucket")
    if not bucket:
        print(utils.err("usage: aws s3api delete-bucket --bucket <name>"))
        return 1
    ok_, msg = s3api.delete_bucket(bucket)
    print(utils.ok(msg) if ok_ else utils.err(msg))
    return 0 if ok_ else 1


def cmd_head_bucket(args):
    flags = parse(args)
    bucket = flags.get("bucket")
    if not bucket:
        print(utils.err("usage: aws s3api head-bucket --bucket <name>"))
        return 1
    ok_, msg = s3api.head_bucket(bucket)
    print(utils.ok(msg) if ok_ else utils.err(msg))
    return 0 if ok_ else 1


if __name__ == "__main__":
    if len(sys.argv) < 2:
        print("usage: s3api_cli.py <command> [options]")
        print("Commands: list-buckets, create-bucket, list-objects,")
        print("          put-object, delete-object, delete-bucket, head-bucket")
        sys.exit(1)
    sub = sys.argv[1]
    args = sys.argv[2:]
    if sub == "list-buckets":   sys.exit(cmd_list_buckets(args))
    if sub == "create-bucket":  sys.exit(cmd_create_bucket(args))
    if sub == "list-objects":   sys.exit(cmd_list_objects(args))
    if sub == "put-object":     sys.exit(cmd_put_object(args))
    if sub == "delete-object":  sys.exit(cmd_delete_object(args))
    if sub == "delete-bucket":  sys.exit(cmd_delete_bucket(args))
    if sub == "head-bucket":    sys.exit(cmd_head_bucket(args))
    print(f"unknown s3api subcommand: {sub}")
    sys.exit(1)
