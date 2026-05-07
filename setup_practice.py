#!/usr/bin/env python3
"""
setup_practice.py
=================
Run this once after cloning to create local practice files in every module folder.

    python3 setup_practice.py

What it does:
  - For folders with practice.md  → creates practice_local.py with Q numbers,
    problem statements, and starter code (NO hints, NO answers)
  - For all other module folders  → creates a blank practice_local.py scratch file

These files are gitignored — they are yours to write in freely.
Full hints and answers are always in practice.md.
"""

import os
import re

REPO_ROOT = os.path.dirname(os.path.abspath(__file__))

MODULE_DIRS = [
    "01_Python_Mastery",
    "02_DSA_Mastery",
    "03_API_Mastery",
    "04_System_Design_Mastery",
    "05_Capstone_Projects",
]

SKIP_DIRS = {"assets", ".git", "__pycache__", "99_interview_master"}


# ── Parser ────────────────────────────────────────────────────────────────────

def parse_practice_md(filepath):
    """
    Extract Q title, problem statement, and starter code from a practice.md.
    Returns a list of dicts: {title, problem, code}
    Hints and answers are intentionally excluded.
    """
    with open(filepath, encoding="utf-8") as f:
        content = f.read()

    problems = []

    # Split on Q headings (### Q1 ..., ### Q2 ..., etc.)
    blocks = re.split(r"(?=\n### Q\d+)", content)

    for block in blocks:
        heading = re.match(r"\n?### (Q\d+\s·\s.+)", block)
        if not heading:
            continue

        full_title = heading.group(1).strip()

        # Problem statement: between **Problem:** and the first ```python or **Your answer:**
        problem_match = re.search(
            r"\*\*Problem:\*\*\n(.*?)(?=```|\*\*Your answer)", block, re.DOTALL
        )
        problem_text = problem_match.group(1).strip() if problem_match else ""

        # Starter code: first ```python block only
        code_match = re.search(r"```python\n(.*?)```", block, re.DOTALL)
        starter_code = code_match.group(1).rstrip() if code_match else ""

        problems.append(
            {"title": full_title, "problem": problem_text, "code": starter_code}
        )

    return problems


# ── Writers ───────────────────────────────────────────────────────────────────

def write_from_practice_md(folder, module_name, problems):
    """Create practice_local.py populated with Q numbers + problem statements."""
    lines = [
        "# " + "=" * 62,
        f"# Practice — {module_name}",
        "# " + "=" * 62,
        "# LOCAL ONLY — this file is gitignored, never pushed.",
        "# Full hints and answers → practice.md",
        "# " + "=" * 62,
        "",
    ]

    for p in problems:
        lines.append("# " + "-" * 62)
        lines.append(f"# {p['title']}")
        lines.append("# " + "-" * 62)

        # Problem statement as comments
        if p["problem"]:
            for line in p["problem"].splitlines():
                lines.append(f"# {line}" if line.strip() else "#")

        lines.append("#")
        lines.append("# ✏️  Write your answer below, then check practice.md")
        lines.append("")

        # Starter code (uncommented so it can be run directly)
        if p["code"]:
            lines.extend(p["code"].splitlines())

        lines.append("")
        lines.append("")

    path = os.path.join(folder, "practice_local.py")
    with open(path, "w", encoding="utf-8") as f:
        f.write("\n".join(lines) + "\n")

    return path


def write_blank(folder, module_name, rel_path):
    """Create a minimal blank scratch file for modules without practice.md."""
    lines = [
        "# " + "=" * 62,
        f"# Practice — {module_name}",
        f"# Path: {rel_path}",
        "# " + "=" * 62,
        "# LOCAL ONLY — this file is gitignored, never pushed.",
        "# Use this file to experiment with concepts from theory.md",
        "# " + "=" * 62,
        "",
        "# Write your code below:",
        "",
    ]
    path = os.path.join(folder, "practice_local.py")
    with open(path, "w", encoding="utf-8") as f:
        f.write("\n".join(lines) + "\n")

    return path


# ── Main ──────────────────────────────────────────────────────────────────────

def get_module_folders():
    """Yield (abs_path, rel_path) for every leaf module folder."""
    for section in MODULE_DIRS:
        section_path = os.path.join(REPO_ROOT, section)
        if not os.path.isdir(section_path):
            continue

        for entry in sorted(os.listdir(section_path)):
            if entry in SKIP_DIRS or entry.startswith("."):
                continue
            full = os.path.join(section_path, entry)
            if os.path.isdir(full):
                yield full, os.path.join(section, entry)


def main():
    created = 0
    skipped = 0
    with_questions = 0

    for folder, rel_path in get_module_folders():
        target = os.path.join(folder, "practice_local.py")
        module_name = os.path.basename(folder).replace("_", " ").title()

        practice_md = os.path.join(folder, "practice.md")

        if os.path.exists(practice_md):
            problems = parse_practice_md(practice_md)
            if problems:
                write_from_practice_md(folder, module_name, problems)
                print(f"  ✅ {rel_path}  ({len(problems)} questions)")
                with_questions += 1
                created += 1
                continue

        # No practice.md or empty → blank scratch file
        write_blank(folder, module_name, rel_path)
        print(f"  📄 {rel_path}  (blank scratch file)")
        created += 1

    print()
    print(f"Created : {created} files")
    print(f"  with questions : {with_questions}")
    print(f"  blank scratch  : {created - with_questions}")
    print()
    print("All practice_local.py files are gitignored.")
    print("Open any one and start writing. Check practice.md for hints and answers.")


if __name__ == "__main__":
    main()
