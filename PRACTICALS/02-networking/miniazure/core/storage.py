"""Storage accounts, containers, and blobs — like `az storage` in Azure."""
import os
import re
import shutil
from datetime import datetime

import config
from utils import (
    now_iso, read_json, write_json, delete_file, ensure_dir,
)
from core import resource_group as rg


STATE_STORAGE = os.path.join(config.STATE_DIR, "storage")
ACCOUNTS_DIR  = os.path.join(STATE_STORAGE, "accounts")
BLOBS_DIR     = os.path.join(STATE_STORAGE, "blobs")


ACCT_RE = re.compile(r"^[a-z0-9]{3,24}$")
CONT_RE = re.compile(r"^[a-z0-9][a-z0-9-]{1,61}[a-z0-9]$")
BLOB_RE = re.compile(r"^[a-zA-Z0-9._-]{1,255}$")


def validate_account_name(name):
    if not name:
        return "account name required"
    if not ACCT_RE.match(name):
        return ("account name must be 3-24 chars, lowercase letters "
                "and digits only (like Azure)")
    return None


def validate_container_name(name):
    if not name:
        return "container name required"
    if not CONT_RE.match(name):
        return ("container name must be 3-63 chars, start and end with "
                "letter/digit, lowercase letters, digits, hyphens only")
    return None


def validate_blob_name(name):
    if not name:
        return "blob name required"
    if not BLOB_RE.match(name):
        return "blob name must be 1-255 chars, no slashes or special chars"
    return None


def _account_path(name):
    return os.path.join(ACCOUNTS_DIR, f"{name}.json")


def _container_path(account, container):
    return os.path.join(BLOBS_DIR, account, container)


def _blob_path(account, container, blob):
    return os.path.join(_container_path(account, container), blob)


def _blob_meta_path(account, container, blob):
    return _blob_path(account, container, blob) + ".meta.json"


def create_account(name, group, region=None):
    e = validate_account_name(name)
    if e:
        return False, e

    if os.path.exists(_account_path(name)):
        return False, f"storage account '{name}' already exists"

    group_data = rg.get(group)
    if not group_data:
        return False, f"resource group '{group}' not found. Create it first."

    region = region or group_data.get("location", config.DEFAULT_REGION)

    data = {
        "id": f"/subscriptions/local/resourceGroups/{group}/providers/Microsoft.Storage/storageAccounts/{name}",
        "name": name,
        "type": "Microsoft.Storage/storageAccounts",
        "location": region,
        "resourceGroup": group,
        "sku": "Standard_LRS",
        "kind": "StorageV2",
        "properties": {
            "provisioningState": "Succeeded",
            "accessTier": "Hot",
        },
        "primaryEndpoints": {
            "blob": f"http://localhost:8080/{name}",
        },
        "created": now_iso(),
    }

    ensure_dir(ACCOUNTS_DIR)
    write_json(_account_path(name), data)
    ensure_dir(os.path.join(BLOBS_DIR, name))
    return True, f"created storage account '{name}' in group '{group}'"


def get_account(name):
    return read_json(_account_path(name))


def list_accounts():
    ensure_dir(ACCOUNTS_DIR)
    out = []
    for f in sorted(os.listdir(ACCOUNTS_DIR)):
        if f.endswith(".json"):
            data = read_json(os.path.join(ACCOUNTS_DIR, f))
            if data:
                out.append(data)
    return out


def delete_account(name):
    if not get_account(name):
        return False, f"storage account '{name}' not found"
    delete_file(_account_path(name))
    shutil.rmtree(os.path.join(BLOBS_DIR, name), ignore_errors=True)
    return True, f"deleted storage account '{name}'"


def create_container(account, container):
    e = validate_container_name(container)
    if e:
        return False, e

    if not get_account(account):
        return False, f"storage account '{account}' not found"

    path = _container_path(account, container)
    if os.path.isdir(path):
        return False, f"container '{container}' already exists in '{account}'"

    ensure_dir(path)
    write_json(os.path.join(path, ".container.json"), {
        "name": container,
        "account": account,
        "created": now_iso(),
    })
    return True, f"created container '{container}' in account '{account}'"


def list_containers(account):
    if not get_account(account):
        return None
    base = os.path.join(BLOBS_DIR, account)
    ensure_dir(base)
    containers = []
    for entry in sorted(os.listdir(base)):
        full = os.path.join(base, entry)
        if os.path.isdir(full):
            containers.append(entry)
    return containers


def delete_container(account, container):
    path = _container_path(account, container)
    if not os.path.isdir(path):
        return False, f"container '{container}' not found in '{account}'"
    shutil.rmtree(path)
    return True, f"deleted container '{container}'"


def upload_blob(account, container, blob_name, local_path):
    e = validate_blob_name(blob_name)
    if e:
        return False, e

    if not get_account(account):
        return False, f"storage account '{account}' not found"
    if not os.path.isdir(_container_path(account, container)):
        return False, f"container '{container}' not found in '{account}'"

    if not os.path.isfile(local_path):
        return False, f"local file not found: {local_path}"

    dest = _blob_path(account, container, blob_name)
    ensure_dir(os.path.dirname(dest))

    size = os.path.getsize(local_path)
    with open(local_path, "rb") as src, open(dest, "wb") as out:
        shutil.copyfileobj(src, out)

    meta = {
        "name": blob_name,
        "account": account,
        "container": container,
        "size": size,
        "url": f"http://localhost:8080/{account}/{container}/{blob_name}",
        "uploaded": now_iso(),
        "contentType": _guess_content_type(blob_name),
    }
    write_json(_blob_meta_path(account, container, blob_name), meta)

    return True, meta["url"]


def list_blobs(account, container):
    path = _container_path(account, container)
    if not os.path.isdir(path):
        return None
    blobs = []
    for entry in sorted(os.listdir(path)):
        if entry == ".container.json" or entry.endswith(".meta.json"):
            continue
        full = os.path.join(path, entry)
        if os.path.isfile(full):
            meta = read_json(_blob_meta_path(account, container, entry)) or {}
            blobs.append({
                "name": entry,
                "size": os.path.getsize(full),
                "uploaded": meta.get("uploaded", "?"),
            })
    return blobs


def delete_blob(account, container, blob_name):
    path = _blob_path(account, container, blob_name)
    meta_path = _blob_meta_path(account, container, blob_name)
    if not os.path.isfile(path):
        return False, f"blob '{blob_name}' not found"
    os.remove(path)
    if os.path.isfile(meta_path):
        os.remove(meta_path)
    return True, f"deleted blob '{blob_name}'"


def get_blob_path(account, container, blob_name):
    path = _blob_path(account, container, blob_name)
    if not os.path.isfile(path):
        return None
    return path


def _guess_content_type(name):
    ext = name.rsplit(".", 1)[-1].lower() if "." in name else ""
    return {
        "jpg": "image/jpeg", "jpeg": "image/jpeg", "png": "image/png",
        "gif": "image/gif", "txt": "text/plain", "html": "text/html",
        "json": "application/json", "pdf": "application/pdf",
    }.get(ext, "application/octet-stream")
