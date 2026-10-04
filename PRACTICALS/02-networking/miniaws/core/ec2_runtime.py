"""Spawn, stop, and manage EC2 instance processes."""
import os
import signal
import subprocess
import sys
import time

import config
from utils import read_json, ensure_dir


EC2_RUNTIME_DIR = os.path.join(config.STATE_DIR, "ec2", "runtime")


def _runtime_dir():
    ensure_dir(EC2_RUNTIME_DIR)
    return EC2_RUNTIME_DIR


def _heartbeat_path(instance_id):
    return os.path.join(_runtime_dir(), f"{instance_id}.heartbeat")


def _log_path(instance_id):
    return os.path.join(_runtime_dir(), f"{instance_id}.log")


def is_running(instance_id):
    hb = read_json(_heartbeat_path(instance_id))
    if not hb:
        return False
    pid = hb.get("pid")
    if not pid:
        return False
    try:
        os.kill(pid, 0)
        return True
    except OSError:
        return False


def get_pid(instance_id):
    hb = read_json(_heartbeat_path(instance_id))
    return hb.get("pid") if hb else None


def get_heartbeat(instance_id):
    return read_json(_heartbeat_path(instance_id))


def get_log(instance_id, lines=30):
    path = _log_path(instance_id)
    if not os.path.exists(path):
        return ""
    with open(path) as f:
        all_lines = f.readlines()
    return "".join(all_lines[-lines:])


def start(instance_id):
    if is_running(instance_id):
        return True, f"instance {instance_id} already running (pid {get_pid(instance_id)})"

    env = os.environ.copy()
    env["MINIAWS_INSTANCE_ID"] = instance_id
    env["MINIAWS_EC2_STATE_DIR"] = _runtime_dir()

    project_root = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))

    try:
        subprocess.Popen(
            [sys.executable, "-m", "core.ec2_agent"],
            cwd=project_root,
            env=env,
            stdout=subprocess.DEVNULL,
            stderr=subprocess.DEVNULL,
            start_new_session=True,
        )
    except Exception as e:
        return False, f"failed to spawn instance: {e}"

    deadline = time.time() + 3
    while time.time() < deadline:
        if _heartbeat_path(instance_id) and is_running(instance_id):
            return True, f"instance {instance_id} started (pid {get_pid(instance_id)})"
        time.sleep(0.1)

    return False, "instance started but did not report heartbeat"


def stop(instance_id):
    if not is_running(instance_id):
        return True, f"instance {instance_id} already stopped"

    pid = get_pid(instance_id)
    if not pid:
        return False, f"instance {instance_id} has no recorded PID"

    try:
        os.kill(pid, signal.SIGTERM)
    except OSError as e:
        return False, f"failed to signal pid {pid}: {e}"

    deadline = time.time() + 5
    while time.time() < deadline:
        if not is_running(instance_id):
            try:
                os.remove(_heartbeat_path(instance_id))
            except Exception:
                pass
            return True, f"instance {instance_id} stopped"
        time.sleep(0.2)

    try:
        os.kill(pid, signal.SIGKILL)
    except OSError:
        pass
    return True, f"instance {instance_id} force-stopped (pid {pid})"


def delete_runtime_files(instance_id):
    for path in (_heartbeat_path(instance_id), _log_path(instance_id)):
        if os.path.exists(path):
            try:
                os.remove(path)
            except Exception:
                pass
