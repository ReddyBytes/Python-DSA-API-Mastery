# 💻 Practice — pathlib

| # | Difficulty | Topic |
|---|---|---|
| Q1 | 🟢 Easy | Path creation — 4 ways |
| Q2 | 🟢 Easy | Path properties |
| Q3 | 🟢 Easy | exists / is_file / is_dir |
| Q4 | 🟡 Medium | read_text / write_text |
| Q5 | 🟡 Medium | mkdir with flags |
| Q6 | 🟡 Medium | glob and rglob |
| Q7 | 🟡 Medium | iterdir — files sorted by size |
| Q8 | 🟡 Medium | rename / unlink |
| Q9 | 🟡 Medium | with_suffix / with_name |
| Q10 | 🟡 Medium | stat — size and mtime |
| Q11 | 🟠 Hard | resolve — path traversal guard |
| Q12 | 🟠 Hard | Capstone — organize_downloads |

---

## Q1 🟢 · Path creation — 4 ways to create a Path object

> 🛠️ **Solve locally:** [practice_local.py → Q1](./practice_local.py)

<details>
<summary>Hint</summary>

`Path()` accepts a string. `Path.home()` and `Path.cwd()` are class methods. The `/` operator is overloaded for joining.

</details>

<details>
<summary>Answer</summary>

```python
from pathlib import Path

# 1. From a plain string
p1 = Path("data/users/export.csv")

# 2. From the user's home directory (class method)
p2 = Path.home() / "Documents" / "report.pdf"

# 3. From the current working directory (class method)
p3 = Path.cwd() / "output" / "result.txt"

# 4. Using the / operator to join segments
base = Path("/var/log")
p4 = base / "app" / "errors.log"

print(p1)  # data/users/export.csv
print(p2)  # /home/alice/Documents/report.pdf  (or C:\Users\alice\...)
print(p3)  # /current/dir/output/result.txt
print(p4)  # /var/log/app/errors.log
```

**Why:** `Path()` normalises separators across Windows/Linux. The `/` operator keeps joining readable — no nested `os.path.join()` calls required.

</details>

---

## Q2 🟢 · Path properties — extract the parts of a path

> 🛠️ **Solve locally:** [practice_local.py → Q2](./practice_local.py)

Given `Path("/data/reports/q3_2024.csv")`, extract `.name`, `.stem`, `.suffix`, `.parent`, `.parts`.

<details>
<summary>Hint</summary>

All are read-only attributes, not methods — no `()` needed.

</details>

<details>
<summary>Answer</summary>

```python
from pathlib import Path

p = Path("/data/reports/q3_2024.csv")

print(p.name)    # "q3_2024.csv"         ← filename + extension
print(p.stem)    # "q3_2024"             ← filename without extension
print(p.suffix)  # ".csv"                ← extension including the dot
print(p.parent)  # PosixPath('/data/reports')
print(p.parts)   # ('/', 'data', 'reports', 'q3_2024.csv')
```

**Why:** These properties save you from `os.path.splitext()` and `os.path.basename()` — each one is self-documenting and returns the right type (Path for `parent`, string for `name`/`stem`/`suffix`, tuple for `parts`).

</details>

---

## Q3 🟢 · exists / is_file / is_dir — describe a path

> 🛠️ **Solve locally:** [practice_local.py → Q3](./practice_local.py)

Write a function `describe_path(p)` that returns `"file"`, `"directory"`, or `"missing"`.

<details>
<summary>Hint</summary>

Call `.exists()` first. Then branch on `.is_file()` / `.is_dir()`.

</details>

<details>
<summary>Answer</summary>

```python
from pathlib import Path

def describe_path(p: Path | str) -> str:
    path = Path(p)
    if not path.exists():
        return "missing"
    if path.is_file():
        return "file"
    if path.is_dir():
        return "directory"
    return "other"  # symlink to nothing, device file, etc.

# Usage:
print(describe_path("/etc/hosts"))     # "file"
print(describe_path("/etc"))           # "directory"
print(describe_path("/no/such/path"))  # "missing"
```

**Why:** `.exists()` returns `False` for broken symlinks too, which is usually the safe default. If you need to detect symlinks specifically, check `.is_symlink()` before `.exists()`.

</details>

---

## Q4 🟡 · read_text / write_text — uppercase a file in place

> 🛠️ **Solve locally:** [practice_local.py → Q4](./practice_local.py)

Read a file, uppercase its content, write it back — using pathlib only (no `open()`).

<details>
<summary>Hint</summary>

`.read_text()` returns a string. `.write_text()` takes a string and overwrites. Always pass `encoding="utf-8"`.

</details>

<details>
<summary>Answer</summary>

```python
from pathlib import Path

def uppercase_file(filepath: str | Path) -> None:
    p = Path(filepath)
    content = p.read_text(encoding="utf-8")
    p.write_text(content.upper(), encoding="utf-8")

# Demo (creates then modifies a temp file):
tmp = Path("/tmp/demo.txt")
tmp.write_text("hello pathlib\n", encoding="utf-8")
uppercase_file(tmp)
print(tmp.read_text(encoding="utf-8"))  # "HELLO PATHLIB\n"
```

**Why:** `.read_text()` / `.write_text()` are one-liners for the common case of full-file reads and writes. They automatically close the file handle. Use `.open("a")` when you need to append.

</details>

---

## Q5 🟡 · mkdir — create nested directories with flags

> 🛠️ **Solve locally:** [practice_local.py → Q5](./practice_local.py)

Create `output/2024/reports/` using `mkdir`. Demonstrate what `parents=True` and `exist_ok=True` each do.

<details>
<summary>Hint</summary>

Try calling `mkdir()` without flags first to see the errors it raises, then add each flag.

</details>

<details>
<summary>Answer</summary>

```python
from pathlib import Path

target = Path("output/2024/reports")

# Without flags — raises FileNotFoundError if parents missing,
# FileExistsError if directory already exists:
# target.mkdir()

# parents=True  → creates output/, output/2024/, output/2024/reports/ in one call
# exist_ok=True → no error if the directory already exists (idempotent)
target.mkdir(parents=True, exist_ok=True)

# Calling it again is safe:
target.mkdir(parents=True, exist_ok=True)  # no error

print(target.is_dir())  # True
```

**Why:** `parents=True` is the pathlib equivalent of `os.makedirs()`. `exist_ok=True` makes it safe to call in scripts that may run multiple times — the same pattern as `CREATE TABLE IF NOT EXISTS` in SQL.

</details>

---

## Q6 🟡 · glob / rglob — find .py files

> 🛠️ **Solve locally:** [practice_local.py → Q6](./practice_local.py)

Find all `.py` files in a directory (non-recursive), then all `.py` files recursively with `rglob`.

<details>
<summary>Hint</summary>

`.glob("*.py")` matches only in the immediate directory. `.rglob("*.py")` descends into all subdirectories.

</details>

<details>
<summary>Answer</summary>

```python
from pathlib import Path

src = Path(".")  # replace with your target directory

# Non-recursive: only .py files directly inside src/
direct_py = list(src.glob("*.py"))
print("Direct .py files:", direct_py)

# Recursive: .py files anywhere in the tree under src/
all_py = list(src.rglob("*.py"))
print(f"All .py files (recursive): {len(all_py)}")

# rglob("*.py") is exactly equivalent to glob("**/*.py"):
equiv = list(src.glob("**/*.py"))
assert sorted(all_py) == sorted(equiv)

# Sort by name for deterministic output:
for f in sorted(all_py):
    print(f.relative_to(src))
```

**Why:** Both return generators of `Path` objects, not strings. Wrap in `list()` if you need to iterate more than once. Prefer `rglob("*.py")` over `glob("**/*.py")` — it is shorter and more readable.

</details>

---

## Q7 🟡 · iterdir — list files sorted by size descending

> 🛠️ **Solve locally:** [practice_local.py → Q7](./practice_local.py)

List all files (not subdirectories) in a directory, sorted by size descending.

<details>
<summary>Hint</summary>

Filter with `.is_file()`. Sort with `key=lambda p: p.stat().st_size` and `reverse=True`.

</details>

<details>
<summary>Answer</summary>

```python
from pathlib import Path

def files_by_size(directory: str | Path) -> list[Path]:
    d = Path(directory)
    files = [p for p in d.iterdir() if p.is_file()]
    return sorted(files, key=lambda p: p.stat().st_size, reverse=True)

# Usage:
for f in files_by_size("."):
    size_kb = f.stat().st_size / 1024
    print(f"{f.name:<40} {size_kb:>8.1f} KB")
```

**Why:** `.iterdir()` yields both files and directories — always filter with `.is_file()` unless you explicitly want both. `.stat().st_size` is in bytes; divide by 1024 for KB or 1_048_576 for MB.

</details>

---

## Q8 🟡 · rename / unlink — safe rename and delete

> 🛠️ **Solve locally:** [practice_local.py → Q8](./practice_local.py)

Rename a file to add a `.bak` extension. Delete a file only if it exists.

<details>
<summary>Hint</summary>

`.with_suffix()` builds the new path. `.unlink(missing_ok=True)` avoids a `FileNotFoundError`.

</details>

<details>
<summary>Answer</summary>

```python
from pathlib import Path

# ── Rename: add .bak extension ────────────────────────────────────────
def backup_file(p: Path | str) -> Path:
    src = Path(p)
    dst = src.with_suffix(src.suffix + ".bak")  # e.g. config.json → config.json.bak
    src.rename(dst)
    return dst

# ── Delete: only if exists ────────────────────────────────────────────
def safe_delete(p: Path | str) -> bool:
    path = Path(p)
    path.unlink(missing_ok=True)   # Python 3.8+ — no FileNotFoundError
    return not path.exists()

# Demo:
tmp = Path("/tmp/test_rename.txt")
tmp.write_text("hello", encoding="utf-8")
bak = backup_file(tmp)
print(bak)             # /tmp/test_rename.txt.bak
safe_delete(bak)       # True
safe_delete(bak)       # True — no error even though it's gone
```

**Why:** `.rename()` on different filesystems may raise `OSError` — use `shutil.move()` for cross-device moves. `missing_ok=True` is the idiomatic way to make deletes idempotent; avoid `if p.exists(): p.unlink()` since it has a TOCTOU race condition.

</details>

---

## Q9 🟡 · with_suffix / with_name — produce variant paths

> 🛠️ **Solve locally:** [practice_local.py → Q9](./practice_local.py)

Given `Path("output/report.txt")`, produce `"output/report.md"` and `"output/summary.txt"`.

<details>
<summary>Hint</summary>

`.with_suffix(".md")` swaps the extension. `.with_name("summary.txt")` replaces the entire filename.

</details>

<details>
<summary>Answer</summary>

```python
from pathlib import Path

p = Path("output/report.txt")

# Change extension only — keep the stem:
md_version = p.with_suffix(".md")
print(md_version)   # output/report.md

# Change full filename — keep the parent directory:
summary = p.with_name("summary.txt")
print(summary)      # output/summary.txt

# Change stem only (Python 3.9+):
renamed = p.with_stem("quarterly_report")
print(renamed)      # output/quarterly_report.txt
```

**Why:** These methods return new `Path` objects — they do not touch the filesystem. They are pure path transformations, useful for deriving output paths from input paths without string manipulation.

</details>

---

## Q10 🟡 · stat — file size and last modified time

> 🛠️ **Solve locally:** [practice_local.py → Q10](./practice_local.py)

Get a file's size in KB and its last modified time as a formatted string.

<details>
<summary>Hint</summary>

`.stat().st_size` gives bytes. `.stat().st_mtime` is a Unix timestamp — pass it to `datetime.fromtimestamp()`.

</details>

<details>
<summary>Answer</summary>

```python
from pathlib import Path
from datetime import datetime

def file_info(p: Path | str) -> dict:
    path = Path(p)
    stat = path.stat()

    size_kb = stat.st_size / 1024
    modified = datetime.fromtimestamp(stat.st_mtime).strftime("%Y-%m-%d %H:%M:%S")

    return {
        "name": path.name,
        "size_kb": round(size_kb, 2),
        "modified": modified,
    }

# Usage:
info = file_info("/etc/hosts")
print(info)
# {'name': 'hosts', 'size_kb': 0.21, 'modified': '2024-03-15 09:22:11'}
```

**Why:** `.stat()` makes a single syscall and returns all metadata at once — cache the result rather than calling `.stat()` multiple times on the same path.

</details>

---

## Q11 🟠 · resolve — prevent path traversal

> 🛠️ **Solve locally:** [practice_local.py → Q11](./practice_local.py)

Use `.resolve()` to canonicalize a path with `../` components and validate it stays inside a safe base directory.

<details>
<summary>Hint</summary>

Resolve both the base and the candidate. Use `.is_relative_to()` (Python 3.9+) to check containment.

</details>

<details>
<summary>Answer</summary>

```python
from pathlib import Path

SAFE_BASE = Path("/var/www/uploads").resolve()

def safe_join(user_input: str) -> Path:
    """
    Join user_input onto SAFE_BASE and verify the result stays inside SAFE_BASE.
    Raises PermissionError on any attempt to escape.
    """
    try:
        candidate = (SAFE_BASE / user_input).resolve()
    except (ValueError, OSError) as e:
        raise PermissionError(f"Invalid path input: {e}") from e

    if not candidate.is_relative_to(SAFE_BASE):
        raise PermissionError(
            f"Path traversal detected: '{user_input}' resolves outside {SAFE_BASE}"
        )

    return candidate

# Safe inputs:
print(safe_join("images/avatar.png"))          # /var/www/uploads/images/avatar.png

# Traversal attempts — all raise PermissionError:
# safe_join("../../etc/passwd")
# safe_join("../secret.txt")
# safe_join("/etc/passwd")                     # absolute path also blocked
```

**Why:** String-level checks (`user_input.startswith("/")`) are bypassable with `%2F` encoding or Unicode tricks. `.resolve()` lets the OS normalise the path first, making `.is_relative_to()` the reliable single gate.

</details>

---

## Q12 🟠 · Capstone — organize_downloads

> 🛠️ **Solve locally:** [practice_local.py → Q12](./practice_local.py)

Write `organize_downloads(downloads_dir)` that moves files into subdirectories by extension — `.pdf` → `PDFs/`, `.jpg`/`.jpeg`/`.png` → `Images/`, anything else → `Other/`.

<details>
<summary>Hint</summary>

Use `.iterdir()` to list files, `.suffix.lower()` to classify, `.mkdir(exist_ok=True)` per destination, and `.rename()` to move. Skip subdirectories encountered in the source.

</details>

<details>
<summary>Answer</summary>

```python
from pathlib import Path
import shutil

EXTENSION_MAP = {
    ".pdf":  "PDFs",
    ".jpg":  "Images",
    ".jpeg": "Images",
    ".png":  "Images",
    ".gif":  "Images",
    ".mp4":  "Videos",
    ".mov":  "Videos",
    ".doc":  "Documents",
    ".docx": "Documents",
    ".xls":  "Spreadsheets",
    ".xlsx": "Spreadsheets",
}

def organize_downloads(downloads_dir: str | Path) -> dict[str, int]:
    """
    Move files in downloads_dir into subdirectories by extension.
    Returns a summary dict: {folder_name: file_count}.
    """
    base = Path(downloads_dir)
    summary: dict[str, int] = {}

    for item in list(base.iterdir()):
        if not item.is_file():
            continue  # skip subdirectories and symlinks

        ext = item.suffix.lower()
        folder_name = EXTENSION_MAP.get(ext, "Other")
        destination_dir = base / folder_name

        destination_dir.mkdir(exist_ok=True)

        # Handle filename collisions: append _1, _2, etc.
        dest = destination_dir / item.name
        counter = 1
        while dest.exists():
            dest = destination_dir / f"{item.stem}_{counter}{item.suffix}"
            counter += 1

        item.rename(dest)
        summary[folder_name] = summary.get(folder_name, 0) + 1

    return summary

# Usage:
# result = organize_downloads(Path.home() / "Downloads")
# for folder, count in sorted(result.items()):
#     print(f"{folder:<20} {count} file(s)")
```

**Why:** `list(base.iterdir())` materialises the iterator before the loop — renaming files inside an open `iterdir()` generator can skip or double-visit entries on some platforms. The collision-handling loop ensures no file is silently overwritten.

</details>

---

## 🔁 Navigation

| | |
|---|---|
| ⬅️ Back to Module | [08_file_handling/theory.md](../theory.md) |
| 📖 Theory | [theory.md](./theory.md) |
| ⬅️ Prev Subfolder | [01_os_module ←](../01_os_module/theory.md) |
| ➡️ Next Subfolder | [03_datetime →](../03_datetime/theory.md) |

---

**Related:** [01_os_module](../01_os_module/theory.md) · [03_datetime](../03_datetime/theory.md)
