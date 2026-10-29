"""Lambda form actions — create/delete function + sandboxed invoke.

The invoke path uses `subprocess.run` with:
  - timeout=10s
  - isolated cwd (tempfile.mkdtemp, cleaned up after)
  - stripped env (PATH + PYTHONPATH + HOME only, no proxy)
  - handler-only execution via generated wrapper script

The CLI path (`core/lambda_svc.invoke_function`) is NOT modified — it keeps
using `exec()` in-process. The subprocess sandbox lives only here, and only
the browser reaches it.
"""
import json
import os
import shutil
import subprocess
import sys
import tempfile
import time
import urllib.parse
from pathlib import Path

import config
from core import lambda_svc as lam
from core.webui import permissions


# Function detail page lives under this path; last-invoke result is saved here
_LAST_INVOKE_SUFFIX = ".last-invoke.json"


def _redirect(loc):
    return ("redirect", loc)


def _ok(path, msg):
    sep = "&" if "?" in path else "?"
    return _redirect(f"{path}{sep}ok={urllib.parse.quote(str(msg))}")


def _err(path, msg):
    sep = "&" if "?" in path else "?"
    return _redirect(f"{path}{sep}error={urllib.parse.quote(str(msg))}")


def _last_invoke_path(name):
    # IMPORTANT: keep cache OUT of the functions/ dir, otherwise
    # lam.list_functions() would parse these as function definitions.
    return os.path.join(
        config.STATE_DIR, "lambda", "invoke-cache", f"{name}.json"
    )


def handle(path, form, files=None):
    routes = {
        "/lambda/functions/create": _create_function,
        "/lambda/functions/delete": _delete_function,
        "/lambda/functions/invoke": _invoke,
    }
    fn = routes.get(path)
    return fn(form) if fn else None


# ---------- Create ----------

def _create_function(form):
    allowed, err = permissions.require("lambda:CreateFunction", back="/lambda/functions/create")
    if not allowed:
        return err
    name = (form.get("name") or "").strip()
    runtime = (form.get("runtime") or "python3.11").strip()
    handler = (form.get("handler") or "lambda_handler").strip()
    code = form.get("code") or ""

    if not name:
        return _err("/lambda/functions/create", "function name required")
    if not code.strip():
        return _err("/lambda/functions/create", "code required")
    if len(code) > 64 * 1024:
        return _err("/lambda/functions/create", "code too large (max 64 KB)")

    # Write code to a tempfile, then call create_function with code_path
    fd, tmp_path = tempfile.mkstemp(suffix=".py", prefix="lam_")
    try:
        with os.fdopen(fd, "w") as f:
            f.write(code)
        ok_, msg, _ = lam.create_function(
            name, runtime=runtime, handler=handler, code_path=tmp_path,
        )
    finally:
        try:
            os.remove(tmp_path)
        except Exception:
            pass

    if not ok_:
        return _err("/lambda/functions/create", msg)
    return _ok(f"/lambda/functions/{urllib.parse.quote(name)}", msg)


# ---------- Delete ----------

def _delete_function(form):
    name = (form.get("name") or "").strip()
    if not name:
        return _err("/lambda/functions", "name required")
    ok_, msg = lam.delete_function(name)
    if not ok_:
        return _err(f"/lambda/functions/{urllib.parse.quote(name)}", msg)
    # Also remove last-invoke cache
    try:
        os.remove(_last_invoke_path(name))
    except Exception:
        pass
    return _ok("/lambda/functions", msg)


# ---------- Invoke (sandboxed) ----------

def _invoke(form):
    name = (form.get("name") or "").strip()
    allowed, err = permissions.require("lambda:InvokeFunction", back=f"/lambda/functions/{name}?tab=test")
    if not allowed:
        return err
    raw_event = (form.get("event_json") or "{}").strip()
    if not name:
        return _err("/lambda/functions", "name required")

    back = f"/lambda/functions/{urllib.parse.quote(name)}?tab=test"

    # Parse event
    try:
        event = json.loads(raw_event) if raw_event else {}
    except json.JSONDecodeError as e:
        return _err(back, f"invalid event JSON: {e}")

    f = lam.get_function(name)
    if not f:
        return _err("/lambda/functions", f"function '{name}' not found")

    code_path = f.get("CodePath")
    handler_name = f.get("Handler", "lambda_handler")

    if not code_path or not os.path.isfile(code_path):
        return _err(back, f"code file missing for '{name}'")

    # --- Run in subprocess sandbox ---
    result = _run_sandboxed(code_path, handler_name, event)

    # Persist for display on next page load
    try:
        _ensure_dir(os.path.dirname(_last_invoke_path(name)))
        with open(_last_invoke_path(name), "w") as fp:
            json.dump(result, fp, indent=2, default=str)
    except Exception:
        pass

    if result.get("ok"):
        return _ok(back, f"invoked '{name}' in {result.get('duration_ms', '?')} ms")
    return _err(back, result.get("error", "invoke failed"))


def _ensure_dir(path):
    if path:
        os.makedirs(path, exist_ok=True)


def _run_sandboxed(code_path, handler_name, event):
    """Execute handler in an isolated subprocess. Never raises."""
    tmpdir = tempfile.mkdtemp(prefix="lam_invoke_")
    start = time.time()
    try:
        # Write a wrapper that:
        #   1. reads the event from event.json
        #   2. execs the user's code
        #   3. calls handler(event, context)
        #   4. prints the result as JSON on stdout prefixed with a marker
        wrapper_path = os.path.join(tmpdir, "_wrapper.py")
        event_path = os.path.join(tmpdir, "event.json")
        with open(event_path, "w") as fp:
            json.dump(event, fp)

        wrapper_src = f'''
import json, sys, io, traceback

EVENT_PATH = {event_path!r}
CODE_PATH = {code_path!r}
HANDLER_NAME = {handler_name!r}

class _Ctx:
    function_name = "lambda"
    memory_limit_in_mb = 128
    invoked_function_arn = "arn:aws:lambda:::function:local"
    aws_request_id = "req-local"

def main():
    try:
        with open(CODE_PATH) as fp:
            src = fp.read()
        ns = {{"__name__": "lambda_module"}}
        exec(compile(src, CODE_PATH, "exec"), ns)
        handler = ns.get(HANDLER_NAME)
        if handler is None:
            print("__LAMBDA_ERR__:" + json.dumps({{
                "error": f"handler '{{HANDLER_NAME}}' not found"
            }}))
            return 2
        with open(EVENT_PATH) as fp:
            event = json.load(fp)
        result = handler(event, _Ctx())
        print("__LAMBDA_OK__:" + json.dumps(result, default=str))
        return 0
    except BaseException as e:
        tb = traceback.format_exc()
        print("__LAMBDA_ERR__:" + json.dumps({{
            "error": str(e),
            "traceback": tb,
        }}, default=str))
        return 1

if __name__ == "__main__":
    sys.exit(main())
'''
        with open(wrapper_path, "w") as fp:
            fp.write(wrapper_src)

        # Strip environment for safety
        safe_env = {
            "PATH": os.environ.get("PATH", "/system/bin:/usr/bin:/bin"),
            "HOME": tmpdir,
            "TMPDIR": tmpdir,
            "PYTHONPATH": "",
            "PYTHONNOUSERSITE": "1",
            # Deliberately unreachable proxy vars to discourage outbound HTTP
            "HTTP_PROXY": "http://127.0.0.1:1",
            "HTTPS_PROXY": "http://127.0.0.1:1",
        }

        try:
            proc = subprocess.run(
                [sys.executable, wrapper_path],
                cwd=tmpdir,
                env=safe_env,
                capture_output=True,
                timeout=10,
                text=True,
            )
        except subprocess.TimeoutExpired:
            duration_ms = int((time.time() - start) * 1000)
            return {
                "ok": False,
                "error": "timeout (10s) — code did not finish",
                "duration_ms": duration_ms,
                "exit_code": -1,
                "stdout": "",
                "stderr": "",
                "payload": None,
            }

        duration_ms = int((time.time() - start) * 1000)
        stdout = proc.stdout or ""
        stderr = proc.stderr or ""
        exit_code = proc.returncode

        # Look for our markers in stdout
        payload = None
        error = None
        for line in stdout.splitlines():
            if line.startswith("__LAMBDA_OK__:"):
                try:
                    payload = json.loads(line[len("__LAMBDA_OK__:"):])
                except Exception:
                    payload = line[len("__LAMBDA_OK__:"):]
            elif line.startswith("__LAMBDA_ERR__:"):
                try:
                    err_obj = json.loads(line[len("__LAMBDA_ERR__:"):])
                    error = err_obj.get("error", "unknown error")
                    stderr = (stderr + "\n" + err_obj.get("traceback", "")).strip()
                except Exception:
                    error = line[len("__LAMBDA_ERR__:"):]

        ok_ = exit_code == 0 and error is None

        return {
            "ok": ok_,
            "error": error,
            "duration_ms": duration_ms,
            "exit_code": exit_code,
            "stdout": stdout,
            "stderr": stderr,
            "payload": payload,
        }
    except Exception as e:
        duration_ms = int((time.time() - start) * 1000)
        return {
            "ok": False,
            "error": f"sandbox error: {e}",
            "duration_ms": duration_ms,
            "exit_code": -1,
            "stdout": "",
            "stderr": "",
            "payload": None,
        }
    finally:
        shutil.rmtree(tmpdir, ignore_errors=True)
