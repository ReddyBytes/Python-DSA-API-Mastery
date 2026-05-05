# Project 02 — Architecture: Data Pipeline CLI Tool

---

## Component Diagram

```
  CLI Entry Point
  (cli.py)
       |
       | argparse routes to subcommand
       |
  +---------+-----------+----------+
  |         |           |          |
fetch     process     report    (shared)
  |         |           |
  |         |           +-- tabulate (text table)
  |         |           +-- pandas (to_csv)
  |         |
  |         +-- pandas (resample, agg)
  |         +-- SQLAlchemy (read)
  |
  +-- requests (HTTP GET)
  +-- Pydantic (validate response)
  +-- SQLAlchemy (write to SQLite)


  +-------------------------------+
  |         SQLite DB             |
  |   weather_pipeline.db         |
  |   table: weather_observations |
  |   id, location, timestamp,    |
  |   temperature_c, windspeed,   |
  |   precipitation_mm            |
  +-------------------------------+

  +-------------------------------+
  |         Open Meteo API        |
  |   GET /v1/forecast            |
  |   ?latitude=&longitude=       |
  |   &hourly=temperature_2m,     |
  |     windspeed_10m,precip      |
  |   &past_days=7                |
  +-------------------------------+
```

---

## Data Flow

```
Step 1: CLI parses arguments
         └── "fetch --lat 51.5 --lon -0.1 --days 7"

Step 2: fetch.fetch_weather(lat, lon, past_days)
         └── GET https://api.open-meteo.com/v1/forecast?...
         └── Returns raw JSON dict

Step 3: schemas.WeatherResponse.model_validate(raw_data)
         └── Validates structure and types
         └── Raises ValidationError on bad data
         └── Returns list[WeatherRecord] (one per hour)

Step 4: database.save_records(records)
         └── Opens SQLite session
         └── Skips duplicates (location + timestamp unique check)
         └── Bulk inserts new rows
         └── Commits, closes session

Step 5 (process command):
        process.load_to_dataframe(location)
         └── SELECT * FROM weather_observations
         └── Returns pandas DataFrame, indexed by timestamp

        process.compute_daily_summary(df)
         └── df.resample("D").agg(...)
         └── Returns daily aggregates DataFrame

Step 6 (report command):
        report.run_report(args)
         └── Calls process.load_to_dataframe + compute_daily_summary
         └── Formats as text table (tabulate) OR csv (pandas.to_csv)
         └── Prints to stdout or writes to file
```

---

## Module Structure

```
weather-pipeline/
├── pipeline/
│   ├── __init__.py
│   ├── cli.py              ← argparse entry point, main()
│   ├── fetch.py            ← HTTP client, retry logic
│   ├── schemas.py          ← Pydantic validation models
│   ├── database.py         ← SQLAlchemy models + session factory
│   ├── process.py          ← pandas aggregation
│   ├── report.py           ← output formatting
│   └── logging_config.py   ← file + console handlers
├── tests/
│   ├── test_fetch.py       ← mocked HTTP tests
│   ├── test_schemas.py     ← Pydantic validation tests
│   └── test_process.py     ← pandas logic tests
├── logs/                   ← created at runtime
│   └── pipeline.log
├── pyproject.toml
└── weather_pipeline.db     ← created at runtime
```

---

## Design Patterns

### Command Pattern (CLI subcommands)

Each subcommand (`fetch`, `process`, `report`) is a separate module with a single `run_*` entry point. The CLI dispatcher in `main()` selects which command to execute at runtime. This mirrors the **Command** design pattern: the caller (CLI) does not need to know how each command is implemented.

```
main() {
    if args.command == "fetch"   → run_fetch(args)
    if args.command == "process" → run_process(args)
    if args.command == "report"  → run_report(args)
}
```

Adding a new subcommand means adding one parser + one module — nothing else changes.

### Strategy Pattern (output format)

The report module selects an output strategy at runtime based on `--format`:

```
run_report(args)
    |
    +-- if format == "csv"   → pandas.to_csv()     (CSV Strategy)
    +-- if format == "table" → tabulate()           (Table Strategy)
```

If you later add `--format json` or `--format html`, you add one branch — no rewiring.

### Pipeline Pattern (data flow)

The three commands form a sequential pipeline. Each stage transforms the data and passes it to the next:

```
Raw HTTP response
      ↓
Pydantic models (validated Python objects)
      ↓
SQLite rows (persisted)
      ↓
pandas DataFrame (in-memory, time-indexed)
      ↓
Aggregated DataFrame (daily summaries)
      ↓
Text table or CSV (human-readable output)
```

Each stage has a clear input type and output type, making it independently testable.

---

## Key Technical Decisions

### Why SQLite and not a flat CSV?

SQLite gives you: deduplication (check by primary key before insert), fast filtered reads (`WHERE location = ?`), and zero infrastructure overhead — it's a single file. For a CLI tool that may run multiple times on the same data, a file-based database is the right tradeoff. PostgreSQL would be overkill here.

### Why resample("D") instead of groupby?

`pandas.resample` is purpose-built for time series with a DatetimeIndex. It handles edge cases that `groupby` misses: empty time buckets still appear in the result (filled with NaN), making gaps visible. With `groupby(df.index.date)`, silent gaps would be invisible.

### Why validate with Pydantic before inserting?

The Open Meteo API is reliable, but external APIs can change without warning: a field renamed, an array shortened, a null value added. Pydantic validation at the boundary means a schema change produces a clear `ValidationError` with a field-level message, not a silent wrong number stored in the database.

### Why use `with_for_update()` in fetch (skipped here)?

Unlike the e-commerce API which needs concurrency protection, this CLI is single-process. No locks needed. If you later add a scheduler running multiple instances, revisit this.

---

## Navigation

| | |
|---|---|
| Back | [README.md](./README.md) |
| Build Guide | [Project_Guide.md](./Project_Guide.md) |
| Starter Code | [starter_code/cli.py](./starter_code/cli.py) |
