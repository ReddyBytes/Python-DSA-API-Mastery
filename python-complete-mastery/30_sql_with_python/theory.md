# 🗄️ SQL with Python

---

Your ML pipeline trains on CSVs today.

In production, that data lives in a database. User events, product metadata, model predictions, feature stores — all of it is in PostgreSQL, MySQL, or SQLite, not flat files on disk.

The engineer who can't query SQL can't debug their own data. And 80% of bugs are data bugs: wrong joins, missing rows, bad filters, stale records. If you can only load a CSV and hope it's right, you're flying blind.

This module teaches you how Python talks to databases — from the standard library's `sqlite3` all the way to SQLAlchemy's ORM, pandas integration, and DuckDB for modern analytics workflows.

---

## 📌 Learning Priority

**Must Learn** — Core concept, daily use, interview essential:
`sqlite3` basics · cursor/execute/fetchall · parameterized queries · CRUD operations · SQL: SELECT/WHERE/JOIN · `pd.read_sql()` · SQLAlchemy engine + session

**Should Learn** — Important for real projects, comes up regularly:
SQLAlchemy ORM + declarative models · `df.to_sql()` · GROUP BY / HAVING · subqueries · transactions · indexes

**Good to Know** — Useful in specific situations:
DuckDB · connection pooling · ACID properties in depth · EXPLAIN/query planning · full-text search

**Reference** — Know it exists, look up when needed:
Alembic migrations · async SQLAlchemy · geospatial extensions · partitioning strategies

---

## 1️⃣ The sqlite3 Module

`sqlite3` ships with Python. No install needed. It stores your entire database in a single `.db` file on disk — perfect for prototypes, scripts, and learning.

Think of it as a filing cabinet in a single drawer. Not for 100 concurrent writers, but perfect for one engineer querying data locally.

**The three objects you always use:**

```python
import sqlite3

# 1. Connection — opens (or creates) the .db file
conn = sqlite3.connect("analytics.db")  # ← creates file if it doesn't exist

# 2. Cursor — the "hand" that executes SQL
cursor = conn.cursor()

# 3. Execute SQL
cursor.execute("CREATE TABLE IF NOT EXISTS users (id INTEGER PRIMARY KEY, name TEXT, age INTEGER)")

# 4. Commit writes — without this, changes are lost
conn.commit()

# 5. Close when done
conn.close()
```

**The context manager pattern — always prefer this:**

```python
import sqlite3

with sqlite3.connect("analytics.db") as conn:  # ← auto-closes on exit
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM users")
    rows = cursor.fetchall()  # ← returns list of tuples
    print(rows)
# conn.close() is called automatically here
```

**fetchall vs fetchone:**

```python
with sqlite3.connect("analytics.db") as conn:
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM users")

    one = cursor.fetchone()   # ← returns single tuple or None
    all_rows = cursor.fetchall()  # ← returns list of all tuples
    
    # Iterate directly — memory-efficient for large results
    for row in cursor.execute("SELECT * FROM users"):
        print(row)  # (1, 'Alice', 30)
```

**Row factory — get dicts instead of tuples:**

```python
conn = sqlite3.connect("analytics.db")
conn.row_factory = sqlite3.Row  # ← magic line

cursor = conn.cursor()
cursor.execute("SELECT * FROM users WHERE id = 1")
row = cursor.fetchone()

print(row["name"])  # ← access by column name, not index
print(row["age"])
```

---

## 2️⃣ CRUD Operations

**CRUD** is the four operations every database does: Create, Read, Update, Delete.

**CREATE TABLE:**

```python
import sqlite3

with sqlite3.connect("analytics.db") as conn:
    conn.execute("""
        CREATE TABLE IF NOT EXISTS products (
            id       INTEGER PRIMARY KEY AUTOINCREMENT,  -- ← auto-incrementing ID
            name     TEXT    NOT NULL,
            price    REAL    NOT NULL,
            category TEXT    DEFAULT 'uncategorized',
            created  TEXT    DEFAULT CURRENT_TIMESTAMP
        )
    """)
    conn.commit()
```

**INSERT — single row:**

```python
with sqlite3.connect("analytics.db") as conn:
    conn.execute(
        "INSERT INTO products (name, price, category) VALUES (?, ?, ?)",
        ("MacBook Pro", 2499.99, "laptops")  # ← parameterized — safe!
    )
    conn.commit()
```

**INSERT — many rows at once:**

```python
products = [
    ("iPad", 799.99, "tablets"),
    ("iPhone", 999.99, "phones"),
    ("AirPods", 249.99, "audio"),
]

with sqlite3.connect("analytics.db") as conn:
    conn.executemany(
        "INSERT INTO products (name, price, category) VALUES (?, ?, ?)",
        products  # ← inserts all rows in one call
    )
    conn.commit()
```

**SELECT — read rows:**

```python
with sqlite3.connect("analytics.db") as conn:
    cursor = conn.execute("SELECT id, name, price FROM products ORDER BY price DESC")
    for row in cursor:
        print(f"  {row[0]}: {row[1]} — ${row[2]:.2f}")
```

**UPDATE — modify existing rows:**

```python
with sqlite3.connect("analytics.db") as conn:
    conn.execute(
        "UPDATE products SET price = ? WHERE name = ?",
        (1999.99, "MacBook Pro")  # ← always parameterized for safety
    )
    conn.commit()
    print(f"Rows changed: {conn.total_changes}")
```

**DELETE — remove rows:**

```python
with sqlite3.connect("analytics.db") as conn:
    conn.execute("DELETE FROM products WHERE price < ?", (100.0,))
    conn.commit()
```

---

## 3️⃣ SQL Query Patterns

**WHERE — filter rows:**

```python
with sqlite3.connect("analytics.db") as conn:
    # Single condition
    rows = conn.execute("SELECT * FROM products WHERE category = ?", ("laptops",)).fetchall()

    # Multiple conditions
    rows = conn.execute(
        "SELECT * FROM products WHERE category = ? AND price < ?",
        ("laptops", 2000.0)
    ).fetchall()

    # IN clause
    rows = conn.execute(
        "SELECT * FROM products WHERE category IN (?, ?)",
        ("laptops", "tablets")
    ).fetchall()

    # LIKE — pattern matching
    rows = conn.execute(
        "SELECT * FROM products WHERE name LIKE ?", ("%Pro%",)
    ).fetchall()
```

**ORDER BY and LIMIT:**

```python
with sqlite3.connect("analytics.db") as conn:
    # Top 3 most expensive
    rows = conn.execute(
        "SELECT name, price FROM products ORDER BY price DESC LIMIT 3"
    ).fetchall()

    # Pagination: skip first 10, return next 10
    rows = conn.execute(
        "SELECT * FROM products ORDER BY id LIMIT 10 OFFSET 10"
    ).fetchall()
```

**GROUP BY and HAVING — aggregation:**

```python
with sqlite3.connect("analytics.db") as conn:
    # Count products per category
    rows = conn.execute("""
        SELECT category, COUNT(*) AS count, AVG(price) AS avg_price
        FROM products
        GROUP BY category
        ORDER BY count DESC
    """).fetchall()

    for row in rows:
        print(f"  {row[0]}: {row[1]} products, avg ${row[2]:.2f}")

    # HAVING — filter on aggregated values (WHERE runs before aggregation, HAVING after)
    rows = conn.execute("""
        SELECT category, COUNT(*) AS count
        FROM products
        GROUP BY category
        HAVING count > 2  -- ← filters groups, not individual rows
    """).fetchall()
```

**Subqueries:**

```python
with sqlite3.connect("analytics.db") as conn:
    # Products that cost more than the average price
    rows = conn.execute("""
        SELECT name, price
        FROM products
        WHERE price > (SELECT AVG(price) FROM products)  -- ← subquery runs first
        ORDER BY price DESC
    """).fetchall()

    # Find categories that have expensive items
    rows = conn.execute("""
        SELECT DISTINCT category
        FROM products
        WHERE id IN (
            SELECT id FROM products WHERE price > 500
        )
    """).fetchall()
```

---

## 4️⃣ Parameterized Queries — Why They Matter

**SQL injection** is one of the most common security vulnerabilities in history. It happens when user input is concatenated directly into a SQL string.

**The dangerous way — never do this:**

```python
# Imagine `user_input` comes from an HTTP request
user_input = "'; DROP TABLE products; --"

# This destroys your database
query = f"SELECT * FROM products WHERE name = '{user_input}'"
conn.execute(query)  # ← CATASTROPHIC
```

**The safe way — parameterized queries:**

```python
# The ? placeholder tells sqlite3: "substitute this value safely"
# sqlite3 escapes the input, so it can never break out of the string context
conn.execute(
    "SELECT * FROM products WHERE name = ?",
    (user_input,)  # ← safely escaped, no injection possible
)
```

**Why `?` works:** sqlite3 sends the SQL and the parameters separately to the database engine. The engine never interprets the parameter as SQL code — it's always treated as a plain value.

For SQLAlchemy and other libraries, the placeholder syntax differs:
- sqlite3: `?`
- SQLAlchemy / psycopg2: `:name` or `%(name)s`

---

## 5️⃣ JOINs — Combining Tables

A **JOIN** lets you combine rows from two tables based on a matching condition. Understanding joins is the single most important SQL skill.

Let's set up two tables: `orders` and `customers`.

```
customers table:         orders table:
+----+--------+          +----+--------+-------------+
| id | name   |          | id | cust_id| product     |
+----+--------+          +----+--------+-------------+
|  1 | Alice  |          |  1 |      1 | MacBook     |
|  2 | Bob    |          |  2 |      1 | iPad        |
|  3 | Carol  |          |  3 |      2 | AirPods     |
|  4 | Dave   |          |  4 |      9 | Mystery     |  ← cust_id 9 doesn't exist
+----+--------+          +----+--------+-------------+
```

**INNER JOIN — only rows that match in BOTH tables:**

```
        customers      orders
        +------+      +------+
        |  1   |      |  1   |
        |  2   |  ∩   |  2   |  ← only overlapping rows
        |  3   |      |  3   |
        |  4   |      +------+
        +------+
        Result: customers 1, 2 with their orders
```

```python
rows = conn.execute("""
    SELECT customers.name, orders.product
    FROM customers
    INNER JOIN orders ON customers.id = orders.cust_id
    -- ← rows with no match in either table are excluded
""").fetchall()
# ('Alice', 'MacBook'), ('Alice', 'iPad'), ('Bob', 'AirPods')
# Dave is excluded (no orders), Mystery order is excluded (no customer)
```

**LEFT JOIN — all rows from the LEFT table, match or not:**

```
        customers      orders
        +------+      +------+
        |  1   |  ←   |  1   |
        |  2   |  ←   |  2   |
        |  3   |  ←   |      |  ← Carol has no orders: NULL in order columns
        |  4   |  ←   |      |  ← Dave has no orders: NULL
        +------+      +------+
        Result: all customers, NULLs where no order exists
```

```python
rows = conn.execute("""
    SELECT customers.name, orders.product
    FROM customers
    LEFT JOIN orders ON customers.id = orders.cust_id
    -- ← all customers appear, even those with no orders
""").fetchall()
# ('Alice', 'MacBook'), ('Alice', 'iPad'), ('Bob', 'AirPods'),
# ('Carol', None), ('Dave', None)  ← NULLs for customers with no orders
```

**RIGHT JOIN — all rows from the RIGHT table:**
*(sqlite3 doesn't support RIGHT JOIN natively — swap table order and use LEFT JOIN instead)*

```python
# Equivalent to RIGHT JOIN in standard SQL:
rows = conn.execute("""
    SELECT customers.name, orders.product
    FROM orders
    LEFT JOIN customers ON customers.id = orders.cust_id
    -- ← all orders appear, even the one with no matching customer
""").fetchall()
# ('Alice', 'MacBook'), ('Alice', 'iPad'), ('Bob', 'AirPods'),
# (None, 'Mystery')  ← order with unknown customer
```

**FULL OUTER JOIN — all rows from BOTH tables:**

```
        customers      orders
        +------+      +------+
        |  1   |  ↔   |  1   |
        |  2   |  ↔   |  2   |
        |  3   |  →   |      |  ← Carol, no order (NULL right)
        |  4   |  →   |      |  ← Dave, no order (NULL right)
        |      |  ←   |  4   |  ← Mystery order, no customer (NULL left)
        +------+      +------+
        Result: everything from both sides
```

```python
# sqlite3 doesn't have FULL OUTER JOIN — simulate with UNION:
rows = conn.execute("""
    SELECT customers.name, orders.product
    FROM customers
    LEFT JOIN orders ON customers.id = orders.cust_id

    UNION ALL

    SELECT customers.name, orders.product
    FROM orders
    LEFT JOIN customers ON customers.id = orders.cust_id
    WHERE customers.id IS NULL
""").fetchall()
```

**JOIN summary:**

```
INNER JOIN  →  only matched rows (intersection)
LEFT JOIN   →  all left rows + matched right (left wins)
RIGHT JOIN  →  all right rows + matched left (right wins)
FULL OUTER  →  everything from both (union)
```

---

## 6️⃣ SQLAlchemy — Core vs ORM

**sqlite3** is low-level. You write raw SQL strings. Fine for scripts.

In production applications, you want:
- **Portability** — swap PostgreSQL for MySQL without rewriting SQL
- **Safety** — objects, not raw strings
- **Abstraction** — define your schema in Python, not SQL dialects

**SQLAlchemy** solves all of this. It has two layers:

```
SQLAlchemy ORM
    ↑  (Python objects ↔ database rows)
SQLAlchemy Core
    ↑  (SQL expression language — safer than raw strings)
Database driver (psycopg2, sqlite3, pymysql...)
    ↑
Database (PostgreSQL, SQLite, MySQL...)
```

**Core — SQL expression language:**

```python
from sqlalchemy import create_engine, text

# Engine = connection factory (not a connection itself)
engine = create_engine("sqlite:///analytics.db", echo=True)  # ← echo=True logs SQL

# Execute raw SQL safely via Core
with engine.connect() as conn:
    result = conn.execute(text("SELECT * FROM products WHERE price > :min_price"),
                          {"min_price": 500})  # ← named params, not ?
    for row in result:
        print(row)
```

**ORM — Python classes as database tables:**

```python
from sqlalchemy import create_engine, Column, Integer, String, Float
from sqlalchemy.orm import DeclarativeBase, Session

engine = create_engine("sqlite:///analytics.db")

# 1. Define base class
class Base(DeclarativeBase):
    pass

# 2. Map a Python class to a table
class Product(Base):
    __tablename__ = "products"  # ← exact table name in DB

    id       = Column(Integer, primary_key=True, autoincrement=True)
    name     = Column(String, nullable=False)
    price    = Column(Float, nullable=False)
    category = Column(String, default="uncategorized")

    def __repr__(self):
        return f"<Product(name={self.name!r}, price={self.price})>"

# 3. Create tables if they don't exist
Base.metadata.create_all(engine)

# 4. Insert rows via ORM
with Session(engine) as session:
    p1 = Product(name="MacBook Pro", price=2499.99, category="laptops")  # ← Python object
    p2 = Product(name="AirPods", price=249.99, category="audio")

    session.add(p1)
    session.add_all([p2])  # ← add multiple at once
    session.commit()       # ← persists to database

# 5. Query
with Session(engine) as session:
    # All products
    all_products = session.query(Product).all()

    # Filtered
    laptops = session.query(Product).filter(Product.category == "laptops").all()

    # Ordered, limited
    top3 = session.query(Product).order_by(Product.price.desc()).limit(3).all()

    for p in top3:
        print(p.name, p.price)

# 6. Update
with Session(engine) as session:
    product = session.query(Product).filter(Product.name == "MacBook Pro").first()
    product.price = 1999.99  # ← just modify the attribute
    session.commit()          # ← SQLAlchemy detects the change and issues UPDATE

# 7. Delete
with Session(engine) as session:
    product = session.query(Product).filter(Product.id == 1).first()
    session.delete(product)
    session.commit()
```

**When to use Core vs ORM:**

- **Core**: data pipelines, ETL, analytics queries, bulk inserts. You want control.
- **ORM**: web applications, REST APIs, when you're working with related objects.

---

## 7️⃣ Pandas + SQL — Bidirectional Data Flow

**Pandas** and **SQL** are natural partners. Pandas lives in memory; SQL lives on disk. You move data between them constantly.

**pd.read_sql() — database → DataFrame:**

```python
import pandas as pd
import sqlite3

conn = sqlite3.connect("analytics.db")

# Simple query → DataFrame
df = pd.read_sql("SELECT * FROM products", conn)  # ← full table
print(df.head())

# Filtered query → DataFrame
df = pd.read_sql(
    "SELECT name, price FROM products WHERE category = ?",
    conn,
    params=("laptops",)  # ← parameterized even through pandas
)

# With SQLAlchemy engine (preferred for production)
from sqlalchemy import create_engine
engine = create_engine("sqlite:///analytics.db")

df = pd.read_sql("SELECT * FROM products ORDER BY price DESC", engine)
df = pd.read_sql_table("products", engine)  # ← entire table, no SQL needed

conn.close()
```

**df.to_sql() — DataFrame → database:**

```python
import pandas as pd
from sqlalchemy import create_engine

# Example: load a CSV and push to database
df = pd.read_csv("sales_data.csv")

engine = create_engine("sqlite:///analytics.db")

df.to_sql(
    name="sales",         # ← table name
    con=engine,
    if_exists="replace",  # ← "replace" | "append" | "fail"
    index=False,          # ← don't write the DataFrame index as a column
    chunksize=1000        # ← write in batches (important for large DataFrames)
)

print("Saved to database.")
```

**Round-trip pattern — the most common workflow:**

```python
import pandas as pd
from sqlalchemy import create_engine

engine = create_engine("postgresql://user:pass@localhost/mydb")

# Pull data, transform, push back
df = pd.read_sql("SELECT * FROM raw_events WHERE date >= '2024-01-01'", engine)

# Transform in pandas
df["revenue"] = df["quantity"] * df["unit_price"]
df_agg = df.groupby("product_id")["revenue"].sum().reset_index()

# Write aggregated results back to DB
df_agg.to_sql("daily_revenue", engine, if_exists="append", index=False)
```

---

## 8️⃣ DuckDB — Modern In-Process Analytics

**DuckDB** is what SQLite would be if it was built for data analytics instead of transactional apps.

Imagine SQLite and pandas had a child: you get an embedded database that runs SQL directly on DataFrames, Parquet files, and CSVs without loading everything into memory first.

Why it matters for data science and ML:
- **Zero setup** — embedded, no server process
- **Columnar storage** — fast for analytical queries (GROUP BY, aggregations)
- **Runs SQL on DataFrames** — no need to write data to a file first
- **Parquet-native** — reads `.parquet` files directly with SQL

```python
import duckdb
import pandas as pd

# Create an in-memory database
con = duckdb.connect()  # ← in-memory
# con = duckdb.connect("analytics.duckdb")  # ← persists to file

# Query a Parquet file directly — no loading needed
result = con.execute("""
    SELECT category, SUM(price) AS total
    FROM read_parquet('sales_data.parquet')
    GROUP BY category
    ORDER BY total DESC
""").df()  # ← .df() returns a pandas DataFrame

print(result)

# Query a DataFrame directly — this is DuckDB's killer feature
df = pd.DataFrame({
    "name": ["MacBook", "iPad", "AirPods"],
    "price": [2499.99, 799.99, 249.99],
    "category": ["laptops", "tablets", "audio"]
})

# SQL on the in-memory DataFrame — no intermediate steps
result = con.execute("""
    SELECT category, AVG(price) AS avg_price
    FROM df  -- ← references the Python variable df directly
    GROUP BY category
""").df()

print(result)

# Query a CSV directly — DuckDB auto-infers schema
result = con.execute("""
    SELECT *
    FROM read_csv_auto('large_data.csv')
    WHERE amount > 1000
    LIMIT 100
""").df()
```

**DuckDB vs sqlite3 vs SQLAlchemy:**

```
sqlite3       →  transactional apps, small data, no extra deps
SQLAlchemy    →  production apps, ORM, multi-database portability
DuckDB        →  analytics, DataFrames, Parquet, OLAP workloads
```

DuckDB is increasingly used in ML pipelines: run feature engineering SQL on Parquet files before training, validate data without spinning up a full database server.

---

## 9️⃣ Transactions and ACID

A **transaction** is a group of operations that either all succeed or all fail together. If your process crashes halfway, the database rolls back to its previous clean state.

**ACID** properties guarantee this:

| Property | Meaning | Example |
|---|---|---|
| **Atomicity** | All-or-nothing | Transfer $100: debit AND credit both succeed, or neither does |
| **Consistency** | No constraint violations | Can't have a negative balance if that's a rule |
| **Isolation** | Concurrent transactions don't interfere | Two users buying the last item — only one wins |
| **Durability** | Committed data survives crashes | Power outage after commit: data still there |

**Using transactions explicitly:**

```python
import sqlite3

conn = sqlite3.connect("bank.db")
try:
    conn.execute("BEGIN TRANSACTION")  # ← explicit transaction start

    conn.execute("UPDATE accounts SET balance = balance - 100 WHERE id = ?", (1,))
    conn.execute("UPDATE accounts SET balance = balance + 100 WHERE id = ?", (2,))

    conn.execute("COMMIT")  # ← all changes persist atomically
    print("Transfer complete.")

except Exception as e:
    conn.execute("ROLLBACK")  # ← undo everything if anything failed
    print(f"Transfer failed, rolled back: {e}")

finally:
    conn.close()
```

**With SQLAlchemy (preferred pattern):**

```python
from sqlalchemy.orm import Session

with Session(engine) as session:
    try:
        session.execute(text("UPDATE accounts SET balance = balance - 100 WHERE id = 1"))
        session.execute(text("UPDATE accounts SET balance = balance + 100 WHERE id = 2"))
        session.commit()   # ← if anything raises before this, nothing is committed
    except Exception:
        session.rollback()
        raise
```

The `with Session(engine) as session:` block rolls back automatically on unhandled exceptions.

---

## 🔟 Indexes and Performance

An **index** is a data structure that lets the database find rows without scanning the entire table. Like a book's index vs reading every page.

```python
# Without index: full table scan — reads every row to find matches
# O(n) where n = number of rows

# With index on category: binary search or B-tree lookup
# O(log n) — dramatically faster at scale

with sqlite3.connect("analytics.db") as conn:
    # Create an index on a frequently-queried column
    conn.execute("CREATE INDEX IF NOT EXISTS idx_category ON products(category)")

    # Composite index — useful when you filter on multiple columns together
    conn.execute("CREATE INDEX IF NOT EXISTS idx_cat_price ON products(category, price)")

    conn.commit()
```

**When to index:**
- Columns you filter on frequently (`WHERE category = ?`)
- Columns you join on (`ON orders.cust_id = customers.id`)
- Columns you sort by (`ORDER BY price`)

**When NOT to index:**
- Small tables (< a few thousand rows) — full scan is fast enough
- Columns you write to constantly — each INSERT/UPDATE must also update the index

**EXPLAIN QUERY PLAN — see what SQLite is doing:**

```python
with sqlite3.connect("analytics.db") as conn:
    plan = conn.execute(
        "EXPLAIN QUERY PLAN SELECT * FROM products WHERE category = 'laptops'"
    ).fetchall()
    for row in plan:
        print(row)
    # Without index: "SCAN products"
    # With index:    "SEARCH products USING INDEX idx_category"
```

---

## 1️⃣1️⃣ Connection Pooling

In production web applications, creating a new database connection for every request is expensive. A **connection pool** keeps a set of connections open and reuses them.

```
Without pooling:
  Request → open connection → query → close → Request → open connection → ...
  Each open/close: ~5-20ms overhead

With pooling:
  App starts → 5 connections pre-opened
  Request → borrow connection → query → return to pool
  Overhead: ~0.1ms
```

SQLAlchemy handles pooling automatically:

```python
from sqlalchemy import create_engine

# Default pool: 5 connections, up to 10 overflow
engine = create_engine(
    "postgresql://user:pass@localhost/mydb",
    pool_size=5,       # ← connections kept open
    max_overflow=10,   # ← extra connections allowed under load
    pool_timeout=30,   # ← seconds to wait for a free connection
    pool_recycle=1800  # ← recycle connections after 30 min (prevents stale connections)
)

# Each `with engine.connect()` borrows from pool, returns on exit
with engine.connect() as conn:
    result = conn.execute(text("SELECT 1"))
```

For sqlite3 (single-file, no concurrency), pooling isn't relevant. It matters for PostgreSQL, MySQL, and other server-based databases.

---

## Summary

SQL is not optional for data engineers and ML engineers. It's where the data actually lives.

The progression:
1. **sqlite3** — learn the fundamentals: cursor, execute, parameterized queries, CRUD
2. **SQL queries** — master WHERE, JOIN, GROUP BY — these are universal across all databases
3. **SQLAlchemy** — production-grade Python↔database layer: ORM for apps, Core for pipelines
4. **Pandas integration** — `read_sql` / `to_sql` for data science workflows
5. **DuckDB** — modern analytics: SQL on DataFrames and Parquet without a server

The engineer who combines Python + SQL + Pandas can debug any data bug, build any ETL pipeline, and understand exactly what data a model trains on.

---

## 🔁 Navigation

Previous: `../29_web_scraping/theory.md`
Next: `../31_file_formats_pdf_xml/theory.md`

---

**[🏠 Back to README](../README.md)**

**Prev:** [← Web Scraping](../29_web_scraping/theory.md) &nbsp;|&nbsp; **Next:** [File Formats: PDF & XML →](../31_file_formats_pdf_xml/theory.md)

**Related Topics:** [Cheat Sheet](./cheetsheet.md) · [Interview Q&A](./interview.md) · [Practice](./practice.py)
