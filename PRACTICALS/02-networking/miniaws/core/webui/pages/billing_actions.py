"""Billing form actions — create/delete budget."""
import urllib.parse

from core.webui import billing_store


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
        "/billing/budgets/create": _create,
        "/billing/budgets/delete": _delete,
    }
    fn = routes.get(path)
    return fn(form) if fn else None


def _create(form):
    name = (form.get("name") or "").strip()
    amount_raw = (form.get("amount") or "").strip()
    if not name:
        return _err("/billing/budgets/create", "name required")
    try:
        amount = float(amount_raw)
    except ValueError:
        return _err("/billing/budgets/create", "amount must be a number")
    ok_, msg = billing_store.add_budget(name, amount)
    if not ok_:
        return _err("/billing/budgets/create", msg)
    return _ok("/billing", msg)


def _delete(form):
    name = (form.get("name") or "").strip()
    if not name:
        return _err("/billing", "name required")
    ok_, msg = billing_store.delete_budget(name)
    return _ok("/billing", msg) if ok_ else _err("/billing", msg)
