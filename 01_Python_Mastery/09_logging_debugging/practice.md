# 💻 Practice — 09_logging_debugging

> Master file — covers all 16 chapters at survey depth.
> For deep dives: [pdb →](./01_pdb_debugging/practice.md) · [Profiling & Advanced →](./02_profiling_advanced/practice.md)

---

## Quick Index

| # | Difficulty | Topic | Skill |
|---|---|---|---|
| [Q1](#q1) | 🟢 Basic | Ch1 — logging basics | Replace print() with logging |
| [Q2](#q2) | 🟢 Basic | Ch2 — log levels | Set level and filter messages |
| [Q3](#q3) | 🟡 Intermediate | Ch3 — handlers | Attach StreamHandler + FileHandler |
| [Q4](#q4) | 🟡 Intermediate | Ch4 — formatters | Build a timestamp formatter |
| [Q5](#q5) | 🟡 Intermediate | Ch4 — basicConfig | Configure logging in one call |
| [Q6](#q6) | 🟢 Basic | Ch5 — format fields | Add filename and lineno |
| [Q7](#q7) | 🟡 Intermediate | Ch6 — RotatingFileHandler | Rotate at 1MB, keep 3 backups |
| [Q8](#q8) | 🟡 Intermediate | Ch7 — hierarchy | Parent/child loggers + propagation |
| [Q9](#q9) | 🟡 Intermediate | Ch7 — propagate | Disable propagation on child |
| [Q10](#q10) | 🟡 Intermediate | Ch8 — logging.exception | Log with full traceback |
| [Q11](#q11) | 🟡 Intermediate | Ch8 — exc_info | error() vs exception() |
| [Q12](#q12) | 🟡 Intermediate | Ch9 — JSON logging | Write a JSONFormatter |
| [Q13](#q13) | 🟡 Intermediate | Ch9 — extra fields | Inject extra context fields |
| [Q14](#q14) | 🟡 Intermediate | Ch10 — LoggerAdapter | Inject request_id automatically |
| [Q15](#q15) | 🟡 Intermediate | Ch11 — lazy formatting | % style vs f-string performance |
| [Q16](#q16) | 🟡 Intermediate | Ch12 — PII redaction | Filter to mask credit card numbers |
| [Q17](#q17) | 🟠 Advanced | Ch13 — dictConfig | Two handlers via dictConfig |
| [Q18](#q18) | 🟢 Basic | Ch14 — assertions | Precondition check with assert |
| [Q19](#q19) | 🟢 Basic | Ch15 — breakpoint | Insert breakpoint(), 5 key commands |
| [Q20](#q20) | 🟡 Intermediate | Ch15 — post-mortem | pdb.pm() after unhandled exception |
| [Q21](#q21) | 🟡 Intermediate | Ch16 — traceback | Capture traceback string without re-raising |
| [Q22](#q22) | 🟡 Intermediate | Ch16 — warnings | Emit a DeprecationWarning |
| [Q23](#q23) | 🟠 Advanced | Mixed — production logger | Factory function create_logger() |
| [Q24](#q24) | 🟠 Advanced | Mixed — timing decorator | @log_timing logs function duration |
| [Q25](#q25) | 🟡 Intermediate | Mixed — caplog in tests | pytest caplog fixture |
| [Q26](#q26) | 🟠 Advanced | Mixed — QueueHandler | Async logging to avoid blocking |
| [Q27](#q27) | 🟠 Advanced | Mixed — Capstone | Request logging middleware |

---

<a id="q1"></a>

### Q1 🟢 · logging basics — Replace print() with logging

> 🛠️ **Solve locally:** [practice_local.py → Q1](./practice_local.py)



**Problem:** You have this script that uses `print()` for diagnostics. Replace it with the `logging` module using `basicConfig()` to output `INFO`-level messages to the console. Show the log level name in the output.

```python
# Before:
def connect(host, port):
    print(f"Connecting to {host}:{port}")
    print("Connection established")
    print("Error: timeout")
```

<details>
<summary>💡 Hint</summary>

Call `logging.basicConfig(level=logging.INFO, format="%(levelname)s:%(name)s:%(message)s")` before any log calls. Then use `logging.info()` and `logging.error()` instead of `print()`.

</details>

<details>
<summary>✅ Answer</summary>

```python
import logging

logging.basicConfig(
    level=logging.INFO,
    format="%(levelname)s:%(name)s:%(message)s",
)


def connect(host, port):
    logging.info("Connecting to %s:%d", host, port)
    logging.info("Connection established")
    logging.error("Error: timeout")


connect("db.prod.internal", 5432)
# INFO:root:Connecting to db.prod.internal:5432
# INFO:root:Connection established
# ERROR:root:Error: timeout
```

**Why:** `logging` adds level names, logger names, and timestamps for free. Unlike `print()`, messages below the configured level are silently dropped — so `DEBUG` calls in this setup produce zero output and zero cost.

</details>

---

<a id="q2"></a>

### Q2 🟢 · log levels — Set level and filter messages (DEBUG through CRITICAL)

> 🛠️ **Solve locally:** [practice_local.py → Q2](./practice_local.py)



**Problem:** Create a root logger configured to `DEBUG` level. Fire one message at each of the five standard levels. Then reconfigure the level to `WARNING` and show which messages are suppressed.

<details>
<summary>💡 Hint</summary>

`logging.basicConfig(level=logging.DEBUG)` makes all five levels visible. Call `logging.getLogger().setLevel(logging.WARNING)` to raise the threshold dynamically — no messages below WARNING will appear after that.

</details>

<details>
<summary>✅ Answer</summary>

```python
import logging

# --- Pass 1: DEBUG threshold — all five levels visible ---
logging.basicConfig(
    level=logging.DEBUG,
    format="%(levelname)-8s | %(message)s",
)

logging.debug("debug: cache miss for key user:42")        # shown
logging.info("info: user alice logged in")                 # shown
logging.warning("warning: retry 2/3 for Stripe call")     # shown
logging.error("error: payment failed for order #4892")    # shown
logging.critical("critical: database unreachable")         # shown

print("\n--- Raising threshold to WARNING ---\n")

# --- Pass 2: WARNING threshold — DEBUG and INFO silenced ---
logging.getLogger().setLevel(logging.WARNING)

logging.debug("debug: this is suppressed")    # NOT shown
logging.info("info: this is suppressed")      # NOT shown
logging.warning("warning: this appears")      # shown
logging.error("error: this appears")          # shown
logging.critical("critical: this appears")    # shown
```

**Why:** The numeric value of each level (DEBUG=10, INFO=20, WARNING=30, ERROR=40, CRITICAL=50) is compared against the logger's threshold. Records below the threshold are discarded before any formatting or I/O happens, so unused debug calls have near-zero runtime cost in production.

</details>

---

<a id="q3"></a>

### Q3 🟡 · handlers — Attach StreamHandler + FileHandler to a named logger

> 🛠️ **Solve locally:** [practice_local.py → Q3](./practice_local.py)



**Problem:** Create a named logger `"myapp"` with two handlers: a `StreamHandler` that writes `WARNING`+ to the console, and a `FileHandler` that writes `DEBUG`+ to `app.log`. Both handlers should share the same formatter. Do not use `basicConfig()`.

<details>
<summary>💡 Hint</summary>

Set the logger's own level to `DEBUG` so it passes all records through. Each handler has its own `setLevel()`. Attach the same `Formatter` instance to both handlers with `handler.setFormatter(fmt)`.

</details>

<details>
<summary>✅ Answer</summary>

```python
import logging

# --- Logger ---
logger = logging.getLogger("myapp")
logger.setLevel(logging.DEBUG)          # pass everything through to handlers

# --- Shared formatter ---
fmt = logging.Formatter(
    "%(asctime)s | %(levelname)-8s | %(name)s | %(message)s",
    datefmt="%H:%M:%S",
)

# --- Console handler: WARNING and above ---
console = logging.StreamHandler()
console.setLevel(logging.WARNING)
console.setFormatter(fmt)

# --- File handler: DEBUG and above ---
file_h = logging.FileHandler("app.log", encoding="utf-8")
file_h.setLevel(logging.DEBUG)
file_h.setFormatter(fmt)

logger.addHandler(console)
logger.addHandler(file_h)

# Test:
logger.debug("cache miss — goes to file only")
logger.info("user logged in — goes to file only")
logger.warning("retry 2/3 — goes to console AND file")
logger.error("payment failed — goes to console AND file")
```

**Why:** Each handler is an independent routing rule. Setting `DEBUG` on the logger lets all records reach the handlers; each handler then applies its own level gate. This pattern gives you verbose file logs for debugging and clean console output in production without any duplication in logic.

</details>

---

<a id="q4"></a>

### Q4 🟡 · formatters — Build a formatter with timestamp, level, name, message

> 🛠️ **Solve locally:** [practice_local.py → Q4](./practice_local.py)



**Problem:** Create a `logging.Formatter` that produces output in this exact format:

```
2025-03-08 14:30:00 | ERROR    | myapp.payment:47 | Payment failed
```

Fields needed: human timestamp, level (left-aligned in 8 chars), logger name + line number, message.

<details>
<summary>💡 Hint</summary>

Use `%(levelname)-8s` for left-aligned level. The `%(name)s:%(lineno)d` pair gives `myapp.payment:47`. Set `datefmt="%Y-%m-%d %H:%M:%S"` on the formatter.

</details>

<details>
<summary>✅ Answer</summary>

```python
import logging

fmt = logging.Formatter(
    fmt="%(asctime)s | %(levelname)-8s | %(name)s:%(lineno)d | %(message)s",
    datefmt="%Y-%m-%d %H:%M:%S",
)

handler = logging.StreamHandler()
handler.setFormatter(fmt)

logger = logging.getLogger("myapp.payment")
logger.setLevel(logging.DEBUG)
logger.addHandler(handler)
logger.propagate = False   # prevent duplicate output to root

logger.error("Payment failed")
# 2025-03-08 14:30:00 | ERROR    | myapp.payment:20 | Payment failed
```

**Why:** The `-8s` width specifier aligns level names so log lines form readable columns. Using `%(name)s:%(lineno)d` gives you instant file + line context — essential for tracing errors in large codebases without hunting through source files.

</details>

---

<a id="q5"></a>

### Q5 🟡 · basicConfig — Configure logging with filename, level, and format in one call

> 🛠️ **Solve locally:** [practice_local.py → Q5](./practice_local.py)



**Problem:** Use a single `logging.basicConfig()` call to: write to `service.log`, set level to `INFO`, use the production format `"%(asctime)s | %(levelname)-8s | %(name)s | %(message)s"`, append to the file, and encode as UTF-8. Then emit one test message.

<details>
<summary>💡 Hint</summary>

`basicConfig()` accepts `filename`, `filemode`, `level`, `format`, `datefmt`, and `encoding` as keyword args. It only takes effect the first time it is called — if the root logger already has handlers, the call is silently ignored.

</details>

<details>
<summary>✅ Answer</summary>

```python
import logging

logging.basicConfig(
    filename="service.log",
    filemode="a",
    level=logging.INFO,
    format="%(asctime)s | %(levelname)-8s | %(name)s | %(message)s",
    datefmt="%Y-%m-%d %H:%M:%S",
    encoding="utf-8",
)

logger = logging.getLogger(__name__)
logger.info("Service started on port 8080")
# Written to service.log:
# 2025-03-08 14:30:00 | INFO     | __main__ | Service started on port 8080
```

**Why:** `basicConfig()` is the fastest path to file logging with zero boilerplate. The `filemode="a"` default appends across restarts so you never lose previous log history. The `encoding="utf-8"` guard prevents crashes when log messages contain non-ASCII characters.

</details>

---

<a id="q6"></a>

### Q6 🟢 · format fields — Add %(filename)s and %(lineno)d to format string

> 🛠️ **Solve locally:** [practice_local.py → Q6](./practice_local.py)



**Problem:** Build a formatter that includes the source filename and line number in every log line, so output looks like:

```
[payment.py:23] ERROR — Card charge failed
```

<details>
<summary>💡 Hint</summary>

`%(filename)s` gives just the basename (e.g. `payment.py`), while `%(pathname)s` gives the full path. `%(lineno)d` is an integer field so use `%d` not `%s`.

</details>

<details>
<summary>✅ Answer</summary>

```python
import logging

fmt = logging.Formatter(
    "[%(filename)s:%(lineno)d] %(levelname)s — %(message)s"
)

handler = logging.StreamHandler()
handler.setFormatter(fmt)

logger = logging.getLogger("demo")
logger.setLevel(logging.DEBUG)
logger.addHandler(handler)
logger.propagate = False

logger.error("Card charge failed")
# [practice_local.py:14] ERROR — Card charge failed
```

**Why:** `%(filename)s` and `%(lineno)d` are populated automatically from Python's inspect machinery — you get file + line context for free with no extra code. This is invaluable in production: when an alert fires you can jump straight to the exact line that emitted the log.

</details>

---

<a id="q7"></a>

### Q7 🟡 · RotatingFileHandler — Rotate at 1MB, keep 3 backups

> 🛠️ **Solve locally:** [practice_local.py → Q7](./practice_local.py)



**Problem:** Configure a logger named `"rotator"` that writes to `rotate_demo.log`, rotates when the file reaches 1 MB, and keeps 3 backup files (`rotate_demo.log.1`, `rotate_demo.log.2`, `rotate_demo.log.3`). Attach a standard formatter.

<details>
<summary>💡 Hint</summary>

`RotatingFileHandler` takes `maxBytes` (bytes as int) and `backupCount`. 1 MB = `1 * 1024 * 1024`. When `maxBytes` is reached, the current file is renamed to `.1`, `.1` to `.2`, and so on. The oldest (`.backupCount`) is deleted.

</details>

<details>
<summary>✅ Answer</summary>

```python
import logging
from logging.handlers import RotatingFileHandler

logger = logging.getLogger("rotator")
logger.setLevel(logging.DEBUG)

handler = RotatingFileHandler(
    filename="rotate_demo.log",
    maxBytes=1 * 1024 * 1024,   # 1 MB
    backupCount=3,
    encoding="utf-8",
)
handler.setFormatter(
    logging.Formatter("%(asctime)s | %(levelname)s | %(message)s")
)

logger.addHandler(handler)
logger.propagate = False

# Simulate log writes:
for i in range(100):
    logger.info("Log entry %d — padding to fill the file faster", i)

# Files on disk after enough writes:
# rotate_demo.log       ← current
# rotate_demo.log.1     ← previous
# rotate_demo.log.2     ← older
# rotate_demo.log.3     ← oldest (4th would be deleted)
```

**Why:** Without rotation, a long-running service's log file grows unbounded and eventually fills the disk. `RotatingFileHandler` caps total disk usage at `maxBytes * (backupCount + 1)` — here 4 MB maximum — preventing the classic "disk full at 3 AM" outage.

</details>

---

<a id="q8"></a>

### Q8 🟡 · hierarchy — Create parent/child loggers and observe propagation

> 🛠️ **Solve locally:** [practice_local.py → Q8](./practice_local.py)



**Problem:** Create three loggers: `"app"` (parent), `"app.services"` (child), and `"app.services.payment"` (grandchild). Attach a handler only to `"app"`. Log a message from `"app.services.payment"` and show that it reaches the `"app"` handler via propagation.

<details>
<summary>💡 Hint</summary>

Python derives the hierarchy from the dots in the logger name — no explicit parent/child registration needed. Records bubble up the tree until `propagate=False` is encountered or the root is reached.

</details>

<details>
<summary>✅ Answer</summary>

```python
import logging

# Attach a single handler only to the top-level "app" logger:
app_logger = logging.getLogger("app")
app_logger.setLevel(logging.DEBUG)

handler = logging.StreamHandler()
handler.setFormatter(
    logging.Formatter("%(levelname)s | [%(name)s] | %(message)s")
)
app_logger.addHandler(handler)

# Child and grandchild — no handlers of their own:
svc_logger     = logging.getLogger("app.services")
payment_logger = logging.getLogger("app.services.payment")

# Log from the deepest child:
payment_logger.info("Payment of $499 processed")
# INFO | [app.services.payment] | Payment of $499 processed
# ↑ bubbled up to "app" handler via propagation

svc_logger.warning("Service response time above threshold")
# WARNING | [app.services] | Service response time above threshold
```

**Why:** Propagation is how the entire Python ecosystem manages logging — library code calls `getLogger(__name__)` and never touches handlers. The application owner attaches handlers at the root or app logger, and every library's records flow up automatically. No coordination required.

</details>

---

<a id="q9"></a>

### Q9 🟡 · propagate — Disable propagation on a child logger

> 🛠️ **Solve locally:** [practice_local.py → Q9](./practice_local.py)



**Problem:** You have a noisy child logger `"app.metrics"` whose `DEBUG` messages are flooding the root handler. Attach a dedicated `FileHandler` to `"app.metrics"` and disable propagation so its records stay there.

<details>
<summary>💡 Hint</summary>

Set `logger.propagate = False` on the child. After that, records logged to `"app.metrics"` only reach handlers attached directly to that logger — they never travel up to `"app"` or root.

</details>

<details>
<summary>✅ Answer</summary>

```python
import logging

# Root: captures everything by default
root = logging.getLogger()
root.setLevel(logging.WARNING)
root_handler = logging.StreamHandler()
root_handler.setFormatter(logging.Formatter("ROOT | %(levelname)s | %(message)s"))
root.addHandler(root_handler)

# app.metrics: isolated — DEBUG logs go to its own file, never to root
metrics_logger = logging.getLogger("app.metrics")
metrics_logger.setLevel(logging.DEBUG)
metrics_logger.propagate = False           # ← key line

metrics_file = logging.FileHandler("metrics.log", encoding="utf-8")
metrics_file.setFormatter(
    logging.Formatter("%(asctime)s | %(levelname)s | %(message)s")
)
metrics_logger.addHandler(metrics_file)

# These go ONLY to metrics.log — root console stays clean:
metrics_logger.debug("cpu_usage=42%")
metrics_logger.debug("mem_usage=1.2GB")

# This still reaches the root console handler:
logging.getLogger("app.api").warning("High latency on /checkout")
```

**Why:** `propagate = False` is how you isolate high-volume loggers (metrics, SQL query logs, tracing) from your main log stream. Without it, enabling `DEBUG` on one child would flood every parent handler — a common cause of accidental log volume explosions.

</details>

---

<a id="q10"></a>

### Q10 🟡 · logging.exception — Log exception with full traceback inside except block

> 🛠️ **Solve locally:** [practice_local.py → Q10](./practice_local.py)



**Problem:** Write a function `safe_divide(a, b)` that catches `ZeroDivisionError` and logs the full traceback using `logger.exception()`. The log message should read `"Division failed"`.

<details>
<summary>💡 Hint</summary>

`logger.exception(msg)` must be called inside an `except` block. It automatically attaches the current exception info — equivalent to `logger.error(msg, exc_info=True)`. You get ERROR level + your message + the full traceback in one call.

</details>

<details>
<summary>✅ Answer</summary>

```python
import logging

logging.basicConfig(
    level=logging.DEBUG,
    format="%(levelname)s | %(name)s | %(message)s",
)
logger = logging.getLogger(__name__)


def safe_divide(a, b):
    try:
        return a / b
    except ZeroDivisionError:
        logger.exception("Division failed")
        return None


result = safe_divide(10, 0)
print("Result:", result)

# Output:
# ERROR | __main__ | Division failed
# Traceback (most recent call last):
#   File "practice_local.py", line 11, in safe_divide
#     return a / b
# ZeroDivisionError: division by zero
# Result: None
```

**Why:** `logger.exception()` is the correct idiom for "log this error and include the full traceback." The traceback is the most important debugging artifact — it tells you exactly where things went wrong. Logging just the error message (`logger.error(str(e))`) throws away all that context.

</details>

---

<a id="q11"></a>

### Q11 🟡 · exc_info — Difference between logging.error() and logging.exception()

> 🛠️ **Solve locally:** [practice_local.py → Q11](./practice_local.py)



**Problem:** Demonstrate the difference between `logger.error("msg")`, `logger.error("msg", exc_info=True)`, and `logger.exception("msg")` inside an `except` block. When would you choose `error()` over `exception()`?

<details>
<summary>💡 Hint</summary>

`logger.exception(msg)` is literally `logger.error(msg, exc_info=True)` — they are equivalent. Use `logger.error()` without `exc_info` when you want ERROR level but have already extracted the relevant info from the exception and don't need the full traceback in the log.

</details>

<details>
<summary>✅ Answer</summary>

```python
import logging

logging.basicConfig(level=logging.DEBUG, format="%(levelname)s | %(message)s")
logger = logging.getLogger(__name__)

try:
    int("not-a-number")
except ValueError as e:

    # 1. Just the message — NO traceback:
    logger.error("Conversion failed: %s", e)
    # ERROR | Conversion failed: invalid literal for int() with base 10: 'not-a-number'

    # 2. exc_info=True — message + full traceback:
    logger.error("Conversion failed with traceback", exc_info=True)
    # ERROR | Conversion failed with traceback
    # Traceback (most recent call last): ...

    # 3. logger.exception — identical to (2), just more concise:
    logger.exception("Conversion failed via exception()")
    # ERROR | Conversion failed via exception()
    # Traceback (most recent call last): ...


# Rule of thumb:
# Use logger.error()     when you've already captured what you need from the
#                        exception and a traceback would add noise (e.g. you're
#                        re-raising and the traceback will appear elsewhere).
# Use logger.exception() when this is the final handler and you want full context.
```

**Why:** Tracebacks are verbose. In systems that forward logs to Elasticsearch or Splunk, large tracebacks inflate storage costs. Use `logger.error()` (no traceback) when the error is expected and the message is self-explanatory. Use `logger.exception()` for unexpected failures where you need the full call stack.

</details>

---

<a id="q12"></a>

### Q12 🟡 · JSON logging — Write a JSONFormatter that outputs log records as JSON

> 🛠️ **Solve locally:** [practice_local.py → Q12](./practice_local.py)



**Problem:** Write a `JSONFormatter` class that subclasses `logging.Formatter`. Its `format()` method should return a JSON string with keys: `timestamp`, `level`, `logger`, `module`, `line`, `message`. Include the exception as an `"exception"` key when present.

<details>
<summary>💡 Hint</summary>

Subclass `logging.Formatter` and override `format(self, record)`. The `record` object has attributes: `record.levelname`, `record.name`, `record.module`, `record.lineno`, `record.exc_info`. Call `record.getMessage()` to get the formatted message string.

</details>

<details>
<summary>✅ Answer</summary>

```python
import json
import logging
from datetime import datetime, timezone


class JSONFormatter(logging.Formatter):
    """Formats log records as single-line JSON strings."""

    def format(self, record: logging.LogRecord) -> str:
        entry = {
            "timestamp": datetime.now(timezone.utc).isoformat(),
            "level":     record.levelname,
            "logger":    record.name,
            "module":    record.module,
            "line":      record.lineno,
            "message":   record.getMessage(),
        }
        if record.exc_info:
            entry["exception"] = self.formatException(record.exc_info)
        return json.dumps(entry, default=str)


# --- Attach and test ---
handler = logging.StreamHandler()
handler.setFormatter(JSONFormatter())

logger = logging.getLogger("json_demo")
logger.setLevel(logging.DEBUG)
logger.addHandler(handler)
logger.propagate = False

logger.info("User logged in", )
# {"timestamp": "2025-03-08T14:30:00.000Z", "level": "INFO", "logger": "json_demo", ...}

try:
    1 / 0
except ZeroDivisionError:
    logger.exception("Division error")
# {..., "exception": "Traceback (most recent call last):\n  ...ZeroDivisionError: division by zero"}
```

**Why:** JSON logs are machine-parseable. Log aggregation platforms (Elasticsearch, Splunk, CloudWatch Logs Insights, Datadog) can index JSON fields natively — you can query `level:ERROR AND module:payment` instead of grepping raw text. This is the production standard for any service at scale.

</details>

---

<a id="q13"></a>

### Q13 🟡 · extra fields — Use logger.info("msg", extra={...}) pattern

> 🛠️ **Solve locally:** [practice_local.py → Q13](./practice_local.py)



**Problem:** Log a payment event with `logger.info()` that includes `request_id`, `user_id`, and `amount` as structured fields via the `extra=` parameter. Show them in the formatted output.

<details>
<summary>💡 Hint</summary>

Fields passed via `extra={"key": "val"}` are merged into the `LogRecord` as attributes. To include them in the format string, reference them as `%(key)s`. The key names must not clash with existing `LogRecord` attributes.

</details>

<details>
<summary>✅ Answer</summary>

```python
import logging

fmt = logging.Formatter(
    "%(asctime)s | %(levelname)s | req=%(request_id)s | user=%(user_id)s | "
    "amount=%(amount).2f | %(message)s",
    datefmt="%H:%M:%S",
)

handler = logging.StreamHandler()
handler.setFormatter(fmt)

logger = logging.getLogger("payments")
logger.setLevel(logging.INFO)
logger.addHandler(handler)
logger.propagate = False

logger.info(
    "Payment processed",
    extra={
        "request_id": "f47ac10b-58cc",
        "user_id": 1042,
        "amount": 499.00,
    },
)
# 14:30:00 | INFO | req=f47ac10b-58cc | user=1042 | amount=499.00 | Payment processed
```

**Why:** The `extra=` pattern lets you attach structured context to individual log calls without building a custom formatter class. When combined with a `JSONFormatter`, these fields become top-level JSON keys — fully queryable in your log platform. This is the lightweight alternative to `LoggerAdapter` when context is call-specific rather than request-wide.

</details>

---

<a id="q14"></a>

### Q14 🟡 · LoggerAdapter — Inject request_id into every log line using LoggerAdapter

> 🛠️ **Solve locally:** [practice_local.py → Q14](./practice_local.py)



**Problem:** Create a `logging.LoggerAdapter` that automatically prepends `[req_id=<value>]` to every log message. Instantiate it with a request ID and use it to log two messages — neither call should pass `extra=` manually.

<details>
<summary>💡 Hint</summary>

Subclass `logging.LoggerAdapter` and override `process(self, msg, kwargs)`. Modify `msg` to prepend the context, then return `(msg, kwargs)`. Alternatively, inject into `kwargs["extra"]` directly.

</details>

<details>
<summary>✅ Answer</summary>

```python
import logging


class RequestAdapter(logging.LoggerAdapter):
    """Injects request_id into every log message automatically."""

    def process(self, msg, kwargs):
        # Prepend the request ID to the message text:
        return f"[req_id={self.extra['request_id']}] {msg}", kwargs


# --- Setup base logger ---
base_logger = logging.getLogger("api")
base_logger.setLevel(logging.DEBUG)
handler = logging.StreamHandler()
handler.setFormatter(logging.Formatter("%(levelname)s | %(name)s | %(message)s"))
base_logger.addHandler(handler)
base_logger.propagate = False

# --- Wrap with adapter for a specific request ---
logger = RequestAdapter(base_logger, {"request_id": "f47ac10b-58cc"})

logger.info("Request received: GET /checkout")
logger.error("Payment gateway timeout")

# INFO | api | [req_id=f47ac10b-58cc] Request received: GET /checkout
# ERROR | api | [req_id=f47ac10b-58cc] Payment gateway timeout
```

**Why:** `LoggerAdapter` is the clean solution when you have context (like a request ID) that should appear in every log line for the duration of a request. You inject it once at request entry and every downstream log call carries it automatically — no need to thread `extra=` through every function signature.

</details>

---

<a id="q15"></a>

### Q15 🟡 · lazy formatting — Explain why logger.debug("val=%s", val) beats f-string

> 🛠️ **Solve locally:** [practice_local.py → Q15](./practice_local.py)



**Problem:** Write a benchmark that demonstrates that `logger.debug("items: %s", large_list)` avoids string formatting when DEBUG is disabled, while `logger.debug(f"items: {large_list}")` does the formatting work regardless of level.

<details>
<summary>💡 Hint</summary>

The f-string is evaluated by Python before `logger.debug()` is even called — the logging system never gets a chance to skip it. The `%s` style is just a template; `logging` only calls `record.getMessage()` (which does the format) if the record will actually be emitted.

</details>

<details>
<summary>✅ Answer</summary>

```python
import logging
import time

logging.basicConfig(level=logging.WARNING)   # DEBUG is OFF
logger = logging.getLogger("perf_demo")

large_list = list(range(100_000))

# --- BAD: f-string always formats, even if DEBUG is disabled ---
start = time.perf_counter()
for _ in range(1000):
    logger.debug(f"items: {large_list}")     # str(large_list) called 1000 times
fstring_time = time.perf_counter() - start

# --- GOOD: % style — formatting skipped when level is disabled ---
start = time.perf_counter()
for _ in range(1000):
    logger.debug("items: %s", large_list)    # large_list never stringified
percent_time = time.perf_counter() - start

print(f"f-string style : {fstring_time:.4f}s")
print(f"%s style       : {percent_time:.6f}s")
print(f"Speedup        : {fstring_time / percent_time:.0f}x faster")

# Typical output:
# f-string style : 0.8500s
# %s style       : 0.000050s
# Speedup        : ~17000x faster

# --- Even better: isEnabledFor guard for expensive computations ---
if logger.isEnabledFor(logging.DEBUG):
    expensive_repr = compute_debug_summary(large_list)   # never called in prod
    logger.debug("summary: %s", expensive_repr)
```

**Why:** In production, `DEBUG` is almost always disabled. But if you use f-strings, Python evaluates the entire expression — calling `str()` on potentially large objects — before the logger can decide to discard the record. With `%s` style, the format call is deferred inside `LogRecord.getMessage()` and only triggered if the record survives the level check. This is a real performance concern in hot code paths.

</details>

---

<a id="q16"></a>

### Q16 🟡 · PII redaction — Write a filter that masks credit card numbers in log messages

> 🛠️ **Solve locally:** [practice_local.py → Q16](./practice_local.py)



**Problem:** Write a `logging.Filter` subclass called `CreditCardFilter` that replaces any 16-digit sequence in log messages with `****-****-****-****`. Attach it to a handler and verify it fires.

<details>
<summary>💡 Hint</summary>

Subclass `logging.Filter` and override `filter(self, record)`. Mutate `record.msg` using `re.sub()`. Return `True` to allow the record through (just modified). Attach the filter to a handler with `handler.addFilter(f)`.

</details>

<details>
<summary>✅ Answer</summary>

```python
import logging
import re


class CreditCardFilter(logging.Filter):
    """Replaces 16-digit card numbers in log messages with ****-****-****-****."""

    _pattern = re.compile(r'\b\d{4}[- ]?\d{4}[- ]?\d{4}[- ]?\d{4}\b')
    _replacement = "****-****-****-****"

    def filter(self, record: logging.LogRecord) -> bool:
        if isinstance(record.msg, str):
            record.msg = self._pattern.sub(self._replacement, record.msg)
        # Also handle pre-formatted args (edge case):
        if record.args:
            record.args = tuple(
                self._pattern.sub(self._replacement, str(a)) if isinstance(a, str) else a
                for a in (record.args if isinstance(record.args, tuple) else (record.args,))
            )
        return True   # always allow — we only redact, not suppress


# --- Attach and test ---
handler = logging.StreamHandler()
handler.addFilter(CreditCardFilter())
handler.setFormatter(logging.Formatter("%(levelname)s | %(message)s"))

logger = logging.getLogger("payments")
logger.setLevel(logging.DEBUG)
logger.addHandler(handler)
logger.propagate = False

logger.info("Processing card 4111111111111111 for order #4892")
# INFO | Processing card ****-****-****-**** for order #4892

logger.warning("Retry for card number: 4111-1111-1111-1111")
# WARNING | Retry for card number: ****-****-****-****
```

**Why:** Security filters belong on handlers, not in application code. Centralising redaction here means a developer can't accidentally log a card number — the filter silently masks it before any I/O. This approach satisfies PCI-DSS requirements without burdening every call site with redaction logic.

</details>

---

<a id="q17"></a>

### Q17 🟠 · dictConfig — Configure two handlers (console + file) using logging.config.dictConfig

> 🛠️ **Solve locally:** [practice_local.py → Q17](./practice_local.py)



**Problem:** Use `logging.config.dictConfig()` to configure: a `"standard"` formatter, a `console` handler (INFO+, stdout), a `file` handler (DEBUG+, `app.log`, rotating at 5MB, 3 backups), and a `"myapp"` logger that uses both handlers with `propagate=False`.

<details>
<summary>💡 Hint</summary>

The dict must have `"version": 1`. Use `"disable_existing_loggers": False` to avoid silencing third-party loggers. Reference handlers in the logger's `"handlers"` list by the names you defined in the top-level `"handlers"` dict.

</details>

<details>
<summary>✅ Answer</summary>

```python
import logging
import logging.config

LOGGING_CONFIG = {
    "version": 1,
    "disable_existing_loggers": False,

    "formatters": {
        "standard": {
            "format": "%(asctime)s | %(levelname)-8s | %(name)s:%(lineno)d | %(message)s",
            "datefmt": "%Y-%m-%d %H:%M:%S",
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
            "formatter": "standard",
            "filename": "app.log",
            "maxBytes": 5 * 1024 * 1024,   # 5 MB
            "backupCount": 3,
            "encoding": "utf-8",
        },
    },

    "loggers": {
        "myapp": {
            "level": "DEBUG",
            "handlers": ["console", "file"],
            "propagate": False,
        },
    },

    "root": {
        "level": "WARNING",
        "handlers": ["console"],
    },
}

logging.config.dictConfig(LOGGING_CONFIG)

logger = logging.getLogger("myapp")
logger.debug("Cache miss — goes to file only")
logger.info("User logged in — goes to console and file")
logger.error("Payment failed — goes to console and file")
```

**Why:** `dictConfig` separates logging policy from application code. In production, you load this dict from a YAML or JSON config file, so ops can adjust log levels and destinations without touching source code or redeploying. It's also idempotent — calling it again reconfigures everything cleanly.

</details>

---

<a id="q18"></a>

### Q18 🟢 · assertions — Write an assert with a descriptive message for a precondition check

> 🛠️ **Solve locally:** [practice_local.py → Q18](./practice_local.py)



**Problem:** Write a function `process_order(order_id, amount)` that uses `assert` statements to enforce two preconditions: `order_id` must be a positive integer, and `amount` must be greater than 0. Each assert must include a descriptive error message.

<details>
<summary>💡 Hint</summary>

`assert <condition>, <message>` raises `AssertionError` with the message if the condition is false. Note: asserts are disabled when Python runs with the `-O` (optimize) flag — use them for internal invariants, not user input validation.

</details>

<details>
<summary>✅ Answer</summary>

```python
def process_order(order_id: int, amount: float) -> dict:
    assert isinstance(order_id, int) and order_id > 0, (
        f"order_id must be a positive integer, got {order_id!r}"
    )
    assert amount > 0, (
        f"amount must be greater than 0, got {amount!r}"
    )

    return {"order_id": order_id, "amount": amount, "status": "processed"}


# Valid:
print(process_order(4892, 499.00))
# {'order_id': 4892, 'amount': 499.0, 'status': 'processed'}

# Invalid — raises AssertionError:
try:
    process_order(-1, 499.00)
except AssertionError as e:
    print(f"AssertionError: {e}")
# AssertionError: order_id must be a positive integer, got -1

try:
    process_order(4892, 0)
except AssertionError as e:
    print(f"AssertionError: {e}")
# AssertionError: amount must be greater than 0, got 0
```

**Why:** Assertions document programmer intent — "this should never be false if the code is correct." A descriptive message turns a cryptic `AssertionError` into an actionable statement. Use `assert` for internal invariants and debug guards; use `raise ValueError` for user-facing validation that must survive the `-O` flag.

</details>

---

<a id="q19"></a>

### Q19 🟢 · breakpoint — Insert breakpoint() and describe the 5 commands you'd use first

> 🛠️ **Solve locally:** [practice_local.py → Q19](./practice_local.py)



**Problem:** Insert `breakpoint()` into the function below at the point where `total` is computed. Then describe the first 5 pdb commands you would run and what each shows.

```python
def calculate_discount(price, discount_pct):
    discount = price * (discount_pct / 100)
    total = price - discount
    return total
```

<details>
<summary>💡 Hint</summary>

`breakpoint()` is a built-in since Python 3.7. It calls `sys.breakpointhook()` which defaults to `pdb.set_trace()`. In the pdb session, the prompt shows `(Pdb)`. Type `h` for help.

</details>

<details>
<summary>✅ Answer</summary>

```python
def calculate_discount(price, discount_pct):
    discount = price * (discount_pct / 100)
    breakpoint()    # ← execution pauses here
    total = price - discount
    return total


calculate_discount(499.00, 10)

# --- What happens in the pdb session ---
# (Pdb) l
# Shows the current source context (±11 lines around the breakpoint).

# (Pdb) p price
# 499.0  — inspect the value of price

# (Pdb) p discount
# 49.9   — inspect the computed discount

# (Pdb) n
# Executes the current line (total = price - discount), steps OVER any calls.

# (Pdb) p total
# 449.1  — inspect total after stepping over the assignment

# (Pdb) c
# Continues execution until the next breakpoint or the program ends.

# Bonus commands:
# (Pdb) a      — show all arguments of the current function
# (Pdb) w      — show full call stack (where am I?)
# (Pdb) pp price.__class__  — pretty-print any expression
```

**Why:** `breakpoint()` replaced the verbose `import pdb; pdb.set_trace()` pattern in Python 3.7. The five most-used commands cover 90% of debugging: `l` (orient yourself), `p` (inspect values), `n` (step forward), `c` (skip to next interesting point), and `q` (bail out). Master these before anything else.

</details>

---

<a id="q20"></a>

### Q20 🟡 · post-mortem — Use pdb.pm() after an unhandled exception in a script

> 🛠️ **Solve locally:** [practice_local.py → Q20](./practice_local.py)



**Problem:** Write a script that calls a function with a bug. Wrap the call in a try/except that invokes `pdb.post_mortem()` to start an interactive debug session at the exact frame where the exception originated.

<details>
<summary>💡 Hint</summary>

`pdb.post_mortem()` with no arguments uses `sys.exc_info()[2]` — the current exception's traceback. Call it inside an `except` block. The debugger starts at the line that raised, with the full call stack available for inspection.

</details>

<details>
<summary>✅ Answer</summary>

```python
import pdb
import traceback


def fetch_user(users: dict, user_id: int) -> str:
    # Bug: no .get() — raises KeyError for missing IDs
    return users[user_id]["name"]


users_db = {1: {"name": "Alice"}, 2: {"name": "Bob"}}

try:
    name = fetch_user(users_db, 99)   # ← KeyError: 99
except Exception:
    print("=== Exception caught — launching post-mortem debugger ===")
    traceback.print_exc()
    pdb.post_mortem()
    # (Pdb) p user_id          → 99
    # (Pdb) p users            → {1: {...}, 2: {...}}
    # (Pdb) p list(users.keys()) → [1, 2]
    # (Pdb) q

# Alternatively — run from command line for automatic post-mortem:
# python -m pdb -c continue script.py
# pdb drops into post-mortem automatically on any unhandled exception.
```

**Why:** Post-mortem debugging is the tool for "it crashed and I want to look around." Unlike placing `breakpoint()` before the crash (which requires knowing where to put it), `pdb.post_mortem()` lands you inside the exact stack frame of the failure. The full call stack and all local variables are frozen and inspectable.

</details>

---

<a id="q21"></a>

### Q21 🟡 · traceback — Capture and log a formatted traceback string without re-raising

> 🛠️ **Solve locally:** [practice_local.py → Q21](./practice_local.py)



**Problem:** Write a function that catches an exception, captures the full traceback as a string using the `traceback` module, logs it at `ERROR` level, and returns a user-friendly message — without re-raising the exception.

<details>
<summary>💡 Hint</summary>

`traceback.format_exc()` returns the current exception's traceback as a string (same text as `traceback.print_exc()` but as a string instead of printing to stderr). Call it inside an `except` block.

</details>

<details>
<summary>✅ Answer</summary>

```python
import logging
import traceback

logging.basicConfig(level=logging.DEBUG, format="%(levelname)s | %(message)s")
logger = logging.getLogger(__name__)


def safe_parse_json(raw: str) -> dict | None:
    """Parse JSON, log full traceback on failure, return None instead of raising."""
    import json
    try:
        return json.loads(raw)
    except json.JSONDecodeError:
        # Capture as string — does NOT re-raise:
        tb_str = traceback.format_exc()
        logger.error("JSON parsing failed:\n%s", tb_str)
        return None


result = safe_parse_json('{"key": broken json}')
print("Result:", result)   # Result: None

# Logged output:
# ERROR | JSON parsing failed:
# Traceback (most recent call last):
#   File "practice_local.py", line 11, in safe_parse_json
#     return json.loads(raw)
# json.decoder.JSONDecodeError: Expecting value: line 1 column 9 (char 8)
```

**Why:** `traceback.format_exc()` lets you store or transmit the traceback text without affecting control flow. This is useful when you want to send the traceback to a monitoring system (Sentry, PagerDuty) as part of an alert payload, or when the calling code must receive a clean return value rather than an exception.

</details>

---

<a id="q22"></a>

### Q22 🟡 · warnings — Use warnings.warn() to emit a DeprecationWarning from a function

> 🛠️ **Solve locally:** [practice_local.py → Q22](./practice_local.py)



**Problem:** Write a function `old_api(data)` that is being deprecated. When called, it should emit a `DeprecationWarning` telling callers to use `new_api(data)` instead. The warning should point to the caller's line, not the line inside `old_api`.

<details>
<summary>💡 Hint</summary>

`warnings.warn(message, WarningClass, stacklevel=N)` where `stacklevel=2` makes the warning point one frame up — to the caller — instead of to the `warn()` call itself. This is standard practice for deprecation warnings in libraries.

</details>

<details>
<summary>✅ Answer</summary>

```python
import warnings


def new_api(data: list) -> list:
    return sorted(data)


def old_api(data: list) -> list:
    warnings.warn(
        "old_api() is deprecated and will be removed in v3.0. "
        "Use new_api() instead.",
        DeprecationWarning,
        stacklevel=2,   # ← points warning to the caller, not this line
    )
    return new_api(data)


# By default Python hides DeprecationWarning — show it explicitly:
warnings.simplefilter("always", DeprecationWarning)

result = old_api([3, 1, 2])   # ← warning points to THIS line
print(result)

# Output:
# practice_local.py:23: DeprecationWarning: old_api() is deprecated and will
# be removed in v3.0. Use new_api() instead.
# [1, 2, 3]

# In tests, treat warnings as errors to enforce migration:
# warnings.filterwarnings("error", category=DeprecationWarning)
```

**Why:** `stacklevel=2` is the critical detail. Without it, the warning always shows the file and line of the `warn()` call inside your library — useless to the developer trying to find which of their call sites to update. With `stacklevel=2`, the warning points directly at the caller's code.

</details>

---

<a id="q23"></a>

### Q23 🟠 · production logger — Build a create_logger(name, level, log_file) factory function

> 🛠️ **Solve locally:** [practice_local.py → Q23](./practice_local.py)



**Problem:** Write a `create_logger(name, level="INFO", log_file=None)` factory that returns a configured `Logger`. It should: use the standard production format, always add a `StreamHandler` (console), optionally add a `RotatingFileHandler` if `log_file` is given (10MB, 5 backups), and guard against adding duplicate handlers on repeated calls.

<details>
<summary>💡 Hint</summary>

Check `if logger.handlers:` before adding handlers — if the logger already has handlers, return it as-is. This prevents duplicate log lines when `create_logger` is called multiple times with the same name (e.g. in tests or module-level calls).

</details>

<details>
<summary>✅ Answer</summary>

```python
import logging
import logging.handlers
import sys
from typing import Optional


def create_logger(
    name: str,
    level: str = "INFO",
    log_file: Optional[str] = None,
) -> logging.Logger:
    """
    Factory: returns a configured named logger.

    Args:
        name:     Logger name (use __name__ in application modules).
        level:    Minimum log level string: DEBUG / INFO / WARNING / ERROR / CRITICAL.
        log_file: Optional path to a rotating log file.

    Returns:
        Configured logging.Logger instance.
    """
    logger = logging.getLogger(name)

    # Guard: don't add handlers if already configured (prevents duplicates):
    if logger.handlers:
        return logger

    logger.setLevel(getattr(logging, level.upper(), logging.INFO))
    logger.propagate = False

    fmt = logging.Formatter(
        fmt="%(asctime)s | %(levelname)-8s | %(name)s:%(lineno)d | %(message)s",
        datefmt="%Y-%m-%d %H:%M:%S",
    )

    # Console handler — always present:
    console = logging.StreamHandler(sys.stdout)
    console.setLevel(logging.DEBUG)
    console.setFormatter(fmt)
    logger.addHandler(console)

    # Rotating file handler — optional:
    if log_file:
        file_h = logging.handlers.RotatingFileHandler(
            filename=log_file,
            maxBytes=10 * 1024 * 1024,   # 10 MB
            backupCount=5,
            encoding="utf-8",
        )
        file_h.setLevel(logging.DEBUG)
        file_h.setFormatter(fmt)
        logger.addHandler(file_h)

    return logger


# --- Usage ---
log = create_logger("myapp.api", level="DEBUG", log_file="api.log")
log.info("API server started on port 8080")
log.debug("Request headers: %s", {"Content-Type": "application/json"})

# Calling again returns the same logger without adding more handlers:
log2 = create_logger("myapp.api")
assert log is log2
```

**Why:** A factory function is the right pattern for application logging setup. The duplicate-handler guard (`if logger.handlers`) is essential because Python's logger registry caches loggers by name — calling `getLogger("myapp.api")` twice returns the same object. Without the guard, every import of your module would add another handler and every message would appear twice (or more).

</details>

---

<a id="q24"></a>

### Q24 🟠 · timing decorator — Write a @log_timing decorator that logs function duration

> 🛠️ **Solve locally:** [practice_local.py → Q24](./practice_local.py)



**Problem:** Write a `@log_timing` decorator that logs the function name, arguments (truncated to 80 chars), return value type, and elapsed time in milliseconds. Use `logging.INFO` for normal runs and `logging.WARNING` if execution exceeds a configurable threshold (default 500ms).

<details>
<summary>💡 Hint</summary>

Use `time.perf_counter()` for high-resolution timing. Use `functools.wraps(func)` to preserve the wrapped function's metadata. Accept an optional `threshold_ms` param by making `log_timing` a decorator factory.

</details>

<details>
<summary>✅ Answer</summary>

```python
import functools
import logging
import time
from typing import Any, Callable

logging.basicConfig(level=logging.DEBUG, format="%(levelname)s | %(name)s | %(message)s")
logger = logging.getLogger("timing")


def log_timing(threshold_ms: float = 500.0):
    """
    Decorator factory: logs function name, args, return type, and elapsed time.
    Logs at WARNING if execution exceeds threshold_ms.

    Usage:
        @log_timing()                    # default 500ms threshold
        @log_timing(threshold_ms=100.0)  # custom threshold
    """
    def decorator(func: Callable) -> Callable:
        @functools.wraps(func)
        def wrapper(*args, **kwargs) -> Any:
            # Truncate args repr to avoid flooding logs:
            args_repr = repr(args)[:80] + ("..." if len(repr(args)) > 80 else "")

            start = time.perf_counter()
            try:
                result = func(*args, **kwargs)
                elapsed_ms = (time.perf_counter() - start) * 1000
                level = logging.WARNING if elapsed_ms > threshold_ms else logging.INFO
                logger.log(
                    level,
                    "%s(%s) → %s in %.2fms%s",
                    func.__name__,
                    args_repr,
                    type(result).__name__,
                    elapsed_ms,
                    " [SLOW]" if elapsed_ms > threshold_ms else "",
                )
                return result
            except Exception as exc:
                elapsed_ms = (time.perf_counter() - start) * 1000
                logger.error(
                    "%s(%s) raised %s after %.2fms",
                    func.__name__, args_repr, type(exc).__name__, elapsed_ms,
                )
                raise

        return wrapper
    return decorator


# --- Usage ---
@log_timing(threshold_ms=10.0)
def fetch_records(table: str, limit: int) -> list:
    time.sleep(0.05)   # simulate slow query
    return [{"id": i} for i in range(limit)]


@log_timing()
def add(a: int, b: int) -> int:
    return a + b


records = fetch_records("orders", 5)
# WARNING | timing | fetch_records(('orders', 5)) → list in 50.12ms [SLOW]

total = add(3, 4)
# INFO | timing | add((3, 4)) → int in 0.01ms
```

**Why:** Timing decorators give you observability at the function level without modifying business logic. The `WARNING` threshold turns slow calls into immediately visible alerts in your log stream — you can grep for `[SLOW]` to find performance regressions without any external profiling tooling.

</details>

---

<a id="q25"></a>

### Q25 🟡 · caplog in tests — Explain how pytest's caplog fixture captures log output

> 🛠️ **Solve locally:** [practice_local.py → Q25](./practice_local.py)



**Problem:** Write a pytest test for a function that logs a `WARNING` message. Use the `caplog` fixture to assert that the warning was emitted with the correct message and level. Show how to set the capture level.

<details>
<summary>💡 Hint</summary>

`caplog` is a built-in pytest fixture — no import needed. Set `caplog.set_level(logging.WARNING)` inside the test to control which records are captured. Access captured records via `caplog.records` (list of `LogRecord`) or `caplog.text` (formatted string).

</details>

<details>
<summary>✅ Answer</summary>

```python
# In your application module (e.g. order_service.py):
import logging

logger = logging.getLogger(__name__)


def process_order(order_id: int, amount: float) -> str:
    if amount <= 0:
        logger.warning("Invalid amount %.2f for order %d", amount, order_id)
        return "rejected"
    logger.info("Order %d processed: $%.2f", order_id, amount)
    return "accepted"


# ── In tests/test_order_service.py ──────────────────────────────────────
import logging
import pytest


def test_process_order_logs_warning_for_invalid_amount(caplog):
    # Set the minimum level caplog will capture:
    with caplog.at_level(logging.WARNING):
        result = process_order(4892, -10.0)

    # Assert the return value:
    assert result == "rejected"

    # Assert a WARNING record was emitted:
    assert len(caplog.records) == 1
    record = caplog.records[0]
    assert record.levelno == logging.WARNING
    assert "Invalid amount" in record.message

    # Alternative: check the rendered text string:
    assert "Invalid amount" in caplog.text


def test_process_order_info_not_captured_at_warning_level(caplog):
    with caplog.at_level(logging.WARNING):
        result = process_order(4892, 100.0)   # valid — emits INFO

    assert result == "accepted"
    assert caplog.records == []   # INFO is below WARNING threshold — not captured


# Run with: pytest tests/test_order_service.py -v
```

**Why:** `caplog` lets you test logging behavior as a first-class concern. This matters because logs are part of your service's contract — on-call engineers rely on specific messages to diagnose incidents. Testing that the right message fires at the right level prevents regressions just as unit tests prevent logic regressions.

</details>

---

<a id="q26"></a>

### Q26 🟠 · QueueHandler — Explain async logging with QueueHandler to avoid blocking

> 🛠️ **Solve locally:** [practice_local.py → Q26](./practice_local.py)



**Problem:** Set up a non-blocking logging pipeline using `QueueHandler` and `QueueListener`. The main logger should enqueue records instantly, while a background thread drains the queue and writes to a file. Demonstrate that the main thread is never blocked by I/O.

<details>
<summary>💡 Hint</summary>

`QueueHandler` puts records into a `queue.Queue`. `QueueListener` runs in a background thread and passes records to the real handlers. Call `listener.start()` at app startup and `listener.stop()` at shutdown.

</details>

<details>
<summary>✅ Answer</summary>

```python
import logging
import logging.handlers
import queue
import time

# ── Step 1: Create the real (slow) handler — file I/O or HTTP ───────────
file_handler = logging.FileHandler("async_app.log", encoding="utf-8")
file_handler.setFormatter(
    logging.Formatter("%(asctime)s | %(levelname)s | %(message)s")
)

# ── Step 2: Create the queue and wire up QueueHandler + QueueListener ────
log_queue: queue.Queue = queue.Queue(maxsize=10_000)

queue_handler = logging.handlers.QueueHandler(log_queue)
# QueueListener runs the real handler in a background daemon thread:
listener = logging.handlers.QueueListener(
    log_queue,
    file_handler,
    respect_handler_level=True,
)

# ── Step 3: Attach only the QueueHandler to the application logger ────────
logger = logging.getLogger("async_app")
logger.setLevel(logging.DEBUG)
logger.addHandler(queue_handler)
logger.propagate = False

# ── Step 4: Start listener at application startup ─────────────────────────
listener.start()

# ── Main thread — non-blocking log calls ─────────────────────────────────
start = time.perf_counter()
for i in range(1000):
    logger.info("Request %d processed", i)   # instant: just puts on queue
elapsed = time.perf_counter() - start
print(f"1000 log calls took {elapsed*1000:.2f}ms (queue puts, no file I/O)")

# ── Shutdown — flush queue and stop background thread ─────────────────────
listener.stop()
print("Listener stopped — all records flushed to async_app.log")

# How it works:
# Main thread:      logger.info() → QueueHandler.emit() → queue.put_nowait()  [microseconds]
# Background thread: QueueListener.dequeue() → FileHandler.emit() → disk write [milliseconds]
# Result: file I/O latency is completely hidden from the main thread.
```

**Why:** Every `FileHandler.emit()` call involves a syscall that can take 1-10ms. At high request rates (1000+ req/s), synchronous logging adds hundreds of milliseconds of latency per second. `QueueHandler` decouples the logging call (a fast queue put) from the actual I/O (done in a background thread). This is the standard pattern for production services that need both reliability and low latency.

</details>

---

<a id="q27"></a>

### Q27 🟠 · Capstone — Build a request logging middleware

> 🛠️ **Solve locally:** [practice_local.py → Q27](./practice_local.py)



**Problem:** Build a `RequestLoggingMiddleware` class that wraps a simple WSGI-like callable. For every request, it must log: HTTP method, path, response status code, elapsed time (ms), and a request ID (from the `X-Request-ID` header or auto-generated). Log at `INFO` on success (2xx/3xx) and `WARNING` on client/server errors (4xx/5xx).

<details>
<summary>💡 Hint</summary>

Simulate a WSGI app with a callable that takes `(environ, start_response)`. Track the status code by wrapping `start_response`. Use `uuid.uuid4()` to generate request IDs and `time.perf_counter()` for timing.

</details>

<details>
<summary>✅ Answer</summary>

```python
import logging
import time
import uuid
from typing import Callable, Iterable

logging.basicConfig(
    level=logging.DEBUG,
    format="%(asctime)s | %(levelname)-8s | %(message)s",
    datefmt="%H:%M:%S",
)
logger = logging.getLogger("middleware.request")


class RequestLoggingMiddleware:
    """
    WSGI middleware: logs method, path, status, duration, and request_id
    for every HTTP request.
    """

    def __init__(self, app: Callable) -> None:
        self.app = app

    def __call__(self, environ: dict, start_response: Callable) -> Iterable:
        # --- Extract or generate request ID ---
        request_id = (
            environ.get("HTTP_X_REQUEST_ID")
            or str(uuid.uuid4())[:8]
        )
        method = environ.get("REQUEST_METHOD", "GET")
        path   = environ.get("PATH_INFO", "/")

        # --- Capture status code by wrapping start_response ---
        status_holder: list[str] = []

        def capturing_start_response(status: str, headers: list, exc_info=None):
            status_holder.append(status)
            return start_response(status, headers, exc_info)

        # --- Time the actual app call ---
        start = time.perf_counter()
        try:
            result = self.app(environ, capturing_start_response)
        except Exception as exc:
            elapsed_ms = (time.perf_counter() - start) * 1000
            logger.error(
                "[%s] %s %s → 500 EXCEPTION in %.2fms — %s",
                request_id, method, path, elapsed_ms, exc,
            )
            raise

        elapsed_ms = (time.perf_counter() - start) * 1000
        status_str = status_holder[0] if status_holder else "???"
        status_code = int(status_str.split()[0]) if status_str[0].isdigit() else 0

        # --- Choose log level by status class ---
        level = logging.INFO if status_code < 400 else logging.WARNING

        logger.log(
            level,
            "[%s] %s %s → %s in %.2fms",
            request_id, method, path, status_str, elapsed_ms,
        )

        return result


# ── Simple WSGI app for testing ─────────────────────────────────────────
def simple_app(environ, start_response):
    path = environ.get("PATH_INFO", "/")
    if path == "/checkout":
        start_response("200 OK", [("Content-Type", "text/plain")])
        return [b"Order placed"]
    elif path == "/missing":
        start_response("404 Not Found", [("Content-Type", "text/plain")])
        return [b"Not found"]
    else:
        start_response("500 Internal Server Error", [("Content-Type", "text/plain")])
        return [b"Error"]


# ── Wire up and simulate requests ───────────────────────────────────────
app = RequestLoggingMiddleware(simple_app)

def simulate(method, path, request_id=None):
    environ = {
        "REQUEST_METHOD": method,
        "PATH_INFO": path,
        "HTTP_X_REQUEST_ID": request_id,
    }
    headers_sent = []
    def mock_start_response(status, headers, exc_info=None):
        headers_sent.append(status)
    list(app(environ, mock_start_response))

simulate("GET",  "/checkout", request_id="req-001")
simulate("POST", "/checkout")
simulate("GET",  "/missing")
simulate("GET",  "/broken")

# 14:30:00 | INFO     | [req-001] GET /checkout → 200 OK in 0.05ms
# 14:30:00 | INFO     | [a1b2c3d4] POST /checkout → 200 OK in 0.03ms
# 14:30:00 | WARNING  | [e5f6a7b8] GET /missing → 404 Not Found in 0.02ms
# 14:30:00 | WARNING  | [c9d0e1f2] GET /broken → 500 Internal Server Error in 0.04ms
```

**Why:** Request logging middleware is the most important logging pattern in any web service. Centralising it here means every request gets the same structured log entry — method, path, status, duration, and trace ID — without any individual handler needing to remember to log. The level split (INFO for 2xx/3xx, WARNING for 4xx/5xx) means error traffic is immediately visible in dashboards without drowning in normal traffic noise.

</details>

---

## 🔁 Navigation

| | |
|---|---|
| ⬅️ Back to Module | [09_logging_debugging/theory.md](./theory.md) |
| 📖 Theory | [theory.md](./theory.md) |
| 🐛 pdb Deep Dive | [01_pdb_debugging/practice.md](./01_pdb_debugging/practice.md) |
| 📊 Profiling Deep Dive | [02_profiling_advanced/practice.md](./02_profiling_advanced/practice.md) |
| ➡️ Next Module | [10_decorators →](../10_decorators/practice.md) |

---

**Related:** [pdb →](./01_pdb_debugging/theory.md) · [Profiling & Advanced →](./02_profiling_advanced/theory.md)
