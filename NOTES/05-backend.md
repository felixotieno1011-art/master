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
