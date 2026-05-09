# 💻 Practice — datetime

| # | Topic | Difficulty |
|---|---|---|
| [Q1](#q1) | Creating datetimes | 🟢 Beginner |
| [Q2](#q2) | strftime | 🟢 Beginner |
| [Q3](#q3) | strptime | 🟢 Beginner |
| [Q4](#q4) | timedelta | 🟡 Intermediate |
| [Q5](#q5) | Unix timestamps | 🟡 Intermediate |
| [Q6](#q6) | fromisoformat | 🟡 Intermediate |
| [Q7](#q7) | Timezone-aware | 🟡 Intermediate |
| [Q8](#q8) | utcnow() pitfall | 🟡 Intermediate |
| [Q9](#q9) | Date arithmetic | 🟡 Intermediate |
| [Q10](#q10) | time module | 🟡 Intermediate |
| [Q11](#q11) | Production logging | 🟠 Advanced |
| [Q12](#q12) | Capstone | 🟠 Advanced |

---


## 📋 Quick Index

| # | Concept | Level |
|---|---------|-------|
| [Q1](#q1) | Creating datetimes — today, now, specific date | 🟢 |
| [Q2](#q2) | strftime — Formatting dates as strings | 🟢 |
| [Q3](#q3) | strptime — Parsing strings to datetimes | 🟢 |
| [Q4](#q4) | timedelta — Date arithmetic | 🟡 |
| [Q5](#q5) | Unix timestamps — Converting to and from | 🟡 |
| [Q6](#q6) | fromisoformat — ISO 8601 parsing | 🟡 |
| [Q7](#q7) | Timezone-aware datetimes | 🟡 |
| [Q8](#q8) | datetime.utcnow() pitfall | 🟡 |
| [Q9](#q9) | Date arithmetic on a list | 🟡 |
| [Q10](#q10) | time module — Benchmarking | 🟡 |
| [Q11](#q11) | Production logging with timestamps | 🟠 |
| [Q12](#q12) | Capstone — Normalize mixed date formats | 🟠 |

---

<a id="q1"></a>

### Q1 🟢 · Creating datetimes — today, now, specific date

> 🛠️ **Solve locally:** [practice_local.py → Q1](./practice_local.py)



> Create three datetime objects: today's date only, the current datetime, and a specific datetime of 2024-03-15 at 09:30:00.

<details>
<summary>Hint</summary>

- `date.today()` returns just the calendar date with no time.
- `datetime.now()` returns local time. Pass `tz=timezone.utc` for UTC.
- `datetime(year, month, day, hour, minute, second)` for explicit construction.
</details>

<details>
<summary>Answer</summary>

```python
from datetime import date, datetime, timezone

# Today's date only
today = date.today()
print(today)                    # → 2024-03-15

# Current datetime (UTC — preferred)
now = datetime.now(tz=timezone.utc)
print(now)                      # → 2024-03-15 09:30:00.123456+00:00

# Specific datetime
specific = datetime(2024, 3, 15, 9, 30, 0)
print(specific)                 # → 2024-03-15 09:30:00
```

**Why:** `date.today()` is for date-only use cases (birthdays, deadlines). Always pass `tz=timezone.utc` to `datetime.now()` in production — a naked `datetime.now()` produces a naive datetime that Python cannot safely compare with other timezone-aware values.
</details>

---

<a id="q2"></a>

### Q2 🟢 · strftime — Formatting dates as strings

> 🛠️ **Solve locally:** [practice_local.py → Q2](./practice_local.py)



> Format `datetime(2024, 3, 15, 9, 30, 0, tzinfo=timezone.utc)` as three different strings: `"March 15, 2024"`, `"2024-03-15T09:30:00"`, and `"15/03/24 09:30"`.

<details>
<summary>Hint</summary>

- `%B` = full month name, `%d` = zero-padded day, `%Y` = 4-digit year.
- `%T` is not portable — use `%H:%M:%S` for the time component.
- `%y` = 2-digit year, `%m` = zero-padded month number.
</details>

<details>
<summary>Answer</summary>

```python
from datetime import datetime, timezone

dt = datetime(2024, 3, 15, 9, 30, 0, tzinfo=timezone.utc)

print(dt.strftime("%B %d, %Y"))          # → March 15, 2024
print(dt.strftime("%Y-%m-%dT%H:%M:%S"))  # → 2024-03-15T09:30:00
print(dt.strftime("%d/%m/%y %H:%M"))     # → 15/03/24 09:30
```

**Why:** `strftime` is your formatting tool when a downstream system, log file, or UI requires a specific string shape. The ISO 8601 form (`%Y-%m-%dT%H:%M:%S`) is the safest default for machine-readable output because it sorts lexicographically and is unambiguous across locales.
</details>

---

<a id="q3"></a>

### Q3 🟢 · strptime — Parsing strings to datetimes

> 🛠️ **Solve locally:** [practice_local.py → Q3](./practice_local.py)



> Parse these three strings into datetime objects: `"2024-03-15"`, `"15 Mar 2024 09:30"`, `"03/15/2024"`.

<details>
<summary>Hint</summary>

- `strptime(string, format)` — the format must exactly match the string's structure.
- `%b` = abbreviated month name (Jan, Feb, Mar...).
- A wrong format raises `ValueError` — wrap in try/except if the input is untrusted.
</details>

<details>
<summary>Answer</summary>

```python
from datetime import datetime

dt1 = datetime.strptime("2024-03-15", "%Y-%m-%d")
print(dt1)  # → 2024-03-15 00:00:00

dt2 = datetime.strptime("15 Mar 2024 09:30", "%d %b %Y %H:%M")
print(dt2)  # → 2024-03-15 09:30:00

dt3 = datetime.strptime("03/15/2024", "%m/%d/%Y")
print(dt3)  # → 2024-03-15 00:00:00
```

**Why:** Every external data source — CSVs, APIs, databases, log files — has its own date format. `strptime` bridges the gap between raw string and a real datetime object you can sort, compare, and do arithmetic on. All three parsed datetimes above represent the same day even though their original strings look completely different.
</details>

---

<a id="q4"></a>

### Q4 🟡 · timedelta — Date arithmetic

> 🛠️ **Solve locally:** [practice_local.py → Q4](./practice_local.py)



> Using `timedelta`: (1) calculate the date 30 days from now, (2) calculate the number of days between `2024-01-01` and `2024-03-15`, (3) find the date of the next Monday from today.

<details>
<summary>Hint</summary>

- `datetime.now() + timedelta(days=30)` for future dates.
- Subtracting two `date` or `datetime` objects returns a `timedelta` — use `.days` to get the integer count.
- `date.weekday()` returns 0 for Monday through 6 for Sunday. Use this to calculate days until next Monday.
</details>

<details>
<summary>Answer</summary>

```python
from datetime import date, timedelta

today = date.today()

# 1. 30 days from now
thirty_out = today + timedelta(days=30)
print(f"30 days from now: {thirty_out}")

# 2. Days between two dates
start = date(2024, 1, 1)
end   = date(2024, 3, 15)
diff  = (end - start).days
print(f"Days between: {diff}")   # → 74

# 3. Next Monday
days_until_monday = (7 - today.weekday()) % 7
# if today IS Monday, days_until = 0; force to 7 to get next Monday
if days_until_monday == 0:
    days_until_monday = 7
next_monday = today + timedelta(days=days_until_monday)
print(f"Next Monday: {next_monday}")
```

**Why:** `timedelta` is the right tool for all date offsets — never add raw integers to `.day` or `.month` because months have different lengths and years have leap days. `timedelta` handles all edge cases (month-end rollovers, leap years) automatically.
</details>

---

<a id="q5"></a>

### Q5 🟡 · Unix timestamps — Converting to and from

> 🛠️ **Solve locally:** [practice_local.py → Q5](./practice_local.py)



> Convert `datetime.now()` to a Unix timestamp and convert `1705334400` back to a UTC datetime. Explain why you should use UTC when converting.

<details>
<summary>Hint</summary>

- `.timestamp()` on a datetime object returns a float (seconds since epoch).
- `datetime.fromtimestamp(ts, tz=timezone.utc)` converts back safely.
- A Unix timestamp is always UTC — if your datetime is naive (no timezone), Python assumes local time when calling `.timestamp()`, which is system-dependent.
</details>

<details>
<summary>Answer</summary>

```python
from datetime import datetime, timezone

# datetime → Unix timestamp
now_utc = datetime.now(tz=timezone.utc)
ts = now_utc.timestamp()
print(f"Unix timestamp: {ts}")            # → e.g. 1705334400.123456

# Unix timestamp → datetime (always pass tz=timezone.utc)
dt = datetime.fromtimestamp(1705334400, tz=timezone.utc)
print(dt)                                 # → 2024-01-15 16:00:00+00:00

# WRONG — no tz argument makes Python use the local timezone
dt_wrong = datetime.fromtimestamp(1705334400)
print(dt_wrong)   # → varies depending on server timezone
```

**Why:** Unix timestamps are defined as seconds since 1970-01-01 00:00:00 UTC. They have no timezone concept — they are always UTC. When you convert back to a datetime without specifying `tz=timezone.utc`, Python assumes local time, which will give a different (and often wrong) result on any server not in your own timezone.
</details>

---

<a id="q6"></a>

### Q6 🟡 · fromisoformat — ISO 8601 parsing

> 🛠️ **Solve locally:** [practice_local.py → Q6](./practice_local.py)



> Parse `"2024-03-15T09:30:00+05:30"` using `fromisoformat()`. Then explain the difference between `fromisoformat()` and `strptime()`.

<details>
<summary>Hint</summary>

- `fromisoformat()` understands the `+HH:MM` offset suffix natively (Python 3.7+).
- In Python 3.10 and earlier, the `"Z"` suffix is NOT handled by `fromisoformat()` — you need `.replace("Z", "+00:00")` first. Python 3.11+ fixed this.
- `strptime()` is more flexible — it works with any format you specify.
</details>

<details>
<summary>Answer</summary>

```python
from datetime import datetime

# fromisoformat — clean for ISO 8601 input
dt = datetime.fromisoformat("2024-03-15T09:30:00+05:30")
print(dt)           # → 2024-03-15 09:30:00+05:30
print(dt.tzinfo)    # → UTC+05:30

# Handling 'Z' suffix (Python < 3.11)
ts_z = "2024-03-15T09:30:00Z"
dt_z = datetime.fromisoformat(ts_z.replace("Z", "+00:00"))
print(dt_z)         # → 2024-03-15 09:30:00+00:00

# Python 3.11+ handles Z natively:
# dt_z = datetime.fromisoformat("2024-03-15T09:30:00Z")  # works on 3.11+
```

**Difference:** `fromisoformat()` is a fast, zero-configuration shortcut for ISO 8601 strings — no format string required. `strptime()` is flexible and can parse any format you can describe with percent-codes, but you must provide the exact format. Use `fromisoformat()` when you control or trust the input format; use `strptime()` when parsing arbitrary or legacy date strings.

**Why:** ISO 8601 is the interchange standard for timestamps in APIs and databases. `fromisoformat()` was designed specifically for this use case and is less error-prone than constructing a `strptime` format string manually.
</details>

---

<a id="q7"></a>

### Q7 🟡 · Timezone-aware datetimes

> 🛠️ **Solve locally:** [practice_local.py → Q7](./practice_local.py)



> Create a UTC datetime for `2024-03-15 09:30:00`, then convert it to `US/Eastern`. Explain what naive and aware datetimes are and why mixing them causes errors.

<details>
<summary>Hint</summary>

- Use `zoneinfo.ZoneInfo` (Python 3.9+) for named timezones.
- `.astimezone(tz)` converts an aware datetime to a different timezone — it does NOT change the actual moment in time, only the representation.
- Python raises `TypeError` if you try to compare or subtract a naive and an aware datetime.
</details>

<details>
<summary>Answer</summary>

```python
from datetime import datetime, timezone
from zoneinfo import ZoneInfo

# Create UTC aware datetime
dt_utc = datetime(2024, 3, 15, 9, 30, 0, tzinfo=timezone.utc)
print(dt_utc)       # → 2024-03-15 09:30:00+00:00

# Convert to US/Eastern
eastern = ZoneInfo("America/New_York")
dt_eastern = dt_utc.astimezone(eastern)
print(dt_eastern)   # → 2024-03-15 05:30:00-04:00  (EDT = UTC-4 in March)

# Attempting to mix naive and aware raises TypeError
naive = datetime(2024, 3, 15, 9, 30, 0)
try:
    result = dt_utc - naive
except TypeError as e:
    print(f"Error: {e}")
    # → Error: can't subtract offset-naive and offset-aware datetimes
```

**Naive vs aware:** A naive datetime has `tzinfo=None` — it is a clock reading with no location. An aware datetime carries a timezone, making it an unambiguous point in universal time. Python enforces this distinction strictly: you cannot compare, subtract, or mix naive and aware datetimes without an explicit conversion.

**Why:** Production systems receive datetimes from multiple sources: APIs send UTC ISO strings, databases return timezone-aware objects, and user input might be local time. Keeping all internal datetimes aware (in UTC) and converting to local only for display prevents an entire class of subtle ordering and comparison bugs.
</details>

---

<a id="q8"></a>

### Q8 🟡 · datetime.utcnow() pitfall

> 🛠️ **Solve locally:** [practice_local.py → Q8](./practice_local.py)



> Explain why `datetime.utcnow()` is dangerous. Demonstrate the problem with a code example and show what to use instead.

<details>
<summary>Hint</summary>

- `datetime.utcnow()` returns a naive datetime with the UTC time — but with no `tzinfo` attached.
- If you then compare it with an aware datetime, you get a `TypeError`.
- If you store it in a database and later read it back as a local time, you get the wrong time.
- The replacement is `datetime.now(tz=timezone.utc)`.
</details>

<details>
<summary>Answer</summary>

```python
from datetime import datetime, timezone

# datetime.utcnow() — returns naive UTC (deprecated in Python 3.12)
naive_utc = datetime.utcnow()
print(naive_utc)            # → 2024-03-15 09:30:00  (no +00:00)
print(naive_utc.tzinfo)     # → None   ← looks like local time!

# The problem — comparing with an aware datetime fails
aware_utc = datetime.now(tz=timezone.utc)
try:
    diff = aware_utc - naive_utc
except TypeError as e:
    print(f"TypeError: {e}")
    # → TypeError: can't subtract offset-naive and offset-aware datetimes

# The correct replacement
correct_utc = datetime.now(tz=timezone.utc)
print(correct_utc)          # → 2024-03-15 09:30:00+00:00
print(correct_utc.tzinfo)   # → UTC
```

**Why it's dangerous:** `datetime.utcnow()` returns a datetime that is in UTC value but has no timezone label. Any code that consumes it cannot tell whether it is UTC or local time. A developer in Tokyo might treat it as JST; a database driver might treat it as the server's local timezone. The result is silent data corruption. `datetime.now(tz=timezone.utc)` returns the same value but with `tzinfo=UTC` attached, making it unambiguous. It was deprecated in Python 3.12 for exactly this reason.
</details>

---

<a id="q9"></a>

### Q9 🟡 · Date arithmetic on a list

> 🛠️ **Solve locally:** [practice_local.py → Q9](./practice_local.py)



> Given a list of ISO date strings, sort them chronologically and find the date range (max date - min date in days).

```python
dates = [
    "2024-03-15",
    "2024-01-01",
    "2024-06-30",
    "2024-02-14",
    "2024-11-28",
]
```

<details>
<summary>Hint</summary>

- Parse each string with `date.fromisoformat()` (available on `date`, not just `datetime`).
- ISO 8601 date strings sort correctly as plain strings too — but parsed `date` objects are safer for arithmetic.
- `max(dates) - min(dates)` on `date` objects gives a `timedelta` — use `.days` to get the integer.
</details>

<details>
<summary>Answer</summary>

```python
from datetime import date

raw = [
    "2024-03-15",
    "2024-01-01",
    "2024-06-30",
    "2024-02-14",
    "2024-11-28",
]

# Parse to date objects
parsed = [date.fromisoformat(s) for s in raw]

# Sort chronologically
sorted_dates = sorted(parsed)
print("Sorted:", [str(d) for d in sorted_dates])
# → ['2024-01-01', '2024-02-14', '2024-03-15', '2024-06-30', '2024-11-28']

# Date range
earliest = min(parsed)
latest   = max(parsed)
span     = (latest - earliest).days
print(f"Range: {earliest} to {latest} = {span} days")
# → Range: 2024-01-01 to 2024-11-28 = 332 days
```

**Why:** Comparing date strings as strings works for ISO 8601 (`YYYY-MM-DD`) because the format sorts lexicographically. But you should still parse to `date` objects before doing arithmetic — string subtraction does not exist, and the `.days` attribute on a `timedelta` gives you an exact integer count that is safe across month and year boundaries.
</details>

---

<a id="q10"></a>

### Q10 🟡 · time module — Benchmarking

> 🛠️ **Solve locally:** [practice_local.py → Q10](./practice_local.py)



> Use `time.perf_counter()` to benchmark two approaches to building a large string: (1) concatenation with `+=`, (2) `"".join()`. Print the elapsed time for each.

<details>
<summary>Hint</summary>

- `time.perf_counter()` returns a float with the highest resolution available on the platform.
- Take two readings — before and after — and subtract to get elapsed seconds.
- For short operations, run them in a loop (e.g., 10,000 iterations) to amplify the timing difference.
</details>

<details>
<summary>Answer</summary>

```python
import time

N = 10_000

# Approach 1 — string concatenation with +=
start = time.perf_counter()
result = ""
for i in range(N):
    result += str(i)
elapsed_concat = time.perf_counter() - start

# Approach 2 — join (builds list first, then joins once)
start = time.perf_counter()
result = "".join(str(i) for i in range(N))
elapsed_join = time.perf_counter() - start

print(f"Concatenation: {elapsed_concat:.6f}s")
print(f"Join:          {elapsed_join:.6f}s")
print(f"Join is {elapsed_concat / elapsed_join:.1f}x faster")
# join is typically 3-10x faster for large N
```

**Why:** `time.perf_counter()` is the correct tool for benchmarking because it uses the highest-resolution clock available and is not affected by OS-level clock adjustments (unlike `time.time()`). The join approach is faster because Python strings are immutable — `+=` creates a new string object on every iteration, while `join` builds the list in memory and concatenates exactly once.
</details>

---

<a id="q11"></a>

### Q11 🟠 · Production logging with timestamps

> 🛠️ **Solve locally:** [practice_local.py → Q11](./practice_local.py)



> Write a `log_event(event: str)` function that prints a log line with: (1) UTC timestamp in ISO format, (2) the local time offset from UTC. Example output: `[2024-03-15T09:30:00Z | local offset: -05:00] user_login`.

<details>
<summary>Hint</summary>

- `datetime.now(tz=timezone.utc)` for UTC time, `.isoformat()` for the string.
- `datetime.now().astimezone()` returns a local-time aware datetime — the `.utcoffset()` method gives the offset as a `timedelta`.
- Format the offset as `+HH:MM` or `-HH:MM`: total seconds from `utcoffset()` divided into hours and minutes.
</details>

<details>
<summary>Answer</summary>

```python
from datetime import datetime, timezone

def log_event(event: str) -> None:
    # UTC timestamp
    now_utc = datetime.now(tz=timezone.utc)
    utc_str = now_utc.strftime("%Y-%m-%dT%H:%M:%SZ")

    # Local offset — astimezone() without args uses system timezone
    local_dt = now_utc.astimezone()
    offset = local_dt.utcoffset()
    total_seconds = int(offset.total_seconds())
    sign = "+" if total_seconds >= 0 else "-"
    total_seconds = abs(total_seconds)
    hours, remainder = divmod(total_seconds, 3600)
    minutes = remainder // 60
    offset_str = f"{sign}{hours:02d}:{minutes:02d}"

    print(f"[{utc_str} | local offset: {offset_str}] {event}")

log_event("user_login")
# → [2024-03-15T09:30:00Z | local offset: -05:00] user_login
```

**Why:** Production logs should always include UTC time so that events from servers in different timezones can be correlated precisely. Including the local offset helps on-call engineers who are reading logs in their local context — they can quickly calculate the local time without doing timezone arithmetic in their head. UTC as the base prevents ambiguity; the offset is supplemental information only.
</details>

---

<a id="q12"></a>

### Q12 🟠 · Capstone — Normalize mixed date formats

> 🛠️ **Solve locally:** [practice_local.py → Q12](./practice_local.py)



> Parse a list of dates in mixed formats, normalize them all to ISO 8601 UTC strings (`"YYYY-MM-DDT00:00:00Z"`), and return them sorted chronologically.

```python
mixed_dates = [
    "2024-03-15",
    "15/03/2024",
    "March 15 2024",
    "2024-01-01",
    "01/25/2024",
    "February 14 2024",
]
```

<details>
<summary>Hint</summary>

- Try each format in sequence using a helper that returns `None` on failure.
- The three formats are: `"%Y-%m-%d"`, `"%d/%m/%Y"`, `"%B %d %Y"`.
- Watch out: `"01/25/2024"` cannot be `%d/%m/%Y` because day 25 is valid but month 25 is not — use `%m/%d/%Y` for US-format slashed dates.
- After parsing, attach `timezone.utc` using `.replace(tzinfo=timezone.utc)` (since the input has no timezone info), then format with `strftime` or `isoformat`.
</details>

<details>
<summary>Answer</summary>

```python
from datetime import datetime, timezone

FORMATS = [
    "%Y-%m-%d",      # 2024-03-15
    "%d/%m/%Y",      # 15/03/2024  (day first — European)
    "%m/%d/%Y",      # 01/25/2024  (month first — US)
    "%B %d %Y",      # March 15 2024
]

def try_parse(date_str: str) -> datetime | None:
    for fmt in FORMATS:
        try:
            return datetime.strptime(date_str, fmt)
        except ValueError:
            continue
    return None

def normalize(date_str: str) -> str:
    dt = try_parse(date_str)
    if dt is None:
        raise ValueError(f"Cannot parse date: {date_str!r}")
    # Attach UTC (inputs are date-only, no timezone info)
    dt_utc = dt.replace(tzinfo=timezone.utc)
    return dt_utc.strftime("%Y-%m-%dT%H:%M:%SZ")

mixed_dates = [
    "2024-03-15",
    "15/03/2024",
    "March 15 2024",
    "2024-01-01",
    "01/25/2024",
    "February 14 2024",
]

normalized = sorted(normalize(d) for d in mixed_dates)
for d in normalized:
    print(d)
# → 2024-01-01T00:00:00Z
# → 2024-02-14T00:00:00Z
# → 2024-03-15T00:00:00Z
# → 2024-03-15T00:00:00Z
# → 2024-03-15T00:00:00Z
# → 2024-01-25T00:00:00Z  (01/25/2024 parsed as US month/day)
```

**Why:** Real-world data is messy. CSVs from different regions use different date conventions; user input is unpredictable. The try-each-format pattern is a pragmatic solution when you cannot enforce a single format at the source. Sorting ISO 8601 strings works correctly because `YYYY-MM-DD` is lexicographically ordered. Attaching UTC before storing ensures that downstream systems, databases, and APIs all interpret the value consistently regardless of server timezone.
</details>

---

## 🔁 Navigation

| | |
|---|---|
| 📖 Theory | [theory.md](./theory.md) |
| 💻 Local Practice | [practice_local.py](./practice_local.py) |
| ⬅️ Back to Module | [08_file_handling/theory.md](../theory.md) |
| ⬅️ Prev Subfolder | [02_pathlib ←](../02_pathlib/theory.md) |

---

**Related:** [01_os_module](../01_os_module/theory.md) · [02_pathlib](../02_pathlib/theory.md)
