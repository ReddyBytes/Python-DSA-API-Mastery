# ⚡ File Handling — Cheatsheet

> Quick reference: modes, reading, writing, CSV, JSON, pathlib, patterns, gotchas.

---

## 📌 File Modes

```
'r'    Read only (default). File must exist.
'w'    Write. Creates / OVERWRITES ← DESTROYS existing content!
'a'    Append. Creates if needed. Never overwrites.
'x'    Exclusive create. Fails if file exists.
'r+'   Read + Write. File must exist. No truncation.
'w+'   Read + Write. Creates / truncates.
'b'    Binary (combine: 'rb', 'wb', 'ab')
't'    Text (default, combine: 'rt', 'wt')
```

---

## 🔧 Opening Files

```python
# Always use with — guarantees close() on any exit:
with open("file.txt", "r", encoding="utf-8") as f:
    content = f.read()

# Multiple files:
with open("in.txt") as i, open("out.txt", "w") as o:
    o.write(i.read())

# Binary:
with open("image.jpg", "rb") as f:
    data = f.read()
```

---

## 📖 Reading Methods

```python
f.read()              # → str: entire file (⚠️ loads all into memory!)
f.read(n)             # → str: next n characters
f.readline()          # → str: one line including \n ("" = EOF)
f.readlines()         # → list: all lines (⚠️ loads all into memory!)
for line in f:        # ✅ one line at a time — O(1) memory, use for large files
```

```
MEMORY COMPARISON (1GB file):
  read()       → 1000MB RAM  ← crashes
  readlines()  → 1000MB RAM  ← crashes
  for line in f → ~1KB RAM   ← handles any size ✓
  read(65536)  →  64KB RAM   ← controlled chunks ✓
```

---

## ✍️ Writing Methods

```python
f.write("line\n")          # write string (no auto newline!)
f.writelines(["a\n","b\n"])  # write iterable (no auto newline!)
print("text", file=f)      # write + auto newline

f.flush()                  # force buffer → OS (file stays open)
os.fsync(f.fileno())        # force OS buffer → hardware
```

---

## 🎯 Seek & Tell

```python
f.tell()        # current byte position
f.seek(0)       # go to start
f.seek(0, 2)    # go to end (2 = SEEK_END)
f.seek(n)       # go to absolute byte n
f.seek(n, 1)    # move n bytes from current (1 = SEEK_CUR)
f.seek(-n, 2)   # n bytes before end
```

---

## 🔤 Encoding

```python
open("file.txt", encoding="utf-8")          # standard, handles most languages
open("file.txt", encoding="utf-8-sig")      # UTF-8 with BOM (Excel files)
open("file.txt", encoding="latin-1")        # Windows legacy, Western European
open("file.txt", encoding="cp1252")         # Windows-1252 (Excel on Windows)

# errors parameter:
open("file.txt", errors="strict")           # raise on bad bytes (default)
open("file.txt", errors="ignore")           # skip bad bytes
open("file.txt", errors="replace")          # replace with ?

# Detect unknown encoding:
# pip install chardet
import chardet
with open("file.txt", "rb") as f:
    enc = chardet.detect(f.read(10000))["encoding"]
```

---

## 📊 CSV

```python
import csv

# Read as lists:
with open("file.csv", newline="", encoding="utf-8") as f:
    reader = csv.reader(f)
    header = next(reader)
    for row in reader:
        print(row)   # ['Alice', '25', 'alice@mail.com']

# Read as dicts:
with open("file.csv", newline="", encoding="utf-8") as f:
    for row in csv.DictReader(f):
        print(row["name"])   # {'name': 'Alice', ...}

# Write lists:
with open("out.csv", "w", newline="", encoding="utf-8") as f:
    w = csv.writer(f)
    w.writerow(["name", "age"])
    w.writerows([["Alice", 25], ["Bob", 30]])

# Write dicts:
with open("out.csv", "w", newline="", encoding="utf-8") as f:
    w = csv.DictWriter(f, fieldnames=["name", "age"])
    w.writeheader()
    w.writerow({"name": "Alice", "age": 25})

# ⚠️ newline="" is REQUIRED — csv handles line endings itself
# Custom delimiter:
csv.reader(f, delimiter="\t")   # TSV
csv.reader(f, delimiter="|")    # pipe-separated
```

---

## 📦 JSON

```python
import json

# Read:
with open("data.json", encoding="utf-8") as f:
    data = json.load(f)           # file → dict/list

# Write:
with open("data.json", "w", encoding="utf-8") as f:
    json.dump(data, f, indent=2, ensure_ascii=False)

# String ←→ dict:
data = json.loads('{"name": "Alice"}')     # str → dict
s    = json.dumps(data, indent=2)           # dict → str

# Custom types:
class MyEncoder(json.JSONEncoder):
    def default(self, obj):
        from datetime import date
        if isinstance(obj, date): return obj.isoformat()
        return super().default(obj)

json.dumps(data, cls=MyEncoder)
```

---

## 🏠 pathlib

```python
from pathlib import Path

p = Path("data/users/report.csv")

# Info:
p.name           # "report.csv"
p.stem           # "report"
p.suffix         # ".csv"
p.parent         # Path("data/users")
p.exists()       # True/False
p.is_file()      # True/False
p.is_dir()       # True/False

# Build paths (cross-platform):
p = Path("data") / "users" / "report.csv"   # ← / operator!
p = Path.home() / "Documents" / "file.txt"
p = Path.cwd() / "output"

# Read/Write:
text = p.read_text(encoding="utf-8")
data = p.read_bytes()
p.write_text("content", encoding="utf-8")
p.write_bytes(b"bytes")

# Create dirs:
p.parent.mkdir(parents=True, exist_ok=True)

# Delete:
p.unlink(missing_ok=True)     # delete file
shutil.rmtree(p)               # delete directory

# Glob:
list(Path("src").glob("*.py"))       # all .py files
list(Path("src").rglob("*.py"))      # recursive
```

---

## ⚛️ Atomic Write

```python
import os, tempfile, json

def atomic_write_json(path: str, data: dict) -> None:
    """Write all-or-nothing — file never in partial state."""
    dir_ = os.path.dirname(os.path.abspath(path))
    fd, tmp = tempfile.mkstemp(dir=dir_, suffix=".tmp")
    try:
        with os.fdopen(fd, "w", encoding="utf-8") as f:
            json.dump(data, f)
            f.flush()
            os.fsync(f.fileno())   # flush to hardware
        os.replace(tmp, path)      # atomic rename
    except:
        os.unlink(tmp)
        raise
```

---

## 🛡️ Security — Path Traversal Prevention

```python
from pathlib import Path

BASE = Path("/var/www/uploads").resolve()

def safe_path(user_input: str) -> Path:
    resolved = (BASE / user_input).resolve()
    if not resolved.is_relative_to(BASE):   # Python 3.9+
        raise PermissionError("Access denied")
    return resolved

# "../../etc/passwd" → resolved = /etc/passwd → not relative to BASE → PermissionError ✓
```

---

## 🔄 Large File Patterns

```python
# Line iteration (O(1) memory):
with open("huge.log") as f:
    for line in f:
        process(line.strip())

# Chunk reading (binary):
with open("data.bin", "rb") as f:
    while chunk := f.read(65536):   # 64KB chunks
        process(chunk)

# Generator pipeline:
def rows(path):
    import csv
    with open(path, newline="") as f:
        yield from csv.DictReader(f)

for row in rows("50gb.csv"):
    if float(row["amount"]) > 0:
        insert_to_db(row)
```

---

## 🗑️ Temp Files

```python
import tempfile

# Auto-deleted context manager:
with tempfile.NamedTemporaryFile(mode="w", suffix=".csv", delete=True) as f:
    f.write("a,b\n1,2\n")
    f.flush()
    process(f.name)

# Temp directory:
with tempfile.TemporaryDirectory() as tmpdir:
    out = Path(tmpdir) / "result.json"
    out.write_text(json.dumps(data))
```

---

## 📦 shutil

```python
import shutil

shutil.copy("src.txt", "dst.txt")          # copy file
shutil.copy2("src.txt", "dst.txt")         # copy + metadata
shutil.copytree("src/", "dst/")            # copy directory
shutil.move("old.txt", "new.txt")          # move/rename
shutil.rmtree("dir/")                       # delete directory
shutil.make_archive("backup", "zip", "src/")  # create zip
shutil.unpack_archive("backup.zip", "dst/")   # extract
usage = shutil.disk_usage("/")              # .total .used .free
```

---

## 🔴 Gotchas

```python
# 1 — "w" destroys content:
open("config.json", "w")   # ← file is EMPTY from this moment, even if crash follows

# 2 — readlines() still loads everything:
for line in f.readlines():   # ← same as read(), loads all into RAM
for line in f:               # ← correct: true streaming

# 3 — CSV needs newline="":
open("out.csv", "w")          # ← blank lines between rows on Windows
open("out.csv", "w", newline="")   # ← correct

# 4 — flush() ≠ fsync():
f.flush()            # Python buffer → OS (OS may cache)
os.fsync(f.fileno()) # OS buffer → hardware (survives power cut)

# 5 — Text mode mangles binary:
open("image.jpg", "r").read()   # UnicodeDecodeError or corrupted data
open("image.jpg", "rb").read()  # ← correct

# 6 — Forgetting encoding:
open("file.txt")                         # uses system default (varies by platform!)
open("file.txt", encoding="utf-8")       # always explicit
```

---

## 🔁 Navigation

| | |
|---|---|
| 📖 Theory | [theory.md](./theory.md) |
| 🎯 Interview | [interview.md](./interview.md) |
| ➡️ Next | [09 — Logging & Debugging](../09_logging_debugging/theory.md) |
