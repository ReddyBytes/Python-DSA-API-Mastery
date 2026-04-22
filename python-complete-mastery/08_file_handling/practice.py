"""
==============================================================================
MODULE 08 — File Handling
==============================================================================
Run with: python3 practice.py

Story: You're building a data pipeline for an e-commerce platform. Every night,
transaction logs arrive as CSV files. Config lives in JSON. Reports need to be
written. And 50GB files must be processed without loading them into memory.

This file covers everything from 'open()' basics to production patterns like
atomic writes, memory-efficient chunked reading, and temporary files.

Concepts covered:
  - open() modes (r, w, a, x, rb, wb, r+)
  - with statement — always use it
  - read(), readline(), readlines(), file iteration
  - write(), writelines(), print(file=f)
  - seek() and tell() — file pointer positioning
  - pathlib.Path — the modern OO path API
  - CSV reading and writing (csv.reader, csv.DictReader, DictWriter)
  - JSON read/write (json.load, json.dump, custom encoder)
  - os.path basics (join, exists, basename, dirname)
  - Temporary files (tempfile module)
  - Encoding — always specify utf-8
  - Memory-efficient patterns for large files
  - Atomic write pattern
  - io.StringIO — in-memory file objects
==============================================================================
"""

import os
import csv
import json
import tempfile
import io
from pathlib import Path

# We'll create a temporary working directory for all file operations
# so this script leaves no mess behind
WORK_DIR = Path(tempfile.mkdtemp(prefix="py_practice_08_"))
print(f"Working directory: {WORK_DIR}")


# ==============================================================================
# CONCEPT 1: open() modes — understanding what each does
# ==============================================================================
print("\n" + "="*60)
print("CONCEPT 1: open() modes")
print("="*60)

"""
MODE  MEANING                  FILE EXISTS?   TRUNCATES?
  r   Read only (default)      Must exist     No
  w   Write only               Creates/opens  YES — destroys content!
  a   Append                   Creates/opens  No — adds to end
  x   Exclusive create         Must NOT exist No — fails if exists
  r+  Read + Write             Must exist     No
  wb  Write binary             Creates/opens  YES
  rb  Read binary              Must exist     No
"""

sample_file = WORK_DIR / "sample.txt"

# --- 'w' mode: write (creates or truncates) ---
with open(sample_file, "w", encoding="utf-8") as f:
    f.write("Line 1: Hello\n")
    f.write("Line 2: World\n")
    f.write("Line 3: Python\n")
print(f"  'w' mode created {sample_file.name} ({sample_file.stat().st_size} bytes)")

# --- 'a' mode: append (does NOT truncate) ---
with open(sample_file, "a", encoding="utf-8") as f:
    f.write("Line 4: Appended\n")
print(f"  'a' mode appended — now {sample_file.stat().st_size} bytes")

# --- 'x' mode: exclusive create (fails if file exists) ---
new_file = WORK_DIR / "exclusive.txt"
try:
    with open(new_file, "x", encoding="utf-8") as f:
        f.write("Created exclusively\n")
    print(f"  'x' mode created {new_file.name}")
    # Try again — should fail
    with open(new_file, "x", encoding="utf-8") as f:
        f.write("This should fail")
except FileExistsError as e:
    print(f"  'x' mode correctly refused to overwrite: {e}")

# --- Binary mode ('rb') --- read back as bytes
with open(sample_file, "rb") as f:
    raw_bytes = f.read()
print(f"  'rb' mode read {len(raw_bytes)} bytes: {raw_bytes[:20]}...")

# --- 'r+' mode: read AND write without truncating ---
with open(sample_file, "r+", encoding="utf-8") as f:
    content = f.read()
    f.seek(0)                    # go back to start
    f.write("MODIFIED ")        # overwrites first 9 bytes
print(f"  'r+' mode partial overwrite done")


# ==============================================================================
# CONCEPT 2: with statement — the context manager guarantee
# ==============================================================================
print("\n" + "="*60)
print("CONCEPT 2: with statement — always use it")
print("="*60)

"""
The 'with' statement calls f.__enter__() at the start and f.__exit__()
at the end — even if an exception occurs. __exit__ closes the file.

Without 'with':
  f = open("data.txt")
  data = f.read()
  process(data)      ← if THIS raises, f.close() never runs
  f.close()          ← never reached → file descriptor leak

The OS has a limit on open file descriptors (typically 1024 on Linux).
A loop that opens files without closing them will hit this limit and crash.
"""

context_file = WORK_DIR / "context_demo.txt"

# Safe — always closes
with open(context_file, "w", encoding="utf-8") as f:
    f.write("Safe content\n")
print(f"  File closed after 'with': {f.closed}")  # True

# Multiple files at once
in_file  = WORK_DIR / "input.txt"
out_file = WORK_DIR / "output.txt"

with open(in_file, "w", encoding="utf-8") as f:
    f.write("upper\nlower\nMixed\n")

with open(in_file, encoding="utf-8") as infile, \
     open(out_file, "w", encoding="utf-8") as outfile:
    for line in infile:
        outfile.write(line.upper())

result = out_file.read_text(encoding="utf-8")
print(f"  Two-file transform result: {result!r}")


# ==============================================================================
# CONCEPT 3: Reading strategies — choosing for file size
# ==============================================================================
print("\n" + "="*60)
print("CONCEPT 3: Reading strategies")
print("="*60)

"""
METHOD           RETURNS         MEMORY COST     USE WHEN
read()           str             ENTIRE FILE     Small files only (< a few MB)
read(n)          str (n chars)   n chars         Controlled chunked reading
readline()       str             One line        One-at-a-time manual control
readlines()      list of str     ALL lines       Small files, need list
for line in f    iterator        One line        Large files — O(1) memory
"""

log_file = WORK_DIR / "app.log"
log_lines = [f"2025-01-{i:02d} INFO Processing order {1000+i}\n" for i in range(1, 11)]
log_file.write_text("".join(log_lines), encoding="utf-8")

# read() — entire file
with open(log_file, encoding="utf-8") as f:
    content = f.read()
print(f"  read() → {len(content)} chars total")

# readline() — one line at a time
with open(log_file, encoding="utf-8") as f:
    first = f.readline()    # includes trailing \n
    second = f.readline()
    eof_check = ""
    while True:
        line = f.readline()
        if line == "":      # empty string = end of file
            break
        eof_check = line
print(f"  readline() first:  {first.strip()!r}")
print(f"  readline() last:   {eof_check.strip()!r}")

# readlines() — all lines as list
with open(log_file, encoding="utf-8") as f:
    lines = f.readlines()
print(f"  readlines() → {len(lines)} lines, type={type(lines[0])}")

# Iteration — most memory-efficient (O(1) regardless of file size)
error_count = 0
with open(log_file, encoding="utf-8") as f:
    for line in f:                      # reads ONE line at a time
        if "INFO" in line:
            error_count += 1
print(f"  Iteration: counted {error_count} INFO lines (O(1) memory)")


# ==============================================================================
# CONCEPT 4: Writing — write(), writelines(), print(file=f), flush()
# ==============================================================================
print("\n" + "="*60)
print("CONCEPT 4: Writing methods")
print("="*60)

write_file = WORK_DIR / "write_demo.txt"

# write() — no automatic newline
with open(write_file, "w", encoding="utf-8") as f:
    f.write("Line A\n")    # you supply the \n
    f.write("Line B\n")

# writelines() — writes list, still no automatic newlines
with open(write_file, "a", encoding="utf-8") as f:
    lines = ["Line C\n", "Line D\n", "Line E\n"]
    f.writelines(lines)    # same as calling write() for each

# print(file=f) — adds \n automatically, like print to stdout
with open(write_file, "a", encoding="utf-8") as f:
    print("Line F (via print)", file=f)    # adds \n
    print(f"Line G total={42}", file=f)

content = write_file.read_text(encoding="utf-8")
print(f"  write_demo.txt:\n{content}")

# flush() — force buffer to disk without closing
live_log = WORK_DIR / "live.log"
with open(live_log, "w", encoding="utf-8") as f:
    f.write("Starting process...\n")
    f.flush()    # ← force write to disk NOW (important for log tailing)
    # ... long operation would happen here ...
    f.write("Done!\n")
print(f"  flush() demo complete: {live_log.stat().st_size} bytes on disk")


# ==============================================================================
# CONCEPT 5: seek() and tell() — file pointer
# ==============================================================================
print("\n" + "="*60)
print("CONCEPT 5: seek() and tell()")
print("="*60)

"""
The file pointer tracks your current position in the file.
seek(offset, whence):
  whence=0 (SEEK_SET) — absolute position from start
  whence=1 (SEEK_CUR) — relative to current position
  whence=2 (SEEK_END) — relative to end of file
"""

seek_file = WORK_DIR / "seek_demo.txt"
with open(seek_file, "w", encoding="utf-8") as f:
    f.write("ABCDEFGHIJ")   # 10 ASCII bytes = 10 chars

with open(seek_file, "r", encoding="utf-8") as f:
    print(f"  tell() at start: {f.tell()}")       # 0

    data = f.read(3)
    print(f"  read(3) = {data!r}, tell() = {f.tell()}")   # 3

    f.seek(0)                                      # back to start
    print(f"  after seek(0): tell() = {f.tell()}, read(3) = {f.read(3)!r}")

    f.seek(0, 2)                                   # seek to END
    size = f.tell()
    print(f"  seek(0, 2) = end of file: {size} bytes")

    # Note: seek with SEEK_END (whence=2) requires binary mode for non-zero offsets
    # In text mode, only seek(0, 0) and seek(pos, 0) and seek(0, 2) are allowed
    # For last-N-chars reads, use binary mode ('rb') or read all and slice:
    last3 = f.read()[-3:]  if False else None   # placeholder
    f.seek(0)
    all_content = f.read()
    last3 = all_content[-3:]
    print(f"  Last 3 chars (via read + slice): {last3!r}")


# ==============================================================================
# CONCEPT 6: pathlib.Path — the modern path API
# ==============================================================================
print("\n" + "="*60)
print("CONCEPT 6: pathlib.Path")
print("="*60)

"""
pathlib.Path is the modern, OO replacement for os.path.
The / operator joins paths (cross-platform safe).
Methods like .read_text(), .write_text(), .glob() make common ops one-liners.
"""

# Creating paths
p = WORK_DIR / "data" / "users" / "export.csv"
print(f"  Path: {p}")
print(f"  p.name    = {p.name!r}")           # 'export.csv'
print(f"  p.stem    = {p.stem!r}")           # 'export'
print(f"  p.suffix  = {p.suffix!r}")         # '.csv'
print(f"  p.parent  = {p.parent}")
print(f"  p.parts   = {p.parts}")
print(f"  p.is_absolute() = {p.is_absolute()}")

# File operations
data_dir = WORK_DIR / "pathlib_demo"
data_dir.mkdir(parents=True, exist_ok=True)   # create directory (and parents)

text_file = data_dir / "notes.txt"
text_file.write_text("Hello from pathlib!\nLine 2\n", encoding="utf-8")
content = text_file.read_text(encoding="utf-8")
print(f"\n  write_text + read_text: {content!r}")

# File metadata
print(f"  exists()  = {text_file.exists()}")
print(f"  is_file() = {text_file.is_file()}")
print(f"  is_dir()  = {text_file.is_dir()}")
print(f"  stat().st_size = {text_file.stat().st_size} bytes")

# Creating multiple files for glob demo
for i in range(3):
    (data_dir / f"report_{i}.csv").write_text(f"id,value\n{i},{i*10}\n")
(data_dir / "config.json").write_text('{"env": "dev"}')

# glob — find files matching a pattern
csv_files = list(data_dir.glob("*.csv"))
print(f"\n  glob('*.csv') found {len(csv_files)} files:")
for f in sorted(csv_files):
    print(f"    {f.name}")

all_files = list(data_dir.rglob("*"))  # recursive
print(f"\n  rglob('*') found {len(all_files)} items total")

# Path arithmetic — special paths
home = Path.home()
cwd  = Path.cwd()
print(f"\n  Path.home() = {home}")
print(f"  Path.cwd()  = {cwd}")

# Resolve — normalize path (resolve symlinks, remove ..)
relative = WORK_DIR / ".." / WORK_DIR.name  # goes up then back
resolved = relative.resolve()
print(f"\n  Relative with '..': {relative}")
print(f"  Resolved:           {resolved}")


# ==============================================================================
# CONCEPT 7: CSV reading and writing
# ==============================================================================
print("\n" + "="*60)
print("CONCEPT 7: CSV files")
print("="*60)

"""
NEVER parse CSV manually with .split(",") — quoted fields contain commas!
  "Smith, John",john@email.com,30
  ^ split(',') would give WRONG result for "Smith, John"

Always use the csv module.
newline="" is required — csv module handles its own line endings.
Without it, Python's text mode may insert extra \\r on Windows.
"""

csv_file = WORK_DIR / "users.csv"

# --- Writing with csv.writer ---
with open(csv_file, "w", newline="", encoding="utf-8") as f:
    writer = csv.writer(f)
    writer.writerow(["name", "email", "age", "score"])   # header
    writer.writerow(["Alice Smith", "alice@example.com", 28, 95.5])
    writer.writerow(["Bob, Jr.", "bob@example.com", 34, 87.0])  # comma in name!
    writer.writerows([
        ["Carol", "carol@example.com", 25, 91.2],
        ["Dave", "dave@example.com", 41, 78.8],
    ])
print(f"  csv.writer created {csv_file.name}")
print(f"  Raw content:\n{csv_file.read_text()}")

# --- Reading with csv.reader (rows as lists) ---
print("  csv.reader (rows as lists):")
with open(csv_file, newline="", encoding="utf-8") as f:
    reader = csv.reader(f)
    header = next(reader)      # consume header separately
    print(f"    Header: {header}")
    for row in reader:
        print(f"    Row: {row}")

# --- Reading with csv.DictReader (rows as dicts — preferred) ---
print("\n  csv.DictReader (rows as dicts):")
with open(csv_file, newline="", encoding="utf-8") as f:
    reader = csv.DictReader(f)
    for row in reader:
        # Access by column name — much more readable
        print(f"    {row['name']:15s} age={row['age']:2s}  "
              f"score={row['score']}")

# --- Writing with csv.DictWriter ---
dict_csv = WORK_DIR / "products.csv"
products = [
    {"name": "Laptop", "price": 999.99, "qty": 15},
    {"name": 'Monitor, 27"', "price": 399.50, "qty": 8},  # comma in name
    {"name": "Keyboard", "price": 79.00, "qty": 50},
]
with open(dict_csv, "w", newline="", encoding="utf-8") as f:
    fieldnames = ["name", "price", "qty"]
    writer = csv.DictWriter(f, fieldnames=fieldnames)
    writer.writeheader()         # writes the header row
    writer.writerows(products)
print(f"\n  DictWriter output:\n{dict_csv.read_text()}")

# --- Custom delimiter (TSV) ---
tsv_file = WORK_DIR / "data.tsv"
with open(tsv_file, "w", newline="", encoding="utf-8") as f:
    writer = csv.writer(f, delimiter="\t")
    writer.writerow(["city", "population"])
    writer.writerow(["New York", 8336817])
    writer.writerow(["Los Angeles", 3979576])
print(f"  TSV file (tab-delimited):\n{tsv_file.read_text()!r}")


# ==============================================================================
# CONCEPT 8: JSON read and write
# ==============================================================================
print("\n" + "="*60)
print("CONCEPT 8: JSON files")
print("="*60)

"""
Python ↔ JSON type mapping:
  dict  ↔ object {}
  list  ↔ array  []
  str   ↔ string ""
  int   ↔ number
  float ↔ number
  True  ↔ true
  False ↔ false
  None  ↔ null

json.load(f)    — reads from file object
json.loads(s)   — reads from string
json.dump(d, f) — writes to file object
json.dumps(d)   — writes to string
"""

config_file = WORK_DIR / "config.json"
config_data = {
    "app_name": "e-commerce-api",
    "version": "2.1.0",
    "database": {
        "host": "localhost",
        "port": 5432,
        "name": "shop_db"
    },
    "features": ["cart", "recommendations", "analytics"],
    "debug": False,
    "max_retries": 3,
    "timeout": None
}

# Write JSON with pretty printing
with open(config_file, "w", encoding="utf-8") as f:
    json.dump(config_data, f, indent=2, ensure_ascii=False)
    # indent=2 → human-readable, ensure_ascii=False → allows unicode chars

print(f"  JSON written ({config_file.stat().st_size} bytes):")
print(config_file.read_text())

# Read JSON back
with open(config_file, encoding="utf-8") as f:
    loaded = json.load(f)

print(f"  Loaded back: type={type(loaded)}, "
      f"app_name={loaded['app_name']!r}, "
      f"features={loaded['features']}")

# json.loads / json.dumps — string versions
json_str = json.dumps({"event": "order_placed", "amount": 49.99})
parsed = json.loads(json_str)
print(f"\n  json.dumps + json.loads round-trip: {parsed}")

# --- Custom encoder for types JSON doesn't know about ---
from datetime import date, datetime

class DateEncoder(json.JSONEncoder):
    """
    By default, json.dumps raises TypeError for datetime objects.
    Subclass JSONEncoder and override default() to handle custom types.
    """
    def default(self, obj):
        if isinstance(obj, (datetime, date)):
            return obj.isoformat()   # "2025-01-15" or "2025-01-15T14:30:00"
        return super().default(obj)  # raise TypeError for anything else

order = {
    "order_id": 1001,
    "placed_at": datetime(2025, 1, 15, 14, 30, 0),
    "ship_date": date(2025, 1, 17),
    "total": 149.99
}

with open(WORK_DIR / "order.json", "w", encoding="utf-8") as f:
    json.dump(order, f, cls=DateEncoder, indent=2)

print(f"\n  Custom DateEncoder output:")
print((WORK_DIR / "order.json").read_text())


# ==============================================================================
# CONCEPT 9: os.path basics
# ==============================================================================
print("\n" + "="*60)
print("CONCEPT 9: os.path basics")
print("="*60)

"""
os.path is the classic (pre-pathlib) path manipulation library.
You'll encounter it in older codebases. Prefer pathlib for new code.
"""

from os.path import join, exists, basename, dirname, splitext, abspath, getsize

sample_path = "/home/user/projects/myapp/data/users.csv"

print(f"  join('a', 'b', 'c.txt') = {join('a', 'b', 'c.txt')!r}")
print(f"  basename(...)          = {basename(sample_path)!r}")    # users.csv
print(f"  dirname(...)           = {dirname(sample_path)!r}")     # /home/.../data
print(f"  splitext(...)          = {splitext(sample_path)}")      # (..., '.csv')
print(f"  abspath('.')           = {abspath('.')!r}")

# exists() — check before opening (LBYL style)
print(f"\n  exists(config_file)  = {exists(str(config_file))}")
print(f"  exists('/no/file')   = {exists('/no/file')}")
print(f"  getsize(config_file) = {getsize(str(config_file))} bytes")

# os.getcwd() and environment
print(f"  os.getcwd()          = {os.getcwd()!r}")
print(f"  os.sep               = {os.sep!r}")            # '/' on Unix, '\\' on Windows

# Directory operations
demo_dir = str(WORK_DIR / "os_demo")
os.makedirs(demo_dir, exist_ok=True)
print(f"\n  os.makedirs created: {demo_dir!r}")
print(f"  os.path.isdir:       {os.path.isdir(demo_dir)}")


# ==============================================================================
# CONCEPT 10: Temporary files
# ==============================================================================
print("\n" + "="*60)
print("CONCEPT 10: Temporary files")
print("="*60)

"""
Temporary files are created in the OS temp directory (/tmp on Linux/Mac).
They are automatically deleted when the context exits.

Use cases:
  - Intermediate processing (sort a large file, validate, then load)
  - Atomic writes (write to temp, then rename atomically)
  - Testing (no permanent artifacts)
  - Building output in stages before exposing to consumers
"""

# NamedTemporaryFile — has a real filename (accessible to other processes)
print("  NamedTemporaryFile:")
with tempfile.NamedTemporaryFile(
    mode="w",
    suffix=".csv",
    delete=True,        # delete on close (default True)
    encoding="utf-8"
) as tmp:
    print(f"    Temp path: {tmp.name}")
    tmp.write("name,score\nAlice,95\nBob,87\n")
    tmp.flush()

    # Can re-open by name while still open
    with open(tmp.name, encoding="utf-8") as verify:
        print(f"    Content: {verify.read()!r}")
print(f"  After context: file deleted (exists={os.path.exists(tmp.name)})")

# TemporaryDirectory — entire directory, all contents auto-deleted
print("\n  TemporaryDirectory:")
with tempfile.TemporaryDirectory(prefix="pipeline_") as tmpdir:
    tmpdir_path = Path(tmpdir)
    print(f"    Created: {tmpdir_path}")

    # Use it like a real directory
    (tmpdir_path / "stage1.json").write_text('{"step": 1}')
    (tmpdir_path / "stage2.json").write_text('{"step": 2}')
    files = list(tmpdir_path.glob("*.json"))
    print(f"    Files: {[f.name for f in files]}")
print(f"  After context: directory exists={tmpdir_path.exists()}")

# tempfile.mkstemp — low-level, returns (fd, path), must delete manually
fd, tmp_path = tempfile.mkstemp(suffix=".txt", dir=str(WORK_DIR))
try:
    with os.fdopen(fd, "w", encoding="utf-8") as f:
        f.write("mkstemp content\n")
    print(f"\n  mkstemp: {tmp_path}")
    print(f"    Content: {Path(tmp_path).read_text()!r}")
finally:
    os.unlink(tmp_path)   # manual cleanup required!
print(f"  Manually deleted: exists={os.path.exists(tmp_path)}")


# ==============================================================================
# CONCEPT 11: Encoding — always specify it
# ==============================================================================
print("\n" + "="*60)
print("CONCEPT 11: Encoding")
print("="*60)

"""
Computers store bytes. Text is an interpretation of bytes.
Encoding is the mapping: bytes ↔ characters.

UTF-8 can represent every Unicode character.
On different systems, the default encoding differs:
  Linux/Mac: usually UTF-8
  Windows:   often CP1252 or UTF-16

ALWAYS specify encoding="utf-8" to be explicit and portable.
"""

# Write a file with non-ASCII characters
unicode_file = WORK_DIR / "unicode.txt"
content_with_unicode = "Hello: こんにちは | Привет | مرحبا | 你好\nCurrency: €, £, ¥\n"

with open(unicode_file, "w", encoding="utf-8") as f:
    f.write(content_with_unicode)
print(f"  UTF-8 file size: {unicode_file.stat().st_size} bytes "
      f"(chars={len(content_with_unicode)})")

# Read it back
with open(unicode_file, "r", encoding="utf-8") as f:
    read_back = f.read()
print(f"  Read back correctly: {read_back[:40]!r}...")

# Encoding errors parameter
print("\n  Encoding error handling:")
with open(unicode_file, "rb") as f:
    raw = f.read()
    # Try to read as latin-1 — will give garbage for multi-byte chars
    try:
        as_latin1 = raw.decode("latin-1")
        print(f"    latin-1 decode: {as_latin1[:30]!r} (garbage!)")
    except Exception as e:
        print(f"    latin-1 error: {e}")

    # 'replace' substitutes undecodable bytes with ?
    as_latin1_replace = raw.decode("latin-1", errors="replace")
    # 'ignore' silently drops them
    as_latin1_ignore  = raw.decode("latin-1", errors="ignore")
    print(f"    errors='replace': {as_latin1_replace[:25]!r}")
    print(f"    errors='ignore':  {as_latin1_ignore[:25]!r}")


# ==============================================================================
# CONCEPT 12: Memory-efficient large file processing
# ==============================================================================
print("\n" + "="*60)
print("CONCEPT 12: Memory-efficient patterns")
print("="*60)

"""
For a 1GB file:
  read()       → 1GB in RAM   (may crash)
  readlines()  → 1GB in RAM   (may crash)
  for line in f → ~1KB in RAM  (safe for any size)
  read(65536)  → 64KB in RAM  (controlled)
"""

# Create a "large" test file (small here but shows the pattern)
large_file = WORK_DIR / "transactions.log"
with open(large_file, "w", encoding="utf-8") as f:
    for i in range(1000):
        status = "ERROR" if i % 50 == 0 else "OK"
        f.write(f"2025-01-15 TX#{i:04d} {status} amount={i*1.5:.2f}\n")
print(f"  Created {large_file.name}: {large_file.stat().st_size:,} bytes")

# Pattern 1: line-by-line iteration — O(1) memory
error_count = 0
total_amount = 0.0
with open(large_file, encoding="utf-8") as f:
    for line in f:                          # reads ONE line at a time
        if "ERROR" in line:
            error_count += 1
        amount_str = line.split("amount=")[-1].strip()
        total_amount += float(amount_str)
print(f"\n  Line iteration: {error_count} errors, "
      f"total amount = {total_amount:,.2f}")

# Pattern 2: chunked reading for binary data (e.g., checksums)
import hashlib

def compute_sha256(filepath: Path) -> str:
    """SHA256 of any size file — loads only 64KB at a time."""
    sha256 = hashlib.sha256()
    with open(filepath, "rb") as f:
        while True:
            chunk = f.read(65536)   # 64KB chunks
            if not chunk:
                break
            sha256.update(chunk)
    return sha256.hexdigest()

checksum = compute_sha256(large_file)
print(f"\n  SHA256 (chunked): {checksum[:16]}...")

# Pattern 3: generator for lazy processing
def read_error_lines(filepath: Path):
    """
    Generator: yields only error lines, one at a time.
    Caller memory = O(1), regardless of file size.
    """
    with open(filepath, encoding="utf-8") as f:
        for line in f:
            if "ERROR" in line:
                yield line.strip()

print(f"\n  Generator — first 3 error lines:")
for line in list(read_error_lines(large_file))[:3]:
    print(f"    {line}")


# ==============================================================================
# CONCEPT 13: Atomic write pattern — preventing corruption
# ==============================================================================
print("\n" + "="*60)
print("CONCEPT 13: Atomic writes")
print("="*60)

"""
Problem: if your process crashes mid-write, the file is partially written.
  - 'w' mode truncates BEFORE writing → file is empty if crash happens
  - The file is in an inconsistent state

Solution: write to a TEMP file, then os.replace() atomically.
os.replace() is atomic on POSIX — readers always see old or new, never partial.
"""

def atomic_write_json(filepath: Path, data: dict) -> None:
    """
    Write JSON atomically:
      1. Write to a temp file in the SAME directory (same filesystem!)
         (cross-filesystem rename is not atomic on all systems)
      2. os.replace() atomically swaps old → new
    If crash occurs during write: temp file is lost, original untouched.
    If crash occurs during replace: OS guarantees atomic completion.
    """
    tmp_path = filepath.with_suffix(".tmp")
    try:
        with open(tmp_path, "w", encoding="utf-8") as f:
            json.dump(data, f, indent=2)
            f.flush()
            os.fsync(f.fileno())   # flush OS-level buffer to disk hardware
        os.replace(str(tmp_path), str(filepath))   # atomic rename
    except Exception:
        if tmp_path.exists():
            tmp_path.unlink()      # clean up temp on failure
        raise

atomic_file = WORK_DIR / "atomic_config.json"
atomic_write_json(atomic_file, {"env": "production", "version": 3, "ok": True})
print(f"  Atomic write complete: {atomic_file.read_text()!r}")
print(f"  Temp file cleaned up: {not atomic_file.with_suffix('.tmp').exists()}")


# ==============================================================================
# CONCEPT 14: io.StringIO — in-memory file objects
# ==============================================================================
print("\n" + "="*60)
print("CONCEPT 14: io.StringIO — in-memory files")
print("="*60)

"""
io.StringIO behaves exactly like a text file object but lives in RAM.
io.BytesIO is the same for binary data.

Use cases:
  1. Testing functions that write to files (no temp files needed)
  2. Building file content in memory, then uploading/sending it
  3. Passing strings to functions that expect file objects
  4. Building CSV/JSON in memory before writing to disk or HTTP response
"""

# Use case 1: build CSV in memory, then use it
print("  Build CSV in memory with StringIO:")
output = io.StringIO()
writer = csv.writer(output)
writer.writerow(["product", "qty", "price"])
writer.writerow(["Laptop", 3, 999.99])
writer.writerow(["Mouse", 10, 29.99])

# getvalue() returns full contents without needing seek(0)
csv_string = output.getvalue()
print(f"    CSV content:\n{csv_string}")

# Use case 2: pass string to function that expects file
def count_csv_rows(f) -> int:
    """Accepts any file-like object (real file or StringIO)."""
    reader = csv.reader(f)
    return sum(1 for _ in reader) - 1   # subtract header

output.seek(0)   # must reset before re-reading
row_count = count_csv_rows(output)
print(f"    Row count (via StringIO): {row_count}")

# Use case 3: use with json.load (expects file object)
json_buffer = io.StringIO('{"name": "Alice", "scores": [95, 87, 92]}')
data = json.load(json_buffer)
print(f"\n  json.load from StringIO: {data}")

# BytesIO for binary data
print("\n  io.BytesIO for binary:")
binary_buf = io.BytesIO()
binary_buf.write(b"\x89PNG\r\n\x1a\n")   # PNG header bytes
binary_buf.write(b"\x00\x00\x00\rIHDR")  # more bytes
binary_buf.seek(0)
header = binary_buf.read(4)
print(f"  First 4 bytes of 'fake PNG': {header}")


# ==============================================================================
# CONCEPT 15: File existence checks and safe patterns
# ==============================================================================
print("\n" + "="*60)
print("CONCEPT 15: File existence and safety patterns")
print("="*60)

target = WORK_DIR / "safe_demo.txt"
target.write_text("original content", encoding="utf-8")

# LBYL style: check then open
if target.exists():
    content = target.read_text(encoding="utf-8")
    print(f"  LBYL: file exists, content={content!r}")

# EAFP style: try then handle (avoids TOCTOU race condition)
try:
    content = Path("/nonexistent_xyz/file.txt").read_text(encoding="utf-8")
except FileNotFoundError as e:
    print(f"  EAFP: FileNotFoundError → {e.strerror}")

# unlink(missing_ok=True) — delete if exists, ignore if not
ghost = WORK_DIR / "ghost.txt"
ghost.unlink(missing_ok=True)   # no error if it doesn't exist
print(f"  unlink(missing_ok=True) on non-existent file: OK (no error)")


# ==============================================================================
# Cleanup
# ==============================================================================
print("\n" + "="*60)
print("Cleaning up temporary files...")
import shutil
shutil.rmtree(WORK_DIR)
print(f"  Removed: {WORK_DIR}")
print(f"  WORK_DIR exists: {WORK_DIR.exists()}")

print("\n" + "="*60)
print("MODULE 08 — All concepts demonstrated.")
print("="*60)
