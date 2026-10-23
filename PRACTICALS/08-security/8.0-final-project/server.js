// cyber-cafe-guestbook — VULNERABLE APP
// This is for training. Do not deploy this to the internet.

const express = require('express');
const { DatabaseSync } = require('node:sqlite');
const jwt = require('jsonwebtoken');
const { exec } = require('node:child_process');

const app = express();
const db = new DatabaseSync(':memory:');
const PORT = 4000;

// VULN 3: Hardcoded secret
const JWT_SECRET = "secret123";

// Database setup
db.exec(`
  CREATE TABLE users (id INTEGER PRIMARY KEY, username TEXT, password TEXT, role TEXT);
  CREATE TABLE messages (id INTEGER PRIMARY KEY, author TEXT, content TEXT);
  INSERT INTO users (username, password, role) VALUES ('admin', 'admin123', 'admin');
  INSERT INTO users (username, password, role) VALUES ('guest', 'guest123', 'guest');
`);

app.use(express.urlencoded({ extended: true }));
app.use(express.json());

// VULN 1: SQL Injection in Login
app.post('/api/login', (req, res) => {
  const { username, password } = req.body;
  // Vulnerable: string concatenation
  const query = `SELECT * FROM users WHERE username = '${username}' AND password = '${password}'`;
  try {
    const user = db.prepare(query).get();
    if (!user) return res.status(401).json({ error: 'Invalid login' });
    
    // VULN 3 continued: signing with hardcoded secret
    const token = jwt.sign({ id: user.id, role: user.role }, JWT_SECRET);
    res.json({ token });
  } catch (e) {
    res.status(500).json({ error: e.message });
  }
});

// VULN 2 & VULN 4: XSS + IDOR
app.get('/api/messages', (req, res) => {
  const rows = db.prepare('SELECT * FROM messages').all();
  // Vulnerable: returning raw HTML content (XSS)
  res.json(rows);
});

app.post('/api/messages', (req, res) => {
  const { author, content } = req.body;
  db.prepare('INSERT INTO messages (author, content) VALUES (?, ?)').run(author, content);
  res.json({ ok: true });
});

// VULN 4: Missing Authorization (Admin panel)
app.get('/api/admin/users', (req, res) => {
  // Vulnerable: no token check, no role check
  const rows = db.prepare('SELECT id, username, role FROM users').all();
  res.json(rows);
});

// VULN 5: Command Injection
app.get('/api/ping', (req, res) => {
  const host = req.query.host || '127.0.0.1';
  // Vulnerable: shell execution with user input
  exec(`ping -c 1 ${host}`, (err, stdout) => {
    res.send(stdout || err.message);
  });
});

// Serve the UI
app.get('/', (req, res) => {
  res.send(`
    <html>
    <body>
      <h1>Cyber Café Guestbook</h1>
      <h2>Login</h2>
      <form action="/api/login" method="POST">
        <input name="username" placeholder="username" />
        <input name="password" placeholder="password" />
        <button>Login</button>
      </form>

      <h2>Guestbook</h2>
      <div id="messages"></div>
      <script>
        fetch('/api/messages').then(r => r.json()).then(rows => {
          document.getElementById('messages').innerHTML = rows.map(m => 
            '<div><b>' + m.author + '</b>: ' + m.content + '</div>'
          ).join('');
        });
      </script>
    </body>
    </html>
  `);
});

app.listen(PORT, () => {
  console.log(`Cyber Café running on http://127.0.0.1:${PORT}`);
});
