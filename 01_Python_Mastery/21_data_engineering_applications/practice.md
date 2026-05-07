# Data Engineering Applications — Practice
25 Questions · ETL · File Processing · Generators · Schema Validation · API Collection · Streaming

---

## Q1–Q8: ETL Flow, File Processing, Generators

### Q1 · etl-mental-model — Describe the three stages of ETL in plain English 🟢

What does each stage do? Which stage should be a generator? Which stage should never raise?

> 🛠️ **Solve locally:** [practice_local.py → Q1](./practice_local.py)

<details><summary>💡 Hint</summary>Extract reads raw data, Transform cleans it, Load writes output. Transform is the stage that should never crash the pipeline.</details>
<details><summary>✅ Answer</summary>

```python
# Extract: read raw data from a source (file, API, DB) as a stream of records
# Transform: clean, validate, enrich each record — collect errors, never raise
# Load: write valid records to the target (DB, file, queue)

def extract(filepath):
    with open(filepath) as f:
        for line in f:
            yield line.strip()

def transform(records):
    for raw in records:
        try:
            yield process(raw)
        except Exception as e:
            log.warning("bad row: %s", e)   # collect, never raise

def load(records, out):
    for r in records:
        out.write(r)
```
**Why:** Separating E/T/L makes each stage testable in isolation with tiny in-memory data.
</details>

---

### Q2 · csv-generator — Write a generator that reads a CSV file row by row 🟢

Write `read_csv(filepath)` that yields one `dict` per row without loading the full file.

> 🛠️ **Solve locally:** [practice_local.py → Q2](./practice_local.py)

<details><summary>💡 Hint</summary>Use `csv.DictReader` inside `with open(...)` and `yield dict(row)` for each row.</details>
<details><summary>✅ Answer</summary>

```python
import csv

def read_csv(filepath):
    with open(filepath, newline="") as f:
        for row in csv.DictReader(f):
            yield dict(row)
```
**Why:** `yield` inside the context manager keeps the file open only while consuming, and holds only one row in RAM.
</details>

---

### Q3 · generator-chain — Chain three transform generators into one pipeline 🟢

Write `strip_fields`, `cast_score`, and `add_grade` as three generator functions. Chain them and collect the output into a list.

> 🛠️ **Solve locally:** [practice_local.py → Q3](./practice_local.py)

<details><summary>💡 Hint</summary>Each function takes an iterator and yields from it. Chain them: `add_grade(cast_score(strip_fields(records)))`.</details>
<details><summary>✅ Answer</summary>

```python
def strip_fields(records):
    for r in records:
        yield {k: v.strip() for k, v in r.items()}

def cast_score(records):
    for r in records:
        r["score"] = float(r.get("score", 0))
        yield r

def add_grade(records):
    for r in records:
        r["grade"] = "A" if r["score"] >= 90 else "B"
        yield r

result = list(add_grade(cast_score(strip_fields(read_csv("data.csv")))))
```
**Why:** Chaining generators means only one record crosses all three stages at once — O(1) memory for any file size.
</details>

---

### Q4 · pathlib-glob — Use pathlib to process all CSV files in a directory 🟢

Write code that iterates over all `.csv` files in a directory and counts total rows across all files.

> 🛠️ **Solve locally:** [practice_local.py → Q4](./practice_local.py)

<details><summary>💡 Hint</summary>Use `Path(dir).glob("*.csv")` to get file paths, then `read_csv` from Q2 inside a loop.</details>
<details><summary>✅ Answer</summary>

```python
from pathlib import Path

def count_all_rows(data_dir):
    total = 0
    for filepath in Path(data_dir).glob("*.csv"):
        total += sum(1 for _ in read_csv(str(filepath)))
    return total
```
**Why:** `Path.glob` is lazy — it yields paths without scanning the whole directory into a list.
</details>

---

### Q5 · chunked-processing — Process a CSV in chunks of 500 rows 🟡

Write `chunk(iterable, size)` and use it to process rows in batches of 500. Print the chunk number and count for each batch.

> 🛠️ **Solve locally:** [practice_local.py → Q5](./practice_local.py)

<details><summary>💡 Hint</summary>Accumulate items in a list; `yield` it when it reaches `size`, then reset to empty list.</details>
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

for i, batch in enumerate(chunk(read_csv("big.csv"), 500), 1):
    print(f"Chunk {i}: {len(batch)} rows")
```
**Why:** Chunks bound memory to O(size) while still enabling aggregations that pure streaming cannot do.
</details>

---

### Q6 · jsonl-reader — Read a JSONL file as a generator, skipping bad lines 🟡

Write `read_jsonl(filepath)` that yields one parsed dict per line, silently skipping lines that are not valid JSON.

> 🛠️ **Solve locally:** [practice_local.py → Q6](./practice_local.py)

<details><summary>💡 Hint</summary>Iterate over lines, call `json.loads(line)` inside `try/except json.JSONDecodeError`.</details>
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
                continue
```
**Why:** JSONL is the standard for log/event files — resilient skipping keeps the pipeline running despite occasional corruption.
</details>

---

### Q7 · eager-vs-lazy — Prove generator uses less memory than a list 🟡

Write two versions of "count rows with score >= 70": one that loads all rows into a list first (eager), one that uses a generator (lazy). Use `tracemalloc` to measure peak memory for each.

> 🛠️ **Solve locally:** [practice_local.py → Q7](./practice_local.py)

<details><summary>💡 Hint</summary>Call `tracemalloc.start()`, run the function, call `tracemalloc.take_snapshot()`, then sum `s.size` over all statistics.</details>
<details><summary>✅ Answer</summary>

```python
import tracemalloc, gc, csv

def eager(path):
    rows = list(csv.DictReader(open(path)))
    return sum(1 for r in rows if float(r["score"]) >= 70)

def lazy(path):
    return sum(1 for r in csv.DictReader(open(path)) if float(r["score"]) >= 70)

def measure(fn, path):
    gc.collect()
    tracemalloc.start()
    result = fn(path)
    snap = tracemalloc.take_snapshot()
    tracemalloc.stop()
    return result, sum(s.size for s in snap.statistics("filename"))

r1, m1 = measure(eager, "data.csv")
r2, m2 = measure(lazy, "data.csv")
print(f"Eager: {m1/1024:.0f} KB | Lazy: {m2/1024:.0f} KB | Ratio: {m1/m2:.1f}x")
```
**Why:** This experiment makes the memory advantage concrete — typically 5-20x difference for medium-sized files.
</details>

---

### Q8 · parallel-files — Process 8 CSV files in parallel using ThreadPoolExecutor 🟡

Write `process_files_parallel(paths, max_workers=4)` that processes each file in a thread and returns a list of row counts.

> 🛠️ **Solve locally:** [practice_local.py → Q8](./practice_local.py)

<details><summary>💡 Hint</summary>Use `ThreadPoolExecutor.map()`. CSV reading is I/O-bound so threads (not processes) are appropriate.</details>
<details><summary>✅ Answer</summary>

```python
from concurrent.futures import ThreadPoolExecutor

def count_rows(path):
    return sum(1 for _ in read_csv(path))

def process_files_parallel(paths, max_workers=4):
    with ThreadPoolExecutor(max_workers=max_workers) as pool:
        return list(pool.map(count_rows, paths))
```
**Why:** File I/O releases the GIL — threads give real concurrency for reading multiple files simultaneously.
</details>

---

## Q9–Q14: Schema Validation, Error Handling, Checkpointing

### Q9 · pydantic-model — Define a Pydantic model for a CSV row with a range validator 🟡

Define `SaleRow` with `sale_id: int`, `product: str`, `amount: float` (must be > 0), `region: str`. Write a function that validates a list of dicts and returns `(valid, errors)`.

> 🛠️ **Solve locally:** [practice_local.py → Q9](./practice_local.py)

<details><summary>💡 Hint</summary>Use `@field_validator("amount")` to check the range. Catch `ValidationError` in the function.</details>
<details><summary>✅ Answer</summary>

```python
from pydantic import BaseModel, field_validator, ValidationError

class SaleRow(BaseModel):
    sale_id: int
    product: str
    amount:  float
    region:  str

    @field_validator("amount")
    @classmethod
    def positive(cls, v):
        if v <= 0:
            raise ValueError("amount must be > 0")
        return v

def validate_rows(rows):
    valid, errors = [], []
    for raw in rows:
        try:
            valid.append(SaleRow(**raw))
        except ValidationError as e:
            errors.append({"raw": raw, "error": str(e)})
    return valid, errors
```
**Why:** Collecting errors as data (not exceptions) lets you report all bad rows at once, not just the first one.
</details>

---

### Q10 · dead-letter-queue — Route bad rows to a dead-letter JSONL file 🟡

Write `pipeline_with_dlq(records, dlq_path)` — a generator that yields clean records and writes bad rows to `dlq_path` as JSON lines.

> 🛠️ **Solve locally:** [practice_local.py → Q10](./practice_local.py)

<details><summary>💡 Hint</summary>Open the DLQ file in append mode inside the generator. Use `try/except` around the transform call.</details>
<details><summary>✅ Answer</summary>

```python
import json

def pipeline_with_dlq(records, dlq_path):
    with open(dlq_path, "a") as dlq:
        for raw in records:
            try:
                yield transform(raw)
            except Exception as e:
                dlq.write(json.dumps({"raw": raw, "error": str(e)}) + "\n")
```
**Why:** A dead-letter queue separates bad records from the main flow — you can replay them later without re-running the whole pipeline.
</details>

---

### Q11 · fail-fast-vs-soft — Compare fail-fast vs soft-fail strategies 🟡

Write two versions of a transform pipeline: `strict_pipeline` raises immediately on the first bad row, `lenient_pipeline` logs and skips bad rows. Show when you would use each.

> 🛠️ **Solve locally:** [practice_local.py → Q11](./practice_local.py)

<details><summary>💡 Hint</summary>In strict mode, let exceptions propagate. In lenient mode, catch all exceptions and continue.</details>
<details><summary>✅ Answer</summary>

```python
def strict_pipeline(records):
    for r in records:
        yield validate(r)   # raises on first bad row — job dies immediately

def lenient_pipeline(records):
    for r in records:
        try:
            yield validate(r)
        except Exception as e:
            print(f"Skipping bad row: {e}")   # log and continue

# Use strict when: critical financial data, any bad row = upstream bug
# Use lenient when: best-effort analytics, occasional bad rows expected
```
**Why:** The right strategy depends on data criticality — financial pipelines should fail loudly, analytics pipelines should log and continue.
</details>

---

### Q12 · checkpoint-row — Implement checkpoint + resume for a row-based pipeline 🟡

Write a `Checkpoint` class and use it to skip already-processed rows when a pipeline restarts.

> 🛠️ **Solve locally:** [practice_local.py → Q12](./practice_local.py)

<details><summary>💡 Hint</summary>Save the last processed `id` to a JSON file. On startup, load it and skip rows with id <= last_id.</details>
<details><summary>✅ Answer</summary>

```python
import json
from pathlib import Path

class Checkpoint:
    def __init__(self, path):
        self._path = Path(path)

    def load(self):
        return json.loads(self._path.read_text())["last_id"] if self._path.exists() else 0

    def save(self, last_id):
        self._path.write_text(json.dumps({"last_id": last_id}))

cp = Checkpoint("cp.json")
start = cp.load()
for row in read_csv("data.csv"):
    if int(row["id"]) <= start:
        continue
    process(row)
    cp.save(int(row["id"]))
```
**Why:** Without checkpointing, a 10-hour job that crashes at hour 9 must restart from the beginning.
</details>

---

### Q13 · schema-migration — Migrate rows from old schema to new schema 🟡

Write `migrate(records)` that converts `{"UserId": str, "FullName": str, "Pts": str}` to `{"user_id": int, "name": str, "score": float}`, using defaults for missing fields.

> 🛠️ **Solve locally:** [practice_local.py → Q13](./practice_local.py)

<details><summary>💡 Hint</summary>Use `.get(key, default)` for each field. Wrap type conversions in `try/except`.</details>
<details><summary>✅ Answer</summary>

```python
def migrate(records):
    for raw in records:
        try:
            yield {
                "user_id": int(raw.get("UserId", 0)),
                "name":    raw.get("FullName", "unknown").strip(),
                "score":   float(raw.get("Pts", 0)),
            }
        except (ValueError, TypeError) as e:
            print(f"Migration failed for row {raw}: {e}")
```
**Why:** Explicit field mapping is the only safe way to migrate schemas — implicit column ordering breaks silently.
</details>

---

### Q14 · idempotency — Implement idempotent file processing with a content-hash registry 🟡

Write a `ProcessedRegistry` that tracks file content hashes. Provide `is_processed(filepath)` and `mark_processed(filepath)` methods. Use MD5 to hash file contents.

> 🛠️ **Solve locally:** [practice_local.py → Q14](./practice_local.py)

<details><summary>💡 Hint</summary>Store hashes in a JSON file on disk. Compute `hashlib.md5(path.read_bytes()).hexdigest()` as the key.</details>
<details><summary>✅ Answer</summary>

```python
import hashlib, json
from pathlib import Path

class ProcessedRegistry:
    def __init__(self, path):
        self._path = Path(path)
        self._data = json.loads(self._path.read_text()) if self._path.exists() else {}

    def _hash(self, filepath):
        return hashlib.md5(Path(filepath).read_bytes()).hexdigest()

    def is_processed(self, filepath):
        return self._hash(filepath) in self._data

    def mark_processed(self, filepath):
        self._data[self._hash(filepath)] = str(filepath)
        self._path.write_text(json.dumps(self._data))
```
**Why:** Hashing file contents (not names) detects the same logical file re-delivered under a different name, preventing double-processing.
</details>

---

## Q15–Q20: API Collection, Async Fetching, Rate Limiting

### Q15 · pagination-loop — Write a cursor-based paginated collector 🟢

Write `paginate_cursor(url)` — a generator that follows `next_cursor` links until the API returns no cursor. Yield one list of items per page.

> 🛠️ **Solve locally:** [practice_local.py → Q15](./practice_local.py)

<details><summary>💡 Hint</summary>Start with `cursor = None`. In each loop, pass it as a param if set. Update cursor from the response. Break when `next_cursor` is absent.</details>
<details><summary>✅ Answer</summary>

```python
import requests

def paginate_cursor(url, page_size=10):
    cursor = None
    while True:
        params = {"page_size": page_size}
        if cursor:
            params["cursor"] = cursor
        data = requests.get(url, params=params).json()
        yield data["items"]
        cursor = data.get("next_cursor")
        if not cursor:
            break
```
**Why:** Cursor pagination is consistent under concurrent inserts — page-number pagination can skip or duplicate rows when the dataset changes between pages.
</details>

---

### Q16 · retry-backoff — Write fetch_with_retry with exponential backoff 🟡

Write `fetch_with_retry(url, max_retries=3, backoff_base=2.0)`. Retry on HTTP 429/500/503. Raise after exhausting retries.

> 🛠️ **Solve locally:** [practice_local.py → Q16](./practice_local.py)

<details><summary>💡 Hint</summary>Use `for attempt in range(1, max_retries + 1)`. Sleep `backoff_base ** attempt` seconds on retryable errors.</details>
<details><summary>✅ Answer</summary>

```python
import time, requests

def fetch_with_retry(url, max_retries=3, backoff_base=2.0):
    for attempt in range(1, max_retries + 1):
        resp = requests.get(url, timeout=10)
        if resp.status_code == 200:
            return resp.json()
        if resp.status_code in (429, 500, 503):
            time.sleep(backoff_base ** attempt)
            continue
        raise Exception(f"HTTP {resp.status_code}")
    raise Exception("Retries exhausted")
```
**Why:** `2 ** attempt` gives waits of 2s, 4s, 8s — giving the server progressively more time to recover.
</details>

---

### Q17 · token-bucket — Implement a token bucket rate limiter 🟡

Write `TokenBucket(rate)` with an `acquire()` method that blocks until a token is available. Rate is in requests per second.

> 🛠️ **Solve locally:** [practice_local.py → Q17](./practice_local.py)

<details><summary>💡 Hint</summary>Track `_tokens` and `_last_refill` time. On each `acquire()`, compute tokens earned since last call. Sleep if tokens < 1.</details>
<details><summary>✅ Answer</summary>

```python
import time, threading

class TokenBucket:
    def __init__(self, rate):
        self._rate   = rate
        self._tokens = rate
        self._last   = time.time()
        self._lock   = threading.Lock()

    def acquire(self):
        with self._lock:
            now = time.time()
            self._tokens = min(self._rate, self._tokens + (now - self._last) * self._rate)
            self._last   = now
            if self._tokens >= 1:
                self._tokens -= 1
            else:
                wait = (1 - self._tokens) / self._rate
                time.sleep(wait)
                self._tokens = 0
```
**Why:** Token bucket is smoother than fixed-window rate limiting — it allows short bursts while enforcing a long-term average rate.
</details>

---

### Q18 · async-gather — Fetch 10 API pages concurrently with asyncio.gather 🟡

Write `async def fetch_all_pages(url, n_pages)` that fetches pages 1 to n_pages concurrently using `aiohttp` and `asyncio.gather`. Return a flat list of all items.

> 🛠️ **Solve locally:** [practice_local.py → Q18](./practice_local.py)

<details><summary>💡 Hint</summary>Create a single `ClientSession`, build one coroutine per page, then `await asyncio.gather(*tasks)`.</details>
<details><summary>✅ Answer</summary>

```python
import asyncio, aiohttp

async def fetch_all_pages(url, n_pages=10):
    async def fetch_page(session, page):
        async with session.get(url, params={"page": page}) as r:
            data = await r.json()
            return data.get("items", [])

    async with aiohttp.ClientSession() as session:
        tasks = [fetch_page(session, p) for p in range(1, n_pages + 1)]
        pages = await asyncio.gather(*tasks)
    return [item for page in pages for item in page]
```
**Why:** One `ClientSession` reuses the HTTP connection pool — creating a new session per request is much slower.
</details>

---

### Q19 · semaphore-limit — Limit concurrent API requests to 3 using asyncio.Semaphore 🟡

Modify `fetch_all_pages` so that at most 3 pages are fetched simultaneously, even when n_pages is large.

> 🛠️ **Solve locally:** [practice_local.py → Q19](./practice_local.py)

<details><summary>💡 Hint</summary>Create `sem = asyncio.Semaphore(3)` outside the task functions. Use `async with sem:` inside each fetch coroutine.</details>
<details><summary>✅ Answer</summary>

```python
import asyncio, aiohttp

async def fetch_limited(url, n_pages=20, max_concurrent=3):
    sem = asyncio.Semaphore(max_concurrent)

    async def fetch_page(session, page):
        async with sem:
            async with session.get(url, params={"page": page}) as r:
                data = await r.json()
                return data.get("items", [])

    async with aiohttp.ClientSession() as session:
        tasks = [fetch_page(session, p) for p in range(1, n_pages + 1)]
        pages = await asyncio.gather(*tasks)
    return [item for page in pages for item in page]
```
**Why:** Without a Semaphore, 20 concurrent requests from a single collector is likely to trigger rate limits.
</details>

---

### Q20 · partial-failures — Return successes and failures separately from a batch fetch 🟡

Write `fetch_batch(urls)` that fetches all URLs and returns `(successes, failures)` — never raising even if some URLs fail.

> 🛠️ **Solve locally:** [practice_local.py → Q20](./practice_local.py)

<details><summary>💡 Hint</summary>Wrap each `requests.get` in `try/except`. Use `resp.raise_for_status()` to surface HTTP errors as exceptions.</details>
<details><summary>✅ Answer</summary>

```python
import requests

def fetch_batch(urls):
    successes, failures = [], []
    for url in urls:
        try:
            resp = requests.get(url, timeout=5)
            resp.raise_for_status()
            successes.append(resp.json())
        except Exception as e:
            failures.append({"url": url, "error": str(e)})
    return successes, failures
```
**Why:** Returning failures as data lets callers decide what to do — retry, alert, or log — without crashing the collector.
</details>

---

## Q21–Q23: Streaming, Backpressure, Retry

### Q21 · producer-consumer — Implement producer/consumer with Queue backpressure 🟡

Write a producer that puts 100 events onto a `queue.Queue(maxsize=10)` and a consumer that processes them. Run both in threads. Confirm all 100 events are processed.

> 🛠️ **Solve locally:** [practice_local.py → Q21](./practice_local.py)

<details><summary>💡 Hint</summary>`queue.Queue(maxsize=10)` automatically blocks the producer when the queue is full — that IS backpressure.</details>
<details><summary>✅ Answer</summary>

```python
import queue, threading

def producer(q, n=100):
    for i in range(n):
        q.put({"id": i})   # blocks when queue is full
    q.put(None)

def consumer(q, results):
    while True:
        item = q.get()
        if item is None:
            break
        results.append(item)

results = []
q = queue.Queue(maxsize=10)
t1 = threading.Thread(target=producer, args=(q,))
t2 = threading.Thread(target=consumer, args=(q, results))
t1.start(); t2.start(); t1.join(); t2.join()
assert len(results) == 100
```
**Why:** `maxsize` is the simplest form of backpressure in Python — no external libraries needed.
</details>

---

### Q22 · sliding-window — Implement a sliding window rate limiter 🟠

Write `SlidingWindowLimiter(max_calls, period)` with an `acquire()` method. Use a `deque` to track call timestamps and sleep when the limit is reached.

> 🛠️ **Solve locally:** [practice_local.py → Q22](./practice_local.py)

<details><summary>💡 Hint</summary>On `acquire()`: evict timestamps older than `period`, check the count, sleep until the oldest call falls outside the window if at the limit.</details>
<details><summary>✅ Answer</summary>

```python
import time
from collections import deque

class SlidingWindowLimiter:
    def __init__(self, max_calls, period):
        self.max_calls = max_calls
        self.period    = period
        self._calls    = deque()

    def acquire(self):
        now = time.time()
        while self._calls and self._calls[0] < now - self.period:
            self._calls.popleft()
        if len(self._calls) >= self.max_calls:
            sleep_for = self.period - (now - self._calls[0])
            time.sleep(max(0, sleep_for))
        self._calls.append(time.time())
```
**Why:** Sliding window is fairer than fixed-window: it measures the last N seconds, not the current minute bucket.
</details>

---

### Q23 · stream-processor — Build a streaming processor with tumbling windows 🟠

Write `TumblingWindow(size)` with `add(event)` and `flush(current_time)` methods. `flush` returns all windows that ended before `current_time` and removes them from state.

> 🛠️ **Solve locally:** [practice_local.py → Q23](./practice_local.py)

<details><summary>💡 Hint</summary>Key each bucket by `(timestamp // size) * size`. In `flush`, pop buckets whose key < `(current_time // size) * size`.</details>
<details><summary>✅ Answer</summary>

```python
class TumblingWindow:
    def __init__(self, size):
        self.size     = size
        self._buckets = {}

    def add(self, event):
        key = (event["ts"] // self.size) * self.size
        self._buckets.setdefault(key, []).append(event)

    def flush(self, current_time):
        cutoff = (current_time // self.size) * self.size
        closed = {k: v for k, v in self._buckets.items() if k < cutoff}
        for k in closed:
            del self._buckets[k]
        return closed
```
**Why:** Tumbling windows are the basis of per-minute/per-hour summaries in every stream processing framework.
</details>

---

## Q24–Q25: Capstone Problems

### Q24 · capstone-etl — Full ETL: CSV → validate → SQLite + error log 🟠

Build a complete pipeline: read a CSV, validate with Pydantic, write valid rows to SQLite (`users` table), write invalid rows to `errors.jsonl`. Print stats at the end.

> 🛠️ **Solve locally:** [practice_local.py → Q24](./practice_local.py)

<details><summary>💡 Hint</summary>Use `sqlite3.connect(":memory:")`, create the table with `CREATE TABLE IF NOT EXISTS`, batch-insert with `executemany`.</details>
<details><summary>✅ Answer</summary>

```python
import csv, json, sqlite3
from pydantic import BaseModel, ValidationError

class UserRow(BaseModel):
    user_id: int
    name:    str
    score:   float

def run_etl(csv_path, db=":memory:", dlq="errors.jsonl"):
    con = sqlite3.connect(db)
    con.execute("CREATE TABLE IF NOT EXISTS users (user_id INT, name TEXT, score REAL)")
    valid, invalid = [], []
    for raw in csv.DictReader(open(csv_path)):
        try:
            r = UserRow(**raw)
            valid.append((r.user_id, r.name, r.score))
        except ValidationError as e:
            invalid.append({"raw": raw, "error": str(e)})
    con.executemany("INSERT INTO users VALUES (?,?,?)", valid)
    con.commit()
    with open(dlq, "w") as f:
        for row in invalid:
            f.write(json.dumps(row) + "\n")
    print(f"Loaded {len(valid)} | Errors {len(invalid)}")
    return con
```
**Why:** Every production ETL has exactly three outputs: target DB, error log, and a stats summary.
</details>

---

### Q25 · capstone-collector — Async paginated collector with Semaphore + retry + checkpoint 🟠

Build `async def resilient_collect(url, total_pages, checkpoint_path, max_concurrent=5, max_retries=3)`. It should load a starting page from `checkpoint_path`, fetch remaining pages with concurrency limit and retry, save checkpoint after each page, and return all collected records.

> 🛠️ **Solve locally:** [practice_local.py → Q25](./practice_local.py)

<details><summary>💡 Hint</summary>Load the starting page from JSON on disk. Use `asyncio.Semaphore` to cap concurrency. Retry with `asyncio.sleep(2**attempt)`. Save checkpoint after each successful page.</details>
<details><summary>✅ Answer</summary>

```python
import asyncio, aiohttp, json
from pathlib import Path

def load_cp(path):
    p = Path(path)
    return json.loads(p.read_text())["last_page"] if p.exists() else 0

def save_cp(path, page):
    Path(path).write_text(json.dumps({"last_page": page}))

async def resilient_collect(url, total_pages, checkpoint_path,
                            max_concurrent=5, max_retries=3):
    start = load_cp(checkpoint_path) + 1
    sem   = asyncio.Semaphore(max_concurrent)

    async def fetch(session, page):
        async with sem:
            for attempt in range(1, max_retries + 1):
                try:
                    async with session.get(url, params={"page": page}) as r:
                        if r.status == 200:
                            data = await r.json()
                            save_cp(checkpoint_path, page)
                            return data.get("items", [])
                        await asyncio.sleep(2 ** attempt)
                except Exception:
                    await asyncio.sleep(2 ** attempt)
            return []

    async with aiohttp.ClientSession() as session:
        tasks = [fetch(session, p) for p in range(start, total_pages + 1)]
        pages = await asyncio.gather(*tasks)
    return [item for page in pages for item in page]
```
**Why:** Combining checkpoint + Semaphore + retry makes a collector that survives crashes, rate limits, and transient network failures.
</details>

---

## Navigation

| | |
|---|---|
| Theory | [theory.md](./theory.md) |
| Practice Local | [practice_local.py](./practice_local.py) |
| ETL Pipelines | [01_etl_pipelines/practice.md](./01_etl_pipelines/practice.md) |
| Streaming | [02_streaming_api_collection/practice.md](./02_streaming_api_collection/practice.md) |
| Interview | [interview.md](./interview.md) |

**[Back to README](../README.md)**
