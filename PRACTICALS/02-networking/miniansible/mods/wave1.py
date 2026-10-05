"""Wave 1 modules. Helpers (ssh_run, etc.) are injected by the loader."""

EXTRA_NAMES = {
    "get_url": "mod_get_url",
}


def mod_shell(host, params):
    ok, out = ssh_run(host, params["shell"])
    lines = out.splitlines()
    return False, ok, _fmt_multiline(lines[0] if lines else "",
                                     "\n".join(lines[1:]))


def mod_copy(host, params):
    spec = params["copy"]
    if "->" not in spec:
        return False, False, "copy needs: <local> -> <remote>"
    local, remote = [x.strip() for x in spec.split("->", 1)]
    if not os.path.exists(local):
        return False, False, f"local file not found: {local}"
    remote_hash_cmd = _expand_remote_var(remote) + 'sha256sum "$F" 2>/dev/null | cut -d" " -f1'
    _, remote_hash = ssh_run(host, remote_hash_cmd)
    remote_hash = remote_hash.strip()
    local_hash = subprocess.run(["sha256sum", local], capture_output=True, text=True).stdout.split()[0]
    if remote_hash == local_hash:
        return False, True, f"already up to date: {remote}"
    _, expanded = ssh_run(host, f'echo {remote} | sed "s|^~|$HOME|"')
    expanded = expanded.strip() or remote
    ok, err = scp_to(host, local, expanded)
    if not ok:
        return False, False, f"scp failed: {err}"
    return True, True, f"copied {local} -> {remote}"


def mod_line(host, params):
    spec = params["line"]
    if " contains " not in spec:
        return False, False, "line needs: <file> contains <text>"
    file_path, line_text = spec.split(" contains ", 1)
    file_path = file_path.strip()
    line_text = line_text.strip()
    b64 = base64.b64encode(line_text.encode()).decode()
    check_cmd = (f'L=$(echo {b64} | base64 -d); ' + _expand_remote_var(file_path) +
                 'grep -F -x -q "$L" "$F" && echo PRESENT || echo MISSING')
    ok, out = ssh_run(host, check_cmd)
    if not ok:
        return False, False, f"check failed: {out}"
    if out.strip() == "PRESENT":
        return False, True, f"already present in {file_path}"
    add_cmd = (f'L=$(echo {b64} | base64 -d); ' + _expand_remote_var(file_path) +
               'printf "%s\\n" "$L" >> "$F" && echo ADDED')
    ok, out2 = ssh_run(host, add_cmd)
    if not ok:
        return False, False, f"append failed: {out2}"
    return True, True, f"added line to {file_path}"


def mod_ping(host, params):
    ok, out = ssh_run(host, 'echo pong')
    if ok and out.strip() == "pong":
        return False, True, "pong"
    return False, False, f"unreachable: {out}"


def mod_debug(host, params):
    return False, True, params["debug"]


def mod_command(host, params):
    ok, out = ssh_run(host, params["command"])
    lines = out.splitlines()
    return False, ok, _fmt_multiline(lines[0] if lines else "",
                                     "\n".join(lines[1:]))


def mod_raw(host, params):
    ok, out = ssh_run(host, params["raw"])
    lines = out.splitlines()
    return False, ok, _fmt_multiline(lines[0] if lines else "",
                                     "\n".join(lines[1:]))


def mod_file(host, params):
    spec = params["file"]
    parts = spec.split()
    if not parts:
        return False, False, "file needs: <path> state=<...>"
    path = parts[0]
    state = "file"
    mode = None
    for p in parts[1:]:
        if p.startswith("state="):
            state = p.split("=", 1)[1]
        elif p.startswith("mode="):
            mode = p.split("=", 1)[1]
    if state not in ("directory", "file", "absent", "touch"):
        return False, False, f"unknown state: {state}"
    check_cmd = _expand_remote_var(path) + \
        'if [ -d "$F" ]; then echo DIR; elif [ -f "$F" ]; then echo FILE; else echo MISSING; fi'
    ok, out = ssh_run(host, check_cmd)
    if not ok:
        return False, False, f"check failed: {out}"
    current = out.strip()
    if state == "absent":
        if current == "MISSING":
            return False, True, f"{path} already absent"
        ok, out = ssh_run(host, _expand_remote_var(path) + 'rm -rf "$F" && echo REMOVED')
        if not ok:
            return False, False, f"remove failed: {out}"
        return True, True, f"removed {path}"
    if state == "directory":
        if current == "DIR":
            return False, True, f"{path} already exists as directory"
        cmd = _expand_remote_var(path) + 'mkdir -p "$F"'
        if mode:
            cmd += f' && chmod {mode} "$F"'
        cmd += ' && echo CREATED'
        ok, out = ssh_run(host, cmd)
        if not ok:
            return False, False, f"mkdir failed: {out}"
        return True, True, f"created directory {path}"
    if state in ("file", "touch"):
        if current == "FILE":
            return False, True, f"{path} already exists"
        cmd = _expand_remote_var(path) + 'touch "$F"'
        if mode:
            cmd += f' && chmod {mode} "$F"'
        cmd += ' && echo CREATED'
        ok, out = ssh_run(host, cmd)
        if not ok:
            return False, False, f"touch failed: {out}"
        return True, True, f"created file {path}"
    return False, False, "unhandled state"


def mod_stat(host, params):
    cmd = _expand_remote_var(params["stat"]) + \
        'if [ -e "$F" ]; then ls -ld "$F"; else echo MISSING; fi'
    ok, out = ssh_run(host, cmd)
    if not ok:
        return False, False, f"stat failed: {out}"
    return False, True, out


def mod_mkdir(host, params):
    path = params["mkdir"]
    ok, out = ssh_run(host, _expand_remote_var(path) + '[ -d "$F" ] && echo DIR || echo MISSING')
    if out.strip() == "DIR":
        return False, True, f"{path} already exists"
    ok, out = ssh_run(host, _expand_remote_var(path) + 'mkdir -p "$F" && echo CREATED')
    if not ok:
        return False, False, f"mkdir failed: {out}"
    return True, True, f"created {path}"


def mod_fetch(host, params):
    spec = params["fetch"]
    if "->" not in spec:
        return False, False, "fetch needs: <remote> -> <local>"
    remote, local = [x.strip() for x in spec.split("->", 1)]
    _, expanded = ssh_run(host, f'echo {remote} | sed "s|^~|$HOME|"')
    expanded = expanded.strip() or remote
    _, out_r = ssh_run(host, f'[ -f "{expanded}" ] && echo YES || echo NO')
    if out_r.strip() != "YES":
        return False, False, f"remote file not found: {remote}"
    if os.path.exists(local):
        r_hash = ssh_run(host, f'sha256sum "{expanded}" | cut -d" " -f1')[1].strip()
        l_hash = subprocess.run(["sha256sum", local], capture_output=True, text=True).stdout.split()[0]
        if r_hash == l_hash:
            return False, True, f"already up to date: {local}"
    ok, err = scp_from(host, expanded, local)
    if not ok:
        return False, False, f"scp failed: {err}"
    return True, True, f"fetched {remote} -> {local}"


def mod_get_url(host, params):
    spec = params["get_url"]
    if "->" not in spec:
        return False, False, "get_url needs: <url> -> <remote_path>"
    url, remote = [x.strip() for x in spec.split("->", 1)]
    ok, out = ssh_run(host, _expand_remote_var(remote) + '[ -f "$F" ] && echo EXISTS || echo MISSING')
    if out.strip() == "EXISTS":
        return False, True, f"{remote} already present"
    dl_cmd = _expand_remote_var(remote) + \
        f'(curl -fsSL "{url}" -o "$F" 2>/dev/null || wget -q "{url}" -O "$F" 2>/dev/null) && echo OK'
    ok, out = ssh_run(host, dl_cmd)
    if not ok or "OK" not in out:
        return False, False, f"download failed: {out}"
    return True, True, f"downloaded {url} -> {remote}"


def mod_env(host, params):
    spec = params["env"]
    if " in " not in spec or "=" not in spec:
        return False, False, "env needs: NAME=value in <file>"
    var_part, file_part = spec.split(" in ", 1)
    var_part = var_part.strip()
    file_part = file_part.strip()
    name = var_part.split("=", 1)[0].strip()
    full_line = f'export {var_part}'
    b64 = base64.b64encode(full_line.encode()).decode()
    check_cmd = (f'L=$(echo {b64} | base64 -d); ' + _expand_remote_var(file_part) +
                 'grep -F -x -q "$L" "$F" && echo PRESENT || echo MISSING')
    ok, out = ssh_run(host, check_cmd)
    if out.strip() == "PRESENT":
        return False, True, f"{name} already set in {file_part}"
    add_cmd = (f'L=$(echo {b64} | base64 -d); ' + _expand_remote_var(file_part) +
               'printf "%s\\n" "$L" >> "$F" && echo ADDED')
    ok, out = ssh_run(host, add_cmd)
    if not ok:
        return False, False, f"append failed: {out}"
    return True, True, f"set {name} in {file_part}"
