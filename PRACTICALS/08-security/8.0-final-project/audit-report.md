# Security Audit Report — Cyber Café Guestbook
**Date:** 2026-10-23
**Auditor:** Felix Otieno

## Executive Summary
The Cyber Café Guestbook has 5 critical vulnerabilities. An attacker can log in as admin without a password, view all users without authentication, steal data, and run system commands on the server.

## Findings

### 1. SQL Injection (Critical)
- **CVSS:** 9.8
- **Location:** `/api/login`
- **Description:** The login endpoint concatenates the username and password directly into the SQL query.
- **PoC:** `curl -X POST .../api/login -d '{"username":"admin' OR 1=1 --","password":"x"}'`
- **Impact:** Attacker logs in as admin without a password. Can dump the entire database.
- **Fix:** Use parameterized queries (`?`).

### 2. Stored XSS (High)
- **CVSS:** 8.2
- **Location:** `/` (guestbook display) and `/api/messages`
- **Description:** Messages are rendered using `innerHTML` without escaping.
- **PoC:** `<img src=x onerror=alert("XSS")>`
- **Impact:** Attacker steals session cookies or executes malicious actions in victim browsers.
- **Fix:** Use `textContent` or `escape-html`.

### 3. Hardcoded Secret (High)
- **CVSS:** 8.0
- **Location:** Line 11 in `server.js` (`const JWT_SECRET = "secret123"`)
- **Description:** The JWT secret is hardcoded in the source code.
- **Impact:** If the source code leaks, attackers can forge valid tokens.
- **Fix:** Use `process.env.JWT_SECRET` in a `.env` file.

### 4. Missing Authorization (Critical)
- **CVSS:** 9.1
- **Location:** `/api/admin/users`
- **Description:** The admin endpoint does not check if the user is logged in or if they have the admin role.
- **PoC:** `curl http://.../api/admin/users` (no token needed)
- **Impact:** Any user on the internet can view all users and roles.
- **Fix:** Check `req.user.role === 'admin'` before returning data.

### 5. Command Injection (Critical)
- **CVSS:** 9.8
- **Location:** `/api/ping`
- **Description:** User input is passed to `exec()` in the shell.
- **PoC:** `curl ".../api/ping?host=127.0.0.1; whoami"`
- **Impact:** Attacker runs arbitrary system commands (e.g., `rm -rf /`, `cat .env`).
- **Fix:** Use `execFile()` or `execFileSync()` with an argument array, not a shell string.

## Remediation Plan
1. Fix SQL Injection immediately (parameterized queries).
2. Fix Command Injection immediately (execFile).
3. Add authorization checks to all admin routes.
4. Move JWT_SECRET to `.env`.
5. Use `textContent` for all user input rendered to HTML.
