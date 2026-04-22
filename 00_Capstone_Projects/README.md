# Capstone Projects

Two end-to-end projects that put every skill in this repo to work.

Each project is self-contained: its own README, a step-by-step build guide, an architecture reference, and a runnable starter skeleton.

---

## Projects

| # | Project | Core Skills | Difficulty |
|---|---------|-------------|------------|
| 01 | [E-Commerce API in FastAPI](./01_Ecommerce_API_FastAPI/README.md) | OOP, FastAPI, SQLAlchemy, JWT auth, pytest, Docker | Intermediate → Advanced |
| 02 | [Data Pipeline CLI Tool](./02_Data_Pipeline_CLI/README.md) | argparse, requests, pandas, SQLite, logging, packaging | Beginner → Intermediate |

---

## Recommended Order

**Start with Project 02** if you are still building confidence with Python tooling. It has no web framework, just pure Python working with external data.

**Move to Project 01** once you are comfortable with: Python OOP, basic REST concepts, Pydantic, and SQLAlchemy fundamentals. All of those are covered in the parent repo's learning sections.

```
python-complete-mastery/05_oops          ← needed for Project 01 models
python-complete-mastery/14_type_hints_and_pydantic  ← needed for both
api-mastery/07_fastapi                   ← needed for Project 01
python-complete-mastery/17_testing       ← needed for both
```

---

## Skill Prerequisites

### Project 01 — E-Commerce API

| Skill | Where to learn it |
|-------|------------------|
| Python OOP | `python-complete-mastery/05_oops` |
| Pydantic models | `python-complete-mastery/14_type_hints_and_pydantic` |
| FastAPI basics | `api-mastery/07_fastapi/first_api.md` |
| SQLAlchemy ORM | `api-mastery/07_fastapi/database_guide.md` |
| JWT auth | `api-mastery/05_authentication` |
| pytest | `python-complete-mastery/17_testing` |
| Docker | `Container-Engineering` repo |

### Project 02 — Data Pipeline CLI

| Skill | Where to learn it |
|-------|------------------|
| Python functions | `python-complete-mastery/04_functions` |
| Pydantic validation | `python-complete-mastery/14_type_hints_and_pydantic` |
| File handling | `python-complete-mastery/08_file_handling` |
| Logging | `python-complete-mastery/09_logging_debugging` |
| Testing with mocks | `python-complete-mastery/17_testing` |

---

## Navigation

| | |
|---|---|
| Back | [Repository README](../README.md) |
| Project 01 | [E-Commerce API in FastAPI](./01_Ecommerce_API_FastAPI/README.md) |
| Project 02 | [Data Pipeline CLI Tool](./02_Data_Pipeline_CLI/README.md) |
