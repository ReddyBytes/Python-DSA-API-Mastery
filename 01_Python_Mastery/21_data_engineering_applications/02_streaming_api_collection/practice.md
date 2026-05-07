# Streaming & API Collection — Practice
12 Questions · Event Streams · Pagination · Rate Limiting · Async · Backpressure · Retry

---

### Q1 · event-stream — Write a generator that simulates an event stream 🟢

Write `event_stream(total)` — a generator that yields dicts with `id`, `type` (one of `["click","view","buy"]`), and `value` (random float). It should yield exactly `total` events.

> 🛠️ **Solve locally:** [practice_local.py → Q1](./practice_local.py)

<details><summary>💡 Hint</summary>Use `random.choice` for the type, `random.uniform` for the value, and `yield` inside a `for` loop.</details>
<details><summary>✅ Answer</summary>

```python
import random

def event_stream(total=50):
    event_types = ["click", "view", "buy"]
    for i in range(total):
        yield {
            "id":    i + 1,
            "type":  random.choice(event_types),
            "value": round(random.uniform(1, 100), 2),
        }
```
**Why:** A generator never builds the full list — callers can process millions of events without loading them into RAM.
</details>

---

### Q2 · paginated-collector — Write a paginated API collector (loop until no next page) 🟢

Write `paginate(url, page_size=10)` — a generator that yields one list of items per page. Stop when the response's `has_more` field is `False`. Use `requests.get` (you can mock or stub the HTTP call).

> 🛠️ **Solve locally:** [practice_local.py → Q2](./practice_local.py)

<details><summary>💡 Hint</summary>Keep a `page` counter. In each iteration, fetch the page, yield `data["items"]`, then check `data["has_more"]`.</details>
<details><summary>✅ Answer</summary>

```python
import requests

def paginate(url, page_size=10):
    page = 1
    while True:
        resp = requests.get(url, params={"page": page, "page_size": page_size})
        data = resp.json()
        yield data["items"]
        if not data.get("has_more"):
            break
        page += 1
```
**Why:** A generator here means callers can process each page immediately, without waiting for all pages to download.
</details>

---

### Q3 · rate-limiting — Add rate limiting to an API collector 🟡

Modify the `paginate` function to sleep `delay` seconds between requests. The delay should be configurable (default 0.1s).

> 🛠️ **Solve locally:** [practice_local.py → Q3](./practice_local.py)

<details><summary>💡 Hint</summary>Call `time.sleep(delay)` at the bottom of the loop, after yielding but before incrementing the page counter.</details>
<details><summary>✅ Answer</summary>

```python
import requests
import time

def paginate_ratelimited(url, page_size=10, delay=0.1):
    page = 1
    while True:
        resp = requests.get(url, params={"page": page, "page_size": page_size})
        data = resp.json()
        yield data["items"]
        if not data.get("has_more"):
            break
        page += 1
        time.sleep(delay)    # ← pause between requests
```
**Why:** Without rate limiting, you'll hit the API's request cap and receive 429 errors.
</details>

---

### Q4 · async-collector — Write an async API collector with asyncio.gather 🟡

Write `async def collect_all(url, total_pages)` using `aiohttp`. Fetch all pages concurrently with `asyncio.gather` and return a flat list of all records.

> 🛠️ **Solve locally:** [practice_local.py → Q4](./practice_local.py)

<details><summary>💡 Hint</summary>Create a list of coroutine tasks (one per page), then `await asyncio.gather(*tasks)`.</details>
<details><summary>✅ Answer</summary>

```python
import asyncio
import aiohttp

async def fetch_page(session, url, page):
    async with session.get(url, params={"page": page}) as resp:
        data = await resp.json()
        return data.get("items", [])

async def collect_all(url, total_pages=5):
    async with aiohttp.ClientSession() as session:
        tasks = [fetch_page(session, url, p) for p in range(1, total_pages + 1)]
        pages = await asyncio.gather(*tasks)
    return [item for page in pages for item in page]
```
**Why:** `asyncio.gather` fires all page requests simultaneously — 5 pages at 200ms each takes ~200ms total, not 1 second.
</details>

---

### Q5 · semaphore — Add a Semaphore to limit concurrent requests to 5 🟡

Modify the async collector so that at most 5 page requests run at the same time, even if `total_pages` is 50. Use `asyncio.Semaphore`.

> 🛠️ **Solve locally:** [practice_local.py → Q5](./practice_local.py)

<details><summary>💡 Hint</summary>Create `sem = asyncio.Semaphore(5)` and wrap each `fetch_page` call with `async with sem:`.</details>
<details><summary>✅ Answer</summary>

```python
import asyncio
import aiohttp

async def collect_with_limit(url, total_pages=50, max_concurrent=5):
    sem = asyncio.Semaphore(max_concurrent)

    async def guarded_fetch(session, page):
        async with sem:
            async with session.get(url, params={"page": page}) as resp:
                data = await resp.json()
                return data.get("items", [])

    async with aiohttp.ClientSession() as session:
        tasks = [guarded_fetch(session, p) for p in range(1, total_pages + 1)]
        pages = await asyncio.gather(*tasks)
    return [item for page in pages for item in page]
```
**Why:** Without a Semaphore, 50 concurrent requests can overwhelm the server or trigger rate limits.
</details>

---

### Q6 · retry-backoff — Add retry with exponential backoff to an HTTP request 🟡

Write `fetch_with_retry(url, max_retries=3, backoff_base=2.0)` that retries on HTTP 429, 500, and 503 status codes. Wait `backoff_base ** attempt` seconds between retries.

> 🛠️ **Solve locally:** [practice_local.py → Q6](./practice_local.py)

<details><summary>💡 Hint</summary>Use a `for attempt in range(1, max_retries + 1)` loop. Break on success; sleep on retryable errors.</details>
<details><summary>✅ Answer</summary>

```python
import time
import requests

RETRYABLE = {429, 500, 503}

def fetch_with_retry(url, max_retries=3, backoff_base=2.0):
    for attempt in range(1, max_retries + 1):
        resp = requests.get(url, timeout=10)
        if resp.status_code == 200:
            return resp.json()
        if resp.status_code in RETRYABLE:
            wait = backoff_base ** attempt
            print(f"HTTP {resp.status_code} — retry {attempt} in {wait}s")
            time.sleep(wait)
            continue
        raise Exception(f"Non-retryable HTTP {resp.status_code}")
    raise Exception(f"All {max_retries} retries exhausted")
```
**Why:** Exponential backoff prevents hammering a struggling server and gives it time to recover.
</details>

---

### Q7 · sliding-window-ratelimit — Implement a sliding window rate limiter for a collector 🟡

Write a `RateLimiter` class with an `acquire()` method that allows at most `max_calls` requests per `period` seconds. Use a `collections.deque` to track request timestamps.

> 🛠️ **Solve locally:** [practice_local.py → Q7](./practice_local.py)

<details><summary>💡 Hint</summary>On each `acquire()` call, evict timestamps older than `period`, check the count, and sleep if at the limit.</details>
<details><summary>✅ Answer</summary>

```python
import time
from collections import deque

class RateLimiter:
    def __init__(self, max_calls, period):
        self.max_calls = max_calls
        self.period    = period
        self._calls    = deque()

    def acquire(self):
        now = time.time()
        # Evict calls older than the window
        while self._calls and self._calls[0] < now - self.period:
            self._calls.popleft()
        if len(self._calls) >= self.max_calls:
            sleep_time = self.period - (now - self._calls[0])
            time.sleep(max(0, sleep_time))
        self._calls.append(time.time())
```
**Why:** A sliding window rate limiter is fairer than a fixed bucket — it measures the last N seconds, not the current minute boundary.
</details>

---

### Q8 · multi-endpoint — Collect from multiple endpoints concurrently 🟡

Write `async def collect_from_endpoints(urls)` that fetches the first page from each URL concurrently and returns a dict mapping each URL to its items list.

> 🛠️ **Solve locally:** [practice_local.py → Q8](./practice_local.py)

<details><summary>💡 Hint</summary>Create one task per URL. Use `asyncio.gather` and `zip(urls, results)` to build the mapping.</details>
<details><summary>✅ Answer</summary>

```python
import asyncio
import aiohttp

async def fetch_first_page(session, url):
    async with session.get(url, params={"page": 1}) as resp:
        data = await resp.json()
        return data.get("items", [])

async def collect_from_endpoints(urls):
    async with aiohttp.ClientSession() as session:
        tasks = [fetch_first_page(session, url) for url in urls]
        results = await asyncio.gather(*tasks, return_exceptions=True)
    return {url: r for url, r in zip(urls, results)}
```
**Why:** `return_exceptions=True` prevents one failed URL from cancelling all the others.
</details>

---

### Q9 · backpressure-queue — Add backpressure: pause producer when consumer is slow 🟠

Implement a producer/consumer pair using `threading.Thread` and `queue.Queue(maxsize=20)`. The producer yields events; the consumer sleeps 0.01s per event (slow). Verify the queue blocks the producer when full.

> 🛠️ **Solve locally:** [practice_local.py → Q9](./practice_local.py)

<details><summary>💡 Hint</summary>Use `q.put(event)` (blocks when queue is full) in the producer. Use `q.get()` in the consumer. End with a `None` sentinel.</details>
<details><summary>✅ Answer</summary>

```python
import queue
import threading
import time

def producer(q, total=50):
    for i in range(total):
        q.put({"id": i, "value": i * 2})   # blocks if queue is full
    q.put(None)   # sentinel

def consumer(q, results):
    while True:
        item = q.get()
        if item is None:
            break
        time.sleep(0.01)   # simulate slow processing
        results.append(item)

results = []
q = queue.Queue(maxsize=20)   # ← backpressure: producer pauses when >20 queued

t1 = threading.Thread(target=producer, args=(q, 50))
t2 = threading.Thread(target=consumer, args=(q, results))
t1.start(); t2.start()
t1.join(); t2.join()
print(f"Consumed {len(results)} items")
```
**Why:** `maxsize` is the simplest backpressure mechanism — no extra dependencies, built into Python.
</details>

---

### Q10 · checkpoint-cursor — Implement a checkpoint that saves the last cursor to a file 🟠

Write a cursor-based collector that saves its `last_cursor` to disk after each page. On restart, it loads the saved cursor and continues from where it left off instead of page 1.

> 🛠️ **Solve locally:** [practice_local.py → Q10](./practice_local.py)

<details><summary>💡 Hint</summary>The API returns a `next_cursor` string. Save it to a JSON file after each page. Load it at startup.</details>
<details><summary>✅ Answer</summary>

```python
import json, requests
from pathlib import Path

def load_cursor(path):
    p = Path(path)
    if p.exists():
        return json.loads(p.read_text()).get("cursor")
    return None

def save_cursor(path, cursor):
    Path(path).write_text(json.dumps({"cursor": cursor}))

def collect_with_cursor_checkpoint(url, checkpoint_path="cursor.json"):
    cursor = load_cursor(checkpoint_path)
    while True:
        params = {"cursor": cursor} if cursor else {}
        data = requests.get(url, params=params).json()
        yield data["items"]
        cursor = data.get("next_cursor")
        if cursor:
            save_cursor(checkpoint_path, cursor)
        if not cursor:
            break
```
**Why:** Cursor checkpointing is crash-safe: if the process dies mid-collection, the next run picks up at the exact page it left off.
</details>

---

### Q11 · partial-failures — Handle partial failures: collect success and failed URLs 🟠

Write `collect_batch(urls)` that fetches all URLs, returns `(successes, failures)` where `successes` is a list of parsed JSON bodies and `failures` is a list of `{"url": ..., "error": ...}` dicts.

> 🛠️ **Solve locally:** [practice_local.py → Q11](./practice_local.py)

<details><summary>💡 Hint</summary>Wrap each `requests.get` in `try/except`. Append to `successes` on 200, `failures` on anything else.</details>
<details><summary>✅ Answer</summary>

```python
import requests

def collect_batch(urls):
    successes = []
    failures  = []
    for url in urls:
        try:
            resp = requests.get(url, timeout=5)
            resp.raise_for_status()
            successes.append(resp.json())
        except Exception as e:
            failures.append({"url": url, "error": str(e)})
    return successes, failures
```
**Why:** Returning failures as data (not exceptions) lets callers decide whether to retry, alert, or log — without crashing.
</details>

---

### Q12 · capstone-collector — Capstone: build an async paginated collector with rate limit + retry 🟠

Build `async def full_collector(url, total_pages, max_concurrent=5, max_retries=3)`. It should: fetch pages concurrently (bounded by Semaphore), retry each page up to `max_retries` times with exponential backoff, and return all records as a flat list.

> 🛠️ **Solve locally:** [practice_local.py → Q12](./practice_local.py)

<details><summary>💡 Hint</summary>Combine the Semaphore pattern from Q5 with the retry loop from Q6. Make `fetch_page` async with its own retry logic.</details>
<details><summary>✅ Answer</summary>

```python
import asyncio, aiohttp

async def full_collector(url, total_pages, max_concurrent=5, max_retries=3):
    sem = asyncio.Semaphore(max_concurrent)

    async def fetch_page(session, page):
        async with sem:
            for attempt in range(1, max_retries + 1):
                try:
                    async with session.get(url, params={"page": page}) as r:
                        if r.status == 200:
                            data = await r.json()
                            return data.get("items", [])
                        if r.status in (429, 500, 503):
                            await asyncio.sleep(2 ** attempt)
                            continue
                        return []   # non-retryable
                except Exception:
                    await asyncio.sleep(2 ** attempt)
            return []   # exhausted retries

    async with aiohttp.ClientSession() as session:
        tasks = [fetch_page(session, p) for p in range(1, total_pages + 1)]
        pages = await asyncio.gather(*tasks)
    return [item for page in pages for item in page]
```
**Why:** Combining Semaphore + retry in async code gives you both throughput (concurrency) and resilience (retries) with minimal code.
</details>

---

## Navigation

| | |
|---|---|
| Theory | [theory.md](./theory.md) |
| Practice Local | [practice_local.py](./practice_local.py) |
| Root Practice | [../practice.md](../practice.md) |
| ETL Practice | [../01_etl_pipelines/practice.md](../01_etl_pipelines/practice.md) |

**[Back to README](../../README.md)**
