"""S3 API — low-level commands matching AWS's s3api syntax.

These are thin wrappers around core/s3.py functions,
but with the exact flag names real AWS uses.
"""
import os

from core import s3 as s3_mod


def list_buckets():
    """Return list of buckets in AWS-style dict format."""
    buckets = s3_mod.ls_buckets()
    return {
        "Buckets": [
            {
                "Name": b["name"],
                "CreationDate": b.get("created", ""),
            }
            for b in buckets
        ],
        "Owner": {
            "DisplayName": "miniaws",
            "ID": "miniaws-owner-id",
        },
    }


def create_bucket(bucket_name):
    """Create a bucket."""
    if not bucket_name:
        return False, "bucket name required"
    return s3_mod.mb_bucket(bucket_name)


def list_objects(bucket_name, prefix=""):
    """List objects in a bucket."""
    if not bucket_name:
        return False, "bucket name required"
    objs = s3_mod.list_objects(bucket_name, prefix=prefix)
    if objs is None:
        return False, f"bucket '{bucket_name}' not found"
    return True, {
        "Name": bucket_name,
        "Prefix": prefix,
        "Contents": [
            {
                "Key": o["key"],
                "Size": o["size"],
                "LastModified": o.get("uploaded", ""),
            }
            for o in objs
        ],
        "KeyCount": len(objs),
    }


def put_object(bucket_name, key, body_path):
    """Upload an object (like aws s3api put-object)."""
    if not bucket_name or not key:
        return False, "bucket and key required"
    if not body_path:
        return False, "--body <file> required"
    return s3_mod.put_object(bucket_name, key, body_path)


def delete_object(bucket_name, key):
    """Delete an object."""
    if not bucket_name or not key:
        return False, "bucket and key required"
    return s3_mod.rm_object(bucket_name, key)


def delete_bucket(bucket_name):
    """Delete a bucket (must be empty unless --force)."""
    if not bucket_name:
        return False, "bucket name required"
    return s3_mod.rb_bucket(bucket_name, force=False)


def head_bucket(bucket_name):
    """Check if a bucket exists."""
    if not bucket_name:
        return False, "bucket name required"
    if s3_mod.bucket_exists(bucket_name):
        return True, f"bucket '{bucket_name}' exists"
    return False, f"bucket '{bucket_name}' not found"
