"""Elastic IPs form actions."""
import urllib.parse

from core import ec2 as ec2_mod
from lib import billing as billing_mod


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
        "/ec2/eips/allocate": _allocate,
        "/ec2/eips/release":  _release,
    }
    fn = routes.get(path)
    return fn(form) if fn else None


def _allocate(form):
    ok_, msg, _aid = ec2_mod.allocate_address()
    if not ok_:
        return _err("/ec2/elastic-ips", msg)
    # Charge the EIP cost
    try:
        billing_mod.charge("ec2.allocate-eip", 1)
    except Exception:
        pass
    return _ok("/ec2/elastic-ips", msg)


def _release(form):
    aid = (form.get("allocation_id") or "").strip()
    if not aid:
        return _err("/ec2/elastic-ips", "allocation_id required")
    ok_, msg = ec2_mod.release_address(aid)
    return _ok("/ec2/elastic-ips", msg) if ok_ else _err("/ec2/elastic-ips", msg)
