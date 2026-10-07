"""IAM — Users, Groups, Policies, Roles.

AWS IAM model:
  - Policies are JSON documents with Effect, Action, Resource
  - Users, Groups, Roles have policies attached
  - Permission check: explicit Deny > explicit Allow > implicit Deny
"""
import json
import os
import re

import config
from utils import (
    now_iso, make_arn,
    read_json, write_json, delete_file, ensure_dir,
)
from core import account


IAM_DIR       = os.path.join(config.STATE_DIR, "iam")
USERS_DIR     = os.path.join(IAM_DIR, "users")
GROUPS_DIR    = os.path.join(IAM_DIR, "groups")
POLICIES_DIR  = os.path.join(IAM_DIR, "policies")
CURRENT_FILE  = os.path.join(IAM_DIR, "current_user.json")
AUDIT_FILE    = os.path.join(IAM_DIR, "audit.log")


USERNAME_RE = re.compile(r"^[a-zA-Z][a-zA-Z0-9._-]{0,63}$")
GROUPNAME_RE = re.compile(r"^[a-zA-Z][a-zA-Z0-9._-]{0,127}$")


# ---------- Users ----------

def _user_path(name):
    return os.path.join(USERS_DIR, f"{name}.json")


def validate_username(name):
    if not name:
        return "username required"
    if not USERNAME_RE.match(name):
        return "username must start with a letter, max 64 chars, use letters/digits/._-"
    return None


def create_user(username, tags=None):
    e = validate_username(username)
    if e: return False, e
    if os.path.exists(_user_path(username)):
        return False, f"user '{username}' already exists"
    if not account.is_initialized():
        return False, "account not initialized"

    region = account.get_region()
    account_id = account.get_account_id()
    arn = make_arn("iam", "", account_id, f"user/{username}")

    data = {
        "userName": username,
        "arn": arn,
        "userId": "AIDA" + account_id[:12],
        "path": "/",
        "created": now_iso(),
        "tags": tags or {},
        "attachedPolicies": [],
        "groups": [],
    }
    ensure_dir(USERS_DIR)
    write_json(_user_path(username), data)
    return True, f"created user '{username}'"


def get_user(username):
    return read_json(_user_path(username))


def list_users():
    ensure_dir(USERS_DIR)
    out = []
    for f in sorted(os.listdir(USERS_DIR)):
        if f.endswith(".json"):
            d = read_json(os.path.join(USERS_DIR, f))
            if d:
                out.append(d)
    return out


def delete_user(username):
    u = get_user(username)
    if not u:
        return False, f"user '{username}' not found"
    delete_file(_user_path(username))
    return True, f"deleted user '{username}'"


# ---------- Groups ----------

def _group_path(name):
    return os.path.join(GROUPS_DIR, f"{name}.json")


def validate_group_name(name):
    if not name:
        return "group name required"
    if not GROUPNAME_RE.match(name):
        return "group name must start with a letter, max 128 chars"
    return None


def create_group(groupname):
    e = validate_group_name(groupname)
    if e: return False, e
    if os.path.exists(_group_path(groupname)):
        return False, f"group '{groupname}' already exists"

    region = account.get_region()
    account_id = account.get_account_id()
    arn = make_arn("iam", "", account_id, f"group/{groupname}")

    data = {
        "groupName": groupname,
        "arn": arn,
        "created": now_iso(),
        "attachedPolicies": [],
        "members": [],
    }
    ensure_dir(GROUPS_DIR)
    write_json(_group_path(groupname), data)
    return True, f"created group '{groupname}'"


def get_group(name):
    return read_json(_group_path(name))


def list_groups():
    ensure_dir(GROUPS_DIR)
    out = []
    for f in sorted(os.listdir(GROUPS_DIR)):
        if f.endswith(".json"):
            d = read_json(os.path.join(GROUPS_DIR, f))
            if d:
                out.append(d)
    return out


def add_user_to_group(username, groupname):
    if not get_user(username):
        return False, f"user '{username}' not found"
    g = get_group(groupname)
    if not g:
        return False, f"group '{groupname}' not found"
    if username in g.get("members", []):
        return False, f"user '{username}' already in group '{groupname}'"
    g.setdefault("members", []).append(username)
    write_json(_group_path(groupname), g)

    u = get_user(username)
    u.setdefault("groups", []).append(groupname)
    write_json(_user_path(username), u)
    return True, f"added '{username}' to group '{groupname}'"


def remove_user_from_group(username, groupname):
    g = get_group(groupname)
    if not g:
        return False, f"group '{groupname}' not found"
    if username not in g.get("members", []):
        return False, f"user '{username}' not in group '{groupname}'"
    g["members"].remove(username)
    write_json(_group_path(groupname), g)

    u = get_user(username)
    if u and groupname in u.get("groups", []):
        u["groups"].remove(groupname)
        write_json(_user_path(username), u)
    return True, f"removed '{username}' from group '{groupname}'"


def delete_group(groupname):
    g = get_group(groupname)
    if not g:
        return False, f"group '{groupname}' not found"
    if g.get("members"):
        return False, f"group has members. Remove them first."
    delete_file(_group_path(groupname))
    return True, f"deleted group '{groupname}'"


# ---------- Policies ----------

def _policy_path(name):
    return os.path.join(POLICIES_DIR, f"{name}.json")


def validate_policy_document(doc):
    """Check a policy is a valid AWS-style document."""
    if not isinstance(doc, dict):
        return "policy must be a JSON object"
    if doc.get("Version") not in ("2012-10-17", "2008-10-17"):
        return "policy Version must be '2012-10-17'"
    stmts = doc.get("Statement")
    if not isinstance(stmts, list) or not stmts:
        return "policy must have a non-empty Statement array"
    for i, s in enumerate(stmts):
        if not isinstance(s, dict):
            return f"statement {i} must be an object"
        if s.get("Effect") not in ("Allow", "Deny"):
            return f"statement {i} Effect must be 'Allow' or 'Deny'"
        if "Action" not in s:
            return f"statement {i} missing Action"
        if "Resource" not in s:
            return f"statement {i} missing Resource"
    return None


def create_policy(name, document):
    """Create a policy from a JSON document (dict)."""
    e = validate_policy_document(document)
    if e: return False, e
    if os.path.exists(_policy_path(name)):
        return False, f"policy '{name}' already exists"

    region = account.get_region()
    account_id = account.get_account_id()
    arn = make_arn("iam", "", account_id, f"policy/{name}")

    data = {
        "policyName": name,
        "arn": arn,
        "document": document,
        "created": now_iso(),
    }
    ensure_dir(POLICIES_DIR)
    write_json(_policy_path(name), data)
    return True, f"created policy '{name}'"


def get_policy(name):
    return read_json(_policy_path(name))


def list_policies():
    ensure_dir(POLICIES_DIR)
    out = []
    for f in sorted(os.listdir(POLICIES_DIR)):
        if f.endswith(".json"):
            d = read_json(os.path.join(POLICIES_DIR, f))
            if d:
                out.append(d)
    return out


def delete_policy(name):
    if not get_policy(name):
        return False, f"policy '{name}' not found"
    delete_file(_policy_path(name))
    return True, f"deleted policy '{name}'"


# ---------- Attach policies ----------

def attach_user_policy(username, policy_name):
    u = get_user(username)
    if not u:
        return False, f"user '{username}' not found"
    if not get_policy(policy_name):
        return False, f"policy '{policy_name}' not found"
    if policy_name in u.get("attachedPolicies", []):
        return False, f"policy '{policy_name}' already attached to '{username}'"
    u.setdefault("attachedPolicies", []).append(policy_name)
    write_json(_user_path(username), u)
    return True, f"attached '{policy_name}' to user '{username}'"


def attach_group_policy(groupname, policy_name):
    g = get_group(groupname)
    if not g:
        return False, f"group '{groupname}' not found"
    if not get_policy(policy_name):
        return False, f"policy '{policy_name}' not found"
    if policy_name in g.get("attachedPolicies", []):
        return False, f"policy '{policy_name}' already attached to group"
    g.setdefault("attachedPolicies", []).append(policy_name)
    write_json(_group_path(groupname), g)
    return True, f"attached '{policy_name}' to group '{groupname}'"


def detach_user_policy(username, policy_name):
    u = get_user(username)
    if not u:
        return False, f"user '{username}' not found"
    if policy_name not in u.get("attachedPolicies", []):
        return False, f"policy not attached"
    u["attachedPolicies"].remove(policy_name)
    write_json(_user_path(username), u)
    return True, f"detached '{policy_name}' from '{username}'"


def detach_group_policy(groupname, policy_name):
    g = get_group(groupname)
    if not g:
        return False, f"group '{groupname}' not found"
    if policy_name not in g.get("attachedPolicies", []):
        return False, f"policy not attached"
    g["attachedPolicies"].remove(policy_name)
    write_json(_group_path(groupname), g)
    return True, f"detached '{policy_name}' from group '{groupname}'"


# ---------- Current user (login) ----------

def get_current_user():
    data = read_json(CURRENT_FILE)
    return data.get("username") if data else None


def login(username):
    """Become a user. Special: 'root' has all permissions."""
    if username == "root":
        ensure_dir(IAM_DIR)
        write_json(CURRENT_FILE, {"username": "root", "since": now_iso()})
        return True, "logged in as root (full access)"
    u = get_user(username)
    if not u:
        return False, f"user '{username}' not found"
    ensure_dir(IAM_DIR)
    write_json(CURRENT_FILE, {"username": username, "since": now_iso()})
    return True, f"logged in as '{username}'"


def logout():
    if os.path.exists(CURRENT_FILE):
        os.remove(CURRENT_FILE)
    return True, "logged out"


def _match_action(pattern, action):
    """Match AWS-style action patterns. '*' matches anything."""
    if pattern == "*":
        return True
    if pattern == action:
        return True
    if pattern.endswith("*"):
        return action.startswith(pattern[:-1])
    if pattern.startswith("*"):
        return action.endswith(pattern[1:])
    # service:* style
    if ":" in pattern and pattern.endswith(":*"):
        return action.startswith(pattern[:-1])
    return False


def _collect_statements(policies):
    """Given a list of policy dicts, return all statements."""
    out = []
    for p in policies:
        for st in p["document"]["Statement"]:
            out.append(st)
    return out


def _user_policies(user):
    """Return all policies attached to user (via user + groups)."""
    policies = []
    for pname in user.get("attachedPolicies", []):
        p = get_policy(pname)
        if p:
            policies.append(p)
    for gname in user.get("groups", []):
        g = get_group(gname)
        if g:
            for pname in g.get("attachedPolicies", []):
                p = get_policy(pname)
                if p:
                    policies.append(p)
    return policies


def can(action, resource="*"):
    """
    Check if the current user can perform the given AWS-style action.
    Returns (allowed: bool, reason: str).
    """
    user = get_current_user()
    if not user:
        return False, "not logged in. Run: aws iam login <user> OR aws iam login root"
    if user == "root":
        return True, ""

    u = get_user(user)
    if not u:
        return False, f"current user '{user}' not found"

    policies = _user_policies(u)
    statements = _collect_statements(policies)

    # 1) Explicit Deny wins
    for s in statements:
        if s.get("Effect") != "Deny":
            continue
        actions = s["Action"] if isinstance(s["Action"], list) else [s["Action"]]
        resources = s["Resource"] if isinstance(s["Resource"], list) else [s["Resource"]]
        if any(_match_action(a, action) for a in actions):
            if "*" in resources or resource in resources:
                return False, f"explicit deny on {action}"

    # 2) Explicit Allow
    for s in statements:
        if s.get("Effect") != "Allow":
            continue
        actions = s["Action"] if isinstance(s["Action"], list) else [s["Action"]]
        resources = s["Resource"] if isinstance(s["Resource"], list) else [s["Resource"]]
        if any(_match_action(a, action) for a in actions):
            if "*" in resources or resource in resources:
                return True, ""

    return False, f"no policy allows '{action}' for user '{user}'"


# ---------- Audit ----------

def audit(action, detail="", success=True):
    ensure_dir(IAM_DIR)
    user = get_current_user() or "(anonymous)"
    status = "OK" if success else "DENIED"
    try:
        with open(AUDIT_FILE, "a") as f:
            f.write(f"{now_iso()} [{status}] {user:<12} {action:<25} {detail}\n")
    except Exception:
        pass


def read_audit(limit=30):
    if not os.path.exists(AUDIT_FILE):
        return []
    with open(AUDIT_FILE) as f:
        lines = f.readlines()
    return [l.rstrip() for l in lines[-limit:]]
