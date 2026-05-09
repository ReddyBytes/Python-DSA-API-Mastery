<a id="top"></a>
# 📂 08 — File Handling

> *"Every program eventually needs to read or write data that outlives it.*
> *Files are how your program talks to the world — past, present, and future."*

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

## 📖 Table of Contents

- [📌 Learning Priority](#learning-priority)
- [1. What Is a File, Really?](#1-what-is-a-file-really)
- [2. File Modes: The Complete Picture](#2-file-modes-the-complete-picture)
- [3. The Context Manager: Your Safety Net](#3-the-context-manager-your-safety-net)
  - [How the Context Manager Works](#how-the-context-manager-works)
- [4. Reading Strategies: Choose Wisely](#4-reading-strategies-choose-wisely)
- [5. Writing: Getting Data to Disk](#5-writing-getting-data-to-disk)
  - [Buffering and flush()](#buffering-and-flush)
- [6. File Pointer: seek() and tell()](#6-file-pointer-seek-and-tell)
- [7. Encoding: The Silent Killer](#7-encoding-the-silent-killer)
- [8. CSV Files: The Right Way](#8-csv-files-the-right-way)
- [9. JSON Files](#9-json-files)
- [10. pathlib: The Modern Way to Handle Paths](#10-pathlib-the-modern-way-to-handle-paths)
- [11. os Module — System & File Operations](#11-os-module-system-file-operations)
- [12. Large Files: Memory-Efficient Patterns](#12-large-files-memory-efficient-patterns)
  - [Pattern 1 — Line-by-Line Iteration](#pattern-1-line-by-line-iteration)
  - [Pattern 2 — Chunk Reading](#pattern-2-chunk-reading)
  - [Pattern 3 — Generator for Lazy Processing](#pattern-3-generator-for-lazy-processing)
  - [Pattern 4 — Memory-Mapped Files](#pattern-4-memory-mapped-files)
- [13. Atomic Writes: Preventing Corruption](#13-atomic-writes-preventing-corruption)
- [14. Temporary Files](#14-temporary-files)
- [15. Security: Path Traversal](#15-security-path-traversal)
- [16. File Locking for Concurrent Access](#16-file-locking-for-concurrent-access)
- [17. shutil: High-Level File Operations](#17-shutil-high-level-file-operations)
- [18. datetime — Working with Dates and Times](#18-datetime-working-with-dates-and-times)
- [19. io.StringIO and io.BytesIO — In-Memory Files](#19-iostringio-and-iobytesio-in-memory-files)
- [Key Takeaways](#key-takeaways)

<a id="learning-priority"></a>
## 📌 Learning Priority

**Must Learn** — Core concept, daily use, interview essential:
`open()` + context manager · Read/write modes · `pathlib.Path` · `json.load` / `json.dump` · CSV reading/writing

**Should Learn** — Important for real projects, comes up regularly:
`io.StringIO` / `io.BytesIO` · Binary mode (`rb`/`wb`) · `str.encode()` / `bytes.decode()` · Directory operations (`mkdir`, `glob`) · `os.environ`

**Good to Know** — Useful in specific situations:
`tempfile` module · `os.stat()` · Atomic file write patterns · `datetime` module basics

**Reference** — Know it exists, look up when needed:
`mmap` module · File locks · `os.chmod()` · Symlinks

<a id="1-what-is-a-file-really"></a>
# 1. What Is a File, Really?

At the OS level, a file is a sequence of bytes on disk.
When you "open" a file in Python, you're creating a **file descriptor** —
a handle the OS gives you to read/write that byte sequence.
The OS tracks every open file descriptor your process holds, and there is a hard limit on how many can be open at once.

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

💡 **Hint:** Always use `with open()` — it closes the file descriptor automatically even on exception, preventing OS limit exhaustion in loops.

📝 **Practice:** [file descriptor / check open-file limit →](./practice.md#q1--open--the-three-modes-you-use-every-day)

> [↑ Back to Top](#top)

<a id="2-file-modes-the-complete-picture"></a>
# 2. File Modes: The Complete Picture

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

⚠️ **Common mistake — overwriting with 'w':** Using `'w'` when you meant `'a'` silently destroys all existing content — no warning, no prompt. Use `'a'` for log files and `'x'` for output files where overwriting would be a bug.

💡 **Hint:** When in doubt: `'r'` to read existing, `'a'` to add to existing, `'x'` to create new (fails safely if it already exists).

📝 **Practice:** [file modes / classify what each mode does →](./practice.md#q2--file-modes--classify-what-each-mode-does)

> [↑ Back to Top](#top)

<a id="3-the-context-manager-your-safety-net"></a>
# 3. The Context Manager: Your Safety Net

Always use `with` for file operations. It guarantees cleanup regardless of how the block exits — normal return, exception, or anything else.

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

<a id="how-the-context-manager-works"></a>
## How the Context Manager Works

The `with` statement uses Python's **context manager protocol** — calling `__enter__` when the block starts and `__exit__` when it ends. For file objects, `__exit__` always calls `close()`, even if an exception was raised inside the block. See the full protocol at [12 — Context Managers →](../12_context_managers/theory.md).

```python
# The with statement calls:
f = open("data.txt")      # __enter__: opens file, returns file object
try:
    ...                   # your code runs here
finally:
    f.close()             # __exit__: always closes, even on exception
```

🔍 **Good to know:** The context manager protocol works for any object with `__enter__`/`__exit__`, not just files. Database connections, network sockets, and threading locks all use the same mechanism — which is why `with` works uniformly across all of them.

📝 **Practice:** [context manager / always use with →](./practice.md#q3--context-manager--always-use-with)

> [↑ Back to Top](#top)

<a id="4-reading-strategies-choose-wisely"></a>
# 4. Reading Strategies: Choose Wisely

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

**Memory impact at 1GB:**

```
read()         → 1000MB in RAM  (may crash)
readlines()    → 1000MB in RAM  (may crash)
for line in f  → ~1KB in RAM    (handles any size)
read(8192)     → 8KB in RAM     (controlled chunks)
```

⚠️ **Common mistake — read() on large files:** `f.read()` and `f.readlines()` load the ENTIRE file into RAM. A 2GB log file causes `MemoryError`. Default to `for line in f` unless you know the file is small and bounded.

💡 **Hint:** When you see `f.read()` in code review, ask "how large can this file get?" — that's the question the original author forgot to ask.

📝 **Practice:** [reading strategies / pick the right method →](./practice.md#q4--reading--all-4-strategies)

> [↑ Back to Top](#top)

<a id="5-writing-getting-data-to-disk"></a>
# 5. Writing: Getting Data to Disk

Python provides three ways to write data to files: `write()` for single strings, `writelines()` for sequences, and `print()` with `file=` for formatted output with automatic newlines.

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

⚠️ **Common mistake — missing newlines:** `write()` and `writelines()` don't add `\n` automatically. Every string you pass must include `\n` or all content runs together on one line.

<a id="buffering-and-flush"></a>
## Buffering and flush()

Python doesn't immediately write bytes to disk when you call `write()` — it accumulates them in a memory buffer first and flushes when the buffer fills or the file is closed. This is faster, but it means a crash mid-write could lose unflushed data. Use `flush()` when you need data on disk right now, without waiting for the file to close.

```python
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

💡 **Hint:** For `tail -f` style live log monitoring, call `flush()` after every write. Without it, new entries sit in the buffer and don't appear until the buffer fills (~8KB).

🔍 **Good to know:** The default buffer size is ~8KB in binary mode. In text mode connected to a terminal, Python uses line-buffering (flushes on `\n`). When writing to a file, it's always block-buffered regardless of newlines.

📝 **Practice:** [write + append / build a log file →](./practice.md#q5--write--append--build-a-log-file)

> [↑ Back to Top](#top)

<a id="6-file-pointer-seek-and-tell"></a>
# 6. File Pointer: seek() and tell()

The file pointer tracks your current read/write position inside the file. Every `read()` or `write()` call advances it automatically. `seek()` moves it manually, and `tell()` reports where it is. This lets you read from the middle of a file, re-read data, or append at a precise location — without loading the whole file into memory.

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

💡 **Hint:** In text mode, only `seek(0)` (go to beginning) and `seek(0, 2)` (go to end) are reliable. Seeking to an arbitrary byte offset in text mode can land mid-character in multi-byte UTF-8 text.

🔍 **Good to know:** Binary mode (`'rb'`) is required for reliable random-access seeking — byte positions are always well-defined in binary mode because there's no character/byte ambiguity.

📝 **Practice:** [seek + tell / random file access →](./practice.md#q6--seekand-tell--random-access)

> [↑ Back to Top](#top)

<a id="7-encoding-the-silent-killer"></a>
# 7. Encoding: The Silent Killer

Computers store bytes. Humans read characters.
**Encoding** is the mapping between them.

The challenge is that the same byte sequence can mean different characters in different encodings. `b'\xe2\x82\xac'` is `€` in UTF-8 but three garbage characters in latin-1. Python cannot know which encoding a file uses — you have to tell it. When the encoding is wrong, you get either a `UnicodeDecodeError` (hard crash) or silently corrupted data (worse — no crash, wrong output).

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

⚠️ **Common mistake — relying on system default:** Omitting `encoding=` works on your UTF-8 Linux dev machine but crashes on Windows where the default is often `cp1252`. Always specify `encoding="utf-8"` explicitly — it costs nothing and prevents production incidents.

💡 **Hint:** When writing files that other systems will read, `encoding="utf-8"` is the safe universal default. Only deviate when you know the target system requires something else (e.g., `latin-1` for old Excel CSVs).

📝 **Practice:** [encoding / read and write unicode →](./practice.md#q7--encoding--read-and-write-unicode)

> [↑ Back to Top](#top)

<a id="8-csv-files-the-right-way"></a>
# 8. CSV Files: The Right Way

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

⚠️ **Common mistake — forgetting newline="":** Opening a CSV file without `newline=""` causes the csv module to produce double line endings (`\r\r\n`) on Windows. The file looks fine on the machine that wrote it, but breaks on every other system.

💡 **Hint:** Prefer `DictReader` over plain `reader` — accessing `row["name"]` is self-documenting and survives column reordering in the source file without breaking your code.

📝 **Practice:** [csv DictReader + DictWriter / read and write structured CSV →](./practice.md#q14--csv--dictreader-and-dictwriter)

> [↑ Back to Top](#top)

<a id="9-json-files"></a>
# 9. JSON Files

The `json` module serializes Python objects to JSON text and back. Use `json.load(f)` to read from a file and `json.loads(s)` to parse a string; `json.dump(obj, f)` to write to a file and `json.dumps(obj)` to serialize to a string. The `s` in `loads`/`dumps` stands for "string" — a simple way to remember which is which.

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

💡 **Hint:** Use `indent=2` for config files that humans edit; omit `indent` for API responses or stored data (smaller file, faster parse).

🔍 **Good to know:** `ensure_ascii=False` lets non-ASCII characters (Chinese, Arabic, emojis) appear as-is in the output. Without it, `"€"` becomes `"\u20ac"` — technically valid JSON, but unreadable in a text editor.

📝 **Practice:** [json / read and write a JSON file →](./practice.md#q16--json--read-and-write-a-json-file)

> [↑ Back to Top](#top)

<a id="10-pathlib-the-modern-way-to-handle-paths"></a>
# 10. pathlib: The Modern Way to Handle Paths

`pathlib.Path` (Python 3.4+) is the modern, OO replacement for `os.path`. Instead of string operations like `os.path.join(os.path.dirname(f), "output")`, you write `Path(f).parent / "output"`. Path objects carry their own API — no more splitting strings manually to extract extensions or parent directories.

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

💡 **Hint:** The `/` operator only works when at least one side is a `Path` object. `"data" / "file.txt"` raises `TypeError` — use `Path("data") / "file.txt"`.

🔍 **Good to know:** `Path` objects are accepted anywhere `str` paths are in Python 3.6+ (most stdlib functions accept both), so you can adopt pathlib incrementally in an existing codebase without rewriting everything at once.

**Deep dive:** [pathlib → OO path operations, glob, stat, advanced patterns](./02_pathlib/theory.md)

📝 **Practice:** [pathlib / basic path operations →](./practice.md#q10--pathlib--basic-path-operations)

> [↑ Back to Top](#top)

<a id="11-os-module-system-file-operations"></a>
# 11. os Module — System & File Operations

The `os` module is Python's bridge to operating system services: environment variables, process information, and low-level filesystem operations. While `pathlib` handles path manipulation more elegantly for new code, `os` remains the standard tool for reading environment variables, walking directory trees recursively with `os.walk()`, and querying process metadata. Both modules coexist and complement each other in production code.

```python
import os

# ── Environment variables ─────────────────────────────────────────────
db_url = os.environ["DATABASE_URL"]        # raises KeyError if missing
debug  = os.environ.get("DEBUG", "false")  # safe — returns default if missing
port   = int(os.environ.get("PORT", "8080"))

# ── Directory traversal ───────────────────────────────────────────────
for root, dirs, files in os.walk("./data"):
    for filename in files:
        filepath = os.path.join(root, filename)
        print(filepath)   # walks every file in every subdirectory

# ── Low-level file operations ─────────────────────────────────────────
os.makedirs("output/reports", exist_ok=True)   # create nested dirs
os.rename("old_name.txt", "new_name.txt")       # rename or move
os.remove("temp.txt")                           # delete a file

# ── Process and system info ───────────────────────────────────────────
os.getcwd()          # current working directory
os.cpu_count()       # number of CPU cores
os.getpid()          # current process ID
```

💡 **Hint:** For path construction, prefer `pathlib.Path` over `os.path.join()` in new code — it's more readable and cross-platform. Use `os` primarily for environment variables, `os.walk()`, and process information.

**Deep dive:** [os Module → environment variables, os.walk, process info, os.path](./01_os_module/theory.md)

> [↑ Back to Top](#top)

<a id="12-large-files-memory-efficient-patterns"></a>
# 12. Large Files: Memory-Efficient Patterns

When a file is too large to fit in memory, you need a strategy that processes it in pieces. Python provides four main patterns, each suited to a different use case.

<a id="pattern-1-line-by-line-iteration"></a>
## Pattern 1 — Line-by-Line Iteration

Line iteration is the simplest memory-efficient approach: Python reads one line at a time from the OS buffer, so RAM usage stays constant regardless of file size.

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

💡 **Hint:** `line.strip()` removes both leading/trailing whitespace including the `\n`. Use `line.rstrip('\n')` if you need to preserve intentional leading spaces in the data.

<a id="pattern-2-chunk-reading"></a>
## Pattern 2 — Chunk Reading

For binary files or when you need to process data in fixed-size blocks (checksums, uploads, network transfers), read explicit chunks using `read(n)` in a loop. Each iteration pulls only `n` bytes into memory.

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

🔍 **Good to know:** `65536` (64KB) is a common chunk size — it matches most OS page sizes and gives a good balance between I/O round trips and memory use. For network-bound workloads, `8192` (8KB) is more typical.

<a id="pattern-3-generator-for-lazy-processing"></a>
## Pattern 3 — Generator for Lazy Processing

A [generator](../11_generators_iterators/theory.md#why-generators-are-lazy--the-memory-story) wraps the file reading so the caller can process records one at a time through a pipeline — without any one stage holding the whole file in memory. The `yield` statement suspends execution until the caller asks for the next record, keeping memory usage at O(1).

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

💡 **Hint:** Generators compose — you can chain `read_csv_rows()` → `filter_high_value()` → `write_to_db()` as a pipeline where each stage processes one record at a time without loading anything into a list.

<a id="pattern-4-memory-mapped-files"></a>
## Pattern 4 — Memory-Mapped Files

For random access to large files without loading them: `mmap` maps the file into virtual memory so you can seek and read any position as if the file were an array, while the OS pages only the needed bytes from disk on demand.

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

⚠️ **Common mistake — not closing mmap:** `mm.close()` must be called explicitly. `mmap` objects hold OS resources even after the file's `with` block exits. Leaving them open causes resource leaks under load.

💡 **Hint:** When unsure which pattern to use: text files → line iteration; binary files or checksums → chunk reading; CSV/record pipelines → generators; database-style random access → mmap.

📝 **Practice:** [large files / chunk reading without MemoryError →](./practice.md#q19--large-files--chunk-reading)

> [↑ Back to Top](#top)

<a id="13-atomic-writes-preventing-corruption"></a>
# 13. Atomic Writes: Preventing Corruption

What happens if your program crashes mid-write? Without atomic writes, you get a partially written file that looks valid at the OS level but contains corrupt or truncated data. The safe pattern is: write to a temp file → verify it's complete → rename it over the original. The rename (`os.replace`) is atomic on POSIX systems — it either fully succeeds or fully fails, never leaving a half-replaced file.

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

⚠️ **Common mistake — temp file on a different filesystem:** Writing the temp file to `/tmp/` and then renaming to a target on a different partition/filesystem makes `os.replace()` non-atomic (it becomes a copy + delete). Always use `dir=os.path.dirname(target)` so the temp file is on the same filesystem as the destination.

💡 **Hint:** `os.replace()` is atomic on POSIX (Linux/macOS). On Windows, it's as close to atomic as the OS allows, but not 100% guaranteed across all filesystems. For truly critical data on Windows, use a database transaction instead.

📝 **Practice:** [atomic write / safe file replacement →](./practice.md#q23--atomic-write--safe-file-replacement)

> [↑ Back to Top](#top)

<a id="14-temporary-files"></a>
# 14. Temporary Files

The `tempfile` module creates files and directories with guaranteed unique names, automatically cleaned up when the context exits. Use this instead of manually choosing a temp filename — you avoid name collisions, permission issues, and cleanup bugs.

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

💡 **Hint:** On Windows, `NamedTemporaryFile` with `delete=True` cannot be opened by another process while still open (Windows locks the file). Use `delete=False` + manual cleanup when you need to pass the filename to an external tool or subprocess.

🔍 **Good to know:** `tempfile.gettempdir()` returns the system's temp directory (`/tmp` on Linux/macOS, the value of `%TEMP%` on Windows). All temp files created by `tempfile` land here unless you specify a `dir=` argument.

📝 **Practice:** [tempfile / safe scratch files →](./practice.md#q25--tempfile--safe-scratch-files)

> [↑ Back to Top](#top)

<a id="15-security-path-traversal"></a>
# 15. Security: Path Traversal

When file paths come from users, **always validate them**. Path traversal is one of the most common file-handling vulnerabilities: an attacker supplies `../../etc/passwd` as a filename and your code opens a system file it was never meant to access. String-based checks (`if ".." in filename`) are bypassable — the only safe approach is resolving the actual filesystem path and checking it's within your allowed directory.

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

⚠️ **Common mistake — string-based path check:** Checking `if ".." in filename` is bypassable with URL encoding (`%2e%2e`), null bytes (`\x00`), or symlinks that resolve outside the directory. Only `.resolve().is_relative_to()` checks the actual resolved filesystem path.

📝 **Practice:** [security / path traversal guard →](./practice.md#q26--security--path-traversal-guard)

> [↑ Back to Top](#top)

<a id="16-file-locking-for-concurrent-access"></a>
# 16. File Locking for Concurrent Access

When multiple processes write to the same file simultaneously, writes can interleave and corrupt the file. File locks serialize access: a process acquires the lock, writes, then releases it. Other processes block at the lock acquisition until it's released.

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

🔍 **Good to know:** `fcntl.flock()` is advisory — it only blocks other processes that also call `flock()` before writing. A process that skips the lock and writes directly bypasses it entirely. For true isolation, use atomic writes (section 13) or a database.

📝 **Practice:** [file locking / safe concurrent writes →](./practice.md#q27--file-locking--safe-concurrent-writes)

> [↑ Back to Top](#top)

<a id="17-shutil-high-level-file-operations"></a>
# 17. shutil: High-Level File Operations

`shutil` provides high-level operations — copy, move, delete, archive — that work on entire files and directory trees. These are cross-platform and handle edge cases that manual file-by-file loops miss (permissions, metadata, symlinks).

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

⚠️ **Common mistake — rmtree with no safety check:** `shutil.rmtree()` permanently deletes with no recycle bin and no confirmation. One wrong variable and critical data is gone. Always verify the path in a dry-run log before calling it in production scripts.

💡 **Hint:** Use `shutil.copy2()` instead of `shutil.copy()` when timestamps matter (backup scripts, audit trails) — `copy2` preserves the original file's modification time and metadata.

📝 **Practice:** [shutil / copy, move, delete →](./practice.md#q28--shutil--copy-move-delete)

> [↑ Back to Top](#top)

<a id="18-datetime-working-with-dates-and-times"></a>
# 18. datetime — Working with Dates and Times

The `datetime` module handles all time-related operations: creating timestamps, parsing date strings, formatting output, and doing arithmetic with time. The most critical production skill is working with **timezone-aware datetimes** — naive datetimes (no timezone) cause subtle bugs when code runs across regions or when comparing timestamps from different sources.

```python
from datetime import datetime, timedelta, timezone

# ── Creating datetimes ────────────────────────────────────────────────
now_utc   = datetime.now(timezone.utc)           # timezone-aware — use in production
now_naive = datetime.now()                       # ⚠️ timezone-naive — avoid in production

# ── Parsing from string ───────────────────────────────────────────────
dt = datetime.fromisoformat("2024-03-15T14:30:00")   # Python 3.7+
dt = datetime.strptime("15/03/2024", "%d/%m/%Y")     # custom format

# ── Formatting to string ──────────────────────────────────────────────
formatted = dt.strftime("%Y-%m-%d %H:%M:%S")         # "2024-03-15 14:30:00"

# ── Arithmetic ────────────────────────────────────────────────────────
tomorrow  = now_utc + timedelta(days=1)
last_week = now_utc - timedelta(weeks=1)
diff      = datetime(2024, 12, 31) - datetime(2024, 1, 1)
print(diff.days)    # 365
```

⚠️ **Common mistake — datetime.utcnow():** `datetime.utcnow()` returns a naive datetime with no timezone info. Comparing it with timezone-aware datetimes raises `TypeError`. Use `datetime.now(timezone.utc)` instead — it returns the same UTC time but as an aware datetime.

💡 **Hint:** Store all timestamps in UTC in your database. Convert to the user's local timezone only at display time — this avoids daylight saving bugs and makes cross-region comparisons straightforward.

**Deep dive:** [datetime → timezone-aware datetimes, strftime/strptime, timedelta, pytz/zoneinfo](./03_datetime/theory.md)

> [↑ Back to Top](#top)

<a id="19-iostringio-and-iobytesio-in-memory-files"></a>
# 19. io.StringIO and io.BytesIO — In-Memory Files

Sometimes you need something that **behaves like a file** but lives entirely in memory — no disk I/O.
`StringIO` is an in-memory text file. `BytesIO` is an in-memory binary file.
Both support the same interface as real files: `read()`, `write()`, `seek()`, `tell()`.

```python
from io import StringIO, BytesIO

# StringIO — in-memory text file:
buffer = StringIO()
buffer.write("Hello\n")
buffer.write("World\n")
buffer.seek(0)              # go back to start
content = buffer.read()     # "Hello\nWorld\n"
buffer.close()

# BytesIO — in-memory binary file:
buf = BytesIO()
buf.write(b"\x89PNG\r\n")   # write bytes
buf.seek(0)
data = buf.read()            # b'\x89PNG\r\n'
```

**Why this matters — the real use cases:**

```python
# 1 — Testing code that writes to files (no temp files needed):
from io import StringIO

def write_report(f):
    f.write("Sales: 1000\n")
    f.write("Returns: 50\n")

# In your test:
output = StringIO()
write_report(output)
output.seek(0)
assert "Sales: 1000" in output.read()   # no disk involved

# 2 — Build a file in memory, then upload/send it:
import csv
from io import StringIO

output = StringIO()
writer = csv.writer(output)
writer.writerow(["name", "score"])
writer.writerow(["Alice", 95])
csv_content = output.getvalue()   # get entire contents as string
# Now send csv_content via HTTP, email, etc.

# 3 — Pass a string to a function that expects a file:
import json
from io import StringIO

def process_file(f):
    return json.load(f)

data = '{"name": "Alice", "age": 30}'
result = process_file(StringIO(data))   # works without creating a real file
```

**`getvalue()` — get entire buffer content without seeking:**

```python
buf = StringIO()
buf.write("line 1\n")
buf.write("line 2\n")
# No need to seek(0):
content = buf.getvalue()   # "line 1\nline 2\n"
```

**Key difference from real files:**
- No file path, no disk usage
- Lives in RAM — garbage collected when reference goes away
- Perfect for testing, building content in memory, or adapting string APIs

💡 **Hint:** Use `StringIO` in unit tests instead of creating temp files — faster, no cleanup needed, and tests stay self-contained.

🔍 **Good to know:** `BytesIO` is required for libraries that work in binary mode — `PIL/Pillow` for images, `zipfile` for zip archives, `requests` for HTTP uploads that accept file-like objects.

📝 **Practice:** [io.StringIO / in-memory file →](./practice.md#q18--iostringio--in-memory-file)

> [↑ Back to Top](#top)

<a id="key-takeaways"></a>
# Key Takeaways

```
• Always use `with open()` — guarantees file.close() on any exit path
• "w" mode DESTROYS existing content — double-check before using
• read() on large files = MemoryError — use line iteration or chunk reading
• Iteration (for line in f) uses O(1) memory for any file size
• Always specify encoding="utf-8" explicitly — don't rely on system default
• newline="" required with csv module to prevent double line endings on Windows
• seek(0) resets pointer to start; seek(0, 2) moves to end
• flush() forces buffer to disk; os.fsync() flushes OS-level buffer too
• Atomic write: write to temp file → os.replace() atomically — temp must be same filesystem
• pathlib.Path is the modern way — / operator, cross-platform, OO
• Use os.environ for environment variables; os.walk() for recursive traversal
• Validate user-supplied paths with .resolve().is_relative_to() — prevent traversal
• Chunk reading (read(65536)) + generators = efficient large file processing
• tempfile for safe scratch files — auto-deleted on context exit
• shutil for high-level copy/move/delete; rmtree is permanent — verify path first
• Store timestamps in UTC; use datetime.now(timezone.utc) not utcnow()
```

> [↑ Back to Top](#top)

# 🔁 Navigation

**[🏠 Back to README](../README.md)**

| Direction | Module |
|---|---|
| ⬅ Prev Module | [07 — Modules & Packages → theory.md](../07_modules_packages/theory.md) |
| ➡ Next Module | [09 — Logging & Debugging → theory.md](../09_logging_debugging/theory.md) |

**This folder:**
[theory.md](./theory.md) · [Practice](./practice.md) · [Cheat Sheet](./cheetsheet.md) · [Interview Q&A](./interview.md)

**Subfolders:**
[os Module →](./01_os_module/theory.md) · [pathlib →](./02_pathlib/theory.md) · [datetime →](./03_datetime/theory.md)

**Related modules:**
[12 — Context Managers →](../12_context_managers/theory.md) · [11 — Generators & Iterators →](../11_generators_iterators/theory.md) · [10 — Decorators →](../10_decorators/theory.md) · [07 — Modules & Packages →](../07_modules_packages/theory.md)

**Jump to specific topics in other files:**
- Context manager protocol → [12_context_managers/theory.md](../12_context_managers/theory.md)
- Generators / lazy evaluation → [11_generators_iterators/theory.md#why-generators-are-lazy--the-memory-story](../11_generators_iterators/theory.md#why-generators-are-lazy--the-memory-story)
