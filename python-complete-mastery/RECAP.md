# Python Complete Mastery — Topic Recap

> One-line summary of every module. Use this to quickly find which module covers the concept you need.

---

## Core Python (01–06)

| Module | Topics Covered |
|--------|---------------|
| **01 — Python Fundamentals** | Variables as references (not boxes), mutable vs immutable objects, `is` vs `==`, shallow vs deep copy, integer interning, garbage collection basics, `id()` and object identity |
| **01.1 — Memory Management** | Stack vs heap memory, reference counting, circular references, generational garbage collector (`gc` module), `__slots__`, `weakref`, memory layout (arenas/pools/blocks), `tracemalloc`, closure cell objects on heap, stack frame internals |
| **02 — Control Flow** | `if`/`elif`/`else`, ternary expressions, `match`/`case` (Python 3.10+), walrus operator `:=`, `for` and `while` loops, `break`/`continue`/`pass`, loop `else`, `enumerate`/`zip`, list/dict/set comprehensions, comprehension scoping, short-circuit evaluation, truthy/falsy values |
| **03 — Data Types** | `int`/`float`/`bool`/`str`/`list`/`tuple`/`set`/`dict`/`None`, float precision trap, integer bases (hex/bin/oct), string indexing and slicing, string methods, set hash table internals, dict insertion-order guarantee (3.7+), `bytes`/`bytearray`, `collections.defaultdict`/`Counter`/`deque`/`frozenset`, type conversion |
| **04 — Functions** | `def`, parameters vs arguments, all 7 parameter types (positional/keyword/default/`*args`/`**kwargs`/keyword-only/positional-only), mutable default argument trap, LEGB scope rule, `global`/`nonlocal`, first-class functions, lambda, closures, late binding trap, closure cell internals, decorators, `@wraps`, decorator factories, recursion, `sys.setrecursionlimit`, `functools.lru_cache`/`partial`, pure functions vs side effects, type annotations, docstrings |
| **05 — OOP** | Classes and objects, `__init__` and `self`, encapsulation (`_`/`__`), inheritance, multiple inheritance, MRO and `super()`, polymorphism, abstraction (`ABC`/`@abstractmethod`), dunder methods (`__repr__`/`__str__`/`__eq__`/`__hash__`/`__len__`), `@property`, `@classmethod`/`@staticmethod`, class vs instance variables, composition vs inheritance, `@dataclass`, `__slots__`, metaclasses, descriptors, mixins, SOLID principles |
| **06 — Exceptions & Error Handling** | Exception hierarchy (`BaseException` → `Exception`), `try`/`except`/`else`/`finally`, exception objects and traceback, `raise`/`raise from`/`raise from None`, custom exception hierarchies, `finally` edge cases (return/continue/break), LBYL vs EAFP, retry with exponential backoff and jitter, circuit breaker pattern, graceful degradation, exception chaining, logging exceptions, `warnings` module, exceptions in threads and async, reading tracebacks |

---

## Advanced Python (07–15)

| Module | Topics Covered |
|--------|---------------|
| **07 — Modules & Packages** | `import` statement mechanics, `from X import Y`, module object vs file on disk, `sys.modules` cache, `__name__ == "__main__"`, package structure (`__init__.py`), relative imports, `__all__`, `importlib.import_module()`, circular imports and fixes, `importlib.reload()`, lazy imports |
| **08 — File Handling** | `open()` with context manager, read/write/append/binary modes, `pathlib.Path`, `json.load`/`json.dump`, CSV reading/writing, `io.StringIO`/`io.BytesIO`, string encoding (`utf-8`/`latin-1`), directory operations (`mkdir`/`glob`), `tempfile`, atomic file write patterns |
| **09 — Logging & Debugging** | `logging.getLogger()`, log levels (DEBUG/INFO/WARNING/ERROR/CRITICAL), `StreamHandler`/`FileHandler`/`RotatingFileHandler`, formatters, logger hierarchy, `logging.config.dictConfig()`, `logging.exception()`, structured logging, `pdb` basics (`n`/`s`/`c`/`p`/`b`), `breakpoint()`, `pdb` guide |
| **10 — Decorators** | Decorator anatomy (wrapper pattern), `@wraps` for metadata preservation, decorator factories (decorators with arguments), stacking multiple decorators, class-based decorators, real-world patterns (logging, retry, caching, auth, timing) |
| **11 — Generators & Iterators** | Iteration protocol (`__iter__`/`__next__`), custom iterators, generator functions (`yield`), generator expressions, lazy evaluation, memory comparison vs lists, `yield from`, `generator.send()`/`throw()`/`close()`, `itertools` (chain/islice/groupby/takewhile/zip_longest), infinite iterators, generator pipelines, async generators |
| **12 — Context Managers** | `with` statement, `__enter__`/`__exit__` protocol, resource cleanup guarantee, `@contextmanager` decorator, `contextlib.ExitStack`, `contextlib.suppress`, `contextlib.redirect_stdout`/`redirect_stderr`, `contextlib.nullcontext`, `async with`/`__aenter__`/`__aexit__` |
| **13 — Concurrency** | GIL and its implications, `threading.Thread`, `ThreadPoolExecutor`, `ProcessPoolExecutor`, `threading.Lock`/`Semaphore`, I/O-bound vs CPU-bound decision, `asyncio` event loop, `async def`/`await`, `asyncio.gather`/`create_task`/`Queue`/`Semaphore`, `asyncio.TaskGroup` (3.11+), task cancellation, `concurrent.futures`, multiprocessing internals |
| **14 — Type Hints & Pydantic** | Basic annotations (`x: int`, `-> str`), `Optional`/`Union`/`Literal`, `List`/`Dict`/`Tuple`/`Set`, `TypeVar`, `Protocol`, `TypedDict`, `typing.overload`, Python 3.10+ `X | Y` syntax, Pydantic `BaseModel`, `@field_validator`, `model_validator`, Pydantic v2 patterns, `pydantic-settings`, `dataclass` vs Pydantic, `mypy`/`pyright` static analysis |
| **15 — Advanced Python** | Dunder methods and Python's protocol system, `__getitem__`/`__setitem__`/`__len__`/`__contains__`, comparison dunders (`__eq__`/`__lt__`/`__hash__`), `__getattr__` vs `__getattribute__`, descriptor protocol (`__get__`/`__set__`/`__delete__`), `@property` internals, `__slots__` deep dive, metaclasses and `type()`, `__init_subclass__`, callable objects (`__call__`), operator overloading, introspection (`inspect`/`dir`/`vars`) |

---

## Architecture & Production (16–21)

| Module | Topics Covered |
|--------|---------------|
| **16 — Design Patterns** | Creational: Singleton, Factory Method; Structural: Adapter, Decorator, Facade, Composite; Behavioral: Strategy, Observer, Command, Template Method, State; Repository pattern, Dependency Injection, SOLID principles (all 5) |
| **17 — Testing** | Testing pyramid (unit/integration/e2e), `unittest` framework, `pytest` test discovery and assertions, fixtures (function/class/module/session scope), `pytest.mark.parametrize`, `unittest.mock.patch`/`MagicMock`, test doubles (mock/stub/fake/spy), `pytest.raises`, `monkeypatch`, `caplog`/`capsys`, async testing (`pytest-asyncio`), code coverage (`pytest-cov`), TDD workflow, property-based testing (`hypothesis`), CI/CD integration |
| **18 — Performance Optimization** | Profiling with `cProfile`/`timeit`/`memory_profiler`/`tracemalloc`, algorithmic complexity and data structure choice, generator vs list tradeoff, `__slots__` for memory, `functools.lru_cache`/`cache`, `dis` bytecode inspection, `py-spy` sampling profiler, Numba JIT basics, flamegraph interpretation |
| **19 — Production Best Practices** | Virtual environments (`venv`), `pip` + `requirements.txt`, `pyproject.toml`, PEP 8 style guide, type hints in production, `pre-commit` hooks (Black/Ruff/mypy), semantic versioning, editable installs (`pip install -e .`), `tox`/`nox`, security scanning (`bandit`/`safety`), project structure conventions, packaging for distribution |
| **20 — System Design with Python** | REST API design principles, HTTP status codes, request/response lifecycle, rate limiting, pagination strategies, API authentication, gRPC vs REST, API versioning, circuit breaker, graceful shutdown, idempotency keys, OpenAPI/Swagger, caching strategies, scalable app design |
| **21 — Data Engineering Applications** | ETL vs ELT, batch vs streaming processing, memory-efficient ETL (generators), idempotency and checkpointing, retry with backoff, Kafka basics (producers/consumers/partitions), schema validation, data deduplication, file processing pipelines, streaming simulation, API data collection patterns |

---

## Data Science & AI (22–33)

| Module | Topics Covered |
|--------|---------------|
| **22 — NumPy for AI** | Array creation and dtypes, indexing and slicing, broadcasting rules, vectorized operations (why they're fast), `reshape`/`flatten`/`ravel`, linear algebra (`np.linalg`: dot product/matmul/norm/SVD), `np.random`, boolean indexing, fancy indexing, `np.where`/`np.select`, memory layout (C vs F order), `np.einsum`, `np.memmap` for large files |
| **23 — Pandas for AI** | `DataFrame`/`Series` fundamentals, `read_csv`/`to_csv`, `loc`/`iloc` indexing, `groupby` and aggregations, `merge`/`join`/`concat`, missing data (`fillna`/`dropna`/`isnull`), `apply`/`map`, string methods, type casting, duplicate detection, `pivot_table`, chunked reading (`chunksize`), memory optimization, JSONL export for LLM fine-tuning |
| **24 — Async Python for AI** | `async def`/`await` for LLM calls, `asyncio.gather` for concurrent API calls, `asyncio.create_task`, streaming responses with async generators (`async for`), `asyncio.Semaphore` for rate limiting, error handling in async code, `aiohttp`/`httpx` async HTTP, sync vs async client choice, production patterns for AI services |
| **25 — Python AI Ecosystem** | `python-dotenv` for API key management, `httpx` async HTTP client, `tenacity` retry decorator, `loguru` structured logging, `pydantic-settings` for config, `tqdm` progress bars, `rich` terminal output, `tiktoken` token counting, `json`/`jsonlines` patterns, `click`/`typer` CLI tools, LangChain basics, LlamaIndex for RAG |
| **26 — Statistics & Probability** | Descriptive stats (mean/median/mode/std/IQR), normal distribution, Central Limit Theorem, hypothesis testing, p-values, confidence intervals, Bayes' theorem, conditional probability, Type I/II errors, A/B testing, chi-square test, correlation vs causation, power analysis, bootstrap sampling, MLE |
| **27 — Matplotlib & Seaborn** | Figure/Axes model, line plots, scatter plots, histograms, bar charts, `subplots`, `tight_layout`, Seaborn `heatmap`/`pairplot`/`boxplot`/`violinplot`/`histplot`, color palettes, figure sizing, log scale, annotations, twin axes |
| **28 — EDA Workflow** | EDA checklist (10-step workflow), `df.info()`/`df.describe()`, missing value analysis, duplicate detection, distribution plots, cardinality and frequency analysis, target variable analysis, correlation matrix, outlier detection (IQR/Z-score), feature-target relationships, `pandas_profiling`/`ydata-profiling` |
| **29 — Web Scraping** | `requests` library, `BeautifulSoup` HTML parsing, CSS selectors, `find()`/`find_all()`, HTTP error handling, robots.txt ethics, `requests.Session`, headers/User-Agent, rate limiting, Selenium for JavaScript pages, `httpx` async scraping, `Scrapy` framework, `Playwright`, pagination handling |
| **30 — SQL with Python** | `sqlite3` basics (connection/cursor/execute/fetchall), parameterized queries, CRUD operations, `pd.read_sql()`/`df.to_sql()`, SQLAlchemy engine and session, SQLAlchemy ORM with declarative models, GROUP BY/HAVING/subqueries, transactions, indexes, DuckDB for analytics, connection pooling, ACID properties |
| **31 — File Formats (PDF/XML/JSON/CSV/Excel)** | `json` module (`load`/`dump`/`loads`/`dumps`), `csv` module, `pd.read_csv()`/`read_excel()`/`read_json()`, file encoding (`utf-8`/`latin-1`), `pymupdf`/`pdfplumber` for PDF extraction, `xml.etree.ElementTree`/`lxml`, `openpyxl` for Excel manipulation, `pickle`, parquet/Arrow via pyarrow, YAML, `pd.json_normalize` |
| **32 — Streamlit & Flask** | Streamlit widgets (`text_input`/`button`/`selectbox`/`slider`), `st.write`/`st.dataframe`, `st.session_state`, `st.cache_data`, file upload, multi-page apps, Flask `@app.route`, `request` object, `jsonify`, Flask error handling, environment variables for secrets, Flask blueprints, Flask-CORS, FastAPI overview |
| **33 — Regular Expressions** | `re.search()`/`re.findall()`/`re.sub()`/`re.split()`/`re.fullmatch()`, character classes `[...]`, quantifiers (`+`/`*`/`?`/`{n,m}`), groups `(...)`, anchors `^`/`$`, named groups `(?P<name>...)`, non-capturing groups `(?:...)`, lookahead/lookbehind, flags (`IGNORECASE`/`MULTILINE`/`DOTALL`), compiled patterns `re.compile()`, non-greedy quantifiers, backreferences |

---

## Interview Master (99)

| Module | Topics Covered |
|--------|---------------|
| **99 — Interview Master** | Tiered by experience: 0–2 years (fundamentals, OOP basics, exception handling, FizzBuzz-level coding), 3–5 years (memory management, GIL, decorators, concurrency, system design thinking), scenario-based questions (debugging production issues, API design, performance problems), tricky edge cases (mutable defaults, late binding, integer caching, `__del__` and GC) |

---

*Total modules: 33 + interview · Last updated: 2026-04-21*
