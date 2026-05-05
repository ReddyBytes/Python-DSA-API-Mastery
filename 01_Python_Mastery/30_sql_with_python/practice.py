"""
SQL with Python — Practice
==========================
Build a mini analytics database from scratch.
Covers: sqlite3 CRUD, joins, aggregations, transactions,
        SQLAlchemy ORM, and pandas integration.

Run this file directly:
    python practice.py

Requirements:
    pip install sqlalchemy pandas

DuckDB section (optional):
    pip install duckdb
"""

import sqlite3
import os
import pandas as pd
from sqlalchemy import create_engine, Column, Integer, String, Float, ForeignKey, text
from sqlalchemy.orm import DeclarativeBase, Session, relationship

# ---------------------------------------------------------------------------
# Database path — use a temp file so re-runs start fresh
# ---------------------------------------------------------------------------
DB_PATH = "/tmp/analytics_practice.db"

if os.path.exists(DB_PATH):
    os.remove(DB_PATH)  # ← start clean on every run

print("=" * 60)
print("SQL with Python — Mini Analytics Database")
print("=" * 60)


# ---------------------------------------------------------------------------
# PART 1: sqlite3 — Schema and CRUD
# ---------------------------------------------------------------------------
print("\n--- Part 1: sqlite3 CRUD ---")

with sqlite3.connect(DB_PATH) as conn:
    conn.row_factory = sqlite3.Row  # ← dict-style access by column name

    # Create tables
    conn.executescript("""
        CREATE TABLE IF NOT EXISTS categories (
            id   INTEGER PRIMARY KEY AUTOINCREMENT,
            name TEXT    NOT NULL UNIQUE
        );

        CREATE TABLE IF NOT EXISTS products (
            id          INTEGER PRIMARY KEY AUTOINCREMENT,
            name        TEXT    NOT NULL,
            price       REAL    NOT NULL,
            stock       INTEGER DEFAULT 0,
            category_id INTEGER REFERENCES categories(id)
        );

        CREATE TABLE IF NOT EXISTS customers (
            id    INTEGER PRIMARY KEY AUTOINCREMENT,
            name  TEXT NOT NULL,
            email TEXT UNIQUE
        );

        CREATE TABLE IF NOT EXISTS orders (
            id          INTEGER PRIMARY KEY AUTOINCREMENT,
            customer_id INTEGER REFERENCES customers(id),
            product_id  INTEGER REFERENCES products(id),
            quantity    INTEGER NOT NULL DEFAULT 1,
            order_date  TEXT    DEFAULT CURRENT_TIMESTAMP
        );
    """)
    conn.commit()
    print("Tables created.")

    # INSERT categories
    categories = [("Electronics",), ("Audio",), ("Wearables",), ("Tablets",)]
    conn.executemany("INSERT INTO categories (name) VALUES (?)", categories)

    # INSERT products (parameterized — injection-safe)
    products = [
        ("MacBook Pro",  2499.99, 10, 1),
        ("MacBook Air",  1299.99, 15, 1),
        ("iPad Pro",      999.99, 20, 4),
        ("AirPods Pro",   249.99, 50, 2),
        ("AirPods Max",   549.99, 12, 2),
        ("Apple Watch",   399.99, 30, 3),
        ("iPhone 15",    1199.99, 25, 1),
        ("HomePod mini",   99.99,  8, 1),
    ]
    conn.executemany(
        "INSERT INTO products (name, price, stock, category_id) VALUES (?, ?, ?, ?)",
        products
    )

    # INSERT customers
    customers_data = [
        ("Alice Chen",    "alice@example.com"),
        ("Bob Martinez",  "bob@example.com"),
        ("Carol White",   "carol@example.com"),
        ("Dave Kim",      "dave@example.com"),
        ("Eve Johnson",   None),               # ← customer with no email
    ]
    conn.executemany("INSERT INTO customers (name, email) VALUES (?, ?)", customers_data)

    # INSERT orders
    orders_data = [
        (1, 1, 1),  # Alice → MacBook Pro
        (1, 4, 2),  # Alice → 2x AirPods Pro
        (2, 3, 1),  # Bob   → iPad Pro
        (2, 5, 1),  # Bob   → AirPods Max
        (3, 6, 1),  # Carol → Apple Watch
        (3, 7, 1),  # Carol → iPhone 15
        (4, 4, 3),  # Dave  → 3x AirPods Pro
        # Eve has no orders — will show up as NULL in LEFT JOIN
    ]
    conn.executemany(
        "INSERT INTO orders (customer_id, product_id, quantity) VALUES (?, ?, ?)",
        orders_data
    )
    conn.commit()
    print("Seed data inserted.")


# ---------------------------------------------------------------------------
# PART 2: SQL Queries
# ---------------------------------------------------------------------------
print("\n--- Part 2: SQL Queries ---")

with sqlite3.connect(DB_PATH) as conn:
    conn.row_factory = sqlite3.Row

    # WHERE + ORDER BY + LIMIT
    print("\nTop 3 most expensive products:")
    rows = conn.execute("""
        SELECT name, price
        FROM products
        ORDER BY price DESC
        LIMIT 3
    """).fetchall()
    for r in rows:
        print(f"  {r['name']}: ${r['price']:.2f}")

    # GROUP BY + HAVING
    print("\nCategories with more than 1 product (avg price):")
    rows = conn.execute("""
        SELECT c.name AS category, COUNT(p.id) AS n, ROUND(AVG(p.price), 2) AS avg_price
        FROM categories c
        JOIN products p ON p.category_id = c.id
        GROUP BY c.name
        HAVING n > 1
        ORDER BY avg_price DESC
    """).fetchall()
    for r in rows:
        print(f"  {r['category']}: {r['n']} products, avg ${r['avg_price']:.2f}")

    # Subquery — products more expensive than average
    avg = conn.execute("SELECT AVG(price) FROM products").fetchone()[0]
    print(f"\nProducts above average price (${avg:.2f}):")
    rows = conn.execute("""
        SELECT name, price
        FROM products
        WHERE price > (SELECT AVG(price) FROM products)
        ORDER BY price DESC
    """).fetchall()
    for r in rows:
        print(f"  {r['name']}: ${r['price']:.2f}")


# ---------------------------------------------------------------------------
# PART 3: JOINs
# ---------------------------------------------------------------------------
print("\n--- Part 3: JOINs ---")

with sqlite3.connect(DB_PATH) as conn:
    conn.row_factory = sqlite3.Row

    # INNER JOIN — customers who placed orders + what they bought
    print("\nINNER JOIN — customers with orders:")
    rows = conn.execute("""
        SELECT c.name AS customer, p.name AS product, o.quantity
        FROM orders o
        INNER JOIN customers c ON c.id = o.customer_id  -- ← only matched rows
        INNER JOIN products  p ON p.id = o.product_id
        ORDER BY c.name
    """).fetchall()
    for r in rows:
        print(f"  {r['customer']} → {r['product']} x{r['quantity']}")

    # LEFT JOIN — ALL customers, including those with no orders
    print("\nLEFT JOIN — all customers (NULLs for those with no orders):")
    rows = conn.execute("""
        SELECT c.name AS customer, p.name AS product
        FROM customers c
        LEFT JOIN orders   o ON o.customer_id = c.id   -- ← all customers appear
        LEFT JOIN products p ON p.id = o.product_id
        ORDER BY c.name
    """).fetchall()
    for r in rows:
        product = r["product"] if r["product"] else "(no orders)"
        print(f"  {r['customer']}: {product}")


# ---------------------------------------------------------------------------
# PART 4: Aggregation with JOINs — revenue per customer
# ---------------------------------------------------------------------------
print("\n--- Part 4: Revenue Per Customer ---")

with sqlite3.connect(DB_PATH) as conn:
    conn.row_factory = sqlite3.Row

    rows = conn.execute("""
        SELECT
            c.name AS customer,
            COUNT(o.id)                          AS order_count,
            SUM(p.price * o.quantity)            AS total_revenue,
            ROUND(AVG(p.price * o.quantity), 2)  AS avg_order_value
        FROM customers c
        LEFT JOIN orders   o ON o.customer_id = c.id
        LEFT JOIN products p ON p.id = o.product_id
        GROUP BY c.name
        ORDER BY total_revenue DESC
    """).fetchall()

    print(f"\n{'Customer':<15} {'Orders':>6} {'Revenue':>10} {'Avg Order':>10}")
    print("-" * 45)
    for r in rows:
        rev = f"${r['total_revenue']:.2f}" if r["total_revenue"] else "$0.00"
        avg = f"${r['avg_order_value']:.2f}" if r["avg_order_value"] else "-"
        print(f"  {r['customer']:<13} {r['order_count']:>6} {rev:>10} {avg:>10}")


# ---------------------------------------------------------------------------
# PART 5: Transactions — safe inventory update
# ---------------------------------------------------------------------------
print("\n--- Part 5: Transactions ---")

def place_order(db_path, customer_id, product_id, quantity):
    """Place an order atomically: check stock, deduct inventory, insert order."""
    conn = sqlite3.connect(db_path)
    try:
        conn.execute("BEGIN")

        # Check current stock
        row = conn.execute(
            "SELECT name, stock FROM products WHERE id = ?", (product_id,)
        ).fetchone()

        if row is None:
            raise ValueError(f"Product {product_id} not found")

        name, stock = row
        if stock < quantity:
            raise ValueError(f"Insufficient stock for {name}: have {stock}, need {quantity}")

        # Deduct stock
        conn.execute(
            "UPDATE products SET stock = stock - ? WHERE id = ?",
            (quantity, product_id)
        )

        # Insert order
        conn.execute(
            "INSERT INTO orders (customer_id, product_id, quantity) VALUES (?, ?, ?)",
            (customer_id, product_id, quantity)
        )

        conn.execute("COMMIT")
        print(f"  Order placed: customer {customer_id} bought {quantity}x {name}")

    except ValueError as e:
        conn.execute("ROLLBACK")  # ← undo stock deduction if order fails
        print(f"  Order failed (rolled back): {e}")

    finally:
        conn.close()

# Successful order
place_order(DB_PATH, customer_id=5, product_id=4, quantity=2)   # Eve buys 2 AirPods Pro

# This should fail — HomePod mini only has 8 in stock
place_order(DB_PATH, customer_id=1, product_id=8, quantity=100)

# Verify stock after transactions
with sqlite3.connect(DB_PATH) as conn:
    row = conn.execute("SELECT name, stock FROM products WHERE id = 4").fetchone()
    print(f"  AirPods Pro stock after transaction: {row[1]}")


# ---------------------------------------------------------------------------
# PART 6: SQLAlchemy ORM
# ---------------------------------------------------------------------------
print("\n--- Part 6: SQLAlchemy ORM ---")

ORM_DB = "sqlite:////tmp/orm_practice.db"

if os.path.exists("/tmp/orm_practice.db"):
    os.remove("/tmp/orm_practice.db")


class Base(DeclarativeBase):
    pass


class Category(Base):
    __tablename__ = "categories"
    id       = Column(Integer, primary_key=True, autoincrement=True)
    name     = Column(String, nullable=False, unique=True)
    products = relationship("Product", back_populates="category")  # ← bidirectional

    def __repr__(self):
        return f"<Category(name={self.name!r})>"


class Product(Base):
    __tablename__ = "products"
    id          = Column(Integer, primary_key=True, autoincrement=True)
    name        = Column(String, nullable=False)
    price       = Column(Float, nullable=False)
    category_id = Column(Integer, ForeignKey("categories.id"))
    category    = relationship("Category", back_populates="products")

    def __repr__(self):
        return f"<Product(name={self.name!r}, price={self.price})>"


engine = create_engine(ORM_DB, echo=False)  # ← echo=True shows SQL queries
Base.metadata.create_all(engine)            # ← creates tables

# INSERT via ORM
with Session(engine) as session:
    electronics = Category(name="Electronics")
    audio       = Category(name="Audio")
    session.add_all([electronics, audio])
    session.flush()  # ← assigns IDs without committing

    products_orm = [
        Product(name="MacBook Pro", price=2499.99, category=electronics),
        Product(name="AirPods Pro", price=249.99,  category=audio),
        Product(name="AirPods Max", price=549.99,  category=audio),
    ]
    session.add_all(products_orm)
    session.commit()
    print("ORM: inserted categories and products")

# QUERY via ORM
with Session(engine) as session:
    # All products ordered by price
    all_p = session.query(Product).order_by(Product.price.desc()).all()
    print("\nAll products (ORM query):")
    for p in all_p:
        print(f"  {p.name}: ${p.price:.2f} [{p.category.name}]")

    # Filter
    audio_products = session.query(Product).join(Category).filter(
        Category.name == "Audio"
    ).all()
    print(f"\nAudio products: {[p.name for p in audio_products]}")

# UPDATE via ORM
with Session(engine) as session:
    product = session.query(Product).filter(Product.name == "MacBook Pro").first()
    product.price = 2299.99  # ← SQLAlchemy tracks this change
    session.commit()
    print(f"\nORM UPDATE: MacBook Pro new price = ${product.price}")

# DELETE via ORM
with Session(engine) as session:
    product = session.query(Product).filter(Product.name == "AirPods Max").first()
    session.delete(product)
    session.commit()
    remaining = session.query(Product).count()
    print(f"ORM DELETE: removed AirPods Max. Products remaining: {remaining}")


# ---------------------------------------------------------------------------
# PART 7: Pandas + SQL Integration
# ---------------------------------------------------------------------------
print("\n--- Part 7: Pandas + SQL ---")

sqlalchemy_engine = create_engine(f"sqlite:///{DB_PATH}")

# Read: database → DataFrame
df_products = pd.read_sql(
    "SELECT p.name, p.price, p.stock, c.name AS category FROM products p JOIN categories c ON c.id = p.category_id",
    sqlalchemy_engine
)
print("\nProducts DataFrame (from SQL):")
print(df_products.to_string(index=False))

# Aggregate in pandas
print("\nRevenue potential by category (price × stock):")
df_products["potential_revenue"] = df_products["price"] * df_products["stock"]
summary = df_products.groupby("category")["potential_revenue"].sum().sort_values(ascending=False)
print(summary.to_string())

# Write DataFrame back to database
df_summary = summary.reset_index()
df_summary.columns = ["category", "potential_revenue"]
df_summary["potential_revenue"] = df_summary["potential_revenue"].round(2)

df_summary.to_sql(
    name="revenue_summary",     # ← new table name
    con=sqlalchemy_engine,
    if_exists="replace",        # ← overwrite if exists
    index=False
)
print("\nWrote revenue_summary table back to DB via df.to_sql()")

# Verify by reading it back
df_check = pd.read_sql("SELECT * FROM revenue_summary ORDER BY potential_revenue DESC", sqlalchemy_engine)
print("\nVerification — revenue_summary table:")
print(df_check.to_string(index=False))


# ---------------------------------------------------------------------------
# PART 8: DuckDB (optional — install with: pip install duckdb)
# ---------------------------------------------------------------------------
print("\n--- Part 8: DuckDB (optional) ---")

try:
    import duckdb  # noqa: PLC0415

    con = duckdb.connect()  # ← in-memory DuckDB instance

    # Run SQL directly on a pandas DataFrame
    df = pd.DataFrame({
        "product":  ["MacBook Pro", "AirPods Pro", "iPad Pro", "AirPods Max", "Apple Watch"],
        "category": ["Electronics", "Audio",       "Tablets",  "Audio",       "Wearables"],
        "price":    [2499.99,        249.99,         999.99,     549.99,         399.99],
        "units_sold": [42, 380, 95, 61, 150],
    })

    # DuckDB references the Python variable `df` directly — no file needed
    result = con.execute("""
        SELECT
            category,
            COUNT(*)                            AS products,
            ROUND(AVG(price), 2)                AS avg_price,
            SUM(units_sold * price)             AS total_revenue
        FROM df
        GROUP BY category
        ORDER BY total_revenue DESC
    """).df()  # ← .df() returns a pandas DataFrame

    print("\nDuckDB — SQL on DataFrame:")
    print(result.to_string(index=False))

    # Filter query
    top = con.execute("""
        SELECT product, price, units_sold, ROUND(price * units_sold, 2) AS revenue
        FROM df
        WHERE price * units_sold > 50000
        ORDER BY revenue DESC
    """).df()

    print("\nHigh-revenue products (>$50k total):")
    print(top.to_string(index=False))

    con.close()

except ImportError:
    print("  duckdb not installed. Run: pip install duckdb")


# ---------------------------------------------------------------------------
# PART 9: Indexes and EXPLAIN
# ---------------------------------------------------------------------------
print("\n--- Part 9: Indexes and Query Plan ---")

with sqlite3.connect(DB_PATH) as conn:
    # Query plan WITHOUT index
    plan_without = conn.execute("""
        EXPLAIN QUERY PLAN
        SELECT * FROM products WHERE category_id = 2
    """).fetchall()
    print("\nQuery plan WITHOUT index:")
    for row in plan_without:
        print(f"  {row}")

    # Create index
    conn.execute("CREATE INDEX idx_products_category ON products(category_id)")
    conn.commit()

    # Query plan WITH index
    plan_with = conn.execute("""
        EXPLAIN QUERY PLAN
        SELECT * FROM products WHERE category_id = 2
    """).fetchall()
    print("\nQuery plan WITH index:")
    for row in plan_with:
        print(f"  {row}")
    print("  (Notice: now uses INDEX instead of full SCAN)")


# ---------------------------------------------------------------------------
# Summary
# ---------------------------------------------------------------------------
print("\n" + "=" * 60)
print("Practice complete.")
print("Concepts covered:")
print("  sqlite3:        connect, cursor, execute, fetchall, row_factory")
print("  CRUD:           CREATE TABLE, INSERT, SELECT, UPDATE, DELETE")
print("  SQL queries:    WHERE, ORDER BY, LIMIT, GROUP BY, HAVING, subqueries")
print("  JOINs:          INNER, LEFT (all 4 types explained)")
print("  Transactions:   BEGIN / COMMIT / ROLLBACK for atomicity")
print("  SQLAlchemy ORM: declarative models, Session, query, relationships")
print("  Pandas + SQL:   read_sql(), to_sql(), round-trip workflow")
print("  DuckDB:         SQL on DataFrames, in-process analytics")
print("  Indexes:        CREATE INDEX, EXPLAIN QUERY PLAN")
print("=" * 60)
