from http.server import BaseHTTPRequestHandler, HTTPServer

class MyServer(BaseHTTPRequestHandler):
    def do_GET(self):
        self.send_response(200)
        self.send_header("Content-type", "text/html")
        self.end_headers()
        self.wfile.write(b"<h1>Karibu! This is Felix's server.</h1>")
        self.wfile.write(b"<p>You are the client. I am the server.</p>")

print("Server running at http://localhost:8000")
HTTPServer(("", 8000), MyServer).serve_forever()
