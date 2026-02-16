# ⚙️ Concurrency in Python  
From Threads to Async — A Complete Deep Dive

---

# 🎯 Why Concurrency Exists

Imagine:

Your program does:

- File reading
- API calls
- Database queries
- Data processing

If it runs everything one-by-one:

It waits.
And waits.
And waits.

Example:

Download 5 files.
Each takes 2 seconds.

Sequential execution:
10 seconds.

Concurrency allows:

Overlapping waiting time.

This improves responsiveness.

But…

Concurrency is NOT parallelism.
And in Python, that difference matters a lot.

---

# 🧠 1️⃣ Concurrency vs Parallelism

This is very important.

---

## 🔹 Concurrency

Multiple tasks making progress at same time.

Example:

Chef cooking:
While rice is boiling,
chopping vegetables.

Not doing both at exact same CPU cycle,
but overlapping.

---

## 🔹 Parallelism

Multiple tasks executing literally at same time.

Requires:

Multiple CPU cores.

In Python:

Due to GIL,
threads are not truly parallel for CPU tasks.

We will explain that next.

---

# 🧠 2️⃣ The Global Interpreter Lock (GIL)

One of the most important concepts.

Python (CPython implementation) has:

Global Interpreter Lock.

Meaning:

Only ONE thread can execute Python bytecode at a time.

Important:

- Multi-threading does NOT speed up CPU-bound tasks.
- It helps I/O-bound tasks.

---

# 🔥 3️⃣ CPU-Bound vs I/O-Bound Tasks

Understanding this is critical.

---

## 🔹 CPU-Bound

Tasks that use heavy computation.

Example:

- Image processing
- Machine learning
- Complex math
- Encryption

These need CPU time.

Threads do NOT help much due to GIL.

Use multiprocessing.

---

## 🔹 I/O-Bound

Tasks waiting for external operations.

Example:

- API requests
- File reading
- Database queries
- Network calls

Threads are useful here.

Because while one thread waits,
another runs.

---

# 🧵 4️⃣ Multithreading in Python

Python module:

```python
import threading
```

Basic structure:

```python
def task():
    print("Task running")

thread = threading.Thread(target=task)
thread.start()
thread.join()
```

---

## 🔍 Important Methods

---

### thread.start()

Starts new thread.

---

### thread.join()

Waits for thread to finish.

Without join,
main program may exit early.

---

### daemon threads

```python
thread.daemon = True
```

Daemon threads:

Stop automatically when main program exits.

Used for background tasks.

---

# ⚠️ 5️⃣ Race Conditions

Very important concept.

Example:

Two threads updating same variable.

```python
counter += 1
```

This is not atomic.

It involves:

- Read value
- Modify
- Write back

Two threads may interfere.

Result:
Wrong value.

---

# 🔐 6️⃣ Thread Safety — Locks

To prevent race condition:

Use Lock.

```python
lock = threading.Lock()

with lock:
    counter += 1
```

Lock ensures:

Only one thread enters critical section.

---

## 🔍 Lock Methods

---

### lock.acquire()

Acquires lock manually.

---

### lock.release()

Releases lock.

---

Using `with lock:` is safer.

---

# 🧠 7️⃣ Deadlocks

Deadlock happens when:

Thread A waits for lock held by B,
Thread B waits for lock held by A.

System freezes.

Avoid:

- Nested locks
- Inconsistent lock ordering

---

# ⚙️ 8️⃣ Multiprocessing

Since GIL prevents true parallelism,
use multiprocessing for CPU-bound tasks.

```python
import multiprocessing
```

Example:

```python
def task():
    print("Running")

process = multiprocessing.Process(target=task)
process.start()
process.join()
```

Each process:

Has separate memory.
Has separate Python interpreter.
Has separate GIL.

True parallelism.

---

# 🧠 9️⃣ Multiprocessing Communication

Processes do NOT share memory.

Use:

- Queue
- Pipe
- Shared memory
- Manager

Example:

```python
queue = multiprocessing.Queue()
```

For sending data between processes.

---

# ⚡ 1️⃣0️⃣ Async Programming

Now comes modern approach.

Async is different from threads.

Uses:

- Event loop
- Coroutines
- await
- async

---

# 🧠 1️⃣1️⃣ What Is async?

```python
async def task():
    print("Hello")
```

This defines coroutine.

Does not execute immediately.

---

# 🔄 1️⃣2️⃣ What Is await?

await pauses coroutine until task completes.

Example:

```python
await asyncio.sleep(1)
```

Allows other tasks to run.

---

# 🧠 1️⃣3️⃣ Event Loop

Core of async system.

Event loop:

- Manages tasks
- Switches between coroutines
- Handles I/O readiness

Runs until tasks complete.

---

# 🧠 1️⃣4️⃣ asyncio Module

Basic example:

```python
import asyncio

async def task():
    print("Start")
    await asyncio.sleep(1)
    print("End")

asyncio.run(task())
```

---

# ⚡ 1️⃣5️⃣ Async vs Threads

Threads:
- OS-level threads
- Context switching by OS
- GIL limitation

Async:
- Single-threaded
- Cooperative multitasking
- Manual yielding with await
- Very lightweight

Async is best for:

High I/O workloads.

---

# 🧠 1️⃣6️⃣ When to Use What?

---

## Use Threads:

- I/O-bound
- Blocking libraries
- Simple concurrency

---

## Use Multiprocessing:

- CPU-bound
- Heavy computations

---

## Use Async:

- Network services
- Web APIs
- High concurrency
- Lightweight tasks

---

# 🧠 1️⃣7️⃣ ThreadPoolExecutor

From:

```python
from concurrent.futures import ThreadPoolExecutor
```

Allows:

Managing thread pool easily.

Example:

```python
with ThreadPoolExecutor() as executor:
    executor.submit(task)
```

Cleaner than manual thread handling.

---

# 🧠 1️⃣8️⃣ ProcessPoolExecutor

Similar to thread pool.

But for processes.

Used for CPU-heavy tasks.

---

# ⚠️ 1️⃣9️⃣ Common Concurrency Mistakes

❌ Ignoring GIL  
❌ Using threads for CPU-heavy tasks  
❌ Forgetting join()  
❌ Not handling race conditions  
❌ Deadlocks  
❌ Blocking calls inside async code  
❌ Mixing threading and async incorrectly  

---

# 🏗 2️⃣0️⃣ Real Production Use Cases

---

## 🔹 Web Servers (FastAPI)

Use async for handling many requests.

---

## 🔹 Data Processing

Use multiprocessing for parallel computation.

---

## 🔹 Background Tasks

Use thread pool.

---

## 🔹 Streaming Systems

Use async for non-blocking I/O.

---

# 🏆 2️⃣1️⃣ Engineering Maturity Levels

Beginner:
Uses threading blindly.

Intermediate:
Understands GIL and I/O-bound vs CPU-bound.

Advanced:
Chooses right concurrency model.

Senior:
Designs scalable concurrent systems safely.

---

# 🧠 Final Mental Model

Concurrency is about:

Managing multiple tasks safely and efficiently.

Key questions:

- Is task CPU-bound?
- Is task I/O-bound?
- Do I need parallelism?
- Do I need scalability?
- Is shared memory safe?

Concurrency is powerful.
But dangerous if misunderstood.

---

# 🔁 Navigation

Previous:  
[12_context_managers/interview.md](../12_context_managers/interview.md)

Next:  
[13_concurrency/interview.md](./interview.md)

