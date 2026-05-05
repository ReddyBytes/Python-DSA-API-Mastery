# The `os` Module — Python's Interface to the Operating System

Your Python script does not run in a vacuum. It runs on an operating system — and the OS controls files, directories, environment variables, processes, and permissions. The `os` module is the bridge. Think of it as the front desk of a hotel: you don't go directly to the boiler room or the kitchen, you ask the front desk, which knows the right people to call. `import os` gives you that front desk — a uniform API that works identically on macOS, Linux, and Windows regardless of the underlying OS differences.

---

## Environment Variables

The most commonly used part of the `os` module in production. Every cloud-deployed Python app reads its configuration from environment variables — database URLs, API keys, feature flags.

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

`os.walk()` is a generator that yields `(dirpath, dirnames, filenames)` for every directory in the tree. It is the standard way to process files recursively without loading the whole tree into memory.

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

`os.path` works on strings. **For new code, prefer `pathlib.Path`** (see `pathlib_guide.md`). But `os.path` appears everywhere in existing codebases, so you need to read it fluently.

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

`os.system()` exists but **use `subprocess` instead** for almost everything. `os.system()` has no output capture, no error handling, and uses the shell (injection risk).

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

## Navigation

**Related:**
- [pathlib Guide](./pathlib_guide.md) — modern path manipulation
- [File Handling Theory](./theory.md) — file I/O, CSV, JSON, buffering
- [Modules and Packages](../07_modules_packages/theory.md) — how imports work
- [Virtual Environments](../07_modules_packages/virtual_environments.md) — `os.environ` for venv config
- [Production Best Practices](../19_production_best_practices/theory.md) — config from env vars
