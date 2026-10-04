"""Small helpers used everywhere."""
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
    """ISO timestamp for state files."""
    return datetime.now().isoformat(timespec="seconds")


def short_id(prefix=""):
    """Short random ID, like Azure resource IDs."""
    s = uuid.uuid4().hex[:8]
    return f"{prefix}-{s}" if prefix else s


def ensure_dir(path):
    os.makedirs(path, exist_ok=True)


def read_json(path):
    """Read JSON file. Return None if missing or broken."""
    if not os.path.exists(path):
        return None
    try:
        with open(path) as f:
            return json.load(f)
    except Exception:
        return None


def write_json(path, data):
    """Atomically write JSON file."""
    ensure_dir(os.path.dirname(path))
    tmp = path + ".tmp"
    with open(tmp, "w") as f:
        json.dump(data, f, indent=2)
    os.replace(tmp, path)


def delete_file(path):
    """Delete file if it exists. Return True if deleted."""
    if os.path.exists(path):
        os.remove(path)
        return True
    return False
