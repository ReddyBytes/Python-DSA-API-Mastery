"""
Data Pipeline CLI — Starter Skeleton
======================================
Runnable with:
    pip install requests pydantic sqlalchemy pandas tabulate
    python cli.py fetch --lat 51.5 --lon -0.1 --days 3
    python cli.py process
    python cli.py report

This file gives you the full CLI wiring. Each subcommand calls a placeholder
function — replace them with the real implementations from Project_Guide.md.
"""

from __future__ import annotations

import argparse
import logging
import sys
import time
from datetime import datetime

# ---------------------------------------------------------------------------
# Logging (basic setup — Step 7 upgrades this to file + console handlers)
# ---------------------------------------------------------------------------

logging.basicConfig(
    level=logging.INFO,
    format="%(levelname)-8s %(name)s — %(message)s",
)
logger = logging.getLogger(__name__)

# ---------------------------------------------------------------------------
# Placeholder data structures (replace with full Pydantic models in Step 3)
# ---------------------------------------------------------------------------

# Simulated record for demonstration before DB is wired up
SAMPLE_RECORDS = [
    {"timestamp": "2024-01-01T00:00", "temperature_c": 10.5, "windspeed_kmh": 15.2, "precipitation_mm": 0.0},
    {"timestamp": "2024-01-01T01:00", "temperature_c": 10.8, "windspeed_kmh": 14.9, "precipitation_mm": 0.1},
    {"timestamp": "2024-01-01T02:00", "temperature_c": 11.1, "windspeed_kmh": 15.5, "precipitation_mm": 0.0},
]


# ---------------------------------------------------------------------------
# Subcommand handlers (stubs — each one is replaced step by step)
# ---------------------------------------------------------------------------


def run_fetch(args: argparse.Namespace) -> None:
    """
    Step 2: Call fetch_weather(lat, lon, past_days) from pipeline/fetch.py
    Step 3: Validate response with Pydantic WeatherResponse
    Step 4: Store records to SQLite via save_records()

    For now: simulate a successful fetch and print what was received.
    """
    logger.info(f"Fetching weather for lat={args.lat}, lon={args.lon}, days={args.days}")

    # --- SIMULATION (remove when fetch.py is implemented) ---
    logger.info("Simulating API call (replace with real requests.get in Step 2)...")
    time.sleep(0.5)  # pretend network latency
    record_count = args.days * 24  # hourly data
    print(f"[STUB] Fetched {record_count} simulated hourly records for location '{args.location}'")
    print("       Replace run_fetch() with real implementation in Step 2.")


def run_process(args: argparse.Namespace) -> None:
    """
    Step 4: Load rows from SQLite into a pandas DataFrame
    Step 5: compute_daily_summary(df) — resample to daily aggregates

    For now: compute aggregates from the hardcoded SAMPLE_RECORDS list.
    """
    location = getattr(args, "location", None)
    logger.info(f"Processing data for location: {location or 'all'}")

    # --- SIMULATION (remove when database.py + process.py are implemented) ---
    try:
        import pandas as pd  # noqa: PLC0415
    except ImportError:
        print("pandas not installed. Run: pip install pandas")
        sys.exit(1)

    df = pd.DataFrame(SAMPLE_RECORDS)
    df["timestamp"] = pd.to_datetime(df["timestamp"])
    df.set_index("timestamp", inplace=True)

    daily = df.resample("D").agg(
        temp_mean=("temperature_c", "mean"),
        temp_min=("temperature_c", "min"),
        temp_max=("temperature_c", "max"),
        wind_mean=("windspeed_kmh", "mean"),
        precip_total=("precipitation_mm", "sum"),
    ).round(2)

    print(f"\n[STUB] Daily summary from sample data ({len(df)} hourly rows → {len(daily)} days):")
    print(daily.to_string())
    print("\nReplace run_process() with real DB load + pandas logic in Steps 4–5.")


def run_report(args: argparse.Namespace) -> None:
    """
    Step 5: Load daily summary DataFrame
    Step 6: Format as text table (tabulate) or CSV (pandas)

    For now: print a fixed sample report to stdout.
    """
    output_format = getattr(args, "format", "table")
    output_file = getattr(args, "output", None)
    location = getattr(args, "location", None)

    logger.info(f"Generating report — format={output_format}, location={location or 'all'}")

    # --- SIMULATION (remove when process.py + report.py are implemented) ---
    sample_report_table = """
| Date       | Temp Mean °C | Temp Min °C | Temp Max °C | Wind Mean km/h | Precip Total mm |
|------------|-------------|------------|------------|---------------|----------------|
| 2024-01-01 | 10.80       | 10.50      | 11.10      | 15.20         | 0.10           |
"""
    sample_report_csv = (
        "Date,Temp Mean °C,Temp Min °C,Temp Max °C,Wind Mean km/h,Precip Total mm\n"
        "2024-01-01,10.80,10.50,11.10,15.20,0.10\n"
    )

    if output_format == "csv":
        content = sample_report_csv
    else:
        content = sample_report_table

    if output_file:
        with open(output_file, "w") as f:
            f.write(content)
        print(f"[STUB] Report written to {output_file}")
    else:
        print(content)

    print("Replace run_report() with real implementation in Step 6.")


# ---------------------------------------------------------------------------
# CLI parser
# ---------------------------------------------------------------------------


def build_parser() -> argparse.ArgumentParser:
    """
    Build the full argument parser with three subcommands.
    Add more arguments to each subcommand as you build each step.
    """
    parser = argparse.ArgumentParser(
        prog="weather-pipeline",
        description="Fetch, process, and report on weather data from Open Meteo.",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  python cli.py fetch --lat 51.5 --lon -0.1 --days 7 --location London
  python cli.py process --location London
  python cli.py report --location London --format csv --output report.csv
  python cli.py report --format table
""",
    )

    # Global flag: applies to all subcommands
    parser.add_argument(
        "--log-level",
        choices=["DEBUG", "INFO", "WARNING", "ERROR"],
        default="INFO",
        metavar="LEVEL",
        help="Logging verbosity (default: INFO)",
    )

    subparsers = parser.add_subparsers(dest="command", metavar="COMMAND")
    subparsers.required = True

    # ------------------------------------------------------------------
    # Subcommand: fetch
    # ------------------------------------------------------------------
    fetch_parser = subparsers.add_parser(
        "fetch",
        help="Download weather data from the Open Meteo API and store it",
        description="Fetches hourly weather data (temperature, wind, precipitation) "
                    "for a given location and stores it in a local SQLite database.",
    )
    fetch_parser.add_argument(
        "--lat", type=float, required=True,
        help="Latitude of the location (e.g. 51.5 for London)",
    )
    fetch_parser.add_argument(
        "--lon", type=float, required=True,
        help="Longitude of the location (e.g. -0.1 for London)",
    )
    fetch_parser.add_argument(
        "--days", type=int, default=7,
        metavar="N",
        help="Number of past days to fetch (default: 7)",
    )
    fetch_parser.add_argument(
        "--location", type=str, default="default",
        help="Label for this location — used to identify stored records (default: 'default')",
    )

    # ------------------------------------------------------------------
    # Subcommand: process
    # ------------------------------------------------------------------
    process_parser = subparsers.add_parser(
        "process",
        help="Aggregate stored hourly data into daily summaries",
        description="Loads stored observations from the database and computes daily "
                    "aggregates: mean/min/max temperature, mean wind, total precipitation.",
    )
    process_parser.add_argument(
        "--location", type=str, default=None,
        help="Filter to a specific location label (default: all locations)",
    )

    # ------------------------------------------------------------------
    # Subcommand: report
    # ------------------------------------------------------------------
    report_parser = subparsers.add_parser(
        "report",
        help="Generate a text or CSV report from the stored data",
        description="Prints a formatted daily weather summary to stdout or a file.",
    )
    report_parser.add_argument(
        "--location", type=str, default=None,
        help="Filter to a specific location label (default: all locations)",
    )
    report_parser.add_argument(
        "--format", choices=["table", "csv"], default="table",
        help="Output format: 'table' (default) or 'csv'",
    )
    report_parser.add_argument(
        "--output", type=str, default=None,
        metavar="FILE",
        help="Write output to this file instead of stdout (optional)",
    )

    return parser


# ---------------------------------------------------------------------------
# Main entry point
# ---------------------------------------------------------------------------


def main() -> None:
    parser = build_parser()
    args = parser.parse_args()

    # Step 7: Replace this with setup_logging() from pipeline/logging_config.py
    logging.getLogger().setLevel(getattr(logging, args.log_level))
    logger.debug(f"Running command: {args.command}")

    try:
        if args.command == "fetch":
            run_fetch(args)
        elif args.command == "process":
            run_process(args)
        elif args.command == "report":
            run_report(args)
    except KeyboardInterrupt:
        print("\nAborted.")
        sys.exit(0)
    except Exception as e:
        # Step 8: Expand this with per-error-type handling
        logger.error(f"Fatal error: {e}", exc_info=(args.log_level == "DEBUG"))
        print(f"Error: {e}", file=sys.stderr)
        sys.exit(1)


if __name__ == "__main__":
    main()
