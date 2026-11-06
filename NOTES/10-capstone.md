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
