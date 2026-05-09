# Python AI Ecosystem — Practice

## Quick Index

| Q | Topic | Difficulty |
|---|---|---|
| [Q1](#q1) | python-dotenv — load API key from .env | 🟢 |
| [Q2](#q2) | python-dotenv — raise if key is missing | 🟢 |
| [Q3](#q3) | httpx — sync GET with authorization header | 🟢 |
| [Q4](#q4) | httpx — async POST with AsyncClient | 🟡 |
| [Q5](#q5) | httpx — configure custom timeout object | 🟡 |
| [Q6](#q6) | tenacity — @retry with stop_after_attempt | 🟢 |
| [Q7](#q7) | tenacity — wait_exponential backoff | 🟡 |
| [Q8](#q8) | tenacity — retry_if_exception_type for specific errors | 🟡 |
| [Q9](#q9) | tiktoken — encode a string and count tokens | 🟢 |
| [Q10](#q10) | tiktoken — truncate text to a token limit | 🟡 |
| [Q11](#q11) | tiktoken — count tokens in a chat messages list | 🟠 |
| [Q12](#q12) | tqdm — wrap a list with a progress bar | 🟢 |
| [Q13](#q13) | tqdm — manual pbar with update() | 🟡 |
| [Q14](#q14) | tqdm — async gather with tqdm_asyncio | 🟡 |
| [Q15](#q15) | loguru — basic logger.info/warning/error | 🟢 |
| [Q16](#q16) | loguru — add a file sink with rotation | 🟡 |
| [Q17](#q17) | loguru — bind() structured context | 🟠 |
| [Q18](#q18) | rich — print colored markup to terminal | 🟢 |
| [Q19](#q19) | rich — build and print a Table | 🟡 |
| [Q20](#q20) | pydantic-settings — BaseSettings with env vars | 🟢 |
| [Q21](#q21) | pydantic-settings — lru_cache singleton pattern | 🟡 |
| [Q22](#q22) | pydantic-settings — Field with validated range | 🟡 |
| [Q23](#q23) | pathlib — build paths and mkdir with parents | 🟢 |
| [Q24](#q24) | pathlib — glob for .jsonl files in a directory | 🟡 |
| [Q25](#q25) | json/jsonlines — read a .jsonl file line by line | 🟢 |
| [Q26](#q26) | json/jsonlines — write and append to .jsonl | 🟡 |
| [Q27](#q27) | Project Structure — describe the standard AI app layout | 🟢 |
| [Q28](#q28) | Project Structure — where do prompts and config live? | 🟢 |
| [Q29](#q29) | requirements.txt — pin AI library versions | 🟢 |
| [Q30](#q30) | pyproject.toml — optional dev extras | 🟡 |

---

<a id="q1"></a>

### Q1 · python-dotenv — Load API Key from .env 🟢

> 🛠️ **Solve locally:** [practice_local.py → Q1](./practice_local.py)


You have a `.env` file with `OPENAI_API_KEY=sk-abc123`. Write the minimal code to load it and print the key.


<details>
<summary>💡 Hint</summary>
Call load_dotenv() before os.getenv().
</details>

<details>
<summary>✅ Answer</summary>

```python
from dotenv import load_dotenv
import os

load_dotenv()                         # ← reads .env file into env vars

api_key = os.getenv("OPENAI_API_KEY") # ← returns None if missing (safe)
print(api_key)                        # sk-abc123
```

**Why:** `load_dotenv()` must come first — it injects `.env` values into the process environment so `os.getenv` can find them.
</details>

---

<a id="q2"></a>

### Q2 · python-dotenv — Raise if Key is Missing 🟢

> 🛠️ **Solve locally:** [practice_local.py → Q2](./practice_local.py)


Load `.env` and raise a clear `ValueError` if `OPENAI_API_KEY` is not set. Show the pattern used in production code.


<details>
<summary>💡 Hint</summary>
os.getenv returns None when the key is absent — check for that.
</details>

<details>
<summary>✅ Answer</summary>

```python
from dotenv import load_dotenv
import os

load_dotenv()

api_key = os.getenv("OPENAI_API_KEY")
if not api_key:                       # ← catches None and empty string ""
    raise ValueError(
        "OPENAI_API_KEY not set. Add it to your .env file."
    )

print("Key loaded:", api_key[:8] + "...")  # show first 8 chars safely
```

**Why:** Fail fast at startup with a human-readable message — much better than a cryptic auth error deep in a pipeline.
</details>

---

<a id="q3"></a>

### Q3 · httpx — Sync GET with Authorization Header 🟢

> 🛠️ **Solve locally:** [practice_local.py → Q3](./practice_local.py)


Make a synchronous GET request to `https://api.example.com/models` using httpx. Include a Bearer token header and print the status code.


<details>
<summary>💡 Hint</summary>
httpx.get() for sync, pass headers= as a dict.
</details>

<details>
<summary>✅ Answer</summary>

```python
import httpx

api_key = "sk-demo"
url = "https://api.example.com/models"

response = httpx.get(
    url,
    headers={"Authorization": f"Bearer {api_key}"}  # ← Bearer token
)

print(response.status_code)   # 200
response.raise_for_status()   # ← raises HTTPStatusError on 4xx/5xx
data = response.json()        # ← parse JSON body
```

**Why:** `raise_for_status()` is the safety net — without it a 404 silently returns empty data.
</details>

---

<a id="q4"></a>

### Q4 · httpx — Async POST with AsyncClient 🟡

> 🛠️ **Solve locally:** [practice_local.py → Q4](./practice_local.py)


Send an async POST to an LLM endpoint using `httpx.AsyncClient`. Wrap it in an `async with` block and return the JSON response.


<details>
<summary>💡 Hint</summary>
Use async with httpx.AsyncClient() as client: then await client.post().
</details>

<details>
<summary>✅ Answer</summary>

```python
import httpx
import asyncio

async def call_llm(api_key: str, prompt: str) -> dict:
    url = "https://api.openai.com/v1/chat/completions"
    payload = {
        "model": "gpt-4o",
        "messages": [{"role": "user", "content": prompt}]
    }
    async with httpx.AsyncClient() as client:   # ← reuses connection pool
        response = await client.post(
            url,
            headers={"Authorization": f"Bearer {api_key}"},
            json=payload
        )
        response.raise_for_status()
        return response.json()                  # ← parsed dict

result = asyncio.run(call_llm("sk-demo", "Hello"))
```

**Why:** `AsyncClient` as a context manager ensures the connection pool is closed cleanly after use.
</details>

---

<a id="q5"></a>

### Q5 · httpx — Configure a Custom Timeout Object 🟡

> 🛠️ **Solve locally:** [practice_local.py → Q5](./practice_local.py)


LLM APIs can take 60 seconds to respond. Create an `httpx.Timeout` that allows 5s to connect, 60s to read, and 10s to write. Apply it to an AsyncClient.


<details>
<summary>💡 Hint</summary>
httpx.Timeout takes connect=, read=, write= parameters.
</details>

<details>
<summary>✅ Answer</summary>

```python
import httpx

timeout = httpx.Timeout(
    connect=5.0,   # ← seconds to establish TCP connection
    read=60.0,     # ← seconds to receive response (LLMs are slow)
    write=10.0,    # ← seconds to send the request body
    pool=5.0       # ← seconds to get a connection from the pool
)

async with httpx.AsyncClient(timeout=timeout) as client:
    response = await client.post("https://api.example.com/v1/chat", json={})
    response.raise_for_status()
```

**Why:** Without a `read` timeout, one slow LLM call can hang your entire async event loop indefinitely.
</details>

---

<a id="q6"></a>

### Q6 · tenacity — @retry with stop_after_attempt 🟢

> 🛠️ **Solve locally:** [practice_local.py → Q6](./practice_local.py)


Use tenacity to make a function retry up to 3 times before giving up. Show the minimal decorator.


<details>
<summary>💡 Hint</summary>
Import retry and stop_after_attempt from tenacity.
</details>

<details>
<summary>✅ Answer</summary>

```python
from tenacity import retry, stop_after_attempt

@retry(stop=stop_after_attempt(3))   # ← retry up to 3 times total
def call_llm(prompt: str) -> dict:
    import httpx
    response = httpx.post("https://api.example.com/chat", json={"prompt": prompt})
    response.raise_for_status()      # ← raises on 4xx/5xx, triggers retry
    return response.json()

# If all 3 attempts fail, the last exception propagates
result = call_llm("Hello")
```

**Why:** Any uncaught exception triggers a retry. The final attempt re-raises so you still see the error.
</details>

---

<a id="q7"></a>

### Q7 · tenacity — wait_exponential Backoff 🟡

> 🛠️ **Solve locally:** [practice_local.py → Q7](./practice_local.py)


Add exponential backoff to an LLM call: start at 2 seconds, double each retry, cap at 60 seconds. Use 5 max attempts.


<details>
<summary>💡 Hint</summary>
wait_exponential takes multiplier=, min=, max= parameters.
</details>

<details>
<summary>✅ Answer</summary>

```python
from tenacity import retry, stop_after_attempt, wait_exponential

@retry(
    stop=stop_after_attempt(5),
    wait=wait_exponential(multiplier=1, min=2, max=60)
    # ← wait sequence: 2s → 4s → 8s → 16s → 32s (capped at 60)
)
async def call_llm(prompt: str) -> dict:
    import httpx
    async with httpx.AsyncClient() as client:
        r = await client.post("https://api.example.com/chat", json={"prompt": prompt})
        r.raise_for_status()
        return r.json()
```

**Why:** Exponential backoff gives the API time to recover from overload — hammering immediately just makes rate limits worse.
</details>

---

<a id="q8"></a>

### Q8 · tenacity — retry_if_exception_type for Specific Errors 🟡

> 🛠️ **Solve locally:** [practice_local.py → Q8](./practice_local.py)


Retry only on `httpx.TimeoutException` and `httpx.NetworkError` — not on auth errors (401) or bad requests (400). Show the decorator.


<details>
<summary>💡 Hint</summary>
Pass retry=retry_if_exception_type() with a tuple of exception types.
</details>

<details>
<summary>✅ Answer</summary>

```python
from tenacity import (
    retry, stop_after_attempt, wait_exponential, retry_if_exception_type
)
import httpx

@retry(
    stop=stop_after_attempt(5),
    wait=wait_exponential(min=1, max=30),
    retry=retry_if_exception_type(          # ← only retry these types
        (httpx.TimeoutException, httpx.NetworkError)
    )
)
async def call_api(client: httpx.AsyncClient, url: str):
    response = await client.get(url)
    response.raise_for_status()   # 401/400 raises HTTPStatusError — NOT retried
    return response.json()
```

**Why:** Retrying auth errors is wasteful — they won't recover on their own. Only transient failures (timeouts, network blips) benefit from retries.
</details>

---

<a id="q9"></a>

### Q9 · tiktoken — Encode a String and Count Tokens 🟢

> 🛠️ **Solve locally:** [practice_local.py → Q9](./practice_local.py)


Count how many GPT-4o tokens are in the string `"Hello, how are you today?"` using tiktoken.


<details>
<summary>💡 Hint</summary>
tiktoken.encoding_for_model("gpt-4o"), then enc.encode(text).
</details>

<details>
<summary>✅ Answer</summary>

```python
import tiktoken

enc = tiktoken.encoding_for_model("gpt-4o")  # ← get model's tokenizer

text = "Hello, how are you today?"
tokens = enc.encode(text)          # ← list of integer token IDs

print(len(tokens))                 # ← 6 tokens
print(tokens)                      # [9906, 11, 1268, 527, 499, 3432, 30]

# Decode back to verify
print(enc.decode(tokens))          # "Hello, how are you today?"
```

**Why:** One word is not one token — punctuation, spaces, and subwords each cost tokens. Counting before sending prevents context-limit errors.
</details>

---

<a id="q10"></a>

### Q10 · tiktoken — Truncate Text to a Token Limit 🟡

> 🛠️ **Solve locally:** [practice_local.py → Q10](./practice_local.py)


Write a function `truncate_to_limit(text, max_tokens, model)` that returns the text truncated so it fits within `max_tokens` for the given model.


<details>
<summary>💡 Hint</summary>
Encode → slice the token list → decode back to a string.
</details>

<details>
<summary>✅ Answer</summary>

```python
import tiktoken

def truncate_to_limit(text: str, max_tokens: int = 4000, model: str = "gpt-4o") -> str:
    enc = tiktoken.encoding_for_model(model)
    tokens = enc.encode(text)          # ← encode to token IDs

    if len(tokens) <= max_tokens:
        return text                    # ← already fits, no change

    truncated = tokens[:max_tokens]    # ← slice to limit
    return enc.decode(truncated)       # ← decode back to string

# Test
long_text = "word " * 10000           # 10000 repetitions
short = truncate_to_limit(long_text, max_tokens=100)
print(len(tiktoken.encoding_for_model("gpt-4o").encode(short)))  # ≤ 100
```

**Why:** Slicing token IDs is safe — you never cut mid-character. Decoding back from tokens always produces valid UTF-8.
</details>

---

<a id="q11"></a>

### Q11 · tiktoken — Count Tokens in a Chat Messages List 🟠

> 🛠️ **Solve locally:** [practice_local.py → Q11](./practice_local.py)


OpenAI chat messages have 4 tokens of overhead per message plus 3 tokens for reply priming. Write a function that counts total tokens for a messages list.


<details>
<summary>💡 Hint</summary>
Loop over messages, add 4 per message, add len(enc.encode(value)) for each field value, add 3 at the end.
</details>

<details>
<summary>✅ Answer</summary>

```python
import tiktoken

def count_message_tokens(messages: list[dict], model: str = "gpt-4o") -> int:
    enc = tiktoken.encoding_for_model(model)
    total = 3                          # ← reply priming overhead
    for message in messages:
        total += 4                     # ← per-message overhead (role + separators)
        for value in message.values():
            if isinstance(value, str):
                total += len(enc.encode(value))  # ← actual content tokens
    return total

messages = [
    {"role": "system", "content": "You are a helpful assistant."},
    {"role": "user",   "content": "What is the capital of France?"}
]
print(count_message_tokens(messages))  # ~26
```

**Why:** The raw content token count underestimates real usage — each message has structural overhead that adds up over long conversations.
</details>

---

<a id="q12"></a>

### Q12 · tqdm — Wrap a List with a Progress Bar 🟢

> 🛠️ **Solve locally:** [practice_local.py → Q12](./practice_local.py)


You have a list of 1000 documents to embed. Wrap the loop with tqdm showing the description "Embedding documents".


<details>
<summary>💡 Hint</summary>
Wrap the iterable: for doc in tqdm(documents, desc="..."):
</details>

<details>
<summary>✅ Answer</summary>

```python
from tqdm import tqdm
import time

documents = [f"doc_{i}" for i in range(1000)]  # ← 1000 docs

for doc in tqdm(documents, desc="Embedding documents"):
    time.sleep(0.001)   # ← simulate work
    # embed(doc)

# Output: Embedding documents: 100%|████████| 1000/1000 [00:01<00:00, 900it/s]
```

**Why:** tqdm wraps any iterable with zero code change — just pass it in. You instantly get time estimates, speed, and completion status.
</details>

---

<a id="q13"></a>

### Q13 · tqdm — Manual pbar with update() 🟡

> 🛠️ **Solve locally:** [practice_local.py → Q13](./practice_local.py)


You process documents in variable-sized batches (not a fixed list). Use a manual `tqdm` progress bar with `total=` and `update()`.


<details>
<summary>💡 Hint</summary>
tqdm(total=N), then pbar.update(batch_size) inside the loop.
</details>

<details>
<summary>✅ Answer</summary>

```python
from tqdm import tqdm

total_items = 500
batches = [list(range(i, min(i + 50, total_items))) for i in range(0, total_items, 50)]

progress = tqdm(total=total_items, desc="Processing", unit="doc")  # ← manual bar

for batch in batches:
    # process_batch(batch)       # your work here
    progress.update(len(batch))  # ← advance by batch size

progress.close()                 # ← always close manually-created bars
```

**Why:** When your batches have uneven sizes, you can't wrap a simple iterable — the manual API gives you exact control.
</details>

---

<a id="q14"></a>

### Q14 · tqdm — Async Gather with tqdm_asyncio 🟡

> 🛠️ **Solve locally:** [practice_local.py → Q14](./practice_local.py)


You have 100 async coroutines. Use `tqdm_asyncio.gather` to run them all with a progress bar showing "Calling LLM".


<details>
<summary>💡 Hint</summary>
from tqdm.asyncio import tqdm_asyncio, then await tqdm_asyncio.gather(*tasks, desc=...).
</details>

<details>
<summary>✅ Answer</summary>

```python
import asyncio
from tqdm.asyncio import tqdm_asyncio

async def fake_llm_call(i: int) -> str:
    await asyncio.sleep(0.05)   # ← simulate API latency
    return f"response_{i}"

async def main():
    tasks = [fake_llm_call(i) for i in range(100)]
    results = await tqdm_asyncio.gather(
        *tasks,
        desc="Calling LLM"   # ← shows progress as tasks complete
    )
    print(len(results))       # 100

asyncio.run(main())
```

**Why:** `tqdm_asyncio.gather` is a drop-in for `asyncio.gather` that shows real-time progress — each completed coroutine advances the bar.
</details>

---

<a id="q15"></a>

### Q15 · loguru — Basic logger.info / warning / error 🟢

> 🛠️ **Solve locally:** [practice_local.py → Q15](./practice_local.py)


Replace three `print()` statements with loguru: one for a startup message, one for a token warning, one for an API failure.


<details>
<summary>💡 Hint</summary>
from loguru import logger, then logger.info/warning/error.
</details>

<details>
<summary>✅ Answer</summary>

```python
from loguru import logger

# Before: print("Starting LLM client")
logger.info("Starting LLM client")              # ← INFO level, green

# Before: print(f"Token count high: {count}/4096")
count = 3900
logger.warning(f"Token count high: {count}/4096")  # ← WARNING, yellow

# Before: print("API call failed: 429 Rate Limited")
logger.error("API call failed: 429 Rate Limited")  # ← ERROR, red

# Output includes timestamp + level + file:function:line automatically:
# 2024-01-15 10:23:45 | INFO     | __main__:...:5 - Starting LLM client
```

**Why:** loguru adds timestamps, log levels, and source location to every message — zero configuration needed.
</details>

---

<a id="q16"></a>

### Q16 · loguru — Add a File Sink with Rotation 🟡

> 🛠️ **Solve locally:** [practice_local.py → Q16](./practice_local.py)


Configure loguru to write DEBUG+ logs to `logs/app.log` with 10 MB rotation and 7-day retention. Also add a separate sink for ERROR+ only.


<details>
<summary>💡 Hint</summary>
logger.add() takes a path, rotation=, retention=, and level= parameters.
</details>

<details>
<summary>✅ Answer</summary>

```python
from loguru import logger

logger.add(
    "logs/app.log",
    rotation="10 MB",     # ← new file every 10 MB
    retention="7 days",   # ← delete files older than 7 days
    level="DEBUG"         # ← write DEBUG and above
)

logger.add(
    "logs/errors.log",
    level="ERROR"         # ← only ERROR and CRITICAL here
)

logger.info("This goes to app.log only")
logger.error("This goes to BOTH app.log and errors.log")
```

**Why:** Separating error logs makes on-call debugging faster — you check `errors.log` first without trawling through thousands of INFO lines.
</details>

---

<a id="q17"></a>

### Q17 · loguru — bind() Structured Context 🟠

> 🛠️ **Solve locally:** [practice_local.py → Q17](./practice_local.py)


You are processing a batch of requests. Use `logger.bind()` to attach a `request_id` to every log message inside a function, without passing the ID to every call manually.


<details>
<summary>💡 Hint</summary>
logger.bind(key=value) returns a new logger with that field attached.
</details>

<details>
<summary>✅ Answer</summary>

```python
from loguru import logger
import uuid

def process_request(prompt: str) -> str:
    request_id = str(uuid.uuid4())[:8]
    log = logger.bind(request_id=request_id)   # ← bind context once

    log.info("Processing started")             # ← request_id appears in every line
    log.debug(f"Prompt length: {len(prompt)} chars")

    # simulate work
    result = f"response to: {prompt[:20]}"
    log.info(f"Processing complete | result_length={len(result)}")
    return result

process_request("Explain quantum computing")
# 2024-01-15 10:23:45 | INFO | request_id=a3f91c2b - Processing started
# 2024-01-15 10:23:45 | INFO | request_id=a3f91c2b - Processing complete | result_length=32
```

**Why:** `bind()` creates a child logger with extra context baked in — you log once, the ID appears everywhere without passing it as an argument.
</details>

---

<a id="q18"></a>

### Q18 · rich — Print Colored Markup to Terminal 🟢

> 🛠️ **Solve locally:** [practice_local.py → Q18](./practice_local.py)


Use rich to print: a bold green "Success!" message, a red "Error:" prefix, and a yellow "Warning:" prefix.


<details>
<summary>💡 Hint</summary>
from rich.console import Console, then console.print("[bold green]text[/bold green]").
</details>

<details>
<summary>✅ Answer</summary>

```python
from rich.console import Console

console = Console()

console.print("[bold green]Success![/bold green] Embedding complete.")
console.print("[red]Error:[/red] API key not found in environment.")
console.print("[yellow]Warning:[/yellow] Token count near limit: 3900/4096")

# You can also use rich's print as a drop-in for the built-in:
from rich import print as rprint
rprint("[bold cyan]Using rich print[/bold cyan]")
```

**Why:** Rich markup uses HTML-style tags that render as colors in any modern terminal — no ANSI escape codes to manage manually.
</details>

---

<a id="q19"></a>

### Q19 · rich — Build and Print a Table 🟡

> 🛠️ **Solve locally:** [practice_local.py → Q19](./practice_local.py)


Build a rich `Table` showing LLM benchmark results: columns for Model, Latency (ms), and Cost per 1k tokens. Add three rows of data.


<details>
<summary>💡 Hint</summary>
from rich.table import Table, then table.add_column() and table.add_row().
</details>

<details>
<summary>✅ Answer</summary>

```python
from rich.table import Table
from rich.console import Console

console = Console()
table = Table(title="LLM Benchmark Results")

table.add_column("Model",               style="cyan")
table.add_column("Latency (ms)",        justify="right")
table.add_column("Cost per 1k tokens",  justify="right")

table.add_row("gpt-4o",         "450",  "$0.005")
table.add_row("claude-3-haiku", "280",  "$0.00025")
table.add_row("gpt-3.5-turbo",  "200",  "$0.0005")

console.print(table)   # ← renders as a formatted box table in terminal
```

**Why:** Rich tables auto-size columns, align numbers, and add borders — far more readable than tab-separated print statements.
</details>

---

<a id="q20"></a>

### Q20 · pydantic-settings — BaseSettings with Env Vars 🟢

> 🛠️ **Solve locally:** [practice_local.py → Q20](./practice_local.py)


Define a `Settings` class that reads `OPENAI_API_KEY` (required string), `MAX_TOKENS` (int, default 4096), and `DEBUG` (bool, default False) from environment variables or a `.env` file.


<details>
<summary>💡 Hint</summary>
Extend BaseSettings and set class Config: env_file = ".env".
</details>

<details>
<summary>✅ Answer</summary>

```python
from pydantic_settings import BaseSettings

class Settings(BaseSettings):
    openai_api_key: str            # ← required — ValidationError if missing
    max_tokens: int = 4096         # ← auto-cast: "4096" (str) → 4096 (int)
    debug: bool = False            # ← auto-cast: "false" (str) → False (bool)

    class Config:
        env_file = ".env"          # ← reads .env automatically
        env_file_encoding = "utf-8"

settings = Settings()
print(settings.max_tokens)         # 4096  (int, not string)
print(settings.debug)              # False (bool, not string)
```

**Why:** pydantic-settings casts types automatically — you never manually do `int(os.getenv(...))` or `.lower() == "true"` again.
</details>

---

<a id="q21"></a>

### Q21 · pydantic-settings — lru_cache Singleton Pattern 🟡

> 🛠️ **Solve locally:** [practice_local.py → Q21](./practice_local.py)


Wrap `Settings()` in an `lru_cache` so the `.env` file is only read once per process, no matter how many modules call `get_settings()`.


<details>
<summary>💡 Hint</summary>
from functools import lru_cache, decorate a factory function get_settings() with @lru_cache(maxsize=1).
</details>

<details>
<summary>✅ Answer</summary>

```python
from pydantic_settings import BaseSettings
from functools import lru_cache

class Settings(BaseSettings):
    openai_api_key: str = "sk-demo"
    model_name: str = "gpt-4o"

    class Config:
        env_file = ".env"

@lru_cache(maxsize=1)            # ← cache the single Settings instance
def get_settings() -> Settings:
    return Settings()            # ← reads .env exactly once

# In any module:
settings = get_settings()        # ← returns cached object after first call
settings2 = get_settings()
print(settings is settings2)     # True — same object
```

**Why:** Without caching, every `Settings()` call re-reads the file from disk. `lru_cache(maxsize=1)` makes it a singleton for free.
</details>

---

<a id="q22"></a>

### Q22 · pydantic-settings — Field with Validated Range 🟡

> 🛠️ **Solve locally:** [practice_local.py → Q22](./practice_local.py)


Add a `temperature` field to Settings that must be a float between 0.0 and 2.0 (inclusive). Use `pydantic.Field` with constraints.


<details>
<summary>💡 Hint</summary>
Field(default=0.7, ge=0.0, le=2.0) — ge means "greater or equal", le means "less or equal".
</details>

<details>
<summary>✅ Answer</summary>

```python
from pydantic_settings import BaseSettings
from pydantic import Field

class Settings(BaseSettings):
    openai_api_key: str = "sk-demo"
    temperature: float = Field(
        default=0.7,
        ge=0.0,    # ← greater than or equal to 0.0
        le=2.0     # ← less than or equal to 2.0
    )

    class Config:
        env_file = ".env"

settings = Settings()
print(settings.temperature)     # 0.7

# Set TEMPERATURE=3.0 in .env → ValidationError at startup
# "temperature: Input should be less than or equal to 2"
```

**Why:** Field constraints validate ranges at startup — a temperature of 5.0 raises an error immediately rather than causing a mysterious API failure later.
</details>

---

<a id="q23"></a>

### Q23 · pathlib — Build Paths and mkdir with parents 🟢

> 🛠️ **Solve locally:** [practice_local.py → Q23](./practice_local.py)


Given `__file__` as your starting point, build a path to `../../data/outputs/results.jsonl`. Create the `outputs` directory (and any parents) if it does not exist.


<details>
<summary>💡 Hint</summary>
Path(__file__).parent.parent / "data" / "outputs", then .mkdir(parents=True, exist_ok=True).
</details>

<details>
<summary>✅ Answer</summary>

```python
from pathlib import Path

BASE_DIR = Path(__file__).parent.parent    # ← two levels up from this file
outputs_dir = BASE_DIR / "data" / "outputs"
result_file = outputs_dir / "results.jsonl"

outputs_dir.mkdir(parents=True, exist_ok=True)
# ← parents=True: creates all missing parent dirs
# ← exist_ok=True: no error if the dir already exists

print(result_file)          # /absolute/path/to/data/outputs/results.jsonl
print(result_file.parent)   # /absolute/path/to/data/outputs
print(result_file.suffix)   # .jsonl
```

**Why:** `Path(__file__).parent` is always relative to the source file — not wherever you run the script from. This prevents path bugs.
</details>

---

<a id="q24"></a>

### Q24 · pathlib — Glob for .jsonl Files in a Directory 🟡

> 🛠️ **Solve locally:** [practice_local.py → Q24](./practice_local.py)


Find all `.jsonl` files in a `data/` directory (and all subdirectories). Print their names and sizes in MB.


<details>
<summary>💡 Hint</summary>
Path("data").rglob("*.jsonl") for recursive search, path.stat().st_size for bytes.
</details>

<details>
<summary>✅ Answer</summary>

```python
from pathlib import Path

data_dir = Path("data")

# rglob = recursive glob (searches all subdirectories)
jsonl_files = list(data_dir.rglob("*.jsonl"))

for f in jsonl_files:
    size_mb = f.stat().st_size / 1_000_000   # ← bytes → MB
    print(f"{f.name:40s}  {size_mb:.2f} MB")

# Just the current directory (no subdirs):
top_level_only = list(data_dir.glob("*.jsonl"))
```

**Why:** `rglob` is the pathlib equivalent of `find . -name "*.jsonl"` — one call, no shell subprocess needed.
</details>

---

<a id="q25"></a>

### Q25 · json/jsonlines — Read a .jsonl File Line by Line 🟢

> 🛠️ **Solve locally:** [practice_local.py → Q25](./practice_local.py)


Write a generator function `read_jsonl(filepath)` that reads a JSONL file one record at a time without loading the whole file into memory.


<details>
<summary>💡 Hint</summary>
yield json.loads(line) for each non-empty line.
</details>

<details>
<summary>✅ Answer</summary>

```python
import json
from pathlib import Path

def read_jsonl(filepath):
    """Generator: yields one dict per line. Memory efficient."""
    with open(filepath, encoding="utf-8") as f:
        for line in f:
            line = line.strip()
            if line:                      # ← skip blank lines
                yield json.loads(line)   # ← parse JSON → dict

# Usage — processes 50k records without loading all into RAM
for record in read_jsonl("training_data.jsonl"):
    print(record["messages"])
```

**Why:** `yield` makes this a generator — only one record lives in memory at a time, regardless of file size.
</details>

---

<a id="q26"></a>

### Q26 · json/jsonlines — Write and Append to .jsonl 🟡

> 🛠️ **Solve locally:** [practice_local.py → Q26](./practice_local.py)


Write a `write_jsonl(filepath, records)` function and an `append_jsonl(filepath, record)` function. Each record should be one line of valid JSON.


<details>
<summary>💡 Hint</summary>
json.dumps(record) + "\n" for each line. Use mode="w" to overwrite, mode="a" to append.
</details>

<details>
<summary>✅ Answer</summary>

```python
import json

def write_jsonl(filepath: str, records: list[dict]) -> None:
    """Write a list of dicts to a JSONL file (overwrites)."""
    with open(filepath, "w", encoding="utf-8") as f:
        for record in records:
            f.write(json.dumps(record) + "\n")  # ← one JSON object per line

def append_jsonl(filepath: str, record: dict) -> None:
    """Append a single record to an existing JSONL file."""
    with open(filepath, "a", encoding="utf-8") as f:
        f.write(json.dumps(record) + "\n")      # ← "a" mode = append

# Usage
records = [{"id": i, "text": f"example {i}"} for i in range(3)]
write_jsonl("output.jsonl", records)
append_jsonl("output.jsonl", {"id": 99, "text": "added later"})
```

**Why:** JSONL has no commas between lines and no outer `[]` — just raw JSON objects, one per line. Each line is independently parseable.
</details>

---

<a id="q27"></a>

### Q27 · Project Structure — Describe the Standard AI App Layout 🟢

> 🛠️ **Solve locally:** [practice_local.py → Q27](./practice_local.py)


Describe the standard folder layout for a production AI application. Name each directory and its purpose.


<details>
<summary>💡 Hint</summary>
Think: secrets, config, prompts, data (raw/processed/outputs), src, tests, scripts.
</details>

<details>
<summary>✅ Answer</summary>

```
my-ai-app/
├── .env                    # API keys — NEVER commit (add to .gitignore)
├── .env.example            # Template with fake values — DO commit
├── .gitignore
├── pyproject.toml          # dependencies + project metadata
│
├── config/
│   └── settings.py         # pydantic-settings BaseSettings (single source of truth)
│
├── prompts/
│   ├── system.txt          # system prompt (loaded at runtime, not hardcoded)
│   └── summarize.txt
│
├── data/
│   ├── raw/                # original data — never modified
│   ├── processed/          # cleaned and ready to use
│   └── outputs/            # LLM responses, embeddings, results
│
├── src/
│   ├── client.py           # LLM client (httpx + tenacity + tiktoken)
│   ├── pipeline.py         # main data processing logic
│   └── utils.py            # shared helpers
│
├── tests/
│   └── test_client.py
│
└── scripts/
    └── embed_documents.py  # one-off batch scripts (use tqdm here)
```

**Why:** This layout ensures secrets never enter code, prompts are versionable separately from code, and raw data is always reproducible.
</details>

---

<a id="q28"></a>

### Q28 · Project Structure — Where Do Prompts and Config Live? 🟢

> 🛠️ **Solve locally:** [practice_local.py → Q28](./practice_local.py)


Where should system prompts and app configuration live in a production AI project? Why should they NOT be hardcoded strings in Python files?


<details>
<summary>💡 Hint</summary>
Prompts change often. Config needs type validation. Both should be loadable at runtime.
</details>

<details>
<summary>✅ Answer</summary>

```python
# prompts/system.txt  ← text file, loaded at runtime
# "You are a helpful assistant specialized in..."

# config/settings.py  ← pydantic-settings, validated at startup
from pydantic_settings import BaseSettings
from pathlib import Path

class Settings(BaseSettings):
    model_name: str = "gpt-4o"
    max_tokens: int = 4096

    class Config:
        env_file = ".env"

# Load prompt at runtime — NOT hardcoded:
PROMPTS_DIR = Path(__file__).parent.parent / "prompts"
system_prompt = (PROMPTS_DIR / "system.txt").read_text(encoding="utf-8")
```

**Why prompts in files:** Prompts change every sprint. Keeping them in `.txt` files means prompt engineers can edit them without touching Python code.

**Why config in settings.py:** Centralizes validation, type casting, and defaults — no scattered `os.getenv()` calls across 20 files.
</details>

---

<a id="q29"></a>

### Q29 · requirements.txt — Pin AI Library Versions 🟢

> 🛠️ **Solve locally:** [practice_local.py → Q29](./practice_local.py)


Write a `requirements.txt` with pinned versions for the core AI utility belt: httpx, tenacity, tiktoken, tqdm, loguru, python-dotenv, pydantic-settings, rich, openai, anthropic.


<details>
<summary>💡 Hint</summary>
Use == for pinned versions. Each library on its own line.
</details>

<details>
<summary>✅ Answer</summary>

```
# requirements.txt — pin exact versions for reproducibility
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

```bash
pip install -r requirements.txt
```

**Why pin with ==:** AI libraries release breaking changes frequently (especially openai and anthropic). Pinned versions ensure every teammate and every deploy uses identical code.
</details>

---

<a id="q30"></a>

### Q30 · pyproject.toml — Optional Dev Extras 🟡

> 🛠️ **Solve locally:** [practice_local.py → Q30](./practice_local.py)


Write a `pyproject.toml` for an AI app. Core dependencies use `>=` (minimum version). Add a `[dev]` optional group with pytest and pytest-asyncio.


<details>
<summary>💡 Hint</summary>
Use [project.optional-dependencies] with a dev key. Install with pip install -e ".[dev]".
</details>

<details>
<summary>✅ Answer</summary>

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
    "pytest-asyncio>=0.23",   # ← needed to test async functions
]
```

```bash
pip install -e .           # core deps only
pip install -e ".[dev]"    # core + dev (for testing)
```

**Why `>=` not `==`:** Libraries published to pypi with a minimum version allow pip to resolve conflicts between packages. Lock files (`pip freeze`) pin exact versions for deployments.
</details>

---

## Navigation

| | |
|---|---|
| 📖 Theory | [theory.md](./theory.md) |
| 📋 Cheatsheet | [cheetsheet.md](./cheetsheet.md) |
| 🎯 Interview | [interview.md](./interview.md) |

---

**[🏠 Back to README](../README.md)**

**Prev:** [← Theory](./theory.md) &nbsp;|&nbsp; **Next:** [Cheat Sheet →](./cheetsheet.md)

**Related Topics:** [Theory](./theory.md) · [Cheat Sheet](./cheetsheet.md) · [Interview Q&A](./interview.md)
