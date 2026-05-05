"""
==============================================================================
MODULE 09 — Logging & Debugging
==============================================================================
Run with: python3 practice.py

Story: It's 3 AM. Orders are failing. Customers can't check out.
The on-call engineer opens the server and finds... nothing. Just:
  "Exception in thread: <unknown error>"

This is why logging exists. This file walks you from the first naive
'print()' all the way to production-grade structured logging, multiple
handlers, formatters, log levels, and the debugging patterns used by
senior engineers to find bugs fast.

Concepts covered:
  - logging.basicConfig — quick setup
  - Log levels: DEBUG / INFO / WARNING / ERROR / CRITICAL
  - logging.getLogger(__name__) — named loggers
  - Formatters — controlling log message format
  - StreamHandler + FileHandler — where logs go
  - logging.exception() inside except blocks
  - Logger hierarchy and propagation
  - Multiple handlers on one logger
  - Logging in functions and classes
  - RotatingFileHandler — preventing disk full
  - Assertions — fast sanity checks during development
  - pdb patterns — shown as commented examples (can't be interactive)
  - traceback module — programmatic traceback capture
  - warnings module — non-fatal alerts
  - Common debugging patterns
==============================================================================
"""

import logging
import logging.handlers
import sys
import os
import traceback
import warnings
import tempfile
from pathlib import Path


# ==============================================================================
# CONCEPT 1: print() vs logging — why logging wins
# ==============================================================================
print("\n" + "="*60)
print("CONCEPT 1: print() vs logging")
print("="*60)

"""
print() problems in production:
  - No timestamp (when did it happen?)
  - No severity (is it info or a crash?)
  - Goes to stdout only (mixed with all other output)
  - No module/line context (where in the code?)
  - Cannot be turned off without changing code
  - Not searchable in log aggregators

logging advantages:
  - Timestamp built-in
  - 5 severity levels — filter noise vs signal
  - Multiple destinations (console, file, HTTP, email)
  - Module + function + line number included
  - Controlled by level — DEBUG off in production = zero cost
  - Structured/JSON output → searchable in Elasticsearch/Splunk
"""

# The wrong way — print debugging
def bad_process_payment(amount):
    print(f"Processing payment {amount}")    # no timestamp, no level
    if amount <= 0:
        print(f"Error: bad amount {amount}") # lost in stdout noise
        return False
    return True

bad_process_payment(100)
bad_process_payment(-5)
print("  ^ Above is print() output — no timestamp, no level, no context")


# ==============================================================================
# CONCEPT 2: Log levels — the severity scale
# ==============================================================================
print("\n" + "="*60)
print("CONCEPT 2: Log levels")
print("="*60)

"""
LEVEL     NUMERIC   WHEN TO USE
DEBUG     10        Detailed internals. Development only.
                    "Entering calculate_tax(amount=499.00, rate=0.09)"
INFO      20        Normal milestones. Always-on in production.
                    "User alice@example.com logged in"
WARNING   30        Unexpected but not broken. Worth investigating.
                    "Retry 2/3 for Stripe API call"
ERROR     40        An operation failed. Needs investigation.
                    "Payment processing failed for order #4892"
CRITICAL  50        System cannot function. Wake someone up.
                    "Cannot connect to database — service shutting down"

The DEFAULT level is WARNING — DEBUG and INFO are hidden until you configure!
"""

# Demonstrate default behavior (root logger, WARNING threshold)
print("  Default root logger (WARNING threshold):")
logging.debug("DEBUG message — HIDDEN by default")
logging.info("INFO message  — HIDDEN by default")
logging.warning("WARNING message — SHOWN")
logging.error("ERROR message   — SHOWN")
logging.critical("CRITICAL message — SHOWN")

print("\n  Level numeric values:")
for name, value in [("DEBUG", logging.DEBUG), ("INFO", logging.INFO),
                    ("WARNING", logging.WARNING), ("ERROR", logging.ERROR),
                    ("CRITICAL", logging.CRITICAL)]:
    print(f"    logging.{name:8s} = {value}")


# ==============================================================================
# CONCEPT 3: basicConfig — quick setup
# ==============================================================================
print("\n" + "="*60)
print("CONCEPT 3: basicConfig — quick configuration")
print("="*60)

"""
logging.basicConfig() configures the ROOT logger.
Key rule: basicConfig only takes effect ONCE — the first call wins.
If any handler is already attached to the root logger (e.g. from a library),
basicConfig does nothing. For reliable setup, configure handlers manually.
"""

# Reset root logger for demo (normally you wouldn't do this)
root_logger = logging.getLogger()
root_logger.handlers.clear()

logging.basicConfig(
    level=logging.DEBUG,
    format="%(asctime)s | %(levelname)-8s | %(name)s:%(lineno)d | %(message)s",
    datefmt="%H:%M:%S",
    stream=sys.stdout,
)

print("  After basicConfig(level=DEBUG):")
logging.debug("DEBUG is now visible")
logging.info("INFO is now visible")
logging.warning("WARNING as usual")

print(f"\n  Root logger level: {logging.getLevelName(logging.getLogger().level)}")
print(f"  Root handlers: {logging.getLogger().handlers}")


# ==============================================================================
# CONCEPT 4: Named loggers with getLogger(__name__)
# ==============================================================================
print("\n" + "="*60)
print("CONCEPT 4: Named loggers — getLogger(__name__)")
print("="*60)

"""
Always use logging.getLogger(__name__) instead of the root logger.

Benefits:
  1. Logger name shows exactly WHICH module logged the message
  2. Logger hierarchy: "myapp.services.payment" inherits from "myapp.services"
     inherits from "myapp" inherits from root
  3. You can silence noisy third-party libraries without affecting your code:
       logging.getLogger("sqlalchemy").setLevel(logging.WARNING)

In __name__:
  Running as script: __name__ == "__main__"
  When imported:     __name__ == "myapp.services.payment" (the module path)
"""

# Create loggers for different "modules" to show the hierarchy
app_logger     = logging.getLogger("myapp")
models_logger  = logging.getLogger("myapp.models")
payment_logger = logging.getLogger("myapp.services.payment")
api_logger     = logging.getLogger("myapp.api")

print("  Logger hierarchy:")
for lgr in [app_logger, models_logger, payment_logger, api_logger]:
    print(f"    {lgr.name!r:35s} parent={lgr.parent.name!r}")

# Named loggers without their own handlers propagate to parent
payment_logger.debug("Payment debug from myapp.services.payment")
payment_logger.info("Payment info — check the name in the output")


# ==============================================================================
# CONCEPT 5: Formatters — controlling what logs look like
# ==============================================================================
print("\n" + "="*60)
print("CONCEPT 5: Formatters")
print("="*60)

"""
Format fields (most useful):
  %(asctime)s    — human timestamp: "2025-01-15 14:30:00,123"
  %(levelname)s  — DEBUG / INFO / WARNING / ERROR / CRITICAL
  %(name)s       — logger name
  %(module)s     — module name (filename without .py)
  %(funcName)s   — function name
  %(lineno)d     — line number
  %(message)s    — the actual log message
  %(process)d    — process ID (useful in multiprocessing)
  %(thread)d     — thread ID (useful in threading)

Padding: %(levelname)-8s pads to 8 chars, left-aligned → aligned columns
"""

# Three common format styles
formats = {
    "minimal":     "%(levelname)s: %(message)s",
    "development": "%(asctime)s | %(levelname)-8s | %(name)s:%(lineno)d | %(message)s",
    "with_func":   "[%(name)s] %(funcName)s():%(lineno)d — %(message)s",
}

# Demonstrate each format with a temporary handler
test_logger = logging.getLogger("format_demo")
test_logger.propagate = False   # don't propagate to root for this demo
test_logger.setLevel(logging.DEBUG)

for fmt_name, fmt_str in formats.items():
    # Replace handler with new formatter
    test_logger.handlers.clear()
    handler = logging.StreamHandler(sys.stdout)
    handler.setFormatter(logging.Formatter(fmt=fmt_str, datefmt="%H:%M:%S"))
    handler.setLevel(logging.DEBUG)
    test_logger.addHandler(handler)

    print(f"\n  Format: {fmt_name!r}")
    test_logger.info("Sample INFO message")
    test_logger.error("Sample ERROR message")


# ==============================================================================
# CONCEPT 6: Handlers — WHERE logs go
# ==============================================================================
print("\n" + "="*60)
print("CONCEPT 6: Handlers — StreamHandler + FileHandler")
print("="*60)

"""
A logger can have MULTIPLE handlers — send to console AND file AND email.
Each handler has its own level and formatter.

Common handlers:
  StreamHandler(stream)        — console (stdout or stderr)
  FileHandler(filename)        — plain file
  RotatingFileHandler          — file with size-based rotation
  TimedRotatingFileHandler     — file with time-based rotation
  NullHandler()                — no output (for library code)
"""

# Create a logger with both console and file output
multi_logger = logging.getLogger("multi_handler_demo")
multi_logger.setLevel(logging.DEBUG)    # let everything through to handlers
multi_logger.propagate = False          # don't double-log to root

# Formatter
fmt = logging.Formatter(
    "%(asctime)s | %(levelname)-8s | %(name)s | %(message)s",
    datefmt="%H:%M:%S"
)

# Handler 1: console — INFO and above
console_handler = logging.StreamHandler(sys.stdout)
console_handler.setLevel(logging.INFO)   # filters below INFO
console_handler.setFormatter(fmt)

# Handler 2: file — ALL levels (DEBUG and above)
tmp_log = tempfile.NamedTemporaryFile(
    mode="w", suffix=".log", delete=False, encoding="utf-8"
)
tmp_log.close()
file_handler = logging.FileHandler(tmp_log.name, encoding="utf-8")
file_handler.setLevel(logging.DEBUG)    # captures everything
file_handler.setFormatter(fmt)

multi_logger.addHandler(console_handler)
multi_logger.addHandler(file_handler)

print(f"  Log file: {tmp_log.name}")
print(f"  Emitting messages at all levels:\n")
multi_logger.debug("Debug details — only in file, not console")
multi_logger.info("Service started successfully")
multi_logger.warning("Response time 3.2s — above 2s threshold")
multi_logger.error("Payment failed for order #4892")

# Show that DEBUG went to file but not console
with open(tmp_log.name, encoding="utf-8") as f:
    file_content = f.read()
print(f"\n  File handler captured (including DEBUG):")
for line in file_content.strip().split("\n"):
    print(f"    {line}")

os.unlink(tmp_log.name)  # cleanup


# ==============================================================================
# CONCEPT 7: logging.exception() — the right way inside except blocks
# ==============================================================================
print("\n" + "="*60)
print("CONCEPT 7: logging.exception() inside except blocks")
print("="*60)

"""
logger.exception() = logger.error() + exc_info=True

It logs at ERROR level AND automatically includes the full traceback.
ALWAYS use this (or logger.error(..., exc_info=True)) inside except blocks.
Never: print(f"Error: {e}") — no traceback, no level, not searchable.
Never: pass — silently swallows the error entirely.
"""

exc_logger = logging.getLogger("exception_demo")
exc_logger.setLevel(logging.DEBUG)
exc_logger.propagate = False
exc_handler = logging.StreamHandler(sys.stdout)
exc_handler.setFormatter(logging.Formatter("  %(levelname)s | %(message)s"))
exc_logger.addHandler(exc_handler)

# Pattern 1: logger.exception() — most common
print("  Pattern 1: logger.exception() — logs ERROR + full traceback")
try:
    result = 10 / 0
except ZeroDivisionError:
    exc_logger.exception("Division failed — full traceback follows")

# Pattern 2: logger.error() with exc_info=True — same output
print("\n  Pattern 2: logger.error(..., exc_info=True)")
try:
    int("not_a_number")
except ValueError as e:
    exc_logger.error("Value conversion failed: %s", e, exc_info=True)

# Pattern 3: log + re-raise (service layer pattern)
print("\n  Pattern 3: log then re-raise")
def fetch_config(key: str) -> str:
    config = {}
    try:
        return config[key]
    except KeyError:
        exc_logger.exception("Config key '%s' not found", key)
        raise   # caller decides the recovery strategy

try:
    fetch_config("DATABASE_URL")
except KeyError as e:
    print(f"  Caller caught re-raised exception: KeyError({e})")

# Pattern 4: WRONG — what NOT to do
print("\n  Pattern 4: WRONG — silent swallow (never do this)")
try:
    1 / 0
except ZeroDivisionError:
    pass   # error disappears completely — nightmare to debug


# ==============================================================================
# CONCEPT 8: Logging in functions and classes
# ==============================================================================
print("\n" + "="*60)
print("CONCEPT 8: Logging in functions and classes")
print("="*60)

# Module-level logger — the standard pattern
module_logger = logging.getLogger(__name__)

class OrderService:
    """
    Production-style class with logging at each decision point.

    Key patterns:
      - Module-level logger (not instance-level) — shared across all instances
      - Log method entry at DEBUG (visible in dev, hidden in prod)
      - Log decisions at INFO
      - Log warnings at WARNING
      - Log failures at ERROR with exc_info=True
      - Never log passwords, card numbers, tokens
    """

    def __init__(self, service_name: str):
        self.service_name = service_name
        # Instance-specific logger for better filtering
        self.logger = logging.getLogger(f"{__name__}.{service_name}")

    def process_order(self, order_id: int, amount: float, user_id: str) -> dict:
        # Log entry point at DEBUG — verbose, only useful in dev
        self.logger.debug(
            "process_order called: order_id=%s, amount=%.2f, user_id=%s",
            order_id, amount, user_id
        )

        if amount <= 0:
            self.logger.warning(
                "Invalid amount %.2f for order %s — rejecting", amount, order_id
            )
            return {"status": "rejected", "reason": "invalid_amount"}

        if amount > 10000:
            self.logger.warning(
                "Large transaction flagged: order=%s, amount=%.2f, user=%s",
                order_id, amount, user_id
            )

        try:
            # Simulate payment processing
            if amount == 999:
                raise ConnectionError("Payment gateway timeout")
            result = {"order_id": order_id, "charged": amount, "status": "ok"}
            self.logger.info(
                "Order %s processed successfully: charged=%.2f", order_id, amount
            )
            return result

        except ConnectionError:
            self.logger.error(
                "Payment gateway failure for order %s", order_id, exc_info=True
            )
            return {"status": "failed", "reason": "gateway_error"}


# Set up a visible logger for the demo
service_logger = logging.getLogger(__name__)
service_logger.setLevel(logging.DEBUG)
service_logger.propagate = False
sh = logging.StreamHandler(sys.stdout)
sh.setFormatter(logging.Formatter("  %(levelname)-8s | %(name)s | %(message)s"))
service_logger.addHandler(sh)

# Also add to child loggers
for child_name in ["__main__.payment", "__main__.OrderService"]:
    cl = logging.getLogger(child_name)
    cl.propagate = True

svc = OrderService("payment")
# The OrderService uses its own logger — attach a handler via parent propagation
svc.logger.propagate = True
svc.logger.parent = service_logger

print("  Processing orders:")
svc.process_order(1001, 49.99, "alice")
svc.process_order(1002, -10.00, "bob")
svc.process_order(1003, 15000.00, "charlie")
svc.process_order(1004, 999, "dave")    # triggers gateway error


# ==============================================================================
# CONCEPT 9: RotatingFileHandler — preventing disk full
# ==============================================================================
print("\n" + "="*60)
print("CONCEPT 9: RotatingFileHandler")
print("="*60)

"""
If you write logs to a plain file, eventually it fills the disk.
RotatingFileHandler creates a new file when the current one hits maxBytes.
It keeps backupCount old files:
  app.log        ← current (newest)
  app.log.1      ← previous
  app.log.2      ← older
  app.log.3      ← oldest (backupCount=3)
  (app.log.4 deleted when log.3 would rotate)

TimedRotatingFileHandler rotates by time instead (daily, hourly, etc.)
Use when you want "one file per day" for log shipping pipelines.
"""

tmp_dir = Path(tempfile.mkdtemp())
rotating_log = tmp_dir / "app.log"

rotating_logger = logging.getLogger("rotating_demo")
rotating_logger.setLevel(logging.DEBUG)
rotating_logger.propagate = False

# maxBytes=200 → rotate every 200 bytes (tiny, for demonstration)
rot_handler = logging.handlers.RotatingFileHandler(
    filename=str(rotating_log),
    maxBytes=200,          # 200 bytes = rotate very quickly for demo
    backupCount=3,         # keep app.log, app.log.1, app.log.2, app.log.3
    encoding="utf-8",
)
rot_handler.setFormatter(logging.Formatter("%(asctime)s %(levelname)s %(message)s"))
rotating_logger.addHandler(rot_handler)

# Write enough to trigger rotation
for i in range(20):
    rotating_logger.info("Log entry number %03d — padding to trigger rotation", i)

# Show the rotated files
log_files = sorted(tmp_dir.glob("app.log*"))
print(f"  Rotated log files ({len(log_files)} total):")
for lf in log_files:
    size = lf.stat().st_size
    print(f"    {lf.name:15s} {size:5d} bytes")

# TimedRotatingFileHandler — shown as config only (would rotate at actual midnight)
print(f"\n  TimedRotatingFileHandler config (daily rotation example):")
print(f"    when='midnight', interval=1, backupCount=30")
print(f"    → creates app.log.2025-01-15, app.log.2025-01-14, ...")
print(f"    → keeps 30 days of history (30 MB if 1MB/day)")

import shutil
shutil.rmtree(tmp_dir)


# ==============================================================================
# CONCEPT 10: Logger hierarchy and propagation
# ==============================================================================
print("\n" + "="*60)
print("CONCEPT 10: Logger hierarchy and propagation")
print("="*60)

"""
Logger hierarchy is based on dotted names:
  root ("")
    └── "myapp"
          ├── "myapp.models"
          ├── "myapp.services"
          │     └── "myapp.services.payment"
          └── "myapp.api"

By default, propagate=True: a log record travels UP through
all ancestors until it hits a handler.

This means:
  - Set up ONE handler on "myapp" → all child loggers use it automatically
  - Silence a noisy child: getLogger("myapp.services.payment").setLevel(WARNING)
  - Silence a third-party library: getLogger("urllib3").setLevel(WARNING)

For library code:
  ALWAYS add NullHandler() to your library's top-level logger.
  This prevents "No handlers could be found" warnings when users don't configure logging.
  Let the APPLICATION decide where library logs go.
"""

# Show propagation visually
prop_logger = logging.getLogger("propagation_demo")
prop_logger.setLevel(logging.DEBUG)
prop_logger.propagate = False

prop_handler = logging.StreamHandler(sys.stdout)
prop_handler.setFormatter(
    logging.Formatter("  %(levelname)-8s [%(name)s] %(message)s")
)
prop_logger.addHandler(prop_handler)

child1 = logging.getLogger("propagation_demo.models")
child2 = logging.getLogger("propagation_demo.services.payment")
# No handlers on child1 or child2 — they propagate up to prop_logger

print("  All child loggers propagate to parent's handler:")
child1.info("From models logger → travels to propagation_demo handler")
child2.warning("From services.payment → also travels up")

# Stop propagation
child2.propagate = False
child2.addHandler(prop_handler)
print("\n  After child2.propagate = False:")
child2.error("From services.payment — handled locally, STOPS here")

# NullHandler for library code
lib_logger = logging.getLogger("my_library")
lib_logger.addHandler(logging.NullHandler())
lib_logger.info("Library log — goes nowhere until user configures it")
print(f"\n  NullHandler: library log silently discarded (no output above)")


# ==============================================================================
# CONCEPT 11: % formatting vs f-strings in log calls
# ==============================================================================
print("\n" + "="*60)
print("CONCEPT 11: % formatting vs f-strings in logging")
print("="*60)

"""
Critical performance difference:

  # BAD — f-string evaluated IMMEDIATELY, even if level is disabled
  logger.debug(f"User data: {expensive_computation()}")
  # expensive_computation() runs even when DEBUG is off!

  # GOOD — % formatting is DEFERRED until the record is actually emitted
  logger.debug("User data: %s", expensive_computation())
  # expensive_computation() only runs if DEBUG is enabled

This is why you see % style in all professional logging code.
"""

perf_logger = logging.getLogger("perf_demo")
perf_logger.setLevel(logging.WARNING)  # DEBUG is OFF
perf_logger.propagate = False
perf_logger.addHandler(logging.StreamHandler(sys.stdout))

call_count = {"n": 0}

def expensive_debug_data():
    """Simulates expensive computation."""
    call_count["n"] += 1
    return f"debug payload (call #{call_count['n']})"

# % style — deferred: the function is NOT called when level is below threshold
perf_logger.debug("Data: %s", expensive_debug_data())
print(f"  After % debug call with level=WARNING: call_count={call_count['n']}")
# call_count is 0 because debug() saw level=WARNING and short-circuited

# isEnabledFor() — explicit check before expensive computation
if perf_logger.isEnabledFor(logging.DEBUG):
    data = expensive_debug_data()    # only runs if DEBUG is on
    perf_logger.debug("Expensive data: %s", data)
print(f"  After isEnabledFor() check: call_count={call_count['n']} (still 0)")

# Show what happens with INFO (which IS above WARNING — wait, let me check):
perf_logger.setLevel(logging.DEBUG)  # enable DEBUG now
perf_logger.debug("Now DEBUG is on: %s", expensive_debug_data())
print(f"  After enabling DEBUG: call_count={call_count['n']} (function called)")


# ==============================================================================
# CONCEPT 12: Assertions — development-time sanity checks
# ==============================================================================
print("\n" + "="*60)
print("CONCEPT 12: Assertions")
print("="*60)

"""
Assertions are fast sanity checks that document assumptions.
They raise AssertionError when the condition is False.

Key rules:
  1. Use assertions to catch programmer errors (bugs in YOUR code)
  2. NEVER use assertions for input validation from users or external systems
     — 'python3 -O script.py' runs with optimizations that DISABLE assertions!
  3. Use assertions freely in tests

  assert condition, "message if condition is False"
"""

def calculate_discount(price: float, pct: float) -> float:
    """
    Assertions document invariants that should ALWAYS be true.
    If they fire, it's a bug in the calling code, not user input.
    """
    assert price >= 0, f"Price must be non-negative, got {price}"
    assert 0 <= pct <= 100, f"Percentage must be 0-100, got {pct}"
    discount = price * (pct / 100)
    result = price - discount
    assert result >= 0, f"Discounted price went negative: {result}"  # should be impossible
    return result

# Happy path
print(f"  calculate_discount(100, 20) = {calculate_discount(100, 20)}")
print(f"  calculate_discount(50, 0)   = {calculate_discount(50, 0)}")

# Assertion failure — programmer error
try:
    calculate_discount(100, 150)   # 150% discount — bug in calling code
except AssertionError as e:
    print(f"  AssertionError caught: {e}")

# Assert as documentation of invariants
def binary_search(arr: list, target) -> int:
    """Assert that preconditions are met — documents the contract."""
    assert arr == sorted(arr), "binary_search requires a sorted array"
    low, high = 0, len(arr) - 1
    while low <= high:
        mid = (low + high) // 2
        if arr[mid] == target:
            return mid
        elif arr[mid] < target:
            low = mid + 1
        else:
            high = mid - 1
    return -1

print(f"\n  binary_search([1,3,5,7,9], 5) = {binary_search([1,3,5,7,9], 5)}")
print(f"  binary_search([1,3,5,7,9], 4) = {binary_search([1,3,5,7,9], 4)}")

try:
    binary_search([3, 1, 5], 5)   # unsorted — assertion catches the bug
except AssertionError as e:
    print(f"  AssertionError (unsorted array): {e}")


# ==============================================================================
# CONCEPT 13: pdb — the Python debugger (shown as commented examples)
# ==============================================================================
print("\n" + "="*60)
print("CONCEPT 13: pdb — Python debugger patterns")
print("="*60)

"""
pdb is Python's built-in interactive debugger.
Since this script runs non-interactively, we show the patterns as comments.

--- HOW TO USE ---

# Drop a breakpoint anywhere (Python 3.7+):
breakpoint()          # pauses execution, opens (Pdb) prompt

# Old syntax:
import pdb
pdb.set_trace()       # same as breakpoint()

--- KEY COMMANDS at (Pdb) prompt ---

n (next)     → execute current line, step OVER function calls
s (step)     → execute current line, step INTO function calls
c (continue) → run until next breakpoint or end
r (return)   → run until current function returns
q (quit)     → exit debugger

p  expr      → print value:     p order.total
pp expr      → pretty print:    pp user.__dict__
l            → show current source context (±11 lines)
ll           → show full function source
w            → show full call stack (where)
u / d        → move up/down the call stack

b 42         → set breakpoint at line 42
b func_name  → set breakpoint at function entry
b 42, x > 5 → conditional breakpoint (only when x > 5)
cl 1         → clear breakpoint 1

! x = 99    → execute arbitrary Python: change a variable
a            → show arguments of current function

--- POST-MORTEM DEBUGGING ---
After an exception, inspect the crash context:

  import pdb, traceback, sys
  try:
      problematic_code()
  except Exception:
      traceback.print_exc()
      pdb.post_mortem()    # drops into debugger at the crash frame

--- EXAMPLE SESSION ---

  def calculate_tax(price, rate):
      breakpoint()
      tax = price * rate
      total = price + tax
      return total

  calculate_tax(499.0, 0.09)
  # (Pdb) p price
  # 499.0
  # (Pdb) p rate
  # 0.09
  # (Pdb) n
  # (Pdb) p tax
  # 44.91
  # (Pdb) c
  # 543.91

--- VS CODE / PYCHARM ---
Both IDEs have GUI debuggers that wrap pdb.
Set breakpoints by clicking the gutter, then use F5 to start debugging.
"""

# We CAN demonstrate programmatic pdb usage in non-interactive mode
import pdb

def buggy_function(items):
    """Function with a deliberate bug for tracing."""
    total = 0
    for item in items:
        # Bug: should check if item is a number
        total += item
    return total

# Instead of breakpoint(), we show traceback capture which IS runnable
try:
    buggy_function([1, 2, "three", 4])   # will raise TypeError
except TypeError:
    tb_string = traceback.format_exc()
    print("  Traceback captured programmatically:")
    # Show just the last few lines (most relevant part)
    lines = tb_string.strip().split("\n")
    for line in lines[-4:]:
        print(f"    {line}")

print("\n  pdb commands reference:")
commands = [
    ("n",  "next — step over"),
    ("s",  "step — step into"),
    ("c",  "continue — run to next breakpoint"),
    ("p expr", "print expression"),
    ("pp expr", "pretty-print"),
    ("l",  "list source context"),
    ("w",  "where — show call stack"),
    ("b N", "breakpoint at line N"),
    ("q",  "quit debugger"),
]
for cmd, desc in commands:
    print(f"    (Pdb) {cmd:12s}→ {desc}")


# ==============================================================================
# CONCEPT 14: traceback module — programmatic traceback capture
# ==============================================================================
print("\n" + "="*60)
print("CONCEPT 14: traceback module")
print("="*60)

"""
The traceback module lets you work with exception tracebacks programmatically.
Useful for:
  - Logging the full traceback as a string
  - Sending tracebacks to error monitoring services (Sentry, Datadog)
  - Displaying abbreviated tracebacks in custom error pages
"""

def level3():
    return 1 / 0

def level2():
    return level3()

def level1():
    return level2()

# Capture traceback as string (for logging/storage)
try:
    level1()
except ZeroDivisionError:
    # format_exc() returns the traceback as a string
    tb_str = traceback.format_exc()
    print(f"  traceback.format_exc():")
    for line in tb_str.strip().split("\n"):
        print(f"    {line}")

    # format_tb() — just the traceback frames (without exception type/message)
    try:
        level1()
    except ZeroDivisionError:
        tb_frames = traceback.format_tb(sys.exc_info()[2])
        print(f"\n  traceback.format_tb() — just frames ({len(tb_frames)} frames)")
        print(f"  Last frame: {tb_frames[-1].strip()!r}")

    # print_exc() — print directly to stderr (or a file)
    print("\n  traceback.print_exc() to stdout:")
    try:
        level1()
    except ZeroDivisionError:
        traceback.print_exc(file=sys.stdout)   # normally goes to stderr


# ==============================================================================
# CONCEPT 15: warnings module — non-fatal alerts
# ==============================================================================
print("\n" + "="*60)
print("CONCEPT 15: warnings module")
print("="*60)

"""
Exceptions stop execution. warnings don't — they just alert.

Use warnings for:
  - Deprecated functions (DeprecationWarning)
  - Suspicious but legal inputs (UserWarning)
  - Future behavior changes (FutureWarning)

Warning categories:
  UserWarning        — general purpose
  DeprecationWarning — API is deprecated (hidden in prod by default!)
  FutureWarning      — behavior will change
  RuntimeWarning     — suspicious runtime behavior
  ResourceWarning    — resource usage issue (file not closed)
"""

def old_function(x: int) -> int:
    """
    stacklevel=2 makes the warning point to the CALLER's line,
    not to this function. Without it, every warning looks like
    it comes from line N of this file — useless.
    """
    warnings.warn(
        "old_function() is deprecated. Use new_function() instead.",
        DeprecationWarning,
        stacklevel=2    # ← points warning to the caller
    )
    return new_function(x)

def new_function(x: int) -> int:
    return x * 2

# DeprecationWarning is hidden by default in production
# Enable it to see it:
warnings.filterwarnings("always", category=DeprecationWarning)
print("  Calling deprecated function:")
result = old_function(21)
print(f"  Result: {result}")

# UserWarning — visible by default
def process_negative(value: float) -> float:
    if value < 0:
        warnings.warn(
            f"Negative value {value} passed to process_negative() — result may be unexpected",
            UserWarning,
            stacklevel=2
        )
    return abs(value) * 2

print("\n  Processing negative value:")
result = process_negative(-5.0)
print(f"  Result: {result}")

# Treat warnings as errors (great for CI/CD — catches deprecations before they bite)
print("\n  Treating warnings as errors (CI/CD pattern):")
warnings.filterwarnings("error", category=DeprecationWarning)
try:
    old_function(5)
except DeprecationWarning as e:
    print(f"  DeprecationWarning became an exception: {e}")

# Reset to default
warnings.filterwarnings("default")


# ==============================================================================
# CONCEPT 16: Production logging setup — putting it all together
# ==============================================================================
print("\n" + "="*60)
print("CONCEPT 16: Production logging setup")
print("="*60)

"""
Production logging setup:
  1. Named loggers with __name__ — one per module
  2. Formatter with timestamp, level, logger name, line number
  3. Console handler for INFO+ (operators reading in real time)
  4. Rotating file handler for DEBUG+ (detailed post-mortem)
  5. Separate error log for ERROR+ (alert routing)
  6. Root logger at WARNING (silences noisy third-party libraries)
  7. Never use basicConfig in library code — only in application entry point
"""

def create_production_logger(name: str, log_dir: Path) -> logging.Logger:
    """
    Creates a logger with three handlers:
      1. Console: INFO+ with human-readable format
      2. File: DEBUG+ with full format (for troubleshooting)
      3. Error file: ERROR+ only (for alerting)
    """
    logger = logging.getLogger(name)
    logger.setLevel(logging.DEBUG)
    logger.propagate = False

    production_fmt = logging.Formatter(
        "%(asctime)s | %(levelname)-8s | %(name)s:%(lineno)d | %(message)s",
        datefmt="%Y-%m-%d %H:%M:%S"
    )

    # Console: INFO+
    console = logging.StreamHandler(sys.stdout)
    console.setLevel(logging.INFO)
    console.setFormatter(production_fmt)

    # Debug file: DEBUG+ (would be RotatingFileHandler in production)
    debug_file = logging.handlers.RotatingFileHandler(
        str(log_dir / f"{name}.log"),
        maxBytes=10 * 1024 * 1024,   # 10MB
        backupCount=5,
        encoding="utf-8",
    )
    debug_file.setLevel(logging.DEBUG)
    debug_file.setFormatter(production_fmt)

    # Error file: ERROR+ only
    error_file = logging.handlers.RotatingFileHandler(
        str(log_dir / f"{name}.error.log"),
        maxBytes=10 * 1024 * 1024,
        backupCount=3,
        encoding="utf-8",
    )
    error_file.setLevel(logging.ERROR)
    error_file.setFormatter(production_fmt)

    logger.addHandler(console)
    logger.addHandler(debug_file)
    logger.addHandler(error_file)

    return logger


# Demonstrate the production setup
tmp_logs = Path(tempfile.mkdtemp())
prod_logger = create_production_logger("payment_service", tmp_logs)

print(f"  Production logger writing to {tmp_logs}")
prod_logger.debug("DB connection pool initialized (size=10)")   # file only
prod_logger.info("Payment service started on port 8080")        # console + file
prod_logger.warning("Stripe API response time: 2.8s")           # console + file
prod_logger.error("Order #9001 payment failed: gateway timeout") # ALL 3 handlers

# Show file contents
print("\n  Debug log (all levels):")
debug_log = tmp_logs / "payment_service.log"
if debug_log.exists():
    for line in debug_log.read_text().strip().split("\n"):
        print(f"    {line}")

print("\n  Error log (ERROR+ only):")
error_log = tmp_logs / "payment_service.error.log"
if error_log.exists():
    for line in error_log.read_text().strip().split("\n"):
        print(f"    {line}")

shutil.rmtree(tmp_logs)


# ==============================================================================
# CONCEPT 17: Common debugging patterns
# ==============================================================================
print("\n" + "="*60)
print("CONCEPT 17: Common debugging patterns")
print("="*60)

"""
Professional debugging workflow:
  1. READ the traceback — bottom to top (last line = the actual error)
  2. FORM a hypothesis — what could cause this specific error?
  3. REPRODUCE in isolation — smallest possible test case
  4. VERIFY with targeted logging or breakpoint
  5. FIX the root cause (not the symptom)
  6. VERIFY the fix doesn't break other things
  7. ADD a test to prevent regression
  8. ADD better logging so next incident is faster

Common patterns:
"""

# Pattern 1: Add debug logging around the suspect code
debug_logger = logging.getLogger("debug_patterns")
debug_logger.setLevel(logging.DEBUG)
debug_logger.propagate = False
debug_logger.addHandler(logging.StreamHandler(sys.stdout))
debug_logger.handlers[-1].setFormatter(
    logging.Formatter("  DBG | %(message)s")
)

def calculate_total(items: list) -> float:
    """
    Instead of print statements, use DEBUG logging.
    These are invisible in production (level=INFO) but
    visible in dev (level=DEBUG) without any code changes.
    """
    debug_logger.debug("calculate_total called with %d items", len(items))
    total = 0.0
    for i, item in enumerate(items):
        debug_logger.debug("item[%d]: name=%s price=%s qty=%s",
                           i, item.get("name"), item.get("price"), item.get("qty"))
        price = float(item.get("price", 0))
        qty   = int(item.get("qty", 0))
        subtotal = price * qty
        debug_logger.debug("  subtotal = %.2f * %d = %.2f", price, qty, subtotal)
        total += subtotal
    debug_logger.debug("Total: %.2f", total)
    return total

cart = [
    {"name": "Laptop", "price": "999.99", "qty": "1"},
    {"name": "Mouse",  "price": "29.99",  "qty": "2"},
    {"name": "Bag",    "price": "49.99",  "qty": "1"},
]
total = calculate_total(cart)
print(f"\n  Cart total: ${total:.2f}")

# Pattern 2: Timing with logging
import time

def timed_operation(label: str):
    """Decorator-free timing using a context manager pattern."""
    class Timer:
        def __enter__(self):
            self.start = time.perf_counter()
            return self
        def __exit__(self, *args):
            elapsed = time.perf_counter() - self.start
            debug_logger.info("TIMING | %s: %.4fs", label, elapsed)
    return Timer()

print("\n  Timing a computation:")
with timed_operation("sum of squares"):
    result = sum(i*i for i in range(100_000))
print(f"  Result: {result:,}")

# Pattern 3: Type checking during debugging
def safe_divide(a, b):
    """
    During debugging, log the types when you're getting TypeError.
    In production, this debug line costs nothing (level=INFO).
    """
    debug_logger.debug(
        "safe_divide(%s: %s, %s: %s)", a, type(a).__name__, b, type(b).__name__
    )
    try:
        return a / b
    except TypeError as e:
        debug_logger.error("Type error in safe_divide: %s / %s — %s", a, b, e)
        raise

print("\n  safe_divide(10, 3) =", safe_divide(10, 3))
try:
    safe_divide("10", 3)    # deliberate TypeError
except TypeError:
    pass


print("\n" + "="*60)
print("MODULE 09 — All concepts demonstrated.")
print("="*60)
