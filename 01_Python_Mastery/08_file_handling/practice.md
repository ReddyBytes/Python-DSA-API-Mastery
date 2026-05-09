# 💻 Practice — File Handling

> **This is the master practice file.** It covers the 16 root theory chapters at survey depth.
> For deep practice on specific tools, use the subfolder files:
> - [os module →](./01_os_module/practice.md)
> - [pathlib →](./02_pathlib/practice.md)
> - [datetime →](./03_datetime/practice.md)

---

## Quick Index

| Q# | Chapter | Concept | Difficulty |
|---|---|---|---|
| [Q1](#q1) | Ch1 | Text vs binary file | 🟢 |
| [Q2](#q2) | Ch2 | All six file modes | 🟢 |
| [Q3](#q3) | Ch3 | Why `with open(...)` | 🟢 |
| [Q4](#q4) | Ch4 | read vs readline vs readlines | 🟢 |
| [Q5](#q5) | Ch4 | Memory-efficient line iteration | 🟢 |
| [Q6](#q6) | Ch5 | write() vs writelines() | 🟡 |
| [Q7](#q7) | Ch5 | print(file=f) | 🟡 |
| [Q8](#q8) | Ch6 | seek/tell round-trip | 🟡 |
| [Q9](#q9) | Ch7 | Explicit UTF-8 encoding | 🟡 |
| [Q10](#q10) | Ch7 | UnicodeDecodeError handling | 🟡 |
| [Q11](#q11) | Ch8 | csv.DictReader | 🟡 |
| [Q12](#q12) | Ch8 | csv.DictWriter | 🟡 |
| [Q13](#q13) | Ch9 | JSON load/modify/write | 🟡 |
| [Q14](#q14) | Ch9 | Custom JSON serializer | 🟡 |
| [Q15](#q15) | Ch10 | Rewrite os.path with pathlib | 🟡 |
| [Q16](#q16) | Ch10 | Recursive glob | 🟡 |
| [Q17](#q17) | Ch11 | Count ERROR lines in 10GB file | 🟡 |
| [Q18](#q18) | Ch11 | Binary chunk reading | 🟡 |
| [Q19](#q19) | Ch12 | Atomic write pattern | 🟡 |
| [Q20](#q20) | Ch13 | NamedTemporaryFile vs mkdtemp | 🟡 |
| [Q21](#q21) | Ch14 | Path traversal attack + defense | 🟡 |
| [Q22](#q22) | Ch15 | flock exclusive lock | 🟡 |
| [Q23](#q23) | Ch16 | shutil copy/move/delete | 🟡 |
| [Q24](#q24) | Ch16 | shutil.make_archive | 🟡 |
| [Q25](#q25) | Mixed | io.StringIO for testing | 🟠 |
| [Q26](#q26) | Mixed | io.BytesIO image processing | 🟠 |
| [Q27](#q27) | Mixed | Generator pipeline | 🟠 |
| [Q28](#q28) | Mixed | Config file read/write | 🟠 |
| [Q29](#q29) | Mixed | Size-based log rotation | 🟠 |
| [Q30](#q30) | Capstone | FileStore class | 🟠 |

---

<a id="q1"></a>

### Q1 🟢 · Ch1 · What is a file — Text vs binary

> 🛠️ **Solve locally:** [practice_local.py → Q1](./practice_local.py)



**Problem:** Explain the difference between a text file and a binary file. When would you use each?

<details>
<summary>💡 Hint</summary>

Think about what Python does when it reads a text file vs a binary file. One involves encoding/decoding. What kinds of data can't survive that round-trip?

</details>

<details>
<summary>✅ Answer</summary>

```python
# Text file: Python decodes bytes → str on read, encodes str → bytes on write.
# The OS also handles newline translation (\r\n → \n on Windows).
# Use for: source code, configs, CSV, JSON, logs — anything human-readable.

with open("notes.txt", "w") as f:
    f.write("Hello\n")          # stores "Hello\r\n" on Windows

# Binary file: raw bytes, no encoding, no newline translation.
# Use for: images, audio, video, PDFs, pickled objects, network packets.

with open("image.png", "rb") as f:
    header = f.read(8)          # read exact bytes — safe for any format
    print(header)               # b'\x89PNG\r\n\x1a\n'
```

**Why:** Opening a PNG in text mode corrupts it — Python tries to decode bytes as UTF-8 and will raise UnicodeDecodeError or silently mangle data. Always use `rb`/`wb` for non-text formats.

</details>

---

<a id="q2"></a>

### Q2 🟢 · Ch2 · File modes — All six modes

> 🛠️ **Solve locally:** [practice_local.py → Q2](./practice_local.py)



**Problem:** Write examples of opening a file in each mode: `r`, `w`, `a`, `x`, `r+`, `rb`. What does each do if the file already exists?

<details>
<summary>💡 Hint</summary>

Which modes truncate on open? Which raise an error if the file exists? Which raise an error if it doesn't?

</details>

<details>
<summary>✅ Answer</summary>

```python
# r  — read-only. File must exist. Cursor at start.
with open("data.txt", "r") as f:
    content = f.read()

# w  — write-only. Creates file if missing. TRUNCATES if exists (data gone).
with open("data.txt", "w") as f:
    f.write("fresh start\n")

# a  — append. Creates if missing. Cursor always at END — can't overwrite.
with open("data.txt", "a") as f:
    f.write("new line\n")

# x  — exclusive create. Raises FileExistsError if file already exists.
try:
    with open("data.txt", "x") as f:
        f.write("only if new\n")
except FileExistsError:
    print("file already exists — x mode refuses to overwrite")

# r+ — read AND write. File must exist. Does NOT truncate. Cursor at start.
with open("data.txt", "r+") as f:
    f.write("overwrite first bytes only")
    f.seek(0)
    print(f.read())

# rb — binary read. Same as r but no encoding/newline translation.
with open("image.png", "rb") as f:
    raw = f.read(16)
```

**Why:** `w` is the silent data-loss trap — it truncates immediately on open, before you write anything. Use `x` when you need to guarantee you're creating a new file.

</details>

---

<a id="q3"></a>

### Q3 🟢 · Ch3 · Context manager — Why `with open(...)`

> 🛠️ **Solve locally:** [practice_local.py → Q3](./practice_local.py)



**Problem:** Why should you always use `with open(...)` instead of `f = open(...)` + `f.close()`? What happens if an exception occurs mid-write?

<details>
<summary>💡 Hint</summary>

What does `with` guarantee that a manual `f.close()` in a try/finally does not automatically provide? Think about buffered writes and OS file descriptor limits.

</details>

<details>
<summary>✅ Answer</summary>

```python
# Bad — manual close. If an exception fires before f.close(), the file
# stays open. The write buffer may never be flushed. The OS file descriptor leaks.
f = open("out.txt", "w")
f.write("partial data")
raise RuntimeError("boom")   # f.close() never reached → buffer not flushed
f.close()

# Good — context manager guarantees __exit__ runs even on exception.
# __exit__ calls f.flush() then f.close() no matter what.
with open("out.txt", "w") as f:
    f.write("partial data")
    raise RuntimeError("boom")   # exception propagates, but file is closed cleanly
```

```python
# Demonstration: what the with statement expands to
f = open("out.txt", "w")
try:
    f.write("data")
finally:
    f.close()   # equivalent to __exit__ — always runs
```

**Why:** Leaked file descriptors cause "Too many open files" crashes in long-running processes. Unflushed buffers mean silent data loss. `with` eliminates both risks with zero extra code.

</details>

---

<a id="q4"></a>

### Q4 🟢 · Ch4 · Reading strategies — read() vs readline() vs readlines()

> 🛠️ **Solve locally:** [practice_local.py → Q4](./practice_local.py)



**Problem:** When would you use `read()`, `readline()`, and `readlines()`? What is the memory implication of `read()` on a 10GB file?

<details>
<summary>💡 Hint</summary>

`read()` loads everything. `readline()` loads one line. `readlines()` loads everything as a list. Which of these can handle a file larger than RAM?

</details>

<details>
<summary>✅ Answer</summary>

```python
# read() — loads entire file into one string. Fast for small files.
# On a 10GB file: allocates 10GB of RAM instantly. Likely OOM crash.
with open("small.txt") as f:
    content = f.read()          # entire file as one str

# read(n) — reads exactly n bytes/characters. Safe for any size.
with open("data.bin", "rb") as f:
    chunk = f.read(4096)        # 4KB at a time

# readline() — reads one line including the newline character.
# Returns "" (empty string) at EOF.
with open("log.txt") as f:
    line = f.readline()         # "2024-01-01 ERROR something\n"
    while line:
        process(line)
        line = f.readline()

# readlines() — reads all lines into a list. Same memory cost as read().
with open("small.txt") as f:
    lines = f.readlines()       # ["line1\n", "line2\n", ...]
    # Useful when you need random access by index or len(lines)
```

**Why:** `read()` and `readlines()` on large files are memory bombs. For files larger than available RAM, use `readline()` in a loop — or better yet, iterate the file object directly (Q5).

</details>

---

<a id="q5"></a>

### Q5 🟢 · Ch4 · Reading strategies — Memory-efficient line iteration

> 🛠️ **Solve locally:** [practice_local.py → Q5](./practice_local.py)



**Problem:** Write the most memory-efficient way to process each line in a file.

<details>
<summary>💡 Hint</summary>

File objects are iterators. You do not need to call any read method explicitly.

</details>

<details>
<summary>✅ Answer</summary>

```python
# Most efficient: iterate the file object directly.
# Python buffers one block at a time (typically 8KB) — constant memory regardless of file size.
with open("huge.log") as f:
    for line in f:
        line = line.rstrip("\n")
        if "ERROR" in line:
            print(line)

# Why this beats readline() in a while loop:
# - Cleaner syntax
# - Same O(1) memory behaviour
# - The file object's __next__ handles buffering internally

# Comparison of memory usage for a 10GB file:
# read()       → 10GB RAM
# readlines()  → 10GB RAM (list of strings)
# for line in f → ~8KB RAM (one read buffer)
```

**Why:** The file object implements `__iter__` and `__next__`, making it directly usable in a for loop. Python reads one internal buffer at a time — you never load more than a small chunk into memory.

</details>

---

<a id="q6"></a>

### Q6 🟡 · Ch5 · Writing — write() vs writelines()

> 🛠️ **Solve locally:** [practice_local.py → Q6](./practice_local.py)



**Problem:** Write a function that takes a list of strings and writes them to a file with newlines. Show `write()` and `writelines()` versions.

<details>
<summary>💡 Hint</summary>

`writelines()` does NOT add newlines automatically — you must include them in each string. `write()` writes exactly what you give it.

</details>

<details>
<summary>✅ Answer</summary>

```python
lines = ["apple", "banana", "cherry"]

# Version 1: write() in a loop
def write_with_write(path: str, lines: list[str]) -> None:
    with open(path, "w") as f:
        for line in lines:
            f.write(line + "\n")

# Version 2: writelines() — must include newlines yourself
def write_with_writelines(path: str, lines: list[str]) -> None:
    with open(path, "w") as f:
        f.writelines(line + "\n" for line in lines)
        # Generator keeps memory low — no intermediate list created

# Version 3: join + single write — fewest syscalls, fastest for small lists
def write_with_join(path: str, lines: list[str]) -> None:
    with open(path, "w") as f:
        f.write("\n".join(lines) + "\n")

write_with_write("out.txt", lines)
write_with_writelines("out.txt", lines)
write_with_join("out.txt", lines)
```

**Why:** `writelines()` is misnamed — it does NOT add line separators. Its advantage is accepting any iterable (including generators), avoiding a full list in memory. For large outputs, pass a generator to `writelines()`.

</details>

---

<a id="q7"></a>

### Q7 🟡 · Ch5 · Writing — print(file=f)

> 🛠️ **Solve locally:** [practice_local.py → Q7](./practice_local.py)



**Problem:** Use `print()` to write formatted output to a file.

<details>
<summary>💡 Hint</summary>

`print()` accepts a `file=` keyword argument. It also handles `sep=` and `end=` — useful for custom formatting without manual string building.

</details>

<details>
<summary>✅ Answer</summary>

```python
from datetime import datetime

records = [
    {"name": "Alice", "score": 95},
    {"name": "Bob",   "score": 87},
]

with open("report.txt", "w") as f:
    print(f"Report generated: {datetime.now().isoformat()}", file=f)
    print("-" * 40, file=f)
    for r in records:
        print(f"{r['name']:<10} {r['score']:>5}", file=f)
    print("-" * 40, file=f)

# print() with sep= and end=
with open("csv_out.txt", "w") as f:
    headers = ["name", "score", "grade"]
    print(*headers, sep=",", end="\n", file=f)
    print("Alice", 95, "A", sep=",", file=f)
```

**Why:** `print(file=f)` automatically adds a newline (`end="\n"`) and handles type conversion — no need to call `str()` on non-string values. It's convenient for human-readable reports but `csv.writer` is better for structured CSV data.

</details>

---

<a id="q8"></a>

### Q8 🟡 · Ch6 · seek/tell — seek/tell round-trip

> 🛠️ **Solve locally:** [practice_local.py → Q8](./practice_local.py)



**Problem:** Open a file, read first 10 bytes, use `tell()` to get current position, seek back to start, then read again.

<details>
<summary>💡 Hint</summary>

`tell()` returns the current byte position. `seek(0)` rewinds to the start. `seek(0, 2)` jumps to the end — what does `tell()` return there?

</details>

<details>
<summary>✅ Answer</summary>

```python
# Create a test file
with open("sample.txt", "w") as f:
    f.write("Hello, World! This is a test file.")

with open("sample.txt", "rb") as f:
    # Read first 10 bytes
    first_ten = f.read(10)
    print(f"First 10 bytes: {first_ten}")       # b'Hello, Wor'

    # tell() reports current position (byte offset from start)
    pos = f.tell()
    print(f"Current position: {pos}")            # 10

    # Read next 5 bytes
    next_five = f.read(5)
    print(f"Next 5 bytes: {next_five}")          # b'ld! T'
    print(f"Position now: {f.tell()}")           # 15

    # seek(0) rewinds to start
    f.seek(0)
    print(f"After seek(0): {f.tell()}")          # 0
    again = f.read(10)
    print(f"Read again: {again}")                # b'Hello, Wor'

    # seek(0, 2) jumps to end — 2 means SEEK_END
    f.seek(0, 2)
    file_size = f.tell()
    print(f"File size: {file_size} bytes")       # 33

    # seek to specific byte offset
    f.seek(7)
    print(f.read(5))                             # b'World'
```

**Why:** `seek`/`tell` enables random access — critical for binary formats (e.g., reading a PNG header without scanning the whole file) and for re-reading data after partial processing. Only works on seekable files (not stdin or network streams).

</details>

---

<a id="q9"></a>

### Q9 🟡 · Ch7 · Encoding — Explicit UTF-8

> 🛠️ **Solve locally:** [practice_local.py → Q9](./practice_local.py)



**Problem:** Open a UTF-8 file with explicit encoding. What happens if you open a UTF-8 file without specifying encoding on Windows?

<details>
<summary>💡 Hint</summary>

Python's default encoding is `locale.getpreferredencoding()`. On Windows this is often `cp1252`. What happens when a UTF-8 byte sequence like `é` (0xC3 0xA9) is decoded as cp1252?

</details>

<details>
<summary>✅ Answer</summary>

```python
# Always specify encoding explicitly — never rely on platform default
with open("data.txt", "w", encoding="utf-8") as f:
    f.write("Café résumé naïve\n")   # non-ASCII characters

with open("data.txt", "r", encoding="utf-8") as f:
    content = f.read()
    print(content)    # Café résumé naïve — correct

# What happens on Windows without encoding="utf-8":
# open("data.txt", "r") uses cp1252 (Windows default)
# UTF-8 multi-byte sequences for é (0xC3 0xA9) get decoded as two cp1252 chars
# Result: "CafÃ©" instead of "Café" — mojibake

# Check the platform default:
import locale
print(locale.getpreferredencoding())   # 'UTF-8' on Mac/Linux, 'cp1252' on Windows

# Best practice: always explicit
with open("file.txt", "r", encoding="utf-8") as f:
    data = f.read()

# For UTF-8 with BOM (common in Windows-generated files):
with open("file.txt", "r", encoding="utf-8-sig") as f:
    data = f.read()   # strips the BOM automatically
```

**Why:** Encoding bugs are silent — the file opens without error but the content is garbled. This is the #1 source of "works on my Mac, broken in production" bugs. Always specify `encoding="utf-8"` explicitly.

</details>

---

<a id="q10"></a>

### Q10 🟡 · Ch7 · Encoding — UnicodeDecodeError handling

> 🛠️ **Solve locally:** [practice_local.py → Q10](./practice_local.py)



**Problem:** You get a `UnicodeDecodeError` reading a file. Show 3 ways to handle it: `strict`, `ignore`, `replace`.

<details>
<summary>💡 Hint</summary>

The `errors=` parameter to `open()` controls what happens when a byte can't be decoded. Each strategy has different data implications.

</details>

<details>
<summary>✅ Answer</summary>

```python
# Create a file with mixed/invalid UTF-8 bytes
with open("messy.txt", "wb") as f:
    f.write(b"Valid text \xff\xfe and more valid text\n")
    # 0xFF 0xFE are not valid UTF-8

# Strategy 1: strict (default) — raises UnicodeDecodeError on bad bytes
try:
    with open("messy.txt", "r", encoding="utf-8", errors="strict") as f:
        content = f.read()
except UnicodeDecodeError as e:
    print(f"Strict mode error: {e}")
    # 'utf-8' codec can't decode byte 0xff in position 11

# Strategy 2: ignore — silently drops undecodable bytes
with open("messy.txt", "r", encoding="utf-8", errors="ignore") as f:
    content = f.read()
    print(repr(content))
    # 'Valid text  and more valid text\n'  — bad bytes gone silently

# Strategy 3: replace — substitutes U+FFFD (replacement character) for bad bytes
with open("messy.txt", "r", encoding="utf-8", errors="replace") as f:
    content = f.read()
    print(repr(content))
    # 'Valid text \ufffd\ufffd and more valid text\n'

# Strategy 4: latin-1 never fails — every byte 0x00–0xFF maps to a Unicode codepoint
with open("messy.txt", "r", encoding="latin-1") as f:
    content = f.read()
    print(repr(content))   # All bytes preserved, different characters

# Detect encoding before opening (requires chardet library)
import chardet
with open("unknown.txt", "rb") as f:
    raw = f.read(10_000)   # sample first 10KB
detected = chardet.detect(raw)
print(detected)   # {'encoding': 'UTF-8', 'confidence': 0.99, 'language': ''}
```

**Why:** `ignore` loses data silently — dangerous for anything financial or medical. `replace` preserves structure while marking bad bytes visibly. For log processing where occasional bad bytes are expected, `errors="replace"` is the safest default.

</details>

---

<a id="q11"></a>

### Q11 🟡 · Ch8 · CSV files — csv.DictReader

> 🛠️ **Solve locally:** [practice_local.py → Q11](./practice_local.py)



**Problem:** Use `csv.DictReader` to read a CSV with headers and print each row as a dict.

<details>
<summary>💡 Hint</summary>

`DictReader` uses the first row as keys automatically. What does it return if a row has fewer columns than headers?

</details>

<details>
<summary>✅ Answer</summary>

```python
import csv
import io

# Sample CSV content
csv_content = """name,age,city
Alice,30,New York
Bob,25,London
Charlie,35,Tokyo
"""

# Reading from a file
with open("people.csv", "w", newline="", encoding="utf-8") as f:
    f.write(csv_content)

with open("people.csv", "r", newline="", encoding="utf-8") as f:
    reader = csv.DictReader(f)
    # reader.fieldnames available after first iteration or accessing it directly
    print(f"Headers: {reader.fieldnames}")   # ['name', 'age', 'city']

    for row in reader:
        print(row)
        # {'name': 'Alice', 'age': '30', 'city': 'New York'}
        # Note: all values are strings — cast as needed
        name = row["name"]
        age  = int(row["age"])    # explicit cast to int

# Custom delimiter (e.g., TSV)
with open("data.tsv", "r", newline="") as f:
    reader = csv.DictReader(f, delimiter="\t")
    for row in reader:
        print(row)

# Using StringIO for in-memory CSV (useful in tests)
f = io.StringIO(csv_content)
reader = csv.DictReader(f)
rows = list(reader)
print(rows[0])   # {'name': 'Alice', 'age': '30', 'city': 'New York'}
```

**Why:** Always use `newline=""` when opening CSV files — this lets the `csv` module handle line endings itself, preventing double-newline bugs on Windows. All values come back as strings — you must cast numeric fields explicitly.

</details>

---

<a id="q12"></a>

### Q12 🟡 · Ch8 · CSV files — csv.DictWriter

> 🛠️ **Solve locally:** [practice_local.py → Q12](./practice_local.py)



**Problem:** Use `csv.DictWriter` to write a list of dicts to CSV with headers.

<details>
<summary>💡 Hint</summary>

You must call `writeheader()` explicitly — it is not automatic. What happens if a dict has a key not in `fieldnames`?

</details>

<details>
<summary>✅ Answer</summary>

```python
import csv

records = [
    {"name": "Alice", "age": 30, "city": "New York"},
    {"name": "Bob",   "age": 25, "city": "London"},
    {"name": "Charlie", "age": 35, "city": "Tokyo"},
]

with open("output.csv", "w", newline="", encoding="utf-8") as f:
    fieldnames = ["name", "age", "city"]
    writer = csv.DictWriter(f, fieldnames=fieldnames)

    writer.writeheader()       # writes: name,age,city
    writer.writerows(records)  # writes all rows at once

# Result in output.csv:
# name,age,city
# Alice,30,New York
# Bob,25,London
# Charlie,35,Tokyo

# Handling extra keys: extrasaction parameter
records_with_extra = [{"name": "Dave", "age": 28, "city": "Paris", "phone": "555-1234"}]

with open("output2.csv", "w", newline="", encoding="utf-8") as f:
    writer = csv.DictWriter(
        f,
        fieldnames=["name", "age", "city"],
        extrasaction="ignore"   # silently drop 'phone'; default is "raise"
    )
    writer.writeheader()
    writer.writerows(records_with_extra)

# Missing keys: use restval to fill with a default
records_partial = [{"name": "Eve", "age": 22}]   # no city
with open("output3.csv", "w", newline="", encoding="utf-8") as f:
    writer = csv.DictWriter(
        f,
        fieldnames=["name", "age", "city"],
        restval=""   # use "" for missing keys
    )
    writer.writeheader()
    writer.writerows(records_partial)
```

**Why:** `DictWriter` is safer than `writer.writerow([...])` because column order is determined by `fieldnames`, not dict insertion order. Always use `newline=""` and `encoding="utf-8"` for cross-platform compatibility.

</details>

---

<a id="q13"></a>

### Q13 🟡 · Ch9 · JSON files — Load, modify, write

> 🛠️ **Solve locally:** [practice_local.py → Q13](./practice_local.py)



**Problem:** Load a JSON file, modify a key, write it back. Use `indent=2` for pretty output.

<details>
<summary>💡 Hint</summary>

`json.load()` reads from a file object. `json.dump()` writes to a file object. `json.loads()` and `json.dumps()` work with strings — don't mix them up.

</details>

<details>
<summary>✅ Answer</summary>

```python
import json

# Create initial config file
initial_config = {
    "version": "1.0",
    "debug": False,
    "database": {
        "host": "localhost",
        "port": 5432
    },
    "allowed_hosts": ["127.0.0.1"]
}

with open("config.json", "w", encoding="utf-8") as f:
    json.dump(initial_config, f, indent=2)

# Load, modify, write back
with open("config.json", "r", encoding="utf-8") as f:
    config = json.load(f)

# Modify values
config["version"] = "1.1"
config["debug"] = True
config["allowed_hosts"].append("192.168.1.0/24")
config["database"]["port"] = 5433

# Write back with pretty formatting
with open("config.json", "w", encoding="utf-8") as f:
    json.dump(config, f, indent=2, ensure_ascii=False)
    # ensure_ascii=False preserves non-ASCII characters (é, 中文, etc.)

# Verify
with open("config.json", "r", encoding="utf-8") as f:
    print(f.read())
```

**Why:** `indent=2` makes the file human-readable and produces clean git diffs. `ensure_ascii=False` is important for internationalized data — without it, `"café"` becomes `"caf\u00e9"`. Always open JSON files with `encoding="utf-8"`.

</details>

---

<a id="q14"></a>

### Q14 🟡 · Ch9 · JSON files — Custom JSON serializer

> 🛠️ **Solve locally:** [practice_local.py → Q14](./practice_local.py)



**Problem:** Write a JSON encoder that handles `datetime` objects (serialize to ISO format string).

<details>
<summary>💡 Hint</summary>

Subclass `json.JSONEncoder` and override `default()`. The `default()` method is called for any object that isn't natively JSON serializable.

</details>

<details>
<summary>✅ Answer</summary>

```python
import json
from datetime import datetime, date
from decimal import Decimal

# Approach 1: Custom JSONEncoder subclass
class CustomEncoder(json.JSONEncoder):
    def default(self, obj):
        if isinstance(obj, datetime):
            return obj.isoformat()           # "2024-01-15T10:30:00"
        if isinstance(obj, date):
            return obj.isoformat()           # "2024-01-15"
        if isinstance(obj, Decimal):
            return float(obj)                # lose precision — consider str instead
        return super().default(obj)          # raises TypeError for unknown types

data = {
    "event": "user_signup",
    "created_at": datetime(2024, 1, 15, 10, 30, 0),
    "date_only": date(2024, 1, 15),
    "amount": Decimal("99.99"),
}

json_str = json.dumps(data, cls=CustomEncoder, indent=2)
print(json_str)
# {
#   "event": "user_signup",
#   "created_at": "2024-01-15T10:30:00",
#   "date_only": "2024-01-15",
#   "amount": 99.99
# }

# Approach 2: default= function (simpler for one-offs)
def json_default(obj):
    if isinstance(obj, (datetime, date)):
        return obj.isoformat()
    raise TypeError(f"Object of type {type(obj)} is not JSON serializable")

json_str2 = json.dumps(data, default=json_default, indent=2)

# Deserialization: parse ISO strings back to datetime
def parse_dates(obj: dict) -> dict:
    for key, value in obj.items():
        if isinstance(value, str):
            try:
                obj[key] = datetime.fromisoformat(value)
            except ValueError:
                pass
    return obj

loaded = json.loads(json_str, object_hook=parse_dates)
print(type(loaded["created_at"]))   # <class 'datetime.datetime'>
```

**Why:** Python's built-in `json` module raises `TypeError` for datetime, Decimal, UUID, and other common types. A custom encoder centralises the serialisation logic — you pass `cls=CustomEncoder` once and all nested datetimes are handled automatically.

</details>

---

<a id="q15"></a>

### Q15 🟡 · Ch10 · pathlib survey — Rewrite os.path code

> 🛠️ **Solve locally:** [practice_local.py → Q15](./practice_local.py)



**Problem:** Rewrite this `os.path` code using pathlib: `os.path.join(os.path.dirname(f), "out", os.path.basename(f))`

<details>
<summary>💡 Hint</summary>

A `Path` object supports `/` as a join operator. `parent` replaces `dirname`, `name` replaces `basename`.

</details>

<details>
<summary>✅ Answer</summary>

```python
import os
from pathlib import Path

f = "/data/input/report.csv"

# Old os.path style — verbose, string-based, error-prone
old_result = os.path.join(os.path.dirname(f), "out", os.path.basename(f))
print(old_result)   # /data/input/out/report.csv

# pathlib equivalent — object-oriented, readable
p = Path(f)
new_result = p.parent / "out" / p.name
print(new_result)   # /data/input/out/report.csv

# pathlib attribute comparison
print(p.parent)       # /data/input         (dirname)
print(p.name)         # report.csv          (basename)
print(p.stem)         # report              (no extension)
print(p.suffix)       # .csv                (extension with dot)
print(p.suffixes)     # ['.csv']            (all extensions)

# More operations that are cleaner in pathlib
print(p.exists())                      # bool — os.path.exists()
print(p.is_file())                     # bool — os.path.isfile()
print(p.resolve())                     # absolute canonical path

# Change extension
new_ext = p.with_suffix(".json")
print(new_ext)        # /data/input/report.json

# Change filename entirely
renamed = p.with_name("summary.csv")
print(renamed)        # /data/input/summary.csv
```

**Why:** `pathlib` paths are objects, not strings — you can't accidentally do `path + "/file"` and get double slashes. The `/` operator always produces a valid path. Code reads left-to-right like a real path instead of nested function calls.

</details>

---

<a id="q16"></a>

### Q16 🟡 · Ch10 · pathlib survey — Recursive glob

> 🛠️ **Solve locally:** [practice_local.py → Q16](./practice_local.py)



**Problem:** Use pathlib to find all `.json` files recursively under a directory.

<details>
<summary>💡 Hint</summary>

`Path.glob()` matches the current directory. `Path.rglob()` recurses into subdirectories. Which pattern syntax triggers recursion in `glob()`?

</details>

<details>
<summary>✅ Answer</summary>

```python
from pathlib import Path

base = Path("/data/configs")

# rglob — recursive glob, simplest syntax
json_files = list(base.rglob("*.json"))
for p in json_files:
    print(p)

# Equivalent using glob with ** — ** matches zero or more directories
json_files2 = list(base.glob("**/*.json"))

# Non-recursive: only direct children
direct_json = list(base.glob("*.json"))

# Multiple extensions — no built-in multi-ext glob, use a comprehension
all_data = [
    p for p in base.rglob("*")
    if p.suffix in {".json", ".yaml", ".toml"}
]

# Sorted by modification time — newest first
sorted_files = sorted(base.rglob("*.json"), key=lambda p: p.stat().st_mtime, reverse=True)

# Filter to files only (exclude directories named *.json — rare but possible)
files_only = [p for p in base.rglob("*.json") if p.is_file()]

# Process each file
for p in files_only:
    import json
    with p.open(encoding="utf-8") as f:
        data = json.load(f)
    print(f"{p.relative_to(base)}: {len(data)} keys")
```

**Why:** `rglob("*.json")` is more readable than `glob("**/*.json")` but both produce the same results. `rglob` returns a lazy generator — it does not load all paths into memory at once, making it safe for very deep directory trees.

</details>

---

<a id="q17"></a>

### Q17 🟡 · Ch11 · Large files — Count ERROR lines in 10GB file

> 🛠️ **Solve locally:** [practice_local.py → Q17](./practice_local.py)



**Problem:** Process a 10GB log file line by line without loading it into memory. Calculate how many lines contain "ERROR".

<details>
<summary>💡 Hint</summary>

Iterate the file object directly. How much memory does this use regardless of file size?

</details>

<details>
<summary>✅ Answer</summary>

```python
from pathlib import Path

def count_errors(log_path: str) -> int:
    """Count lines containing 'ERROR' in a large file. O(1) memory."""
    count = 0
    with open(log_path, encoding="utf-8", errors="replace") as f:
        for line in f:              # one buffer at a time (~8KB), not the whole file
            if "ERROR" in line:
                count += 1
    return count

# Usage
error_count = count_errors("/var/log/app/production.log")
print(f"Error lines: {error_count}")

# Generator version — composable and reusable
def error_lines(log_path: str):
    """Yield only lines containing ERROR."""
    with open(log_path, encoding="utf-8", errors="replace") as f:
        for line in f:
            if "ERROR" in line:
                yield line.rstrip("\n")

# Count without storing all lines
total = sum(1 for _ in error_lines("/var/log/app/production.log"))

# With progress tracking for very large files
import os

def count_errors_with_progress(log_path: str) -> int:
    file_size = os.path.getsize(log_path)
    count = 0
    bytes_read = 0

    with open(log_path, encoding="utf-8", errors="replace") as f:
        for line in f:
            bytes_read += len(line.encode("utf-8"))
            if "ERROR" in line:
                count += 1
            if bytes_read % (100 * 1024 * 1024) < len(line.encode("utf-8")):
                pct = bytes_read / file_size * 100
                print(f"\r{pct:.1f}% complete", end="", flush=True)

    print()
    return count
```

**Why:** Iterating the file object uses a fixed internal buffer (~8KB). Memory usage is constant whether the file is 1MB or 100GB. `errors="replace"` prevents crashes on occasional encoding errors in log files.

</details>

---

<a id="q18"></a>

### Q18 🟡 · Ch11 · Large files — Binary chunk reading

> 🛠️ **Solve locally:** [practice_local.py → Q18](./practice_local.py)



**Problem:** Read a binary file in 4096-byte chunks using a while loop.

<details>
<summary>💡 Hint</summary>

`f.read(n)` returns an empty `bytes` object `b""` at EOF. Use that as the sentinel for your while loop.

</details>

<details>
<summary>✅ Answer</summary>

```python
import hashlib

def read_in_chunks(file_path: str, chunk_size: int = 4096):
    """Generator that yields binary chunks from a file."""
    with open(file_path, "rb") as f:
        while True:
            chunk = f.read(chunk_size)
            if not chunk:           # b"" at EOF — falsy
                break
            yield chunk

# Usage: compute SHA-256 of a large file without loading it
def sha256_of_file(path: str) -> str:
    h = hashlib.sha256()
    for chunk in read_in_chunks(path, chunk_size=65536):  # 64KB chunks
        h.update(chunk)
    return h.hexdigest()

# Equivalent using the walrus operator (Python 3.8+) — more concise
def sha256_walrus(path: str) -> str:
    h = hashlib.sha256()
    with open(path, "rb") as f:
        while chunk := f.read(65536):
            h.update(chunk)
    return h.hexdigest()

# Copy a large file manually in chunks
def copy_in_chunks(src: str, dst: str, chunk_size: int = 65536) -> None:
    with open(src, "rb") as fsrc, open(dst, "wb") as fdst:
        while chunk := fsrc.read(chunk_size):
            fdst.write(chunk)

print(sha256_of_file("/etc/hosts"))
```

**Why:** 4096 bytes (one OS memory page) is the classic chunk size. For hashing or network transfers, 64KB–1MB chunks amortize syscall overhead better. The walrus operator (`:=`) eliminates the double `read()` call and is now the idiomatic Python 3.8+ pattern.

</details>

---

<a id="q19"></a>

### Q19 🟡 · Ch12 · Atomic writes — Atomic write pattern

> 🛠️ **Solve locally:** [practice_local.py → Q19](./practice_local.py)



**Problem:** Explain why writing directly to a file is dangerous if the process crashes mid-write. Implement an atomic write using a temp file + rename.

<details>
<summary>💡 Hint</summary>

`os.replace()` is atomic on POSIX — the old file is replaced in a single syscall with no window where the file is partially written or missing.

</details>

<details>
<summary>✅ Answer</summary>

```python
import os
import json
import tempfile
from pathlib import Path

# DANGEROUS: direct write. If crash at *, the file is half-written.
def write_direct(path: str, data: dict) -> None:
    with open(path, "w") as f:
        json.dump(data, f, indent=2)
        # * crash here = truncated JSON = corrupt config file

# SAFE: atomic write via temp file + rename
def write_atomic(path: str, data: dict) -> None:
    p = Path(path)
    # Write to a temp file in the SAME directory (important for rename to work)
    tmp_fd, tmp_path = tempfile.mkstemp(dir=p.parent, prefix=".tmp_", suffix=p.suffix)
    try:
        with os.fdopen(tmp_fd, "w", encoding="utf-8") as f:
            json.dump(data, f, indent=2)
            f.flush()
            os.fsync(f.fileno())    # flush OS write cache to disk
        # Atomic rename: if this fails, original file is untouched
        os.replace(tmp_path, path)
    except Exception:
        os.unlink(tmp_path)         # clean up temp file on failure
        raise

# Usage
config = {"version": "2.0", "debug": True}
write_atomic("/etc/myapp/config.json", config)

# Why same directory matters:
# os.replace() does an atomic rename, which is only atomic within one filesystem.
# If tmp is on /tmp (different filesystem), it becomes a copy+delete = not atomic.
```

**Why:** A process crash, power loss, or `Ctrl+C` during a direct write leaves a partially written file. Readers see corrupt data. The temp-file-then-rename pattern guarantees: the target file is either the old version or the new complete version — never a partial state.

</details>

---

<a id="q20"></a>

### Q20 🟡 · Ch13 · Temporary files — NamedTemporaryFile vs mkdtemp

> 🛠️ **Solve locally:** [practice_local.py → Q20](./practice_local.py)



**Problem:** Use `tempfile.NamedTemporaryFile` and `tempfile.mkdtemp`. When is each appropriate?

<details>
<summary>💡 Hint</summary>

`NamedTemporaryFile` auto-deletes on close by default. `mkdtemp` creates a directory — who is responsible for cleanup?

</details>

<details>
<summary>✅ Answer</summary>

```python
import tempfile
import os
import shutil
from pathlib import Path

# NamedTemporaryFile — for temporary data that needs a real path on disk
# Use when: you need to pass a path to a subprocess or library that requires a file path
with tempfile.NamedTemporaryFile(
    mode="w",
    suffix=".json",
    prefix="myapp_",
    delete=True,            # auto-delete when closed (default)
    encoding="utf-8"
) as tmp:
    tmp.write('{"key": "value"}')
    tmp.flush()
    print(f"Temp file at: {tmp.name}")   # e.g. /tmp/myapp_abc123.json
    # Pass tmp.name to an external process that reads the file
    os.system(f"cat {tmp.name}")
# File is deleted here automatically

# NamedTemporaryFile with delete=False — you manage cleanup
tmp = tempfile.NamedTemporaryFile(delete=False, suffix=".csv")
try:
    tmp.write(b"name,age\nAlice,30\n")
    tmp.close()
    # Process the file after closing it (required on Windows)
    Path(tmp.name).rename("/data/processed.csv")
finally:
    if os.path.exists(tmp.name):
        os.unlink(tmp.name)

# mkdtemp — for a temporary directory (multiple files, subprocess working dir)
# Use when: you need to extract an archive, run a subprocess with multiple I/O files
tmp_dir = tempfile.mkdtemp(prefix="myapp_work_")
try:
    # Create multiple files inside
    (Path(tmp_dir) / "input.txt").write_text("data")
    (Path(tmp_dir) / "config.json").write_text("{}")
    print(f"Working in: {tmp_dir}")
    # run subprocess here
finally:
    shutil.rmtree(tmp_dir)   # YOU must clean up mkdtemp directories
```

**Why:** `NamedTemporaryFile` is self-cleaning — ideal for single-file temp data. `mkdtemp` gives you a full directory with predictable cleanup responsibility. On Windows, `NamedTemporaryFile` cannot be read by another process while open — use `delete=False` and close it first before passing the path to external code.

</details>

---

<a id="q21"></a>

### Q21 🟡 · Ch14 · Security — Path traversal attack and defense

> 🛠️ **Solve locally:** [practice_local.py → Q21](./practice_local.py)



**Problem:** Show a path traversal attack using `../../../etc/passwd`. Write a `safe_path(base, user_input)` function that blocks it.

<details>
<summary>💡 Hint</summary>

`Path.resolve()` resolves all `..` and symlinks to a canonical absolute path. How do you verify the resolved path is still under your base directory?

</details>

<details>
<summary>✅ Answer</summary>

```python
from pathlib import Path

# THE ATTACK
# A web app serves files from /var/www/uploads/
# User requests: GET /files?name=../../../../etc/passwd
# Naive handler:
def unsafe_read(base: str, user_input: str) -> str:
    path = base + "/" + user_input          # "/var/www/uploads/../../../../etc/passwd"
    with open(path) as f:
        return f.read()                     # reads /etc/passwd — GAME OVER

# Demonstration
base = "/var/www/uploads"
attack = "../../../../etc/passwd"
import os
print(os.path.normpath(base + "/" + attack))   # /etc/passwd — attack succeeds

# THE DEFENSE
def safe_path(base: str, user_input: str) -> Path:
    """
    Resolve user_input relative to base and verify it stays within base.
    Raises ValueError on path traversal attempt.
    """
    base_path = Path(base).resolve()          # canonical, absolute
    requested  = (base_path / user_input).resolve()   # resolves all .. and symlinks

    # The resolved path must start with base_path
    try:
        requested.relative_to(base_path)      # raises ValueError if outside base
    except ValueError:
        raise ValueError(f"Path traversal blocked: {user_input!r}")

    return requested

# Tests
try:
    p = safe_path("/var/www/uploads", "../../../../etc/passwd")
except ValueError as e:
    print(e)   # Path traversal blocked: '../../../../etc/passwd'

# Valid path — allowed
p = safe_path("/var/www/uploads", "subdir/file.txt")
print(p)   # /var/www/uploads/subdir/file.txt

# Symlink attack (points outside base) — also blocked by resolve()
# ln -s /etc/passwd /var/www/uploads/evil
p = safe_path("/var/www/uploads", "evil")
# If evil is a symlink to /etc/passwd, resolve() returns /etc/passwd → blocked
```

**Why:** String-based path checks (`if "../" in user_input`) are bypassable with URL encoding (`%2e%2e/`), Unicode tricks, or symlinks. `Path.resolve()` always returns the true filesystem path — it is the only reliable defense.

</details>

---

<a id="q22"></a>

### Q22 🟡 · Ch15 · File locking — flock exclusive lock

> 🛠️ **Solve locally:** [practice_local.py → Q22](./practice_local.py)



**Problem:** Use `fcntl.flock` (or `portalocker`) to prevent two processes from writing to the same file simultaneously.

<details>
<summary>💡 Hint</summary>

`fcntl.flock` is Unix-only. `portalocker` works cross-platform. An exclusive lock (`LOCK_EX`) blocks until the lock is available. `LOCK_NB` makes it non-blocking — it raises immediately if locked.

</details>

<details>
<summary>✅ Answer</summary>

```python
import fcntl    # Unix/macOS only
import time

# Exclusive lock with fcntl (Unix/macOS)
def append_with_lock(log_path: str, message: str) -> None:
    with open(log_path, "a") as f:
        # Block until we get exclusive write lock
        fcntl.flock(f, fcntl.LOCK_EX)
        try:
            f.write(message + "\n")
            f.flush()
        finally:
            fcntl.flock(f, fcntl.LOCK_UN)   # always unlock

# Non-blocking lock — fail fast if another process holds it
def try_append(log_path: str, message: str) -> bool:
    with open(log_path, "a") as f:
        try:
            fcntl.flock(f, fcntl.LOCK_EX | fcntl.LOCK_NB)
        except BlockingIOError:
            return False    # another process has the lock
        try:
            f.write(message + "\n")
            f.flush()
            return True
        finally:
            fcntl.flock(f, fcntl.LOCK_UN)

# Cross-platform version using portalocker (pip install portalocker)
import portalocker

def append_cross_platform(log_path: str, message: str) -> None:
    with open(log_path, "a") as f:
        portalocker.lock(f, portalocker.LOCK_EX)
        try:
            f.write(message + "\n")
            f.flush()
        finally:
            portalocker.unlock(f)

# Context manager pattern with portalocker
with portalocker.Lock("data.json", timeout=5) as f:
    import json
    data = json.load(f)
    data["count"] += 1
    f.seek(0)
    json.dump(data, f)
    f.truncate()
```

**Why:** `fcntl.flock` is advisory — both processes must cooperate and use it. It does not prevent processes that ignore locks from writing. For Python-only systems this is fine; for mixed-language systems, use a dedicated lock mechanism (Redis, database row lock, or a `.lock` file with O_EXCL).

</details>

---

<a id="q23"></a>

### Q23 🟡 · Ch16 · shutil — Copy, move, delete

> 🛠️ **Solve locally:** [practice_local.py → Q23](./practice_local.py)



**Problem:** Copy a file, copy a directory tree, move a file, delete a directory tree.

<details>
<summary>💡 Hint</summary>

`shutil.copy()` vs `shutil.copy2()` — which preserves metadata? `shutil.copytree()` fails if destination already exists by default (Python < 3.8). What parameter changes this?

</details>

<details>
<summary>✅ Answer</summary>

```python
import shutil
from pathlib import Path

# Setup
Path("/tmp/demo/src").mkdir(parents=True, exist_ok=True)
Path("/tmp/demo/src/file.txt").write_text("hello")
Path("/tmp/demo/src/subdir").mkdir(exist_ok=True)
Path("/tmp/demo/src/subdir/data.json").write_text("{}")

# 1. Copy a single file — content only, no metadata
shutil.copy("/tmp/demo/src/file.txt", "/tmp/demo/file_copy.txt")

# 2. Copy a file with metadata (timestamps, permissions)
shutil.copy2("/tmp/demo/src/file.txt", "/tmp/demo/file_copy2.txt")

# 3. Copy directory tree
shutil.copytree(
    "/tmp/demo/src",
    "/tmp/demo/dst",
    dirs_exist_ok=True   # Python 3.8+: don't fail if dst exists
)

# 4. Move a file (or directory) — rename if same filesystem, copy+delete otherwise
shutil.move("/tmp/demo/file_copy.txt", "/tmp/demo/archive/file.txt")
# creates /tmp/demo/archive/ if needed? No — destination PARENT must exist.
Path("/tmp/demo/archive").mkdir(exist_ok=True)
shutil.move("/tmp/demo/file_copy2.txt", "/tmp/demo/archive/file.txt")

# 5. Delete a directory tree — no trash, gone permanently
shutil.rmtree("/tmp/demo/dst")

# Safe rmtree — ignore errors if directory doesn't exist
shutil.rmtree("/tmp/demo/nonexistent", ignore_errors=True)

# 6. Get disk usage
total, used, free = shutil.disk_usage("/")
print(f"Free: {free / (1024**3):.1f} GB")
```

**Why:** `shutil.copy()` is for simple content duplication. `shutil.copy2()` preserves `mtime` and `atime` — use it for backups. `shutil.move()` is `os.rename()` with a cross-filesystem fallback. `rmtree` is irreversible — consider moving to a backup location first for production use.

</details>

---

<a id="q24"></a>

### Q24 🟡 · Ch16 · shutil — make_archive

> 🛠️ **Solve locally:** [practice_local.py → Q24](./practice_local.py)



**Problem:** Create a `.zip` archive of a directory using `shutil.make_archive`.

<details>
<summary>💡 Hint</summary>

`make_archive(base_name, format, root_dir, base_dir)` — `base_name` is the archive path without extension, `root_dir` is where to cd before archiving.

</details>

<details>
<summary>✅ Answer</summary>

```python
import shutil
from pathlib import Path

# Setup: create a directory with files to archive
src = Path("/tmp/myproject")
src.mkdir(exist_ok=True)
(src / "README.txt").write_text("My project")
(src / "data").mkdir(exist_ok=True)
(src / "data" / "config.json").write_text('{"version": 1}')

# make_archive(base_name, format, root_dir=None, base_dir=None)
# base_name: archive file path WITHOUT extension
# format: 'zip', 'tar', 'gztar', 'bztar', 'xztar'
# root_dir: directory to change to before archiving (becomes the root inside the archive)
# base_dir: directory to archive (relative to root_dir)

archive_path = shutil.make_archive(
    base_name="/tmp/myproject_backup",   # creates /tmp/myproject_backup.zip
    format="zip",
    root_dir="/tmp",
    base_dir="myproject"                 # archive the myproject folder
)
print(f"Created: {archive_path}")        # /tmp/myproject_backup.zip

# Unpack the archive
shutil.unpack_archive("/tmp/myproject_backup.zip", "/tmp/extracted")

# Supported formats
print(shutil.get_archive_formats())
# [('bztar', ...), ('gztar', ...), ('tar', ...), ('xztar', ...), ('zip', ...)]

# Using zipfile directly for more control (add specific files, set compression)
import zipfile

with zipfile.ZipFile("/tmp/custom.zip", "w", compression=zipfile.ZIP_DEFLATED) as zf:
    for p in src.rglob("*"):
        if p.is_file():
            zf.write(p, arcname=p.relative_to(src.parent))
            # arcname controls the path inside the zip
```

**Why:** `shutil.make_archive` is the simplest one-liner for archiving a whole directory. For selective archiving (exclude certain patterns, set compression level, add a password) use `zipfile` or `tarfile` directly. `root_dir` controls what the paths look like *inside* the archive.

</details>

---

<a id="q25"></a>

### Q25 🟠 · Mixed · io.StringIO — In-memory file for testing

> 🛠️ **Solve locally:** [practice_local.py → Q25](./practice_local.py)



**Problem:** Use `io.StringIO` as an in-memory file. Show a use case: testing a function that writes to a file without touching disk.

<details>
<summary>💡 Hint</summary>

`io.StringIO` implements the full file interface — it has `read()`, `write()`, `seek()`, `tell()`, and `getvalue()`. Functions that accept a file object will accept a `StringIO` without modification.

</details>

<details>
<summary>✅ Answer</summary>

```python
import io
import csv
import json

# A production function that writes to any file-like object
def export_users_csv(users: list[dict], out_file) -> None:
    """Write user records to a CSV file-like object."""
    writer = csv.DictWriter(out_file, fieldnames=["name", "email", "role"])
    writer.writeheader()
    writer.writerows(users)

users = [
    {"name": "Alice", "email": "alice@example.com", "role": "admin"},
    {"name": "Bob",   "email": "bob@example.com",   "role": "user"},
]

# Production use: write to a real file
with open("users.csv", "w", newline="") as f:
    export_users_csv(users, f)

# Test use: write to StringIO — no disk I/O, no temp files to clean up
def test_export_users_csv():
    buffer = io.StringIO()
    export_users_csv(users, buffer)

    output = buffer.getvalue()
    lines = output.strip().split("\n")

    assert lines[0] == "name,email,role"
    assert "Alice" in lines[1]
    assert len(lines) == 3    # header + 2 data rows
    print("Test passed!")

test_export_users_csv()

# StringIO as input — simulate reading from a "file" in tests
def parse_config(f) -> dict:
    return json.load(f)

fake_file = io.StringIO('{"host": "localhost", "port": 5432}')
config = parse_config(fake_file)
print(config)   # {'host': 'localhost', 'port': 5432}

# Seeking and reading back
buf = io.StringIO()
buf.write("first line\nsecond line\n")
buf.seek(0)                  # rewind before reading
print(buf.read())            # first line\nsecond line\n
print(buf.getvalue())        # same — getvalue() works from any position
```

**Why:** `io.StringIO` makes functions that accept file objects testable without temp files. Tests run faster (no disk I/O), have no cleanup burden, and work in read-only environments (containers, CI). Design functions to accept `file-like objects` rather than `str paths` to enable this pattern.

</details>

---

<a id="q26"></a>

### Q26 🟠 · Mixed · io.BytesIO — In-memory image processing

> 🛠️ **Solve locally:** [practice_local.py → Q26](./practice_local.py)



**Problem:** Use `io.BytesIO` to process an image in memory without saving to disk.

<details>
<summary>💡 Hint</summary>

`io.BytesIO` is the binary counterpart to `io.StringIO`. Libraries like Pillow and boto3 accept file-like objects — you can download an S3 object and process it without writing to disk.

</details>

<details>
<summary>✅ Answer</summary>

```python
import io

# Basic BytesIO usage
buf = io.BytesIO()
buf.write(b"\x89PNG\r\n\x1a\n")   # PNG magic bytes
buf.write(b"\x00" * 100)          # fake image data
buf.seek(0)

header = buf.read(8)
print(header)                       # b'\x89PNG\r\n\x1a\n'
print(f"Buffer size: {len(buf.getvalue())} bytes")

# Real use case: resize image in memory (requires Pillow)
# from PIL import Image
#
# def resize_image_bytes(image_bytes: bytes, max_width: int) -> bytes:
#     """Resize an image without touching disk."""
#     input_buf = io.BytesIO(image_bytes)
#     img = Image.open(input_buf)
#
#     if img.width > max_width:
#         ratio = max_width / img.width
#         new_size = (max_width, int(img.height * ratio))
#         img = img.resize(new_size, Image.LANCZOS)
#
#     output_buf = io.BytesIO()
#     img.save(output_buf, format="JPEG", quality=85)
#     return output_buf.getvalue()

# Use case: S3 download → process → upload without temp file
# import boto3
#
# s3 = boto3.client("s3")
# buf = io.BytesIO()
# s3.download_fileobj("my-bucket", "photo.jpg", buf)   # write into BytesIO
# buf.seek(0)
# resized = resize_image_bytes(buf.read(), max_width=800)
# s3.upload_fileobj(io.BytesIO(resized), "my-bucket", "photo_thumb.jpg")

# BytesIO in tests — inject fake binary content
def extract_png_dimensions(f) -> tuple[int, int]:
    """Read width/height from PNG IHDR chunk."""
    import struct
    f.read(8)       # skip PNG signature
    f.read(4)       # skip chunk length
    f.read(4)       # skip 'IHDR' marker
    width  = struct.unpack(">I", f.read(4))[0]
    height = struct.unpack(">I", f.read(4))[0]
    return width, height

import struct
fake_png = io.BytesIO(
    b"\x89PNG\r\n\x1a\n"          # PNG signature
    + b"\x00\x00\x00\x0d"         # chunk length (13 bytes)
    + b"IHDR"                      # chunk type
    + struct.pack(">I", 1920)      # width
    + struct.pack(">I", 1080)      # height
)
w, h = extract_png_dimensions(fake_png)
print(f"{w}x{h}")   # 1920x1080
```

**Why:** `io.BytesIO` is the standard bridge between in-memory binary data and APIs that expect file objects. It eliminates temp files in image processing pipelines, reduces latency in cloud workflows (no disk round-trip), and makes binary-parsing code testable with crafted byte sequences.

</details>

---

<a id="q27"></a>

### Q27 🟠 · Mixed · Generator pipeline — CSV filter and transform

> 🛠️ **Solve locally:** [practice_local.py → Q27](./practice_local.py)



**Problem:** Write a generator pipeline that: reads a large CSV line by line → filters rows where `amount > 1000` → transforms to dicts → yields results.

<details>
<summary>💡 Hint</summary>

Each stage is a generator function that takes an iterable and yields. Chain them together: the output of one becomes the input of the next. Memory stays constant.

</details>

<details>
<summary>✅ Answer</summary>

```python
import csv
import io
from typing import Iterator

# Stage 1: Read raw lines from a large CSV (memory: one line at a time)
def read_csv_rows(file_path: str) -> Iterator[dict]:
    with open(file_path, newline="", encoding="utf-8") as f:
        reader = csv.DictReader(f)
        for row in reader:
            yield row

# Stage 2: Filter rows by amount
def filter_large_amounts(rows: Iterator[dict], threshold: float) -> Iterator[dict]:
    for row in rows:
        if float(row["amount"]) > threshold:
            yield row

# Stage 3: Transform — cast types, compute derived fields
def transform_row(rows: Iterator[dict]) -> Iterator[dict]:
    for row in rows:
        yield {
            "id":       int(row["id"]),
            "name":     row["name"].strip().title(),
            "amount":   float(row["amount"]),
            "category": row.get("category", "uncategorized").lower(),
        }

# Compose the pipeline — nothing runs until consumed
def build_pipeline(file_path: str, min_amount: float = 1000.0):
    rows       = read_csv_rows(file_path)
    filtered   = filter_large_amounts(rows, threshold=min_amount)
    transformed = transform_row(filtered)
    return transformed

# Consume the pipeline
for record in build_pipeline("transactions.csv"):
    print(record)

# Functional style using generator expressions
def pipeline_compact(file_path: str) -> Iterator[dict]:
    with open(file_path, newline="") as f:
        reader = csv.DictReader(f)
        return (
            {
                "id":     int(r["id"]),
                "amount": float(r["amount"]),
            }
            for r in reader
            if float(r["amount"]) > 1000
        )

# Test with in-memory CSV
csv_data = "id,name,amount,category\n1,Alice,500,food\n2,Bob,1500,travel\n3,Carol,2000,tech\n"
with io.StringIO(csv_data) as f:
    reader = csv.DictReader(f)
    results = [r for r in transform_row(filter_large_amounts(reader, 1000))]
    print(results)
    # [{'id': 2, 'name': 'Bob', 'amount': 1500.0, ...}, {'id': 3, ...}]
```

**Why:** Generator pipelines process one record at a time — a 10GB CSV and a 10KB CSV use the same memory. Each stage is independently testable. Composing stages is more readable than nested loops and avoids building intermediate lists.

</details>

---

<a id="q28"></a>

### Q28 🟠 · Mixed · Config file — Atomic read/write with error handling

> 🛠️ **Solve locally:** [practice_local.py → Q28](./practice_local.py)



**Problem:** Write `read_config(path)` and `write_config(path, data)` that handle JSON config files with atomic writes and proper error handling.

<details>
<summary>💡 Hint</summary>

`read_config` must handle: file not found, invalid JSON, permission error. `write_config` must be atomic and validate that `data` is JSON-serialisable before writing anything.

</details>

<details>
<summary>✅ Answer</summary>

```python
import json
import os
import tempfile
from pathlib import Path
from typing import Any

class ConfigError(Exception):
    """Raised for config read/write failures."""

def read_config(path: str | Path) -> dict:
    """
    Read a JSON config file.

    Returns: parsed dict
    Raises: ConfigError on any failure
    """
    p = Path(path)
    try:
        with p.open(encoding="utf-8") as f:
            return json.load(f)
    except FileNotFoundError:
        raise ConfigError(f"Config file not found: {p}")
    except PermissionError:
        raise ConfigError(f"Permission denied reading: {p}")
    except json.JSONDecodeError as e:
        raise ConfigError(f"Invalid JSON in {p}: {e}")
    except OSError as e:
        raise ConfigError(f"OS error reading {p}: {e}")

def write_config(path: str | Path, data: dict[str, Any]) -> None:
    """
    Write a JSON config file atomically.

    Validates JSON-serializability before touching the target file.
    Raises: ConfigError on serialization or write failure.
    """
    p = Path(path)

    # Validate serialisability BEFORE we open any file (fail fast)
    try:
        serialized = json.dumps(data, indent=2, ensure_ascii=False)
    except (TypeError, ValueError) as e:
        raise ConfigError(f"Data is not JSON-serializable: {e}")

    # Ensure parent directory exists
    p.parent.mkdir(parents=True, exist_ok=True)

    # Atomic write: temp file in same directory → rename
    tmp_fd, tmp_path = tempfile.mkstemp(dir=p.parent, prefix=".cfg_", suffix=".tmp")
    try:
        with os.fdopen(tmp_fd, "w", encoding="utf-8") as f:
            f.write(serialized)
            f.flush()
            os.fsync(f.fileno())
        os.replace(tmp_path, p)
    except OSError as e:
        try:
            os.unlink(tmp_path)
        except OSError:
            pass
        raise ConfigError(f"Failed to write config to {p}: {e}")

# Usage
try:
    config = read_config("app_config.json")
except ConfigError:
    config = {"version": "1.0", "debug": False}

config["last_run"] = "2024-01-15T10:30:00"
write_config("app_config.json", config)

# Roundtrip verification
loaded = read_config("app_config.json")
assert loaded["last_run"] == "2024-01-15T10:30:00"
print("Config roundtrip OK")
```

**Why:** Validating serializability first means the old config is never corrupted if `data` contains a non-serializable type like a `datetime`. The atomic write guarantees readers always see a complete valid JSON file.

</details>

---

<a id="q29"></a>

### Q29 🟠 · Mixed · Log rotation — Size-based rotation

> 🛠️ **Solve locally:** [practice_local.py → Q29](./practice_local.py)



**Problem:** Write a simple log writer that rotates the file when it exceeds 1MB (rename current → `.1`, start fresh).

<details>
<summary>💡 Hint</summary>

Check file size before each write using `os.path.getsize()` or `Path.stat().st_size`. Python's `logging` module has `RotatingFileHandler` built in — know when to use that vs rolling your own.

</details>

<details>
<summary>✅ Answer</summary>

```python
import os
from pathlib import Path
from datetime import datetime

class SimpleRotatingLog:
    """
    Writes to a log file and rotates it when it exceeds max_bytes.
    Keeps one backup: app.log → app.log.1
    """
    def __init__(self, path: str, max_bytes: int = 1_048_576):
        self.path = Path(path)
        self.max_bytes = max_bytes
        self.path.parent.mkdir(parents=True, exist_ok=True)

    def _rotate(self) -> None:
        """Rename current log to .1, removing old .1 if it exists."""
        backup = self.path.with_suffix(self.path.suffix + ".1")
        if backup.exists():
            backup.unlink()
        self.path.rename(backup)

    def write(self, message: str) -> None:
        """Append a timestamped message, rotating if needed."""
        # Check size before writing
        if self.path.exists() and self.path.stat().st_size >= self.max_bytes:
            self._rotate()

        timestamp = datetime.utcnow().strftime("%Y-%m-%dT%H:%M:%SZ")
        line = f"{timestamp}  {message}\n"

        with self.path.open("a", encoding="utf-8") as f:
            f.write(line)

# Usage
log = SimpleRotatingLog("/tmp/myapp/app.log", max_bytes=1_048_576)
for i in range(100):
    log.write(f"Processing record {i:04d}: status=OK latency=12ms")

# Production alternative: use logging.handlers.RotatingFileHandler (zero custom code)
import logging
from logging.handlers import RotatingFileHandler

logger = logging.getLogger("myapp")
handler = RotatingFileHandler(
    filename="/tmp/myapp/app.log",
    maxBytes=1_048_576,        # 1MB
    backupCount=5,             # keep .1 through .5
    encoding="utf-8",
)
handler.setFormatter(logging.Formatter("%(asctime)s %(levelname)s %(message)s"))
logger.addHandler(handler)
logger.setLevel(logging.DEBUG)

logger.info("Application started")
logger.error("Something went wrong: %s", "disk full")
```

**Why:** `RotatingFileHandler` is production-ready — it handles concurrent writes, configurable backup count, and integrates with the Python logging ecosystem. Roll your own only when you need behaviour the standard handler cannot provide (e.g., S3 upload on rotation, structured JSON logs).

</details>

---

<a id="q30"></a>

### Q30 🟠 · Capstone — FileStore class

> 🛠️ **Solve locally:** [practice_local.py → Q30](./practice_local.py)



**Problem:** Build a `FileStore` class: `store(key, data)` writes JSON atomically; `load(key)` reads with error handling; `list()` returns all keys; `delete(key)` removes safely. Uses pathlib throughout.

<details>
<summary>💡 Hint</summary>

Map each key to a file: `{base_dir}/{key}.json`. Use the safe_path pattern from Q21 to prevent keys like `../../../etc` from escaping the base directory.

</details>

<details>
<summary>✅ Answer</summary>

```python
import json
import os
import tempfile
from pathlib import Path
from typing import Any

class FileStoreError(Exception):
    pass

class FileStore:
    """
    A simple key-value store backed by JSON files on disk.

    - store(key, data)  → atomic write
    - load(key)         → safe read with error handling
    - list()            → all stored keys
    - delete(key)       → safe removal
    """

    def __init__(self, base_dir: str | Path) -> None:
        self.base = Path(base_dir).resolve()
        self.base.mkdir(parents=True, exist_ok=True)

    def _key_path(self, key: str) -> Path:
        """Resolve key to a Path, blocking traversal attacks."""
        if not key or "/" in key or "\\" in key or key.startswith("."):
            raise FileStoreError(f"Invalid key: {key!r}")
        candidate = (self.base / f"{key}.json").resolve()
        try:
            candidate.relative_to(self.base)
        except ValueError:
            raise FileStoreError(f"Key escapes store directory: {key!r}")
        return candidate

    def store(self, key: str, data: Any) -> None:
        """Write data as JSON atomically. Overwrites if key exists."""
        path = self._key_path(key)
        try:
            serialized = json.dumps(data, indent=2, ensure_ascii=False)
        except (TypeError, ValueError) as e:
            raise FileStoreError(f"Data for key {key!r} is not JSON-serializable: {e}")

        tmp_fd, tmp_path = tempfile.mkstemp(dir=self.base, prefix=".store_", suffix=".tmp")
        try:
            with os.fdopen(tmp_fd, "w", encoding="utf-8") as f:
                f.write(serialized)
                f.flush()
                os.fsync(f.fileno())
            os.replace(tmp_path, path)
        except OSError as e:
            try:
                os.unlink(tmp_path)
            except OSError:
                pass
            raise FileStoreError(f"Failed to store key {key!r}: {e}")

    def load(self, key: str) -> Any:
        """Read and return the stored value. Raises FileStoreError if missing."""
        path = self._key_path(key)
        if not path.exists():
            raise FileStoreError(f"Key not found: {key!r}")
        try:
            with path.open(encoding="utf-8") as f:
                return json.load(f)
        except json.JSONDecodeError as e:
            raise FileStoreError(f"Corrupt data for key {key!r}: {e}")
        except OSError as e:
            raise FileStoreError(f"Error reading key {key!r}: {e}")

    def list(self) -> list[str]:
        """Return all stored keys (sorted)."""
        return sorted(p.stem for p in self.base.glob("*.json"))

    def delete(self, key: str) -> None:
        """Delete key. No-op if key does not exist."""
        path = self._key_path(key)
        try:
            path.unlink(missing_ok=True)   # Python 3.8+: no-op if absent
        except OSError as e:
            raise FileStoreError(f"Failed to delete key {key!r}: {e}")

    def __repr__(self) -> str:
        return f"FileStore(base={self.base!r}, keys={len(self.list())})"


# Usage demonstration
store = FileStore("/tmp/my_file_store")

store.store("user:alice", {"name": "Alice", "role": "admin", "score": 95})
store.store("user:bob",   {"name": "Bob",   "role": "user",  "score": 72})
store.store("config",     {"debug": False, "max_retries": 3})

print(store.list())          # ['config', 'user:alice', 'user:bob']

alice = store.load("user:alice")
print(alice["name"])         # Alice

store.delete("user:bob")
print(store.list())          # ['config', 'user:alice']

# Error handling
try:
    store.load("nonexistent")
except FileStoreError as e:
    print(e)                 # Key not found: 'nonexistent'

try:
    store.store("../escape", {"attack": True})
except FileStoreError as e:
    print(e)                 # Invalid key: '../escape'

print(store)                 # FileStore(base=PosixPath('/tmp/my_file_store'), keys=2)
```

**Why:** This class demonstrates the full file handling toolkit: pathlib for path operations, atomic writes for safety, path traversal defense for security, proper error wrapping for a clean API, and `missing_ok=True` for idempotent deletes. It is a common pattern for lightweight local caching, test fixtures, and config management.

</details>

---

## Navigation

| | Link |
|---|---|
| Theory | [theory.md](./theory.md) |
| Cheetsheet | [cheetsheet.md](./cheetsheet.md) |
| Interview | [interview.md](./interview.md) |
| Local practice | [practice_local.py](./practice_local.py) |
| os module deep dive | [01_os_module/practice.md](./01_os_module/practice.md) |
| pathlib deep dive | [02_pathlib/practice.md](./02_pathlib/practice.md) |
| datetime deep dive | [03_datetime/practice.md](./03_datetime/practice.md) |
| Previous module | [07_modules_packages/practice.md](../07_modules_packages/practice.md) |
| Next module | [09_logging_debugging/practice.md](../09_logging_debugging/practice.md) |
