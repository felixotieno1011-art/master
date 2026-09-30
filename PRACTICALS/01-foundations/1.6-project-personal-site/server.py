from http.server import BaseHTTPRequestHandler, HTTPServer

class MySite(BaseHTTPRequestHandler):
    def do_GET(self):
        self.send_response(200)
        self.send_header("Content-type", "text/html")
        self.end_headers()

        if self.path == "/":
            self.wfile.write(b"<h1>Karibu! I am Felix</h1>")
            self.wfile.write(b"<p>I am learning networking and fullstack dev.</p>")
            self.wfile.write(b"<p>Currently based in Kenya.</p>")
            self.wfile.write(b"<hr>")
            self.wfile.write(b"<a href='/skills'>My Skills</a> | ")
            self.wfile.write(b"<a href='/contact'>Contact Me</a>")
        elif self.path == "/skills":
            self.wfile.write(b"<h1>My Skills</h1>")
            self.wfile.write(b"<ul>")
            self.wfile.write(b"<li>Linux basics (Termux)</li>")
            self.wfile.write(b"<li>Git & GitHub</li>")
            self.wfile.write(b"<li>Python HTTP servers</li>")
            self.wfile.write(b"<li>Networking fundamentals</li>")
            self.wfile.write(b"</ul>")
            self.wfile.write(b"<a href='/'>Back Home</a>")
        elif self.path == "/contact":
            self.wfile.write(b"<h1>Contact</h1>")
            self.wfile.write(b"<p>GitHub: felixotieno1011-art</p>")
            self.wfile.write(b"<a href='/'>Back Home</a>")
        else:
            self.wfile.write(b"<h1>404 - Hii page haipo</h1>")
            self.wfile.write(b"<a href='/'>Rudi Home</a>")

print("Duka iko open! http://localhost:8000")
HTTPServer(("", 8000), MySite).serve_forever()
