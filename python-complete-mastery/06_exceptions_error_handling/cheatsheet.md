# ⚡ Exceptions & Error Handling — Cheatsheet

> Quick reference: syntax, hierarchy, patterns, and gotchas at a glance.

---

## 🔧 Full try/except Syntax

```python
try:
    result = risky()              # minimal — only what can fail

except ValueError as e:           # specific exception
    handle(e)

except (TypeError, KeyError) as e:  # multiple types
    handle(e)

except Exception as e:            # broad fallback — use sparingly
    logging.exception("Unexpected")
    raise                         # always re-raise unless you can recover

else:
    use(result)                   # runs only if NO exception raised

finally:
    cleanup()                     # ALWAYS runs — exception or not
```

---

## 🌲 Exception Hierarchy Quick Reference

```
BaseException
 ├── SystemExit          sys.exit() — don't catch
 ├── KeyboardInterrupt   Ctrl+C — don't swallow
 └── Exception
      ├── ArithmeticError
      │    └── ZeroDivisionError   10 / 0
      ├── LookupError
      │    ├── IndexError          list[9]
      │    └── KeyError            dict["missing"]
      ├── ValueError               int("abc")
      ├── TypeError                "x" + 5
      ├── AttributeError           None.strip()
      ├── NameError                undefined_var
      │    └── UnboundLocalError
      ├── OSError
      │    ├── FileNotFoundError   open("no.txt")
      │    ├── PermissionError
      │    └── TimeoutError
      ├── RuntimeError
      │    ├── RecursionError
      │    └── NotImplementedError
      ├── ImportError
      │    └── ModuleNotFoundError
      ├── StopIteration
      └── AssertionError
```

---

## 🔥 raise — All Forms

```python
raise ValueError("message")            # raise new exception
raise                                   # re-raise current exception (keep traceback)
raise ValueError("new") from original  # chain: preserves cause
raise ValueError("new") from None      # suppress cause chain

# ⚠️ NEVER:
raise e    # inside except — creates new exception, loses original traceback
```

---

## 🏗️ Custom Exceptions

```python
class AppError(Exception):
    """Base for all app errors."""
    def __init__(self, message, code=None):
        super().__init__(message)
        self.code    = code or "ERROR"
        self.message = message

class NotFoundError(AppError):
    def __init__(self, resource, id):
        super().__init__(f"{resource} id={id} not found", "NOT_FOUND")

class ValidationError(AppError):
    def __init__(self, field, message):
        super().__init__(f"{field}: {message}", "VALIDATION_ERROR")
        self.field = field

# Catch hierarchy:
except NotFoundError:       # most specific first
except AppError:            # broader
except Exception:           # broadest — log + re-raise
```

---

## 🔒 Context Managers

```python
# Built-in:
with open("file.txt") as f:     # auto-closes on exit
    data = f.read()

# Multiple at once:
with open("in.txt") as i, open("out.txt", "w") as o:
    o.write(i.read())

# Custom with class:
class ManagedConn:
    def __enter__(self):
        self.conn = connect()
        return self.conn
    def __exit__(self, exc_type, exc_val, exc_tb):
        self.conn.close()
        return False    # False = propagate exception, True = suppress

# Custom with contextlib:
from contextlib import contextmanager

@contextmanager
def db_transaction(conn):
    try:
        yield conn
        conn.commit()
    except:
        conn.rollback()
        raise
    finally:
        conn.close()
```

---

## 📋 Logging Exceptions

```python
import logging
logger = logging.getLogger(__name__)

# ✅ Inside except — full traceback:
try:
    risky()
except Exception:
    logger.exception("Failure description")     # = logger.error(..., exc_info=True)

# ✅ With context:
try:
    process(order_id)
except PaymentError as e:
    logger.error("Payment failed", extra={"order_id": order_id, "code": e.code})

# ❌ DON'T:
except Exception as e:
    print(e)    # no traceback, not searchable
    pass        # silent — hides bugs
```

---

## 🔄 Production Patterns

### Retry with Exponential Backoff

```python
import time, random, functools

def retry(max_attempts=3, exceptions=(Exception,), backoff=2.0):
    def decorator(func):
        @functools.wraps(func)
        def wrapper(*args, **kwargs):
            delay, last_exc = 1.0, None
            for i in range(max_attempts):
                try:
                    return func(*args, **kwargs)
                except exceptions as e:
                    last_exc = e
                    if i < max_attempts - 1:
                        time.sleep(delay + random.random() * 0.1)
                        delay *= backoff
            raise last_exc
        return wrapper
    return decorator

@retry(3, exceptions=(ConnectionError, TimeoutError))
def call_api(): ...
```

### Graceful Degradation

```python
def get_page(product_id):
    product = get_product(product_id)   # critical — let it raise

    try:
        recs = get_recommendations(product_id)
    except Exception:
        logger.warning("Recommendations unavailable", exc_info=True)
        recs = []    # fallback — don't crash for non-critical feature

    return {"product": product, "recommendations": recs}
```

### Exception Translation

```python
# Repository → Service → API: translate at each boundary
try:
    db.query(...)
except psycopg2.OperationalError as e:
    raise DatabaseError("DB unavailable") from e   # hide infra details
```

---

## 🐍 LBYL vs EAFP

```python
# LBYL (Look Before You Leap):
if key in d:
    value = d[key]

# EAFP (Easier to Ask Forgiveness — Pythonic):
try:
    value = d[key]
except KeyError:
    value = default

# PREFER EAFP when:
#   • Race conditions exist between check and use
#   • Failure is rare
#   • Multiple conditions would be needed
```

---

## 🔴 Gotchas

```python
# 1 — raise e loses traceback (use bare raise):
except Exception as e:
    raise e    # ← traceback points HERE, not origin
    raise      # ← correct: original traceback preserved

# 2 — finally return overrides try return:
def f():
    try:    return "try"
    finally: return "finally"    # ← "finally" wins!
# Avoid return/break/continue in finally

# 3 — exception variable deleted after except block:
try:    risky()
except Exception as e:
    saved = e    # ← save before block ends
print(e)         # ← NameError! e is deleted after except block
print(saved)     # ← ok

# 4 — order of except matters (specific BEFORE general):
except Exception:        # ← catches everything including ValueError below!
    ...
except ValueError:       # ← DEAD CODE — never reached
    ...

# 5 — bare except catches Ctrl+C:
except:       # catches KeyboardInterrupt, SystemExit — prevents program exit!
    pass

# 6 — exceptions in threads silently drop:
threading.Thread(target=lambda: 1/0).start()   # error printed, main unaware
# Use concurrent.futures + future.result() instead
```

---

## 🆚 Comparison Tables

### When To Use What

```
try/except        Catch recoverable errors and handle them
try/finally       Guaranteed cleanup (no catching needed)
with statement    Resource management (files, DB, locks)
raise X from Y    Translate exceptions while preserving cause
raise (bare)      Re-raise inside except with full traceback
logging.exception Inside except — logs ERROR + full traceback
logging.error     Outside except — logs ERROR, no traceback
```

### Exception Handling by Layer

```
Repository Layer   Catch DB driver errors → raise domain errors
Service Layer      Catch domain errors → translate or re-raise
API/Controller     Catch domain errors → map to HTTP status codes
                   Never expose internal tracebacks to clients!
```

---

## 🔁 Navigation

| | |
|---|---|
| 📖 Theory | [theory.md](./theory.md) |
| 🎯 Interview | [interview.md](./interview.md) |
| ➡️ Next | [07 — Modules & Packages](../07_modules_packages/theory.md) |
