"""S3 — AWS's object storage.

Model:
  bucket  -> a globally-unique named container
  object  -> a file with a key (may contain slashes)

On disk:
  state/s3/buckets/<bucket>/          (bucket metadata + objects)
    .bucket.json                      (bucket metadata)
    <key>                             (object bytes)
    <key>.meta.json                   (object metadata)
"""
import os
import re
import shutil

import config
from utils import (
    now_iso, make_arn,
    read_json, write_json, delete_file, ensure_dir,
)
from core import account


S3_DIR        = os.path.join(config.STATE_DIR, "s3")
BUCKETS_DIR   = os.path.join(S3_DIR, "buckets")


# AWS rules: 3-63 chars, lowercase, digits, hyphens, dots
BUCKET_RE = re.compile(r"^[a-z0-9][a-z0-9.-]{1,61}[a-z0-9]$")


def validate_bucket_name(name):
    if not name:
        return "bucket name required"
    if not BUCKET_RE.match(name):
        return ("bucket name must be 3-63 chars, lowercase letters, digits, "
                "hyphens, dots; must start and end with a letter or digit")
    return None


def _bucket_path(bucket):
    return os.path.join(BUCKETS_DIR, bucket)


def _bucket_meta_path(bucket):
    return os.path.join(_bucket_path(bucket), ".bucket.json")


def _obj_path(bucket, key):
    return os.path.join(_bucket_path(bucket), key)


def _obj_meta_path(bucket, key):
    return _obj_path(bucket, key) + ".meta.json"


def mb_bucket(name):
    """Create a bucket (like `aws s3 mb`)."""
    e = validate_bucket_name(name)
    if e:
        return False, e

    if not account.is_initialized():
        return False, "account not initialized. Run: aws configure"

    if os.path.isdir(_bucket_path(name)):
        return False, f"BucketAlreadyOwnedByYou: bucket '{name}' already exists and is owned by you"

    ensure_dir(_bucket_path(name))

    region = account.get_region()
    account_id = account.get_account_id()

    meta = {
        "name": name,
        "arn": make_arn("s3", region, account_id, name),
        "region": region,
        "account_id": account_id,
        "url": f"https://{name}.s3.{region}.amazonaws.com",
        "created": now_iso(),
    }
    write_json(_bucket_meta_path(name), meta)
    return True, f"make_bucket: {name}"


def ls_buckets():
    """List all buckets."""
    ensure_dir(BUCKETS_DIR)
    out = []
    for entry in sorted(os.listdir(BUCKETS_DIR)):
        full = os.path.join(BUCKETS_DIR, entry)
        if os.path.isdir(full):
            meta = read_json(_bucket_meta_path(entry))
            if meta:
                out.append(meta)
    return out


def get_bucket(name):
    return read_json(_bucket_meta_path(name))


def bucket_exists(name):
    return os.path.isdir(_bucket_path(name))


def rb_bucket(name, force=False):
    """Remove a bucket (like `aws s3 rb`). Refuses non-empty unless force."""
    if not bucket_exists(name):
        return False, f"bucket '{name}' not found"
    contents = list_objects(name)
    if contents and not force:
        return False, (f"bucket '{name}' not empty ({len(contents)} objects). "
                       "Use --force to delete anyway.")
    shutil.rmtree(_bucket_path(name))
    return True, f"remove_bucket: {name}"


# ---- Object operations ----

def put_object(bucket, key, local_path):
    """Upload a local file as an object."""
    if not bucket_exists(bucket):
        return False, f"bucket '{bucket}' not found"
    if not os.path.isfile(local_path):
        return False, f"local file not found: {local_path}"
    if not key:
        return False, "key required"

    dest = _obj_path(bucket, key)
    ensure_dir(os.path.dirname(dest))

    size = os.path.getsize(local_path)
    with open(local_path, "rb") as src, open(dest, "wb") as out:
        shutil.copyfileobj(src, out)

    region = account.get_region()
    url = f"https://{bucket}.s3.{region}.amazonaws.com/{key}"

    meta = {
        "key": key,
        "bucket": bucket,
        "size": size,
        "url": url,
        "uploaded": now_iso(),
        "contentType": _guess_content_type(key),
    }
    write_json(_obj_meta_path(bucket, key), meta)
    return True, url


def put_object_bytes(bucket, key, data, content_type=None):
    """Upload bytes directly."""
    if not bucket_exists(bucket):
        return False, f"bucket '{bucket}' not found"

    dest = _obj_path(bucket, key)
    ensure_dir(os.path.dirname(dest))
    with open(dest, "wb") as out:
        out.write(data)

    region = account.get_region()
    url = f"https://{bucket}.s3.{region}.amazonaws.com/{key}"

    meta = {
        "key": key,
        "bucket": bucket,
        "size": len(data),
        "url": url,
        "uploaded": now_iso(),
        "contentType": content_type or _guess_content_type(key),
    }
    write_json(_obj_meta_path(bucket, key), meta)
    return True, url


def list_objects(bucket, prefix=""):
    """List objects in a bucket, optionally filtered by prefix."""
    if not bucket_exists(bucket):
        return None

    base = _bucket_path(bucket)
    out = []

    for root, dirs, files in os.walk(base):
        for f in files:
            full = os.path.join(root, f)
            rel = os.path.relpath(full, base)
            if rel == ".bucket.json" or rel.endswith(".meta.json"):
                continue
            if prefix and not rel.startswith(prefix):
                continue
            meta = read_json(_obj_meta_path(bucket, rel)) or {}
            out.append({
                "key": rel,
                "size": os.path.getsize(full),
                "uploaded": meta.get("uploaded", "?"),
            })

    out.sort(key=lambda x: x["key"])
    return out


def get_object_path(bucket, key):
    """Return path to object bytes (used by HTTP server)."""
    path = _obj_path(bucket, key)
    if not os.path.isfile(path):
        return None
    return path


def rm_object(bucket, key):
    path = _obj_path(bucket, key)
    meta = _obj_meta_path(bucket, key)
    if not os.path.isfile(path):
        return False, f"object not found: {key}"
    os.remove(path)
    if os.path.isfile(meta):
        os.remove(meta)
    return True, f"delete: s3://{bucket}/{key}"


def cp_object(src_bucket, src_key, dst_bucket, dst_key):
    """Copy between buckets (in same MiniAWS)."""
    src = _obj_path(src_bucket, src_key)
    if not os.path.isfile(src):
        return False, f"source not found: s3://{src_bucket}/{src_key}"
    if not bucket_exists(dst_bucket):
        return False, f"dest bucket not found: {dst_bucket}"

    dst = _obj_path(dst_bucket, dst_key)
    ensure_dir(os.path.dirname(dst))
    shutil.copyfile(src, dst)

    region = account.get_region()
    write_json(_obj_meta_path(dst_bucket, dst_key), {
        "key": dst_key, "bucket": dst_bucket,
        "size": os.path.getsize(dst),
        "url": f"https://{dst_bucket}.s3.{region}.amazonaws.com/{dst_key}",
        "uploaded": now_iso(),
        "contentType": _guess_content_type(dst_key),
    })
    return True, f"copy: s3://{src_bucket}/{src_key} -> s3://{dst_bucket}/{dst_key}"


def _guess_content_type(name):
    ext = name.rsplit(".", 1)[-1].lower() if "." in name else ""
    return {
        "jpg": "image/jpeg", "jpeg": "image/jpeg", "png": "image/png",
        "gif": "image/gif", "txt": "text/plain", "html": "text/html",
        "json": "application/json", "pdf": "application/pdf",
    }.get(ext, "application/octet-stream")


# ---- s3:// URI parsing ----

def parse_s3_uri(uri):
    """
    Parse s3://bucket/key or s3://bucket/prefix/
    Returns (bucket, key) or (None, None).
    """
    if not uri.startswith("s3://"):
        return None, None
    rest = uri[5:]
    if "/" not in rest:
        return rest, ""
    bucket, key = rest.split("/", 1)
    return bucket, key
