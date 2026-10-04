"""IAM: users, roles, permissions, login, audit.

Roles (in order of power):
  reader       - read-only
  contributor  - can create/modify/delete (but not users)
  admin        - everything
"""
import os
import re

import config
from utils import now_iso, read_json, write_json, ensure_dir


IAM_DIR      = os.path.join(config.STATE_DIR, "iam")
USERS_FILE   = os.path.join(IAM_DIR, "users.json")
CURRENT_FILE = os.path.join(IAM_DIR, "current_user.json")
AUDIT_FILE   = os.path.join(IAM_DIR, "audit.log")


ROLES = {
    "reader":      {"level": 1},
    "contributor": {"level": 2},
    "admin":       {"level": 3},
}


ACTION_LEVELS = {
    # read-only
    "group.list": 1, "group.show": 1,
    "vm.list": 1, "vm.show": 1, "vm.stats": 1, "vm.logs": 1,
    "vm.diagnose": 1,
    "storage.list": 1, "storage.show": 1,
    "storage.container.list": 1, "storage.blob.list": 1,
    "network.vnet.list": 1, "network.vnet.show": 1,
    "network.subnet.list": 1, "network.topology": 1,
    "monitor.status": 1, "monitor.alerts": 1,

    # mutating
    "group.create": 2, "group.delete": 2,
    "vm.create": 2, "vm.delete": 2, "vm.start": 2, "vm.stop": 2,
    "vm.restart": 2, "vm.attach": 2, "vm.detach": 2,
    "vm.break": 2, "vm.fix": 2,
    "storage.create": 2, "storage.delete": 2,
    "storage.container.create": 2, "storage.container.delete": 2,
    "storage.upload": 2, "storage.blob.delete": 2,
    "network.vnet.create": 2, "network.vnet.delete": 2,
    "network.subnet.create": 2, "network.subnet.delete": 2,
    "monitor.start": 2, "monitor.stop": 2,
    "deploy.apply": 2,

    # admin
    "user.create": 3, "user.delete": 3, "user.list": 3,
    "user.role": 3,
}


USERNAME_RE = re.compile(r"^[a-z][a-z0-9_-]{1,30}$")


def validate_username(name):
    if not name: return "username required"
    if not USERNAME_RE.match(name):
        return "username must start with a letter, 2-31 chars, lowercase"
    return None


def validate_role(role):
    if role not in ROLES:
        return f"invalid role '{role}'. valid: {', '.join(ROLES.keys())}"
    return None


def _load_users():
    return read_json(USERS_FILE) or {"users": {}}


def _save_users(data):
    ensure_dir(IAM_DIR)
    write_json(USERS_FILE, data)


def create_user(username, role="reader"):
    e = validate_username(username)
    if e: return False, e
    e = validate_role(role)
    if e: return False, e
    data = _load_users()
    if username in data["users"]:
        return False, f"user '{username}' already exists"
    data["users"][username] = {
        "name": username, "role": role, "created": now_iso(),
    }
    _save_users(data)
    return True, f"created user '{username}' with role '{role}'"


def delete_user(username):
    data = _load_users()
    if username not in data["users"]:
        return False, f"user '{username}' not found"
    if username == "admin":
        return False, "cannot delete the built-in 'admin' user"
    del data["users"][username]
    _save_users(data)
    return True, f"deleted user '{username}'"


def list_users():
    return list(_load_users()["users"].values())


def get_user(username):
    return _load_users()["users"].get(username)


def set_role(username, role):
    e = validate_role(role)
    if e: return False, e
    data = _load_users()
    if username not in data["users"]:
        return False, f"user '{username}' not found"
    data["users"][username]["role"] = role
    _save_users(data)
    return True, f"set role of '{username}' to '{role}'"


def get_current_user():
    data = read_json(CURRENT_FILE)
    return data.get("username") if data else None


def login(username):
    user = get_user(username)
    if not user:
        return False, f"user '{username}' not found"
    ensure_dir(IAM_DIR)
    write_json(CURRENT_FILE, {"username": username, "since": now_iso()})
    return True, f"logged in as '{username}' ({user['role']})"


def logout():
    if os.path.exists(CURRENT_FILE):
        os.remove(CURRENT_FILE)
    return True, "logged out"


def _action_level(action):
    return ACTION_LEVELS.get(action, None)


def can(action):
    user = get_current_user()
    if not user:
        return False, "not logged in. Run: miniazure login <username>"
    user_data = get_user(user)
    if not user_data:
        return False, f"current user '{user}' no longer exists"
    user_role = user_data["role"]
    user_level = ROLES[user_role]["level"]
    required = _action_level(action)
    if required is None:
        required = 3
    if user_level >= required:
        return True, ""
    needed = [k for k, v in ROLES.items() if v["level"] >= required]
    return False, (f"permission denied: '{action}' requires role "
                   f"{'/'.join(needed)}, you are '{user_role}'")


def audit(action, detail="", success=True):
    ensure_dir(IAM_DIR)
    user = get_current_user() or "(anonymous)"
    status = "OK" if success else "DENIED"
    try:
        with open(AUDIT_FILE, "a") as f:
            f.write(f"{now_iso()} [{status}] {user:<10} {action:<25} {detail}\n")
    except Exception:
        pass


def read_audit(limit=30):
    if not os.path.exists(AUDIT_FILE):
        return []
    with open(AUDIT_FILE) as f:
        lines = f.readlines()
    return [l.rstrip() for l in lines[-limit:]]


def _ensure_default_admin():
    data = _load_users()
    if not data["users"]:
        data["users"]["admin"] = {
            "name": "admin", "role": "admin",
            "created": now_iso(), "note": "auto-created default user",
        }
        _save_users(data)


_ensure_default_admin()
