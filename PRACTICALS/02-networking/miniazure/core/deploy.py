"""YAML-based deployment — Terraform-lite.

Reads a YAML file declaring resources and creates them in order.
Idempotent: existing resources are skipped, not recreated.
"""
import os

import config
from utils import ok, err, warn, dim
from core import resource_group as rg
from core import vm as vmm
from core import storage
from core import network as netw


def _parse_simple_yaml(text):
    """
    A tiny YAML parser good enough for our format.
    Supports:
      resources:
        - type: xxx
          name: yyy
          ...
    Returns: {"resources": [ {..}, {..} ]}
    """
    lines = text.splitlines()
    resources = []
    current = None
    in_resources = False

    for raw in lines:
        line = raw.rstrip()
        if not line or line.lstrip().startswith("#"):
            continue

        # Top-level "resources:"
        if line.strip() == "resources:":
            in_resources = True
            continue

        if not in_resources:
            continue

        stripped = line.lstrip()
        indent = len(line) - len(stripped)

        # New list item: "- type: xxx"
        if stripped.startswith("- "):
            if current:
                resources.append(current)
            current = {}
            # after "- " there may be "key: value"
            kv = stripped[2:]
            if ":" in kv:
                k, v = kv.split(":", 1)
                current[k.strip()] = v.strip()
            continue

        # "key: value" inside item
        if current is not None and ":" in stripped:
            k, v = stripped.split(":", 1)
            current[k.strip()] = v.strip()

    if current:
        resources.append(current)

    return {"resources": resources}


def load_plan(path):
    """Read + parse a YAML file. Return dict or raise."""
    if not os.path.exists(path):
        raise FileNotFoundError(f"plan file not found: {path}")
    with open(path) as f:
        text = f.read()
    return _parse_simple_yaml(text)


def _create_one(res):
    """Create a single resource. Return (success, message, action)."""
    rtype = (res.get("type") or "").lower()

    if rtype == "group":
        name = res.get("name")
        region = res.get("region") or config.DEFAULT_REGION
        if rg.get(name):
            return True, f"group '{name}' already exists", "skip"
        ok_, msg = rg.create(name, region=region)
        return ok_, msg, "create"

    if rtype == "vm":
        name = res.get("name")
        group = res.get("group")
        size = res.get("size") or "small"
        if vmm.get(name):
            return True, f"vm '{name}' already exists", "skip"
        ok_, msg = vmm.create(name, group=group, size=size)
        return ok_, msg, "create"

    if rtype == "storage":
        name = res.get("name")
        group = res.get("group")
        if storage.get_account(name):
            return True, f"storage '{name}' already exists", "skip"
        ok_, msg = storage.create_account(name, group=group)
        return ok_, msg, "create"

    if rtype == "vnet":
        name = res.get("name")
        group = res.get("group")
        cidr = res.get("cidr")
        if netw.get_vnet(name):
            return True, f"vnet '{name}' already exists", "skip"
        ok_, msg = netw.create_vnet(name, group, cidr)
        return ok_, msg, "create"

    if rtype == "subnet":
        vnet = res.get("vnet")
        name = res.get("name")
        cidr = res.get("cidr")
        subs = netw.list_subnets(vnet) or {}
        if name in subs:
            return True, f"subnet '{name}' already exists", "skip"
        ok_, msg = netw.create_subnet(vnet, name, cidr)
        return ok_, msg, "create"

    return False, f"unknown resource type '{rtype}'", "error"


def apply_plan(path):
    """Apply a plan. Return (success, summary)."""
    try:
        plan = load_plan(path)
    except Exception as e:
        return False, str(e)

    resources = plan.get("resources", [])
    if not resources:
        return False, "plan has no resources"

    # Order: groups -> vnets -> subnets -> vms -> storage
    order = {"group": 0, "vnet": 1, "subnet": 2, "vm": 3, "storage": 3}

    def sort_key(r):
        return order.get((r.get("type") or "").lower(), 99)

    resources_sorted = sorted(resources, key=sort_key)

    results = []
    created = 0
    skipped = 0
    failed = 0

    for r in resources_sorted:
        rtype = (r.get("type") or "?").lower()
        rname = r.get("name") or "?"
        ok_, msg, action = _create_one(r)
        results.append((rtype, rname, action, ok_, msg))
        if not ok_:
            failed += 1
        elif action == "skip":
            skipped += 1
        elif action == "create":
            created += 1

    return (failed == 0), {
        "total": len(resources_sorted),
        "created": created,
        "skipped": skipped,
        "failed": failed,
        "details": results,
    }
