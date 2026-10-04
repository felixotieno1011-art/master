"""AWS account + region model.

In AWS:
  - An account is identified by a 12-digit number
  - Every resource lives in a region within an account
  - Config (region, profile) is stored in ~/.aws/config (locally)
  - We store ours in state/config.json
"""
import os

import config
from utils import now_iso, read_json, write_json, ensure_dir


def _load():
    return read_json(config.CONFIG_FILE) or {}


def _save(data):
    ensure_dir(config.STATE_DIR)
    write_json(config.CONFIG_FILE, data)


def get_account_id():
    """Return the account ID, or None if not initialized."""
    data = _load()
    return data.get("account_id")


def is_initialized():
    return get_account_id() is not None


def init_account(account_id=None):
    """
    Initialize the local account (like `aws configure`).
    If no ID given, generate a fake one.
    """
    import random
    if not account_id:
        # AWS account IDs are 12 digits
        account_id = "".join(str(random.randint(0, 9)) for _ in range(12))

    if len(account_id) != 12 or not account_id.isdigit():
        return False, "account_id must be exactly 12 digits"

    data = _load()
    data["account_id"] = account_id
    data["initialized"] = now_iso()
    if "region" not in data:
        data["region"] = config.DEFAULT_REGION
    if "tags" not in data:
        data["tags"] = {}
    _save(data)
    return True, f"account initialized: {account_id}"


def get_region():
    """Return current region, or default."""
    data = _load()
    return data.get("region", config.DEFAULT_REGION)


def set_region(region):
    """Set current region. Validates against known regions."""
    if region not in config.REGIONS:
        return False, (f"invalid region '{region}'. "
                       f"valid: {', '.join(config.REGIONS.keys())}")
    data = _load()
    if not data.get("account_id"):
        return False, "account not initialized. Run: miniaws account init"
    data["region"] = region
    _save(data)
    return True, f"region set to '{region}'"


def list_regions():
    """Return all known regions."""
    return config.REGIONS


def get_tags():
    """Global account tags (like AWS default tags)."""
    data = _load()
    return data.get("tags", {})


def set_tag(key, value):
    """Set a global tag."""
    data = _load()
    tags = data.setdefault("tags", {})
    tags[key] = value
    _save(data)
    return True, f"tag set: {key}={value}"


def delete_tag(key):
    data = _load()
    tags = data.get("tags", {})
    if key not in tags:
        return False, f"tag '{key}' not found"
    del tags[key]
    _save(data)
    return True, f"tag '{key}' deleted"


def summary():
    """Return a summary dict for display."""
    data = _load()
    return {
        "account_id":   data.get("account_id", "(not initialized)"),
        "region":       data.get("region", config.DEFAULT_REGION),
        "region_name":  config.REGIONS.get(data.get("region", config.DEFAULT_REGION), "?"),
        "initialized":  data.get("initialized"),
        "tags":         data.get("tags", {}),
    }
