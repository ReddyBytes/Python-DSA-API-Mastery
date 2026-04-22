# ⚡ Cheatsheet: OpenTelemetry (OTEL)

---

## Learning Priority

**Must Learn** — foundation for any observability work:
OTEL SDK setup · trace/span creation · log correlation with trace_id

**Should Learn** — required for production observability:
Metric instruments · OTEL collector config · exporter setup (Jaeger/Zipkin/OTLP)

**Good to Know** — advanced OTEL usage:
Baggage propagation · custom attributes · sampling strategies · semantic conventions

**Reference** — look up when needed:
OTEL semantic conventions spec · OTLP proto definitions · Prometheus remote write

---

## Core Concepts in 30 Seconds

```
Trace     — the full journey of one request across all services
Span      — one unit of work within a trace (a function, a DB query, an HTTP call)
TraceID   — shared ID linking all spans of one trace together
SpanID    — unique ID for each individual span
Baggage   — key-value pairs propagated across service boundaries
Metric    — numerical measurement over time (counter, gauge, histogram)
Log       — timestamped text event, linked to trace via trace_id
```

---

## OTEL SDK Setup (Python — FastAPI)

```python
# pip install opentelemetry-sdk
#             opentelemetry-instrumentation-fastapi
#             opentelemetry-instrumentation-httpx
#             opentelemetry-instrumentation-sqlalchemy
#             opentelemetry-exporter-otlp-proto-grpc

from opentelemetry import trace, metrics
from opentelemetry.sdk.trace import TracerProvider
from opentelemetry.sdk.trace.export import BatchSpanProcessor
from opentelemetry.sdk.metrics import MeterProvider
from opentelemetry.sdk.metrics.export import PeriodicExportingMetricReader
from opentelemetry.sdk.resources import Resource
from opentelemetry.exporter.otlp.proto.grpc.trace_exporter import OTLPSpanExporter
from opentelemetry.exporter.otlp.proto.grpc.metric_exporter import OTLPMetricExporter
from opentelemetry.instrumentation.fastapi import FastAPIInstrumentor
from opentelemetry.instrumentation.httpx import HTTPXClientInstrumentor
from opentelemetry.instrumentation.sqlalchemy import SQLAlchemyInstrumentor

def setup_otel(app):
    # Resource — identifies this service in traces
    resource = Resource.create({
        "service.name": "payment-api",
        "service.version": "1.2.3",
        "deployment.environment": "production"
    })

    # Tracing
    tracer_provider = TracerProvider(resource=resource)
    tracer_provider.add_span_processor(
        BatchSpanProcessor(
            OTLPSpanExporter(endpoint="http://otel-collector:4317")
        )
    )
    trace.set_tracer_provider(tracer_provider)

    # Metrics
    metric_reader = PeriodicExportingMetricReader(
        OTLPMetricExporter(endpoint="http://otel-collector:4317"),
        export_interval_millis=60_000
    )
    meter_provider = MeterProvider(resource=resource, metric_readers=[metric_reader])
    metrics.set_meter_provider(meter_provider)

    # Auto-instrument FastAPI, HTTPX, SQLAlchemy
    FastAPIInstrumentor().instrument_app(app)
    HTTPXClientInstrumentor().instrument()
    SQLAlchemyInstrumentor().instrument()
```

---

## Trace and Span Creation

```python
from opentelemetry import trace
from opentelemetry.trace import StatusCode

tracer = trace.get_tracer("payment-api")

# Simple span
async def process_payment(payment_id: str):
    with tracer.start_as_current_span("process_payment") as span:
        span.set_attribute("payment.id", payment_id)
        span.set_attribute("payment.currency", "usd")

        result = await charge_card(payment_id)

        span.set_attribute("payment.status", result["status"])
        return result

# Span with error recording
async def call_external_service(url: str):
    with tracer.start_as_current_span("external.call") as span:
        span.set_attribute("http.url", url)
        try:
            response = await httpx_client.get(url)
            span.set_attribute("http.status_code", response.status_code)
            return response.json()
        except Exception as e:
            span.set_status(StatusCode.ERROR, str(e))
            span.record_exception(e)
            raise

# Nested spans — child automatically links to parent via context
async def order_flow(order_id: str):
    with tracer.start_as_current_span("order.process") as parent_span:
        parent_span.set_attribute("order.id", order_id)

        with tracer.start_as_current_span("order.validate") as child:
            await validate_order(order_id)

        with tracer.start_as_current_span("order.charge") as child:
            await charge_order(order_id)

        with tracer.start_as_current_span("order.fulfill") as child:
            await fulfill_order(order_id)
```

---

## Metric Instruments

| Instrument | Type | Use Case | Example |
|------------|------|----------|---------|
| `Counter` | Monotonically increasing | Count events | requests_total, errors_total |
| `UpDownCounter` | Increases and decreases | Current quantity | active_connections, queue_depth |
| `Histogram` | Distribution of values | Latency, payload size | request_duration_ms, response_size_bytes |
| `Gauge` | Current value (observable) | Resource usage | cpu_usage, memory_bytes |
| `ObservableCounter` | Async counter | System-level counters | disk_io_bytes_total |
| `ObservableGauge` | Async gauge | Polled metrics | cache_hit_ratio |

```python
from opentelemetry import metrics

meter = metrics.get_meter("payment-api")

# Counter
request_counter = meter.create_counter(
    name="api.requests.total",
    description="Total number of API requests",
    unit="1"
)

# Histogram (for latency)
request_duration = meter.create_histogram(
    name="api.request.duration",
    description="API request duration",
    unit="ms"
)

# UpDownCounter
active_connections = meter.create_up_down_counter(
    name="api.connections.active",
    description="Currently active WebSocket connections",
    unit="1"
)

# Usage
request_counter.add(1, {"method": "POST", "route": "/payments", "status": "200"})
request_duration.record(125.4, {"route": "/payments"})
active_connections.add(1)   # on connect
active_connections.add(-1)  # on disconnect
```

---

## Log Correlation with trace_id

```python
import logging
import json
from opentelemetry import trace

class OTELLogFormatter(logging.Formatter):
    """Inject trace context into every log record."""

    def format(self, record):
        # Get current span context
        span = trace.get_current_span()
        ctx = span.get_span_context()

        log_entry = {
            "timestamp": self.formatTime(record),
            "level": record.levelname,
            "logger": record.name,
            "message": record.getMessage(),
        }

        if ctx.is_valid:
            # Convert to hex strings — matches format in trace backends
            log_entry["trace_id"] = format(ctx.trace_id, "032x")
            log_entry["span_id"] = format(ctx.span_id, "016x")
            log_entry["trace_flags"] = format(ctx.trace_flags, "02x")

        if record.exc_info:
            log_entry["exception"] = self.formatException(record.exc_info)

        return json.dumps(log_entry)

# Setup
handler = logging.StreamHandler()
handler.setFormatter(OTELLogFormatter())
logging.basicConfig(level=logging.INFO, handlers=[handler])
logger = logging.getLogger(__name__)

# Now every log statement includes trace_id — correlate logs with traces in Jaeger/Grafana
logger.info("Payment processed", extra={"payment_id": "pay_xxx"})
# Output: {"timestamp": "...", "level": "INFO", "message": "Payment processed",
#           "trace_id": "4bf92f3577b34da6a3ce929d0e0e4736", "span_id": "00f067aa0ba902b7"}
```

---

## OTEL Collector Config Skeleton

```yaml
# otel-collector-config.yaml
receivers:
  otlp:
    protocols:
      grpc:
        endpoint: 0.0.0.0:4317    # receive from apps
      http:
        endpoint: 0.0.0.0:4318

processors:
  batch:
    timeout: 10s
    send_batch_size: 1024

  memory_limiter:
    limit_mib: 512
    spike_limit_mib: 128
    check_interval: 5s

  resource:
    attributes:
      - action: insert
        key: cluster.name
        value: production

  filter:
    traces:
      span:
        - 'attributes["http.route"] == "/health/live"'   # drop health check spans

exporters:
  jaeger:
    endpoint: jaeger:14250
    tls:
      insecure: true

  prometheus:
    endpoint: 0.0.0.0:8889    # scrape metrics from this endpoint

  otlp/tempo:                  # Grafana Tempo for traces
    endpoint: tempo:4317
    tls:
      insecure: true

  logging:
    verbosity: basic           # debug output — disable in production

service:
  pipelines:
    traces:
      receivers: [otlp]
      processors: [memory_limiter, resource, filter, batch]
      exporters: [jaeger, otlp/tempo]

    metrics:
      receivers: [otlp]
      processors: [memory_limiter, batch]
      exporters: [prometheus]

    logs:
      receivers: [otlp]
      processors: [batch]
      exporters: [logging]
```

---

## Jaeger Exporter Setup

```python
from opentelemetry.exporter.jaeger.thrift import JaegerExporter
from opentelemetry.sdk.trace.export import BatchSpanProcessor

jaeger_exporter = JaegerExporter(
    agent_host_name="jaeger",
    agent_port=6831,
)
tracer_provider.add_span_processor(BatchSpanProcessor(jaeger_exporter))
```

## Zipkin Exporter Setup

```python
from opentelemetry.exporter.zipkin.json import ZipkinExporter

zipkin_exporter = ZipkinExporter(
    endpoint="http://zipkin:9411/api/v2/spans"
)
tracer_provider.add_span_processor(BatchSpanProcessor(zipkin_exporter))
```

## OTLP (Preferred in Production)

```python
# OTLP sends to OTEL Collector → collector fans out to Jaeger, Zipkin, Tempo, etc.
# Best practice: always use OTLP → Collector → backends (never vendor lock-in)
from opentelemetry.exporter.otlp.proto.grpc.trace_exporter import OTLPSpanExporter

otlp_exporter = OTLPSpanExporter(
    endpoint="http://otel-collector:4317",
    headers={"api-key": "your-key-if-using-saas-backend"}
)
```

---

## Sampling Strategies

```python
from opentelemetry.sdk.trace.sampling import (
    TraceIdRatioBased,
    ParentBased,
    ALWAYS_ON,
    ALWAYS_OFF
)

# Sample 10% of traces — good for high-traffic APIs
sampler = TraceIdRatioBased(rate=0.1)

# Respect parent's sampling decision (default — do this in child services)
sampler = ParentBased(root=TraceIdRatioBased(rate=0.1))

tracer_provider = TracerProvider(
    resource=resource,
    sampler=sampler
)
```

---

## When to Use / Avoid

| Feature | Use When | Avoid When |
|---------|----------|------------|
| Auto-instrumentation | FastAPI, SQLAlchemy, HTTPX, Redis | Custom protocols (add manual spans) |
| Manual spans | Business logic steps, external calls not auto-instrumented | Every single function call (too noisy) |
| Counter | Counting discrete events | Measuring values — use Histogram |
| Histogram | Latency, sizes, durations | Binary yes/no — use Counter |
| OTLP → Collector | Production (backend flexibility) | Quick dev setup (Jaeger direct is fine) |
| TraceIdRatioBased sampling | High-traffic production (reduce cost) | Debug/staging (use ALWAYS_ON) |
| Log-trace correlation | Any service emitting both logs and traces | Services with no tracing setup yet |

---

**[🏠 Back to README](../README.md)**

**Prev:** [← Real-World APIs](../18_real_world_apis/cheatsheet.md) &nbsp;|&nbsp; **Next:** [Interview Master →](../99_interview_master/)

**Related Topics:** [Production Deployment](../12_production_deployment/) · [API Performance](../09_api_performance_scaling/) · [Interview Master](../99_interview_master/)
