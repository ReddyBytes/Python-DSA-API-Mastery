# 14 — Seeing Your System: Observability

---

## The Problem

It's 2am. Your phone is ringing. Users are tweeting that your app is broken. Your CEO sends a Slack message. Payment processing is failing.

You open your laptop.

Where do you look?

If you don't have observability set up, the answer is: you guess. You SSH into a server and run `top`. You tail some logs from one machine. You restart things and hope. You're flying blind.

**Observability is the ability to understand what your system is doing, from the outside, by examining its outputs.**

The key insight: you cannot fix what you cannot see. All the architecture in the world is worthless if you can't tell when it's broken and why.

---

## The Three Pillars of Observability

There are three complementary ways to observe a running system. They answer different questions.

```
                    THE THREE PILLARS

    METRICS              LOGS                 TRACES
    ─────────────────    ──────────────────    ──────────────────────
    Numbers over time    Text records          Journey of one request

    "CPU is at 94%"      "ERROR: payment       "Request took 2.3s:
    "500 req/sec"         failed for user 42     API GW: 10ms
    "p99 = 800ms"         at 2024-01-01 03:14"   Auth: 5ms
                                                  Payment: 2200ms ← slow
    Answers:             Answers:               Answers:
    "Is something        "What happened?"       "WHERE is it slow?"
     wrong?"             "What exactly          "Which service is
    "How bad is it?"      went wrong?"           the bottleneck?"
```

You need all three. Metrics tell you something is wrong. Logs tell you what. Traces tell you where.

---

## Pillar 1: Metrics

A metric is a number measured over time. CPU percentage. Requests per second. Error rate. Memory used. Queue depth.

### Prometheus and Grafana

The most common open-source stack for metrics:

- **Prometheus** — scrapes metrics from your services and stores them as time-series data.
- **Grafana** — dashboards and visualization on top of Prometheus (and other sources).

```
HOW PROMETHEUS WORKS:

    Your Service exposes a /metrics endpoint:
        GET /metrics
        → http_requests_total{method="GET", status="200"} 15234
        → http_requests_total{method="POST", status="500"} 42
        → http_request_duration_seconds{quantile="0.99"} 0.82

    Prometheus scrapes this every 15 seconds.
    Stores it: (timestamp, value) pairs.

    Grafana queries Prometheus: "give me http_requests_total over the last hour"
    Grafana renders a graph.
```

### Metric Types

```
COUNTER:
    Only goes up. Resets to 0 on restart.
    Use for: total requests, total errors, total bytes sent
    Example: http_requests_total = 15234

    Useful as a rate: "how many requests per second right now?"
    PromQL: rate(http_requests_total[5m])  ← requests per second over last 5 mins

GAUGE:
    Can go up or down. Current snapshot value.
    Use for: current CPU%, current memory usage, current queue depth
    Example: active_connections = 247
             memory_usage_bytes = 4831838208

HISTOGRAM:
    Samples observations into buckets. Lets you compute percentiles.
    Use for: request latency, request size
    Example:
        http_request_duration_seconds_bucket{le="0.1"}  = 8500   (8500 requests ≤ 100ms)
        http_request_duration_seconds_bucket{le="0.5"}  = 14200  (14200 requests ≤ 500ms)
        http_request_duration_seconds_bucket{le="1.0"}  = 14900
        http_request_duration_seconds_bucket{le="+Inf"} = 15000

    From this: p50 ≈ 100ms, p99 ≈ 950ms
```

### The RED Method

For every service you run, track these three metrics:

```
RED:
    R — Rate:    Requests per second (how much traffic?)
    E — Errors:  Error rate (is it failing?)
    D — Duration: Response latency distribution (is it slow?)

These three cover 90% of "is this service healthy?" questions.

On your dashboard, for every service:
    ┌─────────────────────────────────────────┐
    │ Payment Service                          │
    │                                          │
    │ Rate:     1,240 req/min  ← normal        │
    │ Errors:   0.02%          ← normal        │
    │ p50:      45ms           ← normal        │
    │ p99:      820ms          ← hmm, high     │
    └─────────────────────────────────────────┘
```

### SLO Alerting

Don't alert on symptoms ("CPU is high"). Alert on user impact.

```
SLO ALERT EXAMPLE:
    "If the 99th percentile latency of the payment service
     exceeds 500ms for more than 5 consecutive minutes,
     page the on-call engineer."

Why p99 and not average?
    Average hides tail latency.
    Average: 50ms (looks fine)
    p99: 3000ms  (1% of users waiting 3 seconds — real pain)

Why "5 consecutive minutes" and not "any single spike"?
    Spikes happen. Brief ones don't warrant waking someone up at 3am.
    Sustained degradation does.
```

---

## Pillar 2: Logs

Logs are the text record of events in your system. They're the most familiar form of observability — everyone has used `print()` or `console.log()` for debugging.

At scale, logs need more discipline than that.

### Structured Logging (JSON)

Plain text logs are hard to query.

```
UNSTRUCTURED (hard to query):
    2024-01-01 03:14:22 ERROR payment failed for user 42 amount=100 reason=card_declined

STRUCTURED JSON (easy to query):
    {
      "timestamp": "2024-01-01T03:14:22Z",
      "level": "ERROR",
      "service": "payment-service",
      "event": "payment_failed",
      "user_id": 42,
      "amount": 100,
      "reason": "card_declined",
      "trace_id": "abc-123-xyz"   ← we'll return to this
    }
```

With structured logs, you can query:
- "Show me all ERROR events in the last hour"
- "Show me all payments that failed for user 42 in the last week"
- "How many card_declined events per minute over the last 24 hours?"

### Log Levels

Not every log message has the same urgency:

```
DEBUG:   Verbose, detailed. Only enable in development or specific debugging.
         "Entering function processPayment with args: {user_id: 42, amount: 100}"

INFO:    Normal operational events.
         "Payment processed successfully: order_id=9981, amount=$42.00"

WARN:    Something unexpected but not fatal. Worth investigating.
         "Payment retry attempt 2/3 for order_id=9981"

ERROR:   Something failed. Needs attention.
         "Payment failed after 3 retries: order_id=9981, reason=card_declined"

FATAL:   Service is crashing. Immediate attention.
         "Database connection pool exhausted, shutting down"
```

In production, log at INFO level and above. Never log passwords, tokens, or card numbers.

### Log Aggregation — The ELK Stack

With 50 microservices each running 3 instances, you have 150 places where logs are being written. You can't SSH to each one.

The ELK Stack (Elasticsearch, Logstash, Kibana) is a common solution:

```
[Service A instances]  ┐
[Service B instances]  ├──▶ [Logstash / Fluentd]  ──▶  [Elasticsearch]  ──▶  [Kibana]
[Service C instances]  ┘    (collect & transform)        (store & index)        (query & visualize)

You query Kibana:
    - "Show me all ERROR logs across all services in the last 10 minutes"
    - "Show me all logs with trace_id = 'abc-123-xyz'"  ← follows a single request
    - "How many database timeout errors per service per hour?"
```

Alternatives: Grafana Loki (cheaper, simpler), Datadog, Splunk, CloudWatch.

---

## Pillar 3: Distributed Tracing

Here's a request flow in a microservices system:

```
User's request:
    Browser → API Gateway → Auth Service → Product Service → Price Service → DB
        10ms       2ms           8ms            45ms           200ms       3ms

Total: ~268ms

User sees: 268ms response time.

Which part is slow? You can't tell from metrics alone.
    Metrics say: Product Service p99 = 250ms  ← but that's the WHOLE request.
    You need to know which hop took how long.

Answer: Distributed Tracing.
```

### Trace ID and Spans

When a request enters your system, assign it a **Trace ID** — a unique identifier that follows it everywhere.

Each service's contribution is called a **Span**.

```
REQUEST: trace_id = "abc-123-xyz"

    ┌──────────────────────────────────────────────────────────────────┐
    │ TRACE: abc-123-xyz                                               │
    │                                                                  │
    │ [API Gateway          ]  0ms ──────────────────── 268ms         │
    │   [Auth Service   ]      2ms ────────── 10ms                    │
    │   [Product Service                   ]  12ms ──────── 250ms     │
    │     [Price Service  ]                   12ms ──── 57ms          │
    │     [DB Query       ]                            60ms ── 63ms   │
    └──────────────────────────────────────────────────────────────────┘

Immediately clear: Product Service spent 238ms total.
Of that, Price Service took 45ms and DB took 3ms.
So Product Service itself took: 238 - 45 - 3 = 190ms internally. ← investigate here.
```

### How Trace IDs Propagate

```
API Gateway:
    - Generates trace_id = "abc-123-xyz"
    - Starts a span
    - Calls Auth Service:
        HTTP header: X-Trace-ID: abc-123-xyz

Auth Service:
    - Receives X-Trace-ID header
    - Starts its own span (child of API Gateway's span)
    - Does its work
    - Ends its span (records: start_time, end_time, service_name, trace_id)
    - Sends its span to the tracing backend

(Same for every subsequent service)

Tracing Backend (Jaeger, Zipkin):
    - Receives all spans
    - Groups them by trace_id
    - Renders the waterfall diagram above
```

### Tools

- **Jaeger** — open source, created by Uber, CNCF project
- **Zipkin** — open source, created by Twitter
- **Honeycomb, Datadog, Tempo** — commercial or cloud-native options

The key is instrumentation: your services need to be set up to generate spans and propagate trace IDs. Libraries like OpenTelemetry provide vendor-neutral instrumentation.

---

## SLO / SLA / SLI — A Quick Reminder

(Covered in depth in Chapter 02. A brief recap so it connects to alerting.)

```
SLI (Service Level Indicator):
    The metric you're measuring.
    Example: "99th percentile API response latency"

SLO (Service Level Objective):
    Your internal target for that metric.
    Example: "p99 latency should be < 300ms for 99.9% of minutes in a month"

SLA (Service Level Agreement):
    Your contractual commitment to customers.
    Example: "We guarantee 99.9% uptime. If we miss it, you get service credits."

Relationship:
    SLI tells you what happened.
    SLO tells you what you aim for.
    SLA tells you what you've promised.

    SLO should be stricter than SLA — if your SLO fires, you can fix it
    before breaching the SLA.
```

---

## Alerting — When to Wake Someone Up

Not every anomaly deserves a 3am page. Alert fatigue is real: if engineers get paged too often for false alarms, they start ignoring pages. That's when real incidents go unnoticed.

### Rules for Good Alerts

```
Good alert:
    ✓ User-facing impact (or imminent impact)
    ✓ Actionable: the on-call person knows what to do
    ✓ Not self-resolving: it won't fix itself in 30 seconds

Bad alert:
    ✗ "CPU spike for 20 seconds" (almost always self-resolving)
    ✗ "Memory at 85%" (not necessarily a problem on its own)
    ✗ Noise from flapping services (alert, recover, alert, recover...)
    ✗ Anything where the response is "wait and see"
```

### Tiers of Response

```
PAGE (wake someone up):
    - Payment success rate dropped below 95%
    - Error rate > 5% sustained for > 5 minutes
    - Database replication lag > 60 seconds
    - Service completely down

TICKET (fix during business hours):
    - p99 latency elevated but within SLO
    - Cache hit rate declining gradually
    - Disk usage approaching 80% (days away from full)

DASHBOARD (visible, no action required):
    - Normal traffic patterns
    - Expected background error rates
    - Routine metrics
```

### Runbooks

When an alert fires, the on-call engineer should not have to figure out what to do from scratch. A **runbook** is a document that says:

- What does this alert mean?
- What are the likely causes?
- What are the first steps to diagnose?
- What are the steps to remediate each cause?
- Who else to page if you can't fix it?

Good runbooks are the difference between a 10-minute incident and a 2-hour one.

---

## The Stack, Visualized

```
YOUR DISTRIBUTED SYSTEM:
    [Service A]   [Service B]   [Service C]   [DB]
        |              |              |          |
        | metrics       | metrics      | metrics  |
        | logs          | logs         | logs     |
        | spans         | spans        | spans    |
        |              |              |          |
        v              v              v          v
    ┌─────────────────────────────────────────────────┐
    │              OBSERVABILITY PLATFORM             │
    │                                                 │
    │  [Prometheus]    [Elasticsearch]   [Jaeger]     │
    │  (metrics store) (log store)       (trace store)│
    │       |                |               |        │
    │       v                v               v        │
    │                   [Grafana]                     │
    │           (unified dashboards, alerting)        │
    └─────────────────────────────────────────────────┘
                            |
                            v
                    [PagerDuty / OpsGenie]
                    (on-call routing, escalation)
                            |
                            v
                    [On-Call Engineer]
                    (with a runbook and a coffee)
```

---

## The Key Rule

> You cannot fix what you cannot see.

No amount of good architecture saves you when you're debugging a production incident blind. Observability isn't an afterthought. It's infrastructure. Build it before you need it, because when you need it, you really need it.

---

## Quick Reference

| Tool       | Pillar  | What it does                                               |
|------------|---------|------------------------------------------------------------|
| Prometheus | Metrics | Scrapes and stores time-series metrics                     |
| Grafana    | Metrics | Dashboards and alerting on top of metrics                  |
| ELK Stack  | Logs    | Aggregate, index, and query logs from all services         |
| Loki       | Logs    | Lighter-weight log aggregation (Grafana Labs)              |
| Jaeger     | Traces  | Distributed tracing — visualize request flows              |
| Zipkin     | Traces  | Alternative distributed tracing (Twitter-origin)           |
| OpenTelemetry | All  | Vendor-neutral instrumentation SDK (metrics, logs, traces) |
| PagerDuty  | Alerting| On-call routing and escalation                             |

---

## Navigation

| Direction | Link |
|-----------|------|
| Previous  | [13 — Security](../13_security/security_fundamentals.md) |
| Next      | [15 — Cloud Architecture](../15_cloud_architecture/theory.md) |
| Home      | [README.md](../README.md) |
