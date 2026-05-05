# 💻 Production Best Practices — Practice
# Run with: python3 practice.py

# =============================================================================
# SECTION 1: Environment Variables — os.environ with Fallback Defaults
# =============================================================================

# In production, secrets and configuration live in environment variables —
# never hardcoded in source files. The pattern is always:
#   value = os.environ.get("VAR_NAME", "default_for_dev")
# python-dotenv loads a .env file in development; in prod, env vars are
# injected by the orchestrator (Kubernetes, ECS, systemd).

import os

print("=" * 60)
print("SECTION 1: os.environ with fallback defaults")
print("=" * 60)

# Simulate python-dotenv: in real code this is `from dotenv import load_dotenv; load_dotenv()`
# For this demo we inject values directly so no external dependency needed.
os.environ.setdefault("APP_ENV",      "development")
os.environ.setdefault("LOG_LEVEL",    "DEBUG")
os.environ.setdefault("DB_HOST",      "localhost")
os.environ.setdefault("DB_PORT",      "5432")
os.environ.setdefault("DB_NAME",      "appdb")
os.environ.setdefault("MAX_WORKERS",  "4")

# Reading env vars — always prefer .get() with a fallback over direct []
# Direct [] raises KeyError if missing; .get() returns None or your default
APP_ENV     = os.environ.get("APP_ENV",      "production")
LOG_LEVEL   = os.environ.get("LOG_LEVEL",    "INFO")
DB_HOST     = os.environ.get("DB_HOST",      "localhost")
DB_PORT     = int(os.environ.get("DB_PORT",  "5432"))    # type conversion
DB_NAME     = os.environ.get("DB_NAME",      "appdb")
MAX_WORKERS = int(os.environ.get("MAX_WORKERS", "2"))

print(f"  APP_ENV:     {APP_ENV}")
print(f"  LOG_LEVEL:   {LOG_LEVEL}")
print(f"  DB_HOST:     {DB_HOST}")
print(f"  DB_PORT:     {DB_PORT}  (int)")
print(f"  MAX_WORKERS: {MAX_WORKERS}  (int)")

# Pattern: require a var (raise clearly if missing, not with an obscure KeyError)
def require_env(name):
    """Raise a clear error if a required environment variable is missing."""
    value = os.environ.get(name)
    if not value:
        raise EnvironmentError(
            f"Required environment variable {name!r} is not set. "
            f"Add it to .env or your deployment config."
        )
    return value

try:
    secret = require_env("API_SECRET_KEY")   # not set → clear error
except EnvironmentError as e:
    print(f"\n  Missing required var: {e}")
print()


# =============================================================================
# SECTION 2: Dataclass-Based Configuration
# =============================================================================

# A Config dataclass centralises all settings in one typed object.
# Benefits: autocomplete, type errors caught early, easy to pass around,
# testable (inject a test config, not real env vars).

from dataclasses import dataclass, field
from typing import Optional

print("=" * 60)
print("SECTION 2: Dataclass-based configuration")
print("=" * 60)

@dataclass
class DatabaseConfig:
    host:     str
    port:     int
    name:     str
    user:     str
    password: str

    @property
    def url(self) -> str:
        """Build connection URL — password never logged."""
        return f"postgresql://{self.user}:***@{self.host}:{self.port}/{self.name}"

    def __post_init__(self):
        if not (1 <= self.port <= 65535):
            raise ValueError(f"Invalid port: {self.port}")


@dataclass
class AppConfig:
    env:         str   = "development"
    debug:       bool  = False
    log_level:   str   = "INFO"
    max_workers: int   = 4
    db:          Optional[DatabaseConfig] = None

    @classmethod
    def from_env(cls) -> "AppConfig":
        """Factory: build config from environment variables."""
        db = DatabaseConfig(
            host=os.environ.get("DB_HOST", "localhost"),
            port=int(os.environ.get("DB_PORT", "5432")),
            name=os.environ.get("DB_NAME", "appdb"),
            user=os.environ.get("DB_USER", "postgres"),
            password=os.environ.get("DB_PASSWORD", ""),
        )
        return cls(
            env=os.environ.get("APP_ENV", "development"),
            debug=os.environ.get("DEBUG", "false").lower() == "true",
            log_level=os.environ.get("LOG_LEVEL", "INFO"),
            max_workers=int(os.environ.get("MAX_WORKERS", "4")),
            db=db,
        )

    def is_production(self) -> bool:
        return self.env == "production"


config = AppConfig.from_env()
print(f"  Config.env:         {config.env}")
print(f"  Config.debug:       {config.debug}")
print(f"  Config.log_level:   {config.log_level}")
print(f"  Config.db.url:      {config.db.url}")
print(f"  Config.is_prod:     {config.is_production()}")
print()


# =============================================================================
# SECTION 3: Production Logging Setup — JSON Formatter Pattern
# =============================================================================

# In production you almost always want structured (JSON) logs.
# Reason: log aggregators (Splunk, Datadog, CloudWatch) can parse JSON
# and let you filter by field. Human-readable logs are fine for development.
# This demo shows both a plain dev formatter and a JSON production formatter.

import logging
import json
import datetime

print("=" * 60)
print("SECTION 3: Logging setup for production")
print("=" * 60)

class JSONFormatter(logging.Formatter):
    """Emit log records as single-line JSON — parseable by log aggregators."""

    def format(self, record: logging.LogRecord) -> str:
        log_entry = {
            "timestamp": datetime.datetime.utcnow().isoformat() + "Z",
            "level":     record.levelname,
            "logger":    record.name,
            "message":   record.getMessage(),
            "module":    record.module,
            "line":      record.lineno,
        }
        # Include exception info if present
        if record.exc_info:
            log_entry["exception"] = self.formatException(record.exc_info)
        # Include any extra fields passed to the logger
        for key, value in record.__dict__.items():
            if key not in log_entry and not key.startswith("_") and key not in (
                "msg", "args", "exc_info", "exc_text", "stack_info",
                "lineno", "funcName", "created", "msecs", "relativeCreated",
                "thread", "threadName", "processName", "process",
                "pathname", "filename", "module", "name", "levelname",
                "levelno", "asctime",
            ):
                log_entry[key] = value
        return json.dumps(log_entry)


def setup_logging(level: str = "INFO", use_json: bool = False) -> logging.Logger:
    """Configure root logger for the application.

    In development: human-readable format.
    In production:  JSON format for log aggregators.
    """
    logger = logging.getLogger("app")
    logger.setLevel(getattr(logging, level.upper(), logging.INFO))

    # Avoid adding duplicate handlers on repeated calls
    if logger.handlers:
        return logger

    handler = logging.StreamHandler()
    if use_json:
        handler.setFormatter(JSONFormatter())
    else:
        handler.setFormatter(logging.Formatter(
            "%(asctime)s %(levelname)-8s %(name)s: %(message)s",
            datefmt="%H:%M:%S"
        ))
    logger.addHandler(handler)
    return logger


# Dev-style logging
dev_logger = setup_logging(level="DEBUG", use_json=False)
dev_logger.info("Application starting up")
dev_logger.debug("Debug detail: config loaded from env")
dev_logger.warning("Low disk space detected")

print()

# JSON-style logging (what you'd use in production)
# Create a separate logger to avoid duplicates
json_logger = logging.getLogger("app.json_demo")
json_logger.setLevel(logging.DEBUG)
if not json_logger.handlers:
    jh = logging.StreamHandler()
    jh.setFormatter(JSONFormatter())
    json_logger.addHandler(jh)
    json_logger.propagate = False

json_logger.info("Service ready to accept connections")
try:
    raise ValueError("Demo exception for JSON log")
except ValueError:
    json_logger.error("Payment processing failed", exc_info=False)
print()


# =============================================================================
# SECTION 4: __version__ and Package Metadata
# =============================================================================

# Production packages expose __version__ for introspection, debugging,
# and compatibility checks. The canonical approach since Python 3.8
# is importlib.metadata.version("package-name").

print("=" * 60)
print("SECTION 4: __version__ and package metadata")
print("=" * 60)

# Module-level version constant — simple and universal
__version__ = "1.4.2"
__author__  = "Engineering Team"
__email__   = "eng@example.com"

print(f"  __version__: {__version__}")

# Parse version for comparison
def parse_version(version_str):
    """Return (major, minor, patch) tuple from 'X.Y.Z' string."""
    parts = version_str.split(".")
    return tuple(int(p) for p in parts)

current = parse_version(__version__)
required = parse_version("1.3.0")
print(f"  current={current}, required={required}, compatible={current >= required}")

# importlib.metadata approach (reads from installed package metadata)
from importlib import metadata as importlib_metadata

try:
    # Works for actually installed packages
    pip_version = importlib_metadata.version("pip")
    print(f"  pip version (from importlib.metadata): {pip_version}")
except importlib_metadata.PackageNotFoundError:
    print("  pip not found via importlib.metadata")
print()


# =============================================================================
# SECTION 5: argparse — CLI Tools for Production Scripts
# =============================================================================

# Production scripts need consistent CLI interfaces.
# argparse gives you: argument parsing, --help generation, type coercion,
# default values, and subcommands — all from stdlib.

import argparse
import sys

print("=" * 60)
print("SECTION 5: argparse for CLI tools")
print("=" * 60)

def build_parser() -> argparse.ArgumentParser:
    """Build and return the argument parser for this tool."""
    parser = argparse.ArgumentParser(
        description="Data processing CLI — production example",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="Examples:\n  python3 practice.py --env production --workers 8\n"
               "  python3 practice.py --dry-run --verbose"
    )

    parser.add_argument(
        "--env",
        choices=["development", "staging", "production"],
        default="development",
        help="Target environment (default: development)"
    )
    parser.add_argument(
        "--workers",
        type=int,
        default=4,
        metavar="N",
        help="Number of worker threads (default: 4)"
    )
    parser.add_argument(
        "--input",
        type=str,
        default=None,
        help="Path to input file"
    )
    parser.add_argument(
        "--output",
        type=str,
        default="output.json",
        help="Path to output file (default: output.json)"
    )
    parser.add_argument(
        "--dry-run",
        action="store_true",  # flag: present = True, absent = False
        help="Parse and validate without writing output"
    )
    parser.add_argument(
        "--verbose", "-v",
        action="store_true",
        help="Enable verbose logging"
    )
    parser.add_argument(
        "--version",
        action="version",
        version=f"%(prog)s {__version__}"
    )
    return parser


# Simulate parsing a known set of args (don't use sys.argv so script stays runnable)
parser = build_parser()
args = parser.parse_args(["--env", "staging", "--workers", "8", "--dry-run", "--verbose"])

print(f"  args.env:      {args.env}")
print(f"  args.workers:  {args.workers}")
print(f"  args.dry_run:  {args.dry_run}")
print(f"  args.verbose:  {args.verbose}")
print(f"  args.output:   {args.output}")

# Typical main() pattern
def main(args=None):
    """Entry point — parse args, set up, run."""
    parser = build_parser()
    parsed = parser.parse_args(args)

    level = "DEBUG" if parsed.verbose else "INFO"
    use_json = (parsed.env == "production")
    logger = setup_logging(level=level, use_json=use_json)

    logger.info(f"Starting in {parsed.env} with {parsed.workers} workers")

    if parsed.dry_run:
        logger.info("Dry run — no output will be written")
        return 0

    # ... actual work ...
    return 0

# Demonstrate calling main() with injected args
exit_code = main(["--env", "development", "--verbose", "--dry-run"])
print(f"  main() exit code: {exit_code}")
print()


# =============================================================================
# SECTION 6: pathlib — Project Paths in Production Code
# =============================================================================

# pathlib.Path is the modern, cross-platform way to work with file paths.
# Avoid os.path.join() in new code — Path uses / operator and is cleaner.

from pathlib import Path

print("=" * 60)
print("SECTION 6: pathlib for project paths")
print("=" * 60)

# Anchor paths relative to THIS file — not the working directory
# This is critical for scripts run from different directories
THIS_FILE   = Path(__file__).resolve()
PROJECT_ROOT = THIS_FILE.parent.parent   # two levels up from this file

# Typical project structure navigation
def get_project_dirs(root: Path) -> dict:
    """Return a dict of key project directories."""
    return {
        "root":    root,
        "src":     root / "src",
        "tests":   root / "tests",
        "config":  root / "config",
        "logs":    root / "logs",
        "data":    root / "data",
    }

dirs = get_project_dirs(PROJECT_ROOT)
print(f"  THIS_FILE:    {THIS_FILE}")
print(f"  project root: {dirs['root']}")

# Safe file operations with pathlib
import tempfile

def ensure_dir(path: Path) -> Path:
    """Create directory and all parents if they don't exist."""
    path.mkdir(parents=True, exist_ok=True)
    return path

def write_config(config_dir: Path, data: dict) -> Path:
    """Write config dict as JSON to config_dir/app.json."""
    config_dir.mkdir(parents=True, exist_ok=True)
    config_file = config_dir / "app.json"
    config_file.write_text(json.dumps(data, indent=2))
    return config_file

# Demo with a temp directory
with tempfile.TemporaryDirectory() as tmp:
    tmp_path = Path(tmp)
    cfg_path = write_config(tmp_path / "config", {"env": "test", "debug": True})
    print(f"  Config written to: {cfg_path.name}")
    print(f"  Content: {cfg_path.read_text()[:40]}...")

    # Glob — find all JSON files recursively
    json_files = list(tmp_path.rglob("*.json"))
    print(f"  Found {len(json_files)} JSON file(s)")

    # Path properties
    print(f"  cfg_path.stem:   {cfg_path.stem}")
    print(f"  cfg_path.suffix: {cfg_path.suffix}")
    print(f"  cfg_path.parent: {cfg_path.parent.name}")
print()


# =============================================================================
# SECTION 7: Type Hints in Production Code
# =============================================================================

# Type hints make code self-documenting and enable static analysis (mypy/pyright).
# They are NOT enforced at runtime but catch bugs before they reach production.

from typing import TypeVar, Generic, Optional, Union, Callable, Iterator

print("=" * 60)
print("SECTION 7: Type hints in production code")
print("=" * 60)

T = TypeVar("T")

class Result(Generic[T]):
    """Rust-inspired Result type: either Ok(value) or Err(message).
    Forces callers to handle both success and failure paths explicitly."""

    def __init__(self, value: Optional[T] = None, error: Optional[str] = None):
        self._value = value
        self._error = error

    @classmethod
    def ok(cls, value: T) -> "Result[T]":
        return cls(value=value)

    @classmethod
    def err(cls, message: str) -> "Result[T]":
        return cls(error=message)

    def is_ok(self) -> bool:
        return self._error is None

    def unwrap(self) -> T:
        """Return value or raise RuntimeError if this is an Err."""
        if self._error:
            raise RuntimeError(f"Called unwrap on Err: {self._error}")
        return self._value

    def unwrap_or(self, default: T) -> T:
        """Return value or default if this is an Err."""
        return self._value if self.is_ok() else default

    def __repr__(self) -> str:
        if self.is_ok():
            return f"Ok({self._value!r})"
        return f"Err({self._error!r})"


def parse_int(s: str) -> "Result[int]":
    try:
        return Result.ok(int(s))
    except ValueError:
        return Result.err(f"Cannot parse {s!r} as integer")


good = parse_int("42")
bad  = parse_int("not-a-number")

print(f"  parse_int('42'):            {good}")
print(f"  parse_int('not-a-number'):  {bad}")
print(f"  good.unwrap():              {good.unwrap()}")
print(f"  bad.unwrap_or(0):           {bad.unwrap_or(0)}")

try:
    bad.unwrap()
except RuntimeError as e:
    print(f"  bad.unwrap() raised: {e}")
print()


# =============================================================================
# SECTION 8: Health Check Pattern
# =============================================================================

# Every production service needs a /health or /healthz endpoint.
# A health check runs a lightweight probe on each dependency and returns
# an overall status. This pattern works for HTTP services, background jobs, etc.

print("=" * 60)
print("SECTION 8: Health check pattern")
print("=" * 60)

import time

@dataclass
class HealthStatus:
    service:  str
    healthy:  bool
    latency_ms: float
    detail:   str = ""

    def __str__(self):
        status = "OK" if self.healthy else "FAIL"
        return (f"[{status}] {self.service} "
                f"({self.latency_ms:.1f}ms) {self.detail}")


def check_database(host: str, port: int) -> HealthStatus:
    """Probe the database connection."""
    start = time.perf_counter()
    try:
        # In real code: socket.connect / SELECT 1 / ping
        # Here we simulate success
        import socket
        sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        sock.settimeout(1.0)
        # Don't actually connect in this demo — simulate result
        sock.close()
        latency = (time.perf_counter() - start) * 1000
        return HealthStatus("database", True, latency, f"{host}:{port}")
    except Exception as e:
        latency = (time.perf_counter() - start) * 1000
        return HealthStatus("database", False, latency, str(e))


def check_disk_space(threshold_gb: float = 1.0) -> HealthStatus:
    """Verify available disk space is above threshold."""
    start = time.perf_counter()
    try:
        import shutil
        total, used, free = shutil.disk_usage("/")
        free_gb = free / (1024 ** 3)
        healthy = free_gb > threshold_gb
        latency = (time.perf_counter() - start) * 1000
        detail  = f"{free_gb:.1f}GB free (threshold: {threshold_gb}GB)"
        return HealthStatus("disk", healthy, latency, detail)
    except Exception as e:
        latency = (time.perf_counter() - start) * 1000
        return HealthStatus("disk", False, latency, str(e))


def health_check() -> dict:
    """Run all probes and return aggregated health status."""
    checks = [
        check_database("localhost", 5432),
        check_disk_space(threshold_gb=0.1),   # low threshold for demo
    ]

    all_healthy = all(c.healthy for c in checks)
    return {
        "status":  "healthy" if all_healthy else "degraded",
        "checks":  [
            {
                "service":    c.service,
                "healthy":    c.healthy,
                "latency_ms": round(c.latency_ms, 2),
                "detail":     c.detail,
            }
            for c in checks
        ]
    }


result = health_check()
print(f"  Overall status: {result['status']}")
for check in result["checks"]:
    marker = "OK  " if check["healthy"] else "FAIL"
    print(f"  [{marker}] {check['service']}: {check['detail']} ({check['latency_ms']}ms)")
print()


# =============================================================================
# SECTION 9: Putting It All Together — Production App Bootstrap
# =============================================================================

print("=" * 60)
print("SECTION 9: Production app bootstrap pattern")
print("=" * 60)

def bootstrap(cli_args=None) -> int:
    """
    Standard production bootstrap:
    1. Parse CLI args
    2. Load config from env
    3. Set up logging
    4. Run health checks
    5. Start application
    """
    # Step 1: CLI args
    parser = build_parser()
    args = parser.parse_args(cli_args or [])

    # Step 2: Config (env vars take precedence over CLI defaults)
    cfg = AppConfig.from_env()

    # Step 3: Logging
    use_json = cfg.is_production()
    logger   = setup_logging(level=cfg.log_level, use_json=use_json)
    logger.info(
        f"Bootstrapping app v{__version__} "
        f"env={cfg.env} workers={cfg.max_workers}"
    )

    # Step 4: Health checks
    health = health_check()
    if health["status"] != "healthy":
        logger.error(f"Health checks failed: {health}")
        # In production you might want to exit(1) here
        # For demo we continue
        logger.warning("Continuing despite degraded health (demo mode)")

    # Step 5: Would start HTTP server / workers / scheduler here
    if args.dry_run:
        logger.info("Dry run — exiting before starting workers")
        return 0

    logger.info("Application ready")
    return 0


exit_code = bootstrap(["--env", "development", "--dry-run"])
print(f"\n  bootstrap() returned: {exit_code}")
print()
print("All production best practices examples complete.")
