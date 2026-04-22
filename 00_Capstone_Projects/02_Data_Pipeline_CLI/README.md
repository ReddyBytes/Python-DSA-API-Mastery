# Project 02: Data Pipeline CLI Tool

A command-line tool that fetches weather data from a public API, processes it with pandas, stores it to SQLite, and generates reports. No API key required.

---

## What You Will Build

A fully packaged Python CLI application:

```bash
# Fetch 7 days of hourly weather data for a location
weather-pipeline fetch --lat 51.5 --lon -0.1 --days 7

# Process and aggregate the stored data
weather-pipeline process --location "London"

# Generate a text report and CSV export
weather-pipeline report --location "London" --format csv
```

---

## Skills Exercised

| Skill | Where it appears |
|-------|-----------------|
| argparse | CLI subcommands with typed arguments |
| requests + retry | HTTP client with exponential backoff |
| Pydantic v2 | Validating API response data |
| SQLAlchemy ORM | SQLite storage layer |
| pandas | Time-series aggregation, resampling |
| logging | File + console handlers, configurable level |
| unittest.mock | Mocking HTTP calls in tests |
| pyproject.toml | Packaging and `pip install -e .` |
| Error handling | Network, data, and DB failures |

---

## The API: Open Meteo

[Open Meteo](https://open-meteo.com/) is a free, no-auth weather API. Example call:

```
GET https://api.open-meteo.com/v1/forecast
    ?latitude=51.5
    &longitude=-0.1
    &hourly=temperature_2m,windspeed_10m,precipitation
    &past_days=7
```

Returns JSON with hourly arrays. No API key. No rate limits for reasonable use.

---

## Prerequisites

| Skill | Where to learn it |
|-------|------------------|
| Python functions + modules | `python-complete-mastery/04_functions` |
| Pydantic | `python-complete-mastery/14_type_hints_and_pydantic` |
| File handling | `python-complete-mastery/08_file_handling` |
| Logging | `python-complete-mastery/09_logging_debugging` |
| Testing with mocks | `python-complete-mastery/17_testing` |

---

## Project Structure

```
02_Data_Pipeline_CLI/
├── README.md               ← this file
├── Project_Guide.md        ← step-by-step build instructions
├── Architecture.md         ← component diagram, data flow, design patterns
└── starter_code/
    └── cli.py              ← runnable skeleton
```

---

## Tech Stack

| Tool | Version | Purpose |
|------|---------|---------|
| Python | 3.11+ | Language |
| requests | 2.x | HTTP client |
| Pydantic | 2.x | Data validation |
| SQLAlchemy | 2.0+ | ORM (SQLite) |
| pandas | 2.x | Data processing |
| tabulate | 0.9+ | Pretty-print tables |
| pytest | 7+ | Testing |
| unittest.mock | stdlib | Mock HTTP calls |

---

## How to Run (Starter Skeleton)

```bash
cd starter_code
pip install requests pydantic sqlalchemy pandas tabulate
python cli.py fetch --lat 51.5 --lon -0.1 --days 3
python cli.py process
python cli.py report
```

---

## How to Install as a Package (Step 10)

```bash
# From the project root
pip install -e .

# Now available anywhere as:
weather-pipeline fetch --lat 51.5 --lon -0.1 --days 7
weather-pipeline report --format csv
```

---

## Build Order

Follow `Project_Guide.md` step by step:

```
Step 1  →  CLI with argparse (3 subcommands)
Step 2  →  Fetch from Open Meteo with retry logic
Step 3  →  Pydantic validation of API response
Step 4  →  Store to SQLite via SQLAlchemy
Step 5  →  pandas processing (aggregation, resampling)
Step 6  →  Report generation (text table + CSV)
Step 7  →  Logging (file + console)
Step 8  →  Error handling (network, data, DB)
Step 9  →  Tests with unittest.mock
Step 10 →  Package with pyproject.toml
```

---

## Navigation

| | |
|---|---|
| Back | [Capstone Projects](../README.md) |
| Build Guide | [Project_Guide.md](./Project_Guide.md) |
| Architecture | [Architecture.md](./Architecture.md) |
| Starter Code | [starter_code/cli.py](./starter_code/cli.py) |
| Previous Project | [01 — E-Commerce API](../01_Ecommerce_API_FastAPI/README.md) |
