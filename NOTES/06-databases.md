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

## 6.3 SQL Joins, Indexes, Transactions — Phase B DONE ✅

Wrote real JOINs against pos-lab's database.
Created an index. Tested a transaction with rollback.

### Core concepts
- **JOIN** = connecting tables using a shared column (e.g., `users.id = sales.seller_id`).
- **INNER JOIN** = only rows that match in both tables.
- **LEFT JOIN** = all rows from the left table, plus matches (or NULL) from the right.
- **RIGHT JOIN** = opposite of LEFT JOIN.
- **FULL OUTER JOIN** = all rows from both tables.
- **Index** = a lookup table that makes queries faster.
  - Create: `CREATE INDEX idx_name ON table (column);`
  - Speeds up WHERE, JOIN, ORDER BY.
  - Slows down INSERT/UPDATE/DELETE.
- **Transaction** = all or nothing. ACID.
  - `BEGIN`, `COMMIT`, `ROLLBACK`.
  - Atomicity, Consistency, Isolation, Durability.

### Real commands I ran
- `INNER JOIN users ON sales ON users.id = sales.seller_id` → only Sam Seller (5 rows).
- `LEFT JOIN users ON sales ON users.id = sales.seller_id` → all users (7 rows, Boss/Manager with null).
- `CREATE INDEX idx_sales_seller_id ON sales(seller_id);`
- `BEGIN TRANSACTION; UPDATE products SET base_price = 999 WHERE id = 1; ROLLBACK;`

### Things I saw
- INNER JOIN: 5 rows, all Sam Seller.
- LEFT JOIN: 7 rows, including The Boss and Mary Manager with `null` total_amount.
- Index created successfully.
- Transaction: price changed to 999 inside, then rolled back to 60.
- The `1.2000000000000002` float bug from SALE-05 is visible in the sales data.

### My own words (locked in)
- JOIN connects tables by a shared key.
- INNER JOIN = matches only.
- LEFT JOIN = everyone from the left, matched or null.
- Index makes reads faster but writes slower.
- Transaction = all or nothing (ACID).
- ROLLBACK undoes uncommitted changes.
- COMMIT saves changes permanently.
- Foreign keys are the links between tables.
- The database is the source of truth. Always use transactions for critical operations (money transfers, stock updates).
- The float bug in sales data is a real vulnerability (SALE-05).

### Connection to other topics
- 6.1 (Databases) — tables, keys.
- 6.2 (SQL Basics) — SELECT, WHERE.
- 8.10 (Secure API) — the JOIN is how the backend serves related data.
- 12.15 (Web Hacking) — SQL injection can target JOINs.
- pos-lab's `users` and `sales` tables are linked by `seller_id`.

## 6.4 NoSQL (MongoDB, Redis) — Phase B DONE ✅

Installed Redis on Termux. Stored and retrieved strings, lists, and hashes.
Understood the difference between SQL and NoSQL.

### Core concepts
- **NoSQL** = databases that don't use rigid tables (rows/columns).
- **4 types:**
  1. **Document** (MongoDB) — JSON-like documents, flexible schema.
  2. **Key-Value** (Redis, Memcached) — key → value, in-memory, ultra-fast.
  3. **Wide-Column** (Cassandra) — dynamic columns, massive scale.
  4. **Graph** (Neo4j) — nodes and relationships.

### SQL vs NoSQL
| Feature | SQL (PostgreSQL) | NoSQL (MongoDB/Redis) |
|---------|------------------|------------------------|
| Structure | Fixed tables | Flexible documents / key-value |
| Schema | Strict | Dynamic |
| Relationships | JOINs | Embedded documents |
| Scale | Vertical (bigger server) | Horizontal (more servers) |
| Consistency | Strong (ACID) | Eventual |
| Use case | Banking, e-commerce | Chat, feeds, caches, IoT |

### Redis (Key-Value)
- Stores data in **RAM** (fast, but lost on restart unless configured).
- **Types:**
  - String: `SET key value`, `GET key`
  - List: `RPUSH key value`, `LRANGE key start end`
  - Hash: `HSET key field value`, `HGETALL key`
  - Set: `SADD key value`, `SMEMBERS key`
- **Use cases:** Caching, sessions, rate limiting, leaderboards, real-time data.

### Real commands I ran
- `redis-server &`
- `redis-cli ping` → `PONG`
- `redis-cli SET user:1:name "Felix"` → `OK`
- `redis-cli GET user:1:name` → `"Felix"`
- `redis-cli RPUSH mylist "first"` → `(integer) 1`
- `redis-cli LRANGE mylist 0 -1` → `1) "first" 2) "second" 3) "third"`
- `redis-cli HSET user:1 name "Felix" role "hacker" age 25`
- `redis-cli HGETALL user:1` → name: Felix, role: hacker, age: 25

### Things I saw
- Redis 8.10.2 running on port 6379.
- `PONG` confirmed the server was alive.
- Strings, lists, and hashes all worked.
- Redis is **much faster** than SQL (no table creation, no schema).

### My own words (locked in)
- SQL = tables, rows, columns. Strict. Good for money.
- NoSQL = flexible. Good for chat, feeds, caches.
- MongoDB = documents (JSON). Flexible schema.
- Redis = key-value. In-memory. Ultra-fast.
- Use SQL for ACID (banking, inventory).
- Use NoSQL for speed and flexibility (chat, social, caching).
- Redis has strings, lists, hashes, sets.
- Redis is used for caching, sessions, rate limiting.
- Big companies use BOTH. Instagram used PostgreSQL + Cassandra.
- The `1.2000000000000002` float bug from SQL would not happen in Redis (it uses strings for numbers).

### Connection to other topics
- 6.1 (Databases) — the SQL foundation.
- 6.2 (SQL Basics) — SELECT, WHERE.
- 6.3 (Joins, Indexes, Transactions) — SQL power.
- 5.13 (Caching with Redis) — the practical use case.
- 7.6 (Docker) — Redis runs in a container.
- 8.5 (Network Security) — Redis has no auth by default (we saw the warning!).
- 12.15 (Web Hacking) — Redis misconfigurations can be exploited.

## 6.8 Caching Layer (Redis) — Phase B DONE ✅

Added Redis caching to a fake product endpoint.
Saw the difference between a cache miss (536ms) and a cache hit (8ms).

### Core concepts
- **Caching** = storing expensive results in a fast place.
- **Cache hit** = data found in cache (fast).
- **Cache miss** = data not in cache (query the DB).
- **TTL** = Time To Live. The cache expires after a time.
- **Cache invalidation** = the hardest problem (keeping cache in sync with the DB).

### The 3 caching patterns
1. **Cache-Aside (Lazy Loading):** Check cache, if miss query DB, store in cache.
2. **Write-Through:** Write to cache and DB at the same time.
3. **Write-Behind:** Write to cache only, flush to DB later.

### What to cache
- ✅ Product lists, user profiles, search results (rarely change).
- ❌ Live prices, bank balances, OTPs (must be accurate).

### Real commands I ran
- `redis-cli ping` → `PONG`
- `npm install redis`
- `node cache-test.js`

### Things I saw
- Request 1 (miss): 536ms.
- Request 2 (hit): 7.93ms.
- Request 3 (hit): 10.53ms.
- The cache hit was ~50× faster than the miss.
- The error `Socket already opened` taught me to connect once.

### My own words (locked in)
- Caching = the pre-made coffee on the counter.
- Cache hit = fast. Cache miss = slow.
- TTL = expiry time.
- Cache invalidation is the hard problem.
- Redis is the standard cache (in-memory, fast).
- The database load drops by 99.9%.
- Never cache live prices or bank balances.
- Connect to Redis once, not on every request.
- `setEx` = set with expiry.
- `get` = read from cache.
- `client.connect()` must happen once, before the requests.

### Connection to other topics
- 6.4 (NoSQL/Redis) — the basics of Redis.
- 6.2 (SQL) — what we're caching.
- 5.13 (Caching — future) — the backend version.
- 7.6 (Docker) — Redis runs in a container.
- 7.7 (Docker Compose) — Redis + app + Nginx.
- 8.9 (Rate Limiting) — Redis is used for rate limit counters.
- 12.20 (SIEM) — Redis can store SIEM state.
- 7.12 (Monitoring) — cache hit/miss ratio is a key metric.

