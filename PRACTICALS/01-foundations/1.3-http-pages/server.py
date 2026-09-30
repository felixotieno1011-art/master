from http.server import BaseHTTPRequestHandler, HTTPServer

class MyServer(BaseHTTPRequestHandler):
    def do_GET(self):
        self.send_response(200)
        self.send_header("Content-type", "text/html")
        self.end_headers()

        if self.path == "/":
            self.wfile.write(b"<h1>Home Page</h1>")
            self.wfile.write(b"<p>Welcome to Felix's mini website.</p>")
            self.wfile.write(b"<a href='/about'>Go to About</a><br>")
            self.wfile.write(b"<a href='/contact'>Go to Contact</a>")
        elif self.path == "/about":
            self.wfile.write(b"<h1>About Page</h1>")
            self.wfile.write(b"<p>I am learning networking and fullstack.</p>")
            self.wfile.write(b"<a href='/'>Back Home</a>")
        elif self.path == "/contact":
            self.wfile.write(b"<h1>Contact Page</h1>")
            self.wfile.write(b"<p>Reach me on GitHub: felixotieno1011-art</p>")
            self.wfile.write(b"<a href='/'>Back Home</a>")
        else:
            self.send_response(404)
            self.wfile.write(b"<h1>404 - Page Not Found</h1>")
            self.wfile.write(b"<a href='/'>Back Home</a>")

print("Server running at http://localhost:8000")
HTTPServer(("", 8000), MyServer).serve_forever()
