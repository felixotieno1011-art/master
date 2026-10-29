"""Security warnings + service quota checks.

Real AWS shows these on almost every page until resolved:
  - "MFA is not enabled on the root user"
  - "Root account has active access keys"

MiniAWS tracks dismissals in state/security.json so the banner can be
hidden by the user (real AWS doesn't offer dismissal, but the nagging is
excessive when you're just learning — dismissal is optional).
"""
import os

import config
from utils import now_iso, read_json, write_json, ensure_dir
from core import iam as iam_mod
from core import account


SEC_FILE = os.path.join(config.STATE_DIR, "security.json")


def _load():
    return read_json(SEC_FILE) or {"dismissed": []}


def _save(data):
    ensure_dir(os.path.dirname(SEC_FILE))
    write_json(SEC_FILE, data)


def dismiss(key):
    data = _load()
    if key not in data.get("dismissed", []):
        data.setdefault("dismissed", []).append(key)
        _save(data)
        return True, f"dismissed {key}"
    return False, f"{key} already dismissed"


def is_dismissed(key):
    return key in (_load().get("dismissed") or [])


# ---------- Security warnings ----------

def current_identity():
    """Return 'root', 'None', or username."""
    try:
        return iam_mod.get_current_user()
    except Exception:
        return None


def mfa_warning():
    """MFA on root — real AWS shows this until MFA is enabled on root."""
    user = current_identity()
    is_root = user is None or user == "root"
    return {
        "key": "mfa_warning",
        "title": "MFA is not enabled on the root user",
        "body": (
            "Multi-factor authentication (MFA) adds an extra layer of protection "
            "on top of your username and password. We recommend that you enable "
            "MFA for the root user of your AWS account. Without MFA, anyone who "
            "gets your password has full control of your account."
        ),
        "action": "Enable MFA (not simulated)",
        "href": "/iam",
        "active": is_root,  # show only when logged in as root
        "severity": "critical",
    }


def root_keys_warning():
    """Root access keys exist — real AWS warns about this."""
    keys_path = os.path.join(config.STATE_DIR, "iam", "access_keys")
    has_root_keys = False
    if os.path.isdir(keys_path):
        # Any access key file with "root" in the name means root keys exist.
        # (In real AWS, root keys are account-level, but MiniAWS keeps them
        # in the same directory as user keys.)
        for f in os.listdir(keys_path):
            if "root" in f.lower():
                has_root_keys = True
                break
    return {
        "key": "root_keys",
        "title": "You have active access keys for the root user",
        "body": (
            "Active access keys for the root user can be used to access all "
            "AWS resources in your account, with no restrictions. We strongly "
            "recommend that you delete any root user access keys you have, "
            "and use IAM users or roles instead."
        ),
        "action": "Delete root access keys",
        "href": "/iam/access-keys",
        "active": has_root_keys,
        "severity": "critical",
    }


def all_warnings():
    return [w for w in (mfa_warning(), root_keys_warning()) if w.get("active")]


def active_banners():
    """Warnings that should show in the global banner (not dismissed)."""
    return [w for w in all_warnings() if not is_dismissed(w["key"])]


# ---------- Service quotas ----------

# Real AWS defaults (per account, per region)
QUOTA_LIMITS = {
    "vpc":         {"metric": "VPCs", "limit": 5, "warn_at_pct": 80},
    "igw":         {"metric": "Internet gateways", "limit": 5, "warn_at_pct": 80},
    "eip":         {"metric": "Elastic IPs", "limit": 5, "warn_at_pct": 80},
    "ec2":         {"metric": "Running instances", "limit": 20, "warn_at_pct": 80},
    "s3":          {"metric": "S3 buckets (account-wide)", "limit": 100, "warn_at_pct": 80},
    "dynamodb":    {"metric": "DynamoDB tables", "limit": 2500, "warn_at_pct": 80},
    "lambda":      {"metric": "Lambda functions", "limit": 1000, "warn_at_pct": 80},
}


def quota_check(service):
    """Return {metric, used, limit, pct, warn} for a service.
    Returns None if service isn't in QUOTA_LIMITS.
    """
    spec = QUOTA_LIMITS.get(service)
    if not spec:
        return None

    used = 0
    try:
        if service == "vpc":
            from core import vpc as vpc_mod
            used = len(vpc_mod.list_vpcs())
        elif service == "igw":
            from core import vpc as vpc_mod
            used = len(vpc_mod.list_internet_gateways())
        elif service == "eip":
            used = 0  # not simulated
        elif service == "ec2":
            from core import ec2 as ec2_mod
            insts = ec2_mod.list_all()
            used = len([i for i in insts
                        if (i.get("state") or "").lower() in ("running", "pending")])
        elif service == "s3":
            from core import s3 as s3_mod
            used = len(s3_mod.ls_buckets())
        elif service == "dynamodb":
            from core import dynamodb as ddb
            used = len(ddb.list_tables())
        elif service == "lambda":
            from core import lambda_svc as lam
            used = len(lam.list_functions())
    except Exception:
        return None

    pct = (used / spec["limit"] * 100.0) if spec["limit"] else 0
    return {
        "service": service,
        "metric": spec["metric"],
        "used": used,
        "limit": spec["limit"],
        "pct": pct,
        "warn": pct >= spec["warn_at_pct"],
    }


def all_quota_checks():
    out = []
    for svc in ("vpc", "igw", "ec2", "s3", "dynamodb", "lambda"):
        r = quota_check(svc)
        if r:
            out.append(r)
    return out
