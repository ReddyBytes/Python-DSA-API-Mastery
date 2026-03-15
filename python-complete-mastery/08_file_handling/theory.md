# 📂 08 — File Handling
## From Opening Files to Production-Grade Data Processing

> *"Every program eventually needs to read or write data that outlives it.*
> *Files are how your program talks to the world — past, present, and future."*

---

## 🎬 The Story

You're building a data pipeline for an e-commerce company.
Every night, 50GB of transaction logs arrive as CSV files.
They need to be parsed, validated, transformed, and loaded into a database.

A junior developer writes this:

```python
data = open("transactions.csv").read()   # 50GB → MemoryError!
```

Server crashes. No one can log in. Black Friday ruined.

Understanding file handling isn't just syntax.
It's knowing how memory, disk, encoding, and concurrency interact —
and designing code that survives the real world.

---

## 🧠 Chapter 1 — What Is a File, Really?

At the OS level, a file is a sequence of bytes on disk.
When you "open" a file in Python, you're creating a **file descriptor** —
a handle the OS gives you to read/write that byte sequence.

```
MEMORY                              DISK
┌─────────────────────┐             ┌──────────────────┐
│  Python process      │  ←──────→  │  transactions.csv│
│                      │  file      │  (bytes on disk) │
│  file_obj = open()  │  descriptor │                  │
│  file_obj.read()    │             │                  │
└─────────────────────┘             └──────────────────┘

The file descriptor is like a pipe between your program and the disk.
You MUST close it when done — the OS has a limit on open file descriptors.
```

```python
import resource
soft, hard = resource.getrlimit(resource.RLIMIT_NOFILE)
print(f"Max open files: {soft}")   # typically 1024 on Linux
# If you forget to close() files in a loop, you'll hit this limit!
```

---

## 📌 Chapter 2 — File Modes: The Complete Picture

```
MODE    MEANING                  FILE EXISTS?    POSITION   TRUNCATES?
─────────────────────────────────────────────────────────────────────
'r'     Read only (default)      Must exist      Start      No
'w'     Write only               Creates if not  Start      YES ← danger!
'a'     Append                   Creates if not  End        No
'x'     Exclusive create         Must NOT exist  Start      N/A
'r+'    Read + Write             Must exist      Start      No
'w+'    Read + Write             Creates if not  Start      YES
'a+'    Read + Append            Creates if not  End        No

ADD 'b' FOR BINARY:
'rb'    Read binary              Must exist
'wb'    Write binary             Creates / truncates
'ab'    Append binary

ADD 't' FOR EXPLICIT TEXT (default when no 'b'):
'rt'    Read text (same as 'r')
'wt'    Write text (same as 'w')
```

```python
# ⚠️ The "w" mode DESTROYS existing content:
with open("important.txt", "w") as f:
    f.write("new content")
# The previous content of important.txt is GONE.

# ✅ Use "a" to add without destroying:
with open("log.txt", "a") as f:
    f.write("new log entry\n")

# ✅ Use "x" to prevent accidental overwrite:
try:
    with open("output.json", "x") as f:   # fails if file already exists
        json.dump(data, f)
except FileExistsError:
    print("Output file already exists — refusing to overwrite")
```

---

## 🔧 Chapter 3 — The Context Manager: Your Safety Net

Always use `with` for file operations. It guarantees cleanup.

```python
# ❌ DANGEROUS — what if an exception happens before close()?
f = open("data.txt")
data = f.read()
process(data)     # ← if THIS raises, f.close() never runs!
f.close()         # ← never reached

# ✅ SAFE — context manager guarantees close() on any exit path:
with open("data.txt") as f:
    data = f.read()
    process(data)   # ← even if this raises, f.close() is called

# Multiple files at once:
with open("input.txt") as infile, open("output.txt", "w") as outfile:
    for line in infile:
        outfile.write(line.upper())
```

### What happens inside `with open(...)`:

```python
# The with statement calls:
f = open("data.txt")      # __enter__: opens file, returns file object
try:
    ...                   # your code runs here
finally:
    f.close()             # __exit__: always closes, even on exception
```

---

## 📖 Chapter 4 — Reading Strategies: Choose Wisely

```
METHOD          RETURNS         LOADS INTO MEMORY      USE WHEN
──────────────────────────────────────────────────────────────────────
read()          str/bytes       ENTIRE FILE            Small files only
read(n)         str/bytes       n bytes/chars          Chunked reading
readline()      str             One line               One-at-a-time
readlines()     list of str     ALL lines as list      Small files, need list
for line in f   iterator        One line at a time     Large files ← best
```

```python
# ── read() — entire file at once ─────────────────────────────────────
with open("config.json") as f:
    content = f.read()            # returns one big string
    # ⚠️ 1GB file → 1GB in RAM

# ── readline() — one line ────────────────────────────────────────────
with open("data.txt") as f:
    line1 = f.readline()          # "first line\n"
    line2 = f.readline()          # "second line\n"
    line3 = f.readline()          # "" ← empty string means EOF

# ── readlines() — all lines as list ──────────────────────────────────
with open("small.txt") as f:
    lines = f.readlines()         # ["line1\n", "line2\n", "line3\n"]
    # ⚠️ still loads everything into memory

# ── Iteration — most memory efficient ────────────────────────────────
with open("huge.log") as f:
    for line in f:                # reads ONE line at a time
        process(line.strip())     # line includes \n — use .strip()
```

### Memory Comparison

```
FILE SIZE: 1GB

read()         → 1000MB in RAM  (may crash)
readlines()    → 1000MB in RAM  (may crash)
for line in f  → ~1KB in RAM    (handles any size)
read(8192)     → 8KB in RAM     (controlled chunks)
```

---

## ✍️ Chapter 5 — Writing: Getting Data to Disk

```python
# ── write() — write a string ─────────────────────────────────────────
with open("output.txt", "w") as f:
    f.write("Hello, World!\n")    # ⚠️ No automatic newline — you add \n
    f.write("Second line\n")

# ── writelines() — write a list ──────────────────────────────────────
lines = ["Alice,25\n", "Bob,30\n", "Carol,28\n"]
with open("users.txt", "w") as f:
    f.writelines(lines)           # ⚠️ Also no automatic newlines!

# ── print() to file ──────────────────────────────────────────────────
with open("report.txt", "w") as f:
    print("Report Title", file=f)       # ← adds \n automatically
    print(f"Total: {total}", file=f)
```

### Buffering and `flush()`

```python
# Python doesn't immediately write to disk — it buffers in memory first.
# This is faster but means data might not be on disk yet.

with open("live.log", "a") as f:
    f.write("Starting process...\n")
    f.flush()    # ← force write to disk NOW (before close)
    long_running_process()
    f.write("Done!\n")
    # close() also flushes automatically

# Real use case: log files you're watching with `tail -f`
# Without flush(), new writes won't appear until buffer fills up.

# Force immediate disk write:
import os
with open("critical.log", "a") as f:
    f.write("Payment processed\n")
    f.flush()
    os.fsync(f.fileno())   # ← even flushes OS-level buffer to hardware
```

---

## 🎯 Chapter 6 — File Pointer: `seek()` and `tell()`

The file pointer tracks your current position in the file.

```python
with open("data.txt", "r+") as f:
    print(f.tell())         # 0 — at the beginning

    content = f.read(5)     # reads 5 characters
    print(content)          # "Hello"
    print(f.tell())         # 5 — pointer moved forward

    f.seek(0)               # go back to beginning
    print(f.tell())         # 0

    f.seek(0, 2)            # seek to END (2 = SEEK_END)
    print(f.tell())         # file size in bytes

    f.seek(10)              # go to byte position 10
    f.seek(5, 1)            # move 5 bytes FORWARD from current position (1 = SEEK_CUR)
    f.seek(-3, 2)           # 3 bytes BEFORE end
```

```
SEEK WHENCE VALUES:
  0 = SEEK_SET — absolute position (default)
  1 = SEEK_CUR — relative to current position
  2 = SEEK_END — relative to end of file
```

```python
# Use case: read last N lines efficiently:
def tail(filename, n=10):
    with open(filename, "rb") as f:
        f.seek(0, 2)              # go to end
        size = f.tell()
        f.seek(max(0, size - n * 200))   # estimate: go back ~200 bytes/line
        lines = f.read().decode().splitlines()
        return lines[-n:]         # return last n lines
```

---

## 🔤 Chapter 7 — Encoding: The Silent Killer

Computers store bytes. Humans read characters.
**Encoding** is the mapping between them.

```
"Hello"  →  UTF-8  →  b'\x48\x65\x6c\x6c\x6f'
"नमस्ते"  →  UTF-8  →  b'\xe0\xa4\xa8\xe0\xa4...' (3 bytes per character)
"€"      →  UTF-8  →  b'\xe2\x82\xac'  (3 bytes)
"€"      →  latin-1  →  UnicodeDecodeError!  (latin-1 doesn't know €)
```

```python
# ⚠️ Common production bug: system default encoding != file encoding
with open("report.txt", "r") as f:   # uses system default (often UTF-8 on Linux)
    data = f.read()                   # UnicodeDecodeError if file is latin-1!

# ✅ Always specify encoding explicitly:
with open("report.txt", "r", encoding="utf-8") as f:
    data = f.read()

with open("legacy.csv", "r", encoding="latin-1") as f:   # Windows legacy
    data = f.read()

with open("windows.txt", "r", encoding="utf-8-sig") as f:  # handles BOM
    data = f.read()


# ── The errors parameter ──────────────────────────────────────────────
# What to do when a character can't be decoded:

open("file.txt", encoding="utf-8", errors="strict")      # default: raise error
open("file.txt", encoding="utf-8", errors="ignore")       # skip bad bytes
open("file.txt", encoding="utf-8", errors="replace")      # replace with ?
open("file.txt", encoding="utf-8", errors="backslashreplace")  # \xNN notation


# ── Detecting encoding (when you don't know): ─────────────────────────
# pip install chardet
import chardet

with open("mystery.txt", "rb") as f:
    raw = f.read()
    result = chardet.detect(raw)
    print(result)    # {'encoding': 'ISO-8859-1', 'confidence': 0.73, ...}

with open("mystery.txt", encoding=result["encoding"]) as f:
    data = f.read()
```

---

## 📊 Chapter 8 — CSV Files: The Right Way

Never parse CSV manually with `split(",")` — quoted fields contain commas!

```python
import csv


# ── Reading ───────────────────────────────────────────────────────────

# csv.reader — rows as lists:
with open("users.csv", newline="", encoding="utf-8") as f:
    reader = csv.reader(f)
    header = next(reader)           # ['name', 'email', 'age']
    for row in reader:
        name, email, age = row      # ['Alice', 'alice@mail.com', '25']

# csv.DictReader — rows as dicts (column name = key):
with open("users.csv", newline="", encoding="utf-8") as f:
    reader = csv.DictReader(f)
    for row in reader:
        print(row["name"], row["email"])   # {'name': 'Alice', 'email': '...'}


# ── Writing ───────────────────────────────────────────────────────────

# csv.writer:
with open("output.csv", "w", newline="", encoding="utf-8") as f:
    writer = csv.writer(f)
    writer.writerow(["name", "email", "age"])      # header
    writer.writerow(["Alice", "alice@mail.com", 25])
    writer.writerows([
        ["Bob",   "bob@mail.com",   30],
        ["Carol", "carol@mail.com", 28],
    ])

# csv.DictWriter:
with open("output.csv", "w", newline="", encoding="utf-8") as f:
    fieldnames = ["name", "email", "age"]
    writer = csv.DictWriter(f, fieldnames=fieldnames)
    writer.writeheader()
    writer.writerow({"name": "Alice", "email": "alice@mail.com", "age": 25})
    writer.writerows([
        {"name": "Bob", "email": "bob@mail.com", "age": 30},
    ])


# ── Why newline="" is required ─────────────────────────────────────────
# csv module handles line endings itself.
# Without newline="", Python's text mode adds extra \r on Windows!
# Always use newline="" with csv module.


# ── Custom delimiters ─────────────────────────────────────────────────
csv.reader(f, delimiter="\t")        # TSV (tab-separated)
csv.reader(f, delimiter="|")         # pipe-delimited
csv.reader(f, quotechar="'")         # custom quote character
```

---

## 📦 Chapter 9 — JSON Files

```python
import json


# ── Reading ───────────────────────────────────────────────────────────

# From file:
with open("config.json", encoding="utf-8") as f:
    config = json.load(f)        # file → Python dict/list

# From string:
data = json.loads('{"name": "Alice", "age": 25}')   # str → Python


# ── Writing ───────────────────────────────────────────────────────────

# To file:
with open("output.json", "w", encoding="utf-8") as f:
    json.dump(data, f, indent=2, ensure_ascii=False)
    # indent=2 → pretty-printed
    # ensure_ascii=False → allows non-ASCII chars (Hindi, Chinese, etc.)

# To string:
json_str = json.dumps(data, indent=2)


# ── Type mapping ──────────────────────────────────────────────────────
# Python  ←→  JSON
# dict    ←→  object {}
# list    ←→  array []
# str     ←→  string ""
# int     ←→  number
# float   ←→  number
# True    ←→  true
# False   ←→  false
# None    ←→  null


# ── Custom types ─────────────────────────────────────────────────────
from datetime import datetime, date

class DateTimeEncoder(json.JSONEncoder):
    def default(self, obj):
        if isinstance(obj, (datetime, date)):
            return obj.isoformat()
        return super().default(obj)

data = {"created": datetime.now(), "name": "Alice"}
json_str = json.dumps(data, cls=DateTimeEncoder)
# {"created": "2025-03-08T14:30:00.123456", "name": "Alice"}


# ── Large JSON files — streaming ──────────────────────────────────────
# json.load() loads entire file into memory!
# For large files with many records, use ijson:
# pip install ijson

import ijson
with open("large.json", "rb") as f:
    for record in ijson.items(f, "item"):   # streams one item at a time
        process(record)
```

---

## 🏠 Chapter 10 — `pathlib`: The Modern Way to Handle Paths

`pathlib.Path` (Python 3.4+) is the modern, OO replacement for `os.path`.

```python
from pathlib import Path


# ── Creating paths ───────────────────────────────────────────────────
p = Path("data/users/export.csv")
p = Path.home() / "Documents" / "report.pdf"   # ← / operator joins paths!
p = Path.cwd() / "output"


# ── Path information ──────────────────────────────────────────────────
p = Path("data/users/export.csv")

print(p.name)         # "export.csv"
print(p.stem)         # "export"
print(p.suffix)       # ".csv"
print(p.suffixes)     # [".csv"]
print(p.parent)       # Path("data/users")
print(p.parts)        # ('data', 'users', 'export.csv')
print(p.is_absolute()) # False


# ── File operations ───────────────────────────────────────────────────
p = Path("output/report.txt")

p.exists()            # True/False
p.is_file()           # True if it's a file
p.is_dir()            # True if it's a directory

p.parent.mkdir(parents=True, exist_ok=True)   # create parent dirs

p.write_text("Hello, World!\n", encoding="utf-8")   # write string
p.write_bytes(b"binary data")                        # write bytes

content = p.read_text(encoding="utf-8")   # read string
raw     = p.read_bytes()                  # read bytes

p.rename(Path("output/final_report.txt"))  # rename/move
p.unlink()                                 # delete file
p.unlink(missing_ok=True)                  # delete if exists (3.8+)


# ── Directory operations ──────────────────────────────────────────────
d = Path("data")

d.mkdir(exist_ok=True)            # create directory
d.mkdir(parents=True, exist_ok=True)  # create with parents

list(d.iterdir())                 # list contents
list(d.glob("*.csv"))             # glob matching
list(d.rglob("**/*.py"))          # recursive glob
list(d.glob("**/*.json"))         # all JSON files recursively

import shutil
shutil.rmtree(d)                  # delete directory recursively


# ── Cross-platform path separator ─────────────────────────────────────
# ❌ WRONG: hardcoded slash (breaks on Windows):
path = "data/users/" + filename

# ✅ RIGHT: pathlib handles it:
path = Path("data") / "users" / filename   # uses \\ on Windows, / on Unix
```

---

## ⚡ Chapter 11 — Large Files: Memory-Efficient Patterns

### Pattern 1 — Line-by-Line Iteration

```python
def count_errors(logfile: str) -> int:
    """Count error lines in a log file of any size."""
    count = 0
    with open(logfile, encoding="utf-8") as f:
        for line in f:          # reads one line at a time
            if "ERROR" in line:
                count += 1
    return count
```

### Pattern 2 — Chunk Reading

```python
def compute_checksum(filepath: str) -> str:
    """SHA256 checksum of any size file without loading it all."""
    import hashlib
    sha256 = hashlib.sha256()

    with open(filepath, "rb") as f:
        while chunk := f.read(65536):   # 64KB chunks (walrus operator)
            sha256.update(chunk)

    return sha256.hexdigest()
```

### Pattern 3 — Generator for Lazy Processing

```python
def read_csv_rows(filepath: str):
    """Generator: yields one row dict at a time, memory = O(1)."""
    import csv
    with open(filepath, newline="", encoding="utf-8") as f:
        reader = csv.DictReader(f)
        for row in reader:
            yield row    # caller processes one row, then we fetch the next


# Usage — processes 50GB file with constant memory:
for row in read_csv_rows("transactions.csv"):
    if float(row["amount"]) > 10000:
        flag_for_review(row)
```

### Pattern 4 — Memory-Mapped Files

For random access to large files without loading them:

```python
import mmap

with open("huge_binary.dat", "r+b") as f:
    mm = mmap.mmap(f.fileno(), 0)   # map entire file
    # Access any position without reading the whole file:
    mm.seek(1_000_000)
    chunk = mm.read(100)
    mm[500] = 0xFF                   # write at position 500
    mm.close()
# Useful for databases, indexes, large binary formats
```

---

## 🔒 Chapter 12 — Atomic Writes: Preventing Corruption

What happens if your program crashes mid-write?

```python
# ❌ DANGEROUS — crash mid-write = partially written file:
with open("config.json", "w") as f:
    json.dump(new_config, f)   # if power cut here, file is truncated/corrupted!

# ✅ ATOMIC WRITE — all or nothing:
import os
import tempfile
import json

def atomic_write_json(filepath: str, data: dict) -> None:
    """Write JSON atomically: file is either fully updated or unchanged."""
    dirpath = os.path.dirname(os.path.abspath(filepath))

    # Write to a temporary file in the SAME directory (important for rename atomicity):
    fd, tmp_path = tempfile.mkstemp(dir=dirpath, suffix=".tmp")
    try:
        with os.fdopen(fd, "w", encoding="utf-8") as f:
            json.dump(data, f, indent=2)
            f.flush()
            os.fsync(f.fileno())   # ensure OS writes to disk

        os.replace(tmp_path, filepath)   # atomic rename — either succeeds fully or fails
    except Exception:
        os.unlink(tmp_path)   # clean up temp file on error
        raise


# Pathlib version:
from pathlib import Path

def atomic_write(path: Path, content: str) -> None:
    tmp = path.with_suffix(".tmp")
    tmp.write_text(content, encoding="utf-8")
    tmp.replace(path)    # atomic on POSIX systems
```

---

## 🛡️ Chapter 13 — Temporary Files

```python
import tempfile
from pathlib import Path


# ── Named temporary file ───────────────────────────────────────────────
with tempfile.NamedTemporaryFile(
    mode="w",
    suffix=".csv",
    delete=True,         # delete on close (default True)
    encoding="utf-8"
) as tmp:
    tmp.write("name,age\nAlice,25\n")
    tmp.flush()
    process_file(tmp.name)    # tmp.name = "/tmp/tmpXXXXXX.csv"
# File deleted automatically when context exits


# ── Temporary directory ────────────────────────────────────────────────
with tempfile.TemporaryDirectory() as tmpdir:
    tmpdir_path = Path(tmpdir)
    output = tmpdir_path / "results.json"
    output.write_text(json.dumps(data))
    process(output)
# Entire directory + contents deleted automatically


# ── Non-context-manager usage ──────────────────────────────────────────
tmp = tempfile.NamedTemporaryFile(delete=False, suffix=".csv")
tmp.close()   # close but don't delete yet
try:
    process_large_file(tmp.name)
finally:
    os.unlink(tmp.name)   # delete manually
```

---

## 🛡️ Chapter 14 — Security: Path Traversal

When file paths come from users, **always validate them**.

```python
# ⚠️ VULNERABLE — path traversal attack:
def serve_file(user_filename: str):
    with open(f"/var/www/uploads/{user_filename}") as f:
        return f.read()

# Attacker sends: user_filename = "../../etc/passwd"
# Opens: /var/www/uploads/../../etc/passwd = /etc/passwd  ← SECURITY BREACH


# ✅ SAFE — validate that the resolved path is within the allowed directory:
from pathlib import Path

UPLOAD_DIR = Path("/var/www/uploads").resolve()

def serve_file_safe(user_filename: str) -> str:
    # Resolve symlinks and ".." components:
    requested = (UPLOAD_DIR / user_filename).resolve()

    # Check that the resolved path is actually inside UPLOAD_DIR:
    if not requested.is_relative_to(UPLOAD_DIR):
        raise PermissionError(f"Access denied: {user_filename}")

    if not requested.exists():
        raise FileNotFoundError(f"File not found: {user_filename}")

    return requested.read_text(encoding="utf-8")
```

---

## 🔁 Chapter 15 — File Locking for Concurrent Access

When multiple processes write to the same file simultaneously:

```python
# ── fcntl (POSIX only — Linux/macOS) ─────────────────────────────────
import fcntl

with open("shared.log", "a") as f:
    fcntl.flock(f, fcntl.LOCK_EX)    # acquire exclusive lock (blocks until available)
    try:
        f.write("log entry\n")
    finally:
        fcntl.flock(f, fcntl.LOCK_UN)   # release lock


# ── portalocker (cross-platform, pip install portalocker) ─────────────
import portalocker

with open("shared.log", "a") as f:
    portalocker.lock(f, portalocker.LOCK_EX)
    f.write("log entry\n")
    portalocker.unlock(f)


# ── In practice — production logging ──────────────────────────────────
# Don't write to files directly from multiple processes.
# Use Python's logging module (thread-safe) or a centralized log aggregator
# (Logstash, Fluentd, CloudWatch) instead.
```

---

## 📦 Chapter 16 — `shutil`: High-Level File Operations

```python
import shutil
from pathlib import Path


# ── Copy ──────────────────────────────────────────────────────────────
shutil.copy("source.txt", "dest.txt")           # copy file
shutil.copy2("source.txt", "dest.txt")          # copy + preserve metadata
shutil.copytree("src_dir/", "dest_dir/")        # copy entire directory tree


# ── Move ──────────────────────────────────────────────────────────────
shutil.move("old/path.txt", "new/path.txt")     # move or rename
shutil.move("old_dir/", "new_dir/")             # move directory


# ── Delete ────────────────────────────────────────────────────────────
shutil.rmtree("dir_to_delete/")                  # delete directory recursively


# ── Disk usage ────────────────────────────────────────────────────────
usage = shutil.disk_usage("/")
print(f"Total: {usage.total / 1e9:.1f} GB")
print(f"Used:  {usage.used  / 1e9:.1f} GB")
print(f"Free:  {usage.free  / 1e9:.1f} GB")


# ── Archive ───────────────────────────────────────────────────────────
shutil.make_archive("backup_2025", "zip", "my_folder/")   # → backup_2025.zip
shutil.unpack_archive("backup_2025.zip", "restored/")
```

---

## 🎯 Key Takeaways

```
• Always use `with open()` — guarantees file.close() on any exit path
• "w" mode DESTROYS existing content — double-check before using
• read() on large files = MemoryError — use line iteration or chunk reading
• Iteration (for line in f) uses O(1) memory for any file size
• Always specify encoding="utf-8" explicitly — don't rely on system default
• newline="" required with csv module to prevent double line endings on Windows
• seek(0) resets pointer to start; seek(0, 2) moves to end
• flush() forces buffer to disk; os.fsync() flushes OS-level buffer too
• Atomic write: write to temp file → os.replace() atomically
• pathlib.Path is the modern way — / operator, cross-platform, OO
• Validate user-supplied paths with .resolve().is_relative_to() — prevent traversal
• Chunk reading (read(65536)) + generators = efficient large file processing
• tempfile for safe scratch files — auto-deleted on context exit
• shutil for high-level copy/move/delete operations
```

---

## 🔁 Navigation

| | |
|---|---|
| ⬅️ Previous | [07 — Modules & Packages](../07_modules_packages/theory.md) |
| 📖 Interview | [interview.md](./interview.md) |
| ⚡ Cheatsheet | [cheatsheet.md](./cheatsheet.md) |
| ➡️ Next | [09 — Logging & Debugging](../09_logging_debugging/theory.md) |

---

**[🏠 Back to README](../README.md)**

**Prev:** [← Modules Packages — Interview Q&A](../07_modules_packages/interview.md) &nbsp;|&nbsp; **Next:** [Cheat Sheet →](./cheatsheet.md)

**Related Topics:** [Cheat Sheet](./cheatsheet.md) · [Pathlib Guide](./pathlib_guide.md) · [Interview Q&A](./interview.md)
