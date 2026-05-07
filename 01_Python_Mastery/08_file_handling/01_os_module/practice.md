# 💻 Practice — 01_os_module

> Work through these in order. Green = build fundamentals. Yellow = real patterns. Orange = production scenarios.

---

## Quick Index

| # | Difficulty | Topic | Skill |
|---|---|---|---|
| [Q1](#q1--osenviron--read-set-get-with-default) | 🟢 | os.environ | Read, set, get with default |
| [Q2](#q2--osgetcwd--oschdir--navigate-the-working-directory) | 🟢 | os.getcwd / os.chdir | Navigate the working directory |
| [Q3](#q3--oslistdir--osmakedirs--list-and-create-directories) | 🟢 | os.listdir / os.makedirs | List and create directories |
| [Q4](#q4--ospathjoin--cross-platform-path-builder) | 🟡 | os.path.join | Cross-platform path builder |
| [Q5](#q5--ospathexists--isfile--isdir--path-classifier) | 🟡 | os.path.exists/isfile/isdir | Path classifier |
| [Q6](#q6--ospathdirname--basename--splitext--decompose-a-path) | 🟡 | os.path.dirname/basename/splitext | Decompose a path |
| [Q7](#q7--oswalk--find-all-py-files-recursively) | 🟡 | os.walk | Find all .py files recursively |
| [Q8](#q8--osrename--osremove--safe-rename-and-delete) | 🟡 | os.rename / os.remove | Safe rename and delete |
| [Q9](#q9--osstat--ospathgetsize--file-metadata) | 🟡 | os.stat / os.path.getsize | File metadata |
| [Q10](#q10--ospath-vs-pathlib--rewrite-with-pathlib) | 🟡 | os.path vs pathlib | Rewrite with pathlib |
| [Q11](#q11--osscandir--find-large-files-efficiently) | 🟠 | os.scandir | Find large files efficiently |
| [Q12](#q12--capstone--archive-old-log-files) | 🟠 | Capstone | Archive old log files |

---

### Q1 🟢 · os.environ — Read, Set, Get with Default

> 🛠️ **Solve locally:** [practice_local.py → Q1](./practice_local.py)

**Problem:** Read the `HOME` environment variable. Then set a custom variable called `APP_ENV` to `"production"`. Finally, use `os.environ.get()` to read a variable called `DB_PORT` that doesn't exist, returning `"5432"` as the default. Print all three results.

<details>
<summary>💡 Hint</summary>

`os.environ["HOME"]` reads an existing var. `os.environ["APP_ENV"] = "..."` sets a var. `os.environ.get("KEY", "default")` reads with a fallback and never raises `KeyError`.
</details>

<details>
<summary>✅ Answer</summary>

```python
import os

# Read an existing env var
home = os.environ["HOME"]
print(f"HOME: {home}")

# Set a custom env var (lives for this process only)
os.environ["APP_ENV"] = "production"
print(f"APP_ENV: {os.environ['APP_ENV']}")

# Get with default — DB_PORT not set, returns fallback
db_port = os.environ.get("DB_PORT", "5432")
print(f"DB_PORT: {db_port}")
```

**Why:** `os.environ["KEY"]` raises `KeyError` if missing — use it only for vars you know exist. `.get("KEY", "default")` is the safe pattern for optional config with a sensible fallback.
</details>

---

### Q2 🟢 · os.getcwd / os.chdir — Navigate the Working Directory

> 🛠️ **Solve locally:** [practice_local.py → Q2](./practice_local.py)

**Problem:** Print the current working directory. Change to `/tmp`. Print the new working directory. Then change back to the original directory.

<details>
<summary>💡 Hint</summary>

Save the original directory with `os.getcwd()` before changing it, so you can restore it at the end with another `os.chdir()` call.
</details>

<details>
<summary>✅ Answer</summary>

```python
import os

# Save original
original = os.getcwd()
print(f"Start: {original}")

# Move to /tmp
os.chdir("/tmp")
print(f"After chdir: {os.getcwd()}")

# Move back
os.chdir(original)
print(f"Restored: {os.getcwd()}")
```

**Why:** Always save and restore `cwd` when changing directories in a script — otherwise code that runs later and uses relative paths will silently break.
</details>

---

### Q3 🟢 · os.listdir / os.makedirs — List and Create Directories

> 🛠️ **Solve locally:** [practice_local.py → Q3](./practice_local.py)

**Problem:** List all entries in `/tmp`. Then create the nested directory structure `/tmp/myapp/data/raw` using a single call. Use `exist_ok=True` so the call is safe to run more than once.

<details>
<summary>💡 Hint</summary>

`os.listdir(path)` returns a list of names (not full paths). `os.makedirs(path, exist_ok=True)` creates all intermediate directories and does not raise an error if they already exist.
</details>

<details>
<summary>✅ Answer</summary>

```python
import os

# List directory contents (names only)
entries = os.listdir("/tmp")
print(f"Entries in /tmp: {entries[:5]} ...")  # show first 5

# Create nested directories — one call, idempotent
os.makedirs("/tmp/myapp/data/raw", exist_ok=True)
print("Created: /tmp/myapp/data/raw")

# Verify
print(os.path.isdir("/tmp/myapp/data/raw"))  # → True
```

**Why:** `os.makedirs` vs `os.mkdir`: `mkdir` only works if the parent already exists. `makedirs` builds the entire chain. `exist_ok=True` makes it idempotent — safe to call on every startup.
</details>

---

### Q4 🟡 · os.path.join — Cross-Platform Path Builder

> 🛠️ **Solve locally:** [practice_local.py → Q4](./practice_local.py)

**Problem:** Build the path `/data/projects/myapp/config/settings.yaml` by joining its components with `os.path.join()`. Then build the same path starting from `__file__` (the current script), going up one level to a `config` folder, and targeting `settings.yaml`.

<details>
<summary>💡 Hint</summary>

`os.path.join` accepts any number of arguments. To go "up" from a file, use `os.path.dirname(os.path.abspath(__file__))` to get the script's directory, then join from there. You can also use `".."` as a component and resolve it with `os.path.abspath()`.
</details>

<details>
<summary>✅ Answer</summary>

```python
import os

# Build a path from components — works on Windows too (uses \ there)
path = os.path.join("/data", "projects", "myapp", "config", "settings.yaml")
print(path)
# → /data/projects/myapp/config/settings.yaml

# Build a path relative to THIS script's location
script_dir = os.path.dirname(os.path.abspath(__file__))
config_path = os.path.join(script_dir, "config", "settings.yaml")
print(config_path)
# → /path/to/this/script/config/settings.yaml
```

**Why:** Never concatenate paths with `"/" +` — it breaks on Windows where the separator is `\`. `os.path.join()` always uses the correct separator for the current OS.
</details>

---

### Q5 🟡 · os.path.exists/isfile/isdir — Path Classifier

> 🛠️ **Solve locally:** [practice_local.py → Q5](./practice_local.py)

**Problem:** Write a function `classify_path(path)` that returns `"file"`, `"dir"`, or `"missing"` depending on what the path points to. Test it on `/etc/hosts`, `/tmp`, and `/tmp/does_not_exist_xyz`.

<details>
<summary>💡 Hint</summary>

Check `os.path.isfile()` first (most specific), then `os.path.isdir()`, then fall through to `"missing"`. Note: `os.path.exists()` returns `True` for both files and directories.
</details>

<details>
<summary>✅ Answer</summary>

```python
import os

def classify_path(path):
    """Return 'file', 'dir', or 'missing' for a given path."""
    if os.path.isfile(path):
        return "file"
    elif os.path.isdir(path):
        return "dir"
    else:
        return "missing"

print(classify_path("/etc/hosts"))             # → file
print(classify_path("/tmp"))                   # → dir
print(classify_path("/tmp/does_not_exist_xyz"))# → missing
```

**Why:** `os.path.exists()` is true for both files and directories. Use `isfile()` and `isdir()` when you need to distinguish them. Always check before operating on a path — don't rely on try/except for control flow in the normal case.
</details>

---

### Q6 🟡 · os.path.dirname/basename/splitext — Decompose a Path

> 🛠️ **Solve locally:** [practice_local.py → Q6](./practice_local.py)

**Problem:** Given the path `"/data/reports/q3.csv"`, use `os.path` functions to extract: the directory, the full filename, the filename without extension, and the extension alone. Print each component on its own line.

<details>
<summary>💡 Hint</summary>

`os.path.dirname()` gives the directory. `os.path.basename()` gives the filename. `os.path.splitext()` returns a `(name, extension)` tuple where extension includes the dot.
</details>

<details>
<summary>✅ Answer</summary>

```python
import os

path = "/data/reports/q3.csv"

directory  = os.path.dirname(path)          # → /data/reports
filename   = os.path.basename(path)         # → q3.csv
name, ext  = os.path.splitext(filename)     # → ("q3", ".csv")

print(f"Directory : {directory}")
print(f"Filename  : {filename}")
print(f"Name      : {name}")
print(f"Extension : {ext}")
```

**Why:** `splitext` always keeps the dot with the extension (`".csv"` not `"csv"`). This matters when reconstructing paths: `name + ".json"` would double-dot without it. Use `splitext` any time you want to change a file's extension.
</details>

---

### Q7 🟡 · os.walk — Find All .py Files Recursively

> 🛠️ **Solve locally:** [practice_local.py → Q7](./practice_local.py)

**Problem:** Write a function `find_python_files(root)` that walks a directory tree and prints the full path of every `.py` file found. Skip any directories named `__pycache__` or `.git`. Test it on a real directory on your machine.

<details>
<summary>💡 Hint</summary>

In the `os.walk` loop, `dirs[:] = [...]` (in-place slice assignment) controls which subdirectories get visited. Modifying `dirs` without `[:]` has no effect — it replaces the local reference but doesn't affect walk's internal state.
</details>

<details>
<summary>✅ Answer</summary>

```python
import os

def find_python_files(root):
    """Recursively find all .py files, skipping pycache and .git."""
    for dirpath, dirnames, filenames in os.walk(root):
        # Prune directories we don't want to descend into — IN PLACE
        dirnames[:] = [
            d for d in dirnames
            if d not in ("__pycache__", ".git")
        ]
        for filename in filenames:
            if filename.endswith(".py"):
                print(os.path.join(dirpath, filename))

# Test on current directory
find_python_files(".")
```

**Why:** `dirnames[:] = [...]` modifies the list in place, which tells `os.walk` to skip those subdirectories entirely. Without `[:]`, you'd just rebind the local variable and walk would still descend into every directory.
</details>

---

### Q8 🟡 · os.rename / os.remove — Safe Rename and Delete

> 🛠️ **Solve locally:** [practice_local.py → Q8](./practice_local.py)

**Problem:** Write two functions: `safe_rename(src, dst)` that renames a file only if the source exists, and `safe_delete(path)` that deletes a file only if it exists. Both should print a message indicating what happened.

<details>
<summary>💡 Hint</summary>

Check `os.path.isfile(src)` before renaming — not just `os.path.exists()` — because you don't want to rename a directory. For delete, use `os.remove()` (works on files only) or catch `FileNotFoundError`.
</details>

<details>
<summary>✅ Answer</summary>

```python
import os

def safe_rename(src, dst):
    """Rename src to dst only if src exists."""
    if os.path.isfile(src):
        os.rename(src, dst)
        print(f"Renamed: {src} → {dst}")
    else:
        print(f"Skipped rename: {src} not found")

def safe_delete(path):
    """Delete file at path only if it exists."""
    if os.path.isfile(path):
        os.remove(path)
        print(f"Deleted: {path}")
    else:
        print(f"Skipped delete: {path} not found")

# Test
safe_rename("/tmp/old.txt", "/tmp/new.txt")   # only renames if old.txt exists
safe_delete("/tmp/new.txt")                    # only deletes if new.txt exists
```

**Why:** `os.remove()` raises `FileNotFoundError` if the file is missing. Checking first is cleaner than try/except when "file not found" is a normal, expected state. Use `os.replace()` instead of `os.rename()` on Windows for atomic overwrites.
</details>

---

### Q9 🟡 · os.stat / os.path.getsize — File Metadata

> 🛠️ **Solve locally:** [practice_local.py → Q9](./practice_local.py)

**Problem:** Write a function `file_info(path)` that prints the file size in KB and the last-modified timestamp as a human-readable datetime string. Use both `os.path.getsize()` and `os.stat()` to demonstrate both approaches.

<details>
<summary>💡 Hint</summary>

`os.path.getsize(path)` returns bytes directly. `os.stat(path).st_mtime` returns a Unix timestamp (float). Convert it with `datetime.datetime.fromtimestamp()`.
</details>

<details>
<summary>✅ Answer</summary>

```python
import os
import datetime

def file_info(path):
    """Print file size and last-modified time."""
    if not os.path.isfile(path):
        print(f"Not a file: {path}")
        return

    # Size — two equivalent approaches
    size_bytes = os.path.getsize(path)          # quick shortcut
    size_bytes2 = os.stat(path).st_size         # same via stat object
    assert size_bytes == size_bytes2

    # Last modified time
    mtime_ts = os.stat(path).st_mtime           # Unix timestamp (float)
    mtime_dt = datetime.datetime.fromtimestamp(mtime_ts)

    print(f"File  : {path}")
    print(f"Size  : {size_bytes / 1024:.2f} KB")
    print(f"Mtime : {mtime_dt.strftime('%Y-%m-%d %H:%M:%S')}")

file_info("/etc/hosts")
```

**Why:** `os.path.getsize()` is a convenience wrapper around `os.stat().st_size`. Use `stat()` when you need multiple metadata fields at once — it only makes one syscall.
</details>

---

### Q10 🟡 · os.path vs pathlib — Rewrite with pathlib

> 🛠️ **Solve locally:** [practice_local.py → Q10](./practice_local.py)

**Problem:** The snippet below uses `os.path` throughout. Rewrite it using `pathlib.Path` to produce identical results.

```python
import os
base = os.path.dirname(os.path.abspath(__file__))
config = os.path.join(base, "config", "settings.yaml")
name, ext = os.path.splitext(os.path.basename(config))
exists = os.path.exists(config)
print(base, config, name, ext, exists)
```

<details>
<summary>💡 Hint</summary>

`Path(__file__).parent` replaces `dirname(abspath(__file__))`. The `/` operator replaces `os.path.join()`. `.stem` and `.suffix` replace `splitext`. `.exists()` is a method on the Path object.
</details>

<details>
<summary>✅ Answer</summary>

```python
from pathlib import Path

base   = Path(__file__).parent                     # os.path.dirname(abspath(__file__))
config = base / "config" / "settings.yaml"         # os.path.join(...)
name   = config.stem                               # splitext → name part
ext    = config.suffix                             # splitext → extension part
exists = config.exists()                           # os.path.exists(...)

print(base, config, name, ext, exists)
```

**Why:** `pathlib` treats paths as objects rather than strings. The `/` operator is readable and explicit. `.stem` and `.suffix` are properties rather than a function returning a tuple. For new code, `pathlib` is almost always cleaner — but `os.path` is still everywhere in legacy codebases, so you need both.
</details>

---

### Q11 🟠 · os.scandir — Find Large Files Efficiently

> 🛠️ **Solve locally:** [practice_local.py → Q11](./practice_local.py)

**Problem:** Write a function `find_large_files(directory, min_bytes)` that returns a list of `(name, size_in_MB)` tuples for every file in `directory` (non-recursive) that exceeds `min_bytes` in size. Use `os.scandir()` rather than `os.listdir()` + `os.stat()`. Explain why `scandir` is faster.

<details>
<summary>💡 Hint</summary>

`os.scandir()` returns `DirEntry` objects. Each `DirEntry` has a `.stat()` method and an `.is_file()` method. The key performance advantage: on most OSes, `scandir` gets the stat info in the same syscall as the directory listing — `listdir + stat` makes a separate syscall per file.
</details>

<details>
<summary>✅ Answer</summary>

```python
import os

def find_large_files(directory, min_bytes=1_000_000):
    """
    Return (name, size_MB) for all files in directory exceeding min_bytes.
    Uses os.scandir() — gets stat info in the same syscall as the listing.
    """
    results = []
    with os.scandir(directory) as entries:
        for entry in entries:
            if entry.is_file():
                size = entry.stat().st_size
                if size > min_bytes:
                    results.append((entry.name, size / 1_000_000))
    return sorted(results, key=lambda x: x[1], reverse=True)

# Example: find files > 1 MB in /usr/bin
large = find_large_files("/usr/bin", min_bytes=1_000_000)
for name, size_mb in large[:5]:
    print(f"{name}: {size_mb:.2f} MB")
```

**Why:** `os.listdir()` returns only names — you then need a separate `os.stat()` call per file. `os.scandir()` returns `DirEntry` objects that cache the stat data gathered during the directory scan. On a directory with 10,000 files, this can be 2–10x faster because it avoids 10,000 individual syscalls.
</details>

---

### Q12 🟠 · Capstone — Archive Old Log Files

> 🛠️ **Solve locally:** [practice_local.py → Q12](./practice_local.py)

**Problem:** Write a function `archive_old_logs(log_dir, archive_dir, days=7)` that:
1. Walks `log_dir` recursively
2. Finds all files ending in `.log`
3. Checks if each file's last-modified time is more than `days` days ago
4. Moves qualifying files to `archive_dir`, preserving their relative sub-path
5. Creates any needed subdirectories in `archive_dir` with `exist_ok=True`
6. Prints a summary: how many files were moved, total bytes archived

<details>
<summary>💡 Hint</summary>

Use `os.stat(path).st_mtime` for modification time. Compare against `time.time() - (days * 86400)`. Use `os.path.relpath(filepath, log_dir)` to get the relative path, then `os.path.join(archive_dir, relpath)` for the destination. `os.makedirs(dest_dir, exist_ok=True)` before moving.
</details>

<details>
<summary>✅ Answer</summary>

```python
import os
import time
import shutil

def archive_old_logs(log_dir, archive_dir, days=7):
    """
    Move .log files older than `days` days from log_dir to archive_dir,
    preserving subdirectory structure.
    """
    cutoff = time.time() - (days * 86400)
    moved_count = 0
    moved_bytes = 0

    for dirpath, dirnames, filenames in os.walk(log_dir):
        for filename in filenames:
            if not filename.endswith(".log"):
                continue

            src_path = os.path.join(dirpath, filename)
            mtime    = os.stat(src_path).st_mtime

            if mtime < cutoff:
                # Preserve relative subdirectory structure in archive
                rel_path  = os.path.relpath(src_path, log_dir)
                dest_path = os.path.join(archive_dir, rel_path)
                dest_dir  = os.path.dirname(dest_path)

                os.makedirs(dest_dir, exist_ok=True)
                file_size = os.path.getsize(src_path)
                shutil.move(src_path, dest_path)

                moved_count += 1
                moved_bytes += file_size
                print(f"  Archived: {rel_path}")

    print(f"\nSummary: {moved_count} files moved, {moved_bytes / 1024:.1f} KB archived")

# Example usage (won't run without real dirs):
# archive_old_logs("/var/log/myapp", "/var/log/myapp/archive", days=7)
```

**Why:** `os.path.relpath()` is the key — it converts an absolute path back into a path relative to a root, which lets you mirror the exact subdirectory structure in the archive. `shutil.move()` handles the actual move (works across filesystems, unlike `os.rename()`).
</details>

---

## 🔁 Navigation

| | |
|---|---|
| ⬅️ Back to Module | [08_file_handling/theory.md](../theory.md) |
| 📖 Theory | [theory.md](./theory.md) |
| ➡️ Next Subfolder | [02_pathlib →](../02_pathlib/theory.md) |

---

**Related:** [02_pathlib](../02_pathlib/theory.md) · [03_datetime](../03_datetime/theory.md)
