# ETL Pipelines — Practice
12 Questions · File Processing · Generators · Schema Validation · Error Handling · Checkpointing

---


## 📋 Quick Index

| # | Concept | Level |
|---|---------|-------|
| [Q1](#q1) | csv-reader — Write a simple CSV reader that yields rows | 🟢 |
| [Q2](#q2) | etl-functions — Write Extract, Transform, Load as 3 separate functions | 🟢 |
| [Q3](#q3) | chunked-csv — Process a large CSV in chunks of 1000 rows | 🟡 |
| [Q4](#q4) | pydantic-validation — Validate rows with Pydantic, collect validation errors | 🟡 |
| [Q5](#q5) | generator-pipeline — Write a full generator pipeline: extract → filter → transform → load | 🟡 |
| [Q6](#q6) | checkpointing — Add checkpointing: save the last-processed row ID to a file | 🟡 |
| [Q7](#q7) | dead-letter-queue — Write a dead-letter queue: send bad rows to an error log | 🟡 |
| [Q8](#q8) | jsonl-reader — Read a JSON Lines (.jsonl) file as a generator | 🟡 |
| [Q9](#q9) | parallel-processor — Write a parallel file processor using ProcessPoolExecutor | 🟠 |
| [Q10](#q10) | schema-migration — Build ETL with schema migration: old format → new format | 🟠 |
| [Q11](#q11) | memory-profile — Memory profile the ETL pipeline: generator vs list | 🟠 |
| [Q12](#q12) | capstone-etl — Capstone: full ETL from CSV to SQLite with error handling | 🟠 |

---

<a id="q1"></a>

### Q1 · csv-reader — Write a simple CSV reader that yields rows 🟢

> 🛠️ **Solve locally:** [practice_local.py → Q1](./practice_local.py)


Write a function `read_csv(filepath)` that opens a CSV file and **yields** one row as a `dict` at a time. Do not load the whole file into a list.


<details><summary>💡 Hint</summary>Use `csv.DictReader` inside a `with open(...)` block and `yield` each row.</details>
<details><summary>✅ Answer</summary>

```python
import csv

def read_csv(filepath):
    with open(filepath, newline="") as f:
        reader = csv.DictReader(f)
        for row in reader:
            yield dict(row)
```
**Why:** `csv.DictReader` is already an iterator — yielding from inside keeps memory at O(1) regardless of file size.
</details>

---

<a id="q2"></a>

### Q2 · etl-functions — Write Extract, Transform, Load as 3 separate functions 🟢

> 🛠️ **Solve locally:** [practice_local.py → Q2](./practice_local.py)


Write three functions: `extract(filepath)` that yields raw dicts from a CSV, `transform(records)` that strips whitespace from all string values, and `load(records, out_path)` that writes them to a new CSV. Wire them together.


<details><summary>💡 Hint</summary>Each function should be a generator except `load`, which consumes the stream and writes output.</details>
<details><summary>✅ Answer</summary>

```python
import csv

def extract(filepath):
    with open(filepath, newline="") as f:
        for row in csv.DictReader(f):
            yield dict(row)

def transform(records):
    for r in records:
        yield {k: v.strip() for k, v in r.items()}

def load(records, out_path):
    rows = list(records)
    if not rows:
        return 0
    with open(out_path, "w", newline="") as f:
        w = csv.DictWriter(f, fieldnames=rows[0].keys())
        w.writeheader()
        w.writerows(rows)
    return len(rows)

# Wire it
count = load(transform(extract("source.csv")), "output.csv")
```
**Why:** Separating E/T/L makes each stage independently testable with small in-memory data.
</details>

---

<a id="q3"></a>

### Q3 · chunked-csv — Process a large CSV in chunks of 1000 rows 🟡

> 🛠️ **Solve locally:** [practice_local.py → Q3](./practice_local.py)


Write a `chunk(iterable, size)` generator that splits any iterator into lists of `size` items. Then use it to process a CSV in batches of 1000, printing a count per chunk.


<details><summary>💡 Hint</summary>Accumulate items in a local list; `yield` it when it hits `size`, then reset the list.</details>
<details><summary>✅ Answer</summary>

```python
def chunk(iterable, size):
    batch = []
    for item in iterable:
        batch.append(item)
        if len(batch) >= size:
            yield batch
            batch = []
    if batch:
        yield batch

for i, batch in enumerate(chunk(read_csv("big.csv"), 1000), 1):
    print(f"Chunk {i}: {len(batch)} rows")
```
**Why:** Chunking bounds memory to O(chunk_size), enabling aggregations that pure streaming can't do.
</details>

---

<a id="q4"></a>

### Q4 · pydantic-validation — Validate rows with Pydantic, collect validation errors 🟡

> 🛠️ **Solve locally:** [practice_local.py → Q4](./practice_local.py)


Define a Pydantic `UserRow` model with fields `user_id: int`, `name: str`, `email: str`, `score: float` (0–100). Write a function that processes a list of raw dicts, returning `(valid_rows, error_rows)`.


<details><summary>💡 Hint</summary>Wrap `UserRow(**raw)` in `try/except ValidationError` and append to the appropriate list.</details>
<details><summary>✅ Answer</summary>

```python
from pydantic import BaseModel, field_validator, ValidationError

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

def validate_batch(rows):
    valid, errors = [], []
    for raw in rows:
        try:
            valid.append(UserRow(**raw))
        except ValidationError as e:
            errors.append({"raw": raw, "error": str(e)})
    return valid, errors
```
**Why:** Collecting errors (not raising) lets the pipeline process all rows and report failures in bulk.
</details>

---

<a id="q5"></a>

### Q5 · generator-pipeline — Write a full generator pipeline: extract → filter → transform → load 🟡

> 🛠️ **Solve locally:** [practice_local.py → Q5](./practice_local.py)


Chain four generator functions into a single pipeline: `extract` reads CSV rows, `filter_active` keeps only rows where `active == "true"`, `enrich` adds a `grade` field based on `score`, and `load_to_list` collects results.


<details><summary>💡 Hint</summary>Each middle stage takes an iterator and yields from it. Nothing runs until you consume the final stage.</details>
<details><summary>✅ Answer</summary>

```python
def filter_active(records):
    return (r for r in records if r.get("active", "").lower() == "true")

def enrich(records):
    for r in records:
        score = float(r.get("score", 0))
        r["grade"] = "A" if score >= 90 else ("B" if score >= 80 else "C")
        yield r

def load_to_list(records):
    return list(records)

result = load_to_list(enrich(filter_active(extract("data.csv"))))
```
**Why:** Generator chaining means only one record exists in memory across all stages at any moment.
</details>

---

<a id="q6"></a>

### Q6 · checkpointing — Add checkpointing: save the last-processed row ID to a file 🟡

> 🛠️ **Solve locally:** [practice_local.py → Q6](./practice_local.py)


Write a `Checkpoint` class with `load() -> int` (returns last ID, or 0 on first run) and `save(last_id: int)`. Use it in a processing loop to skip already-processed rows on restart.


<details><summary>💡 Hint</summary>Store state as JSON on disk. On load, return 0 if the file does not exist.</details>
<details><summary>✅ Answer</summary>

```python
import json
from pathlib import Path

class Checkpoint:
    def __init__(self, path):
        self._path = Path(path)

    def load(self):
        if self._path.exists():
            return json.loads(self._path.read_text())["last_id"]
        return 0

    def save(self, last_id):
        self._path.write_text(json.dumps({"last_id": last_id}))

cp = Checkpoint("checkpoint.json")
start = cp.load()

for row in read_csv("data.csv"):
    if int(row["id"]) <= start:
        continue
    process(row)
    cp.save(int(row["id"]))
```
**Why:** Checkpointing enables resume-from-failure without reprocessing records that already succeeded.
</details>

---

<a id="q7"></a>

### Q7 · dead-letter-queue — Write a dead-letter queue: send bad rows to an error log 🟡

> 🛠️ **Solve locally:** [practice_local.py → Q7](./practice_local.py)


Write `transform_with_dlq(records, dlq_path)` — a generator that yields clean records and writes failed rows to a `.jsonl` dead-letter file instead of crashing.


<details><summary>💡 Hint</summary>Open the DLQ file in append mode inside the generator. Write bad rows as JSON lines.</details>
<details><summary>✅ Answer</summary>

```python
import json

def transform_with_dlq(records, dlq_path):
    with open(dlq_path, "a") as dlq:
        for raw in records:
            try:
                yield validate_and_transform(raw)
            except Exception as e:
                entry = {"raw": raw, "error": str(e)}
                dlq.write(json.dumps(entry) + "\n")
```
**Why:** Writing failures to a separate file lets you inspect and replay them without blocking the main pipeline.
</details>

---

<a id="q8"></a>

### Q8 · jsonl-reader — Read a JSON Lines (.jsonl) file as a generator 🟡

> 🛠️ **Solve locally:** [practice_local.py → Q8](./practice_local.py)


Write `read_jsonl(filepath)` that yields one parsed dict per line, skipping lines that are not valid JSON.


<details><summary>💡 Hint</summary>Iterate over lines in the file; wrap `json.loads` in `try/except json.JSONDecodeError`.</details>
<details><summary>✅ Answer</summary>

```python
import json

def read_jsonl(filepath):
    with open(filepath) as f:
        for line in f:
            line = line.strip()
            if not line:
                continue
            try:
                yield json.loads(line)
            except json.JSONDecodeError:
                continue   # skip malformed lines
```
**Why:** JSONL is the standard format for log files and streaming data — one object per line, easy to append.
</details>

---

<a id="q9"></a>

### Q9 · parallel-processor — Write a parallel file processor using ProcessPoolExecutor 🟠

> 🛠️ **Solve locally:** [practice_local.py → Q9](./practice_local.py)


Write `process_files_parallel(file_list, max_workers=4)` that processes each file in a separate process, returns a list of `{"file": name, "count": N}` results. Define a simple `process_one_file(path)` function that counts rows.


<details><summary>💡 Hint</summary>Use `ProcessPoolExecutor` with `executor.map()`. Note: the target function must be importable (module-level, not lambda).</details>
<details><summary>✅ Answer</summary>

```python
from concurrent.futures import ProcessPoolExecutor
from pathlib import Path
import csv

def process_one_file(path):
    count = sum(1 for _ in csv.DictReader(open(path)))
    return {"file": Path(path).name, "count": count}

def process_files_parallel(file_list, max_workers=4):
    with ProcessPoolExecutor(max_workers=max_workers) as pool:
        results = list(pool.map(process_one_file, file_list))
    return results
```
**Why:** `ProcessPoolExecutor` bypasses the GIL — each file gets a real CPU core, speeding up CPU-bound parsing.
</details>

---

<a id="q10"></a>

### Q10 · schema-migration — Build ETL with schema migration: old format → new format 🟠

> 🛠️ **Solve locally:** [practice_local.py → Q10](./practice_local.py)


Write a transform that converts old-format rows `{"UserId": str, "FullName": str, "Pts": str}` to new format `{"user_id": int, "name": str, "score": float}`. Handle missing fields with defaults.


<details><summary>💡 Hint</summary>Map old key names to new ones explicitly. Use `.get()` with defaults to handle missing fields.</details>
<details><summary>✅ Answer</summary>

```python
def migrate_schema(records):
    for raw in records:
        yield {
            "user_id": int(raw.get("UserId", 0)),
            "name":    raw.get("FullName", "unknown").strip(),
            "score":   float(raw.get("Pts", 0)),
        }
```
**Why:** Explicit field mapping makes schema changes visible and auditable — no silent data loss from key renames.
</details>

---

<a id="q11"></a>

### Q11 · memory-profile — Memory profile the ETL pipeline: generator vs list 🟠

> 🛠️ **Solve locally:** [practice_local.py → Q11](./practice_local.py)


Using `tracemalloc`, measure peak memory of two approaches to count rows with `score >= 70` in a 10,000-row CSV: (a) load all rows into a list first, (b) use a generator. Print the peak memory for each.


<details><summary>💡 Hint</summary>Call `tracemalloc.start()`, run the function, call `tracemalloc.take_snapshot()`, then `tracemalloc.stop()`. Sum `s.size` over all statistics.</details>
<details><summary>✅ Answer</summary>

```python
import tracemalloc, gc, csv

def eager(path):
    rows = list(csv.DictReader(open(path)))        # all in RAM
    return sum(1 for r in rows if float(r["score"]) >= 70)

def lazy(path):
    return sum(1 for r in csv.DictReader(open(path)) if float(r["score"]) >= 70)

def measure(fn, path):
    gc.collect()
    tracemalloc.start()
    result = fn(path)
    snap = tracemalloc.take_snapshot()
    tracemalloc.stop()
    peak = sum(s.size for s in snap.statistics("filename"))
    return result, peak

r1, m1 = measure(eager, "data.csv")
r2, m2 = measure(lazy,  "data.csv")
print(f"Eager: {m1/1024:.1f} KB  |  Lazy: {m2/1024:.1f} KB  |  Ratio: {m1/m2:.1f}x")
```
**Why:** `tracemalloc` gives concrete proof that generators hold O(1) memory regardless of file size.
</details>

---

<a id="q12"></a>

### Q12 · capstone-etl — Capstone: full ETL from CSV to SQLite with error handling 🟠

> 🛠️ **Solve locally:** [practice_local.py → Q12](./practice_local.py)


Build a complete ETL pipeline that reads a CSV (`user_id, name, email, score`), validates each row with Pydantic, writes valid rows to a SQLite table `users`, writes invalid rows to `errors.jsonl`, and prints final stats.


<details><summary>💡 Hint</summary>Use `sqlite3.connect(":memory:")` for an in-memory DB. Create the table first. Use `executemany` for batch inserts.</details>
<details><summary>✅ Answer</summary>

```python
import sqlite3, csv, json
from pydantic import BaseModel, ValidationError

class UserRow(BaseModel):
    user_id: int
    name:    str
    email:   str
    score:   float

def run_etl(csv_path, db_path=":memory:", dlq_path="errors.jsonl"):
    con = sqlite3.connect(db_path)
    con.execute("CREATE TABLE IF NOT EXISTS users "
                "(user_id INT, name TEXT, email TEXT, score REAL)")

    valid, invalid = 0, 0
    with open(dlq_path, "w") as dlq:
        batch = []
        for raw in csv.DictReader(open(csv_path)):
            try:
                row = UserRow(**raw)
                batch.append((row.user_id, row.name, row.email, row.score))
                valid += 1
            except ValidationError as e:
                dlq.write(json.dumps({"raw": raw, "error": str(e)}) + "\n")
                invalid += 1

        con.executemany("INSERT INTO users VALUES (?,?,?,?)", batch)
        con.commit()

    print(f"Loaded {valid} rows | Errors: {invalid}")
    return con
```
**Why:** A real ETL always has three outputs: the target DB, an error log, and a stats summary.
</details>

---

## Navigation

| | |
|---|---|
| Theory | [theory.md](./theory.md) |
| Practice Local | [practice_local.py](./practice_local.py) |
| Root Practice | [../practice.md](../practice.md) |
| Streaming Practice | [../02_streaming_api_collection/practice.md](../02_streaming_api_collection/practice.md) |

**[Back to README](../../README.md)**
