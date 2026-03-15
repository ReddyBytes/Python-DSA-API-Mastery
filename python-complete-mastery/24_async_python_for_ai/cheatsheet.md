# ⚡ Async Python for AI — Cheatsheet

> Quick reference: async/await, gather, create_task, Semaphore, async generators, streaming, error handling, FastAPI.

---

## ⚡ async/await Syntax

```python
import asyncio

# Define a coroutine:
async def my_func(arg):
    await asyncio.sleep(1)   # yield to event loop
    return arg * 2

# Run from sync code:
result = asyncio.run(my_func(5))

# Await inside another coroutine:
async def main():
    result = await my_func(5)   # suspends main, runs my_func, resumes
    return result
```

---

## 🔀 Concurrent Execution

```python
# gather — run N coroutines concurrently, wait for all:
results = await asyncio.gather(
    call_llm("prompt 1"),
    call_llm("prompt 2"),
    call_llm("prompt 3"),
)
# results = [result1, result2, result3]  (same order as input)

# gather from a list:
tasks = [call_llm(p) for p in prompts]
results = await asyncio.gather(*tasks)

# gather with exception handling — returns exceptions as values:
results = await asyncio.gather(*tasks, return_exceptions=True)
for r in results:
    if isinstance(r, Exception):
        print(f"Failed: {r}")

# create_task — start now, collect later:
task1 = asyncio.create_task(call_llm("prompt 1"))
task2 = asyncio.create_task(call_llm("prompt 2"))
# ... do other work ...
r1 = await task1
r2 = await task2

# wait_for — add a timeout to any coroutine:
try:
    result = await asyncio.wait_for(call_llm("prompt"), timeout=30.0)
except asyncio.TimeoutError:
    result = "[timeout]"
```

---

## 🚦 Semaphore — Rate Limiting

```python
import asyncio

# Limit to max N concurrent operations:
semaphore = asyncio.Semaphore(20)   # max 20 in-flight at once

async def rate_limited_call(prompt, semaphore):
    async with semaphore:           # blocks if 20 already running
        return await call_llm(prompt)

# Use in batch:
async def batch(prompts, max_concurrent=20):
    sem = asyncio.Semaphore(max_concurrent)
    tasks = [rate_limited_call(p, sem) for p in prompts]
    return await asyncio.gather(*tasks, return_exceptions=True)
```

---

## 🌊 Async Generators — Streaming

```python
# Define an async generator:
async def token_stream(prompt):
    words = prompt.split()
    for word in words:
        await asyncio.sleep(0.1)   # simulate token delay
        yield word                 # send token to caller immediately

# Consume with async for:
async def main():
    async for token in token_stream("Hello async world"):
        print(token, end=" ", flush=True)

# Real OpenAI streaming pattern:
from openai import AsyncOpenAI
client = AsyncOpenAI()

async def stream_llm(prompt: str):
    stream = await client.chat.completions.create(
        model="gpt-4o",
        messages=[{"role": "user", "content": prompt}],
        stream=True
    )
    async for chunk in stream:
        delta = chunk.choices[0].delta.content
        if delta is not None:
            yield delta

# Collect streamed result into a string:
full_text = "".join([token async for token in stream_llm("hi")])
```

---

## 🔧 Async Context Managers

```python
# async with — for async setup/teardown:
import httpx

async def fetch(url):
    async with httpx.AsyncClient() as client:   # __aenter__ awaited
        response = await client.get(url)
        return response.text
    # __aexit__ awaited — connection closed cleanly

# Build your own with asynccontextmanager:
from contextlib import asynccontextmanager

@asynccontextmanager
async def managed_client(api_key):
    client = AsyncOpenAI(api_key=api_key)
    try:
        yield client
    finally:
        await client.close()

async def main():
    async with managed_client("sk-...") as client:
        result = await client.chat.completions.create(...)
```

---

## 📬 Async Queue — Producer/Consumer

```python
import asyncio

async def producer(queue, items):
    for item in items:
        await queue.put(item)   # blocks if queue full
    await queue.put(None)       # sentinel

async def consumer(queue, results):
    while True:
        item = await queue.get()    # blocks until item available
        if item is None:
            queue.task_done()
            break
        result = await process(item)
        results.append(result)
        queue.task_done()

async def pipeline(items):
    queue = asyncio.Queue(maxsize=50)
    results = []
    await asyncio.gather(
        producer(queue, items),
        consumer(queue, results),
    )
    await queue.join()
    return results
```

---

## ❌ Error Handling

```python
# try/except works inside async functions normally:
async def safe_call(prompt):
    try:
        return await call_llm(prompt)
    except RateLimitError:
        await asyncio.sleep(5)
        return await call_llm(prompt)   # retry once
    except Exception as e:
        print(f"Unexpected: {e}")
        raise

# Exponential backoff pattern:
import random
async def with_backoff(coro_func, *args, max_retries=5):
    for attempt in range(max_retries):
        try:
            return await coro_func(*args)
        except RateLimitError:
            if attempt == max_retries - 1:
                raise
            delay = (2 ** attempt) + random.random()
            await asyncio.sleep(delay)

# gather: don't let one failure kill the batch:
results = await asyncio.gather(*tasks, return_exceptions=True)
successes = [r for r in results if not isinstance(r, Exception)]
```

---

## 🚀 Running Async from Sync / Jupyter

```python
# Standard entry point:
import asyncio

asyncio.run(main())        # creates new event loop, runs, closes it

# In a script:
if __name__ == "__main__":
    asyncio.run(main())

# In Jupyter — asyncio.run() raises RuntimeError (loop already running):
import nest_asyncio
nest_asyncio.apply()       # patches asyncio to allow nesting
result = asyncio.run(main())

# Or in Jupyter, just use await directly in cells:
result = await main()

# From sync code in production:
result = asyncio.run(async_func())   # safe if no loop is running
```

---

## 🌐 FastAPI Streaming Pattern

```python
from fastapi import FastAPI
from fastapi.responses import StreamingResponse
from openai import AsyncOpenAI

app = FastAPI()
client = AsyncOpenAI()

async def token_generator(prompt: str):
    stream = await client.chat.completions.create(
        model="gpt-4o",
        messages=[{"role": "user", "content": prompt}],
        stream=True
    )
    async for chunk in stream:
        content = chunk.choices[0].delta.content
        if content:
            yield f"data: {content}\n\n"   # SSE format
    yield "data: [DONE]\n\n"

@app.post("/chat/stream")
async def chat_stream(prompt: str):
    return StreamingResponse(
        token_generator(prompt),
        media_type="text/event-stream"
    )

@app.post("/chat")
async def chat(prompt: str) -> dict:
    # Standard async endpoint — handles 100s of concurrent requests:
    response = await client.chat.completions.create(
        model="gpt-4o",
        messages=[{"role": "user", "content": prompt}]
    )
    return {"reply": response.choices[0].message.content}
```

---

## 🔴 Common Gotchas

```python
# 1 — Blocking call inside async function freezes the event loop:
async def bad():
    time.sleep(3)             # blocks ALL other requests for 3 seconds!
    requests.get(url)         # sync HTTP — blocks!
async def good():
    await asyncio.sleep(3)
    async with httpx.AsyncClient() as c: await c.get(url)

# 2 — asyncio.run() inside an already-running loop:
async def bad():
    asyncio.run(inner())      # RuntimeError!
async def good():
    await inner()

# 3 — Not using return_exceptions in batch gather:
results = await asyncio.gather(*tasks)              # one failure crashes all
results = await asyncio.gather(*tasks,
          return_exceptions=True)                   # safe batch

# 4 — Creating a new Semaphore inside the task (no limiting):
async def wrong(item):
    sem = asyncio.Semaphore(10)   # new semaphore every call — no limiting!
    async with sem: ...
async def correct(item, sem):    # pass one shared semaphore
    async with sem: ...

# 5 — Forgetting async for with async generators:
for token in async_gen():       # TypeError — must use async for
    pass
async for token in async_gen(): # correct
    pass
```

---

## 🔥 Rapid-Fire

```
Q: What does await do?
A: Suspends the current coroutine and yields to the event loop until the result is ready.

Q: gather vs create_task?
A: gather: run N and wait for all, returns list.
   create_task: schedule one, collect its result later with await.

Q: What is a Semaphore used for in AI code?
A: Rate limiting — limit how many LLM API calls run concurrently to avoid 429 errors.

Q: How do you stream LLM tokens?
A: async generator with yield inside async for over stream=True response.

Q: Why does time.sleep() break async code?
A: It blocks the thread, so the event loop cannot run any other coroutines.
   Use await asyncio.sleep() instead.

Q: return_exceptions=True in gather — what does it do?
A: Exceptions are returned as values in the results list instead of being raised.
   Allows partial failures without killing the whole batch.

Q: How to use async in Jupyter?
A: Install nest_asyncio and call nest_asyncio.apply(), or just use await in cells directly.

Q: Why is FastAPI ideal for LLM APIs?
A: It's ASGI/async-native. async def handlers let one process handle hundreds of
   concurrent LLM calls via the event loop, not hundreds of threads.
```

---

## 🔁 Navigation

| | |
|---|---|
| 📖 Theory | [theory.md](./theory.md) |
| 🎯 Interview | [interview.md](./interview.md) |
| 🔧 Practice | [practice.py](./practice.py) |
| ⬅️ Prev | [13 — Concurrency](../13_concurrency/theory.md) |
