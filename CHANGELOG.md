# Changelog — Python-DSA-API-Mastery

> Updated at the end of each work session.

---

## Session: 2026-05-06

### One-time setup (repo-wide)

- Created `.gitignore` — excludes `**/practice_local.py` and `**/practice_local.md`
- Created `setup_practice.py` at repo root — generates `practice_local.py` in all 117 module folders after cloning
- Created blank `practice_local.py` in all 117 module folders
- Updated `README.md` — added "Local Practice Setup" section explaining `setup_practice.py` workflow

---

### 01_Python_Mastery / 01_python_fundamentals

- Added `print()` section — what it does, printing text/numbers/variables, `sep=`/`end=`, common mistake
- Added `input()` section — reading user input, why it always returns a string, `int(input(...))` pattern
- Added Scripting vs Programming section — kitchen analogy, comparison table
- Added Python Language Categories table — interpreted, high-level, dynamically typed, multi-paradigm
- Added Python Key Features section — 7 features with plain English explanations
- Added Comments, Quotes, Indentation section — `#`, triple-quote, all string types, IndentationError examples

### 01_Python_Mastery / 01.1_memory_management

- Rewrote Stack vs Heap intro — replaced function-based examples with whiteboard/drawer analogy
- Uses only `name = "Alice"` / `age = 25` level examples (no `def`, no `RecursionError`)

### 01_Python_Mastery / 02_control_flow

- Added `random` module section — `randint`, `choice`, `shuffle`, RPS game example
- Added Rock Paper Scissors to `practice.py` (Exercise 6) before converting to `practice.md`
- Renamed `practice.py` → `practice.md` — 37 problems with `<details>` hint/answer dropdowns
- Added 18 inline `📝 Practice:` links in `theory.md` after every concept section (Q1–Q37)
- Fixed `def find_in_grid()` section — added "skip if you haven't learned functions yet" note
- Updated Related Topics link: `practice.py` → `practice.md`
- Created `practice_local.py` — 37 problems pre-populated (Q numbers + problem statements, no answers)

### 01_Python_Mastery / 03_data_types

- Created `practice.md` — 47 problems with `<details>` hint/answer dropdowns
  - Q1–Q4: int · Q5–Q8: float · Q9–Q11: bool · Q12–Q18: str
  - Q19–Q25: list · Q26–Q30: tuple · Q31–Q35: set · Q36–Q42: dict
  - Q43–Q44: None · Q45–Q47: Type Conversion
- Added 10 inline `📝 Practice:` links in `theory.md` — one after every type section
- Updated Related Topics link: `practice.py` → `practice.md`
- Updated `practice_local.py` — 47 problems pre-populated via `setup_practice.py`

### 01_Python_Mastery / 03_data_types — Subfolder Restructure

- Created 5 numbered subfolders: `01_str/` `02_list/` `03_tuple/` `04_set/` `05_dict/` (numbered = learning order)
- Each subfolder: `theory.md` (full deep-dive) + `practice.md` (12–15 problems with `<details>` hints/answers)
- Moved `.py` files: `strings.py→01_str/` `list_practice.py→02_list/` `tuple_practice.py→03_tuple/` `set_practice.py→04_set/` `dict_practice.py→05_dict/`
- Updated main `theory.md`: replaced 5 long type sections with short summaries + learning order tables + subfolder links
- Learning order: str (1st) → list (2nd) → tuple (3rd) → set (4th) → dict (5th)

---
