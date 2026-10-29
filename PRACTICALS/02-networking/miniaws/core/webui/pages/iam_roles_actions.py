"""IAM Roles form actions — create, delete, attach, detach."""
import urllib.parse

from core.webui import iam_roles as roles_mod


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
        "/iam/roles/create":         _create,
        "/iam/roles/delete":         _delete,
        "/iam/roles/attach-policy":  _attach,
        "/iam/roles/detach-policy":  _detach,
    }
    fn = routes.get(path)
    return fn(form) if fn else None


def _create(form):
    name = (form.get("name") or "").strip()
    entity_type = (form.get("entity_type") or "service").strip()
    description = (form.get("description") or "").strip()

    # Resolve principal based on entity type
    if entity_type == "service":
        principal = (form.get("principal_service") or "").strip()
    elif entity_type == "account":
        acct = (form.get("principal_account") or "").strip()
        principal = f"arn:aws:iam::{acct}:root" if acct else ""
    elif entity_type == "web_identity":
        principal = (form.get("principal_web") or "").strip()
    elif entity_type == "saml":
        principal = (form.get("principal_saml") or "").strip()
    else:
        return _err("/iam/roles/create", f"unknown entity_type '{entity_type}'")

    if not name:
        return _err("/iam/roles/create", "role name required")
    if not principal:
        return _err("/iam/roles/create", "trusted principal required")

    # Multiple policy checkboxes → form parser gives us one value only.
    # Our parser collapses to a single string. Support comma-separated too.
    raw_pol = form.get("policies") or ""
    policies = [p.strip() for p in raw_pol.split(",") if p.strip()] if raw_pol else []

    ok_, msg, _role_name = roles_mod.create_role(
        name, entity_type, principal,
        attached_policies=policies, description=description,
    )
    if not ok_:
        return _err("/iam/roles/create", msg)
    return _ok(f"/iam/roles/{urllib.parse.quote(name)}", msg)


def _delete(form):
    name = (form.get("name") or "").strip()
    if not name:
        return _err("/iam/roles", "name required")
    ok_, msg = roles_mod.delete_role(name)
    return _ok("/iam/roles", msg) if ok_ else _err(f"/iam/roles/{urllib.parse.quote(name)}", msg)


def _attach(form):
    role = (form.get("role") or "").strip()
    policy = (form.get("policy") or "").strip()
    if not role or not policy:
        return _err("/iam/roles", "role and policy required")
    ok_, msg = roles_mod.attach_policy_to_role(role, policy)
    if not ok_:
        return _err(f"/iam/roles/{urllib.parse.quote(role)}", msg)
    return _ok(f"/iam/roles/{urllib.parse.quote(role)}", msg)


def _detach(form):
    role = (form.get("role") or "").strip()
    policy = (form.get("policy") or "").strip()
    if not role or not policy:
        return _err("/iam/roles", "role and policy required")
    ok_, msg = roles_mod.detach_policy_from_role(role, policy)
    if not ok_:
        return _err(f"/iam/roles/{urllib.parse.quote(role)}", msg)
    return _ok(f"/iam/roles/{urllib.parse.quote(role)}", msg)
