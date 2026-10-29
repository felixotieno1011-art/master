"""Budget storage — separate from lib/billing.py so CLI is untouched.

Budgets live in state/billing-budgets.json as a plain list:
  [{"name": "Monthly", "amount": 5.00, "created": "2026-10-29T14:30:00"}]

Actual spend is computed live from lib/billing.get_total() on read — never
stored, so it can't drift.
"""
import json
import os

import config
from utils import now_iso, read_json, write_json, ensure_dir


BUDGETS_FILE = os.path.join(config.STATE_DIR, "billing-budgets.json")


def _ensure():
    ensure_dir(os.path.dirname(BUDGETS_FILE))


def list_budgets():
    _ensure()
    data = read_json(BUDGETS_FILE)
    if not isinstance(data, list):
        return []
    return data


def save_budgets(budgets):
    _ensure()
    write_json(BUDGETS_FILE, budgets)


def add_budget(name, amount):
    if not name or not isinstance(amount, (int, float)):
        return False, "name and numeric amount required"
    if amount <= 0:
        return False, "amount must be positive"
    budgets = list_budgets()
    for b in budgets:
        if b.get("name") == name:
            return False, f"budget '{name}' already exists"
    budgets.append({
        "name": name,
        "amount": float(amount),
        "created": now_iso(),
    })
    save_budgets(budgets)
    return True, f"created budget '{name}' (${amount:.2f})"


def delete_budget(name):
    budgets = list_budgets()
    remaining = [b for b in budgets if b.get("name") != name]
    if len(remaining) == len(budgets):
        return False, f"budget '{name}' not found"
    save_budgets(remaining)
    return True, f"deleted budget '{name}'"


def budget_status():
    """Return list of budgets with computed actual + status.
    Adds: actual, percentage, status ("OK" / "WARNING" / "OVER_BUDGET").
    """
    try:
        from lib import billing as _billing
        actual = float(_billing.get_total())
    except Exception:
        actual = 0.0

    out = []
    for b in list_budgets():
        amt = float(b.get("amount", 0))
        pct = (actual / amt * 100.0) if amt > 0 else 0.0
        if actual > amt:
            status = "OVER_BUDGET"
        elif pct >= 80:
            status = "WARNING"
        else:
            status = "OK"
        out.append({
            "name": b.get("name"),
            "amount": amt,
            "actual": actual,
            "percentage": pct,
            "status": status,
            "created": b.get("created", ""),
        })
    return out
