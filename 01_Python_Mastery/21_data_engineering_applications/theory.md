<a id="top"></a>
# 📊 Data Engineering Applications in Python

## 📖 Table of Contents

- [Learning Priority](#-learning-priority)
- [1. What Is Data Engineering?](#1-what-is-data-engineering)
- [2. ETL (Extract, Transform, Load)](#2-etl-extract-transform-load)
- [3. File Processing Pipelines](#3-file-processing-pipelines)
- [4. API Data Collector Systems](#4-api-data-collector-systems)
- [5. Streaming Systems](#5-streaming-systems)
- [6. Memory-Efficient ETL](#6-memory-efficient-etl)
- [7. Checkpointing & Recovery](#7-checkpointing--recovery)
- [8. Scheduling & Orchestration](#8-scheduling--orchestration)
- [9. Data Validation](#9-data-validation)
- [10. Secure Data Handling](#10-secure-data-handling)
- [11. Observability in Pipelines](#11-observability-in-pipelines)
- [12. Example: Daily ETL Pipeline](#12-example-daily-etl-pipeline)
- [Summary](#-summary)
- [Subfolder Deep Dives](#-subfolder-deep-dives)
- [Navigation](#-navigation)

---

## 📌 Learning Priority

**Must Learn** — Core concept, daily use, interview essential:
ETL vs ELT · Batch vs streaming · Memory-efficient processing (generators) · Idempotency · Checkpointing · Retry with backoff

**Should Learn** — Important for real projects, comes up regularly:
Kafka basics (producers, consumers, partitions) · Schema validation · Data deduplication · Monitoring pipelines

**Good to Know** — Useful in specific situations:
Change Data Capture (CDC) · Stream windowing · Exactly-once semantics · Schema evolution (Avro/Protobuf)

**Reference** — Know it exists, look up when needed:
OLAP vs OLTP · Slowly Changing Dimensions · Data lineage tools · Differential privacy · GDPR compliance in pipelines

---

Modern systems generate billions of events daily — logs, transactions, clickstreams, sensor readings. That data is worthless sitting raw in files. Data engineering is the discipline of building reliable pipelines that collect, clean, transform, and deliver data to the systems that need it. Python is the dominant language for this work: it connects to every database, every API, and every message queue — and its generator model makes memory-efficient processing natural.

---

<a id="1-what-is-data-engineering"></a>
# 1. What Is Data Engineering?

## The Analogy

A water treatment plant takes raw water from a river — full of sediment, bacteria, and minerals — and delivers clean, drinkable water to homes. It does not store all the water in one tank. It processes it continuously through a series of filters, each doing one job.

Data engineering is the water treatment plant for information. Raw data flows in; clean, structured, reliable data flows out.

## ETL vs ELT

The classic pattern is **ETL**: Extract data from a source, Transform it into the right shape, Load it into the destination.

The modern variation is **ELT**: Extract, Load raw data into a data warehouse first, then Transform inside the warehouse using SQL. ELT works when your destination (Snowflake, BigQuery, Redshift) is powerful enough to do the transformation cheaply.

```
ETL (traditional):
Source → [Extract] → [Transform in Python] → [Load] → Data Warehouse

ELT (modern cloud):
Source → [Extract] → [Load raw] → Data Warehouse → [Transform with SQL/dbt]
```

## Batch vs Streaming

**Batch processing** — collect data over a period, process all at once. Simple, efficient, but introduces latency. A daily sales report is batch.

**Streaming processing** — process each event as it arrives. Complex, but near-real-time. Fraud detection, live dashboards, and alerting systems are streaming.

```
Batch:    data accumulates → schedule triggers → process all → load results
          (latency: minutes to hours)

Streaming: event arrives → process immediately → update state
          (latency: milliseconds to seconds)
```

## Where Python Fits

Python is used across the entire data engineering stack:

| Layer | Python tools |
|---|---|
| Ingestion | `requests`, `httpx`, `kafka-python`, `boto3` |
| Transformation | `pandas`, `polars`, generators, `pydantic` |
| Orchestration | Airflow, Prefect, Dagster |
| Storage | `psycopg2`, `SQLAlchemy`, `boto3`, `pyarrow` |
| Validation | `pydantic`, `great_expectations`, `pandera` |
| Monitoring | `prometheus_client`, `structlog`, `sentry-sdk` |

[↑ Back to Top](#top)

---

<a id="2-etl-extract-transform-load"></a>
# 2. ETL (Extract, Transform, Load)

## The Analogy

An assembly line takes raw metal, machines it into parts, and ships finished products. Each station does one job. ETL works the same way: extract the raw material, transform it into the right shape, load it into its final home.

## Extract

Pulling data from its source — APIs, files, databases, message queues. The goal is to get data out without losing any, respecting rate limits, and handling failures.

```python
import httpx
import time
from typing import Iterator

def extract_orders_from_api(
    api_url: str,
    api_key: str,
    since: str,                            # ← ISO 8601 datetime string
) -> Iterator[dict]:
    """Paginated API extractor — yields one order at a time."""
    page = 1
    headers = {"Authorization": f"Bearer {api_key}"}

    while True:
        response = httpx.get(
            api_url,
            headers=headers,
            params={"since": since, "page": page, "per_page": 100},
            timeout=30.0,
        )
        response.raise_for_status()
        data = response.json()

        if not data["orders"]:
            break                          # ← no more pages

        yield from data["orders"]         # ← stream records, don't accumulate
        page += 1

        if "X-RateLimit-Remaining" in response.headers:
            remaining = int(response.headers["X-RateLimit-Remaining"])
            if remaining < 10:
                time.sleep(1)              # ← back off before limit hits
```

## Transform

Cleaning and reshaping data — normalizing fields, filtering bad rows, converting types, enriching with lookups.

```python
from datetime import datetime
from pydantic import BaseModel, ValidationError

class Order(BaseModel):
    order_id: str
    user_id: int
    amount: float
    currency: str
    created_at: datetime

def transform_order(raw: dict) -> Order | None:
    """Transform raw API response into a validated Order. Returns None on bad data."""
    try:
        return Order(
            order_id=raw["id"],
            user_id=int(raw["user"]["id"]),
            amount=float(raw["total"]),       # ← coerce string → float
            currency=raw.get("currency", "USD").upper(),
            created_at=raw["created_at"],     # ← Pydantic parses ISO strings
        )
    except (ValidationError, KeyError, ValueError) as e:
        print(f"Skipping bad record {raw.get('id')}: {e}")
        return None
```

## Load

Writing transformed data to the destination — database, data warehouse, file, or message queue.

```python
import psycopg2
from psycopg2.extras import execute_values

def load_orders(conn, orders: list[Order]) -> int:
    """Upsert orders into PostgreSQL. Returns count of rows written."""
    rows = [
        (o.order_id, o.user_id, o.amount, o.currency, o.created_at)
        for o in orders
    ]
    with conn.cursor() as cur:
        execute_values(
            cur,
            """
            INSERT INTO orders (order_id, user_id, amount, currency, created_at)
            VALUES %s
            ON CONFLICT (order_id) DO UPDATE SET
                amount = EXCLUDED.amount,
                updated_at = NOW()
            """,
            rows,
        )
    conn.commit()
    return len(rows)
```

## Full ETL Pipeline

```python
def run_etl(api_url: str, api_key: str, since: str) -> None:
    conn = psycopg2.connect(DATABASE_URL)
    batch: list[Order] = []
    total_loaded = 0

    for raw_order in extract_orders_from_api(api_url, api_key, since):
        order = transform_order(raw_order)
        if order is None:
            continue                           # ← skip invalid rows

        batch.append(order)
        if len(batch) >= 500:                  # ← write in batches of 500
            total_loaded += load_orders(conn, batch)
            batch.clear()

    if batch:                                  # ← flush remaining
        total_loaded += load_orders(conn, batch)

    print(f"ETL complete: {total_loaded} orders loaded")
    conn.close()
```

📝 **Practice:** [ETL pipelines subfolder](./01_etl_pipelines/practice.md) · [Deep dive →](./01_etl_pipelines/theory.md)

[↑ Back to Top](#top)

---

<a id="3-file-processing-pipelines"></a>
# 3. File Processing Pipelines

## The Analogy

Reading a 10 GB log file is like trying to eat a whole watermelon in one bite. You slice it first. File processing pipelines slice large files into manageable pieces, processing one slice at a time — never holding the whole thing in memory.

## Bad Approach

```python
# NEVER do this for large files
data = open("large_file.csv").read()   # ← loads entire file into memory
rows = data.split("\n")                # ← another full copy in memory
# 10 GB file = 20+ GB RAM consumed → MemoryError or OOM kill
```

## Line-by-Line Streaming

```python
import csv

def process_large_csv(filepath: str) -> None:
    """Process a CSV of any size with constant memory usage."""
    with open(filepath, newline="") as f:
        reader = csv.DictReader(f)
        for row in reader:             # ← Python reads one line at a time
            process_row(row)           # ← only one row in memory at once
```

Memory usage stays flat regardless of file size.

## Chunk Processing

For binary files or when you need more control, read fixed-size chunks using the walrus operator:

```python
def read_in_chunks(filepath: str, chunk_size: int = 1024 * 64) -> None:
    """Process a binary file in 64KB chunks."""
    with open(filepath, "rb") as f:
        while chunk := f.read(chunk_size):   # ← walrus: read + check in one step
            process_chunk(chunk)
```

For CSV/JSON files that are too large even for row-by-row streaming, use pandas chunking:

```python
import pandas as pd

def process_large_csv_pandas(filepath: str) -> None:
    """Process a large CSV in 10,000-row chunks using pandas."""
    for chunk in pd.read_csv(filepath, chunksize=10_000):   # ← returns iterator
        # chunk is a DataFrame with 10,000 rows
        cleaned = chunk.dropna().query("amount > 0")
        load_to_db(cleaned)
```

📝 **Practice:** [Q1–Q3 — File processing](./01_etl_pipelines/practice.md)

[↑ Back to Top](#top)

---

<a id="4-api-data-collector-systems"></a>
# 4. API Data Collector Systems

## The Analogy

Collecting data from an external API is like interviewing a source who can only speak for 60 seconds per minute. You must listen carefully, take notes between pauses, and have a plan for when the source goes silent unexpectedly. Rate limits, pagination, and retries are your interview protocol.

## Challenges

- **Rate limits** — most APIs limit to N requests per minute/hour
- **Pagination** — large datasets are split across many pages
- **Network failures** — transient errors require retry logic
- **Partial responses** — API may return malformed data mid-stream
- **Idempotency** — running the job twice must not create duplicate records

## Pagination Pattern

```python
import httpx
from typing import Iterator

def paginate_api(url: str, headers: dict, params: dict) -> Iterator[dict]:
    """Generic cursor-based paginator. Yields one record at a time."""
    cursor = None

    while True:
        if cursor:
            params["cursor"] = cursor

        response = httpx.get(url, headers=headers, params=params, timeout=30.0)
        response.raise_for_status()
        body = response.json()

        yield from body["data"]            # ← stream records immediately

        cursor = body.get("next_cursor")   # ← None when last page
        if not cursor:
            break
```

## Retry and Rate Limit Handling

```python
import time
import random
import httpx

def fetch_with_retry(
    url: str,
    headers: dict,
    max_retries: int = 3,
    base_delay: float = 1.0,
) -> dict:
    for attempt in range(max_retries):
        try:
            response = httpx.get(url, headers=headers, timeout=30.0)

            if response.status_code == 429:             # ← rate limit hit
                retry_after = int(response.headers.get("Retry-After", 60))
                print(f"Rate limited. Waiting {retry_after}s")
                time.sleep(retry_after)
                continue

            response.raise_for_status()
            return response.json()

        except (httpx.TimeoutException, httpx.NetworkError) as e:
            if attempt == max_retries - 1:
                raise
            delay = base_delay * (2 ** attempt) + random.uniform(0, 0.5)  # ← jitter
            print(f"Attempt {attempt + 1} failed: {e}. Retrying in {delay:.1f}s")
            time.sleep(delay)
```

## Idempotency

If a job runs twice — due to retry, crash, or duplicate scheduling — it must not insert duplicate records. The solution is **upsert**: insert new rows, update existing rows, never duplicate.

```python
# Bad: INSERT creates duplicates on retry
cur.execute("INSERT INTO events (event_id, ...) VALUES (%s, ...)", row)

# Good: ON CONFLICT DO NOTHING (idempotent)
cur.execute(
    "INSERT INTO events (event_id, ...) VALUES (%s, ...) ON CONFLICT (event_id) DO NOTHING",
    row,
)

# Good: ON CONFLICT DO UPDATE (upsert)
cur.execute(
    """
    INSERT INTO events (event_id, payload, updated_at)
    VALUES (%s, %s, NOW())
    ON CONFLICT (event_id) DO UPDATE SET
        payload = EXCLUDED.payload,
        updated_at = NOW()
    """,
    (row["id"], row["payload"]),
)
```

📝 **Practice:** [Q2–Q6 — API collection](./02_streaming_api_collection/practice.md) · [Deep dive →](./02_streaming_api_collection/theory.md)

[↑ Back to Top](#top)

---

<a id="5-streaming-systems"></a>
# 5. Streaming Systems

## The Analogy

A radio station does not wait until the end of the day to broadcast the news. It broadcasts continuously, and listeners tune in at any time. Streaming systems work the same way: events are produced and consumed continuously, with no end to the stream.

## Batch vs Streaming

```
Batch:
  Events accumulate in files/DB over hours
  ─────────────────────────────► time
  [00:00 ─────────────── 23:59]
                                ↓
                          process all at once (daily job)

Streaming:
  Each event processed as it arrives
  ──►event──►event──►event──►event──► time
     ↓        ↓        ↓        ↓
  process  process  process  process (milliseconds latency)
```

Use batch when: latency tolerance is hours/days, data is naturally periodic (daily reports, nightly aggregations).
Use streaming when: latency must be seconds (fraud detection, live metrics, real-time recommendations).

## Kafka Consumer Pattern

**Apache Kafka** is the dominant streaming platform. Producers write events to topics; consumers read from topics, maintaining their own offset (position in the stream).

```python
from kafka import KafkaConsumer
import json

def consume_events(topic: str, bootstrap_servers: list[str]) -> None:
    consumer = KafkaConsumer(
        topic,
        bootstrap_servers=bootstrap_servers,
        group_id="etl-pipeline-v1",        # ← consumer group: Kafka tracks offsets per group
        auto_offset_reset="earliest",      # ← start from beginning if no saved offset
        enable_auto_commit=False,          # ← manual commit: don't ack until processed
        value_deserializer=lambda b: json.loads(b.decode("utf-8")),
    )

    for message in consumer:
        try:
            event = message.value          # ← already deserialized dict
            process_event(event)
            consumer.commit()              # ← only commit after successful processing
        except Exception as e:
            print(f"Failed to process event: {e}")
            # ← do NOT commit: message will be redelivered
```

⚠️ `enable_auto_commit=False` with manual commit ensures at-least-once delivery — if processing fails, the event is redelivered. This is the safe default.

## Python Streaming Tools

| Tool | Use case |
|---|---|
| `kafka-python` / `confluent-kafka` | Kafka producers and consumers |
| `asyncio` + `aiohttp` | Async HTTP event ingestion |
| FastAPI with `StreamingResponse` | HTTP streaming endpoints |
| Celery | Distributed task processing triggered by stream events |
| Faust | Stream processing framework built on Kafka, Python-native |

📝 **Practice:** [Q1, Q9 — Streaming](./02_streaming_api_collection/practice.md) · [Deep dive →](./02_streaming_api_collection/theory.md)

[↑ Back to Top](#top)

---

<a id="6-memory-efficient-etl"></a>
# 6. Memory-Efficient ETL

## The Analogy

A conveyor belt at a factory moves one item at a time — it does not dump the entire warehouse contents onto the floor to sort through. A memory-efficient ETL pipeline works the same way: one record flows through the entire pipeline before the next one starts.

## Use Generators

Generators are the key tool for memory-efficient data processing. They produce values lazily — one at a time, on demand — instead of building a full list in memory.

```python
# Memory-expensive: builds full list (all 10M rows in RAM)
rows = [transform(row) for row in read_csv("huge.csv")]   # ← 10M items in memory

# Memory-efficient: generator (one row in memory at a time)
rows = (transform(row) for row in read_csv("huge.csv"))    # ← lazy, no allocation

# Even better: full generator pipeline
def etl_pipeline(filepath: str):
    raw_rows = read_csv_lazy(filepath)           # ← generator
    valid_rows = filter(is_valid, raw_rows)      # ← lazy filter
    transformed = map(transform, valid_rows)     # ← lazy map
    return transformed                           # ← nothing computed yet

# Processing happens only when you iterate:
for record in etl_pipeline("10gb_file.csv"):
    db.insert(record)                            # ← one record at a time
```

## Generator Pipeline Pattern

Chain generators to build a full pipeline where each stage processes one record at a time:

```python
from typing import Iterator
import csv

def read_rows(filepath: str) -> Iterator[dict]:
    """Stage 1: read from file lazily."""
    with open(filepath, newline="") as f:
        yield from csv.DictReader(f)            # ← one row at a time

def clean_rows(rows: Iterator[dict]) -> Iterator[dict]:
    """Stage 2: filter and normalize."""
    for row in rows:
        if not row.get("user_id"):
            continue                            # ← skip invalid rows
        row["amount"] = float(row["amount"])
        row["user_id"] = int(row["user_id"])
        yield row

def batch_rows(rows: Iterator[dict], size: int = 500) -> Iterator[list[dict]]:
    """Stage 3: group into batches for bulk insert."""
    batch = []
    for row in rows:
        batch.append(row)
        if len(batch) >= size:
            yield batch
            batch.clear()
    if batch:
        yield batch                             # ← flush final partial batch

def run_pipeline(filepath: str) -> None:
    """Compose all stages — memory usage stays constant regardless of file size."""
    raw = read_rows(filepath)
    cleaned = clean_rows(raw)
    for batch in batch_rows(cleaned, size=500):
        db.bulk_insert(batch)
```

Memory usage: constant at ~500 rows regardless of file size, because each batch is immediately inserted and discarded.

📝 **Practice:** [Q3, Q5, Q11 — Memory-efficient ETL](./01_etl_pipelines/practice.md)

[↑ Back to Top](#top)

---

<a id="7-checkpointing--recovery"></a>
# 7. Checkpointing & Recovery

## The Analogy

A long road trip without saving your GPS position means starting over if your phone dies. A checkpoint is a saved position — if your pipeline crashes after processing record 50,000, you resume from 50,000, not from 0.

## Why Checkpointing Matters

Long-running jobs fail. Networks drop, databases timeout, cloud instances get preempted. Without checkpointing, every failure means reprocessing all previously processed data — which wastes compute, risks duplicate writes, and can take hours.

## Offset Tracking Pattern

For API-based collection, track the last successfully processed ID or timestamp:

```python
import json
from pathlib import Path

CHECKPOINT_FILE = Path("/tmp/etl_checkpoint.json")

def load_checkpoint() -> dict:
    """Load last saved position. Returns empty dict on first run."""
    if CHECKPOINT_FILE.exists():
        return json.loads(CHECKPOINT_FILE.read_text())
    return {"last_id": None, "processed_count": 0}

def save_checkpoint(state: dict) -> None:
    """Atomically save checkpoint (write to temp, then rename — avoids partial writes)."""
    tmp = CHECKPOINT_FILE.with_suffix(".tmp")
    tmp.write_text(json.dumps(state))
    tmp.rename(CHECKPOINT_FILE)              # ← atomic on POSIX systems


def run_with_checkpoint(api_url: str) -> None:
    state = load_checkpoint()
    last_id = state.get("last_id")
    processed = state.get("processed_count", 0)

    for record in fetch_records_since(api_url, since_id=last_id):
        process_and_load(record)
        processed += 1
        state = {"last_id": record["id"], "processed_count": processed}

        if processed % 1000 == 0:           # ← save checkpoint every 1000 records
            save_checkpoint(state)
            print(f"Checkpoint saved: {processed} records processed")

    save_checkpoint(state)                  # ← final save on completion
```

## Kafka Offset Checkpointing

In Kafka, the consumer group offset IS the checkpoint — Kafka tracks it per topic/partition automatically when you call `consumer.commit()`. The pattern from Section 5 (manual commit after successful processing) is the Kafka checkpoint pattern.

[↑ Back to Top](#top)

---

<a id="8-scheduling--orchestration"></a>
# 8. Scheduling & Orchestration

## The Analogy

A logistics company does not wait for a driver to remember it is time to pick up a shipment. The dispatch system fires automatically at the right time, assigns the right driver, and monitors for delays. Orchestration systems are your data pipeline dispatch center.

## Why Orchestration?

A simple `cron` job runs a script on a schedule. That is fine for simple, independent tasks. But real pipelines have:

- Dependencies: Task B cannot run until Task A succeeds
- Retries: If a step fails, retry it (not the whole pipeline)
- Parallelism: Multiple tasks can run at the same time
- Monitoring: You need to see which steps succeeded, failed, and took too long
- Backfill: You need to re-run historical periods without manual work

## Tool Comparison

| Tool | Best for |
|---|---|
| **Cron** | Simple, independent scripts with no dependencies |
| **Airflow** | Complex DAG workflows, large teams, rich UI, production standard |
| **Prefect** | Modern Python-native orchestration, easier local testing than Airflow |
| **Dagster** | Data-aware pipelines, strong typing, built-in data quality checks |
| **Celery Beat** | Periodic tasks that are already using Celery for async work |

## Airflow DAG Pattern

```python
from airflow import DAG
from airflow.operators.python import PythonOperator
from datetime import datetime, timedelta

default_args = {
    "owner": "data-team",
    "retries": 3,                              # ← retry each task up to 3 times
    "retry_delay": timedelta(minutes=5),
    "email_on_failure": True,
}

with DAG(
    dag_id="daily_orders_etl",
    schedule_interval="0 2 * * *",             # ← run at 2 AM daily
    start_date=datetime(2024, 1, 1),
    catchup=False,                             # ← don't backfill old runs
    default_args=default_args,
) as dag:

    extract = PythonOperator(
        task_id="extract_orders",
        python_callable=run_extract,
    )

    transform = PythonOperator(
        task_id="transform_orders",
        python_callable=run_transform,
    )

    load = PythonOperator(
        task_id="load_to_warehouse",
        python_callable=run_load,
    )

    extract >> transform >> load               # ← dependency chain
```

[↑ Back to Top](#top)

---

<a id="9-data-validation"></a>
# 9. Data Validation

## The Analogy

A customs inspector does not wave everything through. Each shipment is checked against a manifest — correct contents, correct quantities, correct documentation. Data validation is the customs checkpoint at the entrance to your pipeline.

Never trust input data. Validate at the boundary, before the data enters your system.

## Schema Validation with Pydantic

```python
from pydantic import BaseModel, Field, field_validator
from datetime import datetime
from typing import Literal

class OrderEvent(BaseModel):
    order_id: str = Field(min_length=1)
    user_id: int = Field(gt=0)
    amount: float = Field(ge=0.0)
    currency: Literal["USD", "EUR", "GBP", "JPY"]  # ← enum validation
    status: Literal["pending", "completed", "cancelled"]
    created_at: datetime

    @field_validator("order_id")
    @classmethod
    def order_id_format(cls, v: str) -> str:
        if not v.startswith("ord-"):
            raise ValueError("order_id must start with 'ord-'")
        return v


def validate_record(raw: dict) -> OrderEvent | None:
    try:
        return OrderEvent(**raw)
    except Exception as e:
        return None
```

## Handling Bad Rows

A production pipeline must decide: fail on bad data, or skip and log?

```python
from dataclasses import dataclass, field

@dataclass
class ValidationStats:
    total: int = 0
    valid: int = 0
    invalid: int = 0
    errors: list[str] = field(default_factory=list)

def validate_batch(records: list[dict]) -> tuple[list[OrderEvent], ValidationStats]:
    stats = ValidationStats(total=len(records))
    valid_records = []

    for raw in records:
        try:
            valid_records.append(OrderEvent(**raw))
            stats.valid += 1
        except Exception as e:
            stats.invalid += 1
            stats.errors.append(f"Record {raw.get('order_id', '?')}: {e}")

    return valid_records, stats


# After processing, log stats and alert if error rate is high:
valid, stats = validate_batch(raw_records)
error_rate = stats.invalid / stats.total if stats.total > 0 else 0

if error_rate > 0.05:                        # ← alert if >5% of records are invalid
    alert_team(f"High validation error rate: {error_rate:.1%} ({stats.invalid}/{stats.total})")
```

📝 **Practice:** [Q4 — Schema validation](./01_etl_pipelines/practice.md)

[↑ Back to Top](#top)

---

<a id="10-secure-data-handling"></a>
# 10. Secure Data Handling

## The Analogy

A hospital does not post patient records on the waiting room bulletin board. Medical data is handled on a need-to-know basis: anonymized for research, encrypted in transit, audited for access. Data engineering pipelines handle sensitive data the same way.

## PII Masking

**PII (Personally Identifiable Information)** — names, emails, phone numbers, payment info — must be masked in logs and analytics outputs.

```python
import hashlib
import re

def mask_email(email: str) -> str:
    """Hash email for analytics while preserving uniqueness."""
    return hashlib.sha256(email.lower().encode()).hexdigest()[:16]

def mask_card_number(card: str) -> str:
    """Keep last 4 digits, mask the rest."""
    digits = re.sub(r"\D", "", card)
    return f"****-****-****-{digits[-4:]}"

def sanitize_record(record: dict) -> dict:
    """Return a copy of the record with PII fields masked."""
    safe = record.copy()
    if "email" in safe:
        safe["email"] = mask_email(safe["email"])
    if "card_number" in safe:
        safe["card_number"] = mask_card_number(safe["card_number"])
    if "ssn" in safe:
        del safe["ssn"]                        # ← some fields should be dropped entirely
    return safe
```

⚠️ Never log raw PII. Sanitize before any logging call.

## Encryption Patterns

- **In transit** — use HTTPS/TLS for all API calls and database connections. Never send sensitive data over plain HTTP.
- **At rest** — use database-level encryption (AWS RDS encryption, PostgreSQL `pgcrypto`) or application-level encryption for the most sensitive fields.

```python
from cryptography.fernet import Fernet

ENCRYPTION_KEY = os.getenv("ENCRYPTION_KEY")   # ← must be from secrets manager
cipher = Fernet(ENCRYPTION_KEY)

def encrypt_field(value: str) -> str:
    return cipher.encrypt(value.encode()).decode()

def decrypt_field(encrypted: str) -> str:
    return cipher.decrypt(encrypted.encode()).decode()
```

## Audit Logging

Track who accessed or modified sensitive data, when, and why:

```python
import structlog

audit_log = structlog.get_logger("audit")

def access_pii_record(record_id: str, accessed_by: str, reason: str) -> dict:
    record = db.fetch(record_id)
    audit_log.info(
        "pii_record_accessed",
        record_id=record_id,
        accessed_by=accessed_by,
        reason=reason,
        timestamp=datetime.utcnow().isoformat(),
    )
    return record
```

[↑ Back to Top](#top)

---

<a id="11-observability-in-pipelines"></a>
# 11. Observability in Pipelines

## The Analogy

An air traffic controller cannot physically see every plane. They rely on radar — a continuous stream of position, altitude, and speed data. Without radar, controlling traffic is guesswork. Pipeline observability is your radar: you see what is happening, catch anomalies early, and investigate incidents with evidence.

## Key Metrics

| Metric | What it tells you |
|---|---|
| **Job duration** | Is the pipeline running slower than usual? |
| **Records processed** | Did we get all the data, or is something missing? |
| **Error rate** | What fraction of records failed validation or loading? |
| **Processing latency** | How long between event creation and load into warehouse? |
| **Memory / CPU usage** | Is the pipeline consuming expected resources? |
| **Last successful run** | Is the pipeline running at all? |

Alert on: job duration > 2x baseline, error rate > 5%, or no successful run in 2x schedule interval.

## Pipeline Logging Pattern

```python
import structlog
import time
from contextlib import contextmanager

log = structlog.get_logger()

@contextmanager
def pipeline_span(step_name: str, **context):
    """Context manager that logs start, duration, and success/failure of a pipeline step."""
    start = time.monotonic()
    log.info(f"{step_name}.start", **context)
    try:
        yield
        duration = time.monotonic() - start
        log.info(f"{step_name}.success", duration_seconds=round(duration, 3), **context)
    except Exception as e:
        duration = time.monotonic() - start
        log.error(
            f"{step_name}.failure",
            duration_seconds=round(duration, 3),
            error=str(e),
            **context,
        )
        raise


# Usage:
with pipeline_span("extract", source="orders_api", since="2024-01-15"):
    records = list(extract_orders(...))

with pipeline_span("load", destination="orders_warehouse", record_count=len(records)):
    load_orders(conn, records)
```

Output (structured JSON via structlog):
```json
{"event": "extract.start", "source": "orders_api", "since": "2024-01-15"}
{"event": "extract.success", "duration_seconds": 1.247, "source": "orders_api"}
{"event": "load.start", "destination": "orders_warehouse", "record_count": 4823}
{"event": "load.success", "duration_seconds": 0.389, "record_count": 4823}
```

[↑ Back to Top](#top)

---

<a id="12-example-daily-etl-pipeline"></a>
# 12. Example: Daily ETL Pipeline

## Architecture

A daily orders ETL: extract from a REST API, validate, transform, and load into a PostgreSQL data warehouse, with checkpointing, retries, and structured observability.

```
Airflow Scheduler
       │ triggers at 2 AM
       ▼
  ┌─────────────────────────────────────────────────┐
  │             ETL Pipeline                         │
  │                                                  │
  │  [Extract] ──► [Validate] ──► [Transform]        │
  │      │                            │              │
  │      ▼                            ▼              │
  │  [Checkpoint]              [Batch Load]          │
  │                                   │              │
  │                            [PostgreSQL DW]       │
  │                                   │              │
  │                            [Log Metrics]         │
  └─────────────────────────────────────────────────┘
```

## Full Code Sketch

```python
import structlog
from datetime import datetime, timedelta

log = structlog.get_logger()

def run_daily_etl(execution_date: datetime) -> None:
    """
    Full daily ETL pipeline.
    execution_date: the day being processed (Airflow injects this)
    """
    since = (execution_date - timedelta(days=1)).isoformat()
    until = execution_date.isoformat()

    checkpoint = load_checkpoint()
    stats = {"extracted": 0, "valid": 0, "invalid": 0, "loaded": 0}

    with pipeline_span("daily_etl", date=execution_date.date().isoformat()):

        # ── EXTRACT ──
        with pipeline_span("extract", since=since, until=until):
            records = list(extract_orders_from_api(API_URL, API_KEY, since=since))
            stats["extracted"] = len(records)

        # ── VALIDATE ──
        with pipeline_span("validate", record_count=stats["extracted"]):
            valid_records, validation_stats = validate_batch(records)
            stats["valid"] = validation_stats.valid
            stats["invalid"] = validation_stats.invalid

            if validation_stats.invalid / max(stats["extracted"], 1) > 0.05:
                raise RuntimeError(
                    f"Validation error rate too high: "
                    f"{validation_stats.invalid}/{stats['extracted']}"
                )

        # ── TRANSFORM & LOAD ──
        conn = get_db_connection()
        batch = []

        with pipeline_span("load", record_count=stats["valid"]):
            for record in valid_records:
                transformed = transform_order(record)
                batch.append(transformed)

                if len(batch) >= 500:
                    load_orders(conn, batch)
                    stats["loaded"] += len(batch)
                    save_checkpoint({"last_loaded": batch[-1].order_id})
                    batch.clear()

            if batch:
                load_orders(conn, batch)
                stats["loaded"] += len(batch)

        conn.close()

    # ── FINAL METRICS ──
    log.info(
        "daily_etl.complete",
        **stats,
        success_rate=f"{stats['valid']/max(stats['extracted'],1):.1%}",
    )
```

## Design Considerations

| Concern | Solution in this pipeline |
|---|---|
| Duplicate records on retry | `ON CONFLICT DO NOTHING` upsert |
| Crash mid-run | Checkpoint every 500 records |
| Bad data | Validate before load, reject if >5% invalid |
| API rate limits | Retry with backoff, respect `Retry-After` header |
| Slow step | Structured timing logs catch regressions |
| Schema changes | Pydantic `ValidationError` surfaces mismatches early |

[↑ Back to Top](#top)

---

## 🔥 Summary

Data engineering is about building reliable pipelines for moving and transforming data. Reliability matters more than clever code — a pipeline that runs correctly every day at 2 AM is more valuable than one that is technically elegant but occasionally silently drops records.

**Key principles:**

| Principle | Why it matters |
|---|---|
| Stream large data with generators | Constant memory usage regardless of file size |
| Validate at the boundary | Bad data caught early is cheap; bad data in the warehouse is expensive |
| Design idempotent pipelines | Re-running a failed job must not corrupt data |
| Checkpoint long-running jobs | Never reprocess from scratch after a failure |
| Handle retries gracefully | Transient failures are normal; silent data loss is not |
| Monitor everything | Duration, error rate, and record count catch problems before users do |
| Separate config from code | Credentials in environment variables, never in source |
| Mask PII in logs | One log line with a raw email is a compliance violation |

**Common mistakes to avoid:**

- Loading the entire dataset into memory (use generators)
- No retry logic on API calls (use exponential backoff)
- Ignoring rate limits (check `X-RateLimit-Remaining` headers)
- No monitoring or alerting (silent failures run for days)
- No idempotency (duplicate data after a retry)
- Hardcoded credentials (use secrets manager or environment variables)
- No schema validation (malformed data corrupts downstream queries)

**Engineering maturity levels:**

- **Beginner** — writes a working data script
- **Intermediate** — handles large files efficiently with generators
- **Advanced** — designs reliable pipelines with retries and validation
- **Senior** — designs distributed streaming systems with checkpointing
- **Architect** — builds scalable data platforms with full observability

---

## 📂 Subfolder Deep Dives

| Subfolder | Contents |
|---|---|
| [01_etl_pipelines](./01_etl_pipelines/theory.md) | ETL patterns in depth, chunk processing, upsert strategies, Pandas chunking, pipeline testing |
| [02_streaming_api_collection](./02_streaming_api_collection/theory.md) | Kafka producer/consumer deep dive, cursor pagination, webhook ingestion, streaming rate limiter |

---

## 🔁 Navigation

| | |
|---|---|
| 📖 Theory | [theory.md](./theory.md) |
| ⚡ Cheatsheet | [cheetsheet.md](./cheetsheet.md) |
| 🎤 Interview | [interview.md](./interview.md) |
| 💻 Practice | [practice.md](./practice.md) |
| ⬅️ Prev Module | [← System Design with Python](../20_system_design_with_python/theory.md) |
| ➡️ Next Module | [→ NumPy for AI](../22_numpy_for_ai/01_numpy_fundamentals.md) |

**[🏠 Back to README](../README.md)**

**Prev:** [← System Design with Python](../20_system_design_with_python/theory.md) &nbsp;|&nbsp; **Next:** [NumPy for AI →](../22_numpy_for_ai/01_numpy_fundamentals.md)

**Related Topics:** [ETL Pipelines](./01_etl_pipelines/theory.md) · [Streaming & API Collection](./02_streaming_api_collection/theory.md) · [Interview Q&A](./interview.md) · [Cheatsheet](./cheetsheet.md)

[↑ Back to Top](#top)
