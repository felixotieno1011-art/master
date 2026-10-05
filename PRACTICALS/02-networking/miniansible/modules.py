"""
modules.py — loads every module from mods/*.py automatically.

Each mods/waveN.py file should:
  - define helper functions (ssh_run, etc.) by importing from helpers
  - define module functions named  mod_<name>(host, params) -> (changed, ok, msg)
  - NOT register themselves — the loader scans for functions starting with mod_
  - BUT: some module names differ from function names (e.g. mod_get_url → get_url)
    so each wave file may also provide an  EXTRA_NAMES  dict of aliases.
"""

import os
import importlib
import pkgutil

# Shared connection helpers — exposed to all wave files
import subprocess
import time
import base64
import sys

SSH_TIMEOUT = 20

SSH_BASE = [
    "-o", "BatchMode=yes",
    "-o", "StrictHostKeyChecking=accept-new",
    "-o", f"ConnectTimeout={SSH_TIMEOUT}",
]


def ssh_run(host, command):
    cmd = ["ssh", "-p", str(host["port"])] + SSH_BASE + \
          [f'{host["user"]}@{host["host"]}', command]
    try:
        r = subprocess.run(cmd, capture_output=True, text=True,
                           timeout=SSH_TIMEOUT + 5)
        return r.returncode == 0, (r.stdout + r.stderr).strip()
    except subprocess.TimeoutExpired:
        return False, f"timed out after {SSH_TIMEOUT}s"
    except Exception as e:
        return False, f"error: {e}"


def scp_to(host, local_path, remote_path):
    if not os.path.exists(local_path):
        return False, f"local file not found: {local_path}"
    cmd = ["scp", "-P", str(host["port"])] + SSH_BASE + \
          [local_path, f'{host["user"]}@{host["host"]}:{remote_path}']
    try:
        r = subprocess.run(cmd, capture_output=True, text=True,
                           timeout=SSH_TIMEOUT + 10)
        if r.returncode != 0:
            return False, (r.stdout + r.stderr).strip()
        return True, ""
    except Exception as e:
        return False, f"error: {e}"


def scp_from(host, remote_path, local_path):
    cmd = ["scp", "-P", str(host["port"])] + SSH_BASE + \
          [f'{host["user"]}@{host["host"]}:{remote_path}', local_path]
    try:
        r = subprocess.run(cmd, capture_output=True, text=True,
                           timeout=SSH_TIMEOUT + 10)
        if r.returncode != 0:
            return False, (r.stdout + r.stderr).strip()
        return True, ""
    except Exception as e:
        return False, f"error: {e}"


def _expand_remote_var(path):
    return f'F="{path}"; F="${{F/#\\~/$HOME}}"; '


def _fmt_multiline(first, extra):
    if not extra:
        return first
    return first + "\n    " + extra.replace("\n", "\n    ")


# Inject helpers into each wave module when it loads
_HELPERS = {
    "ssh_run": ssh_run,
    "scp_to": scp_to,
    "scp_from": scp_from,
    "_expand_remote_var": _expand_remote_var,
    "_fmt_multiline": _fmt_multiline,
    "subprocess": subprocess,
    "os": os,
    "time": time,
    "base64": base64,
}


_REGISTRY = None


def _discover():
    """Walk mods/*.py, import each, collect mod_* functions into a registry."""
    global _REGISTRY
    if _REGISTRY is not None:
        return _REGISTRY

    registry = {}
    package_dir = os.path.join(os.path.dirname(os.path.abspath(__file__)), "mods")
    if not os.path.isdir(package_dir):
        _REGISTRY = registry
        return registry

    for _, name, _ in pkgutil.iter_modules([package_dir]):
        if name.startswith("_"):
            continue
        mod = importlib.import_module(f"mods.{name}")
        # inject helpers into module namespace
        for k, v in _HELPERS.items():
            setattr(mod, k, v)

        # collect mod_* functions
        for attr in dir(mod):
            if attr.startswith("mod_") and callable(getattr(mod, attr)):
                short = attr[4:]  # strip "mod_" prefix
                registry[short] = getattr(mod, attr)

        # collect aliases
        aliases = getattr(mod, "EXTRA_NAMES", {})
        for alias, fn_name in aliases.items():
            fn = getattr(mod, fn_name, None)
            if fn:
                registry[alias] = fn

    _REGISTRY = registry
    return registry


def get_registry():
    return _discover()


# Placeholder so  from modules import MODULES  doesn't break older code
MODULES = {}
