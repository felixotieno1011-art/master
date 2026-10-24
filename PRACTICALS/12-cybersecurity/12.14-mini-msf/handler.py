#!/usr/bin/env python3
"""Multi-session handler. Listens on N ports, spawns a Session per connection."""
import socket
import threading
import sys
import time

from session import Session


class Handler:
    def __init__(self, ports):
        self.ports = ports
        self.sessions = {}          # id -> Session
        self._lock = threading.Lock()
        self._listener_threads = []
        self._stop = threading.Event()

    # ---------- lifecycle ----------
    def start(self):
        for p in self.ports:
            t = threading.Thread(target=self._listen_on, args=(p,), daemon=True)
            t.start()
            self._listener_threads.append(t)
        # give listeners a moment to bind
        time.sleep(0.3)

    def stop(self):
        self._stop.set()
        with self._lock:
            for s in list(self.sessions.values()):
                s.close()
            self.sessions.clear()

    # ---------- per-port listener loop ----------
    def _listen_on(self, port):
        srv = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        srv.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
        try:
            srv.bind(("0.0.0.0", port))
            srv.listen(5)
        except OSError as e:
            print(f"[!] Cannot bind port {port}: {e}", flush=True)
            return

        print(f"[*] Handler listening on 0.0.0.0:{port}", flush=True)
        srv.settimeout(1.0)

        while not self._stop.is_set():
            try:
                conn, addr = srv.accept()
            except socket.timeout:
                continue
            except OSError:
                break

            sess = Session(conn, addr, port)
            with self._lock:
                self.sessions[sess.id] = sess
            print(
                f"\n[+] Session {sess.id} opened: {addr[0]}:{addr[1]} "
                f"(port {port})",
                flush=True,
            )

        srv.close()

    # ---------- session management API ----------
    def list_sessions(self):
        with self._lock:
            return list(self.sessions.values())

    def get(self, sid):
        with self._lock:
            return self.sessions.get(sid)

    def kill(self, sid):
        with self._lock:
            s = self.sessions.pop(sid, None)
        if s:
            s.close()
            return True
        return False

    def reap(self):
        """Remove dead sessions."""
        with self._lock:
            dead = [s for s in self.sessions.values() if not s.alive]
            for s in dead:
                self.sessions.pop(s.id, None)
        return dead
