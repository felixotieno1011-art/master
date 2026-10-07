#!/usr/bin/env python3
"""Lambda CLI."""
import json
import sys
import utils
from core import lambda_svc


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
    name = flags.get("function-name")
    runtime = flags.get("runtime") or "python3.11"
    handler = flags.get("handler") or "lambda_handler"
    code = flags.get("zip-file") or flags.get("code")

    if not name or not code:
        print(utils.err("usage: aws lambda create-function "
                        "--function-name <name> --zip-file <path.py> "
                        "[--runtime <r>] [--handler <h>]"))
        return 1

    ok_, msg, _ = lambda_svc.create_function(
        name, runtime=runtime, handler=handler, code_path=code
    )
    print(utils.ok(msg) if ok_ else utils.err(msg))
    return 0 if ok_ else 1


def cmd_list(args):
    funcs = lambda_svc.list_functions()
    if not funcs:
        print(utils.warn("no functions"))
        return 0

    if "--output" in args and "json" in args:
        print(json.dumps({"Functions": funcs}, indent=2))
        return 0

    print(f"{'FUNCTION':<25} {'RUNTIME':<15} {'HANDLER':<20} {'SIZE':<10}")
    print("-" * 75)
    for f in funcs:
        print(f"{f['FunctionName']:<25} {f.get('Runtime','-'):<15} "
              f"{f.get('Handler','-'):<20} {f.get('CodeSize',0):<10}")
    return 0


def cmd_invoke(args):
    flags = parse(args)
    name = flags.get("function-name")
    if not name:
        print(utils.err("usage: aws lambda invoke --function-name <name> "
                        "[--payload <json>]"))
        return 1

    event = {}
    payload_str = flags.get("payload")
    if payload_str:
        try:
            event = json.loads(payload_str)
        except json.JSONDecodeError as e:
            print(utils.err(f"payload must be valid JSON: {e}"))
            return 1

    ok_, result = lambda_svc.invoke_function(name, event)
    if not ok_:
        print(utils.err(result.get("error", "invocation failed")))
        if "traceback" in result:
            print(result["traceback"])
        return 1

    print(f"Status:   {result['StatusCode']}")
    print(f"Duration: {result['Duration']} ms")
    print(f"Payload:")
    print(json.dumps(result["Payload"], indent=2, default=str))
    if result.get("LogResult"):
        print(f"Logs:")
        print(result["LogResult"])
    return 0


def cmd_delete(args):
    flags = parse(args)
    name = flags.get("function-name")
    if not name:
        print(utils.err("usage: aws lambda delete-function --function-name <name>"))
        return 1
    ok_, msg = lambda_svc.delete_function(name)
    print(utils.ok(msg) if ok_ else utils.err(msg))
    return 0 if ok_ else 1


if __name__ == "__main__":
    if len(sys.argv) < 2:
        print("usage: lambda_cli.py <create|list|invoke|delete> [options]")
        sys.exit(1)
    sub = sys.argv[1]
    args = sys.argv[2:]
    if sub == "create":           sys.exit(cmd_create(args))
    if sub == "list":             sys.exit(cmd_list(args))
    if sub == "invoke":           sys.exit(cmd_invoke(args))
    if sub == "delete":           sys.exit(cmd_delete(args))
    print(f"unknown lambda subcommand: {sub}")
    sys.exit(1)
