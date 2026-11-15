# Job Mapping — Fullstack Engineer

### Requirement 1: Build user interfaces (HTML/CSS/JS).
- **My Evidence:** Built the Frontend for the Blog. Added a Login Modal, a "Journal" section, and an Admin editor using vanilla JavaScript.
- **Interview Pitch:** "I don't just build static pages. I write the JavaScript that fetches data from the API and renders it dynamically without page reloads."

### Requirement 2: Develop RESTful APIs.
- **My Evidence:** Built the Backend (`/api/login` and `/api/posts`) using Node.js Serverless Functions. Handled GET, POST, PUT, and DELETE.
- **Interview Pitch:** "I understand REST verbs. I know the difference between GET and POST, and I use the correct status codes (200, 201, 401, 404)."

### Requirement 3: Implement authentication and secure data flow.
- **My Evidence:** Hashed the admin password with bcrypt. Generated a JWT on login. Protected the POST/PUT/DELETE endpoints with `Authorization: Bearer <token>`.
- **Interview Pitch:** "I know how to secure a fullstack app. The frontend never sees the password; it only receives the JWT. The backend verifies that token before writing to the database."

### Requirement 4: Work with PostgreSQL.
- **My Evidence:** Used Prisma Postgres. Created a `posts` table, inserted data, and queried it using parameterized SQL (`$1`, `$2`).
- **Interview Pitch:** "I use parameterized queries to prevent SQL injection. I understand how to connect a Node.js backend to a Postgres database."
