# ⚡ Async Python for AI Engineering — Theory

> *"The difference between a demo AI app and a production AI app is often not the model.*
> *It's whether the Python code can handle 100 users asking questions at the same time."*

---

## 🎬 The Problem: 100 Users, 3 Seconds Each

Your AI chatbot needs to handle 100 users at the same time. Each LLM call takes 3 seconds.

**If you use regular sync Python — the naive approach:**

```python
def chat(user_message):
    response = openai.chat.completions.create(
        model="gpt-4o",
        messages=[{"role": "user", "content": user_message}]
    )
    return response.choices[0].message.content

# Handle 100 users sequentially:
for user in users:         # user 1 waits 3s
    reply = chat(user.message)   # user 2 waits 6s
    send(user, reply)             # user 100 waits 300 seconds!
```

User 100 waits **5 minutes** for a response. Your product is dead on arrival.

**With async — the right approach:**

```python
import asyncio

async def chat(user_message):
    response = await async_openai_client.chat.completions.create(
        model="gpt-4o",
        messages=[{"role": "user", "content": user_message}]
    )
    return response.choices[0].message.content

async def handle_all_users(users):
    tasks = [chat(u.message) for u in users]
    replies = await asyncio.gather(*tasks)   # all 100 start simultaneously
    for user, reply in zip(users, replies):
        send(user, reply)

# Total time: ~3 seconds (the length of ONE LLM call)
```

All 100 users get their response in about 3 seconds. But async in AI is more than just concurrency. There is a second dimension: **streaming**. Instead of waiting 3 full seconds for the complete response, the user sees words appearing word by word in real time — exactly like ChatGPT. That is async generators at work.

This module covers both: concurrency patterns for scale, and streaming patterns for user experience.

---

## 📌 Learning Priority

**Must Learn** — Core concept, daily use, interview essential:
`async def` / `await` · `asyncio.gather` · `asyncio.create_task` · Event loop basics · When to use async vs threads

**Should Learn** — Important for real projects, comes up regularly:
`asyncio.Semaphore` for rate limiting · `asyncio.Queue` · Task cancellation (`task.cancel()`) · `async with` / `async for` · `asyncio.timeout()`

**Good to Know** — Useful in specific situations:
`asyncio.TaskGroup` (Python 3.11+) · `asyncio.shield()` · Async generators · `aiofiles` · Debugging async code

**Reference** — Know it exists, look up when needed:
Event loop policies · `asyncio.Barrier` · Multiple event loops · Greenlets vs asyncio

---

## 1️⃣ Quick Recap — async/await in 60 Seconds

You covered asyncio fundamentals in module 13. Here is the core you need to carry into this module:

```python
import asyncio

# async def creates a coroutine — calling it returns a coroutine OBJECT, not a result:
async def greet(name):
    await asyncio.sleep(1)    # yields to event loop while "waiting"
    return f"Hello, {name}!"

# Nothing runs until you await or asyncio.run():
coro = greet("Alice")         # no output — just a coroutine object
result = asyncio.run(greet("Alice"))   # actually runs it
print(result)                 # Hello, Alice!

# await suspends THIS coroutine and lets the event loop run others:
async def main():
    result = await greet("Bob")   # suspend main, run greet, resume with result

# Run two coroutines concurrently — gather runs both and waits for both:
async def main():
    r1, r2 = await asyncio.gather(greet("Alice"), greet("Bob"))
    # Both sleep 1 second simultaneously → total ~1s, not 2s
```

**The golden rule:** `async def` + `await` = "I'm waiting for I/O — let the event loop do other work."

LLM API calls are pure I/O (you send an HTTP request and wait for the model server to respond). That is exactly where async shines.

---

## 2️⃣ Why AI Apps Specifically Need Async

Not every Python app needs async. AI apps almost always do. Here is why.

### LLM API calls are I/O-bound

When your code calls the OpenAI API, your Python process is not doing any computation. It sends an HTTP request and **waits**. The LLM is running on a remote server. Your CPU is idle.

```
SYNC (sequential):
  User 1: [send] ←—— 3s wait ——→ [receive]
  User 2:                          [send] ←—— 3s wait ——→ [receive]
  User 3:                                                   [send] ...
  Wall time: 3s × N users

ASYNC (concurrent):
  User 1: [send] ←—— 3s wait ——→ [receive]
  User 2: [send] ←—— 3s wait ——→ [receive]
  User 3: [send] ←—— 3s wait ——→ [receive]
  All 3 HTTP requests are in-flight simultaneously
  Wall time: ~3s regardless of N users
```

### Streaming responses

LLMs generate tokens one by one. The API can stream them as they are produced. This means your user sees the first word in under 200ms instead of waiting 3 seconds for the full response.

Streaming requires async generators — covered in section 3.

### Parallel embeddings

To embed 10,000 documents for a vector database, you call the embedding API 10,000 times. With sync code: ~10,000 × 0.5s = 83 minutes. With async: send all requests concurrently, complete in a few minutes. But there are rate limits — covered in section 5.

### Why not just use threads?

You could. `ThreadPoolExecutor` with 100 threads would work. But:

```
asyncio:
  Single thread. No thread creation overhead.
  Can handle thousands of concurrent connections.
  Designed for I/O-bound work.
  Native to modern Python frameworks (FastAPI, etc).

ThreadPoolExecutor:
  Each "concurrent" LLM call needs a real OS thread.
  100 threads = 100 × ~8MB stack = ~800MB RAM just for stacks.
  Thread scheduling overhead compounds at scale.
  Works, but not the modern pattern for Python web/API services.
```

For AI services, asyncio is the standard choice.

---

## 3️⃣ Streaming LLM Responses — [Async Generators](../11_generators_iterators/theory.md#-chapter-12-async-generators-python-36)

This is the feature that makes ChatGPT feel responsive. The model generates tokens one at a time, and instead of buffering them all, the API sends each token immediately.

### What is an async generator?

A regular [generator](../11_generators_iterators/theory.md#-chapter-3-generator-functions--yield) uses `yield` to produce values lazily:

```python
def count_up(n):
    for i in range(n):
        yield i        # caller gets one value, then pauses here

for x in count_up(3):
    print(x)   # 0, 1, 2
```

An async generator is the same idea but each `yield` can `await` something first:

```python
async def token_stream(prompt):
    # Imagine the LLM sends back one word at a time
    words = prompt.split()          # mock: pretend each word takes 0.1s
    for word in words:
        await asyncio.sleep(0.1)    # simulate network delay per token
        yield word                  # send the word to the caller NOW, don't wait

# Consume with 'async for':
async def main():
    async for token in token_stream("Hello how are you"):
        print(token, end=" ", flush=True)   # prints: Hello how are you (with pauses)
```

### Real streaming pattern with the OpenAI SDK

```python
import asyncio
from openai import AsyncOpenAI

client = AsyncOpenAI()   # async version of the client

async def stream_chat(prompt: str):
    """Async generator that yields tokens as they arrive from the LLM."""
    stream = await client.chat.completions.create(
        model="gpt-4o",
        messages=[{"role": "user", "content": prompt}],
        stream=True        # this is the key parameter
    )
    async for chunk in stream:
        delta = chunk.choices[0].delta.content
        if delta is not None:
            yield delta    # yield each token as it arrives

# Use it:
async def main():
    print("Response: ", end="", flush=True)
    async for token in stream_chat("Explain async Python in one sentence"):
        print(token, end="", flush=True)
    print()   # newline at end
```

### Why `async for` instead of regular `for`?

Regular `for` calls `__next__()` synchronously. `async for` calls `__anext__()` which can `await` — meaning the event loop can run other tasks between each token arriving.

```python
# This would BLOCK between tokens (wrong):
for token in some_sync_generator():
    display(token)

# This YIELDS to event loop between tokens (correct):
async for token in some_async_generator():
    display(token)
```

### Collecting the full stream into a string

Sometimes you need the complete response but still want to yield tokens for display:

```python
async def stream_and_collect(prompt: str):
    """Stream tokens to console AND return the full text."""
    full_response = []
    async for token in stream_chat(prompt):
        print(token, end="", flush=True)
        full_response.append(token)
    return "".join(full_response)
```

---

## 4️⃣ Making Parallel LLM Calls — asyncio.gather and asyncio.create_task

### asyncio.gather — run N calls, wait for all

The most common pattern. You have a list of tasks and want all results before continuing:

```python
import asyncio
from openai import AsyncOpenAI

client = AsyncOpenAI()

async def call_llm(prompt: str) -> str:
    response = await client.chat.completions.create(
        model="gpt-4o",
        messages=[{"role": "user", "content": prompt}]
    )
    return response.choices[0].message.content

async def parallel_calls():
    prompts = [
        "Summarize the French Revolution in one sentence.",
        "What is gradient descent?",
        "Explain recursion to a 10-year-old.",
    ]
    # All 3 HTTP requests go out simultaneously:
    results = await asyncio.gather(
        call_llm(prompts[0]),
        call_llm(prompts[1]),
        call_llm(prompts[2]),
    )
    # results is a list in the same order as the inputs
    for prompt, result in zip(prompts, results):
        print(f"Q: {prompt}\nA: {result}\n")

# With a dynamic list:
async def parallel_calls_dynamic(prompts: list[str]) -> list[str]:
    tasks = [call_llm(p) for p in prompts]
    return await asyncio.gather(*tasks)   # unpack the list with *
```

### asyncio.create_task — fire and continue

`gather` waits for everything before moving on. `create_task` lets you start a coroutine and keep doing other work while it runs in the background:

```python
async def main():
    # Start a long LLM call in the background:
    task1 = asyncio.create_task(call_llm("Tell me a story about async Python"))

    # Do other work while the LLM is thinking:
    await asyncio.sleep(0)   # yield to event loop so task1 can start
    print("Doing other setup work while LLM is running...")
    await prepare_database()

    # Now collect the result (await here if not already done):
    result = await task1
    print(result)
```

### gather vs create_task — when to use which

```
asyncio.gather(*tasks):
  Use when: you have a fixed list of tasks and need all results before continuing.
  Returns: list of results in input order.
  Error behavior: first exception cancels others (unless return_exceptions=True).

asyncio.create_task(coro):
  Use when: you want to start a task now but collect it later.
  Returns: a Task object you can await, cancel, or add callbacks to.
  Good for: background work, fire-and-forget side effects.

Timing difference:
  task = asyncio.create_task(coro())  ← scheduled immediately
  result = await task                 ← collected later

  result = await asyncio.gather(coro())  ← scheduled AND collected in one step
```

---

## 5️⃣ Parallel Embeddings — Batch Processing with gather + Semaphore

Embedding 10,000 documents for a RAG (Retrieval-Augmented Generation) system is a common task. Here is the naive async approach and why it fails:

```python
# ❌ Sends 10,000 requests simultaneously — hits rate limits immediately:
async def embed_all_naive(texts: list[str]) -> list[list[float]]:
    tasks = [embed_one(text) for text in texts]
    return await asyncio.gather(*tasks)   # 10,000 concurrent requests!
```

The OpenAI embeddings API has rate limits (e.g., 3,000 requests per minute, 1 million tokens per minute). Sending 10,000 requests at once will get you `RateLimitError` on most of them.

The solution: control concurrency with `asyncio.Semaphore`.

```python
import asyncio
from openai import AsyncOpenAI

client = AsyncOpenAI()

async def embed_one(text: str, semaphore: asyncio.Semaphore) -> list[float]:
    async with semaphore:   # blocks if too many calls are running
        response = await client.embeddings.create(
            model="text-embedding-3-small",
            input=text
        )
        return response.data[0].embedding

async def embed_all(texts: list[str], max_concurrent: int = 20) -> list[list[float]]:
    semaphore = asyncio.Semaphore(max_concurrent)   # max 20 in-flight at once
    tasks = [embed_one(text, semaphore) for text in texts]
    return await asyncio.gather(*tasks)

# Usage:
async def main():
    documents = ["doc 1 text", "doc 2 text", ...]   # 10,000 docs
    embeddings = await embed_all(documents, max_concurrent=20)
    print(f"Embedded {len(embeddings)} documents")
```

### Processing in batches with progress tracking

```python
import asyncio

async def embed_in_batches(
    texts: list[str],
    batch_size: int = 100,
    max_concurrent: int = 20
) -> list[list[float]]:
    """Embed texts in batches, showing progress."""
    semaphore = asyncio.Semaphore(max_concurrent)
    all_embeddings = []

    for i in range(0, len(texts), batch_size):
        batch = texts[i : i + batch_size]
        tasks = [embed_one(text, semaphore) for text in batch]
        batch_results = await asyncio.gather(*tasks, return_exceptions=True)

        # Handle partial failures:
        for j, result in enumerate(batch_results):
            if isinstance(result, Exception):
                print(f"Failed to embed text {i+j}: {result}")
                all_embeddings.append(None)
            else:
                all_embeddings.append(result)

        print(f"Progress: {min(i + batch_size, len(texts))}/{len(texts)}")

    return all_embeddings
```

---

## 6️⃣ Semaphores for Rate Limiting

`asyncio.Semaphore` is the correct tool for controlling how many concurrent operations run at once. Think of it as a bouncer at a club: only N people inside at a time.

```python
import asyncio

# Without semaphore — all 100 run simultaneously:
async def bad_parallel(items):
    tasks = [process(item) for item in items]
    return await asyncio.gather(*tasks)   # 100 concurrent requests!

# With semaphore — max 10 at a time:
async def good_parallel(items, limit=10):
    semaphore = asyncio.Semaphore(limit)

    async def process_with_limit(item):
        async with semaphore:      # blocks until a slot is free
            return await process(item)

    tasks = [process_with_limit(item) for item in items]
    return await asyncio.gather(*tasks)
```

### The pattern in detail

```python
semaphore = asyncio.Semaphore(10)   # internal counter starts at 10

async with semaphore:
    # semaphore.acquire() called → counter goes from 10 to 9
    # if counter was 0 → this coroutine BLOCKS until another releases
    await do_work()
    # semaphore.release() called → counter goes from 9 to 10

# Rule of thumb for OpenAI rate limits:
# text-embedding-3-small: max_concurrent=20 is safe for most tiers
# GPT-4o API calls: max_concurrent=10 is conservative and safe
# Adjust based on your actual tier and observed 429 errors
```

### Semaphore with retry on rate limit errors

```python
import asyncio
import random

async def call_with_retry(
    prompt: str,
    semaphore: asyncio.Semaphore,
    max_retries: int = 3
) -> str:
    async with semaphore:
        for attempt in range(max_retries):
            try:
                return await call_llm(prompt)
            except RateLimitError:
                if attempt == max_retries - 1:
                    raise
                wait = 2 ** attempt + random.random()   # exponential backoff
                print(f"Rate limited, waiting {wait:.1f}s...")
                await asyncio.sleep(wait)
```

---

## 7️⃣ Async Context Managers — async with

You have used `with` for regular context managers (files, locks). Async context managers add `await` to the enter and exit steps — essential for async HTTP clients.

```python
# Regular context manager (sync):
with open("file.txt") as f:
    data = f.read()
# __enter__ and __exit__ are called synchronously

# Async context manager:
async with httpx.AsyncClient() as client:
    response = await client.get("https://api.openai.com/v1/models")
# __aenter__ and __aexit__ are awaited — can do async setup/teardown
```

### Using httpx.AsyncClient for LLM APIs

`httpx` is the modern async HTTP client for Python. It is also used internally by the OpenAI SDK.

```python
import httpx
import asyncio

async def call_openai_raw(prompt: str, api_key: str) -> str:
    """Direct HTTP call to OpenAI API — shows what the SDK does under the hood."""
    async with httpx.AsyncClient() as client:
        response = await client.post(
            "https://api.openai.com/v1/chat/completions",
            headers={"Authorization": f"Bearer {api_key}"},
            json={
                "model": "gpt-4o",
                "messages": [{"role": "user", "content": prompt}]
            },
            timeout=30.0
        )
        response.raise_for_status()
        return response.json()["choices"][0]["message"]["content"]

# Reuse the client across many calls (connection pooling):
async def call_many(prompts: list[str], api_key: str) -> list[str]:
    async with httpx.AsyncClient() as client:   # single client, reused for all calls
        tasks = [
            call_with_client(client, prompt, api_key)
            for prompt in prompts
        ]
        return await asyncio.gather(*tasks)
```

### Building your own async context manager

```python
from contextlib import asynccontextmanager

@asynccontextmanager
async def managed_llm_session(api_key: str):
    """Sets up and tears down an LLM client with logging."""
    client = AsyncOpenAI(api_key=api_key)
    print("LLM session starting")
    try:
        yield client
    finally:
        print("LLM session ending")
        await client.close()

async def main():
    async with managed_llm_session("sk-...") as client:
        result = await client.chat.completions.create(...)
```

---

## 8️⃣ Async Queues — Producer-Consumer for Document Pipelines

When processing a large collection of documents (for indexing, embedding, or summarization), you often have a pipeline: one part reads/downloads documents while another processes them. `asyncio.Queue` is the right tool.

```python
import asyncio

async def producer(queue: asyncio.Queue, document_paths: list[str]):
    """Reads documents from disk and puts them into the queue."""
    for path in document_paths:
        async with aiofiles.open(path) as f:
            content = await f.read()
        await queue.put({"path": path, "content": content})
        print(f"Queued: {path}")
    # Signal that production is done:
    await queue.put(None)   # sentinel value

async def consumer(queue: asyncio.Queue, results: list):
    """Takes documents from queue, embeds them, stores result."""
    while True:
        item = await queue.get()        # blocks until item available
        if item is None:
            queue.task_done()
            break
        try:
            embedding = await embed_one(item["content"])
            results.append({"path": item["path"], "embedding": embedding})
            print(f"Embedded: {item['path']}")
        except Exception as e:
            print(f"Failed to embed {item['path']}: {e}")
        finally:
            queue.task_done()           # always mark as done

async def process_pipeline(document_paths: list[str]) -> list[dict]:
    queue = asyncio.Queue(maxsize=50)   # buffer up to 50 docs in memory
    results = []

    # Start producer and consumer concurrently:
    await asyncio.gather(
        producer(queue, document_paths),
        consumer(queue, results),
    )

    await queue.join()   # wait for all items to be processed
    return results
```

### Multiple consumers for higher throughput

```python
async def process_with_multiple_consumers(paths: list[str], num_consumers: int = 5):
    queue = asyncio.Queue(maxsize=100)
    results = []

    # Multiple consumer tasks process in parallel:
    consumer_tasks = [
        asyncio.create_task(consumer(queue, results))
        for _ in range(num_consumers)
    ]

    # Producer fills the queue:
    await producer_multi(queue, paths, num_consumers)   # puts N sentinels at end

    # Wait for consumers:
    await asyncio.gather(*consumer_tasks)
    return results
```

---

## 9️⃣ Error Handling in Async

Error handling in async code follows the same `try/except` pattern as sync code, but there are a few places where async adds complexity.

### try/except in coroutines

```python
async def safe_llm_call(prompt: str) -> str | None:
    try:
        return await call_llm(prompt)
    except RateLimitError as e:
        print(f"Rate limited: {e}")
        return None
    except APIConnectionError as e:
        print(f"Connection error: {e}")
        return None
    except Exception as e:
        print(f"Unexpected error: {e}")
        raise   # re-raise unexpected errors
```

### asyncio.gather with return_exceptions=True

By default, if any task in `gather` raises an exception, it propagates immediately and cancels the other tasks. This is often not what you want for batch processing:

```python
import asyncio

# ❌ Default behavior — first failure stops everything:
results = await asyncio.gather(
    call_llm("prompt 1"),
    call_llm("prompt 2"),   # if this fails, prompt 3 is cancelled
    call_llm("prompt 3"),
)

# ✅ return_exceptions=True — collect results AND exceptions:
results = await asyncio.gather(
    call_llm("prompt 1"),
    call_llm("prompt 2"),
    call_llm("prompt 3"),
    return_exceptions=True   # exceptions are returned as values, not raised
)

# Now handle results:
for i, result in enumerate(results):
    if isinstance(result, Exception):
        print(f"Task {i} failed: {result}")
    else:
        print(f"Task {i} succeeded: {result[:50]}...")
```

### Timeouts on individual calls

```python
import asyncio

async def call_with_timeout(prompt: str, timeout_seconds: float = 30.0) -> str:
    try:
        return await asyncio.wait_for(
            call_llm(prompt),
            timeout=timeout_seconds
        )
    except asyncio.TimeoutError:
        print(f"LLM call timed out after {timeout_seconds}s")
        return "[timeout]"

# In a batch — each call has its own timeout:
async def batch_with_timeouts(prompts: list[str]) -> list[str]:
    tasks = [call_with_timeout(p, timeout_seconds=30.0) for p in prompts]
    return await asyncio.gather(*tasks, return_exceptions=True)
```

### Task cancellation

```python
async def process_with_deadline(prompts: list[str], total_timeout: float = 60.0):
    """Process all prompts but give up after total_timeout seconds."""
    try:
        async with asyncio.timeout(total_timeout):   # Python 3.11+
            return await asyncio.gather(*[call_llm(p) for p in prompts])
    except asyncio.TimeoutError:
        print("Batch exceeded time limit")
        return []
```

---

## 🔟 Running Async from Sync Code

Sometimes you need to call async code from a sync context — the entry point of a script, a Django view, or a Jupyter notebook.

### asyncio.run — the standard entry point

```python
import asyncio

# asyncio.run creates a new event loop, runs the coroutine, closes the loop:
result = asyncio.run(my_async_function())

# Use at the top level of your script:
if __name__ == "__main__":
    asyncio.run(main())

# ❌ Do NOT call asyncio.run inside an already-running event loop:
async def bad():
    asyncio.run(inner())    # RuntimeError: event loop already running

# ✅ Use await instead:
async def good():
    await inner()
```

### nest_asyncio for Jupyter notebooks

Jupyter runs its own event loop. `asyncio.run()` raises `RuntimeError` inside a notebook cell.

```python
# In a Jupyter cell:
import nest_asyncio
nest_asyncio.apply()   # patches asyncio to allow nested loops

# Now you can use asyncio.run in a notebook cell:
result = asyncio.run(my_async_function())

# Or just use await directly in Jupyter (works in modern Jupyter without nest_asyncio):
result = await my_async_function()
```

### Running async from sync code in production

```python
import asyncio
from concurrent.futures import ThreadPoolExecutor

# If you must call async from sync code (e.g., in a Django view):
def sync_wrapper(prompt: str) -> str:
    """Call async LLM from sync code by running in a new event loop."""
    return asyncio.run(call_llm(prompt))

# Better: use a dedicated thread with its own event loop:
_executor = ThreadPoolExecutor(max_workers=1)
_loop = asyncio.new_event_loop()

def call_async_from_sync(coro):
    future = asyncio.run_coroutine_threadsafe(coro, _loop)
    return future.result(timeout=60)
```

---

## 1️⃣1️⃣ Async in FastAPI for AI Endpoints

FastAPI is built on asyncio. Every request handler can be an `async def` function, and the framework handles concurrency automatically.

### Why FastAPI + async = perfect for LLM APIs

```
FastAPI uses Starlette (ASGI framework) under the hood.
ASGI = Asynchronous Server Gateway Interface.

When request comes in:
  FastAPI schedules the handler as a coroutine.
  While one handler awaits an LLM call, the event loop handles other requests.
  Single worker process handles hundreds of concurrent LLM requests.

Compared to Flask/Django (WSGI, sync):
  Each concurrent request needs a separate worker process or thread.
  10 concurrent LLM calls = 10 processes × memory overhead.
  FastAPI: 100 concurrent LLM calls = 1 process + event loop.
```

### Basic async FastAPI endpoint

```python
from fastapi import FastAPI
from openai import AsyncOpenAI

app = FastAPI()
client = AsyncOpenAI()

@app.post("/chat")
async def chat_endpoint(prompt: str) -> dict:
    # This is a coroutine — FastAPI awaits it automatically:
    response = await client.chat.completions.create(
        model="gpt-4o",
        messages=[{"role": "user", "content": prompt}]
    )
    return {"reply": response.choices[0].message.content}

# 100 users hitting /chat simultaneously → 100 concurrent awaits
# All 100 LLM calls are in-flight at once → responses in ~3s, not 300s
```

### Streaming endpoint with Server-Sent Events

```python
from fastapi import FastAPI
from fastapi.responses import StreamingResponse
from openai import AsyncOpenAI

app = FastAPI()
client = AsyncOpenAI()

async def stream_tokens(prompt: str):
    """Async generator that yields SSE-formatted token chunks."""
    stream = await client.chat.completions.create(
        model="gpt-4o",
        messages=[{"role": "user", "content": prompt}],
        stream=True
    )
    async for chunk in stream:
        delta = chunk.choices[0].delta.content
        if delta:
            yield f"data: {delta}\n\n"   # SSE format
    yield "data: [DONE]\n\n"

@app.post("/stream")
async def stream_endpoint(prompt: str):
    return StreamingResponse(
        stream_tokens(prompt),
        media_type="text/event-stream"
    )

# The client receives tokens as they arrive — the ChatGPT experience
```

### Dependency injection for shared async clients

```python
from fastapi import FastAPI, Depends
from openai import AsyncOpenAI

app = FastAPI()

# One shared client for the whole application — connection pooling:
_client = AsyncOpenAI()

def get_llm_client() -> AsyncOpenAI:
    return _client

@app.post("/summarize")
async def summarize(text: str, client: AsyncOpenAI = Depends(get_llm_client)):
    response = await client.chat.completions.create(
        model="gpt-4o",
        messages=[{"role": "user", "content": f"Summarize: {text}"}]
    )
    return {"summary": response.choices[0].message.content}
```

---

## 1️⃣2️⃣ Real Patterns: Production Async AI

### Pattern 1 — Streaming chat endpoint

The classic ChatGPT-style pattern. Tokens appear as they are generated.

```python
from fastapi import FastAPI
from fastapi.responses import StreamingResponse
from openai import AsyncOpenAI
import asyncio

app = FastAPI()
client = AsyncOpenAI()

async def generate_stream(messages: list[dict]):
    """Core streaming logic — yields token strings."""
    stream = await client.chat.completions.create(
        model="gpt-4o",
        messages=messages,
        stream=True,
        temperature=0.7,
        max_tokens=2000
    )
    async for chunk in stream:
        content = chunk.choices[0].delta.content
        if content is not None:
            yield content

@app.post("/chat/stream")
async def streaming_chat(prompt: str):
    messages = [{"role": "user", "content": prompt}]

    async def event_stream():
        async for token in generate_stream(messages):
            yield f"data: {token}\n\n"
        yield "data: [DONE]\n\n"

    return StreamingResponse(event_stream(), media_type="text/event-stream")
```

### Pattern 2 — Parallel document embedding pipeline

Process thousands of documents for a vector store with controlled concurrency.

```python
import asyncio
from openai import AsyncOpenAI

client = AsyncOpenAI()

async def embed_document(
    doc: dict,
    semaphore: asyncio.Semaphore
) -> dict:
    """Embed a single document with rate limiting."""
    async with semaphore:
        response = await client.embeddings.create(
            model="text-embedding-3-small",
            input=doc["content"]
        )
        return {
            "id": doc["id"],
            "content": doc["content"],
            "embedding": response.data[0].embedding
        }

async def embed_corpus(documents: list[dict], max_concurrent: int = 20) -> list[dict]:
    """Embed all documents with controlled concurrency."""
    semaphore = asyncio.Semaphore(max_concurrent)
    tasks = [embed_document(doc, semaphore) for doc in documents]
    results = await asyncio.gather(*tasks, return_exceptions=True)

    # Separate successes from failures:
    embedded = []
    for doc, result in zip(documents, results):
        if isinstance(result, Exception):
            print(f"Failed to embed {doc['id']}: {result}")
        else:
            embedded.append(result)

    print(f"Embedded {len(embedded)}/{len(documents)} documents")
    return embedded
```

### Pattern 3 — Rate-limited batch processing with retry

Production-grade batch processing that respects API rate limits.

```python
import asyncio
import random
from openai import AsyncOpenAI, RateLimitError

client = AsyncOpenAI()

async def call_with_backoff(
    prompt: str,
    semaphore: asyncio.Semaphore,
    max_retries: int = 5
) -> str:
    """Call LLM with exponential backoff on rate limit errors."""
    async with semaphore:
        for attempt in range(max_retries):
            try:
                response = await client.chat.completions.create(
                    model="gpt-4o",
                    messages=[{"role": "user", "content": prompt}]
                )
                return response.choices[0].message.content
            except RateLimitError:
                if attempt == max_retries - 1:
                    raise
                delay = (2 ** attempt) + random.random()
                print(f"Rate limited (attempt {attempt+1}), retrying in {delay:.1f}s")
                await asyncio.sleep(delay)

async def batch_process(prompts: list[str], max_concurrent: int = 10) -> list[str | None]:
    """Process all prompts respecting rate limits."""
    semaphore = asyncio.Semaphore(max_concurrent)
    tasks = [call_with_backoff(p, semaphore) for p in prompts]
    results = await asyncio.gather(*tasks, return_exceptions=True)
    return [None if isinstance(r, Exception) else r for r in results]
```

---

## 🔥 Summary

```
CORE CONCEPTS:
  async def / await  — coroutine definition and suspension
  asyncio.run()      — entry point: creates event loop, runs coroutine
  asyncio.gather()   — run N coroutines concurrently, wait for all
  asyncio.create_task() — schedule coroutine, collect result later
  asyncio.Semaphore  — limit N concurrent operations (rate limiting)
  asyncio.Queue      — producer-consumer between coroutines
  async for          — iterate over async generators
  async with         — async context managers (HTTP clients, etc.)

AI-SPECIFIC PATTERNS:
  stream=True + async for chunk  → streaming LLM responses
  gather(*tasks)                 → parallel LLM calls
  Semaphore(N) + gather          → rate-limited batch embedding
  asyncio.Queue + producer/consumer → document processing pipeline
  FastAPI async def              → concurrent LLM request handling
  return_exceptions=True         → resilient batch processing

DECISION GUIDE:
  Need results from N LLM calls? → asyncio.gather
  Need to start work and collect later? → asyncio.create_task
  Need to respect rate limits? → asyncio.Semaphore
  Need to stream tokens to user? → async generator + async for
  Need to process pipeline? → asyncio.Queue
  Running from Jupyter? → nest_asyncio or direct await
  Building an API? → FastAPI with async def handlers
```

---

## 🔁 Navigation

| | |
|---|---|
| 🎯 Interview | [interview.md](./interview.md) |
| ⚡ Cheatsheet | [cheatsheet.md](./cheatsheet.md) |
| 🔧 Practice | [practice.py](./practice.py) |
| ⬅️ Prev | [13 — Concurrency](../13_concurrency/theory.md) |

---

**[🏠 Back to README](../README.md)**

**Prev:** [← Pandas For Ai — Interview Q&A](../23_pandas_for_ai/interview.md) &nbsp;|&nbsp; **Next:** [Cheat Sheet →](./cheatsheet.md)

**Related Topics:** [Cheat Sheet](./cheatsheet.md) · [Interview Q&A](./interview.md)
