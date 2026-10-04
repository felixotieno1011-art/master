"""Measure download and upload speed using curl. No installs needed.

Termux note: '/tmp' does not exist. Use tempfile.gettempdir() which
returns the correct temp directory on every platform.
"""
import subprocess
import time
import os
import tempfile
from config import SPEED_TIMEOUT


DOWNLOAD_URLS = [
    "https://speed.cloudflare.com/__down?bytes=10000000",   # 10 MB
    "http://speedtest.tele2.net/10MB.zip",                  # fallback
]

UPLOAD_URL = "https://speed.cloudflare.com/__up"
UPLOAD_SIZE_MB = 0.25     # small — mobile carriers throttle big uploads
UPLOAD_TIMEOUT = 10       # seconds


def _try_download():
    for url in DOWNLOAD_URLS:
        try:
            start = time.time()
            result = subprocess.run(
                ["curl", "-s", "-o", "/dev/null",
                 "-w", "%{size_download}",
                 "--max-time", str(SPEED_TIMEOUT),
                 url],
                capture_output=True, text=True,
                timeout=SPEED_TIMEOUT + 5
            )
            elapsed = time.time() - start
            size = int(result.stdout.strip() or 0)
            if size > 0 and elapsed > 0:
                mbps = round((size * 8) / (elapsed * 1_000_000), 2)
                return mbps, size
        except Exception:
            continue
    return None, 0


def _try_upload():
    """Upload a small file. Returns (mbps, bytes) or (None, 0)."""
    tmp_path = os.path.join(tempfile.gettempdir(), "nm_upload.bin")

    try:
        # Create the temp file with os.urandom (portable, no dd)
        size_bytes = int(UPLOAD_SIZE_MB * 1024 * 1024)
        with open(tmp_path, "wb") as f:
            f.write(os.urandom(size_bytes))

        start = time.time()
        result = subprocess.run(
            ["curl", "-s", "-o", "/dev/null",
             "-w", "%{size_upload}",
             "-X", "POST",
             "--data-binary", "@" + tmp_path,
             "--max-time", str(UPLOAD_TIMEOUT),
             "-H", "Content-Type: application/octet-stream",
             UPLOAD_URL],
            capture_output=True, text=True,
            timeout=UPLOAD_TIMEOUT + 5
        )
        elapsed = time.time() - start
        size = int(result.stdout.strip() or 0)
        if size > 0 and elapsed > 0:
            mbps = round((size * 8) / (elapsed * 1_000_000), 2)
            return mbps, size
        return None, 0
    except Exception:
        return None, 0
    finally:
        try:
            os.remove(tmp_path)
        except Exception:
            pass


def download_speed_mbps():
    mbps, _ = _try_download()
    return mbps


def upload_speed_mbps():
    mbps, _ = _try_upload()
    return mbps
