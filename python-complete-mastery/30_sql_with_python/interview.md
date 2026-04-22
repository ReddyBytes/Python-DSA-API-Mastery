# 🗄️ SQL with Python — Interview Q&A

---

## Q1: What is a parameterized query and why is it important?

A **parameterized query** (also called a prepared statement) separates SQL code from data values by using placeholders instead of embedding values directly in the SQL string.

```python
# Dangerous — string concatenation enables SQL injection
name = "'; DROP TABLE users; --"
conn.execute(f"SELECT * FROM users WHERE name = '{name}'")  # destroys DB

# Safe — parameterized query
conn.execute("SELECT * FROM users WHERE name = ?", (name,))
```

Why it works: the SQL and the parameters are sent to the database engine separately. The engine never interprets the parameter as SQL code — it's always a plain value. This makes **SQL injection** impossible.

The placeholder syntax differs by library:
- `sqlite3` → `?`
- SQLAlchemy Core / psycopg2 → `:name` or `%(name)s`

---

## Q2: What is the difference between sqlite3 and SQLAlchemy?

**sqlite3** is a low-level standard library module for talking to SQLite databases. You write raw SQL strings, manage cursors manually, and get back tuples.

**SQLAlchemy** is a third-party toolkit that sits on top of database drivers (including sqlite3) and provides two layers:
- **Core**: a SQL expression language — safer than raw strings, database-agnostic
- **ORM**: maps Python classes to database tables, so you work with objects not tuples

```
sqlite3        →  raw SQL, tuples, only SQLite, ships with Python
SQLAlchemy     →  Core + ORM, works with any DB (PostgreSQL, MySQL, SQLite...)
```

Use sqlite3 for quick scripts and learning. Use SQLAlchemy for production applications where you need portability and abstraction.

---

## Q3: When would you use DuckDB?

**DuckDB** when you need fast analytical queries on local data without spinning up a database server.

Specifically:
- Running SQL directly on a **pandas DataFrame** without writing to disk
- Querying **Parquet files** with SQL (DuckDB is Parquet-native)
- Aggregations, GROUP BY, window functions on large files faster than pandas
- Data science / ML feature engineering pipelines
- Replacing heavy ETL pipelines with inline SQL on files

```python
# Query a DataFrame with SQL — DuckDB's killer feature
result = duckdb.execute("SELECT category, AVG(price) FROM df GROUP BY category").df()
```

DuckDB uses **columnar storage** internally, which makes analytical queries (aggregations, scans) much faster than sqlite3's row-store model.

---

## Q4: What is the difference between WHERE and HAVING?

Both filter rows, but at different stages of query execution:

- **WHERE** runs before aggregation — filters individual rows from the raw table
- **HAVING** runs after aggregation — filters groups produced by GROUP BY

```sql
-- WHERE: keep only rows with price > 100 before grouping
SELECT category, COUNT(*) AS n
FROM products
WHERE price > 100          -- ← applied to raw rows
GROUP BY category;

-- HAVING: keep only groups with more than 2 products
SELECT category, COUNT(*) AS n
FROM products
GROUP BY category
HAVING n > 2;              -- ← applied to aggregated groups
```

You cannot reference aggregated values (like `COUNT(*)`) in a WHERE clause — that's what HAVING is for.

---

## Q5: Explain the four types of SQL JOINs.

```
INNER JOIN  → only rows that match in BOTH tables
LEFT JOIN   → all rows from left table; NULLs where right has no match
RIGHT JOIN  → all rows from right table; NULLs where left has no match
FULL OUTER  → all rows from both tables; NULLs on either side where no match
```

Practically:
- **INNER JOIN**: "give me orders that have a matching customer"
- **LEFT JOIN**: "give me all customers, and their orders if they have any"
- **FULL OUTER**: "give me every customer and every order, matched where possible"

LEFT JOIN is by far the most common in practice. INNER JOIN is second. RIGHT JOIN is rare (just flip the table order and use LEFT JOIN). FULL OUTER is used in reconciliation queries.

---

## Q6: What are ACID properties?

**ACID** describes the guarantees a relational database provides for transactions:

| Property | Guarantee |
|---|---|
| **Atomicity** | All operations in a transaction succeed or all are rolled back |
| **Consistency** | The database moves from one valid state to another (constraints never violated) |
| **Isolation** | Concurrent transactions don't see each other's partial changes |
| **Durability** | Once committed, data survives crashes and power failures |

Classic example: bank transfer. Debit account A and credit account B must both succeed, or neither should — atomicity guarantees this.

---

## Q7: What is connection pooling and why does it matter?

Opening a database connection is expensive: TCP handshake, authentication, session setup — typically 5-20ms. In a web application handling 1000 requests/second, creating a new connection per request would consume all your time just on setup.

A **connection pool** maintains a set of pre-opened connections. Requests borrow a connection from the pool, use it, and return it — taking ~0.1ms instead of 20ms.

SQLAlchemy manages pooling automatically:

```python
engine = create_engine(
    "postgresql://...",
    pool_size=5,       # keep 5 connections open
    max_overflow=10,   # allow 10 more under peak load
    pool_timeout=30    # raise after 30s waiting for a free connection
)
```

Connection pooling is irrelevant for sqlite3 (no network, single file, not designed for concurrent writers).

---

## Q8: How do you prevent SQL injection in Python?

Three rules:
1. **Always use parameterized queries** — never concatenate user input into SQL strings
2. **Never use f-strings or .format() to build SQL** — treat any external input as untrusted
3. **Use an ORM (SQLAlchemy)** — ORM queries are parameterized by default

```python
# All safe:
conn.execute("SELECT * FROM t WHERE id = ?", (user_id,))           # sqlite3
session.query(User).filter(User.id == user_id)                      # SQLAlchemy ORM
conn.execute(text("SELECT * FROM t WHERE id = :id"), {"id": uid})   # SQLAlchemy Core
```

---

## Q9: What is the difference between fetchone(), fetchall(), and iterating the cursor?

```python
cursor.execute("SELECT * FROM users")

fetchone()   # returns one tuple (or None); subsequent calls return next row
fetchall()   # loads ALL rows into memory at once — dangerous for large tables
for row in cursor:  # iterates lazily, one row at a time — best for large results
    process(row)
```

**fetchall()** is fine for small result sets. For large queries (millions of rows), iterate the cursor directly or use `fetchmany(size=1000)` to avoid loading everything into RAM.

---

## Q10: What is an index and when should you create one?

An **index** is a separate data structure (usually a B-tree) that maps column values to their row locations, enabling fast lookup without a full table scan.

**Create an index when:**
- You frequently filter on a column (`WHERE category = ?`)
- You join tables on a column (`ON orders.cust_id = customers.id`)
- You sort on a column (`ORDER BY price`)

**Avoid indexing when:**
- The table is small (full scan is fast enough)
- The column is written to heavily (every INSERT/UPDATE must update the index)
- The column has very low cardinality (e.g., a boolean — index barely helps)

```sql
CREATE INDEX idx_category ON products(category);     -- single column
CREATE INDEX idx_cat_price ON products(category, price);  -- composite
```

---

## Q11: How does pd.read_sql() differ from pd.read_sql_table() and pd.read_sql_query()?

| Function | Behavior |
|---|---|
| `pd.read_sql(sql, con)` | Accepts either a SQL string or a table name — auto-detects |
| `pd.read_sql_query(sql, con)` | Only accepts a SQL SELECT string |
| `pd.read_sql_table(table, con)` | Only accepts a table name — reads entire table (requires SQLAlchemy engine, not raw connection) |

In practice, `pd.read_sql()` is the most common because it handles both cases.

---

## Q12: What is the SQLAlchemy ORM session and what does session.commit() do?

A **Session** in SQLAlchemy is the "unit of work" — it tracks all Python objects you've added, modified, or deleted since the last commit.

`session.commit()` does three things:
1. Flushes all pending changes to the database (SQL INSERT/UPDATE/DELETE)
2. Commits the transaction (makes changes permanent and visible to other connections)
3. Expires all loaded objects (so next access re-fetches from DB to stay fresh)

`session.rollback()` discards all pending changes and returns to the state at the last commit.

```python
with Session(engine) as session:
    user = session.query(User).first()
    user.name = "New Name"   # ← SQLAlchemy tracks this change
    # session.commit() not called — change is lost when session closes
```

Always call `session.commit()` explicitly to persist changes.

---

## Q13: When would you choose SQLAlchemy Core over the ORM?

**Use Core when:**
- Writing data pipeline / ETL code — bulk inserts, complex aggregations
- You want direct SQL control without object overhead
- Performance matters for high-volume inserts (ORM per-object overhead adds up)
- Working with existing tables you don't want to model as classes

**Use ORM when:**
- Building a web application with related objects (User has many Orders)
- You want Python-idiomatic syntax: `session.query(User).filter(...).all()`
- You want automatic change tracking (modify a field, commit — SQLAlchemy generates the UPDATE)
- Team prefers working with objects over result tuples

---

## 🔁 Navigation

Previous: `../29_web_scraping/theory.md`
Next: `../31_file_formats_pdf_xml/theory.md`

---

**[🏠 Back to README](../README.md)**

**Prev:** [← Web Scraping](../29_web_scraping/theory.md) &nbsp;|&nbsp; **Next:** [File Formats: PDF & XML →](../31_file_formats_pdf_xml/theory.md)

**Related Topics:** [Theory](./theory.md) · [Cheat Sheet](./cheetsheet.md) · [Practice](./practice.py)
