#!/usr/bin/env python3
"""mini-msf — Metasploit-style console with exploit modules (local lab only)."""
import sys
import os
import time
import importlib

from handler import Handler


BANNER = r"""
  __  __ _       __  __ _____ 
 |  \/  (_)_ __ |  \/  / ____|
 | |\/| | | '_ \| |\/| | (___  
 | |  | | | | | | |  | |\___ \ 
 |_|  |_|_|_| |_|_|  |_|_____/ 
       mini-msf v0.2 (local lab only)
"""

HELP = """\
Commands:
  search                     list available modules
  use <module>               select a module (e.g. web_rce)
  show options               show current module's options
  set <OPT> <value>          set an option on the current module
  run | exploit              fire the current module
  back                       deselect module
  sessions -l|-i <id>|-k <id|all>
  handlers                   show listening ports
  help
  exit / quit
"""


def list_modules():
    out = []
    for fname in os.listdir("modules"):
        if fname.endswith(".py") and fname != "__init__.py":
            out.append(fname[:-3])
    return sorted(out)


def load_module(name):
    try:
        mod = importlib.import_module(f"modules.{name}")
        return mod
    except Exception as e:
        print(f"[!] Cannot load module '{name}': {e}")
        return None


def print_sessions(handler):
    sessions = handler.list_sessions()
    if not sessions:
        print("[*] No active sessions.")
        return
    print(f"\n{'ID':<4}{'REMOTE':<24}{'PORT':<8}{'ALIVE':<8}{'AGE(s)':<8}")
    print("-" * 56)
    for s in sessions:
        i = s.info()
        print(f"{i['id']:<4}{i['addr']:<24}{i['port']:<8}{i['alive']:<8}{i['age']:<8}")
    print()


def interact(handler, sid):
    sess = handler.get(sid)
    if not sess or not sess.alive:
        print(f"[!] No live session {sid}.")
        return

    import tty, termios, select
    stdin_fd = sys.stdin.fileno()

    print(f"[*] Interacting with session {sid} ({sess.addr[0]}:{sess.addr[1]}). "
          f"Type 'background' or Ctrl+Z to return.\n")

    def _read_line():
        old = termios.tcgetattr(stdin_fd)
        try:
            tty.setraw(stdin_fd)
            buf = bytearray()
            sys.stderr.write("shell> ")
            sys.stderr.flush()
            while True:
                r, _, _ = select.select([sys.stdin], [], [], 0.5)
                if not r:
                    if not sess.alive:
                        sys.stderr.write("\n[!] Session closed.\n")
                        return None
                    continue
                ch = os.read(stdin_fd, 1)
                if not ch:
                    return None
                if ch in (b"\r", b"\n"):
                    sys.stderr.write("\n"); sys.stderr.flush()
                    return buf.decode(errors="replace")
                if ch == b"\x03":
                    raise KeyboardInterrupt
                if ch == b"\x1a":
                    sys.stderr.write("\n[*] Backgrounding...\n")
                    return "__BACKGROUND__"
                if ch in (b"\x7f", b"\x08"):
                    if buf:
                        buf.pop()
                        sys.stderr.write("\b \b"); sys.stderr.flush()
                    continue
                buf.extend(ch)
                sys.stderr.write(ch.decode(errors="replace")); sys.stderr.flush()
        finally:
            termios.tcsetattr(stdin_fd, termios.TCSADRAIN, old)

    try:
        while True:
            cmd = _read_line()
            if cmd is None:
                break
            if cmd == "__BACKGROUND__":
                return
            if not cmd.strip():
                continue
            if cmd.strip().lower() in ("background", "bg"):
                print("[*] Backgrounding...")
                return
            if cmd.strip().lower() == "exit":
                sess.send("exit")
                time.sleep(0.2)
                handler.kill(sid)
                print(f"[*] Session {sid} closed.")
                return
            sess.send(cmd)
            out = sess.read_response(wait=5.0)
            if out:
                sys.stdout.write(out.decode(errors="replace"))
                if not out.endswith(b"\n"):
                    sys.stdout.write("\n")
                sys.stdout.flush()
            else:
                print("[!] No response.")
    except KeyboardInterrupt:
        print("\n[*] Backgrounding.")


def main():
    print(BANNER)

    ports = [4444, 4445, 4446]
    if len(sys.argv) > 1:
        ports = [int(p) for p in sys.argv[1].split(",")]

    print(f"[*] Starting handlers on ports: {ports}")
    h = Handler(ports)
    h.start()

    current_mod = None
    mod_name = None
    mod_opts = {}

    try:
        while True:
            for dead in h.reap():
                print(f"\n[*] Session {dead.id} died ({dead.addr[0]}:{dead.addr[1]})")

            prompt = f"msf ({mod_name}) > " if mod_name else "msf > "
            try:
                line = input(prompt).strip()
            except EOFError:
                break

            if not line:
                continue
            parts = line.split()
            cmd = parts[0].lower()

            # ---------- exit ----------
            if cmd in ("exit", "quit"):
                break

            # ---------- help ----------
            if cmd == "help":
                print(HELP)

            # ---------- search ----------
            elif cmd == "search":
                mods = list_modules()
                print("\nAvailable modules:")
                for m in mods:
                    print(f"  {m}")
                print()

            # ---------- use ----------
            elif cmd == "use":
                if len(parts) != 2:
                    print("[!] Usage: use <module>")
                    continue
                name = parts[1]
                mod = load_module(name)
                if not mod:
                    continue
                current_mod = mod
                mod_name = name
                mod_opts = {k: v["default"] for k, v in mod.META["options"].items()}
                print(f"[*] Using module: {name}")
                print(f"[*] Description: {mod.META['description']}")

            # ---------- back ----------
            elif cmd == "back":
                current_mod = None
                mod_name = None
                mod_opts = {}
                print("[*] Module deselected.")

            # ---------- show ----------
            elif cmd == "show" and len(parts) == 2 and parts[1] == "options":
                if not current_mod:
                    print("[!] No module selected. Use `use <module>`.")
                    continue
                print(f"\nModule options ({mod_name}):\n")
                print(f"{'NAME':<10}{'REQUIRED':<10}{'CURRENT':<24}DESC")
                print("-" * 70)
                for k, v in current_mod.META["options"].items():
                    print(f"{k:<10}{str(v['required']):<10}{str(mod_opts.get(k, v['default'])):<24}{v['desc']}")
                print()

            # ---------- set ----------
            elif cmd == "set":
                if not current_mod:
                    print("[!] No module selected.")
                    continue
                if len(parts) < 3:
                    print("[!] Usage: set <OPT> <value>")
                    continue
                k = parts[1].upper()
                v = " ".join(parts[2:])
                if k not in current_mod.META["options"]:
                    print(f"[!] Unknown option: {k}")
                    continue
                # cast ints
                if k in ("RPORT", "LPORT"):
                    try:
                        v = int(v)
                    except ValueError:
                        print(f"[!] {k} must be an integer.")
                        continue
                mod_opts[k] = v
                print(f"[*] {k} => {v}")

            # ---------- run / exploit ----------
            elif cmd in ("run", "exploit"):
                if not current_mod:
                    print("[!] No module selected. Use `use <module>`.")
                    continue
                print(f"[*] Running exploit: {mod_name}")
                try:
                    ok, msg = current_mod.exploit(mod_opts)
                except Exception as e:
                    print(f"[!] Exploit error: {e}")
                    continue
                if ok:
                    print(f"[+] {msg}")
                else:
                    print(f"[-] Exploit failed: {msg}")

            # ---------- sessions ----------
            elif cmd == "sessions":
                if len(parts) < 2:
                    print("[!] Usage: sessions -l | -i <id> | -k <id|all>")
                    continue
                flag = parts[1]
                if flag == "-l":
                    print_sessions(h)
                elif flag == "-i" and len(parts) == 3:
                    try:
                        sid = int(parts[2])
                    except ValueError:
                        print("[!] Session ID must be a number.")
                        continue
                    interact(h, sid)
                elif flag == "-k" and len(parts) == 3:
                    if parts[2].lower() == "all":
                        for s in h.list_sessions():
                            h.kill(s.id)
                        print("[*] All sessions killed.")
                    else:
                        try:
                            sid = int(parts[2])
                        except ValueError:
                            print("[!] Session ID must be a number.")
                            continue
                        if h.kill(sid):
                            print(f"[*] Session {sid} killed.")
                        else:
                            print(f"[!] No session {sid}.")
                else:
                    print("[!] Usage: sessions -l | -i <id> | -k <id|all>")

            # ---------- handlers ----------
            elif cmd == "handlers":
                print(f"[*] Listening on: {ports}")

            else:
                print(f"[!] Unknown command: {cmd}. Type 'help'.")
    finally:
        print("[*] Shutting down handlers...")
        h.stop()


if __name__ == "__main__":
    main()
