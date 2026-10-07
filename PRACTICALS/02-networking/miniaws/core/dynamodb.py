"""DynamoDB — AWS's NoSQL key-value store (simulated)."""
import os

import config
from utils import (
    now_iso, make_arn,
    read_json, write_json, delete_file, ensure_dir,
)
from core import account


DYNAMO_DIR = os.path.join(config.STATE_DIR, "dynamodb")
TABLES_DIR = os.path.join(DYNAMO_DIR, "tables")


def _table_path(name):
    return os.path.join(TABLES_DIR, f"{name}.json")


def _ensure():
    ensure_dir(TABLES_DIR)


def create_table(table_name, key_name, key_type="S"):
    """Create a DynamoDB table. key_type: S=string, N=number."""
    if not table_name:
        return False, "table name required"
    if not key_name:
        return False, "key schema required (e.g., --key-schema 'id:S')"

    if os.path.exists(_table_path(table_name)):
        return False, f"table '{table_name}' already exists"

    region = account.get_region()
    account_id = account.get_account_id()

    data = {
        "TableName": table_name,
        "TableArn": make_arn("dynamodb", region, account_id, f"table/{table_name}"),
        "TableStatus": "ACTIVE",
        "KeySchema": [{"AttributeName": key_name, "KeyType": "HASH"}],
        "AttributeDefinitions": [{"AttributeName": key_name, "AttributeType": key_type}],
        "ItemCount": 0,
        "CreationDateTime": now_iso(),
        "items": {},
        "key_name": key_name,
        "key_type": key_type,
    }
    _ensure()
    write_json(_table_path(table_name), data)
    return True, f"created table '{table_name}' (key: {key_name}, type: {key_type})"


def list_tables():
    _ensure()
    out = []
    if not os.path.isdir(TABLES_DIR):
        return out
    for f in sorted(os.listdir(TABLES_DIR)):
        if f.endswith(".json"):
            d = read_json(os.path.join(TABLES_DIR, f))
            if d:
                out.append(d)
    return out


def get_table(name):
    return read_json(_table_path(name))


def delete_table(name):
    if not get_table(name):
        return False, f"table '{name}' not found"
    delete_file(_table_path(name))
    return True, f"deleted table '{name}'"


def put_item(table_name, item):
    """Put an item (create or replace)."""
    t = get_table(table_name)
    if not t:
        return False, f"table '{table_name}' not found"
    if not isinstance(item, dict):
        return False, "item must be a dict"

    key_name = t["key_name"]
    if key_name not in item:
        return False, f"item must contain key '{key_name}'"

    key_value = str(item[key_name])
    t["items"][key_value] = item
    t["ItemCount"] = len(t["items"])
    write_json(_table_path(table_name), t)
    return True, f"put item (key: {key_name}={key_value})"


def get_item(table_name, key_value):
    t = get_table(table_name)
    if not t:
        return False, f"table '{table_name}' not found"
    item = t["items"].get(str(key_value))
    return True, item


def delete_item(table_name, key_value):
    t = get_table(table_name)
    if not t:
        return False, f"table '{table_name}' not found"
    if str(key_value) not in t["items"]:
        return False, f"item with key '{key_value}' not found"
    del t["items"][str(key_value)]
    t["ItemCount"] = len(t["items"])
    write_json(_table_path(table_name), t)
    return True, f"deleted item (key={key_value})"


def scan_table(table_name):
    t = get_table(table_name)
    if not t:
        return False, f"table '{table_name}' not found"
    return True, list(t["items"].values())
