#!/usr/bin/env python3
"""A single session = one live connection from one victim."""
import socket
import select
import threading
import time


class Session:
    _next_id = 1

    def __init__(self, conn, addr, port):
        self.id = Session._next_id
        Session._next_id += 1

        self.conn = conn
        self.addr = addr
        self.port = port          # the listener port this came in on
        self.alive = True
        self.created = time.time()
        self.last_seen = time.time()
        self._recv_buf = b""
        self._lock = threading.Lock()

    # ---------- low-level ----------
    def _drain(self, timeout=0.2):
        """Pull any currently-available bytes."""
        out = b""
        self.conn.setblocking(False)
        try:
            while True:
                try:
                    chunk = self.conn.recv(4096)
                    if not chunk:
                        self.alive = False
                        break
                    out += chunk
                except BlockingIOError:
                    break
        finally:
            self.conn.setblocking(True)
        if out:
            self.last_seen = time.time()
        return out

    # ---------- public API ----------
    def send(self, cmd: str):
        with self._lock:
            self.conn.sendall((cmd + "\n").encode())

    def read_response(self, wait=1.5):
        """Read whatever the victim sends back, with a timeout."""
        if not self.alive:
            return b""
        # wait for the first byte
        r, _, _ = select.select([self.conn], [], [], wait)
        if not r:
            return b""
        data = self._drain()
        self._recv_buf += data
        out, self._recv_buf = self._recv_buf, b""
        return out

    def close(self):
        with self._lock:
            self.alive = False
            try:
                self.conn.close()
            except Exception:
                pass

    # ---------- display ----------
    def info(self):
        return {
            "id": self.id,
            "addr": f"{self.addr[0]}:{self.addr[1]}",
            "port": self.port,
            "alive": "yes" if self.alive else "no",
            "age": int(time.time() - self.created),
        }

    def __repr__(self):
        return f"<Session {self.id} {self.addr[0]}:{self.addr[1]} port={self.port}>"
