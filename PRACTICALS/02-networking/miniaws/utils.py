"""Helpers for MiniAWS."""
import json
import os
import time
import uuid
from datetime import datetime


# --- Colors ---
RESET  = "\033[0m"
BOLD   = "\033[1m"
GREEN  = "\033[92m"
YELLOW = "\033[93m"
RED    = "\033[91m"
BLUE   = "\033[94m"
GRAY   = "\033[90m"


def ok(msg):    return f"{GREEN}✅ {msg}{RESET}"
def warn(msg):  return f"{YELLOW}⚠️  {msg}{RESET}"
def err(msg):   return f"{RED}❌ {msg}{RESET}"
def info(msg):  return f"{BLUE}ℹ️  {msg}{RESET}"
def dim(msg):   return f"{GRAY}{msg}{RESET}"


def now_iso():
    return datetime.now().isoformat(timespec="seconds")


def new_id(prefix="", length=17):
    """
    Generate an AWS-style ID (hex, no dashes).
    AWS EC2 IDs look like: i-0a1b2c3d4e5f6a7b8 (17 hex chars after prefix)
    """
    s = uuid.uuid4().hex[:length]
    return f"{prefix}-{s}" if prefix else s


def ensure_dir(path):
    os.makedirs(path, exist_ok=True)


def read_json(path):
    if not os.path.exists(path):
        return None
    try:
        with open(path) as f:
            return json.load(f)
    except Exception:
        return None


def write_json(path, data):
    ensure_dir(os.path.dirname(path))
    tmp = path + ".tmp"
    with open(tmp, "w") as f:
        json.dump(data, f, indent=2)
    os.replace(tmp, path)


def delete_file(path):
    if os.path.exists(path):
        os.remove(path)
        return True
    return False


def make_arn(service, region, account_id, resource):
    """
    Build an AWS ARN.
    Format: arn:aws:<service>:<region>:<account>:<resource>
    """
    return f"arn:aws:{service}:{region}:{account_id}:{resource}"


def aws_id_display(id_str, max_len=24):
    """Truncate long AWS IDs for display."""
    if not id_str:
        return "-"
    if len(id_str) <= max_len:
        return id_str
    return id_str[:max_len - 3] + "..."
