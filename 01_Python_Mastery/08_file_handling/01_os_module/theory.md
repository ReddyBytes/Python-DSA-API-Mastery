# 🗂️ The os Module — Talking to Your Operating System

> The `os` module is Python's universal translator between your code and the operating system — whether you're on Linux, macOS, or Windows, the same `os.path.join()` call builds the right path separator.
> Think of it as the switchboard operator: you ask "create this directory" or "list these files" in Python, and `os` routes the request to the right OS kernel call.

---

## 📌 Learning Priority

**Must Learn** — Daily use:
`os.environ` · `os.getcwd()` / `os.chdir()` · `os.listdir()` · `os.path.join()` · `os.path.exists()` · `os.makedirs()`

**Should Learn** — Real project patterns:
`os.walk()` · `os.path.dirname/basename/splitext` · `os.path.getsize()` · `os.rename()` · `os.remove()`

**Good to Know** — Useful situationally:
`os.getpid()` · `os.cpu_count()` · `os.scandir()` · `os.stat()`

**Reference** — Modern alternative: prefer `pathlib` for path work; prefer `subprocess` over `os.system()`

---

## Environment Variables

Every application that gets deployed to a server communicates its secrets and config through environment variables — not config files, not hardcoded values. Think of env vars as sticky notes the operating system holds for your process: your app asks for the sticky note by name, and the OS hands it back. `os.environ` is your access to that corkboard.

```python
import os

# Read an env var — raises KeyError if missing
db_url = os.environ["DATABASE_URL"]

# Read with a default — never raises
debug = os.environ.get("DEBUG", "false")
port  = int(os.environ.get("PORT", "8080"))

# Check if a var exists
if "API_KEY" in os.environ:
    key = os.environ["API_KEY"]

# Read all env vars as a dict
all_vars = dict(os.environ)          # ← full copy, safe to modify
print(os.environ.keys())             # ← just the names

# Set an env var (current process only — does NOT affect parent shell)
os.environ["MY_VAR"] = "value"

# Delete an env var
del os.environ["MY_VAR"]
os.environ.pop("MY_VAR", None)       # ← safe version, no error if missing
```

**`os.environ` vs `os.getenv()`:**

```python
# os.getenv is just a shorter os.environ.get
os.getenv("PORT")          # → None if missing
os.getenv("PORT", "8080")  # → "8080" if missing

# os.environ["PORT"]       # → KeyError if missing
# os.environ.get("PORT")   # → None if missing (same as getenv)
```

**Production pattern — validate required env vars at startup:**

```python
import os

REQUIRED = ["DATABASE_URL", "SECRET_KEY", "REDIS_URL"]

missing = [var for var in REQUIRED if not os.environ.get(var)]
if missing:
    raise EnvironmentError(f"Missing required environment variables: {missing}")
    # ← fail fast at startup, not mid-request

DATABASE_URL = os.environ["DATABASE_URL"]
SECRET_KEY   = os.environ["SECRET_KEY"]
```

---

## Working Directory

Imagine your script as a worker standing in a room. Every relative path they mention — "the file in the corner", "the folder by the door" — is relative to the room they're standing in. `os.getcwd()` tells you which room that is. `os.chdir()` moves them to a different room. Scripts that rely on relative paths silently break when called from the wrong room — which is why `os.path.abspath(__file__)` is a lifesaver: it gives you the script's own address regardless of where it was called from.

```python
import os

# Current working directory — where relative paths resolve from
cwd = os.getcwd()
print(cwd)             # → /Users/username/projects/myapp

# Change directory
os.chdir("/tmp")
os.chdir(os.path.expanduser("~"))   # ← change to home directory

# Path of the current script file (not affected by os.chdir)
script_dir = os.path.dirname(os.path.abspath(__file__))
# ← __file__ is relative; abspath makes it absolute; dirname strips the filename
# → /Users/username/projects/myapp/src

# Build paths relative to the script (robust regardless of where you run from)
config_path = os.path.join(script_dir, "config", "settings.yaml")
```

---

## Directory Operations

Think of directory operations like managing a filing cabinet. `os.listdir()` lets you peek inside a drawer and see what's there. `os.makedirs()` builds a whole new cabinet section — drawers and sub-drawers in one call. `os.rename()` is the label gun. These are the building blocks for any script that sets up its own folder structure or processes a directory of files.

```python
import os

# List directory contents (names only, not full paths)
entries = os.listdir(".")            # → ['file.txt', 'subdir', ...]
entries = os.listdir("/etc")

# Create a directory
os.mkdir("new_dir")                  # ← fails if parent doesn't exist
os.makedirs("a/b/c")                 # ← creates all intermediate dirs
os.makedirs("a/b/c", exist_ok=True)  # ← no error if already exists

# Remove directory (must be empty)
os.rmdir("empty_dir")

# Remove directory tree (non-empty) — use shutil
import shutil
shutil.rmtree("dir_to_delete")       # ← WARNING: recursive delete, no undo

# Rename / move
os.rename("old_name.txt", "new_name.txt")
os.replace("src.txt", "dst.txt")     # ← atomic rename (safer than rename on Windows)
```

---

## `os.walk()` — Recursively Traverse a Directory Tree

`os.walk()` is like a tour guide that takes you through every room of a building, one floor at a time. At each stop it hands you three things: the address of the current room, a list of sub-rooms you could visit next, and a list of items on the floor right now. It's a generator — it doesn't map the whole building upfront, it just shows you the next room when you're ready. This makes it memory-safe even on directory trees with millions of files.

```python
import os

# Walk the entire tree from top down
for dirpath, dirnames, filenames in os.walk("/my/project"):
    print(f"In directory: {dirpath}")
    for filename in filenames:
        full_path = os.path.join(dirpath, filename)
        print(f"  File: {full_path}")
```

```
os.walk("/project") yields:
  ("/project",           ["src", "tests"],     ["README.md", "setup.py"])
  ("/project/src",       ["utils"],            ["main.py", "config.py"])
  ("/project/src/utils", [],                   ["helpers.py"])
  ("/project/tests",     [],                   ["test_main.py"])
```

**Common patterns:**

```python
import os

# Find all .py files under a directory
py_files = [
    os.path.join(root, f)
    for root, dirs, files in os.walk(".")
    for f in files
    if f.endswith(".py")
]

# Calculate total size of a directory tree
total_bytes = sum(
    os.path.getsize(os.path.join(root, f))
    for root, dirs, files in os.walk(".")
    for f in files
)
print(f"Total size: {total_bytes / 1024 / 1024:.1f} MB")

# Skip hidden directories (starting with .)
for root, dirs, files in os.walk("."):
    dirs[:] = [d for d in dirs if not d.startswith(".")]
    # ← modifying dirs IN PLACE controls which subdirs are visited
```

---

## `os.path` — Path String Operations

A file path is just a string — but it has strict formatting rules that differ between operating systems. `os.path` is a toolkit of string operations that understand those rules. Think of it as a smart parser for addresses: it can tell you the street name (`basename`), the neighborhood (`dirname`), and the building type (`splitext`) from any address you hand it. For new code, `pathlib` does the same job with a cleaner API — but `os.path` is everywhere in existing codebases, so you need to read it fluently.

```python
import os.path   # or just: import os (os.path is already available)

path = "/home/user/projects/app/config.yaml"

os.path.basename(path)          # → "config.yaml"       (filename only)
os.path.dirname(path)           # → "/home/user/projects/app"  (directory only)
os.path.splitext("config.yaml") # → ("config", ".yaml")  (name, extension)
os.path.split(path)             # → ("/home/user/projects/app", "config.yaml")

os.path.join("/home/user", "projects", "app")  # → "/home/user/projects/app"
# ← always use join instead of string concatenation — handles / differences on Windows

os.path.abspath("../config.yaml")   # → absolute path, resolves ..
os.path.realpath("../config.yaml")  # → absolute path + resolves symlinks
os.path.expanduser("~/config.yaml") # → /home/username/config.yaml

os.path.exists("/etc/hosts")         # → True if path exists (file or dir)
os.path.isfile("/etc/hosts")         # → True only if it's a file
os.path.isdir("/etc")                # → True only if it's a directory
os.path.islink("/usr/bin/python3")   # → True if it's a symlink
os.path.getsize("file.txt")          # → size in bytes
os.path.getmtime("file.txt")         # → last modification time (float timestamp)
```

**`os.path` vs `pathlib` for the same operations:**

```python
# os.path way (old)
import os
config = os.path.join(os.path.dirname(os.path.abspath(__file__)), "config.yaml")

# pathlib way (modern, preferred)
from pathlib import Path
config = Path(__file__).parent / "config.yaml"
```

---

## File and Directory Info

When you need to know more about a file than just its name — how big it is, when it was last touched, who can access it — `os.stat()` is the full dossier. Think of it as the file's metadata record card: size, timestamps, permissions, and ownership all in one object. `os.chmod()` lets you update the permissions column directly.

```python
import os

# File metadata
stat = os.stat("file.txt")
stat.st_size     # ← file size in bytes
stat.st_mtime    # ← last modified time (Unix timestamp)
stat.st_ctime    # ← creation time on Windows, inode change on Linux
stat.st_mode     # ← permissions as integer
stat.st_uid      # ← owner user ID
stat.st_gid      # ← owner group ID

# Human-readable size
import datetime
modified = datetime.datetime.fromtimestamp(os.path.getmtime("file.txt"))

# Permissions
os.chmod("script.sh", 0o755)      # ← rwxr-xr-x (owner execute, world read)
os.chmod("secret.key", 0o600)     # ← rw------- (owner read/write only)

# Check if executable
os.access("script.sh", os.X_OK)   # → True if executable
os.access("file.txt", os.R_OK)    # → True if readable
os.access("file.txt", os.W_OK)    # → True if writable
```

---

## Process Information

Your Python script is a process — a running program with its own ID, parent, and resource footprint. `os.getpid()` is like asking "what's my badge number in this office?" The PID is useful for logging (so you can tell apart multiple worker processes), for writing lock files, and for debugging. `os.cpu_count()` is the most common one in production: it tells you how many parallel workers to spin up.

```python
import os

os.getpid()      # → current process ID (PID)
os.getppid()     # → parent process ID

os.cpu_count()   # → number of logical CPUs (useful for thread pool sizing)
# → 8 on a quad-core with hyperthreading

os.getlogin()    # → current user's login name
os.getenv("USER")  # ← more portable than getlogin()

# Memory usage of current process (Linux/macOS)
import resource
usage = resource.getrusage(resource.RUSAGE_SELF)
print(f"Memory: {usage.ru_maxrss / 1024:.1f} MB")
```

---

## Running Shell Commands

`os.system()` is a blunt instrument: it fires a shell command and gives you back only a thumbs-up or thumbs-down. You can't capture the output, you can't handle errors cleanly, and string interpolation opens you up to shell injection. It's the "shout into the hallway and walk away" approach. Use `subprocess` instead — it's the full conversation: you send the command, you get the output back, you check the exit code.

```python
import os
import subprocess

# os.system — avoid in new code
exit_code = os.system("ls -la")   # ← output goes to stdout directly, can't capture
# → returns 0 on success, non-zero on failure

# subprocess — the correct way
result = subprocess.run(["ls", "-la"], capture_output=True, text=True)
print(result.stdout)              # ← captured output
print(result.returncode)          # ← exit code

# When os.system is OK: fire-and-forget interactive commands where you don't need the output
os.system("clear")   # clear the terminal
```

**`os.popen()` — also avoid:**

```python
# Old pattern (avoid)
output = os.popen("ls").read()

# Correct pattern
import subprocess
output = subprocess.check_output(["ls"], text=True)
```

---

## Temporary Files and Directories

Sometimes you need scratch space — a place to write intermediate results that you don't care about keeping. The OS provides a designated temp directory (`/tmp` on Unix) that gets cleared on reboot. `tempfile` handles the bookkeeping: it gives you a unique filename so two concurrent processes don't collide, and it can auto-delete the file when you're done. Use it whenever you need to write something you'd otherwise throw away.

```python
import os
import tempfile

# Get the system temp directory
tmp_dir = tempfile.gettempdir()   # → /tmp on Linux/macOS, C:\Temp on Windows
# os.environ.get("TMPDIR") also works on Unix

# Create a temp file (auto-deleted when closed if delete=True)
with tempfile.NamedTemporaryFile(mode='w', suffix='.json', delete=False) as f:
    f.write('{"key": "value"}')
    tmp_path = f.name

# Use it...
os.unlink(tmp_path)   # ← manual delete since delete=False
```

---

## OS Detection and Constants

Not everything in Python is cross-platform by default. Some libraries behave differently, some path separators differ, some line endings differ. `os.name` and `sys.platform` let you write conditional logic when you genuinely need OS-specific behavior. The key rule: if you're building a path, always use `os.path.join()` — never concatenate strings with `/`. That single habit makes your path code portable everywhere.

```python
import os
import sys

# Detect operating system
sys.platform        # → 'linux', 'darwin', 'win32'
os.name             # → 'posix' (Linux/macOS) or 'nt' (Windows)

# OS-specific path separators (use os.path.join instead of hardcoding)
os.sep          # → '/' on Unix, '\\' on Windows
os.pathsep      # → ':' on Unix, ';' on Windows (used in PATH variable)
os.linesep      # → '\n' on Unix, '\r\n' on Windows

# Platform-safe path construction
config = os.path.join("config", "settings.yaml")   # ← always use this
config = "config/settings.yaml"                     # ← Unix only (avoid)
```

---

## `os` in Production — Real Patterns

These four patterns cover the majority of real-world `os` module usage. They're not clever tricks — they're the idioms you'll see in every well-structured Python codebase. Read them until they feel automatic.

**Pattern 1: Config loader from environment**

```python
import os

class Config:
    """Load all config from environment. Fail fast if required vars missing."""

    DATABASE_URL = os.environ["DATABASE_URL"]          # required
    SECRET_KEY   = os.environ["SECRET_KEY"]             # required
    DEBUG        = os.environ.get("DEBUG", "false").lower() == "true"
    PORT         = int(os.environ.get("PORT", "8080"))
    LOG_LEVEL    = os.environ.get("LOG_LEVEL", "INFO").upper()
    WORKERS      = int(os.environ.get("WORKERS", str(os.cpu_count() or 4)))
    #                                                      ↑ auto-size to CPU count
```

**Pattern 2: Safe directory setup**

```python
import os

def ensure_dirs(*paths):
    """Create directories if they don't exist."""
    for path in paths:
        os.makedirs(path, exist_ok=True)   # ← exist_ok=True is idempotent

ensure_dirs("logs", "data/raw", "data/processed", "models/checkpoints")
```

**Pattern 3: Find all files of a type**

```python
import os

def find_files(root, extension):
    """Recursively find all files with given extension."""
    for dirpath, _, filenames in os.walk(root):
        for filename in filenames:
            if filename.endswith(extension):
                yield os.path.join(dirpath, filename)

for csv_file in find_files("data", ".csv"):
    process(csv_file)
```

**Pattern 4: Script-relative paths (robust regardless of CWD)**

```python
import os

# Always build paths relative to THIS script's location
BASE_DIR    = os.path.dirname(os.path.abspath(__file__))
CONFIG_DIR  = os.path.join(BASE_DIR, "config")
DATA_DIR    = os.path.join(BASE_DIR, "data")
LOG_DIR     = os.path.join(BASE_DIR, "logs")

os.makedirs(LOG_DIR, exist_ok=True)
```

---

## Common Mistakes

| Mistake | What happens | Fix |
|---|---|---|
| `os.environ["KEY"]` without fallback | `KeyError` crashes app at runtime | Use `.get("KEY", "default")` or validate at startup |
| `"path/" + filename` instead of `os.path.join` | Breaks on Windows (wrong separator) | Always `os.path.join()` or `pathlib /` |
| `os.system("cmd")` to capture output | Returns exit code only, output lost | Use `subprocess.run(capture_output=True)` |
| `os.mkdir("a/b/c")` — nested path | `FileNotFoundError` — parent doesn't exist | Use `os.makedirs("a/b/c", exist_ok=True)` |
| `os.environ["KEY"] = value` expecting child process to inherit | Works for child processes, NOT for the parent shell | Expected behavior — env changes propagate to subprocesses only |
| Not checking `os.path.exists()` before `os.remove()` | `FileNotFoundError` | Check first or catch exception |
| `os.listdir()` returns names, not full paths | `FileNotFoundError` when opening files | Always `os.path.join(dirpath, name)` |
| Using `os.path` for new code | Verbose string manipulation | Prefer `pathlib.Path` for new code |

---

## os vs pathlib — When to Use Each

| Situation | Use |
|---|---|
| Reading env vars | `os.environ` / `os.getenv` — no pathlib equivalent |
| New path manipulation code | `pathlib.Path` — cleaner, OO |
| Reading legacy codebases | Know both — `os.path` is everywhere |
| `os.walk()` | `os.walk()` or `Path.rglob("*")` — both fine |
| Getting script directory | `os.path.dirname(os.path.abspath(__file__))` or `Path(__file__).parent` |
| Process info (PID, CPU count) | `os.getpid()`, `os.cpu_count()` — only in `os` |
| Running shell commands | `subprocess` — never `os.system` |

---

## 🔁 Navigation

| | |
|---|---|
| ⬅️ Back to Module | [08_file_handling/theory.md](../theory.md) |
| 💻 Practice | [practice.md](./practice.md) |
| ➡️ Next Subfolder | [02_pathlib →](../02_pathlib/theory.md) |

---

**Related:** [02_pathlib](../02_pathlib/theory.md) · [03_datetime](../03_datetime/theory.md)
