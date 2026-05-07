# 🛤️ pathlib — Object-Oriented File Paths

> `pathlib` treats file paths as objects rather than raw strings — so instead of `os.path.join(os.path.dirname(f), "output")` you write `Path(f).parent / "output"`.
> It's the difference between working with addresses as opaque strings vs having an Address object with `.street`, `.city`, `.zip` properties.

---

## 📌 Learning Priority

**Must Learn** — Replace os.path in all new code:
`Path()` · `/` operator for joining · `.name` · `.parent` · `.suffix` · `.read_text()` · `.write_text()` · `.exists()` · `.mkdir()`

**Should Learn** — Filesystem operations:
`.glob()` · `.rglob()` · `.iterdir()` · `.rename()` · `.unlink()` · `.stat()` · `.resolve()`

**Good to Know** — Advanced patterns:
`.open()` · `.with_suffix()` · `.with_name()` · `Path.home()` · `Path.cwd()`

**Reference** — When working with legacy code:
`os.fspath()` · `str(path)` conversion · `Path(os.path.expanduser("~"))`

---

## 🎬 Why pathlib Over `os.path`?

Think of `os.path` like navigating a city using raw GPS coordinates written as strings — you have to manually parse and concatenate them. `pathlib` gives you a map object instead: you can ask it for the street name, the district, or walk one step up toward the root — all without string splitting. The code below shows the same five operations, old way vs new way.

```python
# Old way (os.path — string-based, verbose):
import os
path = os.path.join(os.path.expanduser("~"), "Documents", "report.pdf")
dirname  = os.path.dirname(path)
filename = os.path.basename(path)
name     = os.path.splitext(filename)[0]
ext      = os.path.splitext(filename)[1]
exists   = os.path.exists(path)

# New way (pathlib — OO, readable, cross-platform):
from pathlib import Path
path     = Path.home() / "Documents" / "report.pdf"
dirname  = path.parent
filename = path.name
name     = path.stem
ext      = path.suffix
exists   = path.exists()
```

---

## 🔧 Creating Path Objects

A `Path` object is just a wrapper around a string — but the moment you create one, you gain the full API. You can hand it a relative string, an absolute string, or build it piece-by-piece with the `/` operator, which is overloaded to mean "join this segment onto me."

```python
from pathlib import Path

# From string:
p = Path("data/users/export.csv")
p = Path("/absolute/path/to/file.txt")
p = Path("C:/Users/Alice/file.txt")      # Windows absolute

# From parts:
p = Path("data") / "users" / "export.csv"   # / operator joins!

# Special paths:
p = Path.home()         # /home/username  or  C:/Users/username
p = Path.cwd()          # current working directory
p = Path(".")           # current directory
p = Path("..")          # parent directory

# Absolute:
p = Path("relative.txt").resolve()        # converts to absolute + resolves symlinks
p = Path("relative.txt").absolute()       # converts to absolute (no symlink resolution)
```

---

## 📊 Path Properties

If a path is like a postal address, its properties are the individual fields on the envelope — building number, street, city, country, postcode. `pathlib` exposes each one as a named attribute rather than forcing you to split strings by `/` or `.`.

```python
p = Path("/home/alice/projects/myapp/src/main.py")

p.name          # "main.py"             ← filename with extension
p.stem          # "main"                ← filename without extension
p.suffix        # ".py"                 ← extension (with dot)
p.suffixes      # [".py"]               ← list of all suffixes
p.parent        # Path("/home/alice/projects/myapp/src")
p.parents       # [src, myapp, projects, alice, home, /]  ← all ancestors
p.parts         # ('/', 'home', 'alice', ..., 'main.py')
p.anchor        # "/"                   ← root (or drive on Windows: "C:\\")
p.drive         # ""  (on Linux/Mac)    ← "C:" on Windows
p.root          # "/"
p.is_absolute() # True
p.is_relative_to("/home/alice")  # True (Python 3.9+)
```

---

## 🔍 File System Queries

Before you read or write a file, you often need to ask the filesystem: does this thing exist? Is it a file or a folder? `pathlib` exposes these checks as plain English methods rather than constants or flag integers, so the code reads like a sentence.

```python
p = Path("data/report.csv")

p.exists()          # True if path exists (file OR directory)
p.is_file()         # True if path is a regular file
p.is_dir()          # True if path is a directory
p.is_symlink()      # True if path is a symbolic link
p.is_mount()        # True if path is a mount point

p.stat()            # os.stat_result (size, times, permissions)
p.stat().st_size    # file size in bytes
p.stat().st_mtime   # last modification time (Unix timestamp)

import os
os.access(p, os.R_OK)   # can we read?
os.access(p, os.W_OK)   # can we write?
```

---

## 📖 Reading and Writing

For small files, `pathlib` gives you single-line read and write without a context manager — think of it like a notepad app that opens, reads, and closes the file for you in one action. For anything that needs appending or line-by-line streaming, drop into `.open()` as normal.

```python
p = Path("report.txt")

# Read:
text  = p.read_text(encoding="utf-8")         # read entire file as str
data  = p.read_bytes()                          # read entire file as bytes

# Write (OVERWRITES — use carefully):
p.write_text("content\n", encoding="utf-8")    # write str to file
p.write_bytes(b"binary data")                   # write bytes to file

# Append (pathlib has no direct append — use open):
with p.open("a", encoding="utf-8") as f:
    f.write("appended line\n")

# Open for reading in pathlib:
with p.open("r", encoding="utf-8") as f:
    for line in f:
        print(line.strip())
```

---

## 📁 Directory Operations

Creating directories with `os.makedirs` meant remembering two keyword arguments and the exact function name. `pathlib` makes the equivalent feel natural — `.mkdir()` is a method on the path itself, and the two flags map directly to the two questions you would actually ask: "what if the parents don't exist?" and "what if it already exists?"

```python
d = Path("output/reports")

# Create:
d.mkdir()                              # create dir (fails if exists or parent missing)
d.mkdir(exist_ok=True)                 # create, no error if already exists
d.mkdir(parents=True, exist_ok=True)   # create with all parent dirs

# List contents:
list(d.iterdir())                      # all items (files + subdirs)
[p for p in d.iterdir() if p.is_file()]   # only files
[p for p in d.iterdir() if p.is_dir()]    # only subdirectories

# Glob (pattern matching):
list(d.glob("*.csv"))                  # all .csv files in d (not recursive)
list(d.glob("**/*.csv"))               # all .csv files recursively
list(d.rglob("*.py"))                  # rglob = recursive glob (same as glob("**/*.py"))
list(d.glob("data_*.json"))            # pattern: data_anything.json

# Sorted:
sorted(d.glob("*.csv"))
sorted(d.iterdir(), key=lambda p: p.stat().st_mtime)   # by modification time
```

---

## ✏️ Manipulating Paths

Sometimes you want a path that is almost identical to an existing one — same directory, different name, or same name, different extension. Rather than rebuilding a string from scratch, `pathlib` lets you call `.with_suffix()` or `.with_name()` to produce a modified copy without touching the original.

```python
p = Path("data/report.csv")

# Change parts:
p.with_name("summary.csv")      # data/summary.csv
p.with_stem("summary")           # data/summary.csv  (Python 3.9+)
p.with_suffix(".json")           # data/report.json
p.with_suffix("")                # data/report  (remove extension)

# Build related paths:
p.parent / "archive" / p.name   # data/archive/report.csv
```

---

## 🔄 File Operations

Renaming and deleting files in `pathlib` follows the same pattern as the rest of the API — the operation is a method on the path object. For moves across filesystems or directory copies, `shutil` is still required since `pathlib` handles single-path operations only.

```python
p = Path("old_name.txt")
q = Path("new_name.txt")
d = Path("backup/")

# Rename / Move:
p.rename(q)                      # rename (within same filesystem)
p.replace(q)                     # rename and overwrite if target exists
import shutil
shutil.move(str(p), str(d))      # move to different directory

# Copy:
import shutil
shutil.copy(p, q)                # copy file
shutil.copy2(p, q)               # copy + preserve metadata
shutil.copytree(p, q)            # copy directory tree

# Delete:
p.unlink()                        # delete file (error if not exists)
p.unlink(missing_ok=True)         # delete file (no error if not exists) — 3.8+
shutil.rmtree(d)                  # delete directory recursively

# Touch (create empty or update mtime):
p.touch()                         # creates if not exists, updates mtime if exists
p.touch(exist_ok=True)
```

---

## 🔒 Security — Resolving Safe Paths

Imagine your web app lets users download files by name. Without validation, a user could supply `../../etc/passwd` and walk right out of your uploads directory. `.resolve()` collapses all the `..` components into a real absolute path, and `.is_relative_to()` then checks whether that resolved path still lives inside the directory you intended — blocking the escape before it reaches the filesystem.

```python
SAFE_DIR = Path("/var/www/uploads").resolve()

def validate_path(user_input: str) -> Path:
    """Ensure user-supplied path stays within SAFE_DIR."""
    try:
        resolved = (SAFE_DIR / user_input).resolve()
    except (ValueError, OSError):
        raise PermissionError("Invalid path")

    # is_relative_to() checks that resolved starts with SAFE_DIR:
    if not resolved.is_relative_to(SAFE_DIR):
        raise PermissionError(f"Path escapes allowed directory: {user_input}")

    return resolved

# Examples:
validate_path("uploads/user.csv")       # → /var/www/uploads/uploads/user.csv ✓
validate_path("../../etc/passwd")       # → PermissionError ✓
validate_path("../etc/passwd")          # → PermissionError ✓
```

---

## 🔁 Common Recipes

These short snippets cover the patterns you will reach for repeatedly in real projects — finding files, measuring directories, ensuring output paths exist before writing, and batch-renaming. Each one is a self-contained idiom worth memorising.

```python
from pathlib import Path
import shutil

# ── Find all Python files in a project ─────────────────────────────────
py_files = list(Path("src").rglob("*.py"))
print(f"Found {len(py_files)} Python files")

# ── Get latest modified file ───────────────────────────────────────────
latest = max(Path("logs").glob("*.log"), key=lambda p: p.stat().st_mtime)

# ── Calculate directory size ───────────────────────────────────────────
def dir_size(path: Path) -> int:
    return sum(f.stat().st_size for f in path.rglob("*") if f.is_file())

print(f"Size: {dir_size(Path('data')) / 1e6:.1f} MB")

# ── Ensure output directory exists before writing ─────────────────────
output = Path("results/2025/march/report.csv")
output.parent.mkdir(parents=True, exist_ok=True)
output.write_text("name,score\nAlice,95\n", encoding="utf-8")

# ── Rename all .txt files to .md ──────────────────────────────────────
for f in Path("docs").glob("*.txt"):
    f.rename(f.with_suffix(".md"))

# ── Copy file with timestamp suffix ───────────────────────────────────
from datetime import datetime
src = Path("config.json")
backup = src.with_stem(f"{src.stem}_{datetime.now().strftime('%Y%m%d_%H%M%S')}")
shutil.copy2(src, backup)

# ── Walk directory tree (pathlib version of os.walk) ──────────────────
for path in Path("project").rglob("*"):
    if path.is_file():
        rel = path.relative_to("project")
        print(f"{rel}  ({path.stat().st_size} bytes)")
```

---

## 🆚 pathlib vs os.path Quick Reference

When you are reading legacy code or converting it, this table maps every common `os.path` call to its `pathlib` equivalent.

```
TASK                        os.path                     pathlib
──────────────────────────────────────────────────────────────────────────
Join paths                  os.path.join(a, b)          Path(a) / b
Get filename                os.path.basename(p)         p.name
Get directory               os.path.dirname(p)          p.parent
Get extension               os.path.splitext(p)[1]      p.suffix
Get name no ext             os.path.splitext(p)[0]...   p.stem
File exists                 os.path.exists(p)           p.exists()
Is file                     os.path.isfile(p)           p.is_file()
Is directory                os.path.isdir(p)            p.is_dir()
Absolute path               os.path.abspath(p)          p.resolve()
Home directory              os.path.expanduser("~")     Path.home()
Current directory           os.getcwd()                 Path.cwd()
Create directory            os.makedirs(p, exist_ok=True) p.mkdir(parents=True, exist_ok=True)
Delete file                 os.unlink(p)                p.unlink()
Read text                   open(p).read()              p.read_text()
Write text                  open(p,"w").write(s)        p.write_text(s)
```

---

## 🔁 Navigation

| | |
|---|---|
| ⬅️ Back to Module | [08_file_handling/theory.md](../theory.md) |
| 💻 Practice | [practice.md](./practice.md) |
| ⬅️ Prev Subfolder | [01_os_module ←](../01_os_module/theory.md) |
| ➡️ Next Subfolder | [03_datetime →](../03_datetime/theory.md) |

---

**Related:** [01_os_module](../01_os_module/theory.md) · [03_datetime](../03_datetime/theory.md)
