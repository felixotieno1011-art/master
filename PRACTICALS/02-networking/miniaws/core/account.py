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


def _aws_config_path():
    """Path to ~/.aws/config."""
    return os.path.join(os.path.expanduser("~"), ".aws", "config")


def _read_aws_config():
    """Read ~/.aws/config. Return dict of key->value from [default] section."""
    path = _aws_config_path()
    if not os.path.isfile(path):
        return {}
    result = {}
    in_default = False
    try:
        with open(path) as f:
            for line in f:
                line = line.strip()
                if line.startswith("[") and line.endswith("]"):
                    in_default = (line == "[default]")
                    continue
                if in_default and "=" in line:
                    k, v = line.split("=", 1)
                    result[k.strip()] = v.strip()
    except Exception:
        return {}
    return result


def _write_aws_config(values):
    """Merge values into ~/.aws/config [default] section."""
    path = _aws_config_path()
    os.makedirs(os.path.dirname(path), exist_ok=True)

    existing = _read_aws_config()
    existing.update(values)

    lines = ["[default]"]
    for k, v in existing.items():
        lines.append(f"{k} = {v}")

    with open(path, "w") as f:
        f.write("\n".join(lines) + "\n")


def get_region():
    """Return current region. Priority: env override, ~/.aws/config, state, default."""
    override = os.environ.get("MINIAWS_REGION_OVERRIDE")
    if override:
        return override
    aws_cfg = _read_aws_config()
    if "region" in aws_cfg:
        return aws_cfg["region"]
    data = _load()
    return data.get("region", config.DEFAULT_REGION)


def set_region(region):
    """Set region in both ~/.aws/config and internal state."""
    if region not in config.REGIONS:
        return False, (f"invalid region '{region}'. "
                       f"valid: {', '.join(config.REGIONS.keys())}")
    data = _load()
    if not data.get("account_id"):
        return False, "account not initialized. Run: aws configure"

    _write_aws_config({"region": region})

    data["region"] = region
    _save(data)
    return True, f"region set to '{region}' (saved to ~/.aws/config)"

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
    current_region = get_region()
    return {
        "account_id":   data.get("account_id", "(not initialized)"),
        "region":       current_region,
        "region_name":  config.REGIONS.get(current_region, "?"),
        "initialized":  data.get("initialized"),
        "tags":         data.get("tags", {}),
    }
