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

## 6.9 Search (Full-text) — Phase B DONE ✅

Used SQLite FTS5 to search pos-lab's products.
Compared `LIKE '%milk%'` (4ms) vs FTS `MATCH 'milk'` (2ms) on 5 rows.

### Core concepts
- **Full-text search (FTS)** = searching for words inside large text efficiently.
- **LIKE '%...%'** = full table scan. Slow on large tables. No index.
- **FTS** = uses an inverted index. Fast. Supports relevance ranking.
- **Inverted index** = map of every word → the rows that contain it.
- **FTS5** = SQLite's built-in full-text search engine.
- **Tokenization** = splitting text into words.
- **BM25** = relevance ranking algorithm (how relevant is each result?).

### What FTS gives you
- Fast search on large text.
- Relevance ranking (BM25).
- Phrase search (`"fresh milk"`).
- Prefix search (`milk*`).
- Boolean search (`milk AND bread`).

### The tools
- SQLite FTS5 (built-in).
- PostgreSQL `tsvector` (built-in).
- Elasticsearch (industry standard).
- Meilisearch (simpler, fast).
- Algolia (cloud search).

### Real commands I ran
- `SELECT name FROM sqlite_master WHERE type='table' AND name LIKE '%fts%'` → found `products_fts`.
- `SELECT name, description FROM products_fts WHERE products_fts MATCH 'milk'` → returned Milk 1L.
- Timed both approaches: LIKE 4ms, FTS 2ms (on 5 rows).

### Things I saw
- pos-lab has `products_fts` (and 4 internal FTS tables).
- FTS query returned the same result as LIKE.
- With 5 rows, both are fast.
- With 1 million rows, FTS would be ~2,500× faster.
- The LIKE query failed at first because I used `price` instead of `base_price` (schema mistake).

### My own words (locked in)
- FTS = the index at the back of the book.
- LIKE = reading every page.
- FTS uses an inverted index (word → rows).
- FTS is fast on large tables.
- LIKE is slow on large tables.
- FTS supports relevance ranking (BM25).
- FTS supports phrase, prefix, and boolean search.
- SQLite FTS5 is built-in.
- Elasticsearch is the industry standard.
- Google uses a custom FTS system.
- FTS is why search engines are fast.

### Connection to other topics
- 6.2 (SQL) — the LIKE clause.
- 6.3 (Indexes) — FTS uses a special index.
- 6.4 (NoSQL) — Elasticsearch is a NoSQL search engine.
- 6.10 (DB Performance) — FTS is a performance optimization.
- 8.10 (Secure API) — search endpoints need validation.
- 12.15 (Web Hacking) — SQL injection in search (`' OR 1=1`).
- 6.8 (Caching) — search results can be cached.

## 6.5 ORMs — Phase B DONE ✅

Learned why ORMs exist by breaking raw SQL first.
Then proved it with a real SQLAlchemy drill: renamed a column
in one place and nothing else broke.

### Core concepts
- **ORM** = Object-Relational Mapping. A translator between Python and SQL.
- Python **class** ↔ DB **table**
- Python **object** ↔ DB **row**
- Python **attribute** ↔ DB **column**
- You write Python. The ORM generates the SQL and returns objects.
- Main Python ORMs: **SQLAlchemy** (Flask/FastAPI), **Django ORM** (Django).
- Other stacks: Prisma/Sequelize (Node), Hibernate (Java), EF (.NET).

### The problem it solves
- Raw SQL strings are scattered across the codebase.
- Rename a column → every `SELECT`, `INSERT`, `WHERE` using the old name breaks.
- The error is runtime, not compile-time: `sqlite3.OperationalError: no such column: fullname`.
- ORM keeps the column name in ONE place (the class). Rename = edit one line.

### The drill (what I actually ran)
- `pip install sqlalchemy` → 2.1.2
- Defined `class User(Base)` with `__tablename__ = "users"` and `fullname: Mapped[str]`
- `engine = create_engine("sqlite:///drill.db")`
- `Base.metadata.create_all(engine)` → created the table
- `session.add(User(id=1, fullname="Felix"))` + `session.commit()` → INSERT
- `session.get(User, 1)` → SELECT by primary key → printed `found: Felix`
- Renamed `fullname` → `name` in the class + its two references
- `rm drill.db && python3 orm_drill.py` → `table created` / `found: Felix` again
- No SQL written. The ORM generated all of it.

### Things I saw
- The raw-SQL version (6.2-style) crashed instantly on the renamed column.
- The ORM version survived the rename after editing **2 lines**.
- `no such column` is the raw-SQL pain — a runtime error, only found when the code runs.
- In Python, a wrong attribute name would be an `AttributeError` at my desk, not 2am in prod.
- The SQLAlchemy class IS the schema — one source of truth.

### My own words (locked in)
- ORM = conductor between me (Python) and the driver (database).
- I speak Python. The ORM speaks SQL for me.
- Tables become classes. Rows become objects. Columns become attributes.
- The column name lives in one place, not scattered in strings.
- Saves time, but the bigger win is **one source of truth**.
- Raw SQL still matters — ORMs generate SQL, so I need to read it.
- ORMs are not magic. They can produce slow queries if misused (N+1, no index).
- The column rename "crushes" everywhere the old name appears — that's the pain the ORM removes.

### Connection to other topics
- 6.1 (Databases) — tables and columns the ORM maps.
- 6.2 (SQL Basics) — the SQL the ORM generates (you still need to read it).
- 6.3 (Joins) — ORM relationships hide the JOIN (`User.sales`).
- 5.2 (Flask) — SQLAlchemy is the natural ORM there.
- 5.3 (Django) — Django ORM is built-in.
- 6.6 (DB Design) — the schema the ORM maps to.
- 6.7 (Migrations) — ORMs pair with migration tools (Alembic, Django migrations).
- 6.10 (DB Performance) — ORMs can hide N+1 queries if you don't watch them.

## EXPLAIN QUERY PLAN — index experiment

### Before index
SELECT * FROM products WHERE base_price < 100;
QUERY PLAN
`--SCAN products

→ DB reads every row to find matches. Work grows with table size.

### After index
CREATE INDEX idx_products_base_price ON products(base_price);
SELECT * FROM products WHERE base_price < 100;
QUERY PLAN
`--SEARCH products USING INDEX idx_products_base_price (base_price<?)

→ DB uses the index (catalogue), jumps to matching rows.

### Different query, different plan
UPDATE products SET base_price = 99 WHERE id = 1;
QUERY PLAN
`--SEARCH products USING INTEGER PRIMARY KEY (rowid=?)

→ base_price index NOT used. Query filtered by id → primary key index used.
→ An index helps only queries that match its column.

### Lesson
- SCAN = full table read (slow on big tables).
- SEARCH USING INDEX = index lookup (fast).
- Index costs: slower writes, more disk.
- EXPLAIN QUERY PLAN = the tool that shows the plan.
## 6.10 DB Performance — Phase B DONE ✅

Used EXPLAIN QUERY PLAN to see how SQLite finds rows.
Proved an index changes SCAN → SEARCH, and that it only helps matching queries.

### Core concepts
- **Performance = the plan, not the size.** Big table + good index = fast.
- **`SCAN`** = full table read. Reads every row. Slow on large tables.
- **`SEARCH ... USING INDEX`** = index lookup. Jumps to matches. Fast.
- **`EXPLAIN QUERY PLAN`** = the DB's own report of how it will run a query.
- **Index trade-off:** faster reads, slower writes, more disk.
- **Index selectivity:** an index helps only when the query filters/sorts/joins on that column.
- **N+1 queries:** an ORM trap — one query per row in a loop. Fix with JOINs or eager loading.
- **Pagination:** `LIMIT`/`OFFSET` keeps large result sets manageable.
- **Slow query log:** DB feature that records slow queries for review.
- **Connection pooling:** reuse DB connections instead of opening one per request.

### The drill (what I actually ran)
- `EXPLAIN QUERY PLAN SELECT * FROM products WHERE base_price < 100;` → `SCAN products`
- `CREATE INDEX idx_products_base_price ON products(base_price);`
- Re-ran same query → `SEARCH products USING INDEX idx_products_base_price (base_price<?)`
- `EXPLAIN QUERY PLAN UPDATE products SET base_price = 99 WHERE id = 1;` → `SEARCH products USING INTEGER PRIMARY KEY (rowid=?)` — base_price index NOT used

### Things I saw
- Same query, same data — different plan after the index.
- The plan changed because the query matched the indexed column.
- The UPDATE by `id` ignored the new index and used the primary key.
- SCAN on 5 rows feels fine; on 500k rows it's the whole problem.

### My own words (locked in)
- SCAN = DB reads every row. SEARCH = DB uses the index (catalogue) to jump to matches.
- An index helps only queries that match its column.
- An index speeds up reads but slows down writes and takes disk space.
- EXPLAIN QUERY PLAN is the tool that shows the plan — SCAN bad, SEARCH good.
- Size doesn't matter as much as the plan.
- Index what you filter/join/sort by — not everything.

### Connection to other topics
- 6.1 (Databases) — tables, rows, columns.
- 6.2 (SQL Basics) — the queries being optimized.
- 6.3 (Indexes) — same concept, deeper here.
- 6.5 (ORMs) — ORMs hide queries; N+1 is an ORM performance trap.
- 6.8 (Caching) — cache hits reduce DB load.
- 6.9 (FTS) — FTS uses a special index (inverted index).
- 7.12 (Monitoring) — slow query logs feed into monitoring.
- 12.15 (Web Hacking) — SQL injection can exploit missing input validation, separate from performance.


## Bad design drill — update anomaly

### Bad table (one big table)
CREATE TABLE sales_bad (
  sale_id INTEGER PRIMARY KEY,
  product_name TEXT, product_price REAL,
  seller_name TEXT, seller_phone TEXT,
  qty INTEGER, total REAL
);
INSERT: (1,Bread,60,Sam,0712,2,120), (2,Bread,60,Mary,0723,1,60), (3,Milk,75,Sam,0712,3,225)

### Mistake: update only ONE row
UPDATE sales_bad SET product_price = 70 WHERE sale_id = 1;
SELECT * FROM sales_bad;

Output:
sale_id 1: Bread 70.0  Sam
sale_id 2: Bread 60.0  Mary   ← stale
sale_id 3: Milk  75.0  Sam

→ Same product, two prices. DB is now lying.
→ Bonus: sale 1 total=120 but 2×70=140. total is stale too.

### Why it happened
- product_price and seller_phone were repeated in every sale row.
- One fact, many places → update anomaly.
- seller_phone depends on seller_name, not on sale_id (transitive dependency → breaks 3NF).

### The fix
Split into 3 tables:
- products (id, name, price) — stored once
- sellers  (id, name, phone) — stored once
- sales    (id, product_id, seller_id, qty, total) — facts only, FKs to the other two

→ Price change = update one row in products.
→ Phone change = update one row in sellers.
→ No duplicates, no anomalies.

### Lesson
- Redundancy → update anomalies.
- Normalization = every fact in one place.
- Denormalization = deliberate duplicate for speed, needs a sync plan.

## 6.6 Database Design & Normalization — Phase B DONE ✅

Built a deliberately bad one-table design, triggered an update anomaly,
then split it into three normalized tables.

### Core concepts
- **Normalization** = organizing data so each fact lives in exactly one place.
- **Redundancy** = repeating data → risk of inconsistency.
- **Update anomaly** = changing one row but not the others → DB lies.
- **Insert anomaly** = can't add a fact without a related fact (e.g. a product with no sale).
- **Delete anomaly** = deleting one fact wipes unrelated facts with it.

### The three normal forms (plain English)
| Form | Rule | In words |
|------|------|----------|
| **1NF** | No repeating groups | Each cell holds one value |
| **2NF** | 1NF + no partial dependency | Every non-key column depends on the whole key |
| **3NF** | 2NF + no transitive dependency | Non-key columns depend on the key, not on each other |

### Relationships
- **1:1** — one row ↔ one row (user ↔ profile)
- **1:N** — one row ↔ many rows (seller ↔ sales)
- **M:N** — many ↔ many, via a **junction table** (products ↔ sales, if a sale can have many products)

### Denormalization
- Deliberately duplicating data for **speed**.
- Examples: cached `total`, `products_fts` (6.9), materialized views.
- Requires a **sync plan** (triggers, jobs, cache invalidation).
- Otherwise: the DB starts lying again.

### The drill (what I actually ran)
- Created `sales_bad` (one table, repeated product_price + seller_phone)
- Inserted 3 rows
- Updated ONLY row 1's price: 60 → 70
- Query showed Bread @ 70 and Bread @ 60 — contradictory
- `total` was also stale (2 × 70 = 140, but stored 120)
- Designed the 3-table fix: products, sellers, sales with FKs

### Things I saw
- One missed update = two truths in one table.
- The `total` column depends on `product_price` — if price changes, total must too.
- seller_phone depends on seller, not on the sale → transitive dependency.
- The fix is not "update harder" — it's "store once."

### My own words (locked in)
- Update anomaly = two Breads at different prices, from one missed update.
- Redundancy = same fact stored many times.
- Normalization = every fact lives in one place only.
- Fix = split the table, link with foreign keys.
- Denormalization = duplicate on purpose for speed — but keep copies in sync.
- 3NF rule of thumb: non-key columns must depend on the key, not on each other.

### Connection to other topics
- 6.1 (Databases) — tables, rows, columns, keys.
- 6.2 (SQL Basics) — the queries that exposed the anomaly.
- 6.3 (Joins) — how the 3 tables are combined.
- 6.5 (ORMs) — ORM classes map to normalized tables.
- 6.7 (Backups & Migrations) — schema changes happen via migrations.
- 6.8 (Caching) — denormalization is a form of caching at the DB layer.
- 6.9 (FTS) — `products_fts` is denormalized on purpose.
- 6.10 (DB Performance) — denormalization trades consistency for speed.

### Rule of thumb
"Every fact in one place, and only one place."y
