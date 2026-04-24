# The `datetime` Module — Handling Time Correctly in Python

Time is the most deceptively complex thing in programming. A timestamp looks like just a number. A date looks like just three integers. But underneath that simplicity hides a web of decisions: which timezone? Does this region observe daylight saving time? Did a leap second occur? Which calendar?

Consider an airline booking system. A customer in New York books a flight "departing at 3:00 PM." That sentence is meaningless without knowing which city the departure is from. New York at 3 PM and Los Angeles at 3 PM are three hours apart — the same flight cannot depart at both. Every bug that stems from treating time as a simple number traces back to forgetting this: **"3 PM" means nothing without a location, and a location means nothing without knowing its current offset from UTC**.

Python's `datetime` module gives you the tools to handle time correctly. But the tools only work if you use them carefully — especially around timezones.

```python
from datetime import datetime, date, time, timedelta, timezone
```

---

## The Four Main Types

The `datetime` module provides four classes, each representing a different concept:

```
datetime module types:

  date          → just a calendar day      2024-01-15
  time          → just a time of day       14:30:00
  datetime      → both combined            2024-01-15 14:30:00
  timedelta     → a duration               7 days, 3 hours

  date + time  ──────────────────────────► datetime
  datetime - datetime  ──────────────────► timedelta
  datetime + timedelta ──────────────────► datetime
```

In practice, **`datetime`** and **`timedelta`** are what you use most often. `date` is useful when you genuinely have no time component (e.g., a birthday). `time` alone is rare — it is hard to work with without a date.

```python
from datetime import datetime, date, time, timedelta

# date — no time component
d = date(2024, 1, 15)
print(d)                   # → 2024-01-15

# time — no date component
t = time(14, 30, 0)
print(t)                   # → 14:30:00

# datetime — the workhorse
dt = datetime(2024, 1, 15, 14, 30, 0)
print(dt)                  # → 2024-01-15 14:30:00

# timedelta — a duration
delta = timedelta(days=7, hours=3)
print(delta)               # → 7 days, 3:00:00
```

---

## Creating datetime Objects

**From the current moment:**

```python
from datetime import datetime, timezone

# Local time — naive (no timezone info attached)
now_local = datetime.now()
# → datetime(2024, 1, 15, 14, 30, 22, 583421)
# ← "naive" means the datetime object has no timezone attached
# ← Python cannot know whether this is New York or Berlin time

# UTC — the correct way (aware datetime with UTC timezone)
now_utc = datetime.now(tz=timezone.utc)
# → datetime(2024, 1, 15, 19, 30, 22, 583421, tzinfo=datetime.timezone.utc)
# ← "aware" means it knows which timezone it is in

# DEPRECATED as of Python 3.12 — avoid in new code
now_utc_old = datetime.utcnow()
# ← returns naive UTC — dangerous because it looks like local time
```

**Explicit construction:**

```python
from datetime import datetime, date

# datetime(year, month, day, hour, minute, second, microsecond)
dt = datetime(2024, 1, 15, 14, 30, 0)           # ← hour/min/sec default to 0
dt = datetime(2024, 1, 15, 14, 30, 0, 123456)   # ← with microseconds

# date only
d = date(2024, 1, 15)
d = date.today()          # ← today's date in local timezone
```

**From a Unix timestamp:**

```python
from datetime import datetime, timezone

ts = 1705334400   # Unix timestamp (seconds since 1970-01-01 00:00:00 UTC)

# Convert to UTC datetime (aware)
dt_utc = datetime.fromtimestamp(ts, tz=timezone.utc)
print(dt_utc)     # → 2024-01-15 16:00:00+00:00

# Convert to local time (aware, uses system timezone)
dt_local = datetime.fromtimestamp(ts)
print(dt_local)   # → varies by system timezone
```

---

## timedelta — Date Arithmetic

A **`timedelta`** represents a duration — the distance between two points in time. It supports clean arithmetic with datetime objects.

```python
from datetime import datetime, timedelta, timezone

now = datetime.now(tz=timezone.utc)

# Create a timedelta
one_week    = timedelta(days=7)
ninety_mins = timedelta(hours=1, minutes=30)
one_day     = timedelta(days=1)

# Add to a datetime
next_week   = now + one_week
yesterday   = now - one_day
in_90_mins  = now + ninety_mins

# timedelta components
d = timedelta(days=2, hours=5, minutes=30, seconds=15)
print(d.days)              # → 2    (whole days only)
print(d.seconds)           # → 19815  (remaining seconds after whole days)
print(d.total_seconds())   # → 192015.0  (everything as total seconds — use this)
```

**The `.seconds` vs `.total_seconds()` trap:**

```python
from datetime import timedelta

d = timedelta(days=2, hours=3)

print(d.seconds)           # → 10800   (3 hours * 3600 — does NOT include days)
print(d.total_seconds())   # → 183600.0  (2 days + 3 hours in seconds — correct)
# ← always use total_seconds() unless you specifically want the sub-day remainder
```

**Common calculations:**

```python
from datetime import datetime, date, timedelta, timezone

now = datetime.now(tz=timezone.utc)
today = date.today()

# N days ago / from now
seven_days_ago  = now - timedelta(days=7)
thirty_days_out = now + timedelta(days=30)

# Age from birthdate
birthday = date(1990, 6, 15)
age_days = (today - birthday).days
age_years = age_days // 365              # ← approximate; use dateutil for precision

# Difference between two datetimes
start = datetime(2024, 1, 1, 9, 0, 0, tzinfo=timezone.utc)
end   = datetime(2024, 1, 1, 17, 30, 0, tzinfo=timezone.utc)
elapsed = end - start                    # → timedelta
print(elapsed.total_seconds() / 3600)   # → 8.5 hours
```

---

## strftime — Formatting datetime as a String

**`strftime`** ("string format time") converts a datetime object into a human-readable string. You provide a format string made up of percent-codes.

```python
from datetime import datetime, timezone

dt = datetime(2024, 1, 15, 14, 30, 5, 123456, tzinfo=timezone.utc)

# ISO 8601 — the universal standard for machine-readable timestamps
dt.strftime("%Y-%m-%dT%H:%M:%S")        # → '2024-01-15T14:30:05'
dt.strftime("%Y-%m-%dT%H:%M:%S.%f")     # → '2024-01-15T14:30:05.123456'
dt.strftime("%Y-%m-%dT%H:%M:%S%z")      # → '2024-01-15T14:30:05+0000'

# Shortcut — isoformat() is cleaner
dt.isoformat()                           # → '2024-01-15T14:30:05.123456+00:00'
```

**Common format codes:**

| Code | Meaning | Example |
|---|---|---|
| `%Y` | 4-digit year | `2024` |
| `%m` | Month as zero-padded number | `01` |
| `%d` | Day as zero-padded number | `15` |
| `%H` | Hour (24-hour clock), zero-padded | `14` |
| `%M` | Minute, zero-padded | `30` |
| `%S` | Second, zero-padded | `05` |
| `%f` | Microseconds, zero-padded to 6 digits | `123456` |
| `%Z` | Timezone name | `UTC` |
| `%z` | UTC offset as `±HHMM` | `+0000` |
| `%A` | Full weekday name | `Monday` |
| `%b` | Abbreviated month name | `Jan` |

**Common formats in practice:**

```python
from datetime import datetime, timezone

dt = datetime(2024, 1, 15, 14, 30, 5, tzinfo=timezone.utc)

dt.strftime("%Y-%m-%d")                  # → '2024-01-15'           ISO date
dt.strftime("%Y-%m-%d %H:%M:%S")         # → '2024-01-15 14:30:05'  ISO datetime
dt.strftime("%B %d, %Y")                 # → 'January 15, 2024'     Human-readable
dt.strftime("%m/%d/%Y")                  # → '01/15/2024'            US format
dt.strftime("%d/%m/%Y")                  # → '15/01/2024'            European format
dt.strftime("%Y-%m-%dT%H:%M:%SZ")        # → '2024-01-15T14:30:05Z' RFC 3339 / API
dt.strftime("[%Y-%m-%d %H:%M:%S]")       # → '[2024-01-15 14:30:05]' Log format
```

---

## strptime — Parsing a String to datetime

**`strptime`** ("string parse time") is the reverse of `strftime`: it takes a string and a format, and returns a datetime object.

```python
from datetime import datetime

# strptime(string, format)
dt = datetime.strptime("2024-01-15", "%Y-%m-%d")
print(dt)                        # → 2024-01-15 00:00:00

dt = datetime.strptime("15/01/2024 14:30", "%d/%m/%Y %H:%M")
print(dt)                        # → 2024-01-15 14:30:00

# Wrong format → ValueError
datetime.strptime("2024-01-15", "%d/%m/%Y")
# → ValueError: time data '2024-01-15' does not match format '%d/%m/%Y'
```

**`fromisoformat` — the shortcut for ISO 8601 strings:**

```python
from datetime import datetime

# Available in Python 3.7+
dt = datetime.fromisoformat("2024-01-15T14:30:00")
print(dt)                        # → 2024-01-15 14:30:00

# Python 3.11+ handles the full ISO 8601 spec including 'Z' suffix
dt = datetime.fromisoformat("2024-01-15T14:30:00+00:00")
print(dt)                        # → 2024-01-15 14:30:00+00:00  (aware datetime)

# For Python 3.10 and earlier, strip 'Z' or replace it manually
ts = "2024-01-15T14:30:00Z"
dt = datetime.fromisoformat(ts.replace("Z", "+00:00"))
```

**Handling parse errors:**

```python
from datetime import datetime

def parse_date_safe(s, fmt="%Y-%m-%d"):
    """Return parsed datetime or None on failure."""
    try:
        return datetime.strptime(s, fmt)
    except ValueError:
        return None

result = parse_date_safe("not-a-date")
if result is None:
    print("Invalid date string")
```

---

## Timezones — The Hard Part

This is where most datetime bugs live.

A **naive datetime** is one with no timezone information attached — `tzinfo` is `None`. An **aware datetime** has explicit timezone information. Python never implicitly converts between them: comparing a naive and an aware datetime raises a `TypeError`.

```
Naive datetime:   datetime(2024, 1, 15, 14, 30)
                  → Python has no idea what timezone this is
                  → Dangerous in any multi-timezone system

Aware datetime:   datetime(2024, 1, 15, 14, 30, tzinfo=timezone.utc)
                  → Unambiguous — pinned to UTC
                  → Safe to store, compare, and transmit
```

**The built-in UTC timezone:**

```python
from datetime import datetime, timezone

# timezone.utc is always available — no import needed beyond datetime
now_utc = datetime.now(tz=timezone.utc)   # ← aware, UTC
```

**`zoneinfo` — IANA timezones in the standard library (Python 3.9+):**

```python
from datetime import datetime
from zoneinfo import ZoneInfo              # ← standard library in Python 3.9+

# Create aware datetimes in specific timezones
now_nyc = datetime.now(tz=ZoneInfo("America/New_York"))
now_lon = datetime.now(tz=ZoneInfo("Europe/London"))
now_tok = datetime.now(tz=ZoneInfo("Asia/Tokyo"))

# Convert between timezones
now_utc = datetime.now(tz=ZoneInfo("UTC"))
now_la  = now_utc.astimezone(ZoneInfo("America/Los_Angeles"))
print(now_la)   # → same instant, displayed in LA time
```

**`pytz` — for Python versions before 3.9:**

```python
import pytz
from datetime import datetime

# pytz requires calling localize() — do not use replace(tzinfo=...)
tz_nyc = pytz.timezone("America/New_York")
now_nyc = datetime.now(tz_nyc)

# Convert
now_utc = now_nyc.astimezone(pytz.utc)
```

**The golden rule for production systems:**

```
Store everything in UTC.
Display in the user's local timezone only at the last moment (rendering).
```

```python
from datetime import datetime, timezone
from zoneinfo import ZoneInfo

# When an event happens, store it as UTC
event_time = datetime.now(tz=timezone.utc)
# Store event_time in your database — always UTC

# When displaying to a user in Tokyo
user_tz = ZoneInfo("Asia/Tokyo")
display_time = event_time.astimezone(user_tz)
print(display_time.strftime("%Y-%m-%d %H:%M %Z"))   # → '2024-01-16 04:30 JST'
```

**Why naive datetimes are dangerous in production:**

```python
from datetime import datetime, timezone

# This looks fine locally
naive_dt = datetime(2024, 1, 15, 14, 30)    # naive — no timezone

# This raises TypeError — cannot compare naive and aware
aware_dt = datetime.now(tz=timezone.utc)
naive_dt < aware_dt                          # → TypeError: can't compare offset-naive
                                             #   and offset-aware datetimes

# Rule: if you ever write datetime.now() without tz=... you have a naive datetime
# Rule: never store naive datetimes in production databases
```

---

## Unix Timestamps

A **Unix timestamp** (also called epoch time) is the number of seconds elapsed since January 1, 1970, 00:00:00 UTC. It is always in UTC — there are no timezones in a Unix timestamp.

```python
from datetime import datetime, timezone
import time

# Current Unix timestamp
ts = time.time()                      # → 1705334400.583
ts_int = int(time.time())             # → 1705334400  (integer seconds)

# datetime to Unix timestamp
dt = datetime(2024, 1, 15, 16, 0, 0, tzinfo=timezone.utc)
ts = dt.timestamp()
print(ts)                             # → 1705334400.0

# Unix timestamp to datetime (always specify UTC)
dt = datetime.fromtimestamp(1705334400, tz=timezone.utc)
print(dt)                             # → 2024-01-15 16:00:00+00:00

# WRONG — fromtimestamp without tz uses local timezone
dt_local = datetime.fromtimestamp(1705334400)   # ← naive, local time — unreliable
```

Timestamps are the safest way to pass time between systems because they are always UTC and always unambiguous. Store timestamps in databases when portability matters. Store datetime strings in ISO 8601 format with UTC offset when human readability matters.

---

## The `time` Module — Process Timing and Sleep

The `time` module is different from `datetime`. Where `datetime` is about calendar dates and times, `time` is about process timing, sleeping, and high-resolution clocks.

```python
import time

# Current Unix timestamp as a float
ts = time.time()
print(ts)          # → 1705334400.583421

# Pause execution for N seconds
time.sleep(0.5)    # ← sleep 500 milliseconds
time.sleep(2)      # ← sleep 2 seconds
```

**Three clocks and when to use each:**

```
time.time()          Wall-clock time — can jump forward or backward
                     (NTP sync, DST, manual adjustment)
                     Use for: timestamps you store or send to other systems

time.monotonic()     Never goes backward — always increases
                     (starts at an arbitrary point, not Unix epoch)
                     Use for: measuring elapsed time within a process

time.perf_counter()  Highest resolution available on the platform
                     (fractional seconds, implementation-specific start)
                     Use for: benchmarking, measuring short durations precisely
```

```python
import time

# WRONG — time.time() can go backward (clock adjustments, DST)
start = time.time()
do_work()
elapsed = time.time() - start       # ← unreliable for duration measurement

# CORRECT — monotonic clock for elapsed time
start = time.monotonic()
do_work()
elapsed = time.monotonic() - start  # ← always positive, always increasing

# BEST — perf_counter for benchmarking
start = time.perf_counter()
do_work()
elapsed = time.perf_counter() - start
print(f"Elapsed: {elapsed:.4f}s")   # → Elapsed: 0.0023s
```

**Timing code with perf_counter:**

```python
import time
from functools import wraps

def timer(func):
    """Decorator that prints how long a function takes."""
    @wraps(func)
    def wrapper(*args, **kwargs):
        start = time.perf_counter()
        result = func(*args, **kwargs)
        elapsed = time.perf_counter() - start
        print(f"{func.__name__} took {elapsed:.4f}s")
        return result
    return wrapper

@timer
def slow_function():
    time.sleep(0.1)
    return "done"

slow_function()   # → slow_function took 0.1003s
```

---

## Production Patterns

**Expiry check:**

```python
from datetime import datetime, timezone

expires_at = datetime(2024, 6, 30, 0, 0, 0, tzinfo=timezone.utc)

if datetime.now(timezone.utc) > expires_at:
    raise PermissionError("Token has expired")
```

**Date range check:**

```python
from datetime import datetime, timezone

def is_in_range(dt, start, end):
    """Check if dt falls within [start, end] inclusive."""
    return start <= dt <= end

start = datetime(2024, 1, 1, tzinfo=timezone.utc)
end   = datetime(2024, 12, 31, 23, 59, 59, tzinfo=timezone.utc)
event = datetime.now(tz=timezone.utc)

if is_in_range(event, start, end):
    print("Event is within the 2024 range")
```

**"Last 30 days" query:**

```python
from datetime import datetime, timedelta, timezone

now            = datetime.now(tz=timezone.utc)
thirty_days_ago = now - timedelta(days=30)

# Build your SQL query using these bounds
query = """
    SELECT * FROM events
    WHERE created_at >= %(start)s
      AND created_at <= %(end)s
"""
params = {"start": thirty_days_ago, "end": now}
```

**Age from birthdate:**

```python
from datetime import date

def calculate_age(birthdate: date) -> int:
    today = date.today()
    years = today.year - birthdate.year
    # Subtract 1 if birthday hasn't occurred yet this year
    if (today.month, today.day) < (birthdate.month, birthdate.day):
        years -= 1
    return years

age = calculate_age(date(1990, 6, 15))
print(f"Age: {age}")
```

**Log timestamp formatting:**

```python
from datetime import datetime, timezone

def log(message):
    ts = datetime.now(tz=timezone.utc).strftime("%Y-%m-%d %H:%M:%S UTC")
    print(f"[{ts}] {message}")

log("Starting job")    # → [2024-01-15 14:30:05 UTC] Starting job
```

**Measuring function execution time:**

```python
import time
from datetime import timedelta

start = time.perf_counter()

# ... do work ...

elapsed_seconds = time.perf_counter() - start
elapsed = timedelta(seconds=elapsed_seconds)
print(f"Completed in {elapsed}")   # → Completed in 0:00:02.348210
```

---

## Common Mistakes

| Mistake | What happens | Fix |
|---|---|---|
| Comparing naive datetime with aware datetime | `TypeError: can't compare offset-naive and offset-aware datetimes` | Always use aware datetimes; add `tz=timezone.utc` when creating |
| `datetime.utcnow()` in Python 3.12+ | `DeprecationWarning`; returns naive UTC (looks like local time) | Use `datetime.now(tz=timezone.utc)` |
| Storing local time in the database | Queries fail across DST boundaries; timestamps shift when server timezone changes | Always store UTC; convert to local only for display |
| `timedelta.seconds` instead of `timedelta.total_seconds()` | `.seconds` excludes the days component — gives wrong results for durations > 24h | Always use `.total_seconds()` for total elapsed seconds |
| Forgetting `%f` in strptime when string has microseconds | `ValueError: unconverted data remains: .123456` | Include `%f` in the format string, or use `fromisoformat()` |
| `datetime.fromtimestamp(ts)` without `tz=` | Returns naive local time — inconsistent across servers in different timezones | Always `datetime.fromtimestamp(ts, tz=timezone.utc)` |
| Using `time.time()` to measure elapsed duration | Can give negative results if the system clock is adjusted during measurement | Use `time.monotonic()` for elapsed time |
| `"Z"` suffix in ISO strings on Python < 3.11 | `fromisoformat("2024-01-15T14:30:00Z")` raises `ValueError` | Use `.replace("Z", "+00:00")` before calling `fromisoformat` |

---

## Navigation

**Related:**
- [File Handling Theory](./theory.md) — file I/O, buffering, CSV, JSON
- [os Module](./os_module.md) — file metadata timestamps, `os.path.getmtime()`
- [Logging and Debugging Theory](../09_logging_debugging/theory.md) — log formatting with timestamps
