# 🧾 09 — Logging & Debugging
## From print() to Production Observability

> *"Your code runs perfectly in development. It crashes at 3 AM in production.*
> *Logs are the only witness. How well did you log?"*

---

## 🎬 The Story

3:17 AM. PagerDuty fires. Orders are failing.
Ten thousand customers can't check out. Every minute costs money.

The engineer opens the server. No logs. Just:

```
Exception in thread: <unknown error>
```

They restart. It happens again. They restart again. Same.

Six hours later, a senior engineer finds a 3-line log entry buried in stdout
that says the connection pool was exhausted — something that proper logging
would have surfaced in 30 seconds.

**This is why logging exists. This is why you do it properly.**

---

## 💡 Chapter 1 — print() vs logging: The Real Difference

```python
# What a beginner does:
print(f"Processing order {order_id}")
print(f"Error: {e}")

# What it looks like in production at 3 AM:
# Processing order 4892
# Error: Connection refused
# ... 50,000 more lines mixed with everything else
```

```
PRINT vs LOGGING COMPARISON:
┌─────────────────────┬──────────────────────────────────────────────────┐
│  print()            │  logging                                         │
├─────────────────────┼──────────────────────────────────────────────────┤
│  Always outputs     │  Controlled by level (DEBUG off in production)   │
│  No timestamp       │  Timestamp built-in                              │
│  No severity        │  5 severity levels (DEBUG → CRITICAL)            │
│  Stdout only        │  Console, file, HTTP, email, syslog, anything    │
│  No context         │  Module, function, line number, process/thread ID│
│  Not filterable     │  Filter by level, module, custom rules           │
│  Not searchable     │  Structured JSON → searchable in Elasticsearch   │
│  Development only   │  Production-grade, industry standard             │
└─────────────────────┴──────────────────────────────────────────────────┘
```

---

## 📊 Chapter 2 — Log Levels: The Severity Scale

```
LEVEL      NUMERIC   WHEN TO USE
────────────────────────────────────────────────────────────────────────
DEBUG      10        Detailed diagnostic info. Development only.
                     "Entering function calculate_tax with amount=499.00"
                     "Cache miss for key user:42"

INFO       20        Normal operation milestones. Always-on in production.
                     "User alice@mail.com logged in"
                     "Order #4892 placed successfully"
                     "Server started on port 8080"

WARNING    30        Something unexpected but system still works.
                     "Retry 2/3 for API call to Stripe"
                     "Config value missing, using default"
                     "Response time 3.2s — above 2s threshold"

ERROR      40        An operation failed. Needs investigation.
                     "Payment processing failed for order #4892"
                     "Database connection lost"
                     "Failed to send email to user"

CRITICAL   50        System cannot function. Wake someone up NOW.
                     "Cannot connect to database — service shutting down"
                     "Disk full — unable to write logs"
                     "Security breach detected"
```

```python
import logging

# The default level is WARNING — DEBUG and INFO are hidden by default!
logging.debug("This won't show")    # hidden (below WARNING)
logging.info("This won't show")     # hidden
logging.warning("This shows")       # WARNING:root:This shows
logging.error("This shows")         # ERROR:root:This shows
logging.critical("This shows")      # CRITICAL:root:This shows
```

---

## 🏗️ Chapter 3 — The Architecture: Logger → Handler → Formatter

Python's logging is built on three components working together:

```
YOUR CODE
    │
    ▼
┌─────────────────┐
│   LOGGER         │  ← You create and use this. Decides IF to log.
│  (myapp.models) │    Has a name, a level, a list of handlers.
└────────┬────────┘
         │  (if level passes)
         ▼
┌─────────────────┐
│   HANDLER        │  ← Decides WHERE the log goes.
│  (StreamHandler) │    Multiple handlers possible on one logger.
│  (FileHandler)   │
│  (RotatingFile)  │
└────────┬────────┘
         │  (formats the record)
         ▼
┌─────────────────┐
│   FORMATTER      │  ← Decides WHAT the log looks like.
│  "%(asctime)s   │    Timestamp, level, module, line number, message.
│   %(message)s"  │
└─────────────────┘
         │
         ▼
    OUTPUT (console / file / Elasticsearch / Slack / ...)
```

---

## 🔧 Chapter 4 — From Quick Setup to Production Config

### The Quick Way: `basicConfig()`

```python
import logging

# Minimal — just enable INFO to console:
logging.basicConfig(level=logging.INFO)
logging.info("Server started")    # INFO:root:Server started

# More control — file + format:
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s | %(levelname)-8s | %(name)s:%(lineno)d | %(message)s",
    datefmt="%Y-%m-%d %H:%M:%S",
    filename="app.log",        # write to file (omit for console)
    filemode="a",              # append (default 'a')
    encoding="utf-8",
)

# ⚠️ basicConfig only works ONCE — the first call wins.
# If basicConfig was already called (e.g. by a library), this does nothing.
# For reliable configuration, use getLogger() directly.
```

### The Professional Way: Named Loggers

```python
import logging

# Create a named logger — always use __name__ for automatic hierarchy:
logger = logging.getLogger(__name__)
# In myapp/services/payment.py, this creates: "myapp.services.payment"

# Use it exactly like the root logger:
logger.debug("Processing payment for order %s", order_id)
logger.info("Payment successful: %s", payment_id)
logger.warning("Retrying payment (attempt %d/3)", attempt)
logger.error("Payment failed: %s", error_message)
logger.critical("Payment service down: %s", str(e))
```

### Full Manual Setup (Production Standard)

```python
import logging
import logging.handlers
import sys


def setup_logging(app_name: str, level: str = "INFO") -> logging.Logger:
    """Set up application logging with console + rotating file."""

    logger = logging.getLogger(app_name)
    logger.setLevel(getattr(logging, level.upper()))

    # ── Formatter ────────────────────────────────────────────────────
    fmt = logging.Formatter(
        fmt="%(asctime)s | %(levelname)-8s | %(name)s:%(lineno)d | %(message)s",
        datefmt="%Y-%m-%d %H:%M:%S",
    )

    # ── Console handler (INFO and above) ─────────────────────────────
    console = logging.StreamHandler(sys.stdout)
    console.setLevel(logging.INFO)
    console.setFormatter(fmt)

    # ── Rotating file handler (DEBUG and above) ───────────────────────
    file_handler = logging.handlers.RotatingFileHandler(
        filename=f"{app_name}.log",
        maxBytes=10 * 1024 * 1024,   # 10 MB per file
        backupCount=5,                # keep 5 backup files: app.log.1 ... app.log.5
        encoding="utf-8",
    )
    file_handler.setLevel(logging.DEBUG)
    file_handler.setFormatter(fmt)

    # ── Error-only file ───────────────────────────────────────────────
    error_handler = logging.handlers.RotatingFileHandler(
        filename=f"{app_name}.error.log",
        maxBytes=10 * 1024 * 1024,
        backupCount=3,
        encoding="utf-8",
    )
    error_handler.setLevel(logging.ERROR)
    error_handler.setFormatter(fmt)

    logger.addHandler(console)
    logger.addHandler(file_handler)
    logger.addHandler(error_handler)

    return logger


# Usage:
logger = setup_logging("myapp", level="DEBUG")
logger.info("Application started")
```

---

## 🎨 Chapter 5 — Format Fields Reference

```python
# All available format codes:
FORMAT = (
    "%(asctime)s"        # 2025-03-08 14:30:00,123  (human timestamp)
    " %(created)f"       # 1741440600.123456  (Unix timestamp float)
    " %(levelname)s"     # DEBUG / INFO / WARNING / ERROR / CRITICAL
    " %(levelno)d"       # 10 / 20 / 30 / 40 / 50
    " %(name)s"          # logger name (e.g. "myapp.services.payment")
    " %(module)s"        # module name (e.g. "payment")
    " %(filename)s"      # filename (e.g. "payment.py")
    " %(pathname)s"      # full path to source file
    " %(funcName)s"      # function name
    " %(lineno)d"        # line number
    " %(process)d"       # process ID
    " %(processName)s"   # process name
    " %(thread)d"        # thread ID
    " %(threadName)s"    # thread name
    " %(message)s"       # the actual log message
)

# Common production format:
PRODUCTION_FORMAT = "%(asctime)s | %(levelname)-8s | %(name)s:%(lineno)d | %(message)s"
# 2025-03-08 14:30:00 | ERROR    | myapp.services.payment:47 | Payment failed

# JSON format (see structured logging chapter):
JSON_FORMAT = '{"time":"%(asctime)s","level":"%(levelname)s","logger":"%(name)s","line":%(lineno)d,"msg":"%(message)s"}'
```

---

## 🔄 Chapter 6 — Log Rotation: Preventing Disk Full

```python
from logging.handlers import RotatingFileHandler, TimedRotatingFileHandler


# ── RotatingFileHandler — rotate by SIZE ─────────────────────────────
# Creates: app.log, app.log.1, app.log.2, app.log.3 (oldest overwritten)
handler = RotatingFileHandler(
    "app.log",
    maxBytes=10 * 1024 * 1024,   # 10MB per file
    backupCount=5,               # keep 5 backup files (50MB total)
    encoding="utf-8",
)


# ── TimedRotatingFileHandler — rotate by TIME ──────────────────────────
# Creates: app.log.2025-03-08, app.log.2025-03-07, etc.
handler = TimedRotatingFileHandler(
    "app.log",
    when="midnight",     # rotate: 'midnight', 'h' (hourly), 'D' (daily), 'W0'-'W6' (weekly)
    interval=1,          # every 1 midnight
    backupCount=30,      # keep 30 days of logs
    encoding="utf-8",
    utc=True,            # use UTC timestamps for rotation
)


# ── Production recommendation ──────────────────────────────────────────
# Combine both: TimedRotating for daily rotation + external log shipper
# (Fluentd/Filebeat) to send to Elasticsearch/CloudWatch.
# Don't rely only on local file rotation in distributed systems.
```

---

## 🧠 Chapter 7 — The Logger Hierarchy: Parent-Child Propagation

```
ROOT LOGGER ("")
    │
    ├── "myapp"                ← getLogger("myapp")
    │     │
    │     ├── "myapp.models"   ← getLogger("myapp.models")
    │     ├── "myapp.services" ← getLogger("myapp.services")
    │     │         │
    │     │         └── "myapp.services.payment"
    │     └── "myapp.api"
    │
    └── "requests"             ← from the requests library
    └── "sqlalchemy"           ← from SQLAlchemy
```

```python
import logging

# Create hierarchy:
root    = logging.getLogger()                   # root logger
myapp   = logging.getLogger("myapp")
payment = logging.getLogger("myapp.services.payment")

# PROPAGATION: by default, child loggers send records to PARENT handlers too.
# So a log from "myapp.services.payment" goes to:
#   → myapp.services.payment handlers
#   → myapp.services handlers (if exists)
#   → myapp handlers
#   → root logger handlers

# Disable propagation:
payment.propagate = False   # stops at payment's own handlers

# This is how libraries work:
# They use getLogger(__name__) and add NullHandler:
logging.getLogger("mylib").addHandler(logging.NullHandler())
# Ensures library logs go nowhere unless the user explicitly configures them.
```

---

## 📋 Chapter 8 — Exception Logging: The Right Way

```python
import logging
logger = logging.getLogger(__name__)


# ── logging.exception() — USE THIS inside except blocks ──────────────
try:
    process_payment(order_id)
except Exception:
    logger.exception("Payment processing failed for order %s", order_id)
    # Logs: ERROR level + the MESSAGE + the full TRACEBACK automatically
    # Equivalent to: logger.error("...", exc_info=True)


# ── logging.error() with exc_info ─────────────────────────────────────
try:
    fetch_user(user_id)
except ValueError as e:
    logger.error("Invalid user data for id=%s: %s", user_id, e, exc_info=True)


# ── Log, then re-raise ────────────────────────────────────────────────
try:
    send_email(user.email, subject, body)
except SMTPException:
    logger.exception("Failed to send email to %s", user.email)
    raise   # ← let the caller decide what to do


# ── Log with extra context ─────────────────────────────────────────────
try:
    charge_card(card_token, amount)
except PaymentError as e:
    logger.error(
        "Card charge failed",
        extra={                    # ← extra fields included in log record
            "order_id": order_id,
            "amount": amount,
            "error_code": e.code,
        }
    )


# ❌ NEVER:
try:
    risky()
except Exception as e:
    print(f"Error: {e}")    # no traceback, no level, no context
    pass                    # ← SILENT SWALLOW — worst possible thing
```

---

## 🗂️ Chapter 9 — Structured Logging (JSON)

Plain-text logs are hard to search. JSON logs are machine-readable.

```python
# ── Manual JSON formatter ──────────────────────────────────────────────
import json
import logging
from datetime import datetime, timezone


class JSONFormatter(logging.Formatter):
    def format(self, record: logging.LogRecord) -> str:
        log_entry = {
            "timestamp": datetime.now(timezone.utc).isoformat(),
            "level":     record.levelname,
            "logger":    record.name,
            "module":    record.module,
            "function":  record.funcName,
            "line":      record.lineno,
            "message":   record.getMessage(),
        }

        # Include exception info if present:
        if record.exc_info:
            log_entry["exception"] = self.formatException(record.exc_info)

        # Include any extra= fields:
        for key, value in record.__dict__.items():
            if key not in {
                "name","msg","args","levelname","levelno","pathname","filename",
                "module","exc_info","exc_text","stack_info","lineno","funcName",
                "created","msecs","relativeCreated","thread","threadName",
                "processName","process","message","asctime",
            }:
                log_entry[key] = value

        return json.dumps(log_entry, default=str)


# Usage:
handler = logging.StreamHandler()
handler.setFormatter(JSONFormatter())

logger = logging.getLogger("myapp")
logger.addHandler(handler)
logger.setLevel(logging.DEBUG)


# ── structlog — the best library for structured logging ───────────────
# pip install structlog
import structlog

structlog.configure(
    processors=[
        structlog.processors.TimeStamper(fmt="iso"),
        structlog.processors.add_log_level,
        structlog.processors.StackInfoRenderer(),
        structlog.processors.format_exc_info,
        structlog.processors.JSONRenderer(),
    ]
)

log = structlog.get_logger()
log.info("payment_processed", order_id=4892, amount=499.00, currency="USD")
# → {"timestamp": "2025-03-08T14:30:00Z", "level": "info", "event": "payment_processed",
#    "order_id": 4892, "amount": 499.0, "currency": "USD"}
```

---

## 🔗 Chapter 10 — Correlation IDs: Tracing Requests

When a user's request touches 5 microservices, how do you trace it across all logs?

```python
import logging
import uuid
from contextvars import ContextVar


# ── Using contextvars (Python 3.7+) — thread and async safe ───────────
correlation_id: ContextVar[str] = ContextVar("correlation_id", default="")


class CorrelationFilter(logging.Filter):
    """Adds correlation_id to every log record."""

    def filter(self, record: logging.LogRecord) -> bool:
        record.correlation_id = correlation_id.get() or "no-id"
        return True


# Setup:
handler = logging.StreamHandler()
handler.addFilter(CorrelationFilter())
handler.setFormatter(logging.Formatter(
    "%(asctime)s | %(levelname)s | [%(correlation_id)s] | %(name)s | %(message)s"
))

logger = logging.getLogger("myapp")
logger.addHandler(handler)


# Middleware sets correlation_id at request entry:
def request_middleware(request, next_handler):
    # Get from header (if forwarded from upstream) or generate new one:
    cid = request.headers.get("X-Correlation-ID") or str(uuid.uuid4())
    token = correlation_id.set(cid)    # set for this async context
    try:
        response = next_handler(request)
        response.headers["X-Correlation-ID"] = cid
        return response
    finally:
        correlation_id.reset(token)    # clean up


# Now every log in this request has the same correlation_id:
# 2025-03-08 14:30:00 | INFO    | [f47ac10b-58cc-4372-a567-0e02b2c3d479] | myapp.api    | Request received
# 2025-03-08 14:30:00 | INFO    | [f47ac10b-58cc-4372-a567-0e02b2c3d479] | myapp.service| Processing order
# 2025-03-08 14:30:01 | ERROR   | [f47ac10b-58cc-4372-a567-0e02b2c3d479] | myapp.payment| Payment failed
```

---

## ⚡ Chapter 11 — Performance: Logging Without Slowing Down

```python
import logging
logger = logging.getLogger(__name__)


# ── ❌ BAD: string formatting always happens, even if level is disabled:
logger.debug("Processing items: " + str(large_list))    # expensive even if DEBUG is off
logger.debug(f"User data: {user.__dict__}")              # same problem


# ── ✅ GOOD: % formatting — Python defers it until needed:
logger.debug("Processing items: %s", large_list)         # format only if DEBUG enabled
logger.debug("User data: %s", user.__dict__)


# ── ✅ BETTER: isEnabledFor() check before expensive computation:
if logger.isEnabledFor(logging.DEBUG):
    debug_data = compute_expensive_debug_info()
    logger.debug("Debug data: %s", debug_data)


# ── Why % style is preferred over f-strings in logging:
# f"text {var}"   → evaluated IMMEDIATELY regardless of level
# "text %s" % var → evaluated only IF the record is actually emitted
# → ALWAYS use % style in logger.XXX() calls


# ── Disable logging entirely for performance (e.g. benchmarks):
logging.disable(logging.CRITICAL)   # disables all levels ≤ CRITICAL
logging.disable(logging.NOTSET)     # re-enable all levels
```

---

## 🔒 Chapter 12 — Security: What Never Goes in Logs

```python
# ❌ NEVER LOG:
logger.info("User %s logged in with password: %s", username, password)
logger.debug("JWT token: %s", token)
logger.info("Card processed: %s %s", card_number, cvv)
logger.debug("API key: %s", api_key)
logger.info("User DOB: %s, SSN: %s", date_of_birth, ssn)


# ✅ Log identifiers, not secrets:
logger.info("User %s authenticated successfully", user_id)      # ID, not email
logger.info("Payment processed for order %s", order_id)         # reference, not card
logger.debug("API call made, key ends in ...%s", api_key[-4:])  # last 4 only


# ── Redaction filter ──────────────────────────────────────────────────
import re

class SensitiveDataFilter(logging.Filter):
    PATTERNS = [
        (re.compile(r'\b\d{16}\b'), "****-****-****-****"),         # credit card
        (re.compile(r'password["\s:=]+\S+', re.I), "password=***"),  # passwords
        (re.compile(r'token["\s:=]+\S+', re.I), "token=***"),        # tokens
    ]

    def filter(self, record: logging.LogRecord) -> bool:
        if isinstance(record.msg, str):
            for pattern, replacement in self.PATTERNS:
                record.msg = pattern.sub(replacement, record.msg)
        return True
```

---

## 🔧 Chapter 13 — dictConfig: Configuration as Data

For production systems, configure logging from a dict (or JSON/YAML file):

```python
import logging.config

LOGGING_CONFIG = {
    "version": 1,
    "disable_existing_loggers": False,    # ← don't silence third-party libraries

    "formatters": {
        "standard": {
            "format": "%(asctime)s | %(levelname)-8s | %(name)s:%(lineno)d | %(message)s",
            "datefmt": "%Y-%m-%d %H:%M:%S",
        },
        "json": {
            "()": "myapp.logging.JSONFormatter",   # custom formatter class
        },
    },

    "handlers": {
        "console": {
            "class": "logging.StreamHandler",
            "level": "INFO",
            "formatter": "standard",
            "stream": "ext://sys.stdout",
        },
        "file": {
            "class": "logging.handlers.RotatingFileHandler",
            "level": "DEBUG",
            "formatter": "json",
            "filename": "app.log",
            "maxBytes": 10_485_760,   # 10MB
            "backupCount": 5,
            "encoding": "utf-8",
        },
        "error_file": {
            "class": "logging.handlers.RotatingFileHandler",
            "level": "ERROR",
            "formatter": "json",
            "filename": "app.error.log",
            "maxBytes": 10_485_760,
            "backupCount": 3,
            "encoding": "utf-8",
        },
    },

    "loggers": {
        "myapp": {
            "level": "DEBUG",
            "handlers": ["console", "file", "error_file"],
            "propagate": False,
        },
        "sqlalchemy.engine": {
            "level": "WARNING",    # silence SQLAlchemy's verbose SQL logging
            "handlers": ["file"],
            "propagate": False,
        },
    },

    "root": {
        "level": "WARNING",
        "handlers": ["console"],
    },
}

logging.config.dictConfig(LOGGING_CONFIG)
```

---

## 🐛 Chapter 14 — Debugging: The Mindset

```
AMATEUR DEBUGGING:
  1. Add print everywhere
  2. Restart
  3. Guess
  4. Change random things
  5. Give up and rewrite

PROFESSIONAL DEBUGGING:
  1. READ the traceback carefully (bottom → top)
  2. FORM a hypothesis about the root cause
  3. REPRODUCE the issue in isolation
  4. VERIFY your hypothesis with targeted logging/breakpoints
  5. FIX the root cause (not the symptom)
  6. VERIFY the fix didn't break anything else
  7. ADD a test to prevent regression
  8. ADD better logging so next incident is faster to diagnose
```

---

## 🐞 Chapter 15 — pdb: Python's Built-in Debugger

```python
# ── Drop-in breakpoint (Python 3.7+) ────────────────────────────────
breakpoint()   # pauses execution and opens interactive debugger here

# ── Old way ──────────────────────────────────────────────────────────
import pdb
pdb.set_trace()   # same as breakpoint()

# ── Post-mortem (debug after crash) ──────────────────────────────────
import pdb, traceback, sys

try:
    problematic_code()
except Exception:
    traceback.print_exc()
    pdb.post_mortem()    # drop into debugger at the crash point
```

### pdb Command Reference

```
NAVIGATION:
  n  (next)      → execute current line, step OVER function calls
  s  (step)      → execute current line, step INTO function calls
  c  (continue)  → run until next breakpoint or end
  r  (return)    → run until function returns
  q  (quit)      → exit debugger

INSPECTION:
  p  <expr>      → print expression value:    p user.email
  pp <expr>      → pretty-print:              pp user.__dict__
  l  (list)      → show current code context (±11 lines)
  l  1,20        → show lines 1-20
  ll (longlist)  → show full function source
  w  (where)     → show full call stack / traceback
  u  (up)        → move up one frame in call stack
  d  (down)      → move down one frame in call stack
  a  (args)      → show arguments of current function
  !  <stmt>      → execute arbitrary Python statement: ! x = 42

BREAKPOINTS:
  b              → list all breakpoints
  b  <line>      → set breakpoint at line:    b 42
  b  func        → set breakpoint at function: b payment.process
  b  file:line   → set breakpoint in file:    b payment.py:23
  b  cond        → conditional breakpoint:    b 42, amount > 1000
  cl <n>         → clear breakpoint n
  disable <n>    → disable breakpoint n
  enable <n>     → enable breakpoint n
  ignore <n> <c> → skip next c hits of breakpoint n
  commands <n>   → run commands when breakpoint n is hit

EXECUTION:
  run / restart  → restart the program
  j  <line>      → jump to line (skip code)
```

```python
# ── Real debugging session example ────────────────────────────────────
def calculate_tax(price, rate):
    breakpoint()          # ← drops you into pdb here
    tax = price * rate    # (Pdb) n
    total = price + tax   # (Pdb) p price   → 499.0
    return total          # (Pdb) p tax     → 44.91
                          # (Pdb) p total   → 543.91

calculate_tax(499.0, 0.09)
```

---

## 🔬 Chapter 16 — Advanced Debugging Techniques

### Logging as Debugging (Better Than print)

```python
import logging
logger = logging.getLogger(__name__)

# Instead of:
print(f"DEBUG: user = {user}")
print(f"DEBUG: amount = {amount}")

# Do this:
logger.debug("Processing payment: user_id=%s, amount=%.2f, currency=%s",
             user.id, amount, currency)
# Can be turned on/off with log level. Shows in structured logs. Has context.
```

### `traceback` Module for Custom Error Reporting

```python
import traceback

try:
    risky()
except Exception:
    # Get traceback as string:
    tb_str = traceback.format_exc()
    logger.error("Unexpected error:\n%s", tb_str)

    # Get just the last frame:
    lines = traceback.format_tb(sys.exc_info()[2])
    logger.error("Failed at: %s", lines[-1].strip())

    # Print full traceback to stderr:
    traceback.print_exc()
```

### `warnings` Module

```python
import warnings

# Issue a deprecation warning:
warnings.warn(
    "old_function() is deprecated, use new_function() instead",
    DeprecationWarning,
    stacklevel=2    # ← points to the caller's code, not this function
)

# Treat warnings as errors (useful in tests):
warnings.filterwarnings("error")

# Silence specific warnings:
warnings.filterwarnings("ignore", category=DeprecationWarning, module="third_party")
```

### `faulthandler`: Debugging Segfaults and Deadlocks

```python
import faulthandler

# Enable on startup — prints traceback even on SIGSEGV (segfault):
faulthandler.enable()

# Dump traceback after a timeout (detect deadlocks):
import signal
faulthandler.dump_traceback_later(timeout=30, repeat=True)
# If your program hangs for 30s, dumps all thread stacks to stderr
```

### Memory Profiling

```python
# pip install memory-profiler
from memory_profiler import profile

@profile
def load_data():
    data = [i for i in range(1_000_000)]
    return data

# Shows line-by-line memory usage:
# Line #  Mem usage    Increment   Occurrences   Line Contents
# 5      50.1 MiB    50.1 MiB     1   def load_data():
# 6     127.5 MiB    77.4 MiB     1       data = [i for i in range(1_000_000)]

# pip install objgraph  — find memory leaks
import objgraph
objgraph.show_most_common_types(limit=10)   # which objects are taking memory?
objgraph.show_growth()                      # what grew since last call?
```

---

## 🎯 Key Takeaways

```
LOGGING:
• Use logging, never print() in production
• Named loggers with __name__ — automatic hierarchy and filtering
• 5 levels: DEBUG(dev) → INFO(normal) → WARNING(unexpected) → ERROR(failed) → CRITICAL(down)
• Logger → Handler → Formatter: three-layer architecture
• RotatingFileHandler prevents disk-full disasters
• logger.exception() inside except = ERROR + full traceback automatically
• Use % formatting in log calls, NOT f-strings (deferred evaluation)
• isEnabledFor() before expensive debug computations
• Structured/JSON logs = searchable in Elasticsearch/Splunk/CloudWatch
• Correlation IDs = trace a request across microservices
• dictConfig = configure logging from data, not code
• NEVER log passwords, tokens, card numbers, PII
• propagate=False = stop logger from sending records to parent handlers
• NullHandler in library code = user decides where logs go

DEBUGGING:
• Read traceback bottom-to-top — last line is where error actually happened
• breakpoint() = drop into pdb at any point
• pdb n/s/c/p/b = navigate, step into, continue, print, breakpoint
• Post-mortem debugging = pdb.post_mortem() after crash
• faulthandler.enable() = traceback even on segfault/deadlock
• memory_profiler / objgraph = find memory leaks
• Systematic approach: reproduce → isolate → hypothesis → verify → fix → test
```

---

## 🔁 Navigation

| | |
|---|---|
| ⬅️ Previous | [08 — File Handling](../08_file_handling/theory.md) |
| 📖 Interview | [interview.md](./interview.md) |
| ⚡ Cheatsheet | [cheatsheet.md](./cheatsheet.md) |
| 🐛 PDB Guide | [pdb_guide.md](./pdb_guide.md) |
| ➡️ Next | [10 — Decorators](../10_decorators/theory.md) |

---

**[🏠 Back to README](../README.md)**

**Prev:** [← File Handling — Interview Q&A](../08_file_handling/interview.md) &nbsp;|&nbsp; **Next:** [Cheat Sheet →](./cheatsheet.md)

**Related Topics:** [Cheat Sheet](./cheatsheet.md) · [PDB Debugging Guide](./pdb_guide.md) · [Interview Q&A](./interview.md)
