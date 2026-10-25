const express = require('express');
const app = express();

// Allow CORS (for local development only)
app.use((req, res, next) => {
  res.header('Access-Control-Allow-Origin', '*');
  next();
});

// Route 1: Homepage
app.get('/', (req, res) => {
  res.send('Hello, Felix! Node.js and Express are alive.');
});

// Route 2: Greet
app.get('/greet', (req, res) => {
  const name = req.query.name || 'stranger';
  res.send(`Hello, ${name}! You are using Node.js.`);
});

// Start the server
app.listen(5000, () => {
  console.log('Server running on http://127.0.0.1:5000');
});
