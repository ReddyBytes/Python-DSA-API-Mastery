# 🐛 pdb — Python's Built-in Debugger

Think of pdb as a time-freeze button you can drop anywhere in running code — it halts execution and hands you a live REPL inside the program so you can look around before anything crashes. The key fact: it ships with Python and works anywhere Python runs, including SSH sessions, containers, and CI environments where an IDE is unavailable.

## 📌 Learning Priority

**Must Learn** — breakpoint(), n/s/c/q/p commands, where/up/down
**Should Learn** — Conditional breakpoints, post-mortem, .pdbrc config
**Good to Know** — ipdb, remote debugging with debugpy, watch expressions
**Reference** — faulthandler, timed breakpoints, rpdb

---

## 1. Starting the Debugger

Imagine a surgeon who can pause a patient's heart mid-operation to inspect tissue. Each entry method is a different way to perform that freeze — some planned ahead of time, others triggered by an emergency after the fact.

### Method 1: `breakpoint()` — Python 3.7+ (use this)

**`breakpoint()`** is a built-in that pauses execution and opens the pdb REPL at that exact line. It replaced the older `pdb.set_trace()` pattern and is the standard today.

```python
def calculate_discount(price, user):
    breakpoint()   # ← execution freezes here; pdb REPL opens
    discount = DISCOUNT_TABLE.get(user.tier, 0)
    return price * (1 - discount)
```

Run the script normally and pdb takes over:

```bash
python myapp.py
```

```
> /path/to/myapp.py(47)calculate_discount()
-> discount = DISCOUNT_TABLE.get(user.tier, 0)
(Pdb)
```

The `->` arrow shows the line that is *about to execute*. You are paused before it runs.

### Method 2: `pdb.set_trace()` — classic, pre-3.7

```python
import pdb
pdb.set_trace()   # identical behavior to breakpoint()
```

Prefer `breakpoint()` in modern code, but you will see `set_trace()` in older codebases.

### Method 3: Run an entire script under pdb

```bash
python -m pdb myapp.py
# Starts paused at the first line of the script
# Type 'c' to run to the first breakpoint, or step immediately with 'n'
```

This is the right method when you do not want to modify the source file, or when the crash happens early in startup.

### Method 4: Post-mortem — debug AFTER a crash

**Post-mortem debugging** drops you into pdb at the exact frame where an exception was raised, after execution has already stopped.

```python
import pdb

try:
    run_the_thing()
except Exception:
    pdb.post_mortem()   # ← pdb opens at the crash site
```

From the command line, if a script crashes while running under `python -m pdb`, pdb enters post-mortem mode automatically.

In IPython or Jupyter:

```python
%debug   # enters post-mortem after the last unhandled exception
```

---

## 2. Core Commands

The pdb REPL is like the dashboard of a submarine — each button does one specific thing, and knowing them cold is what separates a calm debugging session from a frantic one. There are three groups: navigation (where to go next), inspection (what is the current state), and breakpoint management (where to stop next time).

### Navigation commands

```
n    next        Execute the current line, step OVER function calls
                 Stays in the current function — does not enter callees

s    step        Execute the current line, step INTO function calls
                 Enters the body of whatever function is being called

r    return      Run until the current function returns
                 Useful when you accidentally stepped into a function you do not need

c    continue    Resume execution until the next breakpoint

q    quit        Exit the debugger immediately (raises BdbQuit)
```

**`n` vs `s` — the most important distinction:**

```
def outer():
    x = 1
    y = inner(x)    # ← paused on this line
    return y

(Pdb) n     # executes inner(x), pauses on "return y"    → stepped OVER inner
(Pdb) s     # enters inner() and pauses at its first line → stepped INTO inner
```

### Inspection commands

```
l    list        Show 11 lines of source code around the current line
l .              Re-center the listing on the current line
l 30             Show lines around line 30
l 30, 50         Show lines 30 through 50

p expr           Print the value of any expression
                 (Pdb) p order_id        → 4892
                 (Pdb) p type(user)      → <class 'User'>

pp expr          Pretty-print — readable format for dicts, lists, objects
                 (Pdb) pp vars()         → all local variables, formatted

whatis expr      Print the type of an expression
                 (Pdb) whatis user       → <class 'myapp.models.User'>

args             Show all arguments passed to the current function
                 (Pdb) args → price = 99.0, user = <User id=1023>

w    where       Show the full call stack — where you are in the execution chain
bt   backtrace   Alias for where
```

### Breakpoint management

```
b                        List all currently set breakpoints

b 47                     Set a breakpoint at line 47 of the current file
b mymodule.py:47         Set a breakpoint at line 47 of a specific file
b process_payment        Set a breakpoint at the entry of a named function

b 47, amount > 1000      Conditional breakpoint — only pauses when condition is True
                         (Pdb) b 47, user.tier == "premium"

disable 1                Disable breakpoint #1 without deleting it
enable 1                 Re-enable breakpoint #1
cl   clear               Clear all breakpoints
cl 1                     Clear breakpoint #1 by number
```

**Why conditional breakpoints matter:**

```python
# Without them, you write fragile inline guards:
for i in range(100000):
    if i == 99999:
        breakpoint()   # tedious and must be removed before commit

# With a conditional breakpoint set from pdb:
(Pdb) b 47, i == 99999
Breakpoint 1 at myapp.py:47
(Pdb) c
# Runs 99,999 iterations silently, then pauses exactly when needed
```

### Execution control

```
unt  until [line]    Run until a specific line number is reached
                     (Pdb) unt 60  → runs forward until line 60, skipping loops

j    jump [line]     Jump directly to a line without executing skipped lines
                     Use with caution — can leave state inconsistent
```

### Modifying state mid-session

You can execute any Python expression at the `(Pdb)` prompt:

```python
(Pdb) order_id = 9999           # reassign a variable
(Pdb) user.tier = "premium"     # mutate an object attribute
(Pdb) import json               # run an import
(Pdb) print(json.dumps(vars(user), default=str))   # run complex expressions

# If your variable name conflicts with a pdb command, prefix with !:
(Pdb) !n = 5    # assigns 5 to variable 'n' — without ! this would run 'next'
```

---

## 3. Navigating the Call Stack

When a crash happens deep inside a chain of function calls, the default view only shows you the bottom of that chain. Using `w` / `u` / `d` lets you travel up and down through all the frames to inspect variables at any level — like rewinding a film frame by frame.

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
> /app/services/payments.py(23)charge_card()    # ← current frame, marked with >
-> gateway.charge(amount, card_token)

(Pdb) u                   # move up to process_order frame
> /app/services/orders.py(88)process_order()
(Pdb) p order             # inspect 'order' in THAT frame — not charge_card's frame
<Order id=4892 total=99.0 status='pending'>

(Pdb) u                   # move up again to handle_request frame
(Pdb) p data              # inspect 'data' in handle_request
{'user_id': 1023, 'items': [...]}

(Pdb) d                   # move back down one frame
```

The `>` marker in `w` output always shows your current frame. `u` moves toward the top (the caller), `d` moves back toward the bottom (the callee).

---

## 4. Real Debugging Workflows

Debugging without a plan is like searching a dark house without a flashlight. These four workflows are the flashlights — each one matches a class of bug you will encounter repeatedly in production Python.

### Workflow 1: Find why a variable has the wrong value

```python
# Symptom: discount is always 0.0, even for premium users
def apply_discount(order, user):
    breakpoint()
    tier_discount = DISCOUNTS.get(user.tier, 0.0)
    return order.total * (1 - tier_discount)
```

```
(Pdb) p user.tier       → 'Premium'                           # capital P
(Pdb) p DISCOUNTS       → {'premium': 0.2, 'basic': 0.05}    # lowercase key
# Root cause: case mismatch — 'Premium' != 'premium'
```

### Workflow 2: Isolate which loop iteration fails

Instead of adding `if i == 10: breakpoint()` inline, set a conditional breakpoint from pdb so source code stays clean:

```python
def process_all(items):
    for i, item in enumerate(items):
        result = transform(item)   # crashes on one item
```

```
(Pdb) b transform, item["status"] == "corrupted"
(Pdb) c   # runs silently until a corrupted item reaches transform()
```

### Workflow 3: Post-mortem debugging a crash

```python
# Script crashes with: KeyError: 'amount' in process_payment at line 47

import pdb

try:
    run_full_pipeline()
except Exception:
    pdb.post_mortem()
```

```
# pdb opens at the exact crash frame:
> /app/payments.py(47)process_payment()
-> total = row["amount"]
(Pdb) pp row
{'transaction_id': 'abc123', 'AMOUNT': 99.0}   # key is 'AMOUNT', not 'amount'
```

### Workflow 4: Debug a test failure in pytest

```bash
# Drop into pdb on first test failure:
pytest --pdb

# Or place a breakpoint directly inside a test:
def test_payment():
    order = make_order()
    breakpoint()   # pdb activates here during the test run
    result = process(order)
    assert result.status == "paid"
```

---

## 5. Advanced Techniques

Once you know the basics, these techniques cover the situations that the basics cannot handle: bugs that only surface after many iterations, crashes in remote servers, and state mutations that are hard to trace.

### Conditional breakpoints (already covered in commands — advanced pattern)

```python
# Stop only after 5 loop iterations using a closure counter trick:
count = [0]

def should_break():
    count[0] += 1
    return count[0] > 5

(Pdb) b 47, should_break()   # ← calls your function as the condition
```

### Post-mortem with `pdb.pm()`

**`pdb.pm()`** is a convenience alias for `pdb.post_mortem(sys.last_traceback)`. Call it interactively after a crash in a Python shell:

```python
>>> run_thing()
Traceback (most recent call last):
  ...
KeyError: 'amount'
>>> import pdb; pdb.pm()   # drops into pdb at the crash frame immediately
```

### Simulating watch expressions

pdb has no native watchpoints. The standard workaround is a custom subclass:

```python
class WatchedDict(dict):
    def __setitem__(self, key, value):
        if key == "status":
            import pdb; pdb.set_trace()   # pause every time 'status' is written
        super().__setitem__(key, value)
```

### Timed breakpoints

```python
import time
START = time.time()

def slow_function():
    if time.time() - START > 5.0:   # ← only break if the function has been running > 5s
        breakpoint()
    ...
```

### Remote debugging with rpdb

```bash
pip install rpdb
```

```python
import rpdb
rpdb.set_trace()   # listens on localhost:4444
# Connect from another terminal: nc 127.0.0.1 4444
```

### ipdb — drop-in upgrade with syntax highlighting

```bash
pip install ipdb
```

```python
import ipdb
ipdb.set_trace()   # same as pdb.set_trace() but adds:
                   # - syntax highlighting
                   # - tab completion
                   # - better output formatting
```

Make ipdb the default backend for `breakpoint()`:

```bash
PYTHONBREAKPOINT=ipdb.set_trace python myapp.py
# Or permanently in your shell config:
export PYTHONBREAKPOINT=ipdb.set_trace
```

Disable all breakpoints in CI without touching source code:

```bash
PYTHONBREAKPOINT="" python myapp.py   # ← breakpoint() becomes a no-op
```

---

## 6. .pdbrc Configuration

`.pdbrc` is a startup script for pdb — it runs automatically every time you enter a pdb session, before you type your first command. Think of it as a `.bashrc` for your debugger: a place to define shortcuts, aliases, and default behaviors so you are never starting from zero.

Create `~/.pdbrc` for global settings that apply in every project, or `.pdbrc` in your project root for project-specific config.

```
# ~/.pdbrc

# Show the full source listing when pausing:
alias ll l 1, 999

# Pretty-print all local variables in one command:
alias pl pp locals()

# Show function arguments and all locals together:
alias context args;; pp locals()

# Shorter alias for 'where':
alias ww w
```

Usage — once defined, these aliases work exactly like built-in commands:

```
(Pdb) pl       # runs pp locals()
(Pdb) context  # runs args then pp locals()
(Pdb) ll       # shows full file listing
```

---

## 🔁 Navigation

| | |
|---|---|
| ⬅️ Back to Module | [../theory.md](../theory.md) |
| 💻 Practice | [practice.md](./practice.md) |
| ➡️ Next Subfolder | [../02_profiling_advanced/theory.md](../02_profiling_advanced/theory.md) |

**Related:** [Logging Theory](../theory.md) · [Profiling & Advanced →](../02_profiling_advanced/theory.md)
