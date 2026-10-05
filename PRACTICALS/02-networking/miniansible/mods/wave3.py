"""
Wave 3 modules: template, blockinfile, hostname, setup, pkg, mount, at
"""

EXTRA_NAMES = {
    # none needed — function names match module names
}


# ---------- template ----------
def mod_template(host, params):
    """
    template: <local_file> -> <remote_path>
    Replaces {{var}} tokens using vars you supply via KEY=VAL prefixes.
    Format:  template: <local> -> <remote> with KEY=VAL KEY2=VAL2
    """
    spec = params["template"]
    with_part = None
    if " with " in spec:
        spec, with_part = spec.split(" with ", 1)

    if "->" not in spec:
        return False, False, "template needs: <local> -> <remote> [with KEY=VAL ...]"
    local, remote = [x.strip() for x in spec.split("->", 1)]

    if not os.path.exists(local):
        return False, False, f"local template not found: {local}"

    # parse vars
    vars_map = {}
    if with_part:
        for token in with_part.split():
            if "=" in token:
                k, v = token.split("=", 1)
                vars_map[k] = v

    # read template
    with open(local) as f:
        content = f.read()

    # substitute {{var}} tokens
    import re
    def repl(m):
        key = m.group(1).strip()
        return vars_map.get(key, m.group(0))
    rendered = re.sub(r"\{\{\s*([^}]+?)\s*\}\}", repl, content)

    # compare remote
    b64_new = base64.b64encode(rendered.encode()).decode()
    check_cmd = (
        f'NEW=$(echo {b64_new} | base64 -d); '
        + _expand_remote_var(remote) +
        'if [ -f "$F" ]; then '
        '  OLD=$(cat "$F"); '
        '  [ "$OLD" = "$NEW" ] && echo SAME || echo DIFF; '
        'else echo MISSING; fi'
    )
    ok, out = ssh_run(host, check_cmd)
    if not ok:
        return False, False, f"check failed: {out}"
    state = out.strip().splitlines()[-1] if out.strip() else ""

    if state == "SAME":
        return False, True, f"{remote} already up to date"

    # push rendered content
    write_cmd = (
        f'NEW=$(echo {b64_new} | base64 -d); '
        + _expand_remote_var(remote) +
        'printf "%s" "$NEW" > "$F" && echo WROTE'
    )
    ok, out = ssh_run(host, write_cmd)
    if not ok:
        return False, False, f"write failed: {out}"
    return True, True, f"rendered {local} -> {remote}"


# ---------- blockinfile ----------
def mod_blockinfile(host, params):
    """
    blockinfile: <file> block=<text> marker=<name>
    Inserts/updates a block of text between BEGIN/END markers.
    The 'block=' value uses \\n for newlines (single line in tasks.txt).
    Idempotent: replaces existing block if different.
    """
    spec = params["blockinfile"]
    if " in " in spec:
        # allow 'blockinfile: <file> in <file2> ...' — we standardize on:
        # blockinfile: <file> block=... marker=...
        pass
    tokens = spec.split()
    if not tokens:
        return False, False, "blockinfile needs: <file> block=... marker=..."

    file_path = tokens[0]
    block_text = None
    marker = "MINI-ANSIBLE"
    for t in tokens[1:]:
        if t.startswith("block="):
            block_text = t.split("=", 1)[1].replace("\\n", "\n")
        elif t.startswith("marker="):
            marker = t.split("=", 1)[1]

    if block_text is None:
        return False, False, "blockinfile needs block=..."

    begin = f"# BEGIN {marker}"
    end = f"# END {marker}"

    # send block via base64
    b64_block = base64.b64encode(block_text.encode()).decode()
    b64_begin = base64.b64encode(begin.encode()).decode()
    b64_end   = base64.b64encode(end.encode()).decode()

    # check current file for the block
    check_cmd = (
        f'B=$(echo {b64_begin} | base64 -d); '
        f'E=$(echo {b64_end} | base64 -d); '
        + _expand_remote_var(file_path) +
        '[ ! -f "$F" ] && echo MISSING && exit 0; '
        'grep -F -q "$B" "$F" || { echo MISSING; exit 0; }; '
        # extract block between markers and compare
        f'BLK=$(echo {b64_block} | base64 -d); '
        'CUR=$(awk -v b="$B" -v e="$E" \'$0==b{f=1;next} $0==e{f=0} f\' "$F"); '
        '[ "$CUR" = "$BLK" ] && echo SAME || echo DIFF'
    )
    ok, out = ssh_run(host, check_cmd)
    if not ok:
        return False, False, f"check failed: {out}"
    state = out.strip().splitlines()[-1]

    if state == "SAME":
        return False, True, f"block already up to date in {file_path}"

    # write: strip existing block, then append new block
    b64_file = base64.b64encode(file_path.encode()).decode()
    write_cmd = (
        f'F=$(echo {b64_file} | base64 -d); F="${{F/#\\~/$HOME}}"; '
        f'B=$(echo {b64_begin} | base64 -d); '
        f'E=$(echo {b64_end} | base64 -d); '
        f'BLK=$(echo {b64_block} | base64 -d); '
        'TMP=$(mktemp); '
        # remove any existing block
        'awk -v b="$B" -v e="$E" \'$0==b{f=1;next} $0==e{f=0;next} !f\' "$F" 2>/dev/null > "$TMP" || true; '
        'printf "%s\\n" "$B" >> "$TMP"; '
        'printf "%s\\n" "$BLK" >> "$TMP"; '
        'printf "%s\\n" "$E" >> "$TMP"; '
        'mv "$TMP" "$F" && echo WROTE'
    )
    ok, out = ssh_run(host, write_cmd)
    if not ok:
        return False, False, f"write failed: {out}"
    return True, True, f"inserted block in {file_path}"


# ---------- hostname ----------
def mod_hostname(host, params):
    """
    hostname:                 → just report it (read-only, always ok)
    hostname: set <new-name>  → attempt to set (will fail on Termux without root)
    """
    spec = params["hostname"].strip()
    if spec.startswith("set "):
        new_name = spec[4:].strip()
        cmd = f'hostname "{new_name}" 2>&1 && echo SET'
        ok, out = ssh_run(host, cmd)
        if not ok or "SET" not in out:
            return False, False, f"set hostname failed: {out.strip()}"
        return True, True, f"hostname set to {new_name}"
    # read
    ok, out = ssh_run(host, 'hostname')
    if not ok:
        return False, False, f"hostname failed: {out}"
    return False, True, out.strip()


# ---------- setup ----------
def mod_setup(host, params):
    """Read-only facts. Always ok, never changed."""
    facts_cmd = (
        'echo "hostname: $(hostname)"; '
        'echo "kernel:   $(uname -r)"; '
        'echo "arch:     $(uname -m)"; '
        'echo "user:     $(whoami)"; '
        'echo "home:     $HOME"; '
        'echo "uptime:   $(uptime 2>/dev/null | sed \'s/^ *//\')"'
    )
    ok, out = ssh_run(host, facts_cmd)
    if not ok:
        return False, False, f"setup failed: {out}"
    return False, True, out.strip()


# ---------- pkg (Termux) ----------
def mod_pkg(host, params):
    """
    pkg: <name> [state=present|absent|check]
    On Termux: uses `pkg install` / `pkg uninstall`.
    state=check → only reports whether the package is installed.
    """
    spec = params["pkg"]
    parts = spec.split()
    if not parts:
        return False, False, "pkg needs: <name> [state=present|absent|check]"
    name = parts[0]
    state = "present"
    for p in parts[1:]:
        if p.startswith("state="):
            state = p.split("=", 1)[1]

    # check if installed: dpkg on termux, fallback to command -v
    ok, out = ssh_run(
        host,
        f'dpkg -s "{name}" >/dev/null 2>&1 && echo YES || '
        f'(command -v "{name}" >/dev/null 2>&1 && echo YES || echo NO)'
    )
    installed = "YES" in out

    if state == "check":
        return False, True, f"{name} {'installed' if installed else 'not installed'}"

    if state == "present":
        if installed:
            return False, True, f"{name} already installed"
        ok, out = ssh_run(host, f'pkg install -y "{name}" 2>&1 | tail -2')
        if not ok:
            return False, False, f"pkg install failed: {out.strip()}"
        return True, True, f"installed {name}"

    if state == "absent":
        if not installed:
            return False, True, f"{name} already absent"
        ok, out = ssh_run(host, f'pkg uninstall -y "{name}" 2>&1 | tail -2')
        if not ok:
            return False, False, f"pkg uninstall failed: {out.strip()}"
        return True, True, f"uninstalled {name}"

    return False, False, "state must be present|absent|check"


# ---------- mount ----------
def mod_mount(host, params):
    """
    mount:               → list current mounts (read-only, always ok)
    mount: <dev> <path>  → attempt to mount (will fail without root)
    """
    spec = params["mount"].strip()
    if not spec:
        ok, out = ssh_run(host, 'mount 2>/dev/null | head -10')
        if not ok:
            return False, False, f"mount list failed: {out}"
        return False, True, out.strip()
    parts = spec.split()
    if len(parts) < 2:
        return False, False, "mount needs: <device> <path>"
    dev, path = parts[0], parts[1]
    cmd = f'mount "{dev}" "{path}" 2>&1 && echo MOUNTED'
    ok, out = ssh_run(host, cmd)
    if not ok or "MOUNTED" not in out:
        return False, False, f"mount failed: {out.strip()}"
    return True, True, f"mounted {dev} at {path}"


# ---------- at ----------
def mod_at(host, params):
    """
    at: <time> command=<cmd>   → schedule a one-time job
    Will fail on Termux if `at` isn't installed — reports honestly.
    """
    spec = params["at"]
    if "command=" not in spec:
        return False, False, "at needs: <time> command=<cmd>"
    time_part, cmd_part = spec.split("command=", 1)
    time_part = time_part.strip()
    cmd_part = cmd_part.strip()

    ok_at, _ = ssh_run(host, 'command -v at >/dev/null 2>&1 && echo yes || echo no')
    if "yes" not in ok_at:
        return False, False, "at is not installed on target"

    # Check existing at jobs for a marker
    marker = f"# mini-ansible-at: {cmd_part[:30]}"
    ok, out = ssh_run(host, f'atq 2>/dev/null | grep -F "{marker}" && echo FOUND || echo MISSING')
    if "FOUND" in out:
        return False, True, f"at job already scheduled"

    full = f'{cmd_part} {marker}'
    b64 = base64.b64encode(full.encode()).decode()
    cmd = f'echo "$(echo {b64} | base64 -d)" | at {time_part} 2>&1'
    ok, out = ssh_run(host, cmd)
    if not ok:
        return False, False, f"at failed: {out.strip()}"
    return True, True, f"scheduled at {time_part}: {cmd_part}"
