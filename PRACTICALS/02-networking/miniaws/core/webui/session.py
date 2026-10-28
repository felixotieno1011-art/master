"""WebUI session helpers — region + recently-visited.

All reads/writes go through core.account so the CLI sees identical state.
Nothing here invents a new config shape; we only add a `recent_services` key
inside state/config.json, which account._save() merges naturally.
"""
from urllib.parse import urlencode

import config as _cfg
from core import account


MAX_RECENT = 6


def current_region():
    """Return the active region code (from account, env, or default)."""
    code = account.get_region()
    if code not in _cfg.REGIONS:
        code = _cfg.DEFAULT_REGION
    return code


def region_label(code):
    return _cfg.REGIONS.get(code, code)


def region_tuple(code=None):
    code = code or current_region()
    return (code, region_label(code))


def set_region(code):
    """Persist a new region via account.set_region (writes ~/.aws/config + state)."""
    return account.set_region(code)


def region_from_query(qs):
    """If ?region=... is present and valid, return it; else current_region()."""
    values = qs.get("region") or []
    if values and values[0] in _cfg.REGIONS:
        return values[0]
    return current_region()


def _read_recent():
    data = account._load()
    recent = data.get("recent_services") or []
    from core.webui import aws_ref
    known = {s[0] for s in aws_ref.SERVICES}
    return [sid for sid in recent if sid in known][:MAX_RECENT]


def record_visit(service_id):
    from core.webui import aws_ref
    if service_id not in {s[0] for s in aws_ref.SERVICES}:
        return
    data = account._load()
    recent = [sid for sid in (data.get("recent_services") or []) if sid != service_id]
    recent.insert(0, service_id)
    data["recent_services"] = recent[:MAX_RECENT]
    account._save(data)


def recent_services():
    from core.webui import aws_ref
    by_id = {s[0]: s for s in aws_ref.SERVICES}
    return [by_id[sid] for sid in _read_recent() if sid in by_id]


def with_region(path, region_code=None):
    """Append ?region=<code> if a non-default region is active."""
    code = region_code or current_region()
    if code == _cfg.DEFAULT_REGION:
        return path
    sep = "&" if "?" in path else "?"
    return f"{path}{sep}{urlencode({'region': code})}"
