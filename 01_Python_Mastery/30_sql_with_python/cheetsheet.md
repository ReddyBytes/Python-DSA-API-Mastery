# 🗄️ SQL with Python — Cheat Sheet

---

## sqlite3 Quick Reference

```python
import sqlite3

# Connect / create
conn = sqlite3.connect("mydb.db")          # file-based
conn = sqlite3.connect(":memory:")         # in-memory (tests)

# Context manager (preferred)
with sqlite3.connect("mydb.db") as conn:
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM t")
    rows = cursor.fetchall()               # list of tuples
    row  = cursor.fetchone()               # single tuple or None

# Row dict access
conn.row_factory = sqlite3.Row
row["column_name"]                         # access by name

# Parameterized — always use ? for values
conn.execute("SELECT * FROM t WHERE id = ?", (1,))
conn.executemany("INSERT INTO t VALUES (?,?)", [(1,'a'),(2,'b')])

# Commit / rollback
conn.commit()
conn.rollback()
```

---

## CRUD Patterns

```python
# CREATE TABLE
conn.execute("""
    CREATE TABLE IF NOT EXISTS users (
        id    INTEGER PRIMARY KEY AUTOINCREMENT,
        name  TEXT NOT NULL,
        email TEXT UNIQUE
    )
""")

# INSERT
conn.execute("INSERT INTO users (name, email) VALUES (?, ?)", ("Alice", "alice@x.com"))

# INSERT MANY
conn.executemany("INSERT INTO users (name) VALUES (?)", [("Bob",), ("Carol",)])

# SELECT
rows = conn.execute("SELECT * FROM users").fetchall()
rows = conn.execute("SELECT * FROM users WHERE id = ?", (1,)).fetchall()

# UPDATE
conn.execute("UPDATE users SET name = ? WHERE id = ?", ("Alicia", 1))

# DELETE
conn.execute("DELETE FROM users WHERE id = ?", (1,))
conn.commit()
```

---

## SQL Query Patterns

```sql
-- WHERE
SELECT * FROM t WHERE col = 'val' AND price > 100;
SELECT * FROM t WHERE col IN ('a', 'b', 'c');
SELECT * FROM t WHERE name LIKE '%pro%';      -- case-insensitive pattern
SELECT * FROM t WHERE val BETWEEN 10 AND 50;

-- ORDER BY / LIMIT / OFFSET
SELECT * FROM t ORDER BY price DESC LIMIT 10;
SELECT * FROM t ORDER BY price DESC LIMIT 10 OFFSET 20;  -- pagination

-- GROUP BY / HAVING
SELECT category, COUNT(*) AS n, AVG(price) AS avg
FROM products
GROUP BY category
HAVING n > 2;           -- HAVING filters aggregated groups (WHERE can't)

-- Subquery
SELECT * FROM products
WHERE price > (SELECT AVG(price) FROM products);

-- EXISTS
SELECT * FROM customers c
WHERE EXISTS (SELECT 1 FROM orders o WHERE o.cust_id = c.id);
```

---

## JOIN Diagrams

```
Table A (customers)    Table B (orders)
+------+               +------+
|  1   |               |  1   |
|  2   |               |  2   |
|  3   |               |  3   |  ← B has an entry with no match in A
|  4   |               +------+
+------+

INNER JOIN      LEFT JOIN       RIGHT JOIN      FULL OUTER
   A ∩ B          A (+ B)         B (+ A)         A ∪ B
  [  AB ]       [ A  AB ]       [ AB  B ]       [ A  AB  B ]
  matched        all A           all B            everything
  rows only      + NULLs         + NULLs          + NULLs both sides
```

```sql
-- INNER JOIN: only matched rows
SELECT a.name, b.product
FROM customers a
INNER JOIN orders b ON a.id = b.cust_id;

-- LEFT JOIN: all customers, NULLs for those with no orders
SELECT a.name, b.product
FROM customers a
LEFT JOIN orders b ON a.id = b.cust_id;

-- RIGHT JOIN equivalent (swap tables + LEFT JOIN)
SELECT a.name, b.product
FROM orders b
LEFT JOIN customers a ON a.id = b.cust_id;

-- FULL OUTER (sqlite3: simulate with UNION)
SELECT a.name, b.product FROM customers a LEFT JOIN orders b ON a.id = b.cust_id
UNION ALL
SELECT a.name, b.product FROM orders b LEFT JOIN customers a ON a.id = b.cust_id
WHERE a.id IS NULL;
```

---

## SQLAlchemy Quick Reference

```python
from sqlalchemy import create_engine, Column, Integer, String, Float, text
from sqlalchemy.orm import DeclarativeBase, Session

# Engine
engine = create_engine("sqlite:///mydb.db")                    # SQLite
engine = create_engine("postgresql://user:pass@host/dbname")   # PostgreSQL
engine = create_engine("mysql+pymysql://user:pass@host/dbname")# MySQL

# ORM Model
class Base(DeclarativeBase): pass

class User(Base):
    __tablename__ = "users"
    id    = Column(Integer, primary_key=True, autoincrement=True)
    name  = Column(String, nullable=False)
    email = Column(String, unique=True)

Base.metadata.create_all(engine)   # create tables

# Session CRUD
with Session(engine) as s:
    # INSERT
    s.add(User(name="Alice", email="alice@x.com"))
    s.add_all([User(name="Bob"), User(name="Carol")])
    s.commit()

    # SELECT
    all_users  = s.query(User).all()
    one        = s.query(User).filter(User.name == "Alice").first()
    filtered   = s.query(User).filter(User.id > 2).order_by(User.name).limit(5).all()

    # UPDATE
    user = s.query(User).filter(User.id == 1).first()
    user.name = "Alicia"
    s.commit()

    # DELETE
    s.delete(user)
    s.commit()

# Raw SQL via Core
with engine.connect() as conn:
    result = conn.execute(text("SELECT * FROM users WHERE id = :uid"), {"uid": 1})
    for row in result:
        print(row)
```

---

## Pandas + SQL

```python
import pandas as pd
from sqlalchemy import create_engine

engine = create_engine("sqlite:///mydb.db")

# Read: database → DataFrame
df = pd.read_sql("SELECT * FROM products", engine)
df = pd.read_sql_table("products", engine)          # whole table, no SQL
df = pd.read_sql("SELECT * FROM t WHERE col = %s", engine, params=("val",))

# Write: DataFrame → database
df.to_sql(
    name="products",
    con=engine,
    if_exists="replace",  # "replace" | "append" | "fail"
    index=False,          # don't write DataFrame index as column
    chunksize=1000        # write in batches
)

# Quick pattern: CSV → DB
df = pd.read_csv("data.csv")
df.to_sql("raw_data", engine, if_exists="replace", index=False)

# Quick pattern: DB → CSV
df = pd.read_sql("SELECT * FROM results", engine)
df.to_csv("results.csv", index=False)
```

---

## DuckDB Quick Reference

```python
import duckdb

con = duckdb.connect()                    # in-memory
con = duckdb.connect("analytics.duckdb") # persistent file

# SQL on a Parquet file
result = con.execute("""
    SELECT category, SUM(revenue)
    FROM read_parquet('data.parquet')
    GROUP BY category
""").df()                                 # .df() returns pandas DataFrame

# SQL on a CSV
result = con.execute("SELECT * FROM read_csv_auto('data.csv') LIMIT 10").df()

# SQL on a pandas DataFrame (killer feature)
import pandas as pd
df = pd.read_csv("data.csv")
result = con.execute("SELECT * FROM df WHERE price > 500").df()  # df is the var name

# DuckDB vs sqlite3 at a glance
# sqlite3  → transactional, row-store, OLTP, no deps
# DuckDB   → analytical, column-store, OLAP, DataFrames/Parquet
```

---

## SQL Data Types (sqlite3 / general)

```
INTEGER    →  whole numbers (int)
REAL       →  floating point (float)
TEXT       →  strings
BLOB       →  raw binary data
NULL       →  absence of value

-- PostgreSQL extras
BOOLEAN    →  True/False
TIMESTAMP  →  datetime with timezone
JSONB      →  binary JSON (indexable)
ARRAY      →  native arrays
```

---

## Indexes

```sql
-- Single column index
CREATE INDEX idx_name ON table_name(column);

-- Composite index (order matters: left-to-right prefix rule)
CREATE INDEX idx_cat_price ON products(category, price);

-- Unique index
CREATE UNIQUE INDEX idx_email ON users(email);

-- Drop index
DROP INDEX idx_name;

-- Check query plan (sqlite3)
EXPLAIN QUERY PLAN SELECT * FROM products WHERE category = 'laptops';
```

---

## Transaction Pattern

```python
# sqlite3
try:
    conn.execute("BEGIN")
    conn.execute("UPDATE accounts SET balance = balance - 100 WHERE id = 1")
    conn.execute("UPDATE accounts SET balance = balance + 100 WHERE id = 2")
    conn.execute("COMMIT")
except Exception:
    conn.execute("ROLLBACK")
    raise

# SQLAlchemy
with Session(engine) as session:
    try:
        session.execute(text("UPDATE accounts SET balance = balance - 100 WHERE id = 1"))
        session.execute(text("UPDATE accounts SET balance = balance + 100 WHERE id = 2"))
        session.commit()
    except Exception:
        session.rollback()
        raise
```

---

## ACID Summary

```
A  Atomicity   — all-or-nothing (commit or rollback the whole transaction)
C  Consistency — database stays valid (constraints never violated mid-transaction)
I  Isolation   — concurrent transactions don't interfere with each other
D  Durability  — committed data survives crashes (written to disk)
```

---

## 🔁 Navigation

Previous: `../29_web_scraping/theory.md`
Next: `../31_file_formats_pdf_xml/theory.md`

---

**[🏠 Back to README](../README.md)**

**Prev:** [← Web Scraping](../29_web_scraping/theory.md) &nbsp;|&nbsp; **Next:** [File Formats: PDF & XML →](../31_file_formats_pdf_xml/theory.md)

**Related Topics:** [Theory](./theory.md) · [Interview Q&A](./interview.md) · [Practice](./practice.py)
