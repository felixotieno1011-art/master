## 5.1 How Backend Works — Phase B DONE ✅

Traced the full request flow from browser click to database and back.
Fetched real products from pos-lab's API.

### Core concepts
- Backend = the server-side code that runs behind the scenes
- The backend loop: wait → handle → respond → repeat
- Frontend = what you see (browser)
- Backend = what runs behind the scenes (server)
- The database never talks to the frontend directly
  — always through the backend

### Backend structure
- Startup: load config, connect DB, start server
- Middleware: parse, auth, log, security headers
- Routes: URL → handler mapping
- Handlers: read input, validate, query DB, send response
- Error handling: catch errors, don't leak stack traces

### pos-lab's actual structure
~/pos-lab/
├── server.js          ← startup + routes
├── routes/            ← one file per domain (auth, products, sales...)
├── middleware/        ← auth, csrf, headers, ratelimit
├── lib/               ← env, keys, sessions, audit, orm
├── db/                ← init.js, pos.db
├── public/            ← frontend (HTML/CSS/JS)
└── .env               ← config

### The 5 HTTP methods
GET (read) · POST (create) · PUT (update full) · PATCH (update partial) · DELETE

### The HTTP status codes
200 OK · 201 Created · 400 Bad Request · 401 Unauthorized
403 Forbidden · 404 Not Found · 500 Server Error

### The full request flow (11 steps)
1. User clicks button
2. Frontend JS runs (event listener)
3. fetch() sends HTTP request
4. Backend receives request
5. Middleware runs (headers, rate limit, auth)
6. Route handler runs
7. SQL query to database
8. Database returns rows
9. Backend formats JSON
10. Frontend receives JSON
11. renderProducts() updates DOM

### Real commands I ran
- curl -s http://127.0.0.1:3001/api/products | head -20

### Things I saw
- Response: {"ok":true,"count":5,"products":[...]}
- 5 products returned (Bread, Milk, Soap, Dime, Penny)
- JSON structure: ok, count, products
- No password_hash in the response (handler chose not to ask for it)

### My own words (locked in)
- Backend = loop, waiting for requests, handling them, responding
- Every request = method + URL + headers + body
- Every response = status + headers + body
- Middleware runs BEFORE the handler (step 5)
- SQL happens at the database layer (step 7)
- The handler decides what to query (step 6)
- The database returns what you ask for — not more, not less
- password_hash is filtered at the handler level (by NOT selecting it)
- Never SELECT * on tables with sensitive fields
- Always list the safe columns explicitly
- The backend is the ONLY bridge between frontend and database
- Without backend: static site (no auth, no DB, no data)
- Without frontend: pure API (JSON only, no UI for humans)
- Both = full web app

### Connection to other topics
- 4.1 (HTML) — structure the frontend serves
- 4.4 (JS) — frontend code (fetch, renderProducts)
- 4.5 (DOM) — where the frontend updates the page
- 6.1 (DB) — the data store behind the backend
- 6.2 (SQL) — the language the backend uses to query
- 8.1 (Web security) — every endpoint is a door
- 12.6-12.8 (crypto) — hashes are filtered at the handler
- pos-lab's actual code demonstrates all of this
## 5.2 Python Backend (Flask) — Phase B DONE ✅

Built my first Python backend using Flask.
It reads from a database, accepts POST requests, and saves data.

### Core concepts
- Flask = a micro-framework for Python. Minimal, easy to start.
- `@app.route('/path')` = defines a route (URL → function).
- `request.args` = query string (?name=Felix).
- `request.get_json()` = reads JSON body from POST request.
- `return` = sends the response back to the client.
- `if __name__ == '__main__':` = starts the server (must be at the bottom).

### The two HTTP methods we used
- `GET /messages` = read the database, return JSON.
- `POST /messages` = insert into the database, return success.

### SQLite integration
- `sqlite3.connect('guestbook.db')` = connects to the database file.
- `c.execute("INSERT ... VALUES (?, ?)")` = parameterized query (safe from SQLi).
- `conn.commit()` = saves the changes.
- `c.fetchall()` = reads all rows.

### Real commands I ran
- `pip install flask`
- `python app.py`
- `curl -X POST http://127.0.0.1:5000/messages -H "Content-Type: application/json" -d '{"author":"Felix","content":"Hello"}'`

### Things I saw
- `/` returned "Welcome to the Guestbook API"
- `/messages` GET returned `{"messages": []}` (empty at first)
- POST returned `{"status": "saved!"}`
- GET returned `{"messages": [{"author":"Felix","content":"Hello"}]}`
- After restarting the server, the message was still there (data persisted in `guestbook.db`).
- The file `guestbook.db` is now in the same folder.

### My own words (locked in)
- Flask is a micro-framework. It doesn't force you to use a specific structure.
- `@app.route()` is the link between the URL and the Python function.
- `request.args.get('name')` reads the query string.
- `request.get_json()` reads the JSON body from the client.
- `?name=Felix` is a GET parameter (visible in the URL).
- The `if __name__ == '__main__'` block is essential. Without it, the server doesn't start.
- SQLite stores data in a file (`guestbook.db`), so it survives restarts.
- `INSERT` and `SELECT` are the core of any backend.
- Parameterized queries (`?`) protect against SQL injection (from 8.4).
- This is exactly how pos-lab works, just on a smaller scale.

### Connection to other topics
- 5.1 (Backend loop) — this is the loop in action.
- 6.1 (Databases) — SQLite is the DB.
- 6.2 (SQL basics) — INSERT and SELECT.
- 8.4 (Secure coding) — parameterized queries.
- 8.10 (Secure API) — GET and POST design.
- 12.15 (Web hacking) — SQL injection would break this if we didn't use `?`.

## 5.4 Node.js & Express — Phase B DONE ✅

Built my first Node.js backend using Express.
Ran it on port 5000 and tested with the browser.

### Core concepts
- Node.js = a runtime for JavaScript on the server.
- Express = the most popular Node.js framework (like Flask for Python).
- Node is asynchronous (non-blocking), which makes it fast for I/O.
- `app.get(path, handler)` = defines a route.
- `app.listen(port, callback)` = starts the server.
- `req.query.name` = reads the query string.
- `res.send()` = sends the response.

### Flask vs Express (side-by-side)
| Feature | Flask (Python) | Express (JS) |
|---------|----------------|--------------|
| Install | `pip install flask` | `npm install express` |
| Route | `@app.route('/')` | `app.get('/', ...)` |
| Query param | `request.args.get('name')` | `req.query.name` |
| Send response | `return "..."` | `res.send("...")` |
| Start server | `app.run(port=5000)` | `app.listen(5000)` |

### Real commands I ran
- `npm init -y`
- `npm install express`
- `node server.js`

### Things I saw
- Server printed "Server running on http://127.0.0.1:5000"
- `/` returned "Hello, Felix! Node.js and Express are alive."
- `/greet?name=Felix` returned "Hello, Felix! You are using Node.js."

### My own words (locked in)
- Node.js is JavaScript on the server.
- Express is a micro-framework, like Flask.
- The concepts are the same: route, request, response.
- `req` = what the client sent.
- `res` = what the server sends back.
- Node.js is async, so it handles many requests at once without blocking.
- `npm` is the package manager (like `pip`).
- `npm install express` installs the framework.
- `node server.js` starts the server.
- Express is used by Netflix, PayPal, Uber, and LinkedIn.
- pos-lab uses Node.js, so I can read its code more easily now.

### Connection to other topics
- 5.1 (Backend loop) — same loop, different language.
- 5.2 (Flask) — same concepts, Python syntax.
- 7.5.2 (Processes/Threads) — Node is single-threaded but async.
- 8.4 (Secure coding) — input validation applies to both.
- 8.10 (Secure API) — same API design principles.
- 12.15 (Web hacking) — SQLi/XSS apply to both Flask and Express.

## 5.3 Python Backend (Django) — Phase B DONE ✅

Installed Django on Termux.
Created a project, an app, a model, and used the admin panel.

### Core concepts
- **Django** = a full-stack Python framework ("batteries included").
- **MVT** = Model, View, Template.
- **ORM** = Object-Relational Mapper. Python classes → database tables.
- **Admin Panel** = built-in dashboard to manage data.
- **Migrations** = how Django creates/updates database tables.

### The commands
- `django-admin startproject myproject`
- `python manage.py startapp shop`
- `python manage.py makemigrations`
- `python manage.py migrate`
- `python manage.py createsuperuser`
- `python manage.py runserver`

### The structure


### Real commands I ran
- `pip install django tzdata`
- `django-admin startproject myproject`
- `python manage.py startapp shop`
- `python manage.py makemigrations`
- `python manage.py migrate`
- `python manage.py createsuperuser`
- `python manage.py runserver 0.0.0.0:8000`

### Things I saw
- The Django welcome page ("The install worked successfully!").
- The admin login page.
- The admin dashboard with Users, Groups, and Products.
- Added a product ("Bread") via the web form.
- The change history showed "felix Added" with a timestamp.

### My own words (locked in)
- Django is "batteries included." Flask is minimalist.
- Django gives you the admin panel, the ORM, auth, and security.
- A model is a Python class that becomes a database table.
- Migrations are how Django applies model changes to the database.
- The admin panel is free. You don't build it.
- `createsuperuser` creates the admin account.
- Termux needs `tzdata` (pip install tzdata) for Django to display dates.
- Django is used by Instagram, Pinterest, NASA, Spotify.
- Flask is better for small APIs. Django is better for big apps.
- The ORM means you never write SQL directly.

### Connection to other topics
- 5.1 (Backend) — Django is a backend framework.
- 5.2 (Flask) — the comparison.
- 6.1 (Databases) — the ORM creates the tables.
- 8.4 (Secure Coding) — Django has built-in CSRF, XSS protection.
- 8.10 (Secure API) — Django REST Framework for APIs.
- 7.9 (Nginx) — Django runs behind Nginx.
- 7.6 (Docker) — Django in a container.

## 5.5 REST API Design — Phase B DONE ✅

Understood the rules of REST.
Graded pos-lab's API against the rules.

### Core concepts
- **REST** = Representational State Transfer. A set of rules for web APIs.
- **Resources** = nouns (products, users, sales).
- **Methods** = verbs (GET, POST, PUT, PATCH, DELETE).
- **Golden rule:** nouns in URLs, verbs in methods.

### The 5 methods
| Method | Action | Example |
|--------|--------|---------|
| GET | Read | GET /products |
| POST | Create | POST /products |
| PUT | Update (full) | PUT /products/1 |
| PATCH | Update (partial) | PATCH /products/1 |
| DELETE | Delete | DELETE /products/1 |

### The URL rules
- Plural nouns: `/products`, not `/product`.
- No verbs: `/products`, not `/getProducts`.
- Nested: `/products/1/reviews`.
- Versioned: `/api/v1/products`.

### The status codes
- 200 OK
- 201 Created
- 204 No Content
- 400 Bad Request
- 401 Unauthorized
- 403 Forbidden
- 404 Not Found
- 429 Too Many Requests
- 500 Server Error

### The JSON format
```json
{
  "ok": true,
  "count": 5,
  "products": [...]
}
Real commands I ran
grep -n "GET /api|POST /api|PUT /api|DELETE /api" ~/pos-lab/server.js

Things I saw
pos-lab uses GET /api/products, POST /api/products, PUT /api/products/:id, DELETE /api/products/:id.

It follows REST rules (nouns, methods, plural).

One minor violation: POST /api/security/alerts/:id/ack (verb in URL).


## 5.8 Env Vars & Config — Phase B DONE ✅

Built an Express app that reads from `.env`.
Verified the secret is loaded but not exposed.

### Core concepts
- **`.env` file** = local config/secrets (never committed).
- **`process.env`** = the object that holds environment variables.
- **`dotenv`** = the package that loads `.env` into `process.env`.
- **`.gitignore`** = tells git to ignore `.env` and `node_modules`.

### The 3 files
1. **`.env`** (real secrets, ignored by git).
2. **`.gitignore`** (contains `.env` and `node_modules/`).
3. **`.env.example`** (placeholders, committed to git).

### Real commands I ran
- `npm install express dotenv`
- `nano .env` (PORT=3000, SECRET=my_super_secret_key)
- `nano .gitignore` (node_modules/, .env)
- `nano server.js` (require('dotenv').config())
- `node server.js`

### Things I saw
- The server started on port 3000.
- The secret loaded (`my_s...`).
- The response showed `secretLoaded: "Yes (hidden)"`.

### My own words (locked in)
- Secrets go in `.env`, not in code.
- `.env` goes in `.gitignore`.
- `.env.example` shows what variables are needed (no secrets).
- `dotenv` reads `.env` and puts the values in `process.env`.
- Same code, different config (dev/staging/prod).
- If a secret is in Git, it's leaked forever.
- The average time for a leaked AWS key to be used is 3 minutes.
- In production, use a secrets manager (AWS Secrets Manager, Vault).
- Never commit `.env` to GitHub.
- `.gitignore` is your first line of defense.

### Connection to other topics
- 5.2 (Flask) — Flask uses `python-dotenv`.
- 5.3 (Django) — Django uses `django-environ`.
- 5.4 (Express) — Express uses `dotenv`.
- 7.5.5 (Env Vars & Shells) — the shell-level env vars.
- 7.13 (Environment Management) — the broader concept.
- 7.8 (CI/CD) — GitHub Actions uses secrets.
- 8.10 (Secure API) — secrets in APIs.
- 12.34 (Cloud Security) — secrets managers in the cloud.

## 5.7 Validation & Error Handling — Phase B DONE ✅

Added validation and error handling to an Express API.
Tested with invalid and valid input.

### Core concepts
- **Validation** = checking input before using it.
- **Type:** Is it a number? A string?
- **Format:** Is it a valid email?
- **Length:** Is it too long?
- **Required:** Is it missing?
- **If invalid:** Return `400 Bad Request` with a clear message.
- **Error Handling** = `try/catch` to catch errors before they crash.
- **If server crashes:** Return `500` (generic) but log the real error.

### The golden rules
1. Never trust input.
2. Never leak errors (no stack traces to the user).
3. Always validate before using.
4. Always `try/catch` around risky code.

### Real commands I ran
- `node validation.js`
- `curl -X POST .../api/products -d '{"name":"Bread","price":"abc"}'` → `400` (invalid price).
- `curl -X POST .../api/products -d '{"name":"Bread","price":60}'` → `201` (valid).

### Things I saw
- Invalid input: `{"ok":false,"error":"price must be a number greater than 0"}`
- Valid input: `{"ok":true,"product":{"name":"Bread","price":60}}`
- The server did NOT crash on invalid input.

### My own words (locked in)
- Validation = checking input before using it.
- Never trust user input.
- Return 400 for invalid input.
- Return 500 for server crashes (but hide the stack trace).
- `try/catch` catches errors and prevents crashes.
- The error message should be clear (but not leak secrets).
- If you don't validate, the server crashes or corrupts data.
- A professional API validates everything.
- `typeof` checks the type.
- `!name` checks if it's missing.

### Connection to other topics
- 5.5 (REST API) — the endpoint we validated.
- 5.2 (Flask) — Flask uses `request.get_json()` + `try/except`.
- 5.3 (Django) — Django uses forms or serializers for validation.
- 8.4 (Secure Coding) — validation prevents SQLi, XSS.
- 8.10 (Secure API) — validation is API security.
- 12.15 (Web Hacking) — SQLi is a validation failure.
- 8.9 (Rate Limiting) — 429 for too many requests.
- 5.1 (HTTP Status Codes) — 400, 500.

## 5.6 Auth (JWT, OAuth) — Phase B DONE ✅

Built a JWT authentication system with Express.
Logged in, got a token, and accessed a protected route.

### Core concepts
- **Authentication** = proving who you are (login).
- **Authorization** = proving what you're allowed to do (roles).
- **JWT** = JSON Web Token. 3 parts: header.payload.signature.
- **Payload** contains: `sub` (user ID), `username`, `role`, `iat` (issued), `exp` (expiry).
- **Signature** proves the token wasn't tampered with.
- **OAuth** = "Login with Google" (third-party auth).

### The flow
1. POST /login with username/password.
2. Server verifies.
3. Server signs a JWT with the secret.
4. Client stores the JWT.
5. Client sends `Authorization: Bearer <token>` on every request.
6. Server verifies the signature and decodes the user.

### Real commands I ran
- `npm install jsonwebtoken`
- `node auth.js`
- `curl -X POST .../login -d '{"username":"felix","password":"password123"}'` → got a token.
- `curl .../protected` → `401` (no token).
- `curl .../protected -H "Authorization: Bearer <token>"` → `200` (welcome felix).

### Things I saw
- JWT token: `eyJhbGciOiJIUzI1NiIs...`
- Payload: `{"sub":1,"username":"felix","role":"boss","iat":...,"exp":...}`
- Without token: `{"ok":false,"error":"No token provided"}`
- With token: `{"ok":true,"message":"Welcome, felix","user":{...}}`

### My own words (locked in)
- JWT = the wristband at a concert. You show it instead of your ID.
- The token has 3 parts: header, payload, signature.
- The signature prevents tampering.
- The secret must be in `.env` (never in code).
- The token must have an expiry (`exp`).
- The client sends `Bearer <token>` in the Authorization header.
- OAuth = "Login with Google" (third-party).
- Never store the JWT secret in GitHub.
- Use `RS256` (asymmetric) for production.
- `HS256` (symmetric) is fine for simple apps.
- The token is proof of identity. The server trusts it if the signature is valid.
- If an attacker steals the token, they can act as you (session hijacking, 8.8).

### Connection to other topics
- 8.8 (Auth Attacks) — session hijacking, token theft.
- 8.10 (Secure API) — JWT is API auth.
- 12.7 (Symmetric vs Asymmetric) — HS256 vs RS256.
- 12.9 (Digital Signatures) — how JWT signatures work.
- 7.13 (Env Management) — the secret in `.env`.
- 5.7 (Validation) — validate login input.
- 12.17 (Password Attacks) — never store plaintext passwords.

## 5.10 WebSockets — Phase B DONE ✅

Built a real-time chat app with Socket.io.
Tested broadcasting messages between two browser tabs.

### Core concepts
- **WebSockets** = full-duplex (two-way) communication over a single TCP connection.
- **HTTP** = request-response (client asks, server answers, connection closes).
- **WebSocket** = the connection stays open. Server can push data.
- **Socket.io** = the most popular Node.js library for WebSockets.
- **Broadcast** = sending a message to everyone connected (`io.emit`).
- **Rooms** = sending a message to a specific group (optional, not covered today).

### The flow
1. Client connects to `ws://` (or `http://` with upgrade).
2. Handshake: HTTP request with `Upgrade: websocket`.
3. Connection stays open.
4. Client sends messages (`socket.emit`).
5. Server broadcasts (`io.emit`).
6. Client receives (`socket.on`).

### Real commands I ran
- `npm install express socket.io`
- `node server.js`
- Opened `http://127.0.0.1:3000` in two tabs.
- Typed "Hi" and "Yes" in one tab, saw them in the other.

### Things I saw
- Messages appeared instantly in both tabs.
- No page reload.
- The server logged "A user connected: <socket.id>".

### My own words (locked in)
- WebSockets = phone call. HTTP = letter.
- The connection stays open.
- The server can push data to the client.
- `socket.emit` = send a message.
- `io.emit` = broadcast to everyone.
- `socket.on` = listen for a message.
- Socket.io handles reconnection and fallbacks.
- WebSockets are used for chat, live dashboards, games, notifications.
- HTTP is for APIs (request-response).
- WebSockets are for real-time (two-way).

### Connection to other topics
- 5.1 (Backend loop) — the loop is different for WebSockets (no closing).
- 5.5 (REST API) — REST is request-response. WebSockets are real-time.
- 5.9 (File Uploads) — not covered today, but possible over WebSockets.
- 12.14 (Exploitation) — reverse shells use raw sockets (like WebSockets).
- 7.5.2 (Threads) — Socket.io uses Node's event loop.
- 7.6 (Docker) — Socket.io can run in a container.
- 8.10 (Secure API) — WebSockets need auth too (handshake token).
- 12.33 (API Security) — WebSockets have unique security risks.

## 5.9 File Uploads & Storage — Phase B DONE ✅

Built a secure file upload endpoint with Express + Multer.
Tested with a .txt (rejected) and a .png (accepted, renamed).

### Core concepts
- **File uploads** are the most dangerous feature (OWASP FILE-01 to FILE-04).
- **Multipart/form-data** = the encoding used for file uploads.
- **Multer** = the Express middleware for handling file uploads.
- **The 4 vulnerabilities:**
  - FILE-01: Unrestricted file extension (upload a .php shell).
  - FILE-02: Path traversal (../../etc/passwd).
  - FILE-03: Files served from web root (uploaded .html runs).
  - FILE-04: No size limit (upload 100GB, crash server).

### The 5 validation rules
1. Check the extension (allowlist: .jpg, .png, .pdf).
2. Check the MIME type (Content-Type header).
3. Rename the file (UUID).
4. Limit the size (max 2MB).
5. Store outside the web root.

### Real commands I ran
- `npm install express multer`
- `node server.js`
- `curl -X POST .../upload -F "file=@test.txt"` → `400` (rejected).
- `curl -X POST .../upload -F "file=@test.png"` → `200` (accepted, renamed).
- `ls -la uploads/` → saw the UUID filename.

### Things I saw
- `.txt` file: `{"ok":false,"error":"Only .jpg, .jpeg, .png allowed"}` (clean JSON, no stack trace).
- `.png` file: `{"ok":true,"filename":"65128157-...png"}`.
- The file was saved as a UUID, not the original name.
- The original `.txt` was rejected before saving.

### My own words (locked in)
- Never trust the filename. Rename it.
- Never trust the extension. Check the MIME type.
- Never trust the content. Check the magic bytes (FF D8 FF for JPEG).
- Never store files in the web root. Use a separate folder.
- Never allow unlimited size. Set a max.
- Multer is the standard for Express uploads.
- The error must be clean JSON (no stack traces).
- UUID is the safe way to rename files.
- Path traversal is destroyed by renaming.
- File uploads are a classic path to RCE.

### Connection to other topics
- 5.7 (Validation) — the same rules apply to files.
- 8.2 (OWASP) — A05 (misconfiguration) and FILE-01 to FILE-04.
- 12.15 (Web Hacking) — file upload exploits.
- 8.4 (Secure Coding) — never trust input (including files).
- 7.6 (Docker) — uploads should be in a volume, not the container.
- 7.10 (Cloud) — store uploads in S3, not on the server.
- 5.8 (Env Vars) — upload paths in config.

## 5.13 Caching (Redis) — Phase B DONE ✅

Added Redis caching to an Express API.
Tested cache miss, cache hit, invalidation, and refresh.

### Core concepts
- **Cache-aside pattern:** check cache → if miss, query DB → save to cache.
- **Cache hit:** data found in Redis (fast).
- **Cache miss:** data not in Redis (query DB).
- **TTL:** Time To Live (60 seconds).
- **Invalidation:** delete the cache when the data changes.

### The flow I tested
1. GET → miss → query DB → save to cache.
2. GET → hit → return from cache.
3. POST → add to DB → delete cache.
4. GET → miss → query DB (includes new data) → save to cache.

### Real commands I ran
- `redis-server &`
- `npm install express redis`
- `node server.js`
- `curl /api/products` (miss)
- `curl /api/products` (hit)
- `curl -X POST /api/products` (invalidate)
- `curl /api/products` (miss again, fresh data)

### Things I saw
- Test 1: `source: "database"` (miss).
- Test 2: `source: "cache"` (hit).
- Test 3: `{"ok":true,"product":{...}}`.
- Test 4: `source: "database"` (miss, includes Soap).
- The new product appeared immediately because the cache was invalidated.

### My own words (locked in)
- Cache hit = fast. Cache miss = slow.
- TTL = how long the cache lives.
- Invalidation = delete the cache when data changes.
- Without invalidation, the cache lies.
- Redis is the standard cache.
- `client.get()` = read.
- `client.setEx()` = write with expiry.
- `client.del()` = delete.
- POST/PUT/DELETE must invalidate the cache.
- The database load drops by 99%.
- The pattern is called "cache-aside" (lazy loading).

### Connection to other topics
- 6.8 (Caching Layer) — the database view of caching.
- 6.4 (Redis) — the basics.
- 5.4 (Express) — the backend framework.
- 8.9 (Rate Limiting) — Redis is used for rate limit counters.
- 7.6 (Docker) — Redis in a container.
- 7.7 (Docker Compose) — Redis + app.
- 7.12 (Monitoring) — cache hit ratio is a key metric.
- 12.34 (Cloud Security) — Redis must be secured (no public access).
