"""
16_design_patterns/singleton.py
==================================
CONCEPT: Singleton — a class that has exactly ONE instance throughout the
program's lifetime. All callers share the same object.
WHY THIS MATTERS: Config, loggers, connection pools, caches — many real
components should have exactly one shared instance. Singletons enforce this.
WHY IT'S CONTROVERSIAL: Singletons are global state — they make testing harder
and create hidden dependencies. The pattern taught here includes testability
via reset() and dependency injection alternatives.

Prerequisite: Modules 01–10 (OOP, decorators)
"""

import threading
import time

# =============================================================================
# SECTION 1: Singleton via __new__ — the classic Python approach
# =============================================================================

# CONCEPT: __new__ creates the instance before __init__ initializes it.
# We intercept __new__ to return the SAME instance every time.
# Store it as a class attribute — shared across all calls to the constructor.

print("=== Section 1: Singleton via __new__ ===")

class AppConfig:
    """
    Application configuration singleton.
    WHY SINGLETON: config is read-only after startup and shared everywhere.
    Every component that needs config should see the same values.
    """
    _instance = None   # class attribute: the one shared instance

    def __new__(cls, *args, **kwargs):
        """
        Called BEFORE __init__. Returns the same instance every time.
        Thread-safe for reading; concurrent creation still has a tiny race window
        — see Section 3 for a thread-safe version.
        """
        if cls._instance is None:
            cls._instance = super().__new__(cls)
            cls._instance._initialized = False   # flag to prevent re-init
        return cls._instance

    def __init__(self, env: str = "development", debug: bool = True):
        if self._initialized:
            return   # skip re-initialization on subsequent calls
        self.env    = env
        self.debug  = debug
        self.db_url = f"postgresql://localhost/{env}_db"
        self._initialized = True
        print(f"  AppConfig initialized: env={env}, debug={debug}")

    @classmethod
    def reset(cls):
        """
        FOR TESTING ONLY: destroy singleton so tests can create a fresh one.
        Without this, tests that depend on fresh state would fail.
        """
        cls._instance = None

    def __repr__(self):
        return f"AppConfig(env={self.env!r}, debug={self.debug})"


cfg1 = AppConfig("production", debug=False)
cfg2 = AppConfig("staging", debug=True)   # __init__ args ignored — same instance

print(f"  cfg1 is cfg2: {cfg1 is cfg2}")    # True
print(f"  cfg2.env: {cfg2.env}")             # "production" — cfg2 IS cfg1
print(f"  id(cfg1) == id(cfg2): {id(cfg1) == id(cfg2)}")

# Test isolation: reset between tests
AppConfig.reset()
fresh = AppConfig("test")
print(f"  After reset: {fresh}")


# =============================================================================
# SECTION 2: Singleton via class decorator — reusable, clean
# =============================================================================

# CONCEPT: A decorator that wraps ANY class and enforces singleton behavior.
# Cleaner than inheriting or overriding __new__ — doesn't pollute the class.
# The decorator stores the instance in its own closure — each class gets
# its own storage.

print("\n=== Section 2: Singleton Decorator ===")

def singleton(cls):
    """
    Decorator that turns any class into a singleton.
    WHY DECORATOR over __new__: decouples the singleton mechanism from the class.
    The class itself doesn't know it's a singleton — easier to test.
    """
    instances = {}

    def get_instance(*args, **kwargs):
        if cls not in instances:
            instances[cls] = cls(*args, **kwargs)
        return instances[cls]

    get_instance.__name__ = cls.__name__
    get_instance.__doc__  = cls.__doc__
    get_instance._reset   = lambda: instances.pop(cls, None)   # test helper
    return get_instance


@singleton
class DatabasePool:
    """Connection pool — should exist once, shared by all DB users."""

    def __init__(self, max_connections: int = 10):
        self.max_connections = max_connections
        self._connections    = []
        print(f"  DatabasePool created: max={max_connections} connections")

    def acquire(self) -> str:
        conn_id = f"conn_{len(self._connections) + 1}"
        self._connections.append(conn_id)
        return conn_id

    def release(self, conn_id: str):
        self._connections.remove(conn_id)

    def __repr__(self):
        return f"DatabasePool(active={len(self._connections)}/{self.max_connections})"


pool1 = DatabasePool(max_connections=5)
pool2 = DatabasePool(max_connections=20)  # ignored — pool1 already created

conn = pool1.acquire()
print(f"  pool1 is pool2: {pool1 is pool2}")
print(f"  pool2.max_connections: {pool2.max_connections}")  # still 5!
print(f"  {pool1}")

DatabasePool._reset()   # for tests
pool_fresh = DatabasePool(max_connections=20)
print(f"  After reset: {pool_fresh}")


# =============================================================================
# SECTION 3: Thread-safe singleton with double-checked locking
# =============================================================================

# CONCEPT: Two threads calling the constructor simultaneously can both pass
# the `_instance is None` check before either creates the instance.
# Double-checked locking minimizes lock contention: check without lock first,
# then check again inside the lock (cheap in the common case — already created).

print("\n=== Section 3: Thread-Safe Singleton ===")

class ThreadSafeSingleton:
    _instance = None
    _lock      = threading.Lock()

    def __new__(cls, *args, **kwargs):
        if cls._instance is None:               # fast path — no lock if already created
            with cls._lock:                     # only ONE thread enters this block at a time
                if cls._instance is None:       # second check INSIDE the lock
                    cls._instance = super().__new__(cls)
                    cls._instance._ready = False
        return cls._instance

    def __init__(self, value: int = 0):
        if self._ready:
            return
        self.value = value
        self._ready = True
        print(f"  ThreadSafeSingleton initialized: value={value}")

    @classmethod
    def reset(cls):
        with cls._lock:
            cls._instance = None


# Simulate concurrent creation
results = []

def try_create(val: int) -> None:
    instance = ThreadSafeSingleton(val)
    results.append(id(instance))


threads = [threading.Thread(target=try_create, args=(i,)) for i in range(5)]
for t in threads: t.start()
for t in threads: t.join()

unique_ids = set(results)
print(f"  Created from 5 threads: {len(unique_ids)} unique instance(s)  "
      f"({'SAFE' if len(unique_ids) == 1 else 'RACE CONDITION'})")


# =============================================================================
# SECTION 4: Monostate (Borg) pattern — shared STATE, multiple instances
# =============================================================================

# CONCEPT: Borg pattern shares __dict__ (state) across all instances instead
# of sharing the instance itself. Each Borg() call creates a new object, but
# all objects have the same dictionary — they all see the same state.
# WHY: sometimes you need the identity flexibility of multiple objects but
# shared state semantics. Easier to test than a true singleton.

print("\n=== Section 4: Borg (Monostate) Pattern ===")

class Logger:
    """
    Borg pattern: multiple instances, shared state.
    All Logger() objects see the same log entries and level setting.
    """
    _shared_state: dict = {}   # ALL instances share this exact dict

    def __init__(self):
        self.__dict__ = Logger._shared_state   # point this instance to shared dict
        if not hasattr(self, "_initialized"):
            self._log_entries = []
            self._level       = "INFO"
            self._initialized = True

    def log(self, level: str, message: str) -> None:
        entry = f"[{level}] {message}"
        self._log_entries.append(entry)

    def set_level(self, level: str) -> None:
        self._level = level

    def get_entries(self) -> list:
        return list(self._log_entries)


log1 = Logger()
log2 = Logger()
log1.log("INFO", "Server started")
log2.log("ERROR", "Database timeout")
log1.set_level("DEBUG")

print(f"  log1 is log2: {log1 is log2}")                # False — different objects
print(f"  Same entries: {log1.get_entries() == log2.get_entries()}")  # True
print(f"  log2 level: {log2._level}")                   # DEBUG — set by log1!
print(f"  Entries: {log1.get_entries()}")


# =============================================================================
# SECTION 5: Dependency injection — the testable alternative
# =============================================================================

# CONCEPT: Instead of accessing a singleton directly, accept the instance as
# a constructor parameter. Callers pass in the shared instance in production
# and a fresh mock in tests. This decouples components from global state.
# RULE OF THUMB: use singleton for truly global, lifecycle-spanning resources
# (config, logger, DB pool). Use DI for components that need testability.

print("\n=== Section 5: Dependency Injection Alternative ===")

class EmailService:
    """Sends emails — stateless, can be a singleton or injected."""

    def send(self, to: str, subject: str) -> dict:
        return {"to": to, "subject": subject, "sent": True}


class UserService:
    """
    Depends on EmailService — receives it via constructor (DI).
    In production: pass a real EmailService singleton.
    In tests: pass a mock — no global state needed.
    """

    def __init__(self, email_service: EmailService):
        self._email = email_service   # injected, not hardcoded

    def register(self, email: str) -> dict:
        user = {"email": email, "active": True}
        result = self._email.send(email, "Welcome!")
        return {"user": user, "welcome_email": result}


# Production: shared singleton
shared_email = EmailService()   # could be a @singleton decorated class
user_svc = UserService(email_service=shared_email)
result = user_svc.register("alice@example.com")
print(f"  Registered: {result['user']['email']}, email sent: {result['welcome_email']['sent']}")

# Test: inject a mock (no global state modified)
class MockEmailService:
    def __init__(self):
        self.sent = []
    def send(self, to: str, subject: str) -> dict:
        self.sent.append((to, subject))
        return {"to": to, "subject": subject, "sent": False}  # no real email

mock_email = MockEmailService()
test_svc   = UserService(email_service=mock_email)
test_svc.register("test@example.com")
print(f"  Test captured: {mock_email.sent}")   # inspectable without side effects


print("\n=== Singleton complete ===")
print("When to use each approach:")
print("  __new__ override  → simple, no external decorator needed")
print("  @singleton        → reusable, clean, decoupled")
print("  Thread-safe       → any singleton created from multiple threads")
print("  Borg / Monostate  → shared state, multiple objects (flexible identity)")
print("  Dependency Inject → testable alternative — prefer for most components")
