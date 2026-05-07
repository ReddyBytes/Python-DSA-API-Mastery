# 🎛️ argparse — Command-Line Interfaces

> `argparse` turns a raw list of command-line strings into a structured namespace with type-validated, documented parameters — the difference between a script that says "usage: script.py" on error vs one that says exactly what went wrong.
> Every production CLI tool uses it (or a wrapper like `click`/`typer` that builds on the same ideas).

---

## 📌 Learning Priority

**Must Learn** — Daily use, foundation of CLI tools:
`ArgumentParser` · `add_argument()` · positional vs optional args · `parse_args()` · `type=` · `help=`

**Should Learn** — Common patterns in real scripts:
`default=` · `required=` · `choices=` · `nargs=` · `metavar=` · subcommands (sub-parsers)

**Good to Know** — Less common but useful:
`ArgumentDefaultsHelpFormatter` · `add_mutually_exclusive_group()` · `add_argument_group()`

**Reference** — argparse vs alternatives:
`click` · `typer` · `docopt` — know when to reach for each

---

## 1 — The Minimum Working Parser

Every CLI tool starts the same way — a single `ArgumentParser` object that reads `sys.argv` and transforms it into something structured. Think of it as hiring a receptionist: instead of your script fumbling through a raw string of typed input, the receptionist takes the message, checks it for completeness, and hands you a clean, typed object.

```python
import argparse

parser = argparse.ArgumentParser(description="Process a data file")  # ← describe the program
args = parser.parse_args()                                            # ← read sys.argv
```

Run with `--help` and argparse gives you a formatted help message for free.

---

## 2 — Positional Arguments

Think of positional arguments like seats on a bus: seat 1 is always the driver, seat 2 is always the co-pilot — their position alone tells you who they are. **Positional arguments** work the same way: required, ordered values where the position in the command determines what each value means, no flag name needed. Like `cp source dest`.

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

A toggle switch on a machine does nothing when left alone — but flip it and the machine changes behavior. **Optional arguments** work exactly like that: they sit quietly absent by default and only alter behavior when the user explicitly includes them. They start with `--` (long form) or `-` (short form), and the user can include them or leave them out entirely.

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

Imagine a form where every field is a text box — even the one asking for your age. Someone types "twenty-three" and your code crashes when it tries to do math. `type=` is argparse's way of giving each field the right input control: a number spinner for integers, a dropdown for choices, a file picker for paths. Validation happens automatically before your code ever runs, and the error message points directly at the offending argument.

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

Every option in a well-designed CLI has a sensible default — the same way a new app opens in its most common mode without asking you to configure it first. Argparse lets you declare what a flag means when absent (`default=`), what it means when present with no value (`const=`), and when an "optional" argument must actually always be given (`required=True`).

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

A tool without documentation is a locked room — someone wrote something useful inside, but no one can find their way in. Argparse generates a `--help` page automatically from the metadata you attach to each argument, so the better you annotate your arguments, the better the self-service documentation becomes. The cost is a few extra strings; the payoff is a tool anyone can use without reading the source.

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

Some options are like radio buttons — you can pick one station, but you cannot be on AM and FM at the same time. When two flags cannot be used together, declaring them as a **mutually exclusive group** lets argparse enforce the constraint automatically, with a clear error message, instead of leaving you to write conditional checks after parsing.

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

A cluttered `--help` page is like an instruction manual with no chapter headings — technically complete, but exhausting to navigate. **Argument groups** let you impose structure: related flags cluster together under named headers in the help output, making a complex CLI feel approachable. They add zero logic — only visual organization.

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

`git` could have been designed as one giant command with hundreds of flags, but instead it has verbs: `git commit`, `git push`, `git log`. Each verb is its own mental model with its own flags. **Subparsers** give your tool the same structure — a top-level dispatcher that routes to a dedicated parser depending on which verb the user typed. The result is a tool that scales gracefully as it grows.

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

After all the argument definitions, `parse_args()` is the moment of truth — it reads `sys.argv`, validates everything, and returns a clean `Namespace` object where each argument becomes an attribute. Think of it as the receptionist finishing their checklist and handing you a typed summary sheet: no raw strings, no index lookups, just `args.workers` and you are done.

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

All the concepts above converge in a single, well-structured script. Reading a full real-world example is worth more than reading ten isolated snippets — it shows how argument groups, subcommands, types, and defaults fit together as a coherent whole, the same way you understand a building better by walking through it than by studying individual blueprints.

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

Choosing a CLI library is like choosing a vehicle: the humble stdlib bicycle (argparse) gets you anywhere with zero setup; the electric scooter (click) handles more terrain without much extra weight; the full car (typer) is overkill for a quick errand but the right tool for a long journey. The question is not which is best — it is which fits your project's complexity and dependency budget.

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

Argparse has a handful of quirks that catch nearly every developer at least once. Most come from assumptions carried over from other languages or from misreading the docs. Knowing the pattern in advance turns a frustrating 20-minute debugging session into a one-second fix.

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

## 🔁 Navigation

| | |
|---|---|
| ⬅️ Back to Module | [07_modules_packages/theory.md](../theory.md) |
| 💻 Practice | [practice.md](./practice.md) |
| ⬅️ Prev Subfolder | [01_sys_module ←](../01_sys_module/theory.md) |
| ➡️ Next Subfolder | [03_subprocess →](../03_subprocess/theory.md) |

---

**Related:** [01_sys_module](../01_sys_module/theory.md) · [03_subprocess](../03_subprocess/theory.md) · [04_virtual_environments](../04_virtual_environments/theory.md)
