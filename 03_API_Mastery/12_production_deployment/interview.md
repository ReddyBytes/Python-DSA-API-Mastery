# 🎯 API Production Deployment — Interview Preparation

> This file prepares you to discuss API production deployment like a working engineer.
> Not just definitions — but real-world usage, trade-offs, and production scenarios.

---

# 🔹 Basic Level Questions (0–2 Years)

**Q1: Why do you use Gunicorn with Uvicorn workers for FastAPI instead of running Uvicorn alone?**

<details>
<summary>💡 Show Answer</summary>

Uvicorn alone runs a single process. If that process crashes, the API goes down until it is restarted. Gunicorn is a process manager — it spawns multiple Uvicorn worker processes, monitors their health, and restarts them automatically if they crash. This gives you resilience and parallelism without needing an external supervisor.

Uvicorn workers (uvicorn.workers.UvicornWorker) are async and handle FastAPI's ASGI interface correctly. The typical worker count is (CPU cores × 2) + 1. Each worker is an independent process with its own memory, which also provides isolation — a memory leak in one worker is cleaned up when Gunicorn recycles it via --max-requests. For pure async workloads with no CPU-bound code, running Uvicorn with multiple workers (uvicorn main:app --workers 4) is also valid and avoids Gunicorn overhead, but Gunicorn is the safer production default because of its mature process management.

</details>

<br>

**Q2: What is the difference between a liveness probe and a readiness probe in Kubernetes?**

<details>
<summary>💡 Show Answer</summary>

A liveness probe answers: "is this process still alive?" If it fails, Kubernetes restarts the pod. A readiness probe answers: "is this pod ready to receive traffic?" If it fails, Kubernetes removes the pod from the load balancer's endpoint list but does not restart it.

The critical rule: never check external dependencies (database, Redis) in the liveness probe. If your database is temporarily unavailable, a liveness probe that checks DB connectivity will fail, Kubernetes will restart the pod, the pod starts up and immediately fails again — a restart loop. The pod is healthy; the database is not. The liveness probe should only check that the process is running and not deadlocked — a simple return {"status": "alive"}.

The readiness probe is the right place to check dependencies — it prevents traffic from reaching a pod before its connection pool is warm and all dependencies are reachable.

</details>

<br>

**Q3: What is a multi-stage Docker build and why does it matter for production images?**

<details>
<summary>💡 Show Answer</summary>

A multi-stage build uses multiple FROM instructions in a single Dockerfile. The first stage (builder) installs all build tools and dependencies. The final stage copies only the compiled/installed artifacts into a clean minimal base image, discarding the build tools.

This matters for production because build tools (gcc, pip's build cache, git) add hundreds of megabytes to the image and expand the attack surface. A 1.2 GB builder image becomes a 120 MB final image. Smaller images pull faster, start faster, and have fewer packages that could contain vulnerabilities. The pattern also enforces a clean separation between what is needed to build the application and what is needed to run it — the final image contains only the Python interpreter, installed packages, and application code.

</details>

<br>

**Q4: Why should you never use the "latest" Docker image tag in production Kubernetes deployments?**

<details>
<summary>💡 Show Answer</summary>

The "latest" tag is mutable — it points to whatever was last pushed to the registry. If you deploy image: myapi:latest and a new image is pushed to "latest" between when pod A and pod B start, you have two pods running different versions of your API simultaneously. This causes inconsistent behavior that is nearly impossible to debug.

Pinning a specific version tag (image: myapi:v1.2.3 or image: myapi:abc123def for a git commit hash) makes deployments reproducible and auditable. You know exactly what code is running in every pod. If a bad deployment is pushed, you can roll back to the previous pinned version with one command. Immutable tags are also required for Kubernetes to correctly detect when a deployment should be updated — if the tag never changes, Kubernetes will not pull a new image even if the underlying image has changed.

</details>

<br>

**Q5: What should a production health check endpoint return and why?**

<details>
<summary>💡 Show Answer</summary>

A production health check should have at least two separate endpoints. The liveness endpoint (/health/live) returns a simple 200 with {"status": "alive"} — it only checks that the process is responsive. The readiness endpoint (/health/ready) checks all dependencies the pod needs to serve traffic: database connectivity (run SELECT 1), Redis connectivity (PING), and any other critical services. If any dependency is unhealthy it returns 503 Service Unavailable with a body that identifies which check failed.

The response body detail in the readiness endpoint is for operators, not clients — it should identify the failing component ({"status": "degraded", "checks": {"database": "error: connection refused", "redis": "ok"}}). An optional /health/info endpoint can return the running version, uptime, and environment — useful for verifying that the right version deployed without checking logs.

</details>

<br>

---

# 🔹 Intermediate Level Questions (2–5 Years)

**Q6: How does Pydantic BaseSettings work for environment variable management and why is it better than os.environ directly?**

<details>
<summary>💡 Show Answer</summary>

Pydantic BaseSettings reads environment variables and validates them against a typed schema at startup. If a required variable (like DATABASE_URL or SECRET_KEY) is missing, the application raises a validation error before serving any requests — a fail-fast startup rather than a cryptic AttributeError at request time.

Compared to os.environ: BaseSettings provides type coercion (an env var "8" becomes the integer 8, "true" becomes a boolean True), field-level defaults, and documentation of all expected configuration in one place. The lru_cache wrapper on the get_settings() factory function ensures settings are parsed once at startup and reused for all subsequent calls rather than re-reading environment variables on each request. It also supports loading from a .env file in development without any code change — the same code works locally and in production where the real env vars are injected by Kubernetes Secrets or a secrets manager.

</details>

<br>

**Q7: Explain a rolling deployment strategy in Kubernetes and why maxUnavailable: 0 is important.**

<details>
<summary>💡 Show Answer</summary>

A rolling deployment replaces pods one at a time (or in small batches) rather than taking all pods down and bringing up new ones simultaneously. Kubernetes uses two parameters: maxSurge (how many extra pods above the desired count can exist during rollout) and maxUnavailable (how many pods below the desired count are allowed during rollout).

Setting maxUnavailable: 0 means Kubernetes will never remove an old pod until a new pod is fully ready (readiness probe passing). Combined with maxSurge: 1, the rollout brings up one new pod, waits for it to become ready, then removes one old pod, repeating until all pods are replaced. This guarantees zero downtime — at no point during the rollout is total capacity below the desired replica count. The trade-off is slightly slower rollout (waiting for each pod to become ready) and temporary higher resource usage. This is the correct default for production APIs. The preStop lifecycle hook (sleep 5) gives the load balancer time to drain connections from the pod before it starts shutting down.

</details>

<br>

**Q8: What is the --max-requests flag in Gunicorn and why should you always set it in production?**

<details>
<summary>💡 Show Answer</summary>

--max-requests N instructs Gunicorn to gracefully restart a worker after it has handled N requests. After the restart the worker starts fresh with clean memory.

Python applications can have slow memory leaks — from ORM sessions not being fully released, from third-party libraries accumulating state, or from circular references that the garbage collector does not collect. These leaks are small per request but accumulate over millions of requests until the worker process consumes gigabytes of memory and slows down or is OOM-killed. --max-requests is a safety valve: restart the worker before the leak becomes a problem. --max-requests-jitter adds randomness to the restart threshold (e.g., max-requests + random(0, jitter)) to prevent all workers from restarting simultaneously under load, which would cause a brief capacity drop. The combination max-requests 1000 and max-requests-jitter 100 is a common production starting point.

</details>

<br>

**Q9: How do Kubernetes ConfigMaps and Secrets differ and what should go in each?**

<details>
<summary>💡 Show Answer</summary>

Both ConfigMaps and Secrets inject key-value data into pods as environment variables or mounted files. The difference is handling and intent. ConfigMaps are for non-sensitive configuration: feature flags, log level, CORS origin list, environment name, worker counts. Secrets are for sensitive values: database passwords, API keys, JWT signing keys, TLS certificates.

Kubernetes Secrets are base64-encoded in etcd — they are not encrypted by default, which surprises many engineers. The actual security comes from: RBAC policies that restrict which pods can access which Secrets, etcd encryption at rest (which must be explicitly configured), and never committing Secrets to git. In practice, production teams use an external secrets manager (AWS Secrets Manager, HashiCorp Vault) and sync values into Kubernetes Secrets at deploy time via operators like External Secrets Operator. The application code treats them identically — envFrom: secretRef — the source-of-truth management is the difference.

</details>

<br>

**Q10: What is the --preload flag in Gunicorn and when should you avoid it?**

<details>
<summary>💡 Show Answer</summary>

--preload loads the application once in the master process before forking workers. Workers inherit the loaded application state via copy-on-write, which saves memory (the parsed code, loaded ML models, and compiled templates are shared rather than duplicated per worker) and reduces startup time after a crash.

Avoid it when the application holds resources that cannot be safely shared across fork boundaries. asyncio event loops cannot be forked — if any code at module level calls asyncio.run() or creates an event loop, --preload will create the loop in the master and workers will inherit a broken loop. Database connection pools created at module import time can also behave incorrectly after fork — connections established in the parent process may be shared across workers, causing silent data corruption or connection errors. The safe rule: use --preload only after verifying that all initialization is either idempotent across fork or is deferred to the worker's first request.

</details>

<br>

---

# 🔹 Advanced Level Questions (5+ Years)

**Q11: Walk through a zero-downtime blue-green deployment strategy and when you would choose it over rolling deployments.**

<details>
<summary>💡 Show Answer</summary>

Blue-green deployment maintains two identical production environments — blue (currently live) and green (new version). You deploy the new version to green, run smoke tests and health checks against green while blue continues serving production traffic, then switch the load balancer to route all traffic to green. Blue remains running as an instant rollback target.

Choose blue-green over rolling when: the new version has a database migration that is not backward compatible with the old version (both versions cannot run simultaneously), you need a hard cutover rather than a gradual rollout, or you want the ability to instant rollback by switching the LB back to blue without re-deploying. The trade-off is resource cost — you run two full environments simultaneously during the transition, doubling infrastructure cost for the rollout window.

Rolling deployments are preferred when migrations are backward compatible (additive schema changes), you want gradual traffic shifting to catch errors at low blast radius, and cost matters. Canary deployment (a variant) routes a small percentage of traffic to the new version, monitors error rates, and promotes or rolls back based on metrics — this is more sophisticated than blue-green but provides the best production validation.

</details>

<br>

**Q12: How do you handle database migrations safely in a production Kubernetes deployment?**

<details>
<summary>💡 Show Answer</summary>

The key constraint: during a rolling deployment, old and new pod versions run simultaneously. Any database migration that runs during this window must be compatible with both versions. The pattern is expand-contract (also called parallel change).

Expand phase: add new columns as nullable (no default required), add new tables, create new indexes concurrently (CONCURRENTLY in PostgreSQL prevents table locks). Deploy the new application code that reads and writes the new schema. Old pods ignore new nullable columns. New pods write to both old and new schema.

Contract phase (in a later deployment): remove old columns, drop old tables, make columns non-nullable once all old pods are gone. This phase is only safe after 100% of pods are on the new version.

Alembic migrations run as a Kubernetes Job or an init container before the Deployment rollout starts. The Job must be idempotent — if it runs twice, the second run must not fail or corrupt data. Use IF NOT EXISTS clauses and Alembic's version table to track applied migrations. Never run migrations from application startup code — this causes a race condition when multiple pods start simultaneously.

</details>

<br>

**Q13: How would you debug a production FastAPI pod that is passing liveness probes but serving degraded responses?**

<details>
<summary>💡 Show Answer</summary>

Liveness passing but bad responses means the process is alive but something upstream or internal is failing. Start with the readiness probe response — if it shows a dependency failing, that is the lead. Check database connectivity from inside the pod (kubectl exec -it pod -- python -c "import sqlalchemy; ..."), Redis ping, and any downstream service health endpoints.

If dependencies are healthy, the problem is in the application logic. Pull structured logs for the affected pod: kubectl logs pod-name --since=15m | grep ERROR. Check for slow query logs from the database — the pod may be alive but every request is waiting 30 seconds for a locked table. Look at connection pool exhaustion: if all pool connections are in use (pool_timeout errors in logs), responses succeed eventually but slowly.

For harder-to-reproduce issues: enable debug logging temporarily in a single pod using a ConfigMap change and re-deploy only that pod. Use an APM tool (Datadog, OpenTelemetry + Jaeger) to trace individual slow requests end-to-end. Profile the event loop for async lock contention using aiomonitor or by adding a /debug/tasks endpoint (in a secure, non-public path) that dumps the current asyncio task list.

</details>

<br>

**Q14: What is Horizontal Pod Autoscaling in Kubernetes and what metrics should drive scaling decisions for an API?**

<details>
<summary>💡 Show Answer</summary>

HPA automatically adjusts the number of pod replicas based on observed metrics. The default metric is CPU utilization — scale out when average CPU exceeds a target percentage. For an API this is often the right signal because CPU correlates with active request processing.

For APIs with variable request complexity, CPU alone can be misleading. Better metrics: requests per second from an ingress controller (scales based on actual load, not compute cost), p95 request latency (scale out when latency rises above an SLO threshold), or custom metrics from a Prometheus exporter (connection pool utilization, queue depth for async workers). Scaling on latency is the most user-facing metric — it directly measures whether the API is meeting its SLO.

Configure target CPU utilization at 60–70%, not 100% — autoscaling has a response lag (typically 30–60 seconds to provision and start new pods). At 100% CPU target you will be saturated before new capacity arrives. Set a minimum replica count to handle baseline traffic without cold-start latency, and a maximum to cap cost. Combine HPA with a PodDisruptionBudget that prevents the cluster autoscaler from evicting too many pods simultaneously during a node drain or scale-down event.

</details>

<br>
