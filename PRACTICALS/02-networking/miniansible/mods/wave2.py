"""Wave 2 modules."""


def mod_user(host, params):
    spec = params["user"]
    parts = spec.split()
    if not parts:
        return False, False, "user needs: <name> [state=present|absent]"
    name = parts[0]
    state = "present"
    for p in parts[1:]:
        if p.startswith("state="):
            state = p.split("=", 1)[1]
    ok, out = ssh_run(host, f'id -u "{name}" 2>/dev/null && echo FOUND || echo MISSING')
    exists = "FOUND" in out
    if state == "present":
        if exists:
            return False, True, f"user {name} already exists"
        ok, out = ssh_run(host, f'useradd -m "{name}" 2>&1 && echo ADDED')
        if not ok or "ADDED" not in out:
            return False, False, f"useradd failed: {out.strip()}"
        return True, True, f"created user {name}"
    if state == "absent":
        if not exists:
            return False, True, f"user {name} already absent"
        ok, out = ssh_run(host, f'userdel -r "{name}" 2>&1 && echo REMOVED')
        if not ok or "REMOVED" not in out:
            return False, False, f"userdel failed: {out.strip()}"
        return True, True, f"removed user {name}"
    return False, False, f"unknown state: {state}"


def mod_group(host, params):
    spec = params["group"]
    parts = spec.split()
    if not parts:
        return False, False, "group needs: <name> [state=present|absent]"
    name = parts[0]
    state = "present"
    for p in parts[1:]:
        if p.startswith("state="):
            state = p.split("=", 1)[1]
    ok, out = ssh_run(host, f'getent group "{name}" >/dev/null 2>&1 && echo FOUND || echo MISSING')
    exists = "FOUND" in out
    if state == "present":
        if exists:
            return False, True, f"group {name} already exists"
        ok, out = ssh_run(host, f'groupadd "{name}" 2>&1 && echo ADDED')
        if not ok or "ADDED" not in out:
            return False, False, f"groupadd failed: {out.strip()}"
        return True, True, f"created group {name}"
    if state == "absent":
        if not exists:
            return False, True, f"group {name} already absent"
        ok, out = ssh_run(host, f'groupdel "{name}" 2>&1 && echo REMOVED')
        if not ok or "REMOVED" not in out:
            return False, False, f"groupdel failed: {out.strip()}"
        return True, True, f"removed group {name}"
    return False, False, f"unknown state: {state}"


def mod_service(host, params):
    spec = params["service"]
    parts = spec.split()
    if len(parts) < 2:
        return False, False, "service needs: <name> state=<...>"
    name = parts[0]
    state = None
    for p in parts[1:]:
        if p.startswith("state="):
            state = p.split("=", 1)[1]
    if state not in ("started", "stopped", "restarted"):
        return False, False, "state must be started|stopped|restarted"
    ok_sv, _ = ssh_run(host, 'command -v sv >/dev/null 2>&1 && echo yes || echo no')
    ok_sc, _ = ssh_run(host, 'command -v systemctl >/dev/null 2>&1 && echo yes || echo no')
    has_sv = "yes" in ok_sv
    has_sc = "yes" in ok_sc
    if not has_sv and not has_sc:
        return False, False, "no service manager found (no sv, no systemctl)"
    if has_sc:
        cmd = f'systemctl {state} "{name}" 2>&1'
    else:
        action = {"started": "up", "stopped": "down", "restarted": "restart"}[state]
        cmd = f'sv {action} "{name}" 2>&1'
    ok, out = ssh_run(host, cmd)
    if not ok:
        return False, False, f"service {state} failed: {out.strip()}"
    return True, True, f"{name} {state}"


def mod_cron(host, params):
    spec = params["cron"]
    name = schedule = command = None
    state = "present"
    for token in spec.split():
        if "=" in token:
            k, v = token.split("=", 1)
            if k == "name": name = v
            elif k == "schedule": schedule = v
            elif k == "command": command = v
            elif k == "state": state = v
    if not name:
        return False, False, "cron needs: name=<name> schedule=... command=..."
    marker = f"# mini-ansible: {name}"
    ok, out = ssh_run(host, f'crontab -l 2>/dev/null | grep -F "{marker}" && echo FOUND || echo MISSING')
    exists = "FOUND" in out
    if state == "absent":
        if not exists:
            return False, True, f"cron {name} already absent"
        cmd = (f'crontab -l 2>/dev/null | grep -v -F "{marker}" | '
               f'crontab -')
        ok, out = ssh_run(host, cmd)
        if not ok:
            return False, False, f"crontab remove failed: {out.strip()}"
        return True, True, f"removed cron {name}"
    if exists:
        return False, True, f"cron {name} already present"
    if not schedule or not command:
        return False, False, "cron needs: schedule=... command=..."
    line = f"{schedule} {command} {marker}"
    b64 = base64.b64encode(line.encode()).decode()
    add_cmd = (f'L=$(echo {b64} | base64 -d); '
               f'(crontab -l 2>/dev/null; echo "$L") | crontab -')
    ok, out = ssh_run(host, add_cmd)
    if not ok:
        return False, False, f"crontab add failed: {out.strip()}"
    return True, True, f"added cron {name}"


def mod_git(host, params):
    spec = params["git"]
    if "->" not in spec:
        return False, False, "git needs: <url> -> <dest>"
    url, dest = [x.strip() for x in spec.split("->", 1)]
    ok, out = ssh_run(host, _expand_remote_var(dest) + '[ -d "$F/.git" ] && echo REPO || echo MISSING')
    if out.strip() == "REPO":
        cmd = _expand_remote_var(dest) + 'cd "$F" && git pull --ff-only 2>&1 | tail -1'
        ok, out = ssh_run(host, cmd)
        if not ok:
            return False, False, f"git pull failed: {out.strip()}"
        return True, True, f"pulled {dest}: {out.strip()}"
    ok_g, _ = ssh_run(host, 'command -v git >/dev/null 2>&1 && echo yes')
    if "yes" not in ok_g:
        return False, False, "git not installed on target"
    cmd = _expand_remote_var(dest) + f'git clone "{url}" "$F" 2>&1 | tail -1'
    ok, out = ssh_run(host, cmd)
    if not ok:
        return False, False, f"git clone failed: {out.strip()}"
    return True, True, f"cloned {url} -> {dest}"


def mod_pip(host, params):
    spec = params["pip"]
    parts = spec.split()
    name = parts[0]
    state = "present"
    for p in parts[1:]:
        if p.startswith("state="):
            state = p.split("=", 1)[1]
    pkgname = name.split("==")[0]
    ok, out = ssh_run(host, f'python3 -c "import {pkgname}" 2>/dev/null && echo INSTALLED || echo MISSING')
    installed = "INSTALLED" in out
    if state == "present":
        if installed:
            return False, True, f"{name} already installed"
        ok, out = ssh_run(host, f'pip install "{name}" 2>&1 | tail -1')
        if not ok:
            return False, False, f"pip install failed: {out.strip()}"
        return True, True, f"installed {name}"
    if state == "absent":
        if not installed:
            return False, True, f"{name} already absent"
        ok, out = ssh_run(host, f'pip uninstall -y "{name}" 2>&1 | tail -1')
        if not ok:
            return False, False, f"pip uninstall failed: {out.strip()}"
        return True, True, f"uninstalled {name}"
    return False, False, "state must be present|absent"


def mod_archive(host, params):
    spec = params["archive"]
    if "->" not in spec:
        return False, False, "archive needs: <src> -> <dest.tar.gz>"
    src, dest = [x.strip() for x in spec.split("->", 1)]
    ok, out = ssh_run(host, _expand_remote_var(dest) + '[ -f "$F" ] && echo EXISTS || echo MISSING')
    if out.strip() == "EXISTS":
        return False, True, f"{dest} already exists"
    src_dir = os.path.dirname(src) or "."
    src_base = os.path.basename(src)
    cmd = (_expand_remote_var(dest) +
           f'tar czf "$F" -C "{src_dir}" "{src_base}" 2>&1 && echo OK')
    ok, out = ssh_run(host, cmd)
    if not ok or "OK" not in out:
        return False, False, f"tar failed: {out.strip()}"
    return True, True, f"archived {src} -> {dest}"


def mod_unarchive(host, params):
    spec = params["unarchive"]
    if "->" not in spec:
        return False, False, "unarchive needs: <src.tar.gz> -> <dest_dir>"
    src, dest = [x.strip() for x in spec.split("->", 1)]
    ok, out = ssh_run(host, _expand_remote_var(dest) + '[ -d "$F" ] && echo EXISTS || echo MISSING')
    if out.strip() == "EXISTS":
        return False, True, f"{dest} already extracted"
    cmd = (_expand_remote_var(dest) +
           f'mkdir -p "$F" && tar xzf "{src}" -C "$F" 2>&1 && echo OK')
    ok, out = ssh_run(host, cmd)
    if not ok or "OK" not in out:
        return False, False, f"untar failed: {out.strip()}"
    return True, True, f"extracted {src} -> {dest}"


def mod_replace(host, params):
    spec = params["replace"]
    tokens = spec.split()
    if not tokens:
        return False, False, "replace needs: <file> pattern=... replacement=..."
    file_path = tokens[0]
    pattern = replacement = None
    for t in tokens[1:]:
        if t.startswith("pattern="):
            pattern = t.split("=", 1)[1]
        elif t.startswith("replacement="):
            replacement = t.split("=", 1)[1]
    if pattern is None or replacement is None:
        return False, False, "replace needs pattern= and replacement="
    b64_pat = base64.b64encode(pattern.encode()).decode()
    b64_rep = base64.b64encode(replacement.encode()).decode()
    check_cmd = (f'P=$(echo {b64_pat} | base64 -d); ' +
                 _expand_remote_var(file_path) +
                 'grep -E -q "$P" "$F" && echo MATCH || echo NOMATCH')
    ok, out = ssh_run(host, check_cmd)
    if out.strip() == "NOMATCH":
        return False, True, f"pattern not found in {file_path}"
    sed_cmd = (f'P=$(echo {b64_pat} | base64 -d); R=$(echo {b64_rep} | base64 -d); ' +
               _expand_remote_var(file_path) +
               'sed -i "s|$P|$R|g" "$F" && echo REPLACED')
    ok, out = ssh_run(host, sed_cmd)
    if not ok:
        return False, False, f"sed failed: {out.strip()}"
    return True, True, f"replaced pattern in {file_path}"


def mod_script(host, params):
    local_script = params["script"]
    if not os.path.exists(local_script):
        return False, False, f"local script not found: {local_script}"
    remote_tmp = f"/tmp/mini-ansible-script-{int(time.time())}-{os.path.basename(local_script)}"
    ok, err = scp_to(host, local_script, remote_tmp)
    if not ok:
        return False, False, f"scp failed: {err}"
    run_cmd = f'chmod +x "{remote_tmp}" && "{remote_tmp}"; rc=$?; rm -f "{remote_tmp}"; exit $rc'
    ok, out = ssh_run(host, run_cmd)
    lines = out.splitlines()
    return True, ok, _fmt_multiline(lines[0] if lines else "",
                                    "\n".join(lines[1:]))
