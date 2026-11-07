## 10.2 Blog with Auth — Phase B DONE ✅

Built a fullstack blog with authentication.
Added a Node.js serverless backend, a Postgres database, and an admin login to the portfolio site.

### Core concepts
- **Static vs Dynamic:** Static serves HTML. Dynamic talks to a backend + DB.
- **Serverless Functions:** Vercel automatically turns `api/*.js` into HTTP endpoints.
- **Bcrypt:** Used to hash the admin password.
- **JWT:** Used to secure the `POST /api/posts` endpoint.
- **Environment Variables:** Used for the database URL and JWT secret.
- **CRUD:** Create (POST), Read (GET), Update (PUT/PATCH), Delete (DELETE).

### The drill (what I actually did)
- Created `api/login.js`, `api/posts.js`, `api/db.js`.
- Connected Prisma Postgres.
- Built a frontend UI (login modal, blog list, admin form).
- Tested `GET` (public) and `POST` (protected).
- Deleted test posts using `psql`.

### Things I saw
- `vercel dev` can be fussy with `.env` files.
- Prisma Postgres accepts standard `postgres://` URLs.
- A frontend is just a window into a backend.

### My own words (locked in)
- Static is a poster. Dynamic is a billboard.
- Auth protects the writer, not the reader.
- Env vars keep secrets safe.
- CRUD is the heartbeat of the web.

### Connection to other topics
- 5.2 (Flask) / 5.4 (Express) — the backend logic.
- 5.6 (Auth) — JWT.
- 6.2 (SQL) — the database queries.
- 7.8 (CI/CD) — Vercel deployment.
- 12.8 (Hashing) — bcrypt.## Blog with Auth — Fullstack Build

### Architecture
- **Frontend:** Vanilla JS (fetch API) on `index.html`.
- **Backend:** Vercel Serverless Functions (`api/login.js`, `api/posts.js`).
- **Database:** Prisma Postgres (cloud).
- **Auth:** Bcrypt hashing + JWT (HS256).

### The Flow
1. User visits `index.html`. Frontend calls `GET /api/posts` and renders the list.
2. Admin clicks "Admin Login", enters password.
3. Backend hashes the password and compares it. If valid, returns a JWT.
4. Frontend saves the JWT in `localStorage`.
5. Admin writes a post. Frontend sends `POST /api/posts` with `Authorization: Bearer <token>`.
6. Backend verifies the JWT. If valid, inserts into Postgres and returns the new post.
7. Frontend refreshes the list.

### Challenges Solved
- **Database Connection:** `vercel dev` wasn't reading `.env.local`, so we created a `.env` file to force the environment variable.
- **Prisma Postgres:** It uses a standard `postgres://` URL (not `prisma://`), so the `pg` library works perfectly.

### Real CRUD
- **Create:** `POST /api/posts` (UI).
- **Read:** `GET /api/posts` (UI).
- **Delete:** `DELETE FROM posts;` (psql).

### Lesson
- A static site is just HTML. A fullstack app needs a backend + database.
- Auth protects the *write* actions, not the *read* actions.
- Environment variables are how you keep secrets out of the code.
## REST API CRUD Drill

### The Architecture
- **Frontend:** N/A for this drill (used `curl`).
- **Backend:** Vercel Serverless Functions.
- **Database:** Prisma Postgres.
- **Auth:** JWT (HS256).

### The Endpoints
- `GET /api/posts` → Returns all posts.
- `GET /api/posts/:id` → Returns one post (not implemented yet, but routed).
- `POST /api/posts` → Creates a post (requires JWT).
- `PUT /api/posts/:id` → Updates a post (requires JWT).
- `DELETE /api/posts/:id` → Deletes a post (requires JWT).

### The Drill (what I actually ran)
1. Logged in to get a JWT token.
2. `POST /api/posts` → Created "My First CRUD Post" (ID 4).
3. `PUT /api/posts/4` → Updated the title to "Updated Title".
4. `DELETE /api/posts/4` → Removed the post from the database.

### Lesson
- REST uses HTTP verbs to define actions.
- URLs are nouns (resources), verbs are actions.
- Dynamic routing (`[id].js`) allows one file to handle many IDs.
- Parameterized queries (`$1`) prevent SQL injection.
- JWTs protect state-changing operations (POST, PUT, DELETE).

## 10.3 REST API CRUD — Phase B DONE ✅

Built a complete CRUD REST API with dynamic routing and JWT protection.
Tested all four HTTP methods using `curl`.

### Core concepts
- **CRUD:** Create, Read, Update, Delete.
- **HTTP Verbs:**
  - `GET` = Read.
  - `POST` = Create.
  - `PUT` / `PATCH` = Update.
  - `DELETE` = Delete.
- **REST:** URLs are nouns (resources), HTTP methods are verbs (actions).
- **Dynamic Routing:** Vercel uses `[id].js` to capture URL parameters.
- **Status Codes:** `200 OK` (success), `201 Created`, `400 Bad Request`, `401 Unauthorized`, `404 Not Found`, `405 Method Not Allowed`.
- **Parameterized Queries:** `$1`, `$2` in SQL prevent injection.

### The drill (what I actually did)
- Created `api/posts/[id].js` to handle updates and deletes.
- Used `PUT /api/posts/4` to change the title.
- Used `DELETE /api/posts/4` to remove the post.
- Verified the database changed (and cleaned up).

### Things I saw
- Vercel routing requires a specific file structure (`[id].js`).
- Without dynamic routing, Vercel returns `404` for `/api/posts/4`.
- A `405` error means the route exists, but the method isn't allowed.
- The `pg` library requires parameterized queries for security.

### My own words (locked in)
- GET reads, POST creates, PUT updates, DELETE removes.
- The URL is the noun; the method is the verb.
- Dynamic routing captures IDs from the URL.
- JWT protects the write operations.
- Always parameterize SQL queries.

### Connection to other topics
- 5.5 (REST API Design) — the theory behind this.
- 5.6 (Auth) — JWT.
- 6.2 (SQL) — the queries.
- 10.2 (Blog with Auth) — the frontend and DB setup.
- 12.15 (Web Hacking) — why parameterized queries matter.
