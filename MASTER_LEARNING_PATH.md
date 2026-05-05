# Master Learning Path — All Repos

> A complete, step-by-step roadmap covering every repo in this folder.
> Targeted at: **Senior AI/ML/Backend Engineer (4–5 years experience)**
> Total time: **5–6 months full-time | 9–12 months part-time**

---

## Repo Map

| Repo | What It Covers | When to Use |
|---|---|---|
| [Python-DSA-API-Mastery](https://github.com/ReddyBytes/Python-DSA-API-Mastery) | Python · DSA · APIs · System Design | Phases 1, 3, 5, 8 |
| [AI-ENGINEERS-ATLAS](https://github.com/ReddyBytes/AI-ENGINEERS-ATLAS) | Math · ML · DL · LLMs · RAG · Agents · Production AI | Phases 2, 4, 6, 7 |
| [SQL-Mastery](https://github.com/ReddyBytes/SQL-Mastery) | SQL fundamentals to production | Phase 3 |
| [Linux-Terraform-AWS-Mastery](https://github.com/ReddyBytes/Linux-Terraform-AWS-Mastery) | Linux · Bash · AWS · Terraform | Phase 9 |
| [Container-Engineering](https://github.com/ReddyBytes/Container-Engineering) | Docker · Kubernetes | Phase 9 |
| [observability-zero-to-hero](https://github.com/ReddyBytes/observability-zero-to-hero) | Prometheus · Grafana · EFK · Jaeger · OTEL | Phase 10 |
| [Airflow](https://github.com/ReddyBytes/Airflow) | Pipeline orchestration — beginner to cloud | Phase 10 |
| `linux-guide` | Linux quick reference | Ongoing reference |
| `devmastery` | AI Engineer career roadmap | Read at start — also available locally as `AI_ENGINEER_ROADMAP.md` |

---

## Before You Begin — Read These First

- [AI_ENGINEER_ROADMAP.md](https://github.com/ReddyBytes/AI-ENGINEERS-ATLAS/blob/main/00_Learning_Guide/04_AI_Landscape_Map.md) — understand the destination (local copy)
- [QUICK_START.md](https://github.com/ReddyBytes/Python-DSA-API-Mastery/blob/main/01_Python_Mastery/01_QUICK_START.md) — understand the Python repo structure
- [DAILY_JOB_GUIDE.md](https://github.com/ReddyBytes/Python-DSA-API-Mastery/blob/main/04_DAILY_JOB_GUIDE.md) — understand what skills matter at work
- [How_to_Use_This_Repo.md](https://github.com/ReddyBytes/AI-ENGINEERS-ATLAS/blob/main/00_Learning_Guide/00_How_to_Use.md)
- [Learning_Path.md](https://github.com/ReddyBytes/AI-ENGINEERS-ATLAS/blob/main/00_Learning_Guide/04_AI_Landscape_Map.md)

---

## How to Use This Path

- **Reading order per module:** `theory.md` → `practice.py / Code_Example.md` → `cheetsheet.md` → `interview.md`
- **Do not skip practice files** — reading alone gives 30% retention, coding gives 90%
- **Test yourself** using [Practice Questions](https://github.com/ReddyBytes/AI-ENGINEERS-ATLAS/blob/main/00_Learning_Guide/06_Practice_Questions.md)
- Each phase has a **target level** — if you already know it, skim the cheatsheet and move on

---

## Phase Overview

| Phase | Topic | Repo | Duration | Target Level |
|---|---|---|---|---|
| 1 | Python Core to Advanced | Python-DSA-API | 3 weeks | Gets you interview-ready on Python |
| 2 | Math + ML Foundations | AI-ENGINEERS-ATLAS | 3 weeks | Understand what the models are doing |
| 3 | SQL — Fundamentals to Production | SQL-Mastery | 2 weeks | Write production queries confidently |
| 4 | Deep Learning + NLP | AI-ENGINEERS-ATLAS | 3 weeks | Build and explain neural nets |
| 5 | APIs — REST to Production | Python-DSA-API | 3 weeks | Build and deploy real APIs |
| 6 | Transformers + LLMs + Prompt Engineering | AI-ENGINEERS-ATLAS | 3 weeks | Work fluently with LLMs |
| 7 | RAG Systems + AI Agents | AI-ENGINEERS-ATLAS | 4 weeks | Build production RAG + agent systems |
| 8 | Production AI + System Design | AI-ENGINEERS-ATLAS + Python-DSA-API | 4 weeks | Design scalable AI systems |
| 9 | Linux + AWS + Terraform + Docker + K8s | Linux-Terraform + Container | 3 weeks | Deploy and manage infrastructure |
| 10 | Observability + Airflow (Data Pipelines) | Observability + Airflow | 2 weeks | Operate production data systems |
| 11 | DSA + Interview Preparation | Python-DSA-API | 4 weeks | Crack coding + design interviews |
| 12 | Advanced AI Topics + Claude APIs | AI-ENGINEERS-ATLAS | 2 weeks | Stand out with cutting-edge skills |

---

---

# PHASE 1 — Python Core to Advanced

**Duration:** 3 weeks
**Repo:** [Python-DSA-API-Mastery/01_Python_Mastery/](https://github.com/ReddyBytes/Python-DSA-API-Mastery/tree/main/01_Python_Mastery)
**Goal:** Write clean, production-grade Python confidently

### Week 1 — Core Python

| Module | Folder | What You Learn |
|---|---|---|
| Python Fundamentals | [01_python_fundamentals](https://github.com/ReddyBytes/Python-DSA-API-Mastery/tree/main/01_Python_Mastery/01_python_fundamentals) | Variables, memory model, name binding, mutability |
| Control Flow | [02_control_flow](https://github.com/ReddyBytes/Python-DSA-API-Mastery/tree/main/01_Python_Mastery/02_control_flow) | Loops, comprehensions, loop-else, walrus operator |
| Data Types | [03_data_types](https://github.com/ReddyBytes/Python-DSA-API-Mastery/tree/main/01_Python_Mastery/03_data_types) | Lists, dicts, sets, tuples — internals and performance |
| Functions | [04_functions](https://github.com/ReddyBytes/Python-DSA-API-Mastery/tree/main/01_Python_Mastery/04_functions) | *args, **kwargs, closures, LEGB scope, mutable defaults trap |
| OOP | [05_oops](https://github.com/ReddyBytes/Python-DSA-API-Mastery/tree/main/01_Python_Mastery/05_oops) | Classes, inheritance, super(), dunder methods, MRO |
| Exceptions | [06_exceptions_error_handling](https://github.com/ReddyBytes/Python-DSA-API-Mastery/tree/main/01_Python_Mastery/06_exceptions_error_handling) | try/except/else/finally, custom exceptions, re-raising |

### Week 2 — Intermediate Python

| Module | Folder | What You Learn |
|---|---|---|
| Modules & Packages | [07_modules_packages](https://github.com/ReddyBytes/Python-DSA-API-Mastery/tree/main/01_Python_Mastery/07_modules_packages) | Import system, __init__.py, __all__, importlib |
| File Handling | [08_file_handling](https://github.com/ReddyBytes/Python-DSA-API-Mastery/tree/main/01_Python_Mastery/08_file_handling) | pathlib, CSV, JSON, binary, atomic writes |
| Logging & Debugging | [09_logging_debugging](https://github.com/ReddyBytes/Python-DSA-API-Mastery/tree/main/01_Python_Mastery/09_logging_debugging) | Production logging setup, handlers, formatters, pdb |
| Decorators | [10_decorators](https://github.com/ReddyBytes/Python-DSA-API-Mastery/tree/main/01_Python_Mastery/10_decorators) | @wraps, stacked, class decorators, parametrized |
| Generators | [11_generators_iterators](https://github.com/ReddyBytes/Python-DSA-API-Mastery/tree/main/01_Python_Mastery/11_generators_iterators) | yield, send(), pipelines, memory efficiency |
| Context Managers | [12_context_managers](https://github.com/ReddyBytes/Python-DSA-API-Mastery/tree/main/01_Python_Mastery/12_context_managers) | __enter__/__exit__, contextlib, ExitStack |

### Week 3 — Advanced Python

| Module | Folder | What You Learn |
|---|---|---|
| Concurrency | [13_concurrency](https://github.com/ReddyBytes/Python-DSA-API-Mastery/tree/main/01_Python_Mastery/13_concurrency) | GIL, threading, multiprocessing, asyncio, executors |
| Type Hints & Pydantic | [14_type_hints_and_pydantic](https://github.com/ReddyBytes/Python-DSA-API-Mastery/tree/main/01_Python_Mastery/14_type_hints_and_pydantic) | Annotations, Pydantic models, runtime validation |
| Advanced Python | [15_advanced_python](https://github.com/ReddyBytes/Python-DSA-API-Mastery/tree/main/01_Python_Mastery/15_advanced_python) | Metaclasses, descriptors, protocols, __slots__ |
| Design Patterns | [16_design_patterns](https://github.com/ReddyBytes/Python-DSA-API-Mastery/tree/main/01_Python_Mastery/16_design_patterns) | Singleton, Factory, Observer, Strategy |
| Testing | [17_testing](https://github.com/ReddyBytes/Python-DSA-API-Mastery/tree/main/01_Python_Mastery/17_testing) | pytest, fixtures, Mock, parametrize, TDD |
| Memory Management | [01.1_memory_management](https://github.com/ReddyBytes/Python-DSA-API-Mastery/tree/main/01_Python_Mastery/01.1_memory_management) | Reference counting, GC, slots, profiling |

### Phase 1 Interview Prep

- [python_0_2_years.md](https://github.com/ReddyBytes/Python-DSA-API-Mastery/blob/main/01_Python_Mastery/99_interview_master/python_0_2_years.md)
- [tricky_edge_cases.md](https://github.com/ReddyBytes/Python-DSA-API-Mastery/blob/main/01_Python_Mastery/99_interview_master/tricky_edge_cases.md)

### Phase 1 Practice Projects

- [02_Data_Pipeline_CLI](https://github.com/ReddyBytes/Python-DSA-API-Mastery/tree/main/05_Capstone_Projects/03_Data_Pipeline_CLI) — uses everything from Phase 1

---

---

# PHASE 2 — Math + Machine Learning Foundations

**Duration:** 3 weeks
**Repo:** [AI-ENGINEERS-ATLAS/](https://github.com/ReddyBytes/AI-ENGINEERS-ATLAS)
**Goal:** Understand the math behind ML — explain models in interviews, not just use them

### Week 1 — Math for AI

| Section | Folder | Topics |
|---|---|---|
| Probability | [01_Math_for_AI/01_Probability](https://github.com/ReddyBytes/AI-ENGINEERS-ATLAS/tree/main/01_Math_for_AI/01_Probability) | Bayes theorem, distributions, conditional probability |
| Statistics | [01_Math_for_AI/02_Statistics](https://github.com/ReddyBytes/AI-ENGINEERS-ATLAS/tree/main/01_Math_for_AI/02_Statistics) | Hypothesis testing, p-values, confidence intervals |
| Linear Algebra | [01_Math_for_AI/03_Linear_Algebra](https://github.com/ReddyBytes/AI-ENGINEERS-ATLAS/tree/main/01_Math_for_AI/03_Linear_Algebra) | Vectors, matrices, eigenvalues, SVD |
| Calculus | [01_Math_for_AI/04_Calculus_and_Optimization](https://github.com/ReddyBytes/AI-ENGINEERS-ATLAS/tree/main/01_Math_for_AI/04_Calculus_and_Optimization) | Derivatives, chain rule, gradient descent |
| Information Theory | [01_Math_for_AI/05_Information_Theory](https://github.com/ReddyBytes/AI-ENGINEERS-ATLAS/tree/main/01_Math_for_AI/05_Information_Theory) | Entropy, cross-entropy, KL divergence |

### Week 2 — ML Foundations

| Topic | Folder | Why It Matters |
|---|---|---|
| What is ML | [02_Machine_Learning_Foundations/01_What_is_ML](https://github.com/ReddyBytes/AI-ENGINEERS-ATLAS/tree/main/02_Machine_Learning_Foundations/01_What_is_ML) | Get the mental model right |
| Supervised vs Unsupervised | [02_Machine_Learning_Foundations/03_Supervised_Learning](https://github.com/ReddyBytes/AI-ENGINEERS-ATLAS/tree/main/02_Machine_Learning_Foundations/03_Supervised_Learning) + [04_Unsupervised](https://github.com/ReddyBytes/AI-ENGINEERS-ATLAS/tree/main/02_Machine_Learning_Foundations/04_Unsupervised_Learning) | Foundation for everything |
| Model Evaluation | [02_Machine_Learning_Foundations/05_Model_Evaluation](https://github.com/ReddyBytes/AI-ENGINEERS-ATLAS/tree/main/02_Machine_Learning_Foundations/05_Model_Evaluation) | Precision, recall, AUC — asked in every interview |
| Overfitting & Regularization | [02_Machine_Learning_Foundations/06_Overfitting_and_Regularization](https://github.com/ReddyBytes/AI-ENGINEERS-ATLAS/tree/main/02_Machine_Learning_Foundations/06_Overfitting_and_Regularization) | Bias-variance tradeoff |
| Gradient Descent | [02_Machine_Learning_Foundations/08_Gradient_Descent](https://github.com/ReddyBytes/AI-ENGINEERS-ATLAS/tree/main/02_Machine_Learning_Foundations/08_Gradient_Descent) | Understand how models actually learn |
| Feature Engineering | [02_Machine_Learning_Foundations/07_Feature_Engineering](https://github.com/ReddyBytes/AI-ENGINEERS-ATLAS/tree/main/02_Machine_Learning_Foundations/07_Feature_Engineering) | Encoding, scaling, selection |

### Week 3 — Classical ML Algorithms

| Algorithm | Folder | Interview Weight |
|---|---|---|
| Linear + Logistic Regression | [03_Classical_ML_Algorithms/01_Linear_Regression](https://github.com/ReddyBytes/AI-ENGINEERS-ATLAS/tree/main/03_Classical_ML_Algorithms/01_Linear_Regression) + [02_Logistic_Regression](https://github.com/ReddyBytes/AI-ENGINEERS-ATLAS/tree/main/03_Classical_ML_Algorithms/02_Logistic_Regression) | ⭐⭐⭐ Very high |
| Decision Trees + Random Forests | [03_Classical_ML_Algorithms/03_Decision_Trees](https://github.com/ReddyBytes/AI-ENGINEERS-ATLAS/tree/main/03_Classical_ML_Algorithms/03_Decision_Trees) + [04_Random_Forests](https://github.com/ReddyBytes/AI-ENGINEERS-ATLAS/tree/main/03_Classical_ML_Algorithms/04_Random_Forests) | ⭐⭐⭐ Very high |
| SVM | [03_Classical_ML_Algorithms/05_SVM](https://github.com/ReddyBytes/AI-ENGINEERS-ATLAS/tree/main/03_Classical_ML_Algorithms/05_SVM) | ⭐⭐ High |
| XGBoost & Boosting | [03_Classical_ML_Algorithms/09_XGBoost_and_Boosting](https://github.com/ReddyBytes/AI-ENGINEERS-ATLAS/tree/main/03_Classical_ML_Algorithms/09_XGBoost_and_Boosting) | ⭐⭐⭐ Very high (industry standard) |
| K-Means + PCA | [03_Classical_ML_Algorithms/06_K_Means](https://github.com/ReddyBytes/AI-ENGINEERS-ATLAS/tree/main/03_Classical_ML_Algorithms/06_K_Means) + [07_PCA](https://github.com/ReddyBytes/AI-ENGINEERS-ATLAS/tree/main/03_Classical_ML_Algorithms/07_PCA) | ⭐⭐ High |
| Time Series | [03_Classical_ML_Algorithms/10_Time_Series_Analysis](https://github.com/ReddyBytes/AI-ENGINEERS-ATLAS/tree/main/03_Classical_ML_Algorithms/10_Time_Series_Analysis) | ⭐⭐ High (finance/e-commerce roles) |
| Recommendation Systems | [03_Classical_ML_Algorithms/11_Recommendation_Systems](https://github.com/ReddyBytes/AI-ENGINEERS-ATLAS/tree/main/03_Classical_ML_Algorithms/11_Recommendation_Systems) | ⭐⭐ High |
| Anomaly Detection | [03_Classical_ML_Algorithms/12_Anomaly_Detection](https://github.com/ReddyBytes/AI-ENGINEERS-ATLAS/tree/main/03_Classical_ML_Algorithms/12_Anomaly_Detection) | ⭐⭐ Medium-High |

**Must read:**
- [Algorithm_Comparison.md](https://github.com/ReddyBytes/AI-ENGINEERS-ATLAS/blob/main/03_Classical_ML_Algorithms/Algorithm_Comparison.md) — when to use which algorithm

### Phase 2 + Data Science Track (Python repo)
Run in parallel with Phase 2:

- [22_numpy_for_ai](https://github.com/ReddyBytes/Python-DSA-API-Mastery/tree/main/01_Python_Mastery/22_numpy_for_ai)
- [23_pandas_for_ai](https://github.com/ReddyBytes/Python-DSA-API-Mastery/tree/main/01_Python_Mastery/23_pandas_for_ai)
- [26_statistics_and_probability](https://github.com/ReddyBytes/Python-DSA-API-Mastery/tree/main/01_Python_Mastery/26_statistics_and_probability)
- [27_matplotlib_seaborn](https://github.com/ReddyBytes/Python-DSA-API-Mastery/tree/main/01_Python_Mastery/27_matplotlib_seaborn)
- [28_eda_workflow](https://github.com/ReddyBytes/Python-DSA-API-Mastery/tree/main/01_Python_Mastery/28_eda_workflow)

---

---

# PHASE 3 — SQL Fundamentals to Production

**Duration:** 2 weeks
**Repo:** [SQL-Mastery/](https://github.com/ReddyBytes/SQL-Mastery)
**Goal:** Write complex queries, optimize performance, design schemas

### Week 1 — Core SQL

| Module | Folder | Topics |
|---|---|---|
| Fundamentals | [01_fundamentals](https://github.com/ReddyBytes/SQL-Mastery/tree/main/01_fundamentals) | SELECT, WHERE, ORDER BY, DISTINCT, LIMIT |
| Querying Basics | [02_querying_basics](https://github.com/ReddyBytes/SQL-Mastery/tree/main/02_querying_basics) | Filtering, sorting, NULL handling |
| Aggregation | [03_aggregation](https://github.com/ReddyBytes/SQL-Mastery/tree/main/03_aggregation) | GROUP BY, HAVING, COUNT/SUM/AVG, window functions |
| Schema Design | [04_schema_design](https://github.com/ReddyBytes/SQL-Mastery/tree/main/04_schema_design) | Normalization, data types, constraints, indexes |
| Joins | [05_joins](https://github.com/ReddyBytes/SQL-Mastery/tree/main/05_joins) | INNER, LEFT, RIGHT, OUTER, self-joins, join patterns |

### Week 2 — Advanced SQL + Production

| Module | Folder | Topics |
|---|---|---|
| Advanced Queries | [06_advanced_queries](https://github.com/ReddyBytes/SQL-Mastery/tree/main/06_advanced_queries) | CTEs, subqueries, CASE, string/date functions |
| Data Modification | [07_data_modification](https://github.com/ReddyBytes/SQL-Mastery/tree/main/07_data_modification) | INSERT, UPDATE, DELETE, transactions, ACID |
| Performance | [08_performance](https://github.com/ReddyBytes/SQL-Mastery/tree/main/08_performance) | EXPLAIN ANALYZE, index strategy, query optimization |
| Real World | [09_real_world](https://github.com/ReddyBytes/SQL-Mastery/tree/main/09_real_world) | Views, stored procedures, triggers, SQL with Python |

**Also cover from Python repo:**
- [30_sql_with_python](https://github.com/ReddyBytes/Python-DSA-API-Mastery/tree/main/01_Python_Mastery/30_sql_with_python) — SQLAlchemy ORM + psycopg2

### Phase 3 Interview Prep

- [SQL-Mastery/99_interview_master](https://github.com/ReddyBytes/SQL-Mastery/tree/main/99_interview_master) — 26 Q&As + 25 scenario questions

---

---

# PHASE 4 — Deep Learning + NLP

**Duration:** 3 weeks
**Repo:** [AI-ENGINEERS-ATLAS/](https://github.com/ReddyBytes/AI-ENGINEERS-ATLAS)
**Goal:** Build and explain neural networks — ANN, CNN, RNN, LSTM, NLP pipeline

### Week 1 — Neural Network Foundations

| Topic | Folder | Focus |
|---|---|---|
| Perceptron | [04_Neural_Networks_and_Deep_Learning/01_Perceptron](https://github.com/ReddyBytes/AI-ENGINEERS-ATLAS/tree/main/04_Neural_Networks_and_Deep_Learning/01_Perceptron) | Biological → mathematical model |
| MLPs | [04_Neural_Networks_and_Deep_Learning/02_MLPs](https://github.com/ReddyBytes/AI-ENGINEERS-ATLAS/tree/main/04_Neural_Networks_and_Deep_Learning/02_MLPs) | Hidden layers, universal approximation theorem |
| Activation Functions | [04_Neural_Networks_and_Deep_Learning/03_Activation_Functions](https://github.com/ReddyBytes/AI-ENGINEERS-ATLAS/tree/main/04_Neural_Networks_and_Deep_Learning/03_Activation_Functions) | Sigmoid, ReLU, GELU — why each exists |
| Forward Propagation | [04_Neural_Networks_and_Deep_Learning/05_Forward_Propagation](https://github.com/ReddyBytes/AI-ENGINEERS-ATLAS/tree/main/04_Neural_Networks_and_Deep_Learning/05_Forward_Propagation) | Full matrix math walkthrough |
| Backpropagation | [04_Neural_Networks_and_Deep_Learning/06_Backpropagation](https://github.com/ReddyBytes/AI-ENGINEERS-ATLAS/tree/main/04_Neural_Networks_and_Deep_Learning/06_Backpropagation) | Chain rule, gradient flow — must understand deeply |
| Optimizers | [04_Neural_Networks_and_Deep_Learning/07_Optimizers](https://github.com/ReddyBytes/AI-ENGINEERS-ATLAS/tree/main/04_Neural_Networks_and_Deep_Learning/07_Optimizers) | SGD → Adam — Comparison.md is essential |

### Week 2 — Deep Learning Architectures

| Topic | Folder | Focus |
|---|---|---|
| Regularization | [04_Neural_Networks_and_Deep_Learning/08_Regularization](https://github.com/ReddyBytes/AI-ENGINEERS-ATLAS/tree/main/04_Neural_Networks_and_Deep_Learning/08_Regularization) | Dropout, batch norm, weight decay |
| CNNs | [04_Neural_Networks_and_Deep_Learning/09_CNNs](https://github.com/ReddyBytes/AI-ENGINEERS-ATLAS/tree/main/04_Neural_Networks_and_Deep_Learning/09_CNNs) | Convolutions, pooling, ResNet — Architecture_Deep_Dive.md |
| RNNs + LSTMs | [04_Neural_Networks_and_Deep_Learning/10_RNNs](https://github.com/ReddyBytes/AI-ENGINEERS-ATLAS/tree/main/04_Neural_Networks_and_Deep_Learning/10_RNNs) | Sequential data, vanishing gradient fix |
| Training Techniques | [04_Neural_Networks_and_Deep_Learning/12_Training_Techniques](https://github.com/ReddyBytes/AI-ENGINEERS-ATLAS/tree/main/04_Neural_Networks_and_Deep_Learning/12_Training_Techniques) | Transfer learning, mixed precision |

### Week 3 — NLP Foundations

| Topic | Folder | Focus |
|---|---|---|
| Text Preprocessing | [05_NLP_Foundations/01_Text_Preprocessing](https://github.com/ReddyBytes/AI-ENGINEERS-ATLAS/tree/main/05_NLP_Foundations/01_Text_Preprocessing) | Cleaning, stemming, lemmatization |
| Tokenization | [05_NLP_Foundations/02_Tokenization](https://github.com/ReddyBytes/AI-ENGINEERS-ATLAS/tree/main/05_NLP_Foundations/02_Tokenization) | BPE, sentencepiece — critical for LLM understanding |
| TF-IDF + Bag of Words | [05_NLP_Foundations/03_Bag_of_Words_and_TF_IDF](https://github.com/ReddyBytes/AI-ENGINEERS-ATLAS/tree/main/05_NLP_Foundations/03_Bag_of_Words_and_TF_IDF) | Sparse representations |
| Word Embeddings | [05_NLP_Foundations/04_Word_Embeddings](https://github.com/ReddyBytes/AI-ENGINEERS-ATLAS/tree/main/05_NLP_Foundations/04_Word_Embeddings) | Word2Vec, GloVe, FastText |
| Semantic Similarity | [05_NLP_Foundations/05_Semantic_Similarity](https://github.com/ReddyBytes/AI-ENGINEERS-ATLAS/tree/main/05_NLP_Foundations/05_Semantic_Similarity) | Cosine similarity, nearest neighbor |

**Also cover from Python repo:**
- [25_python_ai_ecosystem](https://github.com/ReddyBytes/Python-DSA-API-Mastery/tree/main/01_Python_Mastery/25_python_ai_ecosystem) — ML library overview
- [29_web_scraping](https://github.com/ReddyBytes/Python-DSA-API-Mastery/tree/main/01_Python_Mastery/29_web_scraping) — data collection

---

---

# PHASE 5 — APIs — REST to Production

**Duration:** 3 weeks
**Repo:** [Python-DSA-API-Mastery/03_API_Mastery/](https://github.com/ReddyBytes/Python-DSA-API-Mastery/tree/main/03_API_Mastery)
**Goal:** Build, secure, test, and deploy production-grade APIs

### Week 1 — REST Foundations + FastAPI

| Module | Folder | Topics |
|---|---|---|
| What is an API | [01_what_is_an_api](https://github.com/ReddyBytes/Python-DSA-API-Mastery/tree/main/03_API_Mastery/01_what_is_an_api) | HTTP fundamentals, request/response anatomy |
| REST Fundamentals | [02_rest_fundamentals](https://github.com/ReddyBytes/Python-DSA-API-Mastery/tree/main/03_API_Mastery/02_rest_fundamentals) | 6 constraints, statelessness, idempotency |
| REST Best Practices | [03_rest_best_practices](https://github.com/ReddyBytes/Python-DSA-API-Mastery/tree/main/03_API_Mastery/03_rest_best_practices) | URL naming, pagination, error formats |
| Data Formats | [04_data_formats](https://github.com/ReddyBytes/Python-DSA-API-Mastery/tree/main/03_API_Mastery/04_data_formats) | JSON, Pydantic validation, serialization |
| Authentication | [05_authentication](https://github.com/ReddyBytes/Python-DSA-API-Mastery/tree/main/03_API_Mastery/05_authentication) | API keys, JWT, OAuth2, CORS |
| Error Handling | [06_error_handling_standards](https://github.com/ReddyBytes/Python-DSA-API-Mastery/tree/main/03_API_Mastery/06_error_handling_standards) | RFC 7807, validation errors, retry logic |
| FastAPI | [07_fastapi](https://github.com/ReddyBytes/Python-DSA-API-Mastery/tree/main/03_API_Mastery/07_fastapi) | Routes, dependency injection, background tasks, WebSockets |

### Week 2 — API Advanced Patterns

| Module | Folder | Topics |
|---|---|---|
| Versioning | [08_versioning_standards](https://github.com/ReddyBytes/Python-DSA-API-Mastery/tree/main/03_API_Mastery/08_versioning_standards) | URL vs header versioning, breaking changes |
| Performance | [09_api_performance_scaling](https://github.com/ReddyBytes/Python-DSA-API-Mastery/tree/main/03_API_Mastery/09_api_performance_scaling) | N+1 problem, connection pooling, caching |
| Testing | [10_testing_documentation](https://github.com/ReddyBytes/Python-DSA-API-Mastery/tree/main/03_API_Mastery/10_testing_documentation) | TestClient, pytest fixtures, OpenAPI |
| Security | [11_api_security_production](https://github.com/ReddyBytes/Python-DSA-API-Mastery/tree/main/03_API_Mastery/11_api_security_production) | OWASP Top 10, input validation, rate limiting |
| Deployment | [12_production_deployment](https://github.com/ReddyBytes/Python-DSA-API-Mastery/tree/main/03_API_Mastery/12_production_deployment) | Docker + Gunicorn/Uvicorn, K8s, CI/CD |

### Week 3 — Advanced API Protocols

| Module | Folder | Topics |
|---|---|---|
| GraphQL | [13_graphql](https://github.com/ReddyBytes/Python-DSA-API-Mastery/tree/main/03_API_Mastery/13_graphql) | Schema-first design, mutations, DataLoader |
| gRPC | [14_grpc](https://github.com/ReddyBytes/Python-DSA-API-Mastery/tree/main/03_API_Mastery/14_grpc) | Protocol Buffers, streaming modes |
| API Gateway | [15_api_gateway](https://github.com/ReddyBytes/Python-DSA-API-Mastery/tree/main/03_API_Mastery/15_api_gateway) | Rate limiting, BFF pattern |
| Design Patterns | [16_api_design_patterns](https://github.com/ReddyBytes/Python-DSA-API-Mastery/tree/main/03_API_Mastery/16_api_design_patterns) | Idempotency, long-running ops, bulk operations |
| WebSockets | [17_websockets](https://github.com/ReddyBytes/Python-DSA-API-Mastery/tree/main/03_API_Mastery/17_websockets) | Full-duplex, broadcast, reconnection |
| OpenTelemetry | [19_opentelemetry](https://github.com/ReddyBytes/Python-DSA-API-Mastery/tree/main/03_API_Mastery/19_opentelemetry) | Traces, metrics, OTEL collector |

### Phase 5 Capstone

- [01_Ecommerce_API_FastAPI](https://github.com/ReddyBytes/Python-DSA-API-Mastery/tree/main/05_Capstone_Projects/01_Ecommerce_API_FastAPI) — full production FastAPI project

### Phase 5 Interview Prep

- [api_questions.md](https://github.com/ReddyBytes/Python-DSA-API-Mastery/blob/main/03_API_Mastery/99_interview_master/api_questions.md)
- [scenario_based_questions.md](https://github.com/ReddyBytes/Python-DSA-API-Mastery/blob/main/03_API_Mastery/99_interview_master/scenario_based_questions.md) — 12 production scenarios

---

---

# PHASE 6 — Transformers + LLMs + Prompt Engineering

**Duration:** 3 weeks
**Repo:** [AI-ENGINEERS-ATLAS/](https://github.com/ReddyBytes/AI-ENGINEERS-ATLAS)
**Goal:** Understand how LLMs work from architecture to API usage

### Week 1 — Transformer Architecture

| Topic | Folder | Must Read |
|---|---|---|
| Before Transformers | [06_Transformers/01_Sequence_Models_Before_Transformers](https://github.com/ReddyBytes/AI-ENGINEERS-ATLAS/tree/main/06_Transformers/01_Sequence_Models_Before_Transformers) | Why RNNs failed |
| Attention Mechanism | [06_Transformers/02_Attention_Mechanism](https://github.com/ReddyBytes/AI-ENGINEERS-ATLAS/tree/main/06_Transformers/02_Attention_Mechanism) | Visual_Guide.md + Math_Intuition.md |
| Self-Attention | [06_Transformers/03_Self_Attention](https://github.com/ReddyBytes/AI-ENGINEERS-ATLAS/tree/main/06_Transformers/03_Self_Attention) | How tokens attend to each other |
| Multi-Head Attention | [06_Transformers/04_Multi_Head_Attention](https://github.com/ReddyBytes/AI-ENGINEERS-ATLAS/tree/main/06_Transformers/04_Multi_Head_Attention) | Architecture_Deep_Dive.md — the core insight |
| Positional Encoding | [06_Transformers/05_Positional_Encoding](https://github.com/ReddyBytes/AI-ENGINEERS-ATLAS/tree/main/06_Transformers/05_Positional_Encoding) | RoPE vs sinusoidal |
| Full Architecture | [06_Transformers/06_Transformer_Architecture](https://github.com/ReddyBytes/AI-ENGINEERS-ATLAS/tree/main/06_Transformers/06_Transformer_Architecture) | Encoder-decoder, layer norm, residuals |
| BERT vs GPT | [06_Transformers/08_BERT](https://github.com/ReddyBytes/AI-ENGINEERS-ATLAS/tree/main/06_Transformers/08_BERT) + [09_GPT](https://github.com/ReddyBytes/AI-ENGINEERS-ATLAS/tree/main/06_Transformers/09_GPT) | Bidirectional vs autoregressive |

### Week 2 — LLM Internals

| Topic | Folder | Must Read |
|---|---|---|
| LLM Fundamentals | [07_Large_Language_Models/01_LLM_Fundamentals](https://github.com/ReddyBytes/AI-ENGINEERS-ATLAS/tree/main/07_Large_Language_Models/01_LLM_Fundamentals) | Scale, emergence, History_Timeline.md |
| Text Generation | [07_Large_Language_Models/02_How_LLMs_Generate_Text](https://github.com/ReddyBytes/AI-ENGINEERS-ATLAS/tree/main/07_Large_Language_Models/02_How_LLMs_Generate_Text) | Temperature, top-p, top-k — Visual_Guide.md |
| Pretraining | [07_Large_Language_Models/03_Pretraining](https://github.com/ReddyBytes/AI-ENGINEERS-ATLAS/tree/main/07_Large_Language_Models/03_Pretraining) | Data curation, scaling laws, Chinchilla |
| RLHF | [07_Large_Language_Models/06_RLHF](https://github.com/ReddyBytes/AI-ENGINEERS-ATLAS/tree/main/07_Large_Language_Models/06_RLHF) | Reward models, PPO, DPO — Architecture_Deep_Dive.md |
| Hallucination | [07_Large_Language_Models/08_Hallucination_and_Alignment](https://github.com/ReddyBytes/AI-ENGINEERS-ATLAS/tree/main/07_Large_Language_Models/08_Hallucination_and_Alignment) | Detection and mitigation |
| Ollama & Local LLMs | [07_Large_Language_Models/10_Ollama_Local_LLMs](https://github.com/ReddyBytes/AI-ENGINEERS-ATLAS/tree/main/07_Large_Language_Models/10_Ollama_Local_LLMs) | Run models locally, REST API |
| Reasoning Models | [07_Large_Language_Models/11_Reasoning_Models](https://github.com/ReddyBytes/AI-ENGINEERS-ATLAS/tree/main/07_Large_Language_Models/11_Reasoning_Models) | Chain-of-thought, o1/Claude extended thinking |

### Week 3 — LLM Applications + Prompt Engineering

| Topic | Folder | Must Read |
|---|---|---|
| Prompt Engineering | [08_LLM_Applications/01_Prompt_Engineering](https://github.com/ReddyBytes/AI-ENGINEERS-ATLAS/tree/main/08_LLM_Applications/01_Prompt_Engineering) | Patterns.md + Common_Mistakes.md |
| Tool Calling | [08_LLM_Applications/02_Tool_Calling](https://github.com/ReddyBytes/AI-ENGINEERS-ATLAS/tree/main/08_LLM_Applications/02_Tool_Calling) | Architecture_Deep_Dive.md + Code_Example.md |
| Structured Outputs | [08_LLM_Applications/03_Structured_Outputs](https://github.com/ReddyBytes/AI-ENGINEERS-ATLAS/tree/main/08_LLM_Applications/03_Structured_Outputs) | JSON mode, extraction pipelines |
| Embeddings | [08_LLM_Applications/04_Embeddings](https://github.com/ReddyBytes/AI-ENGINEERS-ATLAS/tree/main/08_LLM_Applications/04_Embeddings) | Embedding models, batching |
| Vector Databases | [08_LLM_Applications/05_Vector_Databases](https://github.com/ReddyBytes/AI-ENGINEERS-ATLAS/tree/main/08_LLM_Applications/05_Vector_Databases) | Pinecone, pgvector, FAISS — Comparison.md |
| Semantic Search | [08_LLM_Applications/06_Semantic_Search](https://github.com/ReddyBytes/AI-ENGINEERS-ATLAS/tree/main/08_LLM_Applications/06_Semantic_Search) | Dense retrieval, re-ranking |

---

---

# PHASE 7 — RAG Systems + AI Agents

**Duration:** 4 weeks
**Repo:** [AI-ENGINEERS-ATLAS/](https://github.com/ReddyBytes/AI-ENGINEERS-ATLAS)
**Goal:** Build production-grade RAG and agentic AI systems — the most hired skill in 2025–26

### Week 1 — RAG Fundamentals + Pipeline

| Topic | Folder | Focus |
|---|---|---|
| RAG Fundamentals | [09_RAG_Systems/01_RAG_Fundamentals](https://github.com/ReddyBytes/AI-ENGINEERS-ATLAS/tree/main/09_RAG_Systems/01_RAG_Fundamentals) | Why RAG, architecture overview |
| Document Ingestion | [09_RAG_Systems/02_Document_Ingestion](https://github.com/ReddyBytes/AI-ENGINEERS-ATLAS/tree/main/09_RAG_Systems/02_Document_Ingestion) | PDF, HTML, metadata extraction |
| Chunking Strategies | [09_RAG_Systems/03_Chunking_Strategies](https://github.com/ReddyBytes/AI-ENGINEERS-ATLAS/tree/main/09_RAG_Systems/03_Chunking_Strategies) | Fixed vs recursive vs semantic — Comparison.md |
| Embedding & Indexing | [09_RAG_Systems/04_Embedding_and_Indexing](https://github.com/ReddyBytes/AI-ENGINEERS-ATLAS/tree/main/09_RAG_Systems/04_Embedding_and_Indexing) | HNSW, IVF, indexing pipelines |
| Retrieval Pipeline | [09_RAG_Systems/05_Retrieval_Pipeline](https://github.com/ReddyBytes/AI-ENGINEERS-ATLAS/tree/main/09_RAG_Systems/05_Retrieval_Pipeline) | Top-k, MMR, re-ranking, hybrid search |

### Week 2 — Advanced RAG + Build Project

| Topic | Folder | Focus |
|---|---|---|
| Context Assembly | [09_RAG_Systems/06_Context_Assembly](https://github.com/ReddyBytes/AI-ENGINEERS-ATLAS/tree/main/09_RAG_Systems/06_Context_Assembly) | Prompt construction, deduplication |
| Advanced RAG | [09_RAG_Systems/07_Advanced_RAG_Techniques](https://github.com/ReddyBytes/AI-ENGINEERS-ATLAS/tree/main/09_RAG_Systems/07_Advanced_RAG_Techniques) | HyDE, RAPTOR, multi-hop — Architecture_Deep_Dive.md |
| RAG Evaluation | [09_RAG_Systems/08_RAG_Evaluation](https://github.com/ReddyBytes/AI-ENGINEERS-ATLAS/tree/main/09_RAG_Systems/08_RAG_Evaluation) | RAGAS, faithfulness, Evaluation_at_Scale.md |
| GraphRAG | [09_RAG_Systems/10_GraphRAG](https://github.com/ReddyBytes/AI-ENGINEERS-ATLAS/tree/main/09_RAG_Systems/10_GraphRAG) | Entity extraction, knowledge graphs |
| CAG | [09_RAG_Systems/11_CAG_Cache_Augmented_Generation](https://github.com/ReddyBytes/AI-ENGINEERS-ATLAS/tree/main/09_RAG_Systems/11_CAG_Cache_Augmented_Generation) | KV cache reuse, prompt caching API |
| Build a RAG App | [09_RAG_Systems/09_Build_a_RAG_App](https://github.com/ReddyBytes/AI-ENGINEERS-ATLAS/tree/main/09_RAG_Systems/09_Build_a_RAG_App) | Full end-to-end project |

### Week 3 — AI Agents

| Topic | Folder | Focus |
|---|---|---|
| Agent Fundamentals | [10_AI_Agents/01_Agent_Fundamentals](https://github.com/ReddyBytes/AI-ENGINEERS-ATLAS/tree/main/10_AI_Agents/01_Agent_Fundamentals) | Perception → reasoning → action loop |
| ReAct Pattern | [10_AI_Agents/02_ReAct_Pattern](https://github.com/ReddyBytes/AI-ENGINEERS-ATLAS/tree/main/10_AI_Agents/02_ReAct_Pattern) | Thought/Action/Observation — Architecture_Deep_Dive.md |
| Tool Use | [10_AI_Agents/03_Tool_Use](https://github.com/ReddyBytes/AI-ENGINEERS-ATLAS/tree/main/10_AI_Agents/03_Tool_Use) | Schemas, execution, error recovery |
| Agent Memory | [10_AI_Agents/04_Agent_Memory](https://github.com/ReddyBytes/AI-ENGINEERS-ATLAS/tree/main/10_AI_Agents/04_Agent_Memory) | Working, episodic, semantic, procedural |
| Planning | [10_AI_Agents/05_Planning_and_Reasoning](https://github.com/ReddyBytes/AI-ENGINEERS-ATLAS/tree/main/10_AI_Agents/05_Planning_and_Reasoning) | Task decomposition, tree-of-thought |
| Reflection | [10_AI_Agents/06_Reflection_and_Self_Correction](https://github.com/ReddyBytes/AI-ENGINEERS-ATLAS/tree/main/10_AI_Agents/06_Reflection_and_Self_Correction) | Error_Recovery_Patterns.md |

### Week 4 — Multi-Agent + MCP + LangGraph

| Topic | Folder | Focus |
|---|---|---|
| Multi-Agent Systems | [10_AI_Agents/07_Multi_Agent_Systems](https://github.com/ReddyBytes/AI-ENGINEERS-ATLAS/tree/main/10_AI_Agents/07_Multi_Agent_Systems) | Orchestrator-worker, debate, specialization |
| Build an Agent | [10_AI_Agents/09_Build_an_Agent](https://github.com/ReddyBytes/AI-ENGINEERS-ATLAS/tree/main/10_AI_Agents/09_Build_an_Agent) | Full capstone project |
| MCP Protocol | [11_MCP_Model_Context_Protocol](https://github.com/ReddyBytes/AI-ENGINEERS-ATLAS/tree/main/11_MCP_Model_Context_Protocol) | All 9 topics — MCP is rapidly becoming industry standard |
| LangGraph | [15_LangGraph](https://github.com/ReddyBytes/AI-ENGINEERS-ATLAS/tree/main/15_LangGraph) | All 8 topics — stateful agents, human-in-the-loop |

---

---

# PHASE 8 — Production AI + System Design

**Duration:** 4 weeks
**Repos:** [AI-ENGINEERS-ATLAS/](https://github.com/ReddyBytes/AI-ENGINEERS-ATLAS) + [Python-DSA-API-Mastery/04_System_Design_Mastery/](https://github.com/ReddyBytes/Python-DSA-API-Mastery/tree/main/04_System_Design_Mastery)
**Goal:** Design and operate scalable AI systems — what separates 15 LPA from 25 LPA

### Week 1 — Production AI

| Topic | Folder | Focus |
|---|---|---|
| Model Serving | [12_Production_AI/01_Model_Serving](https://github.com/ReddyBytes/AI-ENGINEERS-ATLAS/tree/main/12_Production_AI/01_Model_Serving) | REST vs gRPC, batching, replicas |
| Latency Optimization | [12_Production_AI/02_Latency_Optimization](https://github.com/ReddyBytes/AI-ENGINEERS-ATLAS/tree/main/12_Production_AI/02_Latency_Optimization) | Quantization, speculative decoding, KV cache |
| Cost Optimization | [12_Production_AI/03_Cost_Optimization](https://github.com/ReddyBytes/AI-ENGINEERS-ATLAS/tree/main/12_Production_AI/03_Cost_Optimization) | Cost_Case_Studies.md + Model_Routing_Guide.md |
| Caching Strategies | [12_Production_AI/04_Caching_Strategies](https://github.com/ReddyBytes/AI-ENGINEERS-ATLAS/tree/main/12_Production_AI/04_Caching_Strategies) | Exact-match, semantic, prompt caching |
| Observability | [12_Production_AI/05_Observability](https://github.com/ReddyBytes/AI-ENGINEERS-ATLAS/tree/main/12_Production_AI/05_Observability) | LLM-specific telemetry, logs, traces |
| Evaluation Pipelines | [12_Production_AI/06_Evaluation_Pipelines](https://github.com/ReddyBytes/AI-ENGINEERS-ATLAS/tree/main/12_Production_AI/06_Evaluation_Pipelines) | CI/CD for AI, regression testing |
| Safety & Guardrails | [12_Production_AI/07_Safety_and_Guardrails](https://github.com/ReddyBytes/AI-ENGINEERS-ATLAS/tree/main/12_Production_AI/07_Safety_and_Guardrails) | Prompt injection defense, output validation |

**Must read:**
- [PRODUCTION_CHECKLIST.md](https://github.com/ReddyBytes/AI-ENGINEERS-ATLAS/blob/main/12_Production_AI/Production_Checklist.md) — use before every deployment

### Week 2 — AI System Design Case Studies

All 8 case studies in [13_AI_System_Design](https://github.com/ReddyBytes/AI-ENGINEERS-ATLAS/tree/main/13_AI_System_Design) — read each Architecture_Blueprint + Interview_QA:

| Case Study | Folder |
|---|---|
| Customer Support Agent | [01_Customer_Support_Agent](https://github.com/ReddyBytes/AI-ENGINEERS-ATLAS/tree/main/13_AI_System_Design/01_Customer_Support_Agent) |
| RAG Document Search | [02_RAG_Document_Search_System](https://github.com/ReddyBytes/AI-ENGINEERS-ATLAS/tree/main/13_AI_System_Design/02_RAG_Document_Search_System) |
| AI Coding Assistant | [03_AI_Coding_Assistant](https://github.com/ReddyBytes/AI-ENGINEERS-ATLAS/tree/main/13_AI_System_Design/03_AI_Coding_Assistant) |
| AI Research Assistant | [04_AI_Research_Assistant](https://github.com/ReddyBytes/AI-ENGINEERS-ATLAS/tree/main/13_AI_System_Design/04_AI_Research_Assistant) |
| Multi-Agent Workflow | [05_Multi_Agent_Workflow](https://github.com/ReddyBytes/AI-ENGINEERS-ATLAS/tree/main/13_AI_System_Design/05_Multi_Agent_Workflow) |
| Recommendation System with RAG | [06_Recommendation_System_with_RAG](https://github.com/ReddyBytes/AI-ENGINEERS-ATLAS/tree/main/13_AI_System_Design/06_Recommendation_System_with_RAG) |
| AI Content Moderation | [07_AI_Content_Moderation_Pipeline](https://github.com/ReddyBytes/AI-ENGINEERS-ATLAS/tree/main/13_AI_System_Design/07_AI_Content_Moderation_Pipeline) |
| Cost-Aware AI Router | [08_Cost_Aware_AI_Router](https://github.com/ReddyBytes/AI-ENGINEERS-ATLAS/tree/main/13_AI_System_Design/08_Cost_Aware_AI_Router) |

- [System_Design_Framework.md](https://github.com/ReddyBytes/AI-ENGINEERS-ATLAS/blob/main/13_AI_System_Design/System_Design_Framework.md) — 5-step framework for any design interview

### Week 3 — System Design Foundations

| Module | Folder | Topics |
|---|---|---|
| Computer Fundamentals | [04_System_Design_Mastery/00_computer_fundamentals](https://github.com/ReddyBytes/Python-DSA-API-Mastery/tree/main/04_System_Design_Mastery/00_computer_fundamentals) | CPU, memory, I/O, syscalls |
| Networking | [01_networking_basics](https://github.com/ReddyBytes/Python-DSA-API-Mastery/tree/main/04_System_Design_Mastery/01_networking_basics) | TCP/UDP, HTTP/1–3, DNS, TLS |
| System Fundamentals | [02_system_fundamentals](https://github.com/ReddyBytes/Python-DSA-API-Mastery/tree/main/04_System_Design_Mastery/02_system_fundamentals) | Latency, throughput, CAP theorem, SLOs |
| Databases | [05_databases](https://github.com/ReddyBytes/Python-DSA-API-Mastery/tree/main/04_System_Design_Mastery/05_databases) | SQL vs NoSQL, ACID, indexing |
| Caching | [06_caching](https://github.com/ReddyBytes/Python-DSA-API-Mastery/tree/main/04_System_Design_Mastery/06_caching) | Redis patterns, eviction, cache-aside |
| Load Balancing | [08_load_balancing](https://github.com/ReddyBytes/Python-DSA-API-Mastery/tree/main/04_System_Design_Mastery/08_load_balancing) | Consistent hashing, health checks |
| Message Queues | [09_message_queues](https://github.com/ReddyBytes/Python-DSA-API-Mastery/tree/main/04_System_Design_Mastery/09_message_queues) | Kafka, pub/sub, at-least-once delivery |
| Distributed Systems | [10_distributed_systems](https://github.com/ReddyBytes/Python-DSA-API-Mastery/tree/main/04_System_Design_Mastery/10_distributed_systems) | Raft, replication, partition tolerance |

### Week 4 — Advanced System Design

| Module | Folder | Topics |
|---|---|---|
| Scalability Patterns | [11_scalability_patterns](https://github.com/ReddyBytes/Python-DSA-API-Mastery/tree/main/04_System_Design_Mastery/11_scalability_patterns) | CQRS, event sourcing, saga |
| Microservices | [12_microservices](https://github.com/ReddyBytes/Python-DSA-API-Mastery/tree/main/04_System_Design_Mastery/12_microservices) | Service mesh, circuit breakers |
| Security | [13_security](https://github.com/ReddyBytes/Python-DSA-API-Mastery/tree/main/04_System_Design_Mastery/13_security) | OAuth2, JWT, DDoS mitigation |
| Observability | [14_observability](https://github.com/ReddyBytes/Python-DSA-API-Mastery/tree/main/04_System_Design_Mastery/14_observability) | Prometheus, ELK, Jaeger |
| Cloud Architecture | [15_cloud_architecture](https://github.com/ReddyBytes/Python-DSA-API-Mastery/tree/main/04_System_Design_Mastery/15_cloud_architecture) | AWS/GCP, serverless, multi-region |
| Case Studies | [22_case_studies](https://github.com/ReddyBytes/Python-DSA-API-Mastery/tree/main/04_System_Design_Mastery/22_case_studies) | URL Shortener, Twitter, Netflix, Uber, WhatsApp |
| Interview Framework | [23_interview_framework](https://github.com/ReddyBytes/Python-DSA-API-Mastery/tree/main/04_System_Design_Mastery/23_interview_framework) | 45-minute structured approach |

---

---

# PHASE 9 — Linux + AWS + Terraform + Docker + Kubernetes

**Duration:** 3 weeks
**Repos:** [Linux-Terraform-AWS-Mastery/](https://github.com/ReddyBytes/Linux-Terraform-AWS-Mastery) + [Container-Engineering/](https://github.com/ReddyBytes/Container-Engineering) + `linux-guide/`
**Goal:** Deploy and manage AI/ML infrastructure — required at senior level

### Week 1 — Linux + Bash Scripting

| Module | Folder | Topics |
|---|---|---|
| Linux Fundamentals | [01_Linux/01_fundamentals](https://github.com/ReddyBytes/Linux-Terraform-AWS-Mastery/tree/main/01_Linux/01_fundamentals) | Filesystem, shell basics, package management |
| Users & Permissions | [01_Linux/04_users_permissions](https://github.com/ReddyBytes/Linux-Terraform-AWS-Mastery/tree/main/01_Linux/04_users_permissions) | chmod, chown, sudo, file permissions |
| Processes | [01_Linux/05_processes](https://github.com/ReddyBytes/Linux-Terraform-AWS-Mastery/tree/main/01_Linux/05_processes) | ps, kill, signals, systemd |
| Networking | [01_Linux/06_networking](https://github.com/ReddyBytes/Linux-Terraform-AWS-Mastery/tree/main/01_Linux/06_networking) | SSH, curl, netstat, port management |
| Bash Scripting | [02_Bash-Scripting](https://github.com/ReddyBytes/Linux-Terraform-AWS-Mastery/tree/main/02_Bash-Scripting) | All 8 modules — automate everything |

**Quick reference:**
- `linux-guide/` — use as daily reference for commands

### Week 2 — AWS + Terraform

| Module | Folder | Topics |
|---|---|---|
| Cloud Foundations | [03_AWS/01_cloud_foundations](https://github.com/ReddyBytes/Linux-Terraform-AWS-Mastery/tree/main/03_AWS/01_cloud_foundations) | IaaS/PaaS/SaaS, shared responsibility |
| EC2 + VPC | [03_AWS/03_compute](https://github.com/ReddyBytes/Linux-Terraform-AWS-Mastery/tree/main/03_AWS/03_compute) + [05_networking](https://github.com/ReddyBytes/Linux-Terraform-AWS-Mastery/tree/main/03_AWS/05_networking) | Instances, security groups, subnets |
| S3 + IAM | [03_AWS/04_storage](https://github.com/ReddyBytes/Linux-Terraform-AWS-Mastery/tree/main/03_AWS/04_storage) + [06_security](https://github.com/ReddyBytes/Linux-Terraform-AWS-Mastery/tree/main/03_AWS/06_security) | Object storage, roles, least privilege |
| RDS + CloudWatch | [03_AWS/07_databases](https://github.com/ReddyBytes/Linux-Terraform-AWS-Mastery/tree/main/03_AWS/07_databases) + [08_monitoring](https://github.com/ReddyBytes/Linux-Terraform-AWS-Mastery/tree/main/03_AWS/08_monitoring) | Managed databases, metrics, alarms |
| ECS + Lambda | [03_AWS/10_containers](https://github.com/ReddyBytes/Linux-Terraform-AWS-Mastery/tree/main/03_AWS/10_containers) + [11_serverless](https://github.com/ReddyBytes/Linux-Terraform-AWS-Mastery/tree/main/03_AWS/11_serverless) | Container services, functions |
| Terraform | [04_Terraform](https://github.com/ReddyBytes/Linux-Terraform-AWS-Mastery/tree/main/04_Terraform) | All 9 modules — IaC from intro to AWS with Terraform |

### Week 3 — Docker + Kubernetes

| Module | Folder | Topics |
|---|---|---|
| Docker | [Container-Engineering/01_Docker](https://github.com/ReddyBytes/Container-Engineering/tree/main/01_Docker) | Dockerfile, volumes, networking, Compose, multi-stage |
| Kubernetes | [Container-Engineering/02_Kubernetes](https://github.com/ReddyBytes/Container-Engineering/tree/main/02_Kubernetes) | Pods, Deployments, Services, Ingress, RBAC, HPA |
| Docker to K8s | [Container-Engineering/03_Docker_to_K8s](https://github.com/ReddyBytes/Container-Engineering/tree/main/03_Docker_to_K8s) | Migration workflow |
| Projects | [Container-Engineering/04_Projects](https://github.com/ReddyBytes/Container-Engineering/tree/main/04_Projects) | Dockerize + deploy a Python app end-to-end |

---

---

# PHASE 10 — Observability + Airflow

**Duration:** 2 weeks
**Repos:** [observability-zero-to-hero/](https://github.com/ReddyBytes/observability-zero-to-hero) + [Airflow/](https://github.com/ReddyBytes/Airflow)
**Goal:** Operate production data and AI systems with full visibility

### Week 1 — Observability Stack

| Day | Folder | Topics |
|---|---|---|
| Day 1 | [day-1](https://github.com/ReddyBytes/observability-zero-to-hero/tree/main/day-1) | Metrics vs logs vs traces, why observability matters |
| Day 2 | [day-2](https://github.com/ReddyBytes/observability-zero-to-hero/tree/main/day-2) | Prometheus + Grafana setup on K8s |
| Day 3 | [day-3](https://github.com/ReddyBytes/observability-zero-to-hero/tree/main/day-3) | PromQL — write real queries |
| Day 4 | [day-4](https://github.com/ReddyBytes/observability-zero-to-hero/tree/main/day-4) | Custom metrics, Alertmanager, alert rules |
| Day 5 | [day-5](https://github.com/ReddyBytes/observability-zero-to-hero/tree/main/day-5) | EFK stack — centralized logging |
| Day 6 | [day-6](https://github.com/ReddyBytes/observability-zero-to-hero/tree/main/day-6) | Jaeger — distributed tracing |
| Day 7 | [day-7](https://github.com/ReddyBytes/observability-zero-to-hero/tree/main/day-7) | OpenTelemetry — unified stack |

### Week 2 — Apache Airflow (Pipeline Orchestration)

| Module | Folder | Topics |
|---|---|---|
| Beginner | [01_Beginner](https://github.com/ReddyBytes/Airflow/tree/main/01_Beginner) | Architecture, first DAG, core operators |
| Intermediate | [02_Intermediate](https://github.com/ReddyBytes/Airflow/tree/main/02_Intermediate) | Sensors, executors, XComs, TaskFlow API |
| Advanced | [03_Advanced](https://github.com/ReddyBytes/Airflow/tree/main/03_Advanced) | Dynamic mapping, deferrable operators, testing |
| Airflow 3 Features | [05_Airflow_3_Features](https://github.com/ReddyBytes/Airflow/tree/main/05_Airflow_3_Features) | Asset-driven scheduling, DAG versioning |
| Cloud Airflow | [06_Airflow_on_Cloud](https://github.com/ReddyBytes/Airflow/tree/main/06_Airflow_on_Cloud) | AWS MWAA, EKS deployment |
| Integrations | [07_Integrations](https://github.com/ReddyBytes/Airflow/tree/main/07_Integrations) | dbt, Spark, Great Expectations |

---

---

# PHASE 11 — DSA + Interview Preparation

**Duration:** 4 weeks
**Repo:** [Python-DSA-API-Mastery/02_DSA_Mastery/](https://github.com/ReddyBytes/Python-DSA-API-Mastery/tree/main/02_DSA_Mastery)
**Goal:** Pass coding rounds at top companies, sharpen problem-solving

### Week 1 — Foundations + Linear Structures

| Module | Folder | Interview Weight |
|---|---|---|
| Complexity Analysis | [01_complexity_analysis](https://github.com/ReddyBytes/Python-DSA-API-Mastery/tree/main/02_DSA_Mastery/01_complexity_analysis) | ⭐⭐⭐ Every answer needs Big-O |
| Arrays | [02_arrays](https://github.com/ReddyBytes/Python-DSA-API-Mastery/tree/main/02_DSA_Mastery/02_arrays) | ⭐⭐⭐ Most common interview topic |
| Strings | [03_strings](https://github.com/ReddyBytes/Python-DSA-API-Mastery/tree/main/02_DSA_Mastery/03_strings) | ⭐⭐⭐ Anagrams, palindromes, sliding window |
| Recursion | [04_recursion](https://github.com/ReddyBytes/Python-DSA-API-Mastery/tree/main/02_DSA_Mastery/04_recursion) | ⭐⭐⭐ Foundation for trees/graphs/DP |
| Sorting | [05_sorting](https://github.com/ReddyBytes/Python-DSA-API-Mastery/tree/main/02_DSA_Mastery/05_sorting) | ⭐⭐ Merge sort + quick sort internals |
| Hashing | [10_hashing](https://github.com/ReddyBytes/Python-DSA-API-Mastery/tree/main/02_DSA_Mastery/10_hashing) | ⭐⭐⭐ Most versatile technique |
| Two Pointers | [11_two_pointers](https://github.com/ReddyBytes/Python-DSA-API-Mastery/tree/main/02_DSA_Mastery/11_two_pointers) | ⭐⭐⭐ Dozens of problems solved by this |
| Sliding Window | [12_sliding_window](https://github.com/ReddyBytes/Python-DSA-API-Mastery/tree/main/02_DSA_Mastery/12_sliding_window) | ⭐⭐⭐ String + subarray problems |
| Binary Search | [13_binary_search](https://github.com/ReddyBytes/Python-DSA-API-Mastery/tree/main/02_DSA_Mastery/13_binary_search) | ⭐⭐⭐ Search + answer-space problems |

### Week 2 — Trees + Graphs

| Module | Folder | Interview Weight |
|---|---|---|
| Linked List | [07_linked_list](https://github.com/ReddyBytes/Python-DSA-API-Mastery/tree/main/02_DSA_Mastery/07_linked_list) | ⭐⭐ Fast-slow pointer, reversal |
| Stack + Queue | [08_stack](https://github.com/ReddyBytes/Python-DSA-API-Mastery/tree/main/02_DSA_Mastery/08_stack) + [09_queue](https://github.com/ReddyBytes/Python-DSA-API-Mastery/tree/main/02_DSA_Mastery/09_queue) | ⭐⭐ Monotonic stack problems |
| Trees | [14_trees](https://github.com/ReddyBytes/Python-DSA-API-Mastery/tree/main/02_DSA_Mastery/14_trees) | ⭐⭐⭐ BFS, DFS, LCA, path problems |
| Binary Search Trees | [15_binary_search_trees](https://github.com/ReddyBytes/Python-DSA-API-Mastery/tree/main/02_DSA_Mastery/15_binary_search_trees) | ⭐⭐ Validation, kth element |
| Heaps | [16_heaps](https://github.com/ReddyBytes/Python-DSA-API-Mastery/tree/main/02_DSA_Mastery/16_heaps) | ⭐⭐⭐ Top-K, median stream, task scheduling |
| Trie | [17_trie](https://github.com/ReddyBytes/Python-DSA-API-Mastery/tree/main/02_DSA_Mastery/17_trie) | ⭐⭐ Prefix search, autocomplete |
| Graphs | [18_graphs](https://github.com/ReddyBytes/Python-DSA-API-Mastery/tree/main/02_DSA_Mastery/18_graphs) | ⭐⭐⭐ BFS/DFS, topological sort, union-find |

### Week 3 — Advanced Algorithms

| Module | Folder | Interview Weight |
|---|---|---|
| Greedy | [19_greedy](https://github.com/ReddyBytes/Python-DSA-API-Mastery/tree/main/02_DSA_Mastery/19_greedy) | ⭐⭐ Interval scheduling, activity selection |
| Backtracking | [20_backtracking](https://github.com/ReddyBytes/Python-DSA-API-Mastery/tree/main/02_DSA_Mastery/20_backtracking) | ⭐⭐⭐ Subsets, permutations, N-Queens |
| Dynamic Programming | [21_dynamic_programming](https://github.com/ReddyBytes/Python-DSA-API-Mastery/tree/main/02_DSA_Mastery/21_dynamic_programming) | ⭐⭐⭐ Most feared — 10 core patterns |
| Bit Manipulation | [22_bit_manipulation](https://github.com/ReddyBytes/Python-DSA-API-Mastery/tree/main/02_DSA_Mastery/22_bit_manipulation) | ⭐⭐ XOR tricks, power of 2 checks |
| Advanced Graphs | [25_advanced_graphs](https://github.com/ReddyBytes/Python-DSA-API-Mastery/tree/main/02_DSA_Mastery/25_advanced_graphs) | ⭐⭐ Dijkstra, Bellman-Ford, MST |
| DSU | [24_disjoint_set_union](https://github.com/ReddyBytes/Python-DSA-API-Mastery/tree/main/02_DSA_Mastery/24_disjoint_set_union) | ⭐⭐ Connected components, Kruskal's |
| System Design Patterns (DSA) | [26_system_design_patterns](https://github.com/ReddyBytes/Python-DSA-API-Mastery/tree/main/02_DSA_Mastery/26_system_design_patterns) | ⭐⭐⭐ LRU cache, rate limiter — asked directly |

### Week 4 — Full Interview Simulation

- [dsa_0_2_years.md](https://github.com/ReddyBytes/Python-DSA-API-Mastery/blob/main/02_DSA_Mastery/99_interview_master/0_2_years.md)
- [dsa_3_5_years.md](https://github.com/ReddyBytes/Python-DSA-API-Mastery/blob/main/02_DSA_Mastery/99_interview_master/3_5_years.md)
- [dsa_faang_level.md](https://github.com/ReddyBytes/Python-DSA-API-Mastery/blob/main/02_DSA_Mastery/99_interview_master/faang_level_questions.md)
- [python_scenario_based_questions.md](https://github.com/ReddyBytes/Python-DSA-API-Mastery/blob/main/01_Python_Mastery/99_interview_master/scenario_based_questions.md)
- [python_tricky_edge_cases.md](https://github.com/ReddyBytes/Python-DSA-API-Mastery/blob/main/01_Python_Mastery/99_interview_master/tricky_edge_cases.md)
- [system_design_scenario_questions.md](https://github.com/ReddyBytes/Python-DSA-API-Mastery/blob/main/04_System_Design_Mastery/99_interview_master/scenario_questions.md)
- [system_design_rapid_fire.md](https://github.com/ReddyBytes/Python-DSA-API-Mastery/blob/main/04_System_Design_Mastery/99_interview_master/rapid_fire.md)
- [api_scenario_based_questions.md](https://github.com/ReddyBytes/Python-DSA-API-Mastery/blob/main/03_API_Mastery/99_interview_master/scenario_based_questions.md)

---

---

# PHASE 12 — Advanced AI Topics + Claude APIs

**Duration:** 2 weeks
**Repo:** [AI-ENGINEERS-ATLAS/](https://github.com/ReddyBytes/AI-ENGINEERS-ATLAS)
**Goal:** Stand out with cutting-edge skills — HuggingFace fine-tuning, evaluation, Claude API

### Week 1 — HuggingFace + Evaluation + RL

| Section | Folder | Topics |
|---|---|---|
| HuggingFace | [14_Hugging_Face_Ecosystem](https://github.com/ReddyBytes/AI-ENGINEERS-ATLAS/tree/main/14_Hugging_Face_Ecosystem) | Hub, Transformers, Datasets, PEFT/LoRA, Trainer API |
| AI Evaluation | [18_AI_Evaluation](https://github.com/ReddyBytes/AI-ENGINEERS-ATLAS/tree/main/18_AI_Evaluation) | Benchmarks, LLM-as-Judge, Adversarial_Test_Suite.md |
| Reinforcement Learning | [19_Reinforcement_Learning](https://github.com/ReddyBytes/AI-ENGINEERS-ATLAS/tree/main/19_Reinforcement_Learning) | MDPs, Q-learning, PPO, RL for LLMs |

**Most important file:**
- [04_PEFT_and_LoRA/When_to_Use.md](https://github.com/ReddyBytes/AI-ENGINEERS-ATLAS/blob/main/14_Hugging_Face_Ecosystem/04_PEFT_and_LoRA/When_to_Use.md) — LoRA fine-tuning is asked in every AI interview

### Week 2 — Claude API + Agent SDK

| Track | Folder | Topics |
|---|---|---|
| Claude as AI Model | [21_Claude_Mastery/01_Claude_as_an_AI_Model](https://github.com/ReddyBytes/AI-ENGINEERS-ATLAS/tree/main/21_Claude_Mastery/01_Claude_as_an_AI_Model) | Architecture, RLHF, Constitutional AI, Extended Thinking |
| Claude API | [21_Claude_Mastery/03_Claude_API_and_SDK](https://github.com/ReddyBytes/AI-ENGINEERS-ATLAS/tree/main/21_Claude_Mastery/03_Claude_API_and_SDK) | Messages API, Tool Use, Streaming, Prompt Caching, Batching |
| Agent SDK | [21_Claude_Mastery/04_Claude_Agent_SDK](https://github.com/ReddyBytes/AI-ENGINEERS-ATLAS/tree/main/21_Claude_Mastery/04_Claude_Agent_SDK) | Build agents, multi-agent orchestration, safety |

---

---

# Build These 3 Projects (Portfolio That Gets Interviews)

| # | Project | When to Build | Repo Path |
|---|---|---|---|
| 1 | **Production RAG System** — document Q&A with chunking, re-ranking, RAGAS evaluation, monitoring | After Phase 7 | [AI-ENGINEERS-ATLAS/09_RAG_Systems/09_Build_a_RAG_App](https://github.com/ReddyBytes/AI-ENGINEERS-ATLAS/tree/main/09_RAG_Systems/09_Build_a_RAG_App) |
| 2 | **Multi-Agent Research Assistant** — LangGraph + tools + memory + human-in-the-loop | After Phase 7 | [AI-ENGINEERS-ATLAS/10_AI_Agents/09_Build_an_Agent](https://github.com/ReddyBytes/AI-ENGINEERS-ATLAS/tree/main/10_AI_Agents/09_Build_an_Agent) + [15_LangGraph/08_Build_with_LangGraph](https://github.com/ReddyBytes/AI-ENGINEERS-ATLAS/tree/main/15_LangGraph/08_Build_with_LangGraph) |
| 3 | **E-Commerce FastAPI** — OOP + JWT + SQLAlchemy + Docker + GitHub Actions CI/CD | After Phase 5 | [Python-DSA-API-Mastery/05_Capstone_Projects/01_Ecommerce_API_FastAPI](https://github.com/ReddyBytes/Python-DSA-API-Mastery/tree/main/05_Capstone_Projects/01_Ecommerce_API_FastAPI) |

---

---

# Timeline — Choose Your Track

## 6-Month Full-Time (Recommended)

```
Month 1  │ Phase 1 (Python)       + Phase 2 (ML Foundations)
Month 2  │ Phase 3 (SQL)          + Phase 4 (Deep Learning + NLP)
Month 3  │ Phase 5 (APIs)         + Phase 6 (Transformers + LLMs)
Month 4  │ Phase 7 (RAG + Agents) — build Project 1 + 2
Month 5  │ Phase 8 (Production + System Design) + Phase 9 (Linux + AWS + K8s)
Month 6  │ Phase 10 (Observability + Airflow) + Phase 11 (DSA + Interview Prep)
          │ Phase 12 (Advanced AI) — build Project 3
          │ Start applying from Week 3 of Month 5
```

## 12-Month Part-Time (2–3 hrs/day)

```
Month 1–2   │ Phase 1 + Phase 2
Month 3     │ Phase 3 (SQL)
Month 4–5   │ Phase 4 + Phase 5
Month 6–7   │ Phase 6 + Phase 7
Month 8     │ Phase 8 (Production + System Design)
Month 9     │ Phase 9 (Linux + AWS + K8s)
Month 10    │ Phase 10 + Phase 12
Month 11–12 │ Phase 11 (DSA + Interview Prep) + Projects
```

---

---

# What Each Phase Unlocks (Salary Impact)

| After Completing | Role You Can Target | Expected Package |
|---|---|---|
| Phase 1 + 2 | Junior ML Engineer / Data Analyst | 6–10 LPA |
| Phase 1–4 + SQL | Data Scientist | 10–15 LPA |
| Phase 1–6 + Projects | ML Engineer / AI Engineer | 15–20 LPA |
| Phase 1–8 + Projects | Senior ML/AI Engineer | 20–25 LPA |
| Phase 1–12 + 3 Projects | Senior AI Engineer / Lead | 25–35 LPA |

---

---

# Interview Preparation Checklist

Before every interview round, review:

**Coding Round**
- [dsa-complete-mastery/99_interview_master](https://github.com/ReddyBytes/Python-DSA-API-Mastery/tree/main/02_DSA_Mastery/99_interview_master) — based on company level

**Python Depth**
- [python_3_5_years.md](https://github.com/ReddyBytes/Python-DSA-API-Mastery/blob/main/01_Python_Mastery/99_interview_master/python_3_5_years.md)
- [tricky_edge_cases.md](https://github.com/ReddyBytes/Python-DSA-API-Mastery/blob/main/01_Python_Mastery/99_interview_master/tricky_edge_cases.md)

**ML/AI Conceptual**
- [02_Machine_Learning_Foundations/05_Model_Evaluation/Interview_QA.md](https://github.com/ReddyBytes/AI-ENGINEERS-ATLAS/blob/main/02_Machine_Learning_Foundations/05_Model_Evaluation/Interview_QA.md)
- [03_Classical_ML_Algorithms/Algorithm_Comparison.md](https://github.com/ReddyBytes/AI-ENGINEERS-ATLAS/blob/main/03_Classical_ML_Algorithms/Algorithm_Comparison.md)
- [09_RAG_Systems/Full_Pipeline_Overview.md](https://github.com/ReddyBytes/AI-ENGINEERS-ATLAS/blob/main/09_RAG_Systems/Full_Pipeline_Overview.md)

**System Design**
- [system-design-mastery/23_interview_framework](https://github.com/ReddyBytes/Python-DSA-API-Mastery/tree/main/04_System_Design_Mastery/23_interview_framework) — use this framework every time
- [system-design-mastery/99_interview_master](https://github.com/ReddyBytes/Python-DSA-API-Mastery/tree/main/04_System_Design_Mastery/99_interview_master)
- [13_AI_System_Design/System_Design_Framework.md](https://github.com/ReddyBytes/AI-ENGINEERS-ATLAS/blob/main/13_AI_System_Design/System_Design_Framework.md)

**API Design**
- [api-mastery/99_interview_master/scenario_based_questions.md](https://github.com/ReddyBytes/Python-DSA-API-Mastery/blob/main/03_API_Mastery/99_interview_master/scenario_based_questions.md)

**Production/Cost**
- [PRODUCTION_CHECKLIST.md](https://github.com/ReddyBytes/AI-ENGINEERS-ATLAS/blob/main/12_Production_AI/Production_Checklist.md)
- [12_Production_AI/03_Cost_Optimization/Cost_Case_Studies.md](https://github.com/ReddyBytes/AI-ENGINEERS-ATLAS/blob/main/12_Production_AI/03_Cost_Optimization/Cost_Case_Studies.md)

---

*All repos: [Python-DSA-API-Mastery](https://github.com/ReddyBytes/Python-DSA-API-Mastery) · [AI-ENGINEERS-ATLAS](https://github.com/ReddyBytes/AI-ENGINEERS-ATLAS) · [SQL-Mastery](https://github.com/ReddyBytes/SQL-Mastery) · [Linux-Terraform-AWS-Mastery](https://github.com/ReddyBytes/Linux-Terraform-AWS-Mastery) · [Container-Engineering](https://github.com/ReddyBytes/Container-Engineering) · [observability-zero-to-hero](https://github.com/ReddyBytes/observability-zero-to-hero) · [Airflow](https://github.com/ReddyBytes/Airflow) · `linux-guide` · `devmastery`*

*Last updated: 2026-04-27*
