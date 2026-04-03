# 📊 Data Systems — From Transactions to Analytics

> An e-commerce site processes 10,000 orders per second. At midnight, the data team runs reports asking "which products drove the most revenue last quarter?" You can't run that query on the order database — it would grind transactions to a halt. Data systems are the architecture that separates writing fast from reading deep.

---

## 📌 Learning Priority

**Must Learn** — Core concept, daily use, interview essential:
OLTP vs OLAP · data warehouse vs data lake · ETL vs ELT · columnar storage (Parquet) · batch vs stream processing · CDC (Change Data Capture)

**Should Learn** — Important for real projects, comes up regularly:
data pipeline architecture · Apache Spark overview · Kafka Streams · star schema · data lakehouse pattern

**Good to Know** — Useful in specific situations:
Apache Flink · Delta Lake · dbt (data build tool) · data mesh · data catalog

**Reference** — Know it exists, look up when needed:
specific DWH SQL dialects · Spark tuning parameters · data governance frameworks

---

## 🏪 Chapter 1: OLTP vs OLAP — Two Different Jobs

> A cash register needs to process one sale in milliseconds. A financial analyst needs to aggregate millions of sales over a quarter. These are fundamentally opposite requirements — one optimizes for fast point writes, the other for fast bulk reads.

**OLTP (Online Transaction Processing):**

```
Primary use:    Handle live user transactions
Queries:        Many small queries (INSERT, UPDATE, SELECT by ID)
Data freshness: Real-time
Scale:          Thousands of transactions per second
Storage:        Row-oriented (read/write one row at a time)
Examples:       PostgreSQL, MySQL, DynamoDB, MongoDB
```

**OLAP (Online Analytical Processing):**

```
Primary use:    Business intelligence, analytics, reporting
Queries:        Few large queries (GROUP BY, aggregations, JOINs across millions of rows)
Data freshness: Hours to days (batch-loaded) or minutes (streaming)
Scale:          Terabytes to petabytes of historical data
Storage:        Column-oriented (read entire column in one scan)
Examples:       Snowflake, BigQuery, Redshift, ClickHouse
```

**Why row vs column storage matters:**

```
Row-oriented (PostgreSQL):
  Row 1: [user_id=1, name="Alice", age=30, city="NY"]
  Row 2: [user_id=2, name="Bob",   age=25, city="LA"]
  Good for: fetch one user's full record (one I/O)
  Bad for:  SELECT AVG(age) — must read name, city too (wasted I/O)

Column-oriented (Parquet, Redshift):
  age column: [30, 25, 34, 28, ...]  stored contiguously
  Good for: SELECT AVG(age) — reads only age column
  Bad for:  fetch one full row — must read all columns separately
```

---

## 🏛️ Chapter 2: Data Warehouse — Analytics at Scale

> A data warehouse is the single source of truth for business analytics — all your operational data cleaned, transformed, and loaded into one place optimized for querying.

**Data warehouse architecture:**

```
Source Systems         ETL/ELT Pipeline        Data Warehouse
──────────────       ─────────────────────    ─────────────────
PostgreSQL ─────────►                        ┌──────────────────┐
MySQL ──────────────► Transform & Load ──────► Fact Tables       │
Salesforce ─────────►                        │ Dimension Tables  │
Kafka ──────────────►                        │ Materialized Views│
S3 logs ────────────►                        └──────────────────┘
                                                      │
                                              BI Tools (Looker,
                                              Tableau, Redash)
```

**Star schema — the standard DWH data model:**

```sql
-- Fact table: stores measurable events (orders)
CREATE TABLE fact_orders (
    order_id      BIGINT,
    user_id       INT,          -- FK to dim_users
    product_id    INT,          -- FK to dim_products
    date_id       INT,          -- FK to dim_date
    quantity      INT,
    revenue       DECIMAL(10,2)
);

-- Dimension tables: descriptive attributes
CREATE TABLE dim_users (
    user_id   INT PRIMARY KEY,
    name      VARCHAR,
    country   VARCHAR,
    tier      VARCHAR           -- 'free', 'pro', 'enterprise'
);

-- Query: revenue by country last quarter
SELECT u.country, SUM(o.revenue)
FROM fact_orders o
JOIN dim_users u ON o.user_id = u.user_id
JOIN dim_date d ON o.date_id = d.date_id
WHERE d.quarter = 'Q3-2024'
GROUP BY u.country;
```

**Top managed data warehouses:**

```
Snowflake:   Separate compute and storage. Auto-suspend (pay when querying).
             Multi-cluster for concurrency. Best for variable workloads.

BigQuery:    Serverless. Pay per query (per TB scanned). Built-in ML.
             Best for: Google ecosystem, ad-hoc analytics, massive scale.

Redshift:    AWS-native. Fixed clusters (or Serverless mode).
             Best for: AWS-heavy shops, existing SQL expertise.

ClickHouse:  Open-source. Extreme performance for time-series analytics.
             Best for: real-time analytics, event data.
```

---

## 🏞️ Chapter 3: Data Lake — Raw Storage First, Schema Later

> A data warehouse is like a library — everything catalogued before anyone reads it. A data lake is like a storage unit — throw everything in, figure out organization when you need it.

A **data lake** stores raw, unprocessed data in its native format (JSON, CSV, Parquet, images, logs) at low cost. Schema is applied at query time ("schema on read").

**Data lake vs Data warehouse:**

```
                Data Lake               Data Warehouse
────────────────────────────────────────────────────────────
Data type       Raw (any format)        Structured, cleaned
Schema          On read (flexible)      On write (enforced)
Cost            Low (S3: ~$0.023/GB)    Higher (compute++)
Query speed     Slower (no indexes)     Fast (pre-aggregated)
Users           Data scientists, ML     Business analysts, BI
Best for        Exploration, ML         Reporting, dashboards
```

**Data Lakehouse — best of both worlds:**

```
Delta Lake / Apache Iceberg / Apache Hudi:
  Store data in Parquet on S3 (cheap object storage)
  Add ACID transactions, schema enforcement, time travel
  Query with Spark, Presto, or DuckDB
  Result: data lake economics + data warehouse reliability
```

---

## 🔄 Chapter 4: ETL vs ELT — When to Transform

**ETL (Extract → Transform → Load):**

```
Source → [Extract] → [Transform in pipeline] → [Load to DWH]

Transform happens BEFORE loading.
Traditional approach (Informatica, Talend).
Good when: target DWH has limited compute, or privacy rules require scrubbing first.
```

**ELT (Extract → Load → Transform):**

```
Source → [Extract] → [Load raw to DWH/lake] → [Transform with SQL in DWH]

Transform happens AFTER loading, using DWH compute.
Modern approach (dbt + Snowflake/BigQuery).
Good when: DWH compute is cheap and scalable.
```

**dbt (data build tool) — the modern ELT approach:**

```sql
-- dbt model: models/marts/revenue_by_country.sql
WITH orders AS (
    SELECT * FROM {{ ref('stg_orders') }}
),
users AS (
    SELECT * FROM {{ ref('stg_users') }}
)
SELECT
    u.country,
    DATE_TRUNC('month', o.created_at) AS month,
    SUM(o.revenue) AS total_revenue
FROM orders o
JOIN users u ON o.user_id = u.user_id
GROUP BY 1, 2
```

---

## 📁 Chapter 5: Columnar File Formats — Parquet and ORC

> Parquet is to analytics what JPEG is to images — a compressed, efficient format designed for the specific access patterns of the job.

**Apache Parquet** is the de-facto standard columnar file format for big data. It stores columns contiguously, supports nested schemas, and achieves 5–10x compression over CSV.

```python
import pandas as pd
import pyarrow as pa
import pyarrow.parquet as pq

# Write Parquet
df = pd.DataFrame({"user_id": [1, 2, 3], "revenue": [10.0, 20.0, 30.0]})
pq.write_table(pa.Table.from_pandas(df), "data.parquet",
               compression="snappy")   # ← snappy: fast, good ratio

# Read only specific columns (projection pushdown):
table = pq.read_table("data.parquet", columns=["revenue"])

# Read with filter pushdown (skips row groups):
table = pq.read_table("data.parquet",
                      filters=[("revenue", ">", 15.0)])
```

**Parquet internals:**

```
File → Row Groups → Columns → Pages
         (128 MB)              (1 MB)

Row Group: stores min/max stats per column → skip entire groups on filter
Column:    stored contiguously → read only columns you need
Pages:     compressed independently → partial decompression
```

---

## ⚙️ Chapter 6: Apache Spark — Large-Scale Batch Processing

> Spark is a distributed computing engine. Feed it a terabyte of data split across 100 servers, and it processes it like one massive DataFrame — parallelism is transparent to your code.

```python
from pyspark.sql import SparkSession
from pyspark.sql.functions import col, sum as spark_sum

spark = SparkSession.builder.appName("RevenueAnalysis").getOrCreate()

# Read from S3 data lake (distributed read)
df = spark.read.parquet("s3://data-lake/orders/2024/")

# Lazy transformations (not executed yet)
result = (df
    .filter(col("status") == "completed")
    .groupBy("country")
    .agg(spark_sum("revenue").alias("total"))
    .orderBy("total", ascending=False)
)

# Action triggers execution across the cluster
result.write.parquet("s3://data-warehouse/revenue_by_country/")
```

**Spark execution model:**

```
Driver        → coordinates job, breaks into tasks
Executors     → worker processes on each node
RDD/DataFrame → distributed dataset partitioned across executors
DAG           → logical plan of transformations (lazy)
Job → Stages → Tasks → dispatched to executors
```

Spark on AWS: EMR (managed clusters) or Glue (serverless).

---

## 🌊 Chapter 7: Stream Processing — Real-Time Data Pipelines

> Batch processing is like washing dishes once a day. Stream processing is washing each dish as soon as it gets dirty. For real-time fraud detection, live dashboards, and instant recommendations, batch is too slow.

**Kafka Streams (processing inside Kafka):**

```python
# Python Kafka consumer acting as a stream processor
from kafka import KafkaConsumer, KafkaProducer
import json

consumer = KafkaConsumer("user-events", bootstrap_servers=["localhost:9092"],
                         value_deserializer=lambda x: json.loads(x))
producer = KafkaProducer(bootstrap_servers=["localhost:9092"],
                         value_serializer=lambda x: json.dumps(x).encode())

for message in consumer:
    event = message.value
    if event["type"] == "purchase":
        # Enrich and forward to analytics topic
        enriched = {**event, "processed_at": time.time()}
        producer.send("analytics-events", enriched)
```

**Batch vs Stream processing decision:**

```
Batch:   hourly/daily jobs, historical analysis, large aggregations
         (Spark, dbt, Airflow DAGs)

Stream:  fraud detection, real-time dashboards, live recommendations,
         event-driven microservices
         (Kafka Streams, Flink, Spark Structured Streaming)

Lambda architecture: run BOTH — stream for low-latency, batch for accuracy
Kappa architecture:  stream only — reprocess history by replaying Kafka
```

---

## 🔁 Chapter 8: CDC — Change Data Capture

> When 10 services all need to know when a user updates their profile, polling the database 10 times is wasteful. CDC streams every database change to all consumers automatically.

**Change Data Capture** reads the database write-ahead log (WAL) and emits every insert, update, and delete as an event.

```
PostgreSQL WAL → Debezium → Kafka topic → downstream consumers
```

**Debezium CDC event format:**

```json
{
  "op": "u",
  "before": {"id": 1, "email": "old@example.com"},
  "after":  {"id": 1, "email": "new@example.com"},
  "source": {"table": "users", "ts_ms": 1704067200000}
}
```

**CDC use cases:**
- Sync DB changes to Elasticsearch (search index stays current)
- Invalidate Redis cache when DB rows change
- Near-real-time replication from OLTP to data warehouse
- Audit trail of all data changes
- Event sourcing backfill

---

## 🔁 Navigation

| | |
|---|---|
| ⬅️ Prev | [../19_clean_architecture/theory.md](../19_clean_architecture/theory.md) |
| ➡️ Next | [../21_real_time_systems/theory.md](../21_real_time_systems/theory.md) |
| 🎤 Interview | [interview.md](./interview.md) |

---

**[🏠 Back to README](../README.md)**

**Prev:** [← Clean Architecture](../19_clean_architecture/theory.md) &nbsp;|&nbsp; **Next:** [Real-Time Systems →](../21_real_time_systems/theory.md)

**Related Topics:** [Databases](../05_databases/theory.md) · [Message Queues](../09_message_queues/theory.md) · [Scalability Patterns](../11_scalability_patterns/theory.md)
