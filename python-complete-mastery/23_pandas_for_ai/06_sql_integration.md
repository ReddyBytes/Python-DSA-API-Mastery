# 🎯 SQL Integration — Moving Data Between Pandas and Databases

> A DataFrame in memory and a table in PostgreSQL hold the same kind of data — rows and columns. `pd.read_sql` and `to_sql` are the pipes between them.

Production data almost always lives in a database — PostgreSQL, MySQL, SQLite, or a cloud warehouse. Pandas is the computation layer; the database is the storage layer. **`pd.read_sql()`** pulls query results directly into a DataFrame, and **`df.to_sql()`** writes results back. The bridge between them is a **SQLAlchemy** connection engine that handles authentication, connection pooling, and dialect differences across databases. Mastering this interface means your data science work can operate directly on production data without manual CSV exports.

---

## pd.read_sql — Pulling Data From Any SQL Database

**`pd.read_sql()`** executes a SQL query and returns the results as a DataFrame. It works with any database that Python's DB-API 2.0 (via `sqlite3`) or **SQLAlchemy** supports.

```python
import pandas as pd
import sqlite3

# --- SQLite (no server needed, great for local datasets) ---
conn = sqlite3.connect("local_data.db")

df = pd.read_sql("SELECT * FROM training_samples LIMIT 1000", conn)
df = pd.read_sql(
    "SELECT prompt, completion, quality_score FROM samples WHERE quality_score >= 4",
    conn,
    parse_dates=["created_at"],  # ← auto-parse date columns
)

conn.close()
```

---

## SQLAlchemy — The Production-Grade Connector

For PostgreSQL, MySQL, or any production database, use **SQLAlchemy** to create an **engine** — a reusable connection factory. `pd.read_sql` accepts either a raw connection or an SQLAlchemy engine.

```python
from sqlalchemy import create_engine
import pandas as pd

# PostgreSQL connection string format:
# postgresql+psycopg2://user:password@host:port/database
engine = create_engine(
    "postgresql+psycopg2://ml_user:secret@db.prod.internal:5432/training_db"
)

# Basic read
df = pd.read_sql("SELECT * FROM features WHERE split = 'train'", engine)

# Parameterized query — ALWAYS use params, never f-string SQL (SQL injection risk)
df = pd.read_sql(
    "SELECT * FROM samples WHERE label = %(label)s AND quality >= %(min_q)s",
    engine,
    params={"label": "positive", "min_q": 3},
)

# Read entire table by name
df = pd.read_sql_table("feature_store", engine)  # ← table name, not SQL string
```

---

## to_sql — Writing DataFrames Back to a Database

**`to_sql()`** writes a DataFrame to a SQL table. The **`if_exists`** parameter controls what happens when the table already exists.

```python
# if_exists options:
# "fail"    — raise an error if table exists (safe default)
# "replace" — DROP the table and recreate it (destructive!)
# "append"  — add rows to existing table

# Write a clean DataFrame to PostgreSQL
df_clean.to_sql(
    name="clean_training_samples",
    con=engine,
    if_exists="replace",  # ← safe for dev; use "append" in production
    index=False,           # ← don't write the Pandas index as a column
    method="multi",        # ← batch INSERT — much faster than row-by-row
)

# Append new batch to existing table
df_new_batch.to_sql(
    name="feature_store",
    con=engine,
    if_exists="append",
    index=False,
    method="multi",
    chunksize=1000,         # ← write 1000 rows at a time
)
```

---

## Chunked SQL Reading — Handling Tables Larger Than RAM

When a table is larger than available memory, **chunked reading** processes it in batches. `pd.read_sql()` with `chunksize` returns an iterator of DataFrames.

```python
# Process a 50M-row table in 100K-row chunks
results = []

for chunk in pd.read_sql(
    "SELECT * FROM raw_events WHERE event_date >= '2024-01-01'",
    engine,
    chunksize=100_000,       # ← rows per chunk
    parse_dates=["event_date"],
):
    # Process each chunk independently
    chunk_clean = chunk[chunk["quality_score"] >= 3]
    chunk_clean["text_len"] = chunk_clean["text"].str.len()
    results.append(chunk_clean[chunk_clean["text_len"] > 50])

# Combine processed chunks
df_final = pd.concat(results, ignore_index=True)
print(f"Final rows: {len(df_final):,}")
```

For very large results, instead of collecting into a list, write each chunk directly to a file:

```python
first_chunk = True
for chunk in pd.read_sql("SELECT * FROM huge_table", engine, chunksize=50_000):
    chunk.to_parquet(
        f"output/chunk_{i}.parquet",  # ← write each chunk as a parquet file
        index=False,
    )
```

---

## Using sqlite3 for Local Prototyping

SQLite requires no server and is built into Python. It's ideal for prototyping data pipelines before connecting to PostgreSQL.

```python
import sqlite3
import pandas as pd

# Create and populate an in-memory SQLite database
conn = sqlite3.connect(":memory:")  # ← lives only in RAM

# Write a DataFrame to SQLite
df.to_sql("training_data", conn, if_exists="replace", index=False)

# Run SQL queries against it — useful for complex joins
query = """
    SELECT
        t.user_id,
        t.prompt,
        t.completion,
        m.model_version,
        AVG(r.rating) AS avg_rating
    FROM training_data t
    JOIN model_runs m ON t.run_id = m.id
    JOIN ratings r ON t.sample_id = r.sample_id
    GROUP BY t.user_id, t.prompt, t.completion, m.model_version
    HAVING AVG(r.rating) >= 4.0
"""
df_joined = pd.read_sql(query, conn)
conn.close()
```

---

## Real Use — Pull Training Data From PostgreSQL

This example combines everything above into a single end-to-end pattern: connect via **SQLAlchemy**, pull a filtered and randomly sampled subset of the training table, validate the result immediately after load, then write the processed version back. It's the pattern you'll repeat on almost every ML pipeline that reads from a relational database.

```python
from sqlalchemy import create_engine
import pandas as pd
import os

# Use environment variables for credentials — never hardcode
DB_URL = os.environ["TRAINING_DB_URL"]
engine = create_engine(DB_URL, pool_pre_ping=True)  # ← pool_pre_ping detects stale connections

# Pull balanced sample from training table
query = """
    SELECT
        s.text,
        s.label,
        s.quality_score,
        s.source_domain,
        s.created_at
    FROM training_samples s
    WHERE
        s.split = 'train'
        AND s.quality_score >= 3
        AND s.language = 'en'
        AND s.created_at >= '2024-01-01'
    ORDER BY RANDOM()    -- PostgreSQL random sample
    LIMIT 500000
"""

print("Pulling training data...")
df = pd.read_sql(query, engine, parse_dates=["created_at"])
print(f"Loaded {len(df):,} rows")

# Validate immediately after load
assert df["label"].notna().all(), "Null labels found"
assert df["text"].str.len().min() > 10, "Empty texts found"

# Write processed version back
df_processed = df.drop(columns=["created_at"])  # remove before training
df_processed.to_sql(
    "processed_training_v2",
    engine,
    if_exists="replace",
    index=False,
    method="multi",
    chunksize=5000,
)
print("Written to processed_training_v2")
```

---

## 🔁 Navigation

| | |
|---|---|
| 📖 Main Theory | [theory.md](./README.md) |
| ⚡ Cheatsheet | [cheatsheet.md](./cheatsheet.md) |
| 🏠 Module Home | [theory.md](./README.md) |
