"""S3 form actions — the POST side of the browser (create/upload/delete).

Mirrors console_actions.py shape: handle() returns
  ("redirect", "/some/path?ok=...") or ("html", "<error>")
"""
import urllib.parse

from core import s3 as s3_mod


def _redirect(location):
    return ("redirect", location)


def _ok(path, msg):
    sep = "&" if "?" in path else "?"
    return _redirect(f"{path}{sep}ok={urllib.parse.quote(str(msg))}")


def _err(path, msg):
    sep = "&" if "?" in path else "?"
    return _redirect(f"{path}{sep}error={urllib.parse.quote(str(msg))}")


def handle(path, form, files=None):
    """Dispatch a POST to the right S3 action."""
    files = files or {}

    if path == "/s3/create":
        return _create_bucket(form)
    if path == "/s3/upload":
        return _upload_object(form, files)
    if path == "/s3/delete-object":
        return _delete_object(form)
    if path == "/s3/delete-bucket":
        return _delete_bucket(form)
    return None


# ---------- Actions ----------

def _create_bucket(form):
    name = (form.get("bucket") or "").strip()
    if not name:
        return _err("/s3/create", "Bucket name required")
    ok_, msg = s3_mod.mb_bucket(name)
    if not ok_:
        return _err("/s3/create", msg)
    return _ok(f"/s3/{urllib.parse.quote(name)}", msg)


def _upload_object(form, files):
    bucket = (form.get("bucket") or "").strip()
    if not bucket:
        return _err("/s3", "bucket required")

    back = f"/s3/{urllib.parse.quote(bucket)}"

    # File picker path
    if "file" in files:
        fname, _ctype, data = files["file"]
        if not fname:
            return _err(back, "no file selected")
        key = fname.split("/")[-1]
        ok_, msg = s3_mod.put_object_bytes(bucket, key, data)
        return _ok(back, msg) if ok_ else _err(back, msg)

    # Textarea fallback
    text = form.get("body") or ""
    key = (form.get("key") or "").strip()
    if not key:
        return _err(back, "object key required")
    if not text:
        return _err(back, "body required")
    ok_, msg = s3_mod.put_object_bytes(bucket, key, text.encode("utf-8"))
    return _ok(back, msg) if ok_ else _err(back, msg)


def _delete_object(form):
    bucket = (form.get("bucket") or "").strip()
    key = (form.get("key") or "").strip()
    back = f"/s3/{urllib.parse.quote(bucket)}"
    if not bucket or not key:
        return _err(back, "bucket and key required")
    ok_, msg = s3_mod.rm_object(bucket, key)
    return _ok(back, msg) if ok_ else _err(back, msg)


def _delete_bucket(form):
    bucket = (form.get("bucket") or "").strip()
    if not bucket:
        return _err("/s3", "bucket required")
    ok_, msg = s3_mod.rb_bucket(bucket, force=False)
    if not ok_:
        return _err(f"/s3/{urllib.parse.quote(bucket)}", msg)
    return _ok("/s3", msg)
