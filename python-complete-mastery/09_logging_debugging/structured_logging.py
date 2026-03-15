"""
09_logging_debugging/structured_logging.py
============================================
CONCEPT: Structured logging — JSON log records with typed fields.
WHY THIS MATTERS: Plain text logs are human-readable but machine-unreadable.
In production, logs are ingested by tools (Datadog, Splunk, ELK, CloudWatch).
JSON logs can be filtered by `user_id=42` or `duration_ms > 1000` directly.
This is how modern observability works.

Prerequisite: Modules 01–09 logging_examples.py
"""

import logging
import json
import sys
import time
import uuid
import traceback
from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Optional
import tempfile

# =============================================================================
# SECTION 1: JSON Formatter — turn every log record into a JSON line
# =============================================================================

# CONCEPT: A formatter takes a LogRecord and returns a string.
# A JSON formatter serializes all relevant fields as a JSON object.
# One JSON object per line (NDJSON / JSON Lines format) is the standard
# for log ingestion systems.

print("=== Section 1: JSON Log Formatter ===")

class JSONFormatter(logging.Formatter):
    """
    Formats log records as JSON objects (one per line).
    Each log entry is a self-contained JSON object with:
    - timestamp (ISO 8601 for easy parsing)
    - level, logger name, message
    - source location (file, line, function)
    - any extra fields added by the caller
    - full exception info if present
    """

    def __init__(self, service_name: str = "app", environment: str = "development"):
        super().__init__()
        self.service_name = service_name
        self.environment  = environment

    def format(self, record: logging.LogRecord) -> str:
        # Core fields always present
        log_record = {
            "timestamp":   datetime.fromtimestamp(record.created, tz=timezone.utc).isoformat(),
            "level":       record.levelname,
            "logger":      record.name,
            "message":     record.getMessage(),
            "service":     self.service_name,
            "environment": self.environment,
            "location": {
                "file":     record.pathname,
                "line":     record.lineno,
                "function": record.funcName,
            },
        }

        # Append exception info if an exception was logged
        if record.exc_info:
            log_record["exception"] = {
                "type":    record.exc_info[0].__name__,
                "message": str(record.exc_info[1]),
                "traceback": traceback.format_exception(*record.exc_info),
            }

        # Merge any extra fields added by the caller
        # (anything not in standard LogRecord attributes)
        standard_attrs = {
            'name', 'msg', 'args', 'created', 'filename', 'funcName',
            'levelname', 'levelno', 'lineno', 'module', 'msecs', 'message',
            'pathname', 'process', 'processName', 'relativeCreated',
            'thread', 'threadName', 'exc_info', 'exc_text', 'stack_info',
        }
        for key, value in record.__dict__.items():
            if key not in standard_attrs and not key.startswith("_"):
                try:
                    json.dumps(value)   # check if serializable
                    log_record[key] = value
                except (TypeError, ValueError):
                    log_record[key] = str(value)

        return json.dumps(log_record)


def setup_json_logger(name: str) -> logging.Logger:
    """Create a logger that outputs JSON-formatted records."""
    logger = logging.getLogger(name)
    logger.setLevel(logging.DEBUG)

    handler = logging.StreamHandler(sys.stdout)
    handler.setFormatter(JSONFormatter(service_name="payment-service"))
    logger.addHandler(handler)
    logger.propagate = False
    return logger

log = setup_json_logger("demo")

# Basic log
log.info("Application started")

# Log with extra fields (these appear in the JSON output)
log.info("User logged in", extra={"user_id": 42, "ip": "192.168.1.1", "method": "oauth"})

# Log with exception
try:
    result = 1 / 0
except ZeroDivisionError:
    log.exception("Math error", extra={"calculation": "1/0", "context": "invoice_total"})


# =============================================================================
# SECTION 2: Request context logging (the real-world pattern)
# =============================================================================

# CONCEPT: In web servers, every request gets a unique request_id.
# All log messages from handling that request should include that ID,
# so you can filter all logs for a single request in your log viewer.
# This is done via a LoggerAdapter that injects the request context.

print("\n=== Section 2: Request Context ===")

class StructuredAdapter(logging.LoggerAdapter):
    """
    Logger adapter that injects structured context into every log record.
    The context dict is merged with any extra fields from the log call.
    """
    def process(self, msg: str, kwargs: dict) -> tuple:
        # Merge our persistent context with any call-specific extra fields
        extra = dict(self.extra)
        if "extra" in kwargs:
            extra.update(kwargs["extra"])
        kwargs["extra"] = extra
        return msg, kwargs


base_log = setup_json_logger("api")

def handle_request(method: str, path: str, user_id: Optional[int] = None):
    """Simulates handling an HTTP request with structured logging throughout."""
    request_id = str(uuid.uuid4())[:8]
    start_time = time.perf_counter()

    # Create a request-scoped logger that includes request context on every message
    req_log = StructuredAdapter(base_log, {
        "request_id": request_id,
        "method": method,
        "path": path,
        "user_id": user_id,
    })

    req_log.info("Request received")

    # Simulate some work
    time.sleep(0.001)
    req_log.debug("Auth check passed", extra={"cached": True})

    time.sleep(0.002)
    req_log.info("Processing complete", extra={
        "duration_ms": round((time.perf_counter() - start_time) * 1000, 2),
        "status_code": 200,
        "response_bytes": 1024,
    })

print("\nRequest with structured context:")
handle_request("GET", "/api/users/42", user_id=42)


# =============================================================================
# SECTION 3: Performance logging — timing and metrics
# =============================================================================

# CONCEPT: Structured logs with timing data enable APM (Application Performance
# Monitoring). You can query: "show all requests where duration_ms > 500"
# or "what's the p95 latency for GET /api/users?" with the right log queries.

print("\n=== Section 3: Performance / Timing Logs ===")

import functools

def log_performance(operation: str, logger: logging.Logger):
    """
    Decorator that logs execution time of a function as a structured record.
    WHY: Timing-enriched logs let you spot slow functions without APM tools.
    """
    def decorator(func):
        @functools.wraps(func)
        def wrapper(*args, **kwargs):
            start = time.perf_counter()
            error = None
            try:
                result = func(*args, **kwargs)
                return result
            except Exception as e:
                error = e
                raise
            finally:
                duration_ms = round((time.perf_counter() - start) * 1000, 3)
                level = logging.WARNING if duration_ms > 100 else logging.INFO
                logger.log(level, f"Operation complete: {operation}", extra={
                    "operation": operation,
                    "duration_ms": duration_ms,
                    "success": error is None,
                    "error_type": type(error).__name__ if error else None,
                })
        return wrapper
    return decorator


perf_log = setup_json_logger("performance")

@log_performance("database_query", perf_log)
def fetch_user_from_db(user_id: int) -> dict:
    time.sleep(0.01)  # simulate DB query
    return {"id": user_id, "name": "Alice"}

@log_performance("external_api", perf_log)
def call_payment_gateway(amount: float) -> dict:
    time.sleep(0.05)  # simulate slower external call
    return {"status": "success", "amount": amount}

print("\nPerformance-logged operations:")
fetch_user_from_db(42)
call_payment_gateway(99.99)


# =============================================================================
# SECTION 4: Logging to a structured file
# =============================================================================

# CONCEPT: Writing JSON logs to a file creates an audit trail that log
# aggregation systems (Splunk, Datadog, ELK) can ingest by shipping the file.

print("\n=== Section 4: JSON Log File ===")

tmp_dir = Path(tempfile.mkdtemp())
log_file = tmp_dir / "structured.log"

file_logger = logging.getLogger("file_structured")
file_logger.setLevel(logging.DEBUG)
file_handler = logging.FileHandler(log_file, encoding="utf-8")
file_handler.setFormatter(JSONFormatter(service_name="file-demo", environment="production"))
file_logger.addHandler(file_handler)
file_logger.propagate = False

# Write some structured logs
file_logger.info("Service started", extra={"pid": 12345, "version": "2.1.0"})
file_logger.info("Processed batch", extra={"batch_id": "B001", "count": 500, "duration_ms": 123.4})
file_logger.warning("High memory usage", extra={"memory_mb": 890, "threshold_mb": 800})
try:
    raise ValueError("Invalid config value")
except ValueError:
    file_logger.exception("Config error", extra={"config_key": "timeout"})

# Read and parse back as structured data
print("Structured log file contents (parsed):")
with open(log_file) as f:
    for line in f:
        record = json.loads(line.strip())
        print(f"  [{record['level']:8}] {record['message']}", end="")
        # Print any non-standard fields
        extras = {k: v for k, v in record.items()
                  if k not in {"timestamp","level","logger","message","service","environment","location"}}
        if extras and "exception" not in extras:
            print(f" {extras}", end="")
        print()


# =============================================================================
# SECTION 5: Log aggregation query examples
# =============================================================================

print("\n=== Section 5: Querying Structured Logs ===")

# Parse all log lines and run in-memory "queries" to show the concept
log_records = []
with open(log_file) as f:
    for line in f:
        try:
            log_records.append(json.loads(line.strip()))
        except json.JSONDecodeError:
            pass

print(f"Total log records: {len(log_records)}")

# Query: find all WARNING+ logs
warnings_plus = [r for r in log_records if r["level"] in ("WARNING", "ERROR", "CRITICAL")]
print(f"Warnings and above: {len(warnings_plus)}")
for r in warnings_plus:
    print(f"  [{r['level']}] {r['message']}")

# Query: find records with duration_ms (performance records)
perf_records = [r for r in log_records if "duration_ms" in r]
if perf_records:
    durations = [r["duration_ms"] for r in perf_records]
    print(f"\nPerformance records: {len(perf_records)}")
    print(f"  Max duration: {max(durations)}ms")


print("\n=== Structured logging complete ===")
print("Production structured logging checklist:")
print("  1. JSON formatter: one log line per JSON object")
print("  2. Every request gets a unique request_id, injected into all logs")
print("  3. Always include: timestamp, level, message, service, environment")
print("  4. Performance logs: duration_ms enables latency analysis")
print("  5. Exception logs: full traceback as structured data, not just message")
print("  6. Tools query fields: user_id=42, duration_ms>500, level=ERROR")
