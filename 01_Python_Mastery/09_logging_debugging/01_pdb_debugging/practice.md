# 💻 Practice — 01_pdb_debugging


---

## Quick Index

| # | Difficulty | Topic | Title |
|---|---|---|---|
| [Q1](#q1) | 🟢 | entry points | Insert breakpoint() to pause before a crash |
| [Q2](#q2) | 🟢 | core commands | Use p/pp/l/n/s/c in sequence to trace a bug |
| [Q3](#q3) | 🟢 | navigation | Use w/u/d to inspect call stack frames |
| [Q4](#q4) | 🟡 | breakpoints | Set a conditional breakpoint: only stop when x > 100 |
| [Q5](#q5) | 🟡 | post-mortem | Run pdb.pm() on a script that raises an unhandled exception |
| [Q6](#q6) | 🟡 | inspect locals | Use locals() and pp to pretty-print all frame variables |
| [Q7](#q7) | 🟡 | expression eval | Use ! to change a variable's value mid-session |
| [Q8](#q8) | 🟡 | .pdbrc | Write a .pdbrc that aliases ll and pp |
| [Q9](#q9) | 🟡 | debug from CLI | Launch pdb from the command line with python -m pdb |
| [Q10](#q10) | 🟠 | timed breakpoint | Use a breakpoint condition to only trigger after 5 iterations |
| [Q11](#q11) | 🟠 | ipdb | Replace pdb with ipdb for tab completion and syntax highlighting |
| [Q12](#q12) | 🟠 | Capstone | Debug a recursive function hitting max depth with pdb |

---

<a id="q1"></a>

### Q1 🟢 · entry points — Insert breakpoint() to pause before a crash

> 🛠️ **Solve locally:** [practice_local.py → Q1](./practice_local.py)



You have a function that raises a `KeyError`. Insert a `breakpoint()` call on the line immediately before the crash so you can inspect the local variables before the exception occurs.

```python
def load_config(data):
    name = data["name"]       # KeyError when key is missing
    return name.upper()

load_config({"Name": "alice"})   # wrong key — capital N
```

**What to observe:** once paused at `(Pdb)`, run `p data` to see the actual keys in the dict.

<details>
<summary>Hint</summary>

Place `breakpoint()` on the line directly before the crash line. At the pdb prompt, use `p data` to inspect the dictionary. You will see `{'Name': 'alice'}` — the key is `'Name'`, not `'name'`.

</details>

<details>
<summary>Answer</summary>

```python
def load_config(data):
    breakpoint()              # ← execution pauses here
    name = data["name"]
    return name.upper()

load_config({"Name": "alice"})
```

At the `(Pdb)` prompt:

```
(Pdb) p data
{'Name': 'alice'}
```

**Why:** `breakpoint()` is equivalent to `import pdb; pdb.set_trace()`. It pauses execution before the crash line, giving you a live REPL to inspect all variables in scope. Here you can see the key is `'Name'`, not `'name'` — a case mismatch.

</details>

---

<a id="q2"></a>

### Q2 🟢 · core commands — Use p/pp/l/n/s/c in sequence to trace a bug

> 🛠️ **Solve locally:** [practice_local.py → Q2](./practice_local.py)



Place a `breakpoint()` inside `apply_multiplier` below. Then step through it using these commands in sequence: `l` (list source), `p multiplier` (inspect variable), `n` (next line), `pp vars()` (print all locals), `c` (continue).

```python
MULTIPLIERS = {"gold": 3, "silver": 2, "bronze": 1}

def apply_multiplier(value, tier):
    multiplier = MULTIPLIERS.get(tier, 0)
    result = value * multiplier
    return result

print(apply_multiplier(100, "Gold"))   # returns 0 — wrong tier casing
```

<details>
<summary>Hint</summary>

After `breakpoint()`, use `l` to see source context, `p tier` to see the tier value passed in, then `p MULTIPLIERS` to see the dict keys. You will spot the case mismatch immediately.

</details>

<details>
<summary>Answer</summary>

```python
def apply_multiplier(value, tier):
    breakpoint()
    multiplier = MULTIPLIERS.get(tier, 0)
    result = value * multiplier
    return result
```

Session:

```
(Pdb) l          # shows surrounding source code
(Pdb) p tier     → 'Gold'
(Pdb) p MULTIPLIERS  → {'gold': 3, 'silver': 2, 'bronze': 1}
(Pdb) n          # steps to next line
(Pdb) p multiplier   → 0    ← confirms the bug
(Pdb) pp vars()  # shows all local variables
(Pdb) c          # continues execution
```

**Why:** `l` gives you context so you know what code you are in. `p` lets you inspect individual values. `n` advances one line at a time. `pp vars()` dumps all locals at once. `c` resumes so the program finishes running.

</details>

---

<a id="q3"></a>

### Q3 🟢 · navigation — Use w/u/d to inspect call stack frames

> 🛠️ **Solve locally:** [practice_local.py → Q3](./practice_local.py)



Given this call chain, place a `breakpoint()` inside `inner()`. Once paused, use `w` to view the full stack, `u` to go up to `middle()`'s frame, inspect `step` there, then `u` again to reach `outer()`'s frame and inspect `initial`.

```python
def outer():
    initial = 42
    return middle(initial)

def middle(step):
    doubled = step * 2
    return inner(doubled)

def inner(value):
    breakpoint()
    return value + 1
```

<details>
<summary>Hint</summary>

`w` prints the full stack — the `>` marks your current frame. `u` moves up one frame toward the caller. `p step` at the middle frame and `p initial` at the outer frame should both work after navigating.

</details>

<details>
<summary>Answer</summary>

```
(Pdb) w
  script.py(2)outer()
-> return middle(initial)
  script.py(6)middle()
-> return inner(doubled)
> script.py(10)inner()         ← current frame
-> return value + 1

(Pdb) u                        # go up to middle()
(Pdb) p step                   → 42
(Pdb) p doubled                → 84
(Pdb) u                        # go up to outer()
(Pdb) p initial                → 42
(Pdb) d                        # go back down to inner()
```

**Why:** `w` (where) shows the full call stack. `u` and `d` let you move between frames and inspect variables that belong to each frame — not just the current one. This is essential for tracing how data changes as it passes through a call chain.

</details>

---

<a id="q4"></a>

### Q4 🟡 · breakpoints — Set a conditional breakpoint: only stop when x > 100

> 🛠️ **Solve locally:** [practice_local.py → Q4](./practice_local.py)



You have a loop that runs 200 iterations. You only want pdb to pause when `x` exceeds 100. Set a conditional breakpoint from the pdb prompt using `b`, not an inline `if/breakpoint()` guard.

```python
def process_values():
    for x in range(200):
        result = x * x
    return result

process_values()
```

<details>
<summary>Hint</summary>

Start the script with `python -m pdb script.py`. Once at the pdb prompt on the first line, use `b <line_number>, x > 100` where the line number is the `result = x * x` line. Then `c` to continue.

</details>

<details>
<summary>Answer</summary>

```
$ python -m pdb script.py
(Pdb) b 3, x > 100
Breakpoint 1 at script.py:3
(Pdb) c
> script.py(3)process_values()
-> result = x * x
(Pdb) p x
101
```

Alternatively with an inline `breakpoint()` and condition flag:

```python
def process_values():
    for x in range(200):
        result = x * x
        if x > 100:
            breakpoint()   # inline guard — less clean but works
    return result
```

**Why:** Conditional breakpoints (`b line, condition`) keep your source code clean. The condition is evaluated at that line on every pass — pdb only pauses when it is `True`. This avoids inserting temporary guards that must be cleaned up before commit.

</details>

---

<a id="q5"></a>

### Q5 🟡 · post-mortem — Run pdb.pm() on a script that raises an unhandled exception

> 🛠️ **Solve locally:** [practice_local.py → Q5](./practice_local.py)



Wrap the call below in a `try/except` block and call `pdb.post_mortem()` in the `except` clause. Observe that pdb opens at the exact frame where the exception was raised.

```python
def parse_record(record):
    return record["id"] * record["value"]

parse_record({"id": 10})   # missing 'value' key — raises KeyError
```

<details>
<summary>Hint</summary>

Import `pdb` at the top. Wrap the call in `try/except Exception`. In the `except` block, call `pdb.post_mortem()`. You do not need to pass any arguments — it uses the current exception automatically.

</details>

<details>
<summary>Answer</summary>

```python
import pdb

def parse_record(record):
    return record["id"] * record["value"]

try:
    parse_record({"id": 10})
except Exception:
    pdb.post_mortem()   # opens pdb at the line that raised the KeyError
```

At the pdb prompt:

```
> script.py(4)parse_record()
-> return record["id"] * record["value"]
(Pdb) pp record
{'id': 10}
# 'value' key is missing — confirmed
```

**Why:** `pdb.post_mortem()` is the right tool when you cannot or do not want to add `breakpoint()` before a crash. It drops you into the exact frame where the exception occurred, with all local variables intact for inspection.

</details>

---

<a id="q6"></a>

### Q6 🟡 · inspect locals — Use locals() and pp to pretty-print all frame variables

> 🛠️ **Solve locally:** [practice_local.py → Q6](./practice_local.py)



Inside a pdb session, use `pp locals()` to dump all local variables at once. Then use `pp vars()` and compare output. Also try `args` to see only the function's arguments.

```python
def compute_summary(items, threshold, label):
    total = sum(items)
    above = [i for i in items if i > threshold]
    ratio = len(above) / len(items)
    breakpoint()
    return {"label": label, "total": total, "ratio": ratio}

compute_summary([10, 50, 80, 120, 200], 75, "high_value")
```

<details>
<summary>Hint</summary>

At `(Pdb)`, run `pp locals()` first. Then run `pp vars()` — you will see they produce the same output inside a function. Then run `args` to see only the parameters that were passed in.

</details>

<details>
<summary>Answer</summary>

```
(Pdb) pp locals()
{'above': [80, 120, 200],
 'items': [10, 50, 80, 120, 200],
 'label': 'high_value',
 'ratio': 0.6,
 'threshold': 75,
 'total': 460}

(Pdb) args
items = [10, 50, 80, 120, 200]
threshold = 75
label = 'high_value'
```

**Why:** `pp locals()` and `pp vars()` both dump all variables in the current frame. `args` is narrower — it shows only what was passed into the current function. Use `args` first for a quick sanity check on inputs, then `pp locals()` to see how state has evolved since the function started.

</details>

---

<a id="q7"></a>

### Q7 🟡 · expression eval — Use ! to change a variable's value mid-session

> 🛠️ **Solve locally:** [practice_local.py → Q7](./practice_local.py)



Inside a pdb session, modify a variable to test whether your fix would work — without actually editing source code. Use `!` prefix for variable names that clash with pdb commands.

```python
def apply_tier_price(price, tier):
    breakpoint()
    discount = {"gold": 0.3, "silver": 0.1}.get(tier, 0)
    final = price * (1 - discount)
    return final

result = apply_tier_price(100, "bronze")
print(result)   # prints 100 — no discount applied
```

<details>
<summary>Hint</summary>

At `(Pdb)`, assign `tier = "gold"` and then `n` to step to the next line. Check `p discount` to confirm the new value is used. Try `!n = 5` to see how `!` avoids conflicts with the `n` (next) command.

</details>

<details>
<summary>Answer</summary>

```
(Pdb) tier = "gold"      # reassign — no ! needed, 'tier' is not a pdb command
(Pdb) n                  # step: discount = {"gold": 0.3, ...}.get("gold", 0)
(Pdb) p discount         → 0.3
(Pdb) n
(Pdb) p final            → 70.0   ← confirms the fix works

# For names that conflict with pdb commands:
(Pdb) !n = 5             # assigns 5 to variable 'n' without triggering 'next'
```

**Why:** Any expression typed at the `(Pdb)` prompt is executed in the current frame's scope. This lets you test a fix immediately — change a variable, step through the remaining lines, and verify the outcome — all before touching source code. The `!` prefix is needed only when a variable name shadows a pdb command.

</details>

---

<a id="q8"></a>

### Q8 🟡 · .pdbrc — Write a .pdbrc that aliases ll to longlist and pp to pretty-print locals

> 🛠️ **Solve locally:** [practice_local.py → Q8](./practice_local.py)



Write the contents of a `.pdbrc` file that defines two aliases: `ll` as a shortcut to show the full file listing, and `pl` as a shortcut to pretty-print all local variables.

<details>
<summary>Hint</summary>

The `.pdbrc` file uses pdb's `alias` command. The syntax is `alias <shortname> <command>`. Place the file at `~/.pdbrc` for global use or in your project root for local use.

</details>

<details>
<summary>Answer</summary>

```
# ~/.pdbrc  (or .pdbrc in project root)

# Show full file listing from line 1 to 999:
alias ll l 1, 999

# Pretty-print all local variables:
alias pl pp locals()

# Show arguments + all locals together:
alias context args;; pp locals()
```

Usage at the `(Pdb)` prompt:

```
(Pdb) ll       # runs: l 1, 999
(Pdb) pl       # runs: pp locals()
(Pdb) context  # runs: args then pp locals()
```

**Why:** `.pdbrc` runs automatically at the start of every pdb session. Defining aliases there means you never have to type repetitive commands. The `;;` separator chains multiple commands on one alias line.

</details>

---

<a id="q9"></a>

### Q9 🟡 · debug from CLI — Launch pdb from the command line with python -m pdb script.py

> 🛠️ **Solve locally:** [practice_local.py → Q9](./practice_local.py)



Describe the exact shell command to launch a script named `worker.py` under pdb. Then list: what command runs it to the first breakpoint, what happens if the script crashes, and how to restart the script without leaving pdb.

<details>
<summary>Hint</summary>

The launch command is `python -m pdb worker.py`. The command to run to the first breakpoint is `c`. A crash triggers automatic post-mortem. The restart command is `run` (or `restart`).

</details>

<details>
<summary>Answer</summary>

```bash
python -m pdb worker.py
```

Once at the pdb prompt:

```
(Pdb) c          # continue to first breakpoint (or end of script)

# If script raises an unhandled exception:
# pdb automatically enters post-mortem at the crash frame

(Pdb) run        # restart the script from the beginning without quitting pdb
# alias: restart
```

**Why:** `python -m pdb script.py` is the right approach when you cannot modify the source file to add `breakpoint()`, or when you want to set breakpoints from pdb before the script starts running. It always pauses at the very first line, giving you full control from the beginning.

</details>

---

<a id="q10"></a>

### Q10 🟠 · timed breakpoint — Use a breakpoint condition to only trigger after 5 loop iterations

> 🛠️ **Solve locally:** [practice_local.py → Q10](./practice_local.py)



Write a loop that runs 20 iterations. Use a counter-based condition so `breakpoint()` only fires after the 5th iteration. Do not use `if i == 5: breakpoint()` inline — implement it using a mutable counter or a conditional breakpoint set from pdb.

<details>
<summary>Hint</summary>

Option 1: use a list as a mutable counter `[0]` in a helper function. Option 2: set `b <line>, i >= 5` from the pdb prompt when running under `python -m pdb`.

</details>

<details>
<summary>Answer</summary>

**Option A — helper function with mutable state:**

```python
_count = [0]

def should_break():
    _count[0] += 1
    return _count[0] > 5   # fires on iteration 6+

def run_loop():
    for i in range(20):
        value = i * i
        if should_break():
            breakpoint()
        print(value)

run_loop()
```

**Option B — conditional breakpoint from pdb:**

```bash
python -m pdb script.py
(Pdb) b 4, i >= 5    # line 4 is "value = i * i"
(Pdb) c              # runs silently until i == 5
```

**Why:** A plain `if i == 5: breakpoint()` works but leaves debug code in the source. A helper function with a mutable counter encapsulates the logic and is easier to remove. The pdb conditional approach is cleanest — zero source modification.

</details>

---

<a id="q11"></a>

### Q11 🟠 · ipdb — Replace pdb with ipdb for tab completion and syntax highlighting

> 🛠️ **Solve locally:** [practice_local.py → Q11](./practice_local.py)



Show two ways to use `ipdb` instead of `pdb`: direct import, and the `PYTHONBREAKPOINT` environment variable. Then show how to disable all breakpoints in a CI environment without changing source code.

<details>
<summary>Hint</summary>

`import ipdb; ipdb.set_trace()` is the direct method. `PYTHONBREAKPOINT=ipdb.set_trace` makes `breakpoint()` route to ipdb. `PYTHONBREAKPOINT=""` disables breakpoints entirely.

</details>

<details>
<summary>Answer</summary>

**Direct import:**

```python
import ipdb
ipdb.set_trace()   # same interface as pdb, adds syntax highlighting + tab completion
```

**Via PYTHONBREAKPOINT (no source changes needed):**

```bash
# One-off run using ipdb:
PYTHONBREAKPOINT=ipdb.set_trace python myapp.py

# Persistent — add to ~/.zshrc or ~/.bashrc:
export PYTHONBREAKPOINT=ipdb.set_trace
```

**Disable all breakpoints in CI:**

```bash
PYTHONBREAKPOINT="" python myapp.py   # breakpoint() becomes a no-op
```

```yaml
# In a GitHub Actions workflow:
env:
  PYTHONBREAKPOINT: ""
```

**Why:** `PYTHONBREAKPOINT` is the cleanest way to control pdb behavior without touching source files. In development, point it to `ipdb.set_trace` for a better interactive experience. In CI/CD pipelines, set it to empty string so any forgotten `breakpoint()` calls do not hang the pipeline.

</details>

---

<a id="q12"></a>

### Q12 🟠 · Capstone — Describe a step-by-step pdb session to debug a recursive function hitting max depth

> 🛠️ **Solve locally:** [practice_local.py → Q12](./practice_local.py)



You have a recursive function that raises `RecursionError: maximum recursion depth exceeded`. Describe the exact pdb commands you would run — in order — to identify: which call is looping, what data is causing it, and at what depth it fails.

```python
def flatten(data):
    if isinstance(data, list):
        return [item for sub in data for item in flatten(sub)]
    return data

# Accidentally creates a circular reference:
bad = [1, 2]
bad.append(bad)   # bad now contains itself
flatten(bad)      # RecursionError
```

<details>
<summary>Hint</summary>

Wrap the call in `try/except RecursionError` and call `pdb.post_mortem()`. Use `w` to see the call stack depth. Use `u` repeatedly to travel up frames and inspect the `data` argument at different levels.

</details>

<details>
<summary>Answer</summary>

```python
import pdb

def flatten(data):
    if isinstance(data, list):
        return [item for sub in data for item in flatten(sub)]
    return data

bad = [1, 2]
bad.append(bad)

try:
    flatten(bad)
except RecursionError:
    pdb.post_mortem()
```

Session walkthrough:

```
# Step 1: view the stack depth
(Pdb) w
# Shows hundreds of repeated flatten() frames — confirms infinite recursion

# Step 2: check current frame's data
(Pdb) p data
[1, 2, [...]]   # ← [...] means a list that contains itself

# Step 3: travel up a few frames to confirm the same data is repeated
(Pdb) u
(Pdb) p data    # same object — confirms circular reference
(Pdb) u
(Pdb) p data    # still the same

# Step 4: confirm it is the same object at every level
(Pdb) p id(data)   # same memory address across all frames

# Step 5: check where 'bad.append(bad)' was called
(Pdb) u   # keep going up until you reach the call site
```

Root cause: `bad.append(bad)` creates a circular reference. `flatten` has no base case for this — it recurses forever.

Fix: add a `seen` set using `id()` to detect circular references, or check with `data is bad` before recursing.

**Why:** Post-mortem is ideal for `RecursionError` because you cannot add `breakpoint()` deep enough in advance. `w` immediately shows the stack is thousands of frames deep. `p id(data)` at multiple frames confirms the same object is being passed, pinpointing the circular reference as the cause.

</details>

---

## 🔁 Navigation

| | |
|---|---|
| ⬅️ Back to Module | [../theory.md](../theory.md) |
| 📖 Theory | [theory.md](./theory.md) |
| ➡️ Next Subfolder | [../02_profiling_advanced/practice.md](../02_profiling_advanced/practice.md) |

**Related:** [Logging Theory](../theory.md) · [Profiling & Advanced →](../02_profiling_advanced/theory.md)
