<a id="top"></a>

# Data Systems — From Transactions to Analytics

> Your app's PostgreSQL database works perfectly at 10,000 users. At 10 million users, the CEO asks: "Why did we lose $400K last quarter?" The analyst runs a query. It takes 4 hours. Production slows to a crawl. You have just discovered the difference between OLTP and OLAP.

*Sekhar is a Telugu data platform engineer who has built pipelines processing billions of events daily. He learned the hard way — his first analytics query took down production at 2 AM, paging every on-call engineer. Now he teaches teams how to separate operational from analytical workloads, and why "just run it on prod" is the fastest path to an incident.*

## 📖 Table of Contents

- [1. OLTP vs OLAP — Two Different Worlds](#1-oltp-vs-olap-two-different-worlds)
  - [Why You Cannot Run Analytics on Production](#why-you-cannot-run-analytics-on-production)
- [2. Data Warehouse — Analytics at Scale](#2-data-warehouse-analytics-at-scale)
  - [Column-Oriented Storage](#column-oriented-storage)
  - [Star Schema — The Standard DWH Data Model](#star-schema-the-standard-dwh-data-model)
  - [The Big Three Data Warehouses](#the-big-three-data-warehouses)
- [3. Data Lake — Raw Storage First, Schema Later](#3-data-lake-raw-storage-first-schema-later)
  - [Schema on Read vs Schema on Write](#schema-on-read-vs-schema-on-write)
  - [Data Lakehouse — Best of Both Worlds](#data-lakehouse-best-of-both-worlds)
- [4. ETL vs ELT — When to Transform](#4-etl-vs-elt-when-to-transform)
  - [Modern ELT with dbt](#modern-elt-with-dbt)
- [5. Columnar File Formats — Parquet and ORC](#5-columnar-file-formats-parquet-and-orc)
- [6. Apache Spark — Distributed Computation](#6-apache-spark-distributed-computation)
  - [RDDs and DataFrames](#rdds-and-dataframes)
  - [Spark SQL](#spark-sql)
  - [When Spark vs When a Database](#when-spark-vs-when-a-database)
- [7. Stream Processing — Real-Time Pipelines](#7-stream-processing-real-time-pipelines)
  - [Batch vs Stream Decision](#batch-vs-stream-decision)
- [8. CDC — Change Data Capture](#8-cdc-change-data-capture)
- [9. The Modern Data Stack](#9-the-modern-data-stack)
- [Summary](#summary)

## Learning Priority

**Must Learn** — Core concept, daily use, interview essential:
OLTP vs OLAP, data warehouse vs data lake, ETL vs ELT, columnar storage (Parquet), batch vs stream processing, CDC (Change Data Capture)

**Should Learn** — Important for real projects, comes up regularly:
data pipeline architecture, Apache Spark overview, Kafka Streams, star schema, data lakehouse pattern

**Good to Know** — Useful in specific situations:
Apache Flink, Delta Lake, dbt (data build tool), data mesh, data catalog

**Reference** — Know it exists, look up when needed:
specific DWH SQL dialects, Spark tuning parameters, data governance frameworks

<a id="1-oltp-vs-olap-two-different-worlds"></a>

# 1. OLTP vs OLAP — Two Different Worlds

"Think of it like a cashier versus an accountant," Sekhar tells his new team members. "The cashier scans one item at a time, fast, hundreds of customers per hour — that is OLTP. The accountant sits down at month-end with all the receipts and asks 'what category spent the most?' — that is OLAP. They need completely different desks, different tools, different workflows. You would never make the cashier stop serving customers so the accountant can spread receipts across the counter."

**OLTP (Online Transaction Processing):**

```
Primary use:    Handle live user transactions
Queries:        Many small queries (INSERT, UPDATE, SELECT by ID)
                "Get user 12345's profile"
                "Update order 98765's status to SHIPPED"
                "Insert new payment record for Alice"
Data freshness: Real-time
Latency goal:   Milliseconds (your users are waiting)
Write frequency: Very high (every user action = writes)
Data shape:     Normalized (3NF) — minimize redundancy
Scale:          Thousands to millions of rows changed per hour
Storage:        Row-oriented (read/write one row at a time)
Examples:       PostgreSQL, MySQL, DynamoDB, MongoDB

  ┌──────────────────────────────────────────────┐
  │  users table                                 │
  │  id | name  | email           | joined       │
  │   1 | Alice | alice@email.com | 2023-01-15   │
  │   2 | Bob   | bob@email.com   | 2023-02-20   │
  │                                              │
  │  Query: SELECT * FROM users WHERE id = 1     │
  │  --> returns 1 row, instantly                 │
  └──────────────────────────────────────────────┘
```

**OLAP (Online Analytical Processing):**

```
Primary use:    Business intelligence, analytics, reporting
Queries:        Few large queries (GROUP BY, aggregations, JOINs across millions of rows)
                "What was our revenue by country last quarter?"
                "Which features correlate with user retention?"
                "Show me DAU by cohort for the past 6 months"
Data freshness: Hours to days (batch-loaded) or minutes (streaming)
Latency goal:   Seconds to minutes (analysts are waiting, not users)
Write frequency: Low (data loaded in batches or streams)
Data shape:     Denormalized (star/snowflake schema) — optimize reads
Scale:          Billions to trillions of rows scanned per query
Storage:        Column-oriented (read entire column in one scan)
Examples:       Snowflake, BigQuery, Redshift, ClickHouse

  ┌──────────────────────────────────────────────────────────┐
  │  fact_orders table (denormalized — no JOINs needed)      │
  │  order_id | user_name | country | product | revenue      │
  │  1001     | Alice     | US      | Pro     | 99.00        │
  │  1002     | Bob       | UK      | Basic   | 29.00        │
  │  ...      | ...       | ...     | ...     | ...          │
  │  [500 million rows]                                      │
  │                                                          │
  │  Query: SELECT country, SUM(revenue)                     │
  │         FROM fact_orders                                 │
  │         WHERE quarter = 'Q4-2024'                        │
  │         GROUP BY country                                 │
  │  --> scans 500M rows, returns 50 rows, takes 10 seconds  │
  └──────────────────────────────────────────────────────────┘
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

  Also: similar values in a column compress extremely well.
  "US, US, US, UK, US, US..." --> run-length encoding --> tiny on disk.
```

<a id="why-you-cannot-run-analytics-on-production"></a>

## Why You Cannot Run Analytics on Production

"I learned this the hard way," Sekhar admits. "My first week on the job, I ran a revenue report directly on the production PostgreSQL. Within minutes, the buffer pool was flooded, app queries went from 5ms to 3 seconds, and I got a call from the on-call engineer at 2 AM."

```
Production PostgreSQL database:
  10,000 users making requests per second
  App queries: < 5ms (index lookups, simple reads)

Analyst runs: SELECT COUNT(*), AVG(revenue) FROM orders
              WHERE created_at > '2024-01-01' GROUP BY product_id

  --> Full table scan: locks buffer pool with 200M rows
  --> Evicts cached hot data from shared_buffers
  --> App queries suddenly taking 2-3 seconds instead of 5ms
  --> Users see slow page loads
  --> On-call engineer gets paged at 2 AM
  --> Analyst wonders why everyone is upset

The fix: send analytics queries to a system designed for them.

  Production DB (OLTP)          Data Warehouse (OLAP)
  ──────────────────────        ────────────────────────
  Normalized data               Denormalized (pre-joined)
  Row-oriented storage          Column-oriented storage
  Optimized for writes          Optimized for reads
  ACID transactions             Eventual consistency OK
  GBs to low TBs               TBs to PBs
  Updated continuously          Updated in batch/stream
  Cannot be touched by analysts Built FOR analysts
```

> [↑ Back to Top](#top)

<a id="2-data-warehouse-analytics-at-scale"></a>

# 2. Data Warehouse — Analytics at Scale

"A data warehouse is like a library," Sekhar explains. "Every book (data) is catalogued, indexed, and shelved in a specific way BEFORE anyone can browse it. You cannot just dump a box of papers on the floor and call it a library. The upfront organization cost pays off every time someone asks a question."

A data warehouse is a database built specifically for analytical queries. It stores historical data from production systems, organized for fast aggregation.

**Data warehouse architecture:**

```
Source Systems         ETL/ELT Pipeline        Data Warehouse
──────────────       ─────────────────────    ─────────────────
PostgreSQL ─────────>                        ┌──────────────────┐
MySQL ──────────────> Transform & Load ──────> Fact Tables       │
Salesforce ─────────>                        │ Dimension Tables  │
Kafka ──────────────>                        │ Materialized Views│
S3 logs ────────────>                        └──────────────────┘
                                                      │
                                              BI Tools (Looker,
                                              Tableau, Redash)
```

<a id="column-oriented-storage"></a>

## Column-Oriented Storage

Traditional databases store data row by row. Data warehouses store it column by column. This makes a massive difference for analytics.

```
Row-oriented (PostgreSQL):
  Row 1: [Alice, 25, US, Pro, 99.00]
  Row 2: [Bob, 31, UK, Basic, 29.00]
  Row 3: [Carol, 28, US, Pro, 99.00]

  To compute SUM(revenue): read ALL columns of ALL rows,
                            throw away name/age/country/product.

Column-oriented (Snowflake/BigQuery):
  revenue column: [99.00, 29.00, 99.00, ...]
  country column: [US, UK, US, ...]

  To compute SUM(revenue): read ONLY the revenue column --> much less I/O
  To compute WHERE country='US': read ONLY the country column first

  Also: similar values in a column compress extremely well.
  "US, US, US, UK, US, US..." --> run-length encoding --> tiny on disk.
```

<a id="star-schema-the-standard-dwh-data-model"></a>

## Star Schema — The Standard DWH Data Model

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

```
Star schema visual:

              dim_users
                 |
  dim_products --+-- fact_orders --+-- dim_date
                 |
             dim_geography

  Fact table: center (events, metrics, foreign keys)
  Dimensions: points of the star (descriptive attributes)
  Why "star": the fact table in the center with dimensions radiating out
```

<a id="the-big-three-data-warehouses"></a>

## The Big Three Data Warehouses

```
SNOWFLAKE
  Independent cloud platform (runs on AWS/GCP/Azure)
  Separates storage and compute — scale each independently
  "Virtual warehouses" = compute clusters you spin up on demand
  Excellent SQL support, great for data sharing between organizations
  Pricing: pay per second of compute used

BIGQUERY (GCP)
  Serverless — no clusters to manage, scales automatically
  Pay per query (per TB scanned) — great for intermittent use
  Integrates deeply with Google ecosystem (Looker, Pub/Sub, Dataflow)
  Strongest for: massive datasets, ML integration
  Built-in ML (BigQuery ML) — train models with SQL

REDSHIFT (AWS)
  PostgreSQL-compatible SQL
  Node-based clusters (you provision size upfront — less elastic)
  Redshift Spectrum: query S3 data directly from Redshift
  Strongest for: existing AWS shops, PostgreSQL familiarity

CLICKHOUSE
  Open-source, extreme performance for time-series analytics
  Best for: real-time analytics, event data, log aggregation
  Sub-second queries on billions of rows
  Self-hosted or managed (ClickHouse Cloud)

  "SQL on top of petabytes" — all deliver on this promise.
```

> [↑ Back to Top](#top)

<a id="3-data-lake-raw-storage-first-schema-later"></a>

# 3. Data Lake — Raw Storage First, Schema Later

"A data warehouse is like a library — everything catalogued before anyone reads it," Sekhar says. "A data lake is like a storage unit — throw everything in, figure out organization when you need it. The rent is cheap, and you might need those boxes of papers someday for a question nobody has thought to ask yet."

A **data lake** stores raw, unprocessed data in its native format (JSON, CSV, Parquet, images, logs) at low cost. Schema is applied at query time ("schema on read").

```
Data Lake = Object storage (S3/GCS) full of raw data files

  s3://company-data-lake/
    +-- raw/
    |   +-- postgres/orders/2024-01-15/orders.parquet
    |   +-- postgres/users/2024-01-15/users.parquet
    |   +-- clickstream/2024-01-15/events.json.gz
    |   +-- mobile-logs/2024-01-15/app.log.gz
    +-- curated/
    |   +-- revenue_by_day.parquet
    |   +-- user_cohorts.parquet
    +-- ml-features/
        +-- user_embeddings.parquet

Key properties:
  - Store everything, worry about schema later
  - Parquet format: columnar, compressed, fast for analytics
  - Cheap storage (S3 = $0.023/GB)
  - Query with Spark, Athena, or Hive
```

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

<a id="schema-on-read-vs-schema-on-write"></a>

## Schema on Read vs Schema on Write

```
Schema on Write (Data Warehouse):
  You define the schema BEFORE writing data.
  Bad data is rejected at write time.
  + Queries are fast (data is already clean and structured)
  - Inflexible: schema changes require migrations
  - You must know what questions you'll ask before storing

Schema on Read (Data Lake):
  Write raw data with no schema enforcement.
  Apply schema at query time — interpret bytes when reading.
  + Store anything, figure out structure later
  + Schema can vary per query (different analyses use different views)
  - Raw data is messy — queries do more work
  - "Garbage in, garbage out" — data quality is your problem
```

<a id="data-lakehouse-best-of-both-worlds"></a>

## Data Lakehouse — Best of Both Worlds

```
Delta Lake / Apache Iceberg / Apache Hudi:
  Store data in Parquet on S3 (cheap object storage)
  Add ACID transactions, schema enforcement, time travel
  Query with Spark, Presto, or DuckDB
  Result: data lake economics + data warehouse reliability

Modern answer: "Lakehouse" architecture
  Store in data lake (cheap S3) but add ACID transactions
  and schema enforcement on top. Best of both worlds.
```

> [↑ Back to Top](#top)

<a id="4-etl-vs-elt-when-to-transform"></a>

# 4. ETL vs ELT — When to Transform

"Imagine you are moving houses," Sekhar says. "ETL is like sorting and packing everything perfectly BEFORE the moving truck arrives — takes forever, but the new house is organized on arrival. ELT is like throwing everything into the truck as-is, then unpacking and organizing at the new house which has infinite closet space. Modern cloud warehouses have infinite closet space — so just throw it in and sort there."

Getting data from production systems into the warehouse involves three steps: Extract, Transform, Load. The debate is which order to do them.

**ETL (Extract, Transform, Load):**

```
App DB --> [Extract] --> [Transform server] --> [Load] --> Data Warehouse

Extract:    Pull raw data from PostgreSQL
Transform:  Clean, join, aggregate on a separate server
            (clean bad data, standardize dates, compute metrics)
Load:       Insert processed data into warehouse

Problem:
  The transform server is the bottleneck.
  You have a 1 TB raw data export but a 32-core transform server.
  Transformation takes 6 hours.
  By the time it loads, the data is already stale.
  Adding more compute to the transform server is expensive.

Traditional tools: Informatica, Talend, SSIS
Good when: target DWH has limited compute, or privacy rules require scrubbing first.
```

**ELT (Extract, Load, Transform):**

```
App DB --> [Extract] --> [Load raw] --> Data Warehouse --> [Transform inside]

Extract:    Pull raw data
Load:       Load raw, unprocessed data directly into warehouse
Transform:  Use the warehouse's own massive compute to transform

Why it wins:
  BigQuery/Snowflake have virtually unlimited compute for transformations.
  Transform a 1 TB dataset in minutes using 1000 parallel workers.
  Store raw data forever — re-run transformations if logic changes.
  No separate transform infrastructure to manage.
```

<a id="modern-elt-with-dbt"></a>

## Modern ELT with dbt

**dbt (data build tool)** — write SQL transformations as version-controlled code, run them in the warehouse, document the lineage:

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

```
EL tools (Extract + Load only):
  Fivetran — managed connectors, zero code
  Airbyte — open-source alternative to Fivetran

T tool (Transform in warehouse):
  dbt — SQL-based, version-controlled, tested, documented
```

> [↑ Back to Top](#top)

<a id="5-columnar-file-formats-parquet-and-orc"></a>

# 5. Columnar File Formats — Parquet and ORC

"Parquet is to analytics what JPEG is to images," Sekhar explains. "A raw BMP image is huge but simple. JPEG compresses it intelligently for the way humans see — discarding what does not matter. Parquet does the same for data — compresses and organizes columns for the way analytics queries access them."

**Apache Parquet** is the de-facto standard columnar file format for big data. It stores columns contiguously, supports nested schemas, and achieves 5-10x compression over CSV.

```python
import pandas as pd
import pyarrow as pa
import pyarrow.parquet as pq

# Write Parquet
df = pd.DataFrame({"user_id": [1, 2, 3], "revenue": [10.0, 20.0, 30.0]})
pq.write_table(pa.Table.from_pandas(df), "data.parquet",
               compression="snappy")   # snappy: fast, good ratio

# Read only specific columns (projection pushdown):
table = pq.read_table("data.parquet", columns=["revenue"])

# Read with filter pushdown (skips row groups):
table = pq.read_table("data.parquet",
                      filters=[("revenue", ">", 15.0)])
```

**Parquet internals:**

```
File --> Row Groups --> Columns --> Pages
         (128 MB)                  (1 MB)

Row Group: stores min/max stats per column --> skip entire groups on filter
Column:    stored contiguously --> read only columns you need
Pages:     compressed independently --> partial decompression

Why this matters:
  Query: SELECT AVG(revenue) WHERE country = 'US'
  1. Read row group stats: min(country)='AU', max(country)='US' --> keep
  2. Read ONLY country column pages, find rows matching 'US'
  3. Read ONLY revenue column for those matching rows
  4. Result: read 2% of the file instead of 100%
```

> [↑ Back to Top](#top)

<a id="6-apache-spark-distributed-computation"></a>

# 6. Apache Spark — Distributed Computation

"When your data is too big for one machine," Sekhar says, "you need to split the work across a hundred machines working together. Spark is like a foreman who takes a massive construction project, divides it into a hundred tasks, assigns each to a worker, and combines the results. You write the blueprint once; Spark figures out the parallel execution."

```
Without Spark (single machine):
  Read 1 TB CSV --> RAM cannot hold it --> swap to disk --> 8 hours

With Spark (100-node cluster):
  Split 1 TB across 100 nodes (10 GB each --> fits in RAM)
  Each node processes its partition simultaneously
  Combine results
  --> 5 minutes

Spark is: a framework for writing code that runs in parallel
          across many machines, coordinated automatically.
```

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
Driver        --> coordinates job, breaks into tasks
Executors     --> worker processes on each node
RDD/DataFrame --> distributed dataset partitioned across executors
DAG           --> logical plan of transformations (lazy)
Job --> Stages --> Tasks --> dispatched to executors

Spark on AWS: EMR (managed clusters) or Glue (serverless)
```

<a id="rdds-and-dataframes"></a>

## RDDs and DataFrames

```
RDD (Resilient Distributed Dataset) — low-level, original Spark API:
  A distributed collection of objects across the cluster.
  You write: rdd.filter(...).map(...).groupBy(...)
  Spark figures out how to distribute and execute across nodes.

DataFrame — high-level, SQL-like API (preferred):
  Tabular data with named columns, like a database table.
  Optimized by Spark's Catalyst query optimizer.
  Interoperable with SQL.

Example:
  df = spark.read.parquet("s3://data-lake/orders/")
  result = df.filter(df.year == 2024) \
             .groupBy("country") \
             .agg(sum("revenue").alias("total_revenue")) \
             .orderBy("total_revenue", ascending=False)
  result.write.parquet("s3://output/revenue_by_country/")

  Spark reads from S3, distributes rows across 100 nodes,
  each node filters and aggregates its partition,
  combine phase merges per-node results,
  writes output back to S3.
```

<a id="spark-sql"></a>

## Spark SQL

```
You can write pure SQL against Spark DataFrames:

  df.createOrReplaceTempView("orders")

  result = spark.sql("""
    SELECT country,
           SUM(revenue) as total_revenue,
           COUNT(*) as order_count
    FROM orders
    WHERE year = 2024
      AND status = 'COMPLETED'
    GROUP BY country
    ORDER BY total_revenue DESC
  """)

  Same performance as DataFrame API — Catalyst optimizer treats both identically.
```

<a id="when-spark-vs-when-a-database"></a>

## When Spark vs When a Database

```
Use Spark when:
  - Data is too large for a single machine (> 1 TB typically)
  - Complex transformations (ML feature engineering, graph processing)
  - You need to process data from many sources in one job
  - Batch ETL/ELT pipelines in the data lake
  - Training ML models on large datasets

Use a regular database (or warehouse) when:
  - SQL aggregations on < 1 TB of data in a warehouse
  - Interactive queries (analysts querying ad-hoc)
  - Data already in Snowflake/BigQuery (use their compute instead)
  - You need low-latency results (< 10 seconds) — Spark startup overhead is real

Spark startup overhead:
  Spinning up a Spark cluster: 2-5 minutes
  Bad for: ad-hoc queries where analysts need sub-minute response
  Good for: scheduled batch jobs that process data overnight
```

> [↑ Back to Top](#top)

<a id="7-stream-processing-real-time-pipelines"></a>

# 7. Stream Processing — Real-Time Pipelines

"Batch processing is like washing dishes once a day," Sekhar explains. "Stream processing is washing each dish as soon as it gets dirty. For real-time fraud detection, live dashboards, and instant recommendations, batch is too slow — you need to react to each event within seconds."

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

<a id="batch-vs-stream-decision"></a>

## Batch vs Stream Decision

```
Batch:   hourly/daily jobs, historical analysis, large aggregations
         (Spark, dbt, Airflow DAGs)

Stream:  fraud detection, real-time dashboards, live recommendations,
         event-driven microservices
         (Kafka Streams, Flink, Spark Structured Streaming)

Lambda architecture: run BOTH — stream for low-latency, batch for accuracy
Kappa architecture:  stream only — reprocess history by replaying Kafka

Stream processing decision:

  Situation                         Batch or Stream?
  ────────────────────────────────  ────────────────
  Daily revenue reports             Batch
  Fraud detection on transactions   Stream
  ML model training                 Batch
  Real-time recommendations         Stream
  Month-end billing                 Batch
  Live dashboard for ops team       Stream
  Data warehouse loading            Both (CDC stream + nightly batch)
```

> [↑ Back to Top](#top)

<a id="8-cdc-change-data-capture"></a>

# 8. CDC — Change Data Capture

"When 10 services all need to know when a user updates their profile," Sekhar says, "polling the database 10 times is wasteful and creates load. CDC is like having a security camera on the database — it watches the write-ahead log and broadcasts every change to all interested parties, without the database lifting a finger."

**Change Data Capture** reads the database write-ahead log (WAL) and emits every insert, update, and delete as an event.

```
PostgreSQL WAL --> Debezium --> Kafka topic --> downstream consumers
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
- Feed microservices without coupling them to the source DB

```
CDC pipeline flow:

  Source DB (Postgres)
       |
       | Write-Ahead Log (WAL)
       v
  Debezium Connector (reads WAL, emits events)
       |
       v
  Kafka Topic (users.changes)
       |
       +-----> Elasticsearch (update search index)
       +-----> Redis (invalidate cache)
       +-----> Data Warehouse (near-real-time sync)
       +-----> Analytics Service (update dashboards)

  No polling. No load on source DB. Sub-second latency.
```

> [↑ Back to Top](#top)

<a id="9-the-modern-data-stack"></a>

# 9. The Modern Data Stack

"Here is how all the pieces fit together," Sekhar draws on the whiteboard. "This is what a mid-to-large company's data pipeline looks like when done right."

```
THE MODERN DATA PIPELINE

  ┌──────────────────────────────────────────────────────────────┐
  │                    Source Systems                            │
  │  [App DB (Postgres)] [Mobile Events] [Third-party APIs]      │
  └────────────┬──────────────────┬──────────────────┬───────────┘
               │                  │                  │
              CDC               Kafka             Fivetran/
           (Debezium)          streams            Airbyte
               │                  │                  │
               └──────────────────┼──────────────────┘
                                  │
                         ┌────────v────────┐
                         │      Kafka       │
                         │  (event stream   │
                         │   backbone)      │
                         └────────┬────────┘
                                  │
                    ┌─────────────┼────────────────┐
                    │             │                │
             ┌──────v──────┐  ┌──v────────┐  ┌───v────────┐
             │    Flink    │  │  S3/GCS   │  │ Spark      │
             │  (real-time │  │(data lake │  │(batch ETL  │
             │  processing)│  │ raw dump) │  │ overnight) │
             └──────┬──────┘  └──────────┘  └────┬───────┘
                    │                             │
                    └──────────────┬──────────────┘
                                   │
                         ┌─────────v─────────┐
                         │   Data Warehouse   │
                         │  (Snowflake /      │
                         │   BigQuery /       │
                         │   Redshift)        │
                         └─────────┬─────────┘
                                   │ dbt transforms
                                   │ (version-controlled SQL)
                         ┌─────────v─────────┐
                         │     BI Tools       │
                         │   (Tableau, Looker │
                         │    Metabase, Mode) │
                         └───────────────────┘

COMPONENT RESPONSIBILITIES:
  Debezium/CDC:   Capture every DB change as an event (no polling)
  Kafka:          Buffer and distribute event streams reliably
  Flink/Spark:    Process events (real-time or batch)
  S3 Data Lake:   Store raw events forever (cheap, schema-on-read)
  Warehouse:      Clean, modeled data for business intelligence
  dbt:            Version-controlled SQL transformations
  BI Tool:        Dashboards and ad-hoc queries for non-engineers
```

```
Sekhar's mental models for data systems:

  1. OLTP and OLAP are different paradigms, not just different sizes.
     Never run heavy analytics on your production operational database.

  2. Data warehouses are columnar and denormalized.
     JOINs at query time are expensive. Pre-join at load time instead.

  3. ELT over ETL — load raw data, transform inside the warehouse.
     Cloud compute is cheap. Bottleneck transform servers are not.

  4. Data lake = cheap raw storage (S3 + Parquet).
     Warehouse = structured, modeled data for business questions.
     They are complementary, not competing.

  5. Spark = distributed computation. Use when data > 1 machine capacity.
     Do not use Spark for small data — overhead outweighs benefit.

  6. Stream processing = process as events arrive.
     Batch processing = process data in scheduled chunks.
     Most mature systems need both.
```

> [↑ Back to Top](#top)

<a id="summary"></a>

## 🔥 Summary

```
Data Systems at a Glance:

  Component          Purpose                        Key Tool
  ────────────────   ─────────────────────────────  ──────────────────
  OLTP Database      Live app transactions          PostgreSQL, MySQL
  OLAP Warehouse     Business analytics             Snowflake, BigQuery
  Data Lake          Raw storage, ML exploration    S3 + Parquet
  Lakehouse          Lake + warehouse guarantees    Delta Lake, Iceberg
  ETL/ELT            Move data to warehouse         dbt, Fivetran, Airbyte
  Batch Processing   Large-scale transforms         Apache Spark, Airflow
  Stream Processing  Real-time event handling       Kafka Streams, Flink
  CDC                DB change broadcasting         Debezium

Sekhar's golden rules:
  1. Never run analytics on your production database
  2. Column-oriented storage wins for analytical queries
  3. ELT beats ETL when your warehouse has elastic compute
  4. Store raw data forever in the lake — you will need it
  5. CDC eliminates polling and decouples consumers from producers
  6. Most systems need BOTH batch and stream — plan for both from day one
```

## Mini Exercises

**1.** Your startup's analytics team complains that their reports are causing
production slowdowns. You have one PostgreSQL database. What is your
30-day plan to fix this? What is the architecture change?

**2.** You need to answer: "Which users who signed up in January are still
active 90 days later?" Is this an OLTP or OLAP query? Where would you
run it, and why?

**3.** Your company stores 200 GB of S3 event logs (JSON format) from the
past 3 years. You need to run monthly analysis on them. Compare: (a) Spark
on a 10-node cluster, (b) Amazon Athena (SQL on S3), (c) loading into
BigQuery. What factors drive the choice?

**4.** A data engineer proposes: "Let's ETL everything nightly into the
warehouse — transform on a dedicated EC2 cluster before loading."
What is the modern alternative? What are the trade-offs of each?

**5.** You are designing a data pipeline for a new e-commerce platform.
Draw the flow from app database to BI dashboard. Which components
would you include? Justify your choices for CDC vs polling, batch vs
stream, and warehouse selection.

```
Common mistakes Sekhar sees in data systems interviews:

  WRONG: "We'll just add read replicas for analytics"
  WHY:   Read replicas are row-oriented. Analytics needs columnar.
         Also, replication lag means inconsistent reports.

  WRONG: "We'll use Spark for everything"
  WHY:   Spark startup overhead is 2-5 minutes.
         For sub-10-second queries, use the warehouse directly.

  WRONG: "Data lake and data warehouse are the same thing"
  WHY:   Lake = raw storage, schema-on-read, cheap.
         Warehouse = modeled data, schema-on-write, fast queries.
         They complement each other.

  WRONG: "We poll the database every 5 seconds for changes"
  WHY:   Polling creates load on the source DB and has latency.
         CDC reads the WAL — zero load, sub-second latency.
```

## 📂 Navigation

| | |
|---|---|
| 📘 README | [Back to System Design README](../README.md) |

| ⬅ Previous | ➡ Next |
|---|---|
| [19 — Clean Architecture](../19_clean_architecture/theory.md) | [21 — Real-Time Systems](../21_real_time_systems/theory.md) |

**This folder:** [theory.md](./theory.md) | [cheetsheet.md](./cheetsheet.md) | [interview.md](./interview.md) | [practice_local.py](./practice_local.py) | [data_at_scale.md](./data_at_scale.md)

**Related modules:** [05 — Databases](../05_databases/theory.md) | [09 — Message Queues](../09_message_queues/theory.md) | [11 — Scalability Patterns](../11_scalability_patterns/theory.md) | [21 — Real-Time Systems](../21_real_time_systems/theory.md)

**Jump to topics:** [Star Schema](#star-schema-the-standard-dwh-data-model) | [Spark Execution](#6-apache-spark-distributed-computation) | [CDC Pipeline](#8-cdc-change-data-capture) | [Modern Data Stack](#9-the-modern-data-stack)
