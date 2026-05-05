# Project 04 — CLI Tool

> Every great engineer eventually builds tools for other engineers. A CLI tool is a first-class citizen of the Unix world — composable, scriptable, and shareable. The gap between "a script that works for me" and "a tool I can give to my team" is packaging.

This is a partially guided project. Every step explains the concept, asks you questions to think through before looking, then shows the answer. There are no hints — try to answer the questions yourself first.

---

## What You're Building

A fully packaged, **pip-installable** CLI tool called `devtools`:

```
devtools fetch-users --url https://randomuser.me/api/ --output users.json
devtools stats --file users.json
devtools convert --file users.json --format csv --output users.csv
devtools --version
devtools --help
```

After `pip install -e .`, the `devtools` command works from anywhere in your terminal — it's a real binary, not just a script you run with `python`.

```
pyproject.toml
[project.scripts]
devtools = "devtools.cli:main"
         │
         └──► pip creates a real executable at /usr/local/bin/devtools
              that runs this Python function

$ devtools fetch-users --url https://... --output users.json
       │
       ▼
   ArgumentParser
       │
   ┌───┴────────────────────────┐
   │   subcommand dispatch      │
   └───┬──────┬──────┬──────────┘
       │      │      │
  fetch-   stats  convert
  users
       │
   requests
   (paginated)
       │
   users.json
```

---

## What You Need Installed

```bash
pip install requests pyyaml
```

---

## Step 1 — Why Packaging Matters

Before writing code, understand what transforms a script into a tool.

**The difference:**

| Script | Tool |
|--------|------|
| `python fetch_users.py` | `devtools fetch-users` |
| Only works if you're in the right directory | Works from anywhere |
| You hand someone a file | You hand someone `pip install devtools` |
| Not composable with other CLI tools | Pipes, redirects, shell scripts work naturally |

**How `pip install` creates a command:**

When you install a package, pip reads the `[project.scripts]` table in `pyproject.toml`. For each entry, it creates a small executable wrapper in your environment's `bin/` directory. Running `devtools` in the terminal finds that wrapper, which calls your Python function.

**`__main__.py`:** A special file that runs when you execute a package as a module: `python -m devtools`. Not required when using entry points, but conventional to include.

**Before looking at the answer:**

1. If `devtools = "devtools.cli:main"` is the entry point, what file does the `main` function live in?
2. What does `pip install -e .` do differently from `pip install .`?
3. Why would you put source code under `src/devtools/` instead of just `devtools/` at the root?

<details>
<summary>✅ Answer</summary>

1. The entry point `"devtools.cli:main"` means: in the `devtools` package, find the `cli` module, call the `main` function. So `main` lives in `src/devtools/cli.py`.

2. `pip install -e .` installs in **editable mode** — pip creates a link to your source directory instead of copying it. Changes to your `.py` files take effect immediately without reinstalling.

3. The `src/` layout prevents the local `devtools/` folder from accidentally shadowing the installed package. Without it, `import devtools` might import from your working directory instead of the installed version, causing subtle bugs.

**pyproject.toml:**
```toml
[build-system]
requires = ["setuptools>=68"]
build-backend = "setuptools.backends.legacy:build"

[project]
name = "devtools"
version = "0.1.0"
description = "A developer utility CLI"
requires-python = ">=3.11"
dependencies = [
    "requests",
    "pyyaml",
]

[project.scripts]
devtools = "devtools.cli:main"   # ← this is what creates the `devtools` binary

[tool.setuptools.packages.find]
where = ["src"]                  # ← tells setuptools to look in src/ for packages
```

**Folder structure:**
```
04_CLI_Tool/
├── pyproject.toml
└── src/
    └── devtools/
        ├── __init__.py        ← marks this as a Python package
        ├── __main__.py        ← enables `python -m devtools`
        └── cli.py             ← entry point function lives here
```

**src/devtools/\_\_init\_\_.py:**
```python
__version__ = "0.1.0"  # ← single source of truth for version
```

**src/devtools/\_\_main\_\_.py:**
```python
from devtools.cli import main

if __name__ == "__main__":
    main()  # ← called when running `python -m devtools`
```

</details>

---

## Step 2 — Project Structure

A clean structure before writing any logic prevents pain later. The structure signals intent — someone reading the directory immediately understands what belongs where.

**Before looking at the answer:**

1. If you have three subcommands (`fetch-users`, `stats`, `convert`), would you put all the logic in `cli.py` or split it into separate modules? What's the tradeoff?
2. Where would you put shared utilities (like "read a JSON file")?

<details>
<summary>✅ Answer</summary>

Split into modules — one per subcommand. `cli.py` becomes a thin dispatcher; logic lives in focused files.

```
src/devtools/
├── __init__.py          ← __version__ = "0.1.0"
├── __main__.py          ← if __name__ == "__main__": main()
├── cli.py               ← ArgumentParser, subcommand wiring, dispatch
├── fetch.py             ← fetch-users logic
├── stats.py             ← stats logic
├── convert.py           ← convert logic
└── utils.py             ← shared: read_json(), write_json(), setup_logging()
```

**src/devtools/utils.py:**
```python
import json
import logging
import sys
from pathlib import Path
from typing import Any


logger = logging.getLogger(__name__)  # ← module-level logger, named after the module


def read_json(path: str) -> list[dict[str, Any]]:
    """Read a JSON file and return its contents."""
    file = Path(path)
    if not file.exists():
        print(f"Error: file not found: {path}", file=sys.stderr)
        sys.exit(1)
    with file.open() as f:
        return json.load(f)


def write_json(data: Any, path: str) -> None:
    """Write data to a JSON file."""
    with open(path, "w") as f:
        json.dump(data, f, indent=2)
    logger.debug("Wrote JSON to %s", path)


def setup_logging(verbose: bool) -> None:
    """Configure root logger based on --verbose flag."""
    level = logging.DEBUG if verbose else logging.WARNING
    logging.basicConfig(
        level=level,
        format="%(levelname)s %(name)s: %(message)s",
    )
```

</details>

---

## Step 3 — Main CLI with argparse Subcommands

`argparse` is Python's built-in argument parser. For a multi-subcommand CLI, the key pattern is `add_subparsers()` — each subcommand gets its own parser with its own arguments, and you use `set_defaults(func=...)` to map each subcommand to a handler function.

**Before looking at the answer:**

1. What does `set_defaults(func=handle_fetch)` do, and why is `args.func(args)` the cleanest dispatch pattern?
2. How do you add `--version` to the top-level parser without making it a subcommand?
3. What happens if the user runs `devtools` with no subcommand?

<details>
<summary>✅ Answer</summary>

1. `set_defaults(func=handle_fetch)` stores the function reference on the `args` namespace. Then `args.func(args)` calls whichever function was set — you don't need an `if args.subcommand == "fetch-users":` chain.
2. Use `parser.add_argument("--version", action="version", version=f"%(prog)s {__version__}")` — `action="version"` prints the string and exits.
3. `args.func` won't exist — `hasattr(args, "func")` returns False. Handle this by printing help and exiting.

**src/devtools/cli.py:**
```python
import argparse
import sys
from devtools import __version__
from devtools.fetch import handle_fetch
from devtools.stats import handle_stats
from devtools.convert import handle_convert
from devtools.utils import setup_logging


def main() -> None:
    parser = argparse.ArgumentParser(
        prog="devtools",
        description="Developer utility CLI",
    )
    
    # Top-level flags
    parser.add_argument(
        "--version",
        action="version",                  # ← built-in action: print version and exit
        version=f"%(prog)s {__version__}", # ← %(prog)s is replaced with "devtools"
    )
    parser.add_argument(
        "--verbose", "-v",
        action="store_true",               # ← flag, no value: --verbose sets True
        help="Enable debug logging",
    )
    
    subparsers = parser.add_subparsers(dest="subcommand")  # ← container for subcommands
    
    # --- fetch-users subcommand ---
    fetch_parser = subparsers.add_parser(
        "fetch-users",
        help="Fetch users from a paginated API and save to JSON",
    )
    fetch_parser.add_argument("--url", required=True, help="API endpoint URL")
    fetch_parser.add_argument("--output", required=True, help="Output JSON file path")
    fetch_parser.add_argument("--pages", type=int, default=5, help="Number of pages to fetch")
    fetch_parser.set_defaults(func=handle_fetch)   # ← maps this subcommand to handler
    
    # --- stats subcommand ---
    stats_parser = subparsers.add_parser(
        "stats",
        help="Compute statistics from a users JSON file",
    )
    stats_parser.add_argument("--file", required=True, help="Path to users JSON file")
    stats_parser.set_defaults(func=handle_stats)
    
    # --- convert subcommand ---
    convert_parser = subparsers.add_parser(
        "convert",
        help="Convert users JSON to another format",
    )
    convert_parser.add_argument("--file", required=True, help="Input JSON file")
    convert_parser.add_argument(
        "--format",
        required=True,
        choices=["csv", "yaml"],           # ← argparse validates the value for you
        help="Output format: csv or yaml",
    )
    convert_parser.add_argument("--output", required=True, help="Output file path")
    convert_parser.set_defaults(func=handle_convert)
    
    args = parser.parse_args()
    
    setup_logging(args.verbose)
    
    # If no subcommand given, print help
    if not hasattr(args, "func"):
        parser.print_help()
        sys.exit(0)
    
    args.func(args)  # ← dispatch: calls handle_fetch, handle_stats, or handle_convert
```

</details>

---

## Step 4 — fetch-users Subcommand

Many real APIs are **paginated** — they don't return all results in one response. You loop, requesting the next page each time, until there are no more pages.

The [randomuser.me](https://randomuser.me/api/) API returns users in a `results` list. It doesn't have a `next` URL like some APIs — instead you control pagination with `?page=N&results=10`.

**Before looking at the answer:**

1. How do you show a progress indicator without printing a new line each time (so it updates in place)?
2. If `requests.get()` raises a network error, what exception type should you catch?
3. How do you write an in-place progress update to stdout?

<details>
<summary>✅ Answer</summary>

1. Print with `end=""` and `\r` (carriage return) to overwrite the current line. Use `flush=True` so it appears immediately.
2. Catch `requests.exceptions.RequestException` — the base class for all requests errors (connection error, timeout, HTTP error, etc.).
3. `print(f"\rFetched {n} users...", end="", flush=True)` — `\r` moves cursor to start of current line, then prints over it.

**src/devtools/fetch.py:**
```python
import argparse
import logging
import requests
from devtools.utils import write_json

logger = logging.getLogger(__name__)  # ← named "devtools.fetch" automatically


def fetch_page(url: str, page: int, per_page: int = 10) -> list[dict]:
    """Fetch a single page of users from the API."""
    params = {
        "page": page,
        "results": per_page,
        "seed": "devtools",  # ← seed makes results consistent across runs
    }
    logger.debug("Fetching page %d from %s", page, url)  # ← only visible with --verbose
    
    try:
        response = requests.get(url, params=params, timeout=10)  # ← always set timeout
        response.raise_for_status()  # ← raises HTTPError for 4xx/5xx responses
        data = response.json()
        return data.get("results", [])
    except requests.exceptions.RequestException as e:
        logger.error("Request failed: %s", e)
        raise  # ← re-raise so the caller can handle it


def handle_fetch(args: argparse.Namespace) -> None:
    """Handler for `devtools fetch-users`."""
    all_users = []
    
    try:
        for page in range(1, args.pages + 1):
            users = fetch_page(args.url, page)
            all_users.extend(users)
            # \r moves cursor to start of line — overwrites previous progress message
            print(f"\rFetched {len(all_users)} users...", end="", flush=True)
            
            if not users:  # ← API returned empty page — no more data
                break
    except requests.exceptions.RequestException:
        print(f"\nError: failed to fetch users. Check URL and network.", flush=True)
        return
    
    print()  # ← newline after the \r progress line
    write_json(all_users, args.output)
    print(f"Saved {len(all_users)} users to {args.output}")
```

</details>

---

## Step 5 — stats Subcommand

`collections.Counter` is built for frequency counting. Pass it any iterable and it counts how many times each unique element appears. `counter.most_common(1)` returns the top-N items as `[(element, count)]`.

**Before looking at the answer:**

1. What does `Counter.most_common(1)` return? What does index `[0][0]` get you from that?
2. How do you format a table without importing any library — just string methods?
3. What should you do if a user record is missing the `age` or `nat` field?

<details>
<summary>✅ Answer</summary>

1. `most_common(1)` returns `[("US", 42)]` — a list of one tuple. `[0][0]` gives `"US"` (the most common value). `[0][1]` would give `42` (its count).
2. `str.ljust(width)` left-aligns a string in a field of `width` characters. Combine multiple `ljust` calls to fake columns.
3. Use `.get()` with a default: `user.get("dob", {}).get("age", 0)` returns 0 if either key is missing, instead of raising `KeyError`.

**src/devtools/stats.py:**
```python
import argparse
import logging
from collections import Counter
from devtools.utils import read_json

logger = logging.getLogger(__name__)


def handle_stats(args: argparse.Namespace) -> None:
    """Handler for `devtools stats`."""
    users = read_json(args.file)
    
    if not users:
        print("No users found in file.")
        return
    
    logger.debug("Computing stats for %d users", len(users))
    
    # Extract ages — skip users with missing age data
    ages = [
        user["dob"]["age"]
        for user in users
        if user.get("dob", {}).get("age") is not None  # ← safe access
    ]
    avg_age = sum(ages) / len(ages) if ages else 0
    
    # Count nationalities
    nationalities = [
        user.get("nat", "unknown")          # ← default to "unknown" if field missing
        for user in users
    ]
    nat_counter = Counter(nationalities)
    most_common_nat, most_common_count = nat_counter.most_common(1)[0]
    
    # Count genders
    genders = [user.get("gender", "unknown") for user in users]
    gender_counter = Counter(genders)
    
    # Print as a table using ljust for column alignment
    col = 30  # ← column width for left-aligned labels
    print()
    print("User Statistics")
    print("=" * 50)
    print(f"{'Total users'.ljust(col)} {len(users)}")
    print(f"{'Average age'.ljust(col)} {avg_age:.1f}")
    print(f"{'Most common nationality'.ljust(col)} {most_common_nat} ({most_common_count} users)")
    print()
    print("Gender breakdown:")
    for gender, count in gender_counter.most_common():
        pct = count / len(users) * 100
        print(f"  {gender.ljust(col - 2)} {count} ({pct:.1f}%)")
    print()
```

</details>

---

## Step 6 — convert Subcommand

`csv.DictWriter` takes a list of dicts and writes them as CSV rows, with the dict keys as column headers. The challenge is that user objects from randomuser.me are nested — `{"name": {"first": "Jane", "last": "Doe"}, "email": "..."}`. You need to flatten them first.

**Before looking at the answer:**

1. What arguments does `csv.DictWriter` require at initialization, and what's `extrasaction="ignore"` for?
2. How would you flatten a nested dict like `{"name": {"first": "Jane"}}` into `{"name_first": "Jane"}`?
3. What's missing if you write CSV rows without calling `writer.writeheader()` first?

<details>
<summary>✅ Answer</summary>

1. `DictWriter(file, fieldnames=["col1", "col2"])` — it needs a list of column names. `extrasaction="ignore"` silently drops any dict keys not in `fieldnames`, instead of raising `ValueError`.
2. Recurse or iterate: for each key whose value is a dict, prefix the parent key: `{"name": {"first": "Jane"}}` → `{"name_first": "Jane"}`. One level deep is usually enough.
3. You'd get rows with no header row — the CSV would be missing column names on the first line.

**src/devtools/convert.py:**
```python
import argparse
import csv
import logging
from typing import Any
from devtools.utils import read_json

logger = logging.getLogger(__name__)


def flatten_user(user: dict[str, Any], prefix: str = "") -> dict[str, str]:
    """
    Flatten one level of nesting.
    {"name": {"first": "Jane", "last": "Doe"}} → {"name_first": "Jane", "name_last": "Doe"}
    """
    flat = {}
    for key, value in user.items():
        full_key = f"{prefix}{key}" if not prefix else f"{prefix}_{key}"
        if isinstance(value, dict):
            flat.update(flatten_user(value, prefix=full_key))  # ← recurse one level
        elif isinstance(value, list):
            flat[full_key] = str(value)   # ← convert lists to string representation
        else:
            flat[full_key] = str(value)   # ← everything becomes a string for CSV
    return flat


def convert_to_csv(users: list[dict], output_path: str) -> None:
    if not users:
        print("No data to convert.")
        return
    
    flat_users = [flatten_user(u) for u in users]
    
    # Collect all unique keys across all records (some records may have extra fields)
    all_keys = list(dict.fromkeys(                # ← dict.fromkeys preserves order, deduplicates
        key
        for user in flat_users
        for key in user.keys()
    ))
    
    logger.debug("CSV columns: %s", all_keys)
    
    with open(output_path, "w", newline="") as f:  # ← newline="" required on Windows
        writer = csv.DictWriter(
            f,
            fieldnames=all_keys,
            extrasaction="ignore"   # ← silently skip keys not in fieldnames
        )
        writer.writeheader()        # ← write the column names row
        writer.writerows(flat_users)


def convert_to_yaml(users: list[dict], output_path: str) -> None:
    try:
        import yaml  # ← lazy import — only required if actually converting to yaml
    except ImportError:
        print("Error: pyyaml is required for YAML output. Run: pip install pyyaml")
        return
    
    with open(output_path, "w") as f:
        yaml.dump(users, f, default_flow_style=False, allow_unicode=True)


def handle_convert(args: argparse.Namespace) -> None:
    """Handler for `devtools convert`."""
    users = read_json(args.file)
    logger.debug("Loaded %d records from %s", len(users), args.file)
    
    if args.format == "csv":
        convert_to_csv(users, args.output)
    elif args.format == "yaml":
        convert_to_yaml(users, args.output)
    
    print(f"Converted {len(users)} records to {args.format.upper()} → {args.output}")
```

</details>

---

## Step 7 — --verbose Flag and Logging

The difference between `print()` and `logging` is audience. `print()` is for the user — it always shows. `logging` is for developers and operators — it's filtered by level and can be routed to files, syslog, or monitoring systems without changing the code.

In a CLI tool: user-facing output goes to `print()`. Debug traces, timing, and internal state go to `logging`.

**Before looking at the answer:**

1. What level is `logging.WARNING`, and what does it mean for `logging.DEBUG` messages?
2. Why use `logging.getLogger(__name__)` instead of `logging.getLogger("myapp")`?
3. At what point in `main()` should you call `setup_logging(args.verbose)`?

<details>
<summary>✅ Answer</summary>

1. `WARNING` (level 30) means only WARNING, ERROR, and CRITICAL messages are shown. DEBUG (level 10) messages are below the threshold — they're silently discarded. With `--verbose`, you set level to DEBUG so all messages pass through.
2. `__name__` is the module's fully-qualified name (e.g., `devtools.fetch`). Using it creates a logger hierarchy — `devtools.fetch`, `devtools.stats`, etc. — all under the `devtools` root. You can configure the root `devtools` logger to control all submodules at once.
3. Before `args.func(args)` but after `parse_args()`. Logging needs to be configured before any module tries to log — but you don't know the `--verbose` flag until after parsing.

**src/devtools/utils.py** (setup_logging already shown in Step 2, shown here in context):
```python
import logging


def setup_logging(verbose: bool) -> None:
    """Configure root logger. Call once, early in main()."""
    level = logging.DEBUG if verbose else logging.WARNING
    logging.basicConfig(
        level=level,
        format="%(levelname)s %(name)s: %(message)s",  # ← e.g. "DEBUG devtools.fetch: Fetching page 1"
        handlers=[logging.StreamHandler()],             # ← output to stderr by default
    )
```

**Usage in any module:**
```python
import logging

logger = logging.getLogger(__name__)  # ← once per module, at module level (not inside functions)

def some_function():
    logger.debug("This only shows with --verbose")   # ← DEBUG level
    logger.warning("This always shows")              # ← WARNING level
    logger.error("Something went wrong: %s", error)  # ← use % formatting, not f-strings
    #                                                    (lazy evaluation — no string built if not logged)
```

**Test it:**
```bash
devtools fetch-users --url https://randomuser.me/api/ --output u.json --verbose
# DEBUG devtools.fetch: Fetching page 1 from https://randomuser.me/api/
# DEBUG devtools.fetch: Fetching page 2 from https://randomuser.me/api/
# ...
```

</details>

---

## Step 8 — Config File Support

A config file lets users set their own defaults without passing the same flags every time. The standard location for user-level config files is `~/.toolname.conf` — the tilde expands to the user's home directory.

Python's `configparser` reads INI-format files:
```ini
[defaults]
url = https://randomuser.me/api/
pages = 20
```

**Precedence rule:** CLI args win over config file. If the user passes `--url X` on the command line, use `X`. If they don't, check the config file. If not there, use the hardcoded default.

**Before looking at the answer:**

1. How do you expand `~` in a file path in Python to get the real home directory?
2. If `configparser` can't find the file, does it raise an error or silently do nothing?
3. Where in `main()` should you apply config file defaults — before or after `parse_args()`?

<details>
<summary>✅ Answer</summary>

1. `Path("~/.devtools.conf").expanduser()` — `.expanduser()` replaces `~` with the actual home directory path.
2. `config.read()` silently does nothing if the file doesn't exist — it returns a list of files it successfully read. You can check `if files_read:` but it's not required.
3. After `parse_args()`, before calling `args.func(args)`. You need the parsed args to check which values the user explicitly provided, and you need the config loaded to supply fallbacks for values they didn't provide.

**Config file location:** `~/.devtools.conf`

**Example ~/.devtools.conf:**
```ini
[defaults]
url = https://randomuser.me/api/
pages = 10
```

**src/devtools/cli.py** (add config loading to `main()`):
```python
import configparser
from pathlib import Path


def load_config() -> dict[str, str]:
    """Read ~/.devtools.conf and return [defaults] section as a dict."""
    config = configparser.ConfigParser()
    config_path = Path("~/.devtools.conf").expanduser()  # ← ~ → /Users/yourname
    
    read_files = config.read(config_path)                # ← silently ok if file missing
    
    if read_files:
        return dict(config["defaults"]) if "defaults" in config else {}
    return {}


def main() -> None:
    # ... (parser setup as before) ...
    
    args = parser.parse_args()
    setup_logging(args.verbose)
    
    # Apply config file defaults — only for args the user didn't explicitly pass
    config = load_config()
    
    if hasattr(args, "url") and args.url is None:
        # argparse sets url to None when not provided (default=None)
        args.url = config.get("url")        # ← config file fallback
    
    if hasattr(args, "pages") and args.pages == 5:
        # If pages is still the hardcoded default, allow config to override
        args.pages = int(config.get("pages", 5))
    
    if not hasattr(args, "func"):
        parser.print_help()
        import sys; sys.exit(0)
    
    args.func(args)
```

</details>

---

## Step 9 — Install and Test

The final step — turn the source tree into a real installed command.

**Before looking at the answer:**

1. What does `pip install -e .` do that `python cli.py` doesn't?
2. How do you verify the command is a real binary on your system, not just a Python script alias?
3. After editing `fetch.py`, do you need to reinstall?

<details>
<summary>✅ Answer</summary>

1. `pip install -e .` registers the package with Python and creates an executable entry point at `$(which devtools)`. The command works from any directory, not just the project folder.
2. `which devtools` shows the path (e.g., `/Users/you/.venv/bin/devtools`). `file $(which devtools)` shows it's a Python script wrapper. It's a real binary that your shell finds via `PATH`.
3. No — editable mode (`-e`) means changes to `.py` files are reflected immediately. Only reinstall if you change `pyproject.toml` (e.g., add a new dependency or entry point).

**Install:**
```bash
cd 04_CLI_Tool
pip install -e .
```

**Verify installation:**
```bash
which devtools
# /Users/yourname/.venv/bin/devtools  (or similar)

devtools --version
# devtools 0.1.0

devtools --help
# usage: devtools [-h] [--version] [--verbose] {fetch-users,stats,convert} ...
```

**End-to-end test:**
```bash
# 1. Fetch 3 pages of users (30 users total)
devtools fetch-users \
  --url https://randomuser.me/api/ \
  --output users.json \
  --pages 3

# Expected output:
# Fetched 30 users...
# Saved 30 users to users.json

# 2. Compute stats
devtools stats --file users.json

# Expected output:
# User Statistics
# ==================================================
# Total users                    30
# Average age                    44.2
# Most common nationality        US (6 users)

# 3. Convert to CSV
devtools convert --file users.json --format csv --output users.csv
# Converted 30 records to CSV → users.csv

# 4. Convert to YAML
devtools convert --file users.json --format yaml --output users.yaml
# Converted 30 records to YAML → users.yaml

# 5. Test --verbose
devtools fetch-users --url https://randomuser.me/api/ --output u.json --verbose --pages 1
# DEBUG devtools.fetch: Fetching page 1 from https://randomuser.me/api/
# ...

# 6. Test config file
echo "[defaults]" > ~/.devtools.conf
echo "url = https://randomuser.me/api/" >> ~/.devtools.conf
echo "pages = 2" >> ~/.devtools.conf

devtools fetch-users --output from_config.json
# Uses URL and pages from ~/.devtools.conf
```

</details>

---

## What You Built

```
pyproject.toml  [project.scripts] devtools = "devtools.cli:main"
                        │
                        ▼
              pip install -e .
                        │
             /usr/local/bin/devtools   ← real executable, works anywhere
                        │
              ArgumentParser + subparsers
                        │
         ┌──────────────┼──────────────┐
         │              │              │
   fetch-users        stats         convert
         │              │              │
  requests loop   Counter +       DictWriter
  pagination      ljust table     flatten_user
         │              │          yaml.dump
  users.json      print table    users.csv/yaml
         │
  ~/.devtools.conf ← configparser fallback defaults
  --verbose        ← logging.DEBUG vs WARNING
```

## What You Learned

- `[project.scripts]` in `pyproject.toml` is what turns a Python function into a system-wide command
- `pip install -e .` creates an editable install — source changes take effect without reinstalling
- `add_subparsers()` + `set_defaults(func=...)` + `args.func(args)` is the clean argparse dispatch pattern
- Pagination loops: fetch pages until empty, track count, show progress with `\r` in-place updates
- `collections.Counter` handles frequency counting in one line; `.most_common(N)` does the ranking
- `csv.DictWriter` handles headers and rows from dicts; flatten nested structures first
- `logging` with `getLogger(__name__)` creates a hierarchy you control with one `basicConfig` call
- `configparser` reads INI files; CLI args should always win over config file defaults

## Extend It

- Add `devtools ping --url <url>` — HTTP health check that reports status code and response time
- Add `devtools env --check` — read a `.env.required` file and validate all listed vars are set
- Publish to PyPI: `pip install build twine`, then `python -m build` and `twine upload dist/*`
- Add shell tab completion with `argcomplete`: `pip install argcomplete`, then `eval "$(register-python-argcomplete devtools)"`
