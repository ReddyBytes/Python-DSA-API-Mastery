<a id="top"></a>

# Computer Fundamentals

> Before you design systems that run on computers, you need to understand what
> computers actually do. This is not a textbook chapter — it is Raju's story of
> discovering how hardware brings code to life.

## Table of Contents

- [1. Learning Priority](#learning-priority)
- [2. The Story Begins — You Click Send](#the-story-begins)
- [3. The CPU — The Brain That Never Stops](#the-cpu)
  - [What It Is](#cpu-what-it-is)
  - [The Restaurant Kitchen Analogy](#cpu-kitchen-analogy)
  - [Why This Matters for System Design](#cpu-system-design)
  - [The CPU Cache — Your Chef's Counter](#cpu-cache)
- [4. RAM — The Workspace](#ram)
  - [What It Is](#ram-what-it-is)
  - [The Whiteboard Analogy](#ram-whiteboard-analogy)
  - [Why This Matters for System Design](#ram-system-design)
- [5. Disk — The Filing Cabinet](#disk)
  - [What It Is](#disk-what-it-is)
  - [The Library Stacks Analogy](#disk-library-analogy)
  - [Sequential vs Random I/O](#disk-sequential-random)
- [6. Processes and Threads — How Code Runs](#processes-threads)
  - [The Process — An Independent Worker](#process-worker)
  - [The Thread — A Worker Within a Worker](#thread-worker)
  - [The Restaurant Staff Analogy](#process-thread-analogy)
  - [Context Switching — The Cost of Multitasking](#context-switching)
- [7. Memory Layout Within a Process](#memory-layout)
  - [The Two Regions Every Process Has](#memory-regions)
  - [The Stack Frame — One per Function Call](#stack-frame)
  - [Scope and Memory Lifetime](#scope-lifetime)
  - [Why Stack Access is Faster Than Heap Access](#stack-vs-heap-speed)
- [8. Latency — The Speed of Everything](#latency)
- [9. I/O — The Waiting Problem](#io)
  - [The Blocking I/O Problem](#blocking-io)
  - [The Solution — Async I/O and Event Loop](#async-io)
- [10. Serialization — Speaking a Common Language](#serialization)
  - [The Problem](#serialization-problem)
  - [Formats Compared](#serialization-formats)
- [11. How This All Comes Together — Following Hey](#full-journey)
- [12. Mental Models to Carry Forward](#mental-models)
- [13. Connection to What Comes Next](#connection-next)
- [14. Practice Exercises](#practice)
- [15. Summary](#summary)

<a id="learning-priority"></a>

# 1. Learning Priority

**Must Learn** — Core concept, daily use, interview essential:
latency hierarchy (CPU cache/RAM/SSD/network) · CPU cores and cache levels · memory layout (stack vs heap)

**Should Learn** — Important for real projects, comes up regularly:
process vs thread · context switching cost · I/O blocking vs async models

**Good to Know** — Useful in specific situations, not always tested:
serialization format trade-offs · L1/L2/L3 cache behavior

**Reference** — Know it exists, look up syntax when needed:
specific nanosecond/microsecond latency numbers · NUMA architecture

[Back to Top](#top)

<a id="the-story-begins"></a>

# 2. The Story Begins — You Click Send

Raju is sitting in his hostel room in Hyderabad, chatting with his friend on WhatsApp. He types "Hey!" and taps Send.

In the next **200 milliseconds** — faster than he can blink — that message travels from his thumb, through layers of hardware, across the internet, and arrives on his friend's phone in Vizag.

"How does this actually happen?" Raju wonders. "My professor says it is all just zeros and ones, but what does that really mean?"

Let us follow that journey from the very beginning — and by the end, Raju (and you) will understand every layer a computer uses to bring code to life.

[Back to Top](#top)

<a id="the-cpu"></a>

# 3. The CPU — The Brain That Never Stops

<a id="cpu-what-it-is"></a>

## What It Is

Raju's first computer science lecture began with the professor writing on the board: "CPU = Central Processing Unit. It executes code."

But what does "execute code" actually mean? When Raju writes:

```python
result = 2 + 2
```

...the CPU is what physically adds those numbers together using transistors. Billions of tiny switches, flipping on and off, billions of times per second. Every line of Python Raju writes eventually becomes instructions that these transistors carry out.

<a id="cpu-kitchen-analogy"></a>

## The Restaurant Kitchen Analogy

Raju's uncle runs a restaurant in Vijayawada. Watching the kitchen one summer helped Raju understand CPUs better than any textbook.

Think of the CPU as a **head chef** in a restaurant kitchen.

```
+-------------------------------------------------------------+
|                    Restaurant Kitchen                        |
|                                                             |
|  Head Chef (CPU Core)  <- Takes one order at a time         |
|  +------------------+                                       |
|  |  Chef's Counter  |  <- CPU Cache (ingredients right here)|
|  |  (Super fast)    |                                       |
|  +--------+---------+                                       |
|           |  needs ingredient                               |
|  +--------v---------+                                       |
|  |   Walk-in Fridge |  <- RAM (a bit farther, still fast)   |
|  |   (Fast access)  |                                       |
|  +--------+---------+                                       |
|           |  not in fridge                                  |
|  +--------v---------+                                       |
|  |   Storage Room   |  <- Disk (slow, far away)             |
|  |   (Slow access)  |                                       |
|  +------------------+                                       |
+-------------------------------------------------------------+
```

The chef can only work on ONE dish at a time per hand (core). But a modern CPU has **multiple cores** — imagine 8 chefs working simultaneously. Raju's uncle eventually hired more cooks — that is exactly what multi-core processors do.

<a id="cpu-system-design"></a>

## Why This Matters for System Design

```
Single-core CPU: handles one task at a time
  -> Your server handles one request, then the next

Multi-core CPU: handles multiple tasks simultaneously
  -> 8 cores = 8 requests processed at the same moment

Modern servers: 32-128 cores
  -> Can genuinely do 32-128 things at once
```

**Key numbers to know:**

```
CPU clock speed:        3-4 GHz -> executes 3-4 billion operations/second
CPU cache (L1):         32 KB -> access in ~1 nanosecond
CPU cache (L2):         256 KB -> access in ~4 nanoseconds
CPU cache (L3):         8-32 MB -> access in ~10 nanoseconds
```

When Raju learned these numbers, his reaction was: "Wait, the CPU does 4 billion things a second, but accessing RAM takes 100 nanoseconds? That means the CPU is sitting idle for hundreds of cycles waiting for data!" Exactly right — and that is why caches exist.

<a id="cpu-cache"></a>

## The CPU Cache — Your Chef's Counter

The CPU has its own tiny, ultra-fast memory called **cache**. Think of it as the ingredients on the chef's immediate counter. Before going to the fridge (RAM), the CPU checks its cache first.

```
Cache hit:  Data is on the counter -> use it instantly (1 ns)
Cache miss: Not there -> walk to fridge (RAM) -> 100 ns wait

100x slower on a cache miss!
```

This is why **data locality matters** in system design. Code that accesses memory sequentially (like scanning an array) is much faster than random access — because sequential access stays in cache.

Raju tested this himself by timing two Python loops — one iterating through a list in order, another jumping to random indices. The sequential version was noticeably faster, even in Python. At the C/Rust level, the difference is dramatic.

[Back to Top](#top)

<a id="ram"></a>

# 4. RAM — The Workspace

<a id="ram-what-it-is"></a>

## What It Is

**RAM (Random Access Memory)** is your computer's working memory. It holds everything that is currently in use — running programs, open files, the data your code is actively processing.

When Raju deploys a Python web server, all of these live in RAM:
- His application code
- Every active connection's state
- The data loaded from the database
- Python's interpreter itself

<a id="ram-whiteboard-analogy"></a>

## The Whiteboard Analogy

Raju thinks of RAM as a **giant whiteboard** in the study room. You can write and erase quickly, but when the power goes out (or someone cleans the board), everything is gone.

```
+----------------------------------------------------------+
|                    RAM (The Whiteboard)                   |
|                                                          |
|  App Code    |  Active Connections   |  Temp Data        |
|  [loaded]    |  [conn1][conn2][conn3]|  [query results]  |
|              |                       |                   |
|  OS Kernel   |  Cache (Redis data)   |  Stack/Heap       |
|  [running]   |  [if in-process]      |  [for each req]   |
|                                                          |
|  Size: 8 GB - 1 TB on modern servers                    |
|  Speed: ~100 nanoseconds to read                        |
+----------------------------------------------------------+
```

When the server **restarts**, the whiteboard is **erased**. Everything in RAM is gone. That is why you need a database (persistent storage) for data you cannot afford to lose.

<a id="ram-system-design"></a>

## Why This Matters for System Design

```
RAM is fast but volatile (gone on restart):
  -> Store session data, active connections, computed caches here
  -> Never store user data ONLY here

RAM is limited:
  -> 16 GB RAM x 1 MB per request = only 16,000 simultaneous requests
  -> This is why large-scale servers need careful memory management

RAM latency vs disk:
  RAM:   100 ns
  SSD:   150,000 ns (150 us) -> 1,500x slower
  HDD:   10,000,000 ns (10 ms) -> 100,000x slower
```

**The rule:** Keep hot data in RAM. Only go to disk when you must.

Raju made this mistake once during a college project — he read a config file from disk on every single API request instead of loading it once into RAM. His "API" handled 2 requests per second. After caching the config in memory, it jumped to 500. Lesson learned permanently.

[Back to Top](#top)

<a id="disk"></a>

# 5. Disk — The Filing Cabinet

<a id="disk-what-it-is"></a>

## What It Is

**Disk storage** is permanent. It survives reboots, power cuts, disasters. When you save a file or commit to a database, it goes to disk.

Two types you will encounter constantly:

```
+-------------------------+----------------------------------+
|         HDD             |              SSD                 |
|  (Hard Disk Drive)      |       (Solid State Drive)        |
|                         |                                  |
|  Spinning magnetic disk |  No moving parts, flash memory   |
|  +----------+           |  +----------------------------+  |
|  |  o o o   | (platters)|  | [NAND chip][NAND chip]...  |  |
|  +----------+           |  +----------------------------+  |
|                         |                                  |
|  Read: ~10ms seek       |  Read: ~150us (100x faster!)     |
|  Cost: cheap            |  Cost: more expensive            |
|  Good for: bulk storage |  Good for: databases, fast I/O   |
+-------------------------+----------------------------------+
```

<a id="disk-library-analogy"></a>

## The Library Stacks Analogy

Raju's college library has a huge archive room in the basement. Everything is there, permanently stored, but it takes time to retrieve. You have to walk down the stairs, find the right shelf, pull the book, and walk back. That is exactly how disk access works.

```
Finding a book in the stacks (HDD):
  1. Walk to the shelf (seek time: ~5-10ms)
  2. Find the book (rotational latency: ~5ms)
  3. Pull it out and walk back (transfer time)

Total: ~10ms per random read

Compare to grabbing from the desk (RAM): 0.0001ms
```

<a id="disk-sequential-random"></a>

## Sequential vs Random I/O

This distinction will save you in system design interviews. Raju memorized this before his first interview and it came up immediately.

```
Sequential read:  Reading data in order (like reading a book page by page)
  HDD: very fast -- disk head doesn't need to move, stays in place
  SSD: very fast -- reads consecutive flash cells

Random read:  Jumping to different locations (like flipping to random pages)
  HDD: SLOW -- disk head has to physically seek to each position
  SSD: still fast -- no physical movement needed

Key insight:
  Databases that write sequentially (append-only logs) are much faster
  than those that write randomly. This is WHY Kafka, Cassandra, and
  RocksDB are so fast -- they're designed around sequential I/O.
```

[Back to Top](#top)

<a id="processes-threads"></a>

# 6. Processes and Threads — How Code Runs

Raju once asked his professor: "If the CPU only understands machine instructions, how does my laptop run Chrome, Spotify, and VS Code all at the same time?" The answer involves processes and threads — two concepts that confused Raju until he mapped them to something he already understood.

<a id="process-worker"></a>

## The Process — An Independent Worker

A **process** is a running instance of a program. When you start your Flask server, you create a process. It has:

```
+-----------------------------------------+
|              Process                     |
|                                         |
|  Code (instructions)                    |
|  Memory (its own private space)         |
|  File handles (open connections)        |
|  State (variables, objects in memory)   |
|                                         |
|  Isolated from other processes          |
|  -> crash in one doesn't kill others    |
+-----------------------------------------+
```

Processes are **expensive to create** and **isolated** from each other. Two processes cannot share memory directly (they need IPC — inter-process communication — like pipes or sockets).

<a id="thread-worker"></a>

## The Thread — A Worker Within a Worker

A **thread** lives inside a process and shares its memory.

```
+-----------------------------------------------------+
|                     Process                          |
|                                                     |
|  Shared Memory (heap, global variables, code)       |
|                                                     |
|  +--------------+  +--------------+  +------------+ |
|  |  Thread 1    |  |  Thread 2    |  |  Thread 3  | |
|  |              |  |              |  |            | |
|  |  stack       |  |  stack       |  |  stack     | |
|  |  local vars  |  |  local vars  |  |  local vars| |
|  +--------------+  +--------------+  +------------+ |
|                                                     |
|  Threads can READ/WRITE the same memory             |
|  -> Fast communication, but needs synchronization   |
+-----------------------------------------------------+
```

<a id="process-thread-analogy"></a>

## The Restaurant Staff Analogy

Raju went back to his uncle's restaurant analogy:

```
Process   = A restaurant (has its own kitchen, tables, everything)
Thread    = A waiter in the restaurant (shares the kitchen)

Multiple restaurants (processes):
  -> Independent, isolated
  -> One burns down, others fine
  -> But they can't share ingredients

Multiple waiters (threads) in one restaurant:
  -> Share the kitchen (shared memory)
  -> Fast to spin up, lightweight
  -> But two waiters grabbing the same pan at once = chaos (race condition)
```

This clicked for Raju instantly. A race condition is like two waiters both reaching for the last clean plate — one of them ends up empty-handed, and the customer gets confused.

<a id="context-switching"></a>

## Context Switching — The Cost of Multitasking

Your CPU has 8 cores but might have 500 active threads. How does it handle that?

**Context switching:** The CPU rapidly switches between threads, giving each a tiny slice of time (typically 1-10ms). To the user, it looks parallel.

```
CPU Core timeline:
  -------------------------------------------------
  |Thread A|Thread B|Thread C|Thread A|Thread B|Thread A|
  -------------------------------------------------
       1ms      1ms      1ms      1ms      1ms      1ms

  Each thread thinks it's running continuously.
  In reality: it's time-sliced.
```

**Context switch cost:** ~1-10 microseconds each. Sounds tiny, but:
- 1,000 threads leads to millions of switches per second leading to **significant CPU overhead**
- This is why async/event-loop models (Node.js, Python asyncio) can be more efficient than thread-per-request: they avoid context switching cost.

Raju tested this: he wrote a Python script spawning 10,000 threads doing nothing but sleeping. The process used 200MB of RAM just for thread stacks and the OS spent more time switching between them than doing useful work.

[Back to Top](#top)

<a id="memory-layout"></a>

# 7. Memory Layout Within a Process

The previous section explained that threads share heap memory and each have their own stack. Raju wanted to go one level deeper: what actually lives in each region, and why does it matter for writing efficient code?

<a id="memory-regions"></a>

## The Two Regions Every Process Has

```
+----------------------------------------------------------------+
|                         PROCESS                                 |
|                                                                 |
|  +----------------------------------+                          |
|  |            STACK                  |  Fast. Automatic.       |
|  |  - one frame per function call    |  Size: 1-8 MB typical  |
|  |  - local variable name bindings   |                         |
|  |  - grows downward, shrinks fast   |                         |
|  +----------------------------------+                          |
|             (grows down)                                        |
|                   ...                                           |
|             (grows up)                                          |
|  +----------------------------------+                          |
|  |            HEAP                   |  Flexible. GC-managed. |
|  |  - all objects (int, list, dict)  |  Size: grows as needed |
|  |  - persists across function calls |                         |
|  |  - requires GC or manual free     |                         |
|  +----------------------------------+                          |
|                                                                 |
|  +----------------------------------+                          |
|  |         DATA SEGMENT              |  Permanent.            |
|  |  - global and module-level vars   |  Lives for process     |
|  |  - static constants               |  lifetime.             |
|  +----------------------------------+                          |
+----------------------------------------------------------------+
```

<a id="stack-frame"></a>

## The Stack Frame — One per Function Call

Every time you call a function, the CPU pushes a **stack frame** onto the stack. The frame holds local variable name-to-reference bindings and the return address.

```python
def calculate(x, y):
    result = x + y
    return result

total = calculate(10, 5)
```

Stack state during execution:

```
DURING calculate(10, 5):

  +----------------------------------------------+  <- top of stack
  |  calculate() frame                           |
  |    x      -> [object: 10]  (on heap)         |
  |    y      -> [object: 5]   (on heap)         |
  |    result -> [object: 15]  (on heap)         |
  |    return address: -> back to global frame   |
  +----------------------------------------------+
  |  global frame                                |
  |    calculate -> [function object] (on heap)  |
  |    total -> ???                              |
  +----------------------------------------------+

AFTER calculate() returns:

  +----------------------------------------------+
  |  global frame                                |
  |    total -> [object: 15] (on heap)           |
  +----------------------------------------------+

  calculate() frame is GONE.
  x, y, result name bindings disappear.
  The integer objects on heap are collected when nothing else references them.
```

**Key insight:** The stack stores *name to reference* pairs, not actual values. The values always live on the heap.

<a id="scope-lifetime"></a>

## Scope and Memory Lifetime

This is where the thread diagram from earlier connects to code. Raju drew this table in his notebook and references it constantly:

```
+-----------+---------------------------+-----------------------+
|  Scope    |  Memory Location          |  Lifetime             |
+-----------+---------------------------+-----------------------+
|  Local    |  Stack frame              |  Dies on return       |
|  Enclosing|  Heap - closure cell obj  |  Lives while closure  |
|  (closure)|                           |  function is alive    |
|  Global   |  Module __dict__ (heap)   |  Lives forever        |
|  Built-in |  builtins module (heap)   |  Lives forever        |
+-----------+---------------------------+-----------------------+
```

Closure variables are special: when an inner function captures an outer variable, Python promotes it from the stack to a **cell object** on the heap. The outer function's frame can be destroyed, but the variable lives on.

```python
def make_adder(n):
    # 'n' is captured by inner() -> promoted to heap cell object
    def add(x):
        return x + n
    return add

add5 = make_adder(5)
# make_adder() returned -- its stack frame is gone
# but 'n=5' still lives in a cell on the heap
```

<a id="stack-vs-heap-speed"></a>

## Why Stack Access is Faster Than Heap Access

Connecting back to the latency table Raju will see next:

```
Stack (local variables): ~0.5-1 ns   -- CPU register or L1 cache
Heap  (object access):   ~100 ns     -- RAM access (cache miss)
                         ~100-200x slower
```

The CPU caches recently accessed stack data in L1 cache. Heap objects are scattered in memory — more cache misses, slower access.

**Practical implication:** Caching a frequently-used function/attribute in a local variable (not reaching into the heap dict every iteration) can give real speedups in tight loops. Python's bytecode even has a separate `LOAD_FAST` instruction for locals vs `LOAD_GLOBAL` for globals — because locals are designed to be fast.

Raju verified this with `dis.dis()` and saw that local variable access is a single bytecode instruction while global access requires a dictionary lookup every time.

[Back to Top](#top)

<a id="latency"></a>

# 8. Latency — The Speed of Everything

Raju's professor once said: "If you only memorize one table in your entire CS career, make it this one." She was right. This table fundamentally shapes every system design decision.

```
+-------------------------------------------------------------+
|              Latency Reference (approximate)                 |
|                                                              |
|  Operation                        Time        Analogy        |
|  -----------------------------------------------------------+
|  L1 cache access                  0.5 ns      Grab from hand|
|  L2 cache access                  7 ns        Reach to desk |
|  RAM access                       100 ns      Walk to shelf |
|  SSD random read                  150,000 ns  Drive to store|
|  Network (same data center)       500,000 ns  Cross-city    |
|  HDD seek + read                  10,000,000  Drive to mall |
|  Network (US to Europe)           150,000,000 Cross-country |
|                                                              |
|  If RAM = 1 second, then:                                    |
|    SSD read    = 25 minutes                                  |
|    Network DC  = 1.4 hours                                   |
|    HDD         = 28 hours                                    |
|    US to Europe = 4.8 years                                  |
+-------------------------------------------------------------+
```

**This is why caching matters so much:** If you can serve from RAM instead of disk, you are 1,500x faster. If you can serve from cache instead of making a network call, you save hundreds of milliseconds.

Raju stuck this table on his hostel room wall. Every time he designs a system now, he mentally asks: "Where is the data coming from? Cache? RAM? Disk? Network? How many of those hops can I eliminate?"

[Back to Top](#top)

<a id="io"></a>

# 9. I/O — The Waiting Problem

Raju's biggest "aha" moment came when he realized that most of his server's time is spent **waiting**, not computing. The CPU finishes its work in nanoseconds but then sits idle for milliseconds waiting for a database response.

<a id="blocking-io"></a>

## The Blocking I/O Problem

When your code reads from disk or network, the CPU has to **wait**.

```python
# This line blocks the entire thread for ~150ms (SSD read)
data = read_from_database(query)

# Thread is doing NOTHING during those 150ms
# It's just sitting there, waiting
# Meanwhile: thousands of other requests are waiting in queue
```

```
Thread-per-request model (blocking):

Request 1: [processing][WAITING for DB][processing] -> done
Request 2:                    [waiting for thread]...[processing]
Request 3:                              [waiting for thread]...

Each request holds a thread hostage while waiting for I/O.
100 concurrent requests = 100 threads all sleeping.
```

<a id="async-io"></a>

## The Solution — Async I/O and Event Loop

Raju thought of it like a restaurant again. A smart waiter does not stand at the kitchen window waiting for one dish. He takes multiple orders, drops them off, and checks back when the bell rings.

```
Event loop model (non-blocking):

Single thread:
  -> Start request 1's DB query, register callback
  -> Start request 2's DB query, register callback
  -> Start request 3's DB query, register callback
  -> DB query 1 done! -> run callback, send response
  -> DB query 2 done! -> run callback, send response
  -> DB query 3 done! -> run callback, send response

One thread handles all 3 concurrently!
No blocking. No wasted waiting.
```

This is why **Node.js** became popular for I/O-heavy APIs, and why **Python asyncio** is used for high-concurrency services.

Raju rewrote his college project's database layer using `asyncio` and `asyncpg` instead of synchronous `psycopg2`. Same hardware, same database — but throughput jumped from 200 req/s to 2,000 req/s. The CPU was already fast enough; it was the blocking that killed performance.

[Back to Top](#top)

<a id="serialization"></a>

# 10. Serialization — Speaking a Common Language

<a id="serialization-problem"></a>

## The Problem

When two computers need to share data, they need a common format. Raju's Python dict `{"user": "Alice", "age": 25}` cannot literally be sent over the network — it is an in-memory Python object.

You need to **serialize** it (convert to bytes) to send, and **deserialize** it (convert from bytes back to object) to receive.

Raju thinks of it like translating between languages. Two people who speak different languages need a common written form to communicate. That written form is the serialization format.

<a id="serialization-formats"></a>

## Formats Compared

```
JSON:
  {"user": "Alice", "age": 25}
  + Human readable
  + Universal support
  - Slow to parse at scale
  - No types (everything is string/number/null)
  - Large size

Protocol Buffers (Protobuf):
  [binary bytes]
  + 3-10x smaller than JSON
  + 5-10x faster to serialize/deserialize
  + Typed (int32, string, bool, etc.)
  - Not human readable
  - Need .proto schema file
  - Used by: gRPC, Google internal systems

MessagePack:
  [binary bytes, but dict-like]
  + Smaller than JSON, no schema needed
  + Faster than JSON
  - Less common than JSON or Protobuf

CSV:
  Alice,25
  + Ultra simple
  - Only for flat data

Rule of thumb:
  Public API talking to browsers/mobile:     -> JSON
  Internal service-to-service (high volume): -> Protobuf
  Analytics/bulk data export:                -> Parquet (columnar)
```

[Back to Top](#top)

<a id="full-journey"></a>

# 11. How This All Comes Together — Following Hey

Remember Raju's WhatsApp "Hey!" from the beginning? Now that he understands every layer, let us trace the full journey:

```
Raju's phone taps Send
    |
    v
1. CPU (his phone):
   Serializes message to JSON/Protobuf bytes
   Prepares TCP packet

2. Network (WiFi/4G):
   Packet travels ~20ms to WhatsApp's server

3. Server receives packet:
   CPU core wakes up thread/coroutine handling Raju's connection
   Deserializes bytes back to message struct (RAM)

4. Business logic (RAM):
   "Is recipient online? What's their server ID?"
   Check in-memory hash map: O(1) lookup, ~100ns

5. Disk I/O (if needed):
   Persist message to database (SSD write: ~150us)

6. Forward to recipient:
   Look up recipient's WebSocket connection (RAM)
   Serialize message again
   Send via network

7. Recipient's phone:
   Deserializes message
   CPU updates UI
   Raju's friend sees "Hey!" on screen

Total time: ~50-200ms
```

That entire journey — across hardware, RAM, disk, and network, through serialization, deserialization, and lookup — happens before Raju can look up from his phone. Every concept from this module played a role.

[Back to Top](#top)

<a id="mental-models"></a>

# 12. Mental Models to Carry Forward

Raju distilled everything into five rules he carries into every system design discussion:

```
1. Memory hierarchy: registers -> cache -> RAM -> SSD -> HDD -> network
   Each level is 10-1000x slower than the previous.
   Good design keeps hot data at the fastest level possible.

2. Processes are isolated. Threads share memory.
   Shared memory = fast communication, but requires careful synchronization.

3. I/O is slow. Blocking I/O wastes threads.
   For high concurrency: async I/O > thread-per-request.

4. Serialization is the cost of communication.
   JSON for humans. Protobuf for machines.

5. Every network call is expensive.
   50-500ms x 10 service calls = 500ms-5s of pure waiting.
   Minimize round trips. Batch where possible.
```

[Back to Top](#top)

<a id="connection-next"></a>

# 13. Connection to What Comes Next

Every system design topic Raju will learn connects back to these fundamentals:

```
Databases        -> Disk I/O, memory hierarchy, serialization
Caching          -> Memory hierarchy (RAM vs disk), latency numbers
Message Queues   -> Process/thread isolation, async I/O
Load Balancing   -> Multiple processes/servers, CPU cores
Microservices    -> Processes communicating over network
Observability    -> CPU/memory/I/O metrics are what you monitor
```

Understanding this foundation makes every other topic click. Raju now reads system design articles and thinks: "Oh, they are just keeping hot data in RAM" or "they are avoiding blocking I/O with an event loop." The vocabulary changes but the physics stays the same.

[Back to Top](#top)

<a id="practice"></a>

# 14. Practice Exercises

> **Exercise 1.** A single database query takes 10ms. Your API calls the database 5 times per request. What is the minimum response time? How would you reduce it?

> **Exercise 2.** You have a server with 8 CPU cores. Your web framework uses 1 thread per request. What is the maximum concurrent requests before CPU becomes the bottleneck? (Hint: depends on how much of each request is CPU-bound vs I/O-bound)

> **Exercise 3.** Your service currently serializes responses as JSON. A performance engineer says switching to Protobuf would improve throughput by 10%. When is this worth doing, and when is it premature optimization?

> **Exercise 4.** You have a Python service with a 10ms database call per request. It handles 500 req/s currently. By how much could you increase concurrency by switching from blocking I/O to async I/O? (Think about what is holding it back)

> **Exercise 5.** Raju's API reads a 2KB config from disk on every request. The server handles 1,000 req/s. Calculate the total wasted I/O time per second if each disk read takes 150 microseconds. What is the fix?

[Back to Top](#top)

<a id="summary"></a>

# 15. Summary

**CPU:** The brain that executes billions of operations per second across multiple cores. Cache hierarchy (L1/L2/L3) keeps frequently accessed data close to avoid expensive RAM trips.

**RAM:** Fast volatile workspace (~100ns access). Everything currently running lives here. Gone on restart — never store persistent data only in RAM.

**Disk:** Permanent storage. SSDs are 100x faster than HDDs for random reads. Sequential I/O is the secret weapon behind Kafka and Cassandra.

**Processes and Threads:** Processes are isolated (safe but expensive). Threads share memory (fast but need synchronization). Context switching is the hidden tax of too many threads.

**Memory Layout:** Stack holds name-to-reference bindings per function call (fast, automatic). Heap holds all objects (flexible, GC-managed, slower access). Local variable access is ~100x faster than heap lookups.

**Latency:** The numbers that shape all design decisions. RAM is 1,500x faster than SSD; SSD is 67x faster than HDD; same-datacenter network is 3x slower than SSD.

**I/O:** Blocking I/O wastes threads. Async I/O (event loops) lets one thread handle thousands of concurrent operations by never waiting idle.

**Serialization:** The cost of communication between systems. JSON for human-facing APIs, Protobuf for internal high-throughput services.

[Back to Top](#top)

## Navigation

| | |
|---|---|
| **Section** | 04 System Design Mastery |
| **Module** | 00 Computer Fundamentals |
| **Prev** | -- (first module) |
| **Next** | [01 Networking Basics](../01_networking_basics/theory.md) |
| **Home** | [README](../README.md) |
