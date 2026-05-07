# 🎯 Data Engineering Applications — Interview Preparation Guide  
From ETL Design to Streaming Architecture

---

# 🧠 What Interviewers Actually Test

Data engineering interviews test:

- Can you design reliable pipelines?
- Do you understand batch vs streaming?
- Can you handle failures?
- Do you understand idempotency?
- Can you scale data processing?
- Do you validate data properly?
- Can you optimize memory usage?

They care about correctness and reliability.

---

# 🔹 Level 1: 2–4 Years Experience

Basic pipeline awareness expected.

---

**Q1: What is ETL?**

<details>
<summary>💡 Show Answer</summary>

Strong answer:

> ETL stands for Extract, Transform, Load. It is a process of collecting data from a source, transforming it into required format, and loading it into a target system like a database or warehouse.

Mention:
It can be batch or streaming.

</details>

<br>

**Q2: What is the difference between batch and streaming processing?**

<details>
<summary>💡 Show Answer</summary>

Batch:
Processes large chunks periodically.

Streaming:
Processes data continuously in near real-time.

Important:
Use batch when latency not critical.
Use streaming when near real-time required.

</details>

<br>

**Q3: How do you process large files efficiently in Python?**

<details>
<summary>💡 Show Answer</summary>

Strong answer:

- Use streaming (line-by-line reading)
- Avoid loading entire file into memory
- Use [generators](../11_generators_iterators/theory.md#why-generators-are-lazy--the-memory-story)
- Process in chunks

Mention memory efficiency.

</details>

<br>

**Q4: What is idempotency in data pipelines?**

<details>
<summary>💡 Show Answer</summary>

Strong answer:

> Idempotency ensures that running a pipeline multiple times does not produce duplicate or inconsistent results.

Example:
Use upsert instead of insert.

Idempotency is critical in production pipelines.

</details>


# 🔹 Level 2: 4–7 Years Experience

Now interviewer expects:

- Failure handling
- Checkpointing
- Scheduling
- Rate limiting
- Data validation

---

**Q5: How do you handle API rate limits in data ingestion?**

<details>
<summary>💡 Show Answer</summary>

Strong answer:

- Respect API limits
- Implement retry with exponential backoff
- Track pagination properly
- Store progress checkpoint

Avoid hitting API aggressively.

</details>

<br>

**Q6: What is checkpointing and why is it important?**

<details>
<summary>💡 Show Answer</summary>

Strong answer:

> Checkpointing stores progress state so that if a job fails, it can resume from last processed point instead of restarting from scratch.

Examples:

- Store last processed timestamp
- Store Kafka offset
- Store file pointer

Important for reliability.

</details>

<br>

**Q7: How do you validate incoming data?**

<details>
<summary>💡 Show Answer</summary>

Strong answer:

- Schema validation
- Field type checks
- Required field checks
- Range checks
- Deduplication logic

Data correctness matters more than speed.

</details>

<br>

**Q8: How would you schedule recurring data pipelines?**

<details>
<summary>💡 Show Answer</summary>

Strong answer:

- Use Airflow
- Use cron jobs
- Use workflow orchestrators
- Monitor execution

Mention DAG structure if relevant.

</details>

<br>

**Q9: How do you prevent duplicate data insertion?**

<details>
<summary>💡 Show Answer</summary>

Strong answer:

- Use primary keys
- Use unique constraints
- Use upsert
- Track processed IDs

Shows practical experience.

</details>


# 🔹 Level 3: 7–10 Years Experience

Now discussion becomes architectural and fault-tolerant.

---

**Q10: How would you design a scalable data ingestion system?**

<details>
<summary>💡 Show Answer</summary>

Strong structured answer:

1. Identify data source.
2. Add API ingestion layer.
3. Implement rate limiting.
4. Push data to message queue.
5. Process using workers.
6. Validate data.
7. Store in data warehouse.
8. Add monitoring.
9. Implement retries.
10. Add checkpointing.

Structured thinking wins.

</details>

<br>

**Q11: How do you ensure pipeline reliability?**

<details>
<summary>💡 Show Answer</summary>

Strong answer:

- Idempotent processing
- Retry mechanisms
- Dead-letter queue
- Monitoring and alerting
- Proper logging
- Backpressure handling

Reliability mindset matters.

</details>

<br>

**Q12: How would you handle partial failures?**

<details>
<summary>💡 Show Answer</summary>

Example:
Data loaded partially.

Solution:

- Use transactional writes
- Rollback on failure
- Mark failed records
- Retry only failed portion
- Store failure logs

Graceful failure handling is key.

</details>

<br>

**Q13: How do you optimize memory usage in ETL?**

<details>
<summary>💡 Show Answer</summary>

Strong answer:

- Use [generators](../11_generators_iterators/theory.md#why-generators-are-lazy--the-memory-story)
- Stream processing
- Avoid large in-memory joins
- Process in batches
- Clear unused objects
- Use efficient data structures

Memory efficiency critical in large pipelines.

</details>

<br>

**Q14: What is backpressure in streaming systems?**

<details>
<summary>💡 Show Answer</summary>

Strong answer:

> Backpressure occurs when data is produced faster than it can be consumed.

Solution:

- Slow producers
- Scale consumers
- Buffer properly
- Monitor queue size

Shows advanced streaming knowledge.

</details>

<br>

**Q15: How do you design schema evolution in pipelines?**

<details>
<summary>💡 Show Answer</summary>

Strong answer:

- Version schemas
- Backward compatibility
- Validate new fields
- Maintain migration scripts

Schema evolution is real production problem.

</details>


**Q16: Show the generator-based ETL pipeline pattern in code.**

<details>
<summary>💡 Show Answer</summary>

```python
def extract(filepath):
    with open(filepath, newline="") as f:
        for row in csv.DictReader(f):
            yield dict(row)           # one row at a time

def transform(records):
    for r in records:
        try:
            r["score"] = float(r["score"])
            yield r
        except Exception as e:
            log.warning("bad row: %s", e)  # collect errors, never raise

def load(records, out_path):
    count = 0
    with open(out_path, "w", newline="") as f:
        writer = None
        for r in records:
            if writer is None:
                writer = csv.DictWriter(f, fieldnames=r.keys())
                writer.writeheader()
            writer.writerow(r)
            count += 1
    return count

count = load(transform(extract("source.csv")), "output.csv")
```

Key: each stage is a generator. Only one record exists in memory across all stages at once. O(1) memory regardless of file size.

</details>

<br>

**Q17: What is a dead-letter queue in a pipeline? Show the pattern.**

<details>
<summary>💡 Show Answer</summary>

A dead-letter queue (DLQ) is a separate sink for records that fail validation or transformation. Instead of crashing the pipeline, bad rows are written to an error file for later inspection and replay.

```python
import json

def pipeline_with_dlq(records, dlq_path):
    with open(dlq_path, "a") as dlq:
        for raw in records:
            try:
                yield validate_and_transform(raw)
            except Exception as e:
                dlq.write(json.dumps({"raw": raw, "error": str(e)}) + "\n")
```

Benefits: pipeline keeps running, errors are auditable, bad rows can be replayed after fixing the upstream issue.

</details>

<br>

**Q18: How do you use asyncio.Semaphore for backpressure in an async collector?**

<details>
<summary>💡 Show Answer</summary>

`asyncio.Semaphore(N)` limits how many coroutines run concurrently. Without it, firing 100 page requests at once can overwhelm the API and trigger rate limits.

```python
import asyncio, aiohttp

async def collect_pages(url, total_pages, max_concurrent=5):
    sem = asyncio.Semaphore(max_concurrent)

    async def fetch(session, page):
        async with sem:          # blocks if 5 already running
            async with session.get(url, params={"page": page}) as r:
                return (await r.json()).get("items", [])

    async with aiohttp.ClientSession() as session:
        tasks = [fetch(session, p) for p in range(1, total_pages + 1)]
        pages = await asyncio.gather(*tasks)
    return [item for page in pages for item in page]
```

For thread-based collectors, `queue.Queue(maxsize=N)` provides equivalent backpressure — the producer blocks when the queue is full.

</details>

<br>

**Q19: Show the checkpoint + resume pattern for a long-running pipeline.**

<details>
<summary>💡 Show Answer</summary>

```python
import json
from pathlib import Path

class Checkpoint:
    def __init__(self, path):
        self._path = Path(path)

    def load(self):
        if self._path.exists():
            return json.loads(self._path.read_text())["last_id"]
        return 0   # first run — start from beginning

    def save(self, last_id):
        self._path.write_text(json.dumps({"last_id": last_id}))

cp = Checkpoint("checkpoint.json")
start = cp.load()

for row in read_csv("data.csv"):
    if int(row["id"]) <= start:
        continue               # skip already-processed rows
    process(row)
    cp.save(int(row["id"]))    # update after each successful row
```

Without checkpointing: a 10-hour job that crashes at hour 9 must restart from the beginning. With checkpointing: it resumes from the last saved row ID.

</details>

<br>

**Q20: How does memory-efficient chunked processing differ from pure streaming?**

<details>
<summary>💡 Show Answer</summary>

Pure streaming (one item at a time) cannot do aggregations like GROUP BY without seeing all items. Chunked processing is the middle ground: process N rows at a time, merge partial aggregates.

```python
def chunk(iterable, size):
    batch = []
    for item in iterable:
        batch.append(item)
        if len(batch) >= size:
            yield batch
            batch = []       # clear to free memory
    if batch:
        yield batch

# Memory at any time: O(chunk_size), not O(n)
partial_results = []
for batch in chunk(read_csv("data.csv"), size=1000):
    partial_results.append(aggregate(batch))

final_result = merge(partial_results)
```

| Approach | Memory | Can aggregate? |
|---|---|---|
| Generator pipeline | O(1) | No GROUP BY |
| Chunked processing | O(chunk_size) | Yes, with merge step |
| Eager list | O(n) | Yes | 

</details>

---



---

## Scenario 1:

Your pipeline duplicates data after rerun.

<details>
<summary>💡 Show Answer</summary>

Cause:

No idempotency logic.

Fix:

Use upsert.
Track processed IDs.

</details>
---

## Scenario 2:

Pipeline crashes halfway during batch processing.

<details>
<summary>💡 Show Answer</summary>

Solution:

- Use checkpointing
- Resume from last successful record
- Log failed records

</details>
---

## Scenario 3:

Memory usage grows over time during ETL.

<details>
<summary>💡 Show Answer</summary>

Possible causes:

- Accumulating list
- Not clearing references
- Large in-memory joins

Solution:

Stream data.
Process in chunks.

</details>
---

## Scenario 4:

Kafka consumer lags behind producer.

<details>
<summary>💡 Show Answer</summary>

Possible causes:

- Consumer slow
- Insufficient worker count
- Processing too heavy

Solution:

Scale consumers.
Optimize processing.
Monitor offsets.

</details>
---

## Scenario 5:

API ingestion fails due to network timeout.

<details>
<summary>💡 Show Answer</summary>

Solution:

- Retry with exponential backoff
- Add timeout control
- Log error
- Store failed requests
- Continue processing

Resilience awareness matters.

</details>
---

# 🧠 How to Answer Like a Strong Candidate

Weak:

“I write scripts to process data.”

Strong:

> “I design data pipelines to be idempotent, memory-efficient, and fault-tolerant. I use streaming processing for large datasets, implement checkpointing for reliability, handle retries carefully, and monitor pipeline performance in production.”

Structured.
Reliable.
Professional.

---

# ⚠️ Common Weak Candidate Mistakes

- Ignoring idempotency
- Loading full dataset into memory
- Not handling API failures
- Ignoring rate limits
- No monitoring
- No schema validation
- No retry logic

Data engineering is about reliability.

Not just data movement.

---

# 🎯 Rapid-Fire Revision

- ETL = Extract, Transform, Load
- Batch vs streaming difference
- Use streaming for large files
- Idempotency prevents duplicates
- Checkpointing enables resume
- Retry with exponential backoff
- Validate schema early
- Monitor pipelines
- Handle partial failures gracefully
- Use message queues for scalability

---

# 🏆 Final Interview Mindset

Data engineering interviews test:

- Reliability thinking
- Scalability awareness
- Memory efficiency
- Idempotency clarity
- Failure handling maturity
- Production discipline

If you demonstrate:

- Structured pipeline design
- Idempotent architecture
- Checkpoint strategy
- Retry logic awareness
- Memory-efficient processing
- Monitoring strategy

You appear as senior data engineer.

Data pipelines must be correct, scalable, and reliable.

Not just fast.

---

# 🔁 Navigation

Previous:  
[21_data_engineering_applications/theory.md](./theory.md)

Next:  
[99_interview_master/python_0_2_years.md](../99_interview_master/python_0_2_years.md)

---

**[🏠 Back to README](../README.md)**

**Prev:** [← Theory](./theory.md) &nbsp;|&nbsp; **Next:** [Numpy For Ai — Theory →](../22_numpy_for_ai/theory.md)

**Related Topics:** [Theory](./theory.md)
