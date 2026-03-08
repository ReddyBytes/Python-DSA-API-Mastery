# 🔮 dunder_guide.md — Python Dunder Methods, Deep Dive

> Complete reference for Python's special methods (dunders): every protocol,
> every category, theory-first with production patterns.

---

## 📋 Contents

```
1.  What dunders are — the protocol system
2.  Object lifecycle — __new__, __init__, __del__
3.  String representations — __str__, __repr__, __format__, __bytes__
4.  Comparison and ordering — __eq__, __lt__, __hash__, total_ordering
5.  Arithmetic operators — __add__, __radd__, __iadd__ and friends
6.  Bitwise and unary operators
7.  Container protocol — __len__, __getitem__, __setitem__, __contains__
8.  Iteration protocol — __iter__, __next__, __reversed__
9.  Callable protocol — __call__
10. Attribute access — __getattr__, __getattribute__, __setattr__, __delattr__
11. Context manager protocol — __enter__, __exit__
12. Descriptor protocol — __get__, __set__, __delete__, __set_name__
13. Class creation — __init_subclass__, __class_getitem__
14. Pickling — __getstate__, __setstate__, __reduce__
15. Copy — __copy__, __deepcopy__
16. Complete reference table
```

---

## 1. What Dunders Are — The Protocol System

Python uses **protocols** — sets of dunder methods — to make objects behave
like built-in types. This is the mechanism that lets you write:

```python
len(obj)          # calls obj.__len__()
obj + other       # calls obj.__add__(other)
obj[key]          # calls obj.__getitem__(key)
with obj: ...     # calls obj.__enter__() / obj.__exit__()
for x in obj: ... # calls iter(obj) → obj.__iter__() → obj.__next__()
```

**Why this design?**

Python chose "explicit protocols over inheritance hierarchies". You don't
inherit from a `List` base class to make a list-like object. You implement
`__len__`, `__getitem__`, and optionally others. Python then treats your
object like a sequence automatically — `for` loops work, slicing works,
`len()` works, all without any inheritance.

```
Protocol         Methods Required
─────────────────────────────────────────────────
Sized            __len__
Iterable         __iter__
Iterator         __iter__, __next__
Sequence         __len__, __getitem__
Mapping          __len__, __getitem__, __iter__
Callable         __call__
Context Manager  __enter__, __exit__
Comparable       __eq__, __lt__ (+ others for total ordering)
```

**How Python calls dunders (important!):**

Python calls dunders on the **class**, not the instance. `len(obj)` is really
`type(obj).__len__(obj)`. This has consequences:

```python
class Sneaky:
    def __len__(self):
        return 5

s = Sneaky()
s.__len__ = lambda: 999   # monkey-patch instance attribute

print(len(s))     # → 5  (calls type(s).__len__(s), ignores instance attribute)
print(s.__len__()) # → 999  (direct instance call — bypasses protocol!)
```

This is a deliberate security/performance optimization in CPython.

---

## 2. Object Lifecycle — `__new__`, `__init__`, `__del__`

### `__new__` — Instance Creation

`__new__` is called **before** `__init__`. It creates and returns the instance.
`__init__` then initializes it. You almost never need to override `__new__` —
except for immutable types and singletons.

```python
class ImmutablePoint:
    """Immutable — must set values in __new__ because __init__ runs after."""
    __slots__ = ('x', 'y')

    def __new__(cls, x, y):
        instance = super().__new__(cls)
        # For truly immutable types (subclassing int/str/tuple):
        # object.__setattr__(instance, 'x', x) would bypass __setattr__
        return instance

    def __init__(self, x, y):
        self.x = x   # works fine for regular __slots__ classes
        self.y = y

# Singleton using __new__:
class Singleton:
    _instance = None

    def __new__(cls, *args, **kwargs):
        if cls._instance is None:
            cls._instance = super().__new__(cls)
        return cls._instance

    def __init__(self, value):
        # WARNING: __init__ is called EVERY time Singleton() is called!
        # Guard against re-initialization:
        if not hasattr(self, '_initialized'):
            self.value = value
            self._initialized = True

a = Singleton(1)
b = Singleton(2)
print(a is b)       # True — same object
print(a.value)      # 1 — not overwritten because of guard

# Subclassing immutable types (str, int, tuple):
class AlwaysPositive(int):
    def __new__(cls, value):
        return super().__new__(cls, abs(value))  # must set value in __new__

n = AlwaysPositive(-42)
print(n)   # 42
```

### `__init__` — Initialization

```python
class Config:
    def __init__(self, host, port=8080, **options):
        self.host    = host
        self.port    = port
        self.options = options
        self._validate()   # run validation after all attributes set

    def _validate(self):
        if not 0 < self.port < 65536:
            raise ValueError(f"Invalid port: {self.port}")
```

### `__del__` — Finalizer

Called when the object is about to be garbage collected. **Avoid relying on it** —
the GC is non-deterministic, `__del__` may never run in PyPy, and it can prevent
objects from being collected if it raises exceptions.

```python
class ManagedResource:
    def __init__(self, name):
        self.name = name
        print(f"Opened {name}")

    def __del__(self):
        # Runs when refcount drops to 0 (CPython) or at GC collection
        print(f"Closed {name}")
        # Problem: self.name may be None if Python is shutting down!
        # Problem: exceptions here are silently ignored

    # BETTER: use context manager instead
    def __enter__(self): return self
    def __exit__(self, *_): self.close()
    def close(self): print(f"Closed {self.name}")
```

---

## 3. String Representations

### The Three Representations

```
Method      Called by           Purpose
──────────────────────────────────────────────────────────────
__repr__    repr(obj)           Unambiguous, for developers
            str(obj) fallback   Ideally: eval(repr(obj)) == obj
            f"{obj!r}"
__str__     str(obj)            Human-readable, for users
            print(obj)          Falls back to __repr__ if missing
            f"{obj}"
__format__  format(obj, spec)   Custom format spec support
            f"{obj:spec}"
__bytes__   bytes(obj)          Byte representation
```

### `__repr__` — The Developer View

```python
class Vector:
    def __init__(self, x, y):
        self.x, self.y = x, y

    def __repr__(self):
        # Ideal: eval(repr(v)) == v
        return f"Vector({self.x!r}, {self.y!r})"

v = Vector(1.5, 2.5)
repr(v)   # "Vector(1.5, 2.5)"
# eval("Vector(1.5, 2.5)") would recreate the object (if Vector is in scope)
```

### `__str__` — The User View

```python
class Vector:
    def __repr__(self): return f"Vector({self.x!r}, {self.y!r})"
    def __str__(self):  return f"({self.x}, {self.y})"

v = Vector(1, 2)
str(v)    # "(1, 2)"
repr(v)   # "Vector(1, 2)"
print(v)  # "(1, 2)" — print calls str()
f"{v}"    # "(1, 2)"
f"{v!r}"  # "Vector(1, 2)"
f"{v!s}"  # "(1, 2)"
```

### `__format__` — Custom Format Specs

```python
class Money:
    def __init__(self, amount, currency="USD"):
        self.amount   = amount
        self.currency = currency

    def __repr__(self): return f"Money({self.amount!r}, {self.currency!r})"
    def __str__(self):  return f"{self.currency} {self.amount:.2f}"

    def __format__(self, spec):
        # spec is whatever comes after the colon: f"{m:short}"
        if spec == "short":
            return f"${self.amount:.0f}"
        elif spec == "long":
            return f"{self.amount:.4f} {self.currency}"
        elif spec == "":
            return str(self)
        else:
            # Delegate to float's format for numeric specs like ".2f"
            return format(self.amount, spec)

m = Money(1234.5, "USD")
print(f"{m}")         # "USD 1234.50"
print(f"{m:short}")   # "$1235"
print(f"{m:long}")    # "1234.5000 USD"
print(f"{m:.4f}")     # "1234.5000"
```

---

## 4. Comparison and Ordering

### The Six Comparison Methods

```python
__eq__(self, other)   # ==
__ne__(self, other)   # !=   (default: not self.__eq__(other))
__lt__(self, other)   # <
__le__(self, other)   # <=
__gt__(self, other)   # >
__ge__(self, other)   # >=
```

### `NotImplemented` vs `False`

This is one of Python's most important subtleties:

```python
class Temperature:
    def __init__(self, celsius):
        self.celsius = celsius

    def __eq__(self, other):
        if isinstance(other, Temperature):
            return self.celsius == other.celsius
        return NotImplemented   # ← NOT False!

    def __lt__(self, other):
        if isinstance(other, Temperature):
            return self.celsius < other.celsius
        return NotImplemented
```

**Why `NotImplemented` and not `False`?**

When Python evaluates `a == b`:
1. Try `a.__eq__(b)` → if `NotImplemented`, continue
2. Try `b.__eq__(a)` (reflected) → if `NotImplemented`, fall back to identity
3. Fall back: `a is b`

If `__eq__` returns `False` instead of `NotImplemented`, Python never asks
the right-hand object. A Celsius subclass could never compare equal to a
Temperature parent because the parent would short-circuit with `False`.

```python
t1 = Temperature(100)
t2 = Temperature(100)
print(t1 == t2)   # True

# vs comparing with unknown type:
print(t1 == 100)  # False (NotImplemented → reflected → identity → False)
                  # This is correct — we don't know if 100 means 100°C
```

### `__hash__` — Hashability Rules

**The contract:** if `a == b`, then `hash(a) == hash(b)`.

```python
class Point:
    def __init__(self, x, y):
        self.x, self.y = x, y

    def __eq__(self, other):
        if isinstance(other, Point):
            return self.x == other.x and self.y == other.y
        return NotImplemented

    def __hash__(self):
        # hash must be consistent with __eq__
        return hash((self.x, self.y))   # tuple hash is fine

# If you define __eq__ but not __hash__:
# Python sets __hash__ = None → object becomes unhashable → can't use in set/dict!

# Mutable objects should NOT be hashable (their hash would change):
class MutablePoint:
    def __eq__(self, other): ...
    # DON'T define __hash__ — Python will set it to None automatically
    # because we defined __eq__
```

### `functools.total_ordering`

Only define `__eq__` and ONE of `__lt__/__le__/__gt__/__ge__`, get all 6:

```python
from functools import total_ordering

@total_ordering
class Version:
    def __init__(self, major, minor, patch):
        self.major = major
        self.minor = minor
        self.patch = patch

    def __eq__(self, other):
        if isinstance(other, Version):
            return (self.major, self.minor, self.patch) == (other.major, other.minor, other.patch)
        return NotImplemented

    def __lt__(self, other):
        if isinstance(other, Version):
            return (self.major, self.minor, self.patch) < (other.major, other.minor, other.patch)
        return NotImplemented

    def __repr__(self):
        return f"Version({self.major}, {self.minor}, {self.patch})"

v1 = Version(1, 2, 0)
v2 = Version(2, 0, 0)
print(v1 < v2)   # True
print(v1 > v2)   # False  (derived from __lt__ and __eq__)
print(v1 <= v2)  # True   (derived)
print(sorted([Version(1,0,0), Version(0,9,0), Version(1,1,0)]))
# [Version(0,9,0), Version(1,0,0), Version(1,1,0)]
```

---

## 5. Arithmetic Operators

### The Full Operator Table

```
Method        Operator    Reflected    In-Place
────────────────────────────────────────────────
__add__       a + b       __radd__     __iadd__ (+=)
__sub__       a - b       __rsub__     __isub__ (-=)
__mul__       a * b       __rmul__     __imul__ (*=)
__truediv__   a / b       __rtruediv__ __itruediv__ (/=)
__floordiv__  a // b      __rfloordiv____ifloordiv__ (//=)
__mod__       a % b       __rmod__     __imod__ (%=)
__pow__       a ** b      __rpow__     __ipow__ (**=)
__matmul__    a @ b       __rmatmul__  __imatmul__ (@=)  (3.5+)
```

### Why `__radd__` Exists

When Python evaluates `a + b`:
1. Call `a.__add__(b)` — if `NotImplemented`, continue
2. Call `b.__radd__(a)` — if `NotImplemented`, raise TypeError

This lets a right-hand object of a different type participate in operations:

```python
class Vector:
    def __init__(self, *components):
        self.data = list(components)

    def __add__(self, other):
        if isinstance(other, Vector):
            return Vector(*(a + b for a, b in zip(self.data, other.data)))
        if isinstance(other, (int, float)):
            return Vector(*(x + other for x in self.data))
        return NotImplemented

    def __radd__(self, other):
        # Called when: other + self (and other.__add__(self) returned NotImplemented)
        # For commutative ops, just delegate:
        return self.__add__(other)

    def __iadd__(self, other):
        # Called for +=  — can modify in place and return self (efficient!)
        if isinstance(other, Vector):
            self.data = [a + b for a, b in zip(self.data, other.data)]
            return self
        if isinstance(other, (int, float)):
            self.data = [x + other for x in self.data]
            return self
        return NotImplemented

    def __repr__(self):
        return f"Vector({', '.join(map(str, self.data))})"

v = Vector(1, 2, 3)
print(v + Vector(10, 20, 30))   # Vector(11, 22, 33)
print(v + 5)                     # Vector(6, 7, 8)
print(5 + v)                     # Vector(6, 7, 8) — uses __radd__
v += Vector(1, 1, 1)
print(v)                         # Vector(2, 3, 4)
```

### `__neg__`, `__pos__`, `__abs__`, `__invert__`

Unary operators:

```python
class Vector:
    def __neg__(self):    # -v
        return Vector(*(-x for x in self.data))

    def __pos__(self):    # +v
        return Vector(*self.data)   # copy

    def __abs__(self):    # abs(v)  — also used by math.sqrt etc.
        return sum(x**2 for x in self.data) ** 0.5

    def __invert__(self): # ~v  (bitwise NOT — use for your own semantics)
        return Vector(*(~x for x in self.data))   # only makes sense for ints
```

---

## 6. Container Protocol

### `__len__`, `__getitem__`, `__setitem__`, `__delitem__`

```python
class Matrix:
    def __init__(self, rows, cols, default=0):
        self.rows = rows
        self.cols = cols
        self._data = [[default] * cols for _ in range(rows)]

    def __len__(self):
        # Convention: len of a 2D structure → number of rows
        return self.rows

    def __getitem__(self, key):
        row, col = key   # allow: m[0, 1]
        return self._data[row][col]

    def __setitem__(self, key, value):
        row, col = key
        self._data[row][col] = value

    def __delitem__(self, key):
        row, col = key
        self._data[row][col] = 0   # "delete" means reset to default

    def __contains__(self, value):
        return any(value in row for row in self._data)

    def __iter__(self):
        # Iterating a matrix → iterate rows (each row is a list)
        return iter(self._data)

m = Matrix(3, 3)
m[0, 0] = 1
m[1, 1] = 5
m[2, 2] = 9
print(m[1, 1])   # 5
print(5 in m)    # True
for row in m:
    print(row)
```

### Slicing Support

```python
class CircularBuffer:
    def __init__(self, capacity):
        self._buf  = [None] * capacity
        self._size = 0
        self._head = 0

    def append(self, item):
        idx = (self._head + self._size) % len(self._buf)
        if self._size < len(self._buf):
            self._size += 1
        else:
            self._head = (self._head + 1) % len(self._buf)
        self._buf[idx] = item

    def __len__(self): return self._size

    def __getitem__(self, index):
        if isinstance(index, slice):
            # Handle slice by converting to range of indices
            indices = range(*index.indices(self._size))
            return [self._get_item(i) for i in indices]
        if index < 0:
            index += self._size
        if not (0 <= index < self._size):
            raise IndexError(f"index {index} out of range")
        return self._get_item(index)

    def _get_item(self, index):
        return self._buf[(self._head + index) % len(self._buf)]

buf = CircularBuffer(5)
for i in range(7): buf.append(i)
print(buf[0])     # 2  (oldest = 5 - 5 + 2)
print(buf[-1])    # 6
print(buf[1:3])   # [3, 4]
```

### `__bool__`

Controls truthiness. If absent, Python falls back to `__len__` (empty = falsy):

```python
class QueryResult:
    def __init__(self, rows):
        self.rows = rows

    def __len__(self):   return len(self.rows)
    def __bool__(self):  return bool(self.rows)   # explicit is better

result = QueryResult([])
if result:
    print("has rows")
else:
    print("empty")   # ← this branch
```

---

## 7. Iteration Protocol

```python
class CountDown:
    """Iterable AND iterator — implements both protocols."""

    def __init__(self, start):
        self.start   = start
        self.current = start

    def __iter__(self):
        # Returning self makes this object an iterator (single-pass)
        # To make it re-usable, return a NEW iterator object instead
        return self

    def __next__(self):
        if self.current <= 0:
            raise StopIteration
        value = self.current
        self.current -= 1
        return value

for n in CountDown(5):
    print(n)   # 5 4 3 2 1

# Better: separate iterable from iterator for re-use:
class Range:
    def __init__(self, stop):
        self.stop = stop

    def __iter__(self):
        return RangeIterator(self.stop)   # new iterator each time

class RangeIterator:
    def __init__(self, stop):
        self.stop    = stop
        self.current = 0

    def __iter__(self): return self   # iterators must return self
    def __next__(self):
        if self.current >= self.stop:
            raise StopIteration
        val = self.current
        self.current += 1
        return val

r = Range(5)
list(r)   # [0, 1, 2, 3, 4]
list(r)   # [0, 1, 2, 3, 4] — works again! (new iterator each time)

# __reversed__ — for reversed(obj):
class OrderedData:
    def __init__(self, data):
        self.data = data

    def __iter__(self):     return iter(self.data)
    def __reversed__(self): return iter(reversed(self.data))

    # Without __reversed__, reversed() would require __len__ + __getitem__
```

---

## 8. Callable Protocol — `__call__`

Any object with `__call__` can be called like a function:

```python
class Multiplier:
    def __init__(self, factor):
        self.factor = factor

    def __call__(self, x):
        return x * self.factor

double = Multiplier(2)
triple = Multiplier(3)
print(double(5))   # 10
print(triple(5))   # 15

# Callable objects preserve state between calls — unlike lambdas:
class Counter:
    def __init__(self):
        self.count = 0

    def __call__(self):
        self.count += 1
        return self.count

c = Counter()
print(c(), c(), c())   # 1 2 3

# Check callability:
callable(double)   # True
callable(42)       # False

# Use case: configurable predicates
class InRange:
    def __init__(self, lo, hi):
        self.lo, self.hi = lo, hi
    def __call__(self, x):
        return self.lo <= x <= self.hi

is_valid_port = InRange(1, 65535)
print(is_valid_port(80))     # True
print(is_valid_port(99999))  # False
print(list(filter(is_valid_port, [0, 80, 443, 65536])))  # [80, 443]
```

---

## 9. Attribute Access

### The Attribute Lookup Chain

```
obj.name access order:
1. type(obj).__mro__ → data descriptor (has __get__ AND __set__)
2. obj.__dict__
3. type(obj).__mro__ → non-data descriptor (has __get__ only) or class variable
4. type(obj).__getattr__(name) (if defined, last resort)
```

### `__getattr__` vs `__getattribute__`

```python
class Proxy:
    """__getattr__ — only called when normal lookup fails."""

    def __init__(self, target):
        # Use object.__setattr__ to avoid triggering our __setattr__:
        object.__setattr__(self, '_target', target)

    def __getattr__(self, name):
        # Only reached when attribute NOT found normally
        return getattr(self._target, name)

    def __setattr__(self, name, value):
        if name.startswith('_'):
            object.__setattr__(self, name, value)
        else:
            setattr(self._target, name, value)

# __getattribute__ — called for EVERY attribute access (powerful but careful):
class TracingProxy:
    def __init__(self, target):
        object.__setattr__(self, '_target', target)

    def __getattribute__(self, name):
        # This intercepts EVERYTHING including _target!
        # Must use object.__getattribute__ to access own attributes:
        target = object.__getattribute__(self, '_target')
        if name.startswith('_'):
            return object.__getattribute__(self, name)
        print(f"  Accessing: {name}")
        return getattr(target, name)
```

### `__dir__` — Customizing `dir()`

```python
class NamespacedProxy:
    def __init__(self, data):
        self._data = data

    def __dir__(self):
        default = list(super().__dir__())
        return default + list(self._data.keys())

    def __getattr__(self, name):
        if name in self._data:
            return self._data[name]
        raise AttributeError(name)

p = NamespacedProxy({"color": "red", "size": 42})
print("color" in dir(p))   # True
print(p.color)              # "red"
```

---

## 10. Context Manager Protocol

```python
class Timer:
    """Measure elapsed time using with-statement."""
    import time

    def __enter__(self):
        self._start = time.time()
        return self   # bound to 'as' variable

    def __exit__(self, exc_type, exc_val, exc_tb):
        self.elapsed = time.time() - self._start
        # Return True to suppress exceptions, False/None to propagate
        return False

with Timer() as t:
    result = sum(range(1_000_000))
print(f"Elapsed: {t.elapsed:.3f}s")

# Suppressing exceptions:
class SuppressOSError:
    def __enter__(self): return self
    def __exit__(self, exc_type, exc_val, exc_tb):
        if exc_type is OSError:
            return True    # suppress
        return False       # propagate everything else

with SuppressOSError():
    open("/nonexistent/path")   # silently ignored
print("Still running")
```

---

## 11. Pickling — `__getstate__` / `__setstate__`

```python
import pickle

class Connection:
    """Can't pickle socket — exclude it from pickle state."""

    def __init__(self, host, port):
        self.host   = host
        self.port   = port
        self._socket = self._connect()   # not picklable

    def _connect(self):
        import socket
        s = socket.socket()
        # s.connect((self.host, self.port))  # would actually connect
        return s

    def __getstate__(self):
        # Return the state to be pickled (exclude _socket):
        state = self.__dict__.copy()
        del state['_socket']
        return state

    def __setstate__(self, state):
        # Restore from pickled state:
        self.__dict__.update(state)
        self._socket = self._connect()   # reconnect

conn = Connection("localhost", 8080)
data = pickle.dumps(conn)       # serialize
conn2 = pickle.loads(data)      # deserialize + reconnect
```

---

## 12. Copy Protocol — `__copy__` / `__deepcopy__`

```python
import copy

class Graph:
    def __init__(self, nodes):
        self.nodes = nodes
        self._cache = {}   # don't copy the cache

    def __copy__(self):
        # Shallow copy — new Graph, shared node list
        new = Graph(self.nodes)   # shares self.nodes
        # Don't copy _cache — start fresh
        return new

    def __deepcopy__(self, memo):
        # memo dict: id → copy (prevents infinite recursion on circular refs)
        new = Graph(copy.deepcopy(self.nodes, memo))
        # _cache not copied
        return new

g = Graph([1, 2, 3])
g2 = copy.copy(g)     # calls __copy__
g3 = copy.deepcopy(g) # calls __deepcopy__
```

---

## 13. Complete Reference Table

```
Category         Method              Trigger
──────────────────────────────────────────────────────────────
Lifecycle        __new__             cls()
                 __init__            cls() after __new__
                 __del__             object GC'd

Representation   __repr__            repr(obj)
                 __str__             str(obj), print(obj)
                 __format__          format(obj, spec), f"{obj:spec}"
                 __bytes__           bytes(obj)

Comparison       __eq__              obj == other
                 __ne__              obj != other
                 __lt__              obj < other
                 __le__              obj <= other
                 __gt__              obj > other
                 __ge__              obj >= other
                 __hash__            hash(obj), dict key, set member

Arithmetic       __add__/__radd__    a + b
                 __sub__/__rsub__    a - b
                 __mul__/__rmul__    a * b
                 __truediv__         a / b
                 __floordiv__        a // b
                 __mod__             a % b
                 __pow__             a ** b
                 __matmul__          a @ b
                 __neg__             -a
                 __pos__             +a
                 __abs__             abs(a)
                 __invert__          ~a
                 __iadd__ etc.       a += b (in-place variants)

Bitwise          __and__/__or__      a & b, a | b
                 __xor__             a ^ b
                 __lshift__          a << b
                 __rshift__          a >> b

Type coercion    __int__             int(obj)
                 __float__           float(obj)
                 __complex__         complex(obj)
                 __bool__            bool(obj), if obj:
                 __index__           obj used as int in slice/bin/oct/hex

Container        __len__             len(obj)
                 __length_hint__     operator.length_hint(obj)  (optional est.)
                 __getitem__         obj[key]
                 __setitem__         obj[key] = val
                 __delitem__         del obj[key]
                 __contains__        item in obj
                 __missing__         obj[key] when key missing (dict subclass)

Iteration        __iter__            iter(obj), for x in obj
                 __next__            next(obj)
                 __reversed__        reversed(obj)
                 __aiter__           async for x in obj
                 __anext__           async next

Callable         __call__            obj(args)

Attribute        __getattr__         obj.name (fallback)
                 __getattribute__    obj.name (always)
                 __setattr__         obj.name = val
                 __delattr__         del obj.name
                 __dir__             dir(obj)

Descriptor       __get__             descriptor accessed via class/instance
                 __set__             descriptor set via instance
                 __delete__          descriptor deleted via instance
                 __set_name__        descriptor assigned to class attr

Context Mgr      __enter__           with obj: (entry)
                 __exit__            with obj: (exit)
                 __aenter__          async with obj: (entry)
                 __aexit__           async with obj: (exit)

Class creation   __init_subclass__   when class subclassed
                 __class_getitem__   cls[item] (generics)
                 __instancecheck__   isinstance(obj, cls)
                 __subclasscheck__   issubclass(sub, cls)

Pickling         __getstate__        pickle.dumps
                 __setstate__        pickle.loads
                 __reduce__          full custom pickling

Copy             __copy__            copy.copy(obj)
                 __deepcopy__        copy.deepcopy(obj)

With             __slots__           optimizes memory layout (class-level)
```

---

## 🔁 Navigation

| | |
|---|---|
| 📖 Theory | [theory.md](./theory.md) |
| 🏭 Metaclasses & Descriptors | [metaclasses_descriptors_guide.md](./metaclasses_descriptors_guide.md) |
| 🎯 Interview | [interview.md](./interview.md) |
| ⚡ Cheatsheet | [cheatsheet.md](./cheatsheet.md) |
