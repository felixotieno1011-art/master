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
