# ETL Pipelines — Theory
File Processing, Memory-Efficient ETL, Schema Validation, Error Handling

---

## Learning Priority

**Must Learn**: Extract-Transform-Load flow, generator-based pipelines, chunked file processing
**Should Learn**: schema validation (Pydantic), error handling in pipelines, checkpointing
**Good to Know**: Apache Airflow concepts, dbt, Spark basics
**Reference**: Great Expectations, Prefect, dagster

---

## 1. ETL Mental Model

Think of an ETL pipeline like a factory assembly line. Raw materials (your data) arrive at the dock (Extract). Workers on the line reshape and quality-check each piece (Transform). Finished goods go to the warehouse (Load).

```
RAW FILES → [Extract] → records → [Transform] → clean_records → [Load] → DB/file
              |                        |
           read CSV               validate +
           read API               normalize
```

The three stages are always separate functions. That separation lets you test each stage independently with small data.

**Extract** — pull data from files, APIs, or databases. Produce a stream of raw records.
**Transform** — clean, validate, convert types, enrich. Produce clean records.
**Load** — write to a database, file, or another system.

```python
def extract(filepath):          # ← stage 1: read only
    with open(filepath) as f:
        for line in f:
            yield line.strip()

def transform(records):         # ← stage 2: change only
    for raw in records:
        yield raw.upper()

def load(records, out_file):    # ← stage 3: write only
    for r in records:
        out_file.write(r + "\n")
```

---

## 2. File Processing Pipeline

Imagine reading a 10 GB CSV file on a laptop with 8 GB of RAM. If you load the whole file into a list, Python crashes. If you read one line at a time, you never use more than a few KB.

```python
import csv
from pathlib import Path

def read_csv_rows(filepath):
    """Yield one row dict at a time — never loads full file."""
    with open(filepath, newline="") as f:
        reader = csv.DictReader(f)
        for row in reader:
            yield dict(row)      # ← one row in memory, not all rows
```

**pathlib glob** finds all matching files without listing the whole directory:

```python
from pathlib import Path

data_dir = Path("/data/incoming")
for csv_file in data_dir.glob("*.csv"):   # ← lazy: yields one path at a time
    for row in read_csv_rows(csv_file):
        process(row)
```

JSON Lines (`.jsonl`) files — one JSON object per line — work the same way:

```python
import json

def read_jsonl(filepath):
    with open(filepath) as f:
        for line in f:
            yield json.loads(line)   # ← one object per line
```

---

## 3. Memory-Efficient ETL

Here is the key insight: a list comprehension builds the whole output at once. A generator expression builds it one item at a time. Same result, but the generator uses O(1) memory no matter how big the data is.

```python
# Bad — loads 1 million rows into RAM
rows = [transform(row) for row in data]

# Good — holds only one row at a time
rows = (transform(row) for row in data)
```

You can chain generators into a full pipeline. Nothing runs until the final consumer (like `list()` or a `for` loop) pulls from it:

```python
def cast_types(records):
    for r in records:
        yield {"id": int(r["id"]), "score": float(r["score"])}

def filter_active(records):
    return (r for r in records if r.get("active"))

def add_grade(records):
    for r in records:
        r["grade"] = "A" if r["score"] >= 90 else "B"
        yield r

# Wire the chain — nothing runs yet
pipeline = add_grade(filter_active(cast_types(read_csv_rows("data.csv"))))

# Consume: now all stages run together, one row at a time
for record in pipeline:
    write_to_db(record)
```

**Chunked processing** is the middle ground for aggregations. You can't `GROUP BY` with pure streaming (you'd need all rows to count them). Chunks give you bounded memory with the ability to do partial aggregations:

```python
def chunk(iterable, size):
    """Split any iterator into lists of `size` items."""
    batch = []
    for item in iterable:
        batch.append(item)
        if len(batch) >= size:
            yield batch
            batch = []           # ← clear the batch to free memory
    if batch:
        yield batch

# Process 50,000 rows in chunks of 1,000
for batch in chunk(read_csv_rows("big.csv"), size=1000):
    aggregate(batch)             # ← max 1,000 rows in RAM at any time
```

---

## 4. Schema Validation in ETL

Never trust input data. A CSV from a vendor might have wrong types, missing fields, or negative IDs. Pydantic v2 is the standard tool for row-level validation.

```python
from pydantic import BaseModel, field_validator

class UserRow(BaseModel):
    user_id: int
    name:    str
    email:   str
    score:   float

    @field_validator("score")
    @classmethod
    def score_in_range(cls, v):
        if not (0.0 <= v <= 100.0):
            raise ValueError(f"score out of range: {v}")
        return v

errors = []
valid_rows = []

for raw in read_csv_rows("users.csv"):
    try:
        row = UserRow(**raw)      # ← validates AND converts types
        valid_rows.append(row)
    except Exception as e:
        errors.append({"raw": raw, "error": str(e)})  # ← collect, don't crash
```

The important rule: never raise from inside a pipeline stage. Collect errors, log them, and continue.

---

## 5. Error Handling in Pipelines

A pipeline that crashes on row 50,000 of 100,000 is worse than useless — you have partial data and no idea what failed. The pattern is **dead-letter queue**: bad rows go to a separate error log instead of stopping the job.

```
           valid rows ──────────────────► [Load] ──► DB
[Transform] ─────────────────────────────────────────
           bad rows ────────────────────► [DLQ]  ──► error.jsonl
```

```python
import json

def transform_with_dlq(records, dlq_path):
    """Yield clean records; write failures to dead-letter file."""
    with open(dlq_path, "a") as dlq:
        for raw in records:
            try:
                yield validate_and_transform(raw)
            except Exception as e:
                dlq.write(json.dumps({"raw": raw, "error": str(e)}) + "\n")
```

Two strategies for what to do with bad rows:

| Strategy | When to use |
|---|---|
| **Skip** (soft fail) | Non-critical data, high volume, occasional bad rows expected |
| **Fail-fast** | Critical data, any bad row means something is wrong upstream |

---

## 6. Checkpointing

Long-running pipelines need to know where they stopped if they crash. Checkpointing saves the last successfully processed record ID or file name to disk, so the next run resumes from there instead of starting over.

```python
import json
from pathlib import Path

class Checkpoint:
    """Save/load the last-processed row ID to disk."""

    def __init__(self, path):
        self._path = Path(path)

    def load(self):
        if self._path.exists():
            return json.loads(self._path.read_text())["last_id"]
        return 0              # ← first run: start from beginning

    def save(self, last_id):
        self._path.write_text(json.dumps({"last_id": last_id}))

cp = Checkpoint("checkpoint.json")
start_id = cp.load()

for row in read_csv_rows("data.csv"):
    if int(row["id"]) <= start_id:
        continue              # ← skip already-processed rows
    process(row)
    cp.save(int(row["id"]))   # ← update after every row (or every N rows)
```

---

## 7. Common Mistakes

**Loading everything into memory** — the classic beginner mistake:

```python
# Wrong
all_rows = list(csv.DictReader(open("big.csv")))   # crashes on large files

# Right
for row in csv.DictReader(open("big.csv")):        # one row at a time
    process(row)
```

**No error rows** — one bad record crashes the whole job:

```python
# Wrong
for row in records:
    clean = validate(row)   # raises on bad row → job dies

# Right
for row in records:
    try:
        yield validate(row)
    except Exception as e:
        log.warning("bad row: %s — %s", row, e)
```

**No logging** — when a pipeline silently skips 30% of rows, you won't notice:

```python
# Right: always log stats at the end
log.info("processed %d rows, skipped %d, wrote %d", total, skipped, written)
```

---

## Navigation

| | |
|---|---|
| Root Theory | [../theory.md](../theory.md) |
| Practice | [practice.md](./practice.md) |
| Streaming | [../02_streaming_api_collection/theory.md](../02_streaming_api_collection/theory.md) |
| Cheetsheet | [../cheetsheet.md](../cheetsheet.md) |

**[Back to README](../../README.md)**

**Prev:** [Root Theory](../theory.md) &nbsp;|&nbsp; **Next:** [Streaming & API Collection](../02_streaming_api_collection/theory.md)

**Related Topics:** [Generators & Iterators](../../11_generators_iterators/theory.md) · [File Handling](../../08_file_handling/theory.md) · [Type Hints & Pydantic](../../14_type_hints_and_pydantic/theory.md)
