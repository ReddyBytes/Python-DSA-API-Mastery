# 🎯 OpenTelemetry — Interview Preparation

> This file prepares you to discuss OpenTelemetry like a working engineer.
> Not just definitions — but real-world usage, trade-offs, and production scenarios.

---

# 🔹 Basic Level Questions (0–2 Years)

**Q1: What is OpenTelemetry and what problem does it solve?**

<details>
<summary>💡 Show Answer</summary>

OpenTelemetry (OTEL) is a vendor-neutral, open-source observability framework that standardizes how you collect traces, metrics, and logs from your applications. Before OTEL, each observability vendor (Datadog, New Relic, Jaeger, Zipkin) had its own SDK and proprietary agent — switching vendors meant rewriting all instrumentation code. OTEL provides one SDK and one wire protocol (OTLP) that works with any backend. You instrument your code once using the OTEL SDK and export to any compatible backend via the OTEL Collector. This solves vendor lock-in and makes observability infrastructure a swappable commodity rather than a strategic decision.

</details>

<br>

**Q2: What is the difference between a trace, a span, and a trace ID?**

<details>
<summary>💡 Show Answer</summary>

A trace is the complete journey of one request across all services — from the initial HTTP call through every downstream service, database query, and external API call it triggers. A span is one unit of work within that trace: a function call, a database query, or an HTTP request to another service. Every span belongs to exactly one trace. A trace ID is the identifier shared by all spans in the same trace — it is propagated in request headers (e.g., `traceparent`) from service to service so all spans can be linked together. A span ID identifies a single span. When you look up a trace in Jaeger, you see a timeline of all spans with their durations, linked by the shared trace ID.

</details>

<br>

**Q3: What is the OTEL Collector and why use it instead of exporting directly from your app to Jaeger?**

<details>
<summary>💡 Show Answer</summary>

The OTEL Collector is a standalone service that receives telemetry from applications (via OTLP), processes it (filter, batch, enrich), and exports to one or more backends. Direct export from app to Jaeger works for development, but in production the Collector provides: fan-out to multiple backends (send the same trace to both Jaeger and your SaaS vendor simultaneously), processing (drop health check spans, add cluster labels, sample), retry logic (buffer and retry if the backend is temporarily unavailable), and decoupling (change backends without redeploying applications). The standard pattern is app → OTLP → Collector → backends. Never hard-code a direct Jaeger or Zipkin exporter in production apps.

</details>

<br>

**Q4: What is log-trace correlation and how do you implement it?**

<details>
<summary>💡 Show Answer</summary>

Log-trace correlation means every log line emitted during a request includes the trace ID and span ID of the currently active span. This lets you jump from a log line in your log aggregator (e.g., Splunk, CloudWatch) directly to the corresponding trace in Jaeger to see what that request was doing when the log was emitted. Implementation: create a custom log formatter that reads the current span context using `trace.get_current_span().get_span_context()`, formats the trace ID as a 32-character hex string and the span ID as a 16-character hex string, and injects them into the log record as `trace_id` and `span_id` fields. This works automatically for any log statement made while a span is active in the context.

</details>

<br>

**Q5: What is the difference between a Counter and a Histogram metric, and when do you use each?**

<details>
<summary>💡 Show Answer</summary>

A Counter is a monotonically increasing number — it only goes up and is reset to zero on restart. Use it for counting events: total requests, total errors, total emails sent. You query it as a rate (requests per second) by taking the derivative. A Histogram records the statistical distribution of a measured value — it creates buckets and counts how many measurements fall in each bucket. Use it for latency, request duration, payload size — anything where you want to know percentiles (p50, p95, p99). You cannot derive latency distribution from a counter. In OTEL, `create_counter` for events, `create_histogram` for measurements. An UpDownCounter (like active connections) is different from a Counter — it can go down.

</details>

<br>

---

# 🔹 Intermediate Level Questions (2–5 Years)

**Q6: What is sampling in distributed tracing, why is it necessary, and what is the difference between head-based and tail-based sampling?**

<details>
<summary>💡 Show Answer</summary>

At high traffic (thousands of requests per second), recording 100% of traces is prohibitively expensive in storage and processing. Sampling reduces the volume by only recording a fraction of traces. Head-based sampling: the decision to sample is made at the start of the request (before processing). TraceIdRatioBased sampling in OTEL is head-based — deterministic based on the trace ID so all spans in a trace get the same decision. Simple and low overhead, but you cannot preferentially keep traces for errors or slow requests since you decide before you know the outcome. Tail-based sampling: the Collector buffers all spans and makes the sampling decision after the full trace is assembled — keeping all error traces and slow traces, dropping only fast successful ones. More accurate but requires significant Collector resources to buffer.

</details>

<br>

**Q7: What is context propagation in OTEL and what happens if a service does not propagate the trace context?**

<details>
<summary>💡 Show Answer</summary>

Context propagation is the mechanism by which trace ID and span ID are passed from service to service across process boundaries. OTEL uses the W3C TraceContext standard: the `traceparent` header carries the trace ID, span ID, and sampling flag. When service A calls service B, A's HTTP client automatically injects `traceparent` into the outgoing request (if auto-instrumented with HTTPXClientInstrumentor). Service B extracts the context and creates a child span linked to the parent. If a service does not propagate context — because it uses an un-instrumented HTTP client or strips headers — the trace is broken into two disconnected fragments in Jaeger. You lose the ability to see the full end-to-end request flow. This is a common production issue in polyglot systems where one service (often a legacy one) does not forward the traceparent header.

</details>

<br>

**Q8: How would you configure the OTEL Collector to filter out health check spans and add a cluster label to all telemetry?**

<details>
<summary>💡 Show Answer</summary>

In the Collector config's `processors` section, use the `filter` processor to drop spans matching the health check route, and the `resource` processor to add attributes. The filter processor uses an OTTL (OpenTelemetry Transformation Language) expression: `'attributes["http.route"] == "/health/live"'` drops matching spans before export. The resource processor adds key-value attributes to all telemetry: `action: insert, key: cluster.name, value: production`. Wire both processors into the pipeline: `processors: [memory_limiter, resource, filter, batch]`. Order matters: `memory_limiter` first (drop data if memory is high before processing), `batch` last (buffer before export for efficiency). Filtering health checks alone can reduce trace volume by 20–40% in typical services.

</details>

<br>

**Q9: What is the `ParentBased` sampler in OTEL and why should child services always use it?**

<details>
<summary>💡 Show Answer</summary>

`ParentBased` wraps another sampler and defers the sampling decision to the parent span when one exists. If the incoming request has a traceparent header saying the trace IS being sampled, the child service samples its spans. If the parent said it is NOT sampled, the child does not record spans. This ensures all spans within a single trace have a consistent sampling decision — you never get a trace where half the services recorded spans and the other half did not. Without ParentBased, each service makes its own sampling decision independently, and you end up with broken, incomplete traces. The root service (no parent) uses its own sampler (e.g., TraceIdRatioBased at 10%). All downstream services use `ParentBased(root=TraceIdRatioBased(rate=0.1))` — they respect the root's decision but also apply the same rate to traces that originate within them.

</details>

<br>

**Q10: How do you instrument a background job or async task that is not triggered by an HTTP request?**

<details>
<summary>💡 Show Answer</summary>

Background jobs have no incoming request to extract a parent trace context from, so you start a new root span manually. Use `tracer.start_as_current_span("job.process_payments")` as a context manager. Set attributes that identify the job: `job.type`, `job.id`, `job.batch_size`. For jobs triggered by a message queue (Celery, SQS, Kafka), the message producer should inject the trace context into the message headers when it enqueues. The consumer extracts the context from message headers using `TraceContextTextMapPropagator().extract()` and passes it as the parent context to the new span — this links the background job trace back to the HTTP request that triggered the queue message, giving you full end-to-end tracing across synchronous and async boundaries.

</details>

<br>

---

# 🔹 Advanced Level Questions (5+ Years)

**Q11: How would you design an observability strategy for a microservices system using OTEL, and what are the four golden signals you instrument first?**

<details>
<summary>💡 Show Answer</summary>

The four golden signals from Google SRE: Latency (p50, p95, p99 of request duration — use a Histogram), Traffic (requests per second — use a Counter), Errors (error rate as a percentage of traffic — error counter divided by request counter), and Saturation (how full the service is — thread pool queue depth, CPU, memory).

Strategy: instrument every service with the OTEL SDK and auto-instrumentation for the framework (FastAPI, SQLAlchemy, HTTPX). Deploy a per-cluster OTEL Collector. Export traces to Jaeger/Grafana Tempo and metrics to Prometheus via the Collector's Prometheus exporter. Set up Grafana dashboards with the four golden signals per service. Add log-trace correlation so on-call engineers can jump from an alert to the trace in one click. Instrument business metrics beyond the four signals (payments per second, checkout funnel drop-off) using OTEL custom metrics — this gives engineering and product a shared observability layer.

</details>

<br>

**Q12: What are OTEL semantic conventions and why do they matter for cross-service observability?**

<details>
<summary>💡 Show Answer</summary>

Semantic conventions are a standardized vocabulary for span and metric attribute names defined by the OTEL specification. Instead of one team naming a span attribute `http_status_code` and another naming it `status` or `response.status`, semantic conventions define the canonical name: `http.response.status_code`. When all services follow the same conventions, you can write a single Grafana query or Jaeger search that works across all services regardless of which team wrote them. Examples: `http.request.method`, `db.system`, `db.statement`, `rpc.service`, `rpc.method`, `net.peer.name`. Auto-instrumentation libraries (FastAPIInstrumentor, SQLAlchemyInstrumentor) follow conventions automatically. For custom spans, follow the conventions for the domain (`db.*` for database operations, `rpc.*` for service calls) and add your business attributes as custom namespaced attributes (`payment.id`, `order.total`).

</details>

<br>

**Q13: A service's p99 latency spikes to 2 seconds every 5 minutes but average latency is fine. Walk through how you would diagnose this using OTEL.**

<details>
<summary>💡 Show Answer</summary>

Step 1 — correlate the timing: confirm in Prometheus/Grafana that the p99 spike is periodic and roughly 5 minutes apart. This pattern suggests a background job, cache expiration, or GC pause rather than a traffic spike.

Step 2 — find the slow traces: in Jaeger, filter for traces on this service with duration greater than 1 second in the spike window. Sort by duration. Look at the span waterfall for the slowest traces.

Step 3 — identify the bottleneck span: the waterfall will show which child span (DB query, external call, internal function) is the slow one. Check the span attributes: `db.statement` for a slow query, `http.url` for a slow downstream call, or a custom span name for a business function.

Step 4 — correlate with metrics: if the slow span is a DB query, check connection pool saturation (`db.connection_pool.wait_time` if instrumented) and query execution time in database metrics. If it is a cache miss pattern, check your cache hit ratio metric.

Step 5 — check logs: use the trace ID from the slow trace to find the correlated log lines — they may contain application-level context (e.g., "cache warm-up started") that explains the spike.

</details>

<br>
