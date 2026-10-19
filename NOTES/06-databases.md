## 6.1 Database Fundamentals — Phase B DONE ✅

Explored pos-lab's SQLite database. Found 18 tables, looked at
schema, queried users and products.

### Core concepts
- Database = structured collection of data
- Managed by a DBMS (SQLite here)
- Table = collection of related data (like a spreadsheet tab)
- Row = one entry (one student in a register)
- Column = one attribute (name, price)
- Data types enforced: INTEGER, TEXT, REAL, BOOLEAN (via 0/1)
- Primary key = unique ID for each row (users.id)
- Foreign key = reference to another table (users.shop_id → shops.id)
- Constraints: NOT NULL, UNIQUE, CHECK, DEFAULT, REFERENCES

### The 4 core terms
| Term | What | Example |
|------|------|---------|
| Table | The collection | users |
| Row | One entry | boss, manager, seller |
| Primary key | Unique column | id (1, 2, 3) |
| Foreign key | Points to another table | shop_id → shops.id |

### The 18 tables in pos-lab
Core business: users, shops, products, stock, sales, transactions,
expenses, transfers, sessions, audit_log, uploads, app_settings
SQLite internals: sqlite_sequence, products_fts, products_fts_data,
products_fts_idx, products_fts_docsize, products_fts_config

### The users table schema
CREATE TABLE users (
  id            INTEGER PRIMARY KEY AUTOINCREMENT,
  username      TEXT    NOT NULL UNIQUE,
  email         TEXT    NOT NULL UNIQUE,
  name          TEXT    NOT NULL,
  phone         TEXT    DEFAULT '',
  password_hash TEXT    NOT NULL,
  role          TEXT    NOT NULL CHECK (role IN ('boss','manager','seller')),
  shop_id       INTEGER REFERENCES shops(id) ON DELETE SET NULL,
  is_approved   INTEGER NOT NULL DEFAULT 0,
  is_active     INTEGER NOT NULL DEFAULT 1,
  created_at    TEXT    NOT NULL DEFAULT (datetime('now')),
  updated_at    TEXT
)

### Real commands I ran
- ls -lh ~/pos-lab/db/pos.db           → 184 KB
- node -e "...SELECT name FROM sqlite_master..."  → 18 tables
- node -e "...SELECT sql FROM sqlite_master..."  → users schema
- node -e "...SELECT id, username, role FROM users..."  → 3 rows
- node -e "...SELECT id, name, price FROM products..."  → products

### Things I saw
- 3 users: boss (role=boss), manager (role=manager), seller (role=seller)
- Schema uses constraints: PRIMARY KEY, NOT NULL, UNIQUE, CHECK, DEFAULT, REFERENCES
- password_hash column (NOT password) — fail-safe
- role has CHECK constraint — defense in depth
- shop_id is a foreign key to shops.id
- SQLite = single file, embedded, no server

### My own words (locked in)
- Table = rows + columns. Row = one item. Column = one attribute.
- Primary key = unique ID (users.id = 1, 2, 3)
- Foreign key = link to another table (shop_id → shops.id)
- CHECK enforces allowed values (role must be boss/manager/seller)
- NOT NULL = required. UNIQUE = no duplicates. DEFAULT = auto.
- pos-lab uses SQLite: single file, no server
- Database is like a Python dict but on disk, with millions of rows
- Defensive design:
  - CHECK constraint = DB rejects invalid roles
  - password_hash (not password) = no plaintext leak
  - Multiple layers = defense in depth
- Primary key vs foreign key vs row — three different things:
  - Row = one entry (boss, manager, seller)
  - Primary key = column that uniquely identifies it (id)
  - Foreign key = column that points to another table (shop_id)
- Never use 777 in databases either (well, permissions — not DB)

### Extra insight
- The password_hash column name contains the whole 12.6–12.8 lesson:
  - DB never stores plaintext
  - MD5 = crackable in 10 ms
  - scrypt = uncrackable
  - This is why hashing matters
## 6.2 SQL Basics — Phase B DONE ✅

Ran real SQL queries against pos-lab's SQLite database.
Found 5 products, computed margins, got aggregates.

### Core concepts
- SQL = Structured Query Language
- Created 1974 by IBM (Donald Chamberlin & Raymond Boyce)
- Same language across MySQL, PostgreSQL, SQLite, Oracle, SQL Server
- 5 core verbs: SELECT, INSERT, UPDATE, DELETE, CREATE

### The anatomy of a SELECT
```sql
SELECT name, base_price           -- columns (or * for all)
FROM products                     -- table
WHERE base_price < 100            -- filter rows
ORDER BY base_price ASC           -- sort (ASC / DESC)
LIMIT 10;                         -- take only 10
## 6.2 SQL Basics — Phase B DONE ✅

Ran real SELECT queries against pos-lab's SQLite database.
Filtered, sorted, computed, and aggregated data.

### Core concepts
- SQL = Structured Query Language. Created 1974 at IBM. Still universal.
- 5 core verbs: SELECT, INSERT, UPDATE, DELETE, CREATE
- SELECT is the most-used (reading data)
- SQL is like a Mad Lib: fill in the blanks
  SELECT [columns] FROM [table] WHERE [condition]

### The anatomy of SELECT
SELECT name, base_price         ← columns
FROM products                    ← table
WHERE base_price < 100           ← filter rows
ORDER BY base_price ASC          ← sort
LIMIT 10;                        ← take first 10

### WHERE operators
=, !=, <, >, <=, >=, LIKE, IN, BETWEEN, IS NULL, AND, OR, NOT

### Aggregates (computed across many rows)
- SUM(col) → total
- COUNT(*) → how many
- AVG(col) → average
- Use .get() (one row) not .all() (many rows)

### Computed columns
SELECT (base_price - cost_price) AS margin
- Can do arithmetic in SELECT
- AS gives the result a name
- Can ORDER BY the computed value

### Column naming rule (CRITICAL)
- Always inspect schema before querying
- `SELECT sql FROM sqlite_master WHERE name='table'`
- pos-lab products has: cost_price and base_price, NOT price
- My first query failed: "no such column: price" — real error

### Real commands I ran
- SELECT * FROM users → 3 users (boss, manager, seller)
- SELECT * FROM products WHERE price < 100 → ERROR (no price column)
- SELECT name, base_price FROM products WHERE base_price < 100 → 4 rows
- SELECT ... ORDER BY base_price ASC → 5 rows sorted
- SELECT (base_price - cost_price) AS margin ORDER BY margin DESC → Soap 40, Bread 20, Milk 20
- SELECT SUM(base_price), COUNT(*), AVG(base_price) FROM products → 255.3, 5, 51.06

### Things I saw
- 3 users: boss (role=boss), manager (role=manager), seller (role=seller)
- 5 products: Bread(60/40), Milk(75/55), Soap(120/80), Dime(0.1/0.1), Penny(0.2/0.2)
- Margins: Soap=40 (highest), Bread=20, Milk=20, Dime=0, Penny=0
- Total base value: 255.3 KES
- Average price: 51.06 KES

### My own words (locked in)
- SELECT * = all columns. SELECT name = only name.
- WHERE filters rows. ORDER BY sorts. ASC = small→large, DESC = large→small.
- Aggregates compute one value across many rows (SUM, COUNT, AVG).
- AS = alias. You can name a computed column.
- Inspect schema before querying. Otherwise "no such column" errors.
- The error "no such column: price" taught me more than the query would have.
- Schema inspection = recon for databases.
- Real-world queries answer business questions:
  - Which product has the highest margin?
  - What's my total inventory value?
  - How many users?
- The next topic (6.3 Joins) will show how to combine tables
  (e.g., total inventory = products JOIN stock)

### Compare to Python dicts
- Python dict = one item in memory
- Database = millions of dicts on disk, queryable in ms
- SQL is how you "ask" the database for a subset
