# 🐛 pdb_guide.md — The Python Debugger, From Zero to Expert

> A dedicated deep-dive into `pdb` — Python's built-in interactive debugger.
> No external tools required. Works anywhere Python runs.

---

## 🎬 Why Learn pdb?

> *It's 3 AM. Production is down. Your IDE isn't available because you're SSH'd into a container.*
> *You have one tool: Python itself. That tool is pdb.*

```python
# You can add this to ANY Python file, instantly:
breakpoint()   # execution pauses here. You get a live REPL inside the running program.
```

pdb lets you:
- Pause execution at any line
- Inspect any variable at any point in time
- Step line-by-line through code
- Navigate the call stack up and down
- Modify variables mid-execution
- Set conditional breakpoints
- Debug crashes after they happen (post-mortem)

---

## 🚀 Starting the Debugger

### Method 1: `breakpoint()` (Python 3.7+ — use this)

```python
def calculate_discount(price, user):
    breakpoint()   # ← execution pauses here
    discount = DISCOUNT_TABLE.get(user.tier, 0)
    return price * (1 - discount)
```

Run the script normally:
```bash
python myapp.py
```

Execution stops at the `breakpoint()` line and drops you into the pdb REPL:
```
> /path/to/myapp.py(47)calculate_discount()
-> discount = DISCOUNT_TABLE.get(user.tier, 0)
(Pdb)
```

### Method 2: `pdb.set_trace()` (classic, pre-3.7)

```python
import pdb
pdb.set_trace()   # same as breakpoint()
```

### Method 3: Run entire script under pdb

```bash
python -m pdb myapp.py
# Starts at first line of script
# Type 'c' to run to first breakpoint, or step immediately
```

### Method 4: Post-mortem — debug AFTER a crash

```python
import pdb

try:
    run_the_thing()
except Exception:
    pdb.post_mortem()   # drops into debugger at the EXACT crash frame
```

Or from the command line after a crash:
```bash
python -m pdb myapp.py
# If script crashes, pdb automatically enters post-mortem mode
```

Or in IPython / Jupyter:
```python
%debug   # enters post-mortem after the last exception
```

---

## 📋 Complete Command Reference

### Navigation

```
n    next        Execute current line, step OVER function calls
                 (goes to the next line in the current function)

s    step        Execute current line, step INTO function calls
                 (goes inside the function that is called)

r    return      Execute until current function RETURNS
                 (useful: you stepped into a function by mistake)

c    continue    Resume execution until next breakpoint

u    up          Move UP one frame in the call stack
                 (go to the caller of the current function)

d    down        Move DOWN one frame in the call stack
                 (go back into the called function)

q    quit        Exit the debugger immediately (raises BdbQuit)
```

**When to use n vs s:**
```
def outer():
    x = 1
    y = inner(x)    # ← you are paused HERE
    return y

(Pdb) n     → executes inner(x) and pauses on "return y"  (stepped OVER inner)
(Pdb) s     → enters inner() and pauses on its first line  (stepped INTO inner)
```

---

### Inspection

```
l    list        Show 11 lines of source code around current line
l .              Show lines around current line (re-center)
l 30             Show lines around line 30
l 30, 50         Show lines 30 to 50

p expr           Print the value of expression
                 (Pdb) p order_id   → 4892
                 (Pdb) p type(user) → <class 'User'>

pp expr          Pretty-print (readable format for dicts, lists, objects)
                 (Pdb) pp vars()    → all local variables, formatted

whatis expr      Print the type of expression
                 (Pdb) whatis user  → <class 'myapp.models.User'>

args             Show arguments of the current function
                 (Pdb) args → price = 99.0, user = <User id=1023>

w    where       Show the full call stack (where you are)
bt   backtrace   Alias for where
```

---

### Breakpoints

```
b    breakpoints         List all set breakpoints

b 47                     Set breakpoint at line 47 of current file
b mymodule.py:47         Set breakpoint at line 47 of mymodule.py
b process_payment        Set breakpoint at entry of function process_payment
b mymodule.process_payment  Set breakpoint in specific module

b 47, amount > 1000      Conditional breakpoint: only pause if amount > 1000
                         (Pdb) b 47, user.tier == "premium"

disable 1                Disable breakpoint #1 (number from 'b' list)
enable 1                 Re-enable breakpoint #1
cl   clear               Clear all breakpoints
cl 1                     Clear breakpoint #1
```

**Conditional breakpoints are powerful:**
```python
# Instead of this:
for i in range(100000):
    if i == 99999:
        breakpoint()   # tedious and fragile

# Set this from pdb:
(Pdb) b 47, i == 99999
Breakpoint 1 at myapp.py:47
(Pdb) c
# Runs to iteration 99999, then pauses
```

---

### Execution Control

```
unt  until [line]    Run until reaching a line number (useful to skip loops)
                     (Pdb) unt 60   → runs until line 60 is reached

j    jump [line]     Jump to a specific line (does NOT execute skipped lines!)
                     Use with caution — can cause inconsistent state

ret  return          Run until function returns (alias: r)

run  restart         Restart the program (when using python -m pdb)
```

---

### Modifying State

You can execute **any Python expression** at the pdb prompt:

```
(Pdb) order_id = 9999          ← modify a variable
(Pdb) user.tier = "premium"    ← modify an object attribute
(Pdb) import json              ← run imports
(Pdb) print(json.dumps(vars(user), default=str))   ← complex expressions

! prefix forces execution (when command conflicts with pdb command):
(Pdb) !n = 5    ← assigns to variable 'n' (without ! it would do 'next')
```

---

## 🏗️ Navigating the Call Stack

When a crash or interesting state is deep in a chain of calls, use `w` / `u` / `d`:

```python
# Call chain:
# handle_request()  →  process_order()  →  charge_card()  →  CRASH
```

```
(Pdb) w
  /app/api/routes.py(112)handle_request()
-> return process_order(data)
  /app/services/orders.py(88)process_order()
-> result = charge_card(order.total, order.card)
> /app/services/payments.py(23)charge_card()        ← current frame (>)
-> gateway.charge(amount, card_token)

(Pdb) u           ← go up to process_order
> /app/services/orders.py(88)process_order()
(Pdb) p order     ← inspect 'order' variable in THAT frame
<Order id=4892 total=99.0 status='pending'>

(Pdb) u           ← go up to handle_request
(Pdb) p data      ← inspect 'data' in handle_request frame
{'user_id': 1023, 'items': [...]}

(Pdb) d           ← go back down
```

This lets you inspect variables at **any level** of the call stack, not just the crash point.

---

## 🎯 Real Debugging Workflows

### Workflow 1: Find why a variable has the wrong value

```python
# Symptom: discount is always 0.0 for premium users
def apply_discount(order, user):
    breakpoint()
    tier_discount = DISCOUNTS.get(user.tier, 0.0)
    return order.total * (1 - tier_discount)
```

```
(Pdb) p user.tier     → 'Premium'    ← capital P!
(Pdb) p DISCOUNTS     → {'premium': 0.2, 'basic': 0.05}  ← lowercase key!
# Bug: case mismatch
```

### Workflow 2: Isolate which loop iteration fails

```python
def process_all(items):
    for i, item in enumerate(items):
        if i == 10:
            breakpoint()   # ← check state at iteration 10
        result = transform(item)
```

Better: set a conditional breakpoint from pdb:
```
(Pdb) b transform, item["status"] == "corrupted"
(Pdb) c   # runs until a corrupted item hits transform()
```

### Workflow 3: Post-mortem debugging a crash

```python
# Your script crashes with:
# KeyError: 'amount' in process_payment at line 47

import pdb

try:
    run_full_pipeline()
except Exception:
    pdb.post_mortem()
```

```
# Drops into the EXACT frame where the exception was raised:
> /app/payments.py(47)process_payment()
-> total = row["amount"]
(Pdb) pp row
{'transaction_id': 'abc123', 'AMOUNT': 99.0}   ← column is 'AMOUNT' not 'amount'!
```

### Workflow 4: Debug a test failure in pytest

```bash
# Run pytest, drop into pdb on first failure:
pytest --pdb

# Drop into pdb on first error (not assertion failure):
pytest --pdb --pdbcls=IPython.terminal.debugger:TerminalPdb

# Set breakpoint inside a test:
def test_payment():
    order = make_order()
    breakpoint()   # pdb activates here during test run
    result = process(order)
    assert result.status == "paid"
```

---

## 🔬 Advanced Techniques

### Watch expressions (simulate with commands)

pdb doesn't have native watchpoints, but you can simulate:
```python
# Add a property trap to an object:
class WatchedDict(dict):
    def __setitem__(self, key, value):
        if key == "status":
            import pdb; pdb.set_trace()   # pause when 'status' changes
        super().__setitem__(key, value)
```

### Timed breakpoints

```python
import time
START = time.time()

def slow_function():
    if time.time() - START > 5.0:   # only break if running > 5 seconds
        breakpoint()
    ...
```

### Remote debugging (SSH sessions)

```python
# In code running on a remote server:
import pdb
pdb.Pdb(stdout=open('/tmp/pdb.out', 'w')).set_trace()
# Then tail -f /tmp/pdb.out and send input via /tmp/pdb.in
```

Or use `rpdb` (pip install rpdb):
```python
import rpdb
rpdb.set_trace()   # listens on localhost:4444
# Connect: nc 127.0.0.1 4444
```

---

## 🔧 ipdb — Drop-in pdb Upgrade

```bash
pip install ipdb
```

```python
import ipdb
ipdb.set_trace()   # same as pdb but with:
                   # - syntax highlighting
                   # - tab completion
                   # - better output formatting
```

Set as default debugger for `breakpoint()`:
```bash
PYTHONBREAKPOINT=ipdb.set_trace python myapp.py
```

Or in your shell config:
```bash
export PYTHONBREAKPOINT=ipdb.set_trace
```

---

## 🏥 Debugging Without Stopping Execution

### `traceback` module — print stack without pausing

```python
import traceback

def suspicious_function():
    # Print where this function was called from, without stopping:
    traceback.print_stack()
    # → prints full call stack to stderr

    # Capture as string:
    stack = traceback.format_stack()
    logger.debug("Called from:\n%s", "".join(stack))
```

### `faulthandler` — debug deadlocks and segfaults

```python
import faulthandler
faulthandler.enable()   # call at startup — always

# If process hangs (deadlock):
# Send SIGABRT (kill -SIGABRT <pid>) → Python prints all thread stacks

# Force dump to file:
import signal
with open("fault.log", "w") as f:
    faulthandler.register(signal.SIGUSR1, file=f)
# Send SIGUSR1 → dumps stacks to fault.log without killing process
```

### `warnings` module — catch deprecations

```python
import warnings

# Treat all warnings as errors (catch them early):
warnings.filterwarnings("error")

# In tests (pytest):
# pytest -W error   ← all warnings become test failures
```

---

## 💾 Memory Debugging

```python
# pip install memory-profiler
from memory_profiler import profile

@profile
def load_large_file(path):
    with open(path) as f:
        data = f.read()   # ← see memory usage line-by-line
    return data

# Run: python -m memory_profiler myapp.py
# Output:
# Line  Mem usage    Increment   Line Contents
#   5   50.0 MiB    50.0 MiB    @profile
#   7   550.0 MiB  500.0 MiB    data = f.read()  ← 500MB spike!
```

```python
# pip install objgraph
import objgraph

# Find what's growing in memory:
objgraph.show_growth(limit=10)
# → [('MyClass', 50, +50), ('dict', 120, +30), ...]

# Show what holds a reference to an object:
objgraph.show_backrefs(suspicious_obj, max_depth=3)
```

---

## 🧵 Debugging Threads and Async

### Threads

```python
import threading

# Get all running threads:
for t in threading.enumerate():
    print(t.name, t.is_alive())

# In pdb, inspect thread state:
(Pdb) import threading; threading.enumerate()
```

### Async (asyncio)

```python
import asyncio

async def buggy_coroutine():
    breakpoint()   # ← works in async context too!
    await something()

# Run and inspect in pdb:
# (Pdb) p asyncio.all_tasks()   ← see all running tasks
# (Pdb) n   ← steps work differently in async (step to next await point)
```

### aiodbg for async post-mortem:
```bash
pip install aiodbg
```

---

## 🔁 pdb vs IDE Debugger

```
Feature                    pdb          IDE Debugger
──────────────────────────────────────────────────────
Available everywhere?      ✅ Yes       ❌ Needs IDE
Works over SSH?            ✅ Yes       ❌ Complex
GUI / visual stack?        ❌ No        ✅ Yes
Watch expressions?         ❌ Manual    ✅ Native
Conditional breakpoints?   ✅ Yes       ✅ Yes
Tab completion?            ❌ (use ipdb) ✅ Yes
Production debugging?      ✅ Yes       ❌ Not feasible
Speed?                     Fast         Slower
Learning curve?            Medium       Low
```

> **Rule of thumb:** Use your IDE debugger day-to-day. Learn pdb for emergencies, remote servers, containers, and CI environments where an IDE is unavailable.

---

## ⚡ .pdbrc — Configure pdb at Startup

Create `~/.pdbrc` for global settings, or `.pdbrc` in your project root:

```
# ~/.pdbrc

# Always show source when pausing:
alias ll l 1, 999

# Pretty-print locals on every pause:
alias pl pp locals()

# Show args and locals:
alias context args;; pp locals()

# Shorter where:
alias ww w
```

---

## 🔥 Rapid-Fire Revision

```
Q: What is the difference between n and s?
A: n (next) = step OVER function calls — stays in current function
   s (step) = step INTO function calls — enters the called function

Q: What is post-mortem debugging?
A: Debugging a program AFTER it has already crashed.
   import pdb; pdb.post_mortem()  inside except block
   Drops into pdb at the exact frame where the exception was raised.

Q: How do you see all local variables?
A: (Pdb) pp vars()   or  (Pdb) pp locals()

Q: How do you set a conditional breakpoint?
A: (Pdb) b 47, amount > 1000
   Pauses only when the condition is true.

Q: How do you go up the call stack to inspect a caller's variables?
A: (Pdb) u  (up)   then  (Pdb) p variable_name

Q: How do you modify a variable from pdb?
A: Just assign: (Pdb) order_id = 9999
   If the variable name conflicts with a pdb command, prefix with !:
   (Pdb) !n = 5   (instead of 'next')

Q: What does PYTHONBREAKPOINT do?
A: Controls what breakpoint() calls. Set to empty string to disable all
   breakpoints: PYTHONBREAKPOINT="" python myapp.py (useful in CI)
   Set to "ipdb.set_trace" to use ipdb automatically.

Q: How do you debug with pytest?
A: pytest --pdb    ← drops into pdb on first test failure

Q: What is faulthandler?
A: Prints Python traceback on fatal errors (segfault, SIGABRT, deadlock).
   Enable at startup: import faulthandler; faulthandler.enable()
```

---

## 🔁 Navigation

| | |
|---|---|
| 📖 Theory | [theory.md](./theory.md) |
| 🎯 Interview | [interview.md](./interview.md) |
| ⚡ Cheatsheet | [cheatsheet.md](./cheatsheet.md) |
| ➡️ Next | [10 — Decorators](../10_decorators/theory.md) |

---

**[🏠 Back to README](../README.md)**

**Prev:** [← Cheat Sheet](./cheatsheet.md) &nbsp;|&nbsp; **Next:** [Interview Q&A →](./interview.md)

**Related Topics:** [Theory](./theory.md) · [Cheat Sheet](./cheatsheet.md) · [Interview Q&A](./interview.md)
