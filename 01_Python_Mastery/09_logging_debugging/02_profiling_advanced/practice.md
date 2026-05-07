# 💻 Practice — 02_profiling_advanced

> 🛠️ **Solve locally:** [practice_local.py](./practice_local.py)

---

## Quick Index

| Q | Difficulty | Topic | Title |
|---|-----------|-------|-------|
| [Q1](#q1--cprofile--profile-a-function-with-cprofilerun-and-read-the-output) | 🟢 Easy | cProfile | Profile a function with cProfile.run() and read the output |
| [Q2](#q2--pstats--sort-cprofile-output-by-cumulative-time-show-top-10) | 🟡 Medium | pstats | Sort cProfile output by cumulative time, show top 10 |
| [Q3](#q3--tracemalloc--find-the-3-lines-allocating-the-most-memory-in-a-script) | 🟡 Medium | tracemalloc | Find the 3 lines allocating the most memory in a script |
| [Q4](#q4--line_profiler--add-profile-decorator-and-run-kernprof-to-find-a-slow-line) | 🟡 Medium | line_profiler | Add @profile decorator and run kernprof to find a slow line |
| [Q5](#q5--inspect--use-inspectsignature-to-introspect-a-functions-parameters) | 🟡 Medium | inspect | Use inspect.signature() to introspect a function's parameters |
| [Q6](#q6--inspect-stack--use-inspectstack-inside-a-function-to-print-the-call-chain) | 🟡 Medium | inspect stack | Use inspect.stack() inside a function to print the call chain |
| [Q7](#q7--loguru-basics--replace-loggingbasicconfig-with-logurus-one-liner-setup) | 🟡 Medium | loguru basics | Replace logging.basicConfig with loguru's one-liner setup |
| [Q8](#q8--loguru-bind--use-loggerbind-to-add-context-to-every-log-line) | 🟡 Medium | loguru bind | Use logger.bind(request_id=...) to add context to every log line |
| [Q9](#q9--async-debug--enable-asyncio-debug-mode-and-catch-a-coroutine-that-never-awaits) | 🟡 Medium | async debug | Enable asyncio debug mode and catch a coroutine that never awaits |
| [Q10](#q10--objgraph--use-objgraphshow_most_common_types-to-find-a-memory-leak) | 🟠 Hard | objgraph | Use objgraph.show_most_common_types() to find a memory leak |
| [Q11](#q11--debugpy--configure-debugpy-to-listen-on-port-5678-for-vs-code-attach) | 🟠 Hard | debugpy | Configure debugpy to listen on port 5678 for VS Code attach |
| [Q12](#q12--capstone--profile-optimize-and-verify) | 🟠 Hard | Capstone | Profile a slow function, identify the hotspot, optimize, verify |

---

### Q1 🟢 · cProfile — Profile a function with cProfile.run() and read the output

> 🛠️ **Solve locally:** [practice_local.py → Q1](./practice_local.py)

You have a slow function `slow_sum(n)` that sums squares from 0 to n. Use `cProfile.run()` to profile it and print the stats table to stdout.

**What you should see:** columns named `ncalls`, `tottime`, `cumtime`, and the function names that consumed the most time.

<details>
<summary>Hint</summary>

Pass the function call as a string to `cProfile.run()`. To print immediately without saving to a file, omit the second argument.

</details>

<details>
<summary>Answer</summary>

```python
import cProfile

def slow_sum(n):
    total = 0
    for i in range(n):
        total += i * i       # ← intentionally naive to generate measurable time
    return total

cProfile.run('slow_sum(500_000)')
# Output shows: ncalls, tottime, percall, cumtime, percall for each function in the call tree
```

**Why:** `cProfile.run()` instruments the Python interpreter's function call hooks — every call and return is recorded with timestamps. Passing the expression as a string lets cProfile compile and execute it in a fresh namespace.

</details>

---

### Q2 🟡 · pstats — Sort cProfile output by cumulative time, show top 10

> 🛠️ **Solve locally:** [practice_local.py → Q2](./practice_local.py)

Save a cProfile run to `'output.prof'`, then use `pstats.Stats` to load it, strip directory prefixes from filenames, sort by `'cumtime'`, and print the top 10 rows.

<details>
<summary>Hint</summary>

`pstats.Stats` accepts either a filename string or a `cProfile.Profile` object. Call `.strip_dirs()`, then `.sort_stats()`, then `.print_stats(10)`.

</details>

<details>
<summary>Answer</summary>

```python
import cProfile
import pstats

def work():
    return sum(i ** 2 for i in range(200_000))

cProfile.run('work()', 'output.prof')          # ← save raw stats to file

stats = pstats.Stats('output.prof')
stats.strip_dirs()                              # ← removes full paths, keeps filenames only
stats.sort_stats('cumtime')                     # ← most expensive callers first
stats.print_stats(10)                           # ← show only top 10 entries
```

**Why:** `cumtime` (cumulative time) includes time spent in sub-calls, making it the right column to find entry-point bottlenecks. `tottime` is better for finding where work actually happens inside a function itself.

</details>

---

### Q3 🟡 · tracemalloc — Find the 3 lines allocating the most memory in a script

> 🛠️ **Solve locally:** [practice_local.py → Q3](./practice_local.py)

Use `tracemalloc` to identify the top 3 source lines that allocate the most memory during execution of a function that builds several large lists.

<details>
<summary>Hint</summary>

Call `tracemalloc.start()` before the code runs, `tracemalloc.take_snapshot()` after, then `snapshot.statistics('lineno')` to get results sorted by size.

</details>

<details>
<summary>Answer</summary>

```python
import tracemalloc

def memory_hungry():
    big_list = [i * 2 for i in range(100_000)]          # ← allocates a large list
    strings = [f"item_{i}" for i in range(50_000)]       # ← string allocations
    nested = [[j for j in range(10)] for _ in range(5_000)]  # ← nested list
    return big_list, strings, nested

tracemalloc.start()                                      # ← begin tracing allocations

memory_hungry()

snapshot = tracemalloc.take_snapshot()
top_stats = snapshot.statistics('lineno')                # ← group by source line

print("Top 3 memory consumers:")
for stat in top_stats[:3]:
    print(stat)
```

**Why:** `tracemalloc.start()` installs a trace hook into Python's memory allocator. Every `malloc` call from that point is tagged with the current source file and line number. `statistics('lineno')` groups and sums allocations by line, giving you a ranked view of where memory is going.

</details>

---

### Q4 🟡 · line_profiler — Add @profile decorator and run kernprof to find a slow line

> 🛠️ **Solve locally:** [practice_local.py → Q4](./practice_local.py)

Write a function `compute(n)` that has two steps: one fast (list comprehension) and one slow (a nested loop). Add the `@profile` decorator and show the `kernprof` command to run it. Identify which line dominates.

<details>
<summary>Hint</summary>

`@profile` is injected by `kernprof` at runtime — you do not import it. Run with `kernprof -l -v script.py`. The `% Time` column shows which line is the bottleneck.

</details>

<details>
<summary>Answer</summary>

```python
# save as profiling_example.py

@profile   # ← do NOT import; kernprof injects this decorator at runtime
def compute(n):
    fast_step = [i * 2 for i in range(n)]                # line A — fast
    slow_step = sum(i * j for i in range(n) for j in range(n // 10))  # line B — slow
    return fast_step, slow_step

compute(1000)
```

```bash
kernprof -l -v profiling_example.py
# -l  → write line-level stats to profiling_example.py.lprof
# -v  → immediately print the results to stdout
```

Output will show line B consuming 90%+ of `% Time`.

**Why:** `cProfile` only tells you *which function* is slow. `line_profiler` answers *which line inside that function*. It adds a timer around each bytecode instruction grouped by source line.

</details>

---

### Q5 🟡 · inspect — Use inspect.signature() to introspect a function's parameters

> 🛠️ **Solve locally:** [practice_local.py → Q5](./practice_local.py)

Given a function `create_user(name: str, age: int = 18, admin: bool = False)`, use `inspect.signature()` to loop over its parameters and print each parameter's name, default value, and type annotation.

<details>
<summary>Hint</summary>

`sig.parameters` is an `OrderedDict` of `{name: Parameter}`. Each `Parameter` has `.default` and `.annotation` attributes. A missing default is `inspect.Parameter.empty`.

</details>

<details>
<summary>Answer</summary>

```python
import inspect

def create_user(name: str, age: int = 18, admin: bool = False):
    pass

sig = inspect.signature(create_user)

for name, param in sig.parameters.items():
    default = param.default if param.default is not inspect.Parameter.empty else "REQUIRED"
    annotation = param.annotation.__name__ if param.annotation is not inspect.Parameter.empty else "none"
    print(f"  {name}: type={annotation}, default={default}")

# name:  type=str, default=REQUIRED
# age:   type=int, default=18
# admin: type=bool, default=False
```

**Why:** `inspect.signature()` is the standard way frameworks like FastAPI and pytest introspect function contracts at runtime — it powers automatic request validation, dependency injection, and test fixture resolution without any manual metadata.

</details>

---

### Q6 🟡 · inspect stack — Use inspect.stack() inside a function to print the call chain

> 🛠️ **Solve locally:** [practice_local.py → Q6](./practice_local.py)

Write a helper `who_called_me()` that uses `inspect.stack()` to print the full call chain — function name, filename, and line number — for every frame from the caller up to the top level.

<details>
<summary>Hint</summary>

`inspect.stack()` returns a list of `FrameInfo` objects. Index 0 is the current function. Each frame has `.function`, `.filename`, and `.lineno`. Skip frame 0 (the helper itself) and iterate the rest.

</details>

<details>
<summary>Answer</summary>

```python
import inspect

def who_called_me():
    stack = inspect.stack()
    print("Call chain (most recent first):")
    for i, frame in enumerate(stack[1:], start=1):       # ← skip frame 0 (who_called_me itself)
        print(f"  [{i}] {frame.function}  {frame.filename}:{frame.lineno}")

def inner():
    who_called_me()

def middle():
    inner()

def outer():
    middle()

outer()
# [1] inner      script.py:10
# [2] middle     script.py:13
# [3] outer      script.py:16
# [4] <module>   script.py:19
```

**Why:** `inspect.stack()` captures live frame objects from the interpreter's call stack. This is how logging frameworks, test reporters, and error trackers know where in your code a particular event originated.

</details>

---

### Q7 🟡 · loguru basics — Replace logging.basicConfig with loguru's one-liner setup

> 🛠️ **Solve locally:** [practice_local.py → Q7](./practice_local.py)

Rewrite this stdlib snippet using loguru — eliminate all setup boilerplate and demonstrate that loguru's default output includes timestamp, level, and location with zero configuration.

**Stdlib version to replace:**

```python
import logging
logging.basicConfig(
    level=logging.DEBUG,
    format='%(asctime)s - %(levelname)s - %(message)s'
)
log = logging.getLogger(__name__)
log.info("Service started")
log.warning("Disk usage at 85%")
log.error("Connection to DB lost")
```

<details>
<summary>Hint</summary>

`from loguru import logger` is the entire setup. The `logger` object is ready to use. loguru defaults to stderr with colors, timestamp, level, and `file:line` included automatically.

</details>

<details>
<summary>Answer</summary>

```python
from loguru import logger   # ← single import, zero configuration required

logger.info("Service started")
logger.warning("Disk usage at 85%")
logger.error("Connection to DB lost")
# Output (colored in terminal):
# 2026-05-07 14:23:01.412 | INFO     | __main__:<module>:3 - Service started
# 2026-05-07 14:23:01.413 | WARNING  | __main__:<module>:4 - Disk usage at 85%
# 2026-05-07 14:23:01.413 | ERROR    | __main__:<module>:5 - Connection to DB lost
```

**Why:** loguru ships with a pre-configured default sink (stderr) that includes everything you typically configure manually in stdlib: timestamp with milliseconds, level, file, function, and line number. You only call `logger.add()` when you need additional behavior like file rotation or JSON output.

</details>

---

### Q8 🟡 · loguru bind — Use logger.bind(request_id=...) to add context to every log line

> 🛠️ **Solve locally:** [practice_local.py → Q8](./practice_local.py)

Write a `handle_request(request_id, user_id)` function that creates a bound logger with `request_id` and `user_id` attached, then logs three events. Show that every line in the output carries both context values without repeating them manually.

<details>
<summary>Hint</summary>

`logger.bind(key=value)` returns a new logger object with those extra fields attached to every record it emits. The bound logger does not modify the global `logger`.

</details>

<details>
<summary>Answer</summary>

```python
from loguru import logger

# Add a format that shows the extra context fields
logger.add(
    lambda msg: print(msg, end=""),   # ← custom sink: print to stdout
    format="{time:HH:mm:ss} | {level} | req={extra[request_id]} user={extra[user_id]} | {message}",
    colorize=False,
)

def handle_request(request_id: str, user_id: int):
    req_log = logger.bind(request_id=request_id, user_id=user_id)  # ← context attached once

    req_log.info("Request received")          # ← request_id and user_id appear automatically
    req_log.info("Payload validated")
    req_log.error("Rate limit exceeded")

handle_request("REQ-001", 42)
# 14:05:11 | INFO  | req=REQ-001 user=42 | Request received
# 14:05:11 | INFO  | req=REQ-001 user=42 | Payload validated
# 14:05:11 | ERROR | req=REQ-001 user=42 | Rate limit exceeded
```

**Why:** `logger.bind()` implements the structured logging pattern — context is attached to the logger, not the message. This eliminates repetition and makes log parsing trivial because every line for a request carries identical, machine-readable identifiers.

</details>

---

### Q9 🟡 · async debug — Enable asyncio debug mode and catch a coroutine that never awaits

> 🛠️ **Solve locally:** [practice_local.py → Q9](./practice_local.py)

Write an async function `handle_signup(user_id)` that calls another coroutine but forgets the `await`. Enable asyncio debug mode and show that Python raises a `RuntimeWarning` for the unawaited coroutine.

<details>
<summary>Hint</summary>

Pass `debug=True` to `asyncio.run()`. Python's asyncio will detect that the coroutine object was created but never scheduled. You can also catch the warning with `warnings.filterwarnings("error")` to make it raise an exception.

</details>

<details>
<summary>Answer</summary>

```python
import asyncio
import warnings

warnings.filterwarnings("error")  # ← convert RuntimeWarning to a real exception for this demo

async def send_notification(user_id: int):
    await asyncio.sleep(0)   # ← simulates async work
    print(f"Notification sent to {user_id}")

async def handle_signup(user_id: int):
    print(f"Signup for user {user_id}")
    send_notification(user_id)   # ← BUG: missing await — coroutine created, never run
    # With debug=True + warnings as errors, this line raises RuntimeWarning

async def main():
    try:
        await handle_signup(99)
    except RuntimeWarning as e:
        print(f"Caught: {e}")
        # RuntimeWarning: coroutine 'send_notification' was never awaited

asyncio.run(main(), debug=True)   # ← debug=True activates unawaited coroutine detection
```

**Why:** Without debug mode, a forgotten `await` silently creates and immediately garbage-collects the coroutine — the work never runs and no error is raised. Debug mode installs a finalizer on every coroutine object that fires if it is collected without being awaited.

</details>

---

### Q10 🟠 · objgraph — Use objgraph.show_most_common_types() to find a memory leak

> 🛠️ **Solve locally:** [practice_local.py → Q10](./practice_local.py)

Simulate a memory leak by appending to a module-level list inside a loop. Use `objgraph.show_most_common_types()` before and after the loop to observe which type grows, then use `objgraph.show_growth()` to confirm the delta.

<details>
<summary>Hint</summary>

`objgraph.show_most_common_types(limit=5)` prints a sorted count of live objects by type. `objgraph.show_growth(limit=5)` compares to the count from the previous call and shows only types that grew.

</details>

<details>
<summary>Answer</summary>

```python
import objgraph

_leak_cache = []   # ← module-level list — simulates a global cache that grows forever

def leaky_process(data):
    _leak_cache.append({"processed": data, "extra": list(range(100))})  # ← never freed

print("=== Before leak ===")
objgraph.show_most_common_types(limit=5)   # ← baseline object counts

for i in range(500):
    leaky_process(f"item_{i}")

print("\n=== After leak ===")
objgraph.show_most_common_types(limit=5)   # ← dict and list counts have grown

print("\n=== Growth delta ===")
objgraph.show_growth(limit=5)
# dict  +500
# list  +500
```

**Why:** `objgraph` uses Python's `gc.get_objects()` to enumerate every live object in the interpreter's memory. By comparing counts before and after a suspected leak window, you can identify which type is accumulating — then use `objgraph.show_backrefs()` to trace who is holding the references.

</details>

---

### Q11 🟠 · debugpy — Configure debugpy to listen on port 5678 for VS Code attach

> 🛠️ **Solve locally:** [practice_local.py → Q11](./practice_local.py)

Write the debugpy setup block that: (1) reads an environment variable `ENABLE_DEBUGPY` to gate the debug listener, (2) listens on `0.0.0.0:5678`, and (3) waits for the debugger to attach before continuing. Also write the matching `.vscode/launch.json` attach configuration.

<details>
<summary>Hint</summary>

`debugpy.listen(("0.0.0.0", 5678))` starts the listener. `debugpy.wait_for_client()` blocks until VS Code connects. Always gate both calls behind an environment variable check.

</details>

<details>
<summary>Answer</summary>

```python
import os

# Gate behind environment variable — never enable unconditionally
if os.getenv("ENABLE_DEBUGPY") == "1":
    import debugpy
    debugpy.listen(("0.0.0.0", 5678))   # ← 0.0.0.0 accepts attach from any host
    print("debugpy: waiting for VS Code to attach on port 5678...")
    debugpy.wait_for_client()            # ← process PAUSES until debugger connects
    print("debugpy: attached. Resuming.")

# Normal application entry point continues here
def main():
    print("Application running")

main()
```

Matching `.vscode/launch.json`:

```json
{
    "version": "0.2.0",
    "configurations": [
        {
            "name": "Attach to Remote debugpy",
            "type": "debugpy",
            "request": "attach",
            "connect": {
                "host": "localhost",
                "port": 5678
            },
            "pathMappings": [
                {
                    "localRoot": "${workspaceFolder}",
                    "remoteRoot": "/app"
                }
            ]
        }
    ]
}
```

Run with:

```bash
ENABLE_DEBUGPY=1 python app.py
```

**Why:** `debugpy` implements the Debug Adapter Protocol (DAP) — the standard interface VS Code (and any DAP-compatible IDE) uses to communicate with language runtimes. `0.0.0.0` is required when the process runs inside a container, because `localhost` inside the container is not the same as `localhost` on your machine. The `pathMappings` entry reconciles your local file paths with the paths as they exist on the remote system.

</details>

---

### Q12 🟠 · Capstone — Profile a slow function, identify the hotspot, apply an optimization, and verify the improvement with a second profile run

> 🛠️ **Solve locally:** [practice_local.py → Q12](./practice_local.py)

You have a function `find_duplicates(items)` that finds duplicate values in a list using a naive O(n²) nested-loop approach. Complete all four steps:

1. Profile `find_duplicates` with `cProfile` and identify the bottleneck
2. Identify the root cause from the pstats output
3. Rewrite `find_duplicates_fast` using an O(n) set-based approach
4. Profile the fast version and print the cumtime improvement ratio

<details>
<summary>Hint</summary>

For step 4, capture cumtime for both versions using `pstats.Stats.stats` dict (keys are `(filename, lineno, funcname)`, values are `(cc, nc, tt, ct, callers)` — `ct` is cumtime). Or simply compare `pstats.print_stats(1)` output visually.

</details>

<details>
<summary>Answer</summary>

```python
import cProfile
import pstats
import io

# ── Step 1: The slow O(n²) version ──────────────────────────────────────────
def find_duplicates(items: list) -> set:
    """Naive: compare every element against every other element."""
    duplicates = set()
    for i in range(len(items)):
        for j in range(i + 1, len(items)):    # ← O(n²) — inner loop is the bottleneck
            if items[i] == items[j]:
                duplicates.add(items[i])
    return duplicates

# ── Step 2: Profile the slow version ────────────────────────────────────────
data = list(range(3000)) + list(range(500))   # ← 500 duplicates in 3500 items

slow_profiler = cProfile.Profile()
slow_profiler.enable()
result_slow = find_duplicates(data)
slow_profiler.disable()

slow_stream = io.StringIO()
slow_stats = pstats.Stats(slow_profiler, stream=slow_stream)
slow_stats.sort_stats('cumtime')
slow_stats.print_stats(3)
print("=== SLOW VERSION ===")
print(slow_stream.getvalue())

# ── Step 3: The fast O(n) version ───────────────────────────────────────────
def find_duplicates_fast(items: list) -> set:
    """O(n): single pass using a seen-set."""
    seen = set()
    duplicates = set()
    for item in items:                        # ← single loop — O(n)
        if item in seen:
            duplicates.add(item)
        else:
            seen.add(item)
    return duplicates

# ── Step 4: Profile the fast version and compare ────────────────────────────
fast_profiler = cProfile.Profile()
fast_profiler.enable()
result_fast = find_duplicates_fast(data)
fast_profiler.disable()

fast_stream = io.StringIO()
fast_stats = pstats.Stats(fast_profiler, stream=fast_stream)
fast_stats.sort_stats('cumtime')
fast_stats.print_stats(3)
print("=== FAST VERSION ===")
print(fast_stream.getvalue())

assert result_slow == result_fast, "Results must match!"  # ← correctness check
print(f"Both versions found {len(result_fast)} duplicates. Results match.")
```

**Why:** The O(n²) version runs `find_duplicates` in roughly 3000² / 2 = 4.5 million comparisons. The O(n) version runs in exactly 3500 operations — one hash lookup and one set insertion per element. The pstats `cumtime` output will show the fast version completing in a fraction of the time. This is the complete profiling workflow: measure → identify → optimize → verify.

</details>

---

## 🔁 Navigation

| | |
|---|---|
| ⬅️ Back to Module | [../theory.md](../theory.md) |
| 📖 Theory | [theory.md](./theory.md) |
| ⬅️ Prev Subfolder | [../01_pdb_debugging/practice.md](../01_pdb_debugging/practice.md) |

**Related:** [Logging Theory](../theory.md) · [pdb →](../01_pdb_debugging/theory.md)
