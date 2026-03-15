# 🤖 Python AI Ecosystem — Cheatsheet
Quick reference for every tool in the AI utility belt.

---

## python-dotenv

```bash
pip install python-dotenv
```

```python
from dotenv import load_dotenv
import os

load_dotenv()                              # reads .env in current directory
load_dotenv("path/to/.env")               # specific file
load_dotenv(override=True)                # .env values override existing env vars

api_key = os.getenv("OPENAI_API_KEY")     # None if missing (safe)
api_key = os.environ["OPENAI_API_KEY"]    # KeyError if missing (strict)
api_key = os.getenv("KEY", "default")     # with default value
```

**Gotcha:** Call `load_dotenv()` before any `os.getenv()` calls. Call it once at app startup.

**Gotcha:** Add `.env` to `.gitignore` immediately. Commit `.env.example` with fake values instead.

---

## httpx

```bash
pip install httpx
```

```python
import httpx

# Sync GET
r = httpx.get("https://api.example.com/data", headers={"Authorization": f"Bearer {key}"})
r.json()
r.text
r.status_code
r.raise_for_status()   # raises HTTPStatusError on 4xx/5xx

# Sync POST
r = httpx.post(url, json={"key": "value"}, headers=headers)

# Async client (preferred — reuse for multiple calls)
async with httpx.AsyncClient(timeout=30.0) as client:
    r = await client.post(url, json=payload)

# Custom timeout
timeout = httpx.Timeout(connect=5.0, read=60.0, write=10.0)
async with httpx.AsyncClient(timeout=timeout) as client:
    r = await client.post(url, json=payload)

# Streaming response
async with client.stream("POST", url, json=payload) as r:
    async for chunk in r.aiter_text():
        print(chunk, end="")
```

**Gotcha:** Create `AsyncClient` once and reuse it. Don't create a new client per request.

**Gotcha:** Always set a `read` timeout for LLM calls — responses can take 30-60 seconds.

---

## tenacity

```bash
pip install tenacity
```

```python
from tenacity import (
    retry,
    stop_after_attempt,
    wait_exponential,
    wait_random_exponential,
    retry_if_exception_type,
    before_sleep_log
)
import logging

# Basic retry (3 attempts)
@retry(stop=stop_after_attempt(3))
def call_api(): ...

# Exponential backoff: 2s, 4s, 8s, 16s (capped at 60s)
@retry(
    stop=stop_after_attempt(5),
    wait=wait_exponential(multiplier=1, min=2, max=60)
)
def call_api(): ...

# Random jitter (good for avoiding thundering herd)
@retry(wait=wait_random_exponential(min=1, max=60))
def call_api(): ...

# Only retry specific exceptions
@retry(
    stop=stop_after_attempt(5),
    wait=wait_exponential(min=1, max=30),
    retry=retry_if_exception_type(httpx.TimeoutException)
)
def call_api(): ...

# Log retries
@retry(
    stop=stop_after_attempt(5),
    wait=wait_exponential(min=1, max=30),
    before_sleep=before_sleep_log(logging.getLogger(__name__), logging.WARNING)
)
def call_api(): ...
```

**Gotcha:** Works on async functions too — just decorate `async def` the same way.

**Gotcha:** `wait_random_exponential` adds jitter — important when many clients retry simultaneously (rate limits).

---

## tiktoken

```bash
pip install tiktoken
```

```python
import tiktoken

# Get encoding for a model
enc = tiktoken.encoding_for_model("gpt-4o")

# Count tokens in a string
text = "Hello, world!"
tokens = enc.encode(text)
count = len(tokens)

# Decode tokens back to string
text_back = enc.decode(tokens)

# Truncate text to token limit
def truncate(text, max_tokens=4000):
    tokens = enc.encode(text)
    return enc.decode(tokens[:max_tokens])

# Get encoding by family name (not model)
enc = tiktoken.get_encoding("cl100k_base")  # gpt-4, gpt-3.5-turbo
enc = tiktoken.get_encoding("o200k_base")   # gpt-4o, gpt-4o-mini
enc = tiktoken.get_encoding("p50k_base")    # text-davinci-003

# Count tokens in chat messages (includes overhead)
def count_chat_tokens(messages, model="gpt-4o"):
    enc = tiktoken.encoding_for_model(model)
    total = 3  # reply priming
    for msg in messages:
        total += 4  # per-message overhead
        for value in msg.values():
            total += len(enc.encode(value))
    return total
```

**Gotcha:** `encoding_for_model()` raises `KeyError` for unknown models — use `get_encoding()` with base name as fallback.

**Gotcha:** Anthropic/Claude uses a different tokenizer — tiktoken only applies to OpenAI models.

---

## tqdm

```bash
pip install tqdm
```

```python
from tqdm import tqdm
from tqdm.asyncio import tqdm as async_tqdm
from tqdm.asyncio import tqdm_asyncio

# Wrap any iterable
for item in tqdm(items, desc="Processing"):
    process(item)

# Manual control (for batches)
pbar = tqdm(total=len(items), desc="Embedding")
for batch in batches:
    process_batch(batch)
    pbar.update(len(batch))
pbar.close()

# Async: wrap asyncio.as_completed
tasks = [async_fn(item) for item in items]
for coro in async_tqdm(asyncio.as_completed(tasks), total=len(tasks)):
    result = await coro

# Async: wrap gather
results = await tqdm_asyncio.gather(*tasks, desc="Calling LLM API")

# Nested bars
for epoch in tqdm(range(10), desc="Epochs"):
    for batch in tqdm(batches, desc="Batches", leave=False):
        train(batch)
```

**Gotcha:** `leave=False` on inner loops prevents nested bars from cluttering output after completion.

**Gotcha:** In Jupyter notebooks, use `from tqdm.notebook import tqdm` for nicer rendering.

---

## loguru

```bash
pip install loguru
```

```python
from loguru import logger

# Log levels
logger.debug("Debug message")
logger.info("Server started on port 8080")
logger.warning("Token count near limit: 3900/4096")
logger.error("API call failed with 429")
logger.critical("Cannot reach any API endpoint")

# F-string style (or structured)
logger.info(f"Model {model} returned {tokens} tokens")

# Log to file with rotation
logger.add("logs/app.log", rotation="10 MB", retention="7 days", level="INFO")

# Log only errors to separate file
logger.add("logs/errors.log", level="ERROR")

# Auto-catch exceptions in a function
@logger.catch
def risky_function():
    ...

# Remove default stderr handler
logger.remove()
logger.add("logs/app.log", level="INFO")  # file only

# Timed blocks
with logger.catch():
    expensive_operation()
```

**Gotcha:** loguru's default handler prints to stderr. In production, `logger.remove()` then `logger.add()` to file.

**Gotcha:** Unlike standard logging, loguru has no need for `getLogger(__name__)` — one global `logger` works everywhere.

---

## rich

```bash
pip install rich
```

```python
from rich import print                  # drop-in replacement for print
from rich.console import Console
from rich.table import Table
from rich.panel import Panel
from rich.syntax import Syntax

console = Console()

# Colored text (markup tags)
console.print("[bold green]Done![/bold green] All embeddings complete.")
console.print("[red]Error:[/red] API key missing.")

# Table
table = Table(title="Results")
table.add_column("Model", style="cyan")
table.add_column("Latency", justify="right")
table.add_row("gpt-4o", "450ms")
table.add_row("claude-3-haiku", "280ms")
console.print(table)

# Panel (boxed output)
console.print(Panel("LLM response text here", title="Response", border_style="green"))

# Syntax highlighted code
console.print(Syntax('print("hello")', "python", theme="monokai"))

# Pretty-print any object
from rich import inspect
inspect(my_object)
```

**Gotcha:** `from rich import print` shadows the built-in `print`. Fine for scripts, careful in libraries.

---

## pydantic-settings

```bash
pip install pydantic-settings
```

```python
from pydantic_settings import BaseSettings
from pydantic import Field
from functools import lru_cache

class Settings(BaseSettings):
    # Required (no default = must be in .env or env vars)
    openai_api_key: str

    # Optional with defaults
    anthropic_api_key: str = ""
    model_name: str = "gpt-4o"
    max_tokens: int = 4096         # auto-cast from string
    temperature: float = 0.7
    debug: bool = False            # "true"/"false" -> bool auto-cast

    # Validated range
    temperature: float = Field(default=0.7, ge=0.0, le=2.0)

    class Config:
        env_file = ".env"
        env_file_encoding = "utf-8"
        case_sensitive = False     # OPENAI_API_KEY and openai_api_key both work

# Singleton
@lru_cache(maxsize=1)
def get_settings() -> Settings:
    return Settings()

settings = get_settings()
print(settings.openai_api_key)  # str, validated
print(settings.max_tokens)      # int, auto-cast from "4096"
```

**Gotcha:** If `openai_api_key` is not in `.env` or environment, pydantic raises `ValidationError` at startup — fast fail.

**Gotcha:** Use `@lru_cache` to avoid re-reading `.env` on every call.

---

## pathlib

```python
from pathlib import Path

# Build paths (/ operator works on Path objects)
BASE_DIR = Path(__file__).parent.parent
data_dir = BASE_DIR / "data"
output_file = data_dir / "results.jsonl"

# Create directory
(BASE_DIR / "outputs").mkdir(parents=True, exist_ok=True)

# Read / write text
content = Path("prompts/system.txt").read_text(encoding="utf-8")
Path("outputs/result.txt").write_text(content, encoding="utf-8")

# Check existence
if output_file.exists():
    data = json.loads(output_file.read_text())

# List files
jsonl_files = list(Path("data").glob("*.jsonl"))
all_py = list(Path("src").rglob("*.py"))

# Path components
p = Path("/data/prompts/system_v2.txt")
p.name     # "system_v2.txt"
p.stem     # "system_v2"
p.suffix   # ".txt"
p.parent   # Path("/data/prompts")
p.stat().st_size  # file size in bytes
```

**Gotcha:** `Path("data")` is relative to wherever you run the script. Use `Path(__file__).parent` for paths relative to the source file.

---

## json and jsonlines

```python
import json

# Dict <-> string
s = json.dumps({"key": "value"}, indent=2)
d = json.loads(s)

# File read/write
with open("file.json", "w") as f:
    json.dump(data, f, indent=2)
with open("file.json") as f:
    data = json.load(f)

# JSONL read (memory efficient — generator)
def read_jsonl(path):
    with open(path, encoding="utf-8") as f:
        for line in f:
            if line.strip():
                yield json.loads(line)

# JSONL write
def write_jsonl(path, records):
    with open(path, "w", encoding="utf-8") as f:
        for r in records:
            f.write(json.dumps(r) + "\n")

# JSONL append
def append_jsonl(path, record):
    with open(path, "a", encoding="utf-8") as f:
        f.write(json.dumps(record) + "\n")
```

```bash
pip install jsonlines   # convenience wrapper
```

```python
import jsonlines
with jsonlines.open("data.jsonl") as r:
    for obj in r: process(obj)
with jsonlines.open("out.jsonl", "w") as w:
    w.write_all(records)
```

**Gotcha:** JSONL files have NO commas between lines and NO outer `[]`. One complete JSON object per line.

**Gotcha:** `json.dumps` fails on non-serializable types like `datetime` or numpy arrays. Add `default=str` as fallback: `json.dumps(data, default=str)`.

---

## 🔁 Navigation

| | |
|---|---|
| 📖 Theory | [theory.md](./theory.md) |
| 🎯 Interview | [interview.md](./interview.md) |
| 💻 Practice | [practice.py](./practice.py) |
