"""
features.py — Wave 4 features.
Variables, loops, when, tags, ignore_errors, register, run_once, become,
check_mode, limit.
"""

import os
import re

VARS_FILE = "vars.txt"


# ---------- Variables ----------
def load_vars(path=None):
    """vars.txt format:  key=value  per line."""
    path = path or VARS_FILE
    result = {}
    if not os.path.exists(path):
        return result
    with open(path) as f:
        for line in f:
            line = line.strip()
            if not line or line.startswith("#"):
                continue
            if "=" in line:
                k, v = line.split("=", 1)
                result[k.strip()] = v.strip()
    return result


def substitute(text, vars_map):
    """Replace {{name}} tokens with vars_map values."""
    if not isinstance(text, str):
        return text

    def repl(m):
        key = m.group(1).strip()
        return str(vars_map.get(key, m.group(0)))

    return re.sub(r"\{\{\s*([^}]+?)\s*\}\}", repl, text)


def substitute_task(task, vars_map):
    """Apply variable substitution to every value in a task dict."""
    out = {}
    for k, v in task.items():
        out[k] = substitute(v, vars_map) if isinstance(v, str) else v
    return out


# ---------- Loops ----------
def expand_loops(task, vars_map):
    """
    If a task has 'loop=item1,item2,...', return a list of tasks —
    one per item, with '{{item}}' replaced.
    """
    loop_spec = task.get("loop")
    if not loop_spec:
        return [task]

    items = [x.strip() for x in loop_spec.split(",") if x.strip()]
    expanded = []
    for i, item in enumerate(items, 1):
        new_task = dict(task)
        new_task.pop("loop", None)
        local_vars = dict(vars_map)
        local_vars["item"] = item
        new_task = substitute_task(new_task, local_vars)
        new_task["name"] = f"{task.get('name', 'task')} [item={item}]"
        new_task["_loop_item"] = item
        expanded.append(new_task)
    return expanded


# ---------- Conditionals ----------
def should_run(task):
    """
    when=...  — small subset.
    Supports:  when=A==B  when=A!=B  when=A
    Strips quotes from both sides so {{var}} substitution works.
    """
    cond = task.get("when")
    if not cond:
        return True

    cond = cond.strip()
    if "!=" in cond:
        a, b = cond.split("!=", 1)
        return _clean(a) != _clean(b)
    if "==" in cond:
        a, b = cond.split("==", 1)
        return _clean(a) == _clean(b)
    return bool(_clean(cond))


def _clean(s):
    s = s.strip()
    if len(s) >= 2 and s[0] in ('"', "'") and s[-1] == s[0]:
        s = s[1:-1]
    return s



def _clean(s):
    s = s.strip()
    if len(s) >= 2 and s[0] in ("\"", "'") and s[-1] == s[0]:
        s = s[1:-1]
    return s


# ---------- Tags ----------
def filter_by_tags(tasks, selected_tags):
    """If selected_tags is empty, keep all. Otherwise keep tagged tasks."""
    if not selected_tags:
        return tasks
    selected = set(selected_tags)
    out = []
    for t in tasks:
        tags = t.get("tags", "")
        task_tags = set(x.strip() for x in tags.split(",") if x.strip())
        if task_tags & selected:
            out.append(t)
        elif not task_tags and "always" in selected:
            out.append(t)
    return out
