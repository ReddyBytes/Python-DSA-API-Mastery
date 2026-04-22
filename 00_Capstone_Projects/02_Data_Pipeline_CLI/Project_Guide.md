# Project 02 — Build Guide: Data Pipeline CLI Tool

Work through each step in order. Each step is runnable before the next one starts.

---

## Step 1: CLI Interface with argparse

Think of argparse as a receptionist: you walk up, say what you want (`fetch`, `process`, `report`), hand over your details (flags like `--lat`, `--days`), and it routes you to the right function.

### cli.py skeleton

```python
import argparse
import sys

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
    subparsers.required = True

    # --- fetch ---
    fetch_parser = subparsers.add_parser("fetch", help="Download data from Open Meteo API")
    fetch_parser.add_argument("--lat", type=float, required=True, help="Latitude")
    fetch_parser.add_argument("--lon", type=float, required=True, help="Longitude")
    fetch_parser.add_argument("--days", type=int, default=7, help="Number of past days to fetch")
    fetch_parser.add_argument("--location", type=str, default="default", help="Label for this location")

    # --- process ---
    process_parser = subparsers.add_parser("process", help="Aggregate stored data")
    process_parser.add_argument("--location", type=str, default=None, help="Filter by location label")

    # --- report ---
    report_parser = subparsers.add_parser("report", help="Generate a report")
    report_parser.add_argument("--location", type=str, default=None, help="Filter by location label")
    report_parser.add_argument(
        "--format",
        choices=["table", "csv"],
        default="table",
        help="Output format",
    )
    report_parser.add_argument("--output", type=str, default=None, help="Output file path (optional)")

    return parser


def main():
    parser = build_parser()
    args = parser.parse_args()

    if args.command == "fetch":
        from pipeline.fetch import run_fetch
        run_fetch(args)
    elif args.command == "process":
        from pipeline.process import run_process
        run_process(args)
    elif args.command == "report":
        from pipeline.report import run_report
        run_report(args)


if __name__ == "__main__":
    main()
```

### Test it immediately

```bash
python cli.py --help
python cli.py fetch --help
python cli.py fetch --lat 51.5 --lon -0.1  # will fail (module not found) — that's expected
```

---

## Step 2: Fetch from Open Meteo with Retry Logic

The fetch module is responsible for one thing: get data from the API and return it. **Retry logic** handles the real world — timeouts, transient 5xx errors, network blips.

### pipeline/fetch.py

```python
import time
import logging
import requests
from requests.exceptions import ConnectionError, Timeout, HTTPError

logger = logging.getLogger(__name__)

BASE_URL = "https://api.open-meteo.com/v1/forecast"

def fetch_weather(lat: float, lon: float, past_days: int = 7) -> dict:
    """
    Fetch hourly weather data from Open Meteo.
    Retries up to 3 times with exponential backoff on transient errors.
    """
    params = {
        "latitude": lat,
        "longitude": lon,
        "hourly": "temperature_2m,windspeed_10m,precipitation",
        "past_days": past_days,
        "forecast_days": 1,
        "timezone": "UTC",
    }

    max_retries = 3
    for attempt in range(1, max_retries + 1):
        try:
            logger.info(f"Fetching weather data (attempt {attempt}/{max_retries})...")
            response = requests.get(BASE_URL, params=params, timeout=10)
            response.raise_for_status()
            data = response.json()
            logger.info(f"Fetched {len(data.get('hourly', {}).get('time', []))} hourly records.")
            return data

        except (ConnectionError, Timeout) as e:
            logger.warning(f"Network error on attempt {attempt}: {e}")
            if attempt < max_retries:
                sleep_time = 2 ** attempt  # 2, 4, 8 seconds
                logger.info(f"Retrying in {sleep_time}s...")
                time.sleep(sleep_time)
            else:
                logger.error("All retry attempts exhausted.")
                raise

        except HTTPError as e:
            if response.status_code >= 500:
                logger.warning(f"Server error {response.status_code} on attempt {attempt}")
                if attempt < max_retries:
                    time.sleep(2 ** attempt)
                else:
                    raise
            else:
                # 4xx errors are client errors — do not retry
                logger.error(f"Client error: {e}")
                raise


def run_fetch(args) -> None:
    """Entry point called from CLI."""
    raw_data = fetch_weather(lat=args.lat, lon=args.lon, past_days=args.days)
    # Step 3: validate with Pydantic
    # Step 4: store to DB
    logger.info("Fetch complete.")
    print(f"Fetched {len(raw_data['hourly']['time'])} records for {args.location}")
```

---

## Step 3: Data Validation with Pydantic

The Open Meteo response has a known shape. Wrap it in Pydantic to catch bad data before it reaches your database.

### pipeline/schemas.py

```python
from pydantic import BaseModel, field_validator, model_validator
from datetime import datetime

class HourlyData(BaseModel):
    time: list[str]                   # ISO 8601 strings
    temperature_2m: list[float | None]
    windspeed_10m: list[float | None]
    precipitation: list[float | None]

    @model_validator(mode="after")
    def all_lists_same_length(self) -> "HourlyData":
        lengths = {
            len(self.time),
            len(self.temperature_2m),
            len(self.windspeed_10m),
            len(self.precipitation),
        }
        if len(lengths) != 1:
            raise ValueError("All hourly arrays must have the same length")
        return self

class WeatherResponse(BaseModel):
    latitude: float
    longitude: float
    timezone: str
    hourly: HourlyData

class WeatherRecord(BaseModel):
    """One validated row ready for DB insertion."""
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
            timestamp=datetime.fromisoformat(time_str),
            temperature_c=temperature,
            windspeed_kmh=windspeed,
            precipitation_mm=precipitation,
        )
```

### Integrate into fetch.py

```python
from pipeline.schemas import WeatherResponse, WeatherRecord
from pydantic import ValidationError

def validate_response(raw_data: dict, location: str) -> list[WeatherRecord]:
    try:
        response = WeatherResponse.model_validate(raw_data)
    except ValidationError as e:
        logger.error(f"API response validation failed: {e}")
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
    logger.info(f"Validated {len(records)} records.")
    return records
```

---

## Step 4: Store to SQLite with SQLAlchemy

### pipeline/database.py

```python
from sqlalchemy import create_engine, String, Float, DateTime, Integer
from sqlalchemy.orm import DeclarativeBase, Mapped, mapped_column, sessionmaker, Session
from datetime import datetime
import logging

logger = logging.getLogger(__name__)

DATABASE_URL = "sqlite:///./weather_pipeline.db"
engine = create_engine(DATABASE_URL, connect_args={"check_same_thread": False})
SessionLocal = sessionmaker(bind=engine)


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
    Base.metadata.create_all(bind=engine)
    logger.info("Database initialised.")


def get_session() -> Session:
    return SessionLocal()
```

### Bulk insert with upsert

```python
from pipeline.database import WeatherObservation, get_session, init_db
from pipeline.schemas import WeatherRecord

def save_records(records: list[WeatherRecord]) -> int:
    """
    Insert records. Skip duplicates (same location + timestamp).
    Returns the number of new rows inserted.
    """
    init_db()
    session = get_session()
    inserted = 0

    try:
        for record in records:
            exists = session.query(WeatherObservation).filter_by(
                location=record.location,
                timestamp=record.timestamp,
            ).first()
            if not exists:
                session.add(WeatherObservation(**record.model_dump()))
                inserted += 1
        session.commit()
        logger.info(f"Inserted {inserted} new records (skipped {len(records) - inserted} duplicates).")
    except Exception as e:
        session.rollback()
        logger.error(f"DB insert failed: {e}")
        raise
    finally:
        session.close()

    return inserted
```

---

## Step 5: Pandas Processing (Aggregation and Resampling)

### pipeline/process.py

```python
import pandas as pd
import logging
from pipeline.database import WeatherObservation, get_session, init_db

logger = logging.getLogger(__name__)


def load_to_dataframe(location: str | None = None) -> pd.DataFrame:
    """Load weather observations from SQLite into a pandas DataFrame."""
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
        df.set_index("timestamp", inplace=True)
        df.sort_index(inplace=True)
        return df
    finally:
        session.close()


def compute_daily_summary(df: pd.DataFrame) -> pd.DataFrame:
    """
    Resample hourly data to daily aggregates.
    Think of resample("D") as a GROUP BY date — it bins all hourly rows
    for a calendar day together and applies the aggregation function.
    """
    if df.empty:
        return pd.DataFrame()

    daily = df.resample("D").agg(
        temp_mean=("temperature_c", "mean"),
        temp_min=("temperature_c", "min"),
        temp_max=("temperature_c", "max"),
        wind_mean=("windspeed_kmh", "mean"),
        precip_total=("precipitation_mm", "sum"),
    ).round(2)

    return daily


def run_process(args) -> pd.DataFrame:
    """Entry point called from CLI."""
    df = load_to_dataframe(location=getattr(args, "location", None))
    if df.empty:
        logger.warning("No data found. Run 'fetch' first.")
        return pd.DataFrame()
    daily = compute_daily_summary(df)
    logger.info(f"Processed {len(df)} hourly records into {len(daily)} daily summaries.")
    return daily
```

---

## Step 6: Report Generation (Text Table + CSV)

### pipeline/report.py

```python
import sys
import logging
import pandas as pd
from tabulate import tabulate
from pipeline.process import load_to_dataframe, compute_daily_summary

logger = logging.getLogger(__name__)


def format_table(daily: pd.DataFrame) -> str:
    """Format daily summary as an aligned text table."""
    display = daily.reset_index()
    display["timestamp"] = display["timestamp"].dt.strftime("%Y-%m-%d")
    display.columns = ["Date", "Temp Mean °C", "Temp Min °C", "Temp Max °C",
                       "Wind Mean km/h", "Precip Total mm"]
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
        csv_content = daily.to_csv()
        if output_file:
            with open(output_file, "w") as f:
                f.write(csv_content)
            logger.info(f"CSV written to {output_file}")
            print(f"Report saved to {output_file}")
        else:
            print(csv_content)

    else:  # table
        table = format_table(daily)
        if output_file:
            with open(output_file, "w") as f:
                f.write(table)
            print(f"Report saved to {output_file}")
        else:
            print(table)
```

---

## Step 7: Logging Setup (File + Console)

### pipeline/logging_config.py

```python
import logging
import logging.handlers
from pathlib import Path

LOG_DIR = Path("./logs")


def setup_logging(level: str = "INFO") -> None:
    """
    Two handlers:
    - Console: INFO and above, coloured by level
    - File: DEBUG and above, rotating (max 5MB, 3 backups)
    """
    LOG_DIR.mkdir(exist_ok=True)
    numeric_level = getattr(logging, level.upper(), logging.INFO)

    root_logger = logging.getLogger()
    root_logger.setLevel(logging.DEBUG)  # root captures everything; handlers filter

    # Console handler
    console_handler = logging.StreamHandler()
    console_handler.setLevel(numeric_level)
    console_handler.setFormatter(
        logging.Formatter("%(levelname)-8s %(name)s — %(message)s")
    )

    # Rotating file handler
    file_handler = logging.handlers.RotatingFileHandler(
        LOG_DIR / "pipeline.log",
        maxBytes=5 * 1024 * 1024,  # 5 MB
        backupCount=3,
        encoding="utf-8",
    )
    file_handler.setLevel(logging.DEBUG)
    file_handler.setFormatter(
        logging.Formatter("%(asctime)s | %(levelname)-8s | %(name)s | %(message)s")
    )

    root_logger.addHandler(console_handler)
    root_logger.addHandler(file_handler)
```

### Wire into CLI (main function)

```python
def main():
    parser = build_parser()
    args = parser.parse_args()

    from pipeline.logging_config import setup_logging
    setup_logging(level=args.log_level)   # ← add this line

    logger = logging.getLogger(__name__)
    logger.debug(f"Command: {args.command}")
    ...
```

---

## Step 8: Error Handling (Network, Data, DB)

### Strategy per error type

| Error type | Where it occurs | What to do |
|------------|----------------|------------|
| `ConnectionError` / `Timeout` | `fetch_weather()` | Retry with backoff (already done in Step 2) |
| `HTTPError` 4xx | `fetch_weather()` | Log and exit — bad request, no retry |
| `ValidationError` | `validate_response()` | Log field errors, raise to caller |
| `SQLAlchemy` error | `save_records()` | Rollback, log, raise |
| Empty DataFrame | `run_process()` | Warn user, return early |
| Bad CLI args | argparse | argparse handles this automatically |

### Unified error exit in main()

```python
import sys

def main():
    parser = build_parser()
    args = parser.parse_args()

    from pipeline.logging_config import setup_logging
    setup_logging(level=args.log_level)
    logger = logging.getLogger(__name__)

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
        logger.error(f"Fatal error: {e}", exc_info=True)
        print(f"Error: {e}", file=sys.stderr)
        sys.exit(1)
```

---

## Step 9: Testing with unittest.mock

The rule: never make real HTTP calls in tests. Use `unittest.mock.patch` to replace `requests.get` with a fake that returns controlled data.

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


def test_fetch_success():
    mock_response = MagicMock()
    mock_response.json.return_value = MOCK_RESPONSE
    mock_response.raise_for_status.return_value = None

    with patch("pipeline.fetch.requests.get", return_value=mock_response) as mock_get:
        result = fetch_weather(lat=51.5, lon=-0.1, past_days=1)

    mock_get.assert_called_once()
    assert result["hourly"]["time"] == ["2024-01-01T00:00", "2024-01-01T01:00"]


def test_fetch_retries_on_timeout():
    mock_response = MagicMock()
    mock_response.json.return_value = MOCK_RESPONSE
    mock_response.raise_for_status.return_value = None

    # Fail twice, succeed on third attempt
    with patch("pipeline.fetch.requests.get") as mock_get:
        with patch("pipeline.fetch.time.sleep"):  # skip actual sleeping
            mock_get.side_effect = [Timeout(), Timeout(), mock_response]
            result = fetch_weather(lat=51.5, lon=-0.1, past_days=1)

    assert mock_get.call_count == 3
    assert result is not None


def test_fetch_raises_after_all_retries():
    with patch("pipeline.fetch.requests.get", side_effect=Timeout()):
        with patch("pipeline.fetch.time.sleep"):
            with pytest.raises(Timeout):
                fetch_weather(lat=51.5, lon=-0.1, past_days=1)
```

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


def test_valid_response():
    r = WeatherResponse.model_validate(VALID)
    assert r.latitude == 51.5


def test_mismatched_array_lengths():
    bad = {**VALID, "hourly": {**VALID["hourly"], "temperature_2m": [10.5, 11.0]}}
    with pytest.raises(ValidationError):
        WeatherResponse.model_validate(bad)
```

### tests/test_process.py

```python
import pandas as pd
import pytest
from datetime import datetime
from pipeline.process import compute_daily_summary


def make_df():
    timestamps = pd.date_range("2024-01-01", periods=48, freq="h")
    return pd.DataFrame({
        "location": ["London"] * 48,
        "temperature_c": [10.0 + i * 0.1 for i in range(48)],
        "windspeed_kmh": [15.0] * 48,
        "precipitation_mm": [0.0] * 48,
    }, index=timestamps)


def test_daily_summary_shape():
    df = make_df()
    daily = compute_daily_summary(df)
    assert len(daily) == 2  # 48 hours = 2 days
    assert "temp_mean" in daily.columns
    assert "precip_total" in daily.columns


def test_empty_dataframe():
    result = compute_daily_summary(pd.DataFrame())
    assert result.empty
```

### Run tests

```bash
pytest tests/ -v
pytest tests/ --tb=short -q  # quiet mode
```

---

## Step 10: Package with pyproject.toml

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
weather-pipeline = "pipeline.cli:main"

[tool.hatch.build.targets.wheel]
packages = ["pipeline"]
```

### Install in editable mode

```bash
pip install -e .               # install with live code edits
pip install -e ".[dev]"        # include test dependencies
weather-pipeline --help        # now works as a CLI command
```

### What `pip install -e .` does

The `-e` flag (editable install) creates a link from the Python environment back to your source folder. When you change a `.py` file, the installed package reflects it immediately — no reinstall needed. This is the standard workflow for developing Python packages.

---

## Navigation

| | |
|---|---|
| Back | [README.md](./README.md) |
| Architecture | [Architecture.md](./Architecture.md) |
| Starter Code | [starter_code/cli.py](./starter_code/cli.py) |
