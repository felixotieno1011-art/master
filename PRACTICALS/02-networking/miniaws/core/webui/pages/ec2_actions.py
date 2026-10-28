"""EC2 form actions — launch, start, stop, reboot, terminate."""
import urllib.parse

from core import ec2 as ec2_mod


def _redirect(location):
    return ("redirect", location)


def _ok(path, msg):
    sep = "&" if "?" in path else "?"
    return _redirect(f"{path}{sep}ok={urllib.parse.quote(str(msg))}")


def _err(path, msg):
    sep = "&" if "?" in path else "?"
    return _redirect(f"{path}{sep}error={urllib.parse.quote(str(msg))}")


def handle(path, form, files=None):
    if path == "/ec2/launch":
        return _launch(form)
    if path == "/ec2/action":
        return _state_action(form)
    return None


def _launch(form):
    name = (form.get("name") or "").strip()
    itype = (form.get("instance_type") or "t3.micro").strip()
    if not name:
        return _err("/ec2/launch", "Name required")
    ok_, msg, iid = ec2_mod.create(name, instance_type=itype)
    if not ok_:
        return _err("/ec2/launch", msg)
    return _ok(f"/ec2/instances/{urllib.parse.quote(iid)}", msg)


def _state_action(form):
    iid = (form.get("id") or "").strip()
    action = (form.get("action") or "").strip()
    if not iid or not action:
        return _err("/ec2/instances", "instance id and action required")

    inst = ec2_mod.get(iid)
    back = f"/ec2/instances/{urllib.parse.quote(iid)}" if inst else "/ec2/instances"

    funcs = {
        "start":     ec2_mod.start,
        "stop":      ec2_mod.stop,
        "reboot":    ec2_mod.reboot,
        "terminate": ec2_mod.terminate,
    }
    fn = funcs.get(action)
    if fn is None:
        return _err(back, f"unknown action '{action}'")

    ok_, msg = fn(iid)
    return _ok(back, msg) if ok_ else _err(back, msg)
