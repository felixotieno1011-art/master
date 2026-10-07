"""Lambda — serverless functions (simulated with real execution)."""
import io
import os
import time
import traceback
from contextlib import redirect_stdout, redirect_stderr

import config
from utils import (
    now_iso, new_id, make_arn,
    read_json, write_json, delete_file, ensure_dir,
)
from core import account


LAMBDA_DIR = os.path.join(config.STATE_DIR, "lambda")
FUNCTIONS_DIR = os.path.join(LAMBDA_DIR, "functions")


def _func_path(name):
    return os.path.join(FUNCTIONS_DIR, f"{name}.json")


def _ensure():
    ensure_dir(FUNCTIONS_DIR)


def create_function(name, runtime="python3.11", handler="lambda_handler",
                    code_path=None, role=None):
    if not name:
        return False, "function name required"
    if not code_path:
        return False, "code file required (--zip-file path/to/file.py)"
    if not os.path.isfile(code_path):
        return False, f"code file not found: {code_path}"

    _ensure()
    with open(code_path) as f:
        code_content = f.read()

    code_dest = os.path.join(FUNCTIONS_DIR, f"{name}.py")
    with open(code_dest, "w") as f:
        f.write(code_content)

    region = account.get_region()
    account_id = account.get_account_id()

    data = {
        "FunctionName": name,
        "FunctionArn": make_arn("lambda", region, account_id, f"function:{name}"),
        "Runtime": runtime,
        "Handler": handler,
        "CodeSize": len(code_content),
        "CodePath": code_dest,
        "Role": role or f"arn:aws:iam::{account_id}:role/lambda-basic-execution",
        "LastModified": now_iso(),
        "State": "Active",
        "Version": "$LATEST",
        "MemorySize": 128,
        "Timeout": 3,
    }
    write_json(_func_path(name), data)
    return True, f"created function '{name}' ({runtime})", name


def list_functions():
    _ensure()
    out = []
    if not os.path.isdir(FUNCTIONS_DIR):
        return out
    for f in sorted(os.listdir(FUNCTIONS_DIR)):
        if f.endswith(".json"):
            d = read_json(os.path.join(FUNCTIONS_DIR, f))
            if d:
                out.append(d)
    return out


def get_function(name):
    return read_json(_func_path(name))


def delete_function(name):
    if not get_function(name):
        return False, f"function '{name}' not found"
    code = os.path.join(FUNCTIONS_DIR, f"{name}.py")
    if os.path.isfile(code):
        os.remove(code)
    delete_file(_func_path(name))
    return True, f"deleted function '{name}'"


def invoke_function(name, event=None):
    f = get_function(name)
    if not f:
        return False, f"function '{name}' not found"

    code_path = f.get("CodePath")
    if not code_path or not os.path.isfile(code_path):
        return False, f"code file missing for '{name}'"

    handler_name = f.get("Handler", "lambda_handler")
    event = event if event is not None else {}

    try:
        ns = {"__name__": "lambda_module"}
        with open(code_path) as fp:
            code = fp.read()

        stdout_buf = io.StringIO()
        stderr_buf = io.StringIO()

        start = time.time()
        with redirect_stdout(stdout_buf), redirect_stderr(stderr_buf):
            exec(compile(code, code_path, "exec"), ns)

            handler = ns.get(handler_name)
            if handler is None:
                return False, f"handler '{handler_name}' not found in code"

            class Context:
                function_name = name
                memory_limit_in_mb = f.get("MemorySize", 128)
                invoked_function_arn = f.get("FunctionArn", "")
                aws_request_id = new_id()

            result = handler(event, Context())

        elapsed_ms = round((time.time() - start) * 1000, 2)

        return True, {
            "StatusCode": 200,
            "FunctionError": None,
            "Payload": result,
            "LogResult": stdout_buf.getvalue(),
            "Stderr": stderr_buf.getvalue(),
            "ExecutedVersion": "$LATEST",
            "Duration": elapsed_ms,
        }
    except Exception as e:
        return False, {
            "error": str(e),
            "traceback": traceback.format_exc(),
        }
