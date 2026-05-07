# SQL with Python — Practice

## Quick Index

| Q | Topic | Difficulty |
|---|---|---|
| [Q1](#q1) | sqlite3 — create connection and cursor | 🟢 |
| [Q2](#q2) | sqlite3 — CREATE TABLE with IF NOT EXISTS | 🟢 |
| [Q3](#q3) | sqlite3 — context manager connection | 🟢 |
| [Q4](#q4) | CRUD — INSERT a single row (parameterized) | 🟢 |
| [Q5](#q5) | CRUD — SELECT all rows with fetchall | 🟢 |
| [Q6](#q6) | CRUD — UPDATE with WHERE clause | 🟢 |
| [Q7](#q7) | CRUD — DELETE with WHERE clause | 🟢 |
| [Q8](#q8) | Query Patterns — ORDER BY + LIMIT (top-N) | 🟢 |
| [Q9](#q9) | Query Patterns — GROUP BY + HAVING | 🟡 |
| [Q10](#q10) | Query Patterns — subquery (above average) | 🟡 |
| [Q11](#q11) | Parameterized — ? placeholders explained | 🟢 |
| [Q12](#q12) | Parameterized — executemany bulk insert | 🟡 |
| [Q13](#q13) | Parameterized — SQL injection prevention | 🟡 |
| [Q14](#q14) | JOINs — INNER JOIN two tables | 🟡 |
| [Q15](#q15) | JOINs — LEFT JOIN (include NULLs) | 🟡 |
| [Q16](#q16) | JOINs — self-join pattern | 🟠 |
| [Q17](#q17) | SQLAlchemy — engine + text() raw query | 🟡 |
| [Q18](#q18) | SQLAlchemy — ORM model definition | 🟡 |
| [Q19](#q19) | SQLAlchemy — session CRUD (add/query/delete) | 🟡 |
| [Q20](#q20) | SQLAlchemy — relationship between models | 🟠 |
| [Q21](#q21) | Pandas + SQL — read_sql_query to DataFrame | 🟢 |
| [Q22](#q22) | Pandas + SQL — to_sql write DataFrame to DB | 🟡 |
| [Q23](#q23) | Pandas + SQL — chunked read with chunksize | 🟡 |
| [Q24](#q24) | DuckDB — in-process SQL on a DataFrame | 🟡 |
| [Q25](#q25) | DuckDB — read_csv_auto direct file query | 🟡 |
| [Q26](#q26) | DuckDB — DuckDB vs sqlite3 performance tradeoff | 🟠 |
| [Q27](#q27) | Transactions — explicit BEGIN/COMMIT pattern | 🟡 |
| [Q28](#q28) | Transactions — rollback on error | 🟡 |
| [Q29](#q29) | Transactions — savepoint nested rollback | 🟠 |
| [Q30](#q30) | Indexes — CREATE INDEX single column | 🟢 |
| [Q31](#q31) | Indexes — EXPLAIN QUERY PLAN before/after | 🟡 |
| [Q32](#q32) | Indexes — covering index (composite) | 🟠 |
| [Q33](#q33) | Connection Pooling — pool_size + max_overflow | 🟡 |
| [Q34](#q34) | Connection Pooling — NullPool (no pooling) | 🟡 |
| [Q35](#q35) | Connection Pooling — QueuePool with timeout | 🟠 |

---

## Ch1 — sqlite3 Module

### Q1 · sqlite3 — create connection and cursor 🟢

Open a connection to `mydb.db`, create a cursor, run `SELECT sqlite_version()`, print the result, and close the connection manually.

> 🛠️ **Solve locally:** [practice_local.py → Q1](./practice_local.py)

<details><summary>💡 Hint</summary>sqlite3.connect() returns a connection; call .cursor() on it to get a cursor object</details>
<details><summary>✅ Answer</summary>

```python
import sqlite3

conn = sqlite3.connect("mydb.db")      # ← opens or creates the .db file
cursor = conn.cursor()                 # ← the "hand" that runs SQL

cursor.execute("SELECT sqlite_version()")
version = cursor.fetchone()            # ← returns a single tuple
print(version)                         # ('3.39.5',)

conn.close()                           # ← always close manually when not using context manager
```

**Why:** `connect()` opens the file; `cursor()` gives you the object that sends SQL to the engine; `fetchone()` retrieves the first result row.
</details>

---

### Q2 · sqlite3 — CREATE TABLE with IF NOT EXISTS 🟢

Create a `users` table with columns `id` (INTEGER PRIMARY KEY AUTOINCREMENT), `name` (TEXT NOT NULL), and `email` (TEXT UNIQUE). Use `IF NOT EXISTS` so re-running the script is safe.

> 🛠️ **Solve locally:** [practice_local.py → Q2](./practice_local.py)

<details><summary>💡 Hint</summary>Use conn.execute() with a multi-line CREATE TABLE statement, then conn.commit()</details>
<details><summary>✅ Answer</summary>

```python
import sqlite3

with sqlite3.connect("mydb.db") as conn:
    conn.execute("""
        CREATE TABLE IF NOT EXISTS users (
            id    INTEGER PRIMARY KEY AUTOINCREMENT,  -- auto-assigned
            name  TEXT    NOT NULL,
            email TEXT    UNIQUE                      -- enforces uniqueness
        )
    """)
    conn.commit()
    print("Table created (or already exists).")
```

**Why:** `IF NOT EXISTS` makes this idempotent — running it twice doesn't raise an error; `AUTOINCREMENT` means you never have to supply an `id` on INSERT.
</details>

---

### Q3 · sqlite3 — context manager connection 🟢

Connect to an in-memory SQLite database (`:memory:`), create a `scores` table, insert one row, and read it back — all inside a `with` block. Explain what the `with` statement handles automatically.

> 🛠️ **Solve locally:** [practice_local.py → Q3](./practice_local.py)

<details><summary>💡 Hint</summary>sqlite3.connect(":memory:") creates a temporary DB that disappears when the connection closes</details>
<details><summary>✅ Answer</summary>

```python
import sqlite3

with sqlite3.connect(":memory:") as conn:   # ← auto-closes when block exits
    conn.execute("CREATE TABLE scores (name TEXT, score INTEGER)")
    conn.execute("INSERT INTO scores VALUES (?, ?)", ("Alice", 95))
    conn.commit()

    rows = conn.execute("SELECT * FROM scores").fetchall()
    print(rows)   # [('Alice', 95)]
# conn.close() is called automatically here — no data leaks
```

**Why:** The `with` block calls `conn.close()` on exit whether the code succeeds or raises an exception — the same guarantee as a `try/finally` block.
</details>

---

## Ch2 — CRUD Operations

### Q4 · CRUD — INSERT a single row (parameterized) 🟢

Insert one product (`name="MacBook Pro"`, `price=2499.99`, `category="laptops"`) into a `products` table. Use `?` placeholders, not an f-string.

> 🛠️ **Solve locally:** [practice_local.py → Q4](./practice_local.py)

<details><summary>💡 Hint</summary>Pass a tuple as the second argument to conn.execute() — never build the SQL string with f-string interpolation</details>
<details><summary>✅ Answer</summary>

```python
import sqlite3

with sqlite3.connect("mydb.db") as conn:
    conn.execute("""
        CREATE TABLE IF NOT EXISTS products (
            id       INTEGER PRIMARY KEY AUTOINCREMENT,
            name     TEXT NOT NULL,
            price    REAL NOT NULL,
            category TEXT
        )
    """)
    conn.execute(
        "INSERT INTO products (name, price, category) VALUES (?, ?, ?)",
        ("MacBook Pro", 2499.99, "laptops")   # ← tuple, not f-string
    )
    conn.commit()
    print("Inserted.")
```

**Why:** The `?` placeholder keeps the SQL and the data separate — the engine never interprets the value as SQL code, making injection impossible.
</details>

---

### Q5 · CRUD — SELECT all rows with fetchall 🟢

Query all products from the `products` table ordered by price descending. Print each row using dict-style column access (`row["name"]`).

> 🛠️ **Solve locally:** [practice_local.py → Q5](./practice_local.py)

<details><summary>💡 Hint</summary>Set conn.row_factory = sqlite3.Row before querying to enable column-name access</details>
<details><summary>✅ Answer</summary>

```python
import sqlite3

with sqlite3.connect("mydb.db") as conn:
    conn.row_factory = sqlite3.Row               # ← enables dict-style access

    rows = conn.execute(
        "SELECT * FROM products ORDER BY price DESC"
    ).fetchall()                                 # ← list of Row objects

    for row in rows:
        print(f"{row['name']}: ${row['price']:.2f}")   # ← access by column name
```

**Why:** `sqlite3.Row` lets you write `row["name"]` instead of `row[1]` — much safer when the column order might change.
</details>

---

### Q6 · CRUD — UPDATE with WHERE clause 🟢

Update the price of `"MacBook Pro"` to `1999.99`. After the update, print how many rows were changed using `conn.total_changes`.

> 🛠️ **Solve locally:** [practice_local.py → Q6](./practice_local.py)

<details><summary>💡 Hint</summary>conn.total_changes returns the cumulative count of rows modified since the connection was opened</details>
<details><summary>✅ Answer</summary>

```python
import sqlite3

with sqlite3.connect("mydb.db") as conn:
    conn.execute(
        "UPDATE products SET price = ? WHERE name = ?",
        (1999.99, "MacBook Pro")     # ← parameterized, always
    )
    conn.commit()
    print(f"Rows changed: {conn.total_changes}")   # ← 1 if the row existed
```

**Why:** Without a `WHERE` clause, `UPDATE` modifies every row in the table — always scope your updates with a condition.
</details>

---

### Q7 · CRUD — DELETE with WHERE clause 🟢

Delete all products where `price < 100.0`. Print the number of rows deleted by checking `cursor.rowcount`.

> 🛠️ **Solve locally:** [practice_local.py → Q7](./practice_local.py)

<details><summary>💡 Hint</summary>Use conn.execute() and capture the returned cursor object — cursor.rowcount tells you how many rows were affected</details>
<details><summary>✅ Answer</summary>

```python
import sqlite3

with sqlite3.connect("mydb.db") as conn:
    cursor = conn.execute(
        "DELETE FROM products WHERE price < ?",
        (100.0,)
    )
    conn.commit()
    print(f"Rows deleted: {cursor.rowcount}")   # ← rowcount on the cursor
```

**Why:** `cursor.rowcount` tells you how many rows the last statement affected — useful for confirming a DELETE actually removed something.
</details>

---

## Ch3 — SQL Query Patterns

### Q8 · Query Patterns — ORDER BY + LIMIT (top-N) 🟢

Write a query that returns the top 3 most expensive products by price. Also write a second query that implements pagination: skip the first 10 products, return the next 10.

> 🛠️ **Solve locally:** [practice_local.py → Q8](./practice_local.py)

<details><summary>💡 Hint</summary>Use ORDER BY price DESC LIMIT 3 for top-N; add OFFSET 10 for pagination</details>
<details><summary>✅ Answer</summary>

```python
import sqlite3

with sqlite3.connect("mydb.db") as conn:
    # Top 3 most expensive
    top3 = conn.execute("""
        SELECT name, price
        FROM products
        ORDER BY price DESC
        LIMIT 3                  -- only return 3 rows
    """).fetchall()

    # Page 2 (rows 11-20)
    page2 = conn.execute("""
        SELECT name, price
        FROM products
        ORDER BY price DESC
        LIMIT 10 OFFSET 10       -- skip 10, return next 10
    """).fetchall()

    print(top3)
    print(page2)
```

**Why:** `LIMIT` caps results; `OFFSET` skips rows — together they power pagination. Always pair `LIMIT/OFFSET` with `ORDER BY` for predictable page results.
</details>

---

### Q9 · Query Patterns — GROUP BY + HAVING 🟡

Count the number of products per category and their average price. Only show categories that have more than 1 product. Order results by average price descending.

> 🛠️ **Solve locally:** [practice_local.py → Q9](./practice_local.py)

<details><summary>💡 Hint</summary>HAVING filters aggregated groups (post-GROUP BY); WHERE filters individual rows (pre-GROUP BY) — you cannot use WHERE with COUNT(*)</details>
<details><summary>✅ Answer</summary>

```python
import sqlite3

with sqlite3.connect("mydb.db") as conn:
    rows = conn.execute("""
        SELECT
            category,
            COUNT(*)       AS n,
            AVG(price)     AS avg_price
        FROM products
        GROUP BY category        -- collapse rows into groups
        HAVING n > 1             -- filter AFTER aggregation
        ORDER BY avg_price DESC
    """).fetchall()

    for row in rows:
        print(f"{row[0]}: {row[1]} products, avg ${row[2]:.2f}")
```

**Why:** `HAVING` is the only way to filter on aggregated values — you can't say `WHERE COUNT(*) > 1` because `WHERE` runs before grouping happens.
</details>

---

### Q10 · Query Patterns — subquery (above average) 🟡

Write a query that returns all products whose price is above the average price of all products. Use a subquery — do not pre-compute the average in Python.

> 🛠️ **Solve locally:** [practice_local.py → Q10](./practice_local.py)

<details><summary>💡 Hint</summary>A subquery in the WHERE clause runs first: WHERE price > (SELECT AVG(price) FROM products)</details>
<details><summary>✅ Answer</summary>

```python
import sqlite3

with sqlite3.connect("mydb.db") as conn:
    rows = conn.execute("""
        SELECT name, price
        FROM products
        WHERE price > (
            SELECT AVG(price)     -- subquery runs first, returns one value
            FROM products
        )
        ORDER BY price DESC
    """).fetchall()

    for row in rows:
        print(f"{row[0]}: ${row[1]:.2f}")
```

**Why:** The subquery is evaluated once and its result is used as the filter threshold — the database handles this more efficiently than fetching the average to Python and then re-querying.
</details>

---

## Ch4 — Parameterized Queries

### Q11 · Parameterized — ? placeholders explained 🟢

Show the three safe placeholder styles across libraries: `?` for sqlite3, `:name` for SQLAlchemy Core, and `%(name)s` for psycopg2. Write a sqlite3 example using both positional `?` and named `:name` style.

> 🛠️ **Solve locally:** [practice_local.py → Q11](./practice_local.py)

<details><summary>💡 Hint</summary>sqlite3 supports both ? positional and :name named placeholders</details>
<details><summary>✅ Answer</summary>

```python
import sqlite3

with sqlite3.connect("mydb.db") as conn:
    # Style 1: positional ? (most common in sqlite3)
    conn.execute(
        "SELECT * FROM products WHERE category = ?",
        ("laptops",)
    )

    # Style 2: named :name (also works in sqlite3)
    rows = conn.execute(
        "SELECT * FROM products WHERE category = :cat AND price > :min",
        {"cat": "laptops", "min": 500}
    ).fetchall()

    # SQLAlchemy Core uses :name style with a dict
    # psycopg2 uses %(name)s style with a dict
    # Principle is identical: data never touches the SQL string
    print(rows)
```

**Why:** Named placeholders (`:cat`) are clearer than positional (`?`) when you have multiple parameters — you can see which value goes where without counting question marks.
</details>

---

### Q12 · Parameterized — executemany bulk insert 🟡

Insert 5 products in a single `executemany()` call. Each product is a tuple of `(name, price, category)`. Confirm the insert count using `cursor.rowcount`.

> 🛠️ **Solve locally:** [practice_local.py → Q12](./practice_local.py)

<details><summary>💡 Hint</summary>executemany(sql, list_of_tuples) loops internally and is faster than calling execute() in a Python for-loop</details>
<details><summary>✅ Answer</summary>

```python
import sqlite3

products = [
    ("iPad Pro",     999.99, "tablets"),
    ("AirPods Pro",  249.99, "audio"),
    ("AirPods Max",  549.99, "audio"),
    ("Apple Watch",  399.99, "wearables"),
    ("HomePod mini",  99.99, "speakers"),
]

with sqlite3.connect("mydb.db") as conn:
    cursor = conn.executemany(
        "INSERT INTO products (name, price, category) VALUES (?, ?, ?)",
        products   # ← list of tuples, one INSERT per tuple
    )
    conn.commit()
    print(f"Rows inserted: {cursor.rowcount}")   # 5
```

**Why:** `executemany()` is more efficient than a Python loop of `execute()` calls because the database can pipeline the inserts internally.
</details>

---

### Q13 · Parameterized — SQL injection prevention 🟡

Demonstrate the injection attack vector: show the dangerous f-string pattern (as a comment only — do not execute), then show the safe parameterized version handling the same malicious input string.

> 🛠️ **Solve locally:** [practice_local.py → Q13](./practice_local.py)

<details><summary>💡 Hint</summary>The injection string '; DROP TABLE products; -- breaks out of the string context in the SQL</details>
<details><summary>✅ Answer</summary>

```python
import sqlite3

malicious_input = "'; DROP TABLE products; --"   # ← classic injection payload

# DANGEROUS — never do this:
# query = f"SELECT * FROM products WHERE name = '{malicious_input}'"
# conn.execute(query)  # would execute DROP TABLE!

# SAFE — parameterized:
with sqlite3.connect("mydb.db") as conn:
    rows = conn.execute(
        "SELECT * FROM products WHERE name = ?",
        (malicious_input,)    # ← treated as a plain string value, not SQL
    ).fetchall()
    print(rows)   # [] — no match, but DB is intact
```

**Why:** The `?` placeholder sends SQL and data separately to the engine. The engine never parses the parameter as SQL — the malicious string becomes just a harmless search term.
</details>

---

## Ch5 — JOINs

### Q14 · JOINs — INNER JOIN two tables 🟡

Given `customers` and `orders` tables, write an INNER JOIN query that returns only customers who have placed at least one order, showing `customer name` and `product_id`. Explain what happens to customers with no orders.

> 🛠️ **Solve locally:** [practice_local.py → Q14](./practice_local.py)

<details><summary>💡 Hint</summary>INNER JOIN = intersection — only rows where the ON condition matches in BOTH tables appear in the result</details>
<details><summary>✅ Answer</summary>

```python
import sqlite3

with sqlite3.connect(":memory:") as conn:
    conn.executescript("""
        CREATE TABLE customers (id INTEGER PRIMARY KEY, name TEXT);
        CREATE TABLE orders (id INTEGER PRIMARY KEY, cust_id INTEGER, product_id INTEGER);
        INSERT INTO customers VALUES (1,'Alice'),(2,'Bob'),(3,'Carol');
        INSERT INTO orders VALUES (1,1,101),(2,1,102),(3,2,103);
        -- Carol has no orders
    """)

    rows = conn.execute("""
        SELECT customers.name, orders.product_id
        FROM customers
        INNER JOIN orders ON customers.id = orders.cust_id
        -- Carol is excluded: no matching row in orders
    """).fetchall()

    print(rows)
    # [('Alice', 101), ('Alice', 102), ('Bob', 103)]
    # Carol does not appear — INNER JOIN drops unmatched rows
```

**Why:** INNER JOIN is a set intersection — rows only appear if there is a match on both sides. Customers with no orders are silently excluded.
</details>

---

### Q15 · JOINs — LEFT JOIN (include NULLs) 🟡

Rewrite the Q14 query as a LEFT JOIN so every customer appears in the result, even those with no orders. Show `None` for `product_id` when a customer has no orders.

> 🛠️ **Solve locally:** [practice_local.py → Q15](./practice_local.py)

<details><summary>💡 Hint</summary>LEFT JOIN keeps all rows from the left (first) table; unmatched right-side columns become NULL</details>
<details><summary>✅ Answer</summary>

```python
import sqlite3

with sqlite3.connect(":memory:") as conn:
    conn.executescript("""
        CREATE TABLE customers (id INTEGER PRIMARY KEY, name TEXT);
        CREATE TABLE orders (id INTEGER PRIMARY KEY, cust_id INTEGER, product_id INTEGER);
        INSERT INTO customers VALUES (1,'Alice'),(2,'Bob'),(3,'Carol');
        INSERT INTO orders VALUES (1,1,101),(2,1,102),(3,2,103);
    """)

    rows = conn.execute("""
        SELECT customers.name, orders.product_id
        FROM customers
        LEFT JOIN orders ON customers.id = orders.cust_id
        -- Carol appears with product_id = None
    """).fetchall()

    print(rows)
    # [('Alice', 101), ('Alice', 102), ('Bob', 103), ('Carol', None)]
```

**Why:** LEFT JOIN is the most common join in practice — use it when you want the full left table regardless of whether matches exist on the right.
</details>

---

### Q16 · JOINs — self-join pattern 🟠

You have an `employees` table with columns `id`, `name`, and `manager_id` (which references `employees.id`). Write a self-join query that returns each employee's name alongside their manager's name. Employees with no manager should still appear (NULL manager name).

> 🛠️ **Solve locally:** [practice_local.py → Q16](./practice_local.py)

<details><summary>💡 Hint</summary>Alias the same table twice: FROM employees e LEFT JOIN employees m ON e.manager_id = m.id</details>
<details><summary>✅ Answer</summary>

```python
import sqlite3

with sqlite3.connect(":memory:") as conn:
    conn.executescript("""
        CREATE TABLE employees (id INTEGER PRIMARY KEY, name TEXT, manager_id INTEGER);
        INSERT INTO employees VALUES
            (1, 'Alice', NULL),
            (2, 'Bob',   1),
            (3, 'Carol', 1),
            (4, 'Dave',  2);
    """)

    rows = conn.execute("""
        SELECT
            e.name     AS employee,
            m.name     AS manager
        FROM employees e
        LEFT JOIN employees m ON e.manager_id = m.id   -- same table, two aliases
        ORDER BY e.id
    """).fetchall()

    for row in rows:
        print(f"{row[0]} -> manager: {row[1]}")
    # Alice -> manager: None
    # Bob   -> manager: Alice
    # Carol -> manager: Alice
    # Dave  -> manager: Bob
```

**Why:** A self-join treats one table as two separate logical tables using aliases — essential for hierarchical data like org charts, category trees, or bill-of-materials.
</details>

---

## Ch6 — SQLAlchemy

### Q17 · SQLAlchemy — engine + text() raw query 🟡

Create a SQLAlchemy engine for a SQLite database. Use `engine.connect()` and `text()` to run a raw SQL query with a named parameter (`:min_price`). Print each result row.

> 🛠️ **Solve locally:** [practice_local.py → Q17](./practice_local.py)

<details><summary>💡 Hint</summary>Wrap SQL strings in text() — never pass bare strings to SQLAlchemy 2.0 execute()</details>
<details><summary>✅ Answer</summary>

```python
from sqlalchemy import create_engine, text

engine = create_engine("sqlite:///mydb.db", echo=False)   # ← connection factory

with engine.connect() as conn:
    result = conn.execute(
        text("SELECT name, price FROM products WHERE price > :min_price"),
        {"min_price": 500}       # ← named parameter, not ?
    )
    for row in result:
        print(row.name, row.price)   # ← access by attribute name
```

**Why:** SQLAlchemy 2.0 requires `text()` to wrap raw SQL — it enforces parameterization and prevents bare string execution, which could silently bypass safety checks.
</details>

---

### Q18 · SQLAlchemy — ORM model definition 🟡

Define a `Product` ORM model with columns: `id` (Integer PK), `name` (String, not null), `price` (Float, not null), `category` (String, default `"uncategorized"`). Create the table using `Base.metadata.create_all()`.

> 🛠️ **Solve locally:** [practice_local.py → Q18](./practice_local.py)

<details><summary>💡 Hint</summary>Inherit from DeclarativeBase (SQLAlchemy 2.0 style) — set __tablename__ to the exact DB table name</details>
<details><summary>✅ Answer</summary>

```python
from sqlalchemy import create_engine, Column, Integer, String, Float
from sqlalchemy.orm import DeclarativeBase

engine = create_engine("sqlite:///mydb.db")

class Base(DeclarativeBase):
    pass

class Product(Base):
    __tablename__ = "products"   # ← exact table name in the database

    id       = Column(Integer, primary_key=True, autoincrement=True)
    name     = Column(String, nullable=False)
    price    = Column(Float, nullable=False)
    category = Column(String, default="uncategorized")

    def __repr__(self):
        return f"<Product(name={self.name!r}, price={self.price})>"

Base.metadata.create_all(engine)   # ← CREATE TABLE IF NOT EXISTS
print("Tables created.")
```

**Why:** The ORM model is a Python class that maps to a DB table — SQLAlchemy handles all the CREATE TABLE DDL, so your schema lives in Python, not scattered SQL files.
</details>

---

### Q19 · SQLAlchemy — session CRUD (add/query/delete) 🟡

Using the `Product` model from Q18: (1) insert two products via `session.add_all()`, (2) query all products ordered by price, (3) update one product's price by modifying the attribute and committing, (4) delete the cheapest product.

> 🛠️ **Solve locally:** [practice_local.py → Q19](./practice_local.py)

<details><summary>💡 Hint</summary>After modifying an attribute, just call session.commit() — SQLAlchemy's change tracking detects the mutation and generates the UPDATE automatically</details>
<details><summary>✅ Answer</summary>

```python
from sqlalchemy.orm import Session
# (assume Product model and engine from Q18)

# INSERT
with Session(engine) as session:
    session.add_all([
        Product(name="MacBook Pro", price=2499.99, category="laptops"),
        Product(name="AirPods Pro", price=249.99,  category="audio"),
    ])
    session.commit()

# SELECT
with Session(engine) as session:
    products = session.query(Product).order_by(Product.price.desc()).all()
    for p in products:
        print(p)

# UPDATE — modify attribute, SQLAlchemy auto-generates UPDATE SQL
with Session(engine) as session:
    p = session.query(Product).filter(Product.name == "MacBook Pro").first()
    p.price = 2299.99      # ← just change it
    session.commit()       # ← SQLAlchemy detects the change

# DELETE
with Session(engine) as session:
    cheapest = session.query(Product).order_by(Product.price).first()
    session.delete(cheapest)
    session.commit()
```

**Why:** The ORM session tracks every change to loaded objects — you never write UPDATE SQL by hand; you just mutate Python attributes and commit.
</details>

---

### Q20 · SQLAlchemy — relationship between models 🟠

Define `Category` and `Product` ORM models with a one-to-many relationship. `Category` has many `Products`. Use `relationship()` with `back_populates` for bidirectional access. Insert a category with two products in one session, then query the category and print its products.

> 🛠️ **Solve locally:** [practice_local.py → Q20](./practice_local.py)

<details><summary>💡 Hint</summary>ForeignKey on Product points to categories.id; relationship() on both sides with back_populates linking them</details>
<details><summary>✅ Answer</summary>

```python
from sqlalchemy import create_engine, Column, Integer, String, Float, ForeignKey
from sqlalchemy.orm import DeclarativeBase, Session, relationship

engine = create_engine("sqlite:///orm_rel.db")

class Base(DeclarativeBase):
    pass

class Category(Base):
    __tablename__ = "categories"
    id       = Column(Integer, primary_key=True, autoincrement=True)
    name     = Column(String, nullable=False, unique=True)
    products = relationship("Product", back_populates="category")   # ← one-to-many

class Product(Base):
    __tablename__ = "products"
    id          = Column(Integer, primary_key=True, autoincrement=True)
    name        = Column(String, nullable=False)
    price       = Column(Float, nullable=False)
    category_id = Column(Integer, ForeignKey("categories.id"))      # ← FK
    category    = relationship("Category", back_populates="products")

Base.metadata.create_all(engine)

with Session(engine) as session:
    audio = Category(name="Audio")
    audio.products = [
        Product(name="AirPods Pro", price=249.99),
        Product(name="AirPods Max", price=549.99),
    ]
    session.add(audio)
    session.commit()

with Session(engine) as session:
    cat = session.query(Category).filter_by(name="Audio").first()
    for p in cat.products:           # ← navigate the relationship in Python
        print(p.name, p.price)
```

**Why:** `relationship()` lets you traverse associations as Python attributes (`cat.products`) — SQLAlchemy handles the JOIN behind the scenes.
</details>

---

## Ch7 — Pandas + SQL

### Q21 · Pandas + SQL — read_sql_query to DataFrame 🟢

Read the `products` table into a pandas DataFrame using `pd.read_sql_query()`. Use a SQLAlchemy engine (not a raw sqlite3 connection). Filter for products with `price > 500` directly in the SQL string.

> 🛠️ **Solve locally:** [practice_local.py → Q21](./practice_local.py)

<details><summary>💡 Hint</summary>pd.read_sql_query(sql_string, engine) returns a DataFrame with column names matching the SELECT aliases</details>
<details><summary>✅ Answer</summary>

```python
import pandas as pd
from sqlalchemy import create_engine

engine = create_engine("sqlite:///mydb.db")

df = pd.read_sql_query(
    "SELECT name, price, category FROM products WHERE price > 500 ORDER BY price DESC",
    engine    # ← SQLAlchemy engine preferred over raw sqlite3 connection
)

print(df.head())
print(df.dtypes)
```

**Why:** Using a SQLAlchemy engine (not a raw connection) is the production pattern — it handles connection pooling, retries, and works with any database backend without changing this code.
</details>

---

### Q22 · Pandas + SQL — to_sql write DataFrame to DB 🟡

Build a DataFrame with 5 rows in-memory, then write it to a table called `sales` using `df.to_sql()`. Use `if_exists="replace"` and `index=False`. Verify by reading the table back with `pd.read_sql_query()`.

> 🛠️ **Solve locally:** [practice_local.py → Q22](./practice_local.py)

<details><summary>💡 Hint</summary>index=False prevents the DataFrame's row numbers from becoming an extra column in the DB table</details>
<details><summary>✅ Answer</summary>

```python
import pandas as pd
from sqlalchemy import create_engine

engine = create_engine("sqlite:///mydb.db")

df = pd.DataFrame({
    "product":  ["MacBook", "iPad", "AirPods", "Watch", "HomePod"],
    "units":    [42, 95, 380, 150, 30],
    "revenue":  [104958, 94980, 94962, 59985, 2999],
})

df.to_sql(
    name="sales",           # ← table name in the database
    con=engine,
    if_exists="replace",    # ← "replace" drops and recreates; "append" adds rows
    index=False,            # ← don't write DataFrame index as a DB column
    chunksize=1000          # ← write in batches (matters for large DataFrames)
)
print("Written to DB.")

df_back = pd.read_sql_query("SELECT * FROM sales", engine)
print(df_back)
```

**Why:** `if_exists="replace"` is useful during development; switch to `"append"` in production pipelines where you're adding new rows to an existing table.
</details>

---

### Q23 · Pandas + SQL — chunked read with chunksize 🟡

Use `pd.read_sql_query()` with `chunksize=2` to read a table in chunks. Iterate over the chunks and print the shape of each chunk. Explain why chunking matters for large tables.

> 🛠️ **Solve locally:** [practice_local.py → Q23](./practice_local.py)

<details><summary>💡 Hint</summary>When chunksize is set, read_sql_query returns an iterator of DataFrames instead of one big DataFrame</details>
<details><summary>✅ Answer</summary>

```python
import pandas as pd
from sqlalchemy import create_engine

engine = create_engine("sqlite:///mydb.db")

chunks = pd.read_sql_query(
    "SELECT * FROM products",
    engine,
    chunksize=2    # ← 2 rows per chunk (use 10_000+ in real pipelines)
)

for i, chunk in enumerate(chunks):
    print(f"Chunk {i}: shape={chunk.shape}")
    # Process chunk here: transform and write to another table

# Without chunking: entire result set loads into memory at once.
# For a 10M-row table this can crash the process.
# Chunking keeps memory bounded at the cost of multiple round trips.
```

**Why:** Without chunking, `read_sql_query` loads the entire result set into memory at once — chunking keeps memory bounded at the cost of multiple round trips to the database.
</details>

---

## Ch8 — DuckDB

### Q24 · DuckDB — in-process SQL on a DataFrame 🟡

Create a pandas DataFrame with 5 products (name, category, price). Use DuckDB to run a GROUP BY query on it (count and average price per category) without writing anything to disk. Return the result as a pandas DataFrame using `.df()`.

> 🛠️ **Solve locally:** [practice_local.py → Q24](./practice_local.py)

<details><summary>💡 Hint</summary>DuckDB references the Python variable name directly in SQL: FROM df — no file path, no to_sql() needed</details>
<details><summary>✅ Answer</summary>

```python
import duckdb
import pandas as pd

df = pd.DataFrame({
    "name":     ["MacBook Pro", "AirPods Pro", "iPad Pro", "AirPods Max", "Apple Watch"],
    "category": ["laptops",     "audio",       "tablets",  "audio",       "wearables"],
    "price":    [2499.99,       249.99,         999.99,     549.99,         399.99],
})

con = duckdb.connect()   # ← in-memory DuckDB instance

result = con.execute("""
    SELECT
        category,
        COUNT(*)             AS products,
        ROUND(AVG(price), 2) AS avg_price
    FROM df                  -- references the Python variable df directly
    GROUP BY category
    ORDER BY avg_price DESC
""").df()                    # ← .df() converts result to a pandas DataFrame

print(result)
con.close()
```

**Why:** DuckDB's killer feature is querying Python objects (DataFrames, lists) as if they were SQL tables — no serialization, no temp files, no overhead.
</details>

---

### Q25 · DuckDB — read_csv_auto direct file query 🟡

Use DuckDB's `read_csv_auto()` to query a CSV file with SQL directly — no `pd.read_csv()` needed. Filter rows where `price > 1000` and return the top 5 by price descending.

> 🛠️ **Solve locally:** [practice_local.py → Q25](./practice_local.py)

<details><summary>💡 Hint</summary>read_csv_auto('file.csv') auto-detects column types and treats the file like a SQL table</details>
<details><summary>✅ Answer</summary>

```python
import duckdb

con = duckdb.connect()

result = con.execute("""
    SELECT *
    FROM read_csv_auto('products.csv')   -- auto-infers schema from the file
    WHERE price > 1000
    ORDER BY price DESC
    LIMIT 5
""").df()

print(result)
con.close()

# Same pattern works for Parquet:
# FROM read_parquet('data.parquet')
```

**Why:** `read_csv_auto()` lets you run SQL on files without loading them into memory first — DuckDB streams the file and applies the filter/limit before returning results, which is far more memory-efficient than `pd.read_csv()` followed by a filter.
</details>

---

### Q26 · DuckDB — DuckDB vs sqlite3 performance tradeoff 🟠

Explain with a short code comparison when DuckDB outperforms sqlite3 and when sqlite3 is the better choice. Show the DuckDB columnar advantage for a GROUP BY aggregation vs sqlite3's row-store.

> 🛠️ **Solve locally:** [practice_local.py → Q26](./practice_local.py)

<details><summary>💡 Hint</summary>DuckDB = OLAP (column-store, analytics); sqlite3 = OLTP (row-store, transactions, concurrent writes)</details>
<details><summary>✅ Answer</summary>

```python
# sqlite3 wins at: OLTP, single-row transactions, concurrent writes, small data
import sqlite3
with sqlite3.connect("app.db") as conn:
    conn.execute(
        "INSERT INTO events (user_id, action) VALUES (?, ?)", (42, "click")
    )
    conn.commit()
# Row-store: each INSERT writes one row efficiently

# DuckDB wins at: OLAP, analytics, GROUP BY, aggregations, DataFrames, Parquet
import duckdb, pandas as pd
df = pd.read_csv("100m_events.csv")   # 100M rows
con = duckdb.connect()
result = con.execute("""
    SELECT action, COUNT(*), AVG(value)
    FROM df
    GROUP BY action
""").df()
# DuckDB reads only the 'action' and 'value' columns (columnar skip)
# sqlite3 would read every column of every row for the same query

# Summary:
# sqlite3  -> one engineer, small data, ACID transactions, no extra deps
# DuckDB   -> analytics, DataFrames, Parquet, GROUP BY on millions of rows
```

**Why:** Columnar storage means DuckDB reads only the columns needed for a query. A GROUP BY on 2 of 50 columns reads 4% of the data. Row-store databases like sqlite3 must read all 50 columns for every row scanned.
</details>

---

## Ch9 — Transactions and ACID

### Q27 · Transactions — explicit BEGIN/COMMIT pattern 🟡

Write a function `transfer_funds(conn, from_id, to_id, amount)` that debits one account and credits another inside an explicit `BEGIN ... COMMIT` transaction. Both updates must succeed or neither should persist.

> 🛠️ **Solve locally:** [practice_local.py → Q27](./practice_local.py)

<details><summary>💡 Hint</summary>conn.execute("BEGIN") starts the transaction; conn.execute("COMMIT") ends it — if any execute() raises, call ROLLBACK</details>
<details><summary>✅ Answer</summary>

```python
import sqlite3

def transfer_funds(conn, from_id, to_id, amount):
    conn.execute("BEGIN")                      # ← start transaction explicitly
    try:
        conn.execute(
            "UPDATE accounts SET balance = balance - ? WHERE id = ?",
            (amount, from_id)
        )
        conn.execute(
            "UPDATE accounts SET balance = balance + ? WHERE id = ?",
            (amount, to_id)
        )
        conn.execute("COMMIT")                 # ← persist both changes atomically
        print(f"Transferred ${amount} from {from_id} to {to_id}")
    except Exception as e:
        conn.execute("ROLLBACK")               # ← undo both if either fails
        print(f"Transfer failed: {e}")

conn = sqlite3.connect(":memory:")
conn.execute("CREATE TABLE accounts (id INTEGER, balance REAL)")
conn.executemany("INSERT INTO accounts VALUES (?,?)", [(1, 1000.0), (2, 500.0)])
conn.commit()
transfer_funds(conn, from_id=1, to_id=2, amount=200.0)
```

**Why:** The BEGIN/COMMIT wrapper ensures atomicity — if the credit UPDATE fails after the debit UPDATE, ROLLBACK undoes the debit too. Without it, money vanishes from account 1 with nothing added to account 2.
</details>

---

### Q28 · Transactions — rollback on error 🟡

Demonstrate a transaction that fails mid-way (e.g., inserting a duplicate UNIQUE value). Show that ROLLBACK restores the previous state and no partial data is committed.

> 🛠️ **Solve locally:** [practice_local.py → Q28](./practice_local.py)

<details><summary>💡 Hint</summary>Use a UNIQUE constraint on a column, then try inserting a duplicate inside a transaction to trigger a rollback</details>
<details><summary>✅ Answer</summary>

```python
import sqlite3

conn = sqlite3.connect(":memory:")
conn.execute("CREATE TABLE users (id INTEGER, email TEXT UNIQUE)")
conn.execute("INSERT INTO users VALUES (1, 'alice@x.com')")
conn.commit()

try:
    conn.execute("BEGIN")
    conn.execute("INSERT INTO users VALUES (2, 'bob@x.com')")      # ← succeeds
    conn.execute("INSERT INTO users VALUES (3, 'alice@x.com')")    # ← UNIQUE violation!
    conn.execute("COMMIT")
except Exception as e:
    conn.execute("ROLLBACK")     # ← bob@x.com is also rolled back (atomicity)
    print(f"Rolled back: {e}")

# Verify: only alice@x.com remains
rows = conn.execute("SELECT * FROM users").fetchall()
print(rows)   # [(1, 'alice@x.com')] — bob was rolled back too
conn.close()
```

**Why:** Atomicity means the entire transaction is treated as one unit — when the second INSERT fails, the ROLLBACK undoes the first INSERT too, even though it succeeded on its own.
</details>

---

### Q29 · Transactions — savepoint nested rollback 🟠

Use `SAVEPOINT` to create a partial rollback within a transaction: insert three rows, set a savepoint after the second, insert a third that "fails" (you simulate this), roll back to the savepoint, then commit the first two rows only.

> 🛠️ **Solve locally:** [practice_local.py → Q29](./practice_local.py)

<details><summary>💡 Hint</summary>SAVEPOINT name; ... ROLLBACK TO SAVEPOINT name; RELEASE SAVEPOINT name; — savepoints are nested checkpoints inside a transaction</details>
<details><summary>✅ Answer</summary>

```python
import sqlite3

conn = sqlite3.connect(":memory:")
conn.execute("CREATE TABLE log (msg TEXT)")

conn.execute("BEGIN")
conn.execute("INSERT INTO log VALUES (?)", ("row 1",))
conn.execute("INSERT INTO log VALUES (?)", ("row 2",))

conn.execute("SAVEPOINT sp1")              # ← checkpoint after row 2
conn.execute("INSERT INTO log VALUES (?)", ("row 3 — will be undone",))

# Simulate a failure: roll back to the savepoint
conn.execute("ROLLBACK TO SAVEPOINT sp1") # ← undoes row 3, row 1 and 2 are safe
conn.execute("RELEASE SAVEPOINT sp1")     # ← remove the savepoint

conn.execute("COMMIT")                    # ← commit row 1 and row 2 only

rows = conn.execute("SELECT * FROM log").fetchall()
print(rows)   # [('row 1',), ('row 2',)]
conn.close()
```

**Why:** Savepoints let you undo part of a transaction without losing all the work — useful in long multi-step operations where only the last step failed.
</details>

---

## Ch10 — Indexes and Performance

### Q30 · Indexes — CREATE INDEX single column 🟢

Create an index on the `category` column of the `products` table. Name it `idx_products_category`. Then create a composite index on `(category, price)` named `idx_cat_price`.

> 🛠️ **Solve locally:** [practice_local.py → Q30](./practice_local.py)

<details><summary>💡 Hint</summary>CREATE INDEX IF NOT EXISTS idx_name ON table(column) — composite index column order matters for the left-prefix rule</details>
<details><summary>✅ Answer</summary>

```python
import sqlite3

with sqlite3.connect("mydb.db") as conn:
    # Single-column index — speeds up WHERE category = ?
    conn.execute(
        "CREATE INDEX IF NOT EXISTS idx_products_category ON products(category)"
    )

    # Composite index — speeds up WHERE category = ? AND price > ?
    # Left-prefix rule: also helps queries that filter only on category
    conn.execute(
        "CREATE INDEX IF NOT EXISTS idx_cat_price ON products(category, price)"
    )

    conn.commit()
    print("Indexes created.")
```

**Why:** An index on `category` turns a full O(n) table scan into an O(log n) B-tree lookup. The composite `(category, price)` index also satisfies queries that only filter on `category` (the left prefix) — but not queries that only filter on `price` alone.
</details>

---

### Q31 · Indexes — EXPLAIN QUERY PLAN before/after 🟡

Run `EXPLAIN QUERY PLAN` on a query filtering by `category` before and after creating an index. Print both plans and explain what the output difference means.

> 🛠️ **Solve locally:** [practice_local.py → Q31](./practice_local.py)

<details><summary>💡 Hint</summary>Without an index, the plan shows "SCAN products"; with an index, it shows "SEARCH products USING INDEX"</details>
<details><summary>✅ Answer</summary>

```python
import sqlite3

with sqlite3.connect(":memory:") as conn:
    conn.execute("""
        CREATE TABLE products (
            id INTEGER PRIMARY KEY, name TEXT, price REAL, category TEXT
        )
    """)
    conn.executemany(
        "INSERT INTO products (name, price, category) VALUES (?,?,?)",
        [("MacBook", 2499, "laptops"), ("iPad", 999, "tablets"), ("AirPods", 249, "audio")]
    )

    # Plan WITHOUT index
    plan_before = conn.execute(
        "EXPLAIN QUERY PLAN SELECT * FROM products WHERE category = 'laptops'"
    ).fetchall()
    print("Without index:", plan_before)
    # -> SCAN products  (reads every row)

    conn.execute("CREATE INDEX idx_cat ON products(category)")

    # Plan WITH index
    plan_after = conn.execute(
        "EXPLAIN QUERY PLAN SELECT * FROM products WHERE category = 'laptops'"
    ).fetchall()
    print("With index:", plan_after)
    # -> SEARCH products USING INDEX idx_cat (reads only matching rows)
```

**Why:** `EXPLAIN QUERY PLAN` is your debugging tool for slow queries — "SCAN" means full table scan (slow at scale); "SEARCH USING INDEX" means the optimizer found your index (fast).
</details>

---

### Q32 · Indexes — covering index (composite) 🟠

Explain what a covering index is. Create a composite index on `(category, price, name)` for a query that selects only `name` and `price` filtered by `category`. Show via `EXPLAIN QUERY PLAN` that the query is satisfied entirely by the index without touching the table.

> 🛠️ **Solve locally:** [practice_local.py → Q32](./practice_local.py)

<details><summary>💡 Hint</summary>A covering index contains all columns needed by the query — the DB reads only the index, never the table rows</details>
<details><summary>✅ Answer</summary>

```python
import sqlite3

with sqlite3.connect(":memory:") as conn:
    conn.execute("""
        CREATE TABLE products (
            id INTEGER PRIMARY KEY, name TEXT, price REAL, category TEXT, stock INTEGER
        )
    """)
    conn.executemany(
        "INSERT INTO products VALUES (?,?,?,?,?)",
        [(1,"MacBook",2499,"laptops",10),(2,"iPad",999,"tablets",20),(3,"AirPods",249,"audio",50)]
    )

    # Covering index: includes all columns the query needs
    conn.execute("CREATE INDEX idx_covering ON products(category, price, name)")

    plan = conn.execute("""
        EXPLAIN QUERY PLAN
        SELECT name, price
        FROM products
        WHERE category = 'laptops'
    """).fetchall()
    print(plan)
    # -> SEARCH products USING COVERING INDEX idx_covering
    # "COVERING" means the index satisfies the query without reading the table
```

**Why:** A covering index stores all the data the query needs — the database reads only the (smaller) index structure and never touches the (larger) table rows, making the query significantly faster for high-frequency queries.
</details>

---

## Ch11 — Connection Pooling

### Q33 · Connection Pooling — pool_size + max_overflow 🟡

Create a SQLAlchemy engine for a PostgreSQL database with `pool_size=5`, `max_overflow=10`, and `pool_timeout=30`. Explain what each parameter controls.

> 🛠️ **Solve locally:** [practice_local.py → Q33](./practice_local.py)

<details><summary>💡 Hint</summary>pool_size = idle connections kept open; max_overflow = extra connections allowed under burst traffic; pool_timeout = wait time before raising an error</details>
<details><summary>✅ Answer</summary>

```python
from sqlalchemy import create_engine

engine = create_engine(
    "postgresql://user:pass@localhost/mydb",
    pool_size=5,        # ← keep 5 connections open permanently
    max_overflow=10,    # ← allow 10 extra connections under peak load (total: 15)
    pool_timeout=30,    # ← raise TimeoutError if no connection free after 30s
    pool_recycle=1800   # ← close and reopen connections after 30 min (prevents stale)
)

# Each with engine.connect() block borrows a connection from the pool
with engine.connect() as conn:
    result = conn.execute(text("SELECT 1"))
# Connection returned to pool on context manager exit — not closed
```

**Why:** Without pooling, every web request opens a new DB connection (5-20ms overhead). With `pool_size=5`, the first 5 requests are instant (borrow from pool); requests 6-15 open new connections up to `max_overflow`; request 16 waits up to `pool_timeout` seconds.
</details>

---

### Q34 · Connection Pooling — NullPool (no pooling) 🟡

Create a SQLAlchemy engine using `NullPool` — a pool that opens and closes a fresh connection on every request. Explain when you would intentionally disable connection pooling.

> 🛠️ **Solve locally:** [practice_local.py → Q34](./practice_local.py)

<details><summary>💡 Hint</summary>NullPool is used in multiprocessing/serverless contexts where persistent connections cause issues after fork()</details>
<details><summary>✅ Answer</summary>

```python
from sqlalchemy import create_engine
from sqlalchemy.pool import NullPool

# NullPool: no connections are kept open between requests
engine = create_engine(
    "postgresql://user:pass@localhost/mydb",
    poolclass=NullPool    # ← open fresh connection every time, close after use
)

# Use cases for NullPool:
# 1. Multiprocessing: forked child processes must not share parent's pool connections
# 2. Serverless / Lambda: each invocation is stateless, no persistent connections
# 3. Scripts / one-off jobs: connection reuse isn't worth the overhead
# 4. Testing: clean slate for each test

with engine.connect() as conn:
    result = conn.execute(text("SELECT 1"))
# connection is fully closed here — not returned to a pool
```

**Why:** Connection pooling assumes long-lived processes. In serverless (AWS Lambda) or multiprocessing scenarios, shared persistent connections cause race conditions or stale connection errors after `fork()` — NullPool eliminates those issues.
</details>

---

### Q35 · Connection Pooling — QueuePool with timeout 🟠

Demonstrate what happens when a SQLAlchemy pool is exhausted: set `pool_size=1`, `max_overflow=0`, and `pool_timeout=2`, then try to open two concurrent connections and show the `TimeoutError`. Explain how to tune these settings for a production web app.

> 🛠️ **Solve locally:** [practice_local.py → Q35](./practice_local.py)

<details><summary>💡 Hint</summary>QueuePool is the default pool class — hold one connection open in a context manager, then try to acquire a second to see the timeout</details>
<details><summary>✅ Answer</summary>

```python
from sqlalchemy import create_engine, text
from sqlalchemy.pool import QueuePool
import threading

engine = create_engine(
    "sqlite:///mydb.db",
    poolclass=QueuePool,
    pool_size=1,        # ← only 1 connection in the pool
    max_overflow=0,     # ← no overflow allowed
    pool_timeout=2      # ← raise after 2 seconds of waiting
)

# Hold the only connection open
with engine.connect() as conn1:
    print("conn1 acquired")
    try:
        # Try to acquire a second connection — pool is empty
        with engine.connect() as conn2:   # ← waits pool_timeout seconds, then raises
            print("conn2 acquired")
    except Exception as e:
        print(f"Pool exhausted: {type(e).__name__}")   # TimeoutError

# Production tuning guidance:
# pool_size    = average concurrent DB connections your app needs
# max_overflow = burst capacity (2-3x pool_size is common)
# pool_timeout = 10-30s for web apps (fail fast vs. queue indefinitely)
# pool_recycle = 1800s to avoid "server has gone away" errors
```

**Why:** `pool_timeout` prevents requests from waiting forever when the pool is exhausted — it surfaces the bottleneck immediately so you can scale `pool_size` or add read replicas, rather than silently queuing requests until the app crashes.
</details>

---

## Navigation

**[Back to README](../README.md)**

**Prev:** [Web Scraping](../29_web_scraping/theory.md) | **Next:** [File Formats: PDF & XML](../31_file_formats_pdf_xml/theory.md)

**Related Topics:** [Theory](./theory.md) · [Cheat Sheet](./cheetsheet.md) · [Interview Q&A](./interview.md)
