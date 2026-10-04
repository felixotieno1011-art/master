"""HTTP/HTTPS response time + status codes."""
import time
import urllib.request
import urllib.error


# ---- Sites to test ----
# (label, url)
TEST_SITES = [
    ("Google",     "https://www.google.com"),
    ("Cloudflare", "https://www.cloudflare.com"),
    ("Wikipedia",  "https://www.wikipedia.org"),
]


def http_test(url, timeout=10):
    """
    Fetch url. Return dict:
    {
      'status':   int|None,
      'ms':       float|None,  # total time
      'ttfb_ms':  float|None,  # time to first byte (approx = total for small pages)
      'size':     int|None,    # bytes
      'error':    str|None,
    }
    """
    result = {
        "status":  None,
        "ms":      None,
        "ttfb_ms": None,
        "size":    None,
        "error":   None,
    }

    req = urllib.request.Request(
        url,
        headers={"User-Agent": "NetworkMonitor/4"}
    )

    try:
        start = time.time()
        with urllib.request.urlopen(req, timeout=timeout) as r:
            # First byte arrives here
            ttfb = (time.time() - start) * 1000

            # Read the body
            body = r.read()
            total = (time.time() - start) * 1000

            result["status"]  = r.status
            result["ttfb_ms"] = round(ttfb, 1)
            result["ms"]      = round(total, 1)
            result["size"]    = len(body)
    except urllib.error.HTTPError as e:
        # Server responded with an error (4xx/5xx)
        result["status"] = e.code
        result["error"]  = f"HTTP {e.code} {e.reason}"
    except urllib.error.URLError as e:
        result["error"] = f"URLError: {e.reason}"
    except Exception as e:
        result["error"] = str(e)

    return result


def test_all_sites():
    """
    Return dict: {label: {url, status, ms, ttfb_ms, size, error}}
    """
    results = {}
    for label, url in TEST_SITES:
        r = http_test(url)
        r["url"] = url
        results[label] = r
    return results
