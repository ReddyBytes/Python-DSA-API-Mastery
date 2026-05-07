# 🎯 Logging & Debugging — Interview Questions

> *"Logging questions reveal whether you've worked on real production systems.*
> *Debugging questions reveal how you think when things break."*

---

## 📊 Question Map

```
LEVEL 1 — Junior (0–2 years)
  • print vs logging
  • Log levels and when to use each
  • basicConfig setup
  • logging.exception()

LEVEL 2 — Mid-Level (2–5 years)
  • Logger/Handler/Formatter architecture
  • Log rotation
  • Structured logging
  • Performance considerations
  • pdb debugging

LEVEL 3 — Senior (5+ years)
  • Correlation IDs / distributed tracing
  • Observability (logs + metrics + traces)
  • dictConfig / production config
  • Security: PII in logs
  • Incident investigation approach
```

---

## 🟢 Level 1 — Junior Questions

---

**Q1: Why is `logging` better than `print()` for production code?**

<details>
<summary>💡 Show Answer</summary>

**Weak answer:** "Logging is more professional."

**Strong answer:**

> `print()` always outputs to stdout with no context. `logging` gives you:
> - **Levels** — filter out DEBUG noise in production with one config change
> - **Timestamps** — know exactly when each event happened
> - **Context** — module name, line number, process ID built-in
> - **Multiple destinations** — console, file, remote server simultaneously
> - **Deferred formatting** — `%s` style is only evaluated if the level is enabled

```python
# print in production:
print(f"Error: {e}")   # no timestamp, no level, goes to stdout, mixed with all output

# logging in production:
logger.error("Payment failed for order %s: %s", order_id, e)
# 2025-03-08 14:30:00 | ERROR | myapp.payment:47 | Payment failed for order 4892: timeout
```

</details>

<br>

**Q2: What are the 5 logging levels? What does each mean?**

<details>
<summary>💡 Show Answer</summary>

**Strong answer:**

```
DEBUG    (10)  Detailed diagnostic. Development only. Variable values, cache hits/misses.
INFO     (20)  Normal operation events. "User logged in", "Order placed", "Server started".
WARNING  (30)  Unexpected but non-fatal. Retry attempts, deprecated usage, slow responses.
ERROR    (40)  An operation failed. DB connection lost, payment failed, file not found.
CRITICAL (50)  System cannot function. Immediate alert required. Service down.
```

> The default level is WARNING — DEBUG and INFO are **silent by default**.
> In production, use INFO (always-on) or WARNING (alert-only).
> Never run DEBUG in high-traffic production — the I/O volume is massive.

</details>

<br>

**Q3: How do you log exceptions with the full traceback?**

<details>
<summary>💡 Show Answer</summary>

**Weak answer:** `logger.error(str(e))`

**Strong answer:**

```python
# ✅ logging.exception() — use INSIDE except blocks:
try:
    process_payment(order_id)
except Exception:
    logger.exception("Payment failed for order %s", order_id)
    # Automatically logs: ERROR level + message + FULL TRACEBACK

# ✅ Equivalent:
except Exception:
    logger.error("Payment failed", exc_info=True)   # same result

# ❌ WRONG — loses the traceback:
except Exception as e:
    logger.error(f"Payment failed: {e}")  # only the error message, no traceback!
    logger.error(str(e))                  # same problem
```

</details>

<br>

**Q4: What is `basicConfig()` and what are its limitations?**

<details>
<summary>💡 Show Answer</summary>

**Strong answer:**

> `basicConfig()` is a quick one-line setup for the root logger. It configures level, format, and output destination.

```python
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s | %(levelname)s | %(message)s",
    filename="app.log",
    encoding="utf-8",
)
```

> **Limitations:**
> 1. Only configures the **root logger** — not named loggers
> 2. Only works **once** — subsequent calls are no-ops if root already has handlers
> 3. If a third-party library called `basicConfig()` first, your call is silently ignored
> 4. No support for multiple handlers, rotation, or per-module levels
>
> For production: use `getLogger(__name__)` + manual `addHandler()` or `dictConfig()`.

</details>


## 🔵 Level 2 — Mid-Level Questions

---

**Q: What is loguru and why use it over standard logging?**

<details>
<summary>💡 Show Answer</summary>

**Weak answer:** "It's a third-party logging library."

**Strong answer:**

> `loguru` replaces the Logger/Handler/Formatter trifecta with a single `logger` object that is ready to use with zero configuration. It adds rotation, structured output, colorized console, and async support out of the box.

```python
from loguru import logger

# Zero setup needed — works immediately:
logger.info("Server started on port {port}", port=8080)

# File rotation in one line (no RotatingFileHandler boilerplate):
logger.add("app.log", rotation="10 MB", retention="30 days", level="INFO")

# Bind context to all subsequent log calls:
request_logger = logger.bind(request_id="abc-123", user_id=42)
request_logger.info("Request received")
# → "Request received" | request_id=abc-123 | user_id=42

# Exception tracing with full variable values (not just message):
logger.opt(exception=True).error("Payment failed for order {order_id}", order_id=4892)
```

> Use loguru for new services or scripts where the standard library's setup overhead isn't justified. For large production apps with existing logging infrastructure, stick with the standard library — loguru requires a shim to integrate with third-party libraries that use `logging`.

</details>

<br>

**Q5: Explain the Logger → Handler → Formatter architecture.**

<details>
<summary>💡 Show Answer</summary>

**Strong answer:**

```
Logger   = decides IF to emit (based on level). Created with getLogger(__name__).
Handler  = decides WHERE to send (console, file, HTTP endpoint, email...).
           Multiple handlers can be attached to one logger.
Formatter= decides WHAT the output looks like (timestamp, level, message format).

FLOW:
  logger.error("Payment failed")
    → Logger checks: is ERROR >= my level? Yes
    → Logger passes to each Handler
      → Handler checks: is ERROR >= my level? Yes
        → Handler applies Formatter
          → Handler emits to destination
```

```python
import logging

logger = logging.getLogger("myapp")
logger.setLevel(logging.DEBUG)          # Logger level

handler = logging.StreamHandler()
handler.setLevel(logging.WARNING)       # Handler level (can differ from logger!)
handler.setFormatter(logging.Formatter(
    "%(asctime)s | %(levelname)s | %(message)s"
))

logger.addHandler(handler)
# Only WARNING and above actually reaches the console (handler filters below WARNING)
```

</details>

<br>

**Q6: What is log rotation and why is it critical?**

<details>
<summary>💡 Show Answer</summary>

**Strong answer:**

> Without rotation, log files grow forever and eventually fill the disk, crashing the server. Log rotation automatically limits file size and keeps a configurable number of backup files.

```python
from logging.handlers import RotatingFileHandler, TimedRotatingFileHandler

# By size:
handler = RotatingFileHandler(
    "app.log",
    maxBytes=10 * 1024 * 1024,   # 10MB per file
    backupCount=5,               # app.log.1 ... app.log.5
)

# By time:
handler = TimedRotatingFileHandler(
    "app.log",
    when="midnight",    # rotate daily at midnight
    backupCount=30,     # keep 30 days
    utc=True,
)
```

> In production, combine local rotation with a **log shipper** (Fluentd, Filebeat, CloudWatch agent) that sends logs to a centralized system. Don't rely on local files alone in distributed systems.

</details>

<br>

**Q7: What is structured logging and when would you use it?**

<details>
<summary>💡 Show Answer</summary>

**Weak answer:** "Logging in JSON format."

**Strong answer:**

> Structured logging produces machine-readable records (JSON) instead of free-form text. This makes logs directly searchable and filterable in tools like Elasticsearch, Splunk, Datadog, and CloudWatch.

```python
# Plain text log (hard to filter):
# 2025-03-08 14:30:00 ERROR Payment failed for order 4892 amount=499.00

# Structured log (searchable by any field):
{
  "timestamp": "2025-03-08T14:30:00Z",
  "level": "ERROR",
  "service": "payment-service",
  "event": "payment_failed",
  "order_id": 4892,
  "amount": 499.00,
  "error": "ConnectionTimeout",
  "user_id": 1023
}
# Query: level=ERROR AND order_id=4892 → instant result
```

> Use structured logging for any system that needs to be monitored, alerted on, or has multiple services.

</details>

<br>

**Q8: What is the performance impact of logging? How do you mitigate it?**

<details>
<summary>💡 Show Answer</summary>

**Strong answer:**

> Logging involves string formatting, I/O operations, and potentially network calls — all expensive in hot paths.

```python
# ❌ BAD: f-string evaluated EVERY time, even if DEBUG is disabled:
logger.debug(f"Processing {len(large_list)} items: {large_list}")

# ✅ GOOD: % style deferred — only formatted IF the level is enabled:
logger.debug("Processing %d items: %s", len(large_list), large_list)

# ✅ BEST for expensive operations:
if logger.isEnabledFor(logging.DEBUG):
    debug_info = compute_expensive_debug_repr(large_list)
    logger.debug("Processing: %s", debug_info)

# Rule: use % style in ALL logger.XXX() calls, not f-strings or + concatenation.
```

</details>

<br>

**Q9: How would you use pdb to debug a production issue locally?**

<details>
<summary>💡 Show Answer</summary>

**Strong answer:**

```python
# 1. Add breakpoint at suspicious location:
def process_payment(order_id, amount):
    breakpoint()   # execution pauses here
    ...

# 2. Key pdb commands in the debugger:
# (Pdb) l           ← show current code context
# (Pdb) p order_id  ← print variable value
# (Pdb) pp vars()   ← pretty-print all local variables
# (Pdb) n           ← next line (step over)
# (Pdb) s           ← step into function call
# (Pdb) w           ← show call stack
# (Pdb) u           ← move up the call stack
# (Pdb) b 47        ← set breakpoint at line 47
# (Pdb) c           ← continue until next breakpoint
# (Pdb) q           ← quit debugger

# 3. Post-mortem — debug after crash:
import pdb
try:
    run_the_thing()
except Exception:
    pdb.post_mortem()   # drops into debugger at the crash frame
```

</details>

<br>

**Q10: What logging data should you NEVER include? Why?**

<details>
<summary>💡 Show Answer</summary>

**Strong answer:**

> Logs are often stored in centralized systems, archived, and accessible to ops teams. Including sensitive data violates:
> - **Security**: token leakage enables account takeover
> - **Compliance**: GDPR, PCI-DSS, HIPAA require PII protection

```python
# ❌ NEVER LOG:
logger.info("Login: user=%s password=%s", username, password)
logger.debug("JWT: %s", token)
logger.info("Card: %s CVV: %s", card_number, cvv)
logger.info("Patient: %s diagnosis=%s", name, medical_data)

# ✅ LOG IDENTIFIERS AND EVENTS, NOT VALUES:
logger.info("User %s authenticated", user_id)          # ID not email/password
logger.info("Payment processed, ref=%s", payment_ref)  # reference not card
logger.debug("API call authenticated, key_id=%s", key_id[:8] + "***")
```

</details>

<br>

**Q: How do you profile a Python script to find performance bottlenecks?**

<details>
<summary>💡 Show Answer</summary>

**Weak answer:** "I add print statements with timestamps."

**Strong answer:**

> The workflow is: use `cProfile` to find which functions take the most time, then use `pstats` to sort and filter the results, then use `line_profiler` to drill into the specific lines inside the hotspot function.

```python
# Step 1 — cProfile: find slow functions
import cProfile
cProfile.run('my_function()', filename='output.prof', sort='cumulative')

# Step 2 — pstats: readable output
import pstats
p = pstats.Stats('output.prof')
p.sort_stats('cumulative').print_stats(10)   # top 10 by cumulative time
# Output shows: ncalls, tottime (self), cumtime (including callees), filename:lineno

# Step 3 — timeit: benchmark a specific expression
import timeit
timeit.timeit('"-".join(str(n) for n in range(100))', number=10_000)

# CLI shortcut (no code changes):
# python -m cProfile -s cumulative my_script.py
```

> Key stats to read: `tottime` = time IN the function (excluding callees). `cumtime` = total time including callees. Sort by `cumulative` to find the top-level bottleneck, then sort by `tottime` to find where time is actually spent.

</details>

<br>

**Q: How do you find memory leaks in Python?**

<details>
<summary>💡 Show Answer</summary>

**Strong answer:**

> Python can leak memory through: reference cycles that the GC misses (common with `__del__`), large objects held in module-level caches, and C extension leaks. The workflow uses `tracemalloc` to find where allocations are growing.

```python
# tracemalloc — stdlib, zero overhead when not active:
import tracemalloc

tracemalloc.start()

# ... run the code you want to inspect ...
process_thousand_requests()

snapshot = tracemalloc.take_snapshot()
top_stats = snapshot.statistics('lineno')

print("Top 5 memory allocations:")
for stat in top_stats[:5]:
    print(stat)
# → myapp/cache.py:47: size=24.3 MiB, count=8421, average=2.9 KiB

# Compare two snapshots to find GROWTH:
snapshot1 = tracemalloc.take_snapshot()
process_more_requests()
snapshot2 = tracemalloc.take_snapshot()

for stat in snapshot2.compare_to(snapshot1, 'lineno')[:5]:
    print(stat)   # shows lines whose allocation GREW between snapshots
```

> Also check: `gc.get_objects()` for reference cycles, and `objgraph.show_most_common_types()` (third-party) for a histogram of live objects by type.

</details>


## 🔴 Level 3 — Senior Questions

---

**Q11: What is a correlation ID and how do you implement it?**

<details>
<summary>💡 Show Answer</summary>

**Strong answer:**

> A correlation ID is a unique identifier assigned to each incoming request and propagated through every service that request touches. Every log entry includes it, so you can trace a single user's request across 10 microservices.

```python
from contextvars import ContextVar
import uuid
import logging

correlation_id: ContextVar[str] = ContextVar("correlation_id", default="")

class CorrelationFilter(logging.Filter):
    def filter(self, record):
        record.correlation_id = correlation_id.get() or "no-id"
        return True

# Middleware: set at request entry
def middleware(request, next_handler):
    cid = request.headers.get("X-Correlation-ID") or str(uuid.uuid4())
    token = correlation_id.set(cid)
    try:
        return next_handler(request)
    finally:
        correlation_id.reset(token)

# Now all logs in this request chain show [cid]:
# [abc123] api.routes:45 | Request: GET /orders/4892
# [abc123] service.order:88 | Fetching order 4892
# [abc123] service.payment:23 | Charging card for order 4892
```

</details>

<br>

**Q12: What is observability? How is it different from logging?**

<details>
<summary>💡 Show Answer</summary>

**Strong answer:**

> Observability is the ability to understand the **internal state** of a system purely from its external outputs. It has three pillars:

```
LOGS      → "What happened?"       Text/JSON records of discrete events
METRICS   → "How is the system?"   Numeric measurements over time (latency p99, error rate)
TRACES    → "Where did time go?"   Distributed call graph across services (OpenTelemetry)

Logging alone is not observability.
Observability is the COMBINATION of all three + the ability to ask arbitrary questions.

Tools:
  Logs:    ELK Stack, CloudWatch Logs, Datadog Logs
  Metrics: Prometheus + Grafana, Datadog Metrics, CloudWatch Metrics
  Traces:  Jaeger, Zipkin, AWS X-Ray, Datadog APM (OpenTelemetry standard)
```

</details>

<br>

**Q13: How would you design logging for a microservices architecture?**

<details>
<summary>💡 Show Answer</summary>

**Strong answer:**

> My approach focuses on four principles: **consistency**, **correlation**, **centralization**, and **context**.

```
1. CONSISTENT FORMAT
   All services emit structured JSON logs with the same schema:
   {timestamp, level, service, version, correlation_id, user_id, message, ...}

2. CORRELATION IDs
   Every request gets a UUID at the entry point (API gateway).
   Passed via headers (X-Correlation-ID) to every downstream service.
   Every log includes it → full request trace in one query.

3. CENTRALIZED AGGREGATION
   Log shipper (Fluentd/Filebeat) on each node sends to Elasticsearch/Splunk.
   Never rely on SSHing to individual servers to read logs.

4. CONTEXT ENRICHMENT
   Middleware auto-adds: service_name, environment, host, deployment_version.
   Developers only write the business-level message.

5. SAMPLING FOR DEBUG LOGS
   DEBUG logs are expensive. Sample 1% of requests for detailed debug logging.
   Log all ERROR/WARNING, sample DEBUG.
```

</details>

<br>

**Q14: Walk me through how you'd investigate a 500 error in production.**

<details>
<summary>💡 Show Answer</summary>

**Strong answer:**

```
STEP 1: Find the incident window
  → Check monitoring dashboard for error rate spike
  → Note exact start time

STEP 2: Filter logs to the error window
  → Query: level=ERROR AND timestamp >= start AND service=affected
  → Look for patterns: what % are the same error? different users? one endpoint?

STEP 3: Read the full traceback
  → Find the root cause (bottom of traceback)
  → Check surrounding INFO logs for request context

STEP 4: Correlate with deployments
  → Did a deployment happen before the incident?
  → git log --since="30 minutes ago"

STEP 5: Check system state
  → DB connection pool metrics
  → Memory/CPU at time of incident
  → Third-party API status pages

STEP 6: Reproduce locally
  → Use the request data from logs to recreate locally
  → Run with DEBUG level

STEP 7: Fix → test → deploy → verify
  → Add regression test for the specific case
  → Add better logging so next incident is 10x faster to diagnose
```

</details>

<br>

**Q: How do you debug a Python service running in a Docker container remotely?**

<details>
<summary>💡 Show Answer</summary>

**Strong answer:**

> The standard approach is `debugpy` — Microsoft's debug adapter protocol (DAP) server for Python. The container runs the service with `debugpy` listening on a port, and VS Code (or any DAP-compatible editor) attaches to it from outside.

```python
# In your service entrypoint (or a debug wrapper):
import debugpy

debugpy.listen(("0.0.0.0", 5678))   # listen on all interfaces, port 5678
debugpy.wait_for_client()           # BLOCKS until VS Code attaches — remove in production!

# Then your normal application code:
from myapp import create_app
app = create_app()
app.run(host="0.0.0.0", port=8080)
```

```yaml
# docker-compose.yml — expose the debug port:
services:
  api:
    ports:
      - "8080:8080"
      - "5678:5678"   # ← debugpy port
    environment:
      - DEBUG_MODE=true
```

```json
// VS Code .vscode/launch.json:
{
  "type": "python",
  "request": "attach",
  "connect": {"host": "localhost", "port": 5678},
  "pathMappings": [{"localRoot": "${workspaceFolder}", "remoteRoot": "/app"}]
}
```

> For Kubernetes: use `kubectl port-forward pod/my-pod 5678:5678` to tunnel the port locally, then attach VS Code as above. Never leave `wait_for_client()` in production builds — gate it behind an environment variable.

</details>


## ⚠️ Trap Questions

---

### Trap 1 — basicConfig Called by Library

```python
import requests   # internally calls basicConfig!

import logging
logging.basicConfig(level=logging.DEBUG)   # ← DOES NOTHING — root already has handler!

# FIX: configure your own named logger:
logger = logging.getLogger("myapp")
logger.setLevel(logging.DEBUG)
handler = logging.StreamHandler()
handler.setLevel(logging.DEBUG)
logger.addHandler(handler)
logger.propagate = False   # don't send to root logger
```

---

### Trap 2 — f-string in logger.debug()

```python
# Looks harmless but is a performance trap:
logger.debug(f"User data: {serialize_user(user)}")
# ← serialize_user() is called EVERY TIME this line runs,
#   even when DEBUG is disabled and the message is never emitted!

# Fix:
logger.debug("User data: %s", serialize_user(user))
# ← serialize_user() is only called if DEBUG is actually enabled
```

---

### Trap 3 — Double Logging

```python
# myapp/__init__.py
logging.basicConfig(level=logging.INFO)   # ← adds handler to root

# myapp/payment.py
logger = logging.getLogger("myapp.payment")
handler = logging.StreamHandler()         # ← adds handler to myapp.payment
logger.addHandler(handler)

# Result: every log appears TWICE
# Because myapp.payment's handler emits it,
# AND propagation sends it to root's handler too.

# FIX: set propagate=False on the child logger,
# OR only configure the root logger (not both).
logger.propagate = False
```

---

## 🔥 Rapid-Fire Revision

```
Q: What's the numeric value of each log level?
A: DEBUG=10, INFO=20, WARNING=30, ERROR=40, CRITICAL=50

Q: What does logging.exception() do differently from logging.error()?
A: exception() also logs the current traceback. Equivalent to error(..., exc_info=True).
   Use exception() INSIDE except blocks only.

Q: What is propagate?
A: If True (default), log records are also sent to parent logger's handlers.
   Set propagate=False to stop a logger from sending to the root logger.

Q: What is NullHandler?
A: A handler that does nothing. Library authors add it so their logs
   go nowhere unless the user explicitly configures them.
   import logging; logging.getLogger("mylib").addHandler(logging.NullHandler())

Q: What does disable_existing_loggers=False do in dictConfig?
A: Keeps existing loggers (from imported libraries) alive.
   Setting True (dangerous default!) silences all previously created loggers.

Q: What is the difference between logger.warning() and warnings.warn()?
A: logger.warning() = logging module, for operational events.
   warnings.warn() = warnings module, for code-level notices (DeprecationWarning etc.)

Q: What is faulthandler.enable()?
A: Prints a traceback even on segfault (SIGSEGV) or deadlock.
   Call at startup in any production C-extension heavy program.

Q: How do you get pdb post-mortem?
A: pdb.post_mortem() in except block, or python -m pdb script.py on the CLI.

Q: What's the difference between n and s in pdb?
A: n (next) = execute line, step OVER function calls.
   s (step) = execute line, step INTO function calls.
```

---

## 🔁 Navigation

| | |
|---|---|
| 📖 Theory | [theory.md](./theory.md) |
| ⚡ Cheatsheet | [cheetsheet.md](./cheetsheet.md) |
| 🐛 PDB Guide | [pdb_guide.md](./pdb_guide.md) |
| ➡️ Next | [10 — Decorators](../10_decorators/theory.md) |

---

**[🏠 Back to README](../README.md)**

**Prev:** [← PDB Debugging Guide](./pdb_guide.md) &nbsp;|&nbsp; **Next:** [Decorators — Theory →](../10_decorators/theory.md)

**Related Topics:** [Theory](./theory.md) · [Cheat Sheet](./cheetsheet.md) · [PDB Debugging Guide](./pdb_guide.md)
