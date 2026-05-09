<a id="top"></a>
# 🧾 09 — Logging & Debugging

> *"Your code runs perfectly in development. It crashes at 3 AM in production.*
> *Logs are the only witness. How well did you log?"*

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

## 📖 Table of Contents

- [📌 Learning Priority](#learning-priority)
- [1. print() vs logging: The Real Difference](#1-print-vs-logging-the-real-difference)
- [2. Log Levels: The Severity Scale](#2-log-levels-the-severity-scale)
- [3. The Architecture: Logger → Handler → Formatter](#3-the-architecture-logger--handler--formatter)
- [4. From Quick Setup to Production Config](#4-from-quick-setup-to-production-config)
  - [The Quick Way: basicConfig()](#the-quick-way-basicconfig)
  - [The Professional Way: Named Loggers](#the-professional-way-named-loggers)
  - [Full Manual Setup (Production Standard)](#full-manual-setup-production-standard)
- [5. Format Fields Reference](#5-format-fields-reference)
- [6. Log Rotation: Preventing Disk Full](#6-log-rotation-preventing-disk-full)
- [7. The Logger Hierarchy: Parent-Child Propagation](#7-the-logger-hierarchy-parent-child-propagation)
- [8. Exception Logging: The Right Way](#8-exception-logging-the-right-way)
- [9. Structured Logging (JSON)](#9-structured-logging-json)
- [10. Correlation IDs: Tracing Requests](#10-correlation-ids-tracing-requests)
- [11. Performance: Logging Without Slowing Down](#11-performance-logging-without-slowing-down)
- [12. Security: What Never Goes in Logs](#12-security-what-never-goes-in-logs)
- [13. dictConfig: Configuration as Data](#13-dictconfig-configuration-as-data)
- [14. Debugging: The Mindset](#14-debugging-the-mindset)
- [15. pdb: Python's Built-in Debugger](#15-pdb-pythons-built-in-debugger)
  - [pdb Command Reference](#pdb-command-reference)
- [16. Advanced Debugging Techniques](#16-advanced-debugging-techniques)
  - [Logging as Debugging (Better Than print)](#logging-as-debugging-better-than-print)
  - [traceback Module for Custom Error Reporting](#traceback-module-for-custom-error-reporting)
  - [warnings Module](#warnings-module)
  - [faulthandler: Debugging Segfaults and Deadlocks](#faulthandler-debugging-segfaults-and-deadlocks)
  - [Memory Profiling](#memory-profiling)
- [Key Takeaways](#key-takeaways)

<a id="learning-priority"></a>
## 📌 Learning Priority

**Must Learn** — Core concept, daily use, interview essential:
`logging.getLogger()` · Log levels (DEBUG/INFO/WARNING/ERROR/CRITICAL) · Handlers (StreamHandler, FileHandler) · Formatters · `pdb` basics (`n`, `s`, `c`, `p`, `b`)

**Should Learn** — Important for real projects, comes up regularly:
`logging.config.dictConfig()` · RotatingFileHandler · Logger hierarchy · `logging.exception()` · `breakpoint()` (Python 3.7+)

**Good to Know** — Useful in specific situations:
`logging.captureWarnings()` · `QueueHandler` + `QueueListener` · `sys.settrace()`

**Reference** — Know it exists, look up when needed:
`SMTPHandler` · `SysLogHandler` · `logging.setLoggerClass()` · `pdb` custom commands

<a id="1-print-vs-logging-the-real-difference"></a>
# 1. print() vs logging: The Real Difference

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

💡 **Hint:** The single biggest difference isn't features — it's control. `logging` lets you turn DEBUG messages off in production with one line, and turn them back on during an incident without redeploying.

📝 **Practice:** [print vs logging / replace print with logging →](./practice.md#q1--ch1--replace-print-with-logging)

> [↑ Back to Top](#top)

<a id="2-log-levels-the-severity-scale"></a>
# 2. Log Levels: The Severity Scale

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

⚠️ **Common mistake — wrong level choice:** Logging everything at `ERROR` makes real errors invisible in the noise. Logging nothing at `INFO` means you have no audit trail of what your system actually did. Choose levels that reflect the real severity — `INFO` for business events, `WARNING` for recoverable anomalies, `ERROR` only for genuine failures.

💡 **Hint:** A useful production split: `DEBUG` to file (all detail), `INFO` to console (normal flow), `ERROR` to a separate error log (only failures). Section 4 shows how to set this up.

📝 **Practice:** [log levels / set level and filter messages →](./practice.md#q2--ch2--set-level-and-filter-messages)

> [↑ Back to Top](#top)

<a id="3-the-architecture-logger--handler--formatter"></a>
# 3. The Architecture: Logger → Handler → Formatter

Think of the logging system like a newsroom. The **Logger** is the reporter — it decides whether a story is worth covering (is this message important enough given my level?). The **Handler** is the editor who decides where the story goes — front page (console), archive (file), breaking news alert (email/Slack). The **Formatter** is the copy editor who decides how the story is written — just the headline, or full article with timestamp, byline, and page number.

When you call `logger.error("Payment failed")`, the logger checks: "Is this error above my threshold?" If yes, it creates a `LogRecord` object containing the message, level, module name, line number, timestamp, and more. It hands this record to each of its attached handlers. Each handler checks its own level threshold, then passes the record to its formatter, which turns it into the final string and sends it to the output destination.

This three-layer separation is what makes logging powerful: you can have one logger, write to five different outputs simultaneously, each with a different format and level filter — all without changing a single line of your application code.

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

🔍 **Good to know:** A `Logger` with no handlers attached sends records to its parent logger (propagation). The root logger (`logging.getLogger()`) always exists and is the ultimate fallback. This is why `logging.basicConfig()` works even without creating a named logger — it configures the root logger.

📝 **Practice:** [logger architecture / attach StreamHandler + FileHandler →](./practice.md#q3--ch3--attach-streamhandler--filehandler)

> [↑ Back to Top](#top)

<a id="4-from-quick-setup-to-production-config"></a>
# 4. From Quick Setup to Production Config

There are three levels of logging setup. Quick setup is fine for scripts. Named loggers are the minimum for any importable module. Full manual setup is what production applications use.

<a id="the-quick-way-basicconfig"></a>
## The Quick Way: basicConfig()

`basicConfig()` configures the root logger in one call. It's the fastest way to get logging working in a script or quick prototype — but it only configures the root logger, and it only takes effect once (the first call wins).

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

⚠️ **Common mistake — basicConfig ignored:** If any library you import calls `logging.basicConfig()` or attaches a handler to the root logger before your code does, your `basicConfig()` call silently does nothing. Use `dictConfig` (section 13) or named loggers for reliable production setup.

<a id="the-professional-way-named-loggers"></a>
## The Professional Way: Named Loggers

Instead of using the root logger, create a named logger per module using `__name__`. This gives every logger in your app a unique identity that reflects its location in the package tree — which means you can control log levels and outputs per module.

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

💡 **Hint:** `getLogger(__name__)` is the single most important logging pattern to memorize. It automatically creates a hierarchy (`myapp` → `myapp.services` → `myapp.services.payment`) that you can control from a single config without touching any module's code.

<a id="full-manual-setup-production-standard"></a>
## Full Manual Setup (Production Standard)

For production applications, configure loggers, handlers, and formatters explicitly. This gives you full control: different levels for console vs file, separate error-only logs, multiple outputs with different formats.

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

📝 **Practice:** [logging setup / build a custom formatter →](./practice.md#q4--ch4--build-a-custom-formatter)

> [↑ Back to Top](#top)

<a id="5-format-fields-reference"></a>
# 5. Format Fields Reference

Every log record carries a rich set of metadata fields that your formatter can include. Beyond the message itself, you get the exact file, function, and line that logged it — invaluable when debugging production issues at 3 AM.

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

💡 **Hint:** `%(levelname)-8s` left-aligns the level name in an 8-character field — this keeps all log lines aligned in the console, making them much easier to scan visually.

📝 **Practice:** [format fields / add filename and lineno to format →](./practice.md#q6--ch5--add-filename-and-lineno-to-format)

> [↑ Back to Top](#top)

<a id="6-log-rotation-preventing-disk-full"></a>
# 6. Log Rotation: Preventing Disk Full

Without rotation, a log file on a busy server can grow to hundreds of gigabytes. Log rotation automatically creates a new file when the current one reaches a size or age limit, and deletes the oldest backups to stay within a disk budget.

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

⚠️ **Common mistake — no rotation in production:** A service writing 100MB/day fills a 10GB disk in 100 days with no warning. Always set `maxBytes` and `backupCount` from day one — adding rotation after a disk-full incident means you're already in a crisis.

🔍 **Good to know:** `backupCount=5` with `maxBytes=10MB` caps total log storage at ~50MB. Adjust to your traffic: `backupCount=30` with `TimedRotatingFileHandler` keeps exactly 30 days of history regardless of volume.

📝 **Practice:** [log rotation / RotatingFileHandler →](./practice.md#q7--ch6--rotatingfilehandler)

> [↑ Back to Top](#top)

<a id="7-the-logger-hierarchy-parent-child-propagation"></a>
# 7. The Logger Hierarchy: Parent-Child Propagation

Python's logging system forms a tree. Every logger named `"myapp.services.payment"` is automatically a child of `"myapp.services"`, which is a child of `"myapp"`, which is a child of the root logger. You don't create this tree — it exists the moment you call `getLogger(__name__)` in each module.

The key behavior is **propagation**: when a child logger emits a record, it passes it up to every ancestor in the tree (unless you stop it with `propagate = False`). This means you can configure handlers on `"myapp"` once and every child logger in your whole application writes to them automatically.

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

⚠️ **Common mistake — duplicate log output:** You add a handler to `"myapp"` and also add one to `"myapp.services.payment"`. Every record from payment now appears twice — once from its own handler, once propagated to `myapp`'s handler. Set `propagate = False` on child loggers that have their own handlers.

💡 **Hint:** The `NullHandler` pattern for library code is important. If your library adds a `StreamHandler` to its logger, it will print to the user's console whether they want it or not. Always use `NullHandler` in library code and let the user decide.

📝 **Practice:** [logger hierarchy / propagation control →](./practice.md#q8--ch7--logger-hierarchy-and-propagation)

> [↑ Back to Top](#top)

<a id="8-exception-logging-the-right-way"></a>
# 8. Exception Logging: The Right Way

When an exception occurs, you need two things in your logs: the error message AND the full traceback. Without the traceback, you know something failed but not where or why. `logger.exception()` gives you both automatically — it's the one method you should always reach for inside an `except` block.

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

⚠️ **Common mistake — silent swallow:** `except Exception: pass` is the most destructive logging antipattern. Your code continues running with corrupted state, future errors become inexplicable, and the original failure is completely invisible. At minimum, always `logger.exception(...)`.

💡 **Hint:** `logger.exception()` only works inside an `except` block — it reads the current exception from the interpreter state. If you call it outside an `except` block, it logs `None` for the traceback.

📝 **Practice:** [exception logging / logging.exception inside except →](./practice.md#q10--ch8--loggingexception-inside-except)

> [↑ Back to Top](#top)

<a id="9-structured-logging-json"></a>
# 9. Structured Logging (JSON)

Plain-text logs are hard to search. When you have millions of log lines across dozens of servers, grepping for a keyword is unreliable and slow. JSON logs are machine-readable — each field is a key-value pair that log aggregators (Elasticsearch, Splunk, CloudWatch) can index and query instantly. The difference: `grep "payment_failed"` vs `SELECT * WHERE event="payment_failed" AND amount > 1000 AND user_country="DE"`.

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

💡 **Hint:** For greenfield projects, reach for `structlog` over a custom `JSONFormatter` — it handles processor pipelines, context binding, and async logging with much less boilerplate.

🔍 **Good to know:** `default=str` in `json.dumps()` prevents `TypeError` when log fields contain non-serializable types like `datetime`, `UUID`, or `Decimal` — it falls back to calling `str()` on them.

📝 **Practice:** [structured logging / JSON formatter →](./practice.md#q12--ch9--json-formatter)

> [↑ Back to Top](#top)

---

<a id="10-correlation-ids-tracing-requests"></a>
# 10. Correlation IDs: Tracing Requests

In a microservice world, a single user action triggers calls across five services. A payment fails. You have logs from all five services — but which lines belong to *that* request? Without correlation IDs, you're hunting a specific fish in five different oceans.

A **correlation ID** is a unique identifier (usually a UUID) generated at the edge (API gateway or the first service that receives the request) and forwarded in every downstream call. Every log line from every service stamps it. Now you can filter across five log streams with a single ID and see exactly what happened.

```python
import logging
import uuid
from contextvars import ContextVar

# ContextVar is thread-safe and asyncio-safe — each request gets its own value
request_id_var: ContextVar[str] = ContextVar("request_id", default="no-request-id")


class RequestIdFilter(logging.Filter):
    """Injects the current request ID into every log record."""

    def filter(self, record: logging.LogRecord) -> bool:
        record.request_id = request_id_var.get()
        return True


# Setup — add the filter to your handler
handler = logging.StreamHandler()
handler.addFilter(RequestIdFilter())

formatter = logging.Formatter(
    "%(asctime)s %(levelname)s [%(request_id)s] %(name)s: %(message)s"
)
handler.setFormatter(formatter)

logger = logging.getLogger("app")
logger.addHandler(handler)
logger.setLevel(logging.DEBUG)


# At request entry point (FastAPI middleware, Flask before_request, etc.):
def process_request(request_id: str = None):
    rid = request_id or str(uuid.uuid4())
    token = request_id_var.set(rid)  # ← sets the value for this async context

    try:
        logger.info("Request started")
        # ... all downstream calls inherit the same request_id
        logger.info("Request completed")
    finally:
        request_id_var.reset(token)  # ← restore previous value after request
```

```python
# FastAPI middleware example
from fastapi import Request
import uuid

@app.middleware("http")
async def add_correlation_id(request: Request, call_next):
    # Honor incoming ID (from upstream service) or generate a new one
    rid = request.headers.get("X-Correlation-ID") or str(uuid.uuid4())
    token = request_id_var.set(rid)
    try:
        response = await call_next(request)
        response.headers["X-Correlation-ID"] = rid  # propagate downstream
        return response
    finally:
        request_id_var.reset(token)
```

⚠️ **Common mistake — using `threading.local` instead of `ContextVar`:** `threading.local` breaks under asyncio because multiple coroutines share the same thread. `ContextVar` is the correct primitive for async-safe per-request state.

💡 **Hint:** Always echo the correlation ID back in the HTTP response header (`X-Correlation-ID`). That way clients can include it in bug reports, and your support team can pull the exact trace in seconds.

📝 **Practice:** [correlation ID / ContextVar filter →](./practice.md#q13--ch10--correlation-id)

> [↑ Back to Top](#top)

---

<a id="11-performance-logging-without-slowing-down"></a>
# 11. Performance: Logging Without Slowing Down

Logging has a cost. A high-traffic service logging at DEBUG level to a synchronous file handler on every request can shave 20–30% off throughput. These patterns let you keep rich logs without paying that price.

**The three layers of performance:**
1. **String formatting cost** — evaluated even if the message is never emitted
2. **Handler I/O cost** — synchronous writes block your thread
3. **Log level check cost** — nearly free, but the guard pattern makes it explicit

```python
import logging

logger = logging.getLogger(__name__)

# ── BAD: f-string evaluated even if DEBUG is disabled ──────────────────────
logger.debug(f"Processing {len(items)} items: {items}")  # ← always formats

# ── GOOD: % formatting — deferred, only formats if message will be emitted ─
logger.debug("Processing %d items: %s", len(items), items)  # ← lazy format

# ── ALSO GOOD: explicit guard for expensive computations ──────────────────
if logger.isEnabledFor(logging.DEBUG):
    # Only runs when DEBUG is actually enabled
    expensive_repr = compute_debug_info(items)
    logger.debug("Debug info: %s", expensive_repr)
```

```python
import logging
import logging.handlers
import queue

# ── Async logging with QueueHandler + QueueListener ────────────────────────
# Your handler writes to a queue (non-blocking).
# A background thread reads the queue and does the actual I/O.

log_queue = queue.Queue(maxsize=10_000)

# Real handlers — these do the actual I/O (run in background thread)
file_handler = logging.handlers.RotatingFileHandler("app.log", maxBytes=10_000_000)
stream_handler = logging.StreamHandler()

# Listener runs in a daemon thread — reads from queue, dispatches to real handlers
listener = logging.handlers.QueueListener(
    log_queue, file_handler, stream_handler, respect_handler_level=True
)
listener.start()

# QueueHandler — non-blocking, just puts message on the queue
queue_handler = logging.handlers.QueueHandler(log_queue)

root = logging.getLogger()
root.addHandler(queue_handler)
root.setLevel(logging.DEBUG)

# At shutdown:
listener.stop()
```

⚠️ **Common mistake — f-strings in log calls:** `logger.debug(f"value: {x}")` always evaluates the f-string, even when DEBUG is disabled. Use `%s` style or `isEnabledFor()` guard for anything expensive.

🔍 **Good to know:** `QueueHandler` + `QueueListener` is the production pattern for high-throughput services. The web thread never blocks on I/O — it just enqueues and moves on. This is built into the stdlib from Python 3.2+.

📝 **Practice:** [lazy log formatting / async queue handler →](./practice.md#q14--ch11--logging-performance)

> [↑ Back to Top](#top)

---

<a id="12-security-what-never-goes-in-logs"></a>
# 12. Security: What Never Goes in Logs

Logs are often stored in plain text, shipped to third-party aggregators (Datadog, Splunk, ELK), and retained for months. A single accidental log of a password or credit card number can constitute a data breach — and in GDPR/CCPA jurisdictions, a reportable incident.

**Never log these:**
- Passwords, API keys, tokens, secrets of any kind
- Credit card numbers, CVVs
- Social Security Numbers / national IDs
- Raw JWT payloads (they contain claims — sometimes sensitive)
- Full stack traces to end users (they reveal internal paths and library versions)
- PII in production without explicit masking

```python
import logging
import re


class SensitiveDataFilter(logging.Filter):
    """
    Scrubs sensitive patterns from log messages before they are emitted.
    Applied as a filter on the handler so it catches all records.
    """

    PATTERNS = [
        (re.compile(r"password['\"]?\s*[:=]\s*['\"]?[\w@#$%^&*!]+", re.IGNORECASE), "password=***"),
        (re.compile(r"\b(?:\d[ -]?){13,16}\b"), "****-****-****-****"),  # credit cards
        (re.compile(r"\b\d{3}-\d{2}-\d{4}\b"), "***-**-****"),            # SSN
        (re.compile(r"Bearer\s+[\w\-\.]+"), "Bearer ***"),                 # JWT tokens
        (re.compile(r"api[_-]?key['\"]?\s*[:=]\s*['\"]?[\w\-]+", re.IGNORECASE), "api_key=***"),
    ]

    def filter(self, record: logging.LogRecord) -> bool:
        message = record.getMessage()
        for pattern, replacement in self.PATTERNS:
            message = pattern.sub(replacement, message)
        record.msg = message
        record.args = ()  # ← clear args so getMessage() uses the already-formatted string
        return True


# Apply to handler, not logger — catches everything going to that handler
handler = logging.StreamHandler()
handler.addFilter(SensitiveDataFilter())
```

```python
# Safe user logging pattern
def log_user_action(user_id: str, action: str, metadata: dict):
    # Log only the ID, never the full user object (which may contain email, phone, etc.)
    safe_meta = {
        k: v for k, v in metadata.items()
        if k not in {"password", "token", "ssn", "card_number", "email"}
    }
    logger.info("User action", extra={"user_id": user_id, "action": action, **safe_meta})
```

⚠️ **Common mistake — logging the full request body:** `logger.debug("Request: %s", request.json())` can dump passwords and tokens straight to your log aggregator. Always extract and log only the fields you explicitly need.

💡 **Hint:** Apply `SensitiveDataFilter` at the handler level (not the logger level) so it catches log records regardless of which logger emitted them.

📝 **Practice:** [sensitive data filter / log scrubbing →](./practice.md#q15--ch12--security-filter)

> [↑ Back to Top](#top)

---

<a id="13-dictconfig-configuration-as-data"></a>
# 13. dictConfig: Configuration as Data

Hard-coding `addHandler()` and `setFormatter()` calls scattered across `__init__` files is brittle — change a handler and you're hunting through five files. `dictConfig` centralises your entire logging setup in one Python dict (or a YAML/JSON file), making it auditable, version-controllable, and environment-switchable with a single variable change.

```python
import logging.config

LOGGING_CONFIG = {
    "version": 1,
    "disable_existing_loggers": False,   # ← keep third-party loggers alive

    "formatters": {
        "standard": {
            "format": "%(asctime)s %(levelname)-8s [%(name)s] %(message)s",
            "datefmt": "%Y-%m-%d %H:%M:%S",
        },
        "json": {
            "()": "pythonjsonlogger.jsonlogger.JsonFormatter",  # pip install python-json-logger
            "fmt": "%(asctime)s %(levelname)s %(name)s %(message)s",
        },
    },

    "filters": {
        "request_id": {
            "()": "myapp.logging_filters.RequestIdFilter",  # ← custom filter class
        },
    },

    "handlers": {
        "console": {
            "class": "logging.StreamHandler",
            "level": "DEBUG",
            "formatter": "standard",
            "stream": "ext://sys.stdout",
            "filters": ["request_id"],
        },
        "file": {
            "class": "logging.handlers.RotatingFileHandler",
            "level": "INFO",
            "formatter": "json",
            "filename": "logs/app.log",
            "maxBytes": 10_485_760,  # 10 MB
            "backupCount": 5,
            "encoding": "utf-8",
        },
        "error_file": {
            "class": "logging.handlers.RotatingFileHandler",
            "level": "ERROR",
            "formatter": "json",
            "filename": "logs/errors.log",
            "maxBytes": 10_485_760,
            "backupCount": 10,
        },
    },

    "loggers": {
        "myapp": {
            "level": "DEBUG",
            "handlers": ["console", "file", "error_file"],
            "propagate": False,    # ← don't bubble up to root logger
        },
        "sqlalchemy.engine": {
            "level": "WARNING",   # ← silence noisy third-party logger
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

```python
# Switch config per environment without changing code
import os
import logging.config
import yaml  # pip install pyyaml

env = os.getenv("APP_ENV", "development")
with open(f"config/logging_{env}.yaml") as f:
    logging.config.dictConfig(yaml.safe_load(f))
```

⚠️ **Common mistake — `disable_existing_loggers: True`:** This is the default if you omit the key. It silences any logger created before `dictConfig()` runs — including third-party libraries. Always set it to `False` explicitly.

💡 **Hint:** Put your `LOGGING_CONFIG` dict in a dedicated `config/logging.py` file. Import and call `dictConfig()` once at app startup (e.g., in `__init__.py` or `main.py`). Never call it twice.

📝 **Practice:** [dictConfig setup / multi-handler config →](./practice.md#q16--ch13--dictconfig)

> [↑ Back to Top](#top)

---

<a id="14-debugging-the-mindset"></a>
# 14. Debugging: The Mindset

Debugging is not "stare at the code until you see the bug." It is a systematic investigation with a hypothesis, an experiment, and evidence. The engineers who debug fastest are not the ones who know the most — they are the ones who resist guessing.

**The professional debugging loop:**

```
1. REPRODUCE — make the bug happen reliably before touching any code
2. ISOLATE — narrow the failing surface: which function? which input? which line?
3. HYPOTHESIZE — form a specific, falsifiable theory: "I think X is None here"
4. VERIFY — prove or disprove with evidence (logs, pdb, assertions) — not by changing code
5. FIX — change only what the evidence says is wrong
6. CONFIRM — reproduce the original trigger: does it pass now?
7. EXPLAIN — could you write a one-paragraph post-mortem? If not, you don't fully understand it
```

```python
# Amateur debugging (guessing)
def process_payment(order):
    # Hmm, maybe it's this?
    order["amount"] = float(order.get("amount", 0))  # ← added "just in case"
    # Maybe this?
    if not order:
        return None
    result = charge_card(order)
    return result

# Professional debugging (evidence-first)
def process_payment(order):
    logger.debug("process_payment called: order_id=%s, amount=%s, type=%s",
                 order.get("id"), order.get("amount"), type(order.get("amount")))
    result = charge_card(order)
    logger.debug("charge_card returned: %s", result)
    return result
# → logs reveal: amount is a string "49.99" not float 49.99
# → fix: type coercion at the INPUT boundary, not buried inside the function
```

```python
# Rubber duck debugging — explain it step by step
# Often the act of explaining reveals the assumption that was wrong

# Bisect debugging — binary search through the call stack
# If 10 functions could be responsible, add a log in the middle
# If that log fires correctly, bug is in the second half
# Repeat until isolated to one function
```

💡 **Hint:** The most common cause of "it works locally but fails in production" is an environmental difference: different Python version, missing env var, different database state, or a dependency version mismatch. Check environment before assuming code is broken.

🔍 **Good to know:** When a bug is reported without reproducible steps, your first job is to *make it reproducible* — not to fix it. A fix without a reproduction path is a guess.

📝 **Practice:** [debugging methodology / isolating a bug →](./practice.md#q17--ch14--debugging-mindset)

> [↑ Back to Top](#top)

---

<a id="15-pdb-pythons-built-in-debugger"></a>
# 15. pdb: Python's Built-in Debugger

`print()` debugging is a one-way street: you add a print, run the program, read the output, and repeat. `pdb` is interactive: you pause execution at any line, inspect variables, step through code, modify values live, and resume — without restarting.

Think of `pdb` as a time machine. You can pause time in your program, look around at the exact state, move forward one step at a time, and even jump to any point in the call stack to see how you got here.

```python
# ── Three ways to drop into pdb ────────────────────────────────────────────

# 1. breakpoint() — Python 3.7+, preferred (respects PYTHONBREAKPOINT env var)
def process_order(order):
    breakpoint()   # ← execution pauses here, drops you into interactive pdb
    return charge_card(order)

# 2. Programmatic — older style, still works everywhere
import pdb
def process_order(order):
    pdb.set_trace()
    return charge_card(order)

# 3. Post-mortem — inspect state AFTER an exception, without modifying code
try:
    result = risky_function()
except Exception:
    import pdb, traceback
    traceback.print_exc()
    pdb.post_mortem()   # ← drops into pdb at the frame where the exception occurred
```

```python
# ── Running a script under pdb from the start ──────────────────────────────
# $ python -m pdb myscript.py
# Stops at the first line, lets you set breakpoints before running

# ── Conditional breakpoints (programmatic) ─────────────────────────────────
def process_items(items):
    for i, item in enumerate(items):
        if item["status"] == "error":
            breakpoint()   # only stops when you actually have an error item
        process(item)
```

⚠️ **Common mistake — leaving `breakpoint()` in committed code:** A `breakpoint()` in production will hang your process waiting for keyboard input that never comes. Use pre-commit hooks or `grep -r 'breakpoint\|pdb.set_trace'` in CI to catch these.

💡 **Hint:** Set `PYTHONBREAKPOINT=0` in production to make all `breakpoint()` calls no-ops — a safety net in case one slips through.

---

<a id="pdb-command-reference"></a>
## pdb Command Reference

| Command | Short | What it does |
|---------|-------|-------------|
| `next` | `n` | Execute current line, step OVER function calls |
| `step` | `s` | Execute current line, step INTO function calls |
| `continue` | `c` | Resume execution until next breakpoint |
| `quit` | `q` | Exit pdb (raises BdbQuit) |
| `list` | `l` | Show source code around current line |
| `longlist` | `ll` | Show full source of current function |
| `print expr` | `p expr` | Print the value of an expression |
| `pp expr` | `pp expr` | Pretty-print (useful for dicts/lists) |
| `where` | `w` | Show call stack (where am I?) |
| `up` / `down` | `u` / `d` | Move up/down in the call stack |
| `break lineno` | `b N` | Set breakpoint at line N |
| `break func` | `b func` | Set breakpoint at start of function |
| `tbreak lineno` | `tb N` | Temporary breakpoint (fires once, then removed) |
| `clear` | `cl` | Clear all breakpoints |
| `args` | `a` | Print arguments of current function |
| `return` | `r` | Continue until current function returns |
| `jump lineno` | `j N` | Jump to line N (skips or re-runs lines) |
| `display expr` | — | Auto-display expression after each step |
| `interact` | — | Start an interactive Python session at this frame |

```python
# Example pdb session — step by step
# (Pdb) l        → see the code around current line
# (Pdb) p order  → print the 'order' variable
# (Pdb) pp order → pretty-print if it's a nested dict
# (Pdb) n        → step over: execute the line, move to next
# (Pdb) s        → step into: enter the function being called
# (Pdb) w        → show full call stack — where did we come from?
# (Pdb) u        → go up one frame in the call stack
# (Pdb) p order  → now inspect 'order' in the caller's frame
# (Pdb) c        → continue until next breakpoint
```

🔍 **Good to know:** `ipdb` (`pip install ipdb`) is a drop-in replacement for `pdb` with syntax highlighting, tab completion, and better stack display. Set `PYTHONBREAKPOINT=ipdb.set_trace` to use it everywhere `breakpoint()` is called.

📝 **Practice:** [pdb session / post-mortem debugging →](./practice.md#q18--ch15--pdb)

**Deep dive:** Full pdb walkthrough, conditional breakpoints, remote debugging, and IDE integration →
[`./01_pdb_debugging/theory.md`](./01_pdb_debugging/theory.md)

> [↑ Back to Top](#top)

---

<a id="16-advanced-debugging-techniques"></a>
# 16. Advanced Debugging Techniques

Beyond `pdb`, Python has a toolkit of specialised debugging instruments. Each one targets a different class of problem: `traceback` for structured error reporting, `warnings` for deprecation management, `faulthandler` for the rare cases where Python itself crashes, and memory profiling for leak detection.

---

<a id="logging-as-debugging-better-than-print"></a>
## Logging as Debugging (Better Than print)

Using `logging` for debugging gives you a toggle. Debug output can be silenced for production (by setting level to INFO) without removing a single line of code. With `print`, you either leave noise everywhere or do a search-and-delete before every deployment.

```python
import logging

logger = logging.getLogger(__name__)

# Set to DEBUG during development — silent in production (level=INFO)
logging.basicConfig(level=logging.DEBUG)

def calculate_discount(price: float, user_tier: str) -> float:
    logger.debug("calculate_discount: price=%.2f, tier=%s", price, user_tier)

    if user_tier == "premium":
        discount = price * 0.20
    elif user_tier == "standard":
        discount = price * 0.10
    else:
        discount = 0.0

    logger.debug("discount computed: %.2f (%.0f%%)", discount, (discount / price) * 100)
    return price - discount
```

```python
# Temporary debug context — add rich context without polluting all log lines
import contextlib

@contextlib.contextmanager
def debug_context(logger, label, **kwargs):
    logger.debug(">>> ENTER %s: %s", label, kwargs)
    try:
        yield
    except Exception as e:
        logger.debug("<<< EXCEPTION in %s: %s", label, e)
        raise
    finally:
        logger.debug("<<< EXIT %s", label)

# Usage:
with debug_context(logger, "process_payment", order_id=order_id, amount=amount):
    result = charge_card(order)
```

💡 **Hint:** Add a `DEBUG` env var check at app startup and set logging level dynamically. This lets you turn on debug logging in a running production container without redeploying.

---

<a id="traceback-module-for-custom-error-reporting"></a>
## traceback Module for Custom Error Reporting

The `traceback` module gives you programmatic access to exception stack traces — format them, store them, or send them to an alerting system without Python's default stderr dump.

```python
import traceback
import logging

logger = logging.getLogger(__name__)


def safe_process(items):
    results = []
    for item in items:
        try:
            results.append(process_item(item))
        except Exception as e:
            # Don't crash the whole batch — log richly and continue
            tb_str = traceback.format_exc()           # full traceback as string
            logger.error(
                "Failed to process item %s: %s\nTraceback:\n%s",
                item.get("id"), e, tb_str
            )
    return results


def report_exception():
    """Capture exception info as structured data."""
    exc_type, exc_value, exc_tb = sys.exc_info()

    return {
        "exception_type": exc_type.__name__,
        "message": str(exc_value),
        "traceback": traceback.format_tb(exc_tb),       # list of frame strings
        "summary": traceback.format_exception_only(exc_type, exc_value),
    }
```

```python
# traceback.print_exc() — print current exception with full stack (like Python default)
# traceback.format_exc() — return it as a string (for logging/alerting)
# traceback.format_tb(tb) — just the stack frames, not the exception line
# traceback.walk_stack(frame) — walk the current call stack without an exception
```

⚠️ **Common mistake — `str(e)` instead of `traceback.format_exc()`:** `str(e)` gives you only the exception message. `format_exc()` gives you the full stack trace with line numbers and file paths — the part that actually tells you where the problem is.

---

<a id="warnings-module"></a>
## warnings Module

The `warnings` module is Python's mechanism for *soft* alerts — messages that say "this works today but may break in the future" without raising an exception. It's the right tool for deprecation notices in libraries, and for alerting developers about suboptimal usage patterns.

```python
import warnings


def old_function(data, format="xml"):
    """Legacy function — use new_function() instead."""
    warnings.warn(
        "old_function() is deprecated and will be removed in v3.0. "
        "Use new_function() instead.",
        DeprecationWarning,
        stacklevel=2,   # ← points warning to the CALLER, not this line
    )
    return process(data, format)


# Warning categories:
# DeprecationWarning  — for developers (filtered by default in non-__main__ code)
# UserWarning         — general purpose, always shown
# RuntimeWarning      — potentially dangerous runtime condition
# FutureWarning       — behaviour will change in future versions (shown to end users)
# ResourceWarning     — unclosed file/socket (shown only in debug mode)
```

```python
import warnings

# Control warnings in application code
warnings.filterwarnings("error", category=DeprecationWarning)   # turn into exceptions
warnings.filterwarnings("ignore", message=".*unclosed.*")        # silence specific pattern
warnings.filterwarnings("once",  category=UserWarning)           # show each message once

# Capture warnings as log records (integrates with your logging config)
logging.captureWarnings(True)
# → warnings now appear as WARNING-level log records from the "py.warnings" logger
```

🔍 **Good to know:** `stacklevel=2` is almost always what you want in a wrapper function. It makes the warning point to the line that *called* your function, not the `warnings.warn()` line inside it — which is far more useful to the developer seeing the warning.

---

<a id="faulthandler-debugging-segfaults-and-deadlocks"></a>
## faulthandler: Debugging Segfaults and Deadlocks

Normal Python exceptions are caught with `try/except`. But some failures bypass Python entirely: a C extension corrupts memory, a thread deadlocks, or the interpreter gets a `SIGSEGV`. These produce no Python traceback at all — just a silent crash.

`faulthandler` installs low-level signal handlers that dump a Python-level traceback even when the interpreter is in a broken state.

```python
import faulthandler
import sys

# Dump traceback to stderr on SIGSEGV, SIGFPE, SIGABRT, SIGBUS, SIGILL
faulthandler.enable()

# For a file (useful in production — stderr may not be captured)
faulthandler.enable(file=open("crash.log", "w"))

# Dump all thread stacks on demand (useful for deadlock diagnosis)
faulthandler.dump_traceback()

# Timeout watchdog — dump traceback if program hangs for > N seconds
# (requires a dedicated thread)
faulthandler.dump_traceback_later(timeout=30, repeat=True, file=sys.stderr)
# Call faulthandler.cancel_dump_traceback_later() when done
```

```bash
# Enable from the command line without modifying code
python -X faulthandler myscript.py

# Or via environment variable
PYTHONFAULTHANDLER=1 python myscript.py
```

⚠️ **Common mistake — not enabling faulthandler in long-running services:** Without it, a segfault from a C extension (numpy, lxml, Pillow) produces nothing actionable — just a dead process. Enable it at application startup and redirect output to a crash log file.

🔍 **Good to know:** `faulthandler.dump_traceback_later()` is a deadlock detector. If your service stops responding, the watchdog fires and dumps all thread stacks — showing exactly which thread is blocked and where.

---

<a id="memory-profiling"></a>
## Memory Profiling

A memory leak in Python doesn't always mean a traditional leak — Python's GC handles most object cleanup. But objects can be kept alive unintentionally: a list that grows forever, a cache with no eviction, event listeners that hold references. `tracemalloc` and `memory_profiler` find them.

```python
import tracemalloc

# ── tracemalloc — stdlib, no dependencies ──────────────────────────────────
tracemalloc.start(10)  # ← keep 10-frame stack trace per allocation

snapshot1 = tracemalloc.take_snapshot()

# ... run the code you suspect is leaking ...
process_large_dataset()

snapshot2 = tracemalloc.take_snapshot()

# Show the top 5 memory increases
top_stats = snapshot2.compare_to(snapshot1, "lineno")
for stat in top_stats[:5]:
    print(stat)
# Output: mymodule.py:47: size=8.5 MiB (+8.5 MiB), count=120000 (+120000)
```

```python
# memory_profiler — line-by-line memory usage (pip install memory-profiler)
from memory_profiler import profile

@profile
def load_and_process():
    data = [i ** 2 for i in range(1_000_000)]   # line 4: +31.2 MiB
    filtered = [x for x in data if x % 2 == 0]  # line 5: +15.6 MiB
    del data                                      # line 6: -31.2 MiB
    return filtered

# Run: python -m memory_profiler myscript.py
```

```python
# objgraph — find what's keeping objects alive (pip install objgraph)
import objgraph

objgraph.show_most_common_types(limit=10)
# dict        18420
# list         8301
# function     4200
# ...

# Find what's holding a reference to your objects
objgraph.show_backrefs(some_object, max_depth=3)
```

💡 **Hint:** For production leak detection, use `tracemalloc` with periodic snapshots rather than `@profile` decorators (which require code modification). Compare snapshots taken 60 seconds apart — steady growth means a leak, stable means the initial allocation was just large.

🔍 **Good to know:** The most common Python memory leaks: (1) appending to a module-level list/dict without clearing it, (2) class-level caches with no size limit, (3) circular references involving `__del__` methods, (4) forgotten callbacks registered with event emitters.

📝 **Practice:** [tracemalloc snapshot / memory leak hunt →](./practice.md#q19--ch16--memory-profiling)

**Deep dive:** Full profiling setup, `cProfile`, `py-spy`, flamegraphs, production memory analysis →
[`./02_profiling_advanced/theory.md`](./02_profiling_advanced/theory.md)

> [↑ Back to Top](#top)

---

<a id="key-takeaways"></a>
# Key Takeaways

- **Use `logging`, never `print`** — levels, handlers, formatters, rotation. `print` has none of these.
- **Logger hierarchy** — `getLogger(__name__)` means your library's logs don't pollute the app's root logger and can be silenced in one line by the consumer.
- **`logging.exception()` inside `except` blocks** — the only correct way to log an exception with its full traceback.
- **Structured logging** — JSON logs are machine-queryable. In any system with log aggregation (ELK, Datadog, Splunk), they're not optional.
- **Correlation IDs via `ContextVar`** — thread-safe, async-safe per-request context. Use it.
- **`%s` format, not f-strings** — defers string formatting until the message is actually emitted.
- **`dictConfig`** — one dict, one call, your entire logging setup. Environment-switchable without code changes.
- **`pdb` / `breakpoint()`** — pause execution and inspect live state. Faster than any number of `print` statements.
- **`faulthandler.enable()`** — call it at app startup. The one time you need it, you'll be very glad it was there.
- **Memory leaks** — usually unbounded caches or forgotten references. `tracemalloc` + periodic snapshots finds them without slowing production down.

---

<a id="navigation"></a>
# 🔁 Navigation

**[🏠 Back to Python Mastery README](../README.md)**

| | |
|---|---|
| ⬅ Prev Module | [08 — File Handling](../08_file_handling/theory.md) |
| ➡ Next Module | [10 — Decorators](../10_decorators/theory.md) |

**This folder:**
[theory.md](./theory.md) · [cheetsheet.md](./cheetsheet.md) · [interview.md](./interview.md) · [practice.md](./practice.md) · [logging_examples.py](./logging_examples.py) · [structured_logging.py](./structured_logging.py)

**Subfolders:**
[01 — pdb Debugging](./01_pdb_debugging/theory.md) · [02 — Profiling & Advanced](./02_profiling_advanced/theory.md)

**Related modules:**
[10 — Decorators](../10_decorators/theory.md) · [13 — Concurrency](../13_concurrency/theory.md) · [19 — Production Best Practices](../19_production_best_practices/theory.md)

**Jump to specific topics:**
[Logger Hierarchy](./theory.md#7-the-logger-hierarchy-parent-child-propagation) · [dictConfig](./theory.md#13-dictconfig-configuration-as-data) · [pdb Commands](./theory.md#pdb-command-reference) · [Correlation IDs](./theory.md#10-correlation-ids-tracing-requests) · [Memory Profiling](./theory.md#memory-profiling) · [Exception Logging](./theory.md#8-exception-logging-the-right-way)
