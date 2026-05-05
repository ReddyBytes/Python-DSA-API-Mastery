# Project 08 — Celery Task Queue

You have done three guided projects. No more hand-holding. This is the test — can you build a complete async task system from a spec alone?

Read the spec. Build it. Check the acceptance criteria. Open the solution only when you are done or completely stuck.

---

## What You're Building

A **FastAPI** app that dispatches work to background **Celery** workers through a **Redis** message broker. The API returns immediately with a task ID — the caller polls for the result separately.

```
+-------------------+         +-------------------+         +-------------------+
|                   |         |                   |         |                   |
|   FastAPI App     | ------> |   Redis Broker    | ------> |  Celery Worker 1  |
|   (port 8000)     |  queue  |   (port 6379)     | dequeue |                   |
|                   |         |                   |         +-------------------+
|  POST /send-email |         |  [ task queue ]   |
|  POST /process-   |         |                   | ------> +-------------------+
|    report         |         |  [ result store ] |         |                   |
|  GET /task/{id}   |         |                   |         |  Celery Worker 2  |
|  POST /schedule-  |         +-------------------+         |                   |
|    cleanup        |                  ^                    +-------------------+
|                   |                  |
+-------------------+     results written back
         |                (SUCCESS / FAILURE / PENDING)
         |
         v
  GET /task/{id}
  polls result store
  returns status + result
```

The API never does slow work itself. It queues the task and returns a `task_id` in milliseconds. Workers pick up tasks from Redis, run them, and write results back. The client polls `GET /task/{id}` to check progress.

---

## What You Need Installed

```bash
pip install fastapi uvicorn[standard] celery redis "celery[redis]" pydantic python-dotenv
```

```bash
# Start Redis with Docker — must be running before Celery or FastAPI
docker run -d --name redis-broker -p 6379:6379 redis:7-alpine
```

---

## Spec

### Endpoints

| Method | Path | Request Body | Response | Notes |
|--------|------|-------------|----------|-------|
| `POST` | `/send-email` | `{"to": "string", "subject": "string", "body": "string"}` | `{"task_id": "string", "status": "queued"}` | Returns immediately — task runs in background |
| `POST` | `/process-report` | `{"report_id": "string", "data": [list of ints]}` | `{"task_id": "string", "status": "queued"}` | Returns immediately — result available after ~5s |
| `GET` | `/task/{task_id}` | — | `{"task_id": "string", "status": "PENDING\|STARTED\|SUCCESS\|FAILURE", "result": any}` | `result` is null until SUCCESS |
| `POST` | `/schedule-cleanup` | `{"target": "string"}` | `{"task_id": "string", "scheduled_in_seconds": 30}` | Task runs 30 seconds after this call |

### Task Behaviors

| Task Name | What It Does | Simulated Duration | Retry Config |
|-----------|-------------|-------------------|-------------|
| `send_email` | Print `"Sending email to {to}: {subject}"`, then sleep | 2 seconds | 3 retries, 5s delay between each |
| `process_report` | Sum all ints in `data`, print progress, then sleep | 5 seconds | 3 retries, 5s delay between each |
| `cleanup_task` | Print `"Running cleanup for {target}"`, then sleep | 1 second | 3 retries, 5s delay between each |

### Architecture Requirements

- Use `celery.result.AsyncResult` to check task status in `GET /task/{task_id}` — do not poll Redis directly
- Celery workers must run in separate processes from the FastAPI app — do not run workers inside the API process
- Use the `@shared_task` decorator on all tasks — not `@app.task` — so tasks are importable without importing the full Celery app
- Set `result_expires=3600` — results are kept in Redis for 1 hour then auto-deleted
- Configure both `broker_url` and `result_backend` to point to `redis://localhost:6379/0`
- Set `task_track_started=True` so the STARTED state is visible when a worker picks up a task
- The `process_report` task must return its computed result (the sum) as a dict: `{"report_id": "...", "sum": int, "item_count": int}`

---

## File Structure

```
08_Celery_Task_Queue/
├── main.py            # FastAPI app — endpoints only, no task logic
├── tasks.py           # All @shared_task definitions
├── celery_app.py      # Celery instance + configuration
├── schemas.py         # Pydantic request/response models
├── docker-compose.yml # Redis + optional worker service
└── README.md          # Exact commands to start everything
```

---

## Acceptance Criteria

Work through this checklist before opening the solution. Every item must pass.

- [ ] `POST /send-email` returns a `task_id` in under 200ms — not after the 2s sleep
- [ ] `POST /process-report` returns a `task_id` in under 200ms — not after the 5s sleep
- [ ] `GET /task/{id}` returns `"status": "PENDING"` immediately after queuing
- [ ] `GET /task/{id}` returns `"status": "STARTED"` while the task is running
- [ ] `GET /task/{id}` returns `"status": "SUCCESS"` with a non-null `result` after the task finishes
- [ ] The `process_report` result includes `report_id`, `sum`, and `item_count`
- [ ] Two workers started with `celery -A celery_app worker --concurrency=2` process tasks concurrently — verify by queuing two `process_report` tasks simultaneously and confirming both finish in ~5s, not ~10s
- [ ] A task that is forced to fail (raise an exception in the task body) retries automatically — check worker logs for `Retry` messages
- [ ] `POST /schedule-cleanup` returns immediately and the cleanup task runs ~30 seconds later — confirm in worker logs
- [ ] Restarting the FastAPI app does not lose queued tasks — they are held in Redis

---

## You're On Your Own

Good luck. Come back here only when you're done or truly stuck.

---

## Full Solution

<details>
<summary>✅ Complete solution — only open when done</summary>

### `celery_app.py`

```python
from celery import Celery

celery_app = Celery(
    "task_queue",                             # ← name shown in worker logs
    broker="redis://localhost:6379/0",        # ← Redis as the message broker (database 0)
    backend="redis://localhost:6379/0",       # ← Redis also stores task results
    include=["tasks"],                        # ← tells Celery which modules contain task definitions
)

celery_app.conf.update(
    result_expires=3600,                      # ← results auto-deleted from Redis after 1 hour
    task_track_started=True,                  # ← emit STARTED state when a worker picks up a task
    task_serializer="json",                   # ← serialize task args/kwargs as JSON
    result_serializer="json",                 # ← serialize results as JSON
    accept_content=["json"],                  # ← only accept JSON-serialized messages (security)
    timezone="UTC",                           # ← normalize all timestamps to UTC
    enable_utc=True,
)
```

---

### `tasks.py`

```python
import time
from celery import shared_task  # ← shared_task does not require importing celery_app directly

@shared_task(
    bind=True,                  # ← bind=True gives access to self (the task instance) for retries
    max_retries=3,              # ← retry up to 3 times before marking FAILURE
    default_retry_delay=5,      # ← wait 5 seconds between retries
    name="tasks.send_email",    # ← explicit name avoids issues if module is renamed
)
def send_email(self, to: str, subject: str, body: str) -> dict:
    try:
        print(f"[send_email] Sending email to {to}: {subject}")  # ← simulated email send
        time.sleep(2)                                             # ← simulate network latency
        print(f"[send_email] Done — {to}")
        return {"to": to, "subject": subject, "sent": True}
    except Exception as exc:
        raise self.retry(exc=exc)  # ← self.retry re-queues the task with the configured delay

@shared_task(
    bind=True,
    max_retries=3,
    default_retry_delay=5,
    name="tasks.process_report",
)
def process_report(self, report_id: str, data: list) -> dict:
    try:
        print(f"[process_report] Starting report {report_id} with {len(data)} items")
        time.sleep(5)                              # ← simulate heavy data processing
        total = sum(data)                          # ← the actual "work"
        print(f"[process_report] Done — sum={total}")
        return {
            "report_id": report_id,
            "sum": total,
            "item_count": len(data),               # ← return structured result, not just a number
        }
    except Exception as exc:
        raise self.retry(exc=exc)

@shared_task(
    bind=True,
    max_retries=3,
    default_retry_delay=5,
    name="tasks.cleanup_task",
)
def cleanup_task(self, target: str) -> dict:
    try:
        print(f"[cleanup_task] Running cleanup for {target}")
        time.sleep(1)                              # ← simulate cleanup work
        print(f"[cleanup_task] Cleanup complete for {target}")
        return {"target": target, "cleaned": True}
    except Exception as exc:
        raise self.retry(exc=exc)
```

---

### `schemas.py`

```python
from typing import Any, Optional
from pydantic import BaseModel

class EmailRequest(BaseModel):
    to: str
    subject: str
    body: str

class ReportRequest(BaseModel):
    report_id: str
    data: list[int]             # ← list of integers to sum

class CleanupRequest(BaseModel):
    target: str                 # ← identifier for what to clean up

class TaskQueuedResponse(BaseModel):
    task_id: str
    status: str = "queued"      # ← always "queued" at dispatch time

class ScheduledResponse(BaseModel):
    task_id: str
    scheduled_in_seconds: int

class TaskStatusResponse(BaseModel):
    task_id: str
    status: str                 # ← PENDING | STARTED | SUCCESS | FAILURE | RETRY
    result: Optional[Any] = None  # ← null until SUCCESS, then holds the task return value
```

---

### `main.py`

```python
from celery.result import AsyncResult           # ← used to look up task state from Redis
from fastapi import FastAPI

from celery_app import celery_app               # ← import the configured Celery instance
from schemas import (
    CleanupRequest, EmailRequest, ReportRequest,
    ScheduledResponse, TaskQueuedResponse, TaskStatusResponse,
)
from tasks import cleanup_task, process_report, send_email  # ← import task functions

app = FastAPI(title="Celery Task Queue")

@app.post("/send-email", response_model=TaskQueuedResponse)
def queue_email(payload: EmailRequest):
    task = send_email.delay(                    # ← .delay() queues the task and returns immediately
        to=payload.to,
        subject=payload.subject,
        body=payload.body,
    )
    return TaskQueuedResponse(task_id=task.id)  # ← task.id is the UUID Celery assigned

@app.post("/process-report", response_model=TaskQueuedResponse)
def queue_report(payload: ReportRequest):
    task = process_report.delay(
        report_id=payload.report_id,
        data=payload.data,
    )
    return TaskQueuedResponse(task_id=task.id)

@app.get("/task/{task_id}", response_model=TaskStatusResponse)
def get_task_status(task_id: str):
    result = AsyncResult(task_id, app=celery_app)  # ← look up the task state from Redis backend
    return TaskStatusResponse(
        task_id=task_id,
        status=result.status,                       # ← PENDING / STARTED / SUCCESS / FAILURE / RETRY
        result=result.result if result.ready() else None,  # ← only populated once task is finished
    )

@app.post("/schedule-cleanup", response_model=ScheduledResponse)
def schedule_cleanup(payload: CleanupRequest):
    task = cleanup_task.apply_async(               # ← apply_async allows passing a countdown
        kwargs={"target": payload.target},
        countdown=30,                              # ← delay task execution by 30 seconds
    )
    return ScheduledResponse(task_id=task.id, scheduled_in_seconds=30)
```

---

### `docker-compose.yml`

```yaml
version: "3.9"

services:
  redis:
    image: redis:7-alpine
    ports:
      - "6379:6379"             # ← expose Redis on localhost:6379
    restart: unless-stopped

  worker:
    build: .                    # ← build from Dockerfile in same directory
    command: celery -A celery_app worker --loglevel=info --concurrency=2
    depends_on:
      - redis                   # ← wait for Redis to be up before starting workers
    environment:
      - CELERY_BROKER_URL=redis://redis:6379/0   # ← use service name "redis" inside Docker network
      - CELERY_RESULT_BACKEND=redis://redis:6379/0

  api:
    build: .
    command: uvicorn main:app --host 0.0.0.0 --port 8000
    ports:
      - "8000:8000"
    depends_on:
      - redis
    environment:
      - CELERY_BROKER_URL=redis://redis:6379/0
      - CELERY_RESULT_BACKEND=redis://redis:6379/0
```

---

### Run commands (without Docker Compose)

```bash
# Terminal 1 — start Redis
docker run -d --name redis-broker -p 6379:6379 redis:7-alpine

# Terminal 2 — start two Celery workers (--concurrency=2 = two threads per process)
celery -A celery_app worker --loglevel=info --concurrency=2

# Terminal 3 — start FastAPI
uvicorn main:app --reload --port 8000

# Test — queue an email task
curl -X POST http://localhost:8000/send-email \
  -H "Content-Type: application/json" \
  -d '{"to": "bob@example.com", "subject": "Hello", "body": "World"}'

# Test — check task status (paste task_id from previous response)
curl http://localhost:8000/task/<task_id>

# Test — queue a report (run two at once to confirm concurrency)
curl -X POST http://localhost:8000/process-report \
  -H "Content-Type: application/json" \
  -d '{"report_id": "rpt-001", "data": [1, 2, 3, 4, 5]}'

# Test — schedule cleanup for 30 seconds from now
curl -X POST http://localhost:8000/schedule-cleanup \
  -H "Content-Type: application/json" \
  -d '{"target": "old-sessions"}'
```

</details>

---

## Reflection

After completing this project, you should now be able to:

- Explain why a task queue is necessary and when to use one instead of `asyncio`
- Configure Celery with Redis as both the broker and the result backend
- Write `@shared_task` functions with automatic retry logic
- Use `.delay()` and `.apply_async()` to dispatch tasks from a FastAPI route
- Use `AsyncResult` to poll task state without coupling the API to the worker process
- Run Celery workers in separate processes and verify concurrent task execution
- Schedule deferred tasks with `countdown` and understand how they flow through Redis
- Debug task failures using Celery worker logs and the FAILURE state in the result backend

---

## What's Next

- **Project 07** — WebSockets: replace polling `GET /task/{id}` with a live push when the task completes
- **Project 08** — Rate limiting and background job prioritization with Celery queues and routing keys
- Back to [Capstone Projects README](../README.md) | Previous: [Project 07 — Config-Driven Scheduler](../07_Config_Driven_Scheduler/Project_Guide.md) | Next: [Project 09 — Rate Limiter Middleware](../09_Rate_Limiter_Middleware/Project_Guide.md)
