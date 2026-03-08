# When Your Data Outgrows Your Database
## A Practical Guide to Data Systems at Scale

> Your app's PostgreSQL database works perfectly at 10,000 users.
> At 10 million users, the CEO asks: "Why did we lose $400K last quarter?"
> The analyst runs a query. It takes 4 hours. Production slows to a crawl.
> You have just discovered the difference between OLTP and OLAP.

---

## Part 1: OLTP vs OLAP — Two Completely Different Worlds

These are not just different databases. They are different philosophies
for how data should be organized and accessed.

### OLTP: Your App's Operational Database

OLTP stands for Online Transaction Processing. This is the database your
application reads and writes during normal operation.

```
OLTP characteristics:

  Query pattern:    "Get user 12345's profile"
                    "Update order 98765's status to SHIPPED"
                    "Insert new payment record for Alice"
                    → Operates on individual rows

  Latency goal:     Milliseconds (your users are waiting)
  Write frequency:  Very high (every user action = writes)
  Data shape:       Normalized (3NF) — minimize redundancy
  Scale:            Thousands to millions of rows changed per hour
  Examples:         PostgreSQL, MySQL, SQL Server

  ┌──────────────────────────────────────────────┐
  │  users table                                 │
  │  id | name  | email           | joined       │
  │   1 | Alice | alice@email.com | 2023-01-15   │
  │   2 | Bob   | bob@email.com   | 2023-02-20   │
  │                                              │
  │  Query: SELECT * FROM users WHERE id = 1     │
  │  → returns 1 row, instantly                  │
  └──────────────────────────────────────────────┘
```

### OLAP: The Analytics Database

OLAP stands for Online Analytical Processing. This is what you use to
answer business questions by aggregating millions of rows.

```
OLAP characteristics:

  Query pattern:    "What was our revenue by country last quarter?"
                    "Which features correlate with user retention?"
                    "Show me DAU by cohort for the past 6 months"
                    → Scans millions of rows, aggregates heavily

  Latency goal:     Seconds to minutes (analysts are waiting, not users)
  Write frequency:  Low (data loaded in batches or streams)
  Data shape:       Denormalized (star/snowflake schema) — optimize reads
  Scale:            Billions to trillions of rows scanned per query
  Examples:         BigQuery, Snowflake, Redshift, ClickHouse

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
  │  → scans 500M rows, returns 50 rows, takes 10 seconds    │
  └──────────────────────────────────────────────────────────┘
```

### Why You Cannot Run Analytics on Your Production Database

This is the core insight. It seems convenient to just run reports on
the same PostgreSQL database your app uses. Here is what happens:

```
Production PostgreSQL database:
  10,000 users making requests per second
  App queries: < 5ms (index lookups, simple reads)

Analyst runs: SELECT COUNT(*), AVG(revenue) FROM orders
              WHERE created_at > '2024-01-01' GROUP BY product_id

  → Full table scan: locks buffer pool with 200M rows
  → Evicts cached hot data from shared_buffers
  → App queries suddenly taking 2-3 seconds instead of 5ms
  → Users see slow page loads
  → On-call engineer gets paged at 2 AM
  → Analyst wonders why everyone is upset

The fix: send analytics queries to a system designed for them.
```

---

## Part 2: The Data Warehouse

A data warehouse is a database built specifically for analytical queries.
It stores historical data from your production systems, organized for
fast aggregation.

### Why It's Separate

```
Production DB:                    Data Warehouse:
  Normalized data                   Denormalized (pre-joined) data
  Row-oriented storage              Column-oriented storage
  Optimized for writes              Optimized for reads
  ACID transactions                 Eventual consistency ok
  GBs to low TBs                    TBs to PBs
  Updated continuously              Updated in batch (hourly/daily)
  Cannot be touched by analysts     Built for analysts
```

### Column-Oriented Storage: The Secret Weapon

Traditional databases store data row by row. Data warehouses store it
column by column. This makes a huge difference for analytics:

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

  To compute SUM(revenue): read ONLY the revenue column → much less I/O
  To compute WHERE country='US': read ONLY the country column first

  Also: similar values in a column compress extremely well.
  "US, US, US, UK, US, US..." → run-length encoding → tiny on disk.
```

### The Big Three Data Warehouses

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

REDSHIFT (AWS)
  PostgreSQL-compatible SQL
  Node-based clusters (you provision size upfront — less elastic)
  Redshift Spectrum: query S3 data directly from Redshift
  Strongest for: existing AWS shops, PostgreSQL familiarity

  "SQL on top of petabytes" — all three deliver on this promise.
```

---

## Part 3: ETL vs ELT

Getting data from production systems into the warehouse involves three
steps: Extract, Transform, Load. The debate is which order to do them.

### Traditional ETL: Transform Before Loading

```
App DB → [Extract] → [Transform server] → [Load] → Data Warehouse

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
```

### Modern ELT: Load Raw, Transform in the Warehouse

```
App DB → [Extract] → [Load raw] → Data Warehouse → [Transform inside]

Extract:    Pull raw data
Load:       Load raw, unprocessed data directly into warehouse
Transform:  Use the warehouse's own massive compute to transform

Why it wins:
  BigQuery/Snowflake have virtually unlimited compute for transformations.
  Transform a 1 TB dataset in minutes using 1000 parallel workers.
  Store raw data forever — re-run transformations if logic changes.
  No separate transform infrastructure to manage.

Tools:
  dbt (data build tool): write SQL transformations as version-controlled
  code, run them in the warehouse, document the lineage
  Fivetran/Airbyte: managed EL tools (Extract + Load, no transform)
```

---

## Part 4: The Data Lake

A data lake is simpler to describe and harder to use well.

### What It Is

```
Data Lake = Object storage (S3/GCS) full of raw data files

  s3://company-data-lake/
    ├── raw/
    │   ├── postgres/orders/2024-01-15/orders.parquet
    │   ├── postgres/users/2024-01-15/users.parquet
    │   ├── clickstream/2024-01-15/events.json.gz
    │   └── mobile-logs/2024-01-15/app.log.gz
    ├── curated/
    │   ├── revenue_by_day.parquet
    │   └── user_cohorts.parquet
    └── ml-features/
        └── user_embeddings.parquet

Key properties:
  - Store everything, worry about schema later
  - Parquet format: columnar, compressed, fast for analytics
  - Cheap storage (S3 = $0.023/GB)
  - Query with Spark, Athena, or Hive
```

### Schema on Read vs Schema on Write

This distinction defines the lake vs warehouse philosophical difference:

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

Modern answer: "Lakehouse" architecture (Delta Lake, Apache Iceberg)
  Store in data lake (cheap S3) but add ACID transactions and schema
  enforcement on top. Best of both worlds.
```

---

## Part 5: Stream Processing (Overview)

When you cannot wait for nightly batch jobs, you process data as it arrives.
Stream processing is covered in depth in `21_real_time_systems` — this is
the data engineering view.

```
Batch processing:
  "Every night at 2 AM, load yesterday's data into the warehouse."
  Latency: 24 hours from event to insight.
  Acceptable for: daily reports, monthly billing, archive analytics.

Stream processing:
  "Process each event within seconds of it occurring."
  Latency: sub-second to seconds.
  Required for: fraud detection, live dashboards, real-time recommendations.

The pipeline:

  App DB ──(CDC)──→ Kafka ──→ Flink/Spark Streaming ──→ Data Store
                     │                                    (Redis, DynamoDB,
                     │                                     warehouse, search)
                     └──(raw events)──→ Data Lake (S3)

  CDC = Change Data Capture: captures every row change in the DB as an event
        Tools: Debezium (open source), AWS DMS
        Instead of polling the DB, you stream the changes
```

---

## Part 6: Apache Spark — Distributed Computation Over Huge Datasets

When your data is too big for one machine to process, Spark distributes
the computation across a cluster.

### The Core Idea

```
Without Spark (single machine):
  Read 1 TB CSV → RAM cannot hold it → swap to disk → 8 hours

With Spark (100-node cluster):
  Split 1 TB across 100 nodes (10 GB each → fits in RAM)
  Each node processes its partition simultaneously
  Combine results
  → 5 minutes

Spark is: a framework for writing code that runs in parallel
          across many machines, coordinated automatically.
```

### RDDs and DataFrames

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

### Spark SQL

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

### When Spark vs When a Regular Database

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

---

## Part 7: The Modern Data Stack

Here is how the pieces fit together in a complete data pipeline at a
mid-to-large company:

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
                         ┌────────▼────────┐
                         │      Kafka       │
                         │  (event stream   │
                         │   backbone)      │
                         └────────┬────────┘
                                  │
                    ┌─────────────┼────────────────┐
                    │             │                │
             ┌──────▼──────┐  ┌──▼────────┐  ┌───▼────────┐
             │    Flink    │  │  S3/GCS   │  │ Spark      │
             │  (real-time │  │(data lake │  │(batch ETL  │
             │  processing)│  │ raw dump) │  │ overnight) │
             └──────┬──────┘  └──────────┘  └────┬───────┘
                    │                             │
                    └──────────────┬──────────────┘
                                   │
                         ┌─────────▼─────────┐
                         │   Data Warehouse   │
                         │  (Snowflake /      │
                         │   BigQuery /       │
                         │   Redshift)        │
                         └─────────┬─────────┘
                                   │ dbt transforms
                                   │ (version-controlled SQL)
                         ┌─────────▼─────────┐
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

---

## The Mental Models to Keep

```
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

---

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

---

## Navigation

| | |
|---|---|
| Previous | [19 — Clean Architecture](../19_clean_architecture/theory.md) |
| Next | [21 — Real-Time Systems](../21_real_time_systems/theory.md) |
| Home | [README.md](../README.md) |
