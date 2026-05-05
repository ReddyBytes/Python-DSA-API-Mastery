# CLAUDE.md — Python-DSA-API-Mastery

> Read this file to get complete context of the entire repo without reading any other file.
> Update this file whenever new sections, topics, or files are added.

---

## What This Repo Is

A complete Python, DSA, API, and System Design learning repo — beginner to production.
- Format: Markdown + Python files. No CI/CD pipeline.
- Style: Story-first, practical code examples, interview-ready.
- Audience: Python engineers preparing for interviews and production work.

---

## Repo Root Layout

```
Python-DSA-API-Mastery/
├── README.md
├── CLAUDE.md                    ← THIS FILE
├── MASTER_LEARNING_PATH.md
├── 01_QUICK_START.md
├── 02_LEARNING_PATH.md
├── 03_MASTER_LEARNING_PATH.md
├── 04_DAILY_JOB_GUIDE.md
├── 05_AI_ENGINEER_ROADMAP.md
├── 06_RECAP.md
├── 01_Python_Mastery/           ← 29 modules
├── 02_DSA_Mastery/              ← 27 modules + interview_master
├── 03_API_Mastery/              ← 19 topics + interview_master
├── 04_System_Design_Mastery/    ← 24 topics + interview_master
├── 05_Capstone_Projects/
└── assets/
```

---

## CRITICAL: File Naming Convention

**This repo uses `cheetsheet.md` (double-e) — NOT `cheatsheet.md`.**
This is the established convention across all modules. Never create `cheatsheet.md`.

---

## File Types Per Module

| File | Purpose |
|------|---------|
| `theory.md` | Story-first explanation, concepts, diagrams, gotchas |
| `cheetsheet.md` | Quick-reference commands, patterns, syntax |
| `interview.md` | 3-tier Q&A: Basic (0–2yr) / Intermediate (2–5yr) / Advanced (5+yr) |
| `practice.py` | Coding exercises (most modules) |

Some modules use topic-specific names instead of generic `practice.py` (e.g. `gc_examples.py`, `factory.py`) — this is intentional. Some advanced modules (22/23/27) use numbered sub-files instead of a single theory.md — also intentional.

---

## Section Map

### 01 — Python Mastery (29 modules)

| Module | Topic |
|---|---|
| `01_python_fundamentals` | Variables, types, operators, basic I/O |
| `01.1_memory_management` | Garbage collection, reference counting, memory optimization |
| `02_control_flow` | if/else, loops, comprehensions |
| `03_data_types` | Lists, dicts, sets, tuples, strings |
| `04_functions` | Args, kwargs, closures, LEGB scope, mutable default arg trap |
| `05_oops` | Classes, inheritance, dunder methods, SOLID — uses numbered sub-files |
| `06_exceptions_error_handling` | try/except, custom exceptions, context |
| `07_modules_packages` | imports, __init__, packages, collections module |
| `08_file_handling` | open, pathlib, json, csv, pickle |
| `09_logging_debugging` | logging module, pdb, structlog |
| `10_decorators` | functools, class decorators, stacking |
| `11_generators_iterators` | yield, lazy evaluation, itertools |
| `12_context_managers` | with statement, __enter__/__exit__, contextlib |
| `13_concurrency` | threading, multiprocessing, asyncio, GIL |
| `14_type_hints_and_pydantic` | typing module, Pydantic v2 |
| `15_advanced_python` | metaclasses, descriptors, slots |
| `16_design_patterns` | Factory, singleton, observer, strategy — uses pattern-specific .py files |
| `17_testing` | pytest, fixtures, mocks, coverage |
| `18_performance_optimization` | cProfile, timeit, optimization patterns — uses profiling.md instead of theory.md |
| `19_production_best_practices` | env vars, logging, Docker, CI/CD |
| `20_system_design_with_python` | Rate limiters, caching, scalable design — uses topic-specific .py files |
| `21_data_engineering_applications` | ETL pipelines, streaming simulation — uses topic-specific .py files |
| `22_numpy_for_ai` | NumPy advanced — uses numbered sub-files (01–08) |
| `23_pandas_for_ai` | Pandas advanced — uses numbered sub-files (01–09) |
| `24_async_python_for_ai` | asyncio, aiohttp, async patterns |
| `25_python_ai_ecosystem` | LLM libraries, HuggingFace, LangChain |
| `26_statistics_and_probability` | Stats for ML — topic-specific files |
| `27_matplotlib_seaborn` | Visualization — uses numbered sub-files (01–06) |
| `28_eda_workflow` | Exploratory data analysis |
| `29_web_scraping` | requests, BeautifulSoup, Playwright |

### 02 — DSA Mastery (27 modules)

| Module | Topic |
|---|---|
| `01_complexity_analysis` | Big-O, time/space complexity |
| `02_arrays` | Array operations, sliding window |
| `03_strings` | String manipulation, pattern matching |
| `04_recursion` | Base cases, recursive thinking |
| `05_sorting` | Merge sort, quick sort, counting sort |
| `06_searching` | Linear, binary search variants |
| `07_linked_list` | Singly, doubly, circular |
| `08_stack` | Stack implementations and applications |
| `09_queue` | Queue, deque, priority queue |
| `10_hashing` | Hash maps, collision resolution |
| `11_two_pointers` | Two-pointer technique |
| `12_sliding_window` | Fixed and variable window |
| `13_binary_search` | Binary search patterns |
| `14_trees` | Binary trees, traversals |
| `15_binary_search_trees` | BST operations and balancing |
| `16_heaps` | Min/max heap, heapify |
| `17_trie` | Prefix trees |
| `18_graphs` | BFS, DFS, representations |
| `19_greedy` | Greedy algorithms |
| `20_backtracking` | Permutations, combinations, N-Queens |
| `21_dynamic_programming` | Memoization, tabulation, patterns |
| `22_bit_manipulation` | Bit operations |
| `23_segment_tree` | Range queries |
| `24_disjoint_set_union` | Union-Find |
| `25_advanced_graphs` | Dijkstra, Bellman-Ford, Topological sort |
| `26_system_design_patterns` | Caching, LRU, rate limiter — uses topic-specific files (not theory.md) |
| `99_interview_master` | Tiered interview prep |

### 03 — API Mastery (19 topics)

| Module | Topic |
|---|---|
| `01_what_is_an_api` | API concepts, HTTP basics |
| `02_rest_fundamentals` | REST constraints, statelessness |
| `03_rest_best_practices` | Naming, pagination, filtering |
| `04_data_formats` | JSON, XML, Protobuf, content negotiation |
| `05_authentication` | JWT, OAuth2, API keys |
| `06_error_handling_standards` | RFC 7807, status codes, error envelopes |
| `07_fastapi` | FastAPI framework — dependency injection, middleware |
| `08_versioning_standards` | URL, header, query-param versioning |
| `09_api_performance_scaling` | N+1, caching, connection pooling, pagination |
| `10_testing_documentation` | pytest, TestClient, OpenAPI, contract testing |
| `11_api_security_production` | OWASP, BOLA, rate limiting, mTLS |
| `12_production_deployment` | Gunicorn, Docker, K8s, rolling deploys |
| `13_graphql` | Schema, resolvers, DataLoader, N+1 |
| `14_grpc` | Proto3, streaming modes, interceptors |
| `15_api_gateway` | Kong, Nginx, TLS termination, BFF |
| `16_api_design_patterns` | Idempotency, PATCH semantics, webhooks |
| `17_websockets` | Handshake, auth, backpressure, Redis pub/sub |
| `18_real_world_apis` | Cursor pagination, typed IDs, versioning |
| `19_opentelemetry` | Traces, spans, Collector, log correlation |
| `99_interview_master` | Tiered interview prep |

### 04 — System Design Mastery (24 topics)

| Module | Topic |
|---|---|
| `00_computer_fundamentals` | CPU, memory, OS basics |
| `01_networking_basics` | TCP/IP, DNS, HTTP/HTTPS |
| `02_system_fundamentals` | CAP theorem, consistency, availability |
| `03_api_design` | REST vs GraphQL vs gRPC |
| `04_backend_architecture` | Monolith vs microservices |
| `05_databases` | SQL vs NoSQL, sharding, replication |
| `06_caching` | Redis, CDN, cache patterns |
| `07_storage_cdn` | Object storage, CDN strategies |
| `08_load_balancing` | Algorithms, L4 vs L7, health checks |
| `09_message_queues` | Kafka, RabbitMQ, event-driven |
| `10_distributed_systems` | Consensus, leader election, clocks |
| `11_scalability_patterns` | Horizontal scaling, sharding, replication |
| `12_microservices` | Service mesh, discovery, circuit breaker |
| `13_security` | Auth, encryption, OWASP |
| `14_observability` | Logs, metrics, traces, alerting |
| `15_cloud_architecture` | AWS/GCP/Azure patterns |
| `16_high_level_design` | System design frameworks |
| `17_low_level_design` | Class diagrams, OOP design |
| `18_design_patterns` | GoF patterns in production |
| `19_clean_architecture` | Hexagonal, DDD, SOLID |
| `20_data_systems` | Data lakes, warehouses, pipelines |
| `21_real_time_systems` | Streaming, event sourcing |
| `22_case_studies` | Twitter, Netflix, Uber designs |
| `23_interview_framework` | RESHADED framework, mock interviews |
| `99_interview_master` | Tiered interview prep |

---

## Session Rules

- All work stays within `/Users/1065696/Github/Python-DSA-API-Mastery/`
- No commits until user explicitly asks.
- Always use `cheetsheet.md` — never `cheatsheet.md`.
- Numeric prefix rule for `05_oops/`: files are numbered `01_`, `02_`, etc. Always `ls` first and use N+1.
- After creating any new file, update `Related Topics:` in the folder's `theory.md`.
