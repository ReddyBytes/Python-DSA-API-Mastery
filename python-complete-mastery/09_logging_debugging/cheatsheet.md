# ⚡ Logging & Debugging — Cheatsheet

> Quick reference: levels, setup, handlers, formatting, structured logging, pdb, performance, gotchas.

---

## 📊 Log Levels

```
Level     Numeric   When to use
─────────────────────────────────────────────────────────────────────
DEBUG     10        Variable values, cache hits, function entry/exit. Dev only.
INFO      20        Normal operations. "User logged in", "Server started".
WARNING   30        Non-fatal unexpected events. Retry attempts, slow responses.
ERROR     40        Operation failed. DB lost, file missing, payment failed.
CRITICAL  50        System cannot function. Immediate alert required.

Default level: WARNING — DEBUG and INFO are silent unless configured.
```

---

## 🔧 Basic Setup

```python
import logging

# Quickstart (scripts / notebooks):
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s | %(levelname)-8s | %(name)s | %(message)s",
    datefmt="%Y-%m-%d %H:%M:%S",
    encoding="utf-8",
)

# Named logger (always use __name__ in libraries/modules):
logger = logging.getLogger(__name__)

# Log calls:
logger.debug("Detail: %s", value)
logger.info("Started processing order %s", order_id)
logger.warning("Retry attempt %d of %d", attempt, max_retries)
logger.error("Payment failed for order %s", order_id)
logger.critical("Database unreachable — shutting down")

# Log exception with full traceback (inside except blocks):
try:
    risky_call()
except Exception:
    logger.exception("Unexpected failure in risky_call")   # ← use this!
    # equivalent: logger.error("msg", exc_info=True)
```

---

## 🏗️ Logger → Handler → Formatter

```
Logger   decides IF to emit (checks level, then passes to handlers)
Handler  decides WHERE to send (console, file, network, ...)
         Each handler has its own level filter
Formatter decides WHAT the output looks like

FLOW:
  logger.error("msg")
    ↓ Logger: ERROR >= logger.level? YES
    ↓ For each handler attached:
        Handler: ERROR >= handler.level? YES
        Formatter: apply format string
        Handler: emit to destination
```

```python
import logging

logger = logging.getLogger("myapp")
logger.setLevel(logging.DEBUG)          # Logger gate — let everything through

# Console handler (WARNING and above):
console = logging.StreamHandler()
console.setLevel(logging.WARNING)
console.setFormatter(logging.Formatter(
    "%(asctime)s | %(levelname)-8s | %(message)s"
))

# File handler (DEBUG and above):
file_h = logging.FileHandler("app.log", encoding="utf-8")
file_h.setLevel(logging.DEBUG)
file_h.setFormatter(logging.Formatter(
    "%(asctime)s | %(levelname)-8s | %(name)s:%(lineno)d | %(message)s"
))

logger.addHandler(console)
logger.addHandler(file_h)
logger.propagate = False    # don't send to root logger
```

---

## 📋 Format Codes Reference

```
%(asctime)s        2025-03-08 14:30:00,123
%(levelname)s      DEBUG / INFO / WARNING / ERROR / CRITICAL
%(levelname)-8s    left-aligned, 8 chars wide
%(name)s           logger name (usually module name from __name__)
%(filename)s       source file: payment.py
%(module)s         module name: payment
%(funcName)s       function name
%(lineno)d         line number: 47
%(thread)d         thread ID
%(process)d        process ID
%(message)s        the formatted log message

Custom fields (via Filter or extra=):
%(correlation_id)s  (if added via Filter)
%(user_id)s         (if added via extra={...})
```

---

## 🔄 Log Rotation

```python
from logging.handlers import RotatingFileHandler, TimedRotatingFileHandler

# By size (recommended for most services):
handler = RotatingFileHandler(
    "app.log",
    maxBytes=10 * 1024 * 1024,   # 10 MB per file
    backupCount=5,               # keep app.log.1 … app.log.5
    encoding="utf-8",
)

# By time (recommended for daily archiving):
handler = TimedRotatingFileHandler(
    "app.log",
    when="midnight",    # 'S'=second 'M'=minute 'H'=hour 'D'=day 'midnight'
    backupCount=30,     # keep 30 days
    utc=True,
    encoding="utf-8",
)
```

---

## 🌳 Logger Hierarchy

```
root logger  (logging.getLogger(""))
 ├── myapp   (logging.getLogger("myapp"))
 │    ├── myapp.payment   (logging.getLogger("myapp.payment"))
 │    └── myapp.auth      (logging.getLogger("myapp.auth"))
 └── requests             (third-party library)

Propagation (default True):
  myapp.payment → myapp → root   ← log goes UP the tree unless stopped
  set propagate=False to stop propagation
```

---

## 📦 Exception Logging

```python
# ✅ CORRECT — full traceback automatically:
try:
    process()
except Exception:
    logger.exception("Process failed")

# ✅ Equivalent (manual):
except Exception:
    logger.error("Process failed", exc_info=True)

# ❌ WRONG — loses traceback entirely:
except Exception as e:
    logger.error(f"Process failed: {e}")    # no traceback!
    logger.error(str(e))                    # no traceback!

# Re-raise after logging:
except Exception:
    logger.exception("Payment failed for order %s", order_id)
    raise   # ← re-raise original, not "raise e"
```

---

## 📊 Structured / JSON Logging

```python
import json, logging

class JSONFormatter(logging.Formatter):
    def format(self, record):
        return json.dumps({
            "ts":      self.formatTime(record, "%Y-%m-%dT%H:%M:%SZ"),
            "level":   record.levelname,
            "logger":  record.name,
            "msg":     record.getMessage(),
            "file":    f"{record.filename}:{record.lineno}",
            **({"exc": self.formatException(record.exc_info)}
               if record.exc_info else {}),
        })

handler = logging.StreamHandler()
handler.setFormatter(JSONFormatter())

# Or use structlog (pip install structlog):
import structlog
log = structlog.get_logger()
log.info("payment_processed", order_id=4892, amount=99.99)
# → {"event": "payment_processed", "order_id": 4892, "amount": 99.99, ...}
```

---

## 🔗 Correlation IDs

```python
from contextvars import ContextVar
import uuid, logging

correlation_id: ContextVar[str] = ContextVar("correlation_id", default="")

class CorrelationFilter(logging.Filter):
    def filter(self, record):
        record.correlation_id = correlation_id.get() or "no-id"
        return True

# Add to handler:
handler.addFilter(CorrelationFilter())
handler.setFormatter(logging.Formatter(
    "%(asctime)s [%(correlation_id)s] %(levelname)s | %(message)s"
))

# Middleware — set once per request:
def middleware(request, next_handler):
    cid = request.headers.get("X-Correlation-ID") or str(uuid.uuid4())
    token = correlation_id.set(cid)
    try:
        return next_handler(request)
    finally:
        correlation_id.reset(token)
```

---

## ⚡ Performance Rules

```python
# ❌ BAD — f-string ALWAYS evaluated, even if DEBUG is disabled:
logger.debug(f"Data: {serialize(large_obj)}")

# ✅ GOOD — % style: only formatted IF the level is enabled:
logger.debug("Data: %s", serialize(large_obj))

# ✅ BEST — skip expensive work entirely if level disabled:
if logger.isEnabledFor(logging.DEBUG):
    report = compute_expensive_debug_report(data)
    logger.debug("Report: %s", report)

# Rule: ALWAYS use % style in logger calls.
#       NEVER use f-strings, + concatenation, or str.format() in logger calls.
```

---

## 🔒 Security — PII Redaction

```python
SENSITIVE = {"password", "token", "secret", "card", "cvv", "ssn"}

class RedactionFilter(logging.Filter):
    def filter(self, record):
        msg = record.getMessage()
        for field in SENSITIVE:
            import re
            msg = re.sub(
                rf'(?i)({field}["\']?\s*[:=]\s*["\']?)([^\s"\'&,]+)',
                r'\1[REDACTED]',
                msg
            )
        record.msg = msg
        record.args = ()
        return True

# ❌ NEVER LOG:
logger.info("Login: user=%s password=%s", username, password)
logger.debug("JWT token: %s", token)

# ✅ LOG IDs AND EVENTS, NOT VALUES:
logger.info("User %s authenticated", user_id)
logger.debug("API call authenticated, key_id=%s", key_id[:8] + "***")
```

---

## 🏭 Production dictConfig

```python
import logging.config

logging.config.dictConfig({
    "version": 1,
    "disable_existing_loggers": False,   # ← CRITICAL: never True!
    "formatters": {
        "json": {"()": "myapp.JSONFormatter"},
        "console": {
            "format": "%(asctime)s | %(levelname)-8s | %(name)s | %(message)s"
        },
    },
    "handlers": {
        "console": {
            "class": "logging.StreamHandler",
            "level": "WARNING",
            "formatter": "console",
        },
        "file": {
            "class": "logging.handlers.RotatingFileHandler",
            "filename": "/var/log/myapp/app.log",
            "maxBytes": 10_485_760,
            "backupCount": 5,
            "encoding": "utf-8",
            "level": "DEBUG",
            "formatter": "json",
        },
    },
    "loggers": {
        "myapp": {"level": "DEBUG", "handlers": ["console", "file"], "propagate": False},
    },
    "root": {"level": "WARNING", "handlers": ["console"]},
})
```

---

## 🐛 pdb Quick Reference

```python
# Trigger:
breakpoint()                     # Python 3.7+ (preferred)
import pdb; pdb.set_trace()      # explicit

# Post-mortem (debug after crash):
import pdb
try:
    run_thing()
except Exception:
    pdb.post_mortem()
```

```
(Pdb) NAVIGATION
  n         next line (step OVER calls)
  s         step INTO function call
  r         run until current function RETURNS
  c         continue until next breakpoint
  q         quit debugger

(Pdb) INSPECTION
  l         list source around current line
  l 40,60   list lines 40–60
  p expr    print expression value
  pp expr   pretty-print expression
  pp vars() print all local variables
  whatis x  print type of x

(Pdb) STACK
  w         show full call stack (where)
  u         move UP the call stack
  d         move DOWN the call stack
  bt        backtrace (alias for w)

(Pdb) BREAKPOINTS
  b 47           set breakpoint at line 47
  b func         set breakpoint at function entry
  b 47, x>10     conditional breakpoint
  cl             clear all breakpoints
  disable 1      disable breakpoint #1

(Pdb) EXECUTION
  j 55      jump to line 55 (skip code)
  unt 60    run until line 60 (like n but skips loops)
  ret       run until function returns
```

---

## 🔴 Gotchas

```python
# 1 — basicConfig is a no-op if root already has handlers:
import requests   # may call basicConfig internally!
logging.basicConfig(level=logging.DEBUG)   # DOES NOTHING
# FIX: use getLogger(__name__) + manual addHandler()

# 2 — f-string evaluated even when level disabled:
logger.debug(f"User: {serialize_user(user)}")   # ALWAYS runs serialize_user!
logger.debug("User: %s", serialize_user(user))  # only if DEBUG enabled

# 3 — Double logging (propagate + explicit root):
# If root has handler AND child has handler, logs appear TWICE
logger.propagate = False   # stop child from also sending to root

# 4 — exception() outside except block:
logger.exception("msg")   # outside except → logs NoneType as traceback
# Only call logger.exception() INSIDE except blocks

# 5 — disable_existing_loggers: True kills library loggers:
{"disable_existing_loggers": True}   # silences ALL existing loggers!
{"disable_existing_loggers": False}  # ← correct

# 6 — Bare except silences exceptions before they can be logged:
try:
    risky()
except:          # catches SystemExit, KeyboardInterrupt too!
    pass         # ← exception swallowed, no log, no re-raise

# Correct:
except Exception:
    logger.exception("risky() failed")
    raise
```

---

## 🔥 Rapid-Fire Revision

```
Q: Numeric values of log levels?
A: DEBUG=10, INFO=20, WARNING=30, ERROR=40, CRITICAL=50

Q: logging.exception() vs logging.error()?
A: exception() = error() + exc_info=True (captures traceback automatically)
   Only use exception() INSIDE except blocks.

Q: What is propagate?
A: If True (default), log records also sent to parent logger's handlers.
   Set False to stop child from sending to root logger.

Q: What is NullHandler?
A: No-op handler. Library authors add it so their logs go nowhere
   unless the consuming application configures them.
   logging.getLogger("mylib").addHandler(logging.NullHandler())

Q: disable_existing_loggers=False?
A: Keeps loggers from imported libraries alive after dictConfig runs.
   True is the dangerous default — silences all previously created loggers.

Q: Why % style over f-strings in logger calls?
A: % style is lazy — string only built if message will actually be emitted.
   f-strings always build the string before the call, even if DEBUG is off.

Q: How to prevent double logging?
A: Set logger.propagate = False on the child logger,
   OR configure only the root logger (not both root and child).
```

---

## 🔁 Navigation

| | |
|---|---|
| 📖 Theory | [theory.md](./theory.md) |
| 🎯 Interview | [interview.md](./interview.md) |
| 🐛 PDB Guide | [pdb_guide.md](./pdb_guide.md) |
| ➡️ Next | [10 — Decorators](../10_decorators/theory.md) |
