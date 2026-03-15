"""
13_concurrency/asyncio_examples.py
=====================================
CONCEPT: Real-world asyncio patterns — HTTP client simulation, async queues,
semaphores for rate limiting, async generators, and structuring production
async applications.
WHY THIS MATTERS: These are the patterns you use when building async APIs,
scrapers, real-time services, and data pipelines in production Python.

Prerequisite: Modules 01–12, async_programming.py
"""

import asyncio
import time
import random
import json
from collections import defaultdict

# =============================================================================
# SECTION 1: Simulated async HTTP client — aiohttp-style patterns
# =============================================================================

# CONCEPT: Real HTTP libraries (aiohttp, httpx) are async. This section shows
# the pattern: a session created once, requests fired concurrently, responses
# awaited. The key insight is `async with session.get(url)` — the session
# manages connection pooling and lifecycle automatically.

print("=== Section 1: Async HTTP Client Simulation ===")


class AsyncHTTPSession:
    """Simulates an async HTTP session (like aiohttp.ClientSession)."""

    def __init__(self, base_url: str, timeout: float = 5.0):
        self.base_url   = base_url
        self.timeout    = timeout
        self._open      = False
        self._req_count = 0

    async def __aenter__(self):
        await asyncio.sleep(0.01)   # simulate connection pool creation
        self._open = True
        print(f"  Session opened: {self.base_url}")
        return self

    async def __aexit__(self, *_):
        await asyncio.sleep(0.005)
        self._open = False
        print(f"  Session closed. Total requests: {self._req_count}")

    async def get(self, path: str) -> dict:
        if not self._open:
            raise RuntimeError("Session is not open — use `async with`")
        self._req_count += 1
        latency = random.uniform(0.05, 0.25)
        await asyncio.sleep(latency)

        # Simulate occasional errors
        if random.random() < 0.1:
            raise ConnectionError(f"Request failed: {path}")

        return {
            "url":     f"{self.base_url}{path}",
            "status":  200,
            "latency": latency,
            "data":    {"path": path, "items": random.randint(1, 100)},
        }


async def fetch_all_endpoints(base_url: str, paths: list) -> list:
    """Fetch multiple endpoints concurrently in a single session."""
    async with AsyncHTTPSession(base_url) as session:
        tasks = [
            asyncio.create_task(session.get(path), name=f"GET {path}")
            for path in paths
        ]
        results = await asyncio.gather(*tasks, return_exceptions=True)

    successes = [r for r in results if isinstance(r, dict)]
    errors    = [r for r in results if isinstance(r, Exception)]
    return successes, errors


paths = ["/users", "/products", "/orders", "/inventory", "/analytics"]
start = time.perf_counter()
successes, errors = asyncio.run(fetch_all_endpoints("https://api.example.com", paths))
elapsed = time.perf_counter() - start

print(f"  {len(successes)} succeeded, {len(errors)} failed in {elapsed:.2f}s")
for s in successes[:3]:
    print(f"    {s['url']}: {s['data']['items']} items ({s['latency']*1000:.0f}ms)")


# =============================================================================
# SECTION 2: Semaphore — controlling concurrency to avoid overload
# =============================================================================

# CONCEPT: asyncio.Semaphore(n) allows at most N coroutines to execute
# concurrently inside `async with sem`. Without it, 1000 tasks might all
# try to connect to the DB simultaneously — exhausting connection limits.
# This is the async equivalent of a connection pool size limit.

print("\n=== Section 2: Semaphore for Rate Limiting ===")

async def scrape_url(session: AsyncHTTPSession, url: str, sem: asyncio.Semaphore) -> dict:
    """Scrape a single URL, but limit concurrent scrapes via semaphore."""
    async with sem:   # at most N tasks inside this block simultaneously
        try:
            result = await session.get(url)
            return {"url": url, "ok": True, "items": result["data"]["items"]}
        except ConnectionError as e:
            return {"url": url, "ok": False, "error": str(e)}


async def scrape_with_concurrency_limit(urls: list, max_concurrent: int) -> list:
    sem = asyncio.Semaphore(max_concurrent)

    async with AsyncHTTPSession("") as session:
        tasks = [scrape_url(session, url, sem) for url in urls]
        return await asyncio.gather(*tasks)


N_URLS = 20
urls = [f"/page/{i}" for i in range(N_URLS)]

start = time.perf_counter()
# Without limit: all 20 requests fire simultaneously (fine for 20, bad for 1000)
results = asyncio.run(scrape_with_concurrency_limit(urls, max_concurrent=5))
elapsed = time.perf_counter() - start

ok_count = sum(1 for r in results if r["ok"])
print(f"  Scraped {N_URLS} URLs (max 5 concurrent): {ok_count} ok in {elapsed:.2f}s")


# =============================================================================
# SECTION 3: Async Queue — producer/consumer pipeline
# =============================================================================

# CONCEPT: asyncio.Queue is the async equivalent of queue.Queue.
# Use it to decouple producers and consumers. Each can run at its own pace.
# Multiple consumers can drain from the same queue (worker pool pattern).
# This is the foundation of async data pipelines and job queues.

print("\n=== Section 3: Async Queue (Producer/Consumer) ===")

async def async_producer(q: asyncio.Queue, items: list, delay: float) -> None:
    """Produce items at a fixed rate."""
    for item in items:
        await asyncio.sleep(delay)
        await q.put(item)
        print(f"  [Producer] queued: {item}")
    # Sentinel: one per consumer to stop them
    await q.put(None)


async def async_consumer(q: asyncio.Queue, worker_id: int) -> list:
    """Consume items until the sentinel (None) is received."""
    results = []
    while True:
        item = await q.get()
        if item is None:
            q.task_done()
            break

        # Simulate variable processing time
        await asyncio.sleep(random.uniform(0.02, 0.08))
        result = item ** 2
        print(f"  [Worker-{worker_id}] {item} → {result}")
        results.append(result)
        q.task_done()   # signal that this item is fully processed

    return results


async def pipeline_demo():
    q = asyncio.Queue(maxsize=5)   # bound queue — producer blocks if full

    # 1 producer, 2 consumers (workers)
    producer_task = asyncio.create_task(
        async_producer(q, list(range(1, 8)), delay=0.05)
    )

    consumer_tasks = [
        asyncio.create_task(async_consumer(q, worker_id=i))
        for i in range(1, 3)
    ]

    # Wait for producer to finish, then add sentinel for 2nd consumer
    await producer_task
    await q.put(None)   # first None consumed by consumer 1; add second for consumer 2

    all_results = await asyncio.gather(*consumer_tasks)
    flat = sorted(r for chunk in all_results for r in chunk)
    print(f"\n  All processed: {flat}")


asyncio.run(pipeline_demo())


# =============================================================================
# SECTION 4: Async generators — streaming data lazily
# =============================================================================

# CONCEPT: `async def` + `yield` = async generator.
# `async for` consumes it. Each `yield` can `await` an I/O operation.
# Perfect for: paginated APIs, database cursor streaming, WebSocket messages.
# Normal generators can't `await` — async generators can.

print("\n=== Section 4: Async Generators ===")

async def paginated_api(endpoint: str, total_pages: int):
    """
    Async generator that simulates a paginated API.
    Fetches each page on demand — caller controls how many pages to consume.
    WHY: with 10,000 pages, you don't want to load all into memory upfront.
    """
    for page in range(1, total_pages + 1):
        await asyncio.sleep(0.02)   # simulate HTTP request per page
        items = [f"item_{(page-1)*10 + i}" for i in range(1, 4)]
        yield {"page": page, "items": items, "has_more": page < total_pages}


async def consume_paginated():
    total_items = 0
    async for page_data in paginated_api("/products", total_pages=5):
        print(f"  Page {page_data['page']}: {page_data['items']}")
        total_items += len(page_data["items"])
        if page_data["page"] >= 3:
            break   # early exit — stop fetching after 3 pages

    print(f"  Total items consumed: {total_items}")


asyncio.run(consume_paginated())


# =============================================================================
# SECTION 5: Event-driven pattern — asyncio.Event
# =============================================================================

# CONCEPT: asyncio.Event is a synchronization primitive for coroutines.
# event.wait() suspends until event.set() is called from another coroutine.
# Use it to signal state changes between coroutines without polling.

print("\n=== Section 5: asyncio.Event for Coordination ===")

async def event_demo():
    startup_done   = asyncio.Event()
    shutdown_event = asyncio.Event()

    async def server():
        print("  [Server] Initializing...")
        await asyncio.sleep(0.1)   # simulate startup
        print("  [Server] Ready!")
        startup_done.set()         # signal: startup complete

        await shutdown_event.wait()   # block until shutdown is signalled
        print("  [Server] Shutting down gracefully...")

    async def client():
        print("  [Client] Waiting for server to be ready...")
        await startup_done.wait()   # don't proceed until server signals ready
        print("  [Client] Server is up! Sending requests...")
        await asyncio.sleep(0.15)   # simulate client work
        print("  [Client] Done. Triggering shutdown.")
        shutdown_event.set()        # signal: client work done, server can stop

    await asyncio.gather(server(), client())


asyncio.run(event_demo())


# =============================================================================
# SECTION 6: Real-world async application structure
# =============================================================================

# CONCEPT: A production async app typically has:
# 1. An entry point that calls asyncio.run(main())
# 2. A startup phase (DB connect, cache warm-up)
# 3. A main loop (request handling, job processing)
# 4. A shutdown phase (drain queues, close connections)

print("\n=== Section 6: Structured Async Application ===")

class AsyncApp:
    """
    Template for a production async application.
    Each phase (startup/run/shutdown) is a coroutine — fully controllable.
    """

    def __init__(self, name: str):
        self.name    = name
        self.db      = None
        self.cache   = {}
        self._queue  = asyncio.Queue()
        self._stop   = asyncio.Event()

    async def startup(self):
        """Initialize shared resources once, before serving requests."""
        print(f"  [{self.name}] startup: connecting to DB...")
        await asyncio.sleep(0.05)   # simulate DB connection
        self.db = {"connected": True, "pool_size": 10}
        print(f"  [{self.name}] startup: DB connected — {self.db}")

    async def process_job(self, job: dict) -> dict:
        """Handle a single job — the unit of work."""
        await asyncio.sleep(random.uniform(0.02, 0.06))
        return {"job_id": job["id"], "status": "done", "result": job["id"] ** 2}

    async def run(self, n_jobs: int = 5):
        """Main work loop."""
        jobs = [{"id": i} for i in range(1, n_jobs + 1)]
        results = await asyncio.gather(*[self.process_job(j) for j in jobs])
        for r in results:
            print(f"  [{self.name}] job {r['job_id']} → {r['result']}")

    async def shutdown(self):
        """Cleanup: close connections, flush buffers."""
        print(f"  [{self.name}] shutting down...")
        await asyncio.sleep(0.02)
        self.db = None
        print(f"  [{self.name}] shutdown complete")

    async def __call__(self):
        """Run the full app lifecycle."""
        await self.startup()
        await self.run()
        await self.shutdown()


asyncio.run(AsyncApp("DataProcessor")())


print("\n=== asyncio examples complete ===")
print("Patterns summary:")
print("  gather()         → fan-out: start N, wait for all")
print("  create_task()    → schedule + run in background")
print("  Semaphore        → limit concurrency (connection pools)")
print("  Queue            → async producer/consumer pipelines")
print("  async generator  → lazy streaming from async sources")
print("  Event            → coroutine-to-coroutine signaling")
print("  Structured app   → startup / run / shutdown lifecycle")
