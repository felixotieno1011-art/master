# ============================================
# NETKIT — core/utils.py
# Shared helpers. Used by every tool.
# ============================================

import socket
import subprocess
from . import config


def resolve(host):
    """Return IP for host, or None."""
    try:
        return socket.gethostbyname(host)
    except Exception:
        return None


def check_port(ip, port, timeout=None):
    """Return True if TCP port is open on ip."""
    timeout = timeout or config.PORT_TIMEOUT
    s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    s.settimeout(timeout)
    try:
        result = s.connect_ex((ip, port))
        return result == 0
    except Exception:
        return False
    finally:
        s.close()


def safe_run(cmd, timeout):
    """Run a shell command. Returns (stdout, stderr, ok)."""
    try:
        r = subprocess.run(
            cmd, capture_output=True, text=True, timeout=timeout
        )
        return r.stdout, r.stderr, r.returncode == 0
    except subprocess.TimeoutExpired:
        return "", "timeout", False
    except FileNotFoundError:
        return "", f"command not found: {cmd[0]}", False
    except Exception as e:
        return "", str(e), False


def tool_exists(name):
    """Check if a binary is available on PATH."""
    from shutil import which
    return which(name) is not None
