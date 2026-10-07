#!/usr/bin/env python3
"""DynamoDB CLI."""
import json
import sys
import utils
from core import dynamodb


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


def _parse_key_schema(spec):
    """Parse 'id:S' or 'id:N' or 'pk:S,sk:N' → (name, type)"""
    if not spec:
        return None, None
    first = spec.split(",")[0].strip()
    if ":" in first:
        name, ktype = first.split(":", 1)
        return name.strip(), ktype.strip().upper()
    return first, "S"


def cmd_create_table(args):
    flags = parse(args)
    name = flags.get("table-name")
    schema = flags.get("key-schema")

    if not name or not schema:
        print(utils.err("usage: aws dynamodb create-table "
                        "--table-name <n> --key-schema '<attr>:S'"))
        return 1

    key_name, key_type = _parse_key_schema(schema)
    ok_, msg = dynamodb.create_table(name, key_name, key_type)
    print(utils.ok(msg) if ok_ else utils.err(msg))
    return 0 if ok_ else 1


def cmd_list_tables(args):
    tables = dynamodb.list_tables()
    if "--output" in args and "json" in args:
        print(json.dumps({"TableNames": [t["TableName"] for t in tables]}, indent=2))
        return 0
    if not tables:
        print(utils.warn("no tables"))
        return 0

    print(f"{'TABLE NAME':<30} {'KEY':<15} {'ITEMS':<10} {'STATUS':<12}")
    print("-" * 70)
    for t in tables:
        key = t["KeySchema"][0]["AttributeName"] if t.get("KeySchema") else "-"
        print(f"{t['TableName']:<30} {key:<15} {t.get('ItemCount',0):<10} "
              f"{t.get('TableStatus','-'):<12}")
    return 0


def cmd_delete_table(args):
    flags = parse(args)
    name = flags.get("table-name")
    if not name:
        print(utils.err("usage: aws dynamodb delete-table --table-name <n>"))
        return 1
    ok_, msg = dynamodb.delete_table(name)
    print(utils.ok(msg) if ok_ else utils.err(msg))
    return 0 if ok_ else 1


def cmd_put_item(args):
    flags = parse(args)
    name = flags.get("table-name")
    item_str = flags.get("item")
    if not name or not item_str:
        print(utils.err("usage: aws dynamodb put-item "
                        "--table-name <n> --item '<json>'"))
        return 1
    try:
        item = json.loads(item_str)
    except json.JSONDecodeError as e:
        print(utils.err(f"--item must be valid JSON: {e}"))
        return 1
    ok_, msg = dynamodb.put_item(name, item)
    print(utils.ok(msg) if ok_ else utils.err(msg))
    return 0 if ok_ else 1


def cmd_get_item(args):
    flags = parse(args)
    name = flags.get("table-name")
    key_str = flags.get("key")
    if not name or key_str is None:
        print(utils.err("usage: aws dynamodb get-item "
                        "--table-name <n> --key '<value>'"))
        return 1
    # Accept simple key value or JSON like {"id":"alice"}
    key_value = key_str
    if key_str.startswith("{"):
        try:
            key_obj = json.loads(key_str)
            key_value = list(key_obj.values())[0]
        except Exception as e:
            print(utils.err(f"--key must be valid JSON: {e}"))
            return 1

    ok_, item = dynamodb.get_item(name, key_value)
    if not ok_:
        print(utils.err(item))
        return 1
    if item is None:
        print(utils.warn("item not found"))
        return 0
    print(json.dumps(item, indent=2))
    return 0


def cmd_delete_item(args):
    flags = parse(args)
    name = flags.get("table-name")
    key_str = flags.get("key")
    if not name or key_str is None:
        print(utils.err("usage: aws dynamodb delete-item "
                        "--table-name <n> --key '<value>'"))
        return 1
    key_value = key_str
    if key_str.startswith("{"):
        try:
            key_obj = json.loads(key_str)
            key_value = list(key_obj.values())[0]
        except Exception:
            pass
    ok_, msg = dynamodb.delete_item(name, key_value)
    print(utils.ok(msg) if ok_ else utils.err(msg))
    return 0 if ok_ else 1


def cmd_scan(args):
    flags = parse(args)
    name = flags.get("table-name")
    if not name:
        print(utils.err("usage: aws dynamodb scan --table-name <n>"))
        return 1
    ok_, items = dynamodb.scan_table(name)
    if not ok_:
        print(utils.err(items))
        return 1
    if "--output" in args and "json" in args:
        print(json.dumps({"Items": items, "Count": len(items)}, indent=2))
        return 0
    if not items:
        print(utils.warn("no items"))
        return 0
    print(f"Scan found {len(items)} item(s):")
    for item in items:
        print(json.dumps(item, indent=2))
    return 0


if __name__ == "__main__":
    if len(sys.argv) < 2:
        print("usage: dynamodb_cli.py <create-table|list-tables|put-item|"
              "get-item|delete-item|scan|delete-table>")
        sys.exit(1)
    sub = sys.argv[1]
    args = sys.argv[2:]
    if sub == "create-table":  sys.exit(cmd_create_table(args))
    if sub == "list-tables":   sys.exit(cmd_list_tables(args))
    if sub == "delete-table":  sys.exit(cmd_delete_table(args))
    if sub == "put-item":      sys.exit(cmd_put_item(args))
    if sub == "get-item":      sys.exit(cmd_get_item(args))
    if sub == "delete-item":   sys.exit(cmd_delete_item(args))
    if sub == "scan":          sys.exit(cmd_scan(args))
    print(f"unknown dynamodb subcommand: {sub}")
    sys.exit(1)
