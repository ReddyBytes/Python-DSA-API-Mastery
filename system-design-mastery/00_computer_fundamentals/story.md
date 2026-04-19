# A Day in the Life of a Web Request
## Understanding Computers from the Ground Up

> Before you design systems that run on computers, you need to understand what
> computers actually do. This isn't a textbook chapter — it's a story.

---

## 📌 Learning Priority

**Must Learn** — Core concept, daily use, interview essential:
latency hierarchy (CPU cache/RAM/SSD/network) · CPU cores and cache levels · memory layout (stack vs heap)

**Should Learn** — Important for real projects, comes up regularly:
process vs thread · context switching cost · I/O blocking vs async models

**Good to Know** — Useful in specific situations, not always tested:
serialization format trade-offs · L1/L2/L3 cache behavior

**Reference** — Know it exists, look up syntax when needed:
specific nanosecond/microsecond latency numbers · NUMA architecture

---

## The Story Begins: You Click "Send"

Imagine you're chatting with a friend on WhatsApp. You type "Hey!" and tap Send.

In the next **200 milliseconds** — faster than you can blink — your message travels
from your thumb, through layers of hardware, across the internet, and arrives in
your friend's phone.

How? Let's follow that journey from the very beginning.

---

## Part 1: The CPU — The Brain That Never Stops

### What it is

The **CPU (Central Processing Unit)** is the part of your computer that actually
*executes* code. When you write:

```python
result = 2 + 2
```

...the CPU is what physically adds those numbers together using transistors.
Billions of tiny switches, flipping on and off, billions of times per second.

### The Restaurant Kitchen Analogy

Think of the CPU as a **head chef** in a restaurant kitchen.

```
┌─────────────────────────────────────────────────────────────┐
│                    Restaurant Kitchen                        │
│                                                             │
│  Head Chef (CPU Core)  ← Takes one order at a time         │
│  ┌─────────────────┐                                        │
│  │  Chef's Counter │  ← CPU Cache (ingredients right here) │
│  │  (Super fast)   │                                        │
│  └────────┬────────┘                                        │
│           │  needs ingredient                               │
│  ┌────────▼────────┐                                        │
│  │   Walk-in Fridge│  ← RAM (a bit farther, still fast)     │
│  │   (Fast access) │                                        │
│  └────────┬────────┘                                        │
│           │  not in fridge                                  │
│  ┌────────▼────────┐                                        │
│  │   Storage Room  │  ← Disk (slow, far away)               │
│  │   (Slow access) │                                        │
│  └─────────────────┘                                        │
└─────────────────────────────────────────────────────────────┘
```

The chef can only work on ONE dish at a time per hand (core). But a modern CPU
has **multiple cores** — imagine 8 chefs working simultaneously.

### Why This Matters for System Design

```
Single-core CPU: handles one task at a time
  → Your server handles one request, then the next

Multi-core CPU: handles multiple tasks simultaneously
  → 8 cores = 8 requests processed at the same moment

Modern servers: 32-128 cores
  → Can genuinely do 32-128 things at once
```

**Key numbers to know:**
```
CPU clock speed:        3-4 GHz → executes 3-4 billion operations/second
CPU cache (L1):         32 KB → access in ~1 nanosecond
CPU cache (L2):         256 KB → access in ~4 nanoseconds
CPU cache (L3):         8-32 MB → access in ~10 nanoseconds
```

### The CPU Cache — Your Chef's Counter

The CPU has its own tiny, ultra-fast memory called **cache**.
Think of it as the ingredients on the chef's immediate counter.
Before going to the fridge (RAM), the CPU checks its cache first.

```
Cache hit:  Data is on the counter → use it instantly (1 ns)
Cache miss: Not there → walk to fridge (RAM) → 100 ns wait

100x slower on a cache miss!
```

This is why **data locality matters** in system design. Code that accesses
memory sequentially (like scanning an array) is much faster than random
access — because sequential access stays in cache.

---

## Part 2: RAM — The Workspace

### What it is

**RAM (Random Access Memory)** is your computer's working memory.
It holds everything that's currently in use — running programs, open files,
the data your code is actively processing.

When you deploy a Python web server, all of these live in RAM:
- Your application code
- Every active connection's state
- The data you've loaded from the database
- Python's interpreter itself

### The Whiteboard Analogy

RAM is like a **giant whiteboard** in the office.

```
┌──────────────────────────────────────────────────────────┐
│                    RAM (The Whiteboard)                   │
│                                                          │
│  App Code    │  Active Connections   │  Temp Data       │
│  [loaded]    │  [conn1][conn2][conn3] │  [query results] │
│              │                       │                   │
│  OS Kernel   │  Cache (Redis data)   │  Stack/Heap       │
│  [running]   │  [if in-process]      │  [for each req]  │
│                                                          │
│  Size: 8 GB - 1 TB on modern servers                    │
│  Speed: ~100 nanoseconds to read                        │
└──────────────────────────────────────────────────────────┘
```

When the server **restarts** → the whiteboard is **erased**. Everything in RAM
is gone. That's why you need a database (persistent storage) for data you
can't afford to lose.

### Why This Matters for System Design

```
RAM is fast but volatile (gone on restart):
  → Store session data, active connections, computed caches here
  → Never store user data ONLY here

RAM is limited:
  → 16 GB RAM × 1 MB per request = only 16,000 simultaneous requests
  → This is why large-scale servers need careful memory management

RAM latency vs disk:
  RAM:   100 ns
  SSD:   150,000 ns (150 μs) → 1,500× slower
  HDD:   10,000,000 ns (10 ms) → 100,000× slower
```

**The rule:** Keep hot data in RAM. Only go to disk when you must.

---

## Part 3: Disk — The Filing Cabinet

### What it is

**Disk storage** is permanent. It survives reboots, power cuts, disasters.
When you save a file or commit to a database, it goes to disk.

Two types you'll encounter constantly:

```
┌─────────────────────────┬──────────────────────────────────┐
│         HDD             │              SSD                 │
│  (Hard Disk Drive)      │       (Solid State Drive)        │
│                         │                                  │
│  Spinning magnetic disk │  No moving parts, flash memory  │
│  ┌─────────┐            │  ┌────────────────────────────┐ │
│  │  ○ ○ ○  │ (platters) │  │  [NAND chip][NAND chip]... │ │
│  └─────────┘            │  └────────────────────────────┘ │
│                         │                                  │
│  Read: ~10ms seek       │  Read: ~150μs (100× faster!)    │
│  Cost: cheap            │  Cost: more expensive            │
│  Good for: bulk storage │  Good for: databases, fast I/O  │
└─────────────────────────┴──────────────────────────────────┘
```

### The Library Stacks Analogy

Disk is like the **back stacks of a library** — everything is there,
permanently stored, but it takes time to retrieve.

```
Finding a book in the stacks (HDD):
  1. Walk to the shelf (seek time: ~5-10ms)
  2. Find the book (rotational latency: ~5ms)
  3. Pull it out and walk back (transfer time)

Total: ~10ms per random read

Compare to grabbing from the desk (RAM): 0.0001ms
```

### Sequential vs Random I/O

This distinction will save you in system design interviews.

```
Sequential read:  Reading data in order (like reading a book page by page)
  HDD: very fast — disk head doesn't need to move, stays in place
  SSD: very fast — reads consecutive flash cells

Random read:  Jumping to different locations (like flipping to random pages)
  HDD: SLOW — disk head has to physically seek to each position
  SSD: still fast — no physical movement needed

Key insight:
  Databases that write sequentially (append-only logs) are much faster
  than those that write randomly. This is WHY Kafka, Cassandra, and
  RocksDB are so fast — they're designed around sequential I/O.
```

---

## Part 4: Processes and Threads — How Code Runs

### The Process — An Independent Worker

A **process** is a running instance of a program. When you start your Flask
server, you create a process. It has:

```
┌─────────────────────────────────────────┐
│              Process                    │
│                                         │
│  Code (instructions)                   │
│  Memory (its own private space)         │
│  File handles (open connections)        │
│  State (variables, objects in memory)   │
│                                         │
│  Isolated from other processes          │
│  → crash in one doesn't kill others     │
└─────────────────────────────────────────┘
```

Processes are **expensive to create** and **isolated** from each other.
Two processes can't share memory directly (they need IPC — inter-process
communication — like pipes or sockets).

### The Thread — A Worker Within a Worker

A **thread** lives inside a process and shares its memory.

```
┌─────────────────────────────────────────────────────┐
│                     Process                         │
│                                                     │
│  Shared Memory (heap, global variables, code)       │
│                                                     │
│  ┌─────────────┐  ┌─────────────┐  ┌────────────┐  │
│  │  Thread 1   │  │  Thread 2   │  │  Thread 3  │  │
│  │             │  │             │  │            │  │
│  │  stack      │  │  stack      │  │  stack     │  │
│  │  local vars │  │  local vars │  │  local vars│  │
│  └─────────────┘  └─────────────┘  └────────────┘  │
│                                                     │
│  Threads can READ/WRITE the same memory             │
│  → Fast communication, but needs synchronization   │
└─────────────────────────────────────────────────────┘
```

### The Restaurant Staff Analogy

```
Process   = A restaurant (has its own kitchen, tables, everything)
Thread    = A waiter in the restaurant (shares the kitchen)

Multiple restaurants (processes):
  → Independent, isolated
  → One burns down, others fine
  → But they can't share ingredients

Multiple waiters (threads) in one restaurant:
  → Share the kitchen (shared memory)
  → Fast to spin up, lightweight
  → But two waiters grabbing the same pan at once = chaos (race condition)
```

### Context Switching — The Cost of Multitasking

Your CPU has 8 cores but might have 500 active threads. How does it handle that?

**Context switching:** The CPU rapidly switches between threads, giving each
a tiny slice of time (typically 1-10ms). To the user, it looks parallel.

```
CPU Core timeline:
  ─────────────────────────────────────────────────────
  │Thread A│Thread B│Thread C│Thread A│Thread B│Thread A│
  ─────────────────────────────────────────────────────
       1ms      1ms      1ms      1ms      1ms      1ms

  Each thread thinks it's running continuously.
  In reality: it's time-sliced.
```

**Context switch cost:** ~1-10 microseconds each. Sounds tiny, but:
- 1,000 threads → millions of switches per second → **significant CPU overhead**
- This is why async/event-loop models (Node.js, Python asyncio) can be
  more efficient than thread-per-request: they avoid context switching cost.

---

## Part 4.5: Memory Layout Within a Process — Where Variables Live

The previous section explained that threads share heap memory and each have their own stack. Let's go one level deeper: what actually lives in each region, and why it matters for writing efficient code.

### The Two Regions Every Process Has

```
┌────────────────────────────────────────────────────────────────┐
│                         PROCESS                                │
│                                                                │
│  ┌──────────────────────────────────┐                         │
│  │            STACK                 │  Fast. Automatic.       │
│  │  - one frame per function call   │  Size: 1–8 MB typical   │
│  │  - local variable name bindings  │                         │
│  │  - grows downward, shrinks fast  │                         │
│  └──────────────────────────────────┘                         │
│             ↕ (grows down)                                     │
│                   ...                                          │
│             ↕ (grows up)                                       │
│  ┌──────────────────────────────────┐                         │
│  │            HEAP                  │  Flexible. GC-managed.  │
│  │  - all objects (int, list, dict) │  Size: grows as needed  │
│  │  - persists across function calls│                         │
│  │  - requires GC or manual free    │                         │
│  └──────────────────────────────────┘                         │
│                                                                │
│  ┌──────────────────────────────────┐                         │
│  │         DATA SEGMENT             │  Permanent.             │
│  │  - global and module-level vars  │  Lives for process      │
│  │  - static constants              │  lifetime.              │
│  └──────────────────────────────────┘                         │
└────────────────────────────────────────────────────────────────┘
```

### The Stack Frame — One per Function Call

Every time you call a function, the CPU pushes a **stack frame** onto the stack. The frame holds local variable name-to-reference bindings and the return address.

```
def calculate(x, y):
    result = x + y
    return result

total = calculate(10, 5)
```

Stack state during execution:

```
DURING calculate(10, 5):

  ┌──────────────────────────────────────────────┐  ← top of stack
  │  calculate() frame                           │
  │    x      → [object: 10]  (on heap)          │
  │    y      → [object: 5]   (on heap)          │
  │    result → [object: 15]  (on heap)          │
  │    return address: → back to global frame    │
  ├──────────────────────────────────────────────┤
  │  global frame                                │
  │    calculate → [function object] (on heap)   │
  │    total → ???                               │
  └──────────────────────────────────────────────┘

AFTER calculate() returns:

  ┌──────────────────────────────────────────────┐
  │  global frame                                │
  │    total → [object: 15] (on heap)            │
  └──────────────────────────────────────────────┘

  calculate() frame is GONE.
  x, y, result name bindings disappear.
  The integer objects on heap are collected when nothing else references them.
```

**Key insight:** The stack stores *name → reference* pairs, not actual values. The values always live on the heap.

### Scope and Memory Lifetime

This is where the "thread diagram" from earlier connects to code:

```
┌─────────────────────────────────────────────────────────────────┐
│  Scope      │  Memory Location          │  Lifetime             │
├─────────────┼───────────────────────────┼───────────────────────┤
│  Local      │  Stack frame              │  Dies on return       │
│  Enclosing  │  Heap — closure cell obj  │  Lives while closure  │
│  (closure)  │                           │  function is alive    │
│  Global     │  Module __dict__ (heap)   │  Lives forever        │
│  Built-in   │  builtins module (heap)   │  Lives forever        │
└─────────────────────────────────────────────────────────────────┘
```

Closure variables are special: when an inner function captures an outer variable, Python promotes it from the stack to a **cell object** on the heap. The outer function's frame can be destroyed, but the variable lives on.

```python
def make_adder(n):
    # 'n' is captured by inner() → promoted to heap cell object
    def add(x):
        return x + n
    return add

add5 = make_adder(5)
# make_adder() returned — its stack frame is gone
# but 'n=5' still lives in a cell on the heap
```

### Why Stack Access is Faster Than Heap Access

Connecting back to the latency table you'll see next:

```
Stack (local variables): ~0.5–1 ns   — CPU register or L1 cache
Heap  (object access):   ~100 ns     — RAM access (cache miss)
                         ~100–200× slower
```

The CPU caches recently accessed stack data in L1 cache. Heap objects are scattered in memory — more cache misses, slower access.

**Practical implication:** Caching a frequently-used function/attribute in a local variable (not reaching into the heap dict every iteration) can give real speedups in tight loops. Python's bytecode even has a separate `LOAD_FAST` instruction for locals vs `LOAD_GLOBAL` for globals — because locals are designed to be fast.

---

## Part 5: Latency — The Speed of Everything

### The Numbers That Change How You Design

This table is worth memorizing. It fundamentally shapes system design:

```
┌─────────────────────────────────────────────────────────────┐
│              Latency Reference (approximate)                │
│                                                             │
│  Operation                        Time        Analogy       │
│  ─────────────────────────────────────────────────────────  │
│  L1 cache access                  0.5 ns      Grab from hand│
│  L2 cache access                  7 ns        Reach to desk │
│  RAM access                       100 ns      Walk to shelf │
│  SSD random read                  150,000 ns  Drive to store│
│  Network (same data center)       500,000 ns  Cross-city    │
│  HDD seek + read                  10,000,000  Drive to mall │
│  Network (US → Europe)            150,000,000 Cross-country │
│                                                             │
│  If RAM = 1 second, then:                                   │
│    SSD read    = 25 minutes                                 │
│    Network DC  = 1.4 hours                                  │
│    HDD         = 28 hours                                   │
│    US → Europe = 4.8 years                                  │
└─────────────────────────────────────────────────────────────┘
```

**This is why caching matters so much:** If you can serve from RAM instead
of disk, you're 1,500× faster. If you can serve from cache instead of
making a network call, you save hundreds of milliseconds.

---

## Part 6: I/O — The Waiting Problem

### The Blocking I/O Problem

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

Request 1: [processing][WAITING for DB][processing] → done
Request 2:                    [waiting for thread]...[processing]
Request 3:                              [waiting for thread]...

Each request holds a thread hostage while waiting for I/O.
100 concurrent requests = 100 threads all sleeping.
```

### The Solution: Async I/O / Event Loop

```
Event loop model (non-blocking):

Single thread:
  → Start request 1's DB query, register callback
  → Start request 2's DB query, register callback
  → Start request 3's DB query, register callback
  → DB query 1 done! → run callback, send response
  → DB query 2 done! → run callback, send response
  → DB query 3 done! → run callback, send response

One thread handles all 3 concurrently!
No blocking. No wasted waiting.
```

This is why **Node.js** became popular for I/O-heavy APIs, and why
**Python asyncio** is used for high-concurrency services.

---

## Part 7: Serialization — Speaking a Common Language

### The Problem

When two computers need to share data, they need a common format.
Your Python dict `{"user": "Alice", "age": 25}` cannot literally be
sent over the network — it's an in-memory Python object.

You need to **serialize** it (convert to bytes) to send, and
**deserialize** it (convert from bytes back to object) to receive.

### Formats Compared

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
  + 3-10× smaller than JSON
  + 5-10× faster to serialize/deserialize
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
  Public API talking to browsers/mobile:     → JSON
  Internal service-to-service (high volume): → Protobuf
  Analytics/bulk data export:                → Parquet (columnar)
```

---

## Part 8: How This All Comes Together — Following "Hey!"

Remember the WhatsApp "Hey!" from the beginning? Let's trace it:

```
Your phone taps Send
    │
    ▼
1. CPU (your phone):
   Serializes message to JSON/Protobuf bytes
   Prepares TCP packet

2. Network (WiFi/4G):
   Packet travels ~20ms to WhatsApp's server

3. Server receives packet:
   CPU core wakes up thread/coroutine handling your connection
   Deserializes bytes back to message struct (RAM)

4. Business logic (RAM):
   "Is recipient online? What's their server ID?"
   Check in-memory hash map: O(1) lookup, ~100ns

5. Disk I/O (if needed):
   Persist message to database (SSD write: ~150μs)

6. Forward to recipient:
   Look up recipient's WebSocket connection (RAM)
   Serialize message again
   Send via network

7. Recipient's phone:
   Deserializes message
   CPU updates UI
   Your friend sees "Hey!" on screen

Total time: ~50-200ms
```

That entire journey — across hardware, RAM, disk, and network,
through serialization, deserialization, and lookup — happens before
you can look up from your phone.

---

## The Mental Models to Carry Forward

```
1. Memory hierarchy: registers → cache → RAM → SSD → HDD → network
   Each level is 10-1000× slower than the previous.
   Good design keeps hot data at the fastest level possible.

2. Processes are isolated. Threads share memory.
   Shared memory = fast communication, but requires careful synchronization.

3. I/O is slow. Blocking I/O wastes threads.
   For high concurrency: async I/O > thread-per-request.

4. Serialization is the cost of communication.
   JSON for humans. Protobuf for machines.

5. Every network call is expensive.
   50-500ms × 10 service calls = 500ms-5s of pure waiting.
   Minimize round trips. Batch where possible.
```

---

## Connection to What Comes Next

Every system design topic you'll learn connects back to this:

```
Databases        → Disk I/O, memory hierarchy, serialization
Caching          → Memory hierarchy (RAM vs disk), latency numbers
Message Queues   → Process/thread isolation, async I/O
Load Balancing   → Multiple processes/servers, CPU cores
Microservices    → Processes communicating over network
Observability    → CPU/memory/I/O metrics are what you monitor
```

Understanding this foundation makes every other topic click.

---

## Mini Exercises

**1.** A single database query takes 10ms. Your API calls the database 5 times per request.
What's the minimum response time? How would you reduce it?

**2.** You have a server with 8 CPU cores. Your web framework uses 1 thread per request.
What's the maximum concurrent requests before CPU becomes the bottleneck?
(Hint: depends on how much of each request is CPU-bound vs I/O-bound)

**3.** Your service currently serializes responses as JSON. A performance engineer says
switching to Protobuf would improve throughput by 10%. When is this worth doing,
and when is it premature optimization?

**4.** You have a Python service with a 10ms database call per request. It handles
500 req/s currently. By how much could you increase concurrency by switching
from blocking I/O to async I/O? (Think about what's holding it back)

---

## 🔁 Navigation

| | |
|---|---|
| ➡️ Next | [01 — Networking Basics](../01_networking_basics/theory.md) |
| 🏠 Home | [README.md](../README.md) |

---

**[🏠 Back to README](../README.md)**

**Prev:** — &nbsp;|&nbsp; **Next:** [Networking Basics — Theory →](../01_networking_basics/theory.md)
