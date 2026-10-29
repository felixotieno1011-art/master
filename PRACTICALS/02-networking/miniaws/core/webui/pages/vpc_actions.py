"""VPC form actions — create/delete for all six resource types."""
import urllib.parse

from core import vpc as vpc_mod
from core import sg as sg_mod
from core import nat as nat_mod
from core.webui import permissions


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
        "/vpc/create":          _create_vpc,
        "/vpc/delete":          _delete_vpc,
        "/vpc/subnets/create":  _create_subnet,
        "/vpc/subnets/delete":  _delete_subnet,
        "/vpc/igws/create":     _create_igw,
        "/vpc/igws/attach":     _attach_igw,
        "/vpc/igws/detach":     _detach_igw,
        "/vpc/igws/delete":     _delete_igw,
        "/vpc/nats/create":     _create_nat,
        "/vpc/nats/delete":     _delete_nat,
        "/vpc/sgs/create":      _create_sg,
        "/vpc/sgs/delete":      _delete_sg,
    }
    fn = routes.get(path)
    return fn(form) if fn else None


# ---------- VPC ----------

def _create_vpc(form):
    allowed, err = permissions.require("ec2:CreateVpc", back="/vpc/create")
    if not allowed:
        return err
    cidr = (form.get("cidr") or "").strip()
    if not cidr:
        return _err("/vpc/create", "CIDR required")
    ok_, msg = vpc_mod.create_vpc(cidr)
    if not ok_:
        return _err("/vpc/create", msg)
    return _ok("/vpc", msg)


def _delete_vpc(form):
    vid = (form.get("vpc_id") or "").strip()
    if not vid:
        return _err("/vpc", "vpc_id required")
    ok_, msg = vpc_mod.delete_vpc(vid)
    return _ok("/vpc", msg) if ok_ else _err(f"/vpc/{urllib.parse.quote(vid)}", msg)


# ---------- Subnets ----------

def _create_subnet(form):
    vid = (form.get("vpc_id") or "").strip()
    cidr = (form.get("cidr") or "").strip()
    name = (form.get("name") or "").strip() or None
    if not vid or not cidr:
        return _err("/vpc/subnets/create", "VPC and CIDR required")
    ok_, msg = vpc_mod.create_subnet(vid, cidr, name=name)
    if not ok_:
        return _err("/vpc/subnets/create", msg)
    return _ok("/vpc/subnets", msg)


def _delete_subnet(form):
    sid = (form.get("subnet_id") or "").strip()
    if not sid:
        return _err("/vpc/subnets", "subnet_id required")
    ok_, msg = vpc_mod.delete_subnet(sid)
    if not ok_:
        return _err(f"/vpc/subnets/{urllib.parse.quote(sid)}", msg)
    return _ok("/vpc/subnets", msg)


# ---------- IGWs ----------

def _create_igw(form):
    name = (form.get("name") or "").strip() or None
    ok_, msg = vpc_mod.create_internet_gateway(name=name)
    if not ok_:
        return _err("/vpc/igws/create", msg)
    return _ok("/vpc/igws", msg)


def _attach_igw(form):
    iid = (form.get("igw_id") or "").strip()
    vid = (form.get("vpc_id") or "").strip()
    if not iid or not vid:
        return _err("/vpc/igws", "igw_id and vpc_id required")
    ok_, msg = vpc_mod.attach_internet_gateway(iid, vid)
    return _ok("/vpc/igws", msg) if ok_ else _err("/vpc/igws", msg)


def _detach_igw(form):
    iid = (form.get("igw_id") or "").strip()
    vid = (form.get("vpc_id") or "").strip()
    if not iid or not vid:
        return _err("/vpc/igws", "igw_id and vpc_id required")
    ok_, msg = vpc_mod.detach_internet_gateway(iid, vid)
    return _ok("/vpc/igws", msg) if ok_ else _err("/vpc/igws", msg)


def _delete_igw(form):
    iid = (form.get("igw_id") or "").strip()
    if not iid:
        return _err("/vpc/igws", "igw_id required")
    ok_, msg = vpc_mod.delete_internet_gateway(iid)
    return _ok("/vpc/igws", msg) if ok_ else _err("/vpc/igws", msg)


# ---------- NATs ----------

def _create_nat(form):
    sid = (form.get("subnet_id") or "").strip()
    if not sid:
        return _err("/vpc/nats/create", "subnet_id required")
    ok_, msg = nat_mod.create_nat_gateway(sid)
    if not ok_:
        return _err("/vpc/nats/create", msg)
    return _ok("/vpc/nats", msg)


def _delete_nat(form):
    nid = (form.get("nat_id") or "").strip()
    if not nid:
        return _err("/vpc/nats", "nat_id required")
    ok_, msg = nat_mod.delete_nat_gateway(nid)
    return _ok("/vpc/nats", msg) if ok_ else _err("/vpc/nats", msg)


# ---------- SGs ----------

def _create_sg(form):
    name = (form.get("name") or "").strip()
    desc = (form.get("description") or "").strip()
    vid = (form.get("vpc_id") or "").strip() or None
    if not name:
        return _err("/vpc/sgs/create", "name required")
    ok_, msg, _sgid = sg_mod.create_security_group(name, description=desc, vpc_id=vid)
    if not ok_:
        return _err("/vpc/sgs/create", msg)
    return _ok("/vpc/security-groups", msg)


def _delete_sg(form):
    sid = (form.get("sg_id") or "").strip()
    if not sid:
        return _err("/vpc/security-groups", "sg_id required")
    ok_, msg = sg_mod.delete_security_group(sid)
    return _ok("/vpc/security-groups", msg) if ok_ else _err("/vpc/security-groups", msg)
