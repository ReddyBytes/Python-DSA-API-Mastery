# Async Python for AI — Practice

## Quick Index

| Q | Topic | Difficulty |
|---|---|---|
| [Q1](#q1) | async/await basics — define and run a coroutine | 🟢 |
| [Q2](#q2) | async/await basics — calling without await | 🟢 |
| [Q3](#q3) | Why AI needs async — sync vs async LLM timing | 🟢 |
| [Q4](#q4) | Why AI needs async — blocking vs non-blocking | 🟢 |
| [Q5](#q5) | Streaming LLM — async generator with yield | 🟢 |
| [Q6](#q6) | Streaming LLM — async for loop consumption | 🟢 |
| [Q7](#q7) | Streaming LLM — collect stream into string | 🟡 |
| [Q8](#q8) | Parallel LLM calls — asyncio.gather for 3 prompts | 🟢 |
| [Q9](#q9) | Parallel LLM calls — create_task + await | 🟡 |
| [Q10](#q10) | Parallel LLM calls — results order guarantee | 🟡 |
| [Q11](#q11) | Parallel embeddings — gather + Semaphore pattern | 🟡 |
| [Q12](#q12) | Parallel embeddings — limit N concurrent with Semaphore | 🟡 |
| [Q13](#q13) | Parallel embeddings — chunked batching with progress | 🟠 |
| [Q14](#q14) | Semaphore rate limiting — asyncio.Semaphore(N) basics | 🟢 |
| [Q15](#q15) | Semaphore rate limiting — bounded concurrency wrapper | 🟡 |
| [Q16](#q16) | Semaphore rate limiting — Semaphore vs sleep-based throttle | 🟡 |
| [Q17](#q17) | Async context managers — async with for HTTP session | 🟡 |
| [Q18](#q18) | Async context managers — custom AsyncContextManager class | 🟠 |
| [Q19](#q19) | Async queues — basic producer/consumer with asyncio.Queue | 🟡 |
| [Q20](#q20) | Async queues — multiple consumers for higher throughput | 🟡 |
| [Q21](#q21) | Async queues — backpressure with maxsize | 🟠 |
| [Q22](#q22) | Error handling — try/except in a coroutine | 🟢 |
| [Q23](#q23) | Error handling — gather(return_exceptions=True) | 🟡 |
| [Q24](#q24) | Async from sync — asyncio.run() entry point | 🟢 |
| [Q25](#q25) | Async from sync — asyncio.to_thread() for blocking calls | 🟡 |
| [Q26](#q26) | FastAPI AI endpoint — async def route | 🟡 |
| [Q27](#q27) | FastAPI AI endpoint — streaming response with SSE | 🟠 |
| [Q28](#q28) | Production patterns — retry with exponential backoff | 🟠 |
| [Q29](#q29) | Production patterns — asyncio.TaskGroup structured concurrency | 🟠 |
| [Q30](#q30) | Production patterns — capstone parallel batch processor | 🟠 |

---

## Ch1 — async/await Recap

<a id="q1"></a>

### Q1 · async/await basics — define and run a coroutine 🟢

> 🛠️ **Solve locally:** [practice_local.py → Q1](./practice_local.py)


Write an async function called `greet` that takes a name, waits 1 second, then returns `"Hello, {name}!"`. Run it with `asyncio.run()` and print the result.


<details>
<summary>💡 Hint</summary>
Use `async def` to define it and `await asyncio.sleep(1)` inside. Call it with `asyncio.run(greet("Alice"))`.
</details>

<details>
<summary>✅ Answer</summary>

```python
import asyncio

async def greet(name):
    await asyncio.sleep(1)        # ← yields to event loop; doesn't block it
    return f"Hello, {name}!"

result = asyncio.run(greet("Alice"))  # ← creates loop, runs, closes it
print(result)                     # Hello, Alice!
```

**Why:** `async def` creates a coroutine object. Nothing runs until you `await` it or wrap it in `asyncio.run()`. `await asyncio.sleep(1)` suspends this coroutine for 1 second without freezing the whole program.
</details>

---

<a id="q2"></a>

### Q2 · async/await basics — calling without await 🟢

> 🛠️ **Solve locally:** [practice_local.py → Q2](./practice_local.py)


What does this code print, and why is it a bug? How do you fix it?

```python
import asyncio

async def get_answer():
    return 42

result = get_answer()
print(result)
```


<details>
<summary>💡 Hint</summary>
Calling `async def` without `await` returns a coroutine object, not the value. Check what Python prints for an unawaited coroutine.
</details>

<details>
<summary>✅ Answer</summary>

```python
import asyncio

async def get_answer():
    return 42

# BAD — prints something like: <coroutine object get_answer at 0x...>
result = get_answer()
print(result)   # ← coroutine object, NOT 42

# FIXED — two correct ways:
result = asyncio.run(get_answer())   # ← from sync context
print(result)   # 42

# Or inside another coroutine:
async def main():
    result = await get_answer()      # ← await gets the actual value
    print(result)   # 42
```

**Why:** `async def` functions return a coroutine object when called. The coroutine only executes when it is awaited or driven by an event loop. Python will also emit a `RuntimeWarning: coroutine 'get_answer' was never awaited`.
</details>

---

## Ch2 — Why AI Apps Need Async

<a id="q3"></a>

### Q3 · Why AI needs async — sync vs async LLM timing 🟢

> 🛠️ **Solve locally:** [practice_local.py → Q3](./practice_local.py)


You have 5 LLM prompts. Each call takes 0.5 seconds. Show the timing difference between calling them sequentially vs concurrently using `asyncio.sleep(0.5)` as a stand-in for the LLM call. Print elapsed time for both approaches.


<details>
<summary>💡 Hint</summary>
Use `time.perf_counter()` before and after each approach. Sequential uses a plain `for` loop with `await`. Concurrent uses `asyncio.gather()`.
</details>

<details>
<summary>✅ Answer</summary>

```python
import asyncio, time

async def mock_llm(prompt):
    await asyncio.sleep(0.5)      # ← stands in for a real LLM call
    return f"reply to: {prompt}"

async def sequential(prompts):
    results = []
    for p in prompts:
        results.append(await mock_llm(p))   # ← one at a time
    return results

async def concurrent(prompts):
    return await asyncio.gather(*[mock_llm(p) for p in prompts])

prompts = ["q1", "q2", "q3", "q4", "q5"]

t = time.perf_counter()
asyncio.run(sequential(prompts))
print(f"Sequential: {time.perf_counter() - t:.2f}s")  # ~2.5s

t = time.perf_counter()
asyncio.run(concurrent(prompts))
print(f"Concurrent: {time.perf_counter() - t:.2f}s")  # ~0.5s
```

**Why:** Sequential awaits each call to finish before starting the next. Concurrent sends all 5 at once — they all "wait" at the same time, so total time equals one call, not five.
</details>

---

<a id="q4"></a>

### Q4 · Why AI needs async — blocking vs non-blocking 🟢

> 🛠️ **Solve locally:** [practice_local.py → Q4](./practice_local.py)


This function has a bug that will freeze every other user in a FastAPI server. Identify it and fix it.

```python
import time

async def slow_handler():
    time.sleep(3)   # simulating a "wait"
    return "done"
```


<details>
<summary>💡 Hint</summary>
`time.sleep()` is synchronous. It blocks the OS thread, which means the event loop cannot run any other coroutines. Replace it with the async equivalent.
</details>

<details>
<summary>✅ Answer</summary>

```python
import asyncio

# BAD — blocks the entire event loop for 3 seconds:
async def slow_handler_bad():
    import time
    time.sleep(3)         # ← freezes all other coroutines while sleeping
    return "done"

# GOOD — yields to the event loop while waiting:
async def slow_handler_good():
    await asyncio.sleep(3)   # ← event loop runs other tasks during this 3s
    return "done"

# If you MUST call a blocking library, use to_thread:
async def slow_handler_blocking_lib():
    import time
    result = await asyncio.to_thread(time.sleep, 3)  # ← runs in thread pool
    return "done"
```

**Why:** `time.sleep()` pauses the OS thread itself. The event loop lives on that thread, so all 100 concurrent users freeze. `await asyncio.sleep()` suspends only this coroutine and lets the event loop serve others.
</details>

---

## Ch3 — Streaming LLM Responses

<a id="q5"></a>

### Q5 · Streaming LLM — async generator with yield 🟢

> 🛠️ **Solve locally:** [practice_local.py → Q5](./practice_local.py)


Write an async generator `word_stream(sentence)` that splits a sentence into words and yields each word with a 0.1s delay between them (simulating token-by-token LLM output).


<details>
<summary>💡 Hint</summary>
Use `async def` with `yield` inside. Add `await asyncio.sleep(0.1)` before each yield.
</details>

<details>
<summary>✅ Answer</summary>

```python
import asyncio

async def word_stream(sentence):
    words = sentence.split()
    for word in words:
        await asyncio.sleep(0.1)   # ← simulate network delay per token
        yield word                 # ← send this word NOW, don't wait for rest

async def main():
    async for word in word_stream("Hello async world how are you"):
        print(word, end=" ", flush=True)
    print()

asyncio.run(main())
# prints: Hello async world how are you  (with small pauses between)
```

**Why:** The `yield` inside an `async def` makes this an async generator. Unlike a regular generator, it can `await` between yields — meaning each token can involve real async I/O (like waiting for a network packet from the LLM).
</details>

---

<a id="q6"></a>

### Q6 · Streaming LLM — async for loop consumption 🟢

> 🛠️ **Solve locally:** [practice_local.py → Q6](./practice_local.py)


You have an async generator `token_stream()`. Show the difference between consuming it with `for` vs `async for`, and explain why one is wrong.


<details>
<summary>💡 Hint</summary>
Regular `for` calls `__next__()` synchronously. Async generators implement `__anext__()` which must be awaited. Try the wrong way to see the error.
</details>

<details>
<summary>✅ Answer</summary>

```python
import asyncio

async def token_stream():
    for word in ["Hello", "async", "world"]:
        await asyncio.sleep(0.05)
        yield word

async def main():
    # WRONG — TypeError: 'async_generator' object is not iterable
    # for token in token_stream():
    #     print(token)

    # CORRECT — async for calls __anext__() which can await:
    async for token in token_stream():   # ← yields to event loop between tokens
        print(token, end=" ", flush=True)

asyncio.run(main())
```

**Why:** Regular `for` calls `__next__()` which is synchronous. An async generator's `__anext__()` is a coroutine that must be awaited. `async for` does this automatically. Using regular `for` raises `TypeError`.
</details>

---

<a id="q7"></a>

### Q7 · Streaming LLM — collect stream into string 🟡

> 🛠️ **Solve locally:** [practice_local.py → Q7](./practice_local.py)


Write a function `stream_and_collect(sentence)` that: (1) streams tokens from `word_stream()` printing each one as it arrives, AND (2) returns the full assembled string at the end. Show both side effects happening together.


<details>
<summary>💡 Hint</summary>
Use a list to accumulate tokens inside the `async for` loop, then `"".join()` at the end. Print each token inside the loop before appending.
</details>

<details>
<summary>✅ Answer</summary>

```python
import asyncio

async def word_stream(sentence):
    for word in sentence.split():
        await asyncio.sleep(0.05)
        yield word + " "

async def stream_and_collect(sentence):
    parts = []
    async for token in word_stream(sentence):
        print(token, end="", flush=True)  # ← display as it arrives
        parts.append(token)               # ← collect for later use
    print()
    return "".join(parts)                 # ← return full text

async def main():
    full = await stream_and_collect("The quick brown fox")
    print(f"Full response: '{full.strip()}'")

asyncio.run(main())
```

**Why:** Streaming and collecting are not mutually exclusive. In production you stream tokens to the user's browser AND log the full response to a database — both happen in the same loop.
</details>

---

## Ch4 — Making Parallel LLM Calls

<a id="q8"></a>

### Q8 · Parallel LLM calls — asyncio.gather for 3 prompts 🟢

> 🛠️ **Solve locally:** [practice_local.py → Q8](./practice_local.py)


Use `asyncio.gather` to call a mock LLM with 3 different prompts at the same time. The mock LLM is `async def mock_llm(prompt): await asyncio.sleep(0.5); return f"reply:{prompt}"`. Print all 3 results.


<details>
<summary>💡 Hint</summary>
Pass all 3 coroutine calls directly to `asyncio.gather(...)` as separate arguments. Unpack the returned list.
</details>

<details>
<summary>✅ Answer</summary>

```python
import asyncio

async def mock_llm(prompt):
    await asyncio.sleep(0.5)      # ← all 3 sleep simultaneously
    return f"reply:{prompt}"

async def main():
    r1, r2, r3 = await asyncio.gather(
        mock_llm("What is Python?"),
        mock_llm("What is async?"),
        mock_llm("What is an LLM?"),
    )
    print(r1, r2, r3, sep="\n")

asyncio.run(main())
# All 3 run at the same time — total ~0.5s, not 1.5s
```

**Why:** `asyncio.gather` schedules all coroutines as Tasks on the event loop immediately. While one is awaiting `sleep(0.5)`, the others are too. They all finish at roughly the same time. Results come back in input order.
</details>

---

<a id="q9"></a>

### Q9 · Parallel LLM calls — create_task + await 🟡

> 🛠️ **Solve locally:** [practice_local.py → Q9](./practice_local.py)


Start a long mock LLM call using `asyncio.create_task`. While it runs in the background, print "Doing setup work...". Then collect and print the result.


<details>
<summary>💡 Hint</summary>
Call `asyncio.create_task(mock_llm(...))` to get a Task object. Do other work (like `await asyncio.sleep(0)`), then `await task` to get the value.
</details>

<details>
<summary>✅ Answer</summary>

```python
import asyncio

async def mock_llm(prompt):
    await asyncio.sleep(0.5)
    return f"reply:{prompt}"

async def main():
    # Start the LLM call in the background — it's scheduled but not blocking:
    task = asyncio.create_task(mock_llm("Explain transformers"))

    # Event loop runs our task while we do setup:
    await asyncio.sleep(0)        # ← yield once to let task start
    print("Doing setup work...")  # ← runs while LLM call is in-flight

    result = await task           # ← collect result when ready
    print(f"LLM result: {result}")

asyncio.run(main())
```

**Why:** `create_task` schedules the coroutine immediately. The `await asyncio.sleep(0)` yields control so the event loop can run the task. By the time we `await task`, it may already be done or nearly done.
</details>

---

<a id="q10"></a>

### Q10 · Parallel LLM calls — results order guarantee 🟡

> 🛠️ **Solve locally:** [practice_local.py → Q10](./practice_local.py)


Make 3 mock LLM calls where each takes a different time (0.3s, 0.1s, 0.5s respectively). Use `asyncio.gather`. Show that results come back in input order, not completion order.


<details>
<summary>💡 Hint</summary>
Give each mock call a different sleep time. Print the results — they should match the input order even though the 0.1s call finishes first.
</details>

<details>
<summary>✅ Answer</summary>

```python
import asyncio

async def mock_llm(prompt, delay):
    await asyncio.sleep(delay)    # ← different delays
    print(f"  Finished: {prompt} (took {delay}s)")
    return f"reply:{prompt}"

async def main():
    results = await asyncio.gather(
        mock_llm("slow-first",   0.3),   # finishes 2nd
        mock_llm("fast-second",  0.1),   # finishes 1st
        mock_llm("slowest-third",0.5),   # finishes 3rd
    )
    print("\nResults in input order:")
    for r in results:
        print(r)
    # reply:slow-first, reply:fast-second, reply:slowest-third
    # even though fast-second finished first!

asyncio.run(main())
```

**Why:** `asyncio.gather` always returns results in the same order as the inputs, regardless of which task completed first. This is critical for batch processing where you need to match results back to their prompts.
</details>

---

## Ch5 — Parallel Embeddings

<a id="q11"></a>

### Q11 · Parallel embeddings — gather + Semaphore pattern 🟡

> 🛠️ **Solve locally:** [practice_local.py → Q11](./practice_local.py)


You have 20 documents to embed. A mock embed call takes 0.1s. Use `asyncio.gather` with a `Semaphore(5)` to run all 20 but cap at 5 concurrent. Return all results.


<details>
<summary>💡 Hint</summary>
Create the Semaphore once outside the tasks. Write a wrapper function that does `async with semaphore:` around the embed call. Pass the shared semaphore to every task.
</details>

<details>
<summary>✅ Answer</summary>

```python
import asyncio

async def mock_embed(text):
    await asyncio.sleep(0.1)      # ← simulate embed API latency
    return [0.1, 0.2, 0.3]        # ← fake embedding vector

async def embed_with_limit(text, semaphore):
    async with semaphore:         # ← blocks if 5 slots are taken
        return await mock_embed(text)

async def embed_all(documents):
    semaphore = asyncio.Semaphore(5)   # ← ONE shared semaphore
    tasks = [embed_with_limit(doc, semaphore) for doc in documents]
    return await asyncio.gather(*tasks)

docs = [f"doc {i}" for i in range(20)]
results = asyncio.run(embed_all(docs))
print(f"Embedded {len(results)} docs")   # 20
```

**Why:** Without the Semaphore, all 20 requests fire instantly and could hit rate limits. With `Semaphore(5)`, only 5 are active at any time. As soon as one finishes, the next waiting task grabs the slot.
</details>

---

<a id="q12"></a>

### Q12 · Parallel embeddings — limit N concurrent with Semaphore 🟡

> 🛠️ **Solve locally:** [practice_local.py → Q12](./practice_local.py)


Explain what happens if you create the Semaphore inside the embed function instead of outside. Write code that demonstrates both the broken and correct approach.


<details>
<summary>💡 Hint</summary>
If each task creates its own Semaphore, each one starts with a full counter. There is no shared state. All tasks run without any limiting.
</details>

<details>
<summary>✅ Answer</summary>

```python
import asyncio

async def mock_embed(text):
    await asyncio.sleep(0.05)
    return [0.1]

# BROKEN — new Semaphore each call, no shared state, no limiting:
async def embed_broken(text):
    sem = asyncio.Semaphore(5)    # ← counter starts at 5 every time
    async with sem:               # ← immediately acquires, no contention
        return await mock_embed(text)

# CORRECT — one shared Semaphore, real limiting:
async def embed_correct(text, sem):
    async with sem:               # ← waits if 5 are already running
        return await mock_embed(text)

async def main():
    docs = [f"doc {i}" for i in range(20)]

    # Broken: all 20 run simultaneously (Semaphore has no effect):
    tasks_broken = [embed_broken(d) for d in docs]
    await asyncio.gather(*tasks_broken)   # 20 concurrent — no limit!

    # Correct: at most 5 at a time:
    sem = asyncio.Semaphore(5)
    tasks_correct = [embed_correct(d, sem) for d in docs]
    await asyncio.gather(*tasks_correct)  # max 5 concurrent

asyncio.run(main())
```

**Why:** A Semaphore only limits concurrency if it is shared across all tasks. Creating a new one per task means each task has its own private counter starting at full — no coordination happens.
</details>

---

<a id="q13"></a>

### Q13 · Parallel embeddings — chunked batching with progress 🟠

> 🛠️ **Solve locally:** [practice_local.py → Q13](./practice_local.py)


Write `embed_in_batches(texts, batch_size=5, max_concurrent=3)` that processes texts in batches of 5, with at most 3 concurrent per batch. Print progress after each batch. Use `return_exceptions=True` to handle partial failures.


<details>
<summary>💡 Hint</summary>
Use `range(0, len(texts), batch_size)` to slice into batches. For each batch, create tasks with the shared semaphore and `await asyncio.gather(*tasks, return_exceptions=True)`.
</details>

<details>
<summary>✅ Answer</summary>

```python
import asyncio

async def mock_embed(text):
    await asyncio.sleep(0.05)
    return [0.1, 0.2]

async def embed_one(text, sem):
    async with sem:
        return await mock_embed(text)

async def embed_in_batches(texts, batch_size=5, max_concurrent=3):
    sem = asyncio.Semaphore(max_concurrent)
    all_results = []

    for i in range(0, len(texts), batch_size):
        batch = texts[i : i + batch_size]        # ← slice this batch
        tasks = [embed_one(t, sem) for t in batch]
        batch_results = await asyncio.gather(*tasks, return_exceptions=True)

        for j, result in enumerate(batch_results):
            if isinstance(result, Exception):
                print(f"  Failed: text {i+j}")
                all_results.append(None)
            else:
                all_results.append(result)

        done = min(i + batch_size, len(texts))
        print(f"Progress: {done}/{len(texts)}")  # ← progress after each batch

    return all_results

texts = [f"text {i}" for i in range(17)]
results = asyncio.run(embed_in_batches(texts))
print(f"Total embedded: {sum(1 for r in results if r)}")
```

**Why:** Chunked batching gives you progress reporting and lets you checkpoint between batches. The Semaphore still limits concurrency within each batch. `return_exceptions=True` means one bad embed does not cancel the rest.
</details>

---

## Ch6 — Semaphores for Rate Limiting

<a id="q14"></a>

### Q14 · Semaphore rate limiting — asyncio.Semaphore(N) basics 🟢

> 🛠️ **Solve locally:** [practice_local.py → Q14](./practice_local.py)


Show how `asyncio.Semaphore` works like a bouncer at a club: only N tasks inside at once. Write a demo where 10 tasks try to enter but only 3 are allowed simultaneously. Print when each task enters and exits.


<details>
<summary>💡 Hint</summary>
Create `asyncio.Semaphore(3)`. Inside each task, print "entering" before the `async with` block and "exiting" after it. Use `asyncio.gather` to run all 10 at once.
</details>

<details>
<summary>✅ Answer</summary>

```python
import asyncio

async def task(task_id, semaphore):
    async with semaphore:             # ← blocks if 3 are already inside
        print(f"Task {task_id}: ENTER")
        await asyncio.sleep(0.2)      # ← simulate work
        print(f"Task {task_id}: EXIT")

async def main():
    sem = asyncio.Semaphore(3)        # ← only 3 inside at a time
    tasks = [task(i, sem) for i in range(10)]
    await asyncio.gather(*tasks)
    # You'll see at most 3 "ENTER" lines before any "EXIT" appears

asyncio.run(main())
```

**Why:** The Semaphore internal counter starts at 3. Each `async with` decrements it. When it hits 0, the next task blocks at the `async with` line until another task's `async with` block exits and increments the counter back.
</details>

---

<a id="q15"></a>

### Q15 · Semaphore rate limiting — bounded concurrency wrapper 🟡

> 🛠️ **Solve locally:** [practice_local.py → Q15](./practice_local.py)


Write a reusable function `run_with_limit(coros, limit)` that takes any list of coroutines and runs them with at most `limit` concurrent. It should work for any type of coroutine, not just LLM calls.


<details>
<summary>💡 Hint</summary>
The wrapper needs to accept a list of already-created coroutines. Wrap each one in a helper that acquires the semaphore, then uses `asyncio.gather`.
</details>

<details>
<summary>✅ Answer</summary>

```python
import asyncio

async def run_with_limit(coros, limit):
    """Run any list of coroutines with at most `limit` concurrent."""
    sem = asyncio.Semaphore(limit)

    async def wrap(coro):
        async with sem:           # ← each coroutine waits its turn
            return await coro

    return await asyncio.gather(*[wrap(c) for c in coros])

# Test it with different coroutines:
async def task(n):
    await asyncio.sleep(0.1)
    return n * 2

async def main():
    coros = [task(i) for i in range(10)]
    results = await run_with_limit(coros, limit=3)
    print(results)   # [0, 2, 4, 6, 8, 10, 12, 14, 16, 18]

asyncio.run(main())
```

**Why:** This pattern is useful whenever you have batch work of any kind — embedding, summarizing, fetching URLs — and want to add rate limiting without modifying each individual function.
</details>

---

<a id="q16"></a>

### Q16 · Semaphore rate limiting — Semaphore vs sleep-based throttle 🟡

> 🛠️ **Solve locally:** [practice_local.py → Q16](./practice_local.py)


Compare two approaches to rate limiting: (A) `asyncio.Semaphore(N)` and (B) adding `await asyncio.sleep(0.1)` between calls. Explain why Semaphore is better for burst workloads.


<details>
<summary>💡 Hint</summary>
Sleep-based throttle adds a fixed delay per item, no matter how fast the API is. Semaphore lets fast calls complete quickly and only waits when the concurrency cap is hit.
</details>

<details>
<summary>✅ Answer</summary>

```python
import asyncio, time

async def mock_api(item):
    await asyncio.sleep(0.05)    # fast API response
    return item

# Approach A — Semaphore: max N concurrent, fast when slots free:
async def with_semaphore(items, limit=3):
    sem = asyncio.Semaphore(limit)
    async def call(item):
        async with sem:
            return await mock_api(item)
    return await asyncio.gather(*[call(i) for i in items])

# Approach B — Sleep throttle: always waits, even when API is fast:
async def with_sleep(items, gap=0.1):
    results = []
    for item in items:
        await asyncio.sleep(gap)  # ← always waits even if API responds in 5ms
        results.append(await mock_api(item))
    return results

items = list(range(10))

t = time.perf_counter()
asyncio.run(with_semaphore(items, limit=3))
print(f"Semaphore: {time.perf_counter()-t:.2f}s")   # ~0.2s

t = time.perf_counter()
asyncio.run(with_sleep(items, gap=0.1))
print(f"Sleep:     {time.perf_counter()-t:.2f}s")   # ~1.0s (10 × 0.1s forced waits)
```

**Why:** Semaphore allows maximum throughput up to the concurrency cap. If your API responds in 5ms, Semaphore processes the next item immediately. Sleep adds a fixed artificial delay regardless of actual API speed.
</details>

---

## Ch7 — Async Context Managers

<a id="q17"></a>

### Q17 · Async context managers — async with for HTTP session 🟡

> 🛠️ **Solve locally:** [practice_local.py → Q17](./practice_local.py)


Show how to use `httpx.AsyncClient` as an async context manager to make two GET requests. Explain why you should reuse one client for multiple requests instead of creating a new one each time.


<details>
<summary>💡 Hint</summary>
Wrap both requests inside a single `async with httpx.AsyncClient() as client:` block. The client keeps a connection pool open for both requests.
</details>

<details>
<summary>✅ Answer</summary>

```python
import asyncio
import httpx

async def fetch_two():
    # ONE client handles both requests — connection pool reused:
    async with httpx.AsyncClient() as client:    # ← __aenter__ awaited: sets up pool
        r1 = await client.get("https://httpbin.org/get")
        r2 = await client.get("https://httpbin.org/uuid")
        return r1.json(), r2.json()
    # __aexit__ awaited: all connections closed cleanly

# BAD pattern — new client per call (no connection reuse):
async def fetch_bad(url):
    async with httpx.AsyncClient() as client:    # creates new pool each time
        return await client.get(url)

asyncio.run(fetch_two())
```

**Why:** Opening an HTTP connection involves a TCP handshake (and TLS negotiation for HTTPS). Reusing one client reuses those connections via a pool, saving ~100ms per request. `async with` ensures the pool is closed properly even if an exception occurs.
</details>

---

<a id="q18"></a>

### Q18 · Async context managers — custom AsyncContextManager class 🟠

> 🛠️ **Solve locally:** [practice_local.py → Q18](./practice_local.py)


Write a class `ManagedSession` that acts as an async context manager. On enter: print "Session started" and create a mock client. On exit: print "Session ended". Use `__aenter__` and `__aexit__`.


<details>
<summary>💡 Hint</summary>
Define `async def __aenter__(self)` returning the client, and `async def __aexit__(self, exc_type, exc_val, exc_tb)` for cleanup. The `async with` statement will await both.
</details>

<details>
<summary>✅ Answer</summary>

```python
import asyncio

class MockClient:
    async def call(self, prompt):
        await asyncio.sleep(0.1)
        return f"response:{prompt}"

class ManagedSession:
    async def __aenter__(self):
        print("Session started")          # ← async setup (could await here)
        self.client = MockClient()
        return self.client                # ← yielded to the `as` variable

    async def __aexit__(self, exc_type, exc_val, exc_tb):
        print("Session ended")            # ← async teardown (could await here)
        # Return False to let exceptions propagate (return True to suppress)
        return False

async def main():
    async with ManagedSession() as client:   # ← __aenter__ awaited
        result = await client.call("hello")
        print(result)
    # ← __aexit__ awaited automatically, even if an exception occurred

asyncio.run(main())
```

**Why:** `__aenter__` and `__aexit__` are coroutines, so they can `await` async operations like opening a database connection or authenticating an API client. Regular context managers cannot do this.
</details>

---

## Ch8 — Async Queues

<a id="q19"></a>

### Q19 · Async queues — basic producer/consumer with asyncio.Queue 🟡

> 🛠️ **Solve locally:** [practice_local.py → Q19](./practice_local.py)


Write a producer that puts 5 items into an `asyncio.Queue`, and a consumer that takes and prints them. Run both concurrently with `asyncio.gather`. Use `None` as a sentinel to signal done.


<details>
<summary>💡 Hint</summary>
Producer: `await queue.put(item)` for each item, then `await queue.put(None)`. Consumer: loop with `item = await queue.get()`, break on `None`, call `queue.task_done()` always.
</details>

<details>
<summary>✅ Answer</summary>

```python
import asyncio

async def producer(queue):
    for i in range(5):
        await asyncio.sleep(0.1)         # ← simulate reading from disk
        await queue.put(f"doc_{i}")
        print(f"Produced: doc_{i}")
    await queue.put(None)                # ← sentinel: "I'm done"

async def consumer(queue):
    while True:
        item = await queue.get()         # ← blocks until item available
        if item is None:
            queue.task_done()
            print("Consumer: done")
            break
        print(f"Consumed: {item}")
        await asyncio.sleep(0.05)        # ← simulate processing
        queue.task_done()                # ← always mark done

async def main():
    queue = asyncio.Queue()
    await asyncio.gather(producer(queue), consumer(queue))
    await queue.join()                   # ← wait for all items to be processed

asyncio.run(main())
```

**Why:** The queue decouples the producer (reading speed) from the consumer (processing speed). If consuming is slower, items buffer in the queue. If producing is slower, the consumer just waits. Neither blocks the other.
</details>

---

<a id="q20"></a>

### Q20 · Async queues — multiple consumers for higher throughput 🟡

> 🛠️ **Solve locally:** [practice_local.py → Q20](./practice_local.py)


Extend the producer/consumer pattern to use 3 consumers processing from the same queue. The producer should send one sentinel (`None`) per consumer so they all know when to stop.


<details>
<summary>💡 Hint</summary>
After the producer finishes all real items, put `None` into the queue `num_consumers` times. Each consumer sees exactly one `None` and stops. Use `asyncio.create_task` for each consumer.
</details>

<details>
<summary>✅ Answer</summary>

```python
import asyncio

async def producer(queue, items, num_consumers):
    for item in items:
        await queue.put(item)
    for _ in range(num_consumers):       # ← one sentinel per consumer
        await queue.put(None)

async def consumer(queue, consumer_id):
    count = 0
    while True:
        item = await queue.get()
        if item is None:
            queue.task_done()
            print(f"Consumer {consumer_id}: processed {count} items")
            break
        await asyncio.sleep(0.05)        # ← simulate work
        count += 1
        queue.task_done()

async def main():
    queue = asyncio.Queue(maxsize=10)
    items = [f"doc_{i}" for i in range(15)]
    num_consumers = 3

    consumer_tasks = [
        asyncio.create_task(consumer(queue, i))
        for i in range(num_consumers)
    ]
    await producer(queue, items, num_consumers)
    await asyncio.gather(*consumer_tasks)

asyncio.run(main())
```

**Why:** Multiple consumers increase throughput — if processing one item takes 0.05s, 3 consumers can handle 3 items simultaneously. Each consumer gets exactly one `None` sentinel, so all three stop cleanly.
</details>

---

<a id="q21"></a>

### Q21 · Async queues — backpressure with maxsize 🟠

> 🛠️ **Solve locally:** [practice_local.py → Q21](./practice_local.py)


What is backpressure in a queue and why does it matter? Show how `asyncio.Queue(maxsize=3)` creates backpressure: a fast producer that tries to put 10 items quickly but is slowed down when the queue fills up.


<details>
<summary>💡 Hint</summary>
With `maxsize=3`, `queue.put()` will block (await) when the queue already has 3 items. The producer can only continue when the consumer takes something out.
</details>

<details>
<summary>✅ Answer</summary>

```python
import asyncio, time

async def fast_producer(queue):
    for i in range(10):
        t = time.perf_counter()
        await queue.put(f"item_{i}")    # ← BLOCKS when queue is full (maxsize=3)
        waited = time.perf_counter() - t
        if waited > 0.01:
            print(f"  Producer waited {waited:.2f}s to put item_{i} (queue full)")

async def slow_consumer(queue):
    while True:
        item = await queue.get()
        if item is None:
            queue.task_done()
            break
        await asyncio.sleep(0.2)        # ← slow processing
        print(f"  Consumed: {item}")
        queue.task_done()

async def main():
    queue = asyncio.Queue(maxsize=3)    # ← only 3 items buffered at once
    await asyncio.gather(
        fast_producer(queue),
        slow_consumer(queue),
    )

asyncio.run(main())
```

**Why:** Backpressure prevents unbounded memory growth. Without `maxsize`, a fast producer and slow consumer would pile millions of items in memory. With `maxsize=3`, the producer automatically slows to match the consumer's pace.
</details>

---

## Ch9 — Error Handling in Async

<a id="q22"></a>

### Q22 · Error handling — try/except in a coroutine 🟢

> 🛠️ **Solve locally:** [practice_local.py → Q22](./practice_local.py)


Write `safe_call(prompt)` that calls a mock LLM. If a `ValueError` is raised (mock it with a 30% chance), catch it and return `None`. Otherwise return the result. Show it working in a batch.


<details>
<summary>💡 Hint</summary>
`try/except` works exactly the same inside `async def` as in regular functions. Use `random.random() < 0.3` to simulate occasional failures.
</details>

<details>
<summary>✅ Answer</summary>

```python
import asyncio, random

async def mock_llm(prompt):
    await asyncio.sleep(0.05)
    if random.random() < 0.3:            # ← 30% failure rate
        raise ValueError(f"Mock error for: {prompt}")
    return f"reply:{prompt}"

async def safe_call(prompt):
    try:
        return await mock_llm(prompt)
    except ValueError as e:
        print(f"  Caught error: {e}")
        return None                       # ← graceful fallback

async def main():
    prompts = [f"q{i}" for i in range(8)]
    results = [await safe_call(p) for p in prompts]
    good = [r for r in results if r is not None]
    print(f"Succeeded: {len(good)}/{len(prompts)}")

asyncio.run(main())
```

**Why:** `try/except` inside an `async def` function works identically to sync code. The coroutine catches its own exceptions without affecting other coroutines running concurrently.
</details>

---

<a id="q23"></a>

### Q23 · Error handling — gather(return_exceptions=True) 🟡

> 🛠️ **Solve locally:** [practice_local.py → Q23](./practice_local.py)


Run 5 mock LLM calls with `asyncio.gather`. Two of them will raise exceptions. Show the difference between the default behavior (exception propagates) vs `return_exceptions=True` (exceptions are values). Separate successes from failures.


<details>
<summary>💡 Hint</summary>
First try without `return_exceptions=True` — the first exception cancels everything. Then add it and use `isinstance(result, Exception)` to filter results.
</details>

<details>
<summary>✅ Answer</summary>

```python
import asyncio

async def mock_llm(prompt, should_fail=False):
    await asyncio.sleep(0.05)
    if should_fail:
        raise RuntimeError(f"LLM failed for: {prompt}")
    return f"reply:{prompt}"

async def main():
    calls = [
        mock_llm("q1"),
        mock_llm("q2", should_fail=True),   # ← will fail
        mock_llm("q3"),
        mock_llm("q4", should_fail=True),   # ← will fail
        mock_llm("q5"),
    ]

    # Without return_exceptions — first failure stops everything:
    try:
        results = await asyncio.gather(*calls)
    except RuntimeError as e:
        print(f"Batch aborted: {e}")  # q3, q4, q5 never finish

    # Recreate coroutines (they were consumed above):
    calls = [
        mock_llm("q1"), mock_llm("q2", should_fail=True),
        mock_llm("q3"), mock_llm("q4", should_fail=True), mock_llm("q5"),
    ]
    # With return_exceptions — all 5 run, exceptions are returned as values:
    results = await asyncio.gather(*calls, return_exceptions=True)
    for i, r in enumerate(results):
        if isinstance(r, Exception):
            print(f"  q{i+1} FAILED: {r}")
        else:
            print(f"  q{i+1} OK: {r}")

asyncio.run(main())
```

**Why:** `return_exceptions=True` is essential for batch processing. Without it, one rate-limited request cancels your entire 10,000-document embedding run. With it, you process everything and log failures separately.
</details>

---

## Ch10 — Running Async from Sync Code

<a id="q24"></a>

### Q24 · Async from sync — asyncio.run() entry point 🟢

> 🛠️ **Solve locally:** [practice_local.py → Q24](./practice_local.py)


Show three scenarios for `asyncio.run()`: (1) correct use at script entry point, (2) wrong use inside another coroutine (explain the error), (3) correct fix for case 2.


<details>
<summary>💡 Hint</summary>
`asyncio.run()` creates a new event loop. You cannot call it when an event loop is already running. Inside a coroutine, just `await` instead.
</details>

<details>
<summary>✅ Answer</summary>

```python
import asyncio

async def inner():
    await asyncio.sleep(0.1)
    return "done"

# CASE 1 — Correct: top-level entry point:
# asyncio.run(inner())    # ← creates loop, runs, closes it

# CASE 2 — Wrong: calling asyncio.run inside a running loop:
async def outer_bad():
    result = asyncio.run(inner())   # RuntimeError: event loop already running
    return result

# CASE 3 — Correct: just await inside a coroutine:
async def outer_good():
    result = await inner()          # ← correct — no new loop needed
    return result

# Script entry point:
if __name__ == "__main__":
    result = asyncio.run(outer_good())   # ← only asyncio.run at the top level
    print(result)
```

**Why:** `asyncio.run()` creates a new event loop and blocks the calling thread until it finishes. Calling it inside a coroutine means there is already a running loop — nesting loops is not allowed. Use `await` inside coroutines; use `asyncio.run()` only at the boundary between sync and async.
</details>

---

<a id="q25"></a>

### Q25 · Async from sync — asyncio.to_thread() for blocking calls 🟡

> 🛠️ **Solve locally:** [practice_local.py → Q25](./practice_local.py)


You have a legacy sync function `load_large_file(path)` that takes 2 seconds. Show how to call it from async code without blocking the event loop using `asyncio.to_thread()`.


<details>
<summary>💡 Hint</summary>
`asyncio.to_thread(func, *args)` runs `func` in a thread pool and returns a coroutine you can `await`. The event loop stays free while the thread runs.
</details>

<details>
<summary>✅ Answer</summary>

```python
import asyncio, time

# Legacy blocking function — cannot be made async:
def load_large_file(path):
    time.sleep(0.5)              # ← simulates 2-second disk read
    return f"contents of {path}"

# BAD — blocks event loop for 2 seconds:
async def process_bad(path):
    content = load_large_file(path)  # ← freezes all other coroutines!
    return content

# GOOD — runs blocking function in thread pool, event loop stays free:
async def process_good(path):
    content = await asyncio.to_thread(load_large_file, path)  # ← non-blocking
    return content

async def main():
    # Both file loads happen "simultaneously" (each in its own thread):
    r1, r2 = await asyncio.gather(
        process_good("file1.txt"),
        process_good("file2.txt"),
    )
    print(r1, r2)

asyncio.run(main())
```

**Why:** `asyncio.to_thread` submits the blocking function to `asyncio`'s default thread pool executor. The event loop awaits a future that resolves when the thread finishes. Other coroutines run freely while the thread is doing blocking I/O.
</details>

---

## Ch11 — Async in FastAPI

<a id="q26"></a>

### Q26 · FastAPI AI endpoint — async def route 🟡

> 🛠️ **Solve locally:** [practice_local.py → Q26](./practice_local.py)


Write a minimal FastAPI app with an async `POST /chat` endpoint that accepts a `prompt` string and returns a `{"reply": "..."}` dict. Use a mock async LLM. Explain why `async def` matters here vs a sync `def`.


<details>
<summary>💡 Hint</summary>
Import `FastAPI` and create `app = FastAPI()`. Decorate with `@app.post("/chat")` and make the function `async def`. FastAPI awaits it automatically.
</details>

<details>
<summary>✅ Answer</summary>

```python
import asyncio
from fastapi import FastAPI

app = FastAPI()

async def mock_llm(prompt: str) -> str:
    await asyncio.sleep(0.3)         # ← simulates real LLM call
    return f"Answer to: {prompt}"

@app.post("/chat")
async def chat_endpoint(prompt: str) -> dict:
    # FastAPI schedules this as a coroutine automatically:
    reply = await mock_llm(prompt)   # ← while awaiting, event loop handles others
    return {"reply": reply}

# 100 users hit /chat simultaneously:
# FastAPI runs 100 coroutines — all 100 LLM calls in-flight at once
# Total time: ~0.3s (one LLM call), not 30s (100 × 0.3s sequential)

# Run with: uvicorn module:app --reload
# Test with: curl -X POST "http://localhost:8000/chat?prompt=hello"
```

**Why:** With `async def`, FastAPI runs your handler as a coroutine. While one user's LLM call awaits the API response, the event loop handles the next user's request. With a sync `def`, FastAPI runs it in a thread pool — which still works but uses more memory per concurrent request.
</details>

---

<a id="q27"></a>

### Q27 · FastAPI AI endpoint — streaming response with SSE 🟠

> 🛠️ **Solve locally:** [practice_local.py → Q27](./practice_local.py)


Write a FastAPI `POST /stream` endpoint that returns tokens as Server-Sent Events. Use an async generator to yield tokens and wrap it in `StreamingResponse`.


<details>
<summary>💡 Hint</summary>
The async generator should yield strings in SSE format: `f"data: {token}\n\n"`. Pass it to `StreamingResponse(..., media_type="text/event-stream")`. Add a final `yield "data: [DONE]\n\n"`.
</details>

<details>
<summary>✅ Answer</summary>

```python
import asyncio
from fastapi import FastAPI
from fastapi.responses import StreamingResponse

app = FastAPI()

async def token_generator(prompt: str):
    """Async generator that yields tokens in SSE format."""
    words = f"Here is my response to: {prompt}".split()
    for word in words:
        await asyncio.sleep(0.1)              # ← simulate token arrival
        yield f"data: {word}\n\n"             # ← SSE format: data: <content>\n\n
    yield "data: [DONE]\n\n"                  # ← signals end of stream

@app.post("/stream")
async def stream_endpoint(prompt: str):
    return StreamingResponse(
        token_generator(prompt),
        media_type="text/event-stream",       # ← tells browser to treat as SSE
        headers={"Cache-Control": "no-cache"} # ← no buffering
    )

# Client receives tokens as they are generated — the ChatGPT UX
# Test: curl -N "http://localhost:8000/stream?prompt=hello+world"
```

**Why:** `StreamingResponse` wraps the async generator and flushes each yielded chunk to the HTTP client immediately. `media_type="text/event-stream"` tells the browser it is SSE — the browser's `EventSource` API can consume this directly.
</details>

---

## Ch12 — Production Patterns

<a id="q28"></a>

### Q28 · Production patterns — retry with exponential backoff 🟠

> 🛠️ **Solve locally:** [practice_local.py → Q28](./practice_local.py)


Write `call_with_backoff(prompt, semaphore, max_retries=5)` that: (1) acquires the semaphore, (2) tries the LLM call, (3) on `RateLimitError` waits `2^attempt + random jitter` seconds and retries, (4) re-raises after max retries.


<details>
<summary>💡 Hint</summary>
Use `async with semaphore:` wrapping a `for attempt in range(max_retries):` loop. Catch the specific error class, calculate delay as `(2 ** attempt) + random.random()`, and `await asyncio.sleep(delay)`.
</details>

<details>
<summary>✅ Answer</summary>

```python
import asyncio, random

class RateLimitError(Exception):
    pass

async def mock_llm(prompt):
    await asyncio.sleep(0.05)
    if random.random() < 0.4:        # ← 40% chance of rate limit
        raise RateLimitError("429 Too Many Requests")
    return f"reply:{prompt}"

async def call_with_backoff(prompt, semaphore, max_retries=5):
    async with semaphore:
        for attempt in range(max_retries):
            try:
                return await mock_llm(prompt)
            except RateLimitError:
                if attempt == max_retries - 1:
                    raise             # ← give up after max_retries
                delay = (2 ** attempt) + random.random()  # ← jitter prevents thundering herd
                print(f"  Rate limited (attempt {attempt+1}), wait {delay:.1f}s")
                await asyncio.sleep(delay)

async def main():
    sem = asyncio.Semaphore(3)
    prompts = [f"q{i}" for i in range(6)]
    tasks = [call_with_backoff(p, sem) for p in prompts]
    results = await asyncio.gather(*tasks, return_exceptions=True)
    print(f"Successes: {sum(1 for r in results if not isinstance(r, Exception))}")

asyncio.run(main())
```

**Why:** Exponential backoff (`2^0=1s, 2^1=2s, 2^2=4s, ...`) avoids hammering an already-overloaded API. Random jitter prevents all retrying clients from hitting at the same moment ("thundering herd"). The Semaphore prevents new requests from starting while others are backing off.
</details>

---

<a id="q29"></a>

### Q29 · Production patterns — asyncio.TaskGroup structured concurrency 🟠

> 🛠️ **Solve locally:** [practice_local.py → Q29](./practice_local.py)


Python 3.11+ introduced `asyncio.TaskGroup` as a safer alternative to `asyncio.gather`. Use it to run 3 mock LLM calls. Show how it differs from `gather` in error handling — specifically that it cancels all sibling tasks when one fails.


<details>
<summary>💡 Hint</summary>
Use `async with asyncio.TaskGroup() as tg:` and call `tg.create_task(coro)` for each task. If any task raises, all others are cancelled and the exception is re-raised as an `ExceptionGroup`.
</details>

<details>
<summary>✅ Answer</summary>

```python
import asyncio

async def mock_llm(prompt, fail=False):
    await asyncio.sleep(0.1)
    if fail:
        raise ValueError(f"LLM failed: {prompt}")
    return f"reply:{prompt}"

async def with_task_group():
    results = []
    try:
        async with asyncio.TaskGroup() as tg:    # ← Python 3.11+
            t1 = tg.create_task(mock_llm("q1"))
            t2 = tg.create_task(mock_llm("q2"))
            t3 = tg.create_task(mock_llm("q3"))
        # All tasks completed successfully — access results:
        results = [t1.result(), t2.result(), t3.result()]
    except* ValueError as eg:                    # ← ExceptionGroup handling
        print(f"Some tasks failed: {eg.exceptions}")

    return results

async def with_failing_task():
    try:
        async with asyncio.TaskGroup() as tg:
            t1 = tg.create_task(mock_llm("q1"))
            t2 = tg.create_task(mock_llm("q2", fail=True))   # ← this fails
            t3 = tg.create_task(mock_llm("q3"))
            # When t2 fails, t1 and t3 are cancelled automatically
    except* ValueError as eg:
        print(f"Caught: {eg.exceptions}")   # t2's ValueError

asyncio.run(with_task_group())
asyncio.run(with_failing_task())
```

**Why:** `TaskGroup` provides "structured concurrency" — all tasks created inside the `async with` block are guaranteed to finish (or be cancelled) before the block exits. No dangling background tasks. `gather` can leave tasks running if you don't properly await them.
</details>

---

<a id="q30"></a>

### Q30 · Production patterns — capstone parallel batch processor 🟠

> 🛠️ **Solve locally:** [practice_local.py → Q30](./practice_local.py)


Build a complete `batch_embed_corpus(documents, max_concurrent=10)` function that combines everything from this module: async, Semaphore, gather with return_exceptions, exponential backoff on failure. Process a list of 20 mock documents and print a summary of successes and failures.


<details>
<summary>💡 Hint</summary>
Start with one shared `Semaphore(max_concurrent)`. Write a helper `embed_one(doc, sem)` with retry logic. Use `asyncio.gather(*tasks, return_exceptions=True)`. At the end, count and print successes/failures.
</details>

<details>
<summary>✅ Answer</summary>

```python
import asyncio, random

async def mock_embed(text):
    await asyncio.sleep(0.05)
    if random.random() < 0.15:        # ← 15% transient failure rate
        raise ConnectionError("Rate limit hit")
    return [round(random.random(), 3) for _ in range(4)]

async def embed_one(doc, sem, max_retries=3):
    async with sem:
        for attempt in range(max_retries):
            try:
                embedding = await mock_embed(doc["content"])
                return {"id": doc["id"], "embedding": embedding}
            except ConnectionError:
                if attempt == max_retries - 1:
                    raise
                delay = (2 ** attempt) + random.random()
                await asyncio.sleep(delay)

async def batch_embed_corpus(documents, max_concurrent=10):
    sem = asyncio.Semaphore(max_concurrent)   # ← shared rate limiter
    tasks = [embed_one(doc, sem) for doc in documents]
    results = await asyncio.gather(*tasks, return_exceptions=True)  # ← resilient

    embedded, failed = [], []
    for doc, result in zip(documents, results):
        if isinstance(result, Exception):
            failed.append(doc["id"])
        else:
            embedded.append(result)

    print(f"Embedded: {len(embedded)}/{len(documents)}")
    if failed:
        print(f"Failed IDs: {failed}")
    return embedded

docs = [{"id": i, "content": f"document text {i}"} for i in range(20)]
asyncio.run(batch_embed_corpus(docs, max_concurrent=5))
```

**Why:** This capstone combines every key pattern: coroutines (`async def`), concurrency (`asyncio.gather`), rate limiting (`Semaphore`), resilience (`return_exceptions=True`), and retry (`exponential backoff`). This exact structure appears in production RAG pipelines and embedding jobs.
</details>

---

## Navigation

| | |
|---|---|
| 📖 Theory | [theory.md](./theory.md) |
| 💻 Practice Local | [practice_local.py](./practice_local.py) |
| ⚡ Cheatsheet | [cheetsheet.md](./cheetsheet.md) |
| 🎯 Interview | [interview.md](./interview.md) |

---

**[Back to README](../README.md)**

**Prev:** [Theory](./theory.md) | **Next:** [Cheat Sheet](./cheetsheet.md)

**Related Topics:** [Theory](./theory.md) · [Cheat Sheet](./cheetsheet.md) · [Interview Q&A](./interview.md)
