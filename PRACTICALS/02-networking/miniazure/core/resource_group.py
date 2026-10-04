"""Resource group operations — like `az group` in real Azure.

A resource group is a named container for resources.
In real Azure: a logical group with a region, tags, and metadata.
In MiniAzure: a JSON file in state/groups/<name>.json
"""
import os
import re

import config
from utils import (
    ok, err, warn, dim, now_iso, short_id,
    read_json, write_json, delete_file, ensure_dir,
)


# Validation ------------------------------------------------------

NAME_RE = re.compile(r"^[a-zA-Z0-9][a-zA-Z0-9_-]{1,62}[a-zA-Z0-9]$")


def validate_name(name):
    if not name:
        return "name is required"
    if not NAME_RE.match(name):
        return ("name must be 3-64 chars, start and end with a letter/digit, "
                "and contain only letters, digits, hyphens, underscores")
    return None


def validate_region(region):
    if region not in config.VALID_REGIONS:
        return (f"invalid region '{region}'. "
                f"valid: {', '.join(config.VALID_REGIONS)}")
    return None


# Path helpers ----------------------------------------------------

def _group_path(name):
    return os.path.join(config.GROUPS_DIR, f"{name}.json")


# Operations ------------------------------------------------------

def create(name, region=None, tags=None):
    """Create a resource group. Return (success, message)."""
    # Validate name
    e = validate_name(name)
    if e:
        return False, e

    # Validate region
    region = region or config.DEFAULT_REGION
    e = validate_region(region)
    if e:
        return False, e

    # Check existence
    if os.path.exists(_group_path(name)):
        return False, f"resource group '{name}' already exists"

    # Build state (like Azure's response object)
    data = {
        "id": f"/subscriptions/local/resourceGroups/{name}",
        "name": name,
        "type": "Microsoft.Resources/resourceGroups",
        "location": region,
        "tags": tags or {},
        "properties": {
            "provisioningState": "Succeeded",
        },
        "created": now_iso(),
        "createdBy": "miniazure-cli",
    }

    # Persist
    ensure_dir(config.GROUPS_DIR)
    write_json(_group_path(name), data)

    return True, f"created resource group '{name}' in '{region}'"


def list_all():
    """Return list of all resource groups (as dicts)."""
    ensure_dir(config.GROUPS_DIR)
    groups = []
    for fname in sorted(os.listdir(config.GROUPS_DIR)):
        if not fname.endswith(".json"):
            continue
        data = read_json(os.path.join(config.GROUPS_DIR, fname))
        if data:
            groups.append(data)
    return groups


def get(name):
    """Return one resource group dict, or None."""
    return read_json(_group_path(name))


def delete(name):
    """Delete a resource group. Return (success, message)."""
    if not os.path.exists(_group_path(name)):
        return False, f"resource group '{name}' not found"
    delete_file(_group_path(name))
    return True, f"deleted resource group '{name}'"


def exists(name):
    return os.path.exists(_group_path(name))
