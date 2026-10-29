"""IAM form actions — create/delete/attach for users, groups, policies, keys."""
import json
import urllib.parse

from core import iam as iam_mod
from core.webui import permissions


def _redirect(loc):
    return ("redirect", loc)


def _ok(path, msg):
    sep = "&" if "?" in path else "?"
    return _redirect(f"{path}{sep}ok={urllib.parse.quote(str(msg))}")


def _err(path, msg):
    sep = "&" if "?" in path else "?"
    return _redirect(f"{path}{sep}error={urllib.parse.quote(str(msg))}")


def handle(path, form, files=None):
    routes = {
        "/iam/users/create":              _create_user,
        "/iam/users/delete":              _delete_user,
        "/iam/users/attach-policy":       _attach_user_policy,
        "/iam/users/detach-policy":       _detach_user_policy,
        "/iam/users/create-access-key":   _create_access_key,
        "/iam/users/delete-access-key":   _delete_access_key,
        "/iam/groups/create":             _create_group,
        "/iam/policies/create":           _create_policy,
        "/iam/policies/delete":           _delete_policy,
    }
    fn = routes.get(path)
    return fn(form) if fn else None


def _create_user(form):
    allowed, err = permissions.require("iam:CreateUser", back="/iam/users/create")
    if not allowed:
        return err
    name = (form.get("username") or "").strip()
    if not name:
        return _err("/iam/users/create", "username required")
    ok_, msg = iam_mod.create_user(name)
    if not ok_:
        return _err("/iam/users/create", msg)

    # Attach selected policies
    policies_raw = form.get("policies") or ""
    policies = [p.strip() for p in (policies_raw.split(",") if policies_raw else []) if p.strip()]
    for p in policies:
        try:
            iam_mod.attach_user_policy(name, p)
        except Exception:
            pass

    return _ok(f"/iam/users/{urllib.parse.quote(name)}", msg)


def _delete_user(form):
    name = (form.get("username") or "").strip()
    if not name:
        return _err("/iam/users", "username required")
    ok_, msg = iam_mod.delete_user(name)
    return _ok("/iam/users", msg) if ok_ else _err(f"/iam/users/{urllib.parse.quote(name)}", msg)


def _attach_user_policy(form):
    name = (form.get("username") or "").strip()
    pol = (form.get("policy") or "").strip()
    if not name or not pol:
        return _err("/iam/users", "username and policy required")
    ok_, msg = iam_mod.attach_user_policy(name, pol)
    if not ok_:
        return _err(f"/iam/users/{urllib.parse.quote(name)}", msg)
    return _ok(f"/iam/users/{urllib.parse.quote(name)}", msg)


def _detach_user_policy(form):
    name = (form.get("username") or "").strip()
    pol = (form.get("policy") or "").strip()
    if not name or not pol:
        return _err("/iam/users", "username and policy required")
    ok_, msg = iam_mod.detach_user_policy(name, pol)
    if not ok_:
        return _err(f"/iam/users/{urllib.parse.quote(name)}", msg)
    return _ok(f"/iam/users/{urllib.parse.quote(name)}", msg)


def _create_access_key(form):
    name = (form.get("username") or "").strip()
    if not name:
        return _err("/iam/users", "username required")
    ok_, msg = iam_mod.create_access_key(name)
    if not ok_:
        return _err(f"/iam/users/{urllib.parse.quote(name)}?tab=security", msg)
    return _ok(f"/iam/users/{urllib.parse.quote(name)}?tab=security", msg)


def _delete_access_key(form):
    name = (form.get("username") or "").strip()
    key = (form.get("access_key") or "").strip()
    if not name or not key:
        return _err("/iam/users", "username and access_key required")
    ok_, msg = iam_mod.delete_access_key(name, key)
    if not ok_:
        return _err(f"/iam/users/{urllib.parse.quote(name)}?tab=security", msg)
    return _ok(f"/iam/users/{urllib.parse.quote(name)}?tab=security", msg)


def _create_group(form):
    name = (form.get("name") or "").strip()
    if not name:
        return _err("/iam/groups/create", "group name required")
    ok_, msg = iam_mod.create_group(name)
    if not ok_:
        return _err("/iam/groups/create", msg)
    return _ok("/iam/groups", msg)


def _create_policy(form):
    name = (form.get("name") or "").strip()
    doc = (form.get("document") or "").strip()
    if not name or not doc:
        return _err("/iam/policies/create", "name and document required")
    try:
        parsed = json.loads(doc)
    except json.JSONDecodeError as e:
        return _err("/iam/policies/create", f"invalid JSON: {e}")
    ok_, msg = iam_mod.create_policy(name, parsed)
    if not ok_:
        return _err("/iam/policies/create", msg)
    return _ok("/iam/policies", msg)


def _delete_policy(form):
    name = (form.get("policy") or "").strip()
    if not name:
        return _err("/iam/policies", "policy required")
    ok_, msg = iam_mod.delete_policy(name)
    if not ok_:
        return _err("/iam/policies", msg)
    return _ok("/iam/policies", msg)
