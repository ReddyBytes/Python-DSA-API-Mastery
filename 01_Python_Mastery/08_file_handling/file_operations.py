"""
08_file_handling/file_operations.py
=====================================
CONCEPT: Reading, writing, and manipulating files with Python.
WHY THIS MATTERS: Every real application touches the filesystem.
Config files, logs, data exports, uploads, reports — all require solid
file I/O knowledge. Python's pathlib makes this clean and cross-platform.

Prerequisite: Modules 01–07
"""

import os
import shutil
import tempfile
from pathlib import Path

# =============================================================================
# SECTION 1: Reading files — text and binary
# =============================================================================

# CONCEPT: Always use `with open(...)` — the context manager guarantees the
# file is closed even if an exception occurs. NEVER rely on the file being
# closed by GC — it may happen too late (file descriptor leak in long processes).

print("=== Section 1: Reading Files ===")

# Create a test file to work with
test_file = Path(tempfile.mkdtemp()) / "sample.txt"
test_file.write_text(
    "Line 1: Python file handling\n"
    "Line 2: Always use context managers\n"
    "Line 3: with open() as f: ...\n"
    "Line 4: pathlib > os.path\n"
    "Line 5: read_text() for simple files\n"
)

# Method 1: read entire file as one string
with open(test_file, "r", encoding="utf-8") as f:
    content = f.read()   # entire file as string
print(f"Full content length: {len(content)} chars")

# Method 2: read line by line (memory-efficient for large files)
with open(test_file, "r", encoding="utf-8") as f:
    for line_num, line in enumerate(f, start=1):
        line = line.rstrip("\n")   # remove trailing newline
        print(f"  Line {line_num}: {line}")

# Method 3: read all lines into a list
with open(test_file, "r", encoding="utf-8") as f:
    lines = f.readlines()   # list of strings, each with \n
    lines = [l.rstrip() for l in lines]   # clean up
print(f"\nread_lines: {len(lines)} lines")

# Method 4: pathlib shortcut (best for small files)
content = test_file.read_text(encoding="utf-8")
lines   = test_file.read_text().splitlines()   # no trailing \n on any line
print(f"pathlib.read_text(): {len(lines)} lines")

# Binary reading (for images, PDFs, executables)
binary_file = Path(tempfile.mkdtemp()) / "binary.bin"
binary_file.write_bytes(b"\x00\x01\x02\x03\xFF\xFE\xFD")

with open(binary_file, "rb") as f:     # "rb" = read binary
    data = f.read()
print(f"\nBinary data: {data.hex()} ({len(data)} bytes)")


# =============================================================================
# SECTION 2: Writing files
# =============================================================================

# CONCEPT: Mode strings control read/write/create behavior:
# "r"  read only (default) — file must exist
# "w"  write — creates or TRUNCATES (erases existing content!)
# "a"  append — creates or adds to end
# "x"  exclusive create — fails if file already exists (safe creation)
# "r+" read and write — file must exist
# Add "b" for binary mode, "t" for text (default)

print("\n=== Section 2: Writing Files ===")

write_file = Path(tempfile.mkdtemp()) / "output.txt"

# Write new file (creates or overwrites)
with open(write_file, "w", encoding="utf-8") as f:
    f.write("First line\n")
    f.write("Second line\n")
    # writelines: write an iterable (does NOT add newlines automatically!)
    f.writelines(["Third line\n", "Fourth line\n"])

print(f"Wrote: {write_file.read_text()}")

# Append to existing file
with open(write_file, "a", encoding="utf-8") as f:
    f.write("Appended line\n")

print(f"After append:\n{write_file.read_text()}")

# pathlib write shortcuts (entire content at once)
write_file.write_text("Complete replacement\n", encoding="utf-8")
print(f"After write_text: {write_file.read_text()!r}")

# Safe creation (fails if file exists — prevents accidental overwrites)
safe_file = Path(tempfile.mkdtemp()) / "new_only.txt"
with open(safe_file, "x") as f:   # "x" = exclusive create
    f.write("Created safely\n")

try:
    with open(safe_file, "x") as f:   # same file — should fail
        f.write("This won't work\n")
except FileExistsError as e:
    print(f"FileExistsError (expected): {e}")


# =============================================================================
# SECTION 3: pathlib — modern file path handling
# =============================================================================

# CONCEPT: pathlib.Path represents file system paths as objects.
# It's cross-platform (handles / vs \ automatically), composable with /,
# and has methods for every common file operation.
# Prefer pathlib over os.path for all new Python code.

print("\n=== Section 3: pathlib ===")

# Path construction
home = Path.home()
cwd  = Path.cwd()

print(f"Home: {home}")
print(f"CWD:  {cwd}")

# Building paths with / operator (works on all platforms)
log_dir  = Path("/tmp") / "myapp" / "logs"   # /tmp/myapp/logs
data_dir = Path("/tmp") / "myapp" / "data"

# Path components
p = Path("/home/alice/projects/myapp/src/main.py")
print(f"\nPath: {p}")
print(f"  name:    {p.name}")          # main.py
print(f"  stem:    {p.stem}")          # main
print(f"  suffix:  {p.suffix}")        # .py
print(f"  parent:  {p.parent}")        # /home/alice/projects/myapp/src
print(f"  parts:   {p.parts[:3]}...")  # ('/','home','alice',...)

# File/directory operations
tmp_dir = Path(tempfile.mkdtemp())
new_dir = tmp_dir / "subdir" / "nested"
new_dir.mkdir(parents=True, exist_ok=True)   # creates all intermediate dirs
print(f"\nCreated: {new_dir}")
print(f"  exists: {new_dir.exists()}")
print(f"  is_dir: {new_dir.is_dir()}")

# Create files
(new_dir / "file1.txt").write_text("content 1")
(new_dir / "file2.txt").write_text("content 2")
(new_dir / "notes.md").write_text("# Notes")

# List contents
print(f"\nContents of {new_dir}:")
for item in new_dir.iterdir():
    print(f"  {item.name} ({'dir' if item.is_dir() else 'file'})")

# Glob patterns
txt_files = list(tmp_dir.rglob("*.txt"))   # recursive glob
md_files  = list(tmp_dir.rglob("*.md"))
print(f"\n*.txt files: {[f.name for f in txt_files]}")
print(f"*.md files:  {[f.name for f in md_files]}")

# File metadata
f = txt_files[0]
stat = f.stat()
print(f"\n{f.name} stats:")
print(f"  size:  {stat.st_size} bytes")
print(f"  mtime: {stat.st_mtime:.0f}")


# =============================================================================
# SECTION 4: Atomic file writes — preventing partial writes
# =============================================================================

# CONCEPT: Writing directly to a file is dangerous — if the process crashes
# mid-write, the file is left in a corrupt state. The safe pattern:
# write to a temp file, then atomically rename to the final path.
# `os.rename()` / `Path.replace()` is atomic on most OSes.

print("\n=== Section 4: Atomic File Writes ===")

def write_atomically(filepath: Path, content: str) -> None:
    """
    Write content safely:
    1. Write to a temporary file in the SAME directory (ensures same filesystem)
    2. Rename temp file to target (atomic — never leaves partial file)

    WHY same directory: rename across filesystems is not atomic.
    Using a .tmp file in the target directory ensures both are on same FS.
    """
    tmp_path = filepath.with_suffix(".tmp")
    try:
        tmp_path.write_text(content, encoding="utf-8")
        tmp_path.replace(filepath)   # atomic rename — target is always complete
    except Exception:
        tmp_path.unlink(missing_ok=True)   # clean up on failure
        raise

target = tmp_dir / "important_config.json"
write_atomically(target, '{"key": "value", "count": 42}')
print(f"Atomically written: {target.read_text()}")

# Verify no .tmp file remains
tmp_leftover = target.with_suffix(".tmp")
print(f".tmp leftover exists: {tmp_leftover.exists()}")   # False


# =============================================================================
# SECTION 5: Working with large files — streaming
# =============================================================================

# CONCEPT: Never read a large file entirely into memory.
# Process line by line (text) or in chunks (binary) to keep memory O(1).
# The file iterator in Python is lazy — it reads one line at a time.

print("\n=== Section 5: Large File Processing ===")

# Generate a "large" test file
large_file = tmp_dir / "large.log"
with open(large_file, "w") as f:
    for i in range(10_000):
        f.write(f"2024-01-15 10:{i%60:02d}:00 INFO Request {i} processed\n")

# Count lines without loading entire file into memory
line_count = 0
error_count = 0
with open(large_file, "r") as f:
    for line in f:       # file iterator: reads one line at a time
        line_count += 1
        if "ERROR" in line:
            error_count += 1

print(f"Lines: {line_count:,}, Errors: {error_count}")

# Process binary file in chunks
def count_bytes(filepath: Path, chunk_size: int = 8192) -> int:
    """Count bytes without loading entire file into memory."""
    total = 0
    with open(filepath, "rb") as f:
        while True:
            chunk = f.read(chunk_size)   # reads at most chunk_size bytes
            if not chunk:
                break   # end of file
            total += len(chunk)
    return total

size = count_bytes(large_file)
print(f"File size: {size:,} bytes")


# =============================================================================
# SECTION 6: File copy, move, delete operations
# =============================================================================

# CONCEPT: shutil for high-level file operations (copy, move, rmtree).
# pathlib.Path for single-file operations (rename, unlink).

print("\n=== Section 6: File Operations ===")

src = tmp_dir / "source.txt"
src.write_text("Source file content")

# Copy
dst = tmp_dir / "destination.txt"
shutil.copy2(src, dst)   # copy2 preserves metadata (timestamps, permissions)
print(f"Copied: {dst.read_text()}")

# Move (rename within same filesystem — atomic)
moved = tmp_dir / "moved.txt"
src.rename(moved)    # pathlib rename
print(f"Moved: {moved.read_text()}")

# Copy entire directory tree
src_dir = tmp_dir / "dir_to_copy"
src_dir.mkdir()
(src_dir / "a.txt").write_text("file a")
(src_dir / "b.txt").write_text("file b")

dst_dir = tmp_dir / "dir_copy"
shutil.copytree(src_dir, dst_dir)
print(f"Copied dir contents: {[f.name for f in dst_dir.iterdir()]}")

# Delete single file
dst.unlink()   # or dst.unlink(missing_ok=True) to not raise if missing
print(f"dst exists after unlink: {dst.exists()}")

# Delete directory tree
shutil.rmtree(dst_dir)
print(f"dst_dir exists after rmtree: {dst_dir.exists()}")


# =============================================================================
# SECTION 7: Temporary files and directories
# =============================================================================

# CONCEPT: tempfile module creates files/dirs that are automatically cleaned up.
# Essential for: processing uploads, staging builds, test fixtures.

print("\n=== Section 7: Temporary Files ===")

# NamedTemporaryFile: creates temp file with a real path
with tempfile.NamedTemporaryFile(mode="w", suffix=".csv", delete=True) as f:
    f.write("id,name,score\n")
    f.write("1,Alice,95\n")
    f.write("2,Bob,87\n")
    tmp_name = f.name
    print(f"Temp file: {tmp_name}")
    f.seek(0)   # won't work in "w" mode — showing concept

# File is deleted when with block exits (delete=True is default)

# TemporaryDirectory: creates temp dir, cleans up recursively
with tempfile.TemporaryDirectory() as tmpdir:
    tmpdir = Path(tmpdir)
    (tmpdir / "processed.json").write_text('{"result": "done"}')
    (tmpdir / "output.csv").write_text("id,value\n1,42\n")
    print(f"Temp dir contents: {[f.name for f in tmpdir.iterdir()]}")
# tmpdir and all contents deleted after with block


print("\n=== File operations complete ===")
print("Key file handling practices:")
print("  1. Always use `with open(...)` — never rely on GC to close files")
print("  2. pathlib.Path instead of os.path for all new code")
print("  3. Stream large files line-by-line — never .read() a big file")
print("  4. Atomic writes: write to .tmp, then rename to target")
print("  5. shutil for directory operations, pathlib for single files")
print("  6. tempfile for test fixtures and intermediate processing stages")
