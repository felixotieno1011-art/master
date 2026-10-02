#!/usr/bin/env python3
# ============================================
# mini_tunnel.py — Demonstrates tunneling
# Wraps HTTP request inside a "tunnel" protocol (base64)
# ============================================

import socket
import base64
import json

TUNNEL_HOST = "0.0.0.0"
TUNNEL_PORT = 9999

def server_side():
    """Receive tunneled message, unwrap, show."""
    server = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    server.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
    server.bind((TUNNEL_HOST, TUNNEL_PORT))
    server.listen(5)

    print(f"🚇 Tunnel server listening on port {TUNNEL_PORT}")
    print(f"   Waiting for a client...\n")

    while True:
        client, addr = server.accept()
        data = client.recv(4096)
        if data:
            print(f"[+] Received {len(data)} bytes from {addr[0]}")
            envelope = json.loads(data.decode())
            inner = base64.b64decode(envelope["payload"]).decode()
            print(f"   Tunnel ID: {envelope['tunnel_id']}")
            print(f"   Wrapped type: {envelope['type']}")
            print(f"   Inner message: {inner}")
            print()
            client.send(b'{"status": "received"}')
        client.close()

def client_side(message):
    """Wrap message in a tunnel envelope, send."""
    envelope = {
        "tunnel_id": "abc123",
        "type": "http_request",
        "payload": base64.b64encode(message.encode()).decode(),
    }

    print(f"📤 Sending tunneled message...")
    print(f"   Inner: {message}")
    print(f"   Wrapped: {json.dumps(envelope)[:80]}...")

    s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    s.connect(("127.0.0.1", TUNNEL_PORT))
    s.send(json.dumps(envelope).encode())
    response = s.recv(1024)
    s.close()
    print(f"   Response: {response.decode()}\n")

if __name__ == "__main__":
    import sys
    if len(sys.argv) < 2:
        print("Usage:")
        print("  Terminal 1: python mini_tunnel.py server")
        print("  Terminal 2: python mini_tunnel.py client 'Hello World'")
        sys.exit(1)

    if sys.argv[1] == "server":
        server_side()
    elif sys.argv[1] == "client":
        msg = sys.argv[2] if len(sys.argv) > 2 else "Hello from inside the tunnel"
        client_side(msg)
