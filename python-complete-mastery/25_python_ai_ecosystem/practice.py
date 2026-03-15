"""
Python AI Ecosystem — Practice
A production-ready LLM client that wires together every tool in the AI utility belt:
  - python-dotenv  : load API keys from .env
  - httpx          : async HTTP client with timeout
  - tenacity       : automatic retry with exponential backoff
  - tiktoken       : token counting before sending
  - tqdm           : progress bars for batch processing
  - loguru         : structured logging
  - pathlib        : file path handling
  - json/jsonlines : JSONL read/write

Run:
  pip install httpx tenacity tiktoken tqdm loguru python-dotenv pydantic-settings rich
  python practice.py
"""

# ─────────────────────────────────────────────
# 1. ENVIRONMENT — python-dotenv
# ─────────────────────────────────────────────

import os
from dotenv import load_dotenv

# Load .env file before anything else
# .env contains: OPENAI_API_KEY=sk-...
load_dotenv()


# ─────────────────────────────────────────────
# 2. CONFIG — pydantic-settings
# ─────────────────────────────────────────────

from pydantic_settings import BaseSettings
from pydantic import Field
from functools import lru_cache


class Settings(BaseSettings):
    """All config lives here. Validated at startup. No os.getenv scattered around."""

    openai_api_key: str = "sk-fake-key-for-demo"   # required in real usage
    model_name: str = "gpt-4o"
    max_tokens: int = Field(default=4096, gt=0, le=128_000)
    temperature: float = Field(default=0.7, ge=0.0, le=2.0)
    api_base_url: str = "https://api.openai.com/v1"
    request_timeout: float = 60.0
    max_retries: int = 5

    class Config:
        env_file = ".env"
        env_file_encoding = "utf-8"


@lru_cache(maxsize=1)
def get_settings() -> Settings:
    """Singleton — settings loaded and validated once."""
    return Settings()


# ─────────────────────────────────────────────
# 3. LOGGING — loguru
# ─────────────────────────────────────────────

from loguru import logger
from pathlib import Path

# Create logs directory
LOG_DIR = Path(__file__).parent / "logs"
LOG_DIR.mkdir(parents=True, exist_ok=True)

# Remove default stderr handler, replace with structured file + stderr
logger.remove()
logger.add(
    LOG_DIR / "app.log",
    rotation="10 MB",
    retention="7 days",
    level="DEBUG",
    format="{time:YYYY-MM-DD HH:mm:ss} | {level:<8} | {name}:{function}:{line} - {message}",
)
logger.add(
    lambda msg: print(msg, end=""),
    level="INFO",
    colorize=True,
    format="<green>{time:HH:mm:ss}</green> | <level>{level:<8}</level> | {message}",
)


# ─────────────────────────────────────────────
# 4. TOKEN COUNTING — tiktoken
# ─────────────────────────────────────────────

import tiktoken


def get_encoder(model: str = "gpt-4o") -> tiktoken.Encoding:
    """Get tiktoken encoder, with fallback for unknown models."""
    try:
        return tiktoken.encoding_for_model(model)
    except KeyError:
        logger.warning(f"Unknown model '{model}' for tiktoken, using cl100k_base")
        return tiktoken.get_encoding("cl100k_base")


def count_tokens(text: str, model: str = "gpt-4o") -> int:
    """Count tokens in a plain string."""
    enc = get_encoder(model)
    return len(enc.encode(text))


def count_message_tokens(messages: list[dict], model: str = "gpt-4o") -> int:
    """
    Count tokens in a chat messages list.
    Includes per-message overhead (4 tokens) and reply priming (3 tokens).
    """
    enc = get_encoder(model)
    total = 3  # reply priming
    for message in messages:
        total += 4  # role + separators overhead
        for value in message.values():
            if isinstance(value, str):
                total += len(enc.encode(value))
    return total


def truncate_to_limit(text: str, max_tokens: int = 4000, model: str = "gpt-4o") -> str:
    """Truncate text so it fits within the token limit."""
    enc = get_encoder(model)
    tokens = enc.encode(text)
    if len(tokens) <= max_tokens:
        return text
    logger.warning(f"Truncating text from {len(tokens)} to {max_tokens} tokens")
    return enc.decode(tokens[:max_tokens])


# ─────────────────────────────────────────────
# 5. HTTP CLIENT — httpx + tenacity
# ─────────────────────────────────────────────

import httpx
import asyncio
from tenacity import (
    retry,
    stop_after_attempt,
    wait_random_exponential,
    retry_if_exception_type,
    before_sleep_log,
)
import logging as stdlib_logging


def _should_retry_status(exc: Exception) -> bool:
    """Retry on rate limits and server errors. Not on auth or bad request."""
    if isinstance(exc, httpx.HTTPStatusError):
        return exc.response.status_code in (429, 500, 502, 503, 504)
    return False


def make_retry_decorator(max_attempts: int = 5):
    """Build a tenacity retry decorator for LLM API calls."""
    return retry(
        stop=stop_after_attempt(max_attempts),
        wait=wait_random_exponential(min=1, max=60),
        retry=retry_if_exception_type(
            (httpx.TimeoutException, httpx.NetworkError, httpx.HTTPStatusError)
        ),
        before_sleep=before_sleep_log(
            stdlib_logging.getLogger("tenacity"), stdlib_logging.WARNING
        ),
        reraise=True,
    )


# ─────────────────────────────────────────────
# 6. JSONL UTILITIES — pathlib + json
# ─────────────────────────────────────────────

import json


def read_jsonl(filepath: str | Path):
    """
    Generator: read JSONL file one record at a time.
    Memory efficient — never loads entire file.
    """
    path = Path(filepath)
    if not path.exists():
        logger.warning(f"JSONL file not found: {path}")
        return
    with open(path, encoding="utf-8") as f:
        for line_num, line in enumerate(f, start=1):
            line = line.strip()
            if not line:
                continue
            try:
                yield json.loads(line)
            except json.JSONDecodeError as e:
                logger.error(f"Invalid JSON on line {line_num}: {e}")


def write_jsonl(filepath: str | Path, records: list[dict]) -> int:
    """Write a list of records to a JSONL file. Returns number written."""
    path = Path(filepath)
    path.parent.mkdir(parents=True, exist_ok=True)
    count = 0
    with open(path, "w", encoding="utf-8") as f:
        for record in records:
            f.write(json.dumps(record, default=str) + "\n")
            count += 1
    logger.info(f"Wrote {count} records to {path}")
    return count


def append_jsonl(filepath: str | Path, record: dict) -> None:
    """Append a single record to a JSONL file."""
    path = Path(filepath)
    path.parent.mkdir(parents=True, exist_ok=True)
    with open(path, "a", encoding="utf-8") as f:
        f.write(json.dumps(record, default=str) + "\n")


def count_jsonl_lines(filepath: str | Path) -> int:
    """Count non-empty lines in a JSONL file without loading it."""
    with open(filepath) as f:
        return sum(1 for line in f if line.strip())


# ─────────────────────────────────────────────
# 7. PRODUCTION LLM CLIENT CLASS
#    Combines: httpx + tenacity + tiktoken + loguru
# ─────────────────────────────────────────────

class LLMClient:
    """
    Production-ready LLM client.

    Features:
    - Async HTTP calls via httpx
    - Automatic retry with exponential backoff via tenacity
    - Token counting before every call via tiktoken
    - Structured logging via loguru
    - Config loaded from .env via pydantic-settings
    """

    def __init__(self, settings: Settings | None = None):
        self.settings = settings or get_settings()
        self._client: httpx.AsyncClient | None = None
        self._retry = make_retry_decorator(self.settings.max_retries)
        self._encoder = get_encoder(self.settings.model_name)
        logger.info(
            f"LLMClient initialized | model={self.settings.model_name} "
            f"max_tokens={self.settings.max_tokens}"
        )

    async def __aenter__(self):
        timeout = httpx.Timeout(connect=5.0, read=self.settings.request_timeout, write=10.0)
        self._client = httpx.AsyncClient(
            timeout=timeout,
            headers={"Authorization": f"Bearer {self.settings.openai_api_key}"},
        )
        return self

    async def __aexit__(self, *args):
        if self._client:
            await self._client.aclose()

    def _build_messages(self, prompt: str, system: str = "") -> list[dict]:
        messages = []
        if system:
            messages.append({"role": "system", "content": system})
        messages.append({"role": "user", "content": prompt})
        return messages

    async def _raw_complete(self, messages: list[dict]) -> dict:
        """
        Inner call — separated so tenacity can wrap it cleanly.
        If this raises, tenacity retries.
        """
        url = f"{self.settings.api_base_url}/chat/completions"
        payload = {
            "model": self.settings.model_name,
            "messages": messages,
            "max_tokens": self.settings.max_tokens,
            "temperature": self.settings.temperature,
        }
        response = await self._client.post(url, json=payload)
        response.raise_for_status()
        return response.json()

    async def complete(self, prompt: str, system: str = "") -> str:
        """
        Send a prompt to the LLM. Returns the response text.

        Steps:
        1. Build messages
        2. Count tokens, warn if near limit
        3. Call API with automatic retry
        4. Return response text
        """
        messages = self._build_messages(prompt, system)

        # Token counting before sending
        token_count = count_message_tokens(messages, self.settings.model_name)
        limit = self.settings.max_tokens
        if token_count > limit * 0.9:
            logger.warning(
                f"Token count high: {token_count}/{limit} "
                f"({token_count/limit*100:.0f}%)"
            )
        else:
            logger.debug(f"Token count: {token_count}/{limit}")

        if token_count >= limit:
            raise ValueError(
                f"Prompt exceeds token limit: {token_count} > {limit}. "
                "Truncate your input before calling complete()."
            )

        # Call with retry
        retry_call = self._retry(self._raw_complete)
        data = await retry_call(messages)

        content = data["choices"][0]["message"]["content"]
        usage = data.get("usage", {})
        logger.info(
            f"LLM call complete | "
            f"prompt_tokens={usage.get('prompt_tokens', '?')} "
            f"completion_tokens={usage.get('completion_tokens', '?')}"
        )
        return content


# ─────────────────────────────────────────────
# 8. BATCH PROCESSING — tqdm + JSONL + LLMClient
# ─────────────────────────────────────────────

from tqdm.asyncio import tqdm_asyncio
from tqdm import tqdm


async def batch_process_jsonl(
    input_path: str | Path,
    output_path: str | Path,
    system_prompt: str = "You are a helpful assistant.",
    batch_size: int = 10,
    prompt_field: str = "prompt",
) -> dict:
    """
    Process a JSONL file of prompts through the LLM.

    Each input record must have a `prompt_field` key.
    Writes results to output_path as JSONL.

    Returns summary stats.
    """
    input_path = Path(input_path)
    output_path = Path(output_path)

    if not input_path.exists():
        logger.error(f"Input file not found: {input_path}")
        return {"error": "input file not found"}

    total = count_jsonl_lines(input_path)
    logger.info(f"Starting batch process | input={input_path} total={total}")

    # Clear output file
    output_path.parent.mkdir(parents=True, exist_ok=True)
    if output_path.exists():
        output_path.unlink()

    success_count = 0
    error_count = 0

    async with LLMClient() as client:
        batch: list[dict] = []
        records = list(read_jsonl(input_path))  # collect for progress bar

        with tqdm(total=total, desc="Processing prompts") as pbar:
            for record in records:
                prompt = record.get(prompt_field, "")
                if not prompt:
                    logger.warning(f"Missing '{prompt_field}' field, skipping record")
                    pbar.update(1)
                    continue

                try:
                    response = await client.complete(prompt, system=system_prompt)
                    result = {**record, "response": response, "status": "ok"}
                    append_jsonl(output_path, result)
                    success_count += 1
                except Exception as e:
                    logger.error(f"Failed to process record: {e}")
                    result = {**record, "response": None, "status": "error", "error": str(e)}
                    append_jsonl(output_path, result)
                    error_count += 1
                finally:
                    pbar.update(1)

    summary = {
        "total": total,
        "success": success_count,
        "errors": error_count,
        "output": str(output_path),
    }
    logger.info(f"Batch complete | {summary}")
    return summary


# ─────────────────────────────────────────────
# 9. ASYNC BATCH WITH CONCURRENCY
#    Process multiple prompts concurrently with semaphore
# ─────────────────────────────────────────────

async def concurrent_batch(prompts: list[str], max_concurrent: int = 5) -> list[str]:
    """
    Process a list of prompts concurrently.
    Semaphore limits concurrent API calls to avoid rate limits.
    tqdm_asyncio.gather shows progress.
    """
    semaphore = asyncio.Semaphore(max_concurrent)

    async with LLMClient() as client:

        async def bounded_complete(prompt: str) -> str:
            async with semaphore:
                try:
                    return await client.complete(prompt)
                except Exception as e:
                    logger.error(f"Failed: {e}")
                    return f"ERROR: {e}"

        tasks = [bounded_complete(p) for p in prompts]
        results = await tqdm_asyncio.gather(*tasks, desc="Concurrent LLM calls")

    return results


# ─────────────────────────────────────────────
# 10. RICH — DISPLAY RESULTS IN TERMINAL
# ─────────────────────────────────────────────

from rich.console import Console
from rich.table import Table
from rich.panel import Panel

console = Console()


def display_results_table(results: list[dict]) -> None:
    """Display batch results as a rich table."""
    table = Table(title="Batch Processing Results", show_lines=True)
    table.add_column("Prompt", style="cyan", max_width=40)
    table.add_column("Status", justify="center")
    table.add_column("Response", style="white", max_width=60)

    for r in results:
        prompt = str(r.get("prompt", ""))[:40]
        status = r.get("status", "unknown")
        response = str(r.get("response", ""))[:60]

        status_style = "[green]ok[/green]" if status == "ok" else "[red]error[/red]"
        table.add_row(prompt, status_style, response)

    console.print(table)


def display_summary(summary: dict) -> None:
    """Display run summary in a rich panel."""
    lines = [
        f"Total processed: {summary.get('total', 0)}",
        f"Success:         {summary.get('success', 0)}",
        f"Errors:          {summary.get('errors', 0)}",
        f"Output file:     {summary.get('output', '')}",
    ]
    console.print(Panel("\n".join(lines), title="Run Summary", border_style="green"))


# ─────────────────────────────────────────────
# 11. DEMO — wire everything together
# ─────────────────────────────────────────────

async def demo_token_counting():
    """Show how tiktoken works before sending."""
    console.print(Panel("Token Counting Demo", border_style="blue"))

    texts = [
        "Hello, world!",
        "Explain quantum entanglement in simple terms.",
        "Write a Python function that reads a JSONL file line by line using generators.",
    ]

    enc = get_encoder("gpt-4o")
    table = Table(title="Token Counts")
    table.add_column("Text", style="cyan", max_width=60)
    table.add_column("Tokens", justify="right", style="yellow")

    for text in texts:
        tokens = len(enc.encode(text))
        table.add_row(text[:60], str(tokens))

    console.print(table)


def demo_jsonl_operations():
    """Show JSONL read/write with pathlib."""
    console.print(Panel("JSONL Operations Demo", border_style="blue"))

    # Write some records
    data_dir = Path(__file__).parent / "demo_data"
    data_dir.mkdir(exist_ok=True)
    sample_file = data_dir / "sample.jsonl"

    records = [
        {"id": i, "prompt": f"Explain concept number {i}", "category": "education"}
        for i in range(1, 6)
    ]

    written = write_jsonl(sample_file, records)
    console.print(f"[green]Wrote {written} records to {sample_file}[/green]")

    # Read back
    loaded = list(read_jsonl(sample_file))
    console.print(f"[cyan]Read back {len(loaded)} records[/cyan]")

    # Show first record
    console.print(Panel(json.dumps(loaded[0], indent=2), title="First record", border_style="dim"))


def demo_settings():
    """Show pydantic-settings config."""
    console.print(Panel("Settings Demo", border_style="blue"))

    settings = get_settings()
    table = Table(title="Current Configuration")
    table.add_column("Setting", style="cyan")
    table.add_column("Value", style="yellow")

    table.add_row("model_name", settings.model_name)
    table.add_row("max_tokens", str(settings.max_tokens))
    table.add_row("temperature", str(settings.temperature))
    table.add_row("request_timeout", f"{settings.request_timeout}s")
    table.add_row("api_key", "sk-***" + settings.openai_api_key[-4:] if len(settings.openai_api_key) > 7 else "set")

    console.print(table)


async def demo_batch_with_progress():
    """Show tqdm progress bar with a simulated batch."""
    console.print(Panel("Batch Progress Demo (simulated)", border_style="blue"))

    import random

    items = [f"Document {i}" for i in range(1, 26)]

    results = []
    with tqdm(items, desc="Embedding documents") as pbar:
        for item in pbar:
            # Simulate embedding work
            await asyncio.sleep(0.05)
            token_count = random.randint(50, 300)
            results.append({"document": item, "tokens": token_count, "status": "embedded"})

    logger.info(f"Embedded {len(results)} documents")
    console.print(f"[green]Done! Embedded {len(results)} documents.[/green]")


# ─────────────────────────────────────────────
# MAIN ENTRY POINT
# ─────────────────────────────────────────────

async def main():
    console.print(Panel(
        "[bold cyan]Python AI Ecosystem — Practice Demo[/bold cyan]\n"
        "Demonstrating: dotenv, httpx, tenacity, tiktoken, tqdm, loguru, rich, pydantic-settings, pathlib, jsonlines",
        border_style="cyan"
    ))

    # Run each demo
    demo_settings()
    await demo_token_counting()
    demo_jsonl_operations()
    await demo_batch_with_progress()

    console.print("\n[bold green]All demos complete.[/bold green]")
    console.print(f"[dim]Logs written to: {LOG_DIR / 'app.log'}[/dim]")


if __name__ == "__main__":
    asyncio.run(main())


# ─────────────────────────────────────────────
# QUICK REFERENCE — imports you'll use every day
# ─────────────────────────────────────────────

# from dotenv import load_dotenv
# import os
# load_dotenv()
# api_key = os.getenv("OPENAI_API_KEY")

# import httpx
# async with httpx.AsyncClient(timeout=60.0) as client:
#     r = await client.post(url, json=payload, headers=headers)
#     r.raise_for_status()
#     data = r.json()

# from tenacity import retry, stop_after_attempt, wait_random_exponential
# @retry(stop=stop_after_attempt(5), wait=wait_random_exponential(min=1, max=60))
# async def call_api(): ...

# import tiktoken
# enc = tiktoken.encoding_for_model("gpt-4o")
# token_count = len(enc.encode(text))

# from tqdm import tqdm
# for item in tqdm(items, desc="Processing"):
#     process(item)

# from loguru import logger
# logger.info("Starting")
# logger.warning("Token count high")
# logger.error("API failed")

# from pathlib import Path
# data = (Path(__file__).parent / "prompts" / "system.txt").read_text()

# import json
# records = [json.loads(line) for line in open("data.jsonl") if line.strip()]
