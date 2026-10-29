"""DynamoDB form actions — create/delete table, put/delete item."""
import json
import urllib.parse

from core import dynamodb as ddb
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
        "/dynamodb/tables/create":       _create_table,
        "/dynamodb/tables/delete":       _delete_table,
        "/dynamodb/tables/create-item":  _create_item,
        "/dynamodb/tables/delete-item":  _delete_item,
    }
    fn = routes.get(path)
    return fn(form) if fn else None


def _create_table(form):
    allowed, err = permissions.require("dynamodb:CreateTable", back="/dynamodb/tables/create")
    if not allowed:
        return err
    name = (form.get("table_name") or "").strip()
    key_name = (form.get("key_name") or "").strip()
    key_type = (form.get("key_type") or "S").strip().upper()
    if not name or not key_name:
        return _err("/dynamodb/tables/create", "table_name and key_name required")
    ok_, msg = ddb.create_table(name, key_name, key_type=key_type)
    if not ok_:
        return _err("/dynamodb/tables/create", msg)
    return _ok(f"/dynamodb/tables/{urllib.parse.quote(name)}", msg)


def _delete_table(form):
    name = (form.get("table") or "").strip()
    if not name:
        return _err("/dynamodb/tables", "table required")
    ok_, msg = ddb.delete_table(name)
    return _ok("/dynamodb/tables", msg) if ok_ else _err(f"/dynamodb/tables/{urllib.parse.quote(name)}", msg)


def _create_item(form):
    table = (form.get("table") or "").strip()
    allowed, err = permissions.require("dynamodb:PutItem", back=f"/dynamodb/tables/{table}/items/create")
    if not allowed:
        return err
    raw = (form.get("item_json") or "").strip()
    if not table or not raw:
        return _err("/dynamodb/tables", "table and item_json required")
    back = f"/dynamodb/tables/{urllib.parse.quote(table)}/items"
    try:
        item = json.loads(raw)
    except json.JSONDecodeError as e:
        return _err(back, f"invalid JSON: {e}")
    if not isinstance(item, dict):
        return _err(back, "item must be a JSON object")
    ok_, msg = ddb.put_item(table, item)
    return _ok(back, msg) if ok_ else _err(back, msg)


def _delete_item(form):
    table = (form.get("table") or "").strip()
    key_value = (form.get("key_value") or "").strip()
    if not table or not key_value:
        return _err("/dynamodb/tables", "table and key_value required")
    back = f"/dynamodb/tables/{urllib.parse.quote(table)}/items"
    ok_, msg = ddb.delete_item(table, key_value)
    return _ok(back, msg) if ok_ else _err(back, msg)
