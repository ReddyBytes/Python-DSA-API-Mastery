# ⚡ Data Engineering Applications — Cheetsheet

> Quick reference: ETL vs ELT, pandas I/O, chunked reading, pagination, pipeline skeleton, streaming generators, memory patterns, data quality checks.

---

## 🔄 Pipeline Patterns: ETL vs ELT

| | ETL | ELT |
|---|---|---|
| **Full name** | Extract → Transform → Load | Extract → Load → Transform |
| **Where transform** | Before loading (in pipeline) | After loading (in warehouse) |
| **Best for** | Sensitive data, legacy systems, small-medium data | Cloud DW (BigQuery/Snowflake), large data |
| **Tools** | Python, Airflow, Spark | dbt, BigQuery SQL, Snowflake SQL |
| **Latency** | Higher (transform before write) | Lower (load raw, transform later) |

```
ETL:  Source ──extract──► [transform] ──load──► Warehouse (clean data)
ELT:  Source ──extract──────────────── load──► Warehouse ──[transform]──► Views
```

---

## 📁 Pandas Read/Write Formats

| Format | Read | Write | Notes |
|---|---|---|---|
| CSV | `pd.read_csv("f.csv")` | `df.to_csv("f.csv", index=False)` | Universal, large files |
| Parquet | `pd.read_parquet("f.parquet")` | `df.to_parquet("f.parquet")` | Columnar, fast, compressed |
| JSON | `pd.read_json("f.json")` | `df.to_json("f.json")` | API responses |
| Excel | `pd.read_excel("f.xlsx")` | `df.to_excel("f.xlsx", index=False)` | Requires `openpyxl` |
| SQL | `pd.read_sql(query, engine)` | `df.to_sql("table", engine, if_exists="append")` | SQLAlchemy engine |
| Feather | `pd.read_feather("f.feather")` | `df.to_feather("f.feather")` | Fast IPC, in-memory |
| HDF5 | `pd.read_hdf("f.h5", key="df")` | `df.to_hdf("f.h5", key="df")` | Large numeric arrays |

```python
# Parquet with compression — best for large datasets
df.to_parquet("data.parquet", compression="snappy", engine="pyarrow")
df = pd.read_parquet("data.parquet", columns=["id", "name"])  # column pruning
```

---

## 🔀 Chunked Reading Pattern

```python
import pandas as pd

# Chunked CSV — never loads full file
def process_large_csv(path: str, chunk_size: int = 10_000):
    reader = pd.read_csv(path, chunksize=chunk_size)
    results = []

    for chunk in reader:
        # process each chunk independently
        processed = chunk[chunk["status"] == "active"]
        results.append(processed)

    return pd.concat(results, ignore_index=True)

# Chunked SQL query
for chunk in pd.read_sql("SELECT * FROM events", engine, chunksize=5000):
    process(chunk)

# Pure Python chunked file reader (no pandas)
def read_in_chunks(filepath: str, size: int = 1024 * 1024):
    with open(filepath, "rb") as f:
        while chunk := f.read(size):
            yield chunk
```

---

## 📄 API Pagination Patterns

### Offset/Page Pagination

```python
def fetch_all_offset(url: str, page_size: int = 100) -> list:
    results = []
    offset = 0

    while True:
        response = requests.get(url, params={"limit": page_size, "offset": offset})
        data = response.json()
        batch = data.get("items", [])
        if not batch:
            break
        results.extend(batch)
        offset += len(batch)

    return results
```

### Cursor Pagination (preferred for large datasets)

```python
def fetch_all_cursor(url: str, page_size: int = 100) -> list:
    results = []
    cursor = None

    while True:
        params = {"limit": page_size}
        if cursor:
            params["cursor"] = cursor

        response = requests.get(url, params=params)
        data = response.json()

        results.extend(data.get("items", []))
        cursor = data.get("next_cursor")

        if not cursor:
            break

    return results
```

| | Offset/Page | Cursor |
|---|---|---|
| Simple to implement | Yes | Slightly more complex |
| Consistent under inserts | No — items shift | Yes |
| Can jump to page N | Yes | No |
| Works with large data | Slow (OFFSET N scans) | Fast (WHERE id > cursor) |

---

## 🏗 File Processing Pipeline Skeleton

```python
import logging
from pathlib import Path

logger = logging.getLogger(__name__)

def extract(filepath: str) -> "generator":
    """Yields rows lazily — never loads full file."""
    with open(filepath) as f:
        header = f.readline().strip().split(",")
        for line in f:
            yield dict(zip(header, line.strip().split(",")))

def transform(row: dict) -> dict | None:
    """Returns transformed row or None to drop it."""
    if not row.get("id"):
        return None
    return {
        "id":    int(row["id"]),
        "name":  row["name"].strip().title(),
        "score": float(row.get("score", 0)),
    }

def load(rows: "Iterable", db_conn) -> int:
    """Batch insert — returns count loaded."""
    batch, count = [], 0
    for row in rows:
        batch.append(row)
        if len(batch) >= 1000:
            db_conn.executemany("INSERT INTO ...", batch)
            count += len(batch)
            batch.clear()
    if batch:
        db_conn.executemany("INSERT INTO ...", batch)
        count += len(batch)
    return count

def run_pipeline(filepath: str, db_conn):
    raw    = extract(filepath)
    clean  = (transform(r) for r in raw)      # generator chain
    valid  = (r for r in clean if r is not None)
    count  = load(valid, db_conn)
    logger.info("Loaded %d rows from %s", count, filepath)
```

---

## 🌊 Streaming with Generators

```python
# Generator pipeline — each step is lazy, memory O(1)
def read_lines(path):
    with open(path) as f:
        yield from f                     # one line at a time

def parse_json(lines):
    for line in lines:
        try:
            yield json.loads(line)
        except json.JSONDecodeError:
            continue                     # skip bad lines

def filter_active(records):
    return (r for r in records if r.get("active"))

def transform_record(records):
    for r in records:
        yield {"id": r["id"], "value": r["value"] * 2}

# Compose the pipeline — nothing runs until consumed
pipeline = transform_record(
             filter_active(
               parse_json(
                 read_lines("events.jsonl"))))

for record in pipeline:
    insert_to_db(record)
```

---

## 📊 Memory-Efficient Patterns Comparison

| Pattern | Memory | Speed | Use When |
|---|---|---|---|
| Load all into list | O(n) — full data | Fast random access | Small data fits in RAM |
| Generator pipeline | O(1) — one item | Slightly slower | Large files, streaming |
| Chunked pandas | O(chunk_size) | Good for tabular | CSV/SQL, needs pandas ops |
| Memory-mapped file | O(1) | Very fast reads | Large binary/array data |
| `__slots__` objects | Reduced ~30-50% | Slightly faster | Millions of small objects |

```python
# Memory-mapped file (large binary reads)
import mmap

with open("large.bin", "rb") as f:
    mm = mmap.mmap(f.fileno(), 0, access=mmap.ACCESS_READ)
    chunk = mm[0:1024]    # slice like bytes — OS-managed paging

# vs Generator (text/structured data)
rows = (process(line) for line in open("large.csv"))   # O(1) memory
```

---

## ✅ Common Data Quality Checks

```python
import pandas as pd

def run_quality_checks(df: pd.DataFrame, table: str) -> list[str]:
    issues = []

    # 1. Null checks
    null_counts = df.isnull().sum()
    for col, count in null_counts[null_counts > 0].items():
        issues.append(f"{table}.{col}: {count} nulls ({count/len(df):.1%})")

    # 2. Duplicate rows
    dupes = df.duplicated().sum()
    if dupes:
        issues.append(f"{table}: {dupes} duplicate rows")

    # 3. Schema / type validation
    for col in df.columns:
        if df[col].dtype == object:
            if df[col].str.strip().eq("").any():
                issues.append(f"{table}.{col}: contains empty strings")

    # 4. Range checks (custom)
    if "score" in df.columns:
        out_of_range = df[(df["score"] < 0) | (df["score"] > 100)]
        if len(out_of_range):
            issues.append(f"{table}.score: {len(out_of_range)} values out of [0,100]")

    # 5. Referential integrity (custom)
    # if "user_id" in df: check all user_ids exist in users table

    return issues

# Quick pandas checks
df.info()                          # dtypes + null counts
df.describe()                      # stats — spot outliers
df.isnull().sum()                  # per-column nulls
df.duplicated().sum()              # exact duplicate rows
df["col"].value_counts(dropna=False)  # distribution + nulls
```

---

## 📌 Learning Priority

**Must Learn** — daily use, interview essential:
ETL vs ELT · Batch vs streaming · Generators for memory efficiency · Idempotency · Retry with backoff

**Should Learn** — real projects:
Chunked pandas reading · Cursor pagination · Data quality checks · Pipeline skeleton pattern · Schema validation

**Good to Know** — specific situations:
Change Data Capture (CDC) · Stream windowing · Exactly-once semantics · Schema evolution (Avro/Protobuf)

**Reference** — know it exists:
OLAP vs OLTP · Slowly Changing Dimensions · Data lineage tools · GDPR compliance in pipelines

---

## 🔥 Rapid-Fire

```
Q: ETL vs ELT main difference?
A: ETL transforms before loading. ELT loads raw first, transforms in the warehouse.

Q: Why cursor pagination over offset?
A: Cursor is O(1) per page. OFFSET N scans N rows — slow on large tables.
   Also: cursor is consistent when rows are inserted between pages.

Q: Why generator pipeline over list comprehension for large files?
A: Generator: one item in memory at a time — O(1). List: entire output in RAM — O(n).

Q: Idempotency in pipelines?
A: Running the pipeline twice produces same result. Use upserts (INSERT ... ON CONFLICT UPDATE).

Q: When to use Parquet over CSV?
A: Parquet: columnar, compressed, column pruning — much faster for analytics.
   CSV: universal, human-readable — good for interchange.

Q: What is checkpointing?
A: Saving progress state (offset, timestamp) so a failed job can resume without reprocessing.
```

---

## 🧭 Navigation

| | |
|---|---|
| 📖 Theory | [theory.md](./theory.md) |
| 🎯 Interview | [interview.md](./interview.md) |
| ⬅️ Previous | [20 — System Design with Python](../20_system_design_with_python/cheetsheet.md) |
| ➡️ Next | [22 — NumPy for AI](../22_numpy_for_ai/cheatsheet.md) |

---

**[🏠 Back to README](../README.md)**

**Prev:** [← System Design with Python](../20_system_design_with_python/cheetsheet.md) &nbsp;|&nbsp; **Next:** [NumPy for AI →](../22_numpy_for_ai/cheatsheet.md)

**Related Topics:** [Theory](./theory.md) · [Interview Q&A](./interview.md)
