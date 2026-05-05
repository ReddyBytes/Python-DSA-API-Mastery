"""
09_logging_debugging/logging_examples.py
==========================================
CONCEPT: Python's logging module — the correct way to record what your
application is doing (not print statements).
WHY THIS MATTERS: print() is for development only. In production, you need:
  - Log levels (DEBUG/INFO/WARNING/ERROR/CRITICAL) to filter noise
  - Timestamps and contextual information on every message
  - Multiple output destinations (file + console simultaneously)
  - Ability to enable/disable logging per module without code changes
  - Log rotation to prevent disk from filling up

Prerequisite: Modules 01–08
"""

import logging
import sys
import traceback
from pathlib import Path
import tempfile

tmp_dir = Path(tempfile.mkdtemp())

# =============================================================================
# SECTION 1: Why print() fails in production
# =============================================================================

# CONCEPT: print() has no level, no timestamp, no caller info, no file output,
# and can't be turned off without code changes. It mixes debug noise with
# real output. Logging solves all of these.

print("=== Section 1: print() vs logging ===")

# What you're doing when you use print for debugging:
print("[DEBUG] About to process order...")          # no level, no timestamp
print(f"[INFO] Order 42 processed successfully")    # manual level prefix
print("[ERROR] Payment failed!")                    # no structured data

# What logging gives you for free:
logging.basicConfig(
    level=logging.DEBUG,
    format="%(asctime)s | %(levelname)-8s | %(name)s | %(message)s",
    datefmt="%H:%M:%S",
    stream=sys.stdout,  # output to stdout for this demo
)

log = logging.getLogger("order_service")  # named logger — can be filtered

log.debug("About to process order (only visible when DEBUG level active)")
log.info("Order 42 processed successfully")
log.warning("Payment gateway latency above threshold: 500ms")
log.error("Payment failed for order 99")
log.critical("Database connection lost — all operations halted")


# =============================================================================
# SECTION 2: Logger hierarchy and configuration
# =============================================================================

# CONCEPT: Loggers form a hierarchy. "myapp.api" → "myapp" → root.
# Log records propagate UP the hierarchy unless propagate=False.
# Configure the root or parent logger — all children inherit.
# WHY: in a large codebase, you configure once and all modules just do
# `logging.getLogger(__name__)` — they automatically inherit the config.

print("\n=== Section 2: Logger Hierarchy ===")

# Each module gets its own named logger
root_log   = logging.getLogger()             # root logger
app_log    = logging.getLogger("myapp")      # child of root
api_log    = logging.getLogger("myapp.api")  # child of myapp
db_log     = logging.getLogger("myapp.db")   # child of myapp

# Demonstrate: logs from api_log flow through myapp → root
api_log.info("GET /api/users — handled")
db_log.debug("Query executed: SELECT * FROM users WHERE active=1")

# Control verbosity per subsystem
db_log.setLevel(logging.WARNING)   # only see warnings+ from DB module
api_log.setLevel(logging.DEBUG)    # see everything from API module

api_log.debug("Validating request parameters")
db_log.debug("This debug message is now filtered out")
db_log.warning("Query took 2.3s — slow query alert")


# =============================================================================
# SECTION 3: Handlers — where logs go
# =============================================================================

# CONCEPT: Handlers send log records to destinations.
# StreamHandler → stdout/stderr
# FileHandler   → log file
# RotatingFileHandler → log file with size-based rotation
# TimedRotatingFileHandler → daily/weekly rotation
# You can attach multiple handlers to one logger — logs to all.

print("\n=== Section 3: Multiple Handlers ===")

def setup_logger(name: str, log_file: Path) -> logging.Logger:
    """
    Sets up a logger that writes to BOTH console and a file.
    Different levels for each: DEBUG to file, INFO to console.
    This pattern lets you see INFO in the terminal but have full DEBUG
    logs available in the file for post-incident analysis.
    """
    logger = logging.getLogger(name)
    logger.setLevel(logging.DEBUG)   # master level — handlers filter further

    # Console handler: INFO+ (keep terminal clean)
    console = logging.StreamHandler(sys.stdout)
    console.setLevel(logging.INFO)
    console.setFormatter(logging.Formatter(
        "%(levelname)-8s %(name)s: %(message)s"
    ))

    # File handler: DEBUG+ (capture everything)
    file_handler = logging.FileHandler(log_file, encoding="utf-8")
    file_handler.setLevel(logging.DEBUG)
    file_handler.setFormatter(logging.Formatter(
        "%(asctime)s %(levelname)-8s %(name)s [%(filename)s:%(lineno)d] %(message)s"
    ))

    logger.addHandler(console)
    logger.addHandler(file_handler)
    logger.propagate = False   # don't also send to root logger
    return logger

log_file = tmp_dir / "app.log"
app = setup_logger("myapp_demo", log_file)

app.debug("DB query: SELECT * FROM users")    # only in file
app.info("User 42 logged in")                 # console + file
app.warning("Cache miss rate: 45%")           # console + file
app.error("External API timeout")             # console + file

print(f"\nLog file contents:")
for line in log_file.read_text().splitlines():
    print(f"  {line}")


# =============================================================================
# SECTION 4: Logging exceptions properly
# =============================================================================

# CONCEPT: When logging exceptions, use `logger.exception()` or
# `logger.error(..., exc_info=True)` — this captures the full traceback.
# Without exc_info, you only get the message, not WHERE it happened.
# This is crucial for debugging production incidents.

print("\n=== Section 4: Exception Logging ===")

exc_logger = logging.getLogger("exception_demo")
exc_logger.addHandler(logging.StreamHandler(sys.stdout))
exc_logger.propagate = False

def risky_operation(value):
    return 100 / value

def process_values(values):
    results = []
    for v in values:
        try:
            result = risky_operation(v)
            results.append(result)
            exc_logger.info(f"Processed {v} → {result:.2f}")

        except ZeroDivisionError:
            # logger.exception() logs ERROR level + full traceback automatically
            exc_logger.exception(f"Failed to process value {v}")
            # Equivalent: exc_logger.error(f"...", exc_info=True)
            results.append(None)
    return results

print("\nProcessing with exception logging:")
results = process_values([10, 5, 0, 2])   # 0 will cause ZeroDivisionError
print(f"Results: {results}")


# =============================================================================
# SECTION 5: contextual logging with extra fields
# =============================================================================

# CONCEPT: In web servers, you want every log from handling a request to
# include request_id, user_id, etc. — even across multiple function calls.
# The `extra` parameter adds fields to the log record. A LoggerAdapter
# provides a convenient way to attach persistent context.

print("\n=== Section 5: Contextual Logging ===")

class RequestContextAdapter(logging.LoggerAdapter):
    """
    Wraps a logger to automatically include request context in every message.
    Pass `extra` with initial context; messages are automatically enriched.
    """
    def process(self, msg, kwargs):
        request_id = self.extra.get("request_id", "?")
        user_id    = self.extra.get("user_id", "anonymous")
        return f"[req:{request_id}] [user:{user_id}] {msg}", kwargs

base_logger = logging.getLogger("api_request")
base_logger.addHandler(logging.StreamHandler(sys.stdout))
base_logger.setLevel(logging.DEBUG)
base_logger.propagate = False

def handle_api_request(request_id: str, user_id: int):
    """Simulates handling one API request with consistent log context."""
    # Create an adapter that attaches request context to every log message
    req_log = RequestContextAdapter(base_logger, {
        "request_id": request_id,
        "user_id": user_id,
    })

    req_log.info("Request received: GET /api/profile")
    req_log.debug("Checking authentication cache")
    req_log.info("Cache miss — querying database")
    req_log.info("Profile loaded successfully")

print("\nContextual logging output:")
handle_api_request("req-abc123", 42)


# =============================================================================
# SECTION 6: Log rotation — preventing disk from filling up
# =============================================================================

# CONCEPT: In production, log files grow indefinitely without rotation.
# RotatingFileHandler: rotate when file reaches a size limit
# TimedRotatingFileHandler: rotate daily/weekly

print("\n=== Section 6: Log Rotation ===")

from logging.handlers import RotatingFileHandler, TimedRotatingFileHandler

rotating_log = tmp_dir / "rotating.log"

rotating_logger = logging.getLogger("rotating")
handler = RotatingFileHandler(
    rotating_log,
    maxBytes=1024,       # rotate when file hits 1KB (tiny for demo)
    backupCount=3,       # keep last 3 rotated files (.log.1, .log.2, .log.3)
)
handler.setFormatter(logging.Formatter("%(message)s"))
rotating_logger.addHandler(handler)
rotating_logger.setLevel(logging.DEBUG)
rotating_logger.propagate = False

for i in range(100):
    rotating_logger.info(f"Log line {i:03d}: sample application log message with some content")

# Check what files were created
log_files = list(tmp_dir.glob("rotating*"))
print(f"Rotation created files: {sorted(f.name for f in log_files)}")
print(f"Active log size: {rotating_log.stat().st_size} bytes")

print("\n=== Logging complete ===")
print("Production logging rules:")
print("  1. NEVER use print() in production code — use logging")
print("  2. Named loggers per module: logging.getLogger(__name__)")
print("  3. Configure at app startup, use everywhere")
print("  4. Exception logging: always use .exception() or exc_info=True")
print("  5. Contextual data (request_id, user_id) via LoggerAdapter")
print("  6. RotatingFileHandler to prevent unbounded log file growth")
