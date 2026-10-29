"""IAM Roles — web-layer only. Stored in state/iam/roles/, invisible to CLI.

Roles in AWS:
  - A role is an identity that AWS services (or users) can *assume*.
  - It has two policies: a TRUST policy (who can assume it) and PERMISSIONS
    policies (what the role can do once assumed).

We use the same JSON document format as IAM policies (Version / Statement),
and translate the trust policy back to plain English for the UI.
"""
import json
import os
from datetime import datetime

import config
from utils import (
    now_iso, read_json, write_json, delete_file, ensure_dir, make_arn,
)
from core import account


ROLES_DIR = os.path.join(config.STATE_DIR, "iam", "roles")


# ---------- Storage ----------

def _role_path(name):
    return os.path.join(ROLES_DIR, f"{name}.json")


def _ensure():
    ensure_dir(ROLES_DIR)


def list_roles():
    _ensure()
    out = []
    if not os.path.isdir(ROLES_DIR):
        return out
    for f in sorted(os.listdir(ROLES_DIR)):
        if f.endswith(".json"):
            d = read_json(os.path.join(ROLES_DIR, f))
            if d:
                out.append(d)
    return out


def get_role(name):
    return read_json(_role_path(name))


def delete_role(name):
    if not get_role(name):
        return False, f"role '{name}' not found"
    delete_file(_role_path(name))
    return True, f"deleted role '{name}'"


# ---------- Trust policy builders ----------

def build_trust_policy(entity_type, **kwargs):
    """Return a parsed trust policy dict for the given entity type.

    entity_type ∈ {service, account, web_identity, saml}
    kwargs per type:
      service:     principal = "ec2.amazonaws.com"
      account:     principal = "arn:aws:iam::123456789012:root"
      web_identity: provider = "accounts.google.com" (or "arn:aws:iam::...:oidc-provider/...")
      saml:        provider = "arn:aws:iam::123456789012:saml-provider/Okta"
    """
    statement = {
        "Effect": "Allow",
        "Action": "sts:AssumeRole",
    }
    if entity_type == "service":
        statement["Principal"] = {"Service": kwargs.get("principal", "")}
    elif entity_type == "account":
        statement["Principal"] = {"AWS": kwargs.get("principal", "")}
    elif entity_type == "web_identity":
        statement["Principal"] = {"Federated": kwargs.get("provider", "")}
        # Real AWS needs an additional Action for web identity
        statement["Action"] = "sts:AssumeRoleWithWebIdentity"
    elif entity_type == "saml":
        statement["Principal"] = {"Federated": kwargs.get("provider", "")}
        statement["Action"] = "sts:AssumeRoleWithSAML"
    else:
        raise ValueError(f"unknown entity_type: {entity_type}")

    return {
        "Version": "2012-10-17",
        "Statement": [statement],
    }


def create_role(name, entity_type, principal, attached_policies=None,
                description="", tags=None):
    """Create a role. `principal` is the trust target (service name / ARN)."""
    if not name:
        return False, "role name required", None
    if not principal:
        return False, "trusted principal required", None
    if os.path.exists(_role_path(name)):
        return False, f"role '{name}' already exists", None

    try:
        trust = build_trust_policy(entity_type, principal=principal,
                                    provider=principal)
    except ValueError as e:
        return False, str(e), None

    region = account.get_region()
    account_id = account.get_account_id()
    arn = make_arn("iam", "", account_id, f"role/{name}")

    data = {
        "roleName": name,
        "arn": arn,
        "roleId": "AROA" + (account_id or "000000000000")[:12],
        "path": "/",
        "created": now_iso(),
        "description": description or f"Role for {entity_type}: {principal}",
        "trusted_entity_type": entity_type,
        "trusted_principal": principal,
        "assumeRolePolicyDocument": trust,
        "attachedPolicies": list(attached_policies or []),
        "tags": dict(tags or {}),
    }
    _ensure()
    write_json(_role_path(name), data)
    return True, f"created role '{name}' (trusts {principal})", name


def attach_policy_to_role(role_name, policy_name):
    r = get_role(role_name)
    if not r:
        return False, f"role '{role_name}' not found"
    attached = r.get("attachedPolicies") or []
    if policy_name in attached:
        return False, f"policy '{policy_name}' already attached"
    attached.append(policy_name)
    r["attachedPolicies"] = attached
    write_json(_role_path(role_name), r)
    return True, f"attached '{policy_name}' to role '{role_name}'"


def detach_policy_from_role(role_name, policy_name):
    r = get_role(role_name)
    if not r:
        return False, f"role '{role_name}' not found"
    attached = r.get("attachedPolicies") or []
    if policy_name not in attached:
        return False, f"policy '{policy_name}' not attached to role"
    r["attachedPolicies"] = [p for p in attached if p != policy_name]
    write_json(_role_path(role_name), r)
    return True, f"detached '{policy_name}' from role '{role_name}'"


# ---------- Trust policy translation (for UI) ----------

def translate_trust_policy(trust_doc):
    """Return a list of human-readable statements like:
       [{"who": "EC2 instances (ec2.amazonaws.com)", "via": "sts:AssumeRole"}]
    """
    out = []
    for stmt in (trust_doc.get("Statement") or []):
        if stmt.get("Effect") != "Allow":
            continue
        action = stmt.get("Action", "")
        principal = stmt.get("Principal") or {}
        entities = []
        for k, v in principal.items():
            values = v if isinstance(v, list) else [v]
            for val in values:
                entities.append(_describe_principal(k, val))
        if not entities:
            continue
        out.append({
            "who": entities,
            "via": action,
        })
    return out


def _describe_principal(kind, value):
    """Turn a principal (kind + value) into 'Human description (value)'."""
    if kind == "Service":
        return f"{_service_name(value)} ({value})"
    if kind == "AWS":
        return f"AWS account or user ({value})"
    if kind == "Federated":
        if "oidc-provider" in value or "accounts.google.com" in value:
            return f"Web identity provider ({value})"
        if "saml-provider" in value:
            return f"SAML identity provider ({value})"
        return f"Federated identity ({value})"
    return f"{kind}: {value}"


def _service_name(service_principal):
    """Map 'ec2.amazonaws.com' → 'EC2 instances'."""
    base = service_principal.replace(".amazonaws.com", "")
    mapping = {
        "ec2": "EC2 instances",
        "lambda": "Lambda functions",
        "ecs": "ECS tasks",
        "eks": "EKS clusters",
        "rds": "RDS databases",
        "s3": "S3 buckets",
        "glue": "AWS Glue jobs",
        "sagemaker": "SageMaker jobs",
        "batch": "AWS Batch jobs",
        "stepfunctions": "Step Functions state machines",
        "apigateway": "API Gateway",
        "cognito-identity": "Cognito identities",
        "elasticbeanstalk": "Elastic Beanstalk",
        "cloudformation": "CloudFormation",
    }
    return mapping.get(base, base)
