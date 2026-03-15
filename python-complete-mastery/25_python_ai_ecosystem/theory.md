# 🤖 The Python AI Ecosystem — Utility Belt for AI Engineers
From .env Files to Production LLM Clients

---

# 🎯 The Real Problem

You join a new AI team.

The codebase uses libraries you've never heard of:

- `httpx` instead of `requests`
- `tenacity` decorators on every API call
- `tiktoken` to count tokens before sending
- `loguru` instead of print statements
- `tqdm` progress bars everywhere
- `python-dotenv` loading API keys

None of these are hard.

But not knowing them makes you look lost.

This module covers the Python utility belt every AI engineer uses daily.

---

## 1️⃣ python-dotenv — Loading API Keys Safely

### The Problem

Hardcoding API keys in your code is dangerous:

```python
# NEVER do this
openai_api_key = "sk-abc123..."  # gets committed to git
```

One `git push` and your key is compromised.

### The Solution: .env Files

Create a `.env` file in your project root:

```
OPENAI_API_KEY=sk-abc123...
ANTHROPIC_API_KEY=sk-ant-abc123...
DATABASE_URL=postgresql://user:password@localhost/mydb
DEBUG=false
MAX_TOKENS=4096
```

Add `.env` to `.gitignore` immediately:

```
# .gitignore
.env
.env.local
*.env
```

### Loading with python-dotenv

```python
from dotenv import load_dotenv
import os

# Load .env file into environment variables
load_dotenv()

# Now read them
api_key = os.getenv("OPENAI_API_KEY")
debug = os.getenv("DEBUG", "false")  # second arg is default value

# os.getenv vs os.environ
# os.getenv("KEY") returns None if missing — safe
# os.environ["KEY"] raises KeyError if missing — strict

print(api_key)   # sk-abc123...
```

### Load from a specific path

```python
load_dotenv("/path/to/production.env")
```

### Override existing environment variables

```python
load_dotenv(override=True)  # .env values win over system env vars
```

### Check if variable exists

```python
api_key = os.getenv("OPENAI_API_KEY")
if not api_key:
    raise ValueError("OPENAI_API_KEY not set. Add it to your .env file.")
```

### Install

```bash
pip install python-dotenv
```

---

## 2️⃣ httpx — Modern HTTP Client for AI Work

### Why httpx Replaced requests

`requests` is synchronous only.

AI applications are heavily async — calling multiple LLM APIs concurrently, streaming responses, handling timeouts properly.

`httpx` supports both sync and async with the same API.

### Basic Sync Usage

```python
import httpx

# Simple GET
response = httpx.get("https://api.openai.com/v1/models", headers={
    "Authorization": f"Bearer {api_key}"
})
print(response.json())

# POST with JSON body
response = httpx.post(
    "https://api.openai.com/v1/chat/completions",
    headers={"Authorization": f"Bearer {api_key}"},
    json={
        "model": "gpt-4o",
        "messages": [{"role": "user", "content": "Hello"}]
    }
)
data = response.json()
```

### Async Usage — The Real Power

```python
import httpx
import asyncio

async def call_api():
    async with httpx.AsyncClient() as client:
        response = await client.post(
            "https://api.openai.com/v1/chat/completions",
            headers={"Authorization": f"Bearer {api_key}"},
            json={"model": "gpt-4o", "messages": [{"role": "user", "content": "Hi"}]}
        )
        return response.json()

result = asyncio.run(call_api())
```

### Timeout Handling

LLM APIs can be slow. Always set timeouts.

```python
# Timeout in seconds
timeout = httpx.Timeout(
    connect=5.0,    # time to establish connection
    read=60.0,      # time to read response (LLMs are slow)
    write=10.0,     # time to send request
    pool=5.0        # time to get connection from pool
)

async with httpx.AsyncClient(timeout=timeout) as client:
    response = await client.post(url, json=payload)
```

### Streaming Responses

For streaming LLM output (tokens as they arrive):

```python
async with httpx.AsyncClient() as client:
    async with client.stream("POST", url, json=payload) as response:
        async for chunk in response.aiter_text():
            print(chunk, end="", flush=True)
```

### Reusing a Client (Important for Performance)

```python
# BAD: creates new connection every time
for prompt in prompts:
    httpx.post(url, ...)  # new TCP connection each call

# GOOD: reuse connection pool
async with httpx.AsyncClient() as client:
    for prompt in prompts:
        await client.post(url, ...)  # reuses connections
```

### Install

```bash
pip install httpx
```

---

## 3️⃣ tenacity — Automatic Retries for Flaky LLM APIs

### The Problem

LLM APIs fail randomly:

- Rate limit errors (429)
- Server overload (503)
- Timeout (network blip)
- Temporary unavailability

Without retries, one failed call breaks your entire pipeline.

### Basic Retry Decorator

```python
from tenacity import retry, stop_after_attempt, wait_exponential

@retry(stop=stop_after_attempt(3))
def call_llm(prompt):
    # If this raises any exception, retry up to 3 times
    response = httpx.post(url, json={"prompt": prompt})
    response.raise_for_status()
    return response.json()
```

### Exponential Backoff — The Right Way

Don't retry immediately. Wait longer each time.

```python
from tenacity import (
    retry,
    stop_after_attempt,
    wait_exponential,
    retry_if_exception_type,
    before_sleep_log
)
import logging

logger = logging.getLogger(__name__)

@retry(
    stop=stop_after_attempt(5),
    wait=wait_exponential(multiplier=1, min=2, max=60),
    retry=retry_if_exception_type(httpx.HTTPStatusError),
    before_sleep=before_sleep_log(logger, logging.WARNING)
)
async def call_llm_with_retry(client, prompt):
    response = await client.post(url, json={"prompt": prompt})
    response.raise_for_status()
    return response.json()
```

Wait times: 2s → 4s → 8s → 16s → 32s (capped at 60s).

### Retry Only on Specific Errors

```python
from tenacity import retry_if_exception_type, retry_if_result

def is_rate_limited(response):
    return response.status_code == 429

@retry(
    stop=stop_after_attempt(5),
    wait=wait_exponential(min=1, max=60),
    retry=retry_if_exception_type((httpx.TimeoutException, httpx.NetworkError))
)
async def call_api(client, url):
    return await client.get(url)
```

### Before Sleep Logging

Know exactly what is happening during retries:

```python
from tenacity import before_sleep_log
import logging

@retry(
    stop=stop_after_attempt(5),
    wait=wait_exponential(multiplier=2, min=1, max=30),
    before_sleep=before_sleep_log(logging.getLogger(__name__), logging.WARNING)
)
def flaky_call():
    ...
# Logs: "Retrying flaky_call in 2.0 seconds (attempt 1)"
```

### Install

```bash
pip install tenacity
```

---

## 4️⃣ tiktoken — Count Tokens Before Sending

### The Problem

Every LLM has a context window limit.

GPT-4o: 128k tokens.
Claude 3.5 Sonnet: 200k tokens.

If your prompt + conversation history exceeds the limit, the API returns an error.

Token counting before sending lets you truncate or split safely.

### Basic Token Counting

```python
import tiktoken

# Get encoding for a specific model
enc = tiktoken.encoding_for_model("gpt-4o")

text = "Hello, how are you today?"
tokens = enc.encode(text)
print(len(tokens))   # 6
```

### Count Tokens in a Chat Messages List

OpenAI chat format has overhead per message (role tags etc).

```python
import tiktoken

def count_tokens_in_messages(messages, model="gpt-4o"):
    enc = tiktoken.encoding_for_model(model)

    # Each message has overhead: 4 tokens (role + separators)
    tokens_per_message = 4
    tokens_per_name = 1

    total = 0
    for message in messages:
        total += tokens_per_message
        for key, value in message.items():
            total += len(enc.encode(value))
            if key == "name":
                total += tokens_per_name

    total += 3  # reply priming
    return total

messages = [
    {"role": "system", "content": "You are a helpful assistant."},
    {"role": "user", "content": "What is the capital of France?"}
]
print(count_tokens_in_messages(messages))  # ~26
```

### Truncate to Fit Context Window

```python
def truncate_to_limit(text, max_tokens=4000, model="gpt-4o"):
    enc = tiktoken.encoding_for_model(model)
    tokens = enc.encode(text)

    if len(tokens) <= max_tokens:
        return text

    # Truncate and decode back to string
    truncated = tokens[:max_tokens]
    return enc.decode(truncated)
```

### Get Encoding by Name (Not Model)

```python
# For models not in tiktoken's model map
enc = tiktoken.get_encoding("cl100k_base")  # GPT-4 family
enc = tiktoken.get_encoding("o200k_base")   # GPT-4o family
enc = tiktoken.get_encoding("p50k_base")    # GPT-3 family
```

### Install

```bash
pip install tiktoken
```

---

## 5️⃣ tqdm — Progress Bars for Batch AI Work

### The Problem

Embedding 10,000 documents. Processing 50,000 JSONL rows. Fine-tuning data prep.

Without a progress bar, you stare at a blank terminal wondering if the job is alive.

### Basic Usage

```python
from tqdm import tqdm
import time

documents = ["doc1", "doc2", "doc3", ...]  # 10000 items

for doc in tqdm(documents):
    embed(doc)
# Output: 100%|████████████| 10000/10000 [02:30<00:00, 66.67it/s]
```

### With Description

```python
for doc in tqdm(documents, desc="Embedding documents"):
    embed(doc)
# Output: Embedding documents: 100%|████| 10000/10000 [02:30<00:00]
```

### Manual tqdm (when you control the loop)

```python
from tqdm import tqdm

progress = tqdm(total=10000, desc="Processing")

for batch in batches:
    process_batch(batch)
    progress.update(len(batch))

progress.close()
```

### tqdm with enumerate

```python
for i, doc in enumerate(tqdm(documents)):
    results[i] = embed(doc)
```

### tqdm in Async Code

```python
import asyncio
from tqdm.asyncio import tqdm as async_tqdm

async def embed_all(documents):
    tasks = [embed_async(doc) for doc in documents]
    results = []

    for coro in async_tqdm(asyncio.as_completed(tasks), total=len(tasks)):
        result = await coro
        results.append(result)

    return results
```

### tqdm with gather

```python
from tqdm.asyncio import tqdm_asyncio

results = await tqdm_asyncio.gather(*tasks, desc="Calling LLM")
```

### Nested Progress Bars

```python
from tqdm import tqdm

for epoch in tqdm(range(10), desc="Epochs"):
    for batch in tqdm(batches, desc="Batches", leave=False):
        train(batch)
```

### Install

```bash
pip install tqdm
```

---

## 6️⃣ loguru — Structured Logging for AI Apps

### Why Not print()?

`print()` has no timestamps, no log levels, no file output, no filtering.

### Why Not standard logging?

Standard `logging` is verbose to configure. 15 lines of boilerplate for basic setup.

`loguru` gives you structured, beautiful logging in one import.

### Basic Usage

```python
from loguru import logger

logger.debug("Loading config...")
logger.info("Starting LLM client")
logger.warning("Token count high: 3800/4096")
logger.error("API call failed: 429 Rate Limited")
logger.critical("Cannot connect to API")
```

Output:
```
2024-01-15 10:23:45.123 | INFO     | __main__:main:12 - Starting LLM client
2024-01-15 10:23:46.234 | WARNING  | __main__:call_api:45 - Token count high: 3800/4096
```

### Log Variables Cleanly

```python
model = "gpt-4o"
token_count = 1234

logger.info(f"Calling {model} with {token_count} tokens")
# or with structured fields:
logger.info("API call", model=model, tokens=token_count)
```

### Log to File

```python
logger.add("logs/app.log", rotation="10 MB", retention="7 days")
```

### Log Level Filtering

```python
logger.add("logs/errors.log", level="ERROR")
logger.add("logs/debug.log", level="DEBUG")
```

### Catch Exceptions Automatically

```python
@logger.catch
def process_batch(items):
    for item in items:
        embed(item)  # if this raises, loguru logs full traceback

# or in async:
async def process():
    with logger.catch():
        await call_llm()
```

### Disable for Production

```python
import os

if os.getenv("ENV") == "production":
    logger.remove()  # remove default handler
    logger.add("logs/app.log", level="INFO")
```

### Install

```bash
pip install loguru
```

---

## 7️⃣ rich — Beautiful Terminal Output for AI CLI Tools

### What rich Does

- Colored text and syntax highlighting
- Tables for displaying results
- Panels for grouped output
- Markdown rendering in terminal
- Progress bars (alternative to tqdm)
- Pretty-printing Python objects

### Colored Output

```python
from rich import print
from rich.console import Console

console = Console()

console.print("[bold green]Success![/bold green] Embedding complete.")
console.print("[red]Error:[/red] API key not found.")
console.print("[yellow]Warning:[/yellow] Token count near limit.")
```

### Tables

```python
from rich.table import Table
from rich.console import Console

console = Console()
table = Table(title="LLM Benchmark Results")

table.add_column("Model", style="cyan")
table.add_column("Latency (ms)", justify="right")
table.add_column("Cost per 1k tokens", justify="right")

table.add_row("gpt-4o", "450", "$0.005")
table.add_row("claude-3-haiku", "280", "$0.00025")
table.add_row("gpt-3.5-turbo", "200", "$0.0005")

console.print(table)
```

### Panels

```python
from rich.panel import Panel
from rich.console import Console

console = Console()
console.print(Panel("LLM response goes here", title="GPT-4o", border_style="green"))
```

### Syntax Highlighted Code

```python
from rich.syntax import Syntax
from rich.console import Console

console = Console()
code = 'response = await client.post(url, json={"prompt": "Hello"})'
syntax = Syntax(code, "python", theme="monokai")
console.print(syntax)
```

### Install

```bash
pip install rich
```

---

## 8️⃣ pydantic-settings — Production Config Validation

### The Problem with os.getenv

```python
# Scattered across codebase
api_key = os.getenv("OPENAI_API_KEY")
max_tokens = int(os.getenv("MAX_TOKENS", "4096"))  # manual casting
debug = os.getenv("DEBUG", "false").lower() == "true"  # manual bool
```

No type checking. No validation. No IDE autocompletion. Easy to miss a variable.

### pydantic-settings Solution

```python
from pydantic_settings import BaseSettings
from pydantic import Field

class Settings(BaseSettings):
    openai_api_key: str                          # required, string
    anthropic_api_key: str = ""                  # optional
    max_tokens: int = 4096                       # auto-cast from string
    debug: bool = False                          # "true"/"false" -> bool
    model_name: str = "gpt-4o"
    temperature: float = Field(default=0.7, ge=0.0, le=2.0)  # validated range

    class Config:
        env_file = ".env"          # reads from .env automatically
        env_file_encoding = "utf-8"

# Single instantiation
settings = Settings()

# Usage
print(settings.openai_api_key)   # str, guaranteed
print(settings.max_tokens)       # int, automatically cast from "4096"
print(settings.debug)            # bool, automatically cast from "false"
```

### Singleton Pattern for Settings

```python
from functools import lru_cache

@lru_cache(maxsize=1)
def get_settings() -> Settings:
    return Settings()

# Use everywhere
settings = get_settings()
```

### Nested Settings

```python
from pydantic import BaseModel
from pydantic_settings import BaseSettings

class DatabaseConfig(BaseModel):
    host: str = "localhost"
    port: int = 5432
    name: str = "mydb"

class Settings(BaseSettings):
    openai_api_key: str
    database: DatabaseConfig = DatabaseConfig()

    class Config:
        env_file = ".env"
```

### Install

```bash
pip install pydantic-settings
```

---

## 9️⃣ pathlib — Modern File Path Handling

### Why pathlib Over os.path

```python
# Old way (os.path — string concatenation nightmares)
import os
path = os.path.join("data", "prompts", "system.txt")
exists = os.path.exists(path)

# New way (pathlib — objects, readable, safe)
from pathlib import Path
path = Path("data") / "prompts" / "system.txt"
exists = path.exists()
```

### AI Project File Operations

```python
from pathlib import Path

# Project structure
BASE_DIR = Path(__file__).parent.parent  # two levels up from current file
PROMPTS_DIR = BASE_DIR / "prompts"
DATA_DIR = BASE_DIR / "data"
OUTPUTS_DIR = BASE_DIR / "outputs"

# Create directories
OUTPUTS_DIR.mkdir(parents=True, exist_ok=True)

# Read a prompt template
system_prompt = (PROMPTS_DIR / "system.txt").read_text(encoding="utf-8")

# Write LLM output
output_file = OUTPUTS_DIR / "results.json"
output_file.write_text(json.dumps(results, indent=2), encoding="utf-8")

# List all JSONL files in data directory
jsonl_files = list(DATA_DIR.glob("*.jsonl"))

# Check if file exists before reading
config_file = BASE_DIR / "config.json"
if config_file.exists():
    config = json.loads(config_file.read_text())
```

### Useful pathlib Methods

```python
path = Path("/data/prompts/system_v2.txt")

path.name        # "system_v2.txt"
path.stem        # "system_v2"
path.suffix      # ".txt"
path.parent      # Path("/data/prompts")
path.exists()    # True/False
path.is_file()   # True
path.is_dir()    # False

# Walk directory tree
for f in Path("data").rglob("*.jsonl"):
    print(f)

# Get file size
size_mb = path.stat().st_size / 1_000_000
```

---

## 🔟 json and jsonlines — Standard Formats for LLM Data

### JSON — The Basics

```python
import json

# Dict to JSON string
data = {"model": "gpt-4o", "tokens": 1234, "response": "Hello"}
json_string = json.dumps(data, indent=2)

# JSON string to dict
parsed = json.loads(json_string)

# Read/write JSON files
with open("results.json", "w") as f:
    json.dump(data, f, indent=2)

with open("results.json") as f:
    data = json.load(f)
```

### JSONL — JSON Lines (Standard for LLM Datasets)

JSONL = one JSON object per line. No commas between lines. No outer array.

This is the format for:
- OpenAI fine-tuning datasets
- LLM conversation logs
- Embedding batch jobs
- Large datasets that can't fit in memory

```jsonl
{"messages": [{"role": "user", "content": "Hello"}, {"role": "assistant", "content": "Hi there!"}]}
{"messages": [{"role": "user", "content": "What is 2+2?"}, {"role": "assistant", "content": "4"}]}
```

### Reading JSONL

```python
def read_jsonl(filepath):
    with open(filepath, encoding="utf-8") as f:
        for line in f:
            line = line.strip()
            if line:  # skip empty lines
                yield json.loads(line)

# Usage — memory efficient, generator-based
for record in read_jsonl("training_data.jsonl"):
    print(record["messages"])
```

### Writing JSONL

```python
def write_jsonl(filepath, records):
    with open(filepath, "w", encoding="utf-8") as f:
        for record in records:
            f.write(json.dumps(record) + "\n")

# Append to existing JSONL
def append_jsonl(filepath, record):
    with open(filepath, "a", encoding="utf-8") as f:
        f.write(json.dumps(record) + "\n")
```

### Count Lines Without Loading All

```python
def count_jsonl_lines(filepath):
    with open(filepath) as f:
        return sum(1 for line in f if line.strip())
```

### jsonlines Library (Convenience Wrapper)

```python
import jsonlines

# Read
with jsonlines.open("data.jsonl") as reader:
    for record in reader:
        process(record)

# Write
with jsonlines.open("output.jsonl", mode="w") as writer:
    for record in records:
        writer.write(record)
```

```bash
pip install jsonlines
```

---

## 1️⃣1️⃣ Project Structure for AI Apps

A production AI application needs clear separation of concerns.

```
my-ai-app/
├── .env                    # API keys, never commit
├── .env.example            # Template for team members, commit this
├── .gitignore
├── pyproject.toml          # or requirements.txt
│
├── config/
│   ├── __init__.py
│   └── settings.py         # pydantic-settings BaseSettings
│
├── prompts/
│   ├── system.txt          # System prompts loaded at runtime
│   ├── rag_system.txt
│   └── summarize.txt
│
├── data/
│   ├── raw/                # Original data, never modified
│   │   └── input.jsonl
│   ├── processed/          # Cleaned, ready to use
│   │   └── training.jsonl
│   └── outputs/            # LLM responses, embeddings, results
│       └── results.jsonl
│
├── src/
│   ├── __init__.py
│   ├── client.py           # LLM client (httpx + tenacity + tiktoken)
│   ├── embeddings.py       # Embedding pipeline
│   ├── pipeline.py         # Main data pipeline
│   └── utils.py            # Helper functions
│
├── tests/
│   └── test_client.py
│
└── scripts/
    ├── embed_documents.py  # One-off scripts, use tqdm
    └── prepare_training.py
```

### Key Principles

Keep secrets in `.env`. Never in code.

Load prompts from files, not hardcoded strings. Prompts change often.

Separate `raw/` from `processed/` data. Always reproducible.

One `settings.py` as single source of truth for config.

---

## 1️⃣2️⃣ requirements.txt vs pyproject.toml for AI Projects

### requirements.txt — Simple and Universal

```
# requirements.txt
httpx==0.27.0
tenacity==8.3.0
tiktoken==0.7.0
tqdm==4.66.4
loguru==0.7.2
python-dotenv==1.0.1
pydantic-settings==2.3.4
rich==13.7.1
openai==1.35.0
anthropic==0.28.0
jsonlines==4.0.0
```

Install: `pip install -r requirements.txt`

### pyproject.toml — Modern Standard

```toml
[project]
name = "my-ai-app"
version = "0.1.0"
requires-python = ">=3.11"
dependencies = [
    "httpx>=0.27",
    "tenacity>=8.3",
    "tiktoken>=0.7",
    "tqdm>=4.66",
    "loguru>=0.7",
    "python-dotenv>=1.0",
    "pydantic-settings>=2.3",
    "rich>=13.7",
    "openai>=1.35",
    "anthropic>=0.28",
]

[project.optional-dependencies]
dev = [
    "pytest>=8.0",
    "pytest-asyncio>=0.23",
]
```

Install: `pip install -e .` or `pip install -e ".[dev]"`

### Virtual Environments for AI Projects

AI projects often need conflicting deps (one project uses older numpy, another uses newer).

Always use a virtual environment per project.

```bash
# Create
python -m venv .venv

# Activate (Mac/Linux)
source .venv/bin/activate

# Activate (Windows)
.venv\Scripts\activate

# Install deps
pip install -r requirements.txt

# Deactivate
deactivate
```

### uv — Fast Modern Replacement

```bash
# Install uv
pip install uv

# Create venv + install in seconds
uv venv
uv pip install -r requirements.txt

# 10-100x faster than pip
```

---

# 🧠 Final Mental Model

The Python AI ecosystem is not complicated.

Each tool solves one problem:

- `python-dotenv` → secrets management
- `httpx` → HTTP calls (sync + async)
- `tenacity` → automatic retries
- `tiktoken` → token counting
- `tqdm` → progress visibility
- `loguru` → structured logging
- `rich` → beautiful terminal output
- `pydantic-settings` → config validation
- `pathlib` → file path handling
- `json/jsonlines` → data formats

You do not need to memorize every function.

You need to know these libraries exist and what problem each one solves.

When you join a new AI team and see these in the codebase — you now know exactly what they do.

---

# 🔁 Navigation

Previous:
[24 — (previous module)](../24_whatever/theory.md)

Next:
[25_python_ai_ecosystem/cheatsheet.md](./cheatsheet.md)
