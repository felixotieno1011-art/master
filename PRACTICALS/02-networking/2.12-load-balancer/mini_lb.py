#!/usr/bin/env python3
# ============================================
# mini_lb.py — Simple HTTP Load Balancer
# Round-robins requests across 3 fake backends
# No external websites needed — works offline
# ============================================

import http.server
import socketserver
import itertools

# ---- Our 3 fake backends ----
BACKENDS = ["backend-A", "backend-B", "backend-C"]
cycle = itertools.cycle(BACKENDS)
PORT = 8080

class LBHandler(http.server.BaseHTTPRequestHandler):
    def do_GET(self):
        # Pick next backend (round-robin)
        backend = next(cycle)

        # Respond with which backend handled it
        self.send_response(200)
        self.send_header("Content-type", "text/html")
        self.send_header("X-Backend", backend)
        self.end_headers()

        html = f"<h1>Request served by: {backend}</h1>"
        self.wfile.write(html.encode())

        # Print to terminal so you see it happening
        print(f"   → {backend}")

    def log_message(self, format, *args):
        # Silence default HTTP logging (we have our own)
        pass

if __name__ == "__main__":
    print(f"🚦 Load Balancer running on port {PORT}")
    print(f"   Backends: {BACKENDS}")
    print(f"   Open another Termux session and run:")
    print(f"   curl -s http://localhost:8080")
    print(f"   Press Ctrl+C to stop\n")

    try:
        with socketserver.TCPServer(("", PORT), LBHandler) as httpd:
            httpd.serve_forever()
    except KeyboardInterrupt:
        print("\n🛑 Load balancer stopped.")
