# 🎯 File Handling — Interview Questions

> *"File handling questions test resource management, performance thinking,*
> *and whether you've been burned by real production bugs."*

---

## 📊 Question Map

```
LEVEL 1 — Junior (0–2 years)
  • open() syntax and file modes
  • Context manager (with open)
  • read / readline / readlines difference
  • Text vs binary mode

LEVEL 2 — Mid-Level (2–5 years)
  • Large file handling strategies
  • Encoding and UnicodeDecodeError
  • CSV and JSON processing
  • seek() / tell() / flush()
  • Atomic writes

LEVEL 3 — Senior (5+ years)
  • Memory-mapped files
  • Concurrent file access / locking
  • Streaming architectures
  • Security: path traversal prevention
  • Performance: chunk processing, generators
```

---

## 🟢 Level 1 — Junior Questions

---

### Q1: How do you open and read a file safely in Python?

**Weak answer:** `f = open("file.txt"); data = f.read(); f.close()`

**Strong answer:**

> Always use the `with` statement — it guarantees the file is closed even if an exception occurs, preventing resource leaks.

```python
# ✅ Safe:
with open("data.txt", "r", encoding="utf-8") as f:
    content = f.read()

# ❌ Dangerous — if process() raises, file is never closed:
f = open("data.txt")
content = f.read()
process(content)   # ← exception here leaks the file handle
f.close()          # ← never reached!
```

> Internally, `with` calls `f.__exit__()` which calls `f.close()` regardless of how the block exits — via return, exception, or normally.

---

### Q2: What are the file modes? What's dangerous about `"w"`?

**Strong answer:**

```
'r'   Read only — file MUST exist (default)
'w'   Write — OVERWRITES if file exists, creates if not  ← DANGEROUS
'a'   Append — adds to end, creates if not exists
'x'   Exclusive create — fails if file already exists
'b'   Binary (combine: 'rb', 'wb')
'+'   Read+Write (combine: 'r+', 'w+')
```

> The danger with `"w"` is it silently destroys existing content. If you meant to append, using `"w"` is a data-loss bug. Use `"a"` for logs, `"x"` when you want to fail safely if a file already exists.

---

### Q3: What is the difference between `read()`, `readline()`, and `readlines()`?

**Strong answer:**

```python
f.read()           # → str: entire file content as ONE string (danger: loads all into RAM)
f.readline()       # → str: one line including \n ("" = EOF)
f.readlines()      # → list: all lines as a list (danger: loads all into RAM)
for line in f:     # → str: one line at a time (memory efficient — use this!)
```

> For any file larger than a few MB, use `for line in f` — it reads only one line at a time, so memory usage stays constant regardless of file size.

---

### Q4: What is the difference between text mode and binary mode?

**Strong answer:**

> In **text mode** (default): Python decodes bytes to strings using an encoding, and translates line endings (`\r\n` on Windows ↔ `\n`). You get `str` objects.
>
> In **binary mode** (`"rb"`, `"wb"`): Python gives you raw bytes with no encoding or line-ending translation. You get `bytes` objects.

```python
# Text mode:
with open("hello.txt", "r", encoding="utf-8") as f:
    s = f.read()   # str: "Hello\n"

# Binary mode:
with open("hello.txt", "rb") as f:
    b = f.read()   # bytes: b'Hello\n'

# Use binary for: images, PDFs, audio, video, zip files, any non-text data
# Use text for: .txt, .csv, .json, .xml, .html, source code
```

---

### Q5: What happens if you forget to close a file?

**Strong answer:**

> 1. **File descriptor leak** — OS limits open file descriptors (typically 1024). In a loop that opens files without closing, you'll hit `OSError: [Errno 24] Too many open files`
> 2. **Data not flushed** — buffered writes may not reach disk
> 3. **Other processes can't write** — on Windows, open files are locked

```python
# This leaks 1000 file descriptors:
for i in range(1000):
    f = open(f"file_{i}.txt")
    data = f.read()
    # oops — forgot f.close()!

# Eventually: OSError: [Errno 24] Too many open files
```

---

## 🔵 Level 2 — Mid-Level Questions

---

### Q6: How would you process a 50GB log file without crashing?

**Weak answer:** "I would read it line by line."

**Strong answer:**

```python
# Line-by-line iteration — O(1) memory:
def count_errors(logfile: str) -> int:
    count = 0
    with open(logfile, encoding="utf-8") as f:
        for line in f:             # reads one line at a time — never loads all 50GB
            if "ERROR" in line:
                count += 1
    return count

# Generator for pipeline processing:
def error_lines(logfile: str):
    with open(logfile, encoding="utf-8") as f:
        for line in f:
            if "ERROR" in line:
                yield line.strip()

# Memory stays constant regardless of file size.
# For binary chunks:
with open("huge_binary.dat", "rb") as f:
    while chunk := f.read(65536):   # 64KB at a time
        process(chunk)
```

---

### Q7: What is encoding? How do you debug a `UnicodeDecodeError`?

**Strong answer:**

> Encoding is the mapping between bytes (what's on disk) and characters (what you read). `UnicodeDecodeError` means you tried to decode bytes that don't match the specified encoding.

```python
# Debugging steps:
# 1. Try the most common alternatives:
for enc in ["utf-8", "utf-8-sig", "latin-1", "cp1252", "utf-16"]:
    try:
        with open("mystery.txt", encoding=enc) as f:
            data = f.read()
        print(f"Works with: {enc}")
        break
    except UnicodeDecodeError:
        pass

# 2. Use chardet to detect:
# pip install chardet
import chardet
with open("mystery.txt", "rb") as f:
    result = chardet.detect(f.read(10000))   # sample first 10KB
print(result)  # {'encoding': 'ISO-8859-1', 'confidence': 0.73}

# 3. Use errors='replace' as temporary workaround:
with open("file.txt", encoding="utf-8", errors="replace") as f:
    data = f.read()   # replaces bad bytes with ?
```

---

### Q8: What is `seek()` and when would you use it?

**Strong answer:**

> `seek(offset, whence)` moves the file pointer to a specific position. `tell()` returns the current position.

```python
with open("data.txt", "r") as f:
    content = f.read()   # reads everything, pointer is now at end
    f.seek(0)            # reset to beginning
    again = f.read()     # reads everything again

    f.seek(0, 2)         # jump to END (whence=2)
    size = f.tell()      # file size in bytes

    f.seek(100)          # jump to byte position 100
    f.seek(-20, 2)       # 20 bytes before end
    f.seek(5, 1)         # 5 bytes after current position
```

> **Real use case:** implementing `tail -f` (following a growing log file) — seek to end, read new content, sleep, repeat.

---

### Q9: How do you write to a CSV file correctly?

**Strong answer:**

```python
import csv

# DictWriter — most common pattern:
rows = [
    {"name": "Alice", "email": "alice@mail.com", "age": 25},
    {"name": "Bob",   "email": "bob@mail.com",   "age": 30},
]

with open("users.csv", "w", newline="", encoding="utf-8") as f:
    #                        ^^^^^^^^^^^
    # CRITICAL: newline="" prevents csv module's own line endings
    # from being double-translated on Windows (would produce blank lines)

    writer = csv.DictWriter(f, fieldnames=["name", "email", "age"])
    writer.writeheader()
    writer.writerows(rows)
```

> Common mistake: forgetting `newline=""` → every row has a blank line between it on Windows. Also: never use `str.split(",")` to parse CSV — values can contain commas inside quotes.

---

### Q10: What is an atomic write and when is it necessary?

**Weak answer:** "Writing to a temp file then renaming."

**Strong answer:**

> An atomic write guarantees the file is either fully written or unchanged — never in a partial/corrupt state. This matters for config files, state files, anything that must be consistent.

```python
import os, tempfile, json

def atomic_write_json(path: str, data: dict) -> None:
    dir_ = os.path.dirname(os.path.abspath(path))
    fd, tmp = tempfile.mkstemp(dir=dir_, suffix=".tmp")
    try:
        with os.fdopen(fd, "w", encoding="utf-8") as f:
            json.dump(data, f, indent=2)
            f.flush()
            os.fsync(f.fileno())   # hardware-level flush
        os.replace(tmp, path)     # atomic rename — POSIX guarantees atomicity
    except:
        os.unlink(tmp)
        raise

# Without atomic write: if process crashes during write,
# config.json is half-written and unreadable.
```

---

## 🔴 Level 3 — Senior Questions

---

### Q11: How would you design a streaming ETL pipeline for 50GB CSV files?

**Strong answer:**

```python
import csv
from typing import Iterator

def read_rows(filepath: str) -> Iterator[dict]:
    """Generator: yields one row at a time. Memory: O(row_size)."""
    with open(filepath, newline="", encoding="utf-8") as f:
        yield from csv.DictReader(f)

def transform(row: dict) -> dict | None:
    """Transform and validate. Return None to skip."""
    try:
        amount = float(row["amount"])
        if amount < 0:
            return None   # skip invalid
        return {"id": row["transaction_id"], "amount": amount, "currency": "USD"}
    except (KeyError, ValueError):
        return None

def load_batch(batch: list[dict], conn) -> None:
    """Bulk insert to DB."""
    conn.executemany("INSERT INTO transactions VALUES (:id, :amount, :currency)", batch)

def etl_pipeline(filepath: str, db_conn, batch_size: int = 1000) -> None:
    batch = []
    processed = skipped = 0

    for raw_row in read_rows(filepath):
        row = transform(raw_row)
        if row:
            batch.append(row)
            processed += 1
        else:
            skipped += 1

        if len(batch) >= batch_size:
            load_batch(batch, db_conn)
            batch.clear()

    if batch:
        load_batch(batch, db_conn)   # flush remaining

    print(f"Done: {processed:,} processed, {skipped:,} skipped")
```

---

### Q12: How do you prevent path traversal attacks?

**Strong answer:**

```python
from pathlib import Path

UPLOAD_DIR = Path("/var/www/uploads").resolve()

def safe_read(user_input: str) -> str:
    # Step 1: join with base directory
    # Step 2: resolve() expands all symlinks and ".." components
    # Step 3: check the resolved path is INSIDE the allowed directory
    requested = (UPLOAD_DIR / user_input).resolve()

    if not requested.is_relative_to(UPLOAD_DIR):   # Python 3.9+
        raise PermissionError(f"Access denied")

    return requested.read_text(encoding="utf-8")

# Attack attempt: user_input = "../../etc/passwd"
# (UPLOAD_DIR / "../../etc/passwd").resolve() = /etc/passwd
# /etc/passwd.is_relative_to(/var/www/uploads) = False → PermissionError ✓
```

---

### Q13: How do you handle concurrent writes to the same file?

**Strong answer:**

> Multiple processes writing to the same file simultaneously causes interleaved writes and corruption. The right approach depends on the scale:

```python
# Option 1: File locking (single machine):
import fcntl

with open("shared.log", "a") as f:
    fcntl.flock(f, fcntl.LOCK_EX)    # blocks until lock acquired
    f.write("log entry\n")
    fcntl.flock(f, fcntl.LOCK_UN)

# Option 2: Append mode (atomic for small writes on POSIX):
# Writes ≤ PIPE_BUF (4096 bytes) are atomic in append mode on POSIX.
# For log lines, this is usually sufficient.

# Option 3: Python logging module (thread-safe built-in):
import logging
logging.basicConfig(filename="app.log", level=logging.INFO)
logging.info("This is thread-safe")

# Option 4: Centralized log server (production best practice):
# Send logs to a log aggregator (Logstash, Fluentd, CloudWatch)
# instead of writing to files from multiple processes.
```

---

## ⚠️ Trap Questions

---

### Trap 1 — `"w"` Mode Silent Data Loss

```python
config = load_existing_config()    # loads current config
config["new_key"] = "new_value"

# ❌ Using "w" — if this crashes after opening but before write finishes:
with open("config.json", "w") as f:
    json.dump(config, f)   # if crash here, config.json is empty!

# ✅ Use atomic write:
atomic_write_json("config.json", config)
```

---

### Trap 2 — CSV Without `newline=""`

```python
# ❌ WRONG — blank lines between rows on Windows:
with open("data.csv", "w") as f:
    writer = csv.writer(f)
    writer.writerow(["a", "b"])   # "a,b\r\r\n" — extra \r!

# ✅ CORRECT:
with open("data.csv", "w", newline="") as f:
    writer = csv.writer(f)
    writer.writerow(["a", "b"])   # "a,b\r\n" on Windows, "a,b\n" on Unix
```

---

### Trap 3 — `readlines()` Is Not Memory Efficient

```python
# LOOKS fine but loads all 10GB into memory:
with open("huge.log") as f:
    for line in f.readlines():    # ← readlines() = list of all lines in RAM!
        process(line)

# CORRECT — true streaming:
with open("huge.log") as f:
    for line in f:                 # ← O(1) memory
        process(line)
```

---

### Trap 4 — `os.fsync()` vs `flush()`

```python
with open("critical.dat", "w") as f:
    f.write(data)
    f.flush()           # ← flushes Python's buffer to OS buffer
                        #   but OS may not have written to disk yet!

    os.fsync(f.fileno())  # ← flushes OS buffer to hardware
                          #   guarantees data survives power cut
# Use both for truly critical data (financial records, etc.)
```

---

## 🔥 Rapid-Fire Revision

```
Q: What does "r+" mode do?
A: Read + write. File must exist. Does NOT truncate. Pointer at start.

Q: Why newline="" with csv module?
A: csv handles line endings itself. Without it, Python adds extra \r on Windows.

Q: What is flush() vs close()?
A: flush() writes buffer to disk but keeps file open. close() flushes AND closes.

Q: What is os.replace() used for?
A: Atomic rename — used in atomic write pattern. Old file replaced atomically.

Q: What is pathlib.Path.resolve()?
A: Returns absolute path with all symlinks and ".." resolved — essential for security.

Q: How do you read a file without knowing its encoding?
A: pip install chardet → chardet.detect(raw_bytes) → gives encoding + confidence.

Q: What is mmap?
A: Memory-mapped file — maps file into virtual memory. Random access without loading.
   Used for: databases, large binary formats, indexes.

Q: What is tempfile.mkstemp()?
A: Creates temp file atomically, returns (fd, path). Use for atomic write pattern.

Q: What is the difference between write() and writelines()?
A: write(str) writes one string. writelines(list) writes each item. Neither adds \n.

Q: When does data actually hit the disk?
A: Python buffer → OS buffer (flush()) → hardware (fsync()).
   close() triggers flush(). Only fsync() guarantees hardware write.
```

---

## 🔁 Navigation

| | |
|---|---|
| 📖 Theory | [theory.md](./theory.md) |
| ⚡ Cheatsheet | [cheatsheet.md](./cheatsheet.md) |
| ➡️ Next | [09 — Logging & Debugging](../09_logging_debugging/theory.md) |
