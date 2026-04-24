# The `sys` Module — Python's Window into the Interpreter

Every Python program runs inside an interpreter — a process that reads your code, manages memory, handles imports, and decides when to exit. Most of the time that interpreter is invisible. The `sys` module makes it visible.

Think of the difference between `os` and `sys` like the difference between a pilot's radio and a pilot's cockpit instruments. The radio (`os`) lets the plane communicate with air traffic control — the outside world. The cockpit instruments (`sys`) show what is happening inside the plane right now: airspeed, altitude, fuel level, engine state. `sys` is your read into the interpreter's own state: which Python version is running, what arguments were passed on the command line, where Python looks for modules, what the standard I/O streams are, and how to exit cleanly.

```python
import sys
```

That single import gives you access to variables and functions that are set up by the interpreter itself at startup — before your first line of code runs.

---

## sys.argv — Command-Line Arguments

When you run `python script.py foo bar`, the interpreter captures everything you typed into a list called **`sys.argv`**. It is always a list of strings. The first element is always the script name.

```
python greet.py Alice 42

sys.argv  →  ["greet.py", "Alice", "42"]
             ─────────────────────────────
              [0]          [1]     [2]
              script name  ↑               ↑
                           first arg       second arg
```

```python
import sys

script_name = sys.argv[0]      # ← always the script's filename
args        = sys.argv[1:]     # ← everything the user typed after the script name

print(f"Script: {script_name}")
print(f"Arguments: {args}")
```

**Guard pattern — fail fast with a clear usage message:**

```python
import sys

if len(sys.argv) < 2:
    print("Usage: python greet.py <name>", file=sys.stderr)
    sys.exit(1)                # ← non-zero exit = failure

name = sys.argv[1]
print(f"Hello, {name}!")
```

**Raw `sys.argv` vs `argparse` — when to use each:**

```python
# sys.argv directly — fine for scripts with 1-2 fixed positional arguments
import sys

if len(sys.argv) != 3:
    print("Usage: python copy.py <src> <dst>", file=sys.stderr)
    sys.exit(1)

src, dst = sys.argv[1], sys.argv[2]

# argparse — use once you have flags, optional args, or need --help auto-generated
import argparse

parser = argparse.ArgumentParser(description="Copy a file")
parser.add_argument("src",  help="source file")
parser.add_argument("dst",  help="destination file")
parser.add_argument("--verbose", action="store_true")   # ← optional flag
args = parser.parse_args()

print(f"Copying {args.src} → {args.dst}")
if args.verbose:
    print("verbose mode on")
```

The rule of thumb: once you need flags (things starting with `--`) or optional arguments, reach for `argparse`. For a quick one-off script that takes a filename and nothing else, raw `sys.argv` is fine.

---

## sys.path — Where Python Looks for Modules

When you write `import requests`, Python does not search your whole disk. It searches a specific list of directories in order. That list is **`sys.path`**.

```python
import sys

print(sys.path)
# → ['', '/usr/lib/python312.zip', '/usr/lib/python3.12',
#    '/usr/lib/python3.12/lib-dynload',
#    '/home/user/.local/lib/python3.12/site-packages',
#    '/usr/local/lib/python3.12/dist-packages']
```

The search order matters:

```
sys.path search order:
  [0] ''  ←  current working directory (or script's directory)
  [1] PYTHONPATH entries (from environment variable, if set)
  [2] Standard library paths
  [3] site-packages (where pip installs packages)
```

The first directory that contains the module wins. That is why a local file named `requests.py` would shadow the real `requests` package.

**Adding a directory to the front of sys.path:**

```python
import sys

sys.path.insert(0, "/my/custom/libs")    # ← add at position 0 = search first
sys.path.append("/another/lib/dir")      # ← add at end = search last

# Check what is currently in the path
for p in sys.path:
    print(p)
```

**The `PYTHONPATH` environment variable** is the clean alternative to modifying `sys.path` in code:

```bash
# In the shell — adds /my/libs to sys.path before starting Python
PYTHONPATH=/my/libs python script.py

# Or permanently in .bashrc/.zshrc
export PYTHONPATH="/my/libs:$PYTHONPATH"
```

**Why modifying `sys.path` in code is usually wrong:**

Inserting paths into `sys.path` at runtime is fragile — it depends on CWD, breaks when the script is imported from elsewhere, and is invisible to other developers. The correct approach depends on your situation:

| Situation | Correct approach |
|---|---|
| Sharing code between your own projects | Create a proper Python package with `setup.py` / `pyproject.toml` and `pip install -e .` |
| Utilities inside a monorepo | Configure `PYTHONPATH` in the project's run scripts |
| Quick local experiments | `sys.path.insert` is acceptable — but document it |
| Production application | Always use a proper virtualenv with installed packages |

---

## sys.exit() — Controlled Exit

Every program eventually ends. `sys.exit()` is how you end a program intentionally, with a specific exit code that tells the calling process whether things went well.

The convention is universal across all Unix/Linux systems: **exit code 0 means success, any non-zero means failure**. Shell scripts, CI pipelines, and orchestrators all read this code to decide what to do next.

```python
import sys

sys.exit(0)           # ← success — no error
sys.exit(1)           # ← generic failure
sys.exit(2)           # ← misuse of the command / bad arguments (common convention)
sys.exit(42)          # ← any non-zero works; some tools use specific codes

# Shortcut: pass a string — prints to stderr and exits with code 1
sys.exit("Error: database connection failed")
# equivalent to:
#   print("Error: database connection failed", file=sys.stderr)
#   sys.exit(1)
```

**How sys.exit() actually works — it raises `SystemExit`:**

`sys.exit()` does not terminate the process directly. It raises a **`SystemExit`** exception, which Python's runtime catches and uses to end the interpreter. This matters because:

```python
import sys

# SystemExit can be caught (though rarely should be)
try:
    sys.exit(1)
except SystemExit as e:
    print(f"Caught exit with code: {e.code}")   # → 1
    # execution continues here — but this is unusual

# If you need cleanup on exit, use atexit instead of catching SystemExit
import atexit

def cleanup():
    print("Closing database connections...")
    # ← runs on normal exit, sys.exit(), or unhandled exceptions

atexit.register(cleanup)
```

`atexit` is the right way to guarantee cleanup code runs, rather than wrapping the whole program in a try/except.

---

## sys.stdin, sys.stdout, sys.stderr — Standard Streams

Every running process has three standard I/O channels. Python exposes them as **`sys.stdin`**, **`sys.stdout`**, and **`sys.stderr`**. They are file-like objects — anything that works with `open()` also works with them.

```
stdin  →  [ your script ] →  stdout
                           ↘  stderr
```

**Reading from stdin — pipe-friendly scripts:**

```python
import sys

# Read all lines piped into the script
for line in sys.stdin:
    line = line.rstrip("\n")      # ← strip the newline
    print(f"Processed: {line}")

# Usage:
#   echo "hello" | python script.py
#   cat data.txt | python script.py
```

**Writing to stderr — errors that should not pollute stdout:**

```python
import sys

# This goes to stderr — will not appear in `python script.py > output.txt`
print("Error: file not found", file=sys.stderr)

# These are equivalent
sys.stderr.write("Error: file not found\n")
print("Error: file not found", file=sys.stderr)
```

In Unix pipelines, stdout and stderr are separate channels. Only stdout is captured by `> file.txt` or `| next_command`. Writing errors to stderr keeps them visible to the operator without corrupting the data stream.

**Redirecting stdout — capture all print output:**

```python
import sys

# Redirect all print() calls to a file
original_stdout = sys.stdout

with open("log.txt", "w") as f:
    sys.stdout = f                    # ← all print() now goes to the file
    print("This goes to the file")
    print("So does this")

sys.stdout = original_stdout          # ← restore for console output
print("This goes to the terminal again")
```

**`sys.stdout.flush()` — force buffer flush:**

```python
import sys

# In containers and CI, stdout is often buffered
# Output may not appear until the buffer fills or the process exits
for i in range(100):
    print(f"Processing item {i}...")
    sys.stdout.flush()                # ← force immediate output

# Equivalent: run Python with -u flag (unbuffered)
#   python -u script.py

# Or set environment variable:
#   PYTHONUNBUFFERED=1 python script.py
```

This is critical in Docker containers and Kubernetes pods. Without flushing, log output may appear in bursts or not at all — making debugging nearly impossible. Always set `PYTHONUNBUFFERED=1` in your `Dockerfile` or pod spec.

---

## sys.version and sys.version_info

**`sys.version`** is a human-readable string. **`sys.version_info`** is a named tuple you can compare programmatically.

```python
import sys

print(sys.version)
# → '3.12.3 (main, Apr  9 2024, 08:09:14) [GCC 13.2.0]'

print(sys.version_info)
# → sys.version_info(major=3, minor=12, micro=3, releaselevel='final', serial=0)

# Access individual components
print(sys.version_info.major)    # → 3
print(sys.version_info.minor)    # → 12
print(sys.version_info.micro)    # → 3

# Named tuple also supports indexing
print(sys.version_info[:2])      # → (3, 12)
```

**Version guards — fail fast if running on wrong Python:**

```python
import sys

# Enforce minimum Python version at the top of your module
if sys.version_info < (3, 9):
    raise RuntimeError(
        f"Python 3.9+ is required. You are running {sys.version_info[:2]}"
    )

# Conditional feature use
if sys.version_info >= (3, 11):
    from tomllib import loads                # ← built-in in 3.11+
else:
    from tomli import loads                  # ← third-party backport
```

Version guards are most useful in library code that needs to support multiple Python versions, and at the top of scripts that use features only available in recent versions.

---

## sys.platform — OS Detection

**`sys.platform`** is a short string identifying the operating system. Use it when you need to write code that behaves differently on different platforms.

```python
import sys

print(sys.platform)
# → 'linux'   on Linux
# → 'darwin'  on macOS
# → 'win32'   on Windows (even 64-bit)

# Platform-specific code blocks
if sys.platform == "linux":
    config_dir = "/etc/myapp"
elif sys.platform == "darwin":
    config_dir = "/Library/Application Support/myapp"
elif sys.platform == "win32":
    config_dir = r"C:\ProgramData\myapp"

# Simpler check: "is this Unix-like?"
if sys.platform.startswith(("linux", "darwin")):
    # POSIX-compatible code
    pass
```

**`sys.platform` vs the `platform` module:**

`sys.platform` gives you a short identifier. The `platform` module gives you everything: full OS name, version, architecture, hostname, Python build details.

```python
import platform

print(platform.system())        # → 'Linux', 'Darwin', 'Windows'
print(platform.release())       # → '6.8.0-45-generic'
print(platform.machine())       # → 'x86_64', 'arm64'
print(platform.python_version())# → '3.12.3'
print(platform.node())          # → hostname
```

For simple platform branching, `sys.platform` is enough. For detailed system reporting or logging, use `platform`.

---

## sys.modules — The Import Cache

Python does not re-execute module code every time you `import` it. After the first import, the module object is stored in **`sys.modules`** — a dictionary keyed by module name. Every subsequent `import` just returns the cached object.

```
first import:  reads file → executes code → stores in sys.modules → returns module
second import: looks up sys.modules → returns cached module (fast, no re-execution)
```

```python
import sys
import os

# Check if a module is already imported
print("os" in sys.modules)        # → True
print("requests" in sys.modules)  # → False (if not yet imported)

# Access a cached module by name
os_module = sys.modules["os"]
print(os_module.getcwd())         # → same object as `import os`

# See all currently imported modules
for name in sorted(sys.modules.keys()):
    print(name)
```

**Reloading a module — when you want fresh execution:**

```python
import importlib
import mymodule

# Reload from disk (useful in REPL development, not production)
importlib.reload(mymodule)        # ← re-executes the module file
```

**Monkey patching via sys.modules:**

In tests, you can replace a module in `sys.modules` before it is imported by the code under test:

```python
import sys
from unittest.mock import MagicMock

# Replace 'requests' with a mock before importing the module that uses it
sys.modules["requests"] = MagicMock()

import mymodule   # ← mymodule will get the mock when it does `import requests`
```

This technique is powerful for isolating code under test from external dependencies.

---

## sys.executable — The Python Binary Path

**`sys.executable`** is the absolute path to the Python interpreter that is currently running your script. This matters when you need to spawn a subprocess that must use the exact same Python.

```python
import sys

print(sys.executable)
# → '/home/user/.venv/bin/python3'   (inside a virtualenv)
# → '/usr/bin/python3'               (system Python)
# → '/opt/homebrew/bin/python3.12'   (Homebrew on macOS)
```

**Spawning subprocesses with the same Python:**

```python
import sys
import subprocess

# WRONG — uses whatever 'python3' resolves to on PATH
# This may be a different Python, or not exist at all
subprocess.run(["python3", "worker.py"])

# CORRECT — uses the exact same interpreter that is running this script
subprocess.run([sys.executable, "worker.py"])
subprocess.run([sys.executable, "-m", "mypackage.worker"])  # ← as a module
```

This is especially important in virtualenvs. If you spawn a subprocess using the hardcoded `python3` command, it might pick up the system Python instead of the virtualenv Python, giving you a completely different set of installed packages.

---

## sys.getrecursionlimit() and sys.setrecursionlimit()

Python limits how deeply functions can call themselves. The default **recursion limit** is 1000 stack frames. When you exceed it, Python raises `RecursionError` instead of crashing with a stack overflow.

```python
import sys

print(sys.getrecursionlimit())    # → 1000

# Increase the limit for deep recursive algorithms
sys.setrecursionlimit(5000)

# Example: deep recursive function
def count_down(n):
    if n == 0:
        return "done"
    return count_down(n - 1)    # ← recursive call

count_down(4000)   # works after setrecursionlimit(5000)
```

**When to increase the limit:**

Legitimate cases include processing deeply nested data structures (like ASTs of complex programs) or tree algorithms where depth is bounded but exceeds 1000. The key word is "bounded" — you should know roughly how deep it goes.

**When increasing is a code smell:**

If you find yourself writing `sys.setrecursionlimit(100000)` to make an algorithm work, that is usually a signal to rewrite using an explicit stack (iteration). Python does not have tail-call optimization, so every recursive call adds a frame. Deep recursion is slow and memory-hungry.

```python
# Recursive — hits limit for large n
def factorial_recursive(n):
    if n <= 1:
        return 1
    return n * factorial_recursive(n - 1)

# Iterative — no limit, faster, less memory
def factorial_iterative(n):
    result = 1
    for i in range(2, n + 1):
        result *= i
    return result
```

---

## sys.getsizeof() — Object Memory Size

**`sys.getsizeof(obj)`** returns the size of an object in bytes. It measures the direct memory of the object itself, not the objects it references — this is called the **shallow size**.

```python
import sys

print(sys.getsizeof(42))          # → 28   (int has fixed overhead)
print(sys.getsizeof("hello"))     # → 54   (string base + 5 chars)
print(sys.getsizeof([]))          # → 56   (empty list overhead)
print(sys.getsizeof([1, 2, 3]))   # → 88   (list + 3 pointers, not the ints themselves)
print(sys.getsizeof({}))          # → 64   (empty dict)
```

**The shallow-size trap:**

```python
import sys

data = [list(range(1000)) for _ in range(1000)]

print(sys.getsizeof(data))
# → 8056 bytes  ← just the outer list's pointer array
# Does NOT include the 1000 inner lists or their integers!
# True size is ~8+ MB
```

For deep (total) memory measurement, use `pympler`:

```python
from pympler import asizeof

print(asizeof.asizeof(data))   # → ~35,000,000 bytes (35 MB) — full deep size
```

Use `sys.getsizeof` for quick comparisons of similar objects or for understanding Python's object overhead model. Use `pympler` when you need actual memory profiling.

---

## Common Patterns

**Pattern 1 — Pipe-friendly script:**

```python
import sys

def process_line(line):
    return line.upper().strip()

for line in sys.stdin:
    result = process_line(line)
    print(result)
    sys.stdout.flush()             # ← ensure real-time output in containers

# Usage:
#   cat data.txt | python process.py
#   echo "hello" | python process.py > output.txt
```

**Pattern 2 — Accept file argument or fall back to stdin:**

```python
import sys

def get_input_stream():
    """Return a file handle: the named file if given, else stdin."""
    if len(sys.argv) > 1:
        return open(sys.argv[1], "r")   # ← file was provided
    else:
        return sys.stdin                # ← fall back to piped input

with get_input_stream() as f:
    for line in f:
        print(line.rstrip())

# Usage:
#   python script.py data.txt
#   cat data.txt | python script.py
```

**Pattern 3 — Version check at module import time:**

```python
import sys

if sys.version_info < (3, 9):
    raise ImportError(
        f"This module requires Python 3.9+. "
        f"Currently running: {sys.version_info.major}.{sys.version_info.minor}"
    )

# Safe to use 3.9+ features below
from zoneinfo import ZoneInfo         # ← stdlib in 3.9+
```

---

## Common Mistakes

| Mistake | What happens | Fix |
|---|---|---|
| `sys.argv[1]` without checking length | `IndexError` if no argument provided | Guard with `if len(sys.argv) < 2` first |
| `sys.path.insert(0, ...)` in library code | Import order becomes unpredictable for users of the library | Use proper packaging (`pip install -e .`) instead |
| `print("error")` instead of `print(..., file=sys.stderr)` | Error message appears in stdout, pollutes data pipelines | Always write errors to `sys.stderr` |
| `sys.exit()` inside a `try` block with bare `except:` | `SystemExit` is swallowed, program does not exit | Bare `except:` catches everything including `SystemExit` — use `except Exception:` |
| Not setting `PYTHONUNBUFFERED=1` in containers | Logs appear in bursts or not at all | Set env var or use `python -u` |
| `sys.getsizeof(big_list)` to measure memory | Returns only the list's pointer array size, not the data | Use `pympler.asizeof` for true deep size |
| `sys.setrecursionlimit(99999)` to fix recursion error | Masks the real problem, eventually crashes the process | Rewrite the algorithm iteratively |
| Comparing `sys.version` as a string | String comparison of version numbers is unreliable (`"3.9" > "3.10"` is True) | Always compare `sys.version_info` tuples |

---

## Navigation

**Related:**
- [os Module](../08_file_handling/os_module.md) — OS-level file, dir, and env operations
- [Modules and Packages Theory](./theory.md) — how imports, packages, and `__init__.py` work
- [subprocess Module](./subprocess_module.md) — spawning and managing subprocesses
