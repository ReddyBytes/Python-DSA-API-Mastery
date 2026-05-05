# Async Python for AI Engineering — Practice

"""
Working code examples for:
  1. Streaming response from a mock LLM (async generator pattern)
  2. Parallel API calls with asyncio.gather
  3. Rate-limited batch embedding with Semaphore
  4. Async queue for document processing pipeline
  5. FastAPI endpoint that streams an LLM response

All examples use realistic patterns with mocked APIs.
No real API keys needed — run each section with asyncio.run().
"""

import asyncio
import random
import time
from contextlib import asynccontextmanager


# ============================================================
# SECTION 1: Streaming Response — Async Generator Pattern
# ============================================================
# The ChatGPT effect: words appear one by one instead of
# all at once after a 3-second wait.
# ============================================================

# Mock: simulate an LLM that returns tokens one at a time
MOCK_RESPONSES = {
    "default": "Async Python is a programming model where you can handle many tasks at once without using threads by yielding control at I/O boundaries.",
    "short": "Async generators yield values while awaiting between each one.",
    "haiku": "Event loop runs free. Coroutines yield and breathe. No thread holds them back.",
}


async def mock_llm_stream(prompt: str, delay_per_token: float = 0.08):
    """
    Async generator that simulates an LLM streaming tokens one at a time.

    In a real implementation this would be:
        stream = await client.chat.completions.create(..., stream=True)
        async for chunk in stream:
            yield chunk.choices[0].delta.content
    """
    # Choose a canned response based on keywords in the prompt
    if "haiku" in prompt.lower():
        text = MOCK_RESPONSES["haiku"]
    elif "short" in prompt.lower():
        text = MOCK_RESPONSES["short"]
    else:
        text = MOCK_RESPONSES["default"]

    words = text.split()
    for i, word in enumerate(words):
        await asyncio.sleep(delay_per_token)   # simulate network latency per token
        # Yield the word with a trailing space (except last word)
        yield word if i == len(words) - 1 else word + " "


async def display_stream(prompt: str):
    """Consume the async generator and print tokens as they arrive."""
    print(f"\nPrompt: {prompt}")
    print("Response: ", end="", flush=True)

    full_response = []
    async for token in mock_llm_stream(prompt):
        print(token, end="", flush=True)
        full_response.append(token)

    print()   # newline after stream ends
    return "".join(full_response)


async def stream_to_buffer(prompt: str) -> str:
    """Collect all tokens into a string (for when you need the full response)."""
    return "".join([token async for token in mock_llm_stream(prompt)])


async def run_streaming_examples():
    print("=" * 60)
    print("SECTION 1: Streaming Async Generator")
    print("=" * 60)

    # Basic streaming display
    result = await display_stream("Tell me about async Python")

    # Collect into buffer
    full = await stream_to_buffer("Write a short answer")
    print(f"\nCollected: {full}")

    # Two streams at once — each yields independently
    print("\nTwo streams simultaneously:")
    t_start = time.perf_counter()
    r1, r2 = await asyncio.gather(
        stream_to_buffer("Tell me about async Python"),
        stream_to_buffer("Write a haiku about async"),
    )
    elapsed = time.perf_counter() - t_start
    print(f"Response 1: {r1[:50]}...")
    print(f"Response 2: {r2}")
    print(f"Total time: {elapsed:.2f}s (both streams ran concurrently)")


# ============================================================
# SECTION 2: Parallel API Calls — asyncio.gather
# ============================================================
# Classic use case: summarize 5 documents at once instead of
# sequentially. 5 × 0.5s = 2.5s sequential vs ~0.5s concurrent.
# ============================================================

async def mock_llm_call(prompt: str, mock_delay: float | None = None) -> str:
    """
    Simulates a single LLM API call with a realistic variable delay.

    In production this would be:
        response = await client.chat.completions.create(
            model="gpt-4o",
            messages=[{"role": "user", "content": prompt}]
        )
        return response.choices[0].message.content
    """
    delay = mock_delay if mock_delay is not None else random.uniform(0.3, 0.8)
    await asyncio.sleep(delay)
    word_count = random.randint(10, 20)
    return f"[Mock LLM response to '{prompt[:30]}...' — {word_count} words]"


async def sequential_calls(prompts: list[str]) -> list[str]:
    """Process prompts one at a time — the slow way."""
    results = []
    for prompt in prompts:
        result = await mock_llm_call(prompt)
        results.append(result)
    return results


async def parallel_calls(prompts: list[str]) -> list[str]:
    """Process all prompts concurrently — the fast way."""
    tasks = [mock_llm_call(p) for p in prompts]
    return await asyncio.gather(*tasks)


async def parallel_calls_with_error_handling(prompts: list[str]) -> list[str | None]:
    """
    Process concurrently AND handle individual failures gracefully.
    return_exceptions=True means one failure does not abort the batch.
    """
    tasks = [mock_llm_call(p) for p in prompts]
    results = await asyncio.gather(*tasks, return_exceptions=True)

    output = []
    for prompt, result in zip(prompts, results):
        if isinstance(result, Exception):
            print(f"  [ERROR] Failed for prompt '{prompt[:30]}': {result}")
            output.append(None)
        else:
            output.append(result)
    return output


async def run_parallel_examples():
    print("\n" + "=" * 60)
    print("SECTION 2: Parallel API Calls with gather")
    print("=" * 60)

    prompts = [
        "Summarize the history of machine learning",
        "Explain what a transformer architecture is",
        "What is retrieval-augmented generation?",
        "Describe the attention mechanism in neural networks",
        "What is fine-tuning a language model?",
    ]

    # Sequential (slow):
    t_start = time.perf_counter()
    sequential_results = await sequential_calls(prompts)
    sequential_time = time.perf_counter() - t_start
    print(f"\nSequential: {len(sequential_results)} calls in {sequential_time:.2f}s")

    # Parallel (fast):
    t_start = time.perf_counter()
    parallel_results = await parallel_calls(prompts)
    parallel_time = time.perf_counter() - t_start
    print(f"Parallel:   {len(parallel_results)} calls in {parallel_time:.2f}s")
    print(f"Speedup:    {sequential_time / parallel_time:.1f}x")

    # create_task pattern — start now, collect later:
    print("\ncreate_task pattern:")
    t_start = time.perf_counter()
    task1 = asyncio.create_task(mock_llm_call("What is GPT-4?"))
    task2 = asyncio.create_task(mock_llm_call("What is Claude?"))

    # Both tasks are running while we do other work:
    await asyncio.sleep(0.1)   # simulate other setup work
    print(f"  Doing setup while LLM calls run in background...")

    r1 = await task1
    r2 = await task2
    elapsed = time.perf_counter() - t_start
    print(f"  Collected both results in {elapsed:.2f}s (overlapped with setup)")


# ============================================================
# SECTION 3: Rate-Limited Batch Embedding — Semaphore
# ============================================================
# Embed 50 "documents" but cap at max 10 concurrent calls
# to simulate respecting an API rate limit.
# ============================================================

async def mock_embed(text: str) -> list[float]:
    """
    Simulates an embedding API call.

    In production:
        response = await client.embeddings.create(
            model="text-embedding-3-small",
            input=text
        )
        return response.data[0].embedding
    """
    await asyncio.sleep(random.uniform(0.05, 0.15))   # simulate API latency
    # Return a fake 4-dimensional embedding (real ones are 1536-dim)
    return [random.random() for _ in range(4)]


async def embed_with_semaphore(
    text: str,
    semaphore: asyncio.Semaphore,
    doc_id: int,
) -> dict:
    """Embed one document, waiting for a semaphore slot first."""
    async with semaphore:   # blocks if max_concurrent slots are taken
        embedding = await mock_embed(text)
        return {"id": doc_id, "text": text[:30], "embedding": embedding}


async def embed_corpus(
    documents: list[str],
    max_concurrent: int = 10,
) -> list[dict]:
    """
    Embed all documents with controlled concurrency.
    Even though all tasks are created at once, the semaphore ensures
    at most max_concurrent are running at any moment.
    """
    semaphore = asyncio.Semaphore(max_concurrent)

    # All tasks created at once — semaphore controls concurrency:
    tasks = [
        embed_with_semaphore(doc, semaphore, i)
        for i, doc in enumerate(documents)
    ]
    results = await asyncio.gather(*tasks, return_exceptions=True)

    # Filter out any failures:
    embedded = [r for r in results if not isinstance(r, Exception)]
    failed = [r for r in results if isinstance(r, Exception)]

    if failed:
        print(f"  [WARNING] {len(failed)} embeddings failed")

    return embedded


async def embed_with_retry(
    text: str,
    semaphore: asyncio.Semaphore,
    doc_id: int,
    max_retries: int = 3,
) -> dict:
    """Embed with exponential backoff retry — simulates rate limit recovery."""
    async with semaphore:
        for attempt in range(max_retries):
            try:
                # Simulate occasional rate limit errors (10% chance):
                if random.random() < 0.10:
                    raise ConnectionError("Mock RateLimitError: 429")
                embedding = await mock_embed(text)
                return {"id": doc_id, "text": text[:30], "embedding": embedding}
            except ConnectionError as e:
                if attempt == max_retries - 1:
                    raise
                delay = (2 ** attempt) + random.random()
                print(f"  [RETRY] doc {doc_id} attempt {attempt+1}, waiting {delay:.1f}s")
                await asyncio.sleep(delay)


async def run_semaphore_examples():
    print("\n" + "=" * 60)
    print("SECTION 3: Rate-Limited Batch Embedding with Semaphore")
    print("=" * 60)

    documents = [f"This is document number {i} about topic {i % 5}" for i in range(50)]

    # Without semaphore — all 50 fire at once:
    t_start = time.perf_counter()
    tasks_no_limit = [mock_embed(doc) for doc in documents]
    results_no_limit = await asyncio.gather(*tasks_no_limit)
    time_no_limit = time.perf_counter() - t_start
    print(f"\nNo limit (50 concurrent):    {len(results_no_limit)} docs in {time_no_limit:.2f}s")

    # With semaphore — max 10 at a time:
    t_start = time.perf_counter()
    embedded_10 = await embed_corpus(documents, max_concurrent=10)
    time_10 = time.perf_counter() - t_start
    print(f"Semaphore(10) max concurrent: {len(embedded_10)} docs in {time_10:.2f}s")

    # With semaphore — max 5 at a time (slower but gentler on rate limits):
    t_start = time.perf_counter()
    embedded_5 = await embed_corpus(documents, max_concurrent=5)
    time_5 = time.perf_counter() - t_start
    print(f"Semaphore(5)  max concurrent: {len(embedded_5)} docs in {time_5:.2f}s")

    print(f"\nAll produced correct embeddings: {len(embedded_10) == 50}")

    # With retry:
    print("\nEmbedding with retry on rate limit errors:")
    semaphore = asyncio.Semaphore(10)
    retry_tasks = [
        embed_with_retry(doc, semaphore, i)
        for i, doc in enumerate(documents[:20])
    ]
    retry_results = await asyncio.gather(*retry_tasks, return_exceptions=True)
    success = sum(1 for r in retry_results if not isinstance(r, Exception))
    print(f"Embedded {success}/20 docs (some may have retried)")


# ============================================================
# SECTION 4: Async Queue — Document Processing Pipeline
# ============================================================
# Producer reads documents and puts them in a queue.
# Consumers take documents and process (embed) them.
# Queue decouples reading speed from processing speed.
# ============================================================

async def document_producer(
    queue: asyncio.Queue,
    documents: list[str],
    num_consumers: int,
):
    """
    Puts documents into the queue one by one.
    Sends a None sentinel for each consumer to signal end of input.
    """
    for i, doc in enumerate(documents):
        await queue.put({"id": i, "content": doc})
        await asyncio.sleep(0.01)   # simulate reading from disk or network

    # Send one sentinel per consumer:
    for _ in range(num_consumers):
        await queue.put(None)

    print(f"  Producer: queued {len(documents)} documents + {num_consumers} sentinels")


async def document_consumer(
    queue: asyncio.Queue,
    results: list,
    consumer_id: int,
    semaphore: asyncio.Semaphore,
):
    """
    Takes documents from the queue and embeds them.
    Stops when it receives the None sentinel.
    """
    processed = 0
    while True:
        item = await queue.get()   # blocks until a document is available

        if item is None:
            queue.task_done()
            print(f"  Consumer {consumer_id}: done, processed {processed} docs")
            break

        try:
            async with semaphore:
                embedding = await mock_embed(item["content"])
            results.append({"id": item["id"], "embedding": embedding})
            processed += 1
        except Exception as e:
            print(f"  Consumer {consumer_id}: failed on doc {item['id']}: {e}")
        finally:
            queue.task_done()   # always mark done, even on failure


async def process_document_pipeline(
    documents: list[str],
    num_consumers: int = 3,
    queue_max_size: int = 20,
    max_concurrent_embeds: int = 5,
) -> list[dict]:
    """
    Full producer-consumer pipeline.
    Producer reads docs → queue → consumers embed → results list.
    """
    queue = asyncio.Queue(maxsize=queue_max_size)
    semaphore = asyncio.Semaphore(max_concurrent_embeds)
    results = []

    # Start producer and all consumers concurrently:
    await asyncio.gather(
        document_producer(queue, documents, num_consumers),
        *[
            document_consumer(queue, results, consumer_id=i, semaphore=semaphore)
            for i in range(num_consumers)
        ],
    )

    # Wait for all queued items to be processed:
    await queue.join()

    return results


async def run_queue_examples():
    print("\n" + "=" * 60)
    print("SECTION 4: Async Queue — Document Processing Pipeline")
    print("=" * 60)

    documents = [f"Document {i}: content about topic {i % 10}" for i in range(30)]

    print(f"\nProcessing {len(documents)} documents with 3 consumers:")
    t_start = time.perf_counter()
    results = await process_document_pipeline(
        documents,
        num_consumers=3,
        max_concurrent_embeds=5,
    )
    elapsed = time.perf_counter() - t_start

    print(f"\nPipeline complete: {len(results)}/{len(documents)} embedded in {elapsed:.2f}s")
    print(f"First embedding shape: {len(results[0]['embedding'])} dimensions")


# ============================================================
# SECTION 5: FastAPI Streaming Endpoint
# ============================================================
# Full FastAPI app that streams LLM tokens via Server-Sent Events.
# Run separately with: uvicorn practice:app --reload
# Then test with: curl -N http://localhost:8000/stream?prompt=hello
# ============================================================

try:
    from fastapi import FastAPI
    from fastapi.responses import StreamingResponse
    FASTAPI_AVAILABLE = True
except ImportError:
    FASTAPI_AVAILABLE = False

if FASTAPI_AVAILABLE:
    app = FastAPI(title="Async LLM API", description="Streaming LLM endpoint example")

    # ---- Shared client (in production, use AsyncOpenAI here) ----
    # client = AsyncOpenAI()   # uncomment with real key

    async def generate_tokens(prompt: str):
        """
        Async generator that yields tokens from the mock LLM.
        In production, replace mock_llm_stream with real OpenAI streaming.
        """
        async for token in mock_llm_stream(prompt, delay_per_token=0.08):
            yield token

    async def sse_stream(prompt: str):
        """Wrap token generator in Server-Sent Events format."""
        async for token in generate_tokens(prompt):
            # SSE format: "data: <content>\n\n"
            # The double newline signals end of one event to the client
            yield f"data: {token}\n\n"
        yield "data: [DONE]\n\n"   # signals end of stream to client

    @app.post("/stream")
    async def stream_endpoint(prompt: str):
        """
        Streaming LLM endpoint.
        Tokens appear in the client as they are generated — no waiting for full response.

        Test with:
            curl -N "http://localhost:8000/stream?prompt=hello+world"
        """
        return StreamingResponse(
            sse_stream(prompt),
            media_type="text/event-stream",
            headers={
                "Cache-Control": "no-cache",
                "X-Accel-Buffering": "no",   # disable nginx buffering
            },
        )

    @app.post("/chat")
    async def chat_endpoint(prompt: str) -> dict:
        """
        Standard (non-streaming) LLM endpoint.
        Returns the full response at once.

        Because this is async def, FastAPI can handle 100 concurrent
        requests in one worker — all LLM calls are in-flight simultaneously.
        """
        # Collect the full stream into a string:
        full_response = "".join([
            token async for token in mock_llm_stream(prompt)
        ])
        return {"prompt": prompt, "response": full_response}

    @app.post("/batch")
    async def batch_endpoint(prompts: list[str]) -> dict:
        """
        Run multiple LLM calls in parallel and return all results.
        All calls are in-flight simultaneously via asyncio.gather.
        """
        semaphore = asyncio.Semaphore(5)   # rate limit to 5 concurrent

        async def safe_call(p: str) -> str:
            async with semaphore:
                return "".join([t async for t in mock_llm_stream(p)])

        tasks = [safe_call(p) for p in prompts]
        results = await asyncio.gather(*tasks, return_exceptions=True)

        return {
            "results": [
                {"prompt": p, "response": r if not isinstance(r, Exception) else f"ERROR: {r}"}
                for p, r in zip(prompts, results)
            ]
        }

else:
    print("FastAPI not installed. Section 5 code is shown above but not executable.")
    print("Install with: pip install fastapi uvicorn")


# ============================================================
# BONUS: Timeout and Cancellation
# ============================================================

async def call_with_timeout(prompt: str, timeout: float = 0.5) -> str | None:
    """
    Wrap any LLM call with a timeout.
    If it takes longer than 'timeout' seconds, return None.
    """
    try:
        full = await asyncio.wait_for(
            stream_to_buffer(prompt),
            timeout=timeout,
        )
        return full
    except asyncio.TimeoutError:
        print(f"  [TIMEOUT] Call timed out after {timeout}s")
        return None


async def run_timeout_examples():
    print("\n" + "=" * 60)
    print("BONUS: Timeouts and Cancellation")
    print("=" * 60)

    # Short timeout — fast prompt (short response, finishes in time):
    result = await call_with_timeout("Write a short answer", timeout=2.0)
    print(f"\nWith 2.0s timeout: {'got result' if result else 'timed out'}")

    # Very short timeout — likely to time out:
    result = await call_with_timeout("Tell me about async Python", timeout=0.3)
    print(f"With 0.3s timeout: {'got result' if result else 'timed out'}")

    # Python 3.11+ timeout context manager:
    # async with asyncio.timeout(5.0):
    #     result = await stream_to_buffer("prompt")


# ============================================================
# MAIN RUNNER
# ============================================================

async def main():
    print("Async Python for AI Engineering — Practice Examples")
    print("=" * 60)

    await run_streaming_examples()
    await run_parallel_examples()
    await run_semaphore_examples()
    await run_queue_examples()
    await run_timeout_examples()

    print("\n" + "=" * 60)
    print("All examples complete.")
    if FASTAPI_AVAILABLE:
        print("\nFastAPI app is defined as 'app' in this file.")
        print("Run it with: uvicorn practice:app --reload")
        print("Then test:   curl -N 'http://localhost:8000/stream?prompt=hello'")
    print("=" * 60)


if __name__ == "__main__":
    asyncio.run(main())
