#!/usr/bin/env python3
"""MiniAWS CLI — account, region, tag, ec2, s3."""
import sys
import re
import json

import utils
from core import account
from core import ec2
from core import s3
from lib.errors import AWSError, wrap_legacy


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


# --- Strict flag validation + dry-run helpers (added for AWS parity) ---

# Per-subcommand whitelist of accepted flags.
# A flag is the key without leading "--". e.g. "force" for "--force".
# Common flags accepted by every subcommand — match real AWS global options.
COMMON_FLAGS = {
    "dry-run",
    "output",
    "query",
    "region",
    "profile",
    "endpoint-url",
    "debug",
    "no-verify-ssl",
    "no-paginate",
    "no-sign-request",
}

VALID_FLAGS = {
    # S3
    ("s3", "mb"): set(),
    ("s3", "rb"): {"force"},
    ("s3", "ls"): set(),
    ("s3", "cp"): set(),
    ("s3", "rm"): set(),
    ("s3", "sync"): set(),
    # EC2
    ("ec2", "run-instances"):       {"name", "type", "instance-type",
                                     "tag-specifications", "image-id",
                                     "count", "key-name", "security-group-ids",
                                     "subnet-id", "iam-instance-profile"},
    ("ec2", "describe-instances"):  {"instance-ids", "filters", "tag"},
    ("ec2", "describe-instance"):   set(),
    ("ec2", "start-instances"):     {"instance-ids"},
    ("ec2", "stop-instances"):      {"instance-ids"},
    ("ec2", "reboot-instances"):    {"instance-ids"},
    ("ec2", "terminate-instances"): {"instance-ids"},
    ("ec2", "logs"):                set(),
}

# Subcommands that perform a write and should honor --dry-run.
DRY_RUN_COMMANDS = {
    # S3
    ("s3", "mb"),
    ("s3", "rb"),
    ("s3", "cp"),
    ("s3", "rm"),
    # EC2 (writes only — describes ignore --dry-run)
    ("ec2", "run-instances"),
    ("ec2", "start-instances"),
    ("ec2", "stop-instances"),
    ("ec2", "reboot-instances"),
    ("ec2", "terminate-instances"),
}


def strict_flags(service, action, args):
    """Validate flags in args against VALID_FLAGS[service, action].

    Raises AWSError with code UnknownOptions and exit 255 on unknown flag.
    Returns the parsed flags dict (same as parse_flags).
    """
    flags = parse_flags(args)
    allowed = VALID_FLAGS.get((service, action), set()) | COMMON_FLAGS
    for k in flags:
        if k not in allowed:
            raise AWSError(
                code="UnknownOptions",
                message=f"Unknown options: --{k}",
                operation=f"{service}:{action}",
                exit_code=255,
            )
    return flags


# Map (service, action) -> (operation_name, display_verb)
_OP_NAMES = {
    # S3
    ("s3", "mb"): ("CreateBucket", "make_bucket"),
    ("s3", "rb"): ("DeleteBucket", "remove_bucket"),
    ("s3", "cp"): ("PutObject", "upload"),
    ("s3", "rm"): ("DeleteObject", "delete"),
    # EC2
    ("ec2", "run-instances"):       ("RunInstances", "run-instances"),
    ("ec2", "start-instances"):     ("StartInstances", "start-instances"),
    ("ec2", "stop-instances"):      ("StopInstances", "stop-instances"),
    ("ec2", "reboot-instances"):    ("RebootInstances", "reboot-instances"),
    ("ec2", "terminate-instances"): ("TerminateInstances", "terminate-instances"),
}


def check_dry_run(service, action, args):
    """If --dry-run is present and this is a write command, raise DryRunOperation.

    Behavior matches real AWS: exit 255, no side effects, no resource created.
    """
    if (service, action) not in DRY_RUN_COMMANDS:
        return
    flags = parse_flags(args)
    if flags.get("dry-run") in (True, "true"):
        operation, display = _OP_NAMES.get(
            (service, action), (f"{service}:{action}", f"{service}:{action}")
        )
        err = AWSError(
            code="DryRunOperation",
            message="Request would have succeeded, but DryRun flag is set.",
            operation=operation,
            exit_code=255,
        )
        err._operation_display = display
        raise err


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
    # Strict flag validation and dry-run gate (see helpers above).
    check_dry_run("ec2", sub, rest)
    strict_flags("ec2", sub, rest)
    if sub == "run-instances":
        flags = parse_flags(rest)

        # --- Instance name ---
        # Accept: --name <n>  OR  --tag-specifications '...Name,Value=X...'
        name = flags.get("name")
        if not name and isinstance(flags.get("tag-specifications"), str):
            m = re.search(r"Key=Name,Value=([^}\]\s]+)", flags["tag-specifications"])
            if m:
                name = m.group(1)

        # --- Instance type ---
        # Accept: --type <t>  OR  --instance-type <t>
        itype_raw = (flags.get("type")
                     or flags.get("instance-type")
                     or "t3.micro")

        # Map real AWS t2.x names to MiniAWS t3.x
        type_map = {
            "t2.nano": "t3.nano", "t2.micro": "t3.micro",
            "t2.small": "t3.small", "t2.medium": "t3.medium",
            "t2.large": "t3.large",
        }
        itype = type_map.get(itype_raw, itype_raw)

        if not name:
            print(utils.err("--name is required (or use --tag-specifications with Key=Name)"))
            return 1

        ok_, msg, iid = ec2.create(name, instance_type=itype)
        print(utils.ok(msg) if ok_ else utils.err(msg))
        return 0 if ok_ else 1
    if sub == "describe-instances":
        flags = parse_flags(rest)
        filter_id = flags.get("instance-ids") if isinstance(flags.get("instance-ids"), str) else None
        instances = ec2.list_all()
        if filter_id:
            instances = [i for i in instances if i["instance_id"] == filter_id]
            if not instances:
                # Filtered describe on missing ID → error, exit 255
                raise AWSError(
                    code="InvalidInstanceID.NotFound",
                    message=f"The instance ID '{filter_id}' does not exist",
                    operation="DescribeInstances",
                    exit_code=255,
                )
        if not instances:
            # Unfiltered describe with no instances → empty result, exit 0
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
            print(utils.err(f"usage: ec2 {sub} <id-or-name> OR --instance-ids <id>")); return 1
        flags = parse_flags(rest)
        # Support both positional and --instance-ids flag
        if isinstance(flags.get("instance-ids"), str):
            target = flags["instance-ids"]
        else:
            target = None
            for r in rest:
                if not r.startswith("--"):
                    target = r
                    break
        if not target:
            print(utils.err(f"usage: ec2 {sub} <id-or-name> OR --instance-ids <id>")); return 1
        inst = ec2.resolve(target)
        if not inst:
            print(utils.err(f"instance '{target}' not found")); return 1
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
        check_dry_run("s3", "mb", rest[1:])
        strict_flags("s3", "mb", rest[1:])
        bucket, _ = s3.parse_s3_uri(rest[0])
        if not bucket:
            print(utils.err("expected s3://<bucket>")); return 1
        ok_, msg = s3.mb_bucket(bucket)
        if not ok_:
            err = wrap_legacy(
                False, msg,
                operation="CreateBucket",
                resource=f"s3://{bucket}",
            )
            err._operation_display = "make_bucket"
            raise err
        print(utils.ok(msg))
        return 0

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
        check_dry_run("s3", "cp", rest[2:])
        strict_flags("s3", "cp", rest[2:])
        src, dst = rest[0], rest[1]

        if not src.startswith("s3://") and dst.startswith("s3://"):
            # Upload
            bucket, key = s3.parse_s3_uri(dst)
            if not bucket:
                print(utils.err("dest must be s3://<bucket>/[key]")); return 1
            if not key:
                # Trailing slash (or no key) — use source filename
                import os as _os
                key = _os.path.basename(src)
            ok_, msg = s3.put_object(bucket, key, src)
            if not ok_:
                err = wrap_legacy(
                    False, msg,
                    operation="PutObject",
                    resource=f"s3://{bucket}/{key}",
                )
                err._operation_display = "upload"
                raise err
            print(utils.ok(f"upload: {msg}"))
            return 0

        if src.startswith("s3://") and not dst.startswith("s3://"):
            # Download
            bucket, key = s3.parse_s3_uri(src)
            path = s3.get_object_path(bucket, key)
            if not path:
                err = wrap_legacy(
                    False, f"object not found: s3://{bucket}/{key}",
                    operation="GetObject",
                    resource=f"s3://{bucket}/{key}",
                    code="NoSuchKey",
                )
                err._operation_display = "download"
                raise err
            import shutil
            shutil.copy(path, dst)
            print(utils.ok(f"download: {dst}"))
            return 0

        if src.startswith("s3://") and dst.startswith("s3://"):
            # S3 to S3
            sb, sk = s3.parse_s3_uri(src)
            db, dk = s3.parse_s3_uri(dst)
            ok_, msg = s3.cp_object(sb, sk, db, dk)
            if not ok_:
                err = wrap_legacy(
                    False, msg,
                    operation="CopyObject",
                    resource=f"s3://{sb}/{sk}",
                )
                err._operation_display = "copy"
                raise err
            print(utils.ok(msg))
            return 0

        print(utils.err("at least one of src/dst must be s3://...")); return 1

    if sub == "rm":
        if not rest:
            print(utils.err("usage: s3 rm s3://<bucket>/<key>")); return 1
        check_dry_run("s3", "rm", rest[1:])
        strict_flags("s3", "rm", rest[1:])
        bucket, key = s3.parse_s3_uri(rest[0])
        if not bucket or not key:
            print(utils.err("expected s3://<bucket>/<key>")); return 1
        ok_, msg = s3.rm_object(bucket, key)
        if not ok_:
            err = wrap_legacy(
                False, msg,
                operation="DeleteObject",
                resource=f"s3://{bucket}/{key}",
            )
            err._operation_display = "delete"
            raise err
        print(utils.ok(msg))
        return 0

    if sub == "rb":
        if not rest:
            print(utils.err("usage: s3 rb s3://<bucket> [--force]")); return 1
        check_dry_run("s3", "rb", rest[1:])
        strict_flags("s3", "rb", rest[1:])
        bucket, _ = s3.parse_s3_uri(rest[0])
        if not bucket:
            print(utils.err("expected s3://<bucket>")); return 1
        flags = parse_flags(rest[1:])
        force = bool(flags.get("force"))
        ok_, msg = s3.rb_bucket(bucket, force=force)
        if not ok_:
            err = wrap_legacy(
                False, msg,
                operation="DeleteBucket",
                resource=f"s3://{bucket}",
            )
            err._operation_display = "remove_bucket"
            raise err
        print(utils.ok(msg))
        return 0

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


if __name__ == "__main__" and False:
    sys.exit(main())


# ---------- SAFE MAIN (additive, not yet wired) ----------
# Provides a wrapper that catches AWSError and formats it in AWS style.
# The existing main() is unchanged and still the active entry point.
# Wiring to __main__ happens in a later commit.

# JSON output routing — maps (service, action) -> handler key in lib/json_output.py
JSON_HANDLERS = {
    ("ec2", "describe-vpcs"):                "describe-vpcs",
    ("ec2", "describe-subnets"):             "describe-subnets",
    ("ec2", "describe-internet-gateways"):   "describe-internet-gateways",
    ("ec2", "describe-route-tables"):        "describe-route-tables",
    ("ec2", "describe-instances"):           "describe-instances",
    ("ec2", "describe-availability-zones"):  "describe-availability-zones",
    ("s3",  "ls"):                           "list-buckets",
    ("iam", "list-users"):                   "list-users",
    ("iam", "list-access-keys"):             "list-access-keys",
    ("iam", "get-user"):                     "get-user",
    ("iam", "list-groups"):                  "list-groups",
    ("cloudwatch", "list-alarms"):           "list-alarms",
}


def _try_json_output(args):
    """If args contain '--output json' OR '--query <expr>' AND (service, action)
    has a JSON handler, print AWS-shaped JSON (optionally JMESPath-filtered)
    and return True. Otherwise return False.
    """
    # Pull out --output and --query values, collect positional args
    output_format = None
    query_expr = None
    positional = []
    i = 0
    while i < len(args):
        a = args[i]
        if a == "--output" and i + 1 < len(args):
            output_format = args[i + 1]
            i += 2
            continue
        if a.startswith("--output="):
            output_format = a.split("=", 1)[1]
            i += 1
            continue
        if a == "--query" and i + 1 < len(args):
            query_expr = args[i + 1]
            i += 2
            continue
        if a.startswith("--query="):
            query_expr = a.split("=", 1)[1]
            i += 1
            continue
        if a.startswith("--"):
            if i + 1 < len(args) and not args[i + 1].startswith("--"):
                i += 2
            else:
                i += 1
            continue
        positional.append(a)
        i += 1

    # JSON path is triggered by --output json OR by --query (query implies structured output)
    want_json = (output_format == "json") or (query_expr is not None)
    if not want_json:
        return False

    if len(positional) < 2:
        return False

    service = positional[0]
    action = positional[1]
    key = JSON_HANDLERS.get((service, action))
    if not key:
        return False

    import importlib
    jo = importlib.import_module("lib.json_output")
    handler = jo.HANDLERS.get(key)
    if not handler:
        return False

    result = handler()

    # Apply JMESPath if a --query expression was given
    if query_expr:
        try:
            import jmespath
        except ImportError:
            from lib.errors import AWSError
            raise AWSError(
                code="InvalidParameterValue",
                message="--query requires 'jmespath' (pip install jmespath)",
                operation="Query",
                exit_code=255,
            )
        try:
            result = jmespath.search(query_expr, result)
        except Exception as e:
            from lib.errors import AWSError
            raise AWSError(
                code="InvalidParameterValue",
                message=f"Bad --query expression: {e}",
                operation="Query",
                exit_code=255,
            )

    import json as _json
    print(_json.dumps(result, indent=2))
    return True


def safe_main(argv=None):
    """Entry point that handles structured errors.

    Falls back to legacy behavior for commands that still return
    (False, "msg") tuples — they keep working exactly as before.

    Once commands are migrated to raise AWSError, this function
    will format and route them automatically.
    """
    import sys as _sys
    from lib.errors import AWSError, format_aws_error

    args = _sys.argv[1:] if argv is None else argv

    # Try JSON output path first (opt-in via --output json or --query)
    from lib.errors import AWSError as _AWSError, format_aws_error as _fmt_err
    try:
        if _try_json_output(args):
            return 0
    except _AWSError as e:
        _sys.stderr.write(_fmt_err(e) + "\n")
        return e.exit_code
    except Exception as e:
        _sys.stderr.write(f"❌ JSON output failed: {type(e).__name__}: {e}\n")
        return 1

    # Strip global flags that the pretty path doesn't understand, so
    # --output text / --region / --profile don't get parsed as positional args.
    # Values are still available via env vars set by the wrapper.
    _STRIP_OPTS_WITH_VALUE = {"--output", "--query", "--region", "--profile", "--endpoint-url"}
    _STRIP_OPTS_BARE = {"--debug", "--no-verify-ssl", "--no-paginate", "--no-sign-request"}

    clean = []
    i = 0
    while i < len(args):
        a = args[i]
        # --flag=value form
        if any(a.startswith(o + "=") for o in _STRIP_OPTS_WITH_VALUE):
            i += 1
            continue
        # --flag value form
        if a in _STRIP_OPTS_WITH_VALUE:
            i += 2
            continue
        # bare flag
        if a in _STRIP_OPTS_BARE:
            i += 1
            continue
        clean.append(a)
        i += 1

    _sys.argv = [_sys.argv[0]] + clean

    try:
        rc = main()
        return rc if isinstance(rc, int) else 0

    except AWSError as e:
        # Structured error → AWS-style formatting → stderr
        _sys.stderr.write(format_aws_error(e) + "\n")
        return e.exit_code

    except KeyboardInterrupt:
        _sys.stderr.write("\nInterrupted.\n")
        return 130

    except SystemExit as e:
        # Respect explicit sys.exit(N) from existing code
        raise

    except Exception as e:
        # Unexpected — surface it, but don't crash
        _sys.stderr.write(f"❌ {type(e).__name__}: {e}\n")
        return 1


if __name__ == "__main__":
    # Placeholder for future wiring — currently inert.
    # Commit 3 will flip this to:
    #     if __name__ == "__main__":
    #         sys.exit(safe_main())
    sys.exit(safe_main())
