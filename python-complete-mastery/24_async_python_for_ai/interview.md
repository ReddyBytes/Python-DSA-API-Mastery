# 🎯 Async Python for AI — Interview Questions

> *"AI engineering interviews test whether you understand concurrency at the system level.*
> *Not just 'how do I use await' but 'why does this scale and that doesn't'."*

---

## 📊 Question Map

```
LEVEL 1 — Beginner
  • What is async/await and why do we need it?
  • When should you use async instead of threading?
  • What is an async generator and when would you use one?

LEVEL 2 — Intermediate
  • How does asyncio.gather work under the hood?
  • What is a Semaphore and why do you need one for LLM APIs?
  • Difference between create_task and gather
  • What is an async context manager?
  • How do you handle errors in a batch of async LLM calls?

LEVEL 3 — Advanced
  • How do you implement streaming LLM responses end-to-end?
  • How would you batch-embed 10,000 documents while respecting rate limits?
  • How do you handle partial failures in gather?
  • Why is FastAPI well-suited for LLM API services?
  • How do you run async code from a sync context safely?
```

---

## 🟢 Level 1 — Beginner Questions

---

**Q1: What is async/await and why do we need it for AI applications?**

<details>
<summary>💡 Show Answer</summary>

**Weak answer:** "async is for running things faster. await waits for something."

**Strong answer:**

> `async def` defines a coroutine — a function that can suspend itself at `await` points and let other code run. The `await` keyword means "I'm waiting for I/O — the event loop can do other work until this is ready."
>
> In AI applications, almost every interesting operation is an LLM API call — which is pure network I/O. Your Python process sends an HTTP request and then waits. With sync code, the thread is blocked and can do nothing else. With async, the event loop can handle 100 other users' requests while any one user's LLM call is in flight.

```python
# Sync — user 2 cannot start until user 1's LLM call finishes:
def handle_user(prompt):
    return call_llm(prompt)   # thread blocked for 3 seconds

# Async — all users' calls are in-flight simultaneously:
async def handle_user(prompt):
    return await call_llm(prompt)   # suspends, event loop handles others

async def handle_100_users(prompts):
    tasks = [handle_user(p) for p in prompts]
    return await asyncio.gather(*tasks)   # ~3s total, not 300s
```

> **The key insight:** LLM calls are I/O-bound. Async is the right tool for I/O-bound work at scale.

</details>

<br>

**Q2: When should you use async instead of threading for an AI service?**

<details>
<summary>💡 Show Answer</summary>

**Strong answer:**

> Both can work, but async is the preferred modern choice for AI/API services for these reasons:

```
ASYNC:
  Single thread — no thread creation, no thread scheduling overhead.
  Can handle thousands of concurrent connections with one process.
  Explicitly shows where concurrency happens (every await is visible).
  Native to FastAPI, aiohttp, httpx, asyncpg — all modern Python web tools.
  Low memory: no per-thread stacks.

THREADING:
  Each concurrent request typically needs a thread.
  100 threads × 8MB stack = 800MB RAM just for thread stacks.
  Thread scheduling adds overhead under high load.
  Works well for moderate concurrency (tens of threads).
  Easier to use with legacy sync libraries.

RULE OF THUMB:
  Building a new AI service or API → async (FastAPI + AsyncOpenAI)
  Adding async calls to existing sync codebase → threads (ThreadPoolExecutor)
  Number of concurrent users in the hundreds or thousands → async wins clearly
```

> The OpenAI SDK, Anthropic SDK, and every modern LLM client library ships an async version specifically because async is the right model for LLM API calls.

</details>

<br>

**Q3: What is an [async generator](../11_generators_iterators/theory.md#-chapter-12-async-generators-python-36) and when would you use one for AI?**

<details>
<summary>💡 Show Answer</summary>

**Weak answer:** "It's a generator but async."

**Strong answer:**

> An async generator is a function that uses both `async def` and `yield`. It can `await` between yields — meaning it can do async I/O and stream values one at a time to the caller. The caller consumes it with `async for`.
>
> The primary AI use case is **streaming LLM responses**: the model generates tokens one at a time. Instead of waiting for the full response, you yield each token to the caller as it arrives.

```python
# Async generator — yields values, can await between each:
async def stream_response(prompt: str):
    stream = await client.chat.completions.create(
        model="gpt-4o",
        messages=[{"role": "user", "content": prompt}],
        stream=True
    )
    async for chunk in stream:
        delta = chunk.choices[0].delta.content
        if delta:
            yield delta   # send this token NOW, don't wait for the rest

# Caller uses async for:
async def display():
    async for token in stream_response("Explain AI"):
        print(token, end="", flush=True)
    # User sees words appearing in real time — like ChatGPT
```

> Without streaming, the user stares at a blank screen for 3 seconds. With streaming, they see the first word in under 200ms. Async generators make this possible.

</details>


## 🔵 Level 2 — Intermediate Questions

---

**Q4: How does asyncio.gather work under the hood?**

<details>
<summary>💡 Show Answer</summary>

**Weak answer:** "It runs coroutines in parallel."

**Strong answer:**

> `asyncio.gather` schedules all the passed coroutines as `Task` objects on the current event loop, then awaits a single future that completes when all tasks complete.

```python
# What asyncio.gather does internally (simplified):
#   1. Wraps each coroutine in asyncio.create_task → schedules on event loop
#   2. Creates a Future that resolves when all tasks are done
#   3. Returns results in the same order as input (not completion order)

# Equivalent manual version:
async def manual_gather(*coros):
    tasks = [asyncio.create_task(c) for c in coros]
    results = []
    for task in tasks:
        results.append(await task)
    return results
# (Real gather is more efficient — but same idea)
```

> **Important nuances:**
> - Results come back in input order, not completion order
> - If any task raises, `gather` cancels the rest and re-raises (unless `return_exceptions=True`)
> - `return_exceptions=True` is critical for batch processing — you get all results including failures

```python
# Without return_exceptions — one failure cancels the rest:
results = await asyncio.gather(task1, task2, task3)   # if task2 fails, task3 cancelled

# With return_exceptions — all tasks run, exceptions returned as values:
results = await asyncio.gather(task1, task2, task3, return_exceptions=True)
# results = [value1, SomeException(...), value3]  ← task3 still ran!
```

</details>

<br>

**Q5: What is a Semaphore and why do you need one for LLM APIs?**

<details>
<summary>💡 Show Answer</summary>

**Strong answer:**

> A Semaphore is a concurrency limiter with a counter. When you do `async with semaphore`, it decrements the counter. If the counter reaches zero, the next `async with` blocks until another task releases the semaphore (increments the counter back up).
>
> LLM APIs have **rate limits**: OpenAI enforces limits like 3,000 requests per minute or 1,000,000 tokens per minute per API key. If you fire 10,000 requests simultaneously with `asyncio.gather`, the vast majority get rejected with `429 RateLimitError`.

```python
# Without Semaphore — all 10,000 requests fire at once — almost all fail:
async def embed_naive(texts):
    tasks = [embed_one(text) for text in texts]
    return await asyncio.gather(*tasks)   # 10,000 simultaneous requests!

# With Semaphore — max 20 in-flight at any moment:
async def embed_safe(texts, max_concurrent=20):
    semaphore = asyncio.Semaphore(max_concurrent)

    async def embed_with_limit(text):
        async with semaphore:   # blocks if 20 are already running
            return await embed_one(text)

    tasks = [embed_with_limit(text) for text in texts]
    return await asyncio.gather(*tasks, return_exceptions=True)
# Still concurrent (20 at a time) but not overwhelming the API
```

> **How to choose the limit:** start conservative (10-20), observe if you get 429 errors, increase until you hit the limit, then back off slightly.

</details>

<br>

**Q6: What is the difference between asyncio.create_task and asyncio.gather?**

<details>
<summary>💡 Show Answer</summary>

**Strong answer:**

```
asyncio.create_task(coro):
  Schedules ONE coroutine on the event loop immediately.
  Returns a Task object — you can await it later, cancel it, add callbacks.
  Use when: you want to start work now but collect results at a different time.

asyncio.gather(*coros):
  Schedules ALL coroutines at once AND waits for all to complete.
  Returns a list of results in input order.
  Use when: you have a fixed list and want all results before moving on.
```

```python
# create_task — start work in the background:
async def main():
    task = asyncio.create_task(expensive_llm_call())
    # task is running — event loop runs it whenever we await
    await do_other_setup_work()   # runs while LLM is thinking
    result = await task           # collect result when ready

# gather — fire and collect all:
async def main():
    results = await asyncio.gather(
        call_llm("q1"),
        call_llm("q2"),
        call_llm("q3"),
    )
    # results available here, in order q1, q2, q3

# combine them — create_task + gather:
async def main():
    tasks = [asyncio.create_task(call_llm(q)) for q in questions]
    # All started immediately as Tasks
    results = await asyncio.gather(*tasks)
    # Equivalent to gather(*[call_llm(q) for q in questions])
    # but useful if you need the task handles to cancel individual ones
```

</details>

<br>

**Q7: What is an async context manager and why do HTTP clients use them?**

<details>
<summary>💡 Show Answer</summary>

**Strong answer:**

> An async context manager implements `__aenter__` and `__aexit__` as coroutines instead of regular methods. The `async with` syntax awaits the enter and exit, allowing async setup and teardown.
>
> HTTP clients use them because opening and closing connections involves I/O (TCP handshake, TLS negotiation). With a sync context manager you cannot await those. With `async with`, the client can set up a connection pool asynchronously and tear it down cleanly.

```python
# Wrong — one client object for many calls, but context manager isn't used:
client = httpx.AsyncClient()
response = await client.get(url)   # client is never properly closed

# Correct — connection pool is managed properly:
async with httpx.AsyncClient() as client:
    # __aenter__ sets up connection pool
    r1 = await client.get(url1)   # reuses connections from pool
    r2 = await client.get(url2)
    # __aexit__ closes all connections cleanly

# For many requests, one shared client is better than a new one per request:
app_client = httpx.AsyncClient()   # created once at startup

async def fetch(url):
    return await app_client.get(url)   # reuses connection pool
```

</details>

<br>

**Q8: How do you handle errors across a batch of async LLM calls?**

<details>
<summary>💡 Show Answer</summary>

**Strong answer:**

> The critical choice is `return_exceptions=True` in `asyncio.gather`. Without it, a single failing task cancels all others. With it, exceptions are returned as values — you inspect each result and handle failures individually.

```python
import asyncio

async def process_prompt(prompt: str) -> str:
    try:
        return await call_llm(prompt)
    except RateLimitError:
        await asyncio.sleep(5)
        return await call_llm(prompt)   # one retry

async def batch_with_error_handling(prompts: list[str]) -> dict:
    semaphore = asyncio.Semaphore(10)

    async def safe_call(prompt):
        async with semaphore:
            return await process_prompt(prompt)

    tasks = [safe_call(p) for p in prompts]
    results = await asyncio.gather(*tasks, return_exceptions=True)

    successes = []
    failures = []
    for prompt, result in zip(prompts, results):
        if isinstance(result, Exception):
            failures.append({"prompt": prompt, "error": str(result)})
        else:
            successes.append({"prompt": prompt, "result": result})

    print(f"Succeeded: {len(successes)}, Failed: {len(failures)}")
    return {"successes": successes, "failures": failures}
```

</details>


## 🔴 Level 3 — Advanced Questions

---

**Q9: Walk me through implementing a streaming LLM response in FastAPI end-to-end.**

<details>
<summary>💡 Show Answer</summary>

**Strong answer:**

> Streaming requires three pieces working together: the LLM API with `stream=True`, an async generator that yields tokens, and a FastAPI `StreamingResponse` that flushes each token to the HTTP client as it arrives.

```python
from fastapi import FastAPI
from fastapi.responses import StreamingResponse
from openai import AsyncOpenAI

app = FastAPI()
client = AsyncOpenAI()

# Step 1 — async generator that yields raw tokens from the LLM:
async def token_generator(prompt: str):
    stream = await client.chat.completions.create(
        model="gpt-4o",
        messages=[{"role": "user", "content": prompt}],
        stream=True
    )
    async for chunk in stream:
        content = chunk.choices[0].delta.content
        if content is not None:
            yield content

# Step 2 — wrap in SSE format for the HTTP client:
async def sse_generator(prompt: str):
    async for token in token_generator(prompt):
        yield f"data: {token}\n\n"   # Server-Sent Events format
    yield "data: [DONE]\n\n"

# Step 3 — FastAPI endpoint returns StreamingResponse:
@app.post("/chat/stream")
async def stream_chat(prompt: str):
    return StreamingResponse(
        sse_generator(prompt),
        media_type="text/event-stream",
        headers={"Cache-Control": "no-cache"}
    )
```

> **What happens at runtime:**
> 1. HTTP request arrives at FastAPI
> 2. FastAPI schedules `stream_chat` as a coroutine
> 3. `StreamingResponse` wraps the generator — Flask/WSGI can't do this natively
> 4. Each `yield` in `sse_generator` flushes a token to the HTTP client immediately
> 5. Client receives tokens one by one — rendering them in real time
> 6. `[DONE]` signals the end of the stream

</details>

<br>

**Q10: How would you batch-embed 10,000 documents for a vector store while respecting OpenAI rate limits?**

<details>
<summary>💡 Show Answer</summary>

**Strong answer:**

> This requires three techniques together: asyncio for concurrency, Semaphore for rate limiting, and return_exceptions for resilience. Optionally, add exponential backoff for 429 errors.

```python
import asyncio
import random
from openai import AsyncOpenAI, RateLimitError

client = AsyncOpenAI()

async def embed_one(text: str, semaphore: asyncio.Semaphore, max_retries: int = 5):
    async with semaphore:
        for attempt in range(max_retries):
            try:
                response = await client.embeddings.create(
                    model="text-embedding-3-small",
                    input=text
                )
                return response.data[0].embedding
            except RateLimitError:
                if attempt == max_retries - 1:
                    raise
                delay = (2 ** attempt) + random.uniform(0, 1)
                await asyncio.sleep(delay)   # exponential backoff

async def embed_corpus(documents: list[str], max_concurrent: int = 20):
    semaphore = asyncio.Semaphore(max_concurrent)

    tasks = [embed_one(doc, semaphore) for doc in documents]
    results = await asyncio.gather(*tasks, return_exceptions=True)

    embeddings = []
    failed_indices = []
    for i, result in enumerate(results):
        if isinstance(result, Exception):
            failed_indices.append(i)
            embeddings.append(None)
        else:
            embeddings.append(result)

    print(f"Embedded {len(documents) - len(failed_indices)}/{len(documents)}")
    if failed_indices:
        print(f"Failed indices: {failed_indices}")
    return embeddings

# Run it:
documents = [f"document text {i}" for i in range(10_000)]
asyncio.run(embed_corpus(documents, max_concurrent=20))
```

> **Key design decisions:**
> - `max_concurrent=20`: 20 in-flight is well under most OpenAI tier limits
> - Semaphore is created once, shared across all tasks — essential for it to work
> - `return_exceptions=True`: one failure does not abort the other 9,999
> - Exponential backoff inside each task handles transient 429s

</details>

<br>

**Q11: How do you handle partial failures in asyncio.gather?**

<details>
<summary>💡 Show Answer</summary>

**Strong answer:**

> There are two levels: handling failures inside individual tasks (retry, fallback), and handling the remaining failures at the gather level with `return_exceptions=True`.

```python
import asyncio

# Level 1 — individual task handles its own retries:
async def resilient_call(prompt: str, max_retries: int = 3) -> str | None:
    for attempt in range(max_retries):
        try:
            return await call_llm(prompt)
        except Exception as e:
            if attempt == max_retries - 1:
                return None   # give up — return None as a signal
            await asyncio.sleep(2 ** attempt)

# Level 2 — gather collects all results including exceptions:
async def batch(prompts: list[str]):
    tasks = [resilient_call(p) for p in prompts]
    results = await asyncio.gather(*tasks, return_exceptions=True)

    # Separate successful results from failed:
    output = []
    for prompt, result in zip(prompts, results):
        if isinstance(result, Exception):
            output.append({"prompt": prompt, "status": "error", "error": str(result)})
        elif result is None:
            output.append({"prompt": prompt, "status": "failed_after_retries"})
        else:
            output.append({"prompt": prompt, "status": "ok", "result": result})

    return output

# Logging failures without raising:
async def batch_logged(prompts):
    results = await asyncio.gather(
        *[call_llm(p) for p in prompts],
        return_exceptions=True
    )
    for i, r in enumerate(results):
        if isinstance(r, Exception):
            print(f"[ERROR] Prompt {i} failed: {r}")
        # Don't raise — log and continue
```

</details>

<br>

**Q12: Why is FastAPI well-suited for LLM API services compared to Flask or Django?**

<details>
<summary>💡 Show Answer</summary>

**Strong answer:**

> FastAPI is ASGI-native (Asynchronous Server Gateway Interface). Flask and Django are WSGI (synchronous) frameworks. The difference matters enormously for LLM workloads.

```
WSGI (Flask, Django sync views):
  Each concurrent request needs a separate OS thread or process.
  100 concurrent LLM calls → 100 threads × ~8MB stack = 800MB RAM overhead.
  Thread scheduling under high load adds latency.
  To scale → need multiple gunicorn workers (processes) or uWSGI threads.

ASGI (FastAPI, Starlette, Django Channels):
  One event loop handles all concurrent requests in one thread.
  100 concurrent LLM calls → 100 coroutines awaiting in one thread.
  Memory overhead: a coroutine frame is ~1KB vs ~8MB per thread.
  Native streaming support (StreamingResponse with async generators).
```

```python
# FastAPI async endpoint — handles 100 concurrent requests in one worker:
@app.post("/chat")
async def chat(prompt: str):
    response = await client.chat.completions.create(...)   # event loop runs others while waiting
    return {"reply": response.choices[0].message.content}

# Flask sync endpoint — blocks the thread for each request:
@app.route("/chat", methods=["POST"])
def chat():
    response = openai.chat.completions.create(...)   # thread blocked — can't serve others
    return {"reply": response.choices[0].message.content}
# Flask needs gunicorn -w 10 to serve 10 concurrent requests — 10 processes!
```

> **Bottom line:** FastAPI + async handles hundreds of concurrent LLM calls with one worker. Flask needs dozens of workers to achieve the same. For LLM APIs where every request waits 3 seconds, async concurrency is a major advantage.

</details>


## ⚠️ Trap Questions

---

### Trap 1 — Blocking call inside an async function

```python
# ❌ time.sleep() blocks the ENTIRE event loop:
async def bad_handler(prompt: str):
    time.sleep(3)               # all other requests are frozen for 3 seconds!
    return "done"

# ❌ Sync HTTP client blocks the event loop:
async def bad_call(prompt: str):
    response = requests.get(url)   # sync — blocks!

# ✅ Use async equivalents:
async def good_handler(prompt: str):
    await asyncio.sleep(3)         # yields to event loop

async def good_call(prompt: str):
    async with httpx.AsyncClient() as c:
        response = await c.get(url)   # non-blocking

# ✅ Must run blocking code? Use asyncio.to_thread:
async def with_blocking_lib(data):
    result = await asyncio.to_thread(legacy_sync_function, data)
```

---

### Trap 2 — Creating a new Semaphore inside each task (no limiting)

```python
# ❌ A new Semaphore per call has no limiting effect:
async def embed(text):
    sem = asyncio.Semaphore(10)   # new semaphore — counter starts at 10 — useless!
    async with sem:
        return await embed_one(text)

tasks = [embed(t) for t in texts]   # all 10,000 run simultaneously!

# ✅ Create ONE semaphore, pass it to all tasks:
async def embed_safe(texts):
    sem = asyncio.Semaphore(10)   # one shared semaphore

    async def embed_with_sem(text):
        async with sem:
            return await embed_one(text)

    return await asyncio.gather(*[embed_with_sem(t) for t in texts])
```

---

### Trap 3 — Using asyncio.run() inside a running event loop

```python
# ❌ RuntimeError: this event loop is already running
async def outer():
    result = asyncio.run(inner())   # can't nest event loops!

# ✅ Just await:
async def outer():
    result = await inner()

# ✅ For Jupyter where loop is always running:
import nest_asyncio
nest_asyncio.apply()
asyncio.run(inner())   # now works
```

---

## 🔥 Rapid-Fire Revision

```
Q: Why do AI apps specifically need async?
A: LLM API calls are pure I/O — your code sends a request and waits.
   Async overlaps the waiting for 100 users, not 3s × 100 = 300s.

Q: async generator vs regular generator?
A: Async generator can await between yields.
   Consumed with 'async for' instead of 'for'.

Q: What does return_exceptions=True do in gather?
A: Returns exceptions as values instead of raising.
   Lets you inspect results and handle failures without aborting the batch.

Q: Why does a Semaphore need to be shared, not per-task?
A: A new Semaphore per task starts with a full counter — no limiting.
   One shared Semaphore across all tasks enforces the global limit.

Q: What is the SSE format for streaming?
A: "data: <token>\n\n" — Server-Sent Events.
   FastAPI StreamingResponse + async generator produces this.

Q: gather vs create_task for 5 parallel LLM calls?
A: gather — fire all 5 and wait for all results in one statement.
   create_task — useful if you need to cancel specific tasks or start them separately.

Q: How do you stream tokens to the user in FastAPI?
A: async generator + StreamingResponse with media_type="text/event-stream"

Q: What does asyncio.to_thread do?
A: Runs a blocking (sync) function in a thread pool without freezing the event loop.
   Use for legacy libraries that don't have async versions.

Q: One process in FastAPI can handle how many concurrent LLM calls?
A: Hundreds — limited by open file descriptors and memory, not thread count.
   Each concurrent call is a cheap coroutine frame (~1KB), not a thread (~8MB).
```

---

## 🔁 Navigation

| | |
|---|---|
| 📖 Theory | [theory.md](./theory.md) |
| ⚡ Cheatsheet | [cheatsheet.md](./cheatsheet.md) |
| 🔧 Practice | [practice.py](./practice.py) |
| ⬅️ Prev | [13 — Concurrency](../13_concurrency/theory.md) |

---

**[🏠 Back to README](../README.md)**

**Prev:** [← Cheat Sheet](./cheatsheet.md) &nbsp;|&nbsp; **Next:** [Python Ai Ecosystem — Theory →](../25_python_ai_ecosystem/theory.md)

**Related Topics:** [Theory](./theory.md) · [Cheat Sheet](./cheatsheet.md)
