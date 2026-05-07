# Streaming & API Collection — Theory
Generator-Based Streams, Paginated API Collection, Async Fetching, Backpressure

---

## Learning Priority

**Must Learn**: generator-based stream processing, pagination + API collection, asyncio for concurrent fetching
**Should Learn**: backpressure, rate limiting in collectors, retry with backoff
**Good to Know**: Kafka consumer basics, Server-Sent Events
**Reference**: Faust, Bytewax, Flink

---

## 1. Streaming vs Batch

Think of streaming data like a river. You don't wait for all the water to collect in a lake before using it — you scoop from it as it flows. Batch processing is the lake: you wait until enough has accumulated, then process it all.

```
BATCH:     wait ... wait ... wait ... [process everything] → result
STREAMING: event → [process] → result → event → [process] → result
```

| | Batch | Streaming |
|---|---|---|
| **Latency** | Minutes to hours | Milliseconds to seconds |
| **Use when** | Daily reports, analytics | Real-time alerts, live dashboards |
| **Tools** | Spark, pandas, SQL | Kafka, Kinesis, Flink |
| **Complexity** | Lower | Higher |

When do you use which? If you can wait — use batch. If the value of the data disappears after a few seconds (fraud detection, live prices) — use streaming.

---

## 2. Generator-Based Stream Simulation

In Python, a **generator** is the natural tool for representing an infinite or unbounded data stream. You `yield` one event at a time instead of building a list.

```python
import time
import random

def event_stream(total=50):
    """Simulates a live event feed — replace with Kafka consumer in prod."""
    event_types = ["click", "view", "buy", "error"]
    for i in range(total):
        yield {
            "id":    i + 1,
            "type":  random.choice(event_types),
            "value": round(random.uniform(1, 100), 2),
            "ts":    time.time(),
        }
        # In production: no sleep — events arrive from external source

# Process without ever holding all events in memory
for event in event_stream(total=1000):
    if event["type"] == "buy":
        record_purchase(event)
```

You can chain stream processors just like ETL generators:

```python
def only_buys(stream):
    return (e for e in stream if e["type"] == "buy")

def enrich(stream):
    for e in stream:
        e["revenue"] = e["value"] * 1.1   # ← add tax
        yield e

pipeline = enrich(only_buys(event_stream(1000)))
for event in pipeline:
    save(event)
```

---

## 3. API Data Collection

Most real data comes from paginated REST APIs. The API returns one "page" of results at a time, with a flag telling you whether there are more pages. Your collector loops until `has_more` is false.

```
Page 1 → [collect] → Page 2 → [collect] → Page 3 → [collect] → done
            ↕                      ↕
         save data              save data
```

```python
import requests

def paginate(url, page_size=100):
    """Generator: yields one page of records at a time."""
    page = 1
    while True:
        resp = requests.get(url, params={"page": page, "page_size": page_size})
        data = resp.json()

        yield data["items"]              # ← one page of records

        if not data.get("has_more"):
            break
        page += 1

# Consume: flatten pages into individual records
for page in paginate("https://api.example.com/records"):
    for record in page:
        process(record)
```

**Rate limiting** — most APIs enforce a max requests-per-second. Add a `time.sleep` between pages:

```python
import time

def paginate_with_ratelimit(url, page_size=100, delay=0.1):
    page = 1
    while True:
        resp = requests.get(url, params={"page": page, "page_size": page_size})
        data = resp.json()
        yield data["items"]
        if not data.get("has_more"):
            break
        page += 1
        time.sleep(delay)                # ← pause between requests
```

---

## 4. Async API Collector

Synchronous pagination is slow: you wait for page 1 to finish before asking for page 2. With `asyncio`, you fetch multiple pages at the same time.

```python
import asyncio
import aiohttp

async def fetch_page(session, url, page):
    async with session.get(url, params={"page": page}) as resp:
        return await resp.json()

async def collect_all(url, total_pages=5):
    async with aiohttp.ClientSession() as session:
        tasks = [fetch_page(session, url, p) for p in range(1, total_pages+1)]
        pages = await asyncio.gather(*tasks)   # ← all pages fetched in parallel
    return [item for page in pages for item in page.get("items", [])]

records = asyncio.run(collect_all("https://api.example.com/data"))
```

`asyncio.gather` fires all requests at once and waits for all to complete. For 10 pages that each take 200ms, synchronous = 2 seconds, async = ~200ms.

---

## 5. Backpressure

**Backpressure** is what happens when your producer generates data faster than your consumer can handle it. Without it, memory fills up and the process crashes.

Think of it like a garden hose: if the water pressure is too high, the hose bursts. A pressure-relief valve (backpressure) slows the source.

```python
import asyncio

async def fetch_page(session, url, page):
    async with session.get(url, params={"page": page}) as resp:
        return await resp.json()

async def collect_with_backpressure(url, total_pages, max_concurrent=5):
    """Semaphore limits how many requests run at the same time."""
    sem = asyncio.Semaphore(max_concurrent)   # ← at most 5 at once

    async def guarded_fetch(session, page):
        async with sem:                       # ← blocks if 5 already running
            return await fetch_page(session, url, page)

    async with aiohttp.ClientSession() as session:
        tasks = [guarded_fetch(session, p) for p in range(1, total_pages+1)]
        return await asyncio.gather(*tasks)
```

For thread-based collectors, `queue.Queue(maxsize=N)` applies backpressure — the producer blocks when the queue is full:

```python
import queue
import threading

q = queue.Queue(maxsize=100)   # ← producer blocks when 100 items queued

def producer():
    for event in event_stream(10000):
        q.put(event)           # ← blocks if queue is full (backpressure)
    q.put(None)                # ← sentinel: no more events

def consumer():
    while True:
        event = q.get()
        if event is None:
            break
        process(event)
```

---

## 6. Retry with Backoff

Networks fail. APIs return 500. The correct response is to wait a bit and try again — but not immediately, or you'll hammer a struggling server. **Exponential backoff** doubles the wait time after each failure.

```python
import time

def fetch_with_retry(url, max_retries=3, backoff_base=2.0):
    for attempt in range(1, max_retries + 1):
        try:
            resp = requests.get(url, timeout=10)
            if resp.status_code == 200:
                return resp.json()
            if resp.status_code in (429, 500, 503):
                raise Exception(f"HTTP {resp.status_code}")
        except Exception as e:
            wait = backoff_base ** attempt    # 2s, 4s, 8s
            print(f"Attempt {attempt} failed: {e} — retrying in {wait}s")
            time.sleep(wait)
    raise Exception(f"All {max_retries} retries exhausted for {url}")
```

A **jitter** (small random offset) prevents the "thundering herd" problem when many workers all retry at exactly the same moment:

```python
import random
wait = backoff_base ** attempt + random.uniform(0, 1)   # ← add jitter
```

---

## 7. Common Mistakes

**No backpressure** — producer fills memory until OOM crash:

```python
# Wrong: unbounded list grows forever
all_events = list(event_stream())   # 10M events → crash

# Right: process as you go
for event in event_stream():
    process(event)
```

**Sync HTTP in async code** — `requests` blocks the event loop, destroying the concurrency benefit:

```python
# Wrong in async code
async def collect():
    return requests.get(url).json()   # ← blocks entire event loop

# Right
async def collect():
    async with aiohttp.ClientSession() as s:
        async with s.get(url) as r:
            return await r.json()     # ← non-blocking
```

**Losing failed records** — if a page fails and you move on, you have gaps in your data:

```python
# Right: track success and failure separately
successes = []
failures  = []
for page_num in range(1, total_pages + 1):
    try:
        successes.extend(fetch_page(page_num))
    except Exception as e:
        failures.append({"page": page_num, "error": str(e)})

# Re-queue failures for retry
```

---

## Navigation

| | |
|---|---|
| Root Theory | [../theory.md](../theory.md) |
| Practice | [practice.md](./practice.md) |
| ETL Pipelines | [../01_etl_pipelines/theory.md](../01_etl_pipelines/theory.md) |
| Cheetsheet | [../cheetsheet.md](../cheetsheet.md) |

**[Back to README](../../README.md)**

**Prev:** [ETL Pipelines](../01_etl_pipelines/theory.md) &nbsp;|&nbsp; **Next:** [Root Interview Q&A](../interview.md)

**Related Topics:** [Generators & Iterators](../../11_generators_iterators/theory.md) · [Concurrency](../../13_concurrency/theory.md) · [Async Python for AI](../../24_async_python_for_ai/theory.md)
