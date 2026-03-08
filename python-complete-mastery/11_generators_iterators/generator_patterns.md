# 🔧 generator_patterns.md — Generator Pipeline Pattern Library

> Real production patterns for streaming ETL, pagination, batching,
> file processing, and infinite sequences using generators.

---

## 📋 Pattern Index

```
1.  File line reader          — stream any text file
2.  Chunked reader            — fixed-size binary chunks
3.  JSON-lines processor      — streaming JSONL (newline-delimited JSON)
4.  CSV streaming pipeline    — 50GB CSV without loading to memory
5.  Paginated API iterator    — auto-page through REST endpoints
6.  DB cursor streaming       — stream query results in batches
7.  Batch/chunk generator     — group items into fixed-size batches
8.  Sliding window            — overlapping windows over a sequence
9.  Merge sorted iterables    — K-way merge without materializing
10. Fan-out pipeline          — broadcast one source to multiple consumers
11. Pipeline with error sink  — separate good records from bad
12. Counting / progress wrap  — add progress reporting to any generator
13. Timeout-limited iteration — stop consuming after N seconds
14. Round-robin multiplexer   — interleave multiple generators evenly
15. Infinite retry source     — re-read source on failure
```

---

## 1. File Line Reader

```python
from pathlib import Path

def read_lines(path, encoding="utf-8", skip_blank=True):
    """Stream a text file line by line. O(1) memory."""
    with open(path, encoding=encoding) as f:
        for line in f:
            stripped = line.rstrip("\n")
            if skip_blank and not stripped:
                continue
            yield stripped

# Usage:
for line in read_lines("huge.log"):
    process(line)
```

---

## 2. Chunked Binary Reader

```python
def read_chunks(path, chunk_size=65536):
    """Stream a binary file in fixed-size chunks. For images, archives, etc."""
    with open(path, "rb") as f:
        while True:
            chunk = f.read(chunk_size)
            if not chunk:
                break
            yield chunk

# With walrus operator (Python 3.8+):
def read_chunks(path, chunk_size=65536):
    with open(path, "rb") as f:
        while chunk := f.read(chunk_size):
            yield chunk

# Usage:
import hashlib
hasher = hashlib.sha256()
for chunk in read_chunks("large_file.zip"):
    hasher.update(chunk)
print(hasher.hexdigest())
```

---

## 3. JSON-Lines (JSONL) Processor

```python
import json
from pathlib import Path

def read_jsonl(path, encoding="utf-8"):
    """Stream a .jsonl file (one JSON object per line)."""
    with open(path, encoding=encoding) as f:
        for line_num, line in enumerate(f, 1):
            line = line.strip()
            if not line:
                continue
            try:
                yield json.loads(line)
            except json.JSONDecodeError as e:
                import logging
                logging.warning("Line %d: invalid JSON — %s", line_num, e)

# Usage:
for event in read_jsonl("events.jsonl"):
    if event["level"] == "ERROR":
        alert(event)
```

---

## 4. Full CSV Streaming Pipeline

```python
import csv
from typing import Iterator

def read_csv(path, encoding="utf-8") -> Iterator[dict]:
    """Stage 1: Source — yield one dict per CSV row."""
    with open(path, newline="", encoding=encoding) as f:
        yield from csv.DictReader(f)

def parse_types(rows, schema: dict) -> Iterator[dict]:
    """Stage 2: Transform — cast field types."""
    for row in rows:
        try:
            yield {
                field: cast(row[field])
                for field, cast in schema.items()
                if field in row
            }
        except (ValueError, KeyError) as e:
            import logging
            logging.warning("Skipping row — %s: %s", type(e).__name__, e)

def filter_rows(rows, predicate) -> Iterator[dict]:
    """Stage 3: Filter — keep rows matching predicate."""
    for row in rows:
        if predicate(row):
            yield row

def to_batches(rows, size=500) -> Iterator[list[dict]]:
    """Stage 4: Batch — group into insert-ready batches."""
    batch = []
    for row in rows:
        batch.append(row)
        if len(batch) >= size:
            yield batch
            batch.clear()
    if batch:
        yield batch

# Wire the pipeline:
schema     = {"user_id": int, "amount": float, "status": str}
predicate  = lambda r: r["amount"] > 0 and r["status"] == "completed"

pipeline = to_batches(
    filter_rows(
        parse_types(
            read_csv("transactions.csv"),
            schema
        ),
        predicate
    ),
    size=500
)

for batch in pipeline:
    db.executemany("INSERT INTO transactions VALUES ...", batch)
```

---

## 5. Paginated API Iterator

```python
import requests
from typing import Iterator

def paginate_api(
    url: str,
    params: dict = None,
    page_param: str = "page",
    per_page: int = 100,
    results_key: str = "items",
) -> Iterator[dict]:
    """
    Yield individual items from a paginated REST API.
    Stops when a page returns fewer results than per_page.
    """
    params = dict(params or {})
    params["per_page"] = per_page
    page = 1

    while True:
        params[page_param] = page
        response = requests.get(url, params=params, timeout=30)
        response.raise_for_status()
        data = response.json()

        items = data.get(results_key, []) if isinstance(data, dict) else data
        yield from items

        if len(items) < per_page:
            break   # last page
        page += 1

# Usage:
for user in paginate_api("https://api.example.com/users"):
    process_user(user)
```

---

## 6. Database Cursor Streaming

```python
from typing import Iterator
import sqlite3

def stream_query(
    conn,
    query: str,
    params: tuple = (),
    batch_size: int = 1000,
) -> Iterator[dict]:
    """
    Stream query results one row at a time using server-side cursor.
    Never loads all results into memory.
    """
    cursor = conn.cursor()
    cursor.execute(query, params)
    columns = [desc[0] for desc in cursor.description]

    while True:
        rows = cursor.fetchmany(batch_size)
        if not rows:
            break
        for row in rows:
            yield dict(zip(columns, row))

# Usage:
conn = sqlite3.connect("analytics.db")
for row in stream_query(conn, "SELECT * FROM events WHERE level = ?", ("ERROR",)):
    process(row)
```

---

## 7. Batch / Chunk Generator

```python
from itertools import islice

def batched(iterable, size: int):
    """
    Yield lists of exactly `size` items (last batch may be smaller).
    Pure generator — no intermediate list.
    """
    it = iter(iterable)
    while True:
        batch = list(islice(it, size))
        if not batch:
            break
        yield batch

# Python 3.12+ has itertools.batched built-in.

# Usage:
for batch in batched(range(10), 3):
    print(batch)
# [0, 1, 2]
# [3, 4, 5]
# [6, 7, 8]
# [9]
```

---

## 8. Sliding Window

```python
from collections import deque

def sliding_window(iterable, size: int):
    """Yield overlapping windows of `size` consecutive items."""
    it  = iter(iterable)
    win = deque(islice(it, size), maxlen=size)
    if len(win) == size:
        yield tuple(win)
    for item in it:
        win.append(item)
        yield tuple(win)

# Usage:
list(sliding_window([1, 2, 3, 4, 5], 3))
# [(1,2,3), (2,3,4), (3,4,5)]

# Real use: moving average:
def moving_average(data, window=5):
    for win in sliding_window(data, window):
        yield sum(win) / len(win)
```

---

## 9. K-Way Merge of Sorted Iterables

```python
import heapq

def merge_sorted(*iterables, key=None):
    """
    Merge multiple sorted iterables into one sorted stream.
    Memory: O(number of iterables), not O(total items).
    """
    heap = []
    iterators = [iter(it) for it in iterables]

    for i, it in enumerate(iterators):
        try:
            val = next(it)
            heap.append((key(val) if key else val, i, val, it))
        except StopIteration:
            pass

    heapq.heapify(heap)

    while heap:
        _, i, val, it = heapq.heappop(heap)
        yield val
        try:
            next_val = next(it)
            heapq.heappush(heap, (key(next_val) if key else next_val, i, next_val, it))
        except StopIteration:
            pass

# Usage:
a = [1, 3, 5, 7]
b = [2, 4, 6, 8]
c = [0, 9, 10]
list(merge_sorted(a, b, c))   # [0, 1, 2, 3, 4, 5, 6, 7, 8, 9, 10]
```

---

## 10. Pipeline with Error Sink

```python
def pipeline_with_errors(source, transform, error_sink=None):
    """
    Apply transform to each item. Send failures to error_sink generator.
    Yields (record, None) on success, (None, error) on failure.
    """
    for item in source:
        try:
            yield transform(item), None
        except Exception as e:
            if error_sink is not None:
                error_sink.send((item, e))
            yield None, e

# Usage:
good_records = []
bad_records  = []

def collect_errors():
    while True:
        item, err = yield
        bad_records.append({"item": item, "error": str(err)})

error_collector = collect_errors()
next(error_collector)   # prime

def transform(row):
    return {"id": int(row["id"]), "amount": float(row["amount"])}

for result, error in pipeline_with_errors(read_csv("data.csv"), transform, error_collector):
    if result:
        good_records.append(result)

print(f"Good: {len(good_records)}, Bad: {len(bad_records)}")
```

---

## 11. Progress-Reporting Wrapper

```python
import sys, time

def with_progress(iterable, total=None, every=1000, label=""):
    """Wrap any iterable to print progress every N items."""
    start = time.time()
    for i, item in enumerate(iterable, 1):
        yield item
        if i % every == 0:
            elapsed = time.time() - start
            rate    = i / elapsed if elapsed > 0 else 0
            pct     = f"{i/total*100:.1f}%" if total else f"{i:,}"
            print(
                f"\r{label}{pct} ({rate:.0f}/s)   ",
                end="", flush=True, file=sys.stderr
            )
    print(file=sys.stderr)   # newline at end

# Usage:
for row in with_progress(read_csv("huge.csv"), total=10_000_000, every=10_000):
    process(row)
# stderr: 5.0% (45000/s)
```

---

## 12. Timeout-Limited Iteration

```python
import time

def take_for(iterable, seconds: float):
    """Yield items from iterable for at most `seconds` seconds."""
    deadline = time.monotonic() + seconds
    for item in iterable:
        if time.monotonic() >= deadline:
            break
        yield item

# Usage: process a live stream for exactly 60 seconds:
for event in take_for(live_stream(), seconds=60):
    handle(event)
```

---

## 13. Round-Robin Multiplexer

```python
from itertools import cycle

def round_robin(*iterables):
    """Interleave multiple iterables one item at a time."""
    iterators = [iter(it) for it in iterables]
    active    = list(iterators)
    while active:
        for it in list(active):
            try:
                yield next(it)
            except StopIteration:
                active.remove(it)

# Usage:
list(round_robin([1, 2, 3], ["a", "b"], [True]))
# [1, 'a', True, 2, 'b', 3]
```

---

## 14. Infinite Retry Source

```python
import logging, time

def retry_source(factory, delay=5.0, max_retries=None, logger=None):
    """
    Call factory() to get an iterable. If it raises, retry after delay.
    Useful for consuming a live message queue that may disconnect.
    """
    logger = logger or logging.getLogger(__name__)
    retries = 0
    while max_retries is None or retries <= max_retries:
        try:
            yield from factory()
            return   # source exhausted normally
        except Exception as e:
            retries += 1
            logger.warning("Source failed (attempt %d): %s — retrying in %.1fs",
                           retries, e, delay)
            time.sleep(delay)

# Usage:
def open_kafka_consumer():
    consumer = KafkaConsumer("topic", bootstrap_servers="kafka:9092")
    yield from consumer   # yields messages

for message in retry_source(open_kafka_consumer, delay=10.0):
    process(message)   # auto-reconnects on disconnect
```

---

## 15. Fan-Out (Broadcast) Pipeline

```python
from collections import deque

def fan_out(source, n_consumers: int):
    """
    Broadcast one source to N consumers.
    Each consumer gets its own independent stream.
    Uses buffering — all consumers must consume at similar rates.
    """
    buffers = [deque() for _ in range(n_consumers)]

    def fill():
        for item in source:
            for buf in buffers:
                buf.append(item)

    import threading
    t = threading.Thread(target=fill, daemon=True)
    t.start()

    def make_consumer(buf):
        while t.is_alive() or buf:
            if buf:
                yield buf.popleft()
            else:
                time.sleep(0.001)

    return [make_consumer(buf) for buf in buffers]

# Usage:
stream1, stream2 = fan_out(read_lines("events.log"), n_consumers=2)
# stream1 → write to DB
# stream2 → write to S3 archive
```

---

## 🔁 Navigation

| | |
|---|---|
| 📖 Theory | [theory.md](./theory.md) |
| 🎯 Interview | [interview.md](./interview.md) |
| ⚡ Cheatsheet | [cheatsheet.md](./cheatsheet.md) |
| ➡️ Next | [12 — Context Managers](../12_context_managers/theory.md) |
