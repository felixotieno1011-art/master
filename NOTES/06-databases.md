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
