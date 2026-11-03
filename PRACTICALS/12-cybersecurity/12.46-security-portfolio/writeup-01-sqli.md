# Vulnerability Report: SQL Injection

## 1. Summary
A SQL Injection vulnerability was discovered in the `user_id` parameter of the DVWA application. This allows an attacker to execute arbitrary SQL queries, bypass authentication, and dump the entire database.

## 2. Severity
**High** (CVSS: 8.8)
*(Note: High because it exposes sensitive data).*

## 3. Affected Target
- **App:** DVWA (Damn Vulnerable Web Application)
- **URL:** `/vulnerabilities/sqli/`
- **Environment:** Isolated Docker container (legal lab)

## 4. Steps to Reproduce
1. Log in to DVWA as `admin`.
2. Navigate to the SQL Injection module.
3. Set security level to "Low".
4. In the "User ID" field, enter the payload: `1' OR '1'='1`
5. Click Submit.

## 5. Evidence (Proof)
- **Expected behavior:** Returns the details for User ID 1 (admin).
- **Actual behavior:** Returns the details for ALL users in the database (admin, Gordon Brown, Hack Me, Pablo Picasso, Bob Smith).
- **Screenshot:** (Attach the screenshot you took earlier)

## 6. Root Cause Analysis
The application concatenates user input directly into the SQL query:
```php
$query = "SELECT first_name, last_name FROM users WHERE user_id = '$id';";
```

Because the input $id is wrapped in single quotes, an attacker can break out of the string by submitting a single quote ('), followed by arbitrary SQL.

7. Remediation (The Fix)

Use Parameterized Queries (Prepared Statements).

```php
$stmt = $mysqli->prepare("SELECT first_name, last_name FROM users WHERE user_id = ?");
$stmt->bind_param("s", $id);
$stmt->execute();
```

This ensures the database treats the input strictly as data, never as executable code.

8. References

· OWASP Top 10 (A03:2021 – Injection)
· CWE-89: Improper Neutralization of Special Elements used in an SQL Command

```
