<a id="top"></a>

# 14 — Observability

> Know what your system is doing in production — metrics, tracing, logging, and alerting for reliable systems.

## Table of Contents

- [1. The Three Pillars of Observability](#1-the-three-pillars-of-observability)
- [2. Metrics](#2-metrics)
  - [Prometheus and Grafana](#prometheus-and-grafana)
  - [Metric Types](#metric-types)
  - [The RED Method](#the-red-method)
  - [SLO Alerting](#slo-alerting)
- [3. Logs](#3-logs)
  - [Structured Logging (JSON)](#structured-logging-json)
  - [Log Levels](#log-levels)
  - [Log Aggregation — The ELK Stack](#log-aggregation--the-elk-stack)
- [4. Distributed Tracing](#4-distributed-tracing)
  - [Trace ID and Spans](#trace-id-and-spans)
  - [How Trace IDs Propagate](#how-trace-ids-propagate)
  - [Tracing Tools](#tracing-tools)
- [5. SLO, SLA, and SLI](#5-slo-sla-and-sli)
- [6. Alerting](#6-alerting)
  - [Rules for Good Alerts](#rules-for-good-alerts)
  - [Tiers of Response](#tiers-of-response)
  - [Runbooks](#runbooks)
- [7. The Observability Stack](#7-the-observability-stack)
- [8. Quick Reference](#8-quick-reference)
- [Learning Priority](#learning-priority)
- [Summary](#summary)
- [Navigation](#navigation)

## Learning Priority

**Must Learn** — Core concept, daily use, interview essential:
three pillars (metrics/traces/logs), distributed tracing (spans/trace context), SLO and error budget concepts

**Should Learn** — Important for real projects, comes up regularly:
metrics types (counter/gauge/histogram), structured log correlation, alerting thresholds

**Good to Know** — Useful in specific situations, not always tested:
OpenTelemetry instrumentation, Grafana query basics, ELK stack overview

**Reference** — Know it exists, look up syntax when needed:
metric cardinality explosion, sampling strategies, alert fatigue management

<a id="1-the-three-pillars-of-observability"></a>

# 1. The Three Pillars of Observability

Kavya's phone rings at 2am. Users are tweeting that the app is broken. Her CEO sends a Slack message. Payment processing is failing. She opens her laptop and asks herself one question: where do I look?

If you don't have observability set up, the answer is: you guess. You SSH into a server and run `top`. You tail some logs from one machine. You restart things and hope. You're flying blind.

**Observability is the ability to understand what your system is doing, from the outside, by examining its outputs.**

The key insight: you cannot fix what you cannot see. All the architecture in the world is worthless if you can't tell when it's broken and why.

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

```
Kavya's analogy — the hospital:

    METRICS  = vital signs monitor (heart rate, blood pressure, O2)
               → tells you "patient is deteriorating"

    LOGS     = nurse's handwritten notes ("Patient complained of
               chest pain at 3:14am, administered aspirin")
               → tells you "what happened and when"

    TRACES   = the full patient journey through the hospital
               (ER → triage → X-ray → cardiology → ICU)
               → tells you "where did they get stuck / slow down?"
```

> 📝 **Practice:** [Q63 - observability-pillars](../system_design_practice_questions_100.md#q63--normal--observability-pillars)

> [↑ Back to Top](#top)

<a id="2-metrics"></a>

# 2. Metrics

Kavya thinks of metrics like the dashboard gauges in her car. She doesn't need to know every detail of the engine's internal combustion cycle — she just glances at the speedometer, fuel gauge, and temperature needle. If any of them look wrong, she knows to pull over and investigate.

A metric is a number measured over time. CPU percentage. Requests per second. Error rate. Memory used. Queue depth.

<a id="prometheus-and-grafana"></a>

## Prometheus and Grafana

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

```
Kavya's mental model — pull vs push:

    PULL (Prometheus):
        Prometheus → "Hey service, give me your metrics"
        Service    → "Here you go: {cpu: 42%, reqs: 1200/s}"

        Advantage: Prometheus controls the pace. If a service is down,
                   Prometheus notices immediately (scrape fails).

    PUSH (StatsD, Datadog Agent):
        Service    → "Here are my metrics" → Collector
        Service    → "Here are my metrics" → Collector

        Advantage: Works for short-lived jobs (batch, lambda).
```

<a id="metric-types"></a>

## Metric Types

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

```
Kavya's cheat sheet — when to use which type:

    ┌──────────────────────────────────────────────────────────────┐
    │  "How many total X?"           → COUNTER                     │
    │  "What is the current X?"      → GAUGE                       │
    │  "How long does X take?"       → HISTOGRAM                   │
    │  "What's the distribution?"    → HISTOGRAM (or SUMMARY)      │
    └──────────────────────────────────────────────────────────────┘

    Common mistake: using a GAUGE for total requests.
    Why wrong: if the service restarts, a gauge resets to 0
    and you lose continuity. A counter resets too, but
    rate() handles counter resets correctly.
```

<a id="the-red-method"></a>

## The RED Method

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

```
Related frameworks Kavya keeps on her wall:

    RED  (request-driven services):   Rate, Errors, Duration
    USE  (infrastructure resources):  Utilization, Saturation, Errors
    LETS (Google SRE):                Latency, Errors, Traffic, Saturation

    ┌──────────────────────────────────────────────────────┐
    │  Monitoring a web API?    → RED                       │
    │  Monitoring a CPU/disk?   → USE                       │
    │  Building SLOs?           → LETS (aka "Four Golden    │
    │                              Signals" from Google SRE) │
    └──────────────────────────────────────────────────────┘
```

<a id="slo-alerting"></a>

## SLO Alerting

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

> [↑ Back to Top](#top)

<a id="3-logs"></a>

# 3. Logs

Kavya compares logs to a handwritten diary of events. Every time something happens — a user logs in, a payment processes, an error occurs — the system writes it down with a timestamp. At scale, 50 microservices each running 3 instances means 150 diaries being written simultaneously. You need a way to collect, search, and correlate them.

Logs are the text record of events in your system. They're the most familiar form of observability — everyone has used `print()` or `console.log()` for debugging. At scale, logs need more discipline than that.

<a id="structured-logging-json"></a>

## Structured Logging (JSON)

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

```
Kavya's rule of thumb — what to include in every log line:

    ALWAYS:   timestamp, level, service name, event name, trace_id
    USUALLY:  user_id, request_id, relevant IDs
    NEVER:    passwords, tokens, credit card numbers, PII (GDPR!)

    Common mistake: logging the full request body.
    Why wrong: request bodies contain auth tokens, passwords,
    personal data. Log only what you need for debugging.
```

<a id="log-levels"></a>

## Log Levels

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

```
Kavya's log level decision tree:

    "Did it succeed normally?"
        YES → INFO
        NO  →
            "Can we recover automatically?"
                YES → WARN
                NO  →
                    "Is the service still running?"
                        YES → ERROR
                        NO  → FATAL
```

<a id="log-aggregation--the-elk-stack"></a>

## Log Aggregation — The ELK Stack

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

```
Kavya's comparison — ELK vs Loki:

    ┌────────────────────────────────────────────────────────────────┐
    │  Feature          │  ELK Stack            │  Grafana Loki       │
    ├────────────────────────────────────────────────────────────────┤
    │  Indexing         │  Full-text index       │  Label-based only   │
    │  Storage cost     │  High (indexes all)    │  Low (stores raw)   │
    │  Query speed      │  Fast (pre-indexed)    │  Slower (grep-like) │
    │  Setup complexity │  Heavy (3 components)  │  Light (1 binary)   │
    │  Best for         │  Large teams, complex  │  Small teams, cost- │
    │                   │  queries, compliance   │  sensitive, K8s     │
    └────────────────────────────────────────────────────────────────┘

    Kavya's advice: "Start with Loki. Move to ELK when you outgrow it."
```

> [↑ Back to Top](#top)

<a id="4-distributed-tracing"></a>

# 4. Distributed Tracing

Kavya pictures a single user request as a package being shipped through a warehouse. The package passes through receiving, sorting, quality check, packing, and shipping. If the delivery is late, she needs to know which station caused the delay — not just that the total time was too long.

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

<a id="trace-id-and-spans"></a>

## Trace ID and Spans

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

```
Kavya's mental model — trace anatomy:

    TRACE  = the full journey (one trace per user request)
    SPAN   = one service's contribution (one span per hop)
    PARENT = the span that called this span

    Relationships:
        Trace "abc-123"
         └─ Span: API Gateway (root span, no parent)
             ├─ Span: Auth Service (parent = API Gateway)
             └─ Span: Product Service (parent = API Gateway)
                 ├─ Span: Price Service (parent = Product)
                 └─ Span: DB Query (parent = Product)
```

<a id="how-trace-ids-propagate"></a>

## How Trace IDs Propagate

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

```
Kavya's propagation checklist — what every service must do:

    1. Extract trace_id from incoming request header
    2. If no trace_id exists, generate one (you're the root)
    3. Create a span with: trace_id, span_id, parent_span_id, service_name
    4. Do your work
    5. When calling downstream services, inject trace_id into outgoing headers
    6. When done, record span timing and send to collector
    7. If an error occurs, tag the span with error=true

    Standard headers:
        W3C Trace Context:  traceparent: 00-{trace_id}-{span_id}-01
        B3 (Zipkin):        X-B3-TraceId, X-B3-SpanId, X-B3-ParentSpanId
```

<a id="tracing-tools"></a>

## Tracing Tools

- **Jaeger** — open source, created by Uber, CNCF project
- **Zipkin** — open source, created by Twitter
- **Honeycomb, Datadog, Tempo** — commercial or cloud-native options
- **OpenTelemetry** — vendor-neutral instrumentation SDK (metrics, logs, traces)

The key is instrumentation: your services need to be set up to generate spans and propagate trace IDs. Libraries like OpenTelemetry provide vendor-neutral instrumentation.

```
Kavya's tool selection guide:

    ┌────────────────────────────────────────────────────────────┐
    │  "We want free + self-hosted"     → Jaeger or Zipkin       │
    │  "We want managed + easy"         → Datadog, Honeycomb     │
    │  "We're all-in on Grafana"        → Grafana Tempo          │
    │  "We want vendor-neutral code"    → OpenTelemetry SDK      │
    │                                      (exports to any of    │
    │                                       the above backends)  │
    └────────────────────────────────────────────────────────────┘

    Kavya's advice: "Always instrument with OpenTelemetry.
    Then you can switch backends without changing application code."
```

> [↑ Back to Top](#top)

<a id="5-slo-sla-and-sli"></a>

# 5. SLO, SLA, and SLI

Kavya thinks of SLOs like a fitness goal. Your SLI is the measurement (your actual mile time today). Your SLO is your training target ("run a mile in under 7 minutes, 99% of training days"). Your SLA is the promise you made to your coach ("if I miss more than 3 days this month, I owe extra laps").

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

```
Kavya's error budget concept:

    SLO: 99.9% availability per month
    Total minutes in a month: ~43,200
    Error budget: 0.1% = 43.2 minutes of allowed downtime

    ┌──────────────────────────────────────────────────────┐
    │  Budget remaining: 43.2 min                          │
    │  ████████████████████████████████████░░░░  (90%)     │
    │                                                      │
    │  If budget > 50%: ship features, take risks          │
    │  If budget < 25%: freeze deploys, focus on stability │
    │  If budget = 0:   incident review, no new features   │
    └──────────────────────────────────────────────────────┘

    Error budgets make reliability a SHARED concern between
    product and engineering. "We used our budget — no more
    risky deploys this week."
```

> 📝 **Practice:** [Q64 - slo-sla-sli](../system_design_practice_questions_100.md#q64--interview--slo-sla-sli)

> [↑ Back to Top](#top)

<a id="6-alerting"></a>

# 6. Alerting

Kavya has been on both sides of alert fatigue. Early in her career, her team alerted on everything — CPU spikes, memory at 80%, brief network blips. After a month of false alarms at 3am, engineers started ignoring pages. Then a real incident went unnoticed for 40 minutes. She learned the hard way: not every anomaly deserves a page.

<a id="rules-for-good-alerts"></a>

## Rules for Good Alerts

```
Good alert:
    + User-facing impact (or imminent impact)
    + Actionable: the on-call person knows what to do
    + Not self-resolving: it won't fix itself in 30 seconds

Bad alert:
    - "CPU spike for 20 seconds" (almost always self-resolving)
    - "Memory at 85%" (not necessarily a problem on its own)
    - Noise from flapping services (alert, recover, alert, recover...)
    - Anything where the response is "wait and see"
```

```
Kavya's alert quality test — before adding any alert, ask:

    1. "If this fires at 3am, what will the on-call DO?"
       → If "wait and see" → don't page, make it a ticket
    2. "Does this indicate USER pain?"
       → If only infra pain with no user impact → ticket, not page
    3. "Will this self-resolve in < 5 minutes?"
       → If yes → don't alert at all, or alert only if sustained
    4. "Can we auto-remediate this?"
       → If yes → auto-remediate + ticket, don't page a human
```

<a id="tiers-of-response"></a>

## Tiers of Response

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

```
Kavya's severity mapping:

    ┌───────────────────────────────────────────────────────────────┐
    │  Severity   │  User Impact        │  Response          │ Tool │
    ├───────────────────────────────────────────────────────────────┤
    │  P1 (SEV1)  │  All users affected │  Page NOW          │ PD   │
    │  P2 (SEV2)  │  Some users, major  │  Page within 15min │ PD   │
    │  P3 (SEV3)  │  Minor, workaround  │  Business hours    │ Jira │
    │  P4 (SEV4)  │  Cosmetic / perf    │  Next sprint       │ Jira │
    └───────────────────────────────────────────────────────────────┘
```

<a id="runbooks"></a>

## Runbooks

When an alert fires, the on-call engineer should not have to figure out what to do from scratch. A **runbook** is a document that says:

- What does this alert mean?
- What are the likely causes?
- What are the first steps to diagnose?
- What are the steps to remediate each cause?
- Who else to page if you can't fix it?

Good runbooks are the difference between a 10-minute incident and a 2-hour one.

```
Kavya's runbook template:

    ALERT: payment_error_rate_high
    ────────────────────────────────────────────────────
    MEANING:
        Payment success rate < 95% for 5+ minutes.

    LIKELY CAUSES:
        1. Payment provider outage (Stripe/Braintree)
        2. Database connection pool exhaustion
        3. Bad deploy (recent code change)

    FIRST STEPS:
        1. Check Grafana payment dashboard
        2. Check payment provider status page
        3. Check recent deploys (last 2 hours)
        4. Check DB connection pool metrics

    REMEDIATION:
        - Provider outage → failover to backup provider
        - DB pool exhausted → restart service, investigate leak
        - Bad deploy → rollback via: `kubectl rollout undo`

    ESCALATION:
        - If not resolved in 15 min → page payments-team-lead
        - If data loss suspected → page database-oncall
```

> 📝 **Practice:** [Q65 - alerting-strategies](../system_design_practice_questions_100.md#q65--thinking--alerting-strategies)

> [↑ Back to Top](#top)

<a id="7-the-observability-stack"></a>

# 7. The Observability Stack

Kavya draws this diagram on the whiteboard for every new team member. It shows how all the pieces fit together — from your services emitting telemetry to the on-call engineer being paged with context.

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

```
Kavya's incident workflow — connecting the pieces:

    1. DETECT:   Prometheus alert fires (error rate > 5%)
    2. NOTIFY:   PagerDuty pages Kavya's phone
    3. TRIAGE:   Kavya opens Grafana → sees payment-service RED metrics spiking
    4. DIAGNOSE: Clicks "View Logs" → Kibana shows "connection timeout to DB"
    5. TRACE:    Picks a failing trace_id → Jaeger shows DB span taking 30s
    6. ROOT CAUSE: DB connection pool exhausted (max=50, active=50, waiting=200)
    7. FIX:      Restarts service (immediate), increases pool size (permanent)
    8. POSTMORTEM: Documents timeline, root cause, action items
```

> [↑ Back to Top](#top)

<a id="8-quick-reference"></a>

# 8. Quick Reference

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

```
Kavya's "which tool for which question?" cheat sheet:

    "Is something wrong RIGHT NOW?"           → Grafana (metrics dashboard)
    "What exactly happened?"                  → Kibana/Loki (log search)
    "Where is the bottleneck?"                → Jaeger (trace waterfall)
    "Are we meeting our reliability targets?" → Grafana (SLO dashboard)
    "Who gets paged and when?"                → PagerDuty (routing rules)
```

> 📝 **Practice:** [Q94 - debug-p99-latency-spikes](../system_design_practice_questions_100.md#q94--critical--debug-p99-latency-spikes)
> 📝 **Practice:** [Q62 - chaos-engineering](../system_design_practice_questions_100.md#q62--normal--chaos-engineering)

> [↑ Back to Top](#top)

<a id="learning-priority"></a>

<a id="summary"></a>

## Summary

| Concept | Core Idea | Kavya's One-Liner |
|---------|-----------|-------------------|
| Three Pillars | Metrics + Logs + Traces = complete visibility | "Numbers say WHAT, text says WHY, traces say WHERE" |
| Metrics | Numbers over time (counters, gauges, histograms) | "Your system's vital signs — always on, always watching" |
| RED Method | Rate, Errors, Duration for every service | "Three numbers that tell you if a service is healthy" |
| Logs | Structured JSON records of events | "The diary that makes 3am debugging possible" |
| Traces | End-to-end request journey with timing | "Follow one request like a package through a warehouse" |
| SLO/SLA/SLI | Measurement, target, and promise | "Measure it, aim for it, promise it — in that order" |
| Alerting | Page on user impact, not symptoms | "If the response is 'wait and see,' it's not an alert" |
| Runbooks | Pre-written incident response guides | "The difference between 10 min and 2 hours to fix" |

**The key rule Kavya lives by:** You cannot fix what you cannot see. Observability isn't an afterthought. It's infrastructure. Build it before you need it, because when you need it, you really need it.

> [↑ Back to Top](#top)

<a id="navigation"></a>

## Navigation

[Back to README](../README.md)

| | |
|---|---|
| ⬅ Previous | [13 — Security](../13_security/theory.md) |
| ➡ Next | [15 — Cloud Architecture](../15_cloud_architecture/theory.md) |

**This folder:** [theory.md](./theory.md) | [cheetsheet.md](./cheetsheet.md) | [interview.md](./interview.md)

**Related modules:** [02 — System Fundamentals (SLOs)](../02_system_fundamentals/theory.md) | [12 — Microservices](../12_microservices/theory.md) | [13 — Security](../13_security/theory.md) | [15 — Cloud Architecture](../15_cloud_architecture/theory.md)

**Jump to topics:** [Prometheus and Grafana](#prometheus-and-grafana) | [RED Method](#the-red-method) | [Trace ID and Spans](#trace-id-and-spans) | [ELK Stack](#log-aggregation--the-elk-stack) | [SLO/SLA/SLI](#5-slo-sla-and-sli) | [Runbooks](#runbooks)
