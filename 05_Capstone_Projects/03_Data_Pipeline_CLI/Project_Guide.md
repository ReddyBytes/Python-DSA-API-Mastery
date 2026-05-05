# Project 03 — Build Guide: Data Pipeline CLI Tool

> A data pipeline is like a postal sorting facility: raw parcels (weather data) come in from outside, get inspected and labelled (Pydantic validation), sorted into bins (SQLite), processed into summaries (pandas), and dispatched as reports (CSV/table). Building one teaches you how real data flows through a system — not just how to write code, but how to design the path data takes from source to insight.

Work through each step in order. Each step is runnable before the next one starts. No step shows you the solution — that lives at the bottom.

---

## Step 1: CLI Interface

> The CLI is the front desk: every caller states their intent (fetch, process, report), hands over their details (flags), and gets routed to the right back-office function.

**Requirements:**
- Create `cli.py` with a `build_parser()` function that returns a configured `ArgumentParser`
- Add three subcommands: `fetch` (with `--lat`, `--lon`, `--days`, `--location`), `process` (with `--location`), and `report` (with `--location`, `--format`, `--output`)
- Add a global `--log-level` flag with choices `DEBUG`, `INFO`, `WARNING`, `ERROR` and default `INFO`
- Wire each subcommand to its handler function using `set_defaults(func=...)` or a dispatch block in `main()`
- `main()` must call `parser.parse_args()` and invoke the correct handler

**You need to know:**
- **`argparse.ArgumentParser`**: the standard library class that parses `sys.argv` and produces a `Namespace` object with one attribute per flag
- **subparsers**: a special argparse action that creates named sub-commands, each with their own flags, under one top-level parser
- **`set_defaults(func=...)`**: a pattern for attaching a callable to a subparser so `args.func(args)` dispatches without an if/elif chain
- **`subparsers.required = True`**: tells argparse to error immediately if no subcommand is provided

<details>
<summary>💡 Hint</summary>

Call `parser.add_subparsers(dest="command")` to create the subparser group, then `subparsers.add_parser("fetch")` for each command. The tricky part: `subparsers.required = True` must be set explicitly in Python 3 or argparse silently accepts zero-argument calls. Test with `python cli.py --help` and `python cli.py fetch --help` before moving on.

</details>

---

## Step 2: HTTP Fetch with Retry Logic

> The fetch module is a persistent courier: if the door is locked on first knock (transient network error), it waits and tries again — but if the address is wrong (4xx), it doesn't waste trips.

**Requirements:**
- Create `pipeline/fetch.py` with a `fetch_weather(lat, lon, past_days)` function
- Use `requests.get` to call the Open Meteo `/v1/forecast` endpoint with the params: `latitude`, `longitude`, `hourly` (temperature_2m, windspeed_10m, precipitation), `past_days`, `forecast_days=1`, `timezone="UTC"`
- Mount a `requests.adapters.HTTPAdapter` with `Retry(total=3, backoff_factor=1)` onto the session before making the call
- Pass `timeout=10` to the request
- Create a `run_fetch(args)` entry point that calls `fetch_weather` with values from the parsed args

**You need to know:**
- **`requests.Session`**: a persistent HTTP client that shares connection pools and adapter configuration across multiple requests
- **`HTTPAdapter`**: a transport adapter you attach to a session; it controls retry behaviour, connection pooling, and SSL options
- **`urllib3.util.retry.Retry`**: a config object that defines how many retries to attempt and which status codes or exception types should trigger a retry
- **`session.mount(prefix, adapter)`**: binds an adapter to all URLs starting with `prefix` (e.g., `"https://"`)
- **`response.raise_for_status()`**: raises an `HTTPError` immediately for any 4xx or 5xx response so you do not have to check status codes manually

<details>
<summary>💡 Hint</summary>

Import `Retry` from `urllib3.util.retry` and `HTTPAdapter` from `requests.adapters`. Build the adapter: `HTTPAdapter(max_retries=Retry(total=3, backoff_factor=1, status_forcelist=[500, 502, 503, 504]))`. Mount it with `session.mount("https://", adapter)`. The tricky part: `backoff_factor=1` means wait 1s, 2s, 4s — the formula is `backoff_factor * (2 ** (attempt - 1))`.

</details>

---

## Step 3: Pydantic Validation

> Pydantic is the customs inspector at the border: every parcel (API response) gets opened and checked against a manifest before it's allowed through.

**Requirements:**
- Create `pipeline/schemas.py` with a `HourlyData` model that has four list fields: `time`, `temperature_2m`, `windspeed_10m`, `precipitation` — all allowing `None` values in the lists
- Add a `@model_validator` that checks all four lists have the same length
- Create a `WeatherResponse` model that nests `HourlyData` under an `hourly` field
- Create a `WeatherRecord` model representing a single validated row, with a `from_hourly()` classmethod that converts one index position from `HourlyData` into a row
- Add a `validate_response(raw_data, location)` function in `fetch.py` that calls `WeatherResponse.model_validate()` and returns a `list[WeatherRecord]`

**You need to know:**
- **`BaseModel`**: Pydantic's base class; subclass it and declare fields as annotated attributes — Pydantic validates types on instantiation
- **`model_validate(dict)`**: the Pydantic v2 method for constructing a model from a raw dictionary (replaces v1's `parse_obj`)
- **`@model_validator(mode="after")`**: a decorator for a validator that runs after all fields are individually validated, receiving the fully-constructed model instance
- **`ValidationError`**: raised by Pydantic when input fails any field or model validator; its `.errors()` method returns structured detail per field
- **`list[float | None]`**: a type annotation telling Pydantic each element of the list can be a float or null

<details>
<summary>💡 Hint</summary>

For the length check, collect `{len(self.time), len(self.temperature_2m), ...}` into a set — if the set has more than one element, the lists are uneven. In `from_hourly()`, parse the time string with `datetime.fromisoformat(time_str)`. The tricky part: Pydantic v2 requires `model_validator(mode="after")` to return `self`.

</details>

---

## Step 4: SQLite Storage

> The database is the warehouse: validated parcels go onto labelled shelves (rows in a table), and you need a reliable system for finding them again later without mixing up locations or timestamps.

**Requirements:**
- Create `pipeline/database.py` with a SQLAlchemy ORM model `WeatherObservation` mapping to a `weather_observations` table
- The table must have: `id` (primary key), `location` (indexed string), `timestamp` (indexed datetime), `temperature_c`, `windspeed_kmh`, `precipitation_mm` (all nullable floats)
- Add an `init_db()` function that calls `Base.metadata.create_all()`
- Add a `get_session()` function that returns a `SessionLocal` instance
- Create a `save_records(records)` function that bulk-inserts validated `WeatherRecord` objects, skips duplicates by checking (location, timestamp), commits on success, and rolls back on failure

**You need to know:**
- **`DeclarativeBase`**: SQLAlchemy 2.0's base class; subclass it once and all ORM models that inherit from it share the same metadata registry
- **`Mapped[T]` and `mapped_column()`**: the typed annotation style for SQLAlchemy 2.0 ORM columns — replaces the older `Column()` syntax
- **`sessionmaker`**: a factory that creates `Session` instances bound to an engine; call it once at module level and call the result to get a session
- **`session.add_all(list)`**: queues multiple ORM objects for insertion in one call; more efficient than looping over `session.add()`
- **`session.rollback()`**: undoes all pending changes in the current transaction — always call this in the `except` block before re-raising

<details>
<summary>💡 Hint</summary>

Use `create_engine("sqlite:///./weather_pipeline.db", connect_args={"check_same_thread": False})`. The `check_same_thread=False` flag is required for SQLite when the session is created and used in the same process but potentially different threads. Duplicate check pattern: `session.query(WeatherObservation).filter_by(location=r.location, timestamp=r.timestamp).first()` — if the result is not `None`, skip that record.

</details>

---

## Step 5: Pandas Aggregation

> Pandas is the sorting machine downstream: it takes hundreds of hourly readings, bins them by day, and distils each bin into a single summary row — the same way a weather station issues one daily bulletin from 24 hourly readings.

**Requirements:**
- Create `pipeline/process.py` with a `load_to_dataframe(location)` function that queries `WeatherObservation` rows from the DB and returns a `pd.DataFrame` with a `DatetimeIndex` on the `timestamp` column
- Create a `compute_daily_summary(df)` function that uses `df.resample("D")` to aggregate to daily granularity, producing columns: `temp_mean`, `temp_min`, `temp_max`, `wind_mean`, `precip_total`
- Handle the empty DataFrame case gracefully in both functions
- Create a `run_process(args)` entry point that calls both functions and logs how many hourly records were aggregated into how many daily rows

**You need to know:**
- **`pd.DataFrame.set_index()`**: promotes a column to the DataFrame index, which is required before calling `resample()`
- **`resample("D")`**: groups rows into calendar-day buckets based on the index — equivalent to a `GROUP BY DATE(timestamp)` in SQL
- **`.agg(col_name=(source_col, func))`**: the named-aggregation syntax for applying a specific function to a specific source column and giving the result a new name
- **`df.empty`**: returns `True` if the DataFrame has no rows — always check this before calling `resample` to avoid errors on empty data

<details>
<summary>💡 Hint</summary>

After loading rows into a list of dicts, build the DataFrame with `pd.DataFrame(data)`, then `df["timestamp"] = pd.to_datetime(df["timestamp"])` and `df.set_index("timestamp", inplace=True)`. The tricky part: `resample` requires the index to be a `DatetimeIndex` — if it is still an object column the call will raise a `TypeError`.

</details>

---

## Step 6: Report Generation

> The report module is the dispatch desk: it takes the processed summaries and formats them for their final destination — a terminal table for humans, a CSV file for machines.

**Requirements:**
- Create `pipeline/report.py` with a `format_table(daily)` function that uses `tabulate` to render the daily DataFrame as a `"github"`-style text table with human-readable column headers
- Add a `run_report(args)` entry point that reads `args.format` (`"table"` or `"csv"`) and `args.output` (file path or `None`)
- When `--output` is provided, write the result to that file and print a confirmation; when omitted, print to stdout
- For CSV output use `pandas.DataFrame.to_csv()`; for table output use `tabulate`

**You need to know:**
- **`tabulate(df, headers="keys", tablefmt="github")`**: renders a DataFrame (or list of lists) as an aligned text table; `"github"` produces pipe-separated Markdown
- **`daily.reset_index()`**: moves the DatetimeIndex back into a regular column so it appears as the first column in the table
- **`df.to_csv()`**: serialises a DataFrame to CSV string (when called with no path argument) or writes directly to a file (when a path is provided)
- **`sys.stdout`**: the default output stream; writing to it is equivalent to `print()` and allows the same function to serve both terminal and pipe destinations

<details>
<summary>💡 Hint</summary>

Format the date column before passing to tabulate: `display["timestamp"] = display["timestamp"].dt.strftime("%Y-%m-%d")`. The tricky part: `daily.to_csv()` returns a string when called with no arguments — assign it to a variable, then either `print()` it or write it to a file depending on whether `args.output` is set.

</details>

---

## Step 7: Logging Setup

> Logging is the black box recorder: it writes everything that happens to a persistent file while simultaneously showing the right level of detail on the console — two audiences, one recording system.

**Requirements:**
- Create `pipeline/logging_config.py` with a `setup_logging(level)` function
- Configure two handlers: a `StreamHandler` (console, level from the `--log-level` flag) and a `RotatingFileHandler` (file `./logs/pipeline.log`, always DEBUG, max 5 MB, 3 backups)
- Set the root logger level to `DEBUG` so it does not filter before handlers get a chance
- Wire `setup_logging` into `main()` immediately after `parse_args()` so it runs before any module imports
- Use `logging.getLogger(__name__)` at the top of every module file

**You need to know:**
- **root logger**: the ancestor of all loggers in the hierarchy; its level acts as a global floor — set it to `DEBUG` and let each handler decide what to show
- **`logging.handlers.RotatingFileHandler`**: writes to a file and automatically rolls over to a new file when `maxBytes` is reached, keeping up to `backupCount` old files
- **`getLogger(__name__)`**: gets or creates a logger named after the current module — this gives you per-module filtering and makes log lines easy to trace to their source
- **`getattr(logging, level.upper(), logging.INFO)`**: converts a string like `"DEBUG"` into the integer constant `logging.DEBUG` — cleaner than a manual lookup dict

<details>
<summary>💡 Hint</summary>

Create `LOG_DIR = Path("./logs")` and call `LOG_DIR.mkdir(exist_ok=True)` at the top of `setup_logging`. The tricky part: if you call `setup_logging` after any module has already called `logging.getLogger(__name__)` and logged something, those early messages go to the root logger's default handler. Calling `setup_logging` as the very first thing in `main()` avoids this.

</details>

---

## Step 8: Error Handling

> Error handling is the sorting facility's exception lane: packages that fail inspection get a clear label explaining why, then go to the right holding area — not silently dropped on the floor.

**Requirements:**
- In `fetch.py`: catch `requests.exceptions.RequestException` for all network errors; distinguish 4xx (do not retry, log as error) from 5xx (retry, already handled by the adapter)
- In `fetch.py`: catch `pydantic.ValidationError` from `validate_response`, log the error detail, and re-raise
- In `database.py`: wrap `save_records` in a try/except that rolls back the session on any SQLAlchemy exception and re-raises
- In `cli.py` `main()`: wrap the entire dispatch block in a top-level try/except that catches `KeyboardInterrupt` (exit 0) and all other exceptions (log with `exc_info=True`, print a clean message to stderr, exit 1)
- Never swallow exceptions silently — log then re-raise or exit

**You need to know:**
- **`requests.exceptions.RequestException`**: the base class for all requests errors (connection, timeout, HTTP error) — catching it gives you a single handler for all network failures
- **`exc_info=True`**: a flag on `logger.error()` that appends the full traceback to the log message — essential for diagnosing production failures without exposing it to users
- **`sys.exit(1)`**: terminates the process with a non-zero exit code that signals failure to the shell or any calling script
- **`ValidationError.errors()`**: returns a list of dicts, each describing one field that failed validation — log this for actionable debug output

<details>
<summary>💡 Hint</summary>

In `main()`, the pattern is: `try: args.func(args)` / `except KeyboardInterrupt: sys.exit(0)` / `except Exception as e: logger.error(..., exc_info=True); print(f"Error: {e}", file=sys.stderr); sys.exit(1)`. The tricky part: `logger.error(str(e), exc_info=True)` logs the message AND the traceback — the traceback goes to the log file where it is useful; the `print` to stderr gives the user a clean one-liner.

</details>

---

## Step 9: Testing with Mocks

> Tests with mocks are like rehearsals with stand-ins: you control exactly what the "API" returns so your real logic gets tested in isolation, every time, without network costs.

**Requirements:**
- Create `tests/test_fetch.py`: use `unittest.mock.patch` to replace `requests.get` with a `MagicMock` returning a fake API response; write tests for (a) success, (b) retry on `Timeout` then success, (c) exhausted retries raising `Timeout`
- Create `tests/test_schemas.py`: test `WeatherResponse.model_validate` with valid data and with mismatched array lengths (expect `ValidationError`)
- Create `tests/test_process.py`: build a synthetic DataFrame with `pd.date_range` and test that `compute_daily_summary` returns the right number of rows and columns, and handles an empty DataFrame
- Patch `time.sleep` in retry tests so the test suite does not actually wait

**You need to know:**
- **`unittest.mock.patch`**: a context manager (or decorator) that temporarily replaces a named object with a `MagicMock` for the duration of a test, then restores the original
- **`MagicMock`**: a mock object that accepts any attribute access or method call and returns configurable values — set return values with `.return_value` and sequences with `.side_effect`
- **`side_effect`**: a list or callable on a mock; when a list, each call consumes the next item — use it to simulate fail-then-succeed sequences
- **`mock.assert_called_once()`**: asserts the mock was called exactly once — use it to verify the right code path was taken, not just that the result is correct

<details>
<summary>💡 Hint</summary>

Patch the function at the point of use, not the definition: `patch("pipeline.fetch.requests.get", ...)` not `patch("requests.get", ...)`. For the retry-then-succeed test: `mock_get.side_effect = [Timeout(), Timeout(), mock_response]` — the third element is a `MagicMock` with `.json.return_value = MOCK_RESPONSE` and `.raise_for_status.return_value = None`. Also patch `pipeline.fetch.time.sleep` to skip the backoff delays.

</details>

---

## Step 10: Packaging

> Packaging is graduating from a script you run with `python cli.py` to a tool you install and run as `weather-pipeline` from anywhere — the same way `git` or `pytest` works.

**Requirements:**
- Create `pyproject.toml` with `[build-system]` using `hatchling`, a `[project]` section listing all runtime dependencies, and a `[project.scripts]` entry point `weather-pipeline = "pipeline.cli:main"`
- Add an optional `[dev]` dependency group containing `pytest` and `pytest-cov`
- Install with `pip install -e .` (editable) and verify `weather-pipeline --help` works from the terminal
- Verify `which weather-pipeline` resolves to a path inside your virtual environment

**You need to know:**
- **`pyproject.toml`**: the modern Python packaging standard (PEP 517/518) that replaces `setup.py` — it declares build system, metadata, and dependencies in one file
- **`[project.scripts]`**: the section that creates console-script entry points — pip generates a wrapper executable in the venv's `bin/` directory that calls the named Python function
- **editable install (`-e`)**: installs the package as a live link to your source directory so code changes are reflected immediately without reinstalling
- **`hatchling`**: a modern, standards-compliant build backend that requires zero configuration for simple projects

<details>
<summary>💡 Hint</summary>

The entry point format is `command-name = "package.module:function"` — for this project: `weather-pipeline = "pipeline.cli:main"`. The `pipeline` here refers to the `pipeline/` directory (a Python package), not the top-level project name. Make sure `pipeline/__init__.py` exists (even if empty). After `pip install -e .`, run `which weather-pipeline` — it should point inside your `.venv/bin/` directory.

</details>

---

## Full Solution

<details>
<summary>✅ Complete solution — only open after you've tried</summary>

### Project structure

```
03_Data_Pipeline_CLI/
├── pyproject.toml
├── cli.py
├── pipeline/
│   ├── __init__.py
│   ├── fetch.py
│   ├── schemas.py
│   ├── database.py
│   ├── process.py
│   ├── report.py
│   └── logging_config.py
└── tests/
    ├── test_fetch.py
    ├── test_schemas.py
    └── test_process.py
```

---

### cli.py

```python
import argparse
import logging
import sys

logger = logging.getLogger(__name__)


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        prog="weather-pipeline",
        description="Fetch, process, and report on weather data.",
    )
    parser.add_argument(
        "--log-level",
        choices=["DEBUG", "INFO", "WARNING", "ERROR"],
        default="INFO",
        help="Set logging verbosity",
    )

    subparsers = parser.add_subparsers(dest="command", metavar="COMMAND")
    subparsers.required = True  # ← error if no subcommand given

    # --- fetch ---
    fetch_parser = subparsers.add_parser("fetch", help="Download data from Open Meteo")
    fetch_parser.add_argument("--lat", type=float, required=True)
    fetch_parser.add_argument("--lon", type=float, required=True)
    fetch_parser.add_argument("--days", type=int, default=7)
    fetch_parser.add_argument("--location", type=str, default="default")

    # --- process ---
    process_parser = subparsers.add_parser("process", help="Aggregate stored data")
    process_parser.add_argument("--location", type=str, default=None)

    # --- report ---
    report_parser = subparsers.add_parser("report", help="Generate a report")
    report_parser.add_argument("--location", type=str, default=None)
    report_parser.add_argument("--format", choices=["table", "csv"], default="table")
    report_parser.add_argument("--output", type=str, default=None)

    return parser


def main():
    parser = build_parser()
    args = parser.parse_args()

    from pipeline.logging_config import setup_logging
    setup_logging(level=args.log_level)  # ← must come before any other imports that log

    try:
        if args.command == "fetch":
            from pipeline.fetch import run_fetch
            run_fetch(args)
        elif args.command == "process":
            from pipeline.process import run_process
            run_process(args)
        elif args.command == "report":
            from pipeline.report import run_report
            run_report(args)
    except KeyboardInterrupt:
        print("\nAborted.")
        sys.exit(0)
    except Exception as e:
        logger.error(f"Fatal error: {e}", exc_info=True)  # ← full traceback to log file
        print(f"Error: {e}", file=sys.stderr)              # ← clean one-liner to terminal
        sys.exit(1)


if __name__ == "__main__":
    main()
```

---

### pipeline/fetch.py

```python
import logging
import requests
from requests.adapters import HTTPAdapter
from urllib3.util.retry import Retry
from pydantic import ValidationError

logger = logging.getLogger(__name__)

BASE_URL = "https://api.open-meteo.com/v1/forecast"


def _build_session() -> requests.Session:
    """Create a session with automatic retry on transient server errors."""
    session = requests.Session()
    retry = Retry(
        total=3,               # ← max 3 attempts
        backoff_factor=1,      # ← wait 1s, 2s, 4s between retries
        status_forcelist=[500, 502, 503, 504],  # ← retry only on server errors
    )
    adapter = HTTPAdapter(max_retries=retry)
    session.mount("https://", adapter)  # ← applies to all HTTPS requests
    return session


def fetch_weather(lat: float, lon: float, past_days: int = 7) -> dict:
    """Fetch hourly weather data from Open Meteo. Returns raw API dict."""
    params = {
        "latitude": lat,
        "longitude": lon,
        "hourly": "temperature_2m,windspeed_10m,precipitation",
        "past_days": past_days,
        "forecast_days": 1,
        "timezone": "UTC",
    }
    session = _build_session()
    logger.info(f"Fetching weather (lat={lat}, lon={lon}, past_days={past_days})")
    try:
        response = session.get(BASE_URL, params=params, timeout=10)  # ← 10s hard timeout
        response.raise_for_status()  # ← raises HTTPError for 4xx/5xx
    except requests.exceptions.RequestException as e:
        logger.error(f"HTTP request failed: {e}")
        raise
    data = response.json()
    logger.info(f"Fetched {len(data.get('hourly', {}).get('time', []))} hourly records")
    return data


def validate_response(raw_data: dict, location: str) -> list:
    """Validate raw API dict against Pydantic schema. Returns list of WeatherRecord."""
    from pipeline.schemas import WeatherResponse, WeatherRecord
    try:
        response = WeatherResponse.model_validate(raw_data)  # ← raises ValidationError if bad
    except ValidationError as e:
        logger.error(f"API response validation failed: {e.errors()}")
        raise
    hourly = response.hourly
    records = [
        WeatherRecord.from_hourly(
            location=location,
            time_str=hourly.time[i],
            temperature=hourly.temperature_2m[i],
            windspeed=hourly.windspeed_10m[i],
            precipitation=hourly.precipitation[i],
        )
        for i in range(len(hourly.time))
    ]
    logger.info(f"Validated {len(records)} records for location '{location}'")
    return records


def run_fetch(args) -> None:
    """Entry point called from CLI."""
    raw = fetch_weather(lat=args.lat, lon=args.lon, past_days=args.days)
    records = validate_response(raw, location=args.location)
    from pipeline.database import save_records
    inserted = save_records(records)
    print(f"Fetched and stored {inserted} new records for '{args.location}'")
```

---

### pipeline/schemas.py

```python
from pydantic import BaseModel, model_validator
from datetime import datetime


class HourlyData(BaseModel):
    time: list[str]
    temperature_2m: list[float | None]
    windspeed_10m: list[float | None]
    precipitation: list[float | None]

    @model_validator(mode="after")           # ← runs after all fields are validated
    def all_lists_same_length(self) -> "HourlyData":
        lengths = {
            len(self.time),
            len(self.temperature_2m),
            len(self.windspeed_10m),
            len(self.precipitation),
        }
        if len(lengths) != 1:               # ← set with >1 element means unequal lengths
            raise ValueError("All hourly arrays must have the same length")
        return self                          # ← must return self in mode="after"


class WeatherResponse(BaseModel):
    latitude: float
    longitude: float
    timezone: str
    hourly: HourlyData


class WeatherRecord(BaseModel):
    """One validated row, ready for DB insertion."""
    location: str
    timestamp: datetime
    temperature_c: float | None
    windspeed_kmh: float | None
    precipitation_mm: float | None

    @classmethod
    def from_hourly(
        cls,
        location: str,
        time_str: str,
        temperature: float | None,
        windspeed: float | None,
        precipitation: float | None,
    ) -> "WeatherRecord":
        return cls(
            location=location,
            timestamp=datetime.fromisoformat(time_str),  # ← parse ISO 8601 string
            temperature_c=temperature,
            windspeed_kmh=windspeed,
            precipitation_mm=precipitation,
        )
```

---

### pipeline/database.py

```python
import logging
from datetime import datetime
from sqlalchemy import create_engine, String, Float, DateTime, Integer
from sqlalchemy.orm import DeclarativeBase, Mapped, mapped_column, sessionmaker, Session

logger = logging.getLogger(__name__)

DATABASE_URL = "sqlite:///./weather_pipeline.db"
engine = create_engine(
    DATABASE_URL,
    connect_args={"check_same_thread": False},  # ← required for SQLite in multi-threaded use
)
SessionLocal = sessionmaker(bind=engine)  # ← factory; call SessionLocal() to get a session


class Base(DeclarativeBase):
    pass


class WeatherObservation(Base):
    __tablename__ = "weather_observations"

    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    location: Mapped[str] = mapped_column(String(100), nullable=False, index=True)
    timestamp: Mapped[datetime] = mapped_column(DateTime, nullable=False, index=True)
    temperature_c: Mapped[float | None] = mapped_column(Float)
    windspeed_kmh: Mapped[float | None] = mapped_column(Float)
    precipitation_mm: Mapped[float | None] = mapped_column(Float)


def init_db() -> None:
    """Create all tables if they do not already exist."""
    Base.metadata.create_all(bind=engine)
    logger.debug("Database tables ensured.")


def get_session() -> Session:
    return SessionLocal()


def save_records(records: list) -> int:
    """
    Insert validated WeatherRecord objects. Skips duplicates.
    Returns count of newly inserted rows.
    """
    init_db()
    session = get_session()
    inserted = 0
    try:
        for record in records:
            exists = (
                session.query(WeatherObservation)
                .filter_by(location=record.location, timestamp=record.timestamp)
                .first()
            )
            if not exists:
                session.add(WeatherObservation(**record.model_dump()))  # ← Pydantic v2 serialise
                inserted += 1
        session.commit()
        logger.info(f"Inserted {inserted} rows (skipped {len(records) - inserted} duplicates)")
    except Exception as e:
        session.rollback()   # ← undo partial inserts before re-raising
        logger.error(f"DB insert failed: {e}")
        raise
    finally:
        session.close()
    return inserted
```

---

### pipeline/process.py

```python
import logging
import pandas as pd
from pipeline.database import WeatherObservation, get_session, init_db

logger = logging.getLogger(__name__)


def load_to_dataframe(location: str | None = None) -> pd.DataFrame:
    """Load observations from SQLite into a DataFrame with a DatetimeIndex."""
    init_db()
    session = get_session()
    try:
        query = session.query(WeatherObservation)
        if location:
            query = query.filter(WeatherObservation.location == location)
        rows = query.all()
        if not rows:
            return pd.DataFrame()
        data = [
            {
                "location": r.location,
                "timestamp": r.timestamp,
                "temperature_c": r.temperature_c,
                "windspeed_kmh": r.windspeed_kmh,
                "precipitation_mm": r.precipitation_mm,
            }
            for r in rows
        ]
        df = pd.DataFrame(data)
        df["timestamp"] = pd.to_datetime(df["timestamp"])
        df.set_index("timestamp", inplace=True)  # ← resample requires a DatetimeIndex
        df.sort_index(inplace=True)
        return df
    finally:
        session.close()


def compute_daily_summary(df: pd.DataFrame) -> pd.DataFrame:
    """Resample hourly rows into daily aggregates."""
    if df.empty:
        return pd.DataFrame()
    daily = (
        df.resample("D")  # ← bin by calendar day
        .agg(
            temp_mean=("temperature_c", "mean"),
            temp_min=("temperature_c", "min"),
            temp_max=("temperature_c", "max"),
            wind_mean=("windspeed_kmh", "mean"),
            precip_total=("precipitation_mm", "sum"),
        )
        .round(2)
    )
    return daily


def run_process(args) -> pd.DataFrame:
    """Entry point called from CLI."""
    location = getattr(args, "location", None)
    df = load_to_dataframe(location=location)
    if df.empty:
        logger.warning("No data found. Run 'fetch' first.")
        print("No data to process. Run 'fetch' first.")
        return pd.DataFrame()
    daily = compute_daily_summary(df)
    logger.info(f"Processed {len(df)} hourly rows into {len(daily)} daily summaries")
    return daily
```

---

### pipeline/report.py

```python
import sys
import logging
import pandas as pd
from tabulate import tabulate
from pipeline.process import load_to_dataframe, compute_daily_summary

logger = logging.getLogger(__name__)


def format_table(daily: pd.DataFrame) -> str:
    """Render daily summary as a GitHub-style Markdown table."""
    display = daily.reset_index()  # ← move DatetimeIndex back to a column
    display["timestamp"] = display["timestamp"].dt.strftime("%Y-%m-%d")
    display.columns = [
        "Date", "Temp Mean °C", "Temp Min °C", "Temp Max °C",
        "Wind Mean km/h", "Precip Total mm",
    ]
    return tabulate(display, headers="keys", tablefmt="github", showindex=False)


def run_report(args) -> None:
    """Entry point called from CLI."""
    location = getattr(args, "location", None)
    output_format = getattr(args, "format", "table")
    output_file = getattr(args, "output", None)

    df = load_to_dataframe(location=location)
    if df.empty:
        print("No data available. Run 'fetch' first.")
        return

    daily = compute_daily_summary(df)

    if output_format == "csv":
        content = daily.to_csv()   # ← returns string when no path given
        if output_file:
            with open(output_file, "w") as f:
                f.write(content)
            print(f"CSV saved to {output_file}")
        else:
            print(content)
    else:
        table = format_table(daily)
        if output_file:
            with open(output_file, "w") as f:
                f.write(table)
            print(f"Report saved to {output_file}")
        else:
            print(table)
```

---

### pipeline/logging_config.py

```python
import logging
import logging.handlers
from pathlib import Path

LOG_DIR = Path("./logs")


def setup_logging(level: str = "INFO") -> None:
    """
    Configure root logger with two handlers:
    - Console: level from CLI flag
    - File: always DEBUG, rotating at 5 MB
    """
    LOG_DIR.mkdir(exist_ok=True)
    numeric_level = getattr(logging, level.upper(), logging.INFO)  # ← "DEBUG" → 10

    root = logging.getLogger()
    root.setLevel(logging.DEBUG)  # ← root must be DEBUG; handlers apply their own floor

    console = logging.StreamHandler()
    console.setLevel(numeric_level)
    console.setFormatter(logging.Formatter("%(levelname)-8s %(name)s — %(message)s"))

    file_handler = logging.handlers.RotatingFileHandler(
        LOG_DIR / "pipeline.log",
        maxBytes=5 * 1024 * 1024,  # ← 5 MB per file
        backupCount=3,              # ← keep pipeline.log, pipeline.log.1, .2, .3
        encoding="utf-8",
    )
    file_handler.setLevel(logging.DEBUG)
    file_handler.setFormatter(
        logging.Formatter("%(asctime)s | %(levelname)-8s | %(name)s | %(message)s")
    )

    root.addHandler(console)
    root.addHandler(file_handler)
```

---

### tests/test_fetch.py

```python
import pytest
from unittest.mock import patch, MagicMock
from pipeline.fetch import fetch_weather
from requests.exceptions import Timeout

MOCK_RESPONSE = {
    "latitude": 51.5,
    "longitude": -0.1,
    "timezone": "UTC",
    "hourly": {
        "time": ["2024-01-01T00:00", "2024-01-01T01:00"],
        "temperature_2m": [10.5, 11.0],
        "windspeed_10m": [15.2, 14.8],
        "precipitation": [0.0, 0.2],
    },
}


def _make_mock_response():
    """Helper: MagicMock that looks like a successful requests.Response."""
    m = MagicMock()
    m.json.return_value = MOCK_RESPONSE
    m.raise_for_status.return_value = None  # ← no-op: no error raised
    return m


def test_fetch_success():
    with patch("pipeline.fetch.requests.Session") as mock_session_cls:
        mock_session = MagicMock()
        mock_session_cls.return_value = mock_session
        mock_session.get.return_value = _make_mock_response()

        result = fetch_weather(lat=51.5, lon=-0.1, past_days=1)

    assert result["hourly"]["time"] == ["2024-01-01T00:00", "2024-01-01T01:00"]


def test_fetch_raises_on_network_error():
    with patch("pipeline.fetch.requests.Session") as mock_session_cls:
        mock_session = MagicMock()
        mock_session_cls.return_value = mock_session
        mock_session.get.side_effect = Timeout()  # ← always fails

        with pytest.raises(Timeout):
            fetch_weather(lat=51.5, lon=-0.1, past_days=1)
```

---

### tests/test_schemas.py

```python
import pytest
from pydantic import ValidationError
from pipeline.schemas import WeatherResponse

VALID = {
    "latitude": 51.5,
    "longitude": -0.1,
    "timezone": "UTC",
    "hourly": {
        "time": ["2024-01-01T00:00"],
        "temperature_2m": [10.5],
        "windspeed_10m": [15.0],
        "precipitation": [0.0],
    },
}


def test_valid_response_parses():
    r = WeatherResponse.model_validate(VALID)
    assert r.latitude == 51.5
    assert len(r.hourly.time) == 1


def test_mismatched_array_lengths_raises():
    bad = {
        **VALID,
        "hourly": {**VALID["hourly"], "temperature_2m": [10.5, 11.0]},  # ← length 2 vs 1
    }
    with pytest.raises(ValidationError):
        WeatherResponse.model_validate(bad)


def test_none_values_allowed():
    with_nulls = {
        **VALID,
        "hourly": {**VALID["hourly"], "temperature_2m": [None]},
    }
    r = WeatherResponse.model_validate(with_nulls)
    assert r.hourly.temperature_2m[0] is None
```

---

### tests/test_process.py

```python
import pandas as pd
from pipeline.process import compute_daily_summary


def make_df(hours: int = 48) -> pd.DataFrame:
    """Build a synthetic hourly DataFrame spanning `hours` hours."""
    timestamps = pd.date_range("2024-01-01", periods=hours, freq="h")
    return pd.DataFrame(
        {
            "temperature_c": [10.0 + i * 0.1 for i in range(hours)],
            "windspeed_kmh": [15.0] * hours,
            "precipitation_mm": [0.0] * hours,
        },
        index=timestamps,  # ← DatetimeIndex required for resample
    )


def test_daily_summary_row_count():
    df = make_df(hours=48)
    daily = compute_daily_summary(df)
    assert len(daily) == 2  # ← 48 hours = 2 full calendar days


def test_daily_summary_columns():
    daily = compute_daily_summary(make_df())
    assert set(daily.columns) == {"temp_mean", "temp_min", "temp_max", "wind_mean", "precip_total"}


def test_empty_dataframe_returns_empty():
    result = compute_daily_summary(pd.DataFrame())
    assert result.empty
```

---

### pyproject.toml

```toml
[build-system]
requires = ["hatchling"]
build-backend = "hatchling.build"

[project]
name = "weather-pipeline"
version = "0.1.0"
description = "CLI tool for fetching and reporting weather data"
requires-python = ">=3.11"
dependencies = [
    "requests>=2.31.0",
    "pydantic>=2.0.0",
    "sqlalchemy>=2.0.0",
    "pandas>=2.0.0",
    "tabulate>=0.9.0",
]

[project.optional-dependencies]
dev = [
    "pytest>=7.0.0",
    "pytest-cov>=4.0.0",
]

[project.scripts]
weather-pipeline = "pipeline.cli:main"  # ← creates the `weather-pipeline` executable

[tool.hatch.build.targets.wheel]
packages = ["pipeline"]
```

### Install and verify

```bash
pip install -e ".[dev]"       # editable install + dev deps
weather-pipeline --help       # should print usage
which weather-pipeline        # should point inside .venv/bin/
pytest tests/ -v              # all tests should pass
```

</details>

---

## Navigation

| | |
|---|---|
| Back | [README.md](./README.md) |
| Architecture | [Architecture.md](./Architecture.md) |
| Starter Code | [starter_code/cli.py](./starter_code/cli.py) |
