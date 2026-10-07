"""Actions triggered by console forms (POST handlers)."""
import os
import tempfile
import urllib.parse

from core import vpc as vpc_mod
from core import sg as sg_mod
from core import s3 as s3_mod
from core import nat as nat_mod
from core import lambda_svc
from core import dynamodb as ddb_mod


def _redirect(location):
    return ("redirect", location)


def _ok_redirect(msg):
    return _redirect(f"/?ok={urllib.parse.quote(str(msg))}")


def _err_redirect(msg):
    return _redirect(f"/?error={urllib.parse.quote(str(msg))}")


def handle(path, form):
    route = ROUTES.get(path)
    if route is None:
        return None
    return route(form)


# ---------- Create actions ----------

def _create_vpc(form):
    cidr = form.get("cidr", "").strip()
    if not cidr:
        return _err_redirect("CIDR required")
    ok_, msg = vpc_mod.create_vpc(cidr)
    return _ok_redirect(msg) if ok_ else _err_redirect(msg)


def _create_subnet(form):
    vpc_id = form.get("vpc_id", "").strip()
    cidr = form.get("cidr", "").strip()
    name = form.get("name", "").strip() or None
    if not vpc_id or not cidr:
        return _err_redirect("VPC and CIDR required")
    ok_, msg = vpc_mod.create_subnet(vpc_id, cidr, name=name)
    return _ok_redirect(msg) if ok_ else _err_redirect(msg)


def _create_sg(form):
    name = form.get("name", "").strip()
    desc = form.get("description", "").strip()
    vpc_id = form.get("vpc_id", "").strip() or None
    if not name:
        return _err_redirect("Name required")
    ok_, msg, _sid = sg_mod.create_security_group(name, description=desc, vpc_id=vpc_id)
    return _ok_redirect(msg) if ok_ else _err_redirect(msg)


def _create_s3(form):
    name = form.get("bucket", "").strip()
    if not name:
        return _err_redirect("Bucket name required")
    ok_, msg = s3_mod.mb_bucket(name)
    return _ok_redirect(msg) if ok_ else _err_redirect(msg)


def _create_lambda(form):
    name = form.get("name", "").strip()
    code = form.get("code", "").strip()
    if not name or not code:
        return _err_redirect("Name and code required")

    fd, path = tempfile.mkstemp(suffix=".py", prefix="lambda_")
    try:
        with os.fdopen(fd, "w") as f:
            f.write(code)
        ok_, msg, _ = lambda_svc.create_function(name, code_path=path)
    finally:
        try:
            os.remove(path)
        except Exception:
            pass

    return _ok_redirect(msg) if ok_ else _err_redirect(msg)


def _create_table(form):
    name = form.get("table_name", "").strip()
    key_name = form.get("key_name", "").strip()
    key_type = form.get("key_type", "S").strip().upper()
    if not name or not key_name:
        return _err_redirect("Table name and key name required")
    ok_, msg = ddb_mod.create_table(name, key_name, key_type)
    return _ok_redirect(msg) if ok_ else _err_redirect(msg)


# ---------- Delete actions ----------

def _delete_vpc(form):
    vpc_id = form.get("vpc_id", "").strip()
    if not vpc_id:
        return _err_redirect("VPC ID required")
    ok_, msg = vpc_mod.delete_vpc(vpc_id)
    return _ok_redirect(msg) if ok_ else _err_redirect(msg)


def _delete_subnet(form):
    subnet_id = form.get("subnet_id", "").strip()
    if not subnet_id:
        return _err_redirect("Subnet ID required")
    ok_, msg = vpc_mod.delete_subnet(subnet_id)
    return _ok_redirect(msg) if ok_ else _err_redirect(msg)


def _delete_sg(form):
    sg_id = form.get("sg_id", "").strip()
    if not sg_id:
        return _err_redirect("SG ID required")
    ok_, msg = sg_mod.delete_security_group(sg_id)
    return _ok_redirect(msg) if ok_ else _err_redirect(msg)


def _delete_nat(form):
    nat_id = form.get("nat_id", "").strip()
    if not nat_id:
        return _err_redirect("NAT ID required")
    ok_, msg = nat_mod.delete_nat_gateway(nat_id)
    return _ok_redirect(msg) if ok_ else _err_redirect(msg)


def _delete_lambda(form):
    name = form.get("function_name", "").strip()
    if not name:
        return _err_redirect("Function name required")
    ok_, msg = lambda_svc.delete_function(name)
    return _ok_redirect(msg) if ok_ else _err_redirect(msg)


def _delete_table(form):
    name = form.get("table_name", "").strip()
    if not name:
        return _err_redirect("Table name required")
    ok_, msg = ddb_mod.delete_table(name)
    return _ok_redirect(msg) if ok_ else _err_redirect(msg)


ROUTES = {
    "/create-vpc":    _create_vpc,
    "/create-subnet": _create_subnet,
    "/create-sg":     _create_sg,
    "/create-s3":     _create_s3,
    "/create-lambda": _create_lambda,
    "/create-table":  _create_table,
    "/delete-vpc":    _delete_vpc,
    "/delete-subnet": _delete_subnet,
    "/delete-sg":     _delete_sg,
    "/delete-nat":    _delete_nat,
    "/delete-lambda": _delete_lambda,
    "/delete-table":  _delete_table,
}
