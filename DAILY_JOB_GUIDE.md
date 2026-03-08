# Daily Job Guide — What Software Engineers Actually Use
> This repo has 4 masteries and hundreds of topics.
> Not all of them show up every day at work.
> This guide splits everything by how often you will use it on the job.

---

## The Big Picture

There is a difference between:
- **What you use at work daily** — tools, patterns, and concepts you touch every single day
- **What you need for interviews** — topics that companies test to assess your problem-solving depth
- **What makes you a senior engineer** — concepts you use rarely but must understand deeply when needed

This repo covers all three. This file tells you which category each topic falls into.

---

## Tier 1 — You Use This Every Day

These are the fundamentals. If you work as a Python backend engineer, you will touch these daily.

### Python (Daily Use)
| Topic | Where You Use It |
|-------|-----------------|
| Variables, types, control flow | Every single function you write |
| Functions and closures | Defining endpoints, utilities, helpers |
| Classes and OOP | Models, services, repositories |
| Error handling (try/except) | Every production function needs this |
| List, dict, set operations | Data manipulation everywhere |
| String formatting and manipulation | Logs, messages, API responses |
| File I/O | Config files, reports, data pipelines |
| Modules and imports | Every project with more than one file |
| Logging | Debugging production issues |
| Virtual environments and packages | Setting up every project |

**Files**:
- `python-complete-mastery/01_python_fundamentals/`
- `python-complete-mastery/03_data_types/`
- `python-complete-mastery/04_functions/`
- `python-complete-mastery/05_oops/`
- `python-complete-mastery/06_exceptions_error_handling/`
- `python-complete-mastery/08_file_handling/`
- `python-complete-mastery/09_logging_debugging/`

---

### DSA Structures Used Daily
| Topic | Where You Use It |
|-------|-----------------|
| Arrays / Lists | Processing any collection of data |
| Dictionaries (hash maps) | Caching, lookups, grouping, indexing |
| Sets | Deduplication, membership checks |
| Strings | User input, parsing, formatting |
| Sorting | Ranking results, ordering data |
| Basic searching (in, find) | Checking existence in collections |

**Files**:
- `dsa-complete-mastery/02_arrays/`
- `dsa-complete-mastery/03_strings/`
- `dsa-complete-mastery/10_hashing/`

---

### API Work (Daily)
| Topic | Where You Use It |
|-------|-----------------|
| REST fundamentals | Every API you build or consume |
| HTTP methods and status codes | Writing endpoint responses |
| JSON serialization | Request/response bodies |
| FastAPI / Flask endpoints | The code you ship to production |
| Pydantic models | Request validation |
| Authentication (JWT, API keys) | Every secured endpoint |
| Error handling formats | Consistent error responses |

**Files**:
- `api-mastery/01_what_is_an_api/`
- `api-mastery/02_rest_fundamentals/`
- `api-mastery/05_authentication/`
- `api-mastery/06_error_handling_standards/`
- `api-mastery/07_fastapi/`

---

### System Concepts (Daily Awareness)
| Topic | Where You Use It |
|-------|-----------------|
| SQL basics (SELECT, JOIN, WHERE) | Querying your database every day |
| Database indexes | Understanding why queries are slow |
| HTTP request lifecycle | Every API call you debug |
| Environment variables and config | Every deployed application |

**Files**:
- `system-design-mastery/05_databases/`

---

## Tier 2 — You Use This Weekly

These topics come up frequently but not every single day. You need them to write good production code.

### Python (Weekly)
| Topic | When You Use It |
|-------|----------------|
| Decorators | Auth checks, logging, retry logic, caching |
| Generators | Streaming large datasets, memory efficiency |
| Context managers | File handling, DB sessions, locks |
| Comprehensions | Transforming data cleanly |
| Type hints | Code reviews, IDE support |
| Testing (pytest) | Every PR needs tests |
| Concurrency (async/await) | FastAPI async endpoints |

**Files**:
- `python-complete-mastery/10_decorators/`
- `python-complete-mastery/11_generators_iterators/`
- `python-complete-mastery/12_context_managers/`
- `python-complete-mastery/13_concurrency/`
- `python-complete-mastery/17_testing/`

---

### DSA Patterns Used Weekly
| Topic | When You Use It |
|-------|----------------|
| Binary search | Fast lookups on sorted data, bisect module |
| Stack | Undo/redo, parsing expressions, DFS |
| Queue / deque | BFS, task processing, rate limiting |
| Two pointers | Array manipulation, deduplication |
| Recursion | File system traversal, tree operations |

**Files**:
- `dsa-complete-mastery/04_recursion/`
- `dsa-complete-mastery/06_searching/`
- `dsa-complete-mastery/08_stack/`
- `dsa-complete-mastery/09_queue/`
- `dsa-complete-mastery/11_two_pointers/`
- `dsa-complete-mastery/13_binary_search/`

---

### API and System (Weekly)
| Topic | When You Use It |
|-------|----------------|
| Database migrations (Alembic) | Schema changes, new features |
| Caching (Redis) | Reducing DB load on hot data |
| Pagination | Any endpoint returning lists |
| API versioning | When you change an existing API |
| Background tasks (Celery) | Sending emails, long processing |
| Logging and monitoring | Understanding production behaviour |
| Design patterns (Factory, Repository, Observer) | Structuring your codebase cleanly |

**Files**:
- `api-mastery/07_fastapi/database_guide.md`
- `api-mastery/07_fastapi/advanced_guide.md`
- `api-mastery/08_versioning_standards/`
- `system-design-mastery/06_caching/`
- `python-complete-mastery/16_design_patterns/`
- `system-design-mastery/14_observability/`

---

## Tier 3 — You Need This for Interviews (Less Daily at Work)

These topics are heavily tested in coding interviews but you rarely implement them from scratch in a regular software job. You still need to understand them deeply — they make you a better programmer even if you don't code them daily.

### DSA Interview Topics
| Topic | Why It Matters Even at Work |
|-------|---------------------------|
| Trees and BST | Understanding sorted maps, database indexes, DOM structures |
| Heaps | Priority queues in schedulers, Dijkstra in routing |
| Graphs (BFS/DFS) | Dependency resolution, social networks, routing |
| Greedy algorithms | Scheduling problems, interval merging |
| Backtracking | Configuration generation, constraint satisfaction |
| Dynamic Programming | Recognizing and avoiding exponential algorithms |
| Linked Lists | Interview favourite, rarely hand-rolled in Python |

Even if you never implement a heap at work, knowing how it works helps you choose the right data structure when Python's `heapq` is the right tool.

**Files**:
- `dsa-complete-mastery/14_trees/`
- `dsa-complete-mastery/15_binary_search_trees/`
- `dsa-complete-mastery/16_heaps/`
- `dsa-complete-mastery/18_graphs/`
- `dsa-complete-mastery/19_greedy/`
- `dsa-complete-mastery/20_backtracking/`
- `dsa-complete-mastery/21_dynamic_programming/`

---

### Advanced DSA (Occasionally at Work, Often in Interviews)
| Topic | Real Use Cases |
|-------|---------------|
| Trie | Autocomplete systems, prefix search, IP routing |
| Union-Find (DSU) | Network connectivity, Kruskal MST, social groups |
| Sliding Window | Metrics dashboards, rate limiters, time series |
| Bit Manipulation | Feature flags, permissions, Bloom filters |

**Files**:
- `dsa-complete-mastery/12_sliding_window/`
- `dsa-complete-mastery/17_trie/`
- `dsa-complete-mastery/22_bit_manipulation/`
- `dsa-complete-mastery/24_disjoint_set_union/`

---

## Tier 4 — Senior / Staff Engineer Territory

These are not topics a junior or mid-level engineer works with daily. But they separate mid-level from senior engineers and are critical for system design interviews.

### System Design at Scale
| Topic | When It Matters |
|-------|----------------|
| Load balancing algorithms | Choosing between L4/L7, sticky sessions |
| Message queues (Kafka, RabbitMQ) | Async processing, event-driven architecture |
| Microservices and service mesh | Splitting a monolith, managing inter-service comms |
| Distributed systems (CAP, Raft, quorum) | Multi-region systems, split-brain scenarios |
| CQRS and event sourcing | High-write + high-read systems |
| Consistent hashing | Distributed caches, sharding |
| Rate limiting algorithms | API gateway design |
| High Level Design (HLD) | System design interviews |

**Files**:
- `system-design-mastery/08_load_balancing/`
- `system-design-mastery/09_message_queues/`
- `system-design-mastery/10_distributed_systems/`
- `system-design-mastery/11_scalability_patterns/`
- `system-design-mastery/12_microservices/`
- `system-design-mastery/16_high_level_design/`
- `dsa-complete-mastery/26_system_design_patterns/`

---

### Advanced DSA (Rarely Daily, Niche Systems)
| Topic | Where It Appears in Production |
|-------|-------------------------------|
| Segment Tree | Real-time analytics, range queries at scale |
| Advanced Graphs (Dijkstra, Bellman-Ford, SCC) | Maps, routing engines, network analysis |
| Topological Sort | Build systems, package managers, dependency graphs |
| Max Flow | Network capacity, bipartite matching in scheduling |

You will not write a segment tree at most jobs. But if you work at a trading firm, analytics company, or game engine team, you absolutely will. And understanding these makes you sharper at recognising inefficient code.

**Files**:
- `dsa-complete-mastery/23_segment_tree/`
- `dsa-complete-mastery/25_advanced_graphs/`

---

## Daily Work Checklist

If you are working as a backend Python engineer, this is what you actually touch each day:

```
Every day:
  ✓ Python: functions, classes, dict/list operations, error handling
  ✓ API: REST endpoints, JSON, auth, status codes
  ✓ Database: SQL queries, ORM, indexes
  ✓ Git: commits, branches, code review

Every week:
  ✓ Python: decorators, async/await, testing, logging
  ✓ API: pagination, caching, background tasks
  ✓ System: debugging performance, Redis, config management
  ✓ Design patterns: structuring new features cleanly

Every month:
  ✓ Database: schema migrations, query optimisation, explain plans
  ✓ API: versioning changes, security audit
  ✓ Infrastructure: deployment changes, monitoring dashboards
  ✓ Code review: bigger refactors, architectural decisions

Occasionally:
  ✓ Tree/graph problems when working on hierarchical data
  ✓ Binary search when building search or sorted results
  ✓ Heap when building a priority-based system
  ✓ Advanced system design when scaling a service
```

---

## Recommended Study Priority by Career Goal

### Goal: Get your first backend job
```
Priority 1 (Must): Python Tier 1 + REST + FastAPI + SQL basics
Priority 2 (Should): Testing + DSA Foundations + basic system design
Priority 3 (Nice): Advanced Python + caching + message queues
```

### Goal: Pass a FAANG-style coding interview
```
Priority 1 (Must): All DSA (01–21) + Complexity + Patterns + Common Mistakes
Priority 2 (Should): System Design Foundations + Python Advanced
Priority 3 (Nice): Advanced DSA (22–26) + HLD/LLD
```

### Goal: Get a senior backend role
```
Priority 1 (Must): All Tier 1 + 2 + Python production + API full stack
Priority 2 (Should): System Design (Stages 1–6) + Microservices + Distributed
Priority 3 (Nice): Advanced DSA + Clean Architecture + Data at Scale
```

### Goal: Staff / Principal Engineer
```
Priority 1 (Must): Full system design mastery + HLD/LLD + Distributed Systems
Priority 2 (Should): All Python production patterns + Advanced APIs + Data Systems
Priority 3 (Nice): Advanced DSA for depth of thinking
```

---

## Important Reminder

Even topics you don't use daily are worth learning in this repo.

Knowing how a trie works makes you faster at recognising when to use `str.startswith()` in a loop vs building a prefix index.

Knowing Dijkstra makes you understand why your caching layer invalidates the way it does.

Knowing DP makes you spot exponential time complexity in loops before it causes a 3am incident.

The goal is depth. Not just day-to-day coverage.

---

## Navigation

| | |
|---|---|
| Home | [Readme.md](./Readme.md) |
| Learning Path | [LEARNING_PATH.md](./LEARNING_PATH.md) |
| Quick Start | [QUICK_START.md](./QUICK_START.md) |
| Python Mastery | [python-complete-mastery/README.md](./python-complete-mastery/README.md) |
| DSA Mastery | [dsa-complete-mastery/README.md](./dsa-complete-mastery/README.md) |
| API Mastery | [api-mastery/README.md](./api-mastery/README.md) |
| System Design | [system-design-mastery/README.md](./system-design-mastery/README.md) |
