#!/usr/bin/env python3
# ============================================
# mini_proxy.py — A simple HTTP proxy
# ============================================

import socket
import threading
import sys

PROXY_HOST = "0.0.0.0"
PROXY_PORT = 8888
BUFFER_SIZE = 4096

def handle_client(client_socket, client_addr):
    """Handle one client connection."""
    try:
        # Read the HTTP request
        request = client_socket.recv(BUFFER_SIZE)
        if not request:
            return

        # Parse the first line (e.g., "GET http://example.com/ HTTP/1.1")
        first_line = request.split(b"\n")[0].decode("utf-8", errors="ignore")
        print(f"[{client_addr[0]}] {first_line}")

        # Extract host and port
        parts = first_line.split()
        if len(parts) < 2:
            client_socket.close()
            return

        url = parts[1]

        # Handle http:// URLs
        if url.startswith("http://"):
            url = url[7:]  # remove "http://"
            host = url.split("/")[0]

            if ":" in host:
                host, port = host.split(":")
                port = int(port)
            else:
                port = 80

            # Connect to real server
            server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            server_socket.connect((host, port))

            # Rewrite request — remove full URL, use path only
            path = "/" + "/".join(url.split("/")[1:])
            rest = b"\n".join(request.split(b"\n")[1:])
            new_request = f"{parts[0]} {path} {parts[2]}".encode() + b"\n" + rest
            server_socket.send(new_request)

            # Forward response back
            while True:
                response = server_socket.recv(BUFFER_SIZE)
                if not response:
                    break
                client_socket.send(response)

            server_socket.close()

    except Exception as e:
        print(f"[ERROR] {e}")
    finally:
        client_socket.close()

def main():
    print(f"🔁 Mini Proxy running on {PROXY_HOST}:{PROXY_PORT}")
    print(f"   Configure your browser to use this as HTTP proxy")
    print(f"   Press Ctrl+C to stop\n")

    server = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    server.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
    server.bind((PROXY_HOST, PROXY_PORT))
    server.listen(10)

    try:
        while True:
            client_socket, client_addr = server.accept()
            print(f"[+] Connection from {client_addr[0]}:{client_addr[1]}")
            t = threading.Thread(target=handle_client, args=(client_socket, client_addr))
            t.daemon = True
            t.start()
    except KeyboardInterrupt:
        print("\n🛑 Stopping proxy.")
        server.close()

if __name__ == "__main__":
    main()
