#!/usr/bin/env python3
"""
mini_ansible — a small, real, working Ansible clone.
Runs as: ansible-playbook | ansible | ansible-inventory | ansible-doc
"""

import subprocess
import sys
import os
import time
import threading

import modules as modules_pkg
from modules import get_registry

import features
from features import (
    load_vars, substitute_task, expand_loops,
    should_run, filter_by_tags,
)

DEFAULT_INVENTORY = "hosts.txt"
DEFAULT_PLAYBOOK  = "playbook.yml"
SSH_TIMEOUT = 20


class C:
    RESET  = "\033[0m"
    BOLD   = "\033[1m"
    GREEN  = "\033[32m"
    RED    = "\033[31m"
    YELLOW = "\033[33m"
    CYAN   = "\033[36m"
    GRAY   = "\033[90m"


def banner(text, char="*", width=60):
    side = char * max(1, (width - len(text) - 2) // 2)
    print(f"\n{C.BOLD}{C.CYAN}{side} {text} {side}{C.RESET}")


# ============================================================
# CLI parsing
# ============================================================
def parse_cli(argv):
    """Parse real-Ansible-style arguments."""
    opts = {
        "inventory": DEFAULT_INVENTORY,
        "playbook":  None,
        "tags":      [],
        "skip_tags": [],
        "check":     False,
        "limit":     None,
        "module":    None,
        "args":      None,
        "list":      False,
        "pattern":   None,   # for ad-hoc `ansible <pattern>`
        "doc":       None,
        "help":      False,
        "version":   False,
    }
    i = 0
    positional = []
    while i < len(argv):
        a = argv[i]
        if a in ("-i", "--inventory") and i + 1 < len(argv):
            opts["inventory"] = argv[i+1]; i += 2; continue
        if a in ("-l", "--limit") and i + 1 < len(argv):
            opts["limit"] = argv[i+1]; i += 2; continue
        if a == "--tags" and i + 1 < len(argv):
            opts["tags"] = [t.strip() for t in argv[i+1].split(",")]; i += 2; continue
        if a == "--skip-tags" and i + 1 < len(argv):
            opts["skip_tags"] = [t.strip() for t in argv[i+1].split(",")]; i += 2; continue
        if a in ("-C", "--check"):
            opts["check"] = True; i += 1; continue
        if a in ("-m", "--module-name") and i + 1 < len(argv):
            opts["module"] = argv[i+1]; i += 2; continue
        if a in ("-a", "--args") and i + 1 < len(argv):
            opts["args"] = argv[i+1]; i += 2; continue
        if a in ("--list-hosts", "--list"):
            opts["list"] = True; i += 1; continue
        if a in ("-h", "--help"):
            opts["help"] = True; i += 1; continue
        if a in ("-v", "--version"):
            opts["version"] = True; i += 1; continue
        if a.startswith("-"):
            i += 1; continue
        positional.append(a)
        i += 1

    opts["positional"] = positional
    return opts


# ============================================================
# Loaders
# ============================================================
def load_inventory(path):
    if not os.path.exists(path):
        print(f"{C.RED}[ERROR]: Unable to parse {path} as an inventory source{C.RESET}")
        sys.exit(1)
    hosts = []
    with open(path) as f:
        for line in f:
            line = line.strip()
            if not line or line.startswith("#"):
                continue
            if "@" not in line or ":" not in line:
                print(f"{C.YELLOW}[WARNING]: Skipping malformed host: {line}{C.RESET}")
                continue
            user_host, port = line.rsplit(":", 1)
            user, host = user_host.split("@", 1)
            hosts.append({"user": user, "host": host, "port": port, "raw": line})
    return hosts


def load_tasks_file(path, seen=None):
    if seen is None: seen = set()
    if path in seen:
        print(f"{C.RED}[ERROR]: circular include: {path}{C.RESET}"); sys.exit(1)
    seen.add(path)

    if not os.path.exists(path):
        print(f"{C.RED}[ERROR]: playbook not found: {path}{C.RESET}"); sys.exit(1)

    tasks = []
    current = {}
    with open(path) as f:
        for line in f:
            stripped = line.strip()
            if stripped == "--- task ---":
                if current: tasks.append(current)
                current = {}
                continue
            if not stripped or stripped.startswith("#"): continue
            if ":" not in stripped: continue
            key, val = stripped.split(":", 1)
            current[key.strip()] = val.strip()
    if current: tasks.append(current)

    for t in tasks:
        if "name" not in t: t["name"] = "task"

    expanded = []
    for t in tasks:
        if "include" in t:
            expanded.extend(load_tasks_file(t["include"], seen))
        else:
            expanded.append(t)
    return expanded


def resolve_action(task, registry):
    skip = {"name", "when", "tags", "notify", "handler", "retries", "delay",
            "failed_when", "changed_when", "loop", "register", "become",
            "ignore_errors", "run_once", "include", "forks"}
    actions = [k for k in registry if k in task and k not in skip]
    if len(actions) != 1:
        return None, f"needs exactly one module key (found {actions})"
    return actions[0], None


# ============================================================
# Task running
# ============================================================
def run_task_on_host(module, action, host, task, opts, vars_map):
    retries = int(task.get("retries", "1"))
    delay = int(task.get("delay", "0"))
    changed_when = task.get("changed_when", "")

    changed, ok, msg = False, False, "not run"
    for attempt in range(retries):
        if opts["check"]:
            changed, ok, msg = False, True, f"[check mode] would run {action}"
            break
        try:
            changed, ok, msg = module(host, task)
        except Exception as e:
            changed, ok, msg = False, False, f"module crashed: {e}"
        if ok:
            break
        if attempt < retries - 1 and delay > 0:
            time.sleep(delay)

    if changed_when == "always": changed = True
    elif changed_when == "never": changed = False
    return changed, ok, msg


# ============================================================
# ansible-playbook
# ============================================================
def cmd_playbook(opts):
    start = time.time()
    registry = get_registry()
    vars_map = load_vars()

    pb = opts["playbook"]
    if not pb:
        positional = [p for p in opts["positional"] if not p.startswith("-")]
        pb = positional[0] if positional else DEFAULT_PLAYBOOK

    print(f"{C.BOLD}PLAYBOOK:{C.RESET} {pb}")
    if opts["check"]: print(f"{C.YELLOW}NOTE: check mode is ON{C.RESET}")
    if opts["limit"]: print(f"{C.YELLOW}NOTE: limited to: {opts['limit']}{C.RESET}")
    if opts["tags"]: print(f"{C.YELLOW}NOTE: only tags: {','.join(opts['tags'])}{C.RESET}")

    hosts = load_inventory(opts["inventory"])
    if opts["limit"]:
        hosts = [h for h in hosts if opts["limit"] in h["raw"]]
        if not hosts:
            print(f"{C.RED}[ERROR]: --limit matched no hosts{C.RESET}"); sys.exit(1)

    tasks = load_tasks_file(pb)

    # skip_tags
    if opts["skip_tags"]:
        skip = set(opts["skip_tags"])
        tasks = [t for t in tasks
                 if not (set(x.strip() for x in t.get("tags", "").split(",")) & skip)]

    tasks = filter_by_tags(tasks, opts["tags"])

    handlers = {}
    play_tasks = []
    for t in tasks:
        if "handler" in t: handlers[t["handler"]] = t
        else: play_tasks.append(t)

    banner(f"PLAY [mini-ansible]")
    print(f"{C.GRAY}hosts: {', '.join(h['raw'] for h in hosts)}{C.RESET}")
    print(f"{C.GRAY}tasks: {len(play_tasks)}  handlers: {len(handlers)}{C.RESET}")

    stats = {h["raw"]: {"ok": 0, "changed": 0, "unreachable": 0,
                        "failed": 0, "skipped": 0, "rescued": 0, "ignored": 0}
             for h in hosts}

    for raw_task in play_tasks:
        task = substitute_task(raw_task, vars_map)

        for sub_task in expand_loops(task, vars_map):
            if not should_run(sub_task):
                banner(f"TASK [{sub_task['name']}]")
                print(f"{C.GREEN}skipping: [{hosts[0]['raw']}]{C.RESET}")
                for h in hosts: stats[h["raw"]]["skipped"] += 1
                continue

            banner(f"TASK [{sub_task['name']}]")
            action, err = resolve_action(sub_task, registry)
            if not action:
                print(f"{C.RED}[ERROR]: {err}{C.RESET}")
                for h in hosts: stats[h["raw"]]["failed"] += 1
                continue

            module = registry[action]
            is_parallel = sub_task.get("forks", "").lower() in ("yes", "true", "1")
            notify_name = sub_task.get("notify")
            ignore_errors = sub_task.get("ignore_errors", "").lower() in ("yes", "true", "1")

            results = {}
            if is_parallel and len(hosts) > 1:
                threads = []
                def worker(h): results[h["raw"]] = run_task_on_host(module, action, h, sub_task, opts, vars_map)
                for h in hosts:
                    th = threading.Thread(target=worker, args=(h,))
                    th.start(); threads.append(th)
                for th in threads: th.join()
            else:
                for h in hosts:
                    results[h["raw"]] = run_task_on_host(module, action, h, sub_task, opts, vars_map)

            any_changed = False
            for h in hosts:
                changed, ok, msg = results[h["raw"]]
                if changed: any_changed = True
                s = stats[h["raw"]]
                if not ok:
                    if ignore_errors:
                        s["ignored"] += 1
                        label = f"{C.YELLOW}ignored{C.RESET}"
                    else:
                        s["failed"] += 1
                        label = f"{C.RED}fatal  {C.RESET}"
                elif changed:
                    s["changed"] += 1; s["ok"] += 1
                    label = f"{C.YELLOW}changed{C.RESET}"
                else:
                    s["ok"] += 1
                    label = f"{C.GREEN}ok     {C.RESET}"
                first = msg.splitlines()[0] if msg else ""
                print(f"{label}: [{h['raw']}] => {first}")
                for extra in msg.splitlines()[1:]:
                    print(f"    {C.GRAY}{extra}{C.RESET}")
                if "register" in sub_task:
                    vars_map[sub_task["register"]] = msg

            if notify_name and any_changed and notify_name in handlers:
                banner(f"RUNNING HANDLER [{notify_name}]")
                htask = substitute_task(handlers[notify_name], vars_map)
                haction, herr = resolve_action(htask, registry)
                if not haction:
                    print(f"{C.RED}[ERROR]: handler '{notify_name}' {herr}{C.RESET}")
                    continue
                hmodule = registry[haction]
                for h in hosts:
                    changed, ok, msg = run_task_on_host(hmodule, haction, h, htask, opts, vars_map)
                    s = stats[h["raw"]]
                    if not ok:
                        s["failed"] += 1; label = f"{C.RED}fatal  {C.RESET}"
                    elif changed:
                        s["changed"] += 1; s["ok"] += 1
                        label = f"{C.YELLOW}changed{C.RESET}"
                    else:
                        s["ok"] += 1; label = f"{C.GREEN}ok     {C.RESET}"
                    first = msg.splitlines()[0] if msg else ""
                    print(f"{label}: [{h['raw']}] => {first}")

    banner("PLAY RECAP")
    for host_raw, s in stats.items():
        color = C.GREEN if (s["failed"] == 0 and s["unreachable"] == 0) else C.RED
        print(
            f"{color}{host_raw:<30}{C.RESET} : "
            f"ok={C.GREEN}{s['ok']}{C.RESET} "
            f"changed={C.YELLOW}{s['changed']}{C.RESET} "
            f"unreachable={C.RED}{s['unreachable']}{C.RESET} "
            f"failed={C.RED}{s['failed']}{C.RESET} "
            f"skipped={C.GRAY}{s['skipped']}{C.RESET} "
            f"rescued={C.GRAY}{s['rescued']}{C.RESET} "
            f"ignored={C.GRAY}{s['ignored']}{C.RESET}"
        )

    print(f"\n{C.GRAY}playbook run took {time.time() - start:.2f}s{C.RESET}")
    total_failed = sum(s["failed"] + s["unreachable"] for s in stats.values())
    sys.exit(1 if total_failed else 0)


# ============================================================
# ansible (ad-hoc)
# ============================================================
def cmd_adhoc(opts):
    registry = get_registry()
    pattern = opts["positional"][0] if opts["positional"] else "all"
    module_name = opts["module"]
    module_args = opts["args"] or ""

    if not module_name:
        print(f"{C.RED}[ERROR]: -m <module> is required{C.RESET}"); sys.exit(1)

    if module_name not in registry:
        print(f"{C.RED}[ERROR]: module '{module_name}' not found{C.RESET}")
        print(f"{C.GRAY}Available: {', '.join(sorted(registry))}{C.RESET}")
        sys.exit(1)

    hosts = load_inventory(opts["inventory"])
    if pattern != "all":
        hosts = [h for h in hosts if pattern in h["raw"]]

    module = registry[module_name]
    task = {"name": f"ad-hoc {module_name}", module_name: module_args}

    print(f"{C.BOLD}ANSIBLE (ad-hoc){C.RESET}  pattern: {pattern}  module: {module_name}")
    print(f"{C.GRAY}hosts: {', '.join(h['raw'] for h in hosts)}{C.RESET}\n")

    for h in hosts:
        try:
            changed, ok, msg = module(h, task)
        except Exception as e:
            changed, ok, msg = False, False, f"crashed: {e}"
        if not ok:
            label = f"{C.RED}FAILED {C.RESET}"
        elif changed:
            label = f"{C.YELLOW}CHANGED{C.RESET}"
        else:
            label = f"{C.GREEN}SUCCESS{C.RESET}"
        first = msg.splitlines()[0] if msg else ""
        print(f"{h['raw']} | {label} | rc=0 >>")
        print(f"    {first}")
        for extra in msg.splitlines()[1:]:
            print(f"    {C.GRAY}{extra}{C.RESET}")


# ============================================================
# ansible-inventory
# ============================================================
def cmd_inventory(opts):
    hosts = load_inventory(opts["inventory"])
    print(f"{C.BOLD}Inventory:{C.RESET} {opts['inventory']}")
    print(f"{C.GRAY}{len(hosts)} host(s){C.RESET}\n")
    print("[all]")
    for h in hosts:
        print(f"  {h['raw']}")


# ============================================================
# ansible-doc
# ============================================================
def cmd_doc(opts):
    registry = get_registry()
    topic = opts["positional"][0] if opts["positional"] else None

    if not topic:
        print(f"{C.BOLD}Available modules:{C.RESET}")
        for name in sorted(registry):
            print(f"  {name}")
        return

    if topic not in registry:
        print(f"{C.RED}[ERROR]: no module named '{topic}'{C.RESET}")
        print(f"{C.GRAY}Try: ansible-doc (with no args) to list{C.RESET}")
        sys.exit(1)

    fn = registry[topic]
    doc = fn.__doc__ or "(no documentation)"
    print(f"{C.BOLD}MODULE: {topic}{C.RESET}")
    print(f"{C.GRAY}function: {fn.__name__}{C.RESET}\n")
    print(doc.strip())


# ============================================================
# Dispatcher — decides what to run based on invoked name
# ============================================================
def main():
    invoked = os.path.basename(sys.argv[0])
    argv = sys.argv[1:]
    opts = parse_cli(argv)

    if opts["version"]:
        print("mini-ansible 1.0.0 (small, real, no installs)")
        print("built on Termux by a vibe coder")
        return
    if opts["help"]:
        print_help(invoked)
        return

    # Strip leading positional into opts["playbook"] for playbook mode
    if invoked in ("ansible-playbook", "mini_ansible.py"):
        if opts["positional"]:
            opts["playbook"] = opts["positional"][0]
        cmd_playbook(opts)
    elif invoked == "ansible":
        cmd_adhoc(opts)
    elif invoked == "ansible-inventory":
        cmd_inventory(opts)
    elif invoked == "ansible-doc":
        cmd_doc(opts)
    else:
        # default: behave like ansible-playbook
        if opts["positional"]:
            opts["playbook"] = opts["positional"][0]
        cmd_playbook(opts)


def print_help(invoked):
    if invoked == "ansible":
        print("Usage: ansible <pattern> -m <module> [-a <args>] [-i inventory]")
    elif invoked == "ansible-inventory":
        print("Usage: ansible-inventory [-i inventory]")
    elif invoked == "ansible-doc":
        print("Usage: ansible-doc [module]")
    else:
        print("Usage: ansible-playbook <playbook.yml> [-i inventory] [--tags x] [--check] [--limit x]")


if __name__ == "__main__":
    main()
