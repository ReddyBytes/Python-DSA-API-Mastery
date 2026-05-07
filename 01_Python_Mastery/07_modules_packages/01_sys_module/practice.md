# 💻 Practice — sys Module

> For hints and answers, expand the dropdowns. Work through each problem in `practice_local.py` first.

---

## Quick Index

| Q# | Topic | Difficulty |
|---|---|---|
| [Q1](#q1--argv--parse-command-line-arguments) | argv — Parse command-line arguments | 🟢 Basic |
| [Q2](#q2--syspath--print-all-entries-and-identify-cwd) | sys.path — Print all entries and identify CWD | 🟢 Basic |
| [Q3](#q3--sysexit--validate-input-with-exit-code) | sys.exit() — Validate input with exit code | 🟢 Basic |
| [Q4](#q4--sysmodules--inspect-the-import-cache) | sys.modules — Inspect the import cache | 🟡 Intermediate |
| [Q5](#q5--sysstdin--word-count-from-pipe) | sys.stdin — Word count from pipe | 🟡 Intermediate |
| [Q6](#q6--sysstdoutstderr--split-log-output) | sys.stdout/stderr — Split log output | 🟡 Intermediate |
| [Q7](#q7--sysversion_info--version-guard) | sys.version_info — Version guard | 🟡 Intermediate |
| [Q8](#q8--sysplatform--detect-os) | sys.platform — Detect OS | 🟡 Intermediate |
| [Q9](#q9--sysmodules-manipulation--lazy-import) | sys.modules manipulation — Lazy import | 🟡 Intermediate |
| [Q10](#q10--sysgetsizeof--compare-memory-sizes) | sys.getsizeof — Compare memory sizes | 🟡 Intermediate |
| [Q11](#q11--syspath-manipulation--safe-add-to-path) | sys.path manipulation — Safe add to path | 🟠 Advanced |
| [Q12](#q12--capstone--cli-entry-point) | Capstone — CLI entry point | 🟠 Advanced |

---

### Q1 🟢 · argv — Parse command-line arguments

> 🛠️ **Solve locally:** [practice_local.py → Q1](./practice_local.py)

**Problem:** Write a script that uses `sys.argv` to accept a filename as the first argument and an optional `--verbose` flag anywhere in the remaining args. Print the filename and whether verbose mode is on. Print a usage message to stderr and exit with code 2 if no filename is given.

<details>
<summary>💡 Hint</summary>

Check `len(sys.argv)` before accessing `sys.argv[1]`. For the flag, check if `"--verbose"` is anywhere in `sys.argv[1:]` using `in`.

</details>

<details>
<summary>✅ Answer</summary>

```python
import sys

if len(sys.argv) < 2:
    print("Usage: python script.py <filename> [--verbose]", file=sys.stderr)
    sys.exit(2)

filename = sys.argv[1]
verbose = "--verbose" in sys.argv[1:]

print(f"File: {filename}")
print(f"Verbose: {verbose}")
```

**Why:** Always guard `sys.argv` access with a length check. Exit code 2 is the Unix convention for "bad arguments / misuse of command". The `--verbose` check with `in` is the simplest approach before reaching for `argparse`.

</details>

---

### Q2 🟢 · sys.path — Print all entries and identify CWD

> 🛠️ **Solve locally:** [practice_local.py → Q2](./practice_local.py)

**Problem:** Print all entries in `sys.path`, numbering each one. Then identify and print which entry represents the current working directory (the empty string `''` or the actual CWD path).

<details>
<summary>💡 Hint</summary>

Iterate with `enumerate`. The current directory is represented as `''` (empty string) in `sys.path`. You can also compare entries against `os.getcwd()`.

</details>

<details>
<summary>✅ Answer</summary>

```python
import sys
import os

print("sys.path entries:")
for i, entry in enumerate(sys.path):
    marker = " ← CWD" if entry == "" or entry == os.getcwd() else ""
    display = entry if entry else "(empty string = CWD)"
    print(f"  [{i}] {display}{marker}")

cwd_entries = [e for e in sys.path if e == "" or e == os.getcwd()]
print(f"\nCWD represented by: {cwd_entries or 'not found'}")
```

**Why:** The empty string `''` at index 0 means "search the current working directory first". This is why a local file can accidentally shadow an installed package — it wins because it's at position 0.

</details>

---

### Q3 🟢 · sys.exit() — Validate input with exit code

> 🛠️ **Solve locally:** [practice_local.py → Q3](./practice_local.py)

**Problem:** Write a function `validate_input(value)` that raises a clean error exit if `value` is negative. It should print an error message to stderr and call `sys.exit(1)`. Then write a `main()` that calls it with a value from the user.

<details>
<summary>💡 Hint</summary>

Print to `sys.stderr` before calling `sys.exit(1)`. Remember that `sys.exit()` raises `SystemExit` — you can verify behavior in a test by catching it.

</details>

<details>
<summary>✅ Answer</summary>

```python
import sys

def validate_input(value):
    if value < 0:
        print(f"Error: value must be non-negative, got {value}", file=sys.stderr)
        sys.exit(1)
    return value

def main():
    try:
        value = float(input("Enter a non-negative number: "))
    except ValueError:
        print("Error: not a number", file=sys.stderr)
        sys.exit(1)

    result = validate_input(value)
    print(f"Valid input: {result}")

if __name__ == "__main__":
    main()
```

**Why:** Separating validation from I/O makes `validate_input` testable — you can catch `SystemExit` in unit tests. Writing the error to `sys.stderr` keeps it out of any stdout pipeline.

</details>

---

### Q4 🟡 · sys.modules — Inspect the import cache

> 🛠️ **Solve locally:** [practice_local.py → Q4](./practice_local.py)

**Problem:** Import `json` and `math`. Then: (1) print how many modules are currently in `sys.modules`, (2) check and print whether `'csv'` is cached, (3) import `csv` and check again, (4) print the module object for `json` retrieved directly from `sys.modules`.

<details>
<summary>💡 Hint</summary>

`sys.modules` is a plain dict — use `len()`, `in`, and `[]` access on it. The module object retrieved from `sys.modules["json"]` is the exact same object as what `import json` returns.

</details>

<details>
<summary>✅ Answer</summary>

```python
import sys
import json
import math

print(f"Modules in sys.modules: {len(sys.modules)}")

print(f"'csv' cached before import: {'csv' in sys.modules}")

import csv
print(f"'csv' cached after import:  {'csv' in sys.modules}")

json_from_cache = sys.modules["json"]
print(f"json from sys.modules: {json_from_cache}")
print(f"Same object as import json: {json_from_cache is json}")
```

**Why:** `sys.modules` is the single source of truth for all loaded modules. Checking it before importing is the foundation of lazy import patterns and mock injection in tests. The `is` check confirms Python returns the cached object — not a copy.

</details>

---

### Q5 🟡 · sys.stdin — Word count from pipe

> 🛠️ **Solve locally:** [practice_local.py → Q5](./practice_local.py)

**Problem:** Write a script that reads all lines from `sys.stdin` until EOF and prints three counts: total lines, total words, and total characters (including newlines). Match the output format of the Unix `wc` command: `lines words chars`.

<details>
<summary>💡 Hint</summary>

Iterate `for line in sys.stdin`. Words per line: `len(line.split())`. Characters: `len(line)` (this includes the newline). Accumulate into counters.

</details>

<details>
<summary>✅ Answer</summary>

```python
import sys

lines = 0
words = 0
chars = 0

for line in sys.stdin:
    lines += 1
    words += len(line.split())
    chars += len(line)

print(f"{lines:>8} {words:>8} {chars:>8}")

# Usage:
#   echo "hello world\nfoo bar baz" | python script.py
#   cat somefile.txt | python script.py
```

**Why:** Iterating `sys.stdin` reads line-by-line, which works on arbitrarily large files without loading everything into memory. This is the Unix filter pattern — your script becomes composable with pipes.

</details>

---

### Q6 🟡 · sys.stdout/stderr — Split log output

> 🛠️ **Solve locally:** [practice_local.py → Q6](./practice_local.py)

**Problem:** Write a `log(message, level="INFO")` function that sends `INFO` and `DEBUG` messages to `sys.stdout` and `WARNING`/`ERROR` messages to `sys.stderr`. Format each line as `[LEVEL] message`. Test it with one message of each level.

<details>
<summary>💡 Hint</summary>

Use `file=sys.stderr` in `print()` for the error levels. You can test which stream was used by checking the output when running `python script.py 2>/dev/null` (suppresses stderr) vs `python script.py >/dev/null` (suppresses stdout).

</details>

<details>
<summary>✅ Answer</summary>

```python
import sys

def log(message, level="INFO"):
    formatted = f"[{level}] {message}"
    if level in ("WARNING", "ERROR"):
        print(formatted, file=sys.stderr)
    else:
        print(formatted, file=sys.stdout)

log("Application started")
log("Loading config", level="DEBUG")
log("Disk space low", level="WARNING")
log("Connection failed", level="ERROR")

# Test separation:
#   python script.py 2>/dev/null   → only INFO and DEBUG appear
#   python script.py >/dev/null    → only WARNING and ERROR appear
```

**Why:** Separating log levels across stdout and stderr lets operators filter them independently. Monitoring tools, log aggregators, and shell pipelines all treat the two streams differently. This is standard practice in CLI tools and container workloads.

</details>

---

### Q7 🟡 · sys.version_info — Version guard

> 🛠️ **Solve locally:** [practice_local.py → Q7](./practice_local.py)

**Problem:** Write a function `require_python(major, minor)` that raises a `RuntimeError` with a descriptive message if the currently running Python is older than the required version. Test it by calling `require_python(3, 10)`.

<details>
<summary>💡 Hint</summary>

Compare `sys.version_info` as a tuple: `sys.version_info < (major, minor)`. Named tuple fields `.major` and `.minor` are also available. Include the current version in the error message.

</details>

<details>
<summary>✅ Answer</summary>

```python
import sys

def require_python(major, minor):
    required = (major, minor)
    current = (sys.version_info.major, sys.version_info.minor)
    if current < required:
        raise RuntimeError(
            f"Python {major}.{minor}+ is required. "
            f"Currently running: Python {current[0]}.{current[1]}"
        )
    print(f"Python version OK: {current[0]}.{current[1]} >= {major}.{minor}")

require_python(3, 10)
```

**Why:** Always compare `sys.version_info` tuples — never compare `sys.version` as a string. String comparison makes `"3.9" > "3.10"` evaluate to `True` because `"9" > "1"` lexicographically. Tuple comparison does it correctly.

</details>

---

### Q8 🟡 · sys.platform — Detect OS

> 🛠️ **Solve locally:** [practice_local.py → Q8](./practice_local.py)

**Problem:** Write a function `get_os()` that returns the string `'mac'`, `'linux'`, or `'windows'` based on `sys.platform`. Then write `get_config_dir()` that returns the conventional config directory path for the detected OS. Return `'unknown'` for unrecognized platforms.

<details>
<summary>💡 Hint</summary>

`sys.platform` values: `'darwin'` for macOS, `'linux'` for Linux, `'win32'` for Windows (even 64-bit). Use `startswith` for Linux variants.

</details>

<details>
<summary>✅ Answer</summary>

```python
import sys

def get_os():
    if sys.platform == "darwin":
        return "mac"
    elif sys.platform.startswith("linux"):
        return "linux"
    elif sys.platform == "win32":
        return "windows"
    return "unknown"

def get_config_dir(app_name):
    os_name = get_os()
    if os_name == "mac":
        return f"/Library/Application Support/{app_name}"
    elif os_name == "linux":
        return f"/etc/{app_name}"
    elif os_name == "windows":
        return rf"C:\ProgramData\{app_name}"
    return f"./{app_name}"

print(f"OS: {get_os()}")
print(f"Config dir: {get_config_dir('myapp')}")
```

**Why:** `sys.platform` uses `startswith("linux")` rather than `== "linux"` because some Linux variants return strings like `"linux2"`. The wrapper function `get_os()` isolates the platform detection so the rest of your code works with clean strings.

</details>

---

### Q9 🟡 · sys.modules manipulation — Lazy import

> 🛠️ **Solve locally:** [practice_local.py → Q9](./practice_local.py)

**Problem:** Write a function `lazy_import(name)` that checks `sys.modules` before importing. If the module is already cached, return it from the cache. If not, import it, and return the module. Print whether it was served from cache or freshly imported.

<details>
<summary>💡 Hint</summary>

Use `sys.modules.get(name)` to check without raising `KeyError`. Use `importlib.import_module(name)` to import by string name.

</details>

<details>
<summary>✅ Answer</summary>

```python
import sys
import importlib

def lazy_import(name):
    cached = sys.modules.get(name)
    if cached is not None:
        print(f"'{name}' served from sys.modules cache")
        return cached
    module = importlib.import_module(name)
    print(f"'{name}' freshly imported and cached")
    return module

json_mod = lazy_import("json")    # → freshly imported
json_mod2 = lazy_import("json")   # → from cache
csv_mod = lazy_import("csv")      # → freshly imported

print(json_mod is json_mod2)      # → True — same object
```

**Why:** This pattern is the foundation of optional-dependency handling. Libraries like `pandas` use it to avoid importing heavy optional dependencies (like `sqlalchemy`) until actually needed. Checking `sys.modules` first is faster than a try/import block.

</details>

---

### Q10 🟡 · sys.getsizeof — Compare memory sizes

> 🛠️ **Solve locally:** [practice_local.py → Q10](./practice_local.py)

**Problem:** Compare the memory footprint of: an empty list, a list with 1000 integers, and a list with 1000 strings. Use `sys.getsizeof` and print the results. Then explain why the sizes may be misleading.

<details>
<summary>💡 Hint</summary>

`sys.getsizeof` returns the shallow size — for a list, it's the size of the list object and its pointer array, not the elements themselves. A list of 1000 items holds 1000 pointers (8 bytes each on 64-bit Python).

</details>

<details>
<summary>✅ Answer</summary>

```python
import sys

empty_list = []
int_list = list(range(1000))
str_list = [str(i) for i in range(1000)]

print(f"Empty list:           {sys.getsizeof(empty_list):>8} bytes")
print(f"List of 1000 ints:    {sys.getsizeof(int_list):>8} bytes")
print(f"List of 1000 strings: {sys.getsizeof(str_list):>8} bytes")

# Both int_list and str_list will show similar sizes (~8056 bytes)
# because sys.getsizeof only measures the pointer array, not the elements

print("\nWhy similar? sys.getsizeof measures the list's pointer array only.")
print("A list of 1000 items = 1000 pointers × 8 bytes each = ~8000 bytes")
print("The actual integers and strings are separate objects not counted here.")

# To show the difference, check individual element sizes:
print(f"\nSize of int 42:       {sys.getsizeof(42)} bytes")
print(f"Size of str '42':     {sys.getsizeof('42')} bytes")
```

**Why:** `sys.getsizeof` is intentionally shallow. A list is just an array of pointers — the objects it points to are measured separately. This is why `sys.getsizeof(big_list)` can return 8KB while the list actually occupies hundreds of MB. Use `pympler.asizeof` for true deep measurement.

</details>

---

### Q11 🟠 · sys.path manipulation — Safe add to path

> 🛠️ **Solve locally:** [practice_local.py → Q11](./practice_local.py)

**Problem:** Write a function `add_to_path(directory, position="end")` that adds a directory to `sys.path` only if it is not already present. Support `position="start"` (insert at index 0) and `position="end"` (append). Return `True` if added, `False` if already present. Include input validation.

<details>
<summary>💡 Hint</summary>

Check `directory in sys.path` before modifying. Use `sys.path.insert(0, directory)` for start and `sys.path.append(directory)` for end. Consider using `os.path.abspath` to normalize the path before comparing.

</details>

<details>
<summary>✅ Answer</summary>

```python
import sys
import os

def add_to_path(directory, position="end"):
    if not isinstance(directory, str):
        raise TypeError(f"directory must be a string, got {type(directory).__name__}")
    if position not in ("start", "end"):
        raise ValueError(f"position must be 'start' or 'end', got '{position}'")

    # Normalize to absolute path for reliable comparison
    abs_dir = os.path.abspath(directory)

    if abs_dir in sys.path:
        print(f"Already in sys.path: {abs_dir}")
        return False

    if position == "start":
        sys.path.insert(0, abs_dir)
    else:
        sys.path.append(abs_dir)

    print(f"Added to sys.path ({position}): {abs_dir}")
    return True

# Test it
add_to_path("/tmp/mylibs")              # → adds at end
add_to_path("/tmp/mylibs")              # → already present, skips
add_to_path("/tmp/priority", "start")   # → adds at index 0
print(sys.path[:3])
```

**Why:** Always normalize paths with `os.path.abspath` before comparing — `"/tmp/mylibs"` and `"../mylibs"` could refer to the same directory but won't match as strings. The idempotency check prevents `sys.path` from accumulating duplicate entries across repeated calls (common in REPL sessions or hot-reload scenarios).

</details>

---

### Q12 🟠 · Capstone — CLI entry point

> 🛠️ **Solve locally:** [practice_local.py → Q12](./practice_local.py)

**Problem:** Write a complete CLI entry point for a file-processing script that: (1) uses `sys.argv` to accept one or more filenames, (2) validates that each file exists and prints an error to `sys.stderr` for any that don't, (3) processes each valid file (just print its line count), (4) exits with code 0 if all files were processed, code 1 if any file was missing, and code 2 if no arguments were given at all.

<details>
<summary>💡 Hint</summary>

Track whether any errors occurred with a boolean flag. Use `os.path.exists` to check files. Call `sys.exit()` at the very end with the appropriate code — not in the middle of the loop.

</details>

<details>
<summary>✅ Answer</summary>

```python
import sys
import os

def count_lines(filepath):
    with open(filepath, "r") as f:
        return sum(1 for _ in f)

def main():
    if len(sys.argv) < 2:
        print("Usage: python script.py <file1> [file2 ...]", file=sys.stderr)
        sys.exit(2)

    had_errors = False

    for filepath in sys.argv[1:]:
        if not os.path.exists(filepath):
            print(f"Error: file not found: {filepath}", file=sys.stderr)
            had_errors = True
            continue

        line_count = count_lines(filepath)
        print(f"{line_count:>8}  {filepath}")

    sys.exit(1 if had_errors else 0)

if __name__ == "__main__":
    main()
```

**Why:** This is the canonical pattern for production CLI tools — guard `sys.argv`, write all errors to `sys.stderr`, continue processing remaining valid inputs rather than aborting on first error, and use a single `sys.exit()` at the end with the appropriate code. The `if __name__ == "__main__"` guard makes the script importable for testing.

</details>

---

## 🔁 Navigation

| | |
|---|---|
| ⬅️ Back to Theory | [theory.md](./theory.md) |
| 🖥️ Practice Local | [practice_local.py](./practice_local.py) |
| ⬅️ Back to Module | [07_modules_packages/theory.md](../theory.md) |
| ➡️ Next Subfolder | [02_argparse →](../02_argparse/practice.md) |
