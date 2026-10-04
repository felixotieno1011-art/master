#!/usr/bin/env python3
# ============================================
# mini_lb.py — Simple HTTP Load Balancer
# Simulates 3 backends, round-robins requests
# No internet needed. Works on any network.
# ============================================

import http.server
import socketserver
import itertools

# ---- Fake backends (just names) ----
BACKENDS = ["backend-A", "backend-B", "backend-C"]
cycle = itertools.cycle(BACKENDS)

# ---- Port to listen on ----
PORT = 8080

class LBHandler(http.server.BaseHTTPRequestHandler):
    def do_GET(self):
        # Pick the next backend (round-robin)
        backend = next(cycle)

        # Log it
        print(f"   Proxied request → {backend}")

        # Send the response
        self.send_response(200)
        self.send_header("Content-type", "text/html")
        self.send_header("X-Backend", backend)
        self.end_headers()

        body = f"""
        <html>
        <head><title>Load Balancer</title></head>
        <body style="font-family: sans-serif; padding: 20px;">
            <h1>🚦 Mini Load Balancer</h1>
            <p>Your request was routed to: <b>{backend}</b></p>
            <p>Refresh the page to see round-robin in action!</p>
        </body>
        </html>
        """
        self.wfile.write(body.encode())

    def log_message(self, format, *args):
        # Silence the default logging so our custom logs show cleanly
        pass

# ---- Start the server ----
print(f"🚦 LB listening on port {PORT}")
print(f"   Backends: {BACKENDS}")
print(f"   Test with: curl -I http://localhost:{PORT}")
print(f"   Press Ctrl+C to stop\n")

try:
    with socketserver.TCPServer(("", PORT), LBHandler) as httpd:
        httpd.serve_forever()
except KeyboardInterrupt:
    print("\n🛑 LB stopped.")
