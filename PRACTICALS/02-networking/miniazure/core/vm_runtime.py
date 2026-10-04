"""Spawn, stop, and manage simulated VM processes."""
import os
import signal
import subprocess
import sys
import time

import config
from utils import read_json, write_json, ensure_dir


STATE_VMS = os.path.join(config.STATE_DIR, "vms")


def _runtime_dir():
    """Where heartbeat + log files live for VMs."""
    d = os.path.join(STATE_VMS, "runtime")
    ensure_dir(d)
    return d


def _heartbeat_path(name):
    return os.path.join(_runtime_dir(), f"{name}.heartbeat")


def _log_path(name):
    return os.path.join(_runtime_dir(), f"{name}.log")


def is_running(name):
    """Return True if the VM process appears to be alive."""
    hb = read_json(_heartbeat_path(name))
    if not hb:
        return False
    pid = hb.get("pid")
    if not pid:
        return False
    # Check if PID exists (signal 0 = just check)
    try:
        os.kill(pid, 0)
        return True
    except OSError:
        return False


def get_pid(name):
    hb = read_json(_heartbeat_path(name))
    return hb.get("pid") if hb else None


def get_heartbeat(name):
    return read_json(_heartbeat_path(name))


def get_log(name, lines=20):
    path = _log_path(name)
    if not os.path.exists(path):
        return ""
    with open(path) as f:
        all_lines = f.readlines()
    return "".join(all_lines[-lines:])


def start(name):
    """
    Start a VM process. Return (success, message).
    If already running, returns success without spawning again.
    """
    if is_running(name):
        return True, f"VM '{name}' is already running (pid {get_pid(name)})"

    # Prepare environment for the child process
    env = os.environ.copy()
    env["MINIAZURE_VM_NAME"] = name
    env["MINIAZURE_VM_STATE_DIR"] = _runtime_dir()

    # Find project root (one level up from core/)
    project_root = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))

    # Spawn detached
    try:
        proc = subprocess.Popen(
            [sys.executable, "-m", "core.vm_agent"],
            cwd=project_root,
            env=env,
            stdout=subprocess.DEVNULL,
            stderr=subprocess.DEVNULL,
            start_new_session=True,
        )
    except Exception as e:
        return False, f"failed to spawn VM process: {e}"

    # Wait briefly for the heartbeat to appear
    deadline = time.time() + 3
    while time.time() < deadline:
        if _heartbeat_path(name) and is_running(name):
            return True, f"VM '{name}' started (pid {get_pid(name)})"
        time.sleep(0.1)

    return False, "VM process started but did not report heartbeat in time"


def stop(name):
    """
    Stop a running VM process. Return (success, message).
    """
    if not is_running(name):
        return True, f"VM '{name}' is already stopped"

    pid = get_pid(name)
    if not pid:
        return False, f"VM '{name}' has no recorded PID"

    try:
        os.kill(pid, signal.SIGTERM)
    except OSError as e:
        return False, f"failed to signal PID {pid}: {e}"

    # Wait up to 5s for process to disappear
    deadline = time.time() + 5
    while time.time() < deadline:
        if not is_running(name):
            # Clean up heartbeat
            try:
                os.remove(_heartbeat_path(name))
            except Exception:
                pass
            return True, f"VM '{name}' stopped"
        time.sleep(0.2)

    # Force kill
    try:
        os.kill(pid, signal.SIGKILL)
    except OSError:
        pass

    return True, f"VM '{name}' force-stopped (pid {pid})"


def delete_runtime_files(name):
    """Remove heartbeat and log files."""
    for path in (_heartbeat_path(name), _log_path(name)):
        if os.path.exists(path):
            try:
                os.remove(path)
            except Exception:
                pass
