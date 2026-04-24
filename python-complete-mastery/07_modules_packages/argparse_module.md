# argparse — Build Professional Command-Line Interfaces

> *"Your script is a tool. Tools deserve handles, switches, and labels —*
> *not a pile of mysterious positional arguments users have to guess."*

---

## The Story

Imagine you're handing someone a form to fill out. Two approaches:

**Approach A:** You give them a blank sheet of paper and say "write your name, age, and city somewhere on it." Now you have to read free-form text, guess where each value is, validate that the age is actually a number, and figure out what to do when they leave something blank.

**Approach B:** You hand them a printed form with labeled fields, checkboxes, drop-downs, and required-field markers. The structure enforces itself.

`sys.argv` is Approach A. It gives you a list of raw strings: `["script.py", "--output", "json", "--verbose", "--count", "5"]`. You could parse this manually — check every string, handle missing flags, convert "5" to an integer — but it's fragile, tedious, and breaks the moment you add a new flag.

**`argparse`** is the form designer. You declare what your program accepts — names, types, constraints, help text — and argparse handles parsing, validation, type conversion, and automatic `--help` generation.

```
sys.argv approach:              argparse approach:
─────────────────               ──────────────────
Parse strings manually          Declare the form
Handle missing flags            Argparse enforces requirements
Convert types yourself          type= does it automatically
Write --help yourself           --help is auto-generated
Validate choices yourself       choices= restricts values
```

Once you describe the form, argparse reads it for you.

---

## 1 — The Minimum Working Parser

```python
import argparse

parser = argparse.ArgumentParser(description="Process a data file")  # ← describe the program
args = parser.parse_args()                                            # ← read sys.argv
```

Run with `--help` and argparse gives you a formatted help message for free.

---

## 2 — Positional Arguments

**Positional arguments** are required, ordered values — no flag name needed. Like `cp source dest`.

```python
parser = argparse.ArgumentParser()

parser.add_argument("filename")                   # ← single required positional
parser.add_argument("files", nargs="+")           # ← one or more files (list)
parser.add_argument("files", nargs="*")           # ← zero or more files (list, can be empty)
parser.add_argument("value", nargs="?")           # ← optional single value

args = parser.parse_args()
print(args.filename)                              # ← attribute name = argument name
```

```
nargs cheat sheet:
──────────────────────────────────────────────────────
nargs    Meaning                    Result type
──────────────────────────────────────────────────────
(none)   exactly one value          single value
"?"      zero or one value          value or None
"+"      one or more values         list (error if empty)
"*"      zero or more values        list (can be [])
N (int)  exactly N values           list of length N
──────────────────────────────────────────────────────
```

---

## 3 — Optional Arguments (Flags)

**Optional arguments** start with `--` (long form) or `-` (short form). The user can include them or leave them out.

```python
parser.add_argument("--output", "-o")             # ← --output json or -o json
parser.add_argument("--verbose", "-v",
                    action="store_true")           # ← flag only, no value: True if present
parser.add_argument("--quiet",
                    action="store_false")          # ← True by default, False if flag used
parser.add_argument("--tag",
                    action="append")              # ← --tag a --tag b → ["a", "b"]
parser.add_argument("--verbosity", "-V",
                    action="count", default=0)    # ← -V -V -V → 3

args = parser.parse_args(["--output", "json", "--verbose", "--tag", "a", "--tag", "b"])
print(args.output)      # "json"
print(args.verbose)     # True
print(args.tag)         # ["a", "b"]
print(args.verbosity)   # 0 (not passed)
```

```
action values:
──────────────────────────────────────────────────────────────
store          (default) store the given value
store_true     store True if flag is present
store_false    store False if flag is present
append         collect multiple uses into a list
count          count how many times the flag appears
──────────────────────────────────────────────────────────────
```

---

## 4 — Types and Validation

By default, argparse stores everything as a string. Use `type=` to convert and validate automatically.

```python
parser.add_argument("--count", type=int)             # ← "5" → 5, "abc" → error
parser.add_argument("--ratio", type=float)           # ← "3.14" → 3.14
parser.add_argument("--path", type=Path)             # ← "data/file.csv" → Path object

# restrict to known values
parser.add_argument("--format",
                    choices=["json", "csv", "table"])  # ← anything else → error + help

# open a file and hand you the file object
parser.add_argument("--input",
                    type=argparse.FileType("r"))        # ← opens file, passes handle

# custom validation function
def positive_int(value):
    n = int(value)
    if n <= 0:
        raise argparse.ArgumentTypeError(f"{value} must be a positive integer")
    return n

parser.add_argument("--workers", type=positive_int)   # ← custom validator as type=
```

The `type=` function receives a string and must either return the converted value or raise `argparse.ArgumentTypeError`. If it raises any other exception, argparse wraps it in a generic error message.

---

## 5 — Required vs Optional, Defaults, and Const

```python
# optional argument made required
parser.add_argument("--output", required=True)        # ← error if not provided

# default value when flag is absent
parser.add_argument("--format", default="json")       # ← args.format == "json" if not given

# nargs="?" with const: flag with optional value
parser.add_argument("--log",
                    nargs="?",
                    const="debug.log",                # ← used when --log given with no value
                    default=None)                     # ← used when --log not given at all

# --log          → args.log == "debug.log"  (const)
# --log app.log  → args.log == "app.log"    (explicit value)
# (not given)    → args.log == None         (default)
```

---

## 6 — Help Text and Documentation

Argparse generates `--help` output from the metadata you attach to each argument.

```python
parser = argparse.ArgumentParser(
    description="Process and export data files.",       # ← shown at top of --help
    epilog="Example: script.py data.csv --format json", # ← shown at bottom
    formatter_class=argparse.RawDescriptionHelpFormatter  # ← preserves newlines in epilog
)

parser.add_argument("filename",
                    help="Path to the input data file")              # ← shown in --help

parser.add_argument("--format",
                    choices=["json", "csv", "table"],
                    metavar="FORMAT",                 # ← placeholder in help (instead of {json,csv,table})
                    help="Output format: json, csv, or table")
```

```
--help output (abbreviated):
─────────────────────────────────────────────────────────
usage: script.py [-h] [--format FORMAT] filename

Process and export data files.

positional arguments:
  filename              Path to the input data file

options:
  -h, --help            show this help message and exit
  --format FORMAT       Output format: json, csv, or table

Example: script.py data.csv --format json
─────────────────────────────────────────────────────────
```

---

## 7 — Mutually Exclusive Groups

When two flags cannot be used together, declare them as a **mutually exclusive group**. Argparse enforces the constraint automatically.

```python
parser = argparse.ArgumentParser()

group = parser.add_mutually_exclusive_group()         # ← create the group
group.add_argument("--json", action="store_true")     # ← only one of these
group.add_argument("--csv",  action="store_true")     # ← can be used at a time
group.add_argument("--table", action="store_true")

# python script.py --json --csv  → error: not allowed with argument --json
```

Add `required=True` to the group to force the user to pick exactly one:

```python
group = parser.add_mutually_exclusive_group(required=True)
```

---

## 8 — Argument Groups for Visual Organization

**Argument groups** do not enforce mutual exclusivity — they just group related arguments visually in the `--help` output.

```python
parser = argparse.ArgumentParser()

input_group = parser.add_argument_group("Input options")    # ← named group
input_group.add_argument("filename")
input_group.add_argument("--encoding", default="utf-8")

output_group = parser.add_argument_group("Output options")  # ← another group
output_group.add_argument("--format", choices=["json", "csv"])
output_group.add_argument("--output", "-o", help="Output file path")
```

The `--help` output now shows sections with headers, making complex CLIs far easier to read.

---

## 9 — Subcommands (Sub-parsers)

For tools with distinct modes — like `git commit`, `git push`, `git log` — use **subparsers**. Each subcommand gets its own argument parser with its own flags.

```python
parser = argparse.ArgumentParser(description="Data pipeline tool")
subparsers = parser.add_subparsers(dest="command")            # ← stores which subcommand was used

# --- init subcommand ---
init_parser = subparsers.add_parser("init", help="Initialize a new project")
init_parser.add_argument("name", help="Project name")
init_parser.add_argument("--template", default="default")

# --- run subcommand ---
run_parser = subparsers.add_parser("run", help="Run the pipeline")
run_parser.add_argument("config", help="Config file path")
run_parser.add_argument("--workers", type=int, default=4)
run_parser.add_argument("--dry-run", action="store_true")

# --- status subcommand ---
status_parser = subparsers.add_parser("status", help="Show pipeline status")
status_parser.add_argument("--json", action="store_true")
```

Dispatch pattern — route to the right function based on which subcommand was used:

```python
args = parser.parse_args()

if args.command == "init":
    run_init(args.name, args.template)
elif args.command == "run":
    run_pipeline(args.config, args.workers, args.dry_run)
elif args.command == "status":
    show_status(json_output=args.json)
else:
    parser.print_help()                                       # ← no subcommand given
```

```
CLI topology:
─────────────────────────────────────────────────────────
parser
  ├── subparsers
  │     ├── "init"   → init_parser  (name, --template)
  │     ├── "run"    → run_parser   (config, --workers, --dry-run)
  │     └── "status" → status_parser (--json)
  └── dest="command" tells you which branch was taken
─────────────────────────────────────────────────────────
```

---

## 10 — Parsing and Using Results

```python
# Parse from sys.argv (normal use)
args = parser.parse_args()

# Parse from a list (useful in tests — no sys.argv needed)
args = parser.parse_args(["run", "config.yaml", "--workers", "8"])

# Access as attributes
print(args.workers)     # 8

# Convert namespace to dict
d = vars(args)          # {"command": "run", "config": "config.yaml", "workers": 8, ...}
```

The `Namespace` object argparse returns is just an object with attributes — `vars()` unwraps it into a plain dict when you need that shape.

---

## 11 — Real-World Complete Example

A data processing script with input file, output format, verbosity, and subcommands:

```python
import argparse
from pathlib import Path


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        description="Process and export structured data files.",
        epilog="Example: datapipe.py process data.csv --format json --output result.json",
        formatter_class=argparse.RawDescriptionHelpFormatter,
    )

    subparsers = parser.add_subparsers(dest="command", required=True)  # ← Python 3.7+

    # ── process subcommand ─────────────────────────────────────────
    proc = subparsers.add_parser("process", help="Process an input file")

    proc.add_argument("input",
                      type=Path,
                      help="Input file (CSV or JSON)")

    output_group = proc.add_argument_group("Output options")
    output_group.add_argument("--format", "-f",
                               choices=["json", "csv", "table"],
                               default="json",
                               help="Output format (default: json)")
    output_group.add_argument("--output", "-o",
                               type=Path,
                               help="Output file path (default: stdout)")

    filter_group = proc.add_argument_group("Filter options")
    filter_group.add_argument("--limit", type=int, metavar="N",
                               help="Max rows to process")
    filter_group.add_argument("--tag", action="append", metavar="TAG",
                               help="Filter by tag (repeatable)")

    proc.add_argument("--verbose", "-v",
                      action="count", default=0,
                      help="Increase verbosity (-v, -vv, -vvv)")

    # ── validate subcommand ────────────────────────────────────────
    val = subparsers.add_parser("validate", help="Validate a file without processing")
    val.add_argument("input", type=Path)
    val.add_argument("--strict", action="store_true",
                     help="Fail on warnings, not just errors")

    return parser


def main():
    parser = build_parser()
    args = parser.parse_args()

    if args.command == "process":
        print(f"Processing {args.input} → {args.format}")
        if args.verbose >= 2:
            print(f"  limit={args.limit}, tags={args.tag}")
    elif args.command == "validate":
        print(f"Validating {args.input} (strict={args.strict})")


if __name__ == "__main__":
    main()
```

---

## 12 — argparse vs click vs typer

```
┌─────────────────┬────────────────────────────┬──────────────────────────────────────┐
│ Library         │ Strengths                  │ When to choose                       │
├─────────────────┼────────────────────────────┼──────────────────────────────────────┤
│ argparse        │ stdlib, no install needed  │ Simple tools, scripts, no deps ok    │
│                 │ explicit, well-documented  │ When you want zero external deps     │
├─────────────────┼────────────────────────────┼──────────────────────────────────────┤
│ click           │ decorator-based, composable│ Medium complexity CLIs, plugins      │
│                 │ great for command groups   │ When you want clean decorator syntax │
├─────────────────┼────────────────────────────┼──────────────────────────────────────┤
│ typer           │ type hints drive the CLI   │ FastAPI-style CLI, auto-complete,    │
│                 │ built on click + pydantic  │ when type hints are already in code  │
└─────────────────┴────────────────────────────┴──────────────────────────────────────┘
```

For internal scripts and tools where you cannot add dependencies: argparse is the right choice. For larger projects where developer experience matters: typer is the modern default.

---

## 13 — Common Mistakes

```
┌──────────────────────────────────────────┬────────────────────────────────────────────────────┐
│ Mistake                                  │ Fix                                                │
├──────────────────────────────────────────┼────────────────────────────────────────────────────┤
│ Hyphenated flag: --dry-run               │ Argparse maps it to args.dry_run (hyphens → under- │
│ then accessing args.dry-run (KeyError)   │ scores). Use dest="dry_run" to be explicit.        │
├──────────────────────────────────────────┼────────────────────────────────────────────────────┤
│ Forgetting type=int — value is "5"       │ Always set type= for numeric arguments. argparse   │
│ and int("5") works but "5" > 3 is True  │ stores strings by default.                         │
├──────────────────────────────────────────┼────────────────────────────────────────────────────┤
│ nargs="+" vs nargs="*" confusion         │ "+" requires at least one value. "*" allows zero.  │
│                                          │ Use "+" unless empty list is valid.                │
├──────────────────────────────────────────┼────────────────────────────────────────────────────┤
│ Mixing positional + nargs="*" in a list  │ argparse is greedy. Put nargs="*" positionals last │
│ → earlier positional gets all values     │ or use optional flags instead.                     │
├──────────────────────────────────────────┼────────────────────────────────────────────────────┤
│ Not using subparsers(required=True)      │ Without required=True, no subcommand gives no      │
│ → silent success with args.command=None  │ error. Always set required=True (Python 3.7+).     │
├──────────────────────────────────────────┼────────────────────────────────────────────────────┤
│ Custom type= raises ValueError instead   │ Raise argparse.ArgumentTypeError for a clean error │
│ of ArgumentTypeError → ugly traceback   │ message. ValueError shows a raw exception.         │
└──────────────────────────────────────────┴────────────────────────────────────────────────────┘
```

---

## Navigation

- Back to: [07 Modules & Packages — Theory](theory.md)
- Previous: [sys module](sys_module.md)
- Related: [07 Modules & Packages — Cheatsheet](cheatsheet.md)
