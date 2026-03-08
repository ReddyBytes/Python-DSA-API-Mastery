# Complete Learning Path
> This repo covers Python, DSA, API Mastery, and System Design.
> That is a lot. This guide tells you exactly what to study, in what order, and why.

---

## The Four Masteries — What Each Covers

| Mastery | What You Learn | Folder |
|---------|----------------|--------|
| Python | The language itself — from basics to production patterns | `python-complete-mastery/` |
| DSA | Data structures + algorithms — how to think and solve problems | `dsa-complete-mastery/` |
| API | How services communicate — REST, FastAPI, auth, deployment | `api-mastery/` |
| System Design | How to design large systems — databases, caching, scale | `system-design-mastery/` |

These are not independent. They build on each other.
Python makes DSA possible. DSA sharpens your API code. APIs connect to systems. Systems need design thinking.

---

## Where to Start Based on Your Level

### If you are a beginner (less than 1 year experience)
```
1. Python Complete Mastery → Sections 1 and 2
2. DSA → Phase 1 (Foundations)
3. API → Stages 1–3
4. System Design → Stages 1–2
```
Do not rush. Foundations matter more than speed.

### If you are mid-level (1–3 years experience)
```
1. Python → Section 2 (Advanced) + Section 3 (Production)
2. DSA → Phases 2–4 (Core structures + Pattern solving)
3. API → Stages 4–7 (FastAPI, auth, versioning, deployment)
4. System Design → Stages 3–5 (Data layer + Scale)
```

### If you are preparing for interviews (any level)
```
1. DSA → Full roadmap (Phases 1–5) with interview.md per topic
2. System Design → Stages 5–8 (advanced patterns + interview prep)
3. Python → Interview master files
4. API → Core REST + FastAPI
5. All 99_interview_master folders
```

---

## Full Structured Learning Path

Follow this order. It is intentional — each topic prepares you for the next.

---

### Stage 1 — Python Foundation
**Goal**: Understand how Python works, not just what it does.

| # | Topic | File |
|---|-------|------|
| 1 | Fundamentals | `python-complete-mastery/01_python_fundamentals/theory.md` |
| 2 | Control Flow | `python-complete-mastery/02_control_flow/theory.md` |
| 3 | Data Types | `python-complete-mastery/03_data_types/theory.md` |
| 4 | Functions | `python-complete-mastery/04_functions/theory.md` |
| 5 | OOP | `python-complete-mastery/05_oops/theory.md` |
| 6 | Exceptions | `python-complete-mastery/06_exceptions_error_handling/theory.md` |

**Time**: 2 weeks at 2 hours/day
**Milestone**: Write a class-based Python program that reads a file, processes data, and handles errors.

---

### Stage 2 — DSA Foundations
**Goal**: Understand how data is stored, accessed, and manipulated at the core level.

| # | Topic | File |
|---|-------|------|
| 1 | Complexity Analysis | `dsa-complete-mastery/01_complexity_analysis/theory.md` |
| 2 | Arrays | `dsa-complete-mastery/02_arrays/theory.md` |
| 3 | Strings | `dsa-complete-mastery/03_strings/theory.md` |
| 4 | Recursion | `dsa-complete-mastery/04_recursion/theory.md` |
| 5 | Sorting | `dsa-complete-mastery/05_sorting/theory.md` |
| 6 | Searching | `dsa-complete-mastery/06_searching/theory.md` |

For each topic, read in this order:
```
theory.md → visual_explanation.md → cheatsheet.md → common_mistakes.md → real_world_usage.md → interview.md
```

**Time**: 2 weeks
**Milestone**: Implement merge sort and binary search from scratch without looking.

---

### Stage 3 — API Basics
**Goal**: Know what an API is, how HTTP works, and how to build a simple REST endpoint.

| # | Topic | File |
|---|-------|------|
| 1 | What is an API? | `api-mastery/01_what_is_an_api/story.md` |
| 2 | HTTP Deep Dive | `api-mastery/02_rest_fundamentals/rest_explained.md` |
| 3 | REST Design | `api-mastery/03_rest_best_practices/patterns.md` |
| 4 | Data Formats | `api-mastery/04_data_formats/serialization_guide.md` |

**Time**: 1 week
**Milestone**: Build a REST API with 3 endpoints using FastAPI.

---

### Stage 4 — Core Data Structures (DSA Phase 2)
**Goal**: Master the structures you will use in every real job.

| # | Topic | File |
|---|-------|------|
| 7 | Linked List | `dsa-complete-mastery/07_linked_list/theory.md` |
| 8 | Stack | `dsa-complete-mastery/08_stack/theory.md` |
| 9 | Queue | `dsa-complete-mastery/09_queue/theory.md` |
| 10 | Hashing | `dsa-complete-mastery/10_hashing/theory.md` |
| 11 | Two Pointers | `dsa-complete-mastery/11_two_pointers/theory.md` |
| 12 | Sliding Window | `dsa-complete-mastery/12_sliding_window/theory.md` |
| 13 | Binary Search | `dsa-complete-mastery/13_binary_search/theory.md` |

**Time**: 2–3 weeks
**Milestone**: Solve 5 medium-level LeetCode problems per topic using the pattern files.

---

### Stage 5 — Advanced Python
**Goal**: Write Python code that is clean, efficient, and production-ready.

| # | Topic | File |
|---|-------|------|
| 7 | Modules & Packages | `python-complete-mastery/07_modules_packages/theory.md` |
| 8 | File Handling | `python-complete-mastery/08_file_handling/theory.md` |
| 9 | Logging & Debugging | `python-complete-mastery/09_logging_debugging/theory.md` |
| 10 | Decorators | `python-complete-mastery/10_decorators/theory.md` |
| 11 | Generators | `python-complete-mastery/11_generators_iterators/theory.md` |
| 12 | Context Managers | `python-complete-mastery/12_context_managers/theory.md` |
| 13 | Concurrency | `python-complete-mastery/13_concurrency/theory.md` |
| 14 | Memory Management | `python-complete-mastery/14_memory_management/theory.md` |

**Time**: 2 weeks
**Milestone**: Add logging, async endpoints, and proper error handling to your Stage 3 API.

---

### Stage 6 — FastAPI Mastery + Auth
**Goal**: Build complete, production-quality APIs.

| # | Topic | File |
|---|-------|------|
| 5 | Authentication | `api-mastery/05_authentication/securing_apis.md` |
| 6 | Error Handling | `api-mastery/06_error_handling_standards/error_guide.md` |
| 7 | FastAPI Deep Dive | `api-mastery/07_fastapi/why_fastapi.md` |
|   | FastAPI Basics | `api-mastery/07_fastapi/first_api.md` |
|   | FastAPI Core | `api-mastery/07_fastapi/core_guide.md` |
|   | FastAPI + DB | `api-mastery/07_fastapi/database_guide.md` |
|   | FastAPI Advanced | `api-mastery/07_fastapi/advanced_guide.md` |

**Time**: 2 weeks
**Milestone**: Build a full API with JWT auth, PostgreSQL, Pydantic models, and Alembic migrations.

---

### Stage 7 — Trees, Graphs, and Advanced DSA
**Goal**: Handle hierarchical and network data. The core of hard interview problems.

| # | Topic | File |
|---|-------|------|
| 14 | Trees | `dsa-complete-mastery/14_trees/theory.md` |
| 15 | BST | `dsa-complete-mastery/15_binary_search_trees/theory.md` |
| 16 | Heaps | `dsa-complete-mastery/16_heaps/theory.md` |
| 17 | Trie | `dsa-complete-mastery/17_trie/theory.md` |
| 18 | Graphs | `dsa-complete-mastery/18_graphs/theory.md` |
| 19 | Greedy | `dsa-complete-mastery/19_greedy/theory.md` |
| 20 | Backtracking | `dsa-complete-mastery/20_backtracking/theory.md` |
| 21 | Dynamic Programming | `dsa-complete-mastery/21_dynamic_programming/theory.md` |

**Time**: 4–6 weeks
**Milestone**: Solve 10 tree problems, 5 graph problems, and 5 DP problems without hints.

---

### Stage 8 — System Design Foundations
**Goal**: Understand the infrastructure that your APIs run on.

| Stage | Topic | File |
|-------|-------|------|
| 1 | Computer Fundamentals | `system-design-mastery/00_computer_fundamentals/story.md` |
| 1 | Networking Basics | `system-design-mastery/01_networking_basics/theory.md` |
| 1 | System Fundamentals | `system-design-mastery/02_system_fundamentals/theory.md` |
| 3 | Databases | `system-design-mastery/05_databases/theory.md` |
| 3 | Caching | `system-design-mastery/06_caching/theory.md` |
| 4 | Load Balancing | `system-design-mastery/08_load_balancing/theory.md` |
| 4 | Message Queues | `system-design-mastery/09_message_queues/theory.md` |

**Time**: 3 weeks
**Milestone**: Can explain how a production web app handles 100,000 requests per day.

---

### Stage 9 — Production Python + API
**Goal**: Ship code that works reliably at scale.

| # | Topic | File |
|---|-------|------|
| 16 | Design Patterns | `python-complete-mastery/16_design_patterns/theory.md` |
| 17 | Testing | `python-complete-mastery/17_testing/theory.md` |
| 18 | Performance | `python-complete-mastery/18_performance_optimization/theory.md` |
| 19 | Production Best Practices | `python-complete-mastery/19_production_best_practices/theory.md` |
|   | API Versioning | `api-mastery/08_versioning_standards/versioning_strategy.md` |
|   | API Performance | `api-mastery/09_api_performance_scaling/performance_guide.md` |
|   | Testing APIs | `api-mastery/10_testing_documentation/testing_apis.md` |
|   | Security | `api-mastery/11_api_security_production/security_hardening.md` |
|   | Deployment | `api-mastery/12_production_deployment/deployment_guide.md` |

**Time**: 2–3 weeks
**Milestone**: Add unit tests, CI/CD, Docker deployment, and rate limiting to your API project.

---

### Stage 10 — Advanced System Design + Architecture
**Goal**: Design systems that handle millions of users.

| Stage | Topic | File |
|-------|-------|------|
| 5 | Scalability Patterns | `system-design-mastery/11_scalability_patterns/theory.md` |
| 5 | Microservices | `system-design-mastery/12_microservices/theory.md` |
| 5 | Security | `system-design-mastery/13_security/theory.md` |
| 5 | Observability | `system-design-mastery/14_observability/theory.md` |
| 6 | High Level Design | `system-design-mastery/16_high_level_design/theory.md` |
| 6 | Low Level Design | `system-design-mastery/17_low_level_design/theory.md` |
| 6 | Design Patterns | `system-design-mastery/18_design_patterns/theory.md` |
| 6 | Clean Architecture | `system-design-mastery/19_clean_architecture/theory.md` |
| 8 | Case Studies | `system-design-mastery/22_case_studies/theory.md` |
| 8 | Interview Framework | `system-design-mastery/23_interview_framework/theory.md` |

**Time**: 4 weeks
**Milestone**: Can design Twitter, URL shortener, or ride-sharing app end-to-end with trade-offs.

---

### Stage 11 — Advanced DSA + Interview Mastery
**Goal**: Handle hard algorithm problems and senior-level interview rounds.

| # | Topic | File |
|---|-------|------|
| 22 | Bit Manipulation | `dsa-complete-mastery/22_bit_manipulation/theory.md` |
| 23 | Segment Tree | `dsa-complete-mastery/23_segment_tree/theory.md` |
| 24 | Disjoint Set Union | `dsa-complete-mastery/24_disjoint_set_union/theory.md` |
| 25 | Advanced Graphs | `dsa-complete-mastery/25_advanced_graphs/theory.md` |
| 26 | System Design Patterns | `dsa-complete-mastery/26_system_design_patterns/theory.md` |
|   | DSA Interview Master | `dsa-complete-mastery/99_interview_master/` |
|   | System Design Interview | `system-design-mastery/99_interview_master/` |

**Time**: 3–4 weeks
**Milestone**: Complete mock interviews under timed conditions across DSA + system design + Python.

---

## Time Plans

### 3-Month Accelerated Plan (Interviews Focus)
```
Month 1:  Stages 1–4  →  Python + DSA Foundations + Core Structures
Month 2:  Stages 5–7  →  Advanced Python + FastAPI + Trees/Graphs/DP
Month 3:  Stages 8–11 →  System Design + Production + Interview Simulation
```
Daily: 3–4 hours minimum.

---

### 6-Month Thorough Plan (Job Readiness)
```
Months 1–2:  Stages 1–5  →  Strong Python + Core DSA + API Basics
Months 3–4:  Stages 6–8  →  FastAPI Production + Advanced DSA + System Foundations
Months 5–6:  Stages 9–11 →  Production Engineering + Advanced Design + Mock Interviews
```
Daily: 2 hours.

---

### 12-Month Deep Mastery (Complete Transformation)
```
Q1:  Python Complete + DSA Foundations
Q2:  DSA Advanced + API Mastery (Stages 3–6)
Q3:  System Design Full + Python Production
Q4:  DSA Expert Level + Interview Simulation
```
Daily: 1.5 hours.

---

## How to Study Each Topic

Every DSA folder has these files. Read them in this order:

```
1. theory.md          → Read once, understand the concept deeply
2. visual_explanation.md → Trace through diagrams manually
3. patterns.md        → Learn to recognize the problem type
4. real_world_usage.md → See where it actually appears in production
5. common_mistakes.md → Read before solving any problem
6. cheatsheet.md      → Use as a quick reference during practice
7. interview.md       → Read out loud, practice answering
8. *.py files         → Implement from scratch, do not copy-paste
```

---

## How to Study System Design

Every system-design folder has `theory.md` + `interview.md` + `cheatsheet.md`.

```
1. Read theory.md fully
2. Draw the architecture on paper
3. Write down 3 trade-offs you would make
4. Read interview.md and answer questions out loud
5. Use cheatsheet.md as a 10-minute pre-interview review
```

---

## Prerequisites Chart

```
Python Fundamentals
        ↓
DSA Foundations (arrays, strings, recursion)
        ↓
Core Data Structures (stack, queue, hashing, two pointers)
        ↓
         ├──────────────┬───────────────────────────────┐
         ↓              ↓                               ↓
     FastAPI       Trees + Graphs              System Design Foundations
         ↓              ↓                               ↓
   Advanced Python    DP + Advanced DSA         Advanced Architecture
         ↓              ↓                               ↓
         └──────────────┴───────────────────────────────┘
                        ↓
                  Interview Mastery
```

---

## Don't Skip These — Ever

These topics appear in almost every interview and every production codebase:

| Topic | Why It Matters |
|-------|----------------|
| Big-O Complexity | You must explain the cost of every solution |
| Hashing | Dictionary, cache, deduplication — used everywhere |
| Binary Search | Not just arrays — search on answer space too |
| BFS/DFS on trees | 40% of tree and graph problems |
| DP (coins, knapsack, LCS) | Core patterns appear constantly |
| REST + HTTP | The foundation of all modern APIs |
| Databases + Indexing | Every backend touches a database |
| Caching with Redis | Every production system caches |

---

## Navigation

| | |
|---|---|
| Home | [Readme.md](./Readme.md) |
| Quick Start | [QUICK_START.md](./QUICK_START.md) |
| Daily Job Guide | [DAILY_JOB_GUIDE.md](./DAILY_JOB_GUIDE.md) |
| Python Mastery | [python-complete-mastery/README.md](./python-complete-mastery/README.md) |
| DSA Mastery | [dsa-complete-mastery/README.md](./dsa-complete-mastery/README.md) |
| API Mastery | [api-mastery/README.md](./api-mastery/README.md) |
| System Design | [system-design-mastery/README.md](./system-design-mastery/README.md) |
