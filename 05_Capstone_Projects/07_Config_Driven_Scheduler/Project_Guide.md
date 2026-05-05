# Project 07 — Config-Driven Job Scheduler

> A scheduler is like a kitchen timer panel — each timer is set independently, fires at its own time, and a single timer failing doesn't burn down the kitchen. The config-driven part means the chef can add new timers without rewiring the panel.

**Difficulty: Minimal Hints** — requirements + concepts + one collapsed hint per step. No answer per step. Full working solution at the very end.

---

## What You're Building

A **config-driven job scheduler** where all job definitions live in `jobs.yaml`. No code changes are needed to add, remove, or reschedule a job — only the YAML changes.

Features:
- Cron-style schedules (`"*/5 * * * *"`) and interval schedules (`every: 30s`)
- Each job specifies: name, schedule, Python function path, enabled flag, optional timeout
- `python scheduler.py` — loads config, starts all enabled jobs, runs forever
- `python scheduler.py --list` — prints all jobs with next scheduled run time
- `python scheduler.py --run <job_name>` — runs a specific job immediately, outside the scheduler
- Graceful shutdown on Ctrl+C (finishes the current job run before exiting)
- Each job run logs: start time, duration, success or failure
- A failed job does not stop other jobs

---

## Step 1 — Project Setup

### Requirements

- Create the following folder structure:

```
07_Config_Driven_Scheduler/
├── scheduler.py     # main entry point
├── jobs.yaml        # job definitions
└── tasks.py         # sample task functions
```

- Install the required libraries into a virtual environment.

### You Need to Know

- **APScheduler** is a Python job scheduling library that supports cron, interval, and date triggers — it manages a background thread pool that fires jobs on schedule.
- **PyYAML** parses `.yaml` files into Python dicts — `yaml.safe_load(file)` is the standard safe way to load YAML without executing arbitrary code.
- **click** is a Python library for building CLIs — it handles argument parsing and subcommands with decorators instead of `argparse` boilerplate.

<details>
<summary>💡 Hint</summary>

```bash
python -m venv venv && source venv/bin/activate
pip install apscheduler pyyaml click
```

</details>

---

## Step 2 — Define the `jobs.yaml` Schema

### Requirements

- Design a YAML structure that supports at least these fields per job: `name`, `schedule`, `function`, `enabled`, `timeout`
- `schedule` must support two formats: a cron string (e.g., `"*/5 * * * *"`) and a plain English interval (e.g., `every: 30s`, `every: 2m`, `every: 1h`)
- Write an example `jobs.yaml` with exactly three jobs: one cron, one interval, one disabled
- At least one job should have a timeout set

### You Need to Know

- **YAML anchors** (`&anchor` and `*anchor`) let you reuse values across entries — useful if multiple jobs share the same timeout.
- **Cron syntax** is five space-separated fields: minute, hour, day-of-month, month, day-of-week — `*/5 * * * *` means "every 5 minutes."
- A **function path string** like `"tasks.send_report"` encodes both the module name and the attribute name — you will split this string to dynamically import and call the function in Step 3.

<details>
<summary>💡 Hint</summary>

```yaml
jobs:
  - name: heartbeat
    schedule: "*/1 * * * *"
    function: "tasks.heartbeat"
    enabled: true
    timeout: 10

  - name: cleanup
    schedule: "every: 30s"
    function: "tasks.cleanup"
    enabled: true
    timeout: 20

  - name: weekly_report
    schedule: "0 9 * * 1"
    function: "tasks.weekly_report"
    enabled: false
    timeout: 60
```

The `every: 30s` format is custom — you will need to parse it yourself in Step 5.

</details>

---

## Step 3 — Load and Validate Config

### Requirements

- Write a function `load_config(path: str) -> list[dict]` that reads `jobs.yaml` using PyYAML
- Validate that each job entry has at minimum: `name`, `schedule`, `function`, `enabled`
- Raise a clear `ValueError` with the job name and missing field if validation fails
- Write a function `resolve_function(path: str) -> callable` that takes `"tasks.send_report"` and returns the actual callable
- If the module or attribute doesn't exist, raise a descriptive error — not a raw `ImportError`

### You Need to Know

- **`importlib.import_module(module_name)`** dynamically imports a module by string name at runtime — equivalent to `import tasks` but driven by a variable.
- **`getattr(module, attr_name)`** retrieves a named attribute from a module object — so `getattr(tasks_module, "send_report")` returns the function.
- **`yaml.safe_load`** returns a dict with a top-level key (whatever you named it in the YAML, e.g., `jobs`) — remember to access `data["jobs"]` not just `data`.

<details>
<summary>💡 Hint</summary>

To split `"tasks.send_report"` into module and attribute:

```python
module_path, func_name = path.rsplit(".", 1)  # ← split from the right, once
```

This correctly handles nested paths like `"myapp.jobs.reports.send_report"`.

</details>

---

## Step 4 — APScheduler Basics

### Requirements

- Instantiate a `BackgroundScheduler` from APScheduler
- Understand the difference between `trigger='cron'` and `trigger='interval'` and when you use each
- Know how to start the scheduler (`scheduler.start()`) and stop it cleanly (`scheduler.shutdown(wait=True)`)
- Know what `wait=True` means for in-progress jobs

### You Need to Know

- **`BackgroundScheduler`** runs all jobs in a background thread pool — your main thread stays free to handle CLI commands, signals, or a sleep loop.
- **`trigger='cron'`** accepts individual cron fields as kwargs (`minute`, `hour`, `day_of_week`, etc.) — it does not accept a raw cron string directly, so you must parse the string into these kwargs.
- **`trigger='interval'`** accepts time-unit kwargs (`seconds`, `minutes`, `hours`) — it fires the job repeatedly at a fixed interval from the moment it is first scheduled.
- **`scheduler.shutdown(wait=True)`** blocks until all currently running jobs finish before tearing down the thread pool — `wait=False` kills them immediately.

<details>
<summary>💡 Hint</summary>

To parse a raw cron string `"*/5 * * * *"` into APScheduler cron kwargs:

```python
from apscheduler.triggers.cron import CronTrigger

trigger = CronTrigger.from_crontab("*/5 * * * *")  # ← APScheduler has a built-in parser
```

This is simpler than splitting by hand.

</details>

---

## Step 5 — Register Jobs from Config

### Requirements

- Write a function `register_jobs(scheduler, config: list[dict])` that loops the validated config and adds each enabled job to the scheduler
- Detect the schedule type: if the string matches cron format, use `CronTrigger`; if it starts with `every:`, parse the interval and use `IntervalTrigger`
- Wrap each job's function in a logging wrapper that records: job name, start time (ISO format), wall-clock duration, and success or exception message
- The wrapper must catch all exceptions so one failing job cannot crash the scheduler
- Disabled jobs must be skipped entirely (not added to the scheduler)

### You Need to Know

- **`IntervalTrigger`** from APScheduler accepts `seconds=`, `minutes=`, or `hours=` as int kwargs — you will need to parse `"30s"`, `"2m"`, `"1h"` strings into the right kwarg.
- **`time.perf_counter()`** gives a high-resolution wall-clock time suitable for measuring duration — subtract the start value from the end value to get elapsed seconds.
- **Closures and late binding** are a Python gotcha in loops — if you reference `job` inside a lambda or nested function, all closures end up referencing the last `job` in the loop; capture the value with a default argument (`def wrapper(j=job): ...`).

<details>
<summary>💡 Hint</summary>

Parsing the `every:` format:

```python
def parse_interval(schedule_str: str) -> dict:
    # schedule_str example: "every: 30s"
    value_str = schedule_str.split(":")[1].strip()  # ← "30s"
    if value_str.endswith("s"):
        return {"seconds": int(value_str[:-1])}
    elif value_str.endswith("m"):
        return {"minutes": int(value_str[:-1])}
    elif value_str.endswith("h"):
        return {"hours": int(value_str[:-1])}
    raise ValueError(f"Unknown interval format: {value_str}")
```

</details>

---

## Step 6 — `--list` Command

### Requirements

- Implement `python scheduler.py --list` using click
- The command must start the scheduler, retrieve all registered jobs, print a formatted table, then shut down
- Each row in the table must show: job name, schedule string (from YAML), enabled status, next run time (human-readable)
- If a job is disabled (and therefore not registered), show "disabled" in the next-run column

### You Need to Know

- **`scheduler.get_jobs()`** returns a list of `apscheduler.job.Job` objects — each has a `.next_run_time` attribute (a `datetime` or `None`) and an `.id` attribute (the string you passed as `id=` when adding the job).
- **`datetime.isoformat()`** and **`datetime.strftime()`** both format a datetime to a string — `strftime("%Y-%m-%d %H:%M:%S")` is more human-readable for a table.
- You do not need to start the scheduler with `scheduler.start()` to inspect jobs — you can add jobs and read `.next_run_time` before calling `start()`, though the value may be computed lazily.

<details>
<summary>💡 Hint</summary>

Build a lookup from the registered job list so you can match config entries to their `next_run_time`:

```python
registered = {job.id: job for job in scheduler.get_jobs()}
for entry in config:
    job = registered.get(entry["name"])
    next_run = job.next_run_time.strftime("%Y-%m-%d %H:%M:%S") if job else "disabled"
```

</details>

---

## Step 7 — `--run` Command

### Requirements

- Implement `python scheduler.py --run <job_name>` using click
- Load config, find the job entry by name, resolve the function, call it directly (not through the scheduler)
- Record start time and wall-clock duration
- Print: `[job_name] started at <time>`, then either `[job_name] finished in <duration>s` or `[job_name] FAILED: <error message>`
- If the job name is not found in config, print a clear error and exit with a non-zero status code

### You Need to Know

- **`click.argument`** captures positional CLI arguments while **`click.option`** captures named flags — `--run job_name` is best modelled as an option, not a positional argument, so the user types `--run heartbeat`.
- **`sys.exit(1)`** exits the process with a failure status code — important for scripting so callers can detect failure.
- **`datetime.now().isoformat(timespec='seconds')`** produces a clean timestamp string like `2024-01-15T09:32:01` without microsecond noise.

<details>
<summary>💡 Hint</summary>

Find the job entry safely:

```python
entry = next((j for j in config if j["name"] == job_name), None)
if entry is None:
    click.echo(f"Error: job '{job_name}' not found in config", err=True)
    sys.exit(1)
```

</details>

---

## Step 8 — Graceful Shutdown

### Requirements

- Register signal handlers for both `SIGINT` (Ctrl+C) and `SIGTERM` (process kill) using the `signal` module
- The signal handler must set a `threading.Event` that the main loop polls
- The main loop should be `while not stop_event.is_set(): time.sleep(1)` — not a busy loop
- On receiving the signal, print a message like `Shutting down — waiting for running jobs to finish...`
- Call `scheduler.shutdown(wait=True)` before the process exits
- The process must exit cleanly — no tracebacks, no zombie threads

### You Need to Know

- **`signal.signal(signal.SIGINT, handler)`** registers a Python callable as the handler for Ctrl+C — the handler receives `(signum, frame)` as arguments.
- **`threading.Event`** is a thread-safe boolean flag — `.set()` flips it to True from any thread, `.is_set()` reads it, `.wait(timeout)` blocks until it is set or the timeout expires.
- Signal handlers in Python run in the main thread, so they can safely call `.set()` on an Event that other threads read — but they must not call blocking operations directly.

<details>
<summary>💡 Hint</summary>

```python
import signal, threading

stop_event = threading.Event()

def shutdown_handler(signum, frame):
    click.echo("\nShutting down — waiting for running jobs to finish...")
    stop_event.set()

signal.signal(signal.SIGINT, shutdown_handler)   # ← Ctrl+C
signal.signal(signal.SIGTERM, shutdown_handler)  # ← kill / systemd stop
```

</details>

---

## Step 9 — Job Wrapper with Timeout

### Requirements

- Extend the job wrapper from Step 5 to enforce the per-job `timeout` value from the YAML config
- If a job runs longer than its timeout (in seconds), cancel it and log a timeout error
- The job runner must not block the scheduler thread pool for longer than the timeout
- Jobs without a `timeout` field in YAML run without a time limit

### You Need to Know

- **`concurrent.futures.ThreadPoolExecutor`** runs a callable in a separate thread and returns a `Future` — calling `future.result(timeout=N)` blocks for at most N seconds before raising `concurrent.futures.TimeoutError`.
- **`threading.Timer`** is an alternative: it runs a callable after a delay — but it cannot actually kill a running thread; it can only set a flag that a cooperative function checks.
- Python threads cannot be forcibly killed from outside — the `ThreadPoolExecutor` approach raises `TimeoutError` in the waiting thread but the underlying thread keeps running until it finishes naturally; for true preemption you need a subprocess.

<details>
<summary>💡 Hint</summary>

```python
from concurrent.futures import ThreadPoolExecutor, TimeoutError as FuturesTimeoutError

def timed_wrapper(func, timeout):
    def run():
        with ThreadPoolExecutor(max_workers=1) as executor:
            future = executor.submit(func)
            try:
                future.result(timeout=timeout)  # ← blocks up to `timeout` seconds
            except FuturesTimeoutError:
                raise RuntimeError(f"Job exceeded timeout of {timeout}s")
    return run
```

</details>

---

## Step 10 — Test It

### Requirements

- Add a job to `jobs.yaml` with an interval of `every: 5s` that prints a timestamped message
- Run `python scheduler.py` and verify the job fires every 5 seconds with log output
- Run `python scheduler.py --list` and verify the table shows the correct next run time
- Run `python scheduler.py --run heartbeat` and verify it executes immediately with timing output
- Press Ctrl+C during a run and verify the shutdown message appears and the process exits cleanly
- Add a job that raises an exception and verify the scheduler keeps running other jobs

### You Need to Know

- **APScheduler's default misfire grace time** is 1 second — if the scheduler is busy when a job is due, it will run the job up to 1 second late before marking it misfired; increase `misfire_grace_time` if needed.
- **`logging.basicConfig(level=logging.INFO, format="...")`** sets up root logger output — APScheduler itself uses the `apscheduler` logger, which you can quiet with `logging.getLogger("apscheduler").setLevel(logging.WARNING)`.
- Testing concurrent behavior by inspection is valid for this project — you do not need a formal test framework, but `pytest` with `time.sleep` assertions is a reasonable extension.

<details>
<summary>💡 Hint</summary>

Sample task for testing:

```python
# tasks.py
import datetime

def heartbeat():
    print(f"[heartbeat] alive at {datetime.datetime.now().isoformat(timespec='seconds')}")

def fail_always():
    raise RuntimeError("This job always fails — testing resilience")
```

Run and watch:

```bash
python scheduler.py &
sleep 12
python scheduler.py --list
python scheduler.py --run heartbeat
kill %1
```

</details>

---

## Full Solution

<details>
<summary>✅ Complete solution — only open after you've tried</summary>

### `jobs.yaml`

```yaml
jobs:
  - name: heartbeat
    schedule: "*/1 * * * *"           # ← every minute via cron
    function: "tasks.heartbeat"
    enabled: true
    timeout: 10

  - name: cleanup
    schedule: "every: 30s"            # ← every 30 seconds via interval
    function: "tasks.cleanup"
    enabled: true
    timeout: 20

  - name: weekly_report
    schedule: "0 9 * * 1"             # ← 9am every Monday
    function: "tasks.weekly_report"
    enabled: false                    # ← skipped at startup
    timeout: 60
```

---

### `tasks.py`

```python
import datetime
import time


def heartbeat():
    """Sample task: prints a timestamped heartbeat message."""
    print(f"[heartbeat] alive at {datetime.datetime.now().isoformat(timespec='seconds')}")


def cleanup():
    """Sample task: simulates a cleanup operation."""
    print(f"[cleanup] running at {datetime.datetime.now().isoformat(timespec='seconds')}")
    time.sleep(2)                     # ← simulate work
    print("[cleanup] done")


def weekly_report():
    """Sample task: disabled in config, but runnable via --run."""
    print(f"[weekly_report] generating report at {datetime.datetime.now().isoformat(timespec='seconds')}")
    time.sleep(5)                     # ← simulate slow report generation
    print("[weekly_report] report sent")
```

---

### `scheduler.py`

```python
import importlib
import logging
import signal
import sys
import threading
import time
from concurrent.futures import ThreadPoolExecutor, TimeoutError as FuturesTimeoutError
from datetime import datetime

import click
import yaml
from apscheduler.schedulers.background import BackgroundScheduler
from apscheduler.triggers.cron import CronTrigger
from apscheduler.triggers.interval import IntervalTrigger

# ── Logging setup ─────────────────────────────────────────────────────────────

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s  %(levelname)-8s  %(message)s",
    datefmt="%Y-%m-%d %H:%M:%S",
)
log = logging.getLogger(__name__)

# Quiet APScheduler's own internal logs — they are noisy at INFO level
logging.getLogger("apscheduler").setLevel(logging.WARNING)   # ← suppress APScheduler noise


# ── Config loading ─────────────────────────────────────────────────────────────

def load_config(path: str = "jobs.yaml") -> list[dict]:
    """Read jobs.yaml and return the list of job dicts."""
    with open(path, "r") as f:
        data = yaml.safe_load(f)                             # ← safe_load: no arbitrary code exec

    jobs = data.get("jobs", [])
    required_fields = {"name", "schedule", "function", "enabled"}

    for job in jobs:
        missing = required_fields - set(job.keys())
        if missing:
            raise ValueError(
                f"Job '{job.get('name', '<unnamed>')}' is missing required fields: {missing}"
            )

    return jobs


def resolve_function(path: str):
    """Turn 'tasks.heartbeat' into the actual callable."""
    try:
        module_path, func_name = path.rsplit(".", 1)         # ← split from right, once
        module = importlib.import_module(module_path)
        func = getattr(module, func_name)
    except (ValueError, ModuleNotFoundError) as e:
        raise ImportError(f"Cannot resolve function '{path}': {e}") from e
    except AttributeError:
        raise ImportError(
            f"Module '{module_path}' has no attribute '{func_name}'"
        )
    return func


# ── Schedule parsing ───────────────────────────────────────────────────────────

def _is_cron(schedule: str) -> bool:
    """Return True if the schedule string looks like a cron expression."""
    parts = schedule.strip().split()
    return len(parts) == 5                                    # ← cron has exactly 5 space-separated fields


def _parse_interval(schedule: str) -> dict:
    """Parse 'every: 30s' / 'every: 2m' / 'every: 1h' into APScheduler kwargs."""
    value_str = schedule.split(":")[1].strip()               # ← "30s", "2m", "1h"
    if value_str.endswith("s"):
        return {"seconds": int(value_str[:-1])}
    elif value_str.endswith("m"):
        return {"minutes": int(value_str[:-1])}
    elif value_str.endswith("h"):
        return {"hours": int(value_str[:-1])}
    raise ValueError(f"Unknown interval format: '{value_str}'. Use e.g. '30s', '2m', '1h'")


# ── Job wrapper ────────────────────────────────────────────────────────────────

def make_job_wrapper(name: str, func, timeout: int | None):
    """
    Return a callable that:
    - Logs start time, duration, success/failure
    - Enforces an optional timeout
    - Never raises (so one failing job cannot crash the scheduler)
    """
    def wrapper():
        start = time.perf_counter()                          # ← high-res timer
        log.info("[%s] starting", name)

        def _run():
            func()

        try:
            if timeout:
                with ThreadPoolExecutor(max_workers=1) as executor:
                    future = executor.submit(_run)
                    future.result(timeout=timeout)           # ← blocks up to `timeout` seconds
            else:
                _run()

            elapsed = time.perf_counter() - start
            log.info("[%s] finished in %.2fs", name, elapsed)

        except FuturesTimeoutError:
            elapsed = time.perf_counter() - start
            log.error("[%s] TIMEOUT after %.2fs (limit=%ss)", name, elapsed, timeout)

        except Exception as exc:                             # ← catch everything so other jobs keep running
            elapsed = time.perf_counter() - start
            log.error("[%s] FAILED after %.2fs — %s", name, elapsed, exc)

    return wrapper


# ── Scheduler setup ────────────────────────────────────────────────────────────

def build_scheduler(config: list[dict]) -> BackgroundScheduler:
    """Create a BackgroundScheduler and register all enabled jobs."""
    scheduler = BackgroundScheduler()

    for job in config:
        if not job["enabled"]:
            log.info("Skipping disabled job: %s", job["name"])
            continue

        func = resolve_function(job["function"])
        timeout = job.get("timeout")                         # ← None if not set
        wrapper = make_job_wrapper(job["name"], func, timeout)

        schedule = job["schedule"]

        if _is_cron(schedule):
            trigger = CronTrigger.from_crontab(schedule)     # ← APScheduler parses the cron string
        elif schedule.startswith("every:"):
            trigger = IntervalTrigger(**_parse_interval(schedule))
        else:
            raise ValueError(
                f"Job '{job['name']}': unrecognised schedule format '{schedule}'"
            )

        scheduler.add_job(
            wrapper,
            trigger=trigger,
            id=job["name"],                                  # ← use name as unique job ID
            name=job["name"],
            replace_existing=True,
        )
        log.info("Registered job: %s  schedule=%s", job["name"], schedule)

    return scheduler


# ── CLI ────────────────────────────────────────────────────────────────────────

@click.command()
@click.option("--list", "list_jobs", is_flag=True, help="Print all jobs and their next run time.")
@click.option("--run", "run_job", default=None, metavar="JOB_NAME", help="Run a job immediately by name.")
def main(list_jobs: bool, run_job: str | None):
    """Config-driven job scheduler. Run with no flags to start all enabled jobs."""

    config = load_config()

    # ── --list ──────────────────────────────────────────────────────────────────
    if list_jobs:
        scheduler = build_scheduler(config)
        scheduler.start()                                    # ← needed so next_run_time is populated

        registered = {job.id: job for job in scheduler.get_jobs()}

        click.echo(f"\n{'NAME':<20} {'SCHEDULE':<25} {'ENABLED':<10} {'NEXT RUN'}")
        click.echo("-" * 75)

        for entry in config:
            name = entry["name"]
            sched = entry["schedule"]
            enabled = entry["enabled"]
            job_obj = registered.get(name)

            if job_obj and job_obj.next_run_time:
                next_run = job_obj.next_run_time.strftime("%Y-%m-%d %H:%M:%S")
            elif not enabled:
                next_run = "disabled"
            else:
                next_run = "unknown"

            click.echo(f"{name:<20} {sched:<25} {str(enabled):<10} {next_run}")

        click.echo()
        scheduler.shutdown(wait=False)                       # ← don't need to wait, no jobs ran
        return

    # ── --run ───────────────────────────────────────────────────────────────────
    if run_job:
        entry = next((j for j in config if j["name"] == run_job), None)
        if entry is None:
            click.echo(f"Error: job '{run_job}' not found in config", err=True)
            sys.exit(1)

        func = resolve_function(entry["function"])
        timeout = entry.get("timeout")
        start_ts = datetime.now().isoformat(timespec="seconds")
        click.echo(f"[{run_job}] started at {start_ts}")

        start = time.perf_counter()
        try:
            if timeout:
                with ThreadPoolExecutor(max_workers=1) as executor:
                    future = executor.submit(func)
                    future.result(timeout=timeout)
            else:
                func()
            elapsed = time.perf_counter() - start
            click.echo(f"[{run_job}] finished in {elapsed:.2f}s")
        except FuturesTimeoutError:
            elapsed = time.perf_counter() - start
            click.echo(f"[{run_job}] TIMEOUT after {elapsed:.2f}s (limit={timeout}s)", err=True)
            sys.exit(1)
        except Exception as exc:
            elapsed = time.perf_counter() - start
            click.echo(f"[{run_job}] FAILED after {elapsed:.2f}s — {exc}", err=True)
            sys.exit(1)
        return

    # ── Normal run: start scheduler ─────────────────────────────────────────────
    stop_event = threading.Event()

    def shutdown_handler(signum, frame):
        click.echo("\nShutting down — waiting for running jobs to finish...")
        stop_event.set()

    signal.signal(signal.SIGINT, shutdown_handler)           # ← Ctrl+C
    signal.signal(signal.SIGTERM, shutdown_handler)          # ← kill / systemd stop

    scheduler = build_scheduler(config)
    scheduler.start()
    log.info("Scheduler started. Press Ctrl+C to stop.")

    while not stop_event.is_set():                           # ← poll the event; sleep avoids busy-loop
        time.sleep(1)

    scheduler.shutdown(wait=True)                            # ← blocks until in-progress jobs finish
    log.info("Scheduler stopped cleanly.")


if __name__ == "__main__":
    main()
```

---

### Usage

```bash
# Start the scheduler (runs forever)
python scheduler.py

# List all jobs with next run time
python scheduler.py --list

# Run a specific job immediately
python scheduler.py --run heartbeat
python scheduler.py --run weekly_report

# Stop gracefully
# Press Ctrl+C while scheduler is running
```

### Sample output — `python scheduler.py`

```
2024-01-15 09:30:00  INFO      Registered job: heartbeat  schedule=*/1 * * * *
2024-01-15 09:30:00  INFO      Registered job: cleanup    schedule=every: 30s
2024-01-15 09:30:00  INFO      Scheduler started. Press Ctrl+C to stop.
2024-01-15 09:30:00  INFO      [cleanup] starting
2024-01-15 09:30:02  INFO      [cleanup] finished in 2.01s
2024-01-15 09:31:00  INFO      [heartbeat] starting
2024-01-15 09:31:00  INFO      [heartbeat] finished in 0.00s
```

### Sample output — `python scheduler.py --list`

```
NAME                 SCHEDULE                  ENABLED    NEXT RUN
---------------------------------------------------------------------------
heartbeat            */1 * * * *               True       2024-01-15 09:32:00
cleanup              every: 30s                True       2024-01-15 09:31:15
weekly_report        0 9 * * 1                 False      disabled
```

</details>

---

## Back to Project Series

[Back to Capstone Projects README](../README.md) | Previous: [06 — Webhook Receiver](../06_Webhook_Receiver/Project_Guide.md) | Next: [09 — Rate Limiter Middleware](../09_Rate_Limiter_Middleware/Project_Guide.md)
