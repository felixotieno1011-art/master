# 6.1 Database Fundamentals — Exploration

## SPEC
1. Check database file
2. List all tables
3. Look at users table schema
4. Query all users
5. Query all products

## Results

### Database file
-rw------- 184 KB  ~/pos-lab/db/pos.db

### All tables (18 total)
users, sqlite_sequence, shops, products, stock, transactions,
expenses, transfers, audit_log, sales, uploads, app_settings,
sessions, products_fts, products_fts_data, products_fts_idx,
products_fts_docsize, products_fts_config

### users table schema
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

### Query: SELECT id, username, role FROM users
┌─────────┬────┬───────────┬───────────┐
│ (index) │ id │ username  │ role      │
├─────────┼────┼───────────┼───────────┤
│ 0       │ 1  │ 'boss'    │ 'boss'    │
│ 1       │ 2  │ 'manager' │ 'manager' │
│ 2       │ 3  │ 'seller'  │ 'seller'  │
└─────────┴────┴───────────┴───────────┘

## Core concepts
- Database = structured collection of data
- Managed by a DBMS (here: SQLite)
- Table = collection of related data (like a spreadsheet tab)
- Row = one entry (like one student in a register)
- Column = one attribute (name, price)
- Data types enforced: INTEGER, TEXT, REAL, etc.
- Primary key = unique ID for each row (users.id)
- Foreign key = reference to another table (users.shop_id → shops.id)
- Constraints: NOT NULL, UNIQUE, CHECK, DEFAULT, REFERENCES

## My own words (locked in)
- Table = rows + columns
- Row = one item
- Column = one attribute
- Primary key = unique ID (users.id = 1, 2, 3)
- Foreign key = link to another table (shop_id → shops)
- CHECK enforces values (role must be boss/manager/seller)
- NOT NULL means required
- UNIQUE means no duplicates
- pos-lab uses SQLite: single file, no server, embedded
- The database is like a dict: keys → values, but on disk
- Survives restarts, holds millions of rows, fast search

## Data types I saw
- INTEGER = whole numbers (id, shop_id, is_active)
- TEXT = strings (username, email, name, password_hash)
- REAL = decimals (price — though stored as INTEGER sometimes)
- DEFAULT = auto-value if not provided

## Constraints I saw
- PRIMARY KEY — unique, not null
- AUTOINCREMENT — auto-assigned numbers
- NOT NULL — required field
- UNIQUE — no duplicates
- CHECK — must be one of listed values
- REFERENCES — foreign key
- DEFAULT — fallback value
