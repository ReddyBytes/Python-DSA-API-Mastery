# 🤖 Python AI Ecosystem — Interview Preparation Guide
Tools every AI engineer is expected to know

---

# 🧠 What Interviewers Actually Test

AI engineering interviews test:

- Do you know how to handle API keys safely?
- Can you make your LLM calls resilient to failures?
- Do you understand token limits?
- Can you process large datasets without crashing on memory?
- Do you know how to structure a production AI project?

They care about production discipline, not just writing code that works once.

---

# 🔹 Beginner Questions

---

## 1️⃣ Why should you use python-dotenv instead of hardcoding API keys?

Strong answer:

> Hardcoding API keys means they end up in version control. Anyone with access to the repository — including public GitHub repos — can steal and use your keys. python-dotenv loads keys from a `.env` file that you add to `.gitignore`, so secrets never enter the codebase.

Key points:
- `.env` is excluded from git via `.gitignore`
- `os.getenv("KEY")` reads the variable safely after `load_dotenv()`
- You commit `.env.example` with fake values so teammates know what to configure

---

## 2️⃣ What is tenacity and why is it used in AI applications?

Strong answer:

> tenacity is a Python library for automatic retries. LLM APIs fail randomly — rate limit errors (429), temporary server overload (503), network timeouts. Without retry logic, one transient failure breaks the entire pipeline. tenacity wraps functions with a `@retry` decorator that automatically retries on failure, using exponential backoff so you don't hammer the API.

Example:

```python
from tenacity import retry, stop_after_attempt, wait_exponential

@retry(stop=stop_after_attempt(5), wait=wait_exponential(min=2, max=60))
async def call_llm(prompt):
    response = await client.post(url, json={"prompt": prompt})
    response.raise_for_status()
    return response.json()
```

---

## 3️⃣ What is the difference between httpx and requests?

Strong answer:

> `requests` is synchronous only. `httpx` supports both synchronous and asynchronous usage with the same API. In AI applications, you often call multiple LLM endpoints concurrently — embeddings, completions, reranking — so async is important. httpx also has first-class streaming support and better timeout configuration, which matters when LLM responses can take 30-60 seconds.

Key differences:

- `requests.get()` → blocks thread until complete
- `await client.get()` with httpx → other tasks run while waiting
- Both have similar APIs — easy to switch
- httpx supports HTTP/2

---

## 4️⃣ What does tqdm do?

Strong answer:

> tqdm adds a progress bar to any iterable. In AI work, you often process thousands of documents for embedding, clean large fine-tuning datasets, or run batch inference. Without a progress bar, you have no idea if the job is 5% done or 95% done. tqdm wraps any loop and shows estimated time remaining.

```python
from tqdm import tqdm

for doc in tqdm(documents, desc="Embedding"):
    embed(doc)
# Embedding: 100%|████████| 10000/10000 [02:30<00:00, 66.67it/s]
```

---

## 5️⃣ Why use loguru instead of print statements?

Strong answer:

> `print()` has no timestamps, no log levels, and no way to write to a file. Standard `logging` works but requires verbose configuration. loguru gives you structured logging — with timestamps, severity levels, file/line info, and file output — in a single import. In production, you need to know when something happened, how severe it was, and where in the code it came from.

```python
from loguru import logger

logger.info("Starting pipeline")
logger.warning("Token count near limit")
logger.error("API call failed: 429")
# 2024-01-15 10:23:45 | WARNING | client:call_api:45 - Token count near limit
```

---

# 🔹 Intermediate Questions

---

## 6️⃣ How do you count tokens before an OpenAI API call?

Strong answer:

> Use tiktoken, OpenAI's official tokenizer library. You get the encoding for your model, encode the text to tokens, and check the count before sending. If it exceeds the model's context limit, you truncate or split the input.

```python
import tiktoken

enc = tiktoken.encoding_for_model("gpt-4o")

def is_within_limit(text, max_tokens=100_000):
    return len(enc.encode(text)) <= max_tokens

def truncate(text, max_tokens=100_000):
    tokens = enc.encode(text)
    if len(tokens) <= max_tokens:
        return text
    return enc.decode(tokens[:max_tokens])
```

Mention: for chat messages, add ~4 tokens per message for role overhead plus 3 tokens for reply priming.

---

## 7️⃣ How do you add retries with exponential backoff to an LLM API call?

Strong answer:

> Use the `@retry` decorator from tenacity with `wait_exponential`. This doubles the wait time after each failure, preventing hammering a rate-limited API.

```python
from tenacity import retry, stop_after_attempt, wait_exponential, retry_if_exception_type
import httpx

@retry(
    stop=stop_after_attempt(5),
    wait=wait_exponential(multiplier=1, min=2, max=60),
    retry=retry_if_exception_type(httpx.HTTPStatusError)
)
async def call_llm(client, payload):
    response = await client.post(url, json=payload, headers=headers)
    response.raise_for_status()
    return response.json()
```

Wait sequence: 2s → 4s → 8s → 16s → 32s.

For rate limits specifically, also check the `Retry-After` header if the API provides one.

---

## 8️⃣ How do you structure a production AI project?

Strong answer:

```
my-ai-app/
├── .env                    # secrets, gitignored
├── .env.example            # template, committed
├── config/settings.py      # pydantic-settings BaseSettings
├── prompts/                # prompt templates as text files
├── data/
│   ├── raw/                # original, never modified
│   ├── processed/          # cleaned and ready
│   └── outputs/            # LLM results, embeddings
├── src/
│   ├── client.py           # LLM client with retry + token counting
│   ├── pipeline.py         # main processing logic
│   └── utils.py
└── tests/
```

Key principles:

- Secrets in `.env`, never in code
- Prompts in text files, not hardcoded strings — they change often
- `config/settings.py` as single source of truth
- Separate `raw/` from `processed/` — always reproducible

---

## 9️⃣ How do you validate environment configuration with pydantic-settings?

Strong answer:

> pydantic-settings extends Pydantic's `BaseModel` to read from environment variables and `.env` files. You define a `Settings` class with typed fields, and it validates and casts all values at startup. Missing required values raise `ValidationError` immediately — fast fail rather than discovering missing config mid-run.

```python
from pydantic_settings import BaseSettings
from pydantic import Field
from functools import lru_cache

class Settings(BaseSettings):
    openai_api_key: str          # required
    max_tokens: int = 4096       # auto-cast from string "4096"
    debug: bool = False          # auto-cast from "false"
    temperature: float = Field(default=0.7, ge=0.0, le=2.0)

    class Config:
        env_file = ".env"

@lru_cache(maxsize=1)
def get_settings():
    return Settings()
```

---

# 🔹 Advanced Questions

---

## 🔟 How do you handle rate limit errors (429) with tenacity?

Strong answer:

Rate limit errors (429) are the most common failure when calling LLM APIs at scale. The right approach has three parts:

1. Retry only on 429 and 5xx errors, not on 4xx errors like 400 (bad request) or 401 (auth failure).
2. Use random jitter to avoid thundering herd — if 100 workers all retry at the same time, they all hit the rate limit again.
3. Respect the `Retry-After` header if the API provides one.

```python
from tenacity import retry, stop_after_attempt, wait_random_exponential, retry_if_exception_type
import httpx

def should_retry(exc):
    if isinstance(exc, httpx.HTTPStatusError):
        return exc.response.status_code in (429, 500, 502, 503, 504)
    return isinstance(exc, (httpx.TimeoutException, httpx.NetworkError))

@retry(
    stop=stop_after_attempt(6),
    wait=wait_random_exponential(min=1, max=60),
    retry=retry_if_exception_type(Exception),
    reraise=True
)
async def resilient_llm_call(client, payload):
    try:
        r = await client.post(url, json=payload)
        r.raise_for_status()
        return r.json()
    except httpx.HTTPStatusError as e:
        if not should_retry(e):
            raise  # don't retry auth errors
        raise
```

`wait_random_exponential` adds jitter — each retry waits a random amount between 1s and 60s. This spreads retries out and prevents all workers hitting the API simultaneously.

---

## 1️⃣1️⃣ How do you process a 50,000-row JSONL dataset with progress tracking?

Strong answer:

Key principles: stream the file (never load all 50k rows into memory), process in batches for API efficiency, track progress with tqdm, handle failures per-batch so one bad batch doesn't kill the job.

```python
import json
from tqdm import tqdm
from pathlib import Path
from loguru import logger

def read_jsonl(path):
    with open(path, encoding="utf-8") as f:
        for line in f:
            if line.strip():
                yield json.loads(line)

def count_lines(path):
    with open(path) as f:
        return sum(1 for line in f if line.strip())

async def process_dataset(input_path: str, output_path: str, batch_size: int = 20):
    total = count_lines(input_path)
    logger.info(f"Processing {total} records from {input_path}")

    records = read_jsonl(input_path)
    processed = 0

    with tqdm(total=total, desc="Processing") as pbar:
        batch = []
        for record in records:
            batch.append(record)

            if len(batch) == batch_size:
                try:
                    results = await process_batch(batch)
                    write_results(output_path, results)
                    processed += len(batch)
                except Exception as e:
                    logger.error(f"Batch failed: {e}")
                finally:
                    pbar.update(len(batch))
                    batch = []

        # Flush remaining
        if batch:
            results = await process_batch(batch)
            write_results(output_path, results)
            pbar.update(len(batch))

    logger.info(f"Done. Processed {processed}/{total} records.")
```

---

## 1️⃣2️⃣ How do you validate environment config with pydantic-settings and make it fail fast?

Strong answer:

> Fail fast means the application crashes at startup with a clear error message if config is wrong — rather than crashing mid-request when a user is waiting.

```python
from pydantic_settings import BaseSettings
from pydantic import Field, validator
from functools import lru_cache
import sys

class Settings(BaseSettings):
    openai_api_key: str
    anthropic_api_key: str = ""
    model_name: str = "gpt-4o"
    max_tokens: int = Field(default=4096, gt=0, le=128000)
    temperature: float = Field(default=0.7, ge=0.0, le=2.0)
    environment: str = Field(default="development", pattern="^(development|staging|production)$")

    @validator("openai_api_key")
    def validate_key_format(cls, v):
        if not v.startswith("sk-"):
            raise ValueError("OpenAI API key must start with 'sk-'")
        return v

    class Config:
        env_file = ".env"

@lru_cache(maxsize=1)
def get_settings() -> Settings:
    return Settings()

# Call at module import time — crashes before serving any requests
try:
    settings = get_settings()
except Exception as e:
    print(f"Configuration error: {e}")
    sys.exit(1)
```

The `@validator` runs Pydantic validators at instantiation. Combined with `lru_cache`, the settings object is validated once and shared everywhere.

---

## 1️⃣3️⃣ Rapid-Fire Round

```
Q: What format do LLM fine-tuning datasets use?
A: JSONL — one JSON object per line, no outer array.

Q: How do you make pathlib paths relative to the source file, not cwd?
A: Path(__file__).parent / "data" / "file.txt"

Q: What is the difference between os.getenv and os.environ[]?
A: os.getenv returns None if key missing. os.environ[] raises KeyError.

Q: Why use wait_random_exponential instead of wait_exponential?
A: Random jitter prevents thundering herd — all retrying workers hit the API at different times.

Q: How do you stream LLM token output with httpx?
A: async with client.stream("POST", url, json=payload) as r: async for chunk in r.aiter_text()

Q: How do you check token count for gpt-4o messages?
A: tiktoken.encoding_for_model("gpt-4o"), then len(enc.encode(text))

Q: Why use pydantic-settings instead of just os.getenv everywhere?
A: Type safety, validation, single source of truth, auto-cast types, IDE autocompletion.

Q: What is the @logger.catch decorator in loguru?
A: Wraps a function to catch and log any exception with full traceback instead of crashing silently.

Q: How do you write multiple records to a JSONL file?
A: Open with mode "w" or "a", write json.dumps(record) + "\n" for each record.

Q: What rich class do you use to display tabular data in the terminal?
A: rich.table.Table, then console.print(table)
```

---

# 🔥 How to Answer Like a Strong Candidate

Weak:

"I use requests and print statements."

Strong:

> "For production AI applications, I use httpx for async HTTP calls with proper timeout configuration, tenacity with exponential backoff for API retry logic, tiktoken to validate token counts before sending, loguru for structured logging with file output, and pydantic-settings to validate all environment config at startup. All API keys live in `.env` files loaded by python-dotenv, never hardcoded."

Structured. Tool-aware. Production-minded.

---

# 🔁 Navigation

| | |
|---|---|
| 📖 Theory | [theory.md](./theory.md) |
| 📋 Cheatsheet | [cheatsheet.md](./cheatsheet.md) |
| 💻 Practice | [practice.py](./practice.py) |

---

**[🏠 Back to README](../README.md)**

**Prev:** [← Cheat Sheet](./cheatsheet.md) &nbsp;|&nbsp; **Next:** [Interview Master — Python 0-2 Years →](../99_interview_master/python_0_2_years.md)

**Related Topics:** [Theory](./theory.md) · [Cheat Sheet](./cheatsheet.md)
